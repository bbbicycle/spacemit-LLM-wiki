---
type: evidence
title: "SpacemiT RCPU (ESOS) 实时固件与启动依赖硬规范"
status: needs_review
created: 2026-08-10
updated: 2026-08-10
aliases: [esos_rcpu_firmware_specs, ESOS Firmware Specs, RCPU esos.elf]
domain: bsp_kernel_drivers
target_audience: [实时固件工程师, BSP 驱动]
---

# SpacemiT RCPU (ESOS) 实时固件与启动依赖硬规范

> [!TIP]
> **💡 工程师导读与排坑焦点**：记录 RCPU esos.elf 固件职责、HDMI Audio 转发与内核引导硬依赖红线。
> **目标读者**：`实时固件工程师 / BSP 驱动` | **技术领域**：`bsp_kernel_drivers`

本文档记录 SpacemiT K1 与 K3 处理器中伴随实时 CPU（RCPU）的固件文件 `esos.elf` / `esos` 模块的软硬件职责及系统引导启动红线依赖规范。

---

## 1. ESOS RCPU 核心职责与软硬件架构

| 属性名称 | 物理说明与规格 |
| :--- | :--- |
| **处理器核心** | RCPU (Real-Time RISC-V Co-processor) 独立实时协处理器 |
| **固件二进制路径 (K1)** | `board/spacemit/k1/target_overlay/lib/firmware/esos.elf` (编译注入 initramfs `/lib/firmware/`) |
| **源码路径 (K3)** | `package-src/esos` (Real-Time Operating System 实时小 CPU 代码) |
| **硬件控制职责** | 1. 负责部分底层硬件模块的上电与时钟初始化<br>2. **HDMI Audio 中断转发与硬件音频流同步**<br>3. 实时性敏感接口的 GPIO/PWM 中断离线响应 |

---

## 2. 系统启动依赖与红线告警

> [!CAUTION]
> **启动硬红线依赖 (Hard Boot Dependency)**：
> Linux 内核在加载设备驱动过程中**强依赖 `esos.elf` 实时固件**。
> 若制作第三方 Linux 发行版或自定义根文件系统 (Rootfs) 时缺少安装 `esos.elf` 至 `/lib/firmware/` 目录，系统在 Kernel 引导阶段将触发驱动挂起死锁，导致**无法成功启动至命令行 (Boot Fail)**！

---

## 3. 依赖组件验证检查清单

制作独立 Linux 发行版（如 Debian / Ubuntu / Custom Rootfs）时，启动至命令行的最小核心组件树必须包含：

1. `opensbi` —— 机器模式 (M-Mode) 固件
2. `uboot-2022.10` —— 引导加载程序
3. `linux-6.6` (K1) / `linux-6.18` (K3) —— 操作系统内核
4. **`esos.elf`** —— RCPU 实时刻固件（绝对不可裁剪）
