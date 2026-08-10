<!--
 * Copyright 2022-2023 SPACEMIT. All rights reserved.
 * Use of this source code is governed by a BSD-style license
 * that can be found in the LICENSE file.
 *
 * @Author: David(qiang.fu@spacemit.com)
 * @Date: 2026-03-09 14:26:58
 * @LastEditTime: 2026-05-27 20:31:39
 * @FilePath: \doc\docs-ai\zh\solutions\aicomputer_solution\claude.md
 * @Description:
-->
sidebar_position: 7

# Claude Code(云端算力)

**Claude Code** 是一个用于智能体编程的命令行工具,由**Anthropic**开发。它允许开发者通过命令行界面与 Claude AI 进行交互,实现代码生成、调试、重构等智能编程辅助功能。

## 平台支持情况

|      平台 & 系统       |       是否支持     |
|-----------------------|-----------------------|
| K1 Buildroot          | ❌ 不支持              |
| K1 OpenHarmony     | ❌ 不支持              |
| K1 Bianbu LXQT/GNOME    | ✅ 支持            |
| K3 Buildroot          | ❌ 不支持              |
| K3 OpenHarmony     | ❌ 不支持              |
| K3 Bianbu LXQT/GNOME  | ✅ 支持                |

## 1. 安装

### 1.1. 安装 npm

```shell
sudo apt install npm
```

### 1.2. 安装 Claude Code

```bash
sudo npm i -g @anthropic-ai/claude-code@2.1.112
```

如果网络受限，可以尝试加入镜像源

```bash
sudo npm i --registry=https://registry.npmmirror.com -g @anthropic-ai/claude-code@2.1.112
```

**注意：目前支持最高版本是2.1.112，不要安装高于这个的版本**

验证安装:

```bash
claude --version
```

输出版本号表示安装成功：
![](../static/claude-version.png)

**注意：对于K1需要安装nvm并切换node.js版本**

```bash
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
NVM_NODEJS_ORG_MIRROR=https://archive.spacemit.com/nodejs/k1 nvm install 22
nvm use 22
```

## 2. 配置

### 2.1. 设置环境变量

获取到供应商提供的URL和KEY后，导入到~/.bashrc中，如下：

```bash
cat >> ~/.bashrc << 'EOF'
export ANTHROPIC_BASE_URL="供应商URL"
export ANTHROPIC_AUTH_TOKEN="生成的API_KEY"
EOF
source ~/.bashrc
```

### 2.2. 配置 API Key 自动批准

```bash
(cat ~/.claude.json 2>/dev/null || echo 'null') | jq --arg key "${ANTHROPIC_API_KEY: -20}" '(. // {}) | .customApiKeyResponses.approved |= ([.[]?, $key] | unique)' > ~/.claude.json.tmp && mv ~/.claude.json.tmp ~/.claude.json
```

## 3. 使用

启动 Claude Code 交互式会话:

```shell
claude
```

启动界面如下:
![](../static/claude-use.png)

Say Hello：
![](../static/claude-hello.png)

执行/model切换模型：
![](../static/claude-model.png)


在交互式会话中,您可以:
- 询问编程问题
- 请求代码生成和优化
- 进行代码调试和重构
- 获取技术建议和最佳实践

输入 `/exit` 退出会话。

## 4. 举一个例子

- 输入“帮我写一个程序，调用onnxruntime，下载并使用resnet50模型进行分类，显示分类结果”，Claude开始运行
![](../static/claude-demo1.png)

- Claude完成了编码，并提供了操作步骤：
![](../static/claude-demo2.png)

- 执行“run it”，出现异常，Claude自行修复异常中
![](../static/claude-demo3.png)

- Claude修复完异常后，程序可以正常执行
![](../static/claude-demo4.png)

- 手动执行程序，可正常执行
![](../static/claude-demo5.png)

## 5. 对接端侧AI(简单尝试，无需关注)

### 5.1. 设置环境变量

```bash
cat >> ~/.bashrc << 'EOF'
export ANTHROPIC_BASE_URL="http://localhost:8080"
export ANTHROPIC_AUTH_TOKEN="llama"
EOF
source ~/.bashrc
```

### 5.2. 配置 API Key 自动批准

```bash
(cat ~/.claude.json 2>/dev/null || echo 'null') | jq --arg key "${ANTHROPIC_API_KEY: -20}" '(. // {}) | .customApiKeyResponses.approved |= ([.[]?, $key] | unique)' > ~/.claude.json.tmp && mv ~/.claude.json.tmp ~/.claude.json
```
### 5.3. 拉起llama-server

```bash
llama-server -m Qwen2.5-0.5B-Instruct-Q4_0.gguf -t 8 --host 127.0.0.1 --port 8080 --ctx-size 153600 --n-gpu-layers 0 --batch-size 512 --metrics --no-mmap
```

**注意：因Claude Code的输入上下文很长，--ctx-size需要配置大一些，15360无法满足需求，这里配置了153600**

### 5.4. 运行claude

启动claude并hello：

```bash
claude --model qwen2.5:0.5b
```

![](../static/claude-llama1.png)

hello的耗时特别长，prefill了17000+tokens

![](../static/claude-llama2.png)

后面写算法的耗时明显变短，但准确度欠佳
![](../static/claude-llama3.png)
