---
sidebar_position: 7
---

# Triton

> **SpacemiT Triton** 基于 [spine-triton](https://github.com/spacemit-com/spine-triton) 实现，面向 SpacemiT K1/K3 等 RISC-V CPU 平台提供 Python DSL 的高性能算子开发能力。它继承了社区 Triton 的编程体验，并扩展了面向 CPU 的 `CPUDriver`、面向张量核心的 `SMT` API，以及面向内核调优的 `Proton` 性能分析能力。

---

- [简介](#简介)
- [与标准 Triton 的差异](#与标准-triton-的差异)
- [快速开始](#快速开始)
- [环境准备](#环境准备)
- [最小验证](#最小验证)
- [核心编程模型](#核心编程模型)
- [tl 基础](#tl-基础)
- [SMT 扩展](#smt-扩展)
- [Proton 性能分析](#proton-性能分析)
- [开发建议](#开发建议)
- [参考资源](#参考资源)

## 简介

`spine-triton` fork 自 `microsoft/triton-shared`，目标是在 SpacemiT 平台上提供一套与 Triton 生态兼容、但面向 RISC-V CPU 执行的算子开发与调优框架。

它适合以下场景：

- 为矩阵乘、逐元素、规约等热点路径快速编写定制算子。
- 在 Python 侧验证 block size、micro tile、访存方式等性能参数。
- 为 K1/K3 平台上的模型推理框架补齐特定算子或做算子级性能优化。
- 结合 Proton 对 kernel 粒度或 kernel 内部阶段进行性能剖析。

在 SpacemiT 平台上的典型编译流程如下：

```text
Triton Python DSL
       ↓
   Triton IR (TTIR)
       ↓ (triton-to-linalg)
   Linalg IR
       ↓ (spine-mlir)
   LLVM IR
       ↓ (llc)
   目标代码 (RISC-V)
```

## 与标准 Triton 的差异

| 特性 | 标准 Triton | SpacemiT Triton |
| --- | --- | --- |
| 目标硬件 | NVIDIA GPU | SpacemiT RISC-V CPU |
| 后端生成 | CUDA/PTX | spine-mlir -> LLVM IR -> RISC-V |
| 驱动模型 | GPU Driver | `CPUDriver` |
| 平台扩展 | 以 GPU 为中心 | `SMT` 张量核心接口、CPU 版 Proton |
| 调优重点 | block/grid、显存访问 | block pointer、micro tile、CPU kernel profiling |

对使用者来说，最关键的差异有三点：

- 运行前需要显式启用 `CPUDriver`。
- 矩阵乘等高算力算子优先通过 `triton.language.extra.smt` 调用 SpacemiT 张量核心能力。
- Proton 在 CPU 上既支持手动插桩，也支持通过环境变量启用自动 kernel 捕获。

## 快速开始

### 环境准备

如果直接使用官方预编译 wheel，可按 `spine-triton` README 中的方式准备环境：

```bash
apt update

apt install gcc g++ gdb libsleef-dev libnuma-dev libomp5 libgomp1 python3-dev

pip install PyYAML sympy torch opencv-python pybind11 --index-url https://git.spacemit.com/api/v4/projects/33/packages/pypi/simple
pip install triton --index-url https://git.spacemit.com/api/v4/projects/33/packages/pypi/simple
```

如果是源码构建后在本地开发，通常还需要补充以下环境变量：

```bash
export PYTHONPATH=/path/to/spine-triton/build-riscv64:$PYTHONPATH
export SPINE_TRITON_DUMP_PATH=./ir_dumps
# 仅在需要强制重新编译 kernel 时启用
export TRITON_ALWAYS_COMPILE=1
```

### 最小验证

`spine-triton` README 提供了一个最小矩阵乘示例：

```bash
# export SPINE_TRITON_DUMP_PATH=./ir_dumps
python3 python/examples/test_smt_mm.py
```

无论是运行示例还是自行写算子，初始化模式都基本一致：

```python
import torch
import triton
import triton.language as tl
import triton.language.extra.smt as smt
from triton.backends.spine_triton.driver import CPUDriver

triton.runtime.driver.set_active(CPUDriver())
```

## 核心编程模型

### tl 基础

SpacemiT Triton 保持了 Triton 的核心 DSL 语义，常见写法与社区版本接近：

- 使用 `@triton.jit` 定义 kernel。
- 使用 `tl.program_id(axis)` 计算 block 在不同维度上的索引。
- 使用 `tl.make_block_ptr(...)` 构造块指针，并配合 `tl.load`、`tl.store` 访问数据。
- 对编译期常量参数使用 `tl.constexpr`。

在 SpacemiT 平台上，推荐优先使用 block pointer，而不是传统的 `mask + tl.arange` 访存方式：

```python
block_ptr = tl.make_block_ptr(
    base=ptr,
    shape=[M, N],
    strides=[stride_m, stride_n],
    offsets=[pid_m * BLOCK_M, 0],
    block_shape=[BLOCK_M, BLOCK_N],
    order=[1, 0],
)

data = tl.load(block_ptr, boundary_check=(0, 1))
tl.store(block_ptr, data, boundary_check=(0, 1))
```

### SMT 扩展

`SMT` 是 `spine-triton` 针对 SpacemiT 硬件提供的核心扩展，适合矩阵乘等需要张量核心加速的场景。

常用 API 包括：

- `smt.descriptor_load`：基于 block pointer 的高效块加载。
- `smt.view`：把 2D 张量重排为带 micro tile 的 4D packed 视图。
- `smt.dot`：执行面向张量核心优化的 4D 矩阵乘。
- `smt.parallel`：表达多张量核心参与的并行迭代。

一个简化后的矩阵乘写法如下：

```python
@triton.jit
def mm_kernel(
    a_ptr, b_ptr, c_ptr,
    M, N, K,
    stride_am, stride_ak,
    stride_bk, stride_bn,
    stride_cm, stride_cn,
    BLOCK_SIZE_M: tl.constexpr,
    BLOCK_SIZE_N: tl.constexpr,
    BLOCK_SIZE_K: tl.constexpr,
    MICRO_M: tl.constexpr,
    MICRO_K: tl.constexpr,
    MICRO_N: tl.constexpr,
):
    pid_m = tl.program_id(0)
    pid_n = tl.program_id(1)

    a_block_ptr = tl.make_block_ptr(
        base=a_ptr,
        shape=[M, K],
        strides=[stride_am, stride_ak],
        offsets=[pid_m * BLOCK_SIZE_M, 0],
        block_shape=[BLOCK_SIZE_M, BLOCK_SIZE_K],
        order=[1, 0],
    )
    b_block_ptr = tl.make_block_ptr(
        base=b_ptr,
        shape=[K, N],
        strides=[stride_bk, stride_bn],
        offsets=[0, pid_n * BLOCK_SIZE_N],
        block_shape=[BLOCK_SIZE_K, BLOCK_SIZE_N],
        order=[1, 0],
    )

    a = smt.view(
        smt.descriptor_load(a_block_ptr, (0, 0)),
        (0, 0),
        (BLOCK_SIZE_M, BLOCK_SIZE_K),
        (MICRO_M, MICRO_K),
    )
    b = smt.view(
        smt.descriptor_load(b_block_ptr, (0, 0)),
        (0, 0),
        (BLOCK_SIZE_K, BLOCK_SIZE_N),
        (MICRO_K, MICRO_N),
    )

    acc = smt.dot(a, b)
    acc = smt.view(acc, (0, 0), (BLOCK_SIZE_M, BLOCK_SIZE_N), (1, 1))
    c = acc.to(c_ptr.dtype.element_ty)

    c_block_ptr = tl.make_block_ptr(
        base=c_ptr,
        shape=[M, N],
        strides=[stride_cm, stride_cn],
        offsets=[pid_m * BLOCK_SIZE_M, pid_n * BLOCK_SIZE_N],
        block_shape=[BLOCK_SIZE_M, BLOCK_SIZE_N],
        order=[1, 0],
    )
    tl.store(c_block_ptr, c, boundary_check=(0, 1))
```

从算子类型上看，推荐选择方式如下：

| 算子类型 | 推荐方式 | 说明 |
| --- | --- | --- |
| 矩阵乘法（mm、bmm、addmm） | `smt` 模块 | 优先利用张量核心加速 |
| 逐元素操作（relu、gelu、silu） | `tl` 标准操作 | 代码简单、易调优 |
| 规约操作（softmax、layernorm） | `tl` + 循环 | 需要显式累加器 |
| 矩阵向量乘（mv） | `tl` + 循环 | 适合分块累加 |

### Proton 性能分析

`Proton` 是 Triton 生态中的性能分析工具，在 `spine-triton` 中已经适配到 K1/K3 CPU 平台。对于 SpacemiT Triton，常见有三种使用方式：

- kernel 内部细粒度插桩：用 `pl.enter_scope()` / `pl.exit_scope()` 标出 load、compute、store 等阶段，再用 `profiler.profile()` 采集。
- kernel 外部粗粒度分析：用 `triton.profiler as proton` 和 `proton.scope()` 统计某段 kernel 调用的 cycles / instructions。
- 自动 kernel 捕获：设置 `PROTON_KERNEL_CAPTURE=1` 后，在 CPU 后端自动记录每个 kernel 的时间，无需改业务代码。

最常见的细粒度分析写法如下：

```python
import triton.profiler.language as pl
from triton.profiler.flags import flags
from triton.backends.spine_triton.proton import profiler

pl.enable_semantic("triton")
flags.instrumentation_on = True

@triton.jit
def my_kernel(...):
    pl.enter_scope("load")
    # ... load code ...
    pl.exit_scope("load")

    pl.enter_scope("compute")
    # ... compute code ...
    pl.exit_scope("compute")

with profiler.profile():
    my_kernel[grid](...)
```

如果只想快速看 kernel 级耗时分布，CPU 平台上还可以直接启用自动捕获：

```bash
rm -rf ~/.triton/cache
PROTON_KERNEL_CAPTURE=1 PROTON_OUTPUT=trace.json python3 your_script.py
```

常用环境变量如下：

| 环境变量 | 说明 |
| --- | --- |
| `PROTON_OUTPUT` | 指定输出文件与格式，支持 `.json` 和 `.hatchet` |
| `PROTON_VERBOSE` | 打开详细输出 |
| `TRITON_DISABLE_PROTON` | 临时禁用 Proton |
| `PROTON_KERNEL_CAPTURE` | 启用 CPU 自动 kernel 捕获 |
| `SPINE_TRITON_DUMP_PATH` | 导出 IR，便于调试编译链路 |

其中：

- `.json` 输出可在 `chrome://tracing` 或 `https://ui.perfetto.dev` 中查看。
- `.hatchet` 输出适合进一步做性能聚合分析。
- `PROTON_KERNEL_CAPTURE=1` 是编译时选项，首次启用或切换开关时需要清理 `~/.triton/cache`。

## 开发建议

- 矩阵乘类算子优先使用 `smt.dot`，逐元素与简单规约优先使用 `tl` 原语。
- 优先使用 `tl.make_block_ptr` + `boundary_check` 的访存方式，避免在性能敏感路径过度依赖 `mask`。
- `float16` 算子通常应在中间计算阶段转成 `float32` 累加，再在落盘时转回原始类型。
- 对矩阵乘，`BLOCK_SIZE` 一般从 `128-256` 开始调；对逐元素操作，可先尝试 `1024` 级别的 block。
- 对 `smt.view`，需保证 shape 能被 micro tile 整除；官方指南中推荐 `float16` 使用 `(16, 8, 32)`，`float32` 使用 `(8, 8, 16)`。
- 遇到编译或性能问题时，先结合 `SPINE_TRITON_DUMP_PATH` 查看 IR，再按需打开 `TRITON_ALWAYS_COMPILE=1` 与 Proton 分析。

## 参考资源

- [spine-triton README](https://github.com/spacemit-com/spine-triton/blob/main/README.md)
- [Spine-Triton 算子开发指南](https://github.com/spacemit-com/spine-triton/blob/main/.github/instructions/operator_development_guide.md)
- [Proton 性能分析工具使用指南](https://github.com/spacemit-com/spine-triton/blob/main/.github/instructions/proton_usage_guide.md)
- [Triton 官方文档](https://triton-lang.org/)
