---
type: developer_journey
title: "K3 Pico-ITX 开发板快速上手向导"
status: needs_review
created: 2026-06-30
updated: 2026-06-30
aliases: ["K3 Pico 开发板快速上手向导", "K3 Pico Quick Start Guide", "k3_pico_quick_start"]
---
# K3 Pico-ITX 开发板快速上手向导

本向导旨在帮助开发者快速熟悉 K3 Pico-ITX 迷你 AI 计算机，包括如何使用全功能 Type-C 单线点亮设备、烧录 Bianbu 3.0 系统、配置 UEFI 启动，并跑通 60 TOPS 算力的本地大语言模型。

---

## 阶段 1：点亮设备（推荐单线方案）

K3 Pico-ITX 支持极其简洁的**单线缆（Single-Cable）**启动方案：
* **硬要求**：准备一台具备 **65W 或更大功率**、且支持 **Type-C 反向充电**的显示器。
* **连接步骤**：使用一根**全功能 Type-C 线缆**（必须支持高功率供电与 DP 替代模式），直接连接显示器与 K3 Pico-ITX 的 **全功能 Type-C 接口 (Pin 17)**。
* **效果**：显示器将同时为板卡提供 65W 电源，并接收板卡输出的 4K@60Hz 视频信号，一屏一板一线即可点亮算力。

> [!NOTE]
> 若显示器不支持反向供电，请通过扩展坞接入全功能 Type-C 口，并在扩展坞上接入 PD 65W 电源与 HDMI/DP 线。或者，使用 2-Pin ATX 接口提供 12V @ 5A~7A 直流供电。

---

## 阶段 2：烧录操作系统 (Bianbu 3.0)

K3 Pico-ITX 预装了 Bianbu 操作系统。如果需要重装系统（支持 U-Boot 版本或 UEFI 体验版）：

### 步骤 1：准备烧录接口
1. 准备一根支持高速数据通讯的 Type-C 线。
2. 将线的一端连接到主板的 **DRD Type-C 烧录接口 (Pin 18)**，另一端连接至上位机电脑。
   > [!WARNING]
   > 烧录接口（Pin 18）**不可向内供电**。烧录过程中，必须保持全功能 Type-C 口或 ATX 口处于正常供电状态。

### 步骤 2：进入烧录模式
* **若设备处于关机状态**：按住主板侧边的 **FDL 烧录键** 不松开 ➡️ 插入电源上电 ➡️ 松开 **FDL 键**。
* **若设备处于开机状态**：按住 **FDL 键** 不松开 ➡️ 短按一下 **RST 复位键** ➡️ 松开 **FDL 键**。

### 步骤 3：执行烧录
在上位机上使用进迭时空官方刷机工具 **Titan** 或通过终端执行 `fastboot` 刷机命令，将系统镜像烧录至板载 UFS2.2 本地存储或 M.2 NVMe SSD。

---

## 阶段 3：UEFI 启动与配置体验

K3 Pico-ITX 提供了完整的 UEFI 体验版：
1. **进入设置**：在上电开机 3 秒内，按下键盘上的 **F2** 键，即可进入 UEFI 蓝底配置界面。
2. **启动介质管理 (Boot Manager)**：可在此菜单中自由选择从 `NVMe SSD`、`USB 外部硬盘` 或 `UFS 闪存` 启动。
3. **更改启动顺序**：在 `Boot Maintenance Manager` ➡️ `Boot Options` ➡️ `Change Boot Order` 中，使用 `<+>` 和 `<->` 调整介质优先级，按 `<F10>` 保存。

---

## 阶段 4：跑通 60 TOPS 本地大模型

K3 Pico-ITX 具备 60 TOPS 的通用 AI 算力与计算-智算统一内存架构，最高支持 **300 亿 (30B)** 参数级别的大模型在本地部署。

### 步骤 1：更新 Bianbu 软件源
```bash
sudo apt update
sudo apt install python3-onnxruntime-k3 llama.cpp -y
```

### 步骤 2：下载并部署 Llama-3-8B-GGUF
利用统一内存架构，大模型推理不会因为显存不足而受限。我们可以直接使用 `llama.cpp` 加载 **Llama-3-8B (INT4)** 模型：
```bash
llama-cli -m ./Meta-Llama-3-8B-Instruct-Q4_K_M.gguf -p "介绍一下 RISC-V 架构" -n 128
```
系统将自动调度 K3 内部的 A100 智算核，结合 64-bit LPDDR5 的高带宽，实现极速流畅的本地对话。

---

## 5. 关联技术专题与规格

* 硬件避坑与优先级：[[Knowledge_Atoms/K3_Pico_板级硬件设计专题|K3 Pico-ITX 板级硬件设计与调试专题]]
* 芯片级 AI 部署指南：[[Knowledge_Atoms/K3大模型本地推理与AI算力专题档案|K3 大模型本地推理与 AI 算力专题]]
* 官方完整指南：[K3 Pico 使用指南（原始文件）](file:///Users/bicycle/Spacemit%20LLM%20Wiki/Sources/docs-product/zh/k3_pico/pico_user_guide.md)
