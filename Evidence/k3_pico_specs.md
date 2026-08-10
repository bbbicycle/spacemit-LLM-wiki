---
type: evidence
title: "K3 Pico-ITX 迷你 AI 计算机物理规格参数"
claim_type: "parameter"
verification_status: unverified
status: needs_review
external_use: false
source_file: "Sources/docs-product/zh/k3_pico/root_overview.md"
created: 2026-06-30
updated: 2026-06-30
aliases: ["K3 Pico板级核心参数", "K3 Pico Board Hardware Specs", "k3_pico_specs"]
domain: chip_product_specs
target_audience: [硬件工程师, 产品架构师]
---
# K3 Pico-ITX 迷你 AI 计算机物理规格参数

> [!TIP]
> **💡 工程师导读与排坑焦点**：存放 K3 Pico-ITX 迷你主板处理器、存储、光口与外设物理规格。
> **目标读者**：`硬件工程师 / 产品架构师` | **技术领域**：`chip_product_specs`

本文件汇总了 K3 Pico-ITX 迷你计算机的硬件规格数据，可用于系统集成与硬件开发设计参考。

| 规格维度 | 详细参数规格 | 说明 / 调试设计 |
| :--- | :--- | :--- |
| **主控处理器** | SpacemiT K3 8核（8计算核 + 8智算核） | 融合 60 TOPS AI 算力，符合 RVA23 标准，支持 IME 向量扩展与完整虚拟化 |
| **内存 (DRAM)** | 双通道 2 × 32-bit LPDDR5，6400 MT/s | 可选 16GB / 32GB 容量，计算核与智算核统一内存架构，支持 30B 大模型推理 |
| **本地存储** | 板载 UFS 2.2 闪存 | 可选 128GB / 256GB 容量，读取速率比普通 eMMC 提升 3.4 倍 |
| **存储扩展** | M.2 M-Key (2280) 连接器 | 支持 PCIe Gen3 x4 链路，可挂载 NVMe SSD（注：B-Key 插入设备时降为 Gen3 x2） |
| **高速扩展** | M.2 B-Key (2242/3042) 连接器 | 提供 PCIe Gen3 x2 及 USB 信号，可扩展 SSD 或 4G 模组 |
| **实时运动控制** | FPC 柔性连接器 | 由实时核 **RT24** 直出，支持 EtherCAT、5路 CAN-FD、SPI、I2C、UART，满足微秒级控制 |
| **有线网络** | 1 × 千兆网口 (RJ45) | 支持 1000M / 100M 自适应 |
| **光纤网络** | 1 × 万兆光口 (SFP+) | 支持 10G BASE-R / 10G BASE-X，支持 QinQ、MSI-X 及 WOL |
| **无线网络** | 板载 PCIe Wi-Fi 6 + 蓝牙 5.2 模组 | 支持 802.11a/b/g/n/ac/ax 标准，双天线设计 |
| **显示接口** | 1 × DP (Type-C)<br>1 × eDP (40-Pin FPC) | DP 最高支持 4K @ 60Hz 刷新率<br>eDP 最高支持 2.5K 2560×1600 @ 90Hz 刷新率 |
| **USB 接口** | 2 × USB 3.2 Gen1 Type-C<br>4 × USB 2.0 Type-A Host | Type-C 一路为全功能（支持 DP/供电），一路为 OTG 烧录口 |
| **电源输入** | USB-PD 3.0 (Type-C) 或 2-Pin ATX | Type-C 口额定输入 65W 功率；ATX 端子支持 12V @ 7A 供电 |
| **管理系统** | 板载 EC (Embedded Controller) | 负责电源管理、智能风扇散热策略、RTC 时钟管理及状态监控 |
| **机械尺寸** | 100 mm × 86 mm | 2.5寸 Pico-ITX Plus 紧凑规格 |
| **可靠性** | 接触防护 ±4kV，空气防护 ±8kV（单板） | 整机形态下接触防护提升至 ±6kV，空气 ±12kV |
