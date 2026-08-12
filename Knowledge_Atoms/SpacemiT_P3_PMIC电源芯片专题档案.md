---
type: knowledge_atom
title: "SpacemiT P3 PMIC 电源管理芯片专题档案"
status: needs_review
created: 2026-08-12
updated: 2026-08-12
aliases: ["SpacemiT P3 PMIC 专题", "SpacemiT P3 PMIC Topic", "spacemit_p3_pmic"]
domain: hardware_schematic_design
target_audience: [电源电路工程师, PCB Layout]
---
# SpacemiT P3 PMIC 电源管理芯片专题档案

> [!TIP]
> **💡 工程师导读与排坑焦点**：详解 P3 四相 Buck 32A 大电流 PMIC、5 种相位组合配置、WLCSP 超小封装与 I2C/SPI 调压设计。
> **目标读者**：`电源电路工程师 / PCB Layout` | **技术领域**：`hardware_schematic_design`

> [!IMPORTANT]
> **🆕 2026-08 新增知识原子**：本文档基于 Spacemit 官方 `docs-chip` 仓库新增的 `power_stone/p3/` 官方文档构建。

本专题档案汇总了 SpacemiT Power Stone 系列高性能伴随电源管理芯片 **P3 PMIC** 的核心物理参数、相位配置模式、降压电路拓扑与接口控制规范。

---

## 1. 芯片概述与四大核心优势

P3 是一款专为大电流、紧凑型场景（如边缘计算主板、无人机主控、AR/VR、光模块）设计的高性能四相降压（Buck）电源管理芯片：

*   **32 A 大电流 × 5 种相位配置**：四相并联最大输出电流达 **32 A**（峰值 **40 A**），支持 4+0、3+1、2+2、2+1+1、1+1+1+1 灵活输出架构。
*   **91% 峰值效率 × COT 快速响应**：采用 Constant On-Time (COT) 架构，负载突变快速稳压；支持 PFM/PWM 自动切换与强制 PWM 模式。
*   **WLCSP 超小封装**：80 焊球（Ball）、0.4 mm 间距的晶圆级 WLCSP 封装，满足高密度 PCB 布局。
*   **MTP 可编程时序 & 动态调压**：集成了 MTP 存储，支持灵活配置开关机时序，内置 3.4 MHz 高速 I2C / 30 MHz SPI 接口。

---

## 2. 核心物理与电气规格

| 规格项目 | 参数值 / 说明 |
| :--- | :--- |
| **输入电压 (VIN)** | 2.5 V 至 5.5 V |
| **输出电压 (VOUT)** | 0.25 V ~ 1.20 V (5 mV/step)；1.20 V ~ 1.83 V (10 mV/step) |
| **最大输出电流** | 单芯片最高 32 A 持续（40 A 峰值） |
| **峰值效率** | 91% (VIN = 3.6 V, VOUT = 0.85 V) |
| **斜率控制** | 各路 Buck 输出电压 Ramp-up / Ramp-down 斜率可调 |
| **内置 ADC** | 8 通道 12 位可配置监控 ADC |
| **扩展 GPIO** | 4 路多功能 GPIO 口 |
| **保护机制** | 欠压锁定 (UVLO)、输出短路保护 (SCP) 与过热保护 (OTP) |
| **工作温度** | -40 °C 至 85 °C |

---

## 3. 相位配置模式与拓扑结构

P3 支持 5 种不同的相位分配组合，以适应不同的处理器 Core + IO 电源轨组合：

1.  **4 + 0 模式**：4 相完全并联，单路独享 **32 A** 大电流输出（专门供给超级大核 Core）。
2.  **3 + 1 模式**：3 相并联 (24 A) + 1 相独立 (8 A)。
3.  **2 + 2 模式**：双路双相并联（16 A + 16 A），供给核心与 GPU/NPU。
4.  **2 + 1 + 1 模式**：2 相并联 (16 A) + 2 路单相独立 (8 A + 8 A)。
5.  **1 + 1 + 1 + 1 模式**：4 路完全独立单相 Buck 输出（8 A × 4）。

---

## 4. 关联原始参考文档

*   [P3 简介（官方原始文档）](../Sources/docs-chip/zh/power_stone/p3/p3_docs/root_overview.md)
*   [P3 PDF 产品简介](https://cdn-resource.spacemit.com/file/chip/P3/P3_brief_zh.pdf)
*   生态 PMIC 配合专题：[[Knowledge_Atoms/SpacemiT生态板卡与PMIC电源配合专题档案|SpacemiT 生态板卡与 PMIC 电源配合专题]]
