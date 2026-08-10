---
sidebar_position: 4
---

# 其他数学库

> **其他数学库** 主要用于为上层 AI 框架、数值计算程序和高性能算子提供基础数学能力。在 SpacemiT RISC-V 平台上，常用的数学库主要包括 OpenBLAS 和 SLEEF，分别覆盖线性代数计算与基础数学函数向量化加速场景。

---

- [其他数学库](#其他数学库)
    - [简介](#简介)
    - [资源获取](#资源获取)
    - [OpenBLAS 源码构建](#openblas-源码构建)
      - [使用构建脚本](#使用构建脚本)
    - [SLEEF 源码构建](#sleef-源码构建)
      - [使用脚本构建](#使用脚本构建)
      - [轻量构建建议](#轻量构建建议)
      - [RISC-V 支持说明](#risc-v-支持说明)
    - [项目集成](#项目集成)
      - [CMake 集成示例](#cmake-集成示例)
    - [OpenBLAS Demo](#openblas-demo)
    - [SLEEF Demo](#sleef-demo)
    - [性能验证建议](#性能验证建议)
    - [当前支持状态](#当前支持状态)


### 简介

数学库是 AI 计算软件栈中连接上层框架、算子实现和底层硬件能力的重要基础组件。对于推理框架、科学计算程序和图像处理流水线而言，矩阵乘法、向量运算、三角函数、指数函数和对数函数等基础能力，通常直接决定了大量高频路径的执行效率。

针对进迭时空 RISC-V 平台，当前重点支持并深度优化了以下两类数学组件：

- **OpenBLAS**：提供标准的 BLAS/LAPACK 接口，面向矩阵乘法、向量运算及复杂的线性代数例程，是众多数值计算库和高级推理框架的底层支柱。在平台上的典型优化接口包括 `cblas_sgemm`、`cblas_dgemm`、`cblas_saxpy`、`cblas_sdot` 等。
- **SLEEF**：提供高性能、高精度的 SIMD 数学函数实现，专注于 `sin`、`cos`、`exp`、`log`、`sqrt` 等标量或向量化计算的底层加速。在实际工程中，SLEEF 常被用作标准 `libm` 的补充，或作为向量化计算后端的首选组件。

通过在架构级适配 RVV（RISC-V Vector Extension）指令集，这两类组件为上层推理框架、视觉处理流水线以及自定义算子开发，提供了开箱即用的计算接口与极具竞争力的性能基线。

### 资源获取

> TODO: 补充具体的发布获取链接或途径

### OpenBLAS 源码构建

对于需要在 SpacemiT 平台上利用最新 RVV 加速特性或极致调优矩阵乘性能的用户，我们推荐获取定制化的 OpenBLAS 分支进行构建。

#### 使用构建脚本

获取指定源码后，你可以利用内部提供的交叉编译辅助脚本进行一键构建。在正式编译前，请确保系统中已经配置好支持 RVV 的 Clang/GCC 工具链。

~~~ bash
# <OPENBLAS_SRC_DIR> 代表 OpenBLAS 源码包根目录
cd <OPENBLAS_SRC_DIR>

# 将交叉编译工具链的 bin 目录加入 PATH
export PATH=/path/to/spacemit-toolchain-linux-glibc-x86_64-v1.x.x/bin:$PATH

# 执行一键式构建脚本
./scripts/build_riscv64.sh
~~~

该自动化脚本 `build_riscv64.sh` 涵盖以下核心流程：
1. 清理已有缓存避免编译串扰（`make clean`）；
2. 传递关键参数 `TARGET=x100` 以激活进迭时空微架构层面的软硬协同优化引擎；
3. 将指定编译器覆盖为 `riscv64-unknown-linux-gnu-clang` / `gfortran` 进行高效的后端指令拉取；
4. 构建并执行 `make install`，同时将附带的 `benchmark` 性能工具集一并交叉编译完成。

编译成功后，完整的库文件及头文件将被安装至默认的 `OpenBLAS/install` 或相关产物目录中。


### SLEEF 源码构建

如需通过源码构建面向 SpacemiT 平台的 SLEEF 库，建议获取官方或进迭时空维护的带有 RISC-V 深度适配脚本的特定分支。

获取源码后，首先进入源码顶层目录：

~~~ bash
# <SLEEF_SRC_DIR> 代表 SLEEF 源码包根目录
cd <SLEEF_SRC_DIR>
~~~

针对 RISC-V 交叉编译环境，项目中提供了成熟的构建封装脚本（如 `scripts/build_riscv64_gcc.sh`），该脚本将自主处理 QEMU 辅助配置与依赖项组装。其内置化流程涵盖：

1. 在 Host 主机侧先构建 Native 宿主版本，生成供交叉汇编阶段依赖的基础工具及中间产物；
2. 自动下载、准备并交叉编译第三方 FFTW 完整包，为后续 SLEEF DFT 相关的库和测例提供对齐依赖；
3. 调用指定的 RISC-V GCC 平台级工具链执行正式的 SLEEF 交叉编译；
4. 隐式开启 `SLEEF_ENABLE_RVVM1=ON` 与 `SLEEF_ENABLE_RVVM2=ON` 参数，释放 RISC-V 平台的 RVV 向量化极致性能；
5. 将全部生成物归档至源码目录下的 `build-riscv64/` 以备后续装机使用，或支持通过指定参数修改整体安装前缀（Install Prefix）。

#### 使用脚本构建

启动自动化构建前，请自行确保已配置好 RISC-V 的完整环境（包含 Toolchain 工具链、Sysroot 以及辅助执行的 QEMU），并通过环境变量进行指引：

~~~ bash
cd <SLEEF_SRC_DIR>

export TOOLCHAIN_ROOT=/path/to/spacemit-toolchain-linux-glibc-x86_64-v1.x.x
export QEMU_ROOT_PATH=/path/to/qemu

# (可选) 若使用的交叉工具链前缀存在变更（默认为 riscv64-unknown-linux-gnu），可手工覆盖
export RISCV_TUPLE=riscv64-unknown-linux-gnu

./scripts/build_riscv64_gcc.sh
~~~

上述预检查脚本会自动判定：
- `${TOOLCHAIN_ROOT}` 及下辖的 `sysroot` 是否存在且健康；
- `${QEMU_ROOT_PATH}/bin/qemu-riscv64` 二进制包是否具备可执行权限；
- FFTW 第三方原始依赖包是否存在（若无，则即停并静默拉取 `fftw-3.3.10.tar.gz` 至本地补齐）。

构建完成后，在 `<SLEEF_SRC_DIR>` 或上一级目录下可找到类似如下的产物位置：

~~~ text
build-native/
build-riscv64/
install/
~~~

其中 `build-riscv64/bin/` 通常包含 RISC-V 测试程序或辅助程序，`install/` 用作后续上层工程引用的安装目录。

#### 轻量构建建议

如果只需要为上层项目提供 `libsleef`，而不需要 DFT、QUAD 和完整测试，可在工程验证稳定后准备一套轻量配置，减少第三方依赖和构建时间。典型配置思路如下：

~~~ bash
cd <SLEEF_SRC_DIR>

cmake -S . \
  -B build-riscv64-lite \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=../install-lite \
  -DCMAKE_SYSTEM_NAME=Linux \
  -DCMAKE_SYSTEM_PROCESSOR=riscv64 \
  -DCMAKE_SYSROOT=${TOOLCHAIN_ROOT}/sysroot \
  -DCMAKE_C_COMPILER=${TOOLCHAIN_ROOT}/bin/${RISCV_TUPLE}-gcc \
  -DCMAKE_CXX_COMPILER=${TOOLCHAIN_ROOT}/bin/${RISCV_TUPLE}-g++ \
  -DSLEEF_SHOW_CONFIG=ON \
  -DSLEEF_BUILD_LIBM=ON \
  -DSLEEF_BUILD_DFT=OFF \
  -DSLEEF_BUILD_QUAD=OFF \
  -DSLEEF_BUILD_TESTS=OFF \
  -DSLEEF_ENABLE_TESTER=OFF \
  -DSLEEF_ENABLE_TESTER4=OFF \
  -DSLEEF_ENABLE_RVVM1=ON \
  -DSLEEF_ENABLE_RVVM2=ON

cmake --build build-riscv64-lite -j$(nproc)
cmake --install build-riscv64-lite
~~~

轻量构建适合业务集成和交付验证；完整脚本构建适合库开发、功能覆盖验证和后续性能调优。若需要发布给其他工程使用，建议以 `install/` 或 `install-lite/` 作为统一的 `SLEEF_DIR`。

#### RISC-V 支持说明

SLEEF 当前在上游文档中将 RISC-V RVVM1/RVVM2 标记为未维护特性，因此工程使用时建议遵循以下原则：

- 每次切换编译器、sysroot 或目标板镜像后，都重新运行最小 Demo 与关键业务用例；
- 开启 `SLEEF_SHOW_CONFIG=ON`，确认 CMake 配置阶段确实识别并启用了期望的 RISC-V 选项；
- 对关键数学函数保留与系统 `libm` 或高精度参考实现的误差对比；
- 对性能收益保持按函数、按数据规模记录，不将某个函数的收益泛化到所有数学函数。

### 项目集成

数学库通常通过 CMake、Makefile 或手写编译命令集成到业务工程中。为了降低迁移成本，建议将 OpenBLAS 和 SLEEF 以独立变量的方式配置，避免在源码中硬编码绝对路径。

#### CMake 集成示例

~~~ cmake
set(MATH_LIB_DIR "/path/to/riscv64-math-libs" CACHE PATH "RISC-V math libraries")

target_include_directories(demo PRIVATE
  ${MATH_LIB_DIR}/include
)

target_link_directories(demo PRIVATE
  ${MATH_LIB_DIR}/lib
)

target_link_libraries(demo PRIVATE
  openblas
  sleef
  m
)
~~~

如果项目使用交叉编译工具链，建议在 toolchain file 或构建脚本中统一设置 `CMAKE_SYSROOT`、编译器路径和库搜索路径，而不是在多个子模块中重复配置。

### OpenBLAS Demo

下面的示例演示了如何调用 OpenBLAS 完成一个最小矩阵乘：

- C

~~~ c
#include <cblas.h>
#include <stdio.h>

int main() {
  const int m = 2;
  const int n = 2;
  const int k = 2;

  float a[4] = {1, 2, 3, 4};
  float b[4] = {5, 6, 7, 8};
  float c[4] = {0, 0, 0, 0};

  cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
              m, n, k, 1.0f, a, k, b, n, 0.0f, c, n);

  printf("C = [%f, %f, %f, %f]\n", c[0], c[1], c[2], c[3]);
  return 0;
}
~~~

- Shell

~~~ bash
export OPENBLAS_DIR=/path/to/openblas-riscv64
export LD_LIBRARY_PATH=${OPENBLAS_DIR}/lib:${LD_LIBRARY_PATH}

gcc demo_openblas.c -o demo_openblas \
  -I${OPENBLAS_DIR}/include \
  -L${OPENBLAS_DIR}/lib \
  -lopenblas

./demo_openblas
~~~

期望输出为：

~~~ text
C = [19.000000, 22.000000, 43.000000, 50.000000]
~~~

在实际项目中，OpenBLAS 更常用于较大规模的矩阵乘、向量运算或线性代数例程。对于性能测试场景，建议固定输入规模、线程数和运行环境，并区分冷启动与稳定运行后的耗时。

常用线程配置示例如下：

~~~ bash
# 单线程测试，便于观察单核计算效率
export OPENBLAS_NUM_THREADS=1

# 多线程测试，便于观察整体吞吐能力
export OPENBLAS_NUM_THREADS=4
~~~

### SLEEF Demo

下面的示例演示了如何调用 SLEEF 数学函数库：

- C

~~~ c
#include <stdio.h>
#include <sleef.h>

int main() {
  double x = 0.5;
  double s = Sleef_sind1_u10(x);
  double c = Sleef_cosd1_u10(x);

  printf("sin(%f) = %f\n", x, s);
  printf("cos(%f) = %f\n", x, c);
  return 0;
}
~~~

- Shell

~~~ bash
export SLEEF_DIR=/path/to/sleef-riscv64
export LD_LIBRARY_PATH=${SLEEF_DIR}/lib:${LD_LIBRARY_PATH}

gcc demo_sleef.c -o demo_sleef \
  -I${SLEEF_DIR}/include \
  -L${SLEEF_DIR}/lib \
  -lsleef

./demo_sleef
~~~

如果使用本地源码构建产物，可将 `SLEEF_DIR` 指向安装目录：

~~~ bash
# <INSTALL_DIR> 替换为实际的安装路径，例如 <SLEEF_SRC_DIR>/install
export SLEEF_DIR=<INSTALL_DIR>
export LD_LIBRARY_PATH=${SLEEF_DIR}/lib:${LD_LIBRARY_PATH}
~~~

输出结果会随浮点格式显示略有差异，通常可看到 `sin(0.5)` 和 `cos(0.5)` 的计算结果。

如果上层程序同时依赖 OpenBLAS 与 SLEEF，建议统一收敛到同一套 RISC-V 工具链和 sysroot，以避免 ABI 或运行时库不一致问题。

### 性能验证建议

数学库性能受输入规模、数据布局、线程数、CPU 频率、缓存状态和编译选项影响明显。进行性能对比时，建议遵循以下原则：

- **固定环境**：记录开发板型号、CPU 核型、频率策略、线程数和系统版本。
- **固定输入**：矩阵维度、数据类型、转置参数和 batch 方式保持一致。
- **区分接口开销**：小规模输入容易被函数调用和调度开销主导，应同时测试中大规模输入。
- **多次采样**：剔除首轮冷启动影响，使用多轮 `median` 或 `min` 作为稳定指标。
- **验证正确性**：性能测试前后均应检查输出结果，避免仅统计了错误路径或空计算路径。

以进迭时空 K3 平台（X100 核心）为例，典型的计算基准实测数据可作为性能验收与环境就绪的参考：

#### 1. OpenBLAS SGEMM 性能基准（单核）

利用 OpenBLAS 源码自带的 `benchmark/sgemm.goto` 可评估单精度矩阵乘法（SGEMM）性能。在绑定单核运行大型矩阵时，RVV 加速下的浮点吞吐可稳定在 ~32.7 GFLOPS。

测试命令示例：

~~~ bash
export OPENBLAS_NUM_THREADS=1
# 参数分别为 M N K，此处以 5120x5120x5120 规模为例
taskset -c 0 ./sgemm.goto 5120 5120 5120
~~~

期望输出参考：

~~~ text
From : 5120  To : 5120 Step=5120 : Transa=N : Transb=N
          SIZE                   Flops             Time
 M=5120, N=5120, K=5120 :    32715.45 MFlops   8.205158 sec
~~~

#### 2. SLEEF 离散傅里叶变换性能基准（单核）

利用 SLEEF 内置的 `dftbenchdp` 可评估双精度二维 FFT（1024×1024）性能。开启 RVV 向量化加速后，SleefDFT 单核性能可达 ~6.27 GFLOPS，对比同等条件下主流的标量实现（如 FFTW 约 2.44 GFLOPS）具备显著性能优势。

测试命令示例：

~~~ bash
# 参数解析: log2(1024)=10, log2(1024)=10, 评测时长 1000ms, 迭代 10 次
taskset -c 0 ./dftbenchdp 10 10 1000 10
~~~

期望输出参考（截取）：

~~~ text
DP n = 2^10 = 1024, m = 2^10 = 1024, nr = 0
...
SleefDFT ST niter = 12
6277.58 Mflops
...
FFTW ST niter = 5
2445.73 Mflops
~~~

说明：对于其他基础数学函数（如连续数组上的 `sin`、`cos`、`exp` 等），建议直接依托上层框架（如 ONNXRuntime、OpenCV 等）提供的 Benchmark 工具进行端到端测算，以更真实地反映业务实际收益。

### 当前支持状态

当前进迭时空 RISC-V 平台上的数学库支持状态如下：

| 支持指标 | OpenBLAS | SLEEF |
| -------- | -------- | ----- |
| 目标架构 | `riscv64` | `riscv64` |
| 典型接口 | BLAS/LAPACK、CBLAS | 标量/向量数学函数 |
| 主要用途 | 矩阵乘、向量运算、线性代数 | `sin`、`cos`、`exp`、`log` 等数学函数 |
| 推荐集成方式 | 预编译包或随上层工程交叉编译 | 预编译包或随上层工程交叉编译 |
| 上层协同 | ONNXRuntime、OpenCV、数值计算程序 | OpenCV、推理前后处理、自定义算子 |
| 部署方式 | 动态库或静态库 | 动态库或静态库 |

总体而言，OpenBLAS 更适宜充当矩阵与复杂线性代数计算的坚实底座，而 SLEEF 更专注于提升逐元素的数学函数及通用向量化场景的吞吐极限。在工程落地时，二者可基于应用的核心性能瓶颈独立选用，亦可联合作为全栈 AI 解决方案中不可或缺的补充环节。
