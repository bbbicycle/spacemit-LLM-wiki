---
type: evidence
title: "Spacemit K1 生态衍生终端与实验套件物理规格参数"
claim_type: "parameter"
verification_status: verified
status: "needs_review"
external_use: true
source_tier: tier_1_github_upstream
source_origin: "https://github.com/spacemit-com/docs-product"
source_commit: "8c851807f2c54e8ba54d568b268100ca727d0777"
source_file: "Sources/docs-product/zh/k1_series/k1_muse_paper/root_overview.md"
source_section: "产品规格；其他产品的逐列来源见正文"
source_locator: "MUSE Paper 产品规格，行 39–54"
source_resolution: resolved
source_checked_at: 2026-10-13
conflicts: "MUSE Box简介与规格表USB数量不同；MUSE Shelf特性2/4刀片与规格表4刀片有配置差异，见正文"
verified_at: 2026-10-13
created: 2026-10-07
updated: "2026-10-20"
aliases: ["K1生态终端参数表", "K1 Terminal Products Specs", "k1_terminal_products_specs", "Muse终端规格"]
domain: chip_product_specs
target_audience: [产品架构师, 硬件工程师, 解决方案工程师]
source_related_file: ["Sources/docs-product/zh/k1_series/k1_muse_book/root_overview.md", "Sources/docs-product/zh/k1_series/k1_muse_box/root_overview.md", "Sources/docs-product/zh/k1_series/k1_muse_card/root_overview.md", "Sources/docs-product/zh/k1_series/k1_muse_shelf/root_overview.md", "Sources/docs-product/zh/k1_series/k1_riscv_labkit/root_overview.md"]
source_related_commit: ["8c851807f2c54e8ba54d568b268100ca727d0777", "8c851807f2c54e8ba54d568b268100ca727d0777", "8c851807f2c54e8ba54d568b268100ca727d0777", "8c851807f2c54e8ba54d568b268100ca727d0777", "8c851807f2c54e8ba54d568b268100ca727d0777"]
---

# Spacemit K1 生态衍生终端与实验套件物理规格参数

本表逐项对照上述 commit 的官方产品规格，不把芯片通用能力推断成板卡配置。`verified` 表示本次来源比对完成，`needs_review` 表示仍待人工审核；此处描述固定版本，不保证最新批次配置。

## 1. 便携终端与整机硬件规格

| 规格维度 | MUSE Book | MUSE Box | MUSE Paper |
| :--- | :--- | :--- | :--- |
| 主控 | M1，8 核 64 位 RISC-V | K1，8 核 64 位 RISC-V | K1，8 核 64 位 RISC-V |
| 融合 AI 算力 | 2 TOPS | 2 TOPS | 2 TOPS |
| 内存 | 8 / 16 GB LPDDR4X，2400 MT/s | 8 / 16 GB LPDDR4X，2400 MT/s | 8 / 16 GB LPDDR4X，2400 MT/s |
| 本地存储 | 128 / 256 / 512 GB NVMe SSD | 32 GB eMMC 5.1 | 128 / 256 GB eMMC |
| 扩展存储 | TF，UHS-II | M.2 2280 M-Key NVMe + 1 个 SATA 硬盘 | TF，UHS-II |
| 显示 | 14.1 寸 IPS，1080P@60Hz；DP Type-C，1080P@60Hz | HDMI Type-A，1080P@60Hz | 10.95 寸 LCD，1200 × 1920 |
| 无线 | Wi-Fi 6 / BT 5.2 | M.2 E-Key Wi-Fi 6 / BT 5.2 | Wi-Fi 6 / BT 5.2 |
| 有线网络 | 产品规格未列出 | 2 路 RJ45，1000M / 100M | 产品规格未列出 |
| USB | 2 路 USB 3.0 Type-A；1 路 USB 3.0 Type-C 全功能；1 路 USB 3.0 Type-C OTG | 5 路 USB 2.0 Type-A；2 路 USB 3.0 Type-A（简介与规格表数量不同，采用规格表） | 1 路 USB 3.0 Type-C（含耳机音频）；1 路 USB 2.0 Type-C OTG（PD 快充） |
| 供电 | 38 Wh / 7.6 V 电池，PD 3.0，附 65 W 适配器 | 12 V DC JACK，主板支持 4Pin ATX DC IN | 7000 mAh 电池，18 W 快充 |
| 系统 | Bianbu / Ubuntu / OpenKylin / Deepin | Bianbu Desktop / Ubuntu / OpenKylin / Deepin | OpenHarmony；特性章节标注 OpenHarmony 5.0 与 Linux 6.6 |

## 2. 计算卡、实验架与教学套件

| 规格维度 | MUSE Card | MUSE Shelf | RISC-V Labkit |
| :--- | :--- | :--- | :--- |
| 主控 | M1，8 核 64 位 RISC-V | 80 路 K1 SoM，每颗 8 核 | M1 |
| AI 算力 | 2 TOPS | 每颗 K1 2 TOPS；不能把节点数相乘当作单一推理吞吐 | 2 TOPS |
| 形态 | 85 × 56 mm 单板，可装亚克力外壳 | 2U；规格表为 4 刀片、每刀片 20 路 | 480 × 370 × 170 mm 手提箱，10.1 寸 IPS 触屏 |
| 内存 | 8 / 16 GB LPDDR4X，2400 MT/s | 每 SoM 8 / 16 GB | 16 GB LPDDR4X，2400 MT/s |
| 本地存储 | 64 Mb SPI NOR | 每 SoM 64 / 128 GB Flash | 64 GB eMMC 5.1 |
| 存储扩展 | 2 个 M.2 2242 M-Key NVMe + TF UHS-II | 产品规格未列出 | M.2 2280 M-Key NVMe，单槽最高 1 TB；TF UHS-II |
| 网络 | 1 路 RJ45，1000M / 100M | 每 SoM GbE；每刀片 2 × 25 Gb SFP28，各刀片网络独立 | 2 路 RJ45，1000M / 100M；Wi-Fi 6 / BT 5.2 |
| 扩展与显示 | 40Pin GPIO，2 路 4-lane CSI，1 路 4-lane DSI，HDMI | GbE / USB Device / UART | 4 个 GPIO / SPI / UART / I2C 模块插槽，2 路 4-lane CSI；HDMI 1080P@60Hz 与 1920 × 1200 触屏 |
| 供电 | USB PD 3.0；Type-C 接口支持 12 V / 3 A | 1200 W 白金电源，热插拔、1 + 1 冗余 | 12 V / 3 A 适配器 |

## 3. 固定版本出处与复核范围

六篇均来自 `spacemit-com/docs-product@8c851807f2c54e8ba54d568b268100ca727d0777`，表中每列对应下列文档的「产品规格」章节；MUSE Paper 的系统版本同时取自「特性」。

| 产品列 | 官方文件 |
| :--- | :--- |
| MUSE Book | [产品简介](../Sources/docs-product/zh/k1_series/k1_muse_book/root_overview.md) |
| MUSE Box | [产品简介](../Sources/docs-product/zh/k1_series/k1_muse_box/root_overview.md) |
| MUSE Paper | [产品简介](../Sources/docs-product/zh/k1_series/k1_muse_paper/root_overview.md) |
| MUSE Card | [产品简介](../Sources/docs-product/zh/k1_series/k1_muse_card/root_overview.md) |
| MUSE Shelf | [产品简介](../Sources/docs-product/zh/k1_series/k1_muse_shelf/root_overview.md) |
| RISC-V Labkit | [产品简介](../Sources/docs-product/zh/k1_series/k1_riscv_labkit/root_overview.md) |

MUSE Box 简介写「USB2.06，USB3.04」，规格表写 USB 2.0 × 5、USB 3.0 × 2，保留差异并待人工/上游确认。MUSE Shelf 特性写 2 / 4 刀片，表格给出 4 刀片配置，不推断所有型号相同。未列出的能力不等于不支持，应定向核实硬件资料。
