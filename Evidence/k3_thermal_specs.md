---
type: evidence
title: "K3 芯片热学规格与功耗参数"
claim_type: "parameter"
verification_status: unverified
status: needs_review
external_use: false
source_file: "k3_ds.md"
created: 2026-06-29
updated: 2026-06-29
aliases: ["K3热阻、功耗与结温参数", "K3 Thermal and Temperature Specs", "k3_thermal_specs"]
domain: chip_product_specs
target_audience: [热设计工程师, 系统工程师]
---
# K3 芯片热学规格与功耗参数

> [!TIP]
> **💡 工程师导读与排坑焦点**：存放 K3 芯片热阻参数、极限结温与散热设计上限数据。
> **目标读者**：`热设计工程师 / 系统工程师` | **技术领域**：`chip_product_specs`

本文件包含 K3 芯片级热学要求与功耗限制的原子数据。

## 1. 温度限制
*   **最大结温 (Tj_max)**: **125°C** (超过此温度芯片可能发生不可逆损坏或触发过温保护)
*   **工业级工作环境温度 (Ta)**: **-40°C ~ 85°C**
*   **商业级工作环境温度 (Ta)**: **0°C ~ 70°C**

## 2. 功耗限制 (TDP)
*   **热设计功率 (TDP)**: **15W** (在最高工作频率、满负荷状态下持续运行产生的平均热功率)
*   **长时功耗限制 (PL1)**: **15W** (持续运行的最大功耗阈值)
*   **短时功耗限制 (PL2)**: **25W** (允许瞬时峰值功耗，持续时间窗口通常不超过 10 秒)

## 3. 热阻参数 (Thermal Resistance)
*   **结到外壳热阻 (θ_JC)**: **1.2 °C/W**
*   **结到板级热阻 (θ_JB)**: **3.5 °C/W**
*   **结到环境热阻 (θ_JA - 无散热器自然对流)**: **18.5 °C/W**
