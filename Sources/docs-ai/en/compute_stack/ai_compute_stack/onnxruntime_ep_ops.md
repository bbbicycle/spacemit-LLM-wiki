---
sidebar_position: 2
---

# SpaceMITExecutionProvider Accelerated Operators

> - This page lists the operators accelerated by `SpaceMITExecutionProvider` and the constraints applied during the capability-check phase.
> - [ONNX operator reference](https://onnx.ai/onnx/operators/index.html)
> - [ONNX contrib operator reference](https://github.com/microsoft/onnxruntime/blob/main/docs/ContribOperators.md)

- [SpaceMITExecutionProvider Accelerated Operators](#spacemitexecutionprovider-accelerated-operators)
  - [Dense](#dense)
    - [Conv](#conv)
    - [ConvTranspose](#convtranspose)
    - [Gemm](#gemm)
    - [MatMul](#matmul)
  - [QDQ](#qdq)
    - [DynamicQuantizeMatMul](#dynamicquantizematmul)
    - [MatMulInteger](#matmulinteger)
    - [DynamicQuantizeLinear](#dynamicquantizelinear)
    - [QuantizeLinear](#quantizelinear)
    - [DequantizeLinear](#dequantizelinear)
  - [Pool](#pool)
    - [AveragePool](#averagepool)
    - [GlobalAveragePool](#globalaveragepool)
    - [MaxPool](#maxpool)
    - [GlobalMaxPool](#globalmaxpool)
  - [Reduce](#reduce)
    - [ReduceMean](#reducemean)
    - [ReduceMax](#reducemax)
  - [Math](#math)
    - [Add](#add)
    - [Sub](#sub)
    - [Mul](#mul)
    - [Div](#div)
    - [Pow](#pow)
    - [Sqrt](#sqrt)
    - [Abs](#abs)
    - [Log](#log)
    - [Reciprocal](#reciprocal)
    - [Sin](#sin)
    - [Cos](#cos)
    - [Tan](#tan)
    - [Sinh](#sinh)
    - [Cosh](#cosh)
    - [Floor](#floor)
    - [Ceil](#ceil)
  - [Activation](#activation)
    - [Sigmoid](#sigmoid)
    - [Swish](#swish)
    - [HardSigmoid](#hardsigmoid)
    - [HardSwish](#hardswish)
    - [Tanh](#tanh)
    - [LeakyRelu](#leakyrelu)
    - [Clip](#clip)
    - [Relu](#relu)
    - [Elu](#elu)
    - [Gelu](#gelu)
    - [Celu](#celu)
    - [Softplus](#softplus)
    - [Softsign](#softsign)
    - [Erf](#erf)
    - [Softmax](#softmax)
  - [Tensor](#tensor)
    - [Cast](#cast)
    - [Concat](#concat)
    - [Split](#split)
    - [Transpose](#transpose)
    - [Unsqueeze](#unsqueeze)
    - [Squeeze](#squeeze)
    - [Reshape](#reshape)
    - [Flatten](#flatten)
    - [Gather](#gather)
    - [Slice](#slice)
    - [Resize](#resize)
    - [Where](#where)
  - [Norm](#norm)
    - [LayerNormalization](#layernormalization)
    - [InstanceNormalization](#instancenormalization)
    - [BatchNormalization](#batchnormalization)
  - [Compare](#compare)
    - [Equal](#equal)
    - [Greater](#greater)
    - [GreaterOrEqual](#greaterorequal)
    - [Less](#less)
    - [LessOrEqual](#lessorequal)

## Dense
### Conv
> - Domain: ai.onnx
> - Opset: 11
> - Attributes: `kernel_shape` must be present; `W` must be a constant initializer or provided by a `DequantizeLinear` node with no upstream input edges
> - Type - T: `tensor(float)` | `tensor(float16)`
> - Notes: `kernel_shape` rank must not exceed 3; supports 1D, 2D, and 3D convolutions

### ConvTranspose
> - Domain: ai.onnx
> - Opset: 11
> - Attributes: `kernel_shape` must be present; `W` must be a constant initializer or provided by a `DequantizeLinear` node with no upstream input edges
> - Type - T: `tensor(float)`
> - Notes: `kernel_shape` rank must not exceed 2; supports 1D and 2D

### Gemm
> - Domain: ai.onnx
> - Opset: 13
> - Attributes: `transA == 0`, `alpha == 1.0`, `beta == 1.0`
> - Type - T: `tensor(float)` | `tensor(float16)`
> - Notes: Supports QDQ quantization format. A is asymmetric per-tensor; B is symmetric per-channel. When B is non-constant, B must be asymmetric per-tensor.

### MatMul
> - Domain: ai.onnx
> - Opset: 13
> - Attributes: No additional attribute constraints
> - Type - T: `tensor(float)` | `tensor(float16)`
> - Notes: Supports QDQ quantization format. A is asymmetric per-tensor; B is symmetric per-channel. When B is non-constant, B must be asymmetric per-tensor.

## QDQ
### DynamicQuantizeMatMul
> - Domain: com.microsoft
> - Opset: 1 (see ONNX contrib operators)
> - Attributes: None
> - Type - T1: `tensor(float)`
> - Type - T2: `tensor(float)`

### MatMulInteger
> - Domain: ai.onnx
> - Opset: 10
> - Attributes: None
> - Type - T1: `tensor(int8)` | `tensor(uint8)`
> - Type - T2: `tensor(int32)`

### DynamicQuantizeLinear
> - Domain: ai.onnx
> - Opset: 11
> - Attributes: None
> - Type - T1: `tensor(float)`
> - Type - T2: `tensor(int8)` | `tensor(uint8)`

### QuantizeLinear
> - Domain: ai.onnx
> - Opset: 19
> - Attributes: None
> - Type - T1: `tensor(float)`
> - Type - T2: `tensor(int8)` | `tensor(uint8)`

### DequantizeLinear
> - Domain: ai.onnx
> - Opset: 19
> - Attributes: None
> - Type - T1: `tensor(int8)` | `tensor(uint8)` | `tensor(int32)`
> - Type - T2: `tensor(float)`

## Pool
### AveragePool
> - Domain: ai.onnx
> - Opset: 22
> - Attributes: If `count_include_pad != 1`, all `pads` values must be 0; if `kernel_shape` is present, its rank must not exceed 2
> - Type - T: `tensor(float)` | `tensor(float16)`

### GlobalAveragePool
> - Domain: ai.onnx
> - Opset: 1
> - Attributes: If `kernel_shape` is present, its rank must not exceed 2
> - Type - T: `tensor(float)` | `tensor(float16)`

### MaxPool
> - Domain: ai.onnx
> - Opset: 12
> - Attributes: If `kernel_shape` is present, its rank must not exceed 2
> - Type - T: `tensor(float)` | `tensor(float16)`

### GlobalMaxPool
> - Domain: ai.onnx
> - Opset: 1
> - Attributes: If `kernel_shape` is present, its rank must not exceed 2
> - Type - T: `tensor(float)` | `tensor(float16)`

## Reduce
### ReduceMean
> - Domain: ai.onnx
> - Opset: 18
> - Attributes: All inputs beyond the first must be constant initializers
> - Type - T: `tensor(float)` | `tensor(float16)`

### ReduceMax
> - Domain: ai.onnx
> - Opset: 20
> - Attributes: All inputs beyond the first must be constant initializers
> - Type - T: `tensor(float)` | `tensor(float16)`

## Math
### Add
> - Domain: ai.onnx
> - Opset: 14
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Sub
> - Domain: ai.onnx
> - Opset: 14
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Mul
> - Domain: ai.onnx
> - Opset: 14
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Div
> - Domain: ai.onnx
> - Opset: 14
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Pow
> - Domain: ai.onnx
> - Opset: 14
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Sqrt
> - Domain: ai.onnx
> - Opset: 14
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Abs
> - Domain: ai.onnx
> - Opset: 14
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Log
> - Domain: ai.onnx
> - Opset: 13
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Reciprocal
> - Domain: ai.onnx
> - Opset: 14
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Sin
> - Domain: ai.onnx
> - Opset: 7
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Cos
> - Domain: ai.onnx
> - Opset: 7
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Tan
> - Domain: ai.onnx
> - Opset: 7
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Sinh
> - Domain: ai.onnx
> - Opset: 9
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Cosh
> - Domain: ai.onnx
> - Opset: 9
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Floor
> - Domain: ai.onnx
> - Opset: 6
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Ceil
> - Domain: ai.onnx
> - Opset: 6
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

## Activation
### Sigmoid
> - Domain: ai.onnx
> - Opset: 13
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Swish
> - Domain: ai.onnx
> - Opset: 24
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### HardSigmoid
> - Domain: ai.onnx
> - Opset: 22
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### HardSwish
> - Domain: ai.onnx
> - Opset: 22
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Tanh
> - Domain: ai.onnx
> - Opset: 13
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### LeakyRelu
> - Domain: ai.onnx
> - Opset: 16
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Clip
> - Domain: ai.onnx
> - Opset: 13
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Relu
> - Domain: ai.onnx
> - Opset: 14
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Elu
> - Domain: ai.onnx
> - Opset: 22
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Gelu
> - Domain: ai.onnx
> - Opset: 20
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Celu
> - Domain: ai.onnx
> - Opset: 12
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Softplus
> - Domain: ai.onnx
> - Opset: 1
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Softsign
> - Domain: ai.onnx
> - Opset: 1
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Erf
> - Domain: ai.onnx
> - Opset: 13
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### Softmax
> - Domain: ai.onnx
> - Opset: 13
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

## Tensor
### Cast
> - Domain: ai.onnx
> - Opset: 24
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)` | `tensor(int32)` | `tensor(uint32)` | `tensor(int8)` | `tensor(uint8)` | `tensor(bool)`

### Concat
> - Domain: ai.onnx
> - Opset: 13
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)` | `tensor(int32)` | `tensor(uint32)` | `tensor(int8)` | `tensor(uint8)` | `tensor(bool)`

### Split
> - Domain: ai.onnx
> - Opset: 18
> - Attributes: All inputs beyond the first must be constant initializers
> - Type - T: `tensor(float)` | `tensor(float16)` | `tensor(int32)` | `tensor(uint32)` | `tensor(int8)` | `tensor(uint8)` | `tensor(bool)`

### Transpose
> - Domain: ai.onnx
> - Opset: 24
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)` | `tensor(int8)`

### Unsqueeze
> - Domain: ai.onnx
> - Opset: 24
> - Attributes: The `axes` input must be a constant initializer
> - Type - T: `tensor(float)` | `tensor(float16)` | `tensor(int32)` | `tensor(uint32)` | `tensor(int8)` | `tensor(uint8)` | `tensor(bool)`

### Squeeze
> - Domain: ai.onnx
> - Opset: 24
> - Attributes: The `axes` input must be a constant initializer
> - Type - T: `tensor(float)` | `tensor(float16)` | `tensor(int32)` | `tensor(uint32)` | `tensor(int8)` | `tensor(uint8)` | `tensor(bool)`

### Reshape
> - Domain: ai.onnx
> - Opset: 24
> - Attributes: The `shape` input must be a constant initializer
> - Type - T: `tensor(float)` | `tensor(float16)` | `tensor(int32)` | `tensor(uint32)` | `tensor(int8)` | `tensor(uint8)` | `tensor(bool)`

### Flatten
> - Domain: ai.onnx
> - Opset: 24
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)` | `tensor(int32)` | `tensor(uint32)` | `tensor(int8)` | `tensor(uint8)` | `tensor(bool)`

### Gather
> - Domain: ai.onnx
> - Opset: 13
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)` | `tensor(int32)` | `tensor(uint32)` | `tensor(int8)` | `tensor(uint8)` | `tensor(bool)`

### Slice
> - Domain: ai.onnx
> - Opset: 13
> - Attributes: All inputs beyond the first must be constant initializers; only opset >= 10 is supported
> - Type - T: `tensor(float)` | `tensor(float16)` | `tensor(int32)` | `tensor(uint32)` | `tensor(int8)` | `tensor(uint8)` | `tensor(bool)`

### Resize
> - Domain: ai.onnx
> - Opset: 19
> - Attributes: `coordinate_transformation_mode` supports `asymmetric` and `half_pixel` only; `mode` supports `nearest` and `linear` only
> - Type - T: `tensor(float)` | `tensor(float16)` | `tensor(int8)`

### Where
> - Domain: ai.onnx
> - Opset: 9
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)` | `tensor(int32)` | `tensor(uint32)` | `tensor(int8)` | `tensor(uint8)` | `tensor(bool)`

## Norm
### LayerNormalization
> - Domain: ai.onnx
> - Opset: 17
> - Attributes: No additional constant constraints during the capability-check phase
> - Type - T: `tensor(float)` | `tensor(float16)`

### InstanceNormalization
> - Domain: ai.onnx
> - Opset: 6
> - Attributes: None
> - Type - T: `tensor(float)` | `tensor(float16)`

### BatchNormalization
> - Domain: ai.onnx
> - Opset: 15
> - Attributes: No additional constant constraints during the capability-check phase
> - Type - T: `tensor(float)` | `tensor(float16)`

## Compare
### Equal
> - Domain: ai.onnx
> - Opset: 11
> - Attributes: None
> - Type - T1: `tensor(float)` | `tensor(float16)` | `tensor(int32)` | `tensor(uint32)` | `tensor(int8)` | `tensor(uint8)` | `tensor(bool)`
> - Type - T2: `tensor(uint8)` | `tensor(bool)`

### Greater
> - Domain: ai.onnx
> - Opset: 9
> - Attributes: None
> - Type - T1: `tensor(float)` | `tensor(float16)` | `tensor(int32)` | `tensor(uint32)` | `tensor(int8)` | `tensor(uint8)` | `tensor(bool)`
> - Type - T2: `tensor(uint8)` | `tensor(bool)`

### GreaterOrEqual
> - Domain: ai.onnx
> - Opset: 12
> - Attributes: None
> - Type - T1: `tensor(float)` | `tensor(float16)` | `tensor(int32)` | `tensor(uint32)` | `tensor(int8)` | `tensor(uint8)` | `tensor(bool)`
> - Type - T2: `tensor(uint8)` | `tensor(bool)`

### Less
> - Domain: ai.onnx
> - Opset: 9
> - Attributes: None
> - Type - T1: `tensor(float)` | `tensor(float16)` | `tensor(int32)` | `tensor(uint32)` | `tensor(int8)` | `tensor(uint8)` | `tensor(bool)`
> - Type - T2: `tensor(uint8)` | `tensor(bool)`

### LessOrEqual
> - Domain: ai.onnx
> - Opset: 12
> - Attributes: None
> - Type - T1: `tensor(float)` | `tensor(float16)` | `tensor(int32)` | `tensor(uint32)` | `tensor(int8)` | `tensor(uint8)` | `tensor(bool)`
> - Type - T2: `tensor(uint8)` | `tensor(bool)`
