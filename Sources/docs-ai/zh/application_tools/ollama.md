<!--
 * Copyright 2022-2023 SPACEMIT. All rights reserved.
 * Use of this source code is governed by a BSD-style license
 * that can be found in the LICENSE file.
 * 
 * @Author: David(qiang.fu@spacemit.com)
 * @Date: 2026-05-13 09:53:15
 * @LastEditTime: 2026-05-13 14:16:05
 * @FilePath: \doc\docs-ai\zh\application_tools\ollama.md
 * @Description: 
-->
---
sidebar_position: 5
---

# Ollama

**Ollama** 是一款开源跨平台大语言模型（LLM）本地化部署工具，专注于简化 LLM 在本地环境中的运行、管理和推理流程。它支持用户通过简单命令在个人设备（如 PC、边缘服务器）上直接部署和调用预训练模型（如 LLaMA、DeepSeek 等），无需依赖云端服务或高性能 GPU。

## 平台支持情况

|      平台 & 系统       |       是否支持     |
|-----------------------|-----------------------|
| K1 Buildroot          | ❌ 不支持               |
| K1 OpenHarmony     | ❌ 不支持              |
| K1 Bianbu LXQT/GNOME    | ✅ 支持             |
| K3 Buildroot          | ❌ 不支持              |
| K3 OpenHarmony     | ❌ 不支持              |
| K3 Bianbu LXQT/GNOME  | ❌ 不支持加速               |

## 安装

```shell
sudo apt update
sudo apt install spacemit-ollama-toolkit
```

验证安装：

```shell
ollama list
```

最后输出 `NAME  ID  SIZE  MODIFIED` 表示安装成功。

验证版本（确保为 0.0.8 或以上版本）：

```shell
sudo apt show spacemit-ollama-toolkit
```

确认版本为 0.0.8 或以上，以支持新的模型格式和直接拉取功能。

## 下载模型

### 方式一：直接拉取（推荐，需要 0.0.8+ 版本）

从 spacemit-ollama-toolkit 0.0.8 版本开始，新增支持 **q4_K_M** 和 **q4_1** 模型格式，可以直接使用 `ollama pull` 命令从 Ollama 官网拉取 q4_K_M 格式的模型，并享受加速功能：

```shell
# 直接拉取 q4_K_M 格式的模型（推荐）
ollama pull qwen3:0.6b
```

### 方式二：手动制作模型

因为 **q4_0** 的模型在 K1 开发板上也能发挥很好的性能，您也可以选择手动下载和制作模型。在 modelscope 上选择想要下载的 gguf 类型模型，下载 q4_0 量化精度的模型到开发板或者 musebook。

下方是模型制作的示例：

```shell
sudo apt install wget
wget https://modelscope.cn/models/second-state/Qwen2.5-0.5B-Instruct-GGUF/resolve/master/Qwen2.5-0.5B-Instruct-Q4_0.gguf ~/
wget https://archive.spacemit.com/spacemit-ai/modelfile/qwen2.5:0.5b.modelfile ~/
cd ~/
ollama create qwen2.5:0.5b -f qwen2.5:0.5b.modelfile
```

## 使用

```shell
# 运行直接拉取的模型
ollama run qwen3:0.6b

# 或运行手动制作的模型
ollama run qwen2.5:0.5b
```
