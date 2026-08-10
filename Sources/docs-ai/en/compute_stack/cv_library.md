---
sidebar_position: 3
---

# Computer Vision Library

> **OpenCV** is a core component of the SpacemiT RISC-V AI software stack. It handles image processing, traditional algorithm development, and AI pre/post-processing pipelines, providing a general-purpose vision foundation for building complete vision applications on RISC-V platforms.

---

- [Computer Vision Library](#computer-vision-library)
    - [Overview](#overview)
    - [Integration with the AI Stack](#integration-with-the-ai-stack)
    - [Project Integration](#project-integration)
    - [Building Locally](#building-locally)
      - [1. Deployment-Optimized Build](#1-deployment-optimized-build)
      - [2. RVV Comparison Build](#2-rvv-comparison-build)
    - [RVV Performance Gains](#rvv-performance-gains)
    - [Image Processing Demo](#image-processing-demo)
    - [Current Support Status](#current-support-status)

### Overview

OpenCV is one of the most widely adopted open-source computer vision libraries, covering image processing, matrix operations, geometric transformations, feature extraction, and general vision application development. Within the SpacemiT software stack, OpenCV serves as the bridge between vision data processing and algorithm components. It can be used standalone for traditional vision applications or as the pre/post-processing layer in an AI inference pipeline.

Typical use cases include:

- Image I/O and color space conversion
- Image preprocessing: filtering, thresholding, morphological operations, geometric transforms
- Low-level operator calls: matrix arithmetic, statistical reductions, channel splitting
- Pre/post-processing pipelines for AI detection, segmentation, and classification models
- Prototyping and platform validation of traditional vision algorithms such as calibration and stitching

### Integration with the AI Stack

Within the SpacemiT AI software stack, OpenCV connects the application layer to the compute acceleration layer:

- **Application side**: Provides stable image operations as a standard vision component for intelligent robots and edge camera devices.
- **Inference integration**: Works seamlessly alongside inference frameworks such as [SpacemiT-ONNXRuntime](./ai_compute_stack/onnxruntime.md) to handle preprocessing (color space conversion, resize, normalization) and postprocessing (bounding box drawing, annotation rendering).
- **Operator acceleration**: Through deep RISC-V RVV integration, `OpenCV HAL` calls are lowered to native vector instructions, delivering higher on-device execution efficiency for vision workloads.

This integration model allows most open-source and general-purpose algorithm projects to bring OpenCV and other AI acceleration components onto the SpacemiT RISC-V platform with minimal code changes, forming a complete end-to-end solution.

### Project Integration

> &#x2139;&#xfe0f; On the SpacemiT RISC-V platform, OpenCV is currently integrated primarily via source-based cross-compilation.

The recommended approach is to build from the standard OpenCV source tree using the SpacemiT RISC-V cross-compilation toolchain. Because OpenCV's API behavior is identical across architectures, existing OpenCV-based projects can be migrated to the RISC-V platform without code changes, reusing mature image processing logic as-is.

Common integration paths:

- **Embedded vision component**: Package OpenCV as the standard component for image decoding, resize/crop, color conversion, and result rendering alongside an inference framework such as SpacemiT-ONNXRuntime.
- **Standalone vision compute**: Port existing traditional vision algorithms built on OpenCV `imgproc` and `core` — such as industrial defect inspection or edge feature extraction — directly to K1/K3 development boards.

### Building Locally

On the SpacemiT RISC-V platform, OpenCV is integrated and validated primarily through cross-compilation. There are two build configurations depending on the goal:

- **Deployment-optimized build**: Targets production delivery or engineering integration. The goal is a stable, reusable vision processing library on the verified RISC-V CPU + RVV path.
- **RVV comparison build**: Targets performance evaluation or operator tuning. The goal is to measure the acceleration effect of RVV on individual vision operators by comparing two builds side by side.

#### 1. Deployment-Optimized Build

For general-purpose vision use cases, the recommended approach is a Release static build with RVV enabled by default, using the RISC-V GCC toolchain, the matching sysroot, and OpenCV's bundled `riscv64-gcc.toolchain.cmake`.

A typical build flow:

```bash
export RISCV_TOOLCHAIN_ROOT=/path/to/spacemit-toolchain-linux-glibc-x86_64-v1.0.9

rm -rf build
mkdir -p build
cd build

cmake .. \
  -DCMAKE_C_COMPILER=${RISCV_TOOLCHAIN_ROOT}/bin/riscv64-unknown-linux-gnu-gcc \
  -DCMAKE_CXX_COMPILER=${RISCV_TOOLCHAIN_ROOT}/bin/riscv64-unknown-linux-gnu-g++ \
  -DCMAKE_TOOLCHAIN_FILE=../platforms/linux/riscv64-gcc.toolchain.cmake \
  -DRISCV_SYSROOT=${RISCV_TOOLCHAIN_ROOT}/sysroot \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_SHARED_LIBS=OFF \
  -DCMAKE_EXE_LINKER_FLAGS="-static" \
  -DWITH_OPENCL=OFF \
  -DWITH_PTHREADS_PF=OFF \
  -DWITH_OPENMP=OFF \
  -DBUILD_opencv_calib3d=ON \
  -DBUILD_ZLIB=ON \
  -DBUILD_PNG=ON \
  -DCMAKE_BUILD_WITH_INSTALL_RPATH=1 \
  -DCMAKE_INSTALL_PREFIX=./install \
  -DCPU_BASELINE=RVV \
  -DCPU_BASELINE_REQUIRE=RVV \
  -DRISCV_RVV_SCALABLE=ON

make clean
make -j4
```

The key points of this deployment-optimized build are:

- `Release + static link` ensures the output is easy to deploy and runs reliably.
- `CPU_BASELINE=RVV` and `RISCV_RVV_SCALABLE=ON` enable RVV vector optimization on the SpacemiT platform.
- OpenCL, OpenMP, and other parallel/heterogeneous backends are disabled to reduce build complexity and keep the focus on the core vision processing path.

The term "optimized" here refers specifically to tuning for the primary CPU + RVV execution path, not enabling all available parallel backends simultaneously. This build prioritizes deployment stability, path convergence, and reuse of verified capabilities.

#### 2. RVV Comparison Build

When the goal is to measure the optimization gain of specific operators on SpacemiT hardware, two parallel builds are needed: a baseline with RVV disabled and an optimized build with RVV enabled. The only difference between the two is the RVV-related CMake flags.

The example below shares the same toolchain, build type, and module configuration across both builds, varying only the RVV switches:

```bash
export RISCV_TOOLCHAIN_ROOT=/path/to/spacemit-toolchain-linux-glibc-x86_64-v1.0.9

COMMON_CMAKE_ARGS=(
  -DCMAKE_C_COMPILER=${RISCV_TOOLCHAIN_ROOT}/bin/riscv64-unknown-linux-gnu-gcc
  -DCMAKE_CXX_COMPILER=${RISCV_TOOLCHAIN_ROOT}/bin/riscv64-unknown-linux-gnu-g++
  -DCMAKE_TOOLCHAIN_FILE=../platforms/linux/riscv64-gcc.toolchain.cmake
  -DRISCV_SYSROOT=${RISCV_TOOLCHAIN_ROOT}/sysroot
  -DCMAKE_BUILD_TYPE=Release
  -DBUILD_SHARED_LIBS=OFF
  -DCMAKE_EXE_LINKER_FLAGS=-static
  -DWITH_OPENCL=OFF
  -DWITH_PTHREADS_PF=OFF
  -DWITH_OPENMP=OFF
  -DBUILD_opencv_calib3d=ON
  -DBUILD_ZLIB=ON
  -DBUILD_PNG=ON
  -DCMAKE_BUILD_WITH_INSTALL_RPATH=1
  -DCMAKE_INSTALL_PREFIX=./install
)

# 1) Build the baseline variant with RVV disabled
rm -rf build_rvv_baseline
mkdir -p build_rvv_baseline
cd build_rvv_baseline

cmake .. "${COMMON_CMAKE_ARGS[@]}" \
  -DCPU_BASELINE= \
  -DCPU_BASELINE_REQUIRE= \
  -DRISCV_RVV_SCALABLE=OFF \
  -DENABLE_RVV=OFF \
  -DWITH_HAL_RVV=OFF

make clean
make -j4
cd ..

# 2) Build the optimized variant with RVV enabled
rm -rf build_rvv_optimized
mkdir -p build_rvv_optimized
cd build_rvv_optimized

cmake .. "${COMMON_CMAKE_ARGS[@]}" \
  -DCPU_BASELINE=RVV \
  -DCPU_BASELINE_REQUIRE=RVV \
  -DRISCV_RVV_SCALABLE=ON \
  -DWITH_HAL_RVV=ON

make clean
make -j4
cd ..
```

The core configuration differences between the two builds:

| CMake flag | Baseline | RVV-optimized |
| ---------------------- | -------- | --------------- |
| `CPU_BASELINE` | (empty) | `RVV` |
| `CPU_BASELINE_REQUIRE` | (empty) | `RVV` |
| `RISCV_RVV_SCALABLE` | `OFF` | `ON` |
| `ENABLE_RVV` | `OFF` | Enabled by RVV config |
| `WITH_HAL_RVV` | `OFF` | `ON` |
| Target ISA | `rv64gc` | `rv64gcv` |

### RVV Performance Gains

After building both the baseline and optimized variants using the comparison setup above, the performance testing tools produced by the OpenCV build — `opencv_perf_core` and `opencv_perf_imgproc` — can be run directly on the target board to quantify RVV acceleration. The results below are from a K3 X100 processor. Median latency was compared across both builds (speedup = RVV OFF / RVV ON), showing consistent performance improvements across high-frequency operators.

Geometric mean speedup for representative operators:

| Operator | Geometric mean speedup |
| -------------------- | -------------: |
| `imgproc::threshold` | 9.82x |
| `core::norm` | 4.73x |
| `core::split` | 1.82x |

RVV delivers measurable gains across threshold, reduction, and channel-processing operators, with `threshold` and `norm` showing the most significant improvements.

### Image Processing Demo

After cross-compiling OpenCV and preparing the corresponding headers and libraries, the following minimal example can be used to verify that the basic image processing pipeline works correctly. It covers image loading, resizing, and grayscale conversion — three steps that map directly to typical inference preprocessing.

```cpp
#include <iostream>
#include <opencv2/opencv.hpp>

int main() {
  cv::Mat image = cv::imread("test.jpg");
  if (image.empty()) {
    std::cerr << "failed to load image" << std::endl;
    return 1;
  }

  cv::Mat resized;
  cv::resize(image, resized, cv::Size(224, 224));

  cv::Mat gray;
  cv::cvtColor(resized, gray, cv::COLOR_BGR2GRAY);

  std::cout << "processed image size: " << gray.cols << "x" << gray.rows << std::endl;
  return 0;
}
```

Compile and run instructions are as follows:

```bash
export OPENCV_DIR=/path/to/opencv
export LD_LIBRARY_PATH=${OPENCV_DIR}/lib:${LD_LIBRARY_PATH}

g++ demo_opencv.cpp -o demo_opencv \
  -I${OPENCV_DIR}/include/opencv4 \
  -L${OPENCV_DIR}/lib \
  -lopencv_core -lopencv_imgcodecs -lopencv_imgproc

./demo_opencv
```

In real-world projects, this processing stage is usually performed before model inference to resize input images, convert color spaces, and organize data. It can also occur after inference to draw results, apply thresholding, and generate visualization output.

### Current Support Status

Full cross-compilation of OpenCV for SpacemiT RISC-V hardware has been completed, with RVV optimization coverage across a large set of core operators. The focus is on the `core` and `imgproc` modules, which are the most frequently called. This means preprocessing and feature computation involving heavy parallel operations can fully leverage the platform's vectorization capabilities.

| Indicator | Status |
| ------------- | ------------------------------------- |
| Target architecture | `riscv64` |
| Toolchain | `riscv64-unknown-linux-gnu-gcc/g++` |
| Build type | `Release` |
| Linking | Static |
| Validated modules | `core`, `imgproc` perf test suites |
| Platform validation | K1 X60, K3 X100 |
| Vector baseline | Enabled via `CPU_BASELINE=RVV` |
| Compute HAL | Full pipeline with `WITH_HAL_RVV=ON` |

> Documentation and data on this page are based on the OpenCV `4.12.0-dev` branch. When working within the SpacemiT hardware and software ecosystem, the recommended starting point is the `rv64gcv` build environment to maximize compute throughput. The source-based build also leaves the door open for extending coverage to additional higher-level modules at any time.
