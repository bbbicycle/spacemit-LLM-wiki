---
type: developer_journey
title: "SpaceAI 模型量化与端侧推理快速上手向导"
domain: edge_ai_robotics
target_audience: [AI算法工程师, 应用开发工程师]
status: needs_review
created: 2026-08-10
updated: 2026-10-21
aliases: [SpaceAI_模型量化与端侧推理快速上手向导, SpaceAI Quick Start Guide]
source_file: "Sources/docs-ai/zh/compute_stack/ai_compute_stack/quick_start.md"
source_commit: "2b3894e983a295ed0278bc625867e0c132e0e259"
source_section: "快速入门 模型转换与量化/模型性能测试/推理应用集成；XSlim QuickStart/量化参数配置"
source_resolution: partial
verification_status: unverified
source_checked_at: 2026-10-21
source_note: "本页为 YOLOv8 ONNX 视觉演示，非所有 LLM 通用编译路径；未运行量化、精度评测和板端性能测试。 本轮为来源与关键步骤定向核对，未在实物执行；关联节点保留各自核验状态。"
source_related_file: ["Sources/docs-ai/zh/compute_stack/ai_compute_stack/xslim.md"]
source_related_commit: ["2b3894e983a295ed0278bc625867e0c132e0e259"]
---
# SpaceAI 模型量化与端侧推理快速上手向导

本页以官方 [快速入门](../Sources/docs-ai/zh/compute_stack/ai_compute_stack/quick_start.md) 的 **YOLOv8 ONNX 视觉模型**为例。确认芯片、运行库版本、支持算子与输入后再复现；K1 与 K3 的智算核/精度能力分别核对，不把 K1 A60/2 TOPS 标成两代共用指标。

## 1. 导出模型

在已配置 ultralytics 的主机环境按原文导出：

```python
from ultralytics import YOLO
model = YOLO("yolov8n.pt")
model.export(format="onnx", imgsz=(640, 640), opset=17)
```

已有兼容 ONNX 可跳过。模型来源、opset、输入布局与预处理必须和实际任务一致。

## 2. XSlim 量化

按 [XSlim QuickStart 与配置说明](../Sources/docs-ai/zh/compute_stack/ai_compute_stack/xslim.md) 安装工具，准备实际的校准数据和 `yolov8n.json`，然后执行：

```bash
python -m xslim -c ./yolov8n.json -i yolov8n.onnx -o yolov8n.q.onnx
```

配置文件和校准集不是工具自动提供的通用占位文件；先完成配置再执行。当前官方 CLI 是 `python -m xslim`，旧稿 `xslim convert --quant-config --dataset` 未在此版本确认。选项与软件栈见 [[Evidence/space_ai_software_stack_specs]]。

## 3. 在匹配的板端运行库测试

以下取自官方示例 `spacemit-ort.riscv64.2.0.1` 目录，须先部署匹配运行库和模型：

```bash
export LD_LIBRARY_PATH=./lib
./bin/onnxruntime_perf_test yolov8n.q.onnx -e spacemit -r 10 -x 4 -S 1 -s -I -c 1
```

检查实际输出是否使用 SpaceMITExecutionProvider，再记录初始化、首帧、平均延迟、精度与内存。原文 K1 YOLOv8n 的示例结果不是所有模型/板型的保证；本次未执行这些硬件操作。

## 4. 应用集成与 LLM 分流

按原文“推理应用集成”配置 C++ Session 与运行库，先验证量化前后精度。架构与后续路径见 [[Evidence/space_ai_architecture_specs]]、[[Knowledge_Atoms/SpaceAI_端侧大模型量化与部署专题档案]]。GGUF LLM 应按对应 llama.cpp 文档处理，不能由此视觉演示推断所有框架、精度或模型均可直接运行。
