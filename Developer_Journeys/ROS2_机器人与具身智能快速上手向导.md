---
type: developer_journey
title: "ROS 2 机器人与具身智能快速上手向导"
status: needs_review
created: 2026-08-10
updated: 2026-10-21
aliases: [ROS2_机器人与具身智能快速上手向导, ROS2 Robotics Quick Start Guide]
domain: edge_ai_robotics
source_file: "Sources/docs-ros/zh/root_overview.md"
source_commit: "808d02c1bd11cf0d4376555919bd61c90e38d853"
source_section: "平台支持列表；K1/K3 ROS2 安装 平台要求/软件源/ROS-Base；K3 构建编译 1.2/1.3"
source_resolution: partial
verification_status: unverified
source_checked_at: 2026-10-21
source_note: "覆盖系统/发行版边界、最小环境和后续方案分流；传感器、micro-ROS、ACT/SmolVLA、Reachy 命令未在本轮实机验证。 本轮为来源与关键步骤定向核对，未在实物执行；关联节点保留各自核验状态。"
source_related_file: ["Sources/docs-ros/zh/k3/06-系统与平台/6.6-ROS2/6.6.1-ROS2-INSTALL.md", "Sources/docs-ros/zh/k1/06_Robot_development/6.1_OS_Preparation/6.1.2_ROS2_Installation.md", "Sources/docs-ros/zh/k3/02-快速入门/2.3-构建编译.md"]
source_related_commit: ["808d02c1bd11cf0d4376555919bd61c90e38d853", "808d02c1bd11cf0d4376555919bd61c90e38d853", "808d02c1bd11cf0d4376555919bd61c90e38d853"]
---
# ROS 2 机器人与具身智能快速上手向导

先确认板型、系统镜像、ROS 2 发行版，以及是否需要 Robot SDK。当前 [官方平台表](../Sources/docs-ros/zh/root_overview.md) 为 K1 推荐 Bianbu 2.3.x，K3 推荐 Bianbu 4.x（4.0.1 起），两代支持 Humble/Jazzy；**Lyrical 仅为 K3 计划支持**。

## 1. 配置对应平台环境

- K1 按 [ROS2 安装指南](../Sources/docs-ros/zh/k1/06_Robot_development/6.1_OS_Preparation/6.1.2_ROS2_Installation.md) 确认 ROS2_LXQT 镜像与平台软件源，已预装时避免重复配置。
- K3 Bianbu 4.0.1 起默认有 ROS 2 源，按 [K3 安装指南](../Sources/docs-ros/zh/k3/06-系统与平台/6.6-ROS2/6.6.1-ROS2-INSTALL.md) 核对；不要照抄通用 Ubuntu 源配置或把 Ubuntu 24.04 + Humble 当作本平台通用组合。

在匹配的 K3 Bianbu 环境中，原文最小 Humble 示例为：

```bash
sudo apt update
sudo apt install ros-dev-tools ros-humble-ros-base
source /opt/ros/humble/setup.sh
```

RViz、Nav2、MoveIt 和硬件驱动不是 ROS-Base 自动具备的能力。多机尽量同一 ROS 2 发行版，按实际示例核对中间件、网络和 ROS_DOMAIN_ID，不能保证跨发行版互通。平台表见 [[Evidence/ros2_platform_specs]]。

## 2. 先验证基础通信，再接硬件

按对应安装指南的发布/订阅示例确认 ROS 环境。连接 UART/传感器前核对板型排针、电平与串口是否被控制台占用；不能假定任何板都用 `/dev/ttyS1`。MUSE Pi 参考 [[Knowledge_Atoms/Muse_Pi_板级硬件设计专题]]。

## 3. 按场景进入 Robot SDK

[K3 构建编译指南](../Sources/docs-ros/zh/k3/02-快速入门/2.3-构建编译.md) 区分最小 ROS 2 环境与 SDK 流程，二者不必全量叠加执行。需 SDK 时再按目标板和方案取源码、配置与构建，不用一条未核实的 launch 命令代表所有机器人。

## 4. 核对具身方案的适用范围

ACT、SmolVLA、Reachy 等方案按具体机器人、芯片与发布版本核对，历史 FPS、DOF、子图数量和演示命令不能作为所有设备的保证。先读取 [[Evidence/robot_hardware_specs]] 与 [[Knowledge_Atoms/SpacemiT_ROS2_机器人与具身智能专题档案]]，证据不足时说明缺口；本轮未做机器人实物测试。
