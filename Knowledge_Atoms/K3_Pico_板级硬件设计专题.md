---
type: knowledge_atom
title: "K3 Pico-ITX 板级硬件设计与调试专题档案"
status: needs_review
created: 2026-06-30
updated: 2026-10-07
aliases: ["K3 Pico 板级硬件设计专题", "K3 Pico Board Hardware Design Topic", "k3_pico_hw_design", "K3 Pico产品特点", "K3 Pico单板计算机", "k3_pico_profile"]
domain: hardware_schematic_design
target_audience: [硬件电路工程师, 系统工程师, 产品经理]
---
# K3 Pico-ITX 板级硬件设计与产品特点专题档案

> [!TIP]
> **💡 工程师与产品架构师导读**：
> 本文系统汇总了旗舰级 2.5 寸单板 AI 计算机 **K3 Pico-ITX** 的产品定位、核心差异化卖点、板级供电优先级、高速 PCIe 带宽仲裁机制及实时控制接口设计。
> 快速掌握产品全貌请阅读第 0 节，深入硬件布线请阅读第 1~4 节。

---

## 0. 产品定位与四大核心卖点 (Product Profile)

### 0.1 一句话产品定位
> **K3 Pico-ITX** 是一款专为**具身机器人与边缘工业智算**打造的旗舰级迷你 AI 单板计算机（SBC），在 2.5 寸硬盘大小内融合了 60 TOPS AI 算力、统一内存架构与万兆光纤网络，支持全功能 Type-C 单线点亮。

### 0.2 四大杀手级核心特点
1. **全功能 Type-C 单线点亮 (Single-Cable Deployment)**：
   * 仅需一根全功能 Type-C 线缆连接支持反向供电的显示器，即可同时完成 **65W PD 高功率供电** 与 **4K@60Hz DP 高清视频输出**，展会与实机部署一插即亮，告别繁杂线束。
2. **60 TOPS 统一内存大模型推理 (Unified Memory for Edge LLM)**：
   * 基于 K3 芯片计算核与智算核同构融合架构，板载双通道 64-bit LPDDR5 (6400 MT/s) 与高速 UFS 2.2 本地存储（读取速率比同类 eMMC 提升 3.4 倍），本地可直接部署 **30B MoE 稀疏大模型**（如 Qwen3-30B-A3B，激活约 3B）或 8B 稠密大模型，无显存搬运损耗。
3. **板载万兆光纤直连 (10G SFP+ Optical Port)**：
   * 突破传统嵌入式单板仅配千兆网的瓶颈，板载 1 路万兆 SFP+ 光口（支持 10G BASE-R / BASE-X），为机器视觉高速图传、低延迟工业以太网及多板阵列组网提供超大带宽。
4. **RT24 微秒级实时运动控制直出 (Real-Time Motion Control)**：
   * 专设 FPC 柔性连接器，由芯片内部独立的实时微控制器 **RT24** 物理引脚直出，原生支持 **EtherCAT、5 路 CAN-FD、SPI、UART**，无需外挂从控 MCU，单板同时跑通“多模态大模型大脑 + 微秒级机械臂控制小脑”。

### 0.3 选型定位：K3 Pico vs K3 CoM260
* **选 K3 Pico 的场景**：需要标准化单板形态、追求开箱即用、机壳紧凑（2.5寸）、需万兆光网直连或快速样机验证（如送检样机、极客桌面工作站、机器人整机）。
* **选 K3 CoM260 的场景**：终端客户需要客制化外形、需要量产底板定制、需引出更多特殊工业总线或对接口位置有严苛物理约束的场景（详见 [[Knowledge_Atoms/K3_COM260_板级硬件设计专题|K3 CoM260 专题]]）。

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
