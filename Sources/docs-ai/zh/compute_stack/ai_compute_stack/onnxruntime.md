sidebar_position: 1

# SpacemiT-ONNXRuntime

 > **SpacemiT-ONNXRuntime**包含[ONNXRuntime](https://github.com/microsoft/onnxruntime)基础推理库与SpacemiT-ExecutionProvider加速后端，并保持了整体架构的解耦，因此其使用方法与社区版本ONNXRuntime几乎一致。

 ## 平台支持情况

|      平台 & 系统       |       是否支持      |
|-----------------------|-----------------------|
| K1 Buildroot          | ✅ 支持                |
| K1 OpenHarmony5.0     | ❌ 不支持              |
| K1 Bianbu LXQT/GNOME  | ✅ 支持                |
| K3 Buildroot          | ✅ 支持                |
| K3 OpenHarmony6.1     | ❌ 不支持              |
| K3 Bianbu LXQT/GNOME  | ✅ 支持                |

 ---

- [SpacemiT-ONNXRuntime](#spacemit-onnxruntime)
  - [平台支持情况](#平台支持情况)
  - [QuickStart](#quickstart)
      - [资源获取](#资源获取)
      - [ONNXRuntime模型推理](#onnxruntime模型推理)
      - [SpacemiT-ExecutionProvider后端](#spacemit-executionprovider后端)
      - [快速验证模型性能](#快速验证模型性能)
  - [ProviderOption说明](#provideroption说明)
      - [`SPACEMIT_EP_INTRA_THREAD_NUM`](#spacemit_ep_intra_thread_num)
      - [`SPACEMIT_EP_INTRA_THREAD_AFFINITY`](#spacemit_ep_intra_thread_affinity)
      - [`SPACEMIT_EP_INTER_THREAD_NUM`](#spacemit_ep_inter_thread_num)
      - [`SPACEMIT_EP_USE_GLOBAL_INTRA_THREAD`](#spacemit_ep_use_global_intra_thread)
      - [`SPACEMIT_EP_DUMP_SUBGRAPHS`](#spacemit_ep_dump_subgraphs)
      - [`SPACEMIT_EP_DEBUG_PROFILE`](#spacemit_ep_debug_profile)
      - [`SPACEMIT_EP_DUMP_TENSORS`](#spacemit_ep_dump_tensors)
      - [`SPACEMIT_EP_DISABLE_OP_TYPE_FILTER`](#spacemit_ep_disable_op_type_filter)
      - [`SPACEMIT_EP_DISABLE_OP_NAME_FILTER`](#spacemit_ep_disable_op_name_filter)
      - [`SPACEMIT_EP_DISABLE_FLOAT16_EPILOGUE`](#spacemit_ep_disable_float16_epilogue)
      - [`SPACEMIT_EP_DENSE_ACCURACY_LEVEL`](#spacemit_ep_dense_accuracy_level)
  - [Demo说明](#demo说明)
    - [onnxruntime\_perf\_test](#onnxruntime_perf_test)
    - [onnx\_test\_runner](#onnx_test_runner)
  - [EP算子说明](#ep算子说明)
  - [模型性能数据](#模型性能数据)
  - [FAQ](#faq)

## QuickStart

#### 资源获取
可在[spacemit-onnxruntime](https://github.com/spacemit-com/onnxruntime/releases)路径获得当前最新的发布库，以及订阅release通知，或在bainbu系统内通过包安装获得库资源


```shell
sudo apt-get update
sudo apt-get install -y spacemit-onnxruntime libopencv-dev python3-spacemit-ort python3-pillow python3-matplotlib python3-opencv
```

#### ONNXRuntime模型推理
详情可以参考社区文档[ONNXRuntime推理介绍](https://onnxruntime.ai/docs/#onnx-runtime-for-inferencing)，以及通过[ONNXRuntime示例](https://github.com/microsoft/onnxruntime-inference-examples)获取代码示例

#### SpacemiT-ExecutionProvider后端

* C&C++

~~~
#include <onnxruntime_cxx_api.h>
#include "spacemit_ort_env.h"

Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "demo");
Ort::SessionOptions session_options;
std::unordered_map<std::string, std::string> provider_options;

// 以下为ep的配置，可选
// provider_options["SPACEMIT_EP_DISABLE_FLOAT16_EPILOGUE"] = "1"; 禁止使用近似后处理
// provider_options["SPACEMIT_EP_DUMP_SUBGRAPHS"] = "1"; 导出ep编译子图，在执行程序的目录下，以SpaceMITExecutionProvider_SpineSubgraph_为前缀的ONNX模型
// provider_options["SPACEMIT_EP_DEBUG_PROFILE"] = "demo"; 导出ep执行profile, 以传入字符串为前缀的json
SessionOptionsSpaceMITEnvInit(session_options, provider_options);
Ort::Session session(env, net_param_path, session_options);

// ...后续与社区版ONNXRuntime一致
~~~

* Python

~~~
import onnxruntime as ort
import numpy as np
import spacemit_ort

eps = ort.get_available_providers()
net_param_path = "resnet18.q.onnx"

# provider_options的定义与C++版本一致
ep_provider_options = {}
# 导出ep编译子图，在执行程序的目录下，以SpaceMITExecutionProvider_SpineSubgraph_为前缀的ONNX模型
# ep_provider_options ["SPACEMIT_EP_DUMP_SUBGRAPHS"] = "1";
# 导出ep执行profile, 以传入字符串为前缀的json
# ep_provider_options ["SPACEMIT_EP_DEBUG_PROFILE"] = "demo";

session = ort.InferenceSession(net_param_path,
                providers=["SpaceMITExecutionProvider"],
                provider_options=[ep_provider_options ])

input_tensor = np.ones((1, 3, 224, 224), dtype=np.float32)
outputs = session.run(None, {"data": input_tensor})
~~~

#### 快速验证模型性能
> &#x2139;&#xfe0f;可参考[spacemit-demo](https://github.com/spacemit-com/spacemit-demo)

 ---

## ProviderOption说明
#### `SPACEMIT_EP_INTRA_THREAD_NUM`
>+ 单独指定ep的线程数，并与ONNXRuntime的intra_thread_num独立
>+ &#x2139;&#xfe0f;如果只设置session_options的intra_thread_num，则相当于SPACEMIT_EP_INTRA_THREAD_NUM=intra_thread_num，并启动2 * intra_thread_num个计算线程
~~~ C++
std::unordered_map<std::string, std::string> provider_options;
provider_options["SPACEMIT_EP_INTRA_THREAD_NUM"] = "4";
~~~

#### `SPACEMIT_EP_INTRA_THREAD_AFFINITY`
>+ 指定ep的线程亲和性，分号间隔，数量与`SPACEMIT_EP_INTRA_THREAD_NUM`一致
~~~ C++
std::unordered_map<std::string, std::string> provider_options;
provider_options["SPACEMIT_EP_INTRA_THREAD_NUM"] = "4";
// 具体绑定核心，需要根据K1、K3实际情况判定
provider_options["SPACEMIT_EP_INTRA_THREAD_AFFINITY"] = "8;10;12;14";
~~~

#### `SPACEMIT_EP_INTER_THREAD_NUM`
>+ 指定ep的多会话推理，相当于SPACEMIT_EP_INTRA_THREAD_NUM * SPACEMIT_EP_INTER_THREAD_NUM
>+ 若SPACEMIT_EP_INTER_THREAD_NUM=2，则可以在两个线程中跑同一个Session，达成多路推理的效果
~~~ C++
std::unordered_map<std::string, std::string> provider_options;
provider_options["SPACEMIT_EP_INTRA_THREAD_NUM"] = "4";
provider_options["SPACEMIT_EP_INTER_THREAD_NUM"] = "2";
~~~

#### `SPACEMIT_EP_USE_GLOBAL_INTRA_THREAD`
>+ 在同一个进程内，对所有带ep的session使用同一个intra线程池
~~~ C++
std::unordered_map<std::string, std::string> provider_options;
// "1"表示enable，其他表示disable
provider_options["SPACEMIT_EP_USE_GLOBAL_INTRA_THREAD"] = "1";

SessionOptionsSpaceMITEnvInit(session_options, provider_options);
Ort::Session session0(env, net_param_path, session_options);

SessionOptionsSpaceMITEnvInit(session_options, provider_options);
Ort::Session session1(env, net_param_path, session_options);

// session0和session1将共享EP的线程资源，请保证session和session1不同时执行推理
~~~

#### `SPACEMIT_EP_DUMP_SUBGRAPHS`
>+ 导出ep编译子图，在执行程序的目录下，以SpaceMITExecutionProvider_SpineSubgraph_为前缀的ONNX模型
>+ &#x2139;&#xfe0f;可用于检查ep在推理这个模型时，切分了多少子图，子图数量越少越好
>+ &#x2139;&#xfe0f;支持通过环境变量设置
~~~ C++
std::unordered_map<std::string, std::string> provider_options;
// "1"表示enable，其他表示disable
provider_options["SPACEMIT_EP_DUMP_SUBGRAPHS"] = "1";
~~~

#### `SPACEMIT_EP_DEBUG_PROFILE`
>+ 导出ep执行profile, 以传入字符串为前缀的json，与ort的profile独立
>+ 可以使用Google Trace、或[perfetto](https://www.ui.perfetto.dev/)打开Json文件并查看每个算子的执行情况
>+ 支持通过环境变量设置
~~~ C++
std::unordered_map<std::string, std::string> provider_options;
// 该值表示profile json文件的前缀
provider_options["SPACEMIT_EP_DEBUG_PROFILE"] = "profile_";
~~~

#### `SPACEMIT_EP_DUMP_TENSORS`
>+ 导出ep执行时的每层结果, 以传入字符串为文件夹
>+ &#x2139;&#xfe0f;支持通过环境变量设置
~~~ C++
std::unordered_map<std::string, std::string> provider_options;
// 该值表示导出Tensor NPY文件的文件夹，若不存在，EP会自行创建这个文件夹
provider_options["SPACEMIT_EP_DUMP_TENSORS"] = "dump";
~~~

#### `SPACEMIT_EP_DISABLE_OP_TYPE_FILTER`
>+ 禁止EP推理某些OP类型
>+ &#x2139;&#xfe0f;支持通过环境变量设置
~~~ C++
std::unordered_map<std::string, std::string> provider_options;
// 使用;间隔表示
provider_options["SPACEMIT_EP_DISABLE_OP_TYPE_FILTER"] = "Conv;Gemm";
~~~

#### `SPACEMIT_EP_DISABLE_OP_NAME_FILTER`
>+ 禁止EP推理某些命名的OP
>+ &#x2139;&#xfe0f;支持通过环境变量设置
~~~ C++
std::unordered_map<std::string, std::string> provider_options;
// 使用;间隔表示
provider_options["SPACEMIT_EP_DISABLE_OP_TYPE_FILTER"] = "Conv1;Conv2";
~~~

#### `SPACEMIT_EP_DISABLE_FLOAT16_EPILOGUE`
>+ 禁止使用FP16后处理，例如量化模式下Conv、Gemm的Scale会内部优化为FP16
>+ &#x2139;&#xfe0f;支持通过环境变量设置
~~~ C++
std::unordered_map<std::string, std::string> provider_options;
// "1"表示禁用，其他表示无效
provider_options["SPACEMIT_EP_DISABLE_FLOAT16_EPILOGUE"] = "1";
~~~

#### `SPACEMIT_EP_DENSE_ACCURACY_LEVEL`
>+ 指定动态量化模型中Online MatMul的精度等级
>+ 0：动态量化
>+ 1：FP16
>+ 2+：FP32
>+ &#x2139;&#xfe0f;支持通过环境变量设置
~~~ C++
std::unordered_map<std::string, std::string> provider_options;
provider_options["SPACEMIT_EP_DENSE_ACCURACY_LEVEL"] = "1";
~~~

## Demo说明

### onnxruntime_perf_test
* Shell
~~~ bash
# cd spacemit-ort.riscv64.x.x.x
export LD_LIBRARY_PATH=./lib
# 执行
./bin/onnxruntime_perf_test resnet50.q.onnx -e spacemit -r 1 -x 1 -c 1 -S 1 -I
~~~

* 常用参数说明:
>+ -e: 指定使用的后端，例如`-e spacemit`
>+ -r: 指定测试次数，例如`-r 10`
>+ -x: 指定使用线程数
>+ -c: 指定同时发起多少个推理会话
>+ -S: 给定随机种子，产生相同的输入数据。这默认为-1
>+ -I: 生成输入绑定
>+ -s: 显示统计结果
>+ -p: 生成运行日志

### onnx_test_runner
onnx_test_runner 主要用于验证和测试 ONNX 模型是否正确实现了其预期功能，以及在不同执行后端（例如SpaceMITExecutionProvider）上的正确性和一致性。其核心用途是：
> - 验证模型正确性​：确保从训练框架（如 PyTorch、TensorFlow）导出的 ONNX 模型在 ONNX Runtime 中的推理结果与原始框架一致。
> - 检查算子支持​：验证模型所使用的算子是否被特定的执行提供程序（如 CPU, GPU, NPU 等）支持。
> - 跨平台一致性检查​：保证同一个模型在不同硬件后端（如 CPU、ArmNN、ACL、CUDA 等）上运行的结果是可靠的。
> - 性能测试（辅助）​​：虽然主要关注正确性，但其输出的运行时间也能提供初步的性能参考（更专业的性能测试建议使用 onnxruntime_perf_test）。

* Shell
~~~ bash
onnx_test_runner [选项] <测试数据目录>

#添加环境变量
export LD_LIBRARY_PATH=PATH_TO_YOUR_LIB
#执行
./onnx_test_runner {.....}/resnet50.q-imagenet -j 1 -X 4 -e spacemit
~~~

* 测试数据目录组织
~~~
mobilenetv2
├── mobilenetv2.onnx      # ONNX 模型文件
└── test_data0            # 测试数据目录
    ├── input0.pb         # 输入张量（protocol buffer 格式）
    └── output_0.pb       # 期望的输出张量
└── test_data1
    ├── input0.pb
    └── output_0.pb
~~~

* 常用参数说明
>+ -e 指定EP。这是最关键的选项之一，用于选择在哪个硬件后端上运行测试。
>+ -X 并行运行测试的线程数。
>+ -c 并发运行的会话数。
>+ -r 重复运行测试的次数，可用于稳定性测试。
>+ -v 输出更详细的信息。

## [EP算子说明](./onnxruntime_ep_ops.md)
> &#x2139;&#xfe0f;EP支持的算子表示能够被EP组织为子图并由EP后端推理，不支持的算子将回退至ONNXRuntime的CPUProvider
> &#x2139;&#xfe0f;EP支持的算子算子列表会不断扩充，可根据相关模型瓶颈情况提出需求

## [模型性能数据](./modelzoo.md)
> 以ONNXRuntime+SpaceMITExecutionProvider进行推理，通过onnxruntime_perf_test获得模型性能数据

## [FAQ](./onnxruntime_ep_faq.md)
> 可在[进迭时空开发者社区](https://forum.spacemit.com/)提出问题，我们将尽快给出答复
> 可在[SpacemiT-ONNXRuntime开源页面](https://github.com/spacemit-com/onnxruntime)提出Issues
