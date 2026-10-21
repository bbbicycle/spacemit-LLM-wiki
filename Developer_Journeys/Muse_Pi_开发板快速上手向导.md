---
type: developer_journey
title: "MUSE Pi 开发板快速上手向导"
status: needs_review
created: 2026-06-30
updated: 2026-10-21
aliases: ["Muse Pi 开发板快速上手向导", "Muse Pi Quick Start Guide", "muse_pi_quick_start"]
domain: hardware_schematic_design
source_file: "Sources/docs-product/zh/k1_series/k1_muse_pi/pi_user_guide.md"
source_commit: "bc640755145625cc20745f49861f82588863fca3"
source_section: "MUSE Pi 指南 电源输入/Boot Download Sel/初次设置/刷入固件；Llama.cpp 2"
source_resolution: partial
verification_status: unverified
source_checked_at: 2026-10-21
source_note: "覆盖标准 MUSE Pi 的连接与 FDL，LLM 使用当前官方 GGUF 路径；不把 Pro 的接口或旧演示脚本套入。 本轮为来源与关键步骤定向核对，未在实物执行；关联节点保留各自核验状态。"
source_related_file: ["Sources/docs-ai/zh/compute_stack/ai_compute_stack/llama.cpp.md"]
source_related_commit: ["2b3894e983a295ed0278bc625867e0c132e0e259"]
---
# MUSE Pi 开发板快速上手向导

本页面向 **K1 MUSE Pi 标准板**，不是 Pi Pro。先确认板卡修订与镜像版本，按 [MUSE Pi 用户指南](../Sources/docs-product/zh/k1_series/k1_muse_pi/pi_user_guide.md) 的实物图定位接口。

## 1. 硬件准备

连接 HDMI 显示器、USB 键鼠与网络。Type-C 供电要求匹配 PD3.0 的 12V 档位；拨码按该板 Boot Download Sel&JTAG Sel 表核对，不能把拨码 OFF/ON 直接等同于 SoC Strap 电平。排针与电平参考 [[Knowledge_Atoms/Muse_Pi_板级硬件设计专题]]。

## 2. 烧录固件

从官方发布渠道选择适用该板的 Bianbu Desktop/NAS 镜像，版本、烧录目标及工具按固件说明确认。

1. 断电时按住 DOWNLOAD（FDL），插电后松开；已开机时按住 FDL，短按 Reset 后松开。
2. 将支持数据通信的 USB 线接至刷机连接器，用 Titan 或固件对应的 fastboot 流程。
3. 烧录前核对镜像适用板型；本页不提供未经对应版本确认的自动分区/擦除命令。

## 3. 首次启动

按实际镜像的屏幕向导设置语言、时区、网络及用户；桌面组件和预装包随镜像变化。无法启动时先核对供电、介质和串口日志，不仅根据现象推断芯片损坏。

## 4. 运行本地模型

按 [Llama.cpp 指南](../Sources/docs-ai/zh/compute_stack/ai_compute_stack/llama.cpp.md) 核对当前 Bianbu 包 `llama.cpp-tools-spacemit`，K1 示例为 Qwen3-0.6B GGUF，线程数按 K1 条件不超过 4。先下载适配的量化模型，再用所安装版本的 `llama-cli`/`llama-bench` 运行。

旧固件或旧平台未提供该包时，原文另列 `llama-server` 包路径；先核对实际软件源和版本。

旧稿中的 `chat_inference.py` 和通用 ONNX 0.5B 命令未在当前声明来源确认，不再作为可直接执行步骤；ONNX 视觉模型应走专用推理指南。结果记录模型、精度、固件、内存与速度，不承诺任意板卡均达到同一 tokens/s。

- AI 架构与证据：[[Knowledge_Atoms/K1大模型本地推理与AI算力专题档案]]。
