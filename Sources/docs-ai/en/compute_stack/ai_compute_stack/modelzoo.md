sidebar_position: 9

# ModelZoo

> Model data in ModelZoo is updated regularly. For model application examples, refer to [ai-sdk](https://github.com/spacemit-com/ai-sdk).

- [ModelZoo](#modelzoo)
  - [Base Models](#base-models)
    - [Benchmark Method](#benchmark-method)
    - [ResNet](#resnet)
    - [MobileNet](#mobilenet)
    - [EfficientNet](#efficientnet)
    - [ViT](#vit)
    - [YOLOv5](#yolov5)
    - [YOLOv6](#yolov6)
    - [YOLOv8](#yolov8)
    - [YOLOv8-Seg](#yolov8-seg)
    - [YOLOv8-Pose](#yolov8-pose)
    - [YOLOv12](#yolov12)
    - [Audio Models](#audio-models)
  - [Large Language Models](#large-language-models)
    - [LLM Benchmark Method](#llm-benchmark-method)
    - [Qwen](#qwen)
    - [HunYuan](#hunyuan)
    - [Llama](#llama)
  - [Multimodal Large Models](#multimodal-large-models)
    - [Multimodal Benchmark Method](#multimodal-benchmark-method)
    - [VLM](#vlm)
    - [ASR](#asr)

## Base Models

- K1

 > - Inference engine version: spacemit-ort-2.0.2+beta1
 > - OS: bianbu-3.0
 > - Date: 2026-2-9

- K3

 > - Inference engine version: [v2.0.3](https://github.com/spacemit-com/onnxruntime/releases/download/2.0.3/spacemit-ort.riscv64.2.0.3.tar.gz)
 > - OS: bianbu-4.0rc3
 > - Date: 2026-5-26

### Benchmark Method

~~~bash
# Enter the spacemit-ort library path
# cd {spacemit_ort_lib}/
export LD_LIBRARY_PATH=./lib/

# Replace ${model_path} with your own model file path and ${num of cores} with the number of CPU cores to use
./bin/onnxruntime_perf_test ${model_path} -e spacemit -r 10 -x 1 -S 1 -s -c 1 -i "SPACEMIT_EP_INTRA_THREAD_NUM|${num of cores}" -I

# Example output:
using SpaceMITExecutionProvider
setting SPACEMIT_EP_INTRA_THREAD_NUM : 4
Setting intra_op_num_threads to 1
Session creation time cost: 0.169475 s
First inference time cost: 109 ms
Total inference time cost: 0.0727021 s
Total inference requests: 10
Average inference time cost total: 7.270205 ms
Total inference run time: 0.0727619 s
Number of inferences per second: 137.435
Avg CPU usage: 62 %
Peak working set size: 91336704 bytes
Avg CPU usage:62
Peak working set size:91336704
Runs:10
Min Latency: 0.00720383 s
Max Latency: 0.00730163 s
P50 Latency: 0.00727787 s
P90 Latency: 0.00730163 s
P95 Latency: 0.00730163 s
P99 Latency: 0.00730163 s
P999 Latency: 0.00730163 s

# "Average inference time cost total" indicates the single-frame inference latency.
~~~

### ResNet

- K1

| Model | Type | Shape | 1 Core/ms | 2 Core/ms | 4 Core/ms |
| --- | --- | --- | --- | --- | --- |
| [resnet18](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/resnet/resnet18.q.onnx) | int8 | 224x224 | 39.71 | 22.49 | 13.71 |
| [resnet50](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/resnet/resnet50.q.onnx) | int8 | 224x224 | 93.37 | 53.01 | 32.86 |
| [resnet50](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/resnet/resnet50.fp16.onnx) | fp16 | 224x224 | 667.55 | 349.34 | 217.27 |

- K3

| Model | Type | Shape | 1 Core/ms | 2 Core/ms | 4 Core/ms | 8 Core/ms |
| --- | --- | --- | --- | --- | --- | --- |
| [resnet18](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/resnet/resnet18.q.onnx) | int8 | 224x224 | 7.88 | 4.74 | 2.94 | 2.11 |
| [resnet50](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/resnet/resnet50.q.onnx) | int8 | 224x224 | 19.54 | 11.47 | 7.25 | 5.22 |
| [resnet50.batch4](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/resnet/resnet50.b4.q.onnx) | int8 | 224x224 | 73.37 | 40.19 | 23.19 | 15.55 |
| [resnet50](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/resnet/resnet50.fp16.onnx) | fp16 | 224x224 | 35.38 | 24.00 | 19.27 | 16.68 |

### MobileNet

- K1

| Model | Type | Shape | 1 Core/ms | 2 Core/ms | 4 Core/ms |
| --- | --- | --- | --- | --- | --- |
| [mobilenet_v1](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/mobilenet/mobilenet_v1.q.onnx) | int8 | 224x224 | 32.10 | 16.56 | 10.72 |
| [mobilenet_v2](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/mobilenet/mobilenet_v2.q.onnx) | int8 | 224x224 | 28.44 | 18.17 | 13.03 |
| [mobilenet_v3_small](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/mobilenet/mobilenet_v3_small.fp16.onnx) | fp16 | 224x224 | 24.22 | 16.84 | 12.44 |
| [mobilenet_v3_large](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/mobilenet/mobilenet_v3_large.fp16.onnx) | fp16 | 224x224 | 61.62 | 38.90 | 26.61 |

- K3

| Model | Type | Shape | 1 Core/ms | 2 Core/ms | 4 Core/ms | 8 Core/ms |
| --- | --- | --- | --- | --- | --- | --- |
| [mobilenet_v1](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/mobilenet/mobilenet_v1.q.onnx) | int8 | 224x224 | 12.71 | 7.24 | 3.95 | 2.38 |
| [mobilenet_v2](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/mobilenet/mobilenet_v2.q.onnx) | int8 | 224x224 | 17.35 | 9.80 | 5.14 | 3.29 |
| [mobilenet_v3_small](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/mobilenet/mobilenet_v3_small.fp16.onnx) | fp16 | 224x224 | 7.62 | 4.71 | 3.13 | 2.82 |
| [mobilenet_v3_large](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/mobilenet/mobilenet_v3_large.fp16.onnx) | fp16 | 224x224 | 13.68 | 8.32 | 5.28 | 4.14 |

### EfficientNet

- K1

| Model | Type | Shape | 1 Core/ms | 2 Core/ms | 4 Core/ms |
| --- | --- | --- | --- | --- | --- |
| [efficientnet_v1_b0](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v1_b0.q.onnx) | int8 | 224x224 | 68.81 | 40.65 | 26.30 |
| [efficientnet_v1_b1](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v1_b1.q.onnx) | int8 | 224x224 | 97.24 | 57.21 | 37.28 |
| [efficientnet_v2_s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v2_s.q.onnx) | int8 | 224x224 | 144.81 | 83.11 | 52.66 |
| [efficientnet_v1_b0](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v1_b0.fp16.onnx) | fp16 | 224x224 | 121.70 | 71.87 | 46.47 |
| [efficientnet_v1_b1](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v1_b1.fp16.onnx) | fp16 | 224x224 | 172.87 | 102.10 | 65.98 |
| [efficientnet_v2_s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v2_s.fp16.onnx) | fp16 | 224x224 | 563.58 | 305.40 | 176.87 |

- K3

| Model | Type | Shape | 1 Core/ms | 2 Core/ms | 4 Core/ms | 8 Core/ms |
| --- | --- | --- | --- | --- | --- | --- |
| [efficientnet_v1_b0](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v1_b0.q.onnx) | int8 | 224x224 | 33.32 | 18.66 | 10.36 | 7.93 |
| [efficientnet_v1_b1](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v1_b1.q.onnx) | int8 | 224x224 | 52.32 | 28.79 | 16.12 | 12.07 |
| [efficientnet_v2_s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v2_s.q.onnx) | int8 | 224x224 | 43.06 | 24.64 | 15.19 | 10.65 |
| [efficientnet_v1_b0](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v1_b0.fp16.onnx) | fp16 | 224x224 | 34.16 | 19.70 | 12.82 | 9.86 |
| [efficientnet_v1_b1](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v1_b1.fp16.onnx) | fp16 | 224x224 | 50.25 | 29.40 | 18.94 | 14.44 |
| [efficientnet_v2_s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v2_s.fp16.onnx) | fp16 | 224x224 | 55.02 | 32.48 | 20.85 | 14.25 |

### ViT

- K1

| Model | Type | Shape | 1 Core/ms | 2 Core/ms | 4 Core/ms |
| --- | --- | --- | --- | --- | --- |
| [vit_b_16](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/vit/vit_b_16.q.onnx) | int8 | 224x224 | 527.78 | 356.00 | 200.91 |
| [vit_b_16](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/vit/vit_b_16.fp16.onnx) | fp16 | 224x224 | 2557.03 | 1425.90 | 774.00 |

- K3

| Model | Type | Shape | 1 Core/ms | 2 Core/ms | 4 Core/ms | 8 Core/ms |
| --- | --- | --- | --- | --- | --- | --- |
| [vit_b_16](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/vit/vit_b_16.q.onnx) | int8 | 224x224 | 104.25 | 58.93 | 37.39 | 25.01 |
| [vit_b_16](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/vit/vit_b_16.fp16.onnx) | fp16 | 224x224 | 206.15 | 122.17 | 82.56 | 62.04 |

### YOLOv5

- K1

| Model | Type | Shape | 1 Core/ms | 2 Core/ms | 4 Core/ms |
| --- | --- | --- | --- | --- | --- |
| [yolov5n](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov5/yolov5n.q.onnx) | int8 | 640x640 | 233.24 | 149.24 | 111.18 |
| [yolov5s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov5/yolov5s.q.onnx) | int8 | 640x640 | 450.00 | 238.84 | 140.92 |
| [yolov5m](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov5/yolov5m.q.onnx) | int8 | 640x640 | 996.12 | 483.86 | 269.41 |

- K3

| Model | Type | Shape | 1 Core/ms | 2 Core/ms | 4 Core/ms | 8 Core/ms |
| --- | --- | --- | --- | --- | --- | --- |
| [yolov5n](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov5/yolov5n.q.onnx) | int8 | 640x640 | 44.72 | 24.56 | 14.51 | 9.80 |
| [yolov5s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov5/yolov5s.q.onnx) | int8 | 640x640 | 74.38 | 40.77 | 24.27 | 15.96 |
| [yolov5m](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov5/yolov5m.q.onnx) | int8 | 640x640 | 153.58 | 82.73 | 46.53 | 29.65 |

### YOLOv6

- K1

| Model | Type | Shape | 1 Core/ms | 2 Core/ms | 4 Core/ms |
| --- | --- | --- | --- | --- | --- |
| [yolov6n](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov6/yolov6n.q.onnx) | int8 | 640x640 | 177.65 | 100.04 | 62.43 |
| [yolov6s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov6/yolov6s.q.onnx) | int8 | 640x640 | 462.12 | 237.01 | 132.61 |

- K3

| Model | Type | Shape | 1 Core/ms | 2 Core/ms | 4 Core/ms | 8 Core/ms |
| --- | --- | --- | --- | --- | --- | --- |
| [yolov6n](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov6/yolov6n.q.onnx) | int8 | 640x640 | 32.93 | 18.59 | 11.11 | 7.72 |
| [yolov6s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov6/yolov6s.q.onnx) | int8 | 640x640 | 66.36 | 36.61 | 21.56 | 13.60 |

### YOLOv8

- K1

| Model | Type | Shape | 1 Core/ms | 2 Core/ms | 4 Core/ms |
| --- | --- | --- | --- | --- | --- |
| [yolov8n](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8/yolov8n.q.onnx) | int8 | 640x640 | 211.49 | 118.88 | 76.18 |
| [yolov8s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8/yolov8s.q.onnx) | int8 | 640x640 | 463.19 | 240.62 | 142.38 |
| [yolov8m](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8/yolov8m.q.onnx) | int8 | 640x640 | 994.91 | 510.06 | 284.39 |

- K3

| Model | Type | Shape | 1 Core/ms | 2 Core/ms | 4 Core/ms | 8 Core/ms |
| --- | --- | --- | --- | --- | --- | --- |
| [yolov8n](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8/yolov8n.q.onnx) | int8 | 640x640 | 43.05 | 23.91 | 14.23 | 9.82 |
| [yolov8s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8/yolov8s.q.onnx) | int8 | 640x640 | 76.96 | 42.41 | 25.52 | 17.14 |
| [yolov8m](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8/yolov8m.q.onnx) | int8 | 640x640 | 163.62 | 88.08 | 49.67 | 32.66 |

### YOLOv8-Seg

- K3

| Model | Type | Shape | 1 Core/ms | 2 Core/ms | 4 Core/ms | 8 Core/ms |
| --- | --- | --- | --- | --- | --- | --- |
| [yolov8n-seg](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8_seg/yolov8n-seg.q.onnx) | int8 | 640x640 | 68.70 | 37.34 | 21.44 | 13.97 |
| [yolov8s-seg](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8_seg/yolov8s-seg.q.onnx) | int8 | 640x640 | 111.86 | 60.74 | 35.67 | 23.22 |
| [yolov8m-seg](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8_seg/yolov8m-seg.q.onnx) | int8 | 640x640 | 216.20 | 115.77 | 64.78 | 41.56 |

### YOLOv8-Pose

- K3

| Model | Type | Shape | 1 Core/ms | 2 Core/ms | 4 Core/ms | 8 Core/ms |
| --- | --- | --- | --- | --- | --- | --- |
| [yolov8n-pose](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8_pose/yolov8n-pose.q.onnx) | int8 | 640x640 | 47.14 | 26.73 | 16.46 | 11.44 |
| [yolov8s-pose](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8_pose/yolov8s-pose.q.onnx) | int8 | 640x640 | 83.19 | 46.34 | 28.31 | 19.15 |
| [yolov8m-pose](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8_pose/yolov8m-pose.q.onnx) | int8 | 640x640 | 170.45 | 92.66 | 52.62 | 34.96 |

### YOLOv12

- K1

| Model | Type | Shape | 1 Core/ms | 2 Core/ms | 4 Core/ms |
| --- | --- | --- | --- | --- | --- |
| [yolo12n](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolo12/yolo12n.q.onnx) | int8 | 640x640 | 405.57 | 238.88 | 161.90 |
| [yolo12s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolo12/yolo12s.q.onnx) | int8 | 640x640 | 912.32 | 533.02 | 312.74 |
| [yolo12m](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolo12/yolo12m.q.onnx) | int8 | 640x640 | 2050.74 | 1096.84 | 661.23 |

- K3

| Model | Type | Shape | 1 Core/ms | 2 Core/ms | 4 Core/ms | 8 Core/ms |
| --- | --- | --- | --- | --- | --- | --- |
| [yolo12n](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolo12/yolo12n.q.onnx) | int8 | 640x640 | 119.64 | 64.88 | 38.08 | 27.60 |
| [yolo12s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolo12/yolo12s.q.onnx) | int8 | 640x640 | 218.19 | 117.37 | 68.71 | 48.16 |
| [yolo12m](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolo12/yolo12m.q.onnx) | int8 | 640x640 | 428.03 | 228.18 | 130.62 | 89.44 |

### Audio Models

- K1

| Model | Type | 4 Core/rtf |
| --- | --- | --- |
| melotts | dyn_int8 | 0.984 |
| [sensevoice](https://archive.spacemit.com/spacemit-ai/model_zoo/asr/sensevoice.tar.gz) | dyn_int8 | --- |

- K3

| Model | Type | 4 Core/rtf | 8 Core/rtf |
| --- | --- | --- | --- |
| melotts | dyn_int8 | 0.530 | --- |
| [sensevoice](https://archive.spacemit.com/spacemit-ai/model_zoo/asr/sensevoice.tar.gz) | dyn_int8 | 0.1124 | 0.1380 |

## Large Language Models

- K3

  > - llama.cpp version: [0.1.1](https://github.com/spacemit-com/llama.cpp/releases/download/spacemit-llama.cpp.riscv64.0.1.1/spacemit-llama.cpp.riscv64.0.1.1.tar.gz)
  > - OS: bianbu-4.0rc3
  > - Date: 2026-5-26

### LLM Benchmark Method

~~~bash
# Enter the spacemit-llama.cpp library path
# cd {spacemit-llama.cpp}/
export LD_LIBRARY_PATH=./lib/

# Replace ${model_path} with your own model file path and ${num of cores} with the number of CPU cores to use
./bin/llama-bench -m ${model_path} -t ${num of cores} -p 128 -n 128 -mmp 0 -fa 1 -ub 128

# Example output:
CPU_RISCV64_SPACEMIT: tcm is available, blk_size: 393216, blk_num: 8, is_fake_tcm: 0
CPU_RISCV64_SPACEMIT: num_cores: 16, num_perfer_cores: 8, perfer_core_arch_id: a064, exclude_main_thread: 0, use_ime1: 0, use_ime2: 1, mem_backend: HPAGE, cpu_mask: ff00, aicpu_id_offset: 8
CPU_RISCV64_SPACEMIT: alloc_chunk: open(/dev/tcm_sync_mem) failed, errno=2
CPU_RISCV64_SPACEMIT: failed to allocate init_barrier from shared mem, falling back to heap
| model                          |       size |     params | backend    | threads | n_ubatch | fa | mmap |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | -------: | -: | ---: | --------------: | -------------------: |
| qwen3 0.6B Q4_0                | 358.78 MiB |   596.05 M | CPU        |       8 |      128 |  1 |    0 |           pp128 |        499.75 ± 0.22 |
| qwen3 0.6B Q4_0                | 358.78 MiB |   596.05 M | CPU        |       8 |      128 |  1 |    0 |           tg128 |         53.35 ± 0.03 |
~~~

### Qwen

- K3

| Model | Quantization | PP128 (token/s) | TG128 (token/s) | PP1280 (token/s) | TG1280 (token/s) |
| --- | --- | --- | --- | --- | --- |
| [qwen3-0.6B](https://www.modelscope.cn/models/unsloth/Qwen3-0.6B-GGUF/file/view/master/Qwen3-0.6B-Q4_0.gguf?status=2) | Q4_0 | 499.75 | 53.35 | - | - |
| [qwen3-1.7B](https://www.modelscope.cn/models/unsloth/Qwen3-1.7B-GGUF/file/view/master/Qwen3-1.7B-Q4_0.gguf?status=2) | Q4_0 | 229.79 | 23.11 | - | - |
| [qwen3-4B](https://www.modelscope.cn/models/unsloth/Qwen3-4B-GGUF/file/view/master/Qwen3-4B-Q4_0.gguf?status=2) | Q4_0 | 76.44 | 11.03 | - | - |
| [qwen3-moe-30B-A3B](https://www.modelscope.cn/models/unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF/file/view/master/Qwen3-30B-A3B-Instruct-2507-Q4_0.gguf?status=2) | Q4_0 | 55.67 | 12.32 | 44.03 | 11.17 |
| [qwen3.5-0.8B](https://www.modelscope.cn/models/unsloth/Qwen3.5-0.8B-GGUF/file/view/master/Qwen3.5-0.8B-Q4_0.gguf?status=2) | Q4_0 | 182.69 | 29.33 | - | - |
| [qwen3.5-2B](https://www.modelscope.cn/models/unsloth/Qwen3.5-2B-GGUF/file/view/master/Qwen3.5-2B-Q4_0.gguf?status=2) | Q4_1 | 112.22 | 16.15 | - | - |

### HunYuan

- K3

| Model | Quantization | PP128 (token/s) | TG128 (token/s) | PP1280 (token/s) | TG1280 (token/s) |
| --- | --- | --- | --- | --- | --- |
| [HY-MT1.5-1.8B](https://www.modelscope.cn/models/Tencent-Hunyuan/HY-MT1.5-1.8B-GGUF/resolve/master/HY-MT1.5-1.8B-Q4_K_M.gguf) | Q4_K_M | 157.81 | 20.15 | - | - |

### Llama

- K3

| Model | Quantization | PP128 (token/s) | TG128 (token/s) | PP1280 (token/s) | TG1280 (token/s) |
| --- | --- | --- | --- | --- | --- |
| [llama2-7B](https://www.modelscope.cn/models/TheBloke/Llama-2-7B-GGUF/resolve/master/llama-2-7b.Q4_0.gguf) | Q4_0 | 50.40 | 7.07 | - | - |

## Multimodal Large Models

- K3

  > - llama.cpp version: [0.1.1](https://github.com/spacemit-com/llama.cpp/releases/download/spacemit-llama.cpp.riscv64.0.1.1/spacemit-llama.cpp.riscv64.0.1.1.tar.gz)
  > - Inference engine version: [v2.0.3](https://github.com/spacemit-com/onnxruntime/releases/download/2.0.3/spacemit-ort.riscv64.2.0.3.tar.gz)
  > - OS: bianbu-4.0rc3
  > - Date: 2026-5-26

### Multimodal Benchmark Method

> Using `qwen3vlencoder` as an example:

```bash
export LD_LIBRARY_PATH=./spacemit-llama.cpp/lib:./spacemit_ort/lib
export SPACEMIT_EP_DENSE_ACCURACY_LEVEL=1

llama-server -m qwen3vl-30b-text-q4_1.gguf --media-backend smt --smt-config-dir ./ -ctk f16 -ctv f16 -t 8 -c 1024 --host 0.0.0.0 --port 8080 --reasoning-budget 0 --reasoning off
```

> For detailed parameter descriptions, see [llama.cpp](llama.cpp.md).

### VLM

- K3

| Model | Image Size | LLM 8 Core + VisionEncoder 4 Core/ms | LLM 8 Core + VisionEncoder 8 Core/ms |
| --- | --- | --- | --- |
| [fastvlm-0.5B](https://archive.spacemit.com/spacemit-ai/model_zoo/vlm/fastvlm-mm-0.5b-q4_1.tar.gz) | 512*512 | 256.47 | 164.50 |
| [Qwen3-VL-30B-A3B](https://archive.spacemit.com/spacemit-ai/model_zoo/vlm/qwen30ba3b-mm-q4_1.tar.gz) | 768*768 | 7928.13 | 4753.55 |
| [Qwen3.5-0.8B](https://archive.spacemit.com/spacemit-ai/model_zoo/vlm/Qwen3.5-0.8B.tar.gz) | 384*384 | 340.42 | 245.61 |
| [Qwen3.5-2B](https://archive.spacemit.com/spacemit-ai/model_zoo/vlm/Qwen3.5-2B.tar.gz) | 384*384 | 901.56 | 794.03 |
| [Qwen3.5-4B](https://archive.spacemit.com/spacemit-ai/model_zoo/vlm/Qwen3.5-4B.tar.gz) | 384*384 | 904.73 | 798.71 |

### ASR

- K3

| Model | Quantization | Thread Configuration | RTF |
| --- | --- | --- | --- |
| [Qwen3-ASR 0.6B](https://archive.spacemit.com/spacemit-ai/model_zoo/asr/qwen3-asr-0.6B-dynq-q40.tar.gz) | Q4_0 + dynamic ONNX | LLM 8 / AudioEncoder 4 | 0.169 |
| [Qwen3-ASR 1.7B](https://archive.spacemit.com/spacemit-ai/model_zoo/asr/qwen3-asr-1.7B-dynq-q40.tar.gz) | Q4_0 + dynamic ONNX | LLM 8 / AudioEncoder 4 | 0.329 |
| [Fun-ASR Nano](https://archive.spacemit.com/spacemit-ai/model_zoo/asr/fun-asr-nano-2512-qq-q4km.tar.gz) | Q4_K_M + quantized ONNX | LLM 4 / AudioEncoder 4 | 0.247 |
| [Gemma4 ASR E2B](https://archive.spacemit.com/spacemit-ai/model_zoo/asr/gemma4-asr-E2B-q40.tar.gz) | Q4_0 + quantized ONNX | llama-server 8 / AudioEncoder default | 0.689 (transcription) / 0.578 (translation) |

Qwen3-ASR 0.6B and 1.7B were each measured for three rounds with
`001_zh_daily_weather.wav` and `004_zh_selling_sausages.wav`: 47.331 seconds
of audio and 7.977 and 15.572 seconds of total processing time, respectively.
Fun-ASR Nano was measured with one Chinese, one English, and one Japanese
sample: 28.558 seconds of audio per round and 7.063 seconds of processing time
after warmup. Gemma4 ASR transcription used `004_zh_selling_sausages.wav`:
14.158 seconds of audio and 9.758 seconds of processing time. Its translation
measurement used two rounds of Japanese, Korean, and Cantonese speech-to-English
samples: 34.104 seconds of audio and 19.703 seconds of processing time after
warmup. The first request that initialized the dynamic ONNX encoder session was
excluded. The reported RTF values are end-to-end results. Because the test sets
and tasks differ, these RTF values should not be used to directly compare
recognition or translation quality.
