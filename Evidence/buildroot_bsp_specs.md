---
type: evidence
title: "SpacemiT Buildroot BSP SDK 软件栈与编译配置参数规格"
status: needs_review
created: 2026-08-10
updated: 2026-08-10
aliases: [buildroot_bsp_specs, Buildroot SDK Specs, Buildroot Manifest Specs]
domain: bsp_kernel_drivers
target_audience: [BSP 工程师, 系统构建工程师]
---

# SpacemiT Buildroot BSP SDK 软件栈与编译配置参数规格

> [!TIP]
> **💡 工程师导读与排坑焦点**：存放 Buildroot SDK 软件栈组件、Repo 分支映射与 defconfig 矩阵。
> **目标读者**：`BSP 工程师 / 系统构建工程师` | **技术领域**：`bsp_kernel_drivers`

本文档汇总 SpacemiT K1 与 K3 处理器基于 Buildroot 构建的 Linux SDK 核心组件、Repo 版本分支映射、编译依赖环境及预置 `defconfig` 方案规格。

---

## 1. SDK 核心组件架构规格

| 组件名称 | 英文标识 | 源码位置 / 路径 | 核心功能与作用 |
| :--- | :--- | :--- | :--- |
| **监管程序接口** | OpenSBI | `bsp-src/opensbi` | RISC-V M-Mode 机器模式固件，提供 SBI 服务接口 |
| **引导加载程序** | U-Boot | `bsp-src/uboot-2022.10` | 负责硬件初始化、加密校验、设备树加载与内核引导 |
| **Linux 内核** | Linux Kernel | `bsp-src/linux-6.6` (K1) / `bsp-src/linux-6.18` (K3) | 操作系统主内核，包含驱动程序与系统调用 |
| **实时刻固件** | ESOS (RCPU Firmware) | `board/spacemit/k1/target_overlay/lib/firmware/esos.elf` | 实时 CPU 固件，负责底层硬件初始化及 HDMI Audio 中断转发 |
| **GPU DDK** | PowerVR DDK | `package-src/img-gpu-powervr` & `mesa3d` | PowerVR GPU 硬件驱动与 OpenGL ES/Vulkan 图形库 |
| **VPU/JPU 编解码** | VPU/JPU Firmware | `package-src/k1x-vpu-firmware` / `k3x-vpu-firmware` | 视频/JPEG 硬件编解码器 API 及固件 |
| **多媒体平台** | MPP / FFmpeg / GStreamer | `package-src/mpp` | 硬件加速多媒体处理平台与硬解码中间件 |
| **AI 推理引擎** | onnxruntime & ai-support | `package-src/ai-support` | 硬件加速 ONNX 推理框架及端侧 AI 演示程序 |

---

## 2. Repo 版本清单与分支映射表 (Manifest Specs)

### K1 平台版本映射 (Buildroot 2.x)

| SDK 版本 | Manifest 文件 | 推荐远程分支 | 托管平台支持 |
| :--- | :--- | :--- | :--- |
| **v1.0** | `bl-v1.0.y.xml` | `bl-v1.0.y` | Gitee |
| **v2.0** | `bl-v2.0.y.xml` | `bl-v2.0.y` | Gitee |
| **v2.1** | `k1-bl-v2.1.y.xml` | `k1-bl-v2.1.y` | Gitee |
| **v2.2 (推荐)** | `k1-bl-v2.2.y.xml` | `k1-bl-v2.2.y` | GitHub & Gitee |

> [!NOTE]
> GitHub 仅托管 v2.2 及以后的版本；Gitee 上 v2.0 与 v2.1 分支因仓库容量原因，Linux 内核子仓库移至 `linux-6.6-v2.0.y` / `linux-6.6-v2.1.y`。

### K3 平台版本映射 (Buildroot 1.x)

| SDK 版本 | Manifest 文件 | 推荐远程分支 | 托管平台支持 |
| :--- | :--- | :--- | :--- |
| **v1.0 (推荐)** | `k3-br-v1.0.y.xml` | `k3-br-v1.0.y` | GitHub & Gitee |

---

## 3. 预置方案 (defconfig) 规格矩阵

### K1 编译方案矩阵

| 方案名称 (`defconfig`) | 方案索引 | 适用场景与特性描述 |
| :--- | :--- | :--- |
| `spacemit_k1_upstream_defconfig` | `1` | 主线 Linux 内核支持方案（极简通用驱动） |
| `spacemit_k1_minimal_defconfig` | `2` | 极轻量根文件系统方案（快速启动/嵌入式裁剪） |
| `spacemit_k1_plt_defconfig` | `3` | 自动化测试与平台验证方案 |
| `spacemit_k1_rt_defconfig` | `4` | **PREEMPT_RT 硬实时内核** 方案（低延迟控制场景） |
| `spacemit_k1_v2_defconfig` | `5` | **标准完整版图形多媒体 SDK**（带 GPU/VPU/QT5） |

### K3 编译方案矩阵

| 方案名称 (`defconfig`) | 方案索引 | 适用场景与特性描述 |
| :--- | :--- | :--- |
| `spacemit_k3_ci_defconfig` | `1` | CI/CD 持续集成构建方案 |
| `spacemit_k3_defconfig` | `2` | **标准 K3 全功能 SDK 方案** |
| `spacemit_k3_plt_defconfig` | `3` | K3 硬件平台测试验证方案 |
| `spacemit_k3_rt_defconfig` | `4` | **K3 PREEMPT_RT 实时系统方案** |

---

## 4. 宿主机与 Docker 依赖规格

* **推荐宿主机配置**：CPU 12th Gen Intel i5 以上 / 内存 16GB+ / 硬盘 SSD 256GB+。
* **Docker 编译限制**：Buildroot 2.2.7 (K1) 和 1.0 (K3) 起默认推荐在 Docker 容器内部构建，宿主机仅需安装 Docker CE。
* **宿主机直接编译的环境变量**：须在 Shell 环境设置 `export DIRECT_BUILD=1`。
* **软件依赖包 (Ubuntu 20.04/22.04 LTS)**：
  ```bash
  sudo apt-get install git build-essential cpio unzip rsync file bc wget python3 python-is-python3 libncurses5-dev libssl-dev dosfstools mtools u-boot-tools flex bison python3-pip
  sudo pip3 install pyyaml
  ```
