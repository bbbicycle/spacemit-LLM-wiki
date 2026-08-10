---
sidebar_position: 7
---

# Triton

> **SpacemiT Triton** is built on [spine-triton](https://github.com/spacemit-com/spine-triton) and brings high-performance kernel development via a Python DSL to SpacemiT K1/K3 RISC-V CPU platforms. It preserves the familiar Triton programming model while adding three CPU-specific extensions: `CPUDriver` for CPU execution, the `SMT` API for tensor-core acceleration, and `Proton` for kernel-level performance profiling.

---

- [Triton](#triton)
  - [Overview](#overview)
  - [Differences from Upstream Triton](#differences-from-upstream-triton)
  - [Getting Started](#getting-started)
    - [Environment Setup](#environment-setup)
    - [Minimal Verification](#minimal-verification)
  - [Core Programming Model](#core-programming-model)
    - [tl Basics](#tl-basics)
    - [SMT Extension](#smt-extension)
    - [Proton Profiling](#proton-profiling)
  - [Development Guidelines](#development-guidelines)
  - [References](#references)

## Overview

`spine-triton` is a fork of `microsoft/triton-shared`. Its goal is to provide a Triton-compatible kernel development and tuning framework that targets RISC-V CPU execution on SpacemiT hardware.

It is a good fit for the following use cases:

- Writing custom kernels for hot paths such as matrix multiplication, elementwise ops, and reductions.
- Iterating on performance parameters — block size, micro tile layout, memory access patterns — directly from Python.
- Filling in missing operators or doing operator-level performance tuning for model inference on K1/K3.
- Profiling at kernel granularity or within kernel stages using Proton.

The typical compilation pipeline on SpacemiT looks like this:

```text
Triton Python DSL
       ↓
   Triton IR (TTIR)
       ↓ (triton-to-linalg)
   Linalg IR
       ↓ (spine-mlir)
   LLVM IR
       ↓ (llc)
   Target binary (RISC-V)
```

## Differences from Upstream Triton

| Feature | Upstream Triton | SpacemiT Triton |
| --- | --- | --- |
| Target hardware | NVIDIA GPU | SpacemiT RISC-V CPU |
| Code generation | CUDA / PTX | spine-mlir → LLVM IR → RISC-V |
| Driver model | GPU Driver | `CPUDriver` |
| Platform extensions | GPU-centric | `SMT` tensor-core API, CPU-side Proton |
| Tuning focus | block/grid, VRAM access | block pointer, micro tile, CPU kernel profiling |

From a developer's perspective, the three most important differences are:

- `CPUDriver` must be explicitly activated before running any kernel.
- For compute-heavy ops like matrix multiplication, prefer calling SpacemiT tensor-core capabilities through `triton.language.extra.smt`.
- Proton on CPU supports both manual instrumentation and automatic kernel capture via an environment variable.

## Getting Started

### Environment Setup

When using the official prebuilt wheel, set up the environment as described in the `spine-triton` README:

```bash
apt update

apt install gcc g++ gdb libsleef-dev libnuma-dev libomp5 libgomp1 python3-dev

pip install PyYAML sympy torch opencv-python pybind11 --index-url https://git.spacemit.com/api/v4/projects/33/packages/pypi/simple
pip install triton --index-url https://git.spacemit.com/api/v4/projects/33/packages/pypi/simple
```

When building from source for local development, the following environment variables are also required:

```bash
export PYTHONPATH=/path/to/spine-triton/build-riscv64:$PYTHONPATH
export SPINE_TRITON_DUMP_PATH=./ir_dumps
# Only needed to force kernel recompilation
export TRITON_ALWAYS_COMPILE=1
```

### Minimal Verification

The `spine-triton` README includes a minimal matrix multiplication example to verify the setup:

```bash
# export SPINE_TRITON_DUMP_PATH=./ir_dumps
python3 python/examples/test_smt_mm.py
```

The initialization pattern is the same whether running the example or writing a custom kernel:

```python
import torch
import triton
import triton.language as tl
import triton.language.extra.smt as smt
from triton.backends.spine_triton.driver import CPUDriver

triton.runtime.driver.set_active(CPUDriver())
```

## Core Programming Model

### tl Basics

SpacemiT Triton preserves the core Triton DSL semantics. The common patterns are the same as upstream:

- Define kernels with `@triton.jit`.
- Use `tl.program_id(axis)` to compute the block index along each dimension.
- Use `tl.make_block_ptr(...)` to construct block pointers, then access data with `tl.load` and `tl.store`.
- Mark compile-time constant parameters with `tl.constexpr`.

On SpacemiT, prefer block pointers over the traditional `mask + tl.arange` access pattern:

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

### SMT Extension

`SMT` is the core extension that `spine-triton` provides for SpacemiT hardware. It is designed for ops that benefit from tensor-core acceleration, such as matrix multiplication.

Key APIs:

- `smt.descriptor_load` — efficient block load based on block pointers.
- `smt.view` — reshape a 2D tensor into a 4D packed view with micro tile layout.
- `smt.dot` — tensor-core-optimized 4D matrix multiplication.
- `smt.parallel` — express parallel iteration across multiple tensor cores.

A simplified matrix multiplication kernel looks like this:

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

Use the following table as a quick reference for choosing between `smt` and `tl`:

| Operator type | Recommended approach | Notes |
| --- | --- | --- |
| Matrix multiplication (mm, bmm, addmm) | `smt` module | Leverages tensor-core acceleration |
| Elementwise ops (relu, gelu, silu) | Standard `tl` ops | Simple to write and tune |
| Reductions (softmax, layernorm) | `tl` + loop | Requires an explicit accumulator |
| Matrix-vector multiply (mv) | `tl` + loop | Well-suited for tiled accumulation |

### Proton Profiling

`Proton` is the performance profiling tool in the Triton ecosystem. In `spine-triton` it has been ported to the K1/K3 CPU platform. There are three common usage modes:

- **Fine-grained in-kernel instrumentation** — use `pl.enter_scope()` / `pl.exit_scope()` to mark phases such as load, compute, and store, then collect data with `profiler.profile()`.
- **Coarse-grained external profiling** — use `triton.profiler as proton` and `proton.scope()` to measure cycles and instructions across a block of kernel calls.
- **Automatic kernel capture** — set `PROTON_KERNEL_CAPTURE=1` to have the CPU backend automatically record timing for every kernel, with no changes to the application code.

The most common pattern for fine-grained profiling is:

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

To quickly check kernel-level timing without modifying application code, enable automatic capture:

```bash
rm -rf ~/.triton/cache
PROTON_KERNEL_CAPTURE=1 PROTON_OUTPUT=trace.json python3 your_script.py
```

Available environment variables:

| Variable | Description |
| --- | --- |
| `PROTON_OUTPUT` | Output file path and format; supports `.json` and `.hatchet` |
| `PROTON_VERBOSE` | Enable verbose output |
| `TRITON_DISABLE_PROTON` | Temporarily disable Proton |
| `PROTON_KERNEL_CAPTURE` | Enable automatic kernel capture on CPU |
| `SPINE_TRITON_DUMP_PATH` | Dump IR for debugging the compilation pipeline |

Notes on output formats:

- `.json` output can be viewed in `chrome://tracing` or [Perfetto UI](https://ui.perfetto.dev).
- `.hatchet` output is suited for further aggregated performance analysis.
- `PROTON_KERNEL_CAPTURE=1` is a compile-time option. Clear `~/.triton/cache` the first time it is enabled or whenever the setting is toggled.

## Development Guidelines

- For matrix multiplication kernels, use `smt.dot`. For elementwise ops and simple reductions, use `tl` primitives.
- Prefer `tl.make_block_ptr` with `boundary_check` for memory access. Avoid relying on `mask` in performance-critical paths.
- For `float16` kernels, accumulate in `float32` during intermediate computation and cast back to the original type before storing.
- For matrix multiplication, start tuning `BLOCK_SIZE` in the `128–256` range. For elementwise ops, try `1024` as a starting point.
- When using `smt.view`, ensure the tensor shape is divisible by the micro tile size. The official guide recommends `(16, 8, 32)` for `float16` and `(8, 8, 16)` for `float32`.
- When debugging compilation or performance issues, start by inspecting the IR with `SPINE_TRITON_DUMP_PATH`, then enable `TRITON_ALWAYS_COMPILE=1` and Proton as needed.

## References

- [spine-triton README](https://github.com/spacemit-com/spine-triton/blob/main/README.md)
- [Spine-Triton Operator Development Guide](https://github.com/spacemit-com/spine-triton/blob/main/.github/instructions/operator_development_guide.md)
- [Proton Profiling Tool Guide](https://github.com/spacemit-com/spine-triton/blob/main/.github/instructions/proton_usage_guide.md)
- [Triton Official Documentation](https://triton-lang.org/)
