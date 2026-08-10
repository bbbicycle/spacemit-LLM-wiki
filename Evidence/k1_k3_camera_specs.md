---
type: evidence
title: "K1/K3 摄像系统与图像输入物理规格"
claim_type: "parameter"
verification_status: unverified
status: needs_review
external_use: false
source_file: "k1_hw_design_guide.md"
created: 2026-06-29
updated: 2026-06-29
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
*   **MIPI CSI RX 通道**：
    *   支持多路 MIPI CSI 接口输入，典型配置为 **2 × MIPI CSI 4-Lanes** 与 **2 × MIPI CSI 2-Lanes**。
*   **多摄像头支持**：
    *   支持最多 **4 个摄像头（四摄）同时接入**。
    *   升级版图像信号处理器（ISP）支持更强的多路并发实时处理与低延迟硬件降噪。
*   **智能视觉硬件加速**：配合 256bit RVV 1.0 向量加速，可实时处理多路 AI 视觉算法。
