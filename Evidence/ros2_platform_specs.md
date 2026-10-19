---
type: evidence
title: "SpacemiT ROS 2 平台支持与底层硬件接口规格"
status: needs_review
verification_status: unverified
external_use: false
source_file: "Sources/docs-ros/zh/root_overview.md"
source_origin: "https://github.com/spacemit-com/docs-ros"
source_commit: "808d02c1bd11cf0d4376555919bd61c90e38d853"
source_section: "ROS 2：平台支持列表；使用说明"
source_resolution: partial
metric_source_resolution: unresolved
source_checked_at: 2026-10-19
source_note: "已定位官方 K1/K3 Humble、Jazzy 支持矩阵与安装指南，Lyrical 仅为 K3 规划支持；默认 DDS、micro-ROS 速率和 CPU/RAM/延迟实测出处仍未定位。"
source_related_file: "Sources/docs-ros/zh/k3/06-系统与平台/6.6-ROS2/6.6.1-ROS2-INSTALL.md"
source_related_commit: "808d02c1bd11cf0d4376555919bd61c90e38d853"
created: 2026-08-10
updated: 2026-10-19
aliases: [ros2_platform_specs, ROS 2 Platform Specs, SpacemiT ROS2 Specs]
domain: edge_ai_robotics
target_audience: [机器人工程师, ROS 2 开发者]
---

# SpacemiT ROS 2 平台支持与底层硬件接口规格

> [!TIP]
> **💡 工程师导读与排坑焦点**：存放 ROS 2 Humble/Jazzy 发行版、CycloneDDS 优化、micro-ROS 与节点开销。
> **目标读者**：`机器人工程师 / ROS 2 开发者` | **技术领域**：`edge_ai_robotics`

本文档记录 SpacemiT K1 与 K3 处理器平台支持的 ROS 2 发行版、DDS 网络中间件调优、micro-ROS 硬件通信接口及节点资源消耗参数。

---

## 1. 官方 ROS 2 平台与操作系统支持矩阵

根据 `docs-ros@808d02c1bd11cf0d4376555919bd61c90e38d853` 的 [ROS 2 平台支持列表](https://github.com/spacemit-com/docs-ros/blob/808d02c1bd11cf0d4376555919bd61c90e38d853/zh/root_overview.md#ros-2)：

| 芯片型号 | 当前支持的 ROS 2 版本 | 规划支持的 ROS 2 版本 | 当前推荐的操作系统 |
| :---: | :---: | :---: | :---: |
| **K3** | **Humble、Jazzy** | **Lyrical**（计划支持） | **Bianbu 4.x**（4.0.1 起） |
| **K1** | **Humble、Jazzy** | — | **Bianbu 2.3.x** |

“计划支持”尚未作为正式支持版本提供，时间和配套系统以官方后续发布为准。这里的支持指对应 Bianbu 系统上的 RISC-V 适配，需使用平台配套软件源；当前 SDK 示例主要基于 Humble，不同发行版的软件包、驱动和功能范围可能不同。安装分别参见 [K1 指南](https://github.com/spacemit-com/docs-ros/blob/808d02c1bd11cf0d4376555919bd61c90e38d853/zh/k1/06_Robot_development/6.1_OS_Preparation/6.1.2_ROS2_Installation.md)与 [K3 指南](https://github.com/spacemit-com/docs-ros/blob/808d02c1bd11cf0d4376555919bd61c90e38d853/zh/k3/06-系统与平台/6.6-ROS2/6.6.1-ROS2-INSTALL.md)。

> [!NOTE]
> **多机通信规范**：
> 官方明确建议**板端与开发主机使用相同的 ROS 2 发行版**，并配置一致的 DDS 通信中间件与 `ROS_DOMAIN_ID`。ROS 2 上游官方并不保证不同发行版（如 Humble 与 Jazzy）之间的跨版本节点通信兼容性。

### 1.1 DDS 中间件与底层规格（待核验记录）

以下 DDS 配置及第 2 节硬件接口表保留历史适配记录，默认实现、速率和适用板型仍需核对。平台支持矩阵不构成这些参数已核验的依据。

| 属性名称 | 规格参数与选项 | 推荐应用场景 |
| :--- | :--- | :--- |
| **底层 Linux 发行版** | Bianbu Linux / Ubuntu 22.04 & 24.04 LTS | 容器化或原生二进制部署 |
| **默认 RMW 实现** | `rmw_cyclonedds_cpp` / `rmw_fastrtps_cpp` | 多节点低延迟通信 |
| **双 GMAC 网口优化** | 支持 DDS 多播组网与网口绑定 | 传输高分辨率摄像头点云与 RAW 图像数据 |

---

## 2. 硬件控制接口与 micro-ROS 规格

| 控制接口类型 | 硬件总线 / 引脚复用 | 通信速率 / 描述 | 适用于设备 |
| :--- | :--- | :--- | :--- |
| **micro-ROS Agent** | `/dev/ttyS1` / `/dev/ttyS3` | 波特率 115200 ~ 921600 bps | 串行连接 STM32 / ESP32 实时小板 |
| **PWM 电机驱动** | K1/K3 PWM Channels (PWM0~PWM3) | 周期与占空比精准硬件输出 | 伺服舵机 / 无刷电机驱动板 |
| **GPIO 中断触控** | 多功能复用 GPIO 引脚 | 支持上升沿/下降沿硬件中断 | 机器人碰撞开关 / 极限传感器 |
| **CAN 总线控制** | SocketCAN 控制器 | 500 Kbps / 1 Mbps 通信速率 | 工业级关节电机 / 轮毂电机 |

---

## 3. 典型 ROS 2 节点资源开销 (K1 实测)

> [!WARNING]
> 以下历史数值尚未找到测试记录，测试环境与测量方法不明（`metric_source_resolution: unresolved`），不作为已验证的 CPU、RAM 或延迟指标。

| 节点类型 | CPU 占用率 (8-Core X60) | 内存 (RAM) 占用 | 帧率 / 延迟 |
| :--- | :--- | :--- | :--- |
| **talker / listener 基础节点**| < 1.5% | ~ 18 MB | < 1 ms 延迟 |
| **Camera Publisher (1080p)** | ~ 8.0% (硬解码/MPP) | ~ 65 MB | 30 FPS |
| **2D Laser SLAM (Cartographer)**| ~ 22.0% | ~ 140 MB | 10 Hz 建图 |
| **micro-ROS Agent 串口转发**| < 3.0% | ~ 24 MB | 100 Hz |
