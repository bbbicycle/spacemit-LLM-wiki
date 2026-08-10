---
type: evidence
title: "K3 CoM260 机器人开发套件物理规格参数"
claim_type: "parameter"
verification_status: unverified
status: needs_review
external_use: false
source_file: "Sources/docs-product/zh/k3_com260/root_overview.md"
created: 2026-06-30
updated: 2026-06-30
aliases: ["K3 COM260板级核心参数", "K3 COM260 Board Hardware Specs", "k3_com260_specs"]
domain: chip_product_specs
target_audience: [核心板选型工程师, 硬件工程师]
---
# K3 CoM260 机器人开发套件物理规格参数

> [!TIP]
> **💡 工程师导读与排坑焦点**：存放 K3 CoM260 核心板与参考载板金手指引脚及物理规格。
> **目标读者**：`核心板选型工程师 / 硬件工程师` | **技术领域**：`chip_product_specs`

本文件汇总了 K3 CoM260 核心板及其参考载板的硬件规格数据，主要用于服务机器人、自主智能体开发与核心板集成参考。

## 1. 核心模组 (CoM) 参数

| 规格维度 | 详细参数规格 | 说明 / 调试设计 |
| :--- | :--- | :--- |
| **主控芯片** | SpacemiT K3 RISC-V 芯片 | 机器人专用多核异构处理器 |
| **通用 CPU** | 8 核 X100™ 64 位 RISC-V CPU | 2 Clusters x 4 Cores，每个 Cluster 拥有 4MB 共享 L2 缓存，通用计算 130 KDMIPS |
| **智算 NPU** | 8 核 A100™ 64 位 AI 核心 | 融合 60 TOPS AI 算力，每个 Cluster 拥有 1MB L2 共享缓存及 1.5MB 专用 TCM 紧耦合存储 |
| **图形 GPU** | 集成 3D-GPU | 支持 Vulkan、OpenCL、OpenGL ES，满足机器人图形化界面或视觉渲染 |
| **内存 (DRAM)** | 64-bit LPDDR5，6400 MT/s | 可选 8GB / 16GB / 32GB 容量，统一内存架构，支持 30B 大模型推理 |
| **视频编码** | 4K @ 60Hz (H.264 / H.265) | 满足机器人多路高清行车记录与推流 |
| **视频解码** | 4K @ 120Hz (单路) 或 1080p @ 60Hz (8路) | 支持多路摄像头并发画面的实时解码与视觉处理 |
| **典型功耗** | 18W ~ 35W | 视算力负载动态调压与变频 |
| **安全方案** | 基于 HW-RoT 的可信引导，PMP/IOPMP 隔离 | 支持 OP-TEE 安全可信操作系统，集成硬件加解密引擎（AES/SM4/RSA等） |

## 2. 参考载板 (Carrier Board) 外设接口

| 接口类别 | 详细物理接口规格 | 说明 / 调试设计 |
| :--- | :--- | :--- |
| **摄像头接口** | 2 × MIPI CSI-1.1 连接器 (22-Pin) | 支持多路差分摄像头视频信号接入 |
| **PCIe 扩展槽** | 1 × M.2 M-Key (PCIe Gen3 x4)<br>1 × M.2 M-Key (PCIe Gen3 x1)<br>1 × M.2 E-Key | 用于扩展 NVMe SSD（最高带宽达 4GB/s）及 Wi-Fi/BT 无线网卡 |
| **USB 接口** | 4 × USB 3.0 Type-A Host<br>1 × USB Type-C | 用于连接深度相机、激光雷达等外部机器人传感器 |
| **以太网接口** | 1 × 千兆以太网 (RJ45) | 提供稳定的有线网络连接 |
| **显示接口** | 1 × DP 1.2<br>1 × MIPI DSI-1.2 连接器 (30-Pin) | 支持多路双屏异显 |
| **其他 I/O 排针** | 40-Pin 扩展接口 | 兼容主流开发套件引脚，支持 UART、SPI、I2S、I2C、GPIO 调试 |
| **机械尺寸** | 103 mm x 90.5 mm x 35 mm | 包含底座脚垫、载板、核心模组及散热器整机尺寸 |
