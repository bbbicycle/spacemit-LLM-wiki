sidebar_position: 3

# SpacemiT AI 矩阵扩展指令集

**`Zvvm_spacemit` Profile**

版本：0.6
状态：对外发布版  
更新日期：2026 年 4 月 13 日

## 目录

- 第 1 章 概述
- 第 2 章 SpacemiT 矩阵扩展编程模型
- 第 3 章 SpacemiT 矩阵扩展编程模型与社区 `Zvvm`、`Zvzip` 的差异
- 第 4 章 指令全景、子扩展与快速索引
- 第 5 章 整数矩阵乘法指令
- 第 6 章 浮点矩阵乘法指令
- 第 7 章 数据布局变换指令
- 第 8 章 主要指令编码摘要
- 附录 A. tile 与子扩展速查表

# 第 1 章 概述

## 1.1 设计特点

矩阵乘法是机器学习与人工智能应用中的典型负载。传统矩阵乘法加速器为了获得更高的数据吞吐，通常会引入独立的矩阵寄存器文件来保存累加结果，但这也会同步带来额外的架构状态、上下文切换与软件栈复杂度。

`Zvvm` / IME 矩阵扩展采用另一种设计思路：复用 RISC-V `V` 扩展中的 32 个向量寄存器，将原本的一维向量排布解释为二维矩阵 tile（矩阵分块）排布，从而在不引入新寄存器文件的前提下提升矩阵计算密度。基于这一思路，进迭时空开发了 SpacemiT AI 矩阵扩展指令集，并已在两代算力芯片中落地实现。

Spacemit AI 矩阵扩展指令集可在不同 `VLEN` 配置的RISC-V处理器上保持良好的兼容性，并实现较高的算力利用率。该扩展以 RISC-V Vector 编程模型为基础，复用向量寄存器文件与控制语义，在提供矩阵计算能力的同时尽量减少对既有 RVV 软件栈的扰动，主要具有以下特点：

- 复用现有向量寄存器文件承载二维矩阵 tile；
- 在不引入独立矩阵寄存器文件的前提下提供矩阵乘法算力；
- 直接支持 Int4、Int8、FP16、BF16 等常见 AI 数据类型；
- 针对卷积、稀疏矩阵和分块量化场景提供专用矩阵乘法指令；
- 提供用于调整向量寄存器数据排布的数据布局变换指令；
- 与社区持续演进中的 IME / `Zvvm` / `Zvzip` 扩展在设计理念上相互呼应、协同演进。

## 1.2 指令集提供的能力

Spacemit AI 矩阵扩展中的指令可归纳为 7 类：

1. 整数矩阵乘法指令；
2. 浮点矩阵乘法指令；
3. 面向卷积场景的整数滑窗矩阵乘法；
4. 面向卷积场景的浮点滑窗矩阵乘法；
5. 面向分块量化的整数矩阵乘法指令；
6. 4:2 结构化稀疏整数矩阵乘法；
7. 数据布局变换指令。

若将源操作数的 `signedness` 变体以及适配不同卷积尺寸的指令变体一并计入，本指令集共覆盖 **46 条面向 AI 计算的自定义指令**。

## 1.3 本文推荐的阅读顺序

对首次接触 SpacemiT 矩阵扩展指令的读者，建议按以下顺序阅读：

1. 第 2 章：先理解寄存器约束、`LMUL` 支持范围和全局控制位；
2. 第 4 章：建立“有哪些主要子扩展与指令类型”的整体印象；
3. 第 5～7 章：按类别阅读具体语义；
4. 第 8 章：最后再看主要指令编码摘要，结合前文语义建立“语义—编码”对应关系。

## 1.4 统一的矩阵语义记号

SpacemiT AI 矩阵扩展的典型运算场景为：
$$
C \leftarrow C + A \times B^T
$$

以一条整型矩阵乘法指令 `smt.vmadot vd, vs1, vs2, i8` 为例：

- `Vs1` 存放 `A` tile 的数据；
- `Vs2` 存放 `B^T` tile 的数据；
- `Vd` 存放累加初值和乘累加的结果；
- `i8` 表示矩阵运算的源操作数数据类型。

其中，`B^T` 表示**矩阵元素的几何排布**相对于数学排布的关系，并不要求软件显式地对 `B` 矩阵执行转置。

## 1.5 矩阵分块的几何布局

乘法器与矩阵分块的几何关系由以下参数共同决定：一个用于描述 tile 几何的参数 `lambda`（λ），以及向量参数 `SEW`、`VLEN`。

对乘累加操作 $C \leftarrow A \times B^T + C$，输入数据 `A`、`B` 与输出数据 `C` 均存放于 RISC-V 向量寄存器文件中。三个矩阵的存储布局见图 1。

* _累加矩阵_ `C` 存放在一个元素宽度为 `SEW` 的向量寄存器组中。
    其寄存器组倍数 `MUL_C` 由 tile 几何决定：
    `MUL_C = (VLEN / SEW) / λ^2`。在现有实现中，`λ` 为与对应指令类型相关的固定值，可通过查阅本文档获得。
    `C` 寄存器组可以从任意满足 `MUL_C` 对齐的向量寄存器编号开始。`MUL_C ∈ {1, 2, 4, 8, 16}`。
    当 `MUL_C = 16` 时，仅允许从寄存器编号 `0` 或 `16` 开始。

* _输入矩阵_ `A` 和 `B` 存放在单个向量寄存器中，其元素位宽由指令决定，并直接编码在指令中。在当前的 SpacemiT AI 矩阵扩展实现中，仅支持 `LMUL = 1`，其余 `LMUL` 编码均为保留值；在任意 IME 指令中使用非 1 的 `LMUL` 值，应触发非法指令异常。
    * **注**：在社区 `Zvvm` 扩展中，还存在两个参数 `LMUL` 和 `W`。其中，`LMUL` 表示输入 tile 的寄存器组倍数，`W` 规定指令输出数据类型与输入数据类型的位宽比值。在未来的实现中，`λ` 可以通过 `vtype` 中的 `lambda[2:0]` 字段解码获得，`W` 与 `LMUL` 也会以更统一的方式纳入编程模型；但在当前实现（A60、A100）中，`LMUL` 仅支持 1，`W` 以具体指令的功能约束为准。

![图1：矩阵 tile 几何与参数关系示意图。](images/ime_extension_png/fig0vlen256.png)
*图 1. 在 32 元素向量寄存器、λ=2、W=4、VLEN=256、LMUL=1 条件下的矩阵 tile 几何与元素顺序。向量寄存器按二维 tile 解释，元素下标展示 tile 内元素排序。*


乘法的 K 维（即 A 与 $B^T$ 的共享累加维度）由 λ 决定，再由指令扩位因子 `W` 与 `LMUL` 共同缩放：

    K_eff = λ × W × LMUL

A 与 B tile 的元素宽度为 `SEW ÷ W`；累加矩阵 `C` 的元素宽度为 `SEW`（见下表 1）。
每个输入的有符号/无符号解释直接编码在指令中（`s` 表示有符号，`u` 表示无符号，见下表 2）；累加矩阵 `C` 始终按有符号解释。

tile 维度由扩位设置与 `LMUL` 推导：

    L_A    = LMUL × VLEN ÷ (SEW ÷ W)   （A 或 B 在 LMUL 寄存器组中的总元素数）
    K_eff  = λ × W × LMUL
    M = N  = L_A ÷ K_eff               （方形累加 tile 中行数=列数）

累加寄存器组的基数为 `MUL_C = VLEN ÷ (SEW × λ²)`，与 `W` 和 `LMUL` 均无关。

由图 1 可见，向量寄存器中的元素在 λ 方向上连续。tile `A` 与 tile `C` 按行优先（row-major）排序，而 tile `B` 按列优先（column-major）排序。

![图2：LMUL 缩放下的矩阵 tile 排布关系。](images/ime_extension_png/fig1ime-tile-lmul_2_4.png)
*图 2. 矩阵 tile 在 LMUL=2（左）与 LMUL=4（右）时的元素排布关系。蓝色箭头表示按一维向量顺序访问时，同属一个 tile 的连续元素。*

LMUL 仅沿 K 维缩放 tile，使 tile 的有效 K 维按 LMUL 倍数增长。图中的蓝色箭头表示：在按一维向量元素顺序访问时，哪些连续元素共同构成对应的 tile。

## 1.6 SpacemiT AI 指令集的子扩展

下表给出 SpacemiT AI 矩阵扩展各子扩展与社区 `Zvvm` 命名的对照关系：

| SpacemiT AI 子扩展 | 社区 `Zvvm` 子扩展 | 依赖 | 乘数类型 | scale 类型 | 累加类型 |
|---|---|---|---|---|---|
|Xsmti4i32mm|Zvvi4i8mm| Zve32x | [U]Int4, [U]Int4 | — | Int32 |
|Xsmti8i32mm|Zvvi8i32mm| Zve32x | [U]Int8, [U]Int8 | — | Int32 |
|Xsmti8i32mm_slide|—| Zve32x | [U]Int8, [U]Int8 | — | Int32 |
|Xsmti4i32mm_42sp|—| Zve32x | [U]Int4, [U]Int4 | — | Int32 |
|Xsmti8i32mm_42sp|—| Zve32x | [U]Int8, [U]Int8 | — | Int32 |
|Xsmti4fp16mm_scl16f|—| Zve32f | [U]Int4, [U]Int4 | IEEE binary16 / BFloat16 | IEEE binary16 |
|Xsmti4bf16mm_scl16f|—| Zve32f | [U]Int4, [U]Int4 | IEEE binary16 / BFloat16 | BFloat16 |
|Xsmti8fp16mm_scl16f|—| Zve32f | [U]Int8, [U]Int8 | IEEE binary16 / BFloat16 | IEEE binary16 |
|Xsmti8bf16mm_scl16f|—| Zve32f | [U]Int8, [U]Int8 | IEEE binary16 / BFloat16 | BFloat16 |
|Xsmtfp16fp32mm|Zvvfp16fp32mm| Zve32f | IEEE binary16, IEEE binary16 | — | IEEE binary32 |
|Xsmtbf16fp32mm|Zvvbf16fp32mm| Zve32f | BFloat16, BFloat16 | — | IEEE binary32 |
|Xsmtfp16fp32mm_slide|—| Zve32f | IEEE binary16, IEEE binary16 | — | IEEE binary32 |
|Xsmtbf16fp32mm_slide|—| Zve32f | BFloat16, BFloat16 | — | IEEE binary32 |

## 1.7 K 系列芯片对子扩展的支持情况

K1 芯片中的 A60 核支持的子扩展包括 `Xsmti8i32mm` 和 `Xsmti8i32mm_slide`。

K3 芯片中的 A100 核支持的子扩展包括 `Xsmti4i32mm`、`Xsmti8i32mm`、`Xsmti8i32mm_slide`、`Xsmti4i32mm_42sp`、`Xsmti8i32mm_42sp`、`Xsmti4fp16mm_scl16f`、`Xsmti4bf16mm_scl16f`、`Xsmti8fp16mm_scl16f`、`Xsmti8bf16mm_scl16f`、`Xsmtfp16fp32mm`、`Xsmtbf16fp32mm`、`Xsmtfp16fp32mm_slide` 和 `Xsmtbf16fp32mm_slide`。

| SpacemiT AI 子扩展 | A60 支持情况 | A100 支持情况 |
|---|---|---|
|Xsmti4i32mm| — | √ |
|Xsmti8i32mm| √ | √ |
|Xsmti8i32mm_slide| √ | √ |
|Xsmti4i32mm_42sp| — | √ |
|Xsmti8i32mm_42sp| — | √ |
|Xsmti4fp16mm_scl16f| — | √ |
|Xsmti4bf16mm_scl16f| — | √ |
|Xsmti8fp16mm_scl16f| — | √ |
|Xsmti8bf16mm_scl16f| — | √ |
|Xsmtfp16fp32mm| — | √ |
|Xsmtbf16fp32mm| — | √ |
|Xsmtfp16fp32mm_slide| — | √ |
|Xsmtbf16fp32mm_slide| — | √ |


# 第 2 章 SpacemiT 矩阵扩展编程模型

## 2.1 实现参数

本文档范围内的 SpacemiT 矩阵扩展 `Profile` 采用如下实现参数：`VLEN`、`lambda` 与 `MUL_C`。

各参数的具体含义为：

- `VLEN`：实现固定的向量寄存器位宽；
- `lambda`：实现固定的 tile 几何参数（在 A60 和 A100 中不通过 `vtype` 动态配置）；
- `MUL_C`：目标 `C` tile 占用的向量寄存器数量。

### 2.1.1 A60 采用的实现参数

下表给出了 `Xsmti8i32mm` 与 `Xsmti8i32mm_slide` 的实现参数。
|参数|取值|说明|
|---|---|---|
|`VLEN`|256 bit|固定实现参数|
|`lambda`|2|固定实现参数，不由 `vtype` 动态配置|
|`MUL_C`|2|目标 tile 占用 `Vd` 与 `Vd+1` 两个向量寄存器|
|`SEW`|32 bit|累加结果的数据位宽按 32 位解释|

由此可得：
$$
MUL\_C = \frac{VLEN}{SEW \times \lambda^2} = \frac{256}{32 \times 4} = 2
$$

### 2.1.2 A100 采用的实现参数

下表给出了 `Xsmti4i32mm`、`Xsmti8i32mm`、`Xsmti8i32mm_slide`、`Xsmti4i32mm_42sp`、`Xsmti8i32mm_42sp`、`Xsmtfp16fp32mm`、`Xsmtbf16fp32mm`、`Xsmtfp16fp32mm_slide` 和 `Xsmtbf16fp32mm_slide` 的实现参数。
|参数|取值|说明|
|---|---|---|
|`VLEN`|1024 bit|固定实现参数|
|`lambda`|4|固定实现参数，不由 `vtype` 动态配置|
|`MUL_C`|2|目标 tile 占用 `Vd` 与 `Vd+1` 两个向量寄存器|
|`SEW`|32 bit|累加结果的数据位宽按 32 位解释|

由此可得：
$$
MUL\_C = \frac{VLEN}{SEW \times \lambda^2} = \frac{1024}{32 \times 16} = 2
$$

下表给出了 `Xsmti4fp16mm_scl16f`、`Xsmti4bf16mm_scl16f`、`Xsmti8fp16mm_scl16f` 和 `Xsmti8bf16mm_scl16f` 的实现参数。

|参数|取值|说明|
|---|---|---|
|`VLEN`|1024 bit|固定实现参数|
|`lambda`|8|固定实现参数，不由 `vtype` 动态配置|
|`MUL_C`|1|目标 tile 占用 `Vd` 一个向量寄存器|
|`SEW`|16 bit|累加结果的数据位宽按 16 位解释|

由此可得：
$$
MUL\_C = \frac{VLEN}{SEW \times \lambda^2} = \frac{1024}{16 \times 64} = 1
$$

## 2.2 操作数角色

除非指令另有说明，本指令集使用以下操作数角色：

- `Vd`：目标寄存器组，既提供累加初值，也接收结果；
- `Vs1`：源矩阵 `A`；
- `Vs2`：源矩阵 `B` 的硬件友好布局；
- `V0` / `V1`：仅在部分专有路径中作为稀疏指令的恢复掩码或 scale 参数寄存器使用；
- `MCPM`：控制 16 位浮点数具体格式为 FP16 / BF16 的实现专有控制位。

## 2.3 共同寄存器约束

除第 7 章的数据布局变换指令外，当 `MUL_C = 2` 时，矩阵计算指令满足以下共同约束：

- `Vd` **必须** 为偶数编号向量寄存器；
- `Vd` 与 `Vd+1` 共同构成目标寄存器组；
- `Vd/Vd+1` **不可** 与 `Vs1` 或 `Vs2` 重叠；
- 目标寄存器组的结果布局由指令类型决定；
- 本指令集不将普通 RVV `vm` 掩码位作为矩阵乘法的 mask 控制。

当 `MUL_C = 1` 时，矩阵计算指令满足以下约束：

- `Vd` 可以为任意编号向量寄存器；
- `Vd` **不可** 与 `Vs1` 或 `Vs2` 重叠；
- 目标寄存器组的结果布局由指令类型决定；
- 本指令集不将普通 RVV `vm` 掩码位作为矩阵乘法的 mask 控制。

附加约束：

- 滑窗类指令要求 `Vs1` 为偶数编号寄存器；
- 稀疏类与含 scale 类指令额外使用 `V0` / `V1`；
- 浮点类与含 scale 类指令的浮点格式受 `MCPM.BF16` 控制。

## 2.4 `MUL_C` 与目标寄存器组

`MUL_C` 表示目标矩阵 tile `C` 在向量寄存器文件中占用的寄存器组大小。

在本文涉及的实现中，主要存在两类情况：

- `MUL_C = 2`：目标结果占用 `Vd` 与 `Vd+1` 两个向量寄存器；
- `MUL_C = 1`：目标结果仅占用单个向量寄存器 `Vd`。

对软件而言，`MUL_C` 直接影响：

- 目标寄存器组是否必须按偶数寄存器对齐；
- 结果写回时可见的 tile 几何；
- 目标寄存器与源寄存器之间的重叠合法性约束。

除非具体指令另有说明，软件应始终结合对应指令类型的固定 `Profile` 参数来理解 `MUL_C`，而不应将其视为当前实现中的动态可配置参数。

## 2.5 tile 形状总览

在 A60（`VLEN = 256`）的实现中，各主要子扩展的 tile 形状如下：
|子扩展|输入类型|目标类型|tile 形状 `M × K × N`|
|---|---|---|---|
|`Xsmti8i32mm`：整数矩阵乘法指令|Int8|Int32|`4 × 8 × 4`|
|`Xsmti8i32mm_slide`：面向卷积场景的整数滑窗矩阵乘法|Int8|Int32|`4 × 8 × 4`|

在 A100（`VLEN = 1024`）的实现中，各主要子扩展的 tile 形状如下：

|子扩展|输入类型|目标类型|tile 形状 `M × K × N`|
|---|---|---|---|
|`Xsmti4i32mm`：整数矩阵乘法指令|[U]Int4|Int32|`8 × 32 × 8`|
|`Xsmti8i32mm`：整数矩阵乘法指令|[U]Int8|Int32|`8 × 16 × 8`|
|`Xsmti8i32mm_slide`：面向卷积场景的整数滑窗矩阵乘法|[U]Int8|Int32|`8 × 16 × 8`|
|`Xsmti4i32mm_42sp`：4:2 结构化稀疏整数矩阵乘法|[U]Int4|Int32|`8 × 64 × 8`|
|`Xsmti8i32mm_42sp`：4:2 结构化稀疏整数矩阵乘法|[U]Int8|Int32|`8 × 32 × 8`|
|`Xsmti8*16mm_scl16f`：面向分块量化的整数矩阵乘法指令|[U]Int8 + scale|FP16 / BF16|`8 × 16 × 8`|
|`Xsmti4*16mm_scl16f`：面向分块量化的整数矩阵乘法指令|[U]Int4 + scale|FP16 / BF16|`8 × 32 × 8`|
|`Xsmt*16fp32mm`：浮点矩阵乘法指令|FP16 / BF16|FP32|`8 × 8 × 8`|
|`Xsmt*16fp32mm_slide`：面向卷积场景的浮点滑窗矩阵乘法|FP16 / BF16|FP32|`8 × 8 × 8`|

## 2.6 全局控制与专用辅助操作数

### 2.6.1 `MCPM.BF16`

`MCPM.BF16` 为实现专有控制位，用于决定相关路径的浮点格式解释：

|控制位|含义|
|---|---|
|`MCPM.BF16 = 0`|按 FP16 解释相关浮点输入 / scale / 累加结果|
|`MCPM.BF16 = 1`|按 BF16 解释相关浮点输入 / scale / 累加结果|

作用范围：

- `smt.vfwmadot` / `smt.vfwmadot1/2/3`；
- `smt.vmadot.hp*` 的 scale 参数和累加结果格式。

### 2.6.2 `V0` / `V1`

`V0` / `V1` 在本指令集中不作为通用矩阵 mask 寄存器，而是用于以下专有路径：

|指令类型|`V0` / `V1` 的角色|
|---|---|
|`smt.vmadot.sp*`|存放 4:2 结构化稀疏恢复掩码|
|`smt.vmadot.hp*`|存放逐列或按组 scale 参数|

### 2.6.3 `imm2` 与 `imm3`

|字段|适用指令|立即数位宽|作用|
|---|---|---|---|
|`imm2`|`smt.vmadot.sp*`|2bit|选择掩码寄存器中的分段|
|`imm3`|`smt.vmadot.hp*`|3bit|选择 scale 参数寄存器中的分组|

补充说明：

- `smt.vmadot.sp*` 的 `imm2` 采用分裂编码，分别位于 `[15]` 与 `[7]`；这两位之所以可用于承载 `imm2`，是因为 `Vs1` 与 `Vd` 受偶数寄存器约束，其 `bit 0` 恒为 0，编码时仅需显式保留 `[4:1]`；
- `smt.vmadot.hp*` 的 `imm3` 直接占用独立的 `[14:12]` 字段，不依赖寄存器最低位省出的编码空间。

## 2.7 数据布局

### 2.7.1 字节及更宽元素

对 `EEW = 8` 或 `EEW = 16`，本指令集使用普通线性向量元素顺序：

$$
[k \times EEW + EEW - 1 : k \times EEW]
$$

适用范围包括：

- 输入数据类型为 Int8 的指令；
- 输入数据类型为 FP16 / BF16 的指令；
- 含 scale 的整数量化路径中的 FP16 / BF16 scale 参数。

### 2.7.2 4-bit 元素

对输入数据类型为 Int4 的指令，本指令集使用 packed nibble 存储：

- 元素 `2n` 位于字节 `n` 的 `[3:0]`；
- 元素 `2n+1` 位于字节 `n` 的 `[7:4]`。

可等价写作：

$$
[4k + 3 : 4k]
$$

### 2.7.3 tile 布局约定

对矩阵计算类指令：

- `A` tile 在 `Vs1` 中按行优先组织；
- `B` tile 在 `Vs2` 中按列优先组织；
- `C` tile 在 `Vd` 寄存器组中按实现固定方式保存。

`Vs1`、`Vs2`、`Vd` 的排布见图 3。tile `A` 与 tile `C` 按行优先（row-major）排序，而 tile `B` 按列优先（column-major）排序。

![图3：寄存器中的二维矩阵 tile 排布示意图。](images/ime_extension_png/fig2tilelayout.png)
*图 3. 在 VLEN=256、W=4、λ=2 条件下，`Vs1`、`Vs2` 与 `Vd` 的二维矩阵排布示意。*

# 第 3 章 SpacemiT 矩阵扩展编程模型与社区 `Zvvm`、`Zvzip` 的差异

由于社区 `Zvvm` 扩展提出较晚，进迭时空选择先行开发一套自定义 AI 指令集。当前，社区 `Zvvm` 扩展仍未稳定定稿；但从公开草稿来看，进迭时空的自定义 AI 扩展在编程模型等方面与社区 `Zvvm` 具有较高相似性。下文以表格形式整理两者的主要差异。

| 社区扩展名 | 类别 | 社区方案 | SpacemiT 矩阵扩展 |
|---|---|---|---|
|Zvvm|CSR|vtype.lambda|未在vtype中实现，概念上兼容|
|Zvvm|CSR|vtype.altfmt_A<br>vtype.altfmt_B|未在vtype中实现，相应功能被放在指令编码中|
|Zvvm|CSR|vtype.altfmt|未在vtype中实现，A100使用MCPM|
|Zvvm|data layout|A 和 C 行主序，B 列主序|A 和 C 行主序，B 列主序|
|Zvvm|指令|vmmacc|未支持|
|Zvvm|指令|vwmmacc|未支持|
|Zvvm|指令|vqwmmacc|smt.vmadot*,i8|
|Zvvm|指令|v8wmmacc|smt.vmadot*,i4|
|Zvvm|指令|vfmmacc|未支持|
|Zvvm|指令|vfwmmacc|smt.vfwmadot|
|Zvvm|指令|vfqwmmacc|未支持|
|Zvvm|指令|vf8wmmacc|未支持|
|Zvvm|指令|vfwimmacc|smt.vmadot.hp*, i8；scale 类型 FP16 / BF16|
|Zvvm|指令|vfqwimmacc;scale类型e4m3|smt.vmadot.hp*, i4；scale 类型 FP16 / BF16|
|Zvvm|指令|vf8wimmacc;scale类型e5m2|未支持|
|Zvvm|专用的 load/store 指令|Zvvmtls 指令扩展|未实现；可配合 `vpack` 指令实现近似功能|
|Zvvm|专用指令：卷积加速|未支持|提供专用滑窗卷积指令|
|Zvvm|专用指令：结构化稀疏|未支持|支持 4:2 稀疏|
|Zvzip|指令|vzip.vv|smt.vpack.vv，功能等效|
|Zvzip|指令|vunzipe.v|smt.vupack.vv，可实现等效功能|
|Zvzip|指令|vunzipo.v|smt.vupack.vv，可实现等效功能|
|Zvzip|指令|vpaire.vv|smt.vnpack.vv，可实现等效功能|
|Zvzip|指令|vpairo.vv|smt.vnpack.vv，结合 `vsrl.vv` 可实现等效功能|


# 第 4 章 指令全景、子扩展与快速索引

## 4.1 子扩展总表

|子扩展|指令数|代表指令|输入|输出 / 累加|特殊资源|
|---|---|---|---|---|---|
|`Xsmti*i32mm`：整数矩阵乘法指令|8|`smt.vmadot*`|Int4 / Int8|Int32|无|
|`Xsmti*i32mm_slide`：面向卷积场景的整数滑窗矩阵乘法|12|`smt.vmadot1*`, `smt.vmadot2*`, `smt.vmadot3*`|Int8|Int32|`Vs1` 偶数|
|`Xsmti*i32mm_42sp`：4:2 结构化稀疏整数矩阵乘法|8|`smt.vmadot.sp*`|Int4 / Int8|Int32|`V0` / `V1`, `imm2`|
|`Xsmti**16mm_scl16f`：面向分块量化的整数矩阵乘法指令|8|`smt.vmadot.hp*`|Int4 / Int8 + scale|FP16 / BF16|`V0` / `V1`, `imm3`, `MCPM.BF16`|
|`Xsmt*16fp32mm`：浮点矩阵乘法指令|1|`smt.vfwmadot`|FP16 / BF16|FP32|`MCPM.BF16`|
|`Xsmt*16fp32mm_slide`：面向卷积场景的浮点滑窗矩阵乘法|3|`smt.vfwmadot1/2/3`|FP16 / BF16|FP32|`Vs1` 偶数;<br>`MCPM.BF16`|
|数据布局变换指令|6|`smt.vpack.vv`, `smt.vupack.vv`, `smt.vnpack.vv`, `smt.vnpack4.vv`|多种|多种|`imm2`, `SEW`, `LMUL`|

## 4.2 符号解释（`signedness`）变体约定

本指令集的整数矩阵类指令使用后缀表示 `A` 与 `B` 的符号解释：

|后缀|`A`|`B`|结果 / 累加解释|
|---|---|---|---|
|无后缀|有符号|有符号|有符号累加|
|`u`|无符号|无符号|有符号累加|
|`us`|无符号|有符号|有符号累加|
|`su`|有符号|无符号|有符号累加|

## 4.3 原生助记符索引

### 整数矩阵乘法指令（基础路径）
- `smt.vmadot`
- `smt.vmadotu`
- `smt.vmadotus`
- `smt.vmadotsu`

### 面向卷积场景的整数滑窗矩阵乘法
- `smt.vmadot1`
- `smt.vmadot1u`
- `smt.vmadot1us`
- `smt.vmadot1su`
- `smt.vmadot2`
- `smt.vmadot2u`
- `smt.vmadot2us`
- `smt.vmadot2su`
- `smt.vmadot3`
- `smt.vmadot3u`
- `smt.vmadot3us`
- `smt.vmadot3su`

### 4:2 结构化稀疏整数矩阵乘法
- `smt.vmadot.sp`
- `smt.vmadotu.sp`
- `smt.vmadotus.sp`
- `smt.vmadotsu.sp`

### 面向分块量化的整数矩阵乘法
- `smt.vmadot.hp`
- `smt.vmadotu.hp`
- `smt.vmadotus.hp`
- `smt.vmadotsu.hp`

### 浮点矩阵乘法指令
- `smt.vfwmadot`
- `smt.vfwmadot1`
- `smt.vfwmadot2`
- `smt.vfwmadot3`

### 数据布局变换指令
- `smt.vpack.vv`
- `smt.vupack.vv`
- `smt.vnpack.vv`
- `smt.vnspack.vv`
- `smt.vnpack4.vv`
- `smt.vnspack4.vv`

# 第 5 章 整数矩阵乘法指令

## 5.1 整数矩阵乘法指令（基础路径）：`smt.vmadot*`

### 5.1.1 功能概述

该基础路径执行整数点积并累加到 32 位目标：

$$
C \leftarrow C + A \times B^T
$$

矩阵乘法的几何关系如图 4 所示，其中左侧为 `A` 矩阵，右侧为 `B` 矩阵。

![图4：`smt.vmadot` 基础路径的矩阵计算示意图。](images/ime_extension_png/fig3vmadot.png)
*图 4. 在 VLEN=1024、λ=4、W=4、LMUL=1 条件下的 `smt.vmadot` 矩阵计算示意。左侧为 `A` tile，右侧为 `B` tile。*

### 5.1.2 指令成员
|指令|汇编格式|数据类型路径|tile：M × N × K|
|---|---|---|---|
|`smt.vmadot`|`smt.vmadot vd, vs1, vs2, i4`<br>`smt.vmadot vd, vs1, vs2, i8`|`Int4 × Int4 → Int32`<br>`Int8 × Int8 → Int32`|**A60**：<br>Int8：`4 × 8 × 4`;<br>**A100**：<br>Int4：`8 × 32 × 8`;<br>Int8：`8 × 16 × 8`|
|`smt.vmadotu`|`smt.vmadotu vd, vs1, vs2, i4`<br>`smt.vmadotu vd, vs1, vs2, i8`|`UInt4 × UInt4 → Int32`<br>`UInt8 × UInt8 → Int32`|同上|
|`smt.vmadotus`|`smt.vmadotus vd, vs1, vs2, i4`<br>`smt.vmadotus vd, vs1, vs2, i8`|`UInt4 × Int4 → Int32`<br>`UInt8 × Int8 → Int32`|同上|
|`smt.vmadotsu`|`smt.vmadotsu vd, vs1, vs2, i4`<br>`smt.vmadotsu vd, vs1, vs2, i8`|`Int4 × UInt4 → Int32`<br>`Int8 × UInt8 → Int32`|同上|

### 5.1.3 程序可见语义

#### Int8 路径

```c
if (SpineCoreArchID == A064) {
    M = N = 8; K = 16;
} else if (SpineCoreArchID == A03C) {
    M = N = 4; K = 8;
} else {
    unsupported_profile();
}

for (p = 0; p < (2 * VLEN * LMUL / 32); p++) {
    i = (p / M) * K;
    j = (p % N) * K;
    for (q = 0; q < K; q++) {
        vd[p] = vd[p] + vs1[i + q] * vs2[j + q];
    }
}
```
**注**：0xA03C 是 A60 的 `ArchID`，0xA064 是 A100 的 `ArchID`。

#### Int4 路径

```c
if (SpineCoreArchID == A064) {
    M = N = 8; K = 16;
} else {
    unsupported_profile();
}

if (LMUL != 1) {
    illegal_instruction();
}

M = N = 8; K = 32;

for (p = 0; p < (2 * VLEN / 32); p++) {
    i = (p / M) * K;
    j = (p % N) * K;
    for (q = 0; q < K; q++) {
        vd[p] = vd[p] + vs1[i + q] * vs2[j + q];
    }
}
```

### 5.1.4 非法条件

- Int8 路径中 `LMUL` 非 `1`；
- Int4 路径中 `LMUL` 非 `1`；
- `Vd` 非偶数编号寄存器；
- `Vd/Vd+1` 与 `Vs1` 或 `Vs2` 重叠；

### 5.1.5 算术说明

- 目标累加槽按 32 位整数解释；
- 累加在目标位宽内进行，软件应按 32 位结果解释最终值；
- 本指令集不为该指令类型定义额外的向量 mask 语义。

### 5.1.6 应用举例
```
// A60 应用示例：
// MatrixA[4, 8]          x  MatrixB[8, 4]    =   MatrixC[4, 4]
//    [0 1 2 3 4 5  6  7]       [0 1 2 11]           [140 168 196 224] 
//    [1 2 3 4 5 6  7  8]       [1 2 3  4]           [168 204 240 284] 
//    [2 3 4 5 6 7  8  9]       [2 3 4  5]           [196 240 284 344] 
//    [4 5 6 7 8 9 10 11]       [3 4 5  6]           [252 312 372 464] 
//                              [4 5 6  7]
//                              [5 6 7  8]
//                              [6 7 8  9]
//                              [7 8 9 10]

#include <stdio.h>
#include <stdint.h>

void matmul(const int8_t *A, const int8_t *B, int32_t *C) {
    __asm__ volatile(
        "vsetvli        t0, zero, e8, m1          \n\t"
        "vle8.v         v0, (%[A])                \n\t"
        "vle8.v         v1, (%[B])                \n\t"
        "smt.vmadot         v16, v0, v1               \n\t"
        "vsetvli        t0, zero, e32, m2         \n\t"
        "vse32.v        v16, (%[C])               \n\t"
        : [ A ] "+r"(A), [ B ] "+r"(B), [ C ] "+r"(C)
        :
        : "cc");
}

int main()
{
    printf("Test Start.\n");
    // Init the matrixA, matrixB and matrixC.
    int8_t A[32] = {0, 1, 2, 3, 4, 5, 6, 7,
                    1, 2, 3, 4, 5, 6, 7, 8,
                    2, 3, 4, 5, 6, 7, 8, 9,
                    4, 5, 6, 7, 8, 9, 10, 11};
    int8_t B[32] = {0, 1, 2, 3, 4, 5, 6, 7,
                    1, 2, 3, 4, 5, 6, 7, 8,
                    2, 3, 4, 5, 6, 7, 8, 9,
                    11, 4, 5, 6, 7, 8, 9, 10};
    int32_t C[32] = {0, 0, 0, 0,
                     0, 0, 0, 0,
                     0, 0, 0, 0,
                     0, 0, 0, 0};
    
    // Call the FUNCTION
    matmul(A, B, C);
    
    // Print the OUTPUT
    for(int32_t iter_i=0; iter_i<4; iter_i++){
        for(int32_t iter_j=0; iter_j<4; iter_j++){
            printf("%d \t", C[iter_i*4 + iter_j]);
        }
        printf(" \n");
    }
    printf("Test End.\n");
    return 0;
}
```

## 5.2 面向卷积场景的整数滑窗矩阵乘法：`smt.vmadot1*` / `smt.vmadot2*` / `smt.vmadot3*`

### 5.2.1 功能概述

该滑窗路径仅支持 Int8 输入，其计算类型与基础 Int8 整数矩阵乘法相同，但 `A` 操作数在读取时带有固定滑窗位移。

图 5 展示了 `slide = 1 / 2 / 3` 时的窗口移动方式，以及窗口跨越 `Vs1` 与 `Vs1+1` 时的拼接取数方法。

![图5：整数滑窗矩阵乘法（`slide=1`）示意图。](images/ime_extension_png/fig4vmadotslide.png)
*图 5. 在 VLEN=1024、λ=4、W=4、LMUL=1 条件下，`smt.vmadot1`（即 `slide=1`）的滑窗取数与计算示意。*

### 5.2.2 指令成员
|指令类型|变体|汇编格式|slide|数据类型路径|tile|
|---|---|---|---|---|---|
|`smt.vmadot1*`|`smt.vmadot1`,<br> `smt.vmadot1u`,<br> `smt.vmadot1us`,<br> `smt.vmadot1su`|`smt.vmadot1 vd, vs1, vs2, i8`<br>`smt.vmadot1u vd, vs1, vs2, i8`<br>`smt.vmadot1us vd, vs1, vs2, i8`<br>`smt.vmadot1su vd, vs1, vs2, i8`|1|`[U]Int8 × [U]Int8 → Int32`|**A60**：`4 × 8 × 4`<br>**A100**：`8 × 16 × 8`|
|`smt.vmadot2*`|`smt.vmadot2`,<br> `smt.vmadot2u`,<br> `smt.vmadot2us`,<br> `smt.vmadot2su`|`smt.vmadot2 vd, vs1, vs2, i8`<br>`smt.vmadot2u vd, vs1, vs2, i8`<br>`smt.vmadot2us vd, vs1, vs2, i8`<br>`smt.vmadot2su vd, vs1, vs2, i8`|2|同上|同上|
|`smt.vmadot3*`|`smt.vmadot3`,<br> `smt.vmadot3u`,<br> `smt.vmadot3us`,<br> `smt.vmadot3su`|`smt.vmadot3 vd, vs1, vs2, i8`<br>`smt.vmadot3u vd, vs1, vs2, i8`<br>`smt.vmadot3us vd, vs1, vs2, i8`<br>`smt.vmadot3su vd, vs1, vs2, i8`|3|同上|同上|

### 5.2.3 程序可见语义

```c
if (SpineCoreArchID == A064) {
    M = N = 8; K = 16;
} else if (SpineCoreArchID == A03C) {
    M = N = 4; K = 8;
} else {
    unsupported_profile();
}

slide *= K;

for (p = 0; p < (2 * VLEN * LMUL / 32); p++) {
    i = (p / M) * K;
    j = (p % N) * K;
    for (q = 0; q < K; q++) {
        vd[p] = vd[p] + vs1[i + q + slide] * vs2[j + q];
    }
}
```

### 5.2.4 非法条件

- `LMUL` 非 `1`；
- `Vd` 寄存器编号非偶数；
- `Vd/Vd+1` 与源寄存器重叠；

### 5.2.5 算术说明

- 目标累加槽按 32 位整数解释；
- 累加在目标位宽内进行，软件应按 32 位结果解释最终值；
- 本指令集不为该指令类型定义额外的向量 mask 语义。
- 只在 `A` 的索引侧增加滑窗功能；

### 5.2.6 应用举例
```
/*********************** A60 示例 ************************
* MatrixA(feature)
*     [0 1 2 3  4  5  6  7]
*     [1 2 3 4  5  6  7  8]
*     [2 3 4 5  6  7  8  9]
*     [4 5 6 7  8  9 10 11]
*     [5 6 7 8  9 10 11 12] 
*     [6 7 8 9 10 11 12 13]
*
*  "smt.vmadot     v16, v0, v8             \n\t"
*  MatrixA[4, 8]：         x  MatrixB[8, 4]    =   MatrixC[4, 4]
*     [0 1 2 3 4 5  6  7]       [0 1 2 11]           [140 168 196 224] 
*     [1 2 3 4 5 6  7  8]       [1 2 3  4]           [168 204 240 284] 
*     [2 3 4 5 6 7  8  9]       [2 3 4  5]           [196 240 284 344] 
*     [4 5 6 7 8 9 10 11]       [3 4 5  6]           [252 312 372 464] 
*                               [4 5 6  7]
*                               [5 6 7  8]
*                               [6 7 8  9]
*                               [7 8 9 10]
*
*  "smt.vmadot1    v16, v0, v8             \n\t"
*  MatrixA[4, 8]：         x  MatrixB[8, 4]  + MatrixC[4, 4]  =  MatrixC[4, 4]
*     [1 2 3 4 5  6  7  8]      [0 1 2 11]           [308 372 436 224] 
*     [2 3 4 5 6  7  8  9]      [1 2 3  4]           [364 444 524 628] 
*     [4 5 6 7 8  9 10 11]      [2 3 4  5]           [448 552 656 808] 
*     [5 6 7 8 9 10 11 12]      [3 4 5  6]           [532 660 788 988] 
*                               [4 5 6  7]
*                               [5 6 7  8]
*                               [6 7 8  9]
*                               [7 8 9 10]
*
*  "smt.vmadot2     v16, v0, v8            \n\t"
* MatrixA[4, 8]：         x  MatrixB[8, 4]  + MatrixC[4, 4]   =   MatrixC[4, 4]
*     [2 3 4 5 6  7  8   9]     [0 1 2 11]           [504  612  720  852] 
*     [4 5 6 7 8  9  10 11]     [1 2 3  4]           [616  756  896 1092] 
*     [5 6 7 8 9  10 11 12]     [2 3 4  5]           [728  900 1072 1332] 
*     [6 7 8 9 10 11 12 13]     [3 4 5  6]           [840 1044 1248 1572] 
*                               [4 5 6  7]
*                               [5 6 7  8]
*                               [6 7 8  9]
*                               [7 8 9 10]
******************************************************/
#include <stdio.h>
#include <stdint.h>

void conv1d(const int8_t *feature, const int8_t *weight, int32_t *output) {
    __asm__ volatile(
        "vsetvli    t0, zero, e8, m1        \n\t"
        "vle8.v     v0, (%[A])              \n\t"
        "addi       %[A], %[A], 4*8         \n\t"
        "vle8.v     v1, (%[A])              \n\t"
        "addi       %[A], %[A], 4*8         \n\t"
        "vle8.v     v8, (%[B])              \n\t"
        "addi       %[B], %[B], 4*8         \n\t"
        "smt.vmadot     v16, v0, v8             \n\t"
        "smt.vmadot1    v16, v0, v8             \n\t"
        "smt.vmadot2    v16, v0, v8             \n\t"
        "vsetvli    t0, zero, e32, m2       \n\t"
        "vse32.v    v16, (%[C])             \n\t"
        
        : [A] "+r"(feature), [ B ] "+r"(weight), [ C ] "+r"(output)
        :
        : "cc");
}

int main()
{
    printf("Test Start.\n");
    // Init the matrixA, matrixB and matrixC.
    int8_t A[64] = {0, 1, 2, 3,  4,  5,  6,  7,
                    1, 2, 3, 4,  5,  6,  7,  8,
                    2, 3, 4, 5,  6,  7,  8,  9,
                    4, 5, 6, 7,  8,  9, 10, 11,
                    5, 6, 7, 8,  9, 10, 11, 12,
                    6, 7, 8, 9, 10, 11, 12, 13,
                    0, 0, 0, 0,  0,  0,  0,  0,
                    0, 0, 0, 0,  0,  0,  0,  0};
    int8_t B[32] = {0, 1, 2, 3, 4, 5, 6, 7,
                    1, 2, 3, 4, 5, 6, 7, 8,
                    2, 3, 4, 5, 6, 7, 8, 9,
                    11, 4, 5, 6, 7, 8, 9, 10};
    int32_t C[32] = {0, 0, 0, 0,
                     0, 0, 0, 0,
                     0, 0, 0, 0,
                     0, 0, 0, 0};
    
    // Call the FUNCTION
    conv1d(A, B, C);
    
    // Print the OUTPUT
    for(int32_t iter_i=0; iter_i<4; iter_i++){
        for(int32_t iter_j=0; iter_j<4; iter_j++){
            printf("%d \t", C[iter_i*4 + iter_j]);
        }
        printf(" \n");
    }
    printf("Test End.\n");
    return 0;
}
```

## 5.3 4:2 结构化稀疏整数矩阵乘法：`smt.vmadot.sp*`


### 5.3.1 功能概述

本指令集定义 4:2 结构化稀疏整数矩阵乘法。该路径从 `A` 的每 4 个源元素中，根据 4-bit 掩码恢复 2 个有效值，再与 `B` 执行点积并累加到 Int32 目标。
图 6 展示了 4:2 结构化稀疏恢复过程，同时说明了掩码如何从每 4 个候选元素中恢复出 2 个有效元素。

![图6：4:2 结构化稀疏恢复与 `smt.vmadot.sp` 计算示意图。](images/ime_extension_png/fig5vmadotsp.png)
*图 6. 在 VLEN=1024、λ=4、W=4、LMUL=1 条件下，`smt.vmadot.sp v16, v2, v8, v0, i8` 的稀疏恢复与乘加流程示意。*

### 5.3.2 指令成员

|指令|汇编格式|数据类型路径|掩码寄存器|选择字段|tile|
|---|---|---|---|---|---|
|`smt.vmadot.sp`|`smt.vmadot.sp vd, vs1, vs2, v0/v1, imm2, i4`<br>`smt.vmadot.sp vd, vs1, vs2, v0/v1, imm2, i8`|`Int4 × Int4 → Int32`<br>`Int8 × Int8 → Int32`|`V0` / `V1`|`imm2`|Int4：`8 × 64 × 8`；<br>Int8：`8 × 32 × 8`|
|`smt.vmadotu.sp`|`smt.vmadotu.sp vd, vs1, vs2, v0/v1, imm2, i4`<br>`smt.vmadotu.sp vd, vs1, vs2, v0/v1, imm2, i8`|`UInt4 × UInt4 → Int32`<br>`UInt8 × UInt8 → Int32`|同上|同上|同上|
|`smt.vmadotus.sp`|`smt.vmadotus.sp vd, vs1, vs2, v0/v1, imm2, i4`<br>`smt.vmadotus.sp vd, vs1, vs2, v0/v1, imm2, i8`|`UInt4 × Int4 → Int32`<br>`UInt8 × Int8 → Int32`|同上|同上|同上|
|`smt.vmadotsu.sp`|`smt.vmadotsu.sp vd, vs1, vs2, v0/v1, imm2, i4`<br>`smt.vmadotsu.sp vd, vs1, vs2, v0/v1, imm2, i8`|`Int4 × UInt4 → Int32`<br>`Int8 × UInt8 → Int32`|同上|同上|同上|

### 5.3.3 有效掩码值

本指令集将以下 4-bit 掩码定义为合法稀疏恢复模式：

- `0b'1001`
- `0b'1010`
- `0b'1100`
- `0b'0101`
- `0b'0110`
- `0b'0011`

对除上述 6 种合法掩码值之外的所有取值，`smt.vmadot.sp*` **shall** 不进行元素选取，并将该组恢复结果按零处理（即等效于 `vs1_tmp1 = 0` 且 `vs1_tmp2 = 0`）。

### 5.3.4 程序可见语义

#### Int8 路径

```c
if (SpineCoreArchID != A064) {
    unsupported_profile();
}
if (LMUL != 1) {
    illegal_instruction();
}

M = N = 8; K = 32;
vmask_tmp = vmask[imm2];

for (p = 0; p < (2 * LMUL * VLEN / 32); p++) {
    i = (p / M) * (2 * K);
    j = (p % N) * K;

    for (q = 0; q < (K / 2); q++) {
        switch (vmask_tmp[j/2 + q]) {
            case 0b1001: vs1_tmp1 = vs1[i + 4*q + 0]; vs1_tmp2 = vs1[i + 4*q + 3]; break;
            case 0b1010: vs1_tmp1 = vs1[i + 4*q + 1]; vs1_tmp2 = vs1[i + 4*q + 3]; break;
            case 0b1100: vs1_tmp1 = vs1[i + 4*q + 2]; vs1_tmp2 = vs1[i + 4*q + 3]; break;
            case 0b0101: vs1_tmp1 = vs1[i + 4*q + 0]; vs1_tmp2 = vs1[i + 4*q + 2]; break;
            case 0b0110: vs1_tmp1 = vs1[i + 4*q + 1]; vs1_tmp2 = vs1[i + 4*q + 2]; break;
            case 0b0011: vs1_tmp1 = vs1[i + 4*q + 0]; vs1_tmp2 = vs1[i + 4*q + 1]; break;
            default:     vs1_tmp1 = 0;              vs1_tmp2 = 0;              break;
        }

        vd[p] = vd[p] + vs2[j + 2*q] * vs1_tmp1;
        vd[p] = vd[p] + vs2[j + 2*q + 1] * vs1_tmp2;
    }
}
```

上述 Int8 伪代码中的 `default` 分支即对“非 6 种合法掩码值”的规范性实现：不进行元素选取，并按零参与后续乘加。

#### Int4 路径

以下语义依据现有实现资料整理；若后续实现文档给出更细粒度定义，则应以实现定义为准。

```c
if (SpineCoreArchID != A064) {
    unsupported_profile();
}
if (LMUL != 1) {
    illegal_instruction();
}

M = N = 8; K = 64;
vmask_tmp = vmask[imm2];

for (p = 0; p < (2 * LMUL * VLEN / 32); p++) {
    i = (p / M) * (2 * K);
    j = (p % N) * K;

    for (q = 0; q < (K / 2); q++) {
        switch (vmask_tmp[j/2 + q]) {
            case 0b1001: vs1_tmp1 = vs1[i + 4*q + 0]; vs1_tmp2 = vs1[i + 4*q + 3]; break;
            case 0b1010: vs1_tmp1 = vs1[i + 4*q + 1]; vs1_tmp2 = vs1[i + 4*q + 3]; break;
            case 0b1100: vs1_tmp1 = vs1[i + 4*q + 2]; vs1_tmp2 = vs1[i + 4*q + 3]; break;
            case 0b0101: vs1_tmp1 = vs1[i + 4*q + 0]; vs1_tmp2 = vs1[i + 4*q + 2]; break;
            case 0b0110: vs1_tmp1 = vs1[i + 4*q + 1]; vs1_tmp2 = vs1[i + 4*q + 2]; break;
            case 0b0011: vs1_tmp1 = vs1[i + 4*q + 0]; vs1_tmp2 = vs1[i + 4*q + 1]; break;
            default:     vs1_tmp1 = 0;              vs1_tmp2 = 0;              break;
        }

        vd[p] = vd[p] + vs2[j + 2*q] * vs1_tmp1;
        vd[p] = vd[p] + vs2[j + 2*q + 1] * vs1_tmp2;
    }
}
```

上述 Int4 伪代码中的 `default` 分支与 Int8 路径一致，均对应“非 6 种合法掩码值时按零处理”的规范性条款。

### 5.3.5 非法条件

- `LMUL != 1`；
- `Vd` 非偶数；
- `Vd/Vd+1` 与源寄存器重叠；
- 掩码寄存器选择非法；
- `imm2` 指向的掩码分段超出实现定义范围；

### 5.3.6 算术说明

- 目标累加槽按 32 位整数解释；
- 累加在目标位宽内进行，软件应按 32 位结果解释最终值；
- `V0` / `V1` 作为稀疏恢复参数寄存器；

### 5.3.7 应用举例

```
/*********************** A100 示例 ************************
* MatrixA(feature, sparse M8*K32)
* Vn:     [[ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15]
*          [16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31]
*          [ 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16]
*          [17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32]
*          [ 2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17]
*          [18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33]
*          [ 3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18]
*          [18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33]]
* V(n+1): [[ 4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19]
*          [19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34]
*          [ 5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20]
*          [20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35]
*          [ 6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21]
*          [21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36]
*          [ 7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22]
*          [22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37]]
*
* MatrixB（weight，compressed M8 × K16）
*          [0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15]
*          [1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16]
*          [2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17]
*          [3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18]
*          [4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19]
*          [5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20]
*          [6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21]
*          [7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22]
*
* Sparse parameter of Matrix B(M8*K32 in binary)
* V0/V1    [0x99 0x99 0x99 0x99 0xAA 0xAA 0xAA 0xAA 0xCC 0xCC 0xCC 0xCC 0x55 0x55 0x55 0x55]
*          [0x66 0x66 0x66 0x66 0x33 0x33 0x33 0x33 0x99 0x99 0x99 0x99 0xAA 0xAA 0xAA 0xAA]
*          [...                                                                            ]
*          [...                                                                            ]
*          [...                                                                            ]
*          [...                                                                            ]
*          [...                                                                            ]
*          [...                                                                            ]
*
*  "smt.vmadot.sp     v16, v2, v8, v0, 0, i8            \n\t"
*  MatrixA[8, 32]：    ×  Recover(压缩后的 MatrixBt[8, 16], v0[0 : 511])   =   MatrixC[8, 8]
*     [0 1 ... 30 31]        [0 0 0 1 ... 14  0  0 15]           [2544, 2856, 3184, 3200, 3528, 3576, 4032, 4322,]
*     [1 2 ... 31 32]        [1 0 2 0 ... 15  0 16  0]           [2664, 2992, 3336, 3368, 3712, 3776, 4248, 4544,]
*     [2 3 ... 32 33]        [2 3 0 0 ... 16 17  0  0]           [2784, 3128, 3488, 3536, 3896, 3976, 4464, 4766,]
*     [3 4 ... 33 34]        [0 3 0 4 ...  0 17  0 18]           [2812, 3164, 3532, 3588, 3956, 4044, 4540, 4840,]
*     [4 5 ... 34 35]        [0 4 5 0 ...  0 18 19  0]           [2932, 3300, 3684, 3756, 4140, 4244, 4756, 5062,]
*     [5 6 ... 35 36]        [0 0 5 6 ...  0  0 19 20]           [3052, 3436, 3836, 3924, 4324, 4444, 4972, 5284,]
*     [6 7 ... 36 37]        [6 0 0 7 ... 20  0  0 21]           [3172, 3572, 3988, 4092, 4508, 4644, 5188, 5506,]
*     [7 8 ... 37 38]        [7 0 8 0 ... 21  0 22  0]           [3292, 3708, 4140, 4260, 4692, 4844, 5404, 5728 ]
******************************************************/
#include <stdio.h>
#include <stdint.h>

void spgemm(const int8_t *feature, const int8_t *weight, const int8_t *sparse, int32_t *output) {
    __asm__ volatile(
        "vsetvli    t0, zero, e8, m1        \n\t"
        "vle8.v     v2, (%[A])              \n\t"
        "addi       %[A], %[A], 8*16        \n\t"
        "vle8.v     v3, (%[A])              \n\t"
        "addi       %[A], %[A], 8*16        \n\t"
        "vle8.v     v8, (%[B])              \n\t"
        "addi       %[B], %[B], 8*16        \n\t"
        "vle8.v     v0, (%[B_sp])           \n\t"
        "smt.vmadot.sp  v16, v2, v8, v0, 0, i8  \n\t"
        "vsetvli    t0, zero, e32, m2       \n\t"
        "vse32.v    v16, (%[C])             \n\t"

        : [A] "+r"(feature), [ B ] "+r"(weight), [ B_sp ] "+r"(sparse), [ C ] "+r"(output)
        :
        : "cc");
}

int main()
{
    printf("Test Start.\n");
    // Init the matrixA, matrixB and matrixC.
    int8_t A[8*32] = { 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15,
                    16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
                     1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16,
                    17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
                     2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17,
                    18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33,
                     3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                    18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33,
                     4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                    19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
                     5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                    20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
                     6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
                    21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
                     7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22,
                    22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37};
    int8_t B[8*16] = {0, 1, 2, 3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15,
                      1, 2, 3, 4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16,
                      2, 3, 4, 5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17,
                      3, 4, 5, 6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                      4, 5, 6, 7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                      5, 6, 7, 8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                      6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
                      7, 8, 9, 0, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22};
    int8_t B_sparse[8*4] = {0x99, 0x99, 0x99, 0x99, 0xAA, 0xAA, 0xAA, 0xAA,
                        0xCC, 0xCC, 0xCC, 0xCC, 0x55, 0x55, 0x55, 0x55,
                        0x66, 0x66, 0x66, 0x66, 0x33, 0x33, 0x33, 0x33,
                        0x99, 0x99, 0x99, 0x99, 0xAA, 0xAA, 0xAA, 0xAA};
    int32_t C[64] = {0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0};
    
    // Call the FUNCTION
    spgemm(A, B, B_sparse, C);
    
    // Print the OUTPUT
    for(int32_t iter_i=0; iter_i<8; iter_i++){
        for(int32_t iter_j=0; iter_j<8; iter_j++){
            printf("%d \t", C[iter_i*8 + iter_j]);
        }
        printf(" \n");
    }
    printf("Test End.\n");
    return 0;
}
```

## 5.4 面向分块量化的整数矩阵乘法：`smt.vmadot.hp*`

### 5.4.1 功能概述

高精度恢复指令先进行整数点积，再乘以浮点 scale 参数，最后累加到浮点目标：

$$
C \leftarrow (A \times B) \times S + C
$$

这是本指令集面向分块量化的一条混合计算路径，其目标类型**并非 Int32，而是 FP16 / BF16**。

图 7 给出了该路径的计算流程。

![图7：分块量化整数矩阵乘法（`smt.vmadot.hp`）示意图。](images/ime_extension_png/fig6vmadothp.png)
*图 7. 在 VLEN=1024、λ=8、W=2、LMUL=1 条件下，`smt.vmadot.hp v16, v2, v8, v0, i8` 的计算流程示意。*

### 5.4.2 指令成员


|指令|汇编格式|数据类型路径|scale 来源|选择字段|tile|
|---|---|---|---|---|---|
|`smt.vmadot.hp`|`smt.vmadot.hp vd, vs1, vs2, v0/v1, imm3, i4`<br>`smt.vmadot.hp vd, vs1, vs2, v0/v1, imm3, i8`|`(Int4 × Int4) * FP16 → FP16`<br>`(Int4 × Int4) * BF16 → BF16`<br>`(Int8 × Int8) * FP16 → FP16`<br>`(Int8 × Int8) * BF16 → BF16`|`V0` / `V1`|`imm3`|Int4：`8 × 32 × 8`;<br>Int8：`8 × 16 × 8`|
|`smt.vmadotu.hp`|`smt.vmadotu.hp vd, vs1, vs2, v0/v1, imm3, i4`<br>`smt.vmadotu.hp vd, vs1, vs2, v0/v1, imm3, i8`|`(UInt4 × UInt4) * FP16 → FP16`<br>`(UInt4 × UInt4) * BF16 → BF16`<br>`(UInt8 × UInt8) * FP16 → FP16`<br>`(UInt8 × UInt8) * BF16 → BF16`|同上|同上|同上|
|`smt.vmadotus.hp`|`smt.vmadotus.hp vd, vs1, vs2, v0/v1, imm3, i4`<br>`smt.vmadotus.hp vd, vs1, vs2, v0/v1, imm3, i8`|`(UInt4 × Int4) * FP16 → FP16`<br>`(UInt4 × Int4) * BF16 → BF16`<br>`(UInt8 × Int8) * FP16 → FP16`<br>`(UInt8 × Int8) * BF16 → BF16`|同上|同上|同上|
|`smt.vmadotsu.hp`|`smt.vmadotsu.hp vd, vs1, vs2, v0/v1, imm3, i4`<br>`smt.vmadotsu.hp vd, vs1, vs2, v0/v1, imm3, i8`|`(Int4 × UInt4) * FP16 → FP16`<br>`(Int4 × UInt4) * BF16 → BF16`<br>`(Int8 × UInt8) * FP16 → FP16`<br>`(Int8 × UInt8) * BF16 → BF16`|同上|同上|同上|

### 5.4.3 程序可见语义

#### Int8 路径

```c
if (LMUL != 1) {
    illegal_instruction();
}

M = N = 8; K = 16;

for (p = 0; p < (VLEN / 16); p++) {
    i = (p / M) * K;
    j = (p % N) * K;
    fp16_or_bf16 scale = vscale[imm3 * N + (p % N)];
    Int32 tmp = 0;

    for (q = 0; q < K; q++) {
        tmp = tmp + vs1[i + q] * vs2[j + q];
    }

    vd[p] += (fp16_or_bf16)tmp * scale;
}
```

#### Int4 路径

以下语义依据现有实现资料整理；若后续实现文档给出更细粒度定义，则应以实现定义为准。

```c
if (LMUL != 1) {
    illegal_instruction();
}

M = N = 8; K = 32;

for (p = 0; p < (VLEN / 16); p++) {
    i = (p / M) * K;
    j = (p % N) * K;
    fp16_or_bf16 scale = vscale[imm3 * N + (p % N)];
    Int32 tmp = 0;

    for (q = 0; q < K; q++) {
        tmp = tmp + vs1[i + q] * vs2[j + q];
    }

    vd[p] += (fp16_or_bf16)tmp * scale;
}
```

### 5.4.4 scale 与格式解释

- scale 参数来自 `V0` 或 `V1`；
- `imm3` 选择 8 组 scale 参数之一；
- 当 `MCPM.BF16 = 0` 时，scale 与目标按 FP16 解释；
- 当 `MCPM.BF16 = 1` 时，scale 与目标按 BF16 解释。

其中，上述伪代码中的 `fp16_or_bf16` 表示“由 `MCPM.BF16` 决定的 16 位浮点格式”。

### 5.4.5 非法条件

- `LMUL != 1`；
- `Vd` 与 `Vs1` / `Vs2` 重叠；
- scale 寄存器选择非法；
- `imm3` 指向的 scale 组非法；

### 5.4.6 算术说明

- 目标累加数据类型为 FP16 / BF16，而非 Int32；
- 累加在目标位宽内进行，软件应按 16 位结果解释最终值；
- `V0` / `V1` 作为分块量化路径的 scale 参数寄存器；
- 是“整数输入 + 浮点恢复”的混合路径，而不是普通整数累加路径。


### 5.4.7 应用举例

```
/*********************** A100 示例 ************************
* MatrixA(feature, sparse M8*K16)
*          [0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15]
*          [1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16]
*          [2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17]
*          [3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18]
*          [4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19]
*          [5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20]
*          [6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21]
*          [7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22]
*
* MatrixB（weight，dense M8 × K16）
*          [0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15]
*          [1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16]
*          [2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17]
*          [3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18]
*          [4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19]
*          [5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20]
*          [6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21]
*          [7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22]
*
* Matrix B 的 scale 参数（N = 8，FP16）
* V0/V1    [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
*          [...                                   ]
*          [...                                   ]
*          [...                                   ]
*          [...                                   ]
*          [...                                   ]
*          [...                                   ]
*          [...                                   ]
*
*  "smt.vmadot.hp     v16, v2, v8, v0, 0, i8            \n\t"
*  （MatrixA[8, 16] × MatrixBt[8, 16]）* v0[0 : 128]   =   MatrixC[8, 8]
*     [0 1 ... 30 31]      [0 1 ... 30 31]   [1.0 ... 8.0]      [1240.0 2720.0 4440.0  6400.0  8600.0 11040.0 13720.0 16640.0]
*     [1 2 ... 31 32]      [1 2 ... 31 32]                      [1360.0 2992.0 4896.0  7072.0  9520.0 12240.0 15232.0 18496.0]
*     [2 3 ... 32 33]      [2 3 ... 32 33]                      [1480.0 3264.0 5352.0  7744.0 10440.0 13440.0 16736.0 20352.0]
*     [3 4 ... 33 34]      [3 4 ... 33 34]                      [1600.0 3536.0 5808.0  8416.0 11360.0 14640.0 18256.0 22208.0]
*     [4 5 ... 34 35]      [4 5 ... 34 35]                      [1720.0 3808.0 6264.0  9088.0 12280.0 15840.0 19776.0 24064.0]
*     [5 6 ... 35 36]      [5 6 ... 35 36]                      [1840.0 4080.0 6720.0  9760.0 13200.0 17040.0 21280.0 25920.0]
*     [6 7 ... 36 37]      [6 7 ... 36 37]                      [1960.0 4352.0 7176.0 10432.0 14120.0 18240.0 22784.0 27776.0]
*     [7 8 ... 37 38]      [7 8 ... 37 38]                      [2080.0 4624.0 7632.0 11104.0 15040.0 19440.0 24304.0 29632.0]
******************************************************/
#include <stdio.h>
#include <stdint.h>

void gemm(const int8_t *feature, const int8_t *weight, const _Float16 *scale, _Float16 *output) {
    __asm__ volatile(
        "vsetvli    t0, zero, e8, m1        \n\t"
        "vmv.v.i    v16, 0                  \n\t"
        "vle8.v     v2, (%[A])              \n\t"
        "vle8.v     v8, (%[B])              \n\t"
        "vsetvli    t0, zero, e16, m1       \n\t"
        "vle16.v    v0, (%[BSCL])           \n\t"
        "smt.vmadot.hp  v16, v2, v8, v0, 0, i8  \n\t"
        "vse16.v    v16, (%[C])             \n\t"

        :
        : [A] "r"(feature), [ B ] "r"(weight), [ BSCL ] "r"(scale), [ C ] "r"(output)
        : "cc", "memory", "t0");
}

int main()
{
    printf("Test Start.\n");
    // Init the matrixA, matrixB and matrixC.
    int8_t A[8*16] = {0, 1, 2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15,
                      1, 2, 3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16,
                      2, 3, 4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17,
                      3, 4, 5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                      4, 5, 6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                      5, 6, 7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                      6, 7, 8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
                      7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22};
    int8_t B[8*16] = {0, 1, 2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15,
                      1, 2, 3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16,
                      2, 3, 4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17,
                      3, 4, 5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                      4, 5, 6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                      5, 6, 7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                      6, 7, 8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
                      7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22};
    _Float16 B_scale[64] = {1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0};
    _Float16 C[64] = {0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0};

    // Call the FUNCTION
    gemm(A, B, B_scale, C);

    // Print the OUTPUT
    for(int32_t iter_i=0; iter_i<8; iter_i++){
        for(int32_t iter_j=0; iter_j<8; iter_j++){
            printf("%f \t", (float)C[iter_i*8 + iter_j]);
        }
        printf(" \n");
    }
    printf("Test End.\n");
    return 0;
}
```

# 第 6 章 浮点矩阵乘法指令

## 6.1 浮点矩阵乘法指令（基础路径）：`smt.vfwmadot`

### 6.1.1 功能概述

`smt.vfwmadot` 执行 FP16 / BF16 输入、FP32 累加的浮点矩阵乘法：

$$
C \leftarrow C + A \times B^T
$$
图 8 给出了该路径的计算流程。

![图8：`smt.vfwmadot` 浮点矩阵乘法示意图。](images/ime_extension_png/fig7fwmadot.png)
*图 8. 在 VLEN=1024、λ=8、W=2、LMUL=1 条件下，`smt.vfwmadot v16, v2, v8` 的计算流程示意。*
### 6.1.2 指令成员

|指令|汇编格式|数据类型路径|tile|控制|
|---|---|---|---|---|
|`smt.vfwmadot`|`smt.vfwmadot vd, vs1, vs2`|`FP16 × FP16 → FP32`<br>`BF16 × BF16 → FP32`|`8 × 8 × 8`|`MCPM.BF16`|

### 6.1.3 输入格式解释

|`MCPM.BF16`|输入 `A`|输入 `B`|目标 / 累加|
|---|---|---|---|
|0|FP16|FP16|FP32|
|1|BF16|BF16|FP32|

本指令集 **不定义** 同一条指令中 `A` 与 `B` 使用不同浮点格式的混合输入语义。

### 6.1.4 程序可见语义

```c
if (LMUL != 1) {
    illegal_instruction();
}

M = N = 8; K = 8;

for (p = 0; p < (2 * VLEN / 32); p++) {
    i = (p / M) * K;
    j = (p % N) * K;
    for (q = 0; q < K; q++) {
        vd[p] = vd[p] + (fp32)vs1[i + q] * (fp32)vs2[j + q];
    }
}
```

### 6.1.5 非法条件

- `LMUL != 1`；
- `Vd` 非偶数；
- `Vd/Vd+1` 与 `Vs1` / `Vs2` 重叠；
- 浮点输入格式与 `MCPM.BF16` 控制不一致。

### 6.1.6 算术说明

- 目标累加数据类型为 FP32；
- 累加在目标位宽内进行，软件应按 32 位结果解释最终值；

### 6.1.7 应用举例

```
/*********************** A100 示例 ************************
* MatrixA(feature, M8*K8)
*          [0.0  1.0  2.0  3.0  4.0  5.0  6.0  7.0]
*          [1.0  2.0  3.0  4.0  5.0  6.0  7.0  8.0]
*          [2.0  3.0  4.0  5.0  6.0  7.0  8.0  9.0]
*          [3.0  4.0  5.0  6.0  7.0  8.0  9.0 10.0]
*          [4.0  5.0  6.0  7.0  8.0  9.0 10.0 11.0]
*          [5.0  6.0  7.0  8.0  9.0 10.0 11.0 12.0]
*          [6.0  7.0  8.0  9.0 10.0 11.0 12.0 13.0]
*          [7.0  8.0  9.0 10.0 11.0 12.0 13.0 14.0]
*
* MatrixB(weight, M8*K8)
*          [0.0  1.0  2.0  3.0  4.0  5.0  6.0  7.0]
*          [1.0  2.0  3.0  4.0  5.0  6.0  7.0  8.0]
*          [2.0  3.0  4.0  5.0  6.0  7.0  8.0  9.0]
*          [3.0  4.0  5.0  6.0  7.0  8.0  9.0 10.0]
*          [4.0  5.0  6.0  7.0  8.0  9.0 10.0 11.0]
*          [5.0  6.0  7.0  8.0  9.0 10.0 11.0 12.0]
*          [6.0  7.0  8.0  9.0 10.0 11.0 12.0 13.0]
*          [7.0  8.0  9.0 10.0 11.0 12.0 13.0 14.0]
*
*  "smt.vfwmadot     v16, v2, v8           \n\t"
*   MatrixA[8, 8]   ×  MatrixBt[8, 8]   =   MatrixC[8, 8]
*     [0.0 ...  7.0]      [0.0 ...  7.0]   =   [140.0 168.0 196.0 224.0 252.0 280.0 308.0 336.0]
*     [1.0 ...  8.0]      [1.0 ...  8.0]       [168.0 204.0 240.0 276.0 312.0 348.0 384.0 420.0]
*     [2.0 ...  9.0]      [2.0 ...  9.0]       [196.0 240.0 284.0 328.0 372.0 416.0 460.0 504.0]
*     [3.0 ... 10.0]      [3.0 ... 10.0]       [224.0 276.0 328.0 380.0 432.0 484.0 536.0 588.0]
*     [4.0 ... 11.0]      [4.0 ... 11.0]       [252.0 312.0 372.0 432.0 492.0 552.0 612.0 672.0]
*     [5.0 ... 12.0]      [5.0 ... 12.0]       [280.0 348.0 416.0 484.0 552.0 620.0 688.0 756.0]
*     [6.0 ... 13.0]      [6.0 ... 13.0]       [308.0 384.0 460.0 536.0 612.0 688.0 764.0 840.0]
*     [7.0 ... 14.0]      [7.0 ... 14.0]       [336.0 420.0 504.0 588.0 672.0 756.0 840.0 924.0]
******************************************************/
#include <stdio.h>
#include <stdint.h>

void gemm(const _Float16 *feature, const _Float16 *weight, float *output) {
    __asm__ volatile(
        "vsetvli    t0, zero, e16, m1        \n\t"
        "vmv.v.i    v16, 0                   \n\t"
        "vle16.v    v2, (%[A])               \n\t"
        "vle16.v    v8, (%[B])               \n\t"
        "smt.vfwmadot   v16, v2, v8              \n\t"
        "vsetvli    t0, zero, e32, m2        \n\t"
        "vse32.v    v16, (%[C])              \n\t"

        :
        : [A] "r"(feature), [ B ] "r"(weight), [ C ] "r"(output)
        : "cc", "memory", "t0");
}

int main()
{
    printf("Test Start.\n");
    // Init the matrixA, matrixB and matrixC.
    _Float16 A[8*16] = {0.0, 1.0, 2.0,  3.0,  4.0,  5.0,  6.0,  7.0,
                        1.0, 2.0, 3.0,  4.0,  5.0,  6.0,  7.0,  8.0,
                        2.0, 3.0, 4.0,  5.0,  6.0,  7.0,  8.0,  9.0,
                        3.0, 4.0, 5.0,  6.0,  7.0,  8.0,  9.0, 10.0,
                        4.0, 5.0, 6.0,  7.0,  8.0,  9.0, 10.0, 11.0,
                        5.0, 6.0, 7.0,  8.0,  9.0, 10.0, 11.0, 12.0,
                        6.0, 7.0, 8.0,  9.0, 10.0, 11.0, 12.0, 13.0,
                        7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0};
    _Float16 B[8*16] = {0.0, 1.0, 2.0,  3.0,  4.0,  5.0,  6.0,  7.0,
                        1.0, 2.0, 3.0,  4.0,  5.0,  6.0,  7.0,  8.0,
                        2.0, 3.0, 4.0,  5.0,  6.0,  7.0,  8.0,  9.0,
                        3.0, 4.0, 5.0,  6.0,  7.0,  8.0,  9.0, 10.0,
                        4.0, 5.0, 6.0,  7.0,  8.0,  9.0, 10.0, 11.0,
                        5.0, 6.0, 7.0,  8.0,  9.0, 10.0, 11.0, 12.0,
                        6.0, 7.0, 8.0,  9.0, 10.0, 11.0, 12.0, 13.0,
                        7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0};
    float C[64] = {0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0};

    // Call the FUNCTION
    gemm(A, B, C);

    // Print the OUTPUT
    for(int32_t iter_i=0; iter_i<8; iter_i++){
        for(int32_t iter_j=0; iter_j<8; iter_j++){
            printf("%f \t", C[iter_i*8 + iter_j]);
        }
        printf(" \n");
    }
    printf("Test End.\n");
    return 0;
}

```

## 6.2 面向卷积场景的浮点滑窗矩阵乘法：`smt.vfwmadot1/2/3`

### 6.2.1 功能概述

`smt.vfwmadot1`、`smt.vfwmadot2`、`smt.vfwmadot3` 与 `smt.vfwmadot` 的计算类型相同，但在 `A` 的读取侧附加滑窗位移。

![图9：浮点滑窗矩阵乘法（`smt.vfwmadot1`）示意图。](images/ime_extension_png/fig8fwmadotslide.png)
*图 9. 在 VLEN=1024、λ=8、W=2、LMUL=1 条件下，`smt.vfwmadot1 v16, v2, v8` 的滑窗计算示意。*

### 6.2.2 指令成员

|指令|汇编格式|slide|数据类型路径|tile|控制|
|---|---|---|---|---|---|
|`smt.vfwmadot1`|`smt.vfwmadot1 vd, vs1, vs2`|1|`FP16 × FP16 → FP32`<br>`BF16 × BF16 → FP32`|`8 × 8 × 8`|`MCPM.BF16`|
|`smt.vfwmadot2`|`smt.vfwmadot2 vd, vs1, vs2`|2|`FP16 × FP16 → FP32`<br>`BF16 × BF16 → FP32`|`8 × 8 × 8`|`MCPM.BF16`|
|`smt.vfwmadot3`|`smt.vfwmadot3 vd, vs1, vs2`|3|`FP16 × FP16 → FP32`<br>`BF16 × BF16 → FP32`|`8 × 8 × 8`|`MCPM.BF16`|

### 6.2.3 程序可见语义

```c
if (LMUL != 1) {
    illegal_instruction();
}

M = N = 8; K = 8;
slide *= K;

for (p = 0; p < (2 * VLEN * LMUL / 32); p++) {
    i = (p / M) * K;
    j = (p % N) * K;
    for (q = 0; q < K; q++) {
        vd[p] = vd[p] + (fp32)vs1[i + q + slide] * (fp32)vs2[j + q];
    }
}
```

### 6.2.4 非法条件

- `LMUL != 1`；
- `Vd` 非偶数；
- `Vd/Vd+1` 与 `Vs1` / `Vs2` 重叠；
- 输入格式与 `MCPM.BF16` 控制不一致。

### 6.2.5 算术说明

- 目标累加数据类型为 FP32；
- 根据指令名中的数字 `N`，确定参与运算的 `A` 矩阵滑动 `N` 行。

### 6.2.6 与 `smt.vfwmadot` 的区别

- 计算类型相同；
- tile 形状相同；
- 唯一区别是 `A` 的读取窗口有固定 slide。

### 6.2.7 应用举例
```
/*********************** A100 示例 ************************
* MatrixA(feature, M8*K8)
*          [ 0.0  1.0  2.0  3.0  4.0  5.0  6.0  7.0]
*          [ 1.0  2.0  3.0  4.0  5.0  6.0  7.0  8.0]
*          [ 2.0  3.0  4.0  5.0  6.0  7.0  8.0  9.0]
*          [ 3.0  4.0  5.0  6.0  7.0  8.0  9.0 10.0]
*          [ 4.0  5.0  6.0  7.0  8.0  9.0 10.0 11.0]
*          [ 5.0  6.0  7.0  8.0  9.0 10.0 11.0 12.0]
*          [ 6.0  7.0  8.0  9.0 10.0 11.0 12.0 13.0]
*          [ 7.0  8.0  9.0 10.0 11.0 12.0 13.0 14.0]
*          [ 8.0  9.0 10.0 11.0 12.0 13.0 14.0 15.0]
*          [ 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0]
*          [10.0 11.0 12.0 13.0 14.0 15.0 16.0 17.0]
*          [11.0 12.0 13.0 14.0 15.0 16.0 17.0 18.0]
*          [12.0 13.0 14.0 15.0 16.0 17.0 18.0 19.0]
*          [13.0 14.0 15.0 16.0 17.0 18.0 19.0 20.0]
*          [14.0 15.0 16.0 17.0 18.0 19.0 20.0 21.0]
*          [15.0 16.0 17.0 18.0 19.0 20.0 21.0 22.0]
*
* MatrixB(weight, M8*K8)
*          [0.0  1.0  2.0  3.0  4.0  5.0  6.0  7.0]
*          [1.0  2.0  3.0  4.0  5.0  6.0  7.0  8.0]
*          [2.0  3.0  4.0  5.0  6.0  7.0  8.0  9.0]
*          [3.0  4.0  5.0  6.0  7.0  8.0  9.0 10.0]
*          [4.0  5.0  6.0  7.0  8.0  9.0 10.0 11.0]
*          [5.0  6.0  7.0  8.0  9.0 10.0 11.0 12.0]
*          [6.0  7.0  8.0  9.0 10.0 11.0 12.0 13.0]
*          [7.0  8.0  9.0 10.0 11.0 12.0 13.0 14.0]
*
*  "smt.vfwmadot     v16, v2, v8           \n\t"
*   MatrixA[8, 8]   *  MatrixBt[8, 8]   =   MatrixC[8, 8]
*     [0.0 ...  7.0]      [0.0 ...  7.0]   =   [140.0 168.0 196.0 224.0 252.0 280.0 308.0 336.0]
*     [1.0 ...  8.0]      [1.0 ...  8.0]       [168.0 204.0 240.0 276.0 312.0 348.0 384.0 420.0]
*     [2.0 ...  9.0]      [2.0 ...  9.0]       [196.0 240.0 284.0 328.0 372.0 416.0 460.0 504.0]
*     [3.0 ... 10.0]      [3.0 ... 10.0]       [224.0 276.0 328.0 380.0 432.0 484.0 536.0 588.0]
*     [4.0 ... 11.0]      [4.0 ... 11.0]       [252.0 312.0 372.0 432.0 492.0 552.0 612.0 672.0]
*     [5.0 ... 12.0]      [5.0 ... 12.0]       [280.0 348.0 416.0 484.0 552.0 620.0 688.0 756.0]
*     [6.0 ... 13.0]      [6.0 ... 13.0]       [308.0 384.0 460.0 536.0 612.0 688.0 764.0 840.0]
*     [7.0 ... 14.0]      [7.0 ... 14.0]       [336.0 420.0 504.0 588.0 672.0 756.0 840.0 924.0]
*
*  "smt.vfwmadot1    v16, v0, v8             \n\t"
*  MatrixA[8, 8]   *  MatrixB[8, 8]  + MatrixC[8, 8]  =  MatrixC[8, 8]
*     [1.0 ...  8.0]      [0.0 ...  7.0]   =   [308.0 372.0  436.0  500.0  564.0  628.0  692.0  756.0]
*     [2.0 ...  9.0]      [1.0 ...  8.0]       [364.0 444.0  524.0  604.0  684.0  764.0  844.0  924.0]
*     [3.0 ... 10.0]      [2.0 ...  9.0]       [420.0 516.0  612.0  708.0  804.0  900.0  996.0 1092.0]
*     [4.0 ... 11.0]      [3.0 ... 10.0]       [476.0 588.0  700.0  812.0  924.0 1036.0 1148.0 1260.0]
*     [5.0 ... 12.0]      [4.0 ... 11.0]       [532.0 660.0  788.0  916.0 1044.0 1172.0 1300.0 1428.0]
*     [6.0 ... 13.0]      [5.0 ... 12.0]       [588.0 732.0  876.0 1020.0 1164.0 1308.0 1452.0 1596.0]
*     [7.0 ... 14.0]      [6.0 ... 13.0]       [644.0 804.0  964.0 1124.0 1284.0 1444.0 1604.0 1764.0]
*     [8.0 ... 15.0]      [7.0 ... 14.0]       [700.0 876.0 1052.0 1228.0 1404.0 1580.0 1756.0 1932.0]
*
*  "smt.vfwmadot2     v16, v0, v8            \n\t"
* MatrixA[8, 8]    *  MatrixB[8, 8]  + MatrixC[8, 8]   =   MatrixC[8, 8]
*     [2.0 ...  9.0]      [0.0 ...  7.0]   =   [ 504.0      612.0      720.0      828.0    936.0  1044.0  1152.0  1260.0]
*     [3.0 ... 10.0]      [1.0 ...  8.0]       [ 588.0      720.0      852.0      984.0   1116.0  1248.0  1380.0  1512.0]
*     [4.0 ... 11.0]      [2.0 ...  9.0]       [ 672.0      828.0      984.0     1140.0   1296.0  1452.0  1608.0  1764.0]
*     [5.0 ... 12.0]      [3.0 ... 10.0]       [ 756.0      936.0     1116.0     1296.0   1476.0  1656.0  1836.0  2016.0]
*     [6.0 ... 13.0]      [4.0 ... 11.0]       [ 840.0     1044.0     1248.0     1452.0   1656.0  1860.0  2064.0  2268.0]
*     [7.0 ... 14.0]      [5.0 ... 12.0]       [ 924.0     1152.0     1380.0     1608.0   1836.0  2064.0  2292.0  2520.0]
*     [8.0 ... 15.0]      [6.0 ... 13.0]       [1008.0     1260.0     1512.0     1764.0   2016.0  2268.0  2520.0  2772.0]
*     [9.0 ... 16.0]      [7.0 ... 14.0]       [1092.0     1368.0     1644.0     1920.0   2196.0  2472.0  2748.0  3024.0]
******************************************************/
#include <stdio.h>
#include <stdint.h>

void conv1d(const _Float16 *feature, const _Float16 *weight, float *output) {
    __asm__ volatile(
        "vsetvli    t0, zero, e16, m1        \n\t"
        "vle16.v     v0, (%[A])              \n\t"
        "addi       %[A], %[A], 8*16         \n\t"
        "vle16.v     v1, (%[A])              \n\t"
        "addi       %[A], %[A], 8*16         \n\t"
        "vle16.v     v8, (%[B])              \n\t"
        "smt.vfwmadot     v16, v0, v8            \n\t"
        "smt.vfwmadot1    v16, v0, v8            \n\t"
        "smt.vfwmadot2    v16, v0, v8            \n\t"
        "vsetvli    t0, zero, e32, m2        \n\t"
        "vse32.v    v16, (%[C])              \n\t"
        
        : [A] "+r"(feature), [ B ] "+r"(weight), [ C ] "+r"(output)
        :
        : "cc");
}

int main()
{
    printf("Test Start.\n");
    // Init the matrixA, matrixB and matrixC.
    _Float16 A[16*8] = { 0.0,  1.0,  2.0,  3.0,  4.0,  5.0,  6.0,  7.0,
                         1.0,  2.0,  3.0,  4.0,  5.0,  6.0,  7.0,  8.0,
                         2.0,  3.0,  4.0,  5.0,  6.0,  7.0,  8.0,  9.0,
                         3.0,  4.0,  5.0,  6.0,  7.0,  8.0,  9.0, 10.0,
                         4.0,  5.0,  6.0,  7.0,  8.0,  9.0, 10.0, 11.0,
                         5.0,  6.0,  7.0,  8.0,  9.0, 10.0, 11.0, 12.0,
                         6.0,  7.0,  8.0,  9.0, 10.0, 11.0, 12.0, 13.0,
                         7.0,  8.0,  9.0, 10.0, 11.0, 12.0, 13.0, 14.0,
                         8.0,  9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0,
                         9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0,
                        10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0,
                        11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0,
                        12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0,
                        13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0,
                        14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0,
                        15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0};
    _Float16 B[8*8] = {0.0, 1.0, 2.0,  3.0,  4.0,  5.0,  6.0,  7.0,
                       1.0, 2.0, 3.0,  4.0,  5.0,  6.0,  7.0,  8.0,
                       2.0, 3.0, 4.0,  5.0,  6.0,  7.0,  8.0,  9.0,
                       3.0, 4.0, 5.0,  6.0,  7.0,  8.0,  9.0, 10.0,
                       4.0, 5.0, 6.0,  7.0,  8.0,  9.0, 10.0, 11.0,
                       5.0, 6.0, 7.0,  8.0,  9.0, 10.0, 11.0, 12.0,
                       6.0, 7.0, 8.0,  9.0, 10.0, 11.0, 12.0, 13.0,
                       7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0};
    float C[8*8] = {0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0};
    
    // Call the FUNCTION
    conv1d(A, B, C);
    
    // Print the OUTPUT
    for(int32_t iter_i=0; iter_i<8; iter_i++){
        for(int32_t iter_j=0; iter_j<8; iter_j++){
            printf("%f \t", C[iter_i*8 + iter_j]);
        }
        printf(" \n");
    }
    printf("Test End.\n");
    return 0;
}
```

# 第 7 章 数据布局变换指令

## 7.1 设计目的

除矩阵乘法类指令外，本指令集还定义了一组面向 AI 数据准备的数据布局变换指令，其主要作用包括：

- 将两个源流交织为矩阵扩展所需的输入二维 tile 布局；
- 将交织流恢复为分离布局；
- 将较宽输入缩位并交织；
- 为 Int4 等低位宽数据准备 nibble 级打包格式。

这些指令在功能上与社区 `Zvzip` 扩展具有一定相似性。`pack` 与 `unpack` 的功能见下图：

![图10：`pack` 与 `unpack` 功能示意图。](images/ime_extension_png/fig9packunpack.jpg)
*图 10. `pack` 与 `unpack` 指令对数据流交织与解交织的功能示意。*

## 7.2 指令总表

|指令|汇编格式|功能概述|
|---|---|---|
|`smt.vpack.vv`|`smt.vpack.vv vd, vs1, vs2, imm2`|交织两个源流|
|`smt.vupack.vv`|`smt.vupack.vv vd, vs1, vs2, imm2`|对交织流做解交织|
|`smt.vnpack.vv`|`smt.vnpack.vv vd, vs1, vs2, imm2`|缩位后交织|
|`smt.vnspack.vv`|`smt.vnspack.vv vd, vs1, vs2, imm2`|饱和缩位后交织|
|`smt.vnpack4.vv`|`smt.vnpack4.vv vd, vs1, vs2, imm2`|4-bit 缩位打包|
|`smt.vnspack4.vv`|`smt.vnspack4.vv vd, vs1, vs2, imm2`|4-bit 饱和缩位打包|

## 7.2.1 `imm2` 与 `pack_len` 对照

数据布局变换类指令中的 `imm2` 用于选择交织或打包粒度，但不同指令族对 `imm2` 的解释不同。

### `smt.vpack.vv` / `smt.vupack.vv`

|`imm2`|`pack_len`|说明|
|---|---|---|
|`00`|`SEW`|按当前元素宽度交织 / 解交织|
|`01`|128 bit|按 128-bit 块交织 / 解交织|
|`10`|256 bit|按 256-bit 块交织 / 解交织|
|`11`|512 bit|按 512-bit 块交织 / 解交织|

### `smt.vnpack.vv` / `smt.vnspack.vv` / `smt.vnpack4.vv` / `smt.vnspack4.vv`

|`imm2`|`pack_len`|说明|
|---|---|---|
|`00`|32 bit|按 32-bit 块缩位后交织 / 打包|
|`01`|64 bit|按 64-bit 块缩位后交织 / 打包|
|`10`|128 bit|按 128-bit 块缩位后交织 / 打包|
|`11`|256 bit|按 256-bit 块缩位后交织 / 打包|

对所有数据布局变换指令，若 `pack_len > VLEN × LMUL`，则该指令非法。

## 7.2.2 共同辅助定义

为便于描述缩位路径，本文引入以下辅助函数。

### `CLIP(x)`

`CLIP(x)` 表示**直接截断**到目标位宽，仅保留低位：

```c
CLIP_EEW(x) = x & ((1 << EEW) - 1)
```

其中 `EEW` 为目标元素位宽。

例如：

- 对 `smt.vnpack.vv` / `smt.vnspack.vv`，目标位宽为原始输入位宽的一半；
- 对 `smt.vnpack4.vv` / `smt.vnspack4.vv`，目标位宽固定为 4 bit。

### `SCLIP(x)`

`SCLIP(x)` 表示**饱和截断**到目标位宽；若 `x` 超出目标位宽可表示范围，则钳位到最小值或最大值。

对有符号目标位宽 `EEW`：

```c
SCLIP_EEW(x) =
    (x >  2^(EEW-1)-1) ?  2^(EEW-1)-1 :
    (x < -2^(EEW-1))   ? -2^(EEW-1)   :
                             x
```

若对应实现将源元素按无符号解释，则应采用无符号饱和截断规则；本文正文中的 `SCLIP()` 仅用于表达“先饱和、后缩位”的语义。

## 7.3 `smt.vpack.vv`

`smt.vpack.vv` 将 `vs1` 与 `vs2` 按指定 `pack_len` 交织写入目标：

```c
if (pack_len > VLEN * LMUL) {
    illegal_instruction();
}

switch (imm2) {
    case 0: pack_len = SEW;     break;
    case 1: pack_len = 128;     break;
    case 2: pack_len = 256;     break;
    case 3: pack_len = 512;     break;
}

for (p = 0; p < (VLEN * LMUL / pack_len); p++) {
    q = p * pack_len;

    for (i = 0; i < pack_len / SEW; i++) {
        vd[2 * p * pack_len / SEW + i] = vs1[q + i];
    }

    for (i = 0; i < pack_len / SEW; i++) {
        vd[2 * p * pack_len / SEW + pack_len / SEW + i] = vs2[q + i];
    }
}
```

### 7.3.1 应用举例

![图11：`vpack` 指令示例的数据排布变换效果。](images/ime_extension_png/fig10packexample.jpg)
*图 11. 后文的 `vpack` 指令片段可将输入数据重排为图示布局。*

```
vsetvli  t0, x0, e8, m1, tu, mu
vle8.v  v0, (a0)
add     a0, a0, matrix_row_stride
vle8.v  v1, (a0)
add     a0, a0, matrix_row_stride
vle8.v  v2, (a0)
add     a0, a0, matrix_row_stride
vle8.v  v3, (a0)
add     a0, a0, matrix_row_stride
vsetvli  t0, x0, e64, m1, tu, mu
smt.vpack.vv v8, v0, v1, 0             // abab
smt.vpack.vv v10, v2, v3, 0            // cdcd
smt.vpack.vv v4, v8, v10, 0            // abcd
smt.vpack.vv v6, v9, v11, 0            // abcd
```

## 7.4 `smt.vupack.vv`

`smt.vupack.vv` 对交织布局进行逆变换，将流拆分回扩展后的目标布局：

```c
if (pack_len > VLEN * LMUL) {
    illegal_instruction();
}

switch (imm2) {
    case 0: pack_len = SEW;     break;
    case 1: pack_len = 128;     break;
    case 2: pack_len = 256;     break;
    case 3: pack_len = 512;     break;
}

for (p = 0; p < (VLEN * LMUL / (pack_len * 2)); p++) {
    q = 2 * p * pack_len;

    for (i = 0; i < pack_len / SEW; i++) {
        vd[p * pack_len + i] = vs1[q / SEW + i];
        vd+1[p * pack_len + i] = vs1[q / SEW + pack_len / SEW + i];
        vd[(VLEN/SEW)/2 + p * pack_len + i] = vs2[q / SEW + i];
        vd+1[(VLEN/SEW)/2 + p * pack_len + i] = vs2[q / SEW + pack_len / SEW + i];
    }
}
```

## 7.5 `smt.vnpack.vv` 与 `smt.vnspack.vv`

这两条指令均将输入元素缩位到原位宽的一半，然后按 `pack_len` 交织写入目标。

### 7.5.1 `smt.vnpack.vv`

`smt.vnpack.vv` 先截取输入低半位宽，再执行交织：

```c
if (pack_len > VLEN * LMUL) {
    illegal_instruction();
}

switch (imm2) {
    case 0: pack_len = 32;      break;
    case 1: pack_len = 64;      break;
    case 2: pack_len = 128;     break;
    case 3: pack_len = 256;     break;
}

SEW = 2 * SEW;

for (p = 0; p < (VLEN * LMUL / pack_len); p++) {
    q = p * pack_len;
    for (i = 0; i < pack_len / SEW; i++) {
        vd[p * pack_len / (SEW/2) + i] = CLIP(vs1[q + i]);
    }
    for (i = 0; i < pack_len / SEW; i++) {
        vd[p * pack_len / (SEW/2) + pack_len / SEW + i] = CLIP(vs2[q + i]);
    }
}
```

### 7.5.2 `smt.vnspack.vv`

`smt.vnspack.vv` 在交织前先做饱和缩位：

```c
if (pack_len > VLEN * LMUL) {
    illegal_instruction();
}

switch (imm2) {
    case 0: pack_len = 32;      break;
    case 1: pack_len = 64;      break;
    case 2: pack_len = 128;     break;
    case 3: pack_len = 256;     break;
}

SEW = 2 * SEW;

for (p = 0; p < (VLEN * LMUL / pack_len); p++) {
    q = p * pack_len;
    for (i = 0; i < pack_len / SEW; i++) {
        vd[p * pack_len / (SEW/2) + i] = SCLIP(vs1[q + i]);
    }
    for (i = 0; i < pack_len / SEW; i++) {
        vd[p * pack_len / (SEW/2) + pack_len / SEW + i] = SCLIP(vs2[q + i]);
    }
}
```

## 7.6 `smt.vnpack4.vv` 与 `smt.vnspack4.vv`

- `smt.vnpack4.vv`：面向 4-bit 输出的 nibble 缩位打包；
- `smt.vnspack4.vv`：面向 4-bit 输出的 nibble 饱和缩位打包。

它们可理解为 `smt.vnpack.vv` / `smt.vnspack.vv` 的半字节对应形式，用于 Int4 等低位宽数据准备。

### 7.6.1 `smt.vnpack4.vv`

`smt.vnpack4.vv` 先将输入元素截断到 4 bit，再按 `pack_len` 为粒度交织，并以每两个 4-bit 元素合成一个字节的方式写入目标。

```c
if (pack_len > VLEN * LMUL) {
    illegal_instruction();
}

switch (imm2) {
    case 0: pack_len = 32;      break;
    case 1: pack_len = 64;      break;
    case 2: pack_len = 128;     break;
    case 3: pack_len = 256;     break;
}

for (p = 0; p < (VLEN * LMUL / pack_len); p++) {
    q = p * pack_len;
    out = 0;

    for (i = 0; i < pack_len / 8; i++) {
        lo = CLIP_4(vs1[q / SEW + 2*i + 0]);
        hi = CLIP_4(vs1[q / SEW + 2*i + 1]);
        vd[out++] = lo | (hi << 4);
    }

    for (i = 0; i < pack_len / 8; i++) {
        lo = CLIP_4(vs2[q / SEW + 2*i + 0]);
        hi = CLIP_4(vs2[q / SEW + 2*i + 1]);
        vd[out++] = lo | (hi << 4);
    }
}
```

### 7.6.2 `smt.vnspack4.vv`

`smt.vnspack4.vv` 与 `smt.vnpack4.vv` 的流程相同，但在写入前对每个源元素先执行 4-bit 饱和缩位：

```c
if (pack_len > VLEN * LMUL) {
    illegal_instruction();
}

switch (imm2) {
    case 0: pack_len = 32;      break;
    case 1: pack_len = 64;      break;
    case 2: pack_len = 128;     break;
    case 3: pack_len = 256;     break;
}

for (p = 0; p < (VLEN * LMUL / pack_len); p++) {
    q = p * pack_len;
    out = 0;

    for (i = 0; i < pack_len / 8; i++) {
        lo = SCLIP_4(vs1[q / SEW + 2*i + 0]);
        hi = SCLIP_4(vs1[q / SEW + 2*i + 1]);
        vd[out++] = lo | (hi << 4);
    }

    for (i = 0; i < pack_len / 8; i++) {
        lo = SCLIP_4(vs2[q / SEW + 2*i + 0]);
        hi = SCLIP_4(vs2[q / SEW + 2*i + 1]);
        vd[out++] = lo | (hi << 4);
    }
}
```

### 7.6.3 补充说明

- 上述 `CLIP_4()` 与 `SCLIP_4()` 分别表示针对 4-bit 目标位宽的直接截断与饱和截断；
- `smt.vnpack4.vv` / `smt.vnspack4.vv` 的 nibble 顺序与字节内高低半字节定义，系依据现有实现资料整理；若具体实现另有固定约定，应以实现定义为准；
- 若实现对字节内 nibble 排布另有固定约定，应以实现原始定义为准。

## 7.7 数据布局变换指令的使用定位

这些指令虽然不直接执行矩阵乘法，但在矩阵扩展软件流程中很重要，因为它们常用于：

- 准备 `Vs2` 所需的点积友好布局；
- 将宽位宽中间结果压缩回低位宽表示；
- 构造 Int4 / 稀疏输入所需的紧凑打包格式。

# 第 8 章 主要指令编码摘要

本章对 SpacemiT 实现资料中的编码信息进行了重组，以便查阅；若位级细节与原始定义存在冲突，应以对应实现的原始定义为准。

## 8.1 整数矩阵乘法指令（基础路径）：`smt.vmadot*`

寄存器约束：

- `Vs1`、`Vs2`：任意编号 `0`～`31` 的向量寄存器；
- `Vd`：任意编号 `0`～`30` 且为偶数编号的向量寄存器。

- `funct3[14:12]` 选择 `signedness`：
  - `000`：`smt.vmadotu`
  - `001`：`smt.vmadotus`
  - `010`：`smt.vmadotsu`
  - `011`：`smt.vmadot`
- `DT[30:29]` 选择数据类型：
  - `10`：Int4
  - `11`：Int8

其余编码：保留。

正式编码如下：

|助记符|`[31]`|`[30:29]`|`[28:26]`|`[25]`|`[24:20]`|`[19:15]`|`[14:12]`|`[11:7]`|`[6:0]`|
|---|---|---|---|---|---|---|---|---|---|
|`smt.vmadotu`|`1`|`DT`|`000`|`1`|`vs2`|`vs1`|`000`|`{vd[4:1],0}`|`0101011`|
|`smt.vmadotus`|`1`|`DT`|`000`|`1`|`vs2`|`vs1`|`001`|`{vd[4:1],0}`|`0101011`|
|`smt.vmadotsu`|`1`|`DT`|`000`|`1`|`vs2`|`vs1`|`010`|`{vd[4:1],0}`|`0101011`|
|`smt.vmadot`|`1`|`DT`|`000`|`1`|`vs2`|`vs1`|`011`|`{vd[4:1],0}`|`0101011`|

其中：

- `DT[30:29] = 10/11` 分别表示 Int4 / Int8；
- `Vd` 仅限使用 0–30 范围内的偶数向量寄存器，因此其最低有效位恒为 0，在编码中表示为 `{vd[4:1],0}`。

## 8.2 面向卷积场景的整数滑窗矩阵乘法：`smt.vmadot1/2/3*`

寄存器约束：

- `Vs1`：任意编号 `0`～`30` 且为偶数编号的向量寄存器；
- `Vs2`：任意编号 `0`～`31` 的向量寄存器；
- `Vd`：任意编号 `0`～`30` 且为偶数编号的向量寄存器。

- `funct2[13:12]` 选择 `signedness`：
  - `00`：U × U
  - `01`：U × S
  - `10`：S × U
  - `11`：S × S
- `slide[15:14]` 选择滑窗位移：
  - `00`：slide 1
  - `01`：slide 2
  - `10`：slide 3
  - `11`：保留

- `DT[30:29]` 选择数据类型字段（实现定义字段名；为避免与社区语义混淆，可在正文中称为“数据类型字段”）：
    - `11`：Int8
    - 其他：保留

正式编码如下：

|助记符|`[31]`|`[30:29]`|`[28:26]`|`[25]`|`[24:20]`|`[19:15]`|`[14:12]`|`[11:7]`|`[6:0]`|
|---|---|---|---|---|---|---|---|---|---|
|`smt.vmadot1u`|`1`|`DT`|`001`|`1`|`vs2`|`{vs1[4:1],0}`|`000`|`{vd[4:1],0}`|`0101011`|
|`smt.vmadot1us`|`1`|`DT`|`001`|`1`|`vs2`|`{vs1[4:1],0}`|`001`|`{vd[4:1],0}`|`0101011`|
|`smt.vmadot1su`|`1`|`DT`|`001`|`1`|`vs2`|`{vs1[4:1],0}`|`010`|`{vd[4:1],0}`|`0101011`|
|`smt.vmadot1`|`1`|`DT`|`001`|`1`|`vs2`|`{vs1[4:1],0}`|`011`|`{vd[4:1],0}`|`0101011`|
|`smt.vmadot2u`|`1`|`DT`|`001`|`1`|`vs2`|`{vs1[4:1],0}`|`100`|`{vd[4:1],0}`|`0101011`|
|`smt.vmadot2us`|`1`|`DT`|`001`|`1`|`vs2`|`{vs1[4:1],0}`|`101`|`{vd[4:1],0}`|`0101011`|
|`smt.vmadot2su`|`1`|`DT`|`001`|`1`|`vs2`|`{vs1[4:1],0}`|`110`|`{vd[4:1],0}`|`0101011`|
|`smt.vmadot2`|`1`|`DT`|`001`|`1`|`vs2`|`{vs1[4:1],0}`|`111`|`{vd[4:1],0}`|`0101011`|
|`smt.vmadot3u`|`1`|`DT`|`001`|`1`|`vs2`|`{vs1[4:1],1}`|`000`|`{vd[4:1],0}`|`0101011`|
|`smt.vmadot3us`|`1`|`DT`|`001`|`1`|`vs2`|`{vs1[4:1],1}`|`001`|`{vd[4:1],0}`|`0101011`|
|`smt.vmadot3su`|`1`|`DT`|`001`|`1`|`vs2`|`{vs1[4:1],1}`|`010`|`{vd[4:1],0}`|`0101011`|
|`smt.vmadot3`|`1`|`DT`|`001`|`1`|`vs2`|`{vs1[4:1],1}`|`011`|`{vd[4:1],0}`|`0101011`|

其中：

- `DT[30:29]` 当前仅定义 `11`，即 Int8；
- `slide[15:14]` 由位 `[15]` 与 `[14:12]` 中的高位共同编码，其中 `[15]` 复用了 `Vs1` 因偶数寄存器约束而省出的最低位编码空间；
- 由于 `Vs1` 和 `Vd` 均被约束为偶数编号寄存器，其最低有效位恒为 0，因此在上表中分别表示为 {vs1[4:1],0} 和 {vd[4:1],0}。特别地，`smt.vmadot3u` 指令是一个例外：该指令中 `Vs1` 的最低有效位编码为 1。

## 8.3 4:2 结构化稀疏整数矩阵乘法：`smt.vmadot.sp*`

寄存器约束：

- `Vs1`：任意编号 `0`～`30` 且为偶数编号的向量寄存器；
- `Vs2`：任意编号 `0`～`31` 的向量寄存器；
- `Vd`：任意编号 `0`～`30` 且为偶数编号的向量寄存器。

- `imm2`（位 `[15]` 与 `[7]`）选择掩码分段；
- `funct3[14:12]` 选择 `signedness`；
- `vmask[25]` 选择 `V0` 或 `V1`；
- `DT[30:29]` 选择 Int4 / Int8。

`imm2` 对应的有效掩码分段如下：

- Int4：
    - `00` ：`[511:0]`
    - `01` ：`[1023:512]`
- Int8：
    - `00`：`[255:0]`
    - `01`：`[511:256]`
    - `10`：`[767:512]`
    - `11`：`[1023:768]`

其余编码：保留。

正式编码如下：

|助记符|`[31]`|`[30:29]`|`[28:26]`|`[25]`|`[24:20]`|`[19:16]`|`[15]`|`[14:12]`|`[11:8]`|`[7]`|`[6:0]`|
|---|---|---|---|---|---|---|---|---|---|---|---|
|`smt.vmadotu.sp`|`1`|`DT`|`010`|`v`|`vs2`|`vs1[4:1]`|`imm2[1]`|`000`|`vd[4:1]`|`imm2[0]`|`0101011`|
|`smt.vmadotus.sp`|`1`|`DT`|`010`|`v`|`vs2`|`vs1[4:1]`|`imm2[1]`|`001`|`vd[4:1]`|`imm2[0]`|`0101011`|
|`smt.vmadotsu.sp`|`1`|`DT`|`010`|`v`|`vs2`|`vs1[4:1]`|`imm2[1]`|`010`|`vd[4:1]`|`imm2[0]`|`0101011`|
|`smt.vmadot.sp`|`1`|`DT`|`010`|`v`|`vs2`|`vs1[4:1]`|`imm2[1]`|`011`|`vd[4:1]`|`imm2[0]`|`0101011`|

其中：

- `v` 表示 `vmask[25]`，`0/1` 分别对应选择 `V0` / `V1`；
- `DT[30:29] = 10/11` 分别表示 Int4 / Int8；
- `imm2` 由离散位 `[15]` 与 `[7]` 共同组成，这两位分别复用了 `Vs1` 与 `Vd` 因偶数寄存器约束而省出的最低位编码空间；
- 由于 `Vs1` 和 `Vd` 受偶数寄存器约束，其 `bit 0` 一定为 0，故表中将 `Vs1` 与 `Vd` 字段分别写为 `{vs1[4:1],0}` 和 `{vd[4:1],0}`。

## 8.4 面向分块量化的整数矩阵乘法：`smt.vmadot.hp*`

寄存器约束：

- `Vs1`、`Vs2`、`Vd`：任意编号 `0`～`31` 的向量寄存器。

- `imm3[14:12]` 选择 scale 参数组；
- `vscale[25]` 选择 `V0` 或 `V1`；
- `funct3[28:26]` 选择 `signedness`；
- `DT[30:29]` 选择 Int4 / Int8。

`imm3` 分组定义如下：

- `000`：`[127:0]`，group-0
- `001`：`[255:128]`，group-1
- `010`：`[383:256]`，group-2
- `011`：`[511:384]`，group-3
- `100`：`[639:512]`，group-4
- `101`：`[767:640]`，group-5
- `110`：`[895:768]`，group-6
- `111`：`[1023:896]`，group-7

对应 `funct3[28:26]`：

- `011`：`smt.vmadotu.hp`
- `110`：`smt.vmadotus.hp`
- `101`：`smt.vmadotsu.hp`
- `100`：`smt.vmadot.hp`
- 其他：保留

正式编码如下：

|助记符|`[31]`|`[30:29]`|`[28:26]`|`[25]`|`[24:20]`|`[19:15]`|`[14:12]`|`[11:7]`|`[6:0]`|
|---|---|---|---|---|---|---|---|---|---|
|`smt.vmadotu.hp`|`1`|`DT`|`011`|`vscale`|`vs2`|`vs1`|`imm3`|`vd`|`0101011`|
|`smt.vmadotus.hp`|`1`|`DT`|`110`|`vscale`|`vs2`|`vs1`|`imm3`|`vd`|`0101011`|
|`smt.vmadotsu.hp`|`1`|`DT`|`101`|`vscale`|`vs2`|`vs1`|`imm3`|`vd`|`0101011`|
|`smt.vmadot.hp`|`1`|`DT`|`100`|`vscale`|`vs2`|`vs1`|`imm3`|`vd`|`0101011`|

其中：

- `vscale[25] = 0/1` 分别对应选择 `V0` / `V1`；
- `DT[30:29] = 10/11` 分别表示 Int4 / Int8；
- `imm3` 直接编码在独立字段 `[14:12]` 中，不复用因偶数寄存器约束而省出的最低位编码空间。

## 8.5 浮点类

- `smt.vfwmadot`：`Vs1`、`Vs2` 可为任意编号 `0`～`31` 的向量寄存器，`Vd` 为任意编号 `0`～`30` 且为偶数编号的向量寄存器；
- `smt.vfwmadot1/2/3`：`Vs2` 可为任意编号 `0`～`31` 的向量寄存器，`Vs1`和`Vd` 为任意编号 `0`～`30` 且为偶数编号的向量寄存器；
- `smt.vfwmadot1/2/3` 通过 `funct3[14:12]` 直接区分：`101`→`smt.vfwmadot1`，`110`→`smt.vfwmadot2`，`111`→`smt.vfwmadot3`；
- `smt.vfwmadot` 与 `smt.vfwmadot1/2/3` 的 FP16 / BF16 格式由 `MCPM.BF16` 控制；
- 本指令集不定义同一条浮点矩阵指令中的混合 FP16 / BF16 输入编码。

### 8.5.1 `smt.vfwmadot`

|助记符|`[31:25]`|`[24:20]`|`[19:15]`|`[14:12]`|`[11:7]`|`[6:0]`|
|---|---|---|---|---|---|---|
|`smt.vfwmadot`|`1001111`|`vs2`|`vs1`|`100`|`{vd[4:1],0}`|`0101011`|

其中：

- `[14:12] = 100` 对应 `smt.vfwmadot`；
- `Vd` 受偶数寄存器约束，其 `bit 0` 一定为 0，故表中将 `Vd` 字段写为 `{vd[4:1],0}`。

### 8.5.2 `smt.vfwmadot1/2/3`

|助记符|`[31:25]`|`[24:20]`|`[19:15]`|`[14:12]`|`[11:7]`|`[6:0]`|
|---|---|---|---|---|---|---|
|`smt.vfwmadot1`|`1001111`|`vs2`|`{vs1[4:1],0}`|`101`|`{vd[4:1],0}`|`0101011`|
|`smt.vfwmadot2`|`1001111`|`vs2`|`{vs1[4:1],0}`|`110`|`{vd[4:1],0}`|`0101011`|
|`smt.vfwmadot3`|`1001111`|`vs2`|`{vs1[4:1],0}`|`111`|`{vd[4:1],0}`|`0101011`|

其中：

- 低位功能字段 `[14:12]` 分别为 `101`、`110`、`111`，对应 slide 1、2、3；
- `Vd` 受偶数寄存器约束，其 `bit 0` 一定为 0，故表中将 `Vd` 字段写为 `{vd[4:1],0}`。

## 8.6 数据布局变换指令编码说明

### 8.6.1 `smt.vpack.vv` / `smt.vupack.vv`

寄存器约束：

- `Vs1`、`Vs2`：任意编号 `0`～`31` 的向量寄存器；
- `Vd`：任意编号 `0`～`30` 且为偶数编号的向量寄存器。

`imm2[13:12]` 指定数据交织粒度：

- `00`：按 `SEW` 粒度交织数据
- `01`：按 128-bit 粒度交织数据
- `10`：按 256-bit 粒度交织数据
- `11`：按 512-bit 粒度交织数据

正式编码如下：

|助记符|`[31:26]`|`[25]`|`[24:20]`|`[19:15]`|`[14]`|`[13:12]`|`[11:7]`|`[6:0]`|
|---|---|---|---|---|---|---|---|---|
|`smt.vpack.vv`|`011001`|`1`|`vs2`|`vs1`|`0`|`imm2`|`{vd[4:1],0}`|`0101011`|
|`smt.vupack.vv`|`011001`|`1`|`vs2`|`vs1`|`1`|`imm2`|`{vd[4:1],0}`|`0101011`|

其中：

- `[14]` 区分 `smt.vpack.vv` 与 `smt.vupack.vv`；
- `[13:12]` 为数据交织粒度选择字段；
- `imm2` 直接编码在字段 `[13:12]` 中，不复用因偶数寄存器约束而省出的最低位编码空间；
- `Vd` 受偶数寄存器约束，其 `bit 0` 一定为 0，故表中将 `Vd` 字段写为 `{vd[4:1],0}`。

### 8.6.2 `smt.vnpack.vv` / `smt.vnspack.vv` / `smt.vnpack4.vv` / `smt.vnspack4.vv`

寄存器约束：

- `Vs1`、`Vs2`、`Vd`：任意编号 `0`～`31` 的向量寄存器。

`imm2[13:12]` 指定数据交织粒度：

- `00`：按 32-bit 粒度交织数据
- `01`：按 64-bit 粒度交织数据
- `10`：按 128-bit 粒度交织数据
- `11`：按 256-bit 粒度交织数据

正式编码如下：

|助记符|`[31:26]`|`[25]`|`[24:20]`|`[19:15]`|`[14]`|`[13:12]`|`[11:7]`|`[6:0]`|
|---|---|---|---|---|---|---|---|---|
|`smt.vnpack.vv`|`011000`|`1`|`vs2`|`vs1`|`0`|`imm2`|`vd`|`0101011`|
|`smt.vnspack.vv`|`011000`|`1`|`vs2`|`vs1`|`1`|`imm2`|`vd`|`0101011`|
|`smt.vnpack4.vv`|`010000`|`1`|`vs2`|`vs1`|`0`|`imm2`|`vd`|`0101011`|
|`smt.vnspack4.vv`|`010000`|`1`|`vs2`|`vs1`|`1`|`imm2`|`vd`|`0101011`|

其中：

- `[14]` 区分普通缩位与带饱和缩位路径；
- `[13:12]` 为数据交织粒度选择字段；
- `imm2` 直接编码在字段 `[13:12]` 中，且该类指令的寄存器字段均按常规编码，不涉及偶数寄存器最低位编码空间复用。

# 附录 A. tile 与子扩展速查表

## A.1 tile 速查表

|实现|子扩展|输入|输出|`LMUL=1` tile|
|---|---|---|---|---|
|A60|`Xsmti8i32mm`：整数矩阵乘法指令|Int8|Int32|`4 × 8 × 4`|
|A60|`Xsmti8i32mm_slide`：面向卷积场景的整数滑窗矩阵乘法|Int8|Int32|`4 × 8 × 4`|
|A100|`Xsmti8i32mm`：整数矩阵乘法指令|Int8|Int32|`8 × 16 × 8`|
|A100|`Xsmti4i32mm`：整数矩阵乘法指令|Int4|Int32|`8 × 32 × 8`|
|A100|`Xsmti8i32mm_slide`：面向卷积场景的整数滑窗矩阵乘法|Int8|Int32|`8 × 16 × 8`|
|A100|`Xsmti8i32mm_42sp`：4:2 结构化稀疏整数矩阵乘法|Int8|Int32|`8 × 32 × 8`|
|A100|`Xsmti4i32mm_42sp`：4:2 结构化稀疏整数矩阵乘法|Int4|Int32|`8 × 64 × 8`|
|A100|`Xsmti8*16mm_scl16f`：面向分块量化的整数矩阵乘法指令|Int8 + scale|FP16 / BF16|`8 × 16 × 8`|
|A100|`Xsmti4*16mm_scl16f`：面向分块量化的整数矩阵乘法指令|Int4 + scale|FP16 / BF16|`8 × 32 × 8`|
|A100|`Xsmt*16fp32mm`：浮点矩阵乘法指令|FP16 / BF16|FP32|`8 × 8 × 8`|
|A100|`Xsmt*16fp32mm_slide`：面向卷积场景的浮点滑窗矩阵乘法|FP16 / BF16|FP32|`8 × 8 × 8`|

# 附录 B. 工具链实现

## B.1 指令前缀

SpacemiT 的 Vendor 前缀为 [SMT](https://github.com/riscv-non-isa/riscv-toolchain-conventions/blob/main/src/toolchain-conventions.adoc#list-of-vendor-prefixes)。在开源工具链实现中，上述所有指令均需添加 `smt.` 前缀。

## B.2 扩展名

为便于与 Zvvm 等标准扩展进行对比，本文档将相关指令划分为多个细粒度扩展。考虑到 Zvvm 扩展规范尚未最终定稿，当前工具链实现对扩展名进行了简化：A60 所支持的所有扩展统称为 `Xsmtvdot` 扩展，A100 所支持的所有扩展统称为 `Xsmtvdotii` 扩展。
