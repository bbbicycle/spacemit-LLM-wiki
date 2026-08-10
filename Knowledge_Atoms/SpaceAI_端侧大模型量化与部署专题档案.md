---
type: knowledge_atom
title: "SpaceAI 端侧大模型量化与部署专题档案"
domain: edge_ai_robotics
target_audience: [AI算法工程师, 软件开发工程师]
status: needs_review
created: 2026-08-10
updated: 2026-08-10
aliases: [SpaceAI_端侧大模型量化与部署专题档案, SpaceAI Deployment Dossier, SpaceAI SDK Guide]
---

# SpaceAI 端侧大模型量化与部署专题档案

> [!TIP]
> **💡 工程师导读与排坑焦点**：详解 SpacemiT AI CPU（A60 智算核）同构融合原理、XSlim 量化工具链、ONNX Runtime `SpaceMITExecutionProvider` 接入及 vLLM / llama.cpp 端侧部署。
> **目标读者**：`AI算法工程师 / 软件开发工程师` | **技术领域**：`edge_ai_robotics`

本专题档案系统性解构基于 SpacemiT K1 与 K3 RISC-V 平台的 SpaceAI 软件栈全景。涵盖同构智算核架构原理、XSlim 工具链量化转码、ONNX Runtime 专属硬件执行提供者接入，以及端侧 LLM 推理引擎（llama.cpp / vLLM）的部署调优。

---

## 1. 同构智算核 (AI CPU) 与 IME 矩阵扩展原理

传统的 AI 加速依赖异构 NPU/GPGPU，带来繁重的驱动层与上下文切换开销。SpacemiT 提出了 **AI CPU 同构融合技术**：

```mermaid
graph TD
    UserApp[用户软件 / 应用线程] --> LinuxKernel[Linux 标准线程调度]
    LinuxKernel --> AICPU[SpacemiT A60 智算核 (AI CPU)]

    subgraph HardwareCore [智算核同构内部]
        AICPU --> Scalar[Scalar 标量指令]
        AICPU --> Vector[RVV 1.0 256-bit 向量指令]
        AICPU --> IME[IME 矩阵指令 vmadot (4x8x4 TensorCore)]
    end

    subgraph MemoryAccess [零 DMA 延时访问]
        IME --> TCM[512KB 紧耦合加速存储器 (TCM)]
        TCM --> LPDDR4[32-bit LPDDR4/4X 物理内存]
    end
```

详细的 `cpufp` 算力实测数据（2.046 TOPS Int8 / 533.65 GFLOPS FP16）请参考 [[Evidence/space_ai_architecture_specs|A60 AI CPU 智算核规格]]。

---

## 2. XSlim 模型量化与裁剪工具链

针对端侧有限的物理内存带宽 (10.6 GB/s)，在部署模型前须通过 XSlim 工具链进行量化：

1. **PTQ 静态后量化**：准备少量校准数据集，执行张量级与通道级量化。
2. **算子融合**：自动将 Conv+BN+ReLU、MatMul+Add 融合成 IME 硬件直接支持的超节点算子。
3. **输出导出**：生成集成 `SpaceMITExecutionProvider` 描述节点的 `.onnx` 模型。

工具链参数与命令请参阅 [[Evidence/space_ai_software_stack_specs|SpaceAI 软件栈与 XSlim 规格]]。

---

## 3. ONNX Runtime 硬件执行提供者 (EP) 接入

在应用代码中加入 `SpaceMITExecutionProvider`，推理引擎会自动将 GEMM（矩阵乘法）下发至 Cluster 0 的 A60 智算核：

```cpp
// C++ API 接入示例
Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "SpacemiT_AI");
Ort::SessionOptions session_options;

// 追加 SpacemiT 专属 Execution Provider
Ort::ThrowOnError(OrtSessionOptionsAppendExecutionProvider_SpaceMIT(session_options, 0));

Ort::Session session(env, "quantized_model.onnx", session_options);
```

---

## 4. 端侧大模型 (LLM) 推理引擎部署

1. **llama.cpp 部署**：
   通过编译标志 `-DGGML_CPU_RISCV64_SPACEMIT=ON` 开启 IME 矩阵加速，部署 Q4_K_M 4-bit 量化 GGUF 模型。
2. **vLLM 服务部署**：
   利用 SpacemiT vLLM 分支启动 Open-AI 兼容的 Web API 服务，支持并发 Context 缓存优化。

更详细的大模型实测与调频干货请查阅 [[Knowledge_Atoms/K1大模型本地推理与AI算力专题档案|K1 大模型本地推理专题]] 与 [[Knowledge_Atoms/K3大模型本地推理与AI算力专题档案|K3 大模型本地推理专题]]。
