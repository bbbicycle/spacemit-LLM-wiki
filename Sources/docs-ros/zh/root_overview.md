---
sidebar_position: 1
---

# SpacemiT ROS 2 & 具身智能机器人套件简介

SpacemiT 为 K1 与 K3 处理器平台提供了完整的机器人操作系统（ROS 2）及具身智能（Embodied AI）软件栈，赋能从桌面交互机器人、工业/教研机械臂到移动导航与人形控制的全场景机器人开发。

## 系统架构与支持组件

```
┌─────────────────────────────────────────────────────────┐
│                 具身智能与机器人应用层                     │
│  Reachy Mini   │  LeRobot (SO101)  │  Linksee SLAM/Nav  │
├─────────────────────────────────────────────────────────┤
│                   机器人 SDK & AI 模型                  │
│  ACT / SmolVLA │  RL Policy (MuJoCo)│  SpaceLLM / Vision│
├─────────────────────────────────────────────────────────┤
│                     ROS 2 核心中间件                     │
│  ROS 2 Humble / Jazzy  │  Fast DDS / Cyclone DDS        │
├─────────────────────────────────────────────────────────┤
│                     SpacemiT BSP 硬件层                 │
│  K1 / K3 SoC  │  GPIO/PWM/UART/CAN  │  RCPU (esos.elf)  │
└─────────────────────────────────────────────────────────┘
```

主要功能套件：

- **ROS 2 Humble / Jazzy 运行时**：提供原生编译与 Docker 镜像环境。
- **Reachy Mini 应用套件**：支持双目视觉跟随、语音交互与舞蹈编排。
- **LeRobot 机械臂套件**：支持 SO101 6-DoF 机械臂应用控制、ACT / SmolVLA 模仿学习模型部署。
- **Linksee 移动机器人套件**：基于 MIPI CSI 图像与激光雷达的 2D/3D SLAM 建图与自主导航。
- **RL 具身策略推理引擎**：支持基于 MuJoCo 的强化学习策略模型端侧加速推理。
