---
type: evidence
title: "K1 芯片热学规格与功耗参数"
claim_type: "parameter"
verification_status: unverified
status: needs_review
external_use: false
source_file: "root_overview.md"
created: 2026-06-29
updated: 2026-06-29
aliases: ["K1工作温度与功耗参数", "K1 Thermal and Power Specs", "k1_thermal_specs"]
domain: chip_product_specs
target_audience: [硬件工程师, 热设计工程师]
---
# K1 芯片热学规格与功耗参数

> [!TIP]
> **💡 工程师导读与排坑焦点**：存放 K1 芯片 TDP 功耗、工作结温及极简被动散热规格。
> **目标读者**：`硬件工程师 / 热设计工程师` | **技术领域**：`chip_product_specs`

本文件包含 K1 芯片级热学要求与功耗限制的原子数据。

## 1. 温度限制
*   **工业级工作环境温度 (Ta)**: **-40°C ~ 85°C** (在此温度范围内芯片仍能提供稳定可靠的持续算力输出)

## 2. 功耗限制 (TDP)
*   **热设计功率 (TDP)**: **3W ~ 5W** (最高工作频率、满负荷场景下的平均热功耗。同负载场景功耗只有同档芯片的 80%)
