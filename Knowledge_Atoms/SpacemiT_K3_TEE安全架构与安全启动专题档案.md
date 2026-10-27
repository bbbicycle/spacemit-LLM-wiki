---
type: knowledge_atom
title: "SpacemiT K3 TEE 安全架构与安全启动专题档案"
status: needs_review
verification_status: verified
verified_at: "2026-10-27"
source_file: "Sources/docs-buildroot/zh/k3_buildroot/security/tee_architecture.md"
source_origin: "https://github.com/spacemit-com/docs-buildroot"
source_commit: "c67b37b8a4a90408b95e5532c2df3ab800d80ffe"
source_locator: "TEE在系统中的位置；启动流程；内存布局；安全存储；BSP集成"
source_resolution: resolved
source_checked_at: "2026-10-27"
source_note: "基于 Buildroot 安全文档体系（commit c67b37b），详解 K3 平台 OP-TEE 4.5.0 在 RISC-V 架构下的三域模型、MPXY 通信机制、保留式内存与设备树注入规范、TA/CA 开发及 RPMB 密钥生命周期。"
source_related_file: ["Sources/docs-buildroot/zh/k3_buildroot/security/white_paper.md", "Sources/docs-buildroot/zh/k3_buildroot/security/ta_guide.md", "Sources/docs-buildroot/zh/k3_buildroot/security/key_management_lifecycle.md"]
source_related_commit: ["c67b37b8a4a90408b95e5532c2df3ab800d80ffe", "c67b37b8a4a90408b95e5532c2df3ab800d80ffe", "c67b37b8a4a90408b95e5532c2df3ab800d80ffe"]
created: 2026-10-27
updated: 2026-10-27
aliases: ["K3 TEE安全架构专题", "SpacemiT K3 OP-TEE Topic", "k3_tee_security_architecture", "K3安全启动"]
domain: bsp_kernel_drivers
target_audience: [嵌入式安全工程师, 驱动工程师, 固件工程师]
---
# SpacemiT K3 TEE 安全架构与安全启动专题档案

> [!TIP]
> **💡 工程师导读与排坑焦点**：详解 SpacemiT K3 平台 OP-TEE 4.5.0 系统架构、RISC-V MPXY 通信机制、保留式共享内存、安全启动链与 TA/CA 开发规范。
> **目标读者**：`嵌入式安全工程师 / 驱动工程师 / 固件工程师` | **技术领域**：`bsp_kernel_drivers`

本专题系统阐述基于 SpacemiT K3 芯片平台的硬件安全架构与 TEE（Trusted Execution Environment）软件栈实现。重点解析在缺少传统 Arm SMC 指令的 RISC-V 架构下，K3 如何通过 OpenSBI 域管理与 MPXY 机制实现安全世界（Secure World）与普通世界（REE）的强隔离，并指导可信应用（TA）与客户端应用（CA）的工程落地。

---

## 1. RISC-V 三域安全模型与 OP-TEE 在系统中的位置

在 K3 平台上，OP-TEE 运行于 RISC-V 的 **S 态（Supervisor Mode）**，通过 OpenSBI（运行于 M 态）提供的域模型与物理内存保护（PMP）实现硬件级边界隔离：

*   **普通世界（REE, Rich Execution Environment）**：
    *   包含用户态客户端应用（CA）、`libteec` 运行时库、守护进程 `tee-supplicant`，以及 Linux 内核驱动（`drivers/tee/optee/mpxy_sbi.c`）。
    *   受限于 OpenSBI 的 Root Domain，无法直接访问安全世界的物理内存与外设寄存器。
*   **监控层（M 态, Machine Mode）**：
    *   由 **OpenSBI** 承担，负责平台域管理（Domain Management）、物理内存保护（PMP/IOPMP）配置，以及跨域分发器（`fdt_mpxy_opteed.c`）。
*   **安全世界（TEE, Trusted Execution Environment）**：
    *   运行 **OP-TEE OS 4.5.0**，包含 TEE 内核、用户态可信应用（TA）、动态加载器（ldelf）及密码学加速库，运行于专属的 Trusted Domain。

---

## 2. REE 到 TEE 的调用链与 RISC-V MPXY 通信机制

由于 RISC-V 架构没有 Arm 的 `smc` 陷入指令，K3 创新采用了 **OpenSBI MPXY（Message Proxy）框架 + Per-Hart Mailbox** 实现跨域分发：

1.  **CA 侧发起请求**：CA 通过 GlobalPlatform TEE Client API（如 `TEE_OpenSession` 或 `TEE_InvokeCommand`）发起调用，进入 Linux 内核 TEE 驱动。
2.  **Mailbox 消息投递**：内核驱动通过 16 个独立 Per-Hart 通道绑定的 `mpxy_mbox`（定义于 `arch/riscv/dts/k3-optee.dtsi`），将请求上下文打包。
3.  **M 态陷入与分发**：触发 RISC-V `ecall` 进入 OpenSBI M 态，由 OP-TEE 分发器接住并切换硬件上下文至 Trusted 域。
4.  **安全世界执行**：进入 OP-TEE OS 的 `thread_std_abi_entry()`，分发至具体 TA 执行业务逻辑。
5.  **反向 RPC 代理**：当 TA 需要进行文件系统存储或 RPMB 硬件操作时，OP-TEE 发起 RPC 请求，由普通世界的常驻守护进程 `tee-supplicant` 代理完成。

---

## 3. 内存隔离与设备树注入规范

具体物理内存基址见 [[Evidence/k3_tee_security_specs]]。

*   **保留式共享内存（Reserved SHM）**：
    *   K3 平台固定配置 `CFG_CORE_RESERVED_SHM=y`，基址固定为 `0x1_7200_0000`（16 MB）。
    *   **排坑红线**：静态设备树**严禁手动编写** `reserved-memory` 或 `memory-region`。OP-TEE 在启动阶段会主动向设备树动态插入 `optee_core` 与 `optee_shm` 节点。若在 DTS 中静态硬编码，将造成双重声明导致内核 Panic。
*   **常驻内存保护（TEE RAM）**：
    *   TEE RAM 位于 `0x1_7100_0000`（16 MB），受 OpenSBI PMP 硬件强制保护。
    *   OP-TEE 初始化后**常驻内存不换出**。内核启动时打上 `nomap non-reusable` 标记。排查内存踩踏或偶发崩溃时，必须先在内核启动日志中确认两条 reserved mem 记录是否打印完整。

---

## 4. 安全启动链与固件时序

K3 安全固件遵循严格的自底向上信任链加载顺序（相关 RCPU 固件依赖见 [[Evidence/esos_rcpu_firmware_specs]] 与 [[Evidence/buildroot_bsp_specs]]）：

1.  **BootROM (ZSBL)**：从片内 ROM 执行，初始化基本时钟并加载 SPL。
2.  **SPL (FSBL)**：运行于片内 SRAM，依次加载 `esos.itb`（RCPU）、`optee.itb`（DDR `0x1_7100_0000`）及 `u-boot.itb`（`0x1_0200_0000`）。
3.  **OpenSBI**：运行于 M 态，建立 PMP 隔离域并首次跳转执行 OP-TEE。
4.  **OP-TEE OS**：完成安全世界硬件配置、向设备树注入保留内存节点后常驻。
5.  **U-Boot & Linux**：由 OpenSBI 将控制权切回普通世界执行 U-Boot，最终引导 Linux 内核。

> [!CAUTION]
> 在安全镜像中，MMC/MTD 启动介质将 TEE 设为必需项。若未烧录 `optee.itb` 或镜像签名损坏，SPL 将**直接中止启动**，绝不会静默回退至非安全环境。

---

## 5. TA/CA 开发规范与 GlobalPlatform 契约

K3 平台全面遵循 GlobalPlatform（GP）国际标准，业务代码与平台底层解耦：

*   **CA 开发（普通世界）**：
    *   遵循 GP TEE Client API 规范，链接 `libteec.so`。
    *   构建时通过 Buildroot 自动拉取 `optee_client`，头文件包含 `<tee_client_api.h>`。
*   **TA 开发（安全世界）**：
    *   遵循 GP TEE Internal Core API 规范，依赖 `optee_os` 提供的 `libutee`。
    *   TA 采用独立 UUID 标识，编译为带签名的 `.ta` 格式（如 `bc303bda-6936-4945-82e7-010486e92645.ta`），部署于根文件系统的 `/lib/optee_armtz/` 目录下。

---

## 6. 关联证据与技术规范

*   [[Evidence/k3_tee_security_specs]] - K3 芯片 TEE 内存基址、PMP 域与固件分区参数
*   [[Evidence/esos_rcpu_firmware_specs]] - K3 协处理器固件与启动依赖
*   [[Evidence/buildroot_bsp_specs]] - Buildroot 顶层构建与分区布局规格
