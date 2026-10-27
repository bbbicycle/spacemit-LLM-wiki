---
type: evidence
title: "K3 芯片 Strap Pins 启动与系统配置参数"
claim_type: "parameter"
status: needs_review
verification_status: verified
verified_at: "2026-10-27"
external_use: true
source_file: "Sources/docs-chip/zh/key_stone/k3/k3_hw/k3_hw_design_guide.md"
source_origin: "https://github.com/spacemit-com/docs-chip"
source_commit: "fd016f81034b1a93ad39c2cecf313bb82be7d169"
source_section: "硬件指南V1.2 1.1.5；数据手册V1.9 2.11.2 启动模式映射"
source_resolution: resolved
source_checked_at: 2026-10-27
source_note: "2026-10-21 官方发布硬件设计指南V1.2（commit fd016f8），正式更正1.1.5小节：明确Strap管脚共6个（GPIO52/64/65/66/68/69，去除笔误GPIO90）；并将SPI启动组合修正为01=SPI NOR、10=SPI NAND，与《K3数据手册》2.11.2完全达成一致。官方勘误闭环，解除conflicted状态。"
source_related_file: ["Sources/docs-chip/zh/key_stone/k3/k3_docs/k3_ds.md"]
source_related_commit: ["fd016f81034b1a93ad39c2cecf313bb82be7d169"]
created: 2026-06-29
updated: 2026-10-27
aliases: ["K3 Strap管脚物理配置参数", "K3 Strap Pins Config Specs", "k3_strap_pins_config"]
domain: hardware_schematic_design
target_audience: [硬件电路工程师, 驱动工程师]
---
# K3 芯片 Strap Pins 启动与系统配置参数

> [!NOTE]
> **官方勘误已闭环（2026-10-21）**：官方开发在《K3 硬件设计指南》V1.2 中正式修复了此前两项争议：
> 1. 明确 Strap Pin 共有完整的 **6 个**（GPIO52、GPIO64、GPIO65、GPIO66、GPIO68、GPIO69），移除了旧版笔误出现的 GPIO90。
> 2. 修正了 SPI NOR 与 SPI NAND 的电平定义，与《K3 数据手册》§2.11.2 达成完全统一（`01` 为 SPI NOR，`10` 为 SPI NAND）。

> [!TIP]
> **💡 工程师导读与排坑焦点**：用于指导 K3 单板原理图 Strap 电路上下拉设计与启动介质硬件配置。
> **目标读者**：`硬件电路工程师 / 驱动工程师` | **技术领域**：`hardware_schematic_design`

K3 芯片共有 **6 个 Strap Pin**，分别对应 GPIO52、GPIO64、GPIO65、GPIO66、GPIO68、GPIO69。

---

## 1. Boot 启动介质选择 (Strap 0 & 1)

通过 **GPIO66 (Strap 1)** 与 **GPIO65 (Strap 0)** 决定上电后的次级启动介质，正常启动模式下芯片始终优先尝试 TF/SD 卡引导，未检测到或无有效镜像时回退至次级介质：

| GPIO66 (Strap 1)<br>[默认下拉] | GPIO65 (Strap 0)<br>[默认下拉] | 官方统一启动模式映射 (硬件指南 V1.2 & 数据手册 V1.9) | 说明 |
| :---: | :---: | :--- | :--- |
| **0** | **0** | **TF Card → eMMC [默认]** | 优先尝试 TF 卡，回退至板载 eMMC 启动 |
| **0** | **1** | **TF Card → SPI NOR** | 优先尝试 TF 卡，回退至 SPI NOR Flash 启动 |
| **1** | **0** | **TF Card → SPI NAND** | 优先尝试 TF 卡，回退至 SPI NAND Flash 启动 |
| **1** | **1** | **TF Card → UFS** | 优先尝试 TF 卡，回退至 UFS 存储启动 |

> 来源：[硬件设计指南 §1.1.5](../Sources/docs-chip/zh/key_stone/k3/k3_hw/k3_hw_design_guide.md) 与 [数据手册 §2.11.2](../Sources/docs-chip/zh/key_stone/k3/k3_docs/k3_ds.md)，均已对齐至官方最新版本。

---

## 2. Download sel 下载通道选择 (Strap 2)

通过 **GPIO68 (Strap 2)** 选择系统烧录/下载接口：

| GPIO[68] (Strap 2)<br>[默认下拉] | 烧录/下载接口功能 | 备注 |
| :---: | :--- | :--- |
| **0** | **USB [默认]** | 使用 USB DRD 接口 / Type-C 进行系统烧录 |
| **1** | **UART** | 使用串口进行下载/调试 |

---

## 3. Boot/down_sel 启动与下载模式选择 (Strap 3)

通过 **GPIO69 (Strap 3)** 选择芯片上电后的工作状态：

| GPIO[69] (Strap 3)<br>[默认下拉] | 芯片上电状态 | 说明 |
| :---: | :--- | :--- |
| **0** | **启动模式 [默认]** | 芯片正常读取启动介质并引导系统 |
| **1** | **下载/烧录模式** | 芯片进入烧录接收状态，等待主机写入固件 |

---

## 4. QSPI 电压选择 (Strap 4)

通过 **GPIO64 (Strap 4)** 决定 QSPI Flash 接口的 IO 电压域：

| GPIO[64] (Strap 4)<br>[默认下拉] | QSPI 电压功能 | 备注 |
| :---: | :--- | :--- |
| **0** | **3.3V [默认]** | 适用于 3.3V 工作电压的 SPI Flash |
| **1** | **1.8V** | 适用于 1.8V 工作电压的 SPI Flash |

---

## 5. LPDDR 内存类型选择 (Strap 5)

通过 **GPIO52 (Strap 5)** 决定 DDR 控制器初始化的物理内存类型：

| GPIO[52] (Strap 5)<br>[默认下拉] | 适配内存类型 | 备注 |
| :---: | :--- | :--- |
| **0** | **LPDDR5 [默认]** | 初始化为 LPDDR5 模式 |
| **1** | **LPDDR4x** | 初始化为 LPDDR4x 模式 |
