<!--
 * Copyright 2022-2023 SPACEMIT. All rights reserved.
 * Use of this source code is governed by a BSD-style license
 * that can be found in the LICENSE file.
 * 
 * @Author: David(qiang.fu@spacemit.com)
 * @Date: 2026-05-13 09:53:15
 * @LastEditTime: 2026-05-13 14:16:40
 * @FilePath: \doc\docs-ai\zh\application_tools\llamaindex.md
 * @Description: 
-->
---
sidebar_position: 8
---

# LlamaIndex

## 平台支持情况

|      平台 & 系统       |       是否支持     |
|-----------------------|-----------------------|
| K1 Buildroot          | ❌ 不支持               |
| K1 OpenHarmony     | ❌ 不支持              |
| K1 Bianbu LXQT/GNOME    | ❌ 不支持             |
| K3 Buildroot          | ❌ 不支持              |
| K3 OpenHarmony     | ❌ 不支持              |
| K3 Bianbu LXQT/GNOME  | ✅ 支持                |

## 安装

### 1.1. 安装依赖

安装基本依赖：
```bash
sudo apt update
sudo apt install python3-venv python3-dev libffi-dev libssl-dev pkg-config libjpeg-dev zlib1g-dev libtiff-dev libfreetype6-dev liblcms2-dev libwebp-dev
```

安装rust：
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
source ~/.cargo/env
rustc --version
```

有如下打印说明安装成功：
![](../static/rust-install.png)

### 1.2. 安装langchain

```bash
python3 -m venv ./llamaindex_venv
source llamaindex_venv/bin/activate
pip install llama-index
```

## 使用

```bash
source llamaindex_venv/bin/activate
python -c "from llama_index.core import VectorStoreIndex, SimpleDirectoryReader; print('llama-index  导入成功！')"
```

![](./static/llamaindex-demo.png)