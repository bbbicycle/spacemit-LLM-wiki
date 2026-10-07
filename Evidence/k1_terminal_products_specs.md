---
type: evidence
title: "Spacemit K1 生态衍生终端与实验套件物理规格参数"
claim_type: "parameter"
verification_status: verified
status: needs_review
external_use: true
source_file: "Sources/docs-product/zh"
created: 2026-10-07
updated: 2026-10-07
aliases: ["K1生态终端参数表", "K1 Terminal Products Specs", "k1_terminal_products_specs", "Muse终端规格"]
domain: chip_product_specs
target_audience: [产品架构师, 硬件工程师, 解决方案工程师]
---

# Spacemit K1 生态衍生终端与实验套件物理规格参数

> [!TIP]
> **💡 数据事实与设计导读**：
> 本文件汇集了基于 Spacemit K1 / M1 八核 RISC-V 处理器打造的 **6 大核心生态终端与实验套件**（Muse Book、Muse Box、Muse Card、Muse Paper、Muse Shelf、RISC-V Labkit）的标准化结构物理参数，供整机选型、教学采购与系统集成比对。

---

## 1. 便携终端与整机硬件规格 (Book / Box / Paper)

| 规格维度 | MUSE Book (笔记本电脑) | MUSE Box (Mini-ITX 迷你主机) | MUSE Paper (电子墨水屏平板) |
| :--- | :--- | :--- | :--- |
| **主控芯片** | SpacemiT K1 八核 X60 @ 1.6GHz | SpacemiT K1 八核 X60 @ 1.6GHz | SpacemiT K1 八核 X60 @ 1.6GHz |
| **AI 算力** | 2.0 TOPS 通用 AI 算力 | 2.0 TOPS 通用 AI 算力 | 2.0 TOPS 通用 AI 算力 (RVV 加速) |
| **伴随 PMIC** | Power Stone P1 | Power Stone P1 | Power Stone P1 |
| **内存 (DRAM)** | 8GB / 16GB LPDDR4X @ 2400MT/s | 8GB / 16GB LPDDR4X @ 2400MT/s | 4GB / 8GB LPDDR4X @ 2400MT/s |
| **板载存储** | eMMC 5.1 (64GB / 128GB) | eMMC 5.1 (64GB / 128GB) | 64GB eMMC 闪存 |
| **存储扩展** | 1 × M.2 2280 NVMe SSD + MicroSD | 1 × M.2 2280 NVMe SSD + MicroSD | MicroSD (TF) 卡插槽 |
| **显示屏幕/输出**| 14.1 英寸 IPS (1920×1080 FHD) | 1 × HDMI 2.0 + 1 × DP (支持双屏异显) | 10.3 英寸电子墨水屏 (护眼防眩光) |
| **网络通讯** | Wi-Fi 6 + 蓝牙 5.2 | 2 × 千兆网口 (RJ45) + Wi-Fi 6/BT | Wi-Fi 6 + 蓝牙 5.2 |
| **外部标准 I/O** | 2×USB 3.0, 1×Type-C (充放电/数据), 3.5mm音频 | 4×USB 3.0, 2×USB 2.0, RS232串口端子 | 1 × Type-C OTG / 充电 |
| **电源与电池** | 5000 mAh 锂聚合物电池, Type-C PD 供电 | 12V DC 适配器供电 (整机功耗约 10W) | 内置高密度锂电池, 超长待机 |
| **支持操作系统**| Bianbu Desktop / Ubuntu / OpenKylin | Bianbu Desktop / Bianbu NAS / OpenKylin | **OpenHarmony 5.0 (原生鸿蒙)** / Bianbu |

---

## 2. 算力卡、实验架与教学套件硬件规格 (Card / Shelf / Labkit)

| 规格维度 | MUSE Card (微型计算卡) | MUSE Shelf (2U 云算力实验架) | RISC-V Labkit (教学实验箱) |
| :--- | :--- | :--- | :--- |
| **主控芯片/规模**| 1 × SpacemiT K1 八核 @ 1.6GHz | **80 × SpacemiT K1 八核处理器** | 1 × SpacemiT M1 八核 @ 1.6GHz |
| **总算力规模** | 2.0 TOPS AI 算力 | **160 TOPS 总算力 (640 核并行)** | 2.0 TOPS AI 算力 (支持 0.5B~1B 大模型) |
| **物理形态** | 85 mm × 56 mm 紧凑单板 | 2U 标准机架式 (2/4 模块化刀片设计) | 便携式工程实验箱 (集成 10.1寸触控屏) |
| **内存与存储** | 8GB/16GB LPDDR4X, 64Mb SPI NOR | 80 个独立节点 (各节点配独立内存/存储) | 16GB LPDDR4X, 64GB eMMC 5.1 |
| **存储扩展接口**| **2 × M.2 2242 M-Key NVMe SSD** | 集中式存储池与网络存储挂载 | 1 × M.2 2280 M-Key NVMe (最高支持 1TB) |
| **扩展总线接口**| 40Pin GPIO, 2路 4-lane CSI, 1路 DSI | 内部高速以太网互联背板 | 积木式插拔外设接口 (传感器/电机/机械臂) |
| **网络能力** | 1 × 千兆网口 (RJ45 1000M/100M) | 多路千兆上行汇聚 + 独立管理网口 | 1 × 千兆网口 + Wi-Fi 6 模块 |
| **管理与运维** | 侧边按键 (复位/开关机/烧录) | 支持远程桌面、远程编译、一键批量刷机 | 预装嵌入式与 AI 百余教学实验 SOP |
| **目标场景** | 双 NVMe 便携 NAS、机器视觉前置机 | 进迭云分布式开发云平台、CI/CD 编译农场 | 高校微机原理、操作系统、RISC-V 教学实训 |
