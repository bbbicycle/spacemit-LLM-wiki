---
type: evidence
title: "K1 芯片 AI 算力与大模型推理数据"
claim_type: "metric"
status: needs_review
verification_status: unverified
external_use: false
source_file: "Sources/docs-chip/zh/key_stone/k1/k1_docs/root_overview.md"
source_origin: "https://github.com/spacemit-com/docs-chip"
source_commit: "1ea15a766287024a5bb7b548850826e3525a80dc"
source_section: "概述；特性"
source_resolution: partial
source_checked_at: 2026-10-13
source_note: "产品简介与 AI 架构文档对 CPU 核命名口径不同；保留各自出处。框架兼容、测试年份和全部安全参数未逐项核验。"
source_related_file: "Sources/docs-ai/zh/architecture/concept.md"
source_related_commit: "2b3894e983a295ed0278bc625867e0c132e0e259"
created: 2026-06-29
updated: 2026-10-13
aliases: ["K1 AI算力与大模型性能数据", "K1 AI Performance and LLM Benchmarks", "k1_ai_performance_data"]
domain: edge_ai_robotics
target_audience: [AI 算法工程师, 嵌入式软件]
---
# K1 芯片 AI 算力与大模型推理数据

> [!TIP]
> **💡 工程师导读与排坑焦点**：存放 K1 通用 50KDMIPS、2.0 TOPS AI 算力、K1 AI CPU 与 1B 大模型指标。
> **目标读者**：`AI 算法工程师 / 嵌入式软件` | **技术领域**：`edge_ai_robotics`

本文件包含 K1 芯片的本地 AI 算力及大模型推理的实测与指标数据。

## 1. 算力指标
*   **通用 AI 算力**: **2.0 TOPS** (由 AP-CPU 核通过定制化 RISC-V 指令矩阵运算提供)
*   **通用计算算力**: **50 KDMIPS** (由 8 个高性能自研 X60 大核提供，单核性能 Specint2006 > 4.0/GHz)
*   **并行计算位宽**: X60 核支持 **256bit** 的 RVV 1.0 向量标准 (提供 2 倍于 Neon 的并行处理算力，向量性能达 ARM NEON 150% 以上)

## 2. 大模型本地推理性能 (2026年测算)
*   **本地大模型支持上限**: 可流畅运行最高 **10 亿 (1B)** 及 **5 亿 (0.5B)** 参数的端侧大模型。
*   **1B 本地大模型推理速度**: **> 10 Tokens/s** (得益于 AI-CPU 融合的原生算力)

## 3. 部署与硬件安全引擎规格
*   **硬件加速支持**: 官方 AI 架构文档将 K1 的 AI CPU 称为 **A60**，支持 256-bit RVV 1.0 与 Int8 Matrix 运算；**A100 属于 K3，不能套用于 K1**。ONNX Runtime、TensorFlow Lite 与 SpaceLLM 的具体兼容范围仍需按软件版本验证。
*   **物理内存与带宽**: 32-bit LPDDR4/4X（频率支持 2400 ~ 2666 MT/s），最大支持 16 GB 内存容量，最高物理带宽达 **10.6 GB/s**。
*   **硬件安全模块 (Security Engine)**: 内置硬件级加密引擎，硬件支持 AES-128/256、SHA-256/512、RSA-2048/4048 算法加速与 Key Master 硬件防篡改保密存储。
*   **编程范式**: 遵循通用 CPU / Vector 编程范式，无需依赖复杂异构驱动，AI 算法无缝部署。

