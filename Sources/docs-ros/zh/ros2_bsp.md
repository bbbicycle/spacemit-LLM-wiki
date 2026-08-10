---
sidebar_position: 2
---

# ROS 2 环境搭建与底层接口配置指南

本文档介绍如何在 SpacemiT K1/K3 平台上搭建 ROS 2 环境及配置底层硬件驱动。

## 1. ROS 2 安装

推荐在 Bianbu OS 或 Ubuntu 24.04 上直接安装官方 ROS 2 Jazzy / Humble 二进制包或 Docker 镜像：

```bash
# 1. 软件源设置
sudo apt update && sudo apt install -y software-properties-common curl
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /null

# 2. 安装 ROS 2 基础环境与桌面套件
sudo apt update
sudo apt install -y ros-humble-ros-base ros-humble-demo-nodes-cpp ros-humble-rviz2
```

## 2. DDS 中间件调优

针对 K1/K3 双百兆/千兆网口，推荐配置 Cyclone DDS 或 Fast DDS 提高大流量图像与点云节点的传输效率：

```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

## 3. micro-ROS 硬件接口

通过 UART / USB-CDC 连接外部微控制器（MCU/ESP32/STM32）：

```bash
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyS1 -b 115200
```
