---
type: evidence
title: "K3 芯片 AI 算力与大模型推理数据"
claim_type: "metric"
verification_status: unverified
status: needs_review
external_use: false
source_tier: tier_1_github_upstream
source_origin: "https://github.com/spacemit-com/docs-ai"
source_file: "Sources/docs-ai/zh/compute_stack/ai_compute_stack/modelzoo.md"
source_commit: "2b3894e983a295ed0278bc625867e0c132e0e259"
source_section: "大模型 / Qwen；硬件规格的独立出处见正文"
source_locator: "modelzoo.md:265–299"
source_resolution: partial
conflicts: "旧0.9s、15–18 token/s及FastVLM指标无可复核测试条件，不能作为性能保证"
verified_at: 2026-10-13
created: 2026-06-29
updated: 2026-10-13
aliases: ["K3 AI算力与大模型性能数据", "K3 AI Performance and LLM Benchmarks", "k3_ai_performance_data"]
domain: edge_ai_robotics
target_audience: [AI 算法工程师, 系统架构师]
---
# K3 芯片 AI 算力与大模型推理数据

> [!TIP]
> **💡 工程师导读与排坑焦点**：存放 K3 芯片在 AI 算力与主流 8B / 30B MoE 稀疏大模型本地推理的实测数据。
> **目标读者**：`AI 算法工程师 / 系统架构师` | **技术领域**：`edge_ai_robotics`

本文件包含 K3 芯片的本地 AI 算力及大模型推理的实测与指标数据。

## 1. 算力指标
*   **通用 AI 算力**: **60 TOPS** (由 8 个 A100 智算核提供，支持 1024-bit 智算并行)
*   **通用计算算力**: **130 KDMIPS** (由 8 个高性能 X100 大核提供，支持 256-bit RVV 1.0)
*   **专用加速缓存**: 智算核配备 **3MB 专用 TCM** 紧耦合存储

## 2. 大模型本地推理性能

### 可复核的官方基准

出处：[官方模型表](../Sources/docs-ai/zh/compute_stack/ai_compute_stack/modelzoo.md)，固定版本 `spacemit-com/docs-ai@2b3894e983a295ed0278bc625867e0c132e0e259`，行 265–299，「大模型 / Qwen」。测试环境：K3，SpacemiT llama.cpp **0.1.1**，**bianbu-4.0rc3**，日期 **2026-05-26**；测试命令与示例记录见同章节，示例使用 8 个线程。不要把示例日志直接认定为每一个模型的完整硬件配置。

| 模型 | 量化 | PP128 token/s | TG128 token/s | PP1280 token/s | TG1280 token/s |
| :--- | :--- | ---: | ---: | ---: | ---: |
| Qwen3-MoE-30B-A3B | Q4_0 | 55.67 | 12.32 | 44.03 | 11.17 |

30B-A3B 是 MoE 稀疏模型，单 token 激活约 3B 参数，不能推论为 30B Dense 性能。PP 与 TG 是不同测试项，以上吞吐不能直接换算成首词延迟。它们是固定环境下的历史测试，不保证其他内存配置、量化、上下文长度或软件版本结果一致。

### 保留的历史待核验口径

旧 Wiki 写 Qwen3-30B-A3B 首词 **0.9 秒**、输出 **15 / 18 token/s**，以及 FastVLM-1.5B 首词 **0.5 秒**、输出 **40 token/s**。这些记录没有完整可追溯的测量条件与出处，**不能作为对外性能承诺或评测标准答案**。同样，旧 VIT_b_16「90 fps」缺少输入尺寸、精度和环境，仍待复核。它们不能仅因数值不同就与上述 llama-bench 表格判定同条件冲突。

硬件字段出处：[K3 产品简介](../Sources/docs-chip/zh/key_stone/k3/k3_docs/root_overview.md)，`spacemit-com/docs-chip@1ea15a766287024a5bb7b548850826e3525a80dc`，「概述 / 产品特性」。本次核对模型表不等于本文件所有架构、缓存、模型边界断言已完成逐条核验，因此整体保持 `unverified / needs_review / external_use:false`。

## 3. 部署与数据格式
*   **格式支持**: 支持 FP16, BF16, FP8, INT8, INT4。
*   **硬件首创**: 全球首颗支持 **FP8 原生推理** 的 RISC-V AI 芯片。
*   **模型部署边界**: 支持通过 `spacemit-onnxruntime` 及 SpacemiT 优化版 `llama.cpp` 部署主流量化模型；受 32GB 物理内存与算子适配限制，超大模型（>30B MoE 规模或 >8B Dense 规模）或未适配算子模型需通过集群服务器或云端协同运行。
