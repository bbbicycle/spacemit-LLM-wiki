---
type: knowledge_atom
title: "K1 启动模式与 Strap 管脚配置专题档案"
status: needs_review
created: 2026-06-29
updated: 2026-06-29
aliases: ["K1启动模式与Strap配置专题", "K1 Boot Mode and Strap Config Topic", "k1_boot_strap_config"]
domain: hardware_schematic_design
target_audience: [硬件电路工程师, 嵌入式驱动]
---
# K1 启动模式与 Strap 管脚配置专题档案

> [!TIP]
> **💡 工程师导读与排坑焦点**：指导 K1 芯片上电采样阻值计算、JTAG/UART 物理复用与防挂死布局。
> **目标读者**：`硬件电路工程师 / 嵌入式驱动` | **技术领域**：`hardware_schematic_design`

本专题档案汇总了关于 SpacemiT K1 芯片上电初始化、Strap 管脚硬件设计、以及启动/烧录模式的配置要求。

---

## 1. 硬件配置与阻抗原则

K1 芯片在复位释放（Reset Release）瞬间，会通过采样特定的硬件配置管脚（Strap Pins 0 ~ 5）的电平状态，决定整机的启动介质与工作状态。

*   **弱下拉机制**：Strap 管脚在芯片内部默认带有**弱下拉电阻**。在原理图设计时，若配置值要求为 `0`，管脚通常可以**悬空 (NC)**。
*   **上拉电阻配置**：若需要配置为 `1`，必须使用 **4.7kΩ ~ 10kΩ 的强上拉电阻** 连接到对应的 IO 电源域（VCC1833_QSPI 或 VCC18_GPIO，视引脚电源域而定）。
*   **红线警告**：**严禁将 Strap 管脚直接短接至电源或 GND**。因为上电完成后，这些引脚会复用为 QSPI 数据线或 GPIO，若没有电阻隔离，会造成大电流器件短路烧毁。

---

## 2. 核心启动与烧录对照

进行原理图与 PCB 走线时，必须严格对照物理对照表（详见事实证据 [[Evidence/k1_strap_pins_config]]）：

### 2.1 启动介质配置 (Strap 0 & 1)
通过 **QSPI_DATA1/Strap1** 和 **QSPI_DATA0/Strap0** 决定启动介质：
*   **eMMC 引导 [默认]**：保持两个管脚悬空（`0 0`）。
*   **SPI NAND 引导**：将 **Strap 1** 上拉，**Strap 0** 悬空（`1 0`）。
*   **SD Card 引导**：将 **Strap 1 & 0** 均上拉 10kΩ （`1 1`）。

### 2.2 启动与下载模式切换 (Strap 3)
*   **QSPI_DATA3/Strap3 FDL** 是烧录模式的控制开关：
    *   **正常启动**：保持悬空（`0`）。
    *   **出厂烧录**：硬件上拉至高电平（`1`），芯片上电后将自动进入下载模式，可通过 USB0/UART0 接口由烧录工具写入镜像。

### 2.3 调试 JTAG 路由 (MMC1_SD_CMD)
*   **X60 AP 核心调试**：保持悬空（`0`）。
*   **N308 RCPU 实时核调试**：需上拉电平（`1`），此时 JTAG 信号将被路由至实时内核。

---

## 3. 关联原始参考文档

关于具体的引脚电压配置、PCB 走线等长与阻抗约束，请进一步参阅：
*   [K1 硬件设计指南 - 原始文档](../Sources/docs-chip/zh/key_stone/k1/k1_hw/k1_hw_design_guide.md)
*   [K1 数据手册 - 原始文档](../Sources/docs-chip/zh/key_stone/k1/k1_docs/k1_ds.md)
