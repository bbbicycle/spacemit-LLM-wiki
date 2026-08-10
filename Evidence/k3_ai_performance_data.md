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
> **💡 工程师导读与排坑焦点**：存放 K3 芯片在 AI 算力与主流 8B/30B 大模型本地推理的实测数据。
> **目标读者**：`AI 算法工程师 / 系统架构师` | **技术领域**：`edge_ai_robotics`

本文件包含 K3 芯片的本地 AI 算力及大模型推理的实测与指标数据。

## 1. 算力指标
*   **通用 AI 算力**: **60 TOPS**
*   **通用通用计算算力**: **130 KDMIPS** (由 8 个高性能 X100 大核提供)
*   **并行计算位宽**: A100 核支持 **1024bit** 的 RVV 1.0 并行计算

## 2. 大模型本地推理性能 (2026年测算)
*   **本地大模型支持上限**: 可流畅运行最高 **300 亿 (30B) 参数** 的本地大模型。
*   **Qwen3-30B-A3B 本地推理速度**:
    *   首词延迟 (1st-Word Latency): **0.9 秒**
    *   输出速度: **15 Tokens/s** (部分汇报材料中使用 **18 Tokens/s**，存在口径差异，待复核)
*   **FastVLM-1.5B (多模态)**:
    *   首词延迟: **0.5 秒**
    *   输出速度: **40 Tokens/s**
*   **VIT_b_16 (视觉模型) 运行帧率**: **90 fps**

## 3. 部署与数据格式
*   **格式支持**: 支持 FP16, BF16, FP8, INT8, INT4。
*   **硬件首创**: 全球首颗支持 **FP8 原生推理** 的 RISC-V AI 芯片。
*   **社区模型兼容性**: 可部署 HuggingFace 社区上除 **FP4/FP6** 之外的所有主流大模型。
