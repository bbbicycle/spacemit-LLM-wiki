---
type: evidence
title: "K1/K3 网络通信与网口物理规格"
claim_type: "parameter"
status: needs_review
verification_status: unverified
external_use: false
source_file: "Sources/docs-chip/zh/key_stone/k1/k1_hw/k1_hw_faq.md"
source_origin: "https://github.com/spacemit-com/docs-chip"
source_commit: "2525ee3b68e0f4864f1bf12c8a59df040bf27e84"
source_section: "网络系统"
source_resolution: partial
source_checked_at: 2026-10-21
source_note: "2026-10-21 阶段 B：K1 FAQ 网络系统与 K3 指南 1.4.5：修正 K3 四路 GMAC，RMII/RGMII/MII 不沿用 K1 限制。无线/卸载结论证据不足。 保持 unverified/needs_review；不表示全文事实通过。"
source_related_file: ["Sources/docs-chip/zh/key_stone/k3/k3_hw/k3_hw_design_guide.md"]
source_related_commit: ["2525ee3b68e0f4864f1bf12c8a59df040bf27e84"]
created: 2026-06-29
updated: 2026-10-21
aliases: ["K1/K3以太网与无线网络参数", "K1 K3 Network and Ethernet Specs", "k1_k3_network_specs"]
domain: chip_product_specs
target_audience: [网络驱动工程师, 硬件工程师]
---
# K1/K3 网络通信与网口物理规格

> [!TIP]
> **💡 工程师导读与排坑焦点**：存放双路 GMAC 百兆 PHY 兼容限值、SDIO 无线模组电气参数。
> **目标读者**：`网络驱动工程师 / 硬件工程师` | **技术领域**：`chip_product_specs`

本文件汇集了 K1 和 K3 芯片在以太网 MAC（GMAC）以及无线网络模组接口方面的电气规范与物理参数。

## 1. 进迭时空 K1 芯片网络规格
*   **以太网控制器 (GMAC)**：集成 **2 路千兆 GMAC** 接口，支持 `RGMII` 物理连接，工作速率为 10/100/1000M 自适应。
*   **百兆 PHY 兼容限制**：
    *   **物理红线**：K1 的 GMAC 控制器**不支持纯百兆以太网 PHY 芯片**（即使在 100M 速率下也必须使用千兆级 PHY 芯片）。
    *   **供电要求**：PHY 芯片供电电压必须按其设计连接（通常为 3.3V/1.8V），GMAC0 和 GMAC1 均有独立的电源域控制。
*   **单/双网口软件影响**：系统设计上使用单网口（仅启用 GMAC0 或仅启用 GMAC1）**不会对系统软件运行产生任何功能影响**。

## 2. 进迭时空 K3 芯片网络规格
*   **以太网控制器**：K3 指南 1.4.5 明确为 **4 个 GMAC**，3 路在 ACPU、1 路在 RCPU。
*   **接口组合**：GMAC0/GMAC1 支持 `RGMII / RMII / MII`；GMAC2/GMAC3 支持 `RGMII / RMII`，芯片可提供 25 MHz PHY 时钟。实际板卡引出数与 PHY 支持须按板型核对。
*   **代际边界**：K1 FAQ 的“不能使用纯百兆 PHY”不能直接推广为 K3 的限制。
*   **待核查**：无线模组代际、Wi-Fi 6 吞吐和硬件校验/分流能力未在本轮来源中逐项证实，不承诺上述功能或性能。
