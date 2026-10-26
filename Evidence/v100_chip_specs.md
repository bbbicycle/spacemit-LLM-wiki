---
type: evidence
title: "Vital Stone V100 服务器级 CPU 核心技术规格参数"
claim_type: "parameter"
status: needs_review
verification_status: verified
verified_at: "2026-10-21"
external_use: false
source_file: "Sources/docs-chip/zh/vital_stone/v100/v100_docs/root_overview.md"
source_origin: "https://github.com/spacemit-com/docs-chip"
source_commit: "2525ee3b68e0f4864f1bf12c8a59df040bf27e84"
source_section: "概述；特性"
source_resolution: resolved
source_checked_at: 2026-10-21
source_note: "已严格对照 docs-chip 官方 V100 产品简介提取全量芯片规格与物理电气参数。"
created: 2026-10-21
updated: 2026-10-21
aliases: ["V100芯片核心参数", "V100 处理器规格参数", "v100_chip_specs", "Vital Stone V100 规格", "V100 Specs"]
domain: chip_product_specs
target_audience: [系统架构师, 服务器硬件工程师, 芯片选型工程师]
---
# Vital Stone V100 服务器级 CPU 核心技术规格参数

> [!TIP]
> **💡 工程师导读与排坑焦点**：存放 Vital Stone V100 处理器架构、核心规模、Cache 拓扑、内存带宽、PCIe 5.0、全栈虚拟化及封装功耗等原子事实。
> **目标读者**：`系统架构师 / 服务器硬件工程师 / 芯片选型工程师` | **技术领域**：`chip_product_specs`

本文汇总了 SpacemiT Vital Stone RISC-V 服务器级 CPU **V100** 的芯片级硬件规格与电气参数数据，数据来源于官方 V100 Brief。

| 规格维度 | 详细参数规格 | 说明 / 技术依据 |
| :--- | :--- | :--- |
| **芯片定位** | 首颗完整符合 RISC-V 服务器规范的计算芯片 | 覆盖数据中心 AI 训练/推理、通用计算、海量存储及边缘服务器 |
| **CPU 架构** | 64 位高性能乱序 RISC-V 核心架构 | 全面兼容 RISC-V **RVA23 Profile** 标准规范 |
| **核心规模与主频** | **46 个 RISC-V 高性能计算核**<br>• 6 × 香山昆明湖 V2R2 核心（最高 2.1 GHz）<br>• 40 × 进迭时空自研 X100 核心（最高 2.4 GHz） | 双簇异构大核拓扑；支持 DVFS 动态调频调压 |
| **单核算力性能** | • 香山昆明湖 V2R2：单核 SPECint2006 **≥ 15.0/GHz**<br>• 进迭时空 X100：单核 SPECint2006 **≥ 9.0/GHz** | 昆明湖支持十三级六发射乱序流水线；X100 支持十二级四发射乱序流水线 |
| **Cache 缓存体系** | • 香山昆明湖：64KB L1 I-Cache, 64KB L1 D-Cache, 1MB L2 Cache<br>• 进迭时空 X100：64KB L1 I-Cache, 64KB L1 D-Cache, 2MB L2 Cache<br>• **全片共享 64MB SLC Cache (System Level Cache)** | 多级高密度缓存一致性互联，满足高并发大吞吐读写 |
| **硬件全栈虚拟化** | • **CPU 虚拟化**：支持 RISC-V Hypervisor 1.0 (RVH) 扩展，支持 SV48×4 / SV39×4 Guest 地址翻译<br>• **中断虚拟化**：支持标准 AIA 中断架构，支持 255 个 M-mode MSI、255 个 S-mode MSI、63 个 VS-mode MSI，VS 每个 Hart 配置 7 个 vCPU<br>• **外设虚拟化**：基于 IOMMU 的 I/O 虚拟化，完整实现 SR-IOV 功能 | 业内率先实现 RVH 1.0、AIA 1.0 与 IOMMU 1.0 全栈硬件硬化支持，原生消除云化性能损耗 |
| **内存子系统 (DDR5)** | • 支持 **8 × DDR5 通道**，支持 1DPC<br>• 兼容主流 DDR5 RDIMM 内存模组<br>• 最高速率 **4800 MT/s**，单芯片最大带宽 **307 GB/s**<br>• 单个内存通道支持 80bit DIMM（带 Sideband ECC 边带纠错码）<br>• 每个 DIMM 最大支持 256GB，单芯片最大支持 **2TB** 内存 | 支持多级仲裁、QoS 策略、带宽限制与硬件性能监控 |
| **高速互联总线 (PCIe 5.0)** | • 支持 **PCIe 5.0 标准**，单芯片提供 **52 条高速通道**<br>• 通道拆分配置：支持 3 组 x16 / x8x8 / x8x4x4 与 1 组 x2x1x1<br>• 协议支持：支持 SAS/SATA over PCIe、NVMe over PCIe、USB over PCIe 等 | 高速直连 GPU/NPU 算力卡与企业级 NVMe 存储阵列 |
| **网络控制 (GMAC)** | 1 × GMAC 控制器，支持 IEEE 1588 高精度时间同步 | 满足数据中心时间敏感网络与微秒级时钟对齐 |
| **外围低速 I/O 接口** | • 1 × QSPI<br>• 1 × LPC、1 × eSPI<br>• 3 × SPI Master、1 × SPI Slave<br>• 4 × I3C、12 × I2C、12 × SMBUS<br>• 5 × UART | 完整适配企业级主板外设、基板控制器及环境传感器采样 |
| **服务器级 RAS 机制** | • 遵循 RISC-V RERI RAS 规范与 Firmware First 原则<br>• **CPU RAS**：CE / UEC 差异化容错处理及中断日志记录<br>• **内存 RAS**：ECC / CRC 校验、定期巡检、故障隔离与物理地址保护<br>• **PCIe RAS**：链路自愈恢复、高级错误报告 (AER)、热插拔及日志记录<br>• **总线 RAS**：总线数据校验/标记、SRAM ECC 保护<br>• **系统 RAS**：集成多点片上温度传感器，联动 BMC 带内/带外实时监控调节 | 满足企业级电信与金融关键业务 7×24 小时高可用性要求 |
| **数据中心级安全架构** | • 硬件规范：支持 PMP / ePMP 与 IOPMP (Rapid-k Model) 安全组件<br>• 信任机制：集成 **HSM 硬件安全模块**，支持硬件信任根 (RoT)、安全启动、密钥管理与安全调试<br>• 算法引擎：支持国密 SM2 / SM3 / SM4 以及 AES / SHA / RSA 硬件加密 | 保证数据中心多租户高安全隔离与国家信创合规 |
| **服务器基础固件** | • 遵循 UEFI 2.11 与 ACPI 6.6 规范，支持基于 EDK2 的服务器 BIOS 固件<br>• 支持基于 openBMC 的带内/带外管理固件 | 兼容主流标准服务器运维与管理体系 |
| **软件生态支持** | • 内核版本：Linux 内核 6.6 及以上版本<br>• 工具链：主流 GCC 与 LLVM<br>• 操作系统：openEuler、openKylin、银河麒麟（规划）、Ubuntu、Debian、Fedora 等<br>• 中间件：Tomcat、Redis、Apache、MySQL、PostgreSQL 等<br>• 虚拟化与容器：KVM、QEMU、Docker 容器部署 | 深度适配国产信创与通用开源服务器生态 |
| **热设计功耗 (TDP)** | **120W** | 出色的服务器能效比释放 |
| **工作环境温度** | **0℃ ～ 40℃** | 标准企业级数据中心机房温控环境 |
| **物理封装规格** | **FCBGA 封装**，58.5 mm × 75.4 mm，0.94 mm pitch | 高密度引脚与多通道高速信号走线设计 |
