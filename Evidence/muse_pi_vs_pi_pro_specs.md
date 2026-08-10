---
type: evidence
title: "SpacemiT 生态板卡 Muse Pi 与 Muse Pi Pro 物理规格对比"
claim_type: "parameter"
verification_status: unverified
status: needs_review
external_use: false
source_file: "k1_hw_faq.md"
created: 2026-06-29
updated: 2026-06-29
aliases: ["Muse Pi对Muse Pi Pro规格对比表", "Muse Pi vs Muse Pi Pro Specs", "muse_pi_vs_pi_pro_specs"]
domain: chip_product_specs
target_audience: [系统选型工程师, 硬件工程师]
---
# SpacemiT 生态板卡 Muse Pi 与 Muse Pi Pro 物理规格对比

> [!TIP]
> **💡 工程师导读与排坑焦点**：存放 Muse Pi 与 Muse Pi Pro 板级物理尺寸、电源与外设参数对比。
> **目标读者**：`系统选型工程师 / 硬件工程师` | **技术领域**：`chip_product_specs`

本文件汇总了基于进迭时空 K1 芯片开发的生态开发板 Muse Pi 与高级版 Muse Pi Pro 的硬件设计与物理规格差异。

| 规格维度 | Muse Pi (标准版) | Muse Pi Pro (高级版) | 备注 / 调试设计 |
| :--- | :--- | :--- | :--- |
| **主控 CPU** | SpacemiT Key Stone K1 (8核) | SpacemiT Key Stone K1 (8核) | 均符合 RVA22 / RVV 1.0 标准 |
| **内存支持** | 最大 16GB LPDDR4/LPDDR4X | 最大 16GB LPDDR4/LPDDR4X | 速率高达 2666 Mbps，32-bit |
| **4G / 5G 模块** | 不支持（无插槽） | **内置 Mini PCIe 4G/5G 模块插槽** | 带有板载 Micro SIM 卡槽 |
| **以太网接口** | 1 × 千兆网口 (GMAC0) | **2 × 千兆网口 (GMAC0 & GMAC1)** | 均采用千兆 PHY 芯片 |
| **USB 高速接口** | 2 × USB 3.0 (Type-A) + 2 × USB 2.0 | 2 × USB 3.0 + 2 × USB 2.0 (包含内置扩展) | 包含 1 个 Type-C 烧录/电源口 |
| **音频功放 (PA)** | 仅有 Headphone 耳机口输出 | **集成板载 Speaker PA 功放输出** | 方便直接连接喇叭 |
| **调试串口** | 3-Pin 单排插针 (TX/RX/GND) | 3-Pin 单排插针 (TX/RX/GND) | 电平限 **3.3 V**，波特率 115200 |
| **JTAG 调试口** | PRI JTAG（26Pin排针引出） | PRI JTAG（26Pin排针引出） | SEC JTAG 复用 SD 卡引脚 |
| **扩展排针** | 26-Pin 兼容树莓派排针 | 26-Pin 兼容树莓派排针 | 包含 I2C, SPI, UART, PWM, GPIO |
