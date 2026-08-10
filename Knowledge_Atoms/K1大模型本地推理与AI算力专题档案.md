---
type: knowledge_atom
title: "K1 大模型本地推理与 AI 算力专题档案"
status: needs_review
created: 2026-06-29
updated: 2026-06-29
aliases: ["K1大模型本地推理与AI算力专题", "K1 Local LLM Inference and AI Power Topic", "k1_llm_ai_power"]
domain: edge_ai_robotics
target_audience: [AI 算法工程师, 应用开发]
---
# K1 大模型本地推理与 AI 算力专题档案

> [!TIP]
> **💡 工程师导读与排坑焦点**：详解 X60 算力矩阵、llama.cpp 编译标志 -DGGML_CPU_RISCV64_SPACEMIT=ON 与调频。
> **目标读者**：`AI 算法工程师 / 应用开发` | **技术领域**：`edge_ai_robotics`

本主题档案汇总了 K1 芯片在本地端侧部署大语言模型（LLM）与计算加速的软硬件架构、实测速度与部署设计。

---

## 1. 核心 AI 性能与 DSA 架构

K1 芯片作为高性能、低功耗的 RISC-V AI CPU，具备独特的端侧 AI 部署设计（底层数据参见 [[Evidence/k1_ai_performance_data]]）：
*   **双簇非对称 AP 架构**：
    *   **Cluster 0**：集成 4 个自研 X60™ 64位计算核，**融合 2.0 TOPS AI 算力扩展单元**，并额外配置有 **512KB 专用加速紧耦合存储器 (TCM)**。
    *   **Cluster 1**：包含 4 个 X60™ 核心，主要处理通用计算，不带 AI 加速单元。
*   **向量计算能力**：支持 **256-bit RVV 1.0 标准**（双发射执行宽度），向量并行计算性能是传统 ARM NEON 1.5 倍以上。
*   **本地大模型支持**：最高流畅支持 **1B/0.5B 参数** 级别的模型本地运行（推理速度 **> 10 Tokens/s**），适合低功耗端侧语音助手或控制面板。

---

## 2. 软硬件融合与部署设计

### 2.1 硬件加速核心 (TCM)
*   **紧耦合存储器 (TCM)**：在 Cluster 0 中配置的 512KB TCM 是专为 AI 定制指令（如整型点积矩阵乘加 `smt.vmadot`）设计的极速缓存，能够避免大模型频繁读取外存带来的带宽限制。

### 2.2 内存限制与带宽
*   大模型运行对内存带宽敏感，K1 搭配 32bit LPDDR4/LPDDR4X，最大容量支持 **16GB**，最高速率达 2666 MT/s（提供 **10.6 GB/s** 物理带宽）。

### 2.3 软硬件编译与 llama.cpp 实战调优干货

为了在 K1 上发挥最大端侧推理吞吐，须使用 SpacemiT 官方适配的 [llama.cpp 仓库](https://github.com/spacemit-com/llama.cpp) 并进行硬核编译与调频：

1. **核心 CMake 编译标志**：
   ```bash
   cmake -B build -DGGML_CPU_RISCV64_SPACEMIT=ON -DGGML_RV_ZBA=ON
   cmake --build build --config Release -j8
   ```
   * **`-DGGML_CPU_RISCV64_SPACEMIT=ON`**：开启核心 `vmadot` (Int4/Int8 矩阵乘加) IME1/IME2 矢量加速内核。
   * **`-DGGML_RV_ZBA=ON`**：防止新版 GCC 编译器在 Zba 位操作指令集中报编译异常。

2. **运行时验证与调频 (Scaling Governor)**：
   * **开启高性能 CPU 调频**（避免降频导致首包延迟提升）：
     ```bash
     echo performance | sudo tee /sys/devices/system/cpu/cpufreq/policy0/scaling_governor
     ```
   * **验证硬件加速日志**：模型初始化时日志中必须出现 `CPU_RISCV64_SPACEMIT` 和 `use_ime2: 1` 标识，确认硬件矢量 AI 算力已被完美激活。

3. **量化策略 (Quantization)**：
   * 强力推荐使用 **`Q4_K_M`** 4-bit 量化 GGUF 模型，平衡内存带宽瓶颈 (10.6 GB/s) 与推理精度，实测 1B 参数模型生成吞吐达到 **10 ~ 15 tokens/s**。

---

## 3. 关联原始参考文档

关于具体 AI 定制指令（IME 扩展）以及编译转换命令，请参阅：
* [K1 产品简介 - 原始文档](../Sources/docs-chip/zh/key_stone/k1/k1_docs/root_overview.md)
* [K1 SDK 使用指南 - 原始文档](../Sources/docs-chip/zh/key_stone/k1/k1_sw/k1_sdk_user_guide.md)
* 进迭时空官方 llama.cpp 加速库：[spacemit-com/llama.cpp](https://github.com/spacemit-com/llama.cpp)
* 进迭时空官方定制指令规范库：[spacemit-com/riscv-ime-extension-spec](https://github.com/spacemit-com/riscv-ime-extension-spec)

