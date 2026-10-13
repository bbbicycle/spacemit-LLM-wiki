---
type: evidence
title: "K3 芯片热学规格与功耗参数"
claim_type: "parameter"
status: needs_review
verification_status: unverified
external_use: false
source_file: "Sources/docs-chip/zh/key_stone/k3/k3_docs/k3_ds.md"
source_origin: "https://github.com/spacemit-com/docs-chip"
source_commit: "1ea15a766287024a5bb7b548850826e3525a80dc"
source_section: "5.2.2 封装参数；5.3 热特性"
source_resolution: partial
thermal_source_resolution: unresolved
source_checked_at: 2026-10-13
source_note: "温度范围和带散热盖热阻已定位；原 θJC/θJB/θJA、PL1/PL2 与时间窗口缺少对应来源和测量条件，不能作为已验证设计输入。"
created: 2026-06-29
updated: 2026-10-13
aliases: ["K3热阻、功耗与结温参数", "K3 Thermal and Temperature Specs", "k3_thermal_specs"]
domain: chip_product_specs
target_audience: [热设计工程师, 系统工程师]
---
# K3 芯片热学规格与功耗参数

> [!TIP]
> **💡 工程师导读与排坑焦点**：存放 K3 芯片热阻参数、极限结温与散热设计上限数据。
> **目标读者**：`热设计工程师 / 系统工程师` | **技术领域**：`chip_product_specs`

本文件包含 K3 芯片级热学要求与功耗限制的原子数据。

> [!WARNING]
> 官方数据手册 5.2.2 支持工业环境温度 -40～85°C 与最大结温 125°C；5.3 仅写“热阻：0.23°C/W（带散热盖）”，未标注 θJC/θJB/θJA 类型。下述历史热阻、PL1/PL2、时间窗口及商业级温度缺少对应来源和条件，保留待复核，不能作为已验证的散热设计输入。不同测量定义下的热阻不能直接替换。

## 1. 温度限制
*   **最大结温 (Tj_max)**: **125°C** (超过此温度芯片可能发生不可逆损坏或触发过温保护)
*   **工业级工作环境温度 (Ta)**: **-40°C ~ 85°C**
*   **商业级工作环境温度 (Ta)**: **0°C ~ 70°C**

## 2. 历史功耗记录（来源与条件待复核）
*   **热设计功率 (TDP)**: **15W** (在最高工作频率、满负荷状态下持续运行产生的平均热功率)
*   **长时功耗限制 (PL1)**: **15W** (持续运行的最大功耗阈值)
*   **短时功耗限制 (PL2)**: **25W** (允许瞬时峰值功耗，持续时间窗口通常不超过 10 秒)

## 3. 历史热阻记录（来源与测量方法待复核）
*   **结到外壳热阻 (θ_JC)**: **1.2 °C/W**
*   **结到板级热阻 (θ_JB)**: **3.5 °C/W**
*   **结到环境热阻 (θ_JA - 无散热器自然对流)**: **18.5 °C/W**
