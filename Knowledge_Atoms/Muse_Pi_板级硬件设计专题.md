---
type: knowledge_atom
title: "MUSE Pi / Pro 板级硬件设计与调试专题档案"
status: "needs_review"
created: 2026-06-30
updated: "2026-10-21"
aliases: ["Muse Pi 板级硬件设计专题", "Muse Pi Board Hardware Design Topic", "muse_pi_hw_design", "Muse Pi产品特点", "Muse Pi Pro", "muse_pi_profile", "MusePi选型"]
domain: hardware_schematic_design
target_audience: [硬件电路工程师, 嵌入式工程师, 产品经理]
source_file: "Sources/docs-product/zh/k1_series/k1_muse_pi/root_overview.md"
source_commit: "bc640755145625cc20745f49861f82588863fca3"
source_locator: "MUSE Pi/Pro 产品规格；Pi 用户指南硬件介绍；其他历史板级细节待复核"
source_resolution: "partial"
verification_status: "unverified"
source_checked_at: "2026-10-21"
source_note: "2026-10-21 评测定向核对两份产品表，撤回旧稿功放与网口/排针错误；主来源由误绑MUSE Box改为MUSE Pi，供电拓扑及其他正文仍未全文核验。"
source_origin: "https://github.com/spacemit-com/docs-product"
source_related_file: ["Sources/docs-product/zh/k1_series/k1_muse_pi/pi_user_guide.md", "Sources/docs-product/zh/k1_series/k1_muse_pi/root_overview.md", "Sources/docs-product/zh/k1_series/k1_muse_pi_pro/root_overview.md", "Sources/docs-chip/zh/power_stone/p1/p1_docs/p1_ds.md"]
source_related_commit: ["bc640755145625cc20745f49861f82588863fca3", "bc640755145625cc20745f49861f82588863fca3", "bc640755145625cc20745f49861f82588863fca3", "1ea15a766287024a5bb7b548850826e3525a80dc"]
---
# MUSE Pi / Pro 板级硬件设计与产品特点专题档案

> [!TIP]
> **💡 工程师与产品选型导读**：
> 本文系统汇总了基于 SpacemiT K1 八核处理器的开源单板计算机 **MUSE Pi** 与 **MUSE Pi Pro** 的产品定位差异、选型决策、12V PD 供电规范、Strap 拨码启动以及调试引脚复用设计。
> 快速掌握选型区别请阅读第 0 节，深入硬件布线请阅读第 1~4 节。

---

## 0. 产品定位与 MUSE Pi vs Pro 差异化选型 (Product Profile)

### 0.1 一句话产品定位
* **MUSE Pi**：产品表列 129.45×80mm、双 RJ45 与双 M.2 2280，适用于按该板接口配置开展原型开发；芯片功耗不等同于整机功耗。
* **MUSE Pi Pro**：产品表列 85×56mm、40-Pin、M.2 2230 与 miniPCIe。连接兼容扩展板前仍需逐针核对复用、电平及驱动，不将物理排针相似当作全面兼容。

### 0.2 标准版 (Muse Pi) 与增强版 (Muse Pi Pro) 核心差异速查

| 核心维度 | MUSE Pi (标准版) | MUSE Pi Pro (增强版) | 选型建议 / 场景决策 |
| :--- | :--- | :--- | :--- |
| **扩展插针规格** | **26-Pin** | **40-Pin** | 按各板用户指南接线 |
| **处理器表述** | 产品表列 M1 | 产品表列 M1 | K1 MUSE 是产品系列名，芯片与板级规格分别确认 |
| **以太网** | 2 路 RJ45 | 1 路 RJ45 | 不能按 Pro 名称推断双网口 |
| **存储与 USB** | 双 M.2 2280；1×USB3.0 Type-A | M.2 2230；4×USB3.0 Type-A | 详细配置及 Type-C 角色见下方 Evidence |
| **音频接口** | 3.5mm耳麦接口 | 3.5mm耳麦接口 | 当前产品表不足以确认旧稿“Pro板载3W功放” |
| **显示与相机** | DSI 4lane、CSI 4+4/4+2+2 | DSI 2lane、CSI 4lane+2lane | 按板型核对连接器，不能套用 SoC 总能力 |
| **系统与镜像** | 按 MUSE Pi 版本核对 | 按 MUSE Pi Pro 版本核对 | 不保证任意镜像或排针配置互换 |

> 💡 *详细物理规格与物料尺寸对比表参阅：[[Evidence/muse_pi_vs_pi_pro_specs|Muse Pi 与 Muse Pi Pro 规格比对表]]*

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

> [!NOTE]
> **2026-08 官方更新**：`docs-product` 仓库中 K1 Muse Box 产品简介页的 PDF 下载链接文件名已修正。若此前下载失败，请重新获取。

* 物理规格对比：[[Evidence/muse_pi_vs_pi_pro_specs|Muse Pi 与 Muse Pi Pro 物理规格对比]]
* 板级扩展管脚映射：[[Knowledge_Atoms/MUSE_Pi_26Pin_IOMAP管脚映射专题|MUSE Pi 26-Pin IOMAP 管脚映射专题]]
* 芯片级启动机制：[[Knowledge_Atoms/K1启动模式与Strap管脚配置专题档案|K1 启动模式与 JTAG 路由专题]]
* 板级供电配合：[[Knowledge_Atoms/SpacemiT生态板卡与PMIC电源配合专题档案|SpacemiT 生态板卡与 PMIC 电源配合专题]]
* 原始文档参考：[MUSE Pi 用户指南](../Sources/docs-product/zh/k1_series/k1_muse_pi/pi_user_guide.md)
* K1 Muse Box 参考：[Muse Box 产品简介](../Sources/docs-product/zh/k1_series/k1_muse_box/root_overview.md)
