---
type: developer_journey
title: "MUSE Pi 开发板快速上手向导"
status: needs_review
created: 2026-06-30
updated: 2026-06-30
aliases: ["Muse Pi 开发板快速上手向导", "Muse Pi Quick Start Guide", "muse_pi_quick_start"]
domain: hardware_schematic_design
---
# MUSE Pi 开发板快速上手向导

本向导旨在帮助开发者在最短时间内完成 K1 MUSE Pi 开发板的硬件连接、操作系统烧录、首次开机配置，并跑通本地大语言模型（LLM）。

---

## 阶段 1：硬件准备与连接

在上电前，请正确连接以下外设：
1. **显示器**：通过标准 HDMI 线缆连接至板载 `HDMI Type-A` 接口。
2. **输入设备**：插上 USB 键盘和鼠标。
3. **网络**：接入 RJ45 网线至千兆网口，或安装好随包装附赠的 Wi-Fi SMA 天线。
4. **启动拨码**：检查板载双位拨码开关是否处于默认的 **OFF + OFF** 位置（即从 TF 卡或 eMMC 启动）。

---

## 阶段 2：操作系统烧录 (Bianbu OS)

MUSE Pi 预装或支持 Bianbu Desktop 桌面系统。若需要重新烧录：

### 步骤 1：获取固件与工具
* 下载最新的 [MUSE Pi Bianbu 镜像](https://spacemit.com/community/resources-download/)。
* 在上位机（PC）上安装进迭时空官方刷机工具 **Titan**（支持 Windows/Linux/macOS）。

### 步骤 2：进入刷机（FEL）模式
1. **断电状态下**：按住板载侧边的 **Download 烧录按键 (FDL)** 不松开。
2. **给设备上电**：使用 Type-C 供电线连接支持 **PD3.0 (12V/3A)** 的电源适配器。
3. **连接电脑**：使用 Type-C 数据线将 MUSE Pi 的 Type-C 接口连接至上位机电脑。
4. **松开按键**：松开 **FDL 按键**。此时电脑上的 Titan 工具应能识别到处于 FEL 模式的设备。

### 步骤 3：执行烧录
在 Titan 软件中加载下载好的 `.zip` 格式固件包，点击“开始烧录”，等待进度条完成至 100% 后设备会自动重启。

---

## 阶段 3：首次启动与系统配置

系统首次开机后，显示器将输出 Bianbu Desktop 的配置向导：
1. **语言与键盘**：选择“简体中文”与“标准美国英语键盘”。
2. **时区**：选择 `Asia/Shanghai`。
3. **网络连接**：若使用无线，在此步骤中连接您的 Wi-Fi 网络。
4. **创建用户**：设置您的用户名和登录密码。
5. **进入桌面**：配置完成后，系统将载入轻量级的 LXQt 桌面环境。

---

## 阶段 4：部署本地大语言模型 (LLM)

MUSE Pi 搭载的 K1 芯片在 CPU 内融合了 2.0 TOPS 的 AI 算力，支持零成本部署 1B / 0.5B 参数级别的端侧模型。

### 步骤 1：安装运行时环境
在 Bianbu OS 终端中执行以下命令，安装进迭时空优化的 ONNX Runtime 与 Python 依赖：
```bash
sudo apt update
sudo apt install python3-pip python3-onnxruntime -y
```

### 步骤 2：获取量化模型
从官方社区或 HuggingFace 下载经过 `smt.vmadot` 指令集量化编译的 **Qwen-1.5-0.5B-Chat-INT8** 模型。

### 步骤 3：运行推理
使用 SDK 附带的极简推理脚本启动模型：
```bash
python3 chat_inference.py --model ./qwen1.5-0.5b-chat-int8.onnx
```
系统将直接利用 K1 芯片的 Cluster 0（带 AI 加速 TCM 缓存的 4 核）进行极速端侧推理，速度可达 **>10 Tokens/s**。

---

## 5. 关联技术专题与规格

* 硬件避坑与调试：[[Knowledge_Atoms/Muse_Pi_板级硬件设计专题|MUSE Pi 板级硬件设计与调试专题]]
* 芯片级 AI 部署指南：[[Knowledge_Atoms/K1大模型本地推理与AI算力专题档案|K1 大模型本地推理与 AI 算力专题]]
* 官方完整指南：[MUSE Pi 使用指南（原始文件）](file:///Users/bicycle/Spacemit%20LLM%20Wiki/Sources/docs-product/zh/k1_muse_pi/pi_user_guide.md)
