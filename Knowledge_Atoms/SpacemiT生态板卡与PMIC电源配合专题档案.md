---
type: knowledge_atom
title: "SpacemiT 生态板卡与 PMIC 电源配合专题档案"
status: needs_review
created: 2026-06-29
updated: 2026-08-12
aliases: ["SpacemiT生态板卡与PMIC电源配合专题", "SpacemiT Board and PMIC Power Matching Topic", "spacemit_pmic_matching"]
domain: hardware_schematic_design
target_audience: [电源电路工程师, PCB Layout]
---
# SpacemiT 生态板卡与 PMIC 电源配合专题档案

> [!TIP]
> **💡 工程师导读与排坑焦点**：详解 K1/P1 与 K3/P1S 动态反馈 DVFS 调压、P3 高性能 32A Buck 拓扑、SW/FB 布线与闹钟开机避坑。
> **目标读者**：`电源电路工程师 / PCB Layout` | **技术领域**：`hardware_schematic_design`

本专题档案打破芯片与单板的边界，梳理了 K1 芯片与 PMIC P1、K3 芯片与 PMIC P1S/P3 的供电与上下电配合设计，并对比了生态开发板 Muse Pi 与 Muse Pi Pro 的硬件设计差异。

---

## 1. 伴随电源管理 (PMIC P1/P1S/P3) 配合设计

### 1.1 远端反馈动态调压 (DVFS)
为了实现极佳的能效比，K1 的 `VDD09_CORE` 电源必须配合 PMIC P1 进行动态调压：
*   **物理环路设计**：
    *   反馈信号 `VDD09_CORE_B_FB` 必须直接从 K1 芯片主控球脚（Ball）引出，连接到 PMIC P1 的反馈端。
    *   反馈地 `VDD09_CORE_B_FBGND` 必须从主控的 `VSS_FB` 引出，并在 PCB 走线时**严格远离高频干扰源**，以确保电压采样的精确性。
*   **上下电时序控制**：Core 电源、DDR 电源与 GPIO IO 电源的上下电时序必须严格遵循 PMIC P1 的内部固化时序，外部无需分立延时电路。

### 1.2 高性能大电流供电扩展（P3 PMIC）
针对高算力芯片 Core 或大电流计算场景，SpacemiT 推出全新的四相降压 PMIC **P3**：
*   **32 A 大电流支持**：支持 4+0、3+1、2+2 等 5 种相位组合，详情参阅知识档案 [[Knowledge_Atoms/SpacemiT_P3_PMIC电源芯片专题档案|SpacemiT P3 PMIC 电源芯片专题档案]]。

### 1.3 PMIC P1 调压避坑
*   **RTC 定时开机**：P1 PMIC 具备 RTC 闹钟自动开机功能（精度参见 [[Evidence/k1_hardware_debug_parameters]]）。当系统处于关机且电池有电的状态时，若定时时间到达，P1 会自动拉高启动，无需外部中断信号。
*   **开关管未开启导通问题**：P1 集成的 SW 开关在未开启时，会通过内置 MOS管的体二极管微弱导通。这属于设计已知特性，通流极弱。为确保外设稳定工作，**在软件中必须显式写入寄存器开启该 SW**。

### 1.4 PMIC P1/P1S PCB 布局布线规范
为了保障高电流 BUCK 轨的输出电压稳定、降低高频电磁干扰，在 PCB 设计中必须严格遵守以下 Layout 规范：
*   **输入滤波电容 (Cin) 摆放**：
    *   **单面贴片**：Cin 必须与相应的 Vin 引脚**垂直放置**并尽量就近摆放，以使输入电流回路尽可能短。
    *   **双面贴片**：若 Cin 放在底层，必须与相应的 Vin 引脚**平行放置**，且 Cin 的 GND 端必须**指向芯片的中心裸露焊盘 (EPAD)**。
*   **BUCK VIN 轨隔离**：Buck1/Buck2、Buck3/Buck4、Buck5/Buck6 的 Vin 走线（铜箔）在顶层/底层必须完全分开，且其 Cin 电容必须各自独立，防止相间串扰。
*   **SW 开关节点走线**：SW 走线**必须且只能在表层（顶层）进行**，严禁打过孔走内层。SW 电感下面表层铺铜应挖空，而内层（L2 地层）应保留。
*   **电感与输出电容 (Cout)**：
    *   电感应尽量**垂直摆放**（若平行摆放，间距需大于 2 mm），以减小相互磁场干扰。
    *   Cout 应紧贴电感摆放，就近打孔（推荐每路各打 6 个及以上 0.25/0.5mm 过孔）至内层 GND。
*   **远端反馈网络 (FB)**：反馈走线必须从**最外侧（靠近负载、远离芯片）**的 Cout 焊盘拉回至芯片引脚，严禁在电感下方或 SW 走线附近走反馈线，避免引入高频纹波干扰。
*   **电源层设计**：PCB 第二层必须作为**完整地平面 (GND)**，不走任何信号线。第三层作为 VIN 输入层，Vin 铜箔应绕过芯片 EPAD 呈**环形铺铜**，为 Cin 提供完整的回流路径。EPAD 需打 7x7 的散热过孔。

### 1.5 模拟供电磁珠隔离与测流电阻合并规则
在设计芯片外围供电电路时，必须严格区分“功能滤波器（磁珠）”与“调试测流电阻”：
*   **模拟与数字电源隔离**：原理图中为模拟 PHY（如 AVDD、PLL、Audio、CSI/DSI 等）与数字 IO 供电之间设计的**隔离磁珠（如 120Ω@100MHz）绝对不能省略或直接合并走线**。磁珠能阻断数字高频噪声耦合到敏感的模拟电路上。若省略，将直接导致外设性能下降甚至无法正常初始化。
*   **测试测流电阻短接**：参考设计中为测量各路电源功耗而星形连接的多级测流电阻，在实际量产或无需测流的板卡设计中，**可以直接删除并进行短接合并**，直接连接到主电源层。
*   **DSI / CSI 闲置供电要求**：即使单板设计中**完全不使用 DSI 显示或 CSI 摄像头**，SoC 上的 DSI/CSI 模块引脚电源域**仍然必须接通 1.8V 供电**，绝对不能悬空，否则会导致芯片内部产生漏电，影响整机功耗与可靠性。

---

## 2. 生态开发板对比与固件适配 (Muse Pi vs Muse Pi Pro)

基于 K1 芯片开发的 Muse Pi 与 Muse Pi Pro 在接口设计上存在明确的硬件差异（参见 [[Evidence/muse_pi_vs_pi_pro_specs]]）：
*   **双网口与 4G 扩展**：
    *   `Muse Pi (标准版)`：仅引出了 1 个千兆网口，未板载任何通信插槽。
    *   `Muse Pi Pro (高级版)`：引出了 **双千兆网口**，且板载了 **Mini PCIe 4G/5G 模组插槽与 Micro SIM 卡槽**，适合做软路由或边缘物联网关。
*   **固件适配注意事项**：
    *   由于两款开发板的外设配置不同，在编译 Linux/Bianbu OS 镜像时，必须在编译脚本或 U-Boot 阶段配置不同的 **DTB (设备树)** 文件（如 `k1-x_muse_pi.dtb` 或 `k1-x_muse_pi_pro.dtb`），否则双网口或 4G 模组将无法正常工作。

---

## 3. 关联事实证据与参考源

> [!NOTE]
> **2026-08 官方更新**：P1 Datasheet 已更新至 **V2.1**（2026.05.21），主要变更为“更新寄存器描述”。其中 5.3 节 `Digital I/O Electrical Characteristics` 详细列出了 I/O 输入/输出电气特性参数（包括 V(IH)/V(IL)/V(OH)/V(OL) 及弱上拉/下拉电阻值）。
> **2026-08 官方新增**：Power Stone 系列新增高性能四相降压 PMIC P3 芯片，详见 [[Knowledge_Atoms/SpacemiT_P3_PMIC电源芯片专题档案]]。

*   PMIC 芯片规格：[[Evidence/p1_pmic_specs|P1 PMIC 核心规格]]，[[Evidence/p1s_pmic_specs|P1S PMIC 核心规格]]
*   物理参数对比表：[[Evidence/muse_pi_vs_pi_pro_specs|Muse Pi 与 Muse Pi Pro 对比表]]
*   [K1 硬件常见问题 FAQ - 原始文档](../Sources/docs-chip/zh/key_stone/k1/k1_hw/k1_hw_faq.md)
*   [P1 产品简介 - 原始文档](../Sources/docs-chip/zh/power_stone/p1/p1_docs/root_overview.md)
*   [P1 硬件设计指南 - 原始文档](../Sources/docs-chip/zh/power_stone/p1/p1_hw/p1_pcb_guide.md)
*   [P3 产品简介 - 原始文档](../Sources/docs-chip/zh/power_stone/p3/p3_docs/root_overview.md)

