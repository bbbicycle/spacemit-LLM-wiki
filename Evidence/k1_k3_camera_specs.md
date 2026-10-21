---
type: evidence
title: "K1/K3 摄像系统与图像输入物理规格"
claim_type: "parameter"
status: "needs_review"
verification_status: unverified
external_use: false
source_file: "Sources/docs-chip/zh/key_stone/k1/k1_hw/k1_hw_design_guide.md"
source_origin: "https://github.com/spacemit-com/docs-chip"
source_commit: "1ea15a766287024a5bb7b548850826e3525a80dc"
source_section: "1.3.3 MIPI CSI RX 配置接口设计"
source_resolution: partial
source_checked_at: 2026-10-21
source_note: "2026-10-21 阶段 B：K3 指南 1.3.2 的 12 Lane 组合；修正物理输入与 ISP 软件并发的混用，不承诺未定位的降噪/低延迟指标。 保持 unverified/needs_review；不表示全文事实通过。"
source_related_file: ["Sources/docs-chip/zh/key_stone/k3/k3_hw/k3_hw_design_guide.md"]
source_related_commit: ["2525ee3b68e0f4864f1bf12c8a59df040bf27e84"]
created: 2026-06-29
updated: 2026-10-21
aliases: ["K1/K3摄像与ISP规格参数", "K1 K3 Camera and ISP Specs", "k1_k3_camera_specs"]
domain: chip_product_specs
target_audience: [ISP图像工程师, 硬件工程师]
---
# K1/K3 摄像系统与图像输入物理规格

> [!TIP]
> **💡 工程师导读与排坑焦点**：存放 K1/K3 MIPI CSI RX 通道组合及 ISP 并发硬加速处理限制。
> **目标读者**：`ISP图像工程师 / 硬件工程师` | **技术领域**：`chip_product_specs`

本文件汇集了 K1 和 K3 芯片在摄像头输入（MIPI CSI）以及图像信号处理器（ISP）方面的物理引脚组合与并发处理能力。

## 1. 进迭时空 K1 芯片摄像规格
*   **MIPI CSI RX 通道**：共支持 **8 Lanes** 差分输入，硬件可灵活配置为：
    *   `4 Lanes + 4 Lanes` 或 `4 Lanes + 2 Lanes + 2 Lanes`。
*   **摄像头并发限制**：
    *   在 `4+2+2` 模式下，**物理上支持三摄同时出图**。
    *   **ISP 管道限制**：芯片内置 ISP **仅能同时处理两路图像**。
    *   **第三路规避方案**：剩余的第 3 路摄像头必须为 `YUV` 或 `RAW` 格式，不能经过 ISP，只能通过内置的 **CCIC DMA** 模块将原始图像数据直接 dump 到 DDR 内存中。
*   **单摄最高分辨率**：最大支持 **16 MP** 摄像头输入。

## 2. 进迭时空 K3 芯片摄像规格
*   **MIPI CSI RX 通道**：K3 硬件设计指南 1.3.2 给出 **12 Lanes**，支持 `4+4+4` 或 `4+4+2+2` 输入。
*   **时钟关系**：CSI2 的 D2/D3 在 2-Lane 模式参考 CSI3 时钟，D0/D1 参考 CSI2 时钟；4-Lane 模式统一参考 CSI2 时钟。具体连接须核对该节原图。
*   **边界**：四路物理输入不等于四路 ISP/AI 并发性能保证；本轮未定位此前“低延迟降噪”和具体 AI 并发指标的证据，不能从 Lane 数推导。K3 A100 的 RVV 位宽也不能套用 K1 X60 的值。
