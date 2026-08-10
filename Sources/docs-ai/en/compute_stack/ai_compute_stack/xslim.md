---
sidebar_position: 4
---

# XSlim

> **XSlim** is a post-training quantization (PTQ) tool from **SpacemiT**. It ships with chip-tuned quantization strategies out of the box and exposes a unified API driven by a JSON configuration file. The source code is available at [github-xslim](https://github.com/spacemit-com/xslim).

---

- [XSlim](#xslim)
  - [Quick Start](#quick-start)
  - [Quantization Configuration](#quantization-configuration)
  - [Accuracy Tuning](#accuracy-tuning)
  - [Changelog](#changelog)

## Quick Start

**Install**

```bash
pip install xslim
```

**Python API**

```python
import xslim

demo_json = dict()
# Populate demo_json with the required fields (see Configuration below)

demo_json_path = "./demo_json.json"

# Pass a config dict directly
xslim.quantize_onnx_model(demo_json)

# Or pass a path to a JSON config file
xslim.quantize_onnx_model(demo_json_path)

# The API also accepts an optional model path or an in-memory ONNX proto:
# xslim.quantize_onnx_model("resnet18.json", "/home/share/modelzoo/classification/resnet18/resnet18.onnx")

# xslim.quantize_onnx_model(
#    "resnet18.json", "/home/share/modelzoo/classification/resnet18/resnet18.onnx", "resnet18_output.onnx"
# )

# import onnx
# onnx_model = onnx.load("/home/share/modelzoo/classification/resnet18/resnet18.onnx")
# quantized_onnx_model = xslim.quantize_onnx_model("resnet18.json", onnx_model)
```

**Shell**

```bash
python -m xslim --config ./demo_json.json

# Specify input and output model paths explicitly
python -m xslim -c ./demo_json.json -i demo.onnx -o demo.q.onnx

# Dynamic quantization — no JSON config required
python -m xslim -i demo.onnx -o demo.q.onnx --dynq

# Convert to FP16 — no JSON config required
python -m xslim -i demo.onnx -o demo.q.onnx --fp16

# Model slimming only, no quantization — no JSON config required
python -m xslim -i demo.onnx -o demo.q.onnx
```

---

## Quantization Configuration

**JSON config example**

```json
{
    "model_parameters": {
        "onnx_model": "",          // Path to the ONNX model
        "output_prefix": "",       // Optional. Prefix for the output quantized model filename
        "working_dir": "",         // Optional. Output directory and working directory for intermediate files
        "skip_onnxsim": false      // Skip onnxslim graph simplification. Default: false
    },
    "calibration_parameters": {
        "calibration_step": 100,   // Optional. Max number of calibration samples. Default: 100
        "calibration_device": "cpu", // Optional. Default: cuda (auto-detected), fallback: cpu
        "calibration_type": "default", // Optional. Default: default. Options: kl, minmax, percentile, mse
        "input_parameters": [
            {
                "input_name": "data",              // Optional. Read from the model if omitted
                "input_shape": [1, 3, 224, 224],   // Optional. Read from the model if omitted
                "dtype": "float32",                // Optional. Read from the model if omitted
                "file_type": "img",                // Optional. Default: img. Options: img, npy, raw
                "color_format": "bgr",             // Optional. Default: bgr
                "mean_value": [103.94, 116.78, 123.68], // Optional. Default: none
                "std_value": [57, 57, 57],         // Optional. Default: none
                "preprocess_file": "",             // Custom preprocessing script (path:function).
                                                   // Built-in presets: PT_IMAGENET, IMAGENET
                "data_list_path": ""               // Required. Path to the calibration data list file
            },
            {
                "input_name": "data1",
                "input_shape": [1, 3, 224, 224],
                "dtype": "float32",
                "file_type": "img",
                "mean_value": [103.94, 116.78, 123.68],
                "std_value": [57, 57, 57],
                "preprocess_file": "",
                "data_list_path": ""
            }
        ]
    },
    // All fields below are optional
    "quantization_parameters": {
        "analysis_enable": true,   // Enable post-quantization analysis. Default: true
        "precision_level": 0,
        "finetune_level": 1,       // Default: 1. Options: 0, 1, 2, 3
        "max_percentile": 0.9999,  // Clipping ratio for percentile calibration
        "custom_setting": [
            // Applies to all quantizable ops enclosed by the specified input/output edges.
            // Constant inputs on the input side may be omitted.
            {
                "input_names": ["aaa", "bbb"],
                "output_names": ["ccc"],
                "max_percentile": 0.999,
                "precision_level": 2,
                "calibration_type": "default"
            }
        ],
        "truncate_var_names": ["/Concat_5_output_0", "/Transpose_6_output_0"] // Truncate the graph at these tensor names
    }
}
```

**Optional fields reference**

| Field | Default | Options | Notes |
| --- | --- | --- | --- |
| `output_prefix` | Model filename without extension; output ends in `.q.onnx` | — | |
| `working_dir` | Directory containing `onnx_model` | — | |
| `calibration_step` | `100` | | Recommended range: 100–1000 |
| `calibration_device` | `cuda` | `cuda`, `cpu` | Auto-detected by the system |
| `calibration_type` | `default` | `default`, `kl`, `minmax`, `percentile`, `mse` | Start with `default`; try `percentile` or `minmax` if accuracy is insufficient |
| `input_name` | Read from the ONNX model | | |
| `input_shape` | Read from the ONNX model | | All dimensions must be integers; symbolic batch dimensions default to 1 |
| `dtype` | Read from the ONNX model | `float32`, `int8`, `uint8`, `int16` | Only `float32` is supported at this time |
| `file_type` | `img` | `img`, `npy`, `raw` | `raw` files must match `dtype` (i.e., `float32` by default) |
| `preprocess_file` | `None` | `PT_IMAGENET`, `IMAGENET` | Two standard ImageNet preprocessing presets are built in |
| `finetune_level` | `1` | `0`, `1`, `2`, `3` | `0`: no aggressive parameter calibration; `1`: may apply some static calibration; `2+`: calibrates based on per-block quantization loss |
| `precision_level` | `0` | `0`, `1`, `2`, `3`, `4` | `0`: full int8 (tuning stays within int8); `1–2`: partial int8, suitable for typical Transformer models; `3`: dynamic quantization; `4`: FP16 |
| `max_percentile` | `0.9999` | | Clipping range for percentile calibration; minimum allowed value is `0.99` |
| `custom_setting` | `None` | | |
| `truncate_var_names` | `[]` | | Splits the graph into two subgraphs at the specified tensor names; the split result is validated and an error is raised if invalid |

**Calibration data list format**

Each line in the list file (e.g. `img_list.txt`) is a path to one calibration sample. Paths can be absolute or relative to the directory containing the list file. For multi-input models, ensure the ordering across all input list files is consistent.

```
QuantZoo/Data/Imagenet/Calib/n01440764/ILSVRC2012_val_00002138.JPEG
QuantZoo/Data/Imagenet/Calib/n01443537/ILSVRC2012_val_00000994.JPEG
QuantZoo/Data/Imagenet/Calib/n01484850/ILSVRC2012_val_00014467.JPEG
QuantZoo/Data/Imagenet/Calib/n01491361/ILSVRC2012_val_00003204.JPEG
QuantZoo/Data/Imagenet/Calib/n01494475/ILSVRC2012_val_00015545.JPEG
QuantZoo/Data/Imagenet/Calib/n01496331/ILSVRC2012_val_00008640.JPEG
```

**Custom `preprocess_file`**

Set `preprocess_file` to `<script_path>:<function_name>` to point to a specific function in a Python script. For example, given `custom_preprocess.py`, set the field to `custom_preprocess.py:preprocess_impl`. For multi-input models, the same preprocessing function can often be reused across inputs.

```python
from typing import Sequence
import torch
import cv2
import numpy as np

def preprocess_impl(path_list: Sequence[str], input_parametr: dict) -> torch.Tensor:
    """
    Reads a batch of files from path_list, applies preprocessing according to
    input_parametr, and returns a batched torch.Tensor.

    Args:
        path_list (Sequence[str]): List of file paths for one calibration batch.
        input_parametr (dict): Corresponds to calibration_parameters.input_parameters[idx]
                               in the config file.

    Returns:
        torch.Tensor: A batched tensor of calibration data.
    """
    batch_list = []
    mean_value = input_parametr["mean_value"]
    std_value = input_parametr["std_value"]
    input_shape = input_parametr["input_shape"]
    for file_path in path_list:
        img = cv2.imread(file_path)
        img = cv2.resize(img, (input_shape[-1], input_shape[-2]), interpolation=cv2.INTER_AREA)
        img = img.astype(np.float32)
        img = (img - mean_value) / std_value
        img = np.transpose(img, (2, 0, 1))
        img = torch.from_numpy(img)
        img = torch.unsqueeze(img, 0)
        batch_list.append(img)
    return torch.cat(batch_list, dim=0)
```

## Accuracy Tuning

See [github-xslim-accuracy-tuning](https://github.com/spacemit-com/xslim/blob/main/doc/accuracy_tuning_zh.md) for details.

## Changelog

See [github-xslim-releases](https://github.com/spacemit-com/xslim/releases) for the full release history.
