---
type: evidence
title: "K3 芯片 Strap Pins 启动与系统配置参数"
claim_type: "parameter"
status: needs_review
verification_status: conflicted
conflicts: "K3指南1.1.5概述列5脚含GPIO90，功能表却列Strap0～5含GPIO64/52；另与K3数据手册2.11.2的GPIO66/65启动选择冲突：指南10=SPI NOR、01=SPI NAND，数据手册10=SPI NAND、01=SPI NOR。00/11一致；SPI接线与完整管脚清单待官方确认。"
external_use: false
source_file: "Sources/docs-chip/zh/key_stone/k3/k3_hw/k3_hw_design_guide.md"
source_origin: "https://github.com/spacemit-com/docs-chip"
source_commit: "2525ee3b68e0f4864f1bf12c8a59df040bf27e84"
source_section: "硬件指南1.1.5；数据手册V1.9 2.11.2 启动模式映射"
source_resolution: resolved
source_checked_at: 2026-10-21
source_note: "2026-10-21 阶段B再次定向对照指南1.1.5与数据手册2.11.2，发现SPI NOR/NAND选择电平互换；并列表格，不按文档日期自行裁决。来源定位成功不代表接线结论已确认，保持conflicted/needs_review。"
source_related_file: ["Sources/docs-chip/zh/key_stone/k3/k3_docs/k3_ds.md"]
source_related_commit: ["2525ee3b68e0f4864f1bf12c8a59df040bf27e84"]
created: 2026-06-29
updated: 2026-10-21
aliases: ["K3 Strap管脚物理配置参数", "K3 Strap Pins Config Specs", "k3_strap_pins_config"]
domain: hardware_schematic_design
target_audience: [硬件电路工程师, 驱动工程师]
---
# K3 芯片 Strap Pins 启动与系统配置参数

> [!WARNING]
> **待官方确认（2026-10-21）**：① 完整 Strap 管脚清单及 GPIO90/64/52 的角色；② GPIO66/GPIO65 的 SPI NOR/NAND 启动映射。维护者已与开发同步修订，等待官方 GitHub 原文更新后再复核并修正本页。两份现有原表继续并列保留，争议接线结论尚未确定。

> [!TIP]
> **💡 工程师导读与排坑焦点**：保留 K3 Strap 官方原表与冲突依据，接线前需确认具体板型与官方结论。
> **目标读者**：`硬件电路工程师 / 驱动工程师` | **技术领域**：`hardware_schematic_design`

本文件按 K3 指南 1.1.5 的功能表列出 Strap 0～5。

> [!WARNING]
> **两类官方冲突，待确认**：指南开头写“共有 5 个 strap pin”，并列 GPIO65/66/68/69/90，后面的 QSPI 与 LPDDR 表却写 GPIO64 和 GPIO52；同时，指南与数据手册对 SPI NOR/NAND 的 GPIO66/65 组合相反。不能将任一单表作为已确认的完整接线依据；电阻、供电和实际接线须对照对应板型经审定原理图及官方勘误。

## 1. Boot 启动介质选择 (Strap 0 & 1)
以下按相同的 **GPIO66 / GPIO65** 列顺序对照两份固定来源；正常启动对应 GPIO69=0。指南标注相关管脚 default down，数据手册表中的 x 表示不影响该启动模式选择。

| GPIO66 | GPIO65 | 硬件设计指南 V1.1 §1.1.5 | 数据手册 V1.9 §2.11.2 |
| :---: | :---: | :--- | :--- |
| 0 | 0 | TF Card → eMMC [默认] | SD Card → eMMC |
| 1 | 0 | TF Card → SPI NOR | SD Card → SPI NAND |
| 0 | 1 | TF Card → SPI NAND | SD Card → SPI NOR |
| 1 | 1 | TF Card → UFS | SD Card → UFS |

**SPI 选择冲突尚未裁决**：两份来源均先尝试 SD/TF，00 的次级介质为 eMMC、11 为 UFS；10/01 的 SPI NOR 与 SPI NAND 互换。不能仅凭文档日期、表格编号或文件名决定哪一套电平正确，也不能将本表用于直接选择 SPI 启动接线。

来源：[硬件设计指南 §1.1.5](../Sources/docs-chip/zh/key_stone/k3/k3_hw/k3_hw_design_guide.md)与[数据手册 §2.11.2](../Sources/docs-chip/zh/key_stone/k3/k3_docs/k3_ds.md)，均固定于 `2525ee3b68e0f4864f1bf12c8a59df040bf27e84`。

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
