---
type: evidence
title: "SpacemiT 生态板卡 Muse Pi 与 Muse Pi Pro 物理规格对比"
claim_type: "parameter"
status: "needs_review"
verification_status: unverified
external_use: false
source_file: "Sources/docs-product/zh/k1_series/k1_muse_pi/root_overview.md"
source_origin: "https://github.com/spacemit-com/docs-product"
source_commit: "bc640755145625cc20745f49861f82588863fca3"
source_section: "产品规格"
source_resolution: partial
source_checked_at: 2026-10-21
source_note: "2026-10-21 评测定向对照两份产品简介，修正旧表网口、排针、USB 与存储差异；用户指南另证实 Pro 40Pin。仍待人工终审，不保证所有可选配置。"
source_related_file: ["Sources/docs-product/zh/k1_series/k1_muse_pi_pro/root_overview.md"]
source_related_commit: ["bc640755145625cc20745f49861f82588863fca3"]
created: 2026-06-29
updated: "2026-10-21"
aliases: ["Muse Pi对Muse Pi Pro规格对比表", "Muse Pi vs Muse Pi Pro Specs", "muse_pi_vs_pi_pro_specs"]
domain: chip_product_specs
target_audience: [系统选型工程师, 硬件工程师]
---
# Muse Pi 与 Muse Pi Pro 物理规格对比

适用于固定 docs-product 产品简介中的配置，不能由“Pro”命名推断接口更多或与 K3 同代。产品名 K1 MUSE 系列的两份规格表均将处理器写为 **SpacemiT M1**；具体芯片丝印、板卡版本与 SDK 要分别确认。

| 项目 | MUSE Pi | MUSE Pi Pro |
| --- | --- | --- |
| 处理器 | M1，8 核 64 位 RISC-V，融合 2 TOPS AI | M1，融合 2 TOPS AI |
| 内存 | LPDDR4X 2400MT/s，8GB/16GB | LPDDR4X 2400MT/s，8GB/16GB |
| 板载存储 | eMMC 32GB/64GB | eMMC 64GB/128GB |
| NVMe 扩展 | 2×M.2 2280 M-Key | M.2 M-Key，2230 尺寸 |
| 网口 | 2 路 RJ45，1000M/100M | 1 路 RJ45，1000M/100M |
| USB | 1×USB3.0 + 1×USB2.0 Type-A Host，1×USB2.0 Type-C OTG | 4×USB3.0 Type-A Host，1×USB2.0 Type-C Device |
| 扩展排针 | 26-Pin | 40-Pin |
| 无线扩展 | Wi-Fi6、BT5.2 | Wi-Fi6、BT5.2；标准 miniPCIe 支持 4G/5G 等扩展 |
| MIPI | DSI 4lane；CSI 两路4lane，支持4+4/4+2+2 | DSI 2lane；CSI 一路4lane与一路2lane |
| 尺寸 | 129.45×80mm | 85×56mm |
| 供电入口 | USB PD3.0，Type-C OTG 表列12V/3A | USB-PD，5V/3A、9V/3A、12V/3A |

旧表将 Pro 写成双网口/26Pin，以及将两者写成同一 USB 和存储配置，均已撤回。两份简介仅列3.5mm音频接口，不据此承诺 Pro 具有特定功率的板载喇叭功放。JTAG/UART 针脚以对应用户指南和原理图为准。

**状态**：`partial / unverified / needs_review / external_use:false`，来源定位与本轮逐表比对不等于硬件实测或对外批准。
