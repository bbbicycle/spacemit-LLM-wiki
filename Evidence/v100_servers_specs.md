---
type: evidence
title: "V100 系列机架式服务器整机物理规格参数对比表"
claim_type: "parameter"
status: needs_review
verification_status: verified
verified_at: "2026-10-21"
external_use: false
source_file: "Sources/docs-product/zh/v100_series/index.md"
source_origin: "https://github.com/spacemit-com/docs-product"
source_commit: "bc640755145625cc20745f49861f82588863fca3"
source_related_file: ["Sources/docs-product/zh/v100_series/v100_c2201/root_overview.md", "Sources/docs-product/zh/v100_series/v100_s5236/root_overview.md", "Sources/docs-product/zh/v100_series/v100_g5201/root_overview.md"]
source_related_commit: ["bc640755145625cc20745f49861f82588863fca3", "bc640755145625cc20745f49861f82588863fca3", "bc640755145625cc20745f49861f82588863fca3"]
source_section: "产品规格；特性；概述"
source_resolution: resolved
source_checked_at: 2026-10-21
source_note: "已严格对照 docs-product 官方 C2201、S5236、G5201 产品简介逐项核对三款整机配置与物理参数。"
created: 2026-10-21
updated: 2026-10-21
aliases: ["V100服务器规格对比表", "C2201_S5236_G5201规格参数", "v100_servers_specs", "V100系列整机规格", "V100 Server Specs"]
domain: chip_product_specs
target_audience: [系统架构师, 数据中心运维工程师, 服务器硬件工程师, 解决方案架构师]
---
# V100 系列机架式服务器整机物理规格参数对比表

> [!TIP]
> **💡 工程师导读与排坑焦点**：存放基于 V100 芯片的 C2201 计算服务器、S5236 存储服务器、G5201 智算服务器在机箱尺寸、双路 CPU 拓扑、内存插槽、硬盘布局、PCIe 扩展、网络及供电冗余维度的横向硬数据对比。
> **目标读者**：`系统架构师 / 数据中心运维工程师 / 服务器硬件工程师` | **技术领域**：`chip_product_specs`

本文汇总基于 SpacemiT Vital Stone V100 处理器的 3 款官方机架式服务器核心参数对比，数据来源于 docs-product 官方产品简介。

| 规格维度 | C2201 计算服务器 | S5236 存储服务器 | G5201 智算服务器 |
| :--- | :--- | :--- | :--- |
| **官方代号与定位** | `v100_c2201`<br>**2U 双路机架式计算服务器** | `v100_s5236`<br>**4U 高密度机架式存储服务器** | `v100_g5201`<br>**4U 双路高密度机架式智算服务器** |
| **典型应用场景** | 数据中心、云计算、科学计算及行业关键业务 | 云计算、云存储、智算中心、数据归档、备份容灾 | 大模型推理、科学计算、智算中心、数据中心及政企垂直场景 |
| **处理器配置** | **2 颗进迭时空 V100 处理器**<br>整机共 **92 核**（12×香山昆明湖 + 80×X100），最高主频 2.4 GHz | **2 颗进迭时空 V100 处理器**<br>整机共 **92 核**，最高主频 2.4 GHz | **2 颗进迭时空 V100 处理器**<br>整机共 **92 核**，最高主频 2.4 GHz |
| **内存架构与槽位** | • **16 个 DDR5 内存插槽**<br>• 最高支持 **2 TB** 内存<br>• 速率高达 **4800 MT/s**<br>• 单颗芯片最大带宽 307 GB/s | • **16 个 DDR5 内存插槽**<br>• 最高支持 **2 TB** 内存<br>• 速率 4800 MT/s，理论带宽最高 307 GB/s<br>• （默认出厂插入 2 个 DDR5） | • **16 个 DDR5 内存插槽**<br>• 最高支持 **2 TB** 内存<br>• 8 通道 4800 MT/s DDR5 |
| **硬盘存储槽位** | • **前置**：最大支持 8 块 3.5 英寸 U.2 NVMe SSD<br>• **内置**：最大支持 1 块 M.2 NVMe SSD<br>• **后置**：最大支持 2 块 2.5 英寸 SATA HDD/SSD | • **前置**：24 个 SATA 盘（3.5 英寸）<br>• **后置**：12 个 SATA 盘（3.5 英寸）+ 2 个 2.5 英寸 SATA 系统盘<br>• **总盘位**：共 36 个 3.5 寸 + 2 个 2.5 寸 | • **前置**：8 个 SATA 盘 + 4 个 NVMe 盘 |
| **PCIe 高速通道与扩展** | • 整机提供 **88 条 PCIe 5.0 Lane**<br>• 插槽配置：最多支持 3 个 PCIe 扩展卡（×8）；或 2 个 PCIe 扩展卡（×16）；或 1 个 PCIe（×16）+ 2 个 PCIe（×8） | • 支持 **3 个 RISER 卡槽**<br>（标配 2 张网卡、1 张 RAID 卡） | • **GPU 扩展能力**：支持 **8 张 600W PCIe 风冷加速卡**<br>• **互联带宽**：支持最高 **256 GB/s GPU 卡间互联**<br>• **显存规格**：配备大容量 HBM3E 高显存带宽<br>• **扩展插槽**：PCIE_SW 板支持 12 个插槽；MCIO 转接板支持 5 个插槽 |
| **网络配置** | 国产网络控制器，支持通过 **OCP 扩展**千兆、万兆网络 | 标配 **1 × OCP 3.0 网卡** + **2 × 25GbE 双端口网卡** | 标配 **1 × OCP 3.0 网卡** + **4 × 400GbE RoCE 高速网卡**（支持 RDMA RoCEv2） |
| **前置 / 后置 I/O 接口** | • **前置**：2 × USB 3.0、1 × VGA<br>• **后置**：2 × 电源接口、1 × VGA、2 × USB 3.0、1 × Type-C 调试口、1 × 管理网口 | • **前置**：2 × USB 3.0、1 × VGA<br>• **后置**：2 × 电源接口、1 × VGA、2 × USB 3.0、1 × Type-C 调试口、1 × 管理网口 | • **前置**：2 × USB 3.0、1 × VGA<br>• **后置**：2 × 电源接口、1 × VGA、2 × USB 3.0、1 × Type-C 调试口、1 × 管理网口 |
| **散热风扇** | 支持 N+1 冗余热插拔风扇 | 标配 12 个 6056 风扇，支持 N+1 冗余与热插拔 | 标配 12 个 6056 风扇，支持 N+1 冗余与热插拔 |
| **电源供应 (PSU)** | 标准 **1600W CRPS 铂金电源**，支持 1+1 冗余 | 标准 **CRPS 电源**，支持 1+1 冗余 | **4 个标准 CRPS 电源**，支持 N+1 冗余（满足 8×600W 高功耗释放） |
| **系统管理与 BMC** | 集成 BMC 管理芯片 **AST2600**；支持标准 UEFI 及 ACPI；支持 IPMI、Redfish、SOL、KVM 虚拟媒介 | 支持远程 KVM over IP、风扇智能调速与远程电源控制 | 支持远程 KVM over IP、风扇智能调速与远程电源控制 |
| **操作系统支持** | 支持 Ubuntu、Red Hat、Fedora、Rocky Linux、openRuyi、openEuler、openKylin 等 | 支持 Ubuntu、Red Hat、Fedora、Rocky Linux、openRuyi、openEuler、openKylin 等 | 支持 Ubuntu、Red Hat、Fedora、Rocky Linux、openRuyi、openEuler、openKylin 等 |
| **整机重量与噪声** | 重量：**≤ 35 kg**；噪声：**< 55 dB** | 重量：**55 kg**；噪声：**< 55 dB** | 重量：**约 60 kg**；噪声：**< 55 dB** |
| **环境温湿度** | 工作：0℃～40℃，35%～80% 湿度<br>存储：-40℃～55℃，20%～93% 湿度 | 工作：0℃～40℃，35%～80% 湿度<br>存储：-40℃～55℃，20%～93% 湿度 | 工作：0℃～40℃，35%～80% 湿度<br>存储：-40℃～55℃，20%～93% 湿度 |
| **机箱物理尺寸** | **820 × 447.4 × 87.8 mm**（深×宽×高，2U） | **820 × 447.4 × 176.9 mm**（深×宽×高，4U） | **895 × 447.4 × 176.8 mm**（深×宽×高，4U） |
