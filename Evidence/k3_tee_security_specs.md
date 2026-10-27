---
type: evidence
title: "K3 芯片 TEE 安全架构与固件分区参数"
claim_type: "parameter"
status: needs_review
verification_status: verified
verified_at: "2026-10-27"
external_use: true
source_file: "Sources/docs-buildroot/zh/k3_buildroot/security/tee_architecture.md"
source_origin: "https://github.com/spacemit-com/docs-buildroot"
source_commit: "c67b37b8a4a90408b95e5532c2df3ab800d80ffe"
source_section: "TEE在系统中的位置；组件清单；启动流程；内存布局；安全存储"
source_resolution: resolved
source_checked_at: "2026-10-27"
source_note: "基于 Buildroot 安全文档体系（commit c67b37b），系统梳理 OP-TEE 4.5.0 在 K3 上的内存划分、OpenSBI PMP 隔离基址、固件加载顺序、MPXY 通信与 LCS 生命周期规格。"
source_related_file: ["Sources/docs-buildroot/zh/k3_buildroot/security/white_paper.md", "Sources/docs-buildroot/zh/k3_buildroot/security/key_management_lifecycle.md"]
source_related_commit: ["c67b37b8a4a90408b95e5532c2df3ab800d80ffe", "c67b37b8a4a90408b95e5532c2df3ab800d80ffe"]
created: 2026-10-27
updated: 2026-10-27
aliases: ["K3 TEE安全架构参数", "K3 OP-TEE Specs", "k3_tee_security_specs", "K3安全启动与固件分区"]
domain: bsp_kernel_drivers
target_audience: [安全工程师, 驱动工程师, 系统架构师]
---
# K3 芯片 TEE 安全架构与固件分区参数

> [!TIP]
> **💡 工程师导读与排坑焦点**：存放 K3 芯片 OP-TEE 4.5.0 内存基址、保留共享内存、固件加载时序、PMP 域隔离与安全生命周期（LCS）规格。
> **目标读者**：`安全工程师 / 驱动工程师 / 系统架构师` | **技术领域**：`bsp_kernel_drivers`

本文件汇总了 SpacemiT K3 平台在 Buildroot 下启用 OP-TEE（Open Portable Trusted Execution Environment）安全环境的核心物理地址、内存切分、固件加载时序及安全生命周期参数。

---

## 1. TEE 物理内存布局与保留区规格

K3 平台采用**保留式共享内存（Reserved SHM）**方案（`CFG_CORE_RESERVED_SHM=y`，`CFG_CORE_DYN_SHM=n`），不启用动态共享内存。

| 区域名称 | 配置符号 | 物理起始基址 | 分配大小 | 访问权限与属性 | 说明 |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **TEE RAM (TDDRAM)** | `CFG_TDDRAM_START` / `SIZE` | `0x1_7100_0000` | **16 MB** | 安全世界独占（S态 Trusted Domain），PMP 硬件保护，内核不可见 | 存放 TEE 内核本体、TA 代码、堆栈与安全驱动，常驻内存不换出 |
| **共享内存 (SHMEM)** | `CFG_SHMEM_START` / `SIZE` | `0x1_7200_0000` | **16 MB** | REE 与 TEE 共同可见，普通世界注册，安全世界映射 | 用于 CA 与 TA 之间传递请求/响应参数包 |

> [!IMPORTANT]
> **设备树注入机制**：
> 平台静态设备树（DTS）**不需要手动声明**共享内存与 TEE RAM。OP-TEE 启动后会主动向设备树 `/reserved-memory` 动态注入 `optee_core` 与 `optee_shm` 节点，内核据此打上 `nomap non-reusable` 标记。在静态设备树重复声明会导致重复映射冲突。

---

## 2. 固件加载顺序与目标内存地址

在安全固件构建中，SPL（FSBL）承担安全镜像加载职责，各组件加载时序与目标地址如下：

| 顺序 | 固件镜像文件 | 加载方 | 加载目标物理地址 | 运行时所处架构态 | 失败行为 |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **1** | `FSBL.bin` (SPL) | BootROM (ZSBL) | `0xc080_1000` (SRAM) | M 态 (Machine Mode) | BROM 回退次级启动设备 |
| **2** | `esos.itb` | SPL | — (RCPU 独立域) | 实时协处理器固件 | 内核启动死锁 |
| **3** | `optee.itb` | SPL | `0x1_7100_0000` (DDR) | S 态 (安全 Trusted Domain) | MMC/MTD 路径直接中止启动 |
| **4** | `u-boot.itb` | SPL | `0x1_0200_0000` (DDR) | S 态 (普通 Root Domain) | 启动终止 |
| **5** | OpenSBI (`fw_dynamic.itb`) | U-Boot | `0x1_0000_0000` (DDR) | M 态 (监控层) | 引导失败 |

---

## 3. RISC-V 跨域通信与 Mailbox 通道

RISC-V 架构没有 Arm 的 `smc` 指令，K3 平台通过 OpenSBI MPXY 框架与 Mailbox 进行世界间切换：

| 维度 | 参数 / 配置 | 说明 |
| :--- | :--- | :--- |
| **通信机制** | OpenSBI MPXY 协议 + RISC-V `ecall` / `mret` | 普通世界驱动向 M 态发起 ecall，由 OpenSBI 切换至 Trusted 域分发 |
| **通道数量** | **16 个 Per-Hart 通道** | 每个 CPU 核心独立绑定一组 Mailbox 通道，避免并发核间锁竞争 |
| **设备树 Mailbox 绑定** | `mboxes = <&mpxy_mbox 0x1000 0x2>` | 定义于 U-Boot 源码树 `arch/riscv/dts/k3-optee.dtsi` |
| **REE 侧驱动入口** | `drivers/tee/optee/mpxy_sbi.c` | 内核暴露 `/dev/tee0` 与 `/dev/teepriv0` 字符设备供用户态 CA 访问 |
| **用户态守护进程** | `tee-supplicant` | 常驻进程，处理来自 OP-TEE 的反向 RPC 请求（如安全文件系统与 RPMB 访问） |

---

## 4. 密钥管理与安全生命周期 (LCS) 规格

K3 安全方案符合 RISC-V Platform Security Model 0.9.1 规范：

| 属性 | 规格 / 取值 | 说明 |
| :--- | :--- | :--- |
| **硬件根密钥 (HUK)** | 芯片内部硬件一次性烧录密钥 | 作为密钥派生树的根，不对外暴露，用于派生安全存储密钥（SSK） |
| **安全存储介质** | eMMC RPMB（Replay Protected Memory Block） | 硬件防回滚与防重放攻击的安全存储分区 |
| **生命周期状态 (LCS)** | **CM (Chip Manufacture)** | 芯片出厂状态，全功能开放，未烧录客户根密钥 |
| | **DM (Device Manufacture)** | 设备量产状态，烧录 OEM 公钥哈希与 RPMB 密钥 |
| | **SE (Secure / Production)** | 终端安全量产态，安全启动强校验开启，JTAG 调试通道默认关闭 |
| | **RMA (Return Merchandise)** | 售后退回分析态，需特定厂商授权凭证解锁调试接口 |
