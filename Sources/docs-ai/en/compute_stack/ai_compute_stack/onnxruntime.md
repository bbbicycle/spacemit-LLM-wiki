sidebar_position: 1

# SpacemiT-ONNXRuntime
  
**SpacemiT-ONNXRuntime** integrates the base inference library of [ONNXRuntime](https://github.com/microsoft/onnxruntime) with the SpacemiT ExecutionProvider acceleration backend. The overall architecture remains decoupled, so its usage is almost identical to the community version of ONNXRuntime.

## Platform Support

| Platform & OS               | Support |
|-----------------------------|----------------|
| K1 Buildroot                | ✅ Yes    |
| K1 OpenHarmony 5.0          | ❌ No|
| K1 Bianbu LXQT/GNOME        | ✅ Yes    |
| K3 Buildroot                | ✅ Yes    |
| K3 OpenHarmony 6.1          | ❌ No|
| K3 Bianbu LXQT/GNOME        | ✅ Yes    |

---

- [SpacemiT-ONNXRuntime](#spacemit-onnxruntime)
  - [Platform Support](#platform-support)
  - [QuickStart](#quickstart)
    - [Getting Resources](#getting-resources)
    - [ONNXRuntime Model Inference](#onnxruntime-model-inference)
      - [SpacemiT-ExecutionProvider Backend](#spacemit-executionprovider-backend)
      - [Quick Performance Validation](#quick-performance-validation)
  - [Provider Option Reference](#provider-option-reference)
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
  - [Demo Guide](#demo-guide)
    - [`onnxruntime_perf_test`](#onnxruntime_perf_test)
    - [`onnx_test_runner`](#onnx_test_runner)
  - [EP Operator Support](#ep-operator-support)
  - [Model Performance Data](#model-performance-data)
  - [FAQ](#faq)

## QuickStart

### Getting Resources

The latest release is available at [spacemit-onnxruntime](https://github.com/spacemit-com/onnxruntime/releases). You can also subscribe to release notifications, or install via the package manager on Bianbu systems:

```shell
sudo apt-get update
sudo apt-get install -y spacemit-onnxruntime libopencv-dev python3-spacemit-ort python3-pillow python3-matplotlib python3-opencv
```

### ONNXRuntime Model Inference

For details, refer to

- The community documentation [ONNXRuntime Inference Overview](https://onnxruntime.ai/docs/#onnx-runtime-for-inferencing)
- Code examples from [ONNXRuntime Inference Examples](https://github.com/microsoft/onnxruntime-inference-examples)

#### SpacemiT-ExecutionProvider Backend

- **C&C++**

```c++
#include <onnxruntime_cxx_api.h>
#include "spacemit_ort_env.h"

Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "demo");
Ort::SessionOptions session_options;
std::unordered_map<std::string, std::string> provider_options;

// Optional EP configurations
// provider_options["SPACEMIT_EP_DISABLE_FLOAT16_EPILOGUE"] = "1"; // Disable approximate epilogue
// provider_options["SPACEMIT_EP_DUMP_SUBGRAPHS"] = "1"; // Dump compiled EP subgraphs as ONNX models
// provider_options["SPACEMIT_EP_DEBUG_PROFILE"] = "demo"; // Dump EP execution profile as JSON

SessionOptionsSpaceMITEnvInit(session_options, provider_options);
Ort::Session session(env, net_param_path, session_options);

// ... remaining usage is identical to community ONNXRuntime
```

- **Python**

```python
import onnxruntime as ort
import numpy as np
import spacemit_ort

eps = ort.get_available_providers()
net_param_path = "resnet18.q.onnx"

# provider_options are the same as in C++
ep_provider_options = {}
# Dump EP-compiled subgraphs as ONNX models in the execution directory,
# with filenames prefixed by "SpaceMITExecutionProvider_SpineSubgraph_"
# ep_provider_options["SPACEMIT_EP_DUMP_SUBGRAPHS"] = "1"

# Dump EP execution profiling data as a JSON file,
# using the specified string as the filename prefix
# ep_provider_options["SPACEMIT_EP_DEBUG_PROFILE"] = "demo"


session = ort.InferenceSession(net_param_path,
                providers=["SpaceMITExecutionProvider"],
                provider_options=[ep_provider_options ])

input_tensor = np.ones((1, 3, 224, 224), dtype=np.float32)
outputs = session.run(None, {"data": input_tensor})
```

#### Quick Performance Validation

Refer to [spacemit-demo](https://github.com/spacemit-com/spacemit-demo)

## Provider Option Reference

### `SPACEMIT_EP_INTRA_THREAD_NUM`

- Explicitly sets the number of threads used by the EP, independent of ONNXRuntime `intra_thread_num`
- If only `session_options.intra_thread_num` is set, it is equivalent to `SPACEMIT_EP_INTRA_THREAD_NUM = intra_thread_num`, and `2 × intra_thread_num` compute threads are launched

```cpp
std::unordered_map<std::string, std::string> provider_options;
provider_options["SPACEMIT_EP_INTRA_THREAD_NUM"] = "4";
```

### `SPACEMIT_EP_INTRA_THREAD_AFFINITY`

- Specifies the thread affinity for EP threads, separated by semicolons. The count must match `SPACEMIT_EP_INTRA_THREAD_NUM`

```c++
std::unordered_map<std::string, std::string> provider_options;
provider_options["SPACEMIT_EP_INTRA_THREAD_NUM"] = "4";
// Pin to specific cores — adjust based on actual K1/K3 topology
provider_options["SPACEMIT_EP_INTRA_THREAD_AFFINITY"] = "8;10;12;14";
```

### `SPACEMIT_EP_INTER_THREAD_NUM`

- Enables multi-session inference within the EP, equivalent to `SPACEMIT_EP_INTRA_THREAD_NUM × SPACEMIT_EP_INTER_THREAD_NUM` total threads
- For example, setting `SPACEMIT_EP_INTER_THREAD_NUM=2` allows the same Session to run on two threads simultaneously, achieving multi-stream inference

```c++
std::unordered_map<std::string, std::string> provider_options;
provider_options["SPACEMIT_EP_INTRA_THREAD_NUM"] = "4";
provider_options["SPACEMIT_EP_INTER_THREAD_NUM"] = "2";
```

### `SPACEMIT_EP_USE_GLOBAL_INTRA_THREAD`

- Use a shared intra-thread pool for all EP-enabled sessions within the same process

```c++
std::unordered_map<std::string, std::string> provider_options;
// 1: Enable; Others: Disable
provider_options["SPACEMIT_EP_USE_GLOBAL_INTRA_THREAD"] = "1";

SessionOptionsSpaceMITEnvInit(session_options, provider_options);
Ort::Session session0(env, net_param_path, session_options);

SessionOptionsSpaceMITEnvInit(session_options, provider_options);
Ort::Session session1(env, net_param_path, session_options);

// session0 and session1 share EP thread resources;
// ensure they do not run inference concurrently
```

### `SPACEMIT_EP_DUMP_SUBGRAPHS`

- Exports the subgraphs compiled by the SpacemiT Execution Provider (EP). The exported ONNX models are saved in the program’s working directory with the prefix `SpaceMITExecutionProvider_SpineSubgraph_`.
- This is useful to **check how many subgraphs EP creates** when running inference on a model. Fewer subgraphs usually indicate better performance.
- Supports environment variable configuration

```c++
std::unordered_map<std::string, std::string> provider_options;
// "1" to enable, any other value to disable
provider_options["SPACEMIT_EP_DUMP_SUBGRAPHS"] = "1";
```

### `SPACEMIT_EP_DEBUG_PROFILE`

- Exports the execution profile of the SpacemiT Execution Provider (EP) as a JSON file, using the given string as a filename prefix. This profile is **independent from the standard ONNX Runtime profile**.
- You can open the JSON file with **Google Trace** or [Perfetto](https://www.ui.perfetto.dev/) to inspect the execution time of each operator.
- Supports environment variable configuration

```c++
std::unordered_map<std::string, std::string> provider_options;
// This value sets the prefix for the profile JSON files
provider_options["SPACEMIT_EP_DEBUG_PROFILE"] = "profile_";
```

### `SPACEMIT_EP_DUMP_TENSORS`

- Dump intermediate tensor results during EP execution into the specified directory
- Supports environment variable configuration

```c++
std::unordered_map<std::string, std::string> provider_options;
// This value specifies the directory used to store dumped tensor (.npy) files
provider_options["SPACEMIT_EP_DUMP_TENSORS"] = "dump";
```

### `SPACEMIT_EP_DISABLE_OP_TYPE_FILTER`

- Prevents the Execution Provider (EP) from handling specific **operator types** during inference.
- Supports environment variable configuration

```c++
std::unordered_map<std::string, std::string> provider_options;
// Use semicolons (;) to separate multiple operator types
provider_options["SPACEMIT_EP_DISABLE_OP_TYPE_FILTER"] = "Conv;Gemm";
```

### `SPACEMIT_EP_DISABLE_OP_NAME_FILTER`

- Disable EP execution for specific operator types
- Supports environment variable configuration

```c++
std::unordered_map<std::string, std::string> provider_options;
// Use semicolons (;) to separate multiple operator types
provider_options["SPACEMIT_EP_DISABLE_OP_TYPE_FILTER"] = "Conv1;Conv2";
```

#### `SPACEMIT_EP_DISABLE_FLOAT16_EPILOGUE`

- Disable FP16 epilogue optimizations, e.g., FP16 scaling in quantized Conv/Gemm
- Supports environment variable configuration

```c++
std::unordered_map<std::string, std::string> provider_options;
// 1: Disable; Others: Invalid
provider_options["SPACEMIT_EP_DISABLE_FLOAT16_EPILOGUE"] = "1";
```

#### `SPACEMIT_EP_DENSE_ACCURACY_LEVEL`

- Specifies the precision level of **Online MatMul** in dynamic quantization models
- 0: Dynamic Quantization
- 1: FP16
- 2+: FP32
- ℹ️ Can be configured via environment variable

```c++
std::unordered_map<std::string, std::string> provider_options;
provider_options["SPACEMIT_EP_DENSE_ACCURACY_LEVEL"] = "1";
```

## Demo Guide

### `onnxruntime_perf_test`

**Shell Command**

```bash
# cd spacemit-ort.riscv64.x.x.x
export LD_LIBRARY_PATH=./lib
# run
./bin/onnxruntime_perf_test resnet50.q.onnx -e spacemit -r 1 -x 1 -c 1 -S 1 -I
```

**Common Parameter Descriptions**

- `-e`: Specifies the execution provider (backend) to use, e.g. `-e spacemit`
- `-r`: Sets number of runs, e.g. `-r 10`
- `-x`: Defines number of threads to use
- `-c`: Specifies the number of concurrent inference sessions to launch
- `-S`: Sets a random seed to generate reproducible input data. Default: -1 (random)
- `-I`: Enables pre-allocation and binding of input tensors
- `-s`: Displays detailed statistical results
- `-p`: Generates a runtime logs

### `onnx_test_runner`

The `onnx_test_runner` is primarily used to validate and test ONNX models, ensuring they correctly implement the intended functionality and produce consistent results across different execution providers (e.g., SpaceMITExecutionProvider). Its core purposes include:

- Model Correctness Validation: Verifies that an ONNX model exported from a training framework (such as PyTorch or TensorFlow) produces inference results in ONNX Runtime that match those from the original framework.
- Operator Support Checking: Confirms whether the operators used in the model are supported by the specified execution provider (e.g., CPU, GPU, NPU).
- Cross-Platform Consistency: Ensures reliable and identical results when running the same model on different hardware backends (e.g., CPU, ArmNN, ACL, CUDA).
- Auxiliary Performance Insights: While focused on correctness, it also reports execution times, providing basic performance references (for detailed performance benchmarking, use `onnxruntime_perf_test` instead).

**Shell Command**

``` bash
onnx_test_runner [options] <test_data_directory>

# Set the library path environment variable
export LD_LIBRARY_PATH=PATH_TO_YOUR_LIB
# Run
./onnx_test_runner {.....}/resnet50.q-imagenet -j 1 -X 4 -e spacemit
```

**Test Data Directory Layout**

```
mobilenetv2
├── mobilenetv2.onnx      # ONNX model file
└── test_data0            # Test case directory
    ├── input0.pb         # Input tensor（protocol buffer format）
    └── output_0.pb       # Expected output tensor
└── test_data1
    ├── input0.pb
    └── output_0.pb
```

**Common Parameter Descriptions**

- `-e`: Specifies the execution provider (EP) to use. This is one of the most important options for selecting the target hardware backend. Example: `-e spacemit`
- `-X`: Sets number of parallel test threads
- `-c`: Specifies number of concurrent sessions
- `-r`: Defines the number of repetitions for each test (useful for stability validation)
- `-v`: Outputs more detailed information

## [EP Operator Support](./onnxruntime_ep_ops.md)

- Supported operators can be grouped into subgraphs and executed by the EP.
- Unsupported operators fall back to ONNXRuntime CPUExecutionProvider.
- The supported operator list is continuously expanding based on model bottlenecks.

## [Model Performance Data](./modelzoo.md)

- Performance results obtained using ONNXRuntime + SpaceMITExecutionProvider with `onnxruntime_perf_test`.

## [FAQ](./onnxruntime_ep_faq.md)

Questions can be raised in the [SpacemiT Developer Community](https://forum.spacemit.com/), and we will respond as soon as possible.
Issues can be submitted on the [SpacemiT ONNX Runtime repository on GitHub](https://github.com/spacemit-com/onnxruntime).
