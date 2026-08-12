---
type: knowledge_atom
title: "K3 安全启动 (Secure Boot) 开发专题档案"
status: needs_review
created: 2026-08-10
updated: 2026-08-10
aliases: ["K3 Secure Boot 专题", "K3 Secure Boot Development Topic", "k3_secure_boot"]
domain: bsp_kernel_drivers
target_audience: [BSP 工程师, 安全固件工程师]
---
# K3 安全启动 (Secure Boot) 开发专题档案

> [!TIP]
> **💡 工程师导读与排坑焦点**：详解 K3 芯片安全启动信任链架构、eFuse 不可逆烧录约束、FIT 签名容器与密钥管理规范。
> **目标读者**：`BSP 工程师 / 安全固件工程师` | **技术领域**：`bsp_kernel_drivers`

> [!IMPORTANT]
> **🆕 2026-08 新增知识原子**：本文档基于 Spacemit 官方 `docs-buildroot` 仓库新增的 `secureboot.md` 构建。

本专题档案梳理了 SpacemiT K3 芯片安全启动 (Secure Boot) 机制的核心架构、密钥体系、eFuse 烧录约束与开发调试要点。

---

## 1. 信任链总览

K3 安全启动建立了一条**从硬件到软件的完整信任链 (Chain of Trust)**：

```
BootROM → FSBL → OpenSBI / U-Boot → Linux 内核
```

*   **BootROM**：芯片内置不可修改的引导代码，负责验证 FSBL 固件签名。
*   **FSBL (First Stage Boot Loader)**：承载 FSBL 证书链结构，验证后续固件的合法性。
*   **OpenSBI / U-Boot**：通过 FIT (Flattened Image Tree) 签名容器机制验证内核镜像。
*   **Linux 内核**：最终被信任链末端加载运行。

---

## 2. 密钥体系与 FIT 签名容器

### 2.1 密钥层级
安全启动使用非对称加密体系，需要准备以下密钥与证书：
*   **ROTPK (Root of Trust Public Key)**：根信任公钥，其哈希值 (ROTPKH) 将被烧录到芯片 eFuse 中。
*   **FSBL 签名密钥**：用于签名 FSBL 固件。
*   **U-Boot / 内核签名密钥**：用于 FIT 签名容器中的镜像签名。

### 2.2 FIT 签名容器
*   U-Boot 使用 FIT 格式封装内核、DTB 等组件，并在容器中嵌入签名信息。
*   公钥通过**静态注入机制**编译进 U-Boot DTB 中，实现启动时的离线验签。

### 2.3 公钥注入机制
*   公钥在编译阶段被注入到 U-Boot 的设备树 (DTB) 中，而非运行时动态加载。
*   板型 FIT config 选择通过 DTB 中的配置节点实现，支持多板型共用同一镜像。

---

## 3. eFuse 烧录约束（不可逆操作）

> [!CAUTION]
> **eFuse 烧录为物理不可逆操作**。一旦写入，无法擦除或修改。错误烧录将导致芯片永久无法启动。

*   **eFuse Bank 4**：存储 ROTPKH（根信任公钥哈希），是安全启动的硬件锚点。
*   **密钥槽位定义**：eFuse 中定义了多个密钥槽位，支持密钥轮换策略。
*   **启用前务必在测试环境中完成全流程验证**，确认密钥对、签名流程、启动链路全部正确后，再进行量产 eFuse 烧录。

---

## 4. 启用安全启动的两种路径

### 4.1 方式一：deb 构建路径（推荐）
*   通过 `KEY_DIR` 环境变量指定签名密钥目录，构建系统自动完成 FIT 签名与公钥注入。
*   适合 CI/CD 自动化集成与 OTA 升级场景。

### 4.2 方式二：镜像构建路径
*   直接在 SDK 镜像编译流程中集成签名步骤。
*   适合离线量产场景。

---

## 5. 签名模式的行为差异

启用签名模式后，U-Boot 的启动行为会发生以下变化：
*   **不读取外部环境变量文件**：签名模式下 U-Boot 不会加载 `uEnv.txt` 等外部配置，防止被篡改。
*   **内核镜像名与启动命令**：使用签名后的 FIT 镜像路径启动，与非签名模式的路径不同。

---

## 6. 常见问题 (FAQ)

*   **可以使用自定义密钥名吗？** — 可以，但需要在 `KEY_DIR` 中按规范放置。
*   **安全启动可以关闭吗？** — 未烧录 eFuse 前可以关闭；eFuse 烧录后**无法关闭**。
*   **安全启动对启动耗时的影响？** — 签名验证会增加约数百毫秒的启动延迟。
*   **多板型能否共用同一签名镜像？** — 可以，通过 FIT config 节点选择不同板型配置。

---

## 7. 关联原始参考文档

*   [K3 安全启动开发指南 - 官方原始文档](../Sources/docs-buildroot/zh/k3_buildroot/device/secureboot.md)
*   芯片级启动机制：[[Knowledge_Atoms/K3启动模式与Strap管脚配置专题档案|K3 启动模式与 Strap 管脚配置专题]]
*   BSP 编译与内核定制：[[Knowledge_Atoms/Buildroot_嵌入式系统定制与内核编译专题档案|Buildroot 嵌入式系统定制与内核编译专题]]
