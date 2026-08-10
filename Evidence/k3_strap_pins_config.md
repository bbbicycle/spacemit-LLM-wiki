---
type: evidence
title: "K3 芯片 Strap Pins 启动与系统配置参数"
claim_type: "parameter"
verification_status: unverified
status: needs_review
external_use: false
source_file: "k3_hw_design_guide.md"
created: 2026-06-29
updated: 2026-06-29
aliases: ["K3 Strap管脚物理配置参数", "K3 Strap Pins Config Specs", "k3_strap_pins_config"]
domain: hardware_schematic_design
target_audience: [硬件电路工程师, 驱动工程师]
---
# K3 芯片 Strap Pins 启动与系统配置参数

> [!TIP]
> **💡 工程师导读与排坑焦点**：详细标注 K3 芯片 Strap 管脚配置阻值与启动介质引脚选择。
> **目标读者**：`硬件电路工程师 / 驱动工程师` | **技术领域**：`hardware_schematic_design`

本文件包含 K3 芯片级硬件初始化配置管脚（Strap Pins）的物理连接与功能组合。共有 6 个配置管脚（Strap 0 ~ 5）。

## 1. Boot 启动介质选择 (Strap 0 & 1)
通过 **GPIO66 (Strap 1)** 与 **GPIO65 (Strap 0)** 的电平组合选择芯片引导介质：

| 组合 | GPIO[66] (Strap 1)<br>[默认下拉] | GPIO[65] (Strap 0)<br>[默认下拉] | 启动顺序 / 引导功能 |
| :--- | :---: | :---: | :--- |
| **1** | 0 | 0 | **TF Card $\rightarrow$ eMMC [默认]** |
| **2** | 1 | 0 | **TF Card $\rightarrow$ SPI NOR** |
| **3** | 0 | 1 | **TF Card $\rightarrow$ SPI NAND** |
| **4** | 1 | 1 | **TF Card $\rightarrow$ UFS** |

## 2. Download sel 下载通道选择 (Strap 2)
通过 **GPIO68 (Strap 2)** 选择系统烧录/下载接口：

| GPIO[68] (Strap 2)<br>[默认下拉] | 烧录/下载接口功能 | 备注 |
| :---: | :--- | :--- |
| **0** | **USB [默认]** | 使用 USB DRD 接口 / Type-C 进行系统烧录 |
| **1** | **UART** | 使用串口进行下载/调试 |

## 3. Boot/down_sel 启动与下载模式选择 (Strap 3)
通过 **GPIO69 (Strap 3)** 选择芯片上电后的工作状态：

| GPIO[69] (Strap 3)<br>[默认下拉] | 芯片上电状态 | 说明 |
| :---: | :--- | :--- |
| **0** | **启动模式 [默认]** | 芯片正常读取启动介质并引导系统 |
| **1** | **下载/烧录模式** | 芯片进入烧录接收状态，等待主机写入固件 |

## 4. QSPI 电压选择 (Strap 4)
通过 **GPIO64 (Strap 4)** 决定 QSPI Flash 接口的 IO 电压域：

| GPIO[64] (Strap 4)<br>[默认下拉] | QSPI 电压功能 | 备注 |
| :---: | :--- | :--- |
| **0** | **3.3V [默认]** | 适用于 3.3V 工作电压的 SPI Flash |
| **1** | **1.8V** | 适用于 1.8V 工作电压的 SPI Flash |

## 5. LPDDR 内存类型选择 (Strap 5)
通过 **GPIO52 (Strap 5)** 决定 DDR 控制器初始化的物理内存类型：

| GPIO[52] (Strap 5)<br>[默认下拉] | 适配内存类型 | 备注 |
| :---: | :--- | :--- |
| **0** | **LPDDR5 [默认]** | 初始化为 LPDDR5 模式 |
| **1** | **LPDDR4x** | 初始化为 LPDDR4x 模式 |
