---
sidebar_position: 3
---

# 具身智能与机器人示例应用指南

本文档介绍如何在 SpacemiT 芯片平台上部署 Reachy Mini、LeRobot 及 Linksee 导航机器人应用。

## 1. Reachy Mini 桌面机器人

Reachy Mini 包含头部双摄与动作电机。

* **动作控制与视觉跟随**：
  ```bash
  ros2 launch reachy_mini_bringup reachy_mini.launch.py
  ```

## 2. LeRobot (SO101 机械臂)

支持通过 Hugging Face LeRobot 框架控制 6 自由度 SO101 机械臂，进行轨迹录制与 ACT (Action Chunking with Transformers) 模仿学习模型端侧部署：

* **端侧推理运行**：
  ```bash
  python3 -m lerobot.scripts.control_robot --robot-type so101 --policy-type act --eval
  ```

## 3. Linksee 移动导航机器人

* **2D/3D SLAM 建图**：
  ```bash
  ros2 launch linksee_navigation slam.launch.py
  ```
* **Nav2 自主导航**：
  ```bash
  ros2 launch linksee_navigation navigation.launch.py
  ```
