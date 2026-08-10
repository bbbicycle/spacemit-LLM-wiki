---
type: evidence
title: "K1 芯片 Strap Pins 启动与系统配置参数"
claim_type: "parameter"
verification_status: unverified
status: needs_review
external_use: false
source_file: "k1_hw_design_guide.md"
created: 2026-06-29
updated: 2026-06-29
aliases: ["K1 Strap管脚物理配置参数", "K1 Strap Pins Config Specs", "k1_strap_pins_config"]
domain: hardware_schematic_design
target_audience: [硬件电路工程师, 驱动工程师]
---
# K1 芯片 Strap Pins 启动与系统配置参数

> [!TIP]
> **💡 工程师导读与排坑焦点**：详细标注 K1 芯片 Strap Pins 原理图上下拉阻值与 JTAG 路由复用要点。
> **目标读者**：`硬件电路工程师 / 驱动工程师` | **技术领域**：`hardware_schematic_design`

本文件包含 K1 芯片级硬件初始化配置管脚（Strap Pins）的物理连接与功能组合。

## 1. Boot 启动介质选择 (Strap 0 & 1)
通过 **QSPI_DATA1/Strap1** 与 **QSPI_DATA0/Strap0** 的电平组合选择芯片引导介质：

| 组合 | Strap 1 [默认下拉] | Strap 0 [默认下拉] | 启动顺序 / 引导功能 |
| :--- | :---: | :---: | :--- |
| **1** | 0 | 0 | **eMMC [默认]** |
| **2** | 0 | 1 | **SPI NOR** |
| **3** | 1 | 0 | **SPI NAND** |
| **4** | 1 | 1 | **SD CARD** |

## 2. Download sel 下载通道选择 (Strap 2)
通过 **QSPI_DATA2/Strap2** 选择系统烧录/下载接口：

| Strap 2 [默认下拉] | 烧录/下载接口功能 | 备注 |
| :---: | :--- | :--- |
| **0** | **USB (USB0) [默认]** | 使用 USB 接口进行系统烧录 |
| **1** | **UART (UART0)** | 使用串口进行下载/调试 |

## 3. Boot/Download 启动与下载模式选择 (Strap 3)
通过 **QSPI_DATA3/Strap3 FDL** 选择芯片上电后的工作状态：

| Strap 3 [默认下拉] | 芯片上电状态 | 说明 |
| :---: | :--- | :--- |
| **0** | **启动模式 [默认]** | 正常读取引导介质启动系统 |
| **1** | **下载模式** | 芯片进入烧录接收状态 |

## 4. QSPI/Flash 电压选择 (Strap 4)
通过 **GPIO_90/Strap4** 决定 QSPI Flash 接口的供电电压：

| Strap 4 [默认下拉] | Flash 供电电压 | 说明与关联配置 |
| :---: | :--- | :--- |
| **0** | **1.8 V [默认]** | 芯片上拉到 1.8V GPIO 时，VCC1833_QSPI 必须工作在 3.3V 供电；下拉 GND 时工作在 1.8V 供电。 |
| **1** | **3.3 V** | 适用于 3.3V Flash 供电。 |

## 5. JTAG 与 CPU 路由配置
*   **JTAG_SEL**：Sec JTAG 选择。`0`：其他功能（默认），`1`：SEC JTAG。
*   **MMC1_SD_CMD**：JTAG 路由选择。`0`：调试 X60 核心，`1`：调试 N308 实时核心。
