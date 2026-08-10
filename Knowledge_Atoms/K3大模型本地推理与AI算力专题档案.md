---
type: knowledge_atom
title: "K3 大模型本地推理与 AI 算力专题档案"
status: needs_review
created: 2026-06-29
updated: 2026-06-29
aliases: ["K3大模型本地推理与AI算力专题", "K3 Local LLM Inference and AI Power Topic", "k3_llm_ai_power"]
domain: edge_ai_robotics
target_audience: [AI 算法工程师, 系统优化]
---
# K3 大模型本地推理与 AI 算力专题档案

> [!TIP]
> **💡 工程师导读与排坑焦点**：详解 K3 大模型本地运行吞吐、统一内存共享与多线程推理加速。
> **目标读者**：`AI 算法工程师 / 系统优化` | **技术领域**：`edge_ai_robotics`

本主题档案汇总了 K3 芯片在本地端侧部署大语言模型（LLM）与多模态模型（VLM）的软硬件架构、实测速度与部署流程。

---

## 1. 核心 AI 性能指标

K3 芯片作为高性能 RISC-V AI CPU，具备强大的端侧推理能力（底层数据参见 [[Evidence/k3_ai_performance_data]]）：
*   **算力保障**：搭载 8 核高性能 A100 核，提供 **60 TOPS** 的通用 AI 算力。
*   **本地大模型支持**：最高流畅支持 **30B 参数** 级别的模型本地运行，满足端侧“高智力”本地化部署需求。
*   **首创特性**：全球首颗支持 **FP8 原生推理** 的 RISC-V 芯片，极大地降低了模型量化后的精度损失。

---

## 2. 本地部署软硬件融合设计

为了在端侧将 60 TOPS 算力完全榨干，K3 采用了软硬件同构融合的设计：

### 2.1 硬件加速核心：TCM 缓存
*   K3 设计有 **3MB 专用加速缓存 TCM**。
*   在运行大模型推理时，TCM 作为算力核心的“超快速草稿纸”，使高频数据读写性能直接提升 **3 倍**，大幅降低了对外部 DDR 带宽的依赖。

### 2.2 内存配置限制
*   运行 30B 级别大模型，系统内存必须配置为最大支持的 **32GB LPDDR5**，以防止内存溢出。
*   内存带宽最大可达 **51.2GB/s**（LPDDR5-6400Mbps，双通道 64-bit），为大模型的 Token 持续生成提供数据吞吐保障。

### 2.3 软件部署流
*   开发者可以通过 SpacemiT 提供的 AI 工具链，将 HuggingFace 上的大模型编译转换为适用于 A100 核的格式。
*   当前 SDK 完整支持 FP16, BF16, FP8, INT8, INT4 格式。目前**暂不支持 FP4/FP6** 格式。

---

## 3. 关联原始参考文档

关于具体的 AI 编译器使用、SDK 依赖库安装以及模型量化命令，请进一步参阅：
*   [K3 产品简介 - 原始文档](../Sources/docs-chip/zh/key_stone/k3/k3_docs/root_overview.md)
*   [K3 SDK 使用指南 - 原始文档](../Sources/docs-chip/zh/key_stone/k3/k3_sw/k3_sdk_user_guide.md)
