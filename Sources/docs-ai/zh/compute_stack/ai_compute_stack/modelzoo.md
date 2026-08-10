sidebar_position: 9

# ModelZoo
>
> ModelZoo内模型数据定期更新，模型应用示例请参考[ai-sdk
> ](https://github.com/spacemit-com/ai-sdk)

- [ModelZoo](#modelzoo)
  - [基础模型](#基础模型)
    - [测试方式](#测试方式)
    - [resnet](#resnet)
    - [mobilenet](#mobilenet)
    - [efficientnet](#efficientnet)
    - [vit](#vit)
    - [yolov5](#yolov5)
    - [yolov6](#yolov6)
    - [yolov8](#yolov8)
    - [yolov8-seg](#yolov8-seg)
    - [yolov8-pose](#yolov8-pose)
    - [yolov12](#yolov12)
    - [音频模型](#音频模型)
  - [大模型](#大模型)
    - [测试方式](#测试方式-1)
    - [Qwen](#qwen)
    - [HunYuan](#hunyuan)
    - [Llama](#llama)
  - [多模态大模型](#多模态大模型)
    - [测试方式](#测试方式-2)
    - [VLM](#vlm)
    - [ASR](#asr)

## 基础模型
- K1
>- 推理引擎版本: spacemit-ort-2.0.2+beta1
>- OS：bianbu-3.0
>- date：2026-2-9

- K3
>- 推理引擎版本: [v2.0.3](https://github.com/spacemit-com/onnxruntime/releases/download/2.0.3/spacemit-ort.riscv64.2.0.3.tar.gz)
>- OS：bianbu-4.0rc3
>- date：2026-5-26

### 测试方式
~~~
# 进入spacemit-ort库路径
# cd {spacemit_ort_lib}/
export LD_LIBRARY_PATH=./lib/

# 调整为自己的${model_path}(模型文件路径)，${num of cores}(选择跑几个核心)
./bin/onnxruntime_perf_test ${model_path} -e spacemit -r 10 -x 1 -S 1 -s -c 1 -i "SPACEMIT_EP_INTRA_THREAD_NUM|${num of cores}" -I

# 输出信息如下
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

# Average inference time cost total即单帧推理耗时
~~~

### resnet

- K1

| 模型名 | type | shape | 1 Core/ms | 2 Core/ms | 4 Core/ms |
| --- | --- | --- | --- | --- | --- |
| [resnet18](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/resnet/resnet18.q.onnx) | int8 | 224x224 | 39.71 | 22.49 | 13.71 |
| [resnet50](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/resnet/resnet50.q.onnx) | int8 | 224x224 | 93.37 | 53.01 | 32.86 |
| [resnet50](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/resnet/resnet50.fp16.onnx) | fp16 | 224x224 | 667.55 | 349.34 | 217.27 |

- K3

| 模型名 | type | shape | 1 Core/ms | 2 Core/ms | 4 Core/ms | 8 Core/ms |
| --- | --- | --- | --- | --- | --- | --- |
| [resnet18](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/resnet/resnet18.q.onnx) | int8 | 224x224 | 7.88 | 4.74 | 2.94 | 2.11 |
| [resnet50](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/resnet/resnet50.q.onnx) | int8 | 224x224 | 19.54 | 11.47 | 7.25 | 5.22 |
| [resnet50.batch4](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/resnet/resnet50.b4.q.onnx) | int8 | 224x224 | 73.37 | 40.19 | 23.19 | 15.55 |
| [resnet50](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/resnet/resnet50.fp16.onnx) | fp16 | 224x224 | 35.38 | 24.00 | 19.27 | 16.68 |

### mobilenet

- K1

| 模型名 | type | shape | 1 Core/ms | 2 Core/ms | 4 Core/ms |
| --- | --- | --- | --- | --- | --- |
| [mobilenet_v1](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/mobilenet/mobilenet_v1.q.onnx) | int8 | 224x224 | 32.10 | 16.56 | 10.72 |
| [mobilenet_v2](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/mobilenet/mobilenet_v2.q.onnx) | int8 | 224x224 | 28.44 | 18.17 | 13.03 |
| [mobilenet_v3_small](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/mobilenet/mobilenet_v3_small.fp16.onnx) | fp16 | 224x224 | 24.22 | 16.84 | 12.44 |
| [mobilenet_v3_large](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/mobilenet/mobilenet_v3_large.fp16.onnx) | fp16 | 224x224 | 61.62 | 38.90 | 26.61 |

- K3

| 模型名 | type | shape | 1 Core/ms | 2 Core/ms | 4 Core/ms | 8 Core/ms |
| --- | --- | --- | --- | --- | --- |---|
| [mobilenet_v1](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/mobilenet/mobilenet_v1.q.onnx) | int8 | 224x224 | 12.71 | 7.24 | 3.95 | 2.38 |
| [mobilenet_v2](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/mobilenet/mobilenet_v2.q.onnx) | int8 | 224x224 | 17.35 | 9.80 | 5.14 | 3.29 |
| [mobilenet_v3_small](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/mobilenet/mobilenet_v3_small.fp16.onnx) | fp16 | 224x224 | 7.62 | 4.71 | 3.13 | 2.82 |
| [mobilenet_v3_large](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/mobilenet/mobilenet_v3_large.fp16.onnx) | fp16 | 224x224 | 13.68 | 8.32 | 5.28 | 4.14 |

### efficientnet

- K1

| 模型名 | type | shape | 1 Core/ms | 2 Core/ms | 4 Core/ms |
| --- | --- | --- | --- | --- | --- |
| [efficientnet_v1_b0](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v1_b0.q.onnx) | int8 | 224x224 | 68.81 | 40.65 | 26.30 |
| [efficientnet_v1_b1](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v1_b1.q.onnx) | int8 | 224x224 | 97.24 | 57.21 | 37.28 |
| [efficientnet_v2_s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v2_s.q.onnx) | int8 | 224x224 | 144.81 | 83.11 | 52.66 |
| [efficientnet_v1_b0](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v1_b0.fp16.onnx) | fp16 | 224x224 | 121.70 | 71.87 | 46.47 |
| [efficientnet_v1_b1](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v1_b1.fp16.onnx) | fp16 | 224x224 | 172.87 | 102.10 | 65.98 |
| [efficientnet_v2_s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v2_s.fp16.onnx) | fp16 | 224x224 | 563.58 | 305.40 | 176.87 |

- K3

| 模型名 | type | shape | 1 Core/ms | 2 Core/ms | 4 Core/ms | 8 Core/ms |
| --- | --- | --- | --- | --- | --- |---|
| [efficientnet_v1_b0](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v1_b0.q.onnx) | int8 | 224x224 | 33.32 | 18.66 | 10.36 | 7.93 |
| [efficientnet_v1_b1](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v1_b1.q.onnx) | int8 | 224x224 | 52.32 | 28.79 | 16.12 | 12.07 |
| [efficientnet_v2_s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v2_s.q.onnx) | int8 | 224x224 | 43.06 | 24.64 | 15.19 | 10.65 |
| [efficientnet_v1_b0](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v1_b0.fp16.onnx) | fp16 | 224x224 | 34.16 | 19.70 | 12.82 | 9.86 |
| [efficientnet_v1_b1](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v1_b1.fp16.onnx) | fp16 | 224x224 | 50.25 | 29.40 | 18.94 | 14.44 |
| [efficientnet_v2_s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/efficientnet/efficientnet_v2_s.fp16.onnx) | fp16 | 224x224 | 55.02 | 32.48 | 20.85 | 14.25 |

### vit

- K1

| 模型名 | type | shape | 1 Core/ms | 2 Core/ms | 4 Core/ms |
| --- | --- | --- | --- | --- | --- |
| [vit_b_16](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/vit/vit_b_16.q.onnx) | int8 | 224x224 | 527.78 | 356.00 | 200.91 |
| [vit_b_16](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/vit/vit_b_16.fp16.onnx) | fp16 | 224x224 | 2557.03 | 1425.90 | 774.00 |

- K3

| 模型名 | type | shape | 1 Core/ms | 2 Core/ms | 4 Core/ms | 8 Core/ms |
| --- | --- | --- | --- | --- | --- | --- |
| [vit_b_16](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/vit/vit_b_16.q.onnx) | int8 | 224x224 | 104.25 | 58.93 | 37.39 | 25.01 |
| [vit_b_16](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/vit/vit_b_16.fp16.onnx) | fp16 | 224x224 | 206.15 | 122.17 | 82.56 | 62.04 |

### yolov5

- K1

| 模型名 | type | shape | 1 Core/ms | 2 Core/ms | 4 Core/ms |
| --- | --- | --- | --- | --- | --- |
| [yolov5n](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov5/yolov5n.q.onnx) | int8 | 640x640 | 233.24 | 149.24 | 111.18 |
| [yolov5s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov5/yolov5s.q.onnx) | int8 | 640x640 | 450.00 | 238.84 | 140.92 |
| [yolov5m](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov5/yolov5m.q.onnx) | int8 | 640x640 | 996.12 | 483.86 | 269.41 |

- K3

| 模型名 | type | shape | 1 Core/ms | 2 Core/ms | 4 Core/ms | 8 Core/ms |
| --- | --- | --- | --- | --- | --- | --- |
| [yolov5n](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov5/yolov5n.q.onnx) | int8 | 640x640 | 44.72 | 24.56 | 14.51 | 9.80 |
| [yolov5s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov5/yolov5s.q.onnx) | int8 | 640x640 | 74.38 | 40.77 | 24.27 | 15.96 |
| [yolov5m](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov5/yolov5m.q.onnx) | int8 | 640x640 | 153.58 | 82.73 | 46.53 | 29.65 |

### yolov6

- K1

| 模型名 | type | shape | 1 Core/ms | 2 Core/ms | 4 Core/ms |
| --- | --- | --- | --- | --- | --- |
| [yolov6n](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov6/yolov6n.q.onnx) | int8 | 640x640 | 177.65 | 100.04 | 62.43 |
| [yolov6s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov6/yolov6s.q.onnx) | int8 | 640x640 | 462.12 | 237.01 | 132.61 |

- K3

| 模型名 | type | shape | 1 Core/ms | 2 Core/ms | 4 Core/ms | 8 Core/ms |
| --- | --- | --- | --- | --- | --- | --- |
| [yolov6n](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov6/yolov6n.q.onnx) | int8 | 640x640 | 32.93 | 18.59 | 11.11 | 7.72 |
| [yolov6s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov6/yolov6s.q.onnx) | int8 | 640x640 | 66.36 | 36.61 | 21.56 | 13.60 |

### yolov8
- K1

| 模型名 | type | shape | 1 Core/ms | 2 Core/ms | 4 Core/ms |
| --- | --- | --- | --- | --- | --- |
| [yolov8n](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8/yolov8n.q.onnx) | int8 | 640x640 | 211.49 | 118.88 | 76.18 |
| [yolov8s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8/yolov8s.q.onnx) | int8 | 640x640 | 463.19 | 240.62 | 142.38 |
| [yolov8m](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8/yolov8m.q.onnx) | int8 | 640x640 | 994.91 | 510.06 | 284.39 |

- K3

| 模型名 | type | shape | 1 Core/ms | 2 Core/ms | 4 Core/ms | 8 Core/ms |
| --- | --- | --- | --- | --- | --- | --- |
| [yolov8n](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8/yolov8n.q.onnx) | int8 | 640x640 | 43.05 | 23.91 | 14.23 | 9.82 |
| [yolov8s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8/yolov8s.q.onnx) | int8 | 640x640 | 76.96 | 42.41 | 25.52 | 17.14 |
| [yolov8m](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8/yolov8m.q.onnx) | int8 | 640x640 | 163.62 | 88.08 | 49.67 | 32.66 |

### yolov8-seg

- K3

| 模型名 | type | shape | 1 Core/ms | 2 Core/ms | 4 Core/ms | 8 Core/ms |
| --- | --- | --- | --- | --- | --- | --- |
| [yolov8n-seg](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8_seg/yolov8n-seg.q.onnx) | int8 | 640x640 | 68.70 | 37.34 | 21.44 | 13.97 |
| [yolov8s-seg](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8_seg/yolov8s-seg.q.onnx) | int8 | 640x640 | 111.86 | 60.74 | 35.67 | 23.22 |
| [yolov8m-seg](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8_seg/yolov8m-seg.q.onnx) | int8 | 640x640 | 216.20 | 115.77 | 64.78 | 41.56 |

### yolov8-pose

- K3

| 模型名 | type | shape | 1 Core/ms | 2 Core/ms | 4 Core/ms | 8 Core/ms |
| --- | --- | --- | --- | --- | --- | --- |
| [yolov8n-pose](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8_pose/yolov8n-pose.q.onnx) | int8 | 640x640 | 47.14 | 26.73 | 16.46 | 11.44 |
| [yolov8s-pose](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8_pose/yolov8s-pose.q.onnx) | int8 | 640x640 | 83.19 | 46.34 | 28.31 | 19.15 |
| [yolov8m-pose](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolov8_pose/yolov8m-pose.q.onnx) | int8 | 640x640 | 170.45 | 92.66 | 52.62 | 34.96 |

### yolov12

- K1

| 模型名 | type | shape | 1 Core/ms | 2 Core/ms | 4 Core/ms |
| --- | --- | --- | --- | --- | --- |
| [yolo12n](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolo12/yolo12n.q.onnx) | int8 | 640x640 | 405.57 | 238.88 | 161.90 |
| [yolo12s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolo12/yolo12s.q.onnx) | int8 | 640x640 | 912.32 | 533.02 | 312.74 |
| [yolo12m](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolo12/yolo12m.q.onnx) | int8 | 640x640 | 2050.74 | 1096.84 | 661.23 |

- K3

| 模型名 | type | shape | 1 Core/ms | 2 Core/ms | 4 Core/ms | 8 Core/ms |
| --- | --- | --- | --- | --- | --- | --- |
| [yolo12n](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolo12/yolo12n.q.onnx) | int8 | 640x640 | 119.64 | 64.88 | 38.08 | 27.60 |
| [yolo12s](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolo12/yolo12s.q.onnx) | int8 | 640x640 | 218.19 | 117.37 | 68.71 | 48.16 |
| [yolo12m](https://archive.spacemit.com/spacemit-ai/model_zoo/vision/yolo12/yolo12m.q.onnx) | int8 | 640x640 | 428.03 | 228.18 | 130.62 | 89.44 |

### 音频模型

- K1

| 模型名 | type | 4 Core/rtf |
| --- | --- | --- |
| melotts | dyn_int8  | 0.984 |
| [sensevoice](https://archive.spacemit.com/spacemit-ai/model_zoo/asr/sensevoice.tar.gz) | dyn_int8 | --- |

- K3

| 模型名 | type | 4 Core/rtf | 8 Core/rtf |
| --- | --- | --- | --- |
| melotts | dyn_int8  | 0.530 | --- |
| [sensevoice](https://archive.spacemit.com/spacemit-ai/model_zoo/asr/sensevoice.tar.gz) | dyn_int8 | 0.1124 | 0.1380 |

## 大模型

- K3
>- llama.cpp版本：[0.1.1](https://github.com/spacemit-com/llama.cpp/releases/download/spacemit-llama.cpp.riscv64.0.1.1/spacemit-llama.cpp.riscv64.0.1.1.tar.gz)
>- OS：bianbu-4.0rc3
>- date：2026-5-26

### 测试方式
~~~
# 进入spacemit-llama.cpp库路径
# cd {spacemit-llama.cpp}/
export LD_LIBRARY_PATH=./lib/

# 调整为自己的${model_path}(模型文件路径)，${num of cores}(选择跑几个核心)
./bin/llama-bench -m ${model_path} -t ${num of cores} -p 128 -n 128 -mmp 0 -fa 1 -ub 128

# 输出信息如下
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

| 模型名 | 量化类型 | PP128 (token/s) | TG128 (token/s) | PP1280 (token/s) | TG1280 (token/s) |
| --- | --- | --- | --- | --- | --- |
| [qwen3-0.6B](https://www.modelscope.cn/models/unsloth/Qwen3-0.6B-GGUF/file/view/master/Qwen3-0.6B-Q4_0.gguf?status=2) | Q4_0 | 499.75 | 53.35 | - | - |
| [qwen3-1.7B](https://www.modelscope.cn/models/unsloth/Qwen3-1.7B-GGUF/file/view/master/Qwen3-1.7B-Q4_0.gguf?status=2) | Q4_0 | 229.79 | 23.11 | - | - |
| [qwen3-4B](https://www.modelscope.cn/models/unsloth/Qwen3-4B-GGUF/file/view/master/Qwen3-4B-Q4_0.gguf?status=2) | Q4_0 | 76.44 | 11.03 | - | - |
| [qwen3-moe-30B-A3B](https://www.modelscope.cn/models/unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF/file/view/master/Qwen3-30B-A3B-Instruct-2507-Q4_0.gguf?status=2) | Q4_0 | 55.67 | 12.32 | 44.03 | 11.17
| [qwen3.5-0.8B](https://www.modelscope.cn/models/unsloth/Qwen3.5-0.8B-GGUF/file/view/master/Qwen3.5-0.8B-Q4_0.gguf?status=2) | Q4_0 | 182.69 | 29.33 | - | - |
| [qwen3.5-2B](https://www.modelscope.cn/models/unsloth/Qwen3.5-2B-GGUF/file/view/master/Qwen3.5-2B-Q4_0.gguf?status=2) | Q4_1 | 112.22 | 16.15 | - | - |

### HunYuan

- K3

| 模型名 | 量化类型 | PP128 (token/s) | TG128 (token/s) | PP1280 (token/s) | TG1280 (token/s) |
| --- | --- | --- | --- | --- | --- |
| [HY-MT1.5-1.8B](https://www.modelscope.cn/models/Tencent-Hunyuan/HY-MT1.5-1.8B-GGUF/resolve/master/HY-MT1.5-1.8B-Q4_K_M.gguf) | Q4_K_M | 157.81 | 20.15 | - | - |

### Llama

- K3

| 模型名 | 量化类型 | PP128 (token/s) | TG128 (token/s) | PP1280 (token/s) | TG1280 (token/s) |
| --- | --- | --- | --- | --- | --- |
| [llama2-7B](https://www.modelscope.cn/models/TheBloke/Llama-2-7B-GGUF/resolve/master/llama-2-7b.Q4_0.gguf) | Q4_0 | 50.40 | 7.07 | - | - |

## 多模态大模型

- K3
>- llama.cpp版本：[0.1.1](https://github.com/spacemit-com/llama.cpp/releases/download/spacemit-llama.cpp.riscv64.0.1.1/spacemit-llama.cpp.riscv64.0.1.1.tar.gz)
>- 推理引擎版本: [v2.0.3](https://github.com/spacemit-com/onnxruntime/releases/download/2.0.3/spacemit-ort.riscv64.2.0.3.tar.gz)
>- OS：bianbu-4.0rc3
>- date：2026-5-26

### 测试方式


> 以qwen3vlencoder为例

```bash
export LD_LIBRARY_PATH=./spacemit-llama.cpp/lib:./spacemit_ort/lib
export SPACEMIT_EP_DENSE_ACCURACY_LEVEL=1

llama-server -m qwen3vl-30b-text-q4_1.gguf --media-backend smt --smt-config-dir ./ -ctk f16 -ctv f16 -t 8 -c 1024 --host 0.0.0.0 --port 8080 --reasoning-budget 0 --reasoning off
```
> 详细参数含义见llama.cpp.md

### VLM

- K3

| 模型名 | 图像规格 | LLM 8 Core + VisionEncoder 4 Core/ms | LLM 8 Core + VisionEncoder 8 Core/ms |
| --- | --- | --- | --- |
| [fastvlm-0.5B](https://archive.spacemit.com/spacemit-ai/model_zoo/vlm/fastvlm-mm-0.5b-q4_1.tar.gz) | 512*512 | 256.47 | 164.50 |
| [Qwen3-VL-30B-A3B](https://archive.spacemit.com/spacemit-ai/model_zoo/vlm/qwen30ba3b-mm-q4_1.tar.gz) | 768*768 | 7928.13 | 4753.55 |
| [Qwen3.5-0.8B](https://archive.spacemit.com/spacemit-ai/model_zoo/vlm/Qwen3.5-0.8B.tar.gz) | 384*384 | 340.42 | 245.61 |
| [Qwen3.5-2B](https://archive.spacemit.com/spacemit-ai/model_zoo/vlm/Qwen3.5-2B.tar.gz) | 384*384 | 901.56 | 794.03 |
| [Qwen3.5-4B](https://archive.spacemit.com/spacemit-ai/model_zoo/vlm/Qwen3.5-4B.tar.gz) | 384*384 | 904.73 | 798.71 |

### ASR

- K3

| 模型名 | 量化方式 | 线程配置 | RTF |
| --- | --- | --- | --- |
| [Qwen3-ASR 0.6B](https://archive.spacemit.com/spacemit-ai/model_zoo/asr/qwen3-asr-0.6B-dynq-q40.tar.gz) | Q4_0 + 动态量化 ONNX | LLM 8 / AudioEncoder 4 | 0.169 |
| [Qwen3-ASR 1.7B](https://archive.spacemit.com/spacemit-ai/model_zoo/asr/qwen3-asr-1.7B-dynq-q40.tar.gz) | Q4_0 + 动态量化 ONNX | LLM 8 / AudioEncoder 4 | 0.329 |
| [Fun-ASR Nano](https://archive.spacemit.com/spacemit-ai/model_zoo/asr/fun-asr-nano-2512-qq-q4km.tar.gz) | Q4_K_M + 量化 ONNX | LLM 4 / AudioEncoder 4 | 0.247 |
| [Gemma4 ASR E2B](https://archive.spacemit.com/spacemit-ai/model_zoo/asr/gemma4-asr-E2B-q40.tar.gz) | Q4_0 + 量化 ONNX | llama-server 8 / AudioEncoder 默认 | 0.689（转写）/ 0.578（翻译） |

Qwen3-ASR 0.6B 和 1.7B 均使用 `001_zh_daily_weather.wav` 和
`004_zh_selling_sausages.wav` 连续测试 3 轮，总音频时长 47.331 秒，总处理时间分别为
7.977 秒和 15.572 秒。Fun-ASR Nano 使用中文、英文、日文三条音频测试，单轮总音频
时长 28.558 秒，预热后处理时间 7.063 秒。Gemma4 ASR 中文转写使用
`004_zh_selling_sausages.wav`，音频时长 14.158 秒，处理时间 9.758 秒；翻译使用
日语、韩语、粤语样例连续测试 2 轮，总音频时长 34.104 秒，预热后处理时间
19.703 秒。首个动态 ONNX encoder session 初始化请求未计入。表中 RTF 为端到端
结果。由于测试集和任务不同，各模型的 RTF 不宜直接横向比较识别或翻译质量。
