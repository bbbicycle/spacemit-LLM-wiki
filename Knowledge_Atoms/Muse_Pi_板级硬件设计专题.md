---
type: knowledge_atom
title: "MUSE Pi / Pro 板级硬件设计与调试专题档案"
status: needs_review
created: 2026-06-30
updated: 2026-06-30
aliases: ["Muse Pi 板级硬件设计专题", "Muse Pi Board Hardware Design Topic", "muse_pi_hw_design"]
domain: hardware_schematic_design
target_audience: [硬件电路工程师, 嵌入式工程师]
---
# MUSE Pi / Pro 板级硬件设计与调试专题档案

> [!TIP]
> **💡 工程师导读与排坑焦点**：详解 Muse Pi/Pro 12V PD 供电电路、Strap 拨码与 UART 调试复用设计。
> **目标读者**：`硬件电路工程师 / 嵌入式工程师` | **技术领域**：`hardware_schematic_design`

本专题档案汇总了基于 SpacemiT K1 芯片的生态旗舰开发板 MUSE Pi 与 MUSE Pi Pro 的板级硬件设计、供电规范、启动选择（Strap Pin）以及调试复用设计。

---

## 1. 电源输入与 PD 供电规范

MUSE Pi 系列板卡采用 **USB Type-C 单电源输入**方案：
* **供电协议**：必须使用支持 **USB PD 3.0** 协议的适配器。
* **电压与电流**：输入电压默认通过前端协议芯片调节为 **12V**，额定电流需达到 **3A**（即 36W 及以上）。
* **板级电源拓扑**：
  * 12V 适配器输入首先经过前端降压变换器（Buck）转换为 `VCC5V0_SYS` 与 `VCC4V0`。
  * `VCC4V0` 供给主 PMIC（[[Evidence/p1_pmic_specs|Power Stone P1]]）及外挂 DCDC。
  * `VCC5V0_SYS` 负责给大电流外设（如 M.2 扩展槽的 3.3V 供电）提供前端降压。

> [!WARNING]
> 严禁使用普通 5V 手机充电器为 MUSE Pi 供电，否则会导致板载大功率外设（如 M.2 SSD 或 Wi-Fi 模组）满载时系统因欠压强行复位。

---

## 2. 启动模式配置 (Strap Pins)

MUSE Pi 通过板载双位拨码开关（Strap Pins）选择上电时的第一启动介质。

### 拨码配置与启动顺序：
* **开关 1 (OFF) + 开关 2 (OFF)**：`TF Card` ➡️ `eMMC`（出厂默认配置，适合日常开发与Bianbu系统运行）。
* **开关 1 (ON) + 开关 2 (OFF)**：`TF Card` ➡️ `SPI NOR Flash`（SPI NOR 默认配置为加载 SSD 上的内核）。

### 启动避坑红线：
1. **TF 卡优先权**：无论拨码开关处于何种状态，**只要设备中插入了写有引导固件的 TF 卡，系统一律强制优先从 TF 卡启动**。
2. **刷机默认路径**：刷机时，固件会默认烧录到当前拨码开关所指向的介质中。例如：若拨码配置为从 SPI NOR 启动，则固件会被烧录到 SPI NOR 和 SSD（SSD 必须安装在 **M.2 一号槽位**）。

---

## 3. 调试与复用设计 (JTAG / UART)

为了最大化利用 K1 芯片的管脚，MUSE Pi 采用了高度复用的调试设计。

### 3.1 调试串口 (UART)
* **X60 计算核调试**：引出于板载专属 **3-Pin 单排插针 (J25)**，引脚顺序为 `TX (GPIO68)`、`RX (GPIO69)`、`GND`。电平为 **3.3V**，波特率 **115200**。
* **RCPU 实时核调试**：引出于 26-Pin 扩展排针的 **Pin 6 (GND)、Pin 8 (TX)、Pin 10 (RX)**。

### 3.2 JTAG 调试复用
* **Primary JTAG (主调试口)**：直接引出于 26-Pin 扩展排针，引脚为：
  * Pin 7: `PRI_TDI`
  * Pin 11: `PRI_TMS`
  * Pin 13: `PRI_TCK`
  * Pin 15: `PRI_TDO`
* **Secondary JTAG (SEC2 调试口)**：与 **MMC1 (TF Card) 接口复用**。
  * **启用方法**：当 `JTAG_SEL` 信号拉高，且 `MMC1_CMD` 拉低时，TF 卡插槽引脚将被重配置为 SEC2 JTAG 调试接口，用于调试 X60 核心。
  * **引脚映射关系**：
    * `MMC1_CLK` ➡️ `SEC2_TCK`
    * `MMC1_DATA0` ➡️ `SEC2_TRSTn`
    * `MMC1_DATA1` ➡️ `SEC2_TDO`
    * `MMC1_DATA2` ➡️ `SEC2_TDI`
    * `MMC1_DATA3` ➡️ `SEC2_TMS`

---

## 4. 关联事实证据与芯片专题

* 物理规格对比：[[Evidence/muse_pi_vs_pi_pro_specs|Muse Pi 与 Muse Pi Pro 物理规格对比]]
* 板级扩展管脚映射：[[Knowledge_Atoms/MUSE_Pi_26Pin_IOMAP管脚映射专题|MUSE Pi 26-Pin IOMAP 管脚映射专题]]
* 芯片级启动机制：[[Knowledge_Atoms/K1启动模式与Strap管脚配置专题档案|K1 启动模式与 JTAG 路由专题]]
* 板级供电配合：[[Knowledge_Atoms/SpacemiT生态板卡与PMIC电源配合专题档案|SpacemiT 生态板卡与 PMIC 电源配合专题]]
* 原始文档参考：[MUSE Pi 用户指南](file:///Users/bicycle/Spacemit%20LLM%20Wiki/Sources/docs-product/zh/k1_muse_pi/pi_user_guide.md)
