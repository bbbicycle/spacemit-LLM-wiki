sidebar_position: 4

# XSlim
> **XSlim**是**SpacemiT**推出的PTQ量化工具，集成了已经调整好的适配芯片的量化策略，使用Json配置文件调用统一接口实现模型量化。同时开源于[github-xslim](https://github.com/spacemit-com/xslim)


---

- [XSlim](#xslim)
  - [QuickStart](#quickstart)
  - [量化参数配置](#量化参数配置)
  - [量化精度调优](#量化精度调优)
  - [ChangeLog](#changelog)

## QuickStart
- Install
~~~
pip install xslim
~~~

- Python
~~~ python
import xslim

demo_json = dict()
# 以下缺省对demo_json内容的填入

demo_json_path = "./demo_json.json"
# 使用字典的方式
xslim.quantize_onnx_model(demo_json)
# 使用json文件的方式
xslim.quantize_onnx_model(demo_json_path)

# 支持API调用时传入模型路径或模型Proto
# xslim.quantize_onnx_model("resnet18.json", "/home/share/modelzoo/classification/resnet18/resnet18.onnx")

# xslim.quantize_onnx_model(
#    "resnet18.json", "/home/share/modelzoo/classification/resnet18/resnet18.onnx", "resnet18_output.onnx"
# )

# import onnx
# onnx_model = onnx.load("/home/share/modelzoo/classification/resnet18/resnet18.onnx")
# quantized_onnx_model = xslim.quantize_onnx_model("resnet18.json", onnx_model)
~~~

- Shell
~~~ bash
python -m xslim --config ./demo_json.json
# 指定输入以及输出模型路径
python -m xslim -c ./demo_json.json -i demo.onnx -o demo.q.onnx
# 使用动态量化，不需要json配置文件
python -m xslim -i demo.onnx -o demo.q.onnx --dynq
# 转为FP16，不需要json配置文件
python -m xslim -i demo.onnx -o demo.q.onnx --fp16
# 不量化仅模型精简，不需要json配置文件
python -m xslim -i demo.onnx -o demo.q.onnx
~~~

---

## 量化参数配置
- Json配置示例
~~~
{
    "model_parameters" : {
        "onnx_model": "", "onnx模型的目录"
        "output_prefix": "", "可缺省，输出量化模型文件的前缀"
        "working_dir": "" "可缺省，输出目录以及量化时产生文件的存放目录"
        "skip_onnxsim": false "跳过使用onnxslim化简模型，默认为false"
    },
    "calibration_parameters" : {
        "calibration_step": 100, "可缺省，限制最大的校准文件个数，默认为100"
        "calibration_device": "cpu", "可缺省，默认为cuda，自动检测，否则为cpu"
        "calibration_type": "default",  "可缺省，默认为default，可选kl、minmax、percentile、mse"
        "input_parameters": [
            {
                "input_name": "data", "可缺省，由工具从模型中读取",
                "input_shape": [1, 3, 224, 224], "可缺省，输入的shape，由工具从模型中读取"
                "dtype": "float32", "可缺省，当前输入的数据类型，由工具从模型中读取"
                "file_type": "img", "可缺省，默认为img，校准文件的类型，可以有img，npy，raw"
                "color_format": "bgr", "可缺省，默认为bgr"
                "mean_value": [103.94, 116.78, 123.68], "可缺省，默认为空"
                "std_value": [57, 57, 57], "可缺省，默认为空"
                "preprocess_file": "", "自定义预处理方法的py脚本文件，
                                        内部预设了PT_IMAGENET,IMAGENET字段直接使用"
                "data_list_path": "" "不可缺省，校准数据列表的路径"
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
    "以下均可缺省"
    "quantization_parameters": {
        "analysis_enable": true, "开启量化后分析，默认为true"
        "precision_level": 0
        "finetune_level": 1 "默认为1， 可选0， 1， 2，3"
        "max_percentile": 0.9999 "指定percentile量化时的占比"
        "custom_setting": [
            "出入边包围的全部量化算子，入边可不写常量"
            {
                "input_names": ["aaa", "bbb"],
                "output_names": ["ccc"],
                "max_percentile": 0.999,
                "precision_level": 2,
                "calibration_type": "default"
            }
        ],
        "truncate_var_names": ["/Concat_5_output_0", "/Transpose_6_output_0"] "截断模型"
    }
}
~~~

- 可以省略的字段

| 字段名 | 默认值 | 可选值 | 备注 |
| --- | --- | --- | --- |
| output_prefix | onnx_model的去后缀文件名，输出以.q.onnx结尾 | / |  |
| working_dir | onnx_model所在的目录 | / |  |
| calibration_step | 100 |  | 一般建议设置为100-1000范围 |
| calibration_device | cuda | cuda、cpu | 系统自动检测 |
| calibration_type | default | default、kl、minmax、percentile、mse | 推荐先使用default，而后是percentile或minmax |
| input_name | 从onnx模型中读取 |  |  |
| input_shape | 从onnx模型中读取 |  | 需要shape为全int，支持batch为符号，并默认填为1 |
| dtype | 从onnx模型中读取<br> | float32、int8、uint8、int16<br> | - 当前仅支持float32 |
| file_type | img | img、npy、raw | - 只支持读取与dtype一致的raw数据，即默认为float32 |
| preprocess_file | None | PT_IMAGENET、IMAGENET | 系统预设了两种IMAGENET标准预处理 |
| finetune_level | 1 | 0，1，2，3 | - 0，不进行任何激进的参数校准<br>- 1，可能进行一些静态量化参数校准<br>- 2+，将根据逐块量化的损失情况进行量化参数校准 |
| precision_level<br> | 0 | 0、1、2、3、4<br> | - 0，为全int8量化，即使调优也限制在int8<br>- 1-2，只将部分算子量化为int8，可适用于一般Transformer模型<br>- 3，动态量化<br>- 4，FP16 |
| max_percentile | 0.9999 |  | percentile量化时的截断范围，限制最小值为0.99 |
| custom_setting | None |  |  |
| truncate_var_names | [] |  | 只支持依据截断Tensor名，将计算图二分，并且将检查二分结果，否则报错 |

- 校准数据列表文件的规则

img_list.txt每行表示一个校准数据文件路径，可以写相对于img_list.txt 所在目录的相对路径，也可以写绝对路径，如果模型是多输入的，请确保每个文件列表的顺序是对应的。
~~~
QuantZoo/Data/Imagenet/Calib/n01440764/ILSVRC2012_val_00002138.JPEG
QuantZoo/Data/Imagenet/Calib/n01443537/ILSVRC2012_val_00000994.JPEG
QuantZoo/Data/Imagenet/Calib/n01484850/ILSVRC2012_val_00014467.JPEG
QuantZoo/Data/Imagenet/Calib/n01491361/ILSVRC2012_val_00003204.JPEG
QuantZoo/Data/Imagenet/Calib/n01494475/ILSVRC2012_val_00015545.JPEG
QuantZoo/Data/Imagenet/Calib/n01496331/ILSVRC2012_val_00008640.JPEG
~~~

- preprocess_file的规则

例如这是一个custom_preprocess.py脚本文件，则在配置文件中将preprocess_file设为custom_preprocess.py:preprocess_impl 指向具体py文件的具体方法，如果是多输入的情况，code差距不大的情况下，可以直接复用自己的预处理方法。
~~~ python
from typing import Sequence
import torch
import cv2
import numpy as np

def preprocess_impl(path_list: Sequence[str], input_parametr: dict) -> torch.Tensor:
    """
    读取path_list, 并依据input_parametr中的参数预处理, 返回一个torch.Tensor

    Args:
        path_list (Sequence[str]): 一个校准batch的文件列表
        input_parametr (dict): 等同于配置中的calibration_parameters.input_parameters[idx]

    Returns:
        torch.Tensor: 一个batch的校准数据
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
~~~

## 量化精度调优
详情参考[github-xslim-accuracy-tuning](https://github.com/spacemit-com/xslim/blob/main/doc/accuracy_tuning_zh.md)

## ChangeLog
详情参考[github-xslim-releases](https://github.com/spacemit-com/xslim/releases)
