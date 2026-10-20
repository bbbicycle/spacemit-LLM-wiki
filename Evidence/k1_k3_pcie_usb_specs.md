---
type: evidence
title: "K1/K3 高速外设接口物理规格"
claim_type: "parameter"
status: "needs_review"
verification_status: unverified
external_use: false
source_file: "Sources/docs-chip/zh/key_stone/k1/k1_docs/root_overview.md"
source_origin: "https://github.com/spacemit-com/docs-chip"
source_commit: "1ea15a766287024a5bb7b548850826e3525a80dc"
source_section: "特性"
source_resolution: partial
source_checked_at: 2026-10-13
source_note: "K3 UFS 2.2 与 PCIe/USB Combo 已据补充来源的 1.1.9 和 1.4.1 修正；其余扩展芯片兼容细节尚未逐项核验。"
source_related_file: ["Sources/docs-chip/zh/key_stone/k3/k3_hw/k3_hw_design_guide.md"]
source_related_commit: ["1ea15a766287024a5bb7b548850826e3525a80dc"]
created: 2026-06-29
updated: "2026-10-20"
aliases: ["K1/K3 PCIe与USB规格参数", "K1 K3 PCIe and USB Specs", "k1_k3_pcie_usb_specs"]
domain: chip_product_specs
target_audience: [高速接口工程师, 硬件工程师]
---
# K1/K3 高速外设接口物理规格

> [!TIP]
> **💡 工程师导读与排坑焦点**：存放 PCIe 2.1/3.0 通道拆分、USB OTG 复用及 SATA 免驱芯片规格。
> **目标读者**：`高速接口工程师 / 硬件工程师` | **技术领域**：`chip_product_specs`

本文件汇集了 K1 和 K3 芯片在 PCIe 链路、USB 3.0/2.0 通道以及外接存储拓展（SATA等）方面的芯片级物理规格与电气限制。

## 1. 进迭时空 K1 芯片高速接口规格
*   **PCIe 2.1 链路**：集成 **5 Lanes** 的 PCIe 2.1 物理通道，每通道最大速率为 **5 Gbps**。硬件支持灵活通道拆分：
    *   `x2 + x2 + x1` 组合。
    *   **1 槽独立 Lane 选择限制**：当配置为单 Lane（1 Lane）工作时，必须选择使用 `TX0N/P` 和 `RX0N/P` 通道，其余通道不能单独作首通道使用。
*   **USB 接口**：
    *   **USB 3.0**：集成 1 个 USB 3.0 通道（与 PCIe 2.1 的第 5 个 x1 通道进行引脚复用，即二选一）。
    *   **USB 2.0**：集成 2 个独立的 USB 2.0 接口。`USB0` 默认作为 Device 用于系统固件烧录，同时也支持 Host 模式；`USB2` 接口支持 OTG 主从切换，但不支持烧录。
*   **SATA 接口扩展**：
    *   **扩展限制**：K1 SoC 内部没有直接集成的 SATA 控制器。
    *   **物理桥接方案**：支持通过 PCIe 桥接 SATA，系统已默认集成了 **ASM1061** 和 **JMB582** 两种 PCIe 转 SATA 桥接芯片的驱动。

## 2. 进迭时空 K3 芯片高速接口规格
*   **PCIe 接口升级**：
    *   支持高性能 **PCIe 3.0** 接口，物理通道带宽是 K1 (PCIe 2.1) 的两倍，支持高速固态硬盘（NVMe SSD）的极致读写。
*   **USB 3.0 / USB 2.0**：
    *   支持 **4 个 USB 3.0** 和 **5 个 USB 2.0** 接口，其中 **3 个 USB 3.0 与 PCIe Combo 复用**、**4 个 USB 2.0 与 USB 3.0 Combo 复用**；另有 1 个独立 USB 2.0 Host。具体可同时使用的组合须按 K3 硬件设计指南 1.4.1 核对。
*   **UFS 与 eMMC 接口**：
    *   支持 **eMMC 5.1** 与 **UFS 2.2**；UFS 版本依据 K3 硬件设计指南 1.1.9，不应写为 UFS 3.1。
