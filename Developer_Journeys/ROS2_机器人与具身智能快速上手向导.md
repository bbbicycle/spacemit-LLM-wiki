---
type: developer_journey
title: "ROS 2 机器人与具身智能快速上手向导"
status: needs_review
created: 2026-08-10
updated: 2026-08-10
aliases: [ROS2_机器人与具身智能快速上手向导, ROS2 Robotics Quick Start Guide]
domain: edge_ai_robotics
---

# ROS 2 机器人与具身智能快速上手向导

本向导提供从环境搭建、硬件连接、micro-ROS 节点启动到端侧模仿学习（ACT / SmolVLA）模型部署的极简通关动线，帮助开发者快速在 SpacemiT K1 / K3 芯片与生态板卡上开发具身智能机器人应用。

---

## 🗺️ 通关路线图

```mermaid
graph LR
    Step1[1. 环境准备] --> Step2[2. 硬件连接与 micro-ROS]
    Step2 --> Step3[3. ROS 2 驱动启动]
    Step3 --> Step4[4. 具身 AI 模型部署]
```

---

## 步骤 1：准备 ROS 2 开发环境

推荐在 **Bianbu OS** 或 **Ubuntu 24.04** 上安装 ROS 2 Humble 或 Jazzy 环境：

```bash
# 1. 软件源与 ROS 2 基础环境安装
sudo apt update && sudo apt install -y ros-humble-ros-base ros-humble-rviz2

# 2. 设置 ROS 2 环境变量
source /opt/ros/humble/setup.bash

# 3. 指定 Cyclone DDS 中间件
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

详细环境依赖与节点消耗请参考 [[Evidence/ros2_platform_specs|SpacemiT ROS 2 平台规格表]]。

---

## 步骤 2：硬件接口连接与 micro-ROS Agent 启动

将微控制器 / 机械臂舵机板通过 UART 串口线连接至主板（如 `/dev/ttyS1`）：

```bash
# 启动 micro-ROS 串口桥接节点
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyS1 -b 115200
```

板级 JTAG / UART 调试排针规范参考 [[Knowledge_Atoms/Muse_Pi_板级硬件设计专题|Muse Pi 板级硬件设计专题]]。

---

## 步骤 3：部署 LeRobot 机械臂或 Reachy Mini 应用

### 3.1 运行 SO101 机械臂 ACT 模仿学习推理

使用已安装的 LeRobot 库，在 K1/K3 端侧直接运行 ACT 轨迹预测模型驱动 SO101 6-DoF 机械臂：

```bash
# 运行端侧抓取推理闭环
python3 -m lerobot.scripts.control_robot --robot-type so101 --policy-type act --eval
```

### 3.2 运行 Reachy Mini 视线追踪与交互

```bash
ros2 launch reachy_mini_bringup reachy_mini.launch.py
```

更多机械臂与具身智能模型规格详见 [[Evidence/robot_hardware_specs|SpacemiT 机器人硬件与具身 AI 模型参数规格]] 及 [[Knowledge_Atoms/SpacemiT_ROS2_机器人与具身智能专题档案|SpacemiT ROS 2 机器人与具身智能专题档案]]。
