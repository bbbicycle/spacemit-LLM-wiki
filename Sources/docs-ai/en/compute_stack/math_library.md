---
sidebar_position: 4
---

# Additional Math Libraries

> **Additional math libraries** provide foundational numerical capabilities for upper-layer AI frameworks, numerical computing applications, and high-performance operator implementations. On the SpacemiT RISC-V platform, the most commonly used math libraries are OpenBLAS and SLEEF, which cover linear algebra acceleration and vectorized elementary math functions, respectively.

---

- [Additional Math Libraries](#additional-math-libraries)
    - [Overview](#overview)
    - [Getting Resources](#getting-resources)
    - [OpenBLAS Source Build](#openblas-source-build)
      - [Build Script Usage](#build-script-usage)
    - [SLEEF Source Build](#sleef-source-build)
      - [Script-Based Build](#script-based-build)
      - [Lightweight Build Recommendations](#lightweight-build-recommendations)
      - [RISC-V Support Notes](#risc-v-support-notes)
    - [Project Integration](#project-integration)
      - [CMake Integration Example](#cmake-integration-example)
    - [OpenBLAS Demo](#openblas-demo)
    - [SLEEF Demo](#sleef-demo)
    - [Performance Validation Recommendations](#performance-validation-recommendations)
      - [1. OpenBLAS SGEMM Benchmark (Single Core)](#1-openblas-sgemm-benchmark-single-core)
      - [2. SLEEF DFT Benchmark (Single Core)](#2-sleef-dft-benchmark-single-core)
    - [Current Support Status](#current-support-status)

### Overview

Math libraries are foundational components that connect upper-layer frameworks, operator implementations, and underlying hardware in the AI compute stack. For inference frameworks, scientific computing workloads, and image processing pipelines, core capabilities such as matrix multiplication, vector operations, trigonometric functions, exponential functions, and logarithms often determine the execution efficiency of many high-frequency paths.

For the SpacemiT RISC-V platform, the following two math components are the current focus of support and deep optimization:

- **OpenBLAS**: Provides standard BLAS/LAPACK interfaces for matrix multiplication, vector operations, and complex linear algebra routines. It is the underlying backbone for many numerical libraries and higher-level inference frameworks on the platform. Typical optimized interfaces include `cblas_sgemm`, `cblas_dgemm`, `cblas_saxpy`, and `cblas_sdot`.
- **SLEEF**: Provides high-performance, high-precision SIMD math functions, with acceleration for scalar and vectorized computations such as `sin`, `cos`, `exp`, `log`, and `sqrt`. In practice, SLEEF is often used as a complement to the standard `libm` or as the preferred backend for vectorized math workloads.

By adapting these components at the architectural level to the RISC-V Vector Extension (RVV), they provide out-of-the-box computational interfaces and a competitive performance baseline for inference frameworks, vision pipelines, and custom operator development.

### Getting Resources

> This section should be updated with specific release links or distribution channels for OpenBLAS and SLEEF.

### OpenBLAS Source Build

For users who want to leverage the latest RVV acceleration features or maximize matrix multiplication performance on the SpacemiT platform, use a customized OpenBLAS branch and build from source.

#### Build Script Usage

After acquiring the appropriate source tree, use the provided cross-compilation helper script for a one-step build. Before starting, ensure that an RVV-capable Clang/GCC toolchain is properly configured on the host.

~~~ bash
# <OPENBLAS_SRC_DIR> is the root directory of the OpenBLAS source tree
cd <OPENBLAS_SRC_DIR>

# Add the cross-compilation toolchain bin directory to PATH
export PATH=/path/to/spacemit-toolchain-linux-glibc-x86_64-v1.x.x/bin:$PATH

# Run the build helper script
./scripts/build_riscv64.sh
~~~

The `build_riscv64.sh` automation script covers the following core steps:

1. Clean existing build artifacts to avoid cross-build interference (`make clean`).
2. Pass the key parameter `TARGET=x100` to activate the platform-specific microarchitecture optimizations for SpacemiT hardware.
3. Override the compiler selection to `riscv64-unknown-linux-gnu-clang` / `gfortran` for efficient backend code generation.
4. Run `make install` to build the library and cross-compile the bundled `benchmark` tools.

After a successful build, the full library and header outputs are installed under the default `OpenBLAS/install` or the corresponding output directory.

### SLEEF Source Build

To build a SLEEF library optimized for the SpacemiT platform, use an official or SpacemiT-maintained branch that includes RISC-V adaptation scripts.

After obtaining the source tree, start from the repository root:

~~~ bash
# <SLEEF_SRC_DIR> is the root directory of the SLEEF source tree
cd <SLEEF_SRC_DIR>
~~~

For RISC-V cross-compilation, the project provides a mature wrapper script such as `scripts/build_riscv64_gcc.sh`. This script handles QEMU-assisted configuration and dependency assembly automatically. Its workflow typically includes:

1. Building a native host version first to generate the auxiliary tools and intermediate artifacts required for the cross-compilation stage.
2. Downloading, preparing, and cross-compiling the third-party FFTW package for SLEEF DFT-related libraries and tests.
3. Invoking the specified RISC-V GCC toolchain to perform the actual SLEEF cross-compilation.
4. Enabling `SLEEF_ENABLE_RVVM1=ON` and `SLEEF_ENABLE_RVVM2=ON` to unlock the RVV vectorization performance on the RISC-V platform.
5. Archiving all generated artifacts under `build-riscv64/` for later deployment or allowing the install prefix to be modified via script parameters.

#### Script-Based Build

Before running the automated build, ensure the full RISC-V environment is configured, including the toolchain, sysroot, and the QEMU binaries needed for target execution. Set the environment variables as follows:

~~~ bash
cd <SLEEF_SRC_DIR>

export TOOLCHAIN_ROOT=/path/to/spacemit-toolchain-linux-glibc-x86_64-v1.x.x
export QEMU_ROOT_PATH=/path/to/qemu

# Optional: override the cross-toolchain prefix if it differs from riscv64-unknown-linux-gnu
export RISCV_TUPLE=riscv64-unknown-linux-gnu

./scripts/build_riscv64_gcc.sh
~~~

The preflight script automatically verifies:

- that `${TOOLCHAIN_ROOT}` and its `sysroot` exist and are healthy;
- that `${QEMU_ROOT_PATH}/bin/qemu-riscv64` is executable;
- whether the FFTW dependency archive is present, and if not, it will download `fftw-3.3.10.tar.gz` locally.

When the build completes, output directories appear as follows:

~~~ text
build-native/
build-riscv64/
install/
~~~

The `build-riscv64/bin/` directory typically contains RISC-V test binaries and auxiliary programs, while `install/` serves as the installation root for upper-layer projects.

#### Lightweight Build Recommendations

If the goal is only to provide `libsleef` for downstream projects, and you do not need DFT, QUAD, or the full test suite, use a lightweight configuration to reduce dependencies and build time. A typical lightweight setup looks like this:

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

The lightweight build is suitable for integration and validation, while the full scripted build is better for library development, functional coverage verification, and performance tuning. For reuse by other projects, use `install/` or `install-lite/` as the unified `SLEEF_DIR`.

#### RISC-V Support Notes

Upstream SLEEF currently marks RISC-V RVVM1/RVVM2 as an unsupported or unmaintained feature set, so the following practices are recommended:

- Re-run minimal demos and key business use cases after changing the compiler, sysroot, or target firmware image.
- Enable `SLEEF_SHOW_CONFIG=ON` and verify that CMake recognizes and enables the expected RISC-V options.
- Compare results for critical math functions against the system `libm` or a high-precision reference implementation.
- Record performance gains per function and per data size, and avoid generalizing the benefits from one function to all math routines.

### Project Integration

Math libraries are typically integrated into application projects via CMake, Makefile, or handwritten compiler commands. To reduce migration cost, configure OpenBLAS and SLEEF using standalone variables instead of embedding absolute paths in source code.

#### CMake Integration Example

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

If the project uses a cross-compilation toolchain, set `CMAKE_SYSROOT`, compiler paths, and library search paths centrally in the toolchain file or build script rather than repeating them across multiple submodules.

### OpenBLAS Demo

The following example shows a minimal matrix multiplication using OpenBLAS:

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

Expected output:

~~~ text
C = [19.000000, 22.000000, 43.000000, 50.000000]
~~~

In real projects, OpenBLAS is more commonly used for larger matrix multiplications, vector operations, or linear algebra routines. For performance testing, maintain consistent input size, thread count, and runtime environment, and distinguish between cold startup and steady-state measurements.

Common thread settings are:

~~~ bash
# Single-threaded test for single-core efficiency
export OPENBLAS_NUM_THREADS=1

# Multi-threaded test for overall throughput
export OPENBLAS_NUM_THREADS=4
~~~

### SLEEF Demo

The following example shows how to call SLEEF math functions:

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

If using locally built artifacts, point `SLEEF_DIR` to the install directory:

~~~ bash
# Replace <INSTALL_DIR> with the actual installation path, e.g. <SLEEF_SRC_DIR>/install
export SLEEF_DIR=<INSTALL_DIR>
export LD_LIBRARY_PATH=${SLEEF_DIR}/lib:${LD_LIBRARY_PATH}
~~~

Output formatting may vary slightly depending on floating-point precision, but the computed values for `sin(0.5)` and `cos(0.5)` should be displayed.

If a downstream application depends on both OpenBLAS and SLEEF, use the same RISC-V toolchain and sysroot for both libraries to avoid ABI or runtime mismatches.

### Performance Validation Recommendations

Math library performance is strongly affected by input size, data layout, thread count, CPU frequency, cache state, and compiler options. When comparing performance, follow these guidelines:

- **Fix the environment**: record the board model, CPU configuration, frequency policy, thread count, and system version.
- **Fix the inputs**: use consistent matrix dimensions, data types, transpose flags, and batch patterns.
- **Separate interface overhead**: small inputs can be dominated by call and scheduling overhead; test medium and large inputs as well.
- **Sample multiple runs**: discard the first cold start iteration and use `median` or `min` from subsequent runs as the stable metric.
- **Verify correctness**: check outputs before and after performance testing to ensure measurements are not from incorrect or empty code paths.

On the SpacemiT K3 platform (X100 cores), representative benchmark data can serve as a reference for performance validation and readiness checks.

#### 1. OpenBLAS SGEMM Benchmark (Single Core)

Use the OpenBLAS `benchmark/sgemm.goto` tool to evaluate single-precision matrix multiplication (SGEMM) performance. Single-core throughput with RVV acceleration can stabilize around ~32.7 GFLOPS for large matrices.

Example command:

~~~ bash
export OPENBLAS_NUM_THREADS=1
# Parameters are M N K; this example uses 5120x5120x5120
taskset -c 0 ./sgemm.goto 5120 5120 5120
~~~

Expected output sample:

~~~ text
From : 5120  To : 5120 Step=5120 : Transa=N : Transb=N
          SIZE                   Flops             Time
 M=5120, N=5120, K=5120 :    32715.45 MFlops   8.205158 sec
~~~

#### 2. SLEEF DFT Benchmark (Single Core)

Use the built-in SLEEF `dftbenchdp` utility to evaluate double-precision 2D FFT performance for a 1024×1024 input. With RVV vectorization enabled, SleefDFT single-core performance can reach approximately ~6.27 GFLOPS, compared with roughly 2.44 GFLOPS for a comparable scalar implementation such as FFTW.

Example command:

~~~ bash
# Parameters: log2(1024)=10, log2(1024)=10, duration 1000ms, iterations 10
taskset -c 0 ./dftbenchdp 10 10 1000 10
~~~

Expected output sample:

~~~ text
DP n = 2^10 = 1024, m = 2^10 = 1024, nr = 0
...
SleefDFT ST niter = 12
6277.58 Mflops
...
FFTW ST niter = 5
2445.73 Mflops
~~~

Note: For other elementary math functions such as `sin`, `cos`, and `exp`, use benchmark tools provided by higher-level frameworks such as ONNXRuntime or OpenCV for end-to-end measurements. This approach better reflects real application benefits.

### Current Support Status

The current support status for math libraries on the SpacemiT RISC-V platform is as follows:

| Indicator | OpenBLAS | SLEEF |
| -------- | -------- | ----- |
| Target architecture | `riscv64` | `riscv64` |
| Typical interface | BLAS/LAPACK, CBLAS | scalar/vector math functions |
| Primary use cases | matrix multiplication, vector math, linear algebra | `sin`, `cos`, `exp`, `log` math functions |
| Recommended integration | prebuilt package or cross-build with the application | prebuilt package or cross-build with the application |
| Upper-layer collaboration | ONNXRuntime, OpenCV, numerical computing | OpenCV, inference pre/post-processing, custom operators |
| Deployment mode | shared or static libraries | shared or static libraries |

In general, OpenBLAS is best suited as the foundation for matrix and complex linear algebra computation, while SLEEF focuses on throughput for elementwise math functions and broadly vectorized workloads. In practical engineering deployments, they can be selected independently based on the application's core performance bottleneck, or used together as complementary components in a full-stack AI solution.
