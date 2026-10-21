---
type: developer_journey
title: "K3 Pico-ITX 开发板快速上手向导"
status: needs_review
created: 2026-06-30
updated: 2026-10-21
aliases: ["K3 Pico 开发板快速上手向导", "K3 Pico Quick Start Guide", "k3_pico_quick_start"]
domain: hardware_schematic_design
source_file: "Sources/docs-product/zh/k3_series/k3_pico/pico_user_guide.md"
source_commit: "bc640755145625cc20745f49861f82588863fca3"
source_section: "Pico 指南 1/2.3.1～2.3.3/3.1；Llama.cpp 2"
source_resolution: partial
verification_status: unverified
source_checked_at: 2026-10-21
source_note: "覆盖供电、烧录、UEFI 与 LLM 包名；镜像版本、实际性能和所有板载外设未实测。 本轮为来源与关键步骤定向核对，未在实物执行；关联节点保留各自核验状态。"
source_related_file: ["Sources/docs-ai/zh/compute_stack/ai_compute_stack/llama.cpp.md"]
source_related_commit: ["2b3894e983a295ed0278bc625867e0c132e0e259"]
---
# K3 Pico-ITX 开发板快速上手向导

按 [K3 Pico-ITX 用户指南](../Sources/docs-product/zh/k3_series/k3_pico/pico_user_guide.md) 确认单板/机箱套餐和 U-Boot/UEFI 镜像。源文不同段落提到 Bianbu 3.0 与 4.0 UEFI 镜像，不能据本页指定所有设备的预装版本。

## 1. 上电与显示

可用具备 **65W 或更大 Type-C 反向供电能力**的显示器和全功能线连接图示 **No.17** 接口；No.17 是图中位置编号，不是物理针脚。也可用带 PD 的扩展坞或 ATX-2 Pin 供电，按指南核对额定档位和原装散热器。ATX 与 PD 不支持 1+1 热冗余，切换按指南关机处理。

## 2. 进入烧录模式

图示 **No.18 烧录口仅传数据、不能向板内供电**，须保持其他电源口供电并使用数据线：

1. 关机时按住 FDL，上电后松开；开机时按住 FDL，短按 Reset 后松开。
2. 将烧录数据口接至上位机，使用 Titan 或对应固件的 fastboot 流程。
3. 核对目标介质和镜像适用板型后烧录，具体命令以固件说明为准。

## 3. UEFI 体验版

仅在对应 UEFI 镜像下，上电 3 秒内按 F2 进入设置；通过 Boot Manager 选择介质。更改启动顺序后按原文 Commit Change and Exit 与 F10 保存。不要将 UEFI 菜单步骤套用于 U-Boot 镜像。

## 4. 跑通本地 LLM

按 [Llama.cpp 指南](../Sources/docs-ai/zh/compute_stack/ai_compute_stack/llama.cpp.md) 安装 `llama.cpp-tools-spacemit`（旧固件另查 `llama-server`），下载匹配的 GGUF，先检查可用内存再运行 `llama-cli` 或 `llama-bench`。统一内存仍受总容量、权重、KV cache 和运行时开销约束，不代表没有内存上限。Qwen3-30B-A3B 的总参数与激活量、量化格式及测量条件分别记录。

- 板级设计：[[Knowledge_Atoms/K3_Pico_板级硬件设计专题]]。
- 芯片代际与模型边界：[[Knowledge_Atoms/K3大模型本地推理与AI算力专题档案]]。
