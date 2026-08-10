---
type: evidence
title: "SpacemiT 机器人硬件与具身 AI 模型参数规格"
status: needs_review
created: 2026-08-10
updated: 2026-08-10
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
| **Reachy Mini** | 桌面人形/头胸组件 | Muse Pi / K1 | 双目 CSI 摄像头、双耳麦克风阵列、头部 3-DoF 舵机 | 桌面语音交互、视线跟踪、人机协同 |
| **LeRobot SO101** | 6-DoF 机械臂 | Muse Pi / K3 Pico | 6x 串行总线舵机、夹爪、USB/CSI 视角摄像头 | 模仿学习抓取、教研实验、工件分拣 |
| **Linksee 移动车** | 轮式差速/全向底盘 | K3 Pico / Muse Pi | 激光雷达 (LiDAR)、差速电机编码器、IMU 惯导 | 室内 2D/3D SLAM 建图与自主导航 |

---

## 2. 端侧具身 AI 模型与推理性能规格

| 模型名称 | 模型类型 / 架构 | 控制任务 | 运行平台 | 算力与推理帧率 |
| :--- | :--- | :--- | :--- | :--- |
| **ACT (Action Chunking)** | Transformer 模仿学习 | 机械臂轨迹与抓取预测 | K1 (2.0 TOPS NPU/Vector) | 25 FPS 实时轨迹输出 |
| **SmolVLA** | 视觉-语言-动作多模态 | 自然语言指令驱动机械臂 | K3 (算力拓展) | 端侧 8 FPS 闭环控制 |
| **RL Policy (MuJoCo)**| 深度强化学习策略 | 双足/四足步态与平稳控制 | K1/K3 Vector 算力 | 100 Hz 控制频次 |
| **SpaceLLM 1B** | 端侧大语言模型 | 机器人语音对话与指令理解 | K1 (3W TDP 超低功耗) | 15.4 tokens/s 首包响应 |
