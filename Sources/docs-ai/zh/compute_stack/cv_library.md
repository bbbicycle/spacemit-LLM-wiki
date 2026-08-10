---
sidebar_position: 3
---

# 计算机视觉库

> **OpenCV** 是进迭时空 RISC-V AI 软件栈中的重要基础组件，主要承接视觉应用中的图像处理、传统算法开发以及 AI 前后处理流程，为客户在 RISC-V 平台上快速构建完整视觉应用提供通用能力支撑。

---

- [计算机视觉库](#计算机视觉库)
    - [简介](#简介)
    - [与 AI 软件栈协同](#与-ai-软件栈协同)
    - [项目集成](#项目集成)
    - [本地构建](#本地构建)
      - [1. 面向部署的优化构建](#1-面向部署的优化构建)
      - [2. RVV 对比构建](#2-rvv-对比构建)
    - [RVV 性能收益](#rvv-性能收益)
    - [图像处理 Demo](#图像处理-demo)
    - [当前支持状态](#当前支持状态)

### 简介

OpenCV 是业界最具代表性的开源计算机视觉基础库之一，覆盖图像处理、矩阵运算、几何变换、特征提取以及视觉应用开发等常见需求。在进迭时空软件栈中，OpenCV 主要承担视觉数据处理与算法组件衔接的角色，既可独立用于传统视觉应用，也可作为 AI 推理流水线中的前后处理基础库。

常见应用场景包括：

- 图像格式读写与颜色空间转换
- 滤波、阈值、形态学、几何变换等图像预处理
- 矩阵运算、统计归约、通道拆分等底层算子调用
- AI 检测、分割、分类模型的前后处理链路对接
- 传统视觉算法（如标定、拼接）的原型开发与平台验证

### 与 AI 软件栈协同

在进迭时空 AI 整个软件栈中，OpenCV 起到了连通应用层与计算加速层的作用：

- **在应用侧**：基于稳定的图像操作，作为智能机器人、边缘相机设备的标准视觉组件。
- **推理协同**：无缝搭配 [SpacemiT-ONNXRuntime](./ai_compute_stack/onnxruntime.md) 等推理框架，将前处理（颜色域转换、缩放归一化）或后处理（绘制框与标注文本）逻辑高效完成。
- **算子加速层**：借助于 RISC-V RVV 的深度优化集成，将 `OpenCV HAL` 调用转化至底层的自持指令集，为视觉运算带来更高的端侧执行效率。

这种协同模式能够让大部分开源与通用算法项目以极低的修改成本，将 OpenCV 和其他 AI 加速推理组件完整引入进迭时空 RISC-V 开发平台，形成闭环方案。

### 项目集成

> &#x2139;&#xfe0f;当前进迭时空 RISC-V 平台上的 OpenCV 落地以源码集成和交叉编译为主。

通常建议开发者基于标准 OpenCV 源码，配合进迭时空 RISC-V 交叉编译工具链完成平台适配。由于 OpenCV 的 API 行为在不同架构上完全一致，现有基于 OpenCV 的业务工程可以无缝迁移至 RISC-V 平台，复用成熟的图像处理代码。

常见的集成路径如下：

- **基础视觉组件嵌入**：作为图像输入解码、Resize 裁剪、颜色转换和结果绘制的标准组件，与推理框架（如 SpacemiT-ONNXRuntime）打包。
- **独立视觉算力支撑**：将现有基于 OpenCV `imgproc` 和 `core` 的传统视觉算法（如工业缺陷检测、边缘特征提取）直接落地至 K1/K3 开发板。

### 本地构建

当前在进迭时空 RISC-V 平台上，OpenCV 主要通过交叉编译方式进行集成和验证。围绕实际使用目标，构建方式可以分为两类：

- **面向部署的优化构建**：面向业务交付或工程集成，目标是在当前已验证的 RISC-V CPU + RVV 路径上提供稳定、可复用的基础视觉处理能力。
- **RVV 对比构建**：面向性能评估或算子调优，目标是横向观测 RVV 能力开启前后对基础视觉算子的加速效果。

#### 1. 面向部署的优化构建

如果目标是把 OpenCV 作为实际项目中的视觉通用组件使用，推荐采用默认开启 RVV 的方式，使用 RISC-V GCC 工具链、配套 sysroot 以及 OpenCV 自带的 `riscv64-gcc.toolchain.cmake` 完成 Release 静态构建。

一个典型的构建流程如下：

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

从上述流程可以看到，这类面向部署的优化构建重点在于：

- 采用 `Release + static link` 方式以确保产物易于部署和稳定运行；
- 通过 `CPU_BASELINE=RVV` 与 `RISCV_RVV_SCALABLE=ON` 启用进迭时空平台的 RVV 向量优化；
- 关闭 OpenCL、OpenMP 等当前场景下非重点的并行与异构计算选项，降低构建复杂度并聚焦基础视觉处理链路。

这里的“优化”主要指围绕当前主推的 CPU + RVV 执行路径进行裁剪和增强，而不是同时启用所有可选并行后端。因此，这一构建方式更强调部署稳定性、路径收敛与已验证能力的复用。

#### 2. RVV 对比构建

如果关注重点是分析具体算子在进迭时空硬件上的优化收益，则需要并行准备两份构建：一份关闭 RVV 的基线对照组，一份开启 RVV 优化的实验组。对比时重点在于修改 RVV 相关的构建配置。

参考构建示例如下。为了便于对比，两组构建共用同一套工具链、编译类型和基础模块配置，仅调整 RVV 相关开关：

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

# 1) 构建 RVV 关闭的基线版本
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

# 2) 构建 RVV 打开的优化版本
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

两组构建的核心配置差异如下表：

| 配置项                 | 基线版本 | RVV 优化版本    |
| ---------------------- | -------- | --------------- |
| `CPU_BASELINE`         | 空       | `RVV`           |
| `CPU_BASELINE_REQUIRE` | 空       | `RVV`           |
| `RISCV_RVV_SCALABLE`   | `OFF`    | `ON`            |
| `ENABLE_RVV`           | `OFF`    | 由 RVV 配置启用 |
| `WITH_HAL_RVV`         | `OFF`    | `ON`            |
| 编译目标指令集         | `rv64gc` | `rv64gcv`       |

### RVV 性能收益

在依靠上述对比机制分别完成基线版本与优化版本的构建后，可以直接使用 OpenCV 源码编译产出的性能测试工具（如 `opencv_perf_core` 和 `opencv_perf_imgproc`）在目标板端量化评估 RVV 加速收益。以 K3 X100 处理器的测试结果为例，我们对高频使用的基础算子进行了两组产物的 `median` 耗时对比（评估公式为 `speedup = RVV OFF / RVV ON`），可以观察到稳定的性能跃升。

代表性算子的几何平均加速比如下：

| 算子模块             | 几何平均加速比 |
| -------------------- | -------------: |
| `imgproc::threshold` |          9.82x |
| `core::norm`         |          4.73x |
| `core::split`        |          1.82x |

从当前测试结果看，RVV 对阈值、归约和通道处理类基础算子均带来了不同程度的性能提升，其中 `threshold` 和 `norm` 的收益更为明显。

### 图像处理 Demo

在完成 OpenCV 交叉编译并准备好对应头文件与库文件后，可以通过一个极简示例快速验证基础图像处理链路是否工作正常。下面的示例包含图像读取、缩放与灰度转换三个典型步骤，可直接对应推理前的数据整理流程。

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

编译与运行方式如下：

```bash
export OPENCV_DIR=/path/to/opencv
export LD_LIBRARY_PATH=${OPENCV_DIR}/lib:${LD_LIBRARY_PATH}

g++ demo_opencv.cpp -o demo_opencv \
  -I${OPENCV_DIR}/include/opencv4 \
  -L${OPENCV_DIR}/lib \
  -lopencv_core -lopencv_imgcodecs -lopencv_imgproc

./demo_opencv
```

在实际项目中，这类处理流程通常位于模型推理之前，用于完成输入图像的尺寸调整、颜色空间转换和数据整理；也可以位于推理之后，用于结果绘制、阈值过滤和可视化输出。

### 当前支持状态

当前围绕进迭时空 RISC-V 硬件资源，已完成了 OpenCV 的全量交叉编译及 RVV 大批量核心算子优化覆盖，其重心主要在调用频次极高的 `core` 和 `imgproc` 模块。这意味着图像运算中涉及大量并行操作的预处理和特征运算可充分依赖新平台的向量化赋能。

| 支持指标      | 验证与发布状态                        |
| ------------- | ------------------------------------- |
| 目标架构      | `riscv64`                             |
| 工具链        | `riscv64-unknown-linux-gnu-gcc/g++`   |
| 构建类型      | `Release`                             |
| 链接方式      | 静态链接                              |
| 已验证模块    | 基于 `core`、`imgproc` perf 测试套件  |
| 跨平台验证    | K1 X60、K3 X100 计算平台              |
| 基础向量兼容  | 经由 `CPU_BASELINE=RVV` 构建使能      |
| 计算 HAL 支持 | 使用 `WITH_HAL_RVV=ON` 全链路贯通能力 |

> 此处文档与数据基于 OpenCV `4.12.0-dev` 分支验证得出。在结合 SpacemiT 软硬件生态时，我们推荐开发者优先结合 `rv64gcv` 编译环境挖掘算力极限，同时也保留了随时基于源码拓展更多高阶模块的开放可能。
