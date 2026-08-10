sidebar_position: 2

# 4.2 Matrix 扩展指令集

- [4.2.1 指令集介绍](#421-指令集介绍)
- [4.2.2 进迭时空指令集](#422-进迭时空指令集)
- [4.2.3 简单使用](#423-简单使用)

## 4.2.1 指令集介绍

matirx扩展指令主要用于AI中最重要的计算，矩阵乘法。矩阵乘法的一般形式为：

C+ = A x B

其中，C为输出矩阵，A和B为输入矩阵。根据输入输出矩阵使用的寄存器不同，***RISC-V***社区把matirx扩展指令分为三个方案 ，如下图所示：![三个指令集对比](./images/matrix_inst.jpg)

- IME方案，矩阵计算的输入、输出矩阵都使用vector寄存器，详情可以加入[IME subgroup](https://lists.riscv.org/g/tech-integrated-matrix-extension)查看。
- VME方案，矩阵计算的输入矩阵复用vector寄存器，输出矩阵使用专用扩展寄存器，详情可以加入[VME subgroup](https://lists.riscv.org/g/tech-vme)查看。
- AME方案，矩阵计算的输入、输出矩阵都使用个专用寄存器，详情可以加入[AME subgroup](https://lists.riscv.org/g/tech-attached-matrix-extension)查看。

## 4.2.2 进迭时空指令集

进迭时空自定义的matirx扩展指令集，是IME的，[详情可见](./ime_extension.md)。可以看到，K1（vlen=256）中的matrix计算单元形状是：

4 x 8 x 4

则单个matrix计算单元的算力为：

2 x 4 x 8 x 4 x 2Ghz = 0.5TOPS

## 4.2.3 简单使用

进迭时空基于IME标准的扩展指令集，基本延续了vector标准指令集的编程模型。标准vector的使用[可参考]()。
IME指令集的使用[可参考](https://github.com/spacemit-com/riscv-ime-extension-spec/tree/master/example)
