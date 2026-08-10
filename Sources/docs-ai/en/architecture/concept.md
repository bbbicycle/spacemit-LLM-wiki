sidebar_position: 1

# 4.1 Design Philosophy

## 4.1.1 Overview

To accelerate AI workloads, many chip vendors have introduced dedicated processor architectures such as GPGPUs, NPUs, and TPUs. When running scheduling logic and application code, these accelerators usually rely on a host CPU to work together, as shown below. As a result, systems often need complex heterogeneous scheduling mechanisms to handle data movement and synchronization between the CPU and the accelerator (XPU).

![architect](./images/architect.webp)

To make AI computing more general-purpose and easier to use, SpacemiT builds on its in-house CPU core design and takes a different approach. Based on standard RISC-V cores, Tensor Cores are integrated directly into the CPU. The RISC-V instruction set is used as a unified software–hardware interface to drive Scalar, Vector, and Matrix AI computing.

With this design, both regular software and AI models can run on the same RISC-V AI core. Standard program control flow enables data exchange and event coordination between software logic and AI computation, allowing the entire AI application to run end to end on a single architecture.

We call this approach—using the RISC-V instruction set as a unified interface to combine Scalar, Vector, and Matrix AI computing—**homogeneous fusion technology**. A CPU that includes this capability is referred to as an **AI CP**U, also known as an **Intelligent Computing Core**.

The **AI CPU** keeps the familiar CPU programming model. Developers can use standard Linux threads to drive AI computation, without dealing with heterogeneous schedulers or complex driver management. Because it is based on **RISC-V**, it integrates naturally with open-source ecosystems and existing software workflows. In addition, the **AI CPU** supports both parallel computation and control logic, making it well suited for MoE (Mixture of Experts) model inference.

In AI workloads, all three types of computing are used:
- Scalar computing is provided by the **RISC-V** standard instruction set
- Vector computing is provided by the **RISC-V** Vector 1.0 instruction set
- Matrix AI computing is provided by the **RISC-V** [Matrix Extension Instruction Set](./instruction.md)

## 4.1.2 Architectural Practice

We have released the first-generation chip featuring **AI CPUs**, named **K1**. It includes four general-purpose CPU cores (**X60**) and four intelligent computing cores (**A60**). In the **A60** core, the RISC-V Vector width is 256 bits. The theoretical matrix and vector performance is shown below; the performance calculation method can be found in [Matrix Extension Instruction Set](./instruction.md).

Matrix performance:
- 0.5 TOPS/Core (INT8)
- 2 TOPS/Cluster (INT8)

Vector performance:
- 0.128 TOPS/Core (INT8), 0.5 TOPS/Cluster (INT8)
- 0.064 TOPS/Core (FP16), 0.25 TOPS/Cluster (FP16)
- 0.032 TOPS/Core (FP32)

Based on the open-source project [cpufp](https://github.com/pigirons/cpufp), we evaluated the **A60** core in the K1 **AI CPU**. The measured results are shown below:

```
$ ./cpufp --thread_pool=[0]
Number Threads: 1
Thread Pool Binding: 0
---------------------------------------------------------------
| Instruction Set | Core Computation       | Peak Performance |
| ime             | vmadot(s32,s8,s8)      | 511.53 GOPS      |
| ime             | vmadotu(u32,u8,u8)     | 511.5 GOPS       |
| ime             | vmadotus(s32,u8,s8)    | 511.53 GOPS      |
| ime             | vmadotsu(s32,s8,u8)    | 511.51 GOPS      |
| ime             | vmadotslide(s32,s8,s8) | 511.51 GOPS      |
| vector          | vfmacc.vf(f16,f16,f16) | 66.722 GFLOPS    |
| vector          | vfmacc.vv(f16,f16,f16) | 63.936 GFLOPS    |
| vector          | vfmacc.vf(f32,f32,f32) | 33.36 GFLOPS     |
| vector          | vfmacc.vv(f32,f32,f32) | 31.968 GFLOPS    |
| vector          | vfmacc.vf(f64,f64,f64) | 16.679 GFLOPS    |
| vector          | vfmacc.vv(f64,f64,f64) | 15.985 GFLOPS    |
---------------------------------------------------------------
For cluster 0(with ime extension), 4 cores:
$ ./cpufp --thread_pool=[0-3]
Number Threads: 4
Thread Pool Binding: 0 1 2 3
---------------------------------------------------------------
| Instruction Set | Core Computation       | Peak Performance |
| ime             | vmadot(s32,s8,s8)      | 2.046 TOPS       |
| ime             | vmadotu(u32,u8,u8)     | 2.0462 TOPS      |
| ime             | vmadotus(s32,u8,s8)    | 2.0461 TOPS      |
| ime             | vmadotsu(s32,s8,u8)    | 2.0462 TOPS      |
| ime             | vmadotslide(s32,s8,s8) | 2.0461 TOPS      |
| vector          | vfmacc.vf(f16,f16,f16) | 266.88 GFLOPS    |
| vector          | vfmacc.vv(f16,f16,f16) | 255.75 GFLOPS    |
| vector          | vfmacc.vf(f32,f32,f32) | 133.43 GFLOPS    |
| vector          | vfmacc.vv(f32,f32,f32) | 127.85 GFLOPS    |
| vector          | vfmacc.vf(f64,f64,f64) | 66.709 GFLOPS    |
| vector          | vfmacc.vv(f64,f64,f64) | 63.935 GFLOPS    |
---------------------------------------------------------------
For 2 clusters, 8 cores:
$ ./cpufp --thread_pool=[0-7]
Number Threads: 8
Thread Pool Binding: 0 1 2 3 4 5 6 7
---------------------------------------------------------------
| Instruction Set | Core Computation       | Peak Performance |
| vector          | vfmacc.vf(f16,f16,f16) | 533.65 GFLOPS    |
| vector          | vfmacc.vv(f16,f16,f16) | 511.45 GFLOPS    |
| vector          | vfmacc.vf(f32,f32,f32) | 266.89 GFLOPS    |
| vector          | vfmacc.vv(f32,f32,f32) | 255.75 GFLOPS    |
| vector          | vfmacc.vf(f64,f64,f64) | 133.42 GFLOPS    |
| vector          | vfmacc.vv(f64,f64,f64) | 127.86 GFLOPS    |
---------------------------------------------------------------
```