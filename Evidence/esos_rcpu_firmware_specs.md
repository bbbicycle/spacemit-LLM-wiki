---
type: evidence
title: "SpacemiT RCPU (ESOS) 实时固件与启动依赖硬规范"
status: "needs_review"
verification_status: unverified
external_use: false
source_file: "Sources/docs-buildroot/zh/k1_buildroot/faqs.md"
source_origin: "https://github.com/spacemit-com/docs-buildroot"
source_commit: "6d4c2a65989f0b61819bebfbc85f77d72732745e"
source_section: "组件；制作一个Linux发行版需要集成哪些组件？"
source_resolution: partial
source_checked_at: 2026-10-13
source_note: "已核对 K1/K3 启动依赖和固件文件名；额外 GPIO/PWM 职责未定位。"
source_related_file: ["Sources/docs-buildroot/zh/k3_buildroot/faqs.md"]
source_related_commit: ["6d4c2a65989f0b61819bebfbc85f77d72732745e"]
created: 2026-08-10
updated: "2026-10-20"
aliases: [esos_rcpu_firmware_specs, ESOS Firmware Specs, RCPU esos.elf]
domain: bsp_kernel_drivers
target_audience: [实时固件工程师, BSP 驱动]
---

# SpacemiT RCPU (ESOS) 实时固件与启动依赖硬规范

> [!TIP]
> **💡 工程师导读与排坑焦点**：记录 RCPU esos.elf 固件职责、HDMI Audio 转发与内核引导硬依赖红线。
> **目标读者**：`实时固件工程师 / BSP 驱动` | **技术领域**：`bsp_kernel_drivers`

本文档记录 SpacemiT K1 与 K3 处理器的 RCPU 固件启动依赖。K1 使用 `esos.elf`，K3 的 ESOS 构建输出为 `rt24_os0_rcpu.elf` 与 `rt24_os1_rcpu.elf`，不可跨代套用文件名。

---

## 1. ESOS RCPU 核心职责与软硬件架构

| 属性名称 | 物理说明与规格 |
| :--- | :--- |
| **处理器核心** | RCPU (Real-Time RISC-V Co-processor) 独立实时协处理器 |
| **固件二进制路径 (K1)** | `board/spacemit/k1/target_overlay/lib/firmware/esos.elf` (编译注入 initramfs `/lib/firmware/`) |
| **固件二进制文件 (K3)** | `rt24_os0_rcpu.elf` 与 `rt24_os1_rcpu.elf`，安装到 initramfs 的 `/lib/firmware/` |
| **源码路径 (K3)** | `package-src/esos` (Real-Time Operating System 实时小 CPU 代码) |
| **硬件控制职责** | 1. 负责部分底层硬件模块的上电与时钟初始化<br>2. **HDMI Audio 中断转发与硬件音频流同步**<br>3. 实时性敏感接口的 GPIO/PWM 中断离线响应 |

---

## 2. 系统启动依赖与红线告警

> [!CAUTION]
> **启动硬红线依赖 (Hard Boot Dependency)**：
> 官方 K1/K3 FAQ 均说明 Linux 内核依赖相应 RCPU 固件，缺失会无法启动。
> K1 需在 initramfs `/lib/firmware/` 安装 `esos.elf`；K3 则需安装 `rt24_os0_rcpu.elf` 和 `rt24_os1_rcpu.elf`。具体故障机制未在该 FAQ 中说明，不应一概描述为驱动死锁。

---

## 3. 依赖组件验证检查清单

制作独立 Linux 发行版（如 Debian / Ubuntu / Custom Rootfs）时，启动至命令行的最小核心组件树必须包含：

1. `opensbi` —— 机器模式 (M-Mode) 固件
2. `uboot-2022.10` —— 引导加载程序
3. `linux-6.6` (K1) / `linux-6.18` (K3) —— 操作系统内核
4. **RCPU 实时固件** —— K1 为 `esos.elf`；K3 为 `rt24_os0_rcpu.elf` 与 `rt24_os1_rcpu.elf`，均需按对应 SDK 放入 initramfs
