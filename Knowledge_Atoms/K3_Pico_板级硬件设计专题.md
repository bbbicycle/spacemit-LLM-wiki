---
type: knowledge_atom
title: "K3 Pico-ITX 板级硬件设计与调试专题档案"
status: needs_review
created: 2026-06-30
updated: 2026-08-10
aliases: ["K3 Pico 板级硬件设计专题", "K3 Pico Board Hardware Design Topic", "k3_pico_hw_design"]
domain: hardware_schematic_design
target_audience: [硬件电路工程师, 系统工程师]
---
# K3 Pico-ITX 板级硬件设计与调试专题档案

> [!TIP]
> **💡 工程师导读与排坑焦点**：详解 K3 Pico 双电源输入优先级、M.2 动态带宽复用与 RT24 直出。
> **目标读者**：`硬件电路工程师 / 系统工程师` | **技术领域**：`hardware_schematic_design`

本专题档案汇总了基于 SpacemiT K3 芯片的旗舰级迷你计算机 K3 Pico-ITX 的板级硬件设计规范、电源优先级、高速 PCIe 带宽复用机制、实时控制直出设计及显示输出逻辑。

---

## 1. 双电源输入与切换优先级

K3 Pico-ITX 支持两种物理电源输入通道，但**不支持热冗余**：
* **输入通道**：
  1. **USB Type-C (全功能口)**：支持 USB-PD 3.0 协议，最大支持 **20V @ 3.25A** (65W) 或以上，推荐 20V @ 5A。
  2. **ATX 2-Pin 接口**：直流 12V 输入，最大支持 **12V @ 7A** (84W)。
* **电源优先级与切换逻辑**：
  * **ATX 优先**：系统上电时，若同时连接了 ATX 和 Type-C PD，系统将**强行优先使用 ATX 供电**。
  * **非热冗余切换（触发重启）**：
    * 当系统处于开机状态，若拔除正在供电的 ATX 电源，系统会**自动重启**，并在重启后无缝切换为 Type-C PD 供电。
    * 当系统由 Type-C PD 供电时，若中途接入 ATX 电源，系统也会**自动重启**，并在重启后切换为 ATX 供电。

> [!CAUTION]
> 由于双电源切换会触发系统硬件重启，因此在进行重要数据读写或部署模型时，切勿插拔任何一路电源。

---

## 2. 高速接口与 M.2 带宽复用机制

为了在紧凑的 Pico-ITX 尺寸内提供极佳的扩展性，K3 Pico-ITX 设计了 PCIe 3.0 链路的动态复用机制：
* **物理槽位**：
  * **M.2 M-Key (2280)**：主要用于扩展高带宽 NVMe SSD。
  * **M.2 B-Key (2242/3042)**：用于扩展低带宽 SSD 或 USB 2.0 4G/5G 模组。
* **带宽复用规则**：
  * **B-Key 空闲**：M.2 M-Key 独享完整的 **PCIe 3.0 x4** 信号链路。
  * **B-Key 占用**：当 M.2 B-Key 插入 PCIe SSD 或其他 PCIe 设备时，B-Key 占用 2 lanes，**M.2 M-Key 的带宽将自动降级为 PCIe 3.0 x2**。

> [!IMPORTANT]
> 1. M.2 B-Key 插槽作为存储扩展时**仅支持 PCIe 协议的 SSD，不支持 SATA 协议的 SSD**。
> 2. M.2 槽位均不支持热插拔，装卸前必须彻底断电。

---

## 3. FPC 实时控制直出设计 (RT24)

K3 Pico-ITX 专为机器人和工业控制设计了外设扩展通道：
* **直出引脚**：板载 26-Pin 和 36-Pin FPC 高速连接器，其信号由 K3 芯片内部的**实时控制核 RT24** 直接引出，绕过了通用大核的操作系统调度，实现微秒级延迟。
* **支持总线**：
  * **26-Pin FPC**：引出 CAN (from RT24) + I2C (from RT24) + UART + PWM 信号。
  * **36-Pin FPC**：引出 GMAC-MII 以太网 (from RT24) + CAN + SPI 信号。支持直接外接 EtherCAT、CAN-FD 工业实时控制扩展板。

---

## 4. 双显示输出逻辑 (eDP / DP)

板卡支持 **Type-C DP** 和 **40-Pin eDP** 双路显示输出：
* **分辨率**：DP 最高支持 4K @ 60Hz；eDP 最高支持 2.5K @ 90Hz。
* **主屏选择逻辑**：
  * 仅接 DP 屏或仅接 eDP 屏：连接的屏幕自动作为主显。
  * **双屏并发连接**：系统默认将 **eDP 屏幕作为主显示器**，DP 屏幕作为副屏扩展。若需更改，必须在操作系统（如 Bianbu OS）的显示设置中手动切换。

---

## 5. 关联事实证据与芯片专题

> [!NOTE]
> **2026-08 官方更新**：K3 硬件资源文件已更新至 **v2.1**，包括 Pin List 与最小系统参考设计原理图。eDP 信号命名已修正。请确保使用最新版本硬件资源进行设计。
*   [K3 硬件资源下载页 (v2.1)](../Sources/docs-chip/en/key_stone/k3/k3_hw/k3_hw_resources.md)

* 物理规格数据：[[Evidence/k3_pico_specs|K3 Pico-ITX 规格参数]]
* FPC扩展管脚映射：[[Knowledge_Atoms/K3_Pico_扩展接口管脚映射专题|K3 Pico 扩展接口管脚映射专题]]
* 芯片级规格：[[Evidence/k1_k3_display_specs|K1/K3 显示与多媒体规格]]
* 网络通道设计：[[Knowledge_Atoms/K1_K3网络通信与千兆网口专题档案|K1/K3 网络通信与千兆网口专题]]
* 原始文档参考：[K3 Pico 用户指南](file:///Users/bicycle/Spacemit%20LLM%20Wiki/Sources/docs-product/zh/k3_pico/pico_user_guide.md)
