---
type: knowledge_atom
title: "K3 启动模式与 Strap 管脚配置专题档案"
status: "needs_review"
created: 2026-06-29
updated: 2026-10-21
aliases: ["K3启动模式与Strap配置专题", "K3 Boot Mode and Strap Config Topic", "k3_boot_strap_config"]
domain: hardware_schematic_design
target_audience: [硬件电路工程师, 嵌入式驱动]
source_file: "Sources/docs-chip/zh/key_stone/k3/k3_hw/k3_hw_design_guide.md"
source_commit: "2525ee3b68e0f4864f1bf12c8a59df040bf27e84"
source_locator: "硬件设计指南 1.1.5/1.4.4；数据手册 V1.9 2.11.2；其他正文未全文核验"
source_resolution: "partial"
verification_status: conflicted
conflicts: "K3指南1.1.5的管脚概述与Strap0～5功能表不一致；该指南与数据手册2.11.2还将GPIO66/65的SPI NOR/NAND组合互换。SPI选择及完整管脚清单待官方裁决，详见k3_strap_pins_config。"
source_checked_at: 2026-10-21
source_note: "2026-10-21 阶段B复核指南1.1.5/1.4.4，并与数据手册2.11.2逐位比较启动映射；补SPI选择电平冲突，下载模式按GPIO69与GPIO68共同判断。其他正文未全文核验，保持conflicted/needs_review。"
source_origin: "https://github.com/spacemit-com/docs-chip"
source_related_file: ["Sources/docs-chip/zh/key_stone/k3/k3_hw/k3_hw_faq.md", "Sources/docs-chip/zh/key_stone/k3/k3_sw/k3_sdk_user_guide.md", "Sources/docs-chip/zh/key_stone/k3/k3_docs/k3_ds.md"]
source_related_commit: ["15254b1cfe339c1863d8edf8137a337681fb2780", "15254b1cfe339c1863d8edf8137a337681fb2780", "2525ee3b68e0f4864f1bf12c8a59df040bf27e84"]
---
# K3 启动模式与 Strap 管脚配置专题档案

> [!WARNING]
> **待官方确认（2026-10-21）**：① 完整 Strap 管脚清单及 GPIO90/64/52 的角色；② GPIO66/GPIO65 的 SPI NOR/NAND 启动映射。维护者已与开发同步修订，等待官方 GitHub 原文更新后再复核并修正本页。两份现有原表继续并列保留，争议接线结论尚未确定。

> [!TIP]
> **💡 工程师导读与排坑焦点**：指导 K3 芯片 Strap Pins 硬件上下拉设计与物理启动介质配置。
> **目标读者**：`硬件电路工程师 / 嵌入式驱动` | **技术领域**：`hardware_schematic_design`

本专题档案汇总了关于 SpacemiT K3 芯片上电初始化、Strap 管脚硬件设计、以及系统启动/烧录模式的配置要点。

---

## 1. 硬件配置核心原则

K3 芯片在复位释放（Reset Release）的瞬间，会通过采样特定的配置管脚（Strap Pins）的电平状态，来决定芯片的启动介质、烧录通道、内存类型和接口电压。

*   **硬件连接要求**：
    *   功能表将相关项标为 default down，但同节的管脚数量/列表存在内部矛盾，必须同时保留 [[Evidence/k3_strap_pins_config]] 的冲突提示。
    *   本轮未在声明来源中确认旧稿的通用 `4.7kΩ～10kΩ` 上拉范围或“默认可悬空”的板级接线保证。按对应版本原理图核对电阻、IO 电源域、采样与复用条件；不能照抄 K1 或其他板型的接线。

---

## 2. 核心配置逻辑对照

进行单板原理图设计前，先阅读 [[Evidence/k3_strap_pins_config]] 的两份原表与冲突说明；争议项不能作为已确认的接线参数。

### 2.1 启动介质（Boot Mode）
两份来源均通过 **GPIO66 / GPIO65** 配置次级启动介质，并优先尝试 SD/TF：
*   `0/0` 对应 **TF/SD Card → eMMC**，`1/1` 对应 **TF/SD Card → UFS**。
*   **SPI 选择冲突**：硬件指南 §1.1.5 写 `1/0 → SPI NOR`、`0/1 → SPI NAND`；数据手册 §2.11.2 写 `1/0 → SPI NAND`、`0/1 → SPI NOR`。不能单方面采用其中一套或按文档日期裁决；接线与电阻实现须等待官方确认或对应板型经审定原理图。

### 2.2 烧录与启动切换（Boot / Download）
*   **GPIO69** 是决定单板是“正常工作”还是“进入烧录”的开关：
    *   **正常运行**：功能表 GPIO69 为 `0`，具体上下拉接线按原理图。
    *   **出厂烧录**：GPIO69=`1` 进入下载模式，仍由 GPIO68 选择通道：`0` 为 USB、`1` 为 UART。GPIO69=`1` 本身不能保证一定走 USB；电平实现按板型原理图核对。

### 2.3 核心板强制刷机 (Recovery) 与升级限制
对于基于 K3 核心板（如 CoM260）的设计：
*   **强制刷机 (Recovery)**：核心板第 214 引脚为 `FORCE_RECOVERY`。在开发或量产时，将该引脚**下拉到 GND 状态后上电**，系统将强制进入 USB 刷机模式。
*   **MMC 边界**：芯片指南 1.4.4 说明 MMC1 支持 SD 卡完整功能和动态电压切换；MMC2 只支持固定电平下的低速模式或仅 1.8V SD 卡。启动/升级还须核对核心板与 ROM 的支持，不能把该限制表述为 MMC2 完全不能接 SD 卡。

### 2.4 GPIO 双电压自适应设计
K3 芯片的 GPIO 电平支持 1.8V 与 3.3V 自适应切换：
*   **电压参考**：`VCC18_GPIOx` 是 IO 内部 LDO 的参考基准，固定为 1.8V。
*   **工作电平**：GPIO 的实际工作电平由其供电引脚 `VCCxx_1833GPIOx` 决定。当其接入 1.8V 时，该组 GPIO 电平自动为 1.8V；当其接入 3.3V 时，电平自动为 3.3V。**该自适应电平切换完全由硬件决定，无需软件进行任何寄存器配置**。
*   **中断输入限制**：并非所有 IO 都支持中断输入，**仅复用为 GPIO 属性的引脚**才具备中断输入和唤醒功能。

### 2.5 LPDDR 64-bit 物理连线红线
*   **设计红线**：K3 芯片支持 LPDDR5 和 LPDDR4x。当设计中采用 64-bit 位宽的 DDR 拓扑时，**绝对不能仅使用其中的 32-bit 而将另外 32-bit 悬空**。必须保证 64-bit 物理连线完整，否则内存控制器将无法正确初始化。

### 2.6 JTAG 调试连接与 CoM260 交叉接线注意事项

> [!WARNING]
> **2026-08 官方更新**：Spacemit 官方在 `docs-chip` 仓库的 `k3_hw_faq.md` 中新增了 K3 Pico-ITX 和 K3 CoM260 的 JTAG 调试接线详细说明。

*   **K3 Pico-ITX 调试**：串口线 TX 接 K3 Pico-ITX 的 RX，RX 接 TX。串口调试要求使用 **3.3V** 电平串口线。PRI JTAG 直接连接即可。
*   **K3 CoM260 JTAG 调试红线**：CoM260 开发套件支持通过 TF 卡接口转 JTAG 进行调试。**特别注意：JTAG 调试器与转接子板的 TMS 和 TDI 需要交叉连接（TDO 直连）**。误接将导致 JTAG 完全无法通信。
*   详细接线图片参考官方文档：[K3 硬件 FAQ - JTAG 调试图解](../Sources/docs-chip/zh/key_stone/k3/k3_hw/k3_hw_faq.md)（含 `com260_debug_00.png` 配图）

---

## 3. 关联原始参考文档

关于具体的 Strap Pin 电阻选型、PMIC 上电时序以及烧录软件的操作，请进一步参阅：
*   [K3 硬件设计指南 - 原始文档](../Sources/docs-chip/zh/key_stone/k3/k3_hw/k3_hw_design_guide.md)
*   [K3 数据手册 §2.11.2 - SPI 启动选择冲突对照](../Sources/docs-chip/zh/key_stone/k3/k3_docs/k3_ds.md)
*   [K3 SDK 使用指南 - 原始文档](../Sources/docs-chip/zh/key_stone/k3/k3_sw/k3_sdk_user_guide.md)
