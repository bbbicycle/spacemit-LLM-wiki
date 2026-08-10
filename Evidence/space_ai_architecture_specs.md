---
type: evidence
title: "SpacemiT AI CPU (A60) 智算核架构与 IME 指令算力规格"
domain: edge_ai_robotics
target_audience: [AI算法工程师, 芯片架构师, 嵌入式开发]
status: needs_review
created: 2026-08-10
updated: 2026-08-10
aliases: [space_ai_architecture_specs, A60 AI CPU Specs, IME Instruction Specs]
---

# SpacemiT AI CPU (A60) 智算核架构与 IME 指令算力规格

> [!TIP]
> **💡 工程师导读与排坑焦点**：记录 SpacemiT A60 智算核“同构融合”架构参数、IME 矩阵扩展单元规格及 `cpufp` 实测算力指标。
> **目标读者**：`AI算法工程师 / 芯片架构师 / 嵌入式开发` | **技术领域**：`edge_ai_robotics`

本文档记录 SpacemiT K1 / K3 芯片中 **AI CPU（A60 智算核）** 的同构融合硬件架构、IME (Integrated Matrix Extension) 矩阵扩展指令形状及实测峰值算力参数。

---

## 1. AI CPU (A60) 同构融合架构规格

| 架构属性 | 物理参数与设计规格 | 优势与技术特性 |
| :--- | :--- | :--- |
| **处理器类型** | **AI CPU (智算核)** / RISC-V A60 核心 | 同构融合 CPU 与 TensorCore，无需复杂异构驱动 |
| **矢量总线宽度** | 256-bit RISC-V Vector 1.0 (RVV 1.0) | 提供 2 倍于传统 NEON 的向量并行计算位宽 |
| **Matrix 矩阵形状** | `4 x 8 x 4` 硬件矩阵乘加计算单元 | 输入/输出复用 Vector 寄存器（IME 架构路线） |
| **紧耦合存储器** | 512 KB 专用加速 TCM (Tight-Coupled Memory) | 零 DMA 延时，解决大模型矩阵计算外存带宽瓶颈 |
| **工作主频** | 2.0 GHz (K1 默认频率) | 单核提供 0.5 TOPS (Int8) 硬件矩阵算力 |

---

## 2. cpufp 峰值算力实测数据矩阵 (K1 A60 4-Core Cluster0)

基于开源工具 `cpufp` 在 K1 平台上的单核与 Cluster 0 多核实测表现：

### 2.1 IME 矩阵算力 (Matrix AI Core)

| 指令/算子名称 | 输入/输出数据格式 | 单核实测性能 (1-Core) | Cluster 0 (4-Core) 实测性能 |
| :--- | :--- | :--- | :--- |
| `vmadot` | s32 $\leftarrow$ s8 $\times$ s8 | **511.53 GOPS** | **2.046 TOPS** |
| `vmadotu` | u32 $\leftarrow$ u8 $\times$ u8 | **511.50 GOPS** | **2.0462 TOPS** |
| `vmadotus` | s32 $\leftarrow$ u8 $\times$ s8 | **511.53 GOPS** | **2.0461 TOPS** |
| `vmadotslide` | s32 $\leftarrow$ s8 $\times$ s8 (滑动窗口) | **511.51 GOPS** | **2.0461 TOPS** |

### 2.2 Vector 矢量算力 (RVV 1.0 Vector Core)

| 向量指令与精细度 | 1-Core 性能 | 4-Core Cluster 性能 | 全局 8-Core 性能 |
| :--- | :--- | :--- | :--- |
| `vfmacc.vf` (FP16 标乘矢) | 66.72 GFLOPS | 266.88 GFLOPS | **533.65 GFLOPS** |
| `vfmacc.vv` (FP16 矢乘矢) | 63.93 GFLOPS | 255.75 GFLOPS | **511.45 GFLOPS** |
| `vfmacc.vf` (FP32 标乘矢) | 33.36 GFLOPS | 133.43 GFLOPS | **266.89 GFLOPS** |
| `vfmacc.vv` (FP32 矢乘矢) | 31.96 GFLOPS | 127.85 GFLOPS | **255.75 GFLOPS** |

---

## 3. RISC-V 矩阵扩展三大路线对比

* **IME (SpacemiT 采用路线)**：矩阵计算输入与输出**完全复用 Vector 向量寄存器**，编译模型简易、硬件开销小、与编译器原生结合极佳。
* **VME 路线**：输入复用 Vector 寄存器，输出使用专用矩阵扩展寄存器。
* **AME 路线**：输入与输出均使用专用独立矩阵寄存器。
