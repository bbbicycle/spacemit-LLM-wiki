---
type: evidence
title: "K3 芯片 AI 算力与大模型推理数据"
claim_type: "metric"
verification_status: unverified
status: needs_review
external_use: false
source_file: "root_overview.md"
created: 2026-06-29
updated: 2026-06-29
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

## 2. 大模型本地推理性能 (2026年测算)
*   **本地 MoE 大模型支持**: 可流畅运行最高 **300 亿 (30B) 参数级别的 MoE 稀疏大模型**（单 Token 实际激活约 3B 参数）。
*   **Qwen3-30B-A3B (MoE 架构) 本地推理速度**:
    *   首词延迟 (1st-Word Latency): **0.9 秒**
    *   输出速度: **15 Tokens/s** (部分汇报材料中使用 **18 Tokens/s**，存在口径差异，待复核)
*   **FastVLM-1.5B (端侧多模态 VLM)**:
    *   首词延迟: **0.5 秒**
    *   输出速度: **40 Tokens/s**
*   **Qwen3.5-0.8B / 2B / 4B (VLM)**: 官方 llama.cpp 推荐端侧多模态基线模型
*   **VIT_b_16 (视觉模型) 运行帧率**: **90 fps**

## 3. 部署与数据格式
*   **格式支持**: 支持 FP16, BF16, FP8, INT8, INT4。
*   **硬件首创**: 全球首颗支持 **FP8 原生推理** 的 RISC-V AI 芯片。
*   **模型部署边界**: 支持通过 `spacemit-onnxruntime` 及 SpacemiT 优化版 `llama.cpp` 部署主流量化模型；受 32GB 物理内存与算子适配限制，超大模型（>30B MoE 规模或 >8B Dense 规模）或未适配算子模型需通过集群服务器或云端协同运行。
