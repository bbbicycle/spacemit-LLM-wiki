---
type: evidence
title: "SpacemiT SpaceAI 软件栈与模型量化组件规格"
domain: edge_ai_robotics
target_audience: [AI算法工程师, 软件开发工程师]
status: needs_review
created: 2026-08-10
updated: 2026-08-10
aliases: [space_ai_software_stack_specs, SpaceAI Stack Specs, XSlim Specs]
---

# SpacemiT SpaceAI 软件栈与模型量化组件规格

> [!TIP]
> **💡 工程师导读与排坑焦点**：记录 SpacemiT 官方 AI 计算软件栈组件、ONNX Runtime `SpaceMITExecutionProvider` 接口、XSlim 量化工具链及 Triton 编译支持规格。
> **目标读者**：`AI算法工程师 / 软件开发工程师` | **技术领域**：`edge_ai_robotics`

本文档汇总 SpacemiT 提供的 SpaceAI 软件栈（SpaceAI Compute Stack）各多层级交付组件规格与使用参数。

---

## 1. 软件栈多层级交付组件矩阵

| 交付层级 | 核心组件名称 | 交付形式 / API 接口 | 功能与技术特性 |
| :--- | :--- | :--- | :--- |
| **端到端推理** | **ONNX Runtime** | `SpaceMITExecutionProvider` | ONNX 模型专属硬件执行提供者，自动映射 IME 矢量矩阵指令 |
| **模型量化精简**| **XSlim** | Python SDK & 命令行 | 模型量化与裁剪工具链，支持 PTQ/QAT 量化校准与算子融合 |
| **大模型推理** | **llama.cpp** | C++/Python 接口 | 深度集成 IME 矢量加速的 GGUF 大模型引擎 |
| **高性能服务** | **vLLM** | OpenAI API 兼容服务 | 高吞吐大模型推理与 Web 服务框架 |
| **算子加速库** | **SpaceCV / SpaceMath** | C/C++ 库 (OpenCV / OpenBLAS 加速) | 硬件加速视觉与基础数学计算库 |
| **AI 编程语言** | **Triton** | Python 交互模式 | 针对 RISC-V Vector/IME 的高性能 AI 算子 DSL |

---

## 2. XSlim 量化工具链规格

* **支持的量化精度**：INT8 / INT4 权重量化与激活值量化。
* **量化调优策略**：包含 MinMax、Entropy 及 Percentile 校准策略，支持通道级 (Per-channel) 与张量级 (Per-tensor) 量化。
* **模型转换流程**：
  ```bash
  xslim convert --model input_model.onnx --output quantized_model.onnx --quant-config int8_config.json
  ```

---

## 3. ONNX Runtime 硬件执行提供者 (EP) 参数

在 C++ 或 Python 中通过指定 `SpaceMITExecutionProvider` 即可自动调用 A60 智算核的 2.0 TOPS 矩阵算力：

```python
import onnxruntime as ort

# 设置配置选项
options = ort.SessionOptions()
provider_options = {"device_id": "0", "precision": "int8"}

# 创建包含 SpaceMITExecutionProvider 的推理 Session
session = ort.InferenceSession("quantized_model.onnx", providers=["SpaceMITExecutionProvider"], provider_options=[provider_options])
```
