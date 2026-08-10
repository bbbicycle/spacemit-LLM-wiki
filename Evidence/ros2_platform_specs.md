---
type: evidence
title: "SpacemiT ROS 2 平台支持与底层硬件接口规格"
status: needs_review
created: 2026-08-10
updated: 2026-08-10
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

## 1. ROS 2 版本与 DDS 中间件规格

| 属性名称 | 规格参数与选项 | 推荐应用场景 |
| :--- | :--- | :--- |
| **支持的 ROS 2 版本** | ROS 2 Humble LTS / ROS 2 Jazzy LTS | 工业机器人、教研科研、具身智能应用 |
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

| 节点类型 | CPU 占用率 (8-Core X60) | 内存 (RAM) 占用 | 帧率 / 延迟 |
| :--- | :--- | :--- | :--- |
| **talker / listener 基础节点**| < 1.5% | ~ 18 MB | < 1 ms 延迟 |
| **Camera Publisher (1080p)** | ~ 8.0% (硬解码/MPP) | ~ 65 MB | 30 FPS |
| **2D Laser SLAM (Cartographer)**| ~ 22.0% | ~ 140 MB | 10 Hz 建图 |
| **micro-ROS Agent 串口转发**| < 3.0% | ~ 24 MB | 100 Hz |
