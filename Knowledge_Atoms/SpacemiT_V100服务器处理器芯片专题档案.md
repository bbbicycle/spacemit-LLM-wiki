---
type: knowledge_atom
title: "SpacemiT V100 服务器处理器芯片专题档案"
status: "needs_review"
verification_status: verified
verified_at: "2026-10-21"
source_origin: "https://github.com/spacemit-com/docs-chip"
source_file: "Sources/docs-chip/zh/vital_stone/v100/v100_docs/root_overview.md"
source_commit: "2525ee3b68e0f4864f1bf12c8a59df040bf27e84"
source_section: "概述；特性；产品框图"
source_resolution: resolved
source_checked_at: 2026-10-21
source_note: "已对照 docs-chip 官方 V100 处理器产品简介核对全量芯片微架构、虚拟化、内存总线与 RAS 容错特性。"
created: 2026-10-21
updated: 2026-10-21
aliases: ["V100服务器芯片专题", "Vital Stone V100", "SpacemiT V100", "v100_chip", "V100芯片档案", "V100处理器专题档案"]
domain: chip_product_specs
target_audience: [系统架构师, 服务器硬件工程师, 操作系统与内核研发, 芯片选型专家]
source_related_file: ["Sources/docs-product/zh/v100_series/index.md"]
source_related_commit: ["bc640755145625cc20745f49861f82588863fca3"]
---

# SpacemiT V100 服务器处理器芯片专题档案

> [!TIP]
> **💡 工程师导读与架构焦点**：
> SpacemiT Vital Stone **V100** 是进迭时空面向云计算、企业级数据中心及智算基础设施研发的高性能服务器级 RISC-V 处理器。作为业内**首颗完整符合 RISC-V 服务器规范的计算芯片**，V100 率先突破了 RISC-V 进入数据中心 IDC 领域的关键软硬件虚拟化与 I/O 虚拟化瓶颈。
> **目标读者**：`系统架构师 / 服务器硬件工程师 / 内核驱动开发 / 芯片选型专家` | **技术领域**：`chip_product_specs`

---

## 1. 处理器定位与核心微架构

V100 芯片采用 64 位高性能乱序 RISC-V 核心拓扑，全面符合 **RISC-V RVA23 Profile** 标准规范。单芯片集成 **46 个高性能计算大核**，采用双簇异构计算大核架构：

```mermaid
graph TD
    subgraph V100_Die [SpacemiT Vital Stone V100 单芯片 (TDP: 120W)]
        subgraph KMH_Cluster [开源高性能大核簇 (6 Cores @ 2.1GHz)]
            KMH["6 × 香山昆明湖 V2R2<br>十三级六发射乱序流水线<br>SPECint2006 ≥ 15.0/GHz<br>各 64KB L1 I/D + 1MB L2"]
        end
        subgraph X100_Cluster [自研高并发能效大核簇 (40 Cores @ 2.4GHz)]
            X100["40 × 进迭时空 X100<br>十二级四发射乱序流水线<br>SPECint2006 ≥ 9.0/GHz<br>各 64KB L1 I/D + 2MB L2"]
        end
        SLC["全片共享 64MB SLC Cache (System Level Cache)"]
        KMH_Cluster --- SLC
        X100_Cluster --- SLC
        DDR["8 通道 DDR5 4800 MT/s (307 GB/s, 最高 2TB)"]
        PCIE["PCIe 5.0 控制器 (52 通道高速互联)"]
        SLC --- DDR
        SLC --- PCIE
    end
```

### 微架构核心特性
1. **香山昆明湖 V2R2 核心（6 核）**：主频 2.1 GHz，十三级六发射深乱序执行流水线，配备 64KB L1 I-Cache、64KB L1 D-Cache 及 1MB L2 Cache，单核 SPECint2006 ≥ 15.0/GHz，专为高单线程关键负载优化。
2. **进迭时空自研 X100 核心（40 核）**：主频 2.4 GHz，支持 DVFS 动态调频调压，十二级四发射乱序流水线，配备 64KB L1 I-Cache、64KB L1 D-Cache 及独立的 2MB L2 Cache，单核 SPECint2006 ≥ 9.0/GHz，提供强大的多线程高并发吞吐能力。
3. **片上一致性与超大缓存**：全片共享 **64MB SLC Cache**，实现 46 核之间的高速低延迟缓存一致性通信。

---

## 2. 突破全栈硬件级虚拟化 (Full-Stack RVH)

长期以来，缺乏硬件级系统虚拟化与 I/O 虚拟化是 RISC-V 架构进入企业级云计算领域的核心障碍。V100 率先实现了规范的全栈硬化突破：

* **CPU 虚拟化**：完整支持 **RISC-V Hypervisor 1.0 (RVH)** 扩展，硬件支持内存虚拟化（SV48×4 与 SV39×4 Guest 物理地址翻译），大幅降低二级页表转换损耗。
* **中断虚拟化**：基于 **RISC-V AIA（先进中断架构）** 标准中断控制器，提供 255 个 M-mode MSI、255 个 S-mode MSI 及 63 个 VS-mode MSI，VS 模式下每个 Hart 原生配置了 7 个 vCPU 中断通道，原生打通低延迟虚拟机中断投递。
* **外设 I/O 虚拟化**：完整实现 **IOMMU 1.0** 硬件外设虚拟化规范，全面支持 **SR-IOV**（单根 I/O 虚拟化），虚拟机可直接高效穿透访问物理网卡与高速算力卡。

---

## 3. 高带宽大容量内存与高速 PCIe 5.0 扩展

### 8 通道企业级 DDR5
* **通道规模**：单芯片提供 **8 个 DDR5 独立物理通道**，支持 1DPC。
* **速率与带宽**：兼容主流 DDR5 RDIMM 内存模组，额定传输速率达 **4800 MT/s**，单芯片理论物理带宽高达 **307 GB/s**。
* **纠错与容量**：单个通道支持 80bit DIMM 并搭载 **Sideband ECC（边带纠错码）**，支持每插槽最大 256GB，单芯片可扩展至 **2TB** 物理内存。
* **智能仲裁调度**：内置硬件多级仲裁机制、QoS 服务质量保证策略、内存带宽限流与实时吞吐监控功能。

### 满足智算场景的 PCIe 5.0
* **通道规模**：支持 **PCIe 5.0** 标准协议，单芯片引出 **52 条高速通道**。
* **弹性拆分能力**：支持灵活配置为 3 组 x16 / x8x8 / x8x4x4 及 1 组 x2x1x1，既能满速挂接高性能 AI 加速卡，也可下拆接入高速存储。
* **协议栈兼容**：支持 NVMe over PCIe、SAS/SATA over PCIe 及高速网卡通信。

---

## 4. 企业级 RAS 高可用性与电信级安全防御

### RISC-V 服务器 RAS 体系
遵循 **RISC-V RERI RAS** 规范与 **Firmware First** 故障处理原则：
* **CPU RAS**：支持正确性错误（CE）与不可恢复错误（UEC）差异化中断日志上报。
* **内存 RAS**：支持 ECC / CRC 校验、后台巡检机制、硬件故障行隔离与物理地址保护。
* **PCIe RAS**：支持链路异常自愈恢复、AER 高级错误报告、热插拔事件拦截及日志追溯。
* **总线与系统 RAS**：总线事务数据校验标记、SRAM ECC 保护，结合片上多点温度传感器联动 BMC 带内/带外实时风扇智能调速与功率封顶。

### 硬件信任根与安全架构
* **安全标准**：完整遵循 RISC-V PMP/ePMP 内存隔离规范，并引入 **IOPMP (Rapid-k Model)** 实现外设 DMA 级内存边界防御。
* **硬件安全模块 (HSM)**：集成独立的片上硬件安全模块，基于硬件信任根（HW-RoT）实现安全启动链、密钥安全存储与生命周期受控管理。
* **密码学硬件加速**：硬化支持国密 **SM2 / SM3 / SM4** 算法，并集成国际主流 AES、SHA、RSA 加解密硬件加速引擎。

---

## 5. 服务器基础软件与系统生态

* **固件规范**：严格遵循 **UEFI 2.11** 与 **ACPI 6.6** 标准，支持基于 **EDK2** 的服务器 BIOS 固件引导；支持基于 **openBMC** 的基板管理系统。
* **操作系统适配**：全面支持 Linux 内核 6.6 及以上版本，支持企业级发行版（openEuler、BC-Linux、Ubuntu Server、Debian Server、openKylin 等）。
* **虚拟化与容器**：跑通 KVM 原生硬件辅助虚拟化，原生支持 QEMU 与 Docker 容器生态。
* **基础中间件**：适配 Redis、Tomcat、MySQL、PostgreSQL、Apache 等主流开源数据库与应用中间件。

---

## 6. 生态产品应用与事实关联

* **芯片核心事实证据**：[[Evidence/v100_chip_specs|Vital Stone V100 服务器级 CPU 核心技术规格参数]]
* **机架式服务器整机生态**：[[Knowledge_Atoms/SpacemiT_V100系列机架式服务器专题档案|SpacemiT V100 系列机架式服务器专题档案]]
  * [[Evidence/v100_servers_specs|V100 系列机架式服务器整机物理规格参数对比表]]
* **顶层生态图谱**：[[Knowledge_Atoms/Spacemit_产品矩阵与硬件生态全景档案|Spacemit 产品矩阵与硬件生态全景档案]]
* **官方原始出处**：[V100 芯片产品简介 - docs-chip](https://github.com/spacemit-com/docs-chip/blob/main/zh/vital_stone/v100/v100_docs/root_overview.md)
