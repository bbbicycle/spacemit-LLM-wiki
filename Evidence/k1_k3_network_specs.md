---
type: evidence
title: "K1/K3 网络通信与网口物理规格"
claim_type: "parameter"
verification_status: unverified
status: needs_review
external_use: false
source_file: "k1_hw_faq.md"
created: 2026-06-29
updated: 2026-06-29
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
*   **以太网控制器**：同样集成 **2 路千兆级以太网 MAC**，支持标准 `RGMII` 与外部 PHY 芯片进行对接。
*   **无线连接接口 (Wi-Fi / BT)**：
    *   内置高性能 **SDIO 3.0** 通道（用于高带宽 Wi-Fi 6 传输）以及 **UART/PCM** 接口（用于蓝牙音频与数据传输）。
    *   支持通过 PCIe 扩展高性能工业级无线网卡。
*   **网络数据硬加速**：支持以太网数据包硬件校验和分流，降低大流量下的 CPU 占用率。
