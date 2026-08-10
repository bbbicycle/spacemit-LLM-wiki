sidebar_position: 8

# Quick Start Guide

A step-by-step YOLOv8 inference example

This guide walks through a complete inference workflow using **YOLOv8**, including model export, quantization, performance benchmarking, and application integration with **ONNXRuntime + SpaceMITExecutionProvider**.

## Model Export and Quantization

- Export the **YOLOv8n** model from `ultralytics` to ONNX format.

   > If you already have an ONNX model, you can skip this step.

   ```python
   from ultralytics import YOLO

   model = YOLO("yolov8n.pt")
   model.export(format="onnx", imgsz=(640, 640), opset=17)
   ```

- Model Quantization

   Install **XSlim** and prepare calibration data and configuration files as described in the
[XSlim Quantization Guide](./xslim.md).

   ```bash
   # Static Quantization 
   python -m xslim -c ./yolov8n.json -i yolov8n.onnx -o yolov8n.q.onnx
   ```

   ```bash
   # Dynamic Quantization
   python -m xslim -i yolov8n.onnx -o yolov8n.fp16.onnx --dynq
   ```

   ```bash
   # FP16 Conversion
   python -m xslim -i yolov8n.onnx -o yolov8n.fp16.onnx --fp16
   ```

## Model Performance Benchmarking

```bash
# Example: inside the spacemit-ort.riscv64.2.0.1 directory
export LD_LIBRARY_PATH=./lib

# Select the correct model path
./bin/onnxruntime_perf_test yolov8n.q.onnx \
  -e spacemit -r 10 -x 4 -S 1 -s -I -c 1
```

Example Output (K1 Platform)
The output below provides a high-level view of model performance on a **K1** device.

```
./bin/onnxruntime_perf_test /mnt/modelzoo/detection/yolov8n/yolov8n.q.onnx -e spacemit -r 10 -x 4 -S 1 -s -I -c 1
using SpaceMITExecutionProvider
Setting intra_op_num_threads to 4
Session creation time cost: 1.14476 s
First inference time cost: 248 ms
Total inference time cost: 0.823382 s
Total inference requests: 10
Average inference time cost: 82.3382 ms
Total inference run time: 0.823483 s
Number of inferences per second: 12.1435
Avg CPU usage: 48 %
Peak working set size: 78946304 bytes
Avg CPU usage:48
Peak working set size:78946304
Runs:10
Min Latency: 0.0808129 s
Max Latency: 0.0838817 s
P50 Latency: 0.0826095 s
P90 Latency: 0.0838817 s
P95 Latency: 0.0838817 s
P99 Latency: 0.0838817 s
P999 Latency: 0.0838817 s
```

## Inference Application Integration

Here is an example for application-level integration, refer to the official
[yolov8_cpp_ort inference source](https://github.com/ultralytics/ultralytics/blob/main/examples/YOLOv8-ONNXRuntime-CPP/inference.cpp).

```c++
session = new Ort::Session(env, modelPath, sessionOption);
```

To enable SpacemiT EP acceleration, initialize the session options as shown below:

```c++
#include <onnxruntime_cxx_api.h>
#include "spacemit_ort_env.h"
//....
//....
//....
SessionOptionsSpaceMITEnvInit(session_options, provider_options);
session = new Ort::Session(env, modelPath, sessionOption);
```
