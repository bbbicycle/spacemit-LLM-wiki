---
type: evidence
title: "SpacemiT 机器人硬件与具身 AI 模型参数规格"
status: needs_review
verification_status: unverified
external_use: false
source_file: "Sources/docs-ros/zh/k3/03-参考方案/3.1-桌面机器人Reachy-mini.md"
source_origin: "https://github.com/spacemit-com/docs-ros"
source_commit: "5b94e7e61e3be4bf00981fd74b7c9eba7595f4e1"
source_section: "1. 方案概述；2. 硬件清单"
source_resolution: partial
metric_source_resolution: unresolved
source_checked_at: 2026-10-13
source_note: "仅 Reachy Mini 条目已定向核对；SO101/Linksee 配置以及 25 FPS、8 FPS、100 Hz、15.4 tokens/s 的实测出处尚未定位。"
created: 2026-08-10
updated: 2026-10-13
aliases: [robot_hardware_specs, SpacemiT Robot Hardware, LeRobot SO101 Specs]
domain: edge_ai_robotics
target_audience: [具身智能工程师, 机器人工程师]
---

# SpacemiT 机器人硬件与具身 AI 模型参数规格

> [!TIP]
> **💡 工程师导读与排坑焦点**：存放 Reachy Mini、LeRobot SO101 机械臂、Linksee 移动车与 ACT/SmolVLA 参数。
> **目标读者**：`具身智能工程师 / 机器人工程师` | **技术领域**：`edge_ai_robotics`

本文档记录基于 SpacemiT K1/K3 平台适配的具身智能机器人硬件（Reachy Mini、LeRobot SO101 机械臂、Linksee 导航车）参数及端侧 AI 模型规格。

---

## 1. 具身机器人硬件物理参数矩阵

| 机器人产品名称 | 硬件类型 / 自由度 | 控制主板 | 传感器与执行器配置 | 应用场景 |
| :--- | :--- | :--- | :--- | :--- |
| **Reachy Mini Lite（官方适配方案）** | 头部 6-DoF（x/y/z/roll/pitch/yaw），身体垂直轴旋转，双天线电机 | **K3-COM260** | Sony IMX708 摄像头、PDM MEMS 数字麦克风、扬声器、XL330 舵机 | 视觉跟随、语音对话控制、舞蹈与仿真控制 |
| **LeRobot SO101** | 6-DoF 机械臂 | Muse Pi / K3 Pico | 6x 串行总线舵机、夹爪、USB/CSI 视角摄像头 | 模仿学习抓取、教研实验、工件分拣 |
| **Linksee 移动车** | 轮式差速/全向底盘 | K3 Pico / Muse Pi | 激光雷达 (LiDAR)、差速电机编码器、IMU 惯导 | 室内 2D/3D SLAM 建图与自主导航 |

---

## 2. 端侧具身 AI 模型与推理性能规格

> [!WARNING]
> 下表为待复核历史记录。25 FPS、8 FPS、100 Hz、15.4 tokens/s 的测试来源、模型版本及运行条件尚未定位（`metric_source_resolution: unresolved`），不得据此对外承诺性能，也不能把 tokens/s 吞吐量当作首包延迟。

| 模型名称 | 模型类型 / 架构 | 控制任务 | 运行平台 | 算力与推理帧率 |
| :--- | :--- | :--- | :--- | :--- |
| **ACT (Action Chunking)** | Transformer 模仿学习 | 机械臂轨迹与抓取预测 | K1 (Muse Pi / 2.0 TOPS) | 25 FPS 实时轨迹输出 |
| **SmolVLA** | 视觉-语言-动作多模态 (ONNX 4子图拆解) | 自然语言指令驱动机械臂 | K3 (K3 Pico / 60 TOPS) | 端侧 8 FPS 闭环控制 |
| **RL Policy (MuJoCo)**| 深度强化学习策略 (ONNX) | 双足/四足步态与平稳控制 | K1 / K3 (RVV 数学加速) | 100 Hz 控制频次 |
| **SpaceLLM 1B** | 端侧大语言模型 | 机器人语音对话与指令理解 | K1 (Muse Pi / 3W TDP) | 15.4 tokens/s 首包响应 |
