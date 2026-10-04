---
type: knowledge_atom
title: "SpaceAI 端侧大模型量化与部署专题档案"
domain: edge_ai_robotics
target_audience: [AI算法工程师, 软件开发工程师]
status: needs_review
created: 2026-08-10
updated: 2026-10-04
aliases: [SpaceAI_端侧大模型量化与部署专题档案, SpaceAI Deployment Dossier, SpaceAI SDK Guide]
---

# SpaceAI 端侧大模型量化与部署专题档案

> [!TIP]
> **💡 工程师导读与排坑焦点**：详解 SpacemiT AI CPU（A60 智算核）同构融合原理、XSlim 量化工具链、ONNX Runtime `SpaceMITExecutionProvider` 接入、vLLM / llama.cpp 端侧部署及官方 AI Computer 解决方案矩阵。
> **目标读者**：`AI算法工程师 / 软件开发工程师` | **技术领域**：`edge_ai_robotics`

本专题档案系统性解构基于 SpacemiT K1 与 K3 RISC-V 平台的 SpaceAI 软件栈全景。涵盖同构智算核架构原理、XSlim 工具链量化转码、ONNX Runtime 专属硬件执行提供者接入、端侧 LLM 推理引擎部署，以及官方发布的 AI Computer 桌面级解决方案矩阵。

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

---

## 5. 官方 AI Computer 落地应用与评估方案全景

SpacemiT 基于 K3 高算力平台，在官方 `docs-ai` 中推出了完整的端侧全栈 AI 应用落地方案：

*   **File2MD 本地文档解析应用**：针对 SpacemiT K3 Bianbu 桌面系统打造的本地文档转 Markdown 工具。支持 PDF、Office、扫描图像的本地版面分析、OCR 与公式表格提取，实现“数据不出端”的安全办公。
*   **与会 (Yumeet) & 多路实时 ASR**：集成 VAD 语音激活检测、端侧 ASR、声纹说话人分离（Diarization）与 LLM 总结能力，实现全离线会议录制、实时字幕与智能纪要生成。
*   **知了 (Zenow)**：设备端本地运行的个人与企业知识库问答助手，深度结合 RAG 向量检索与本地离线 LLM。
*   **见智 (Seewise) & 多路视觉分析**：支持本地视频或 RTSP 摄像头接入，通过端侧视觉特征提取与自然语言跨模态匹配，实现毫秒级自然语言以图搜视频。
*   **点将 (Agentforce)**：基于端侧轻量 Agent 框架与数字员工多角色管理调度平台。
*   **SpacemiT AI Lab 在线评估云平台**：官方搭建的网页化 K3 算力沙箱体验平台，开发者无需实体开发板即可一键申请云端 K3 实例进行模型评测。
