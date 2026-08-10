---
type: evidence
title: "K1/K3 显示系统与多媒体输出物理规格"
claim_type: "parameter"
verification_status: unverified
status: needs_review
external_use: false
source_file: "root_overview.md"
created: 2026-06-29
updated: 2026-06-29
aliases: ["K1/K3显示规格参数", "K1 K3 Display Resolution and Codec Specs", "k1_k3_display_specs"]
domain: chip_product_specs
target_audience: [显示驱动工程师, 硬件工程师]
---
# K1/K3 显示系统与多媒体输出物理规格

> [!TIP]
> **💡 工程师导读与排坑焦点**：存放 K1/K3 HDMI/DSI 显示分辨率极限、硬解码能力与接口规格。
> **目标读者**：`显示驱动工程师 / 硬件工程师` | **技术领域**：`chip_product_specs`

本文件汇集了 K1 和 K3 芯片在显示接口与多媒体输出方面的芯片级物理规格与极限参数。

## 1. 进迭时空 K1 芯片显示规格
*   **双屏异显能力**：硬件支持双屏异显，最高分辨率可达 **1920 × 1440 @ 60fps**。
*   **物理接口**：
    *   **MIPI DSI**：内置 1 个 MIPI TX PHY，用于对接 LCD 屏。
    *   **HDMI**：内置 1 个 HDMI PHY（支持 HDMI 输出）。
    *   **SPI LCD**：支持 1 线串行外设 SPI 显示接口（使用 `SPILCD_DOUT0` 或 `SPILCD_DIN` 传输数据）。
*   **引脚复用排他性**：液晶屏撕裂效应控制信号 `LCD_TE` **不能**同时用于 SPI_LCD 显示与 MIPI DSI LCD 显示。

## 2. 进迭时空 K3 芯片显示规格
*   **超高清多屏输出**：
    *   支持最高达 **4K @ 60fps** 的高清多屏显示输出。
*   **物理接口支持**：
    *   内置高性能 **HDMI 2.0 / DP 1.4 / MIPI DSI** 接口，能够流畅支持大屏幕及超高清智能终端显示需求。
*   **编解码硬加速**：支持 4K H.265/H.264 等主流高清格式硬件编解码。
