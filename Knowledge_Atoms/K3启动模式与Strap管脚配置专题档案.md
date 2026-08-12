---
type: knowledge_atom
title: "K3 启动模式与 Strap 管脚配置专题档案"
status: needs_review
created: 2026-06-29
updated: 2026-08-10
aliases: ["K3启动模式与Strap配置专题", "K3 Boot Mode and Strap Config Topic", "k3_boot_strap_config"]
domain: hardware_schematic_design
target_audience: [硬件电路工程师, 嵌入式驱动]
---
# K3 启动模式与 Strap 管脚配置专题档案

> [!TIP]
> **💡 工程师导读与排坑焦点**：指导 K3 芯片 Strap Pins 硬件上下拉设计与物理启动介质配置。
> **目标读者**：`硬件电路工程师 / 嵌入式驱动` | **技术领域**：`hardware_schematic_design`

本专题档案汇总了关于 SpacemiT K3 芯片上电初始化、Strap 管脚硬件设计、以及系统启动/烧录模式的配置要点。

---

## 1. 硬件配置核心原则

K3 芯片在复位释放（Reset Release）的瞬间，会通过采样特定的配置管脚（Strap Pins）的电平状态，来决定芯片的启动介质、烧录通道、内存类型和接口电压。

*   **硬件连接要求**：
    *   所有 Strap 管脚在芯片内部默认都有**弱下拉**电阻。因此，若需要配置为 `0`（默认值），在单板设计时该管脚可以**悬空**。
    *   若需要配置为 `1`，必须通过 **4.7kΩ ~ 10kΩ 的强上拉电阻** 连接到对应的 IO 电源域（通常为 VCC18_PMIC 或 3.3V，根据管脚电压域而定）。
    *   **警告**：切勿将 Strap 管脚直接硬连到电源或地，必须通过电阻进行隔离，否则会导致管脚在作为普通 GPIO 使用时发生短路损坏。

---

## 2. 核心配置逻辑对照

进行单板原理图设计时，必须严格对照以下底层参数表（详见事实证据 [[Evidence/k3_strap_pins_config]]）：

### 2.1 启动介质（Boot Mode）
单板设计时，需通过拨码开关或强上拉电阻配置 **GPIO66** 和 **GPIO65**：
*   若从内置的 **eMMC** 启动，双管脚保持悬空（`0 0`）即可。
*   若设计为使用 **SPI NAND** 启动，必须在 **GPIO65** 上拉 10kΩ 电阻（`0 1`）。

### 2.2 烧录与启动切换（Boot / Download）
*   **GPIO69** 是决定单板是“正常工作”还是“进入烧录”的开关：
    *   **正常运行**：GPIO69 保持悬空（`0`）。
    *   **出厂烧录**：将 GPIO69 上拉到高电平（`1`），芯片上电后将自动进入下载模式，等待通过 USB 接口烧录固件。

### 2.3 核心板强制刷机 (Recovery) 与升级限制
对于基于 K3 核心板（如 CoM260）的设计：
*   **强制刷机 (Recovery)**：核心板第 214 引脚为 `FORCE_RECOVERY`。在开发或量产时，将该引脚**下拉到 GND 状态后上电**，系统将强制进入 USB 刷机模式。
*   **固件升级限制**：固件升级必须使用 **MMC1** 通道（核心板自带的 TF 卡接口），**MMC2 接口不支持 TF 卡固件升级**，亦不能作为普通 SD 卡存储引导接口。

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
*   [K3 SDK 使用指南 - 原始文档](../Sources/docs-chip/zh/key_stone/k3/k3_sw/k3_sdk_user_guide.md)
