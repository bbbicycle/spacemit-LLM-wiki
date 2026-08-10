---
sidebar_position: 7
---

# Claude Code (Cloud Compute)

**Claude Code** is an AI-driven command-line coding tool developed by **Anthropic**. It provides a terminal interface for interacting with Claude and supports AI-assisted development workflows such as code generation, debugging, refactoring, and technical guidance.

## Platform Support

| Platform / OS        | Support |
| -------------------- | ------- |
| K1 Buildroot         | ❌ No   |
| K1 OpenHarmony       | ❌ No   |
| K1 Bianbu LXQT/GNOME | ✅ Yes  |
| K3 Buildroot         | ❌ No   |
| K3 OpenHarmony       | ❌ No   |
| K3 Bianbu LXQT/GNOME | ✅ Yes  |

## 1. Installation

### 1.1 Install npm

```bash
sudo apt install npm
```

### 1.2 Install Claude Code

```bash
sudo npm i -g @anthropic-ai/claude-code@2.1.112
```

If access to the default npm registry is restricted, install from a mirror registry instead.

```bash
sudo npm i --registry=https://registry.npmmirror.com -g @anthropic-ai/claude-code@2.1.112
```

**Note:** Version 2.1.112 is the currently supported release. Do not install a later version.

Verify the installation:

```bash
claude --version
```

If a version number is returned, Claude Code has been installed successfully.

![Claude Code version](../static/claude-version.png)

**Note:** On K1, install nvm and switch to the required Node.js version before using Claude Code.

```bash
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
NVM_NODEJS_ORG_MIRROR=https://archive.spacemit.com/nodejs/k1 nvm install 22
nvm use 22
```

## 2. Configuration

### 2.1 Set Environment Variables

After obtaining the provider URL and API key, add them to `~/.bashrc` as follows:

```bash
cat >> ~/.bashrc << 'EOF'
export ANTHROPIC_BASE_URL="Provider URL"
export ANTHROPIC_AUTH_TOKEN="Generated API key"
EOF
source ~/.bashrc
```

### 2.2 Configure Automatic API Key Approval

```bash
(cat ~/.claude.json 2>/dev/null || echo 'null') | jq --arg key "${ANTHROPIC_API_KEY: -20}" '(. // {}) | .customApiKeyResponses.approved |= ([.[]?, $key] | unique)' > ~/.claude.json.tmp && mv ~/.claude.json.tmp ~/.claude.json
```

## 3. Basic Usage

Start an interactive Claude Code session:

```bash
claude
```

The startup screen appears below.

![Claude Code startup interface](../static/claude-use.png)

Example greeting using the `Say Hello` prompt:

![Claude Code hello example](../static/claude-hello.png)

Use `/model` to switch models.

![Claude Code model selection](../static/claude-model.png)

During an interactive session, Claude Code can help with:

- Answering programming questions
- Generating and optimizing code
- Debugging and refactoring existing code
- Providing technical recommendations and best practices

Enter `/exit` to end the session.

## 4. Example Workflow

This example demonstrates Claude Code generating and debugging an ONNX Runtime image-classification program.

- Enter the following request:

   ```text
   Write a program that calls ONNX Runtime, downloads and uses the ResNet50 model for image classification, and displays the classification result.
   ```

   Claude Code starts analyzing the request and generating the program.

   ![Claude Code demo request](../static/claude-demo1.png)

- Claude Code completes the implementation and provides the execution steps.

   ![Claude Code generated steps](../static/claude-demo2.png)

- Run the program. If an exception occurs, Claude Code analyzes the error and applies a fix.

   ![Claude Code debugging exception](../static/claude-demo3.png)

- After the fix, the program runs successfully.

   ![Claude Code fixed program](../static/claude-demo4.png)

- The program can also be executed manually and produces the expected result.

   ![Claude Code manual execution result](../static/claude-demo5.png)

## 5. Connecting to On-Device AI: Basic Trial

Claude Code can also connect to a local on-device inference service for basic experimentation. This section is optional and serves as a simple local trial.

### 5.1 Set Environment Variables

```bash
cat >> ~/.bashrc << 'EOF'
export ANTHROPIC_BASE_URL="http://localhost:8080"
export ANTHROPIC_AUTH_TOKEN="llama"
EOF
source ~/.bashrc
```

### 5.2 Configure Automatic API Key Approval

```bash
(cat ~/.claude.json 2>/dev/null || echo 'null') | jq --arg key "${ANTHROPIC_API_KEY: -20}" '(. // {}) | .customApiKeyResponses.approved |= ([.[]?, $key] | unique)' > ~/.claude.json.tmp && mv ~/.claude.json.tmp ~/.claude.json
```

### 5.3 Start llama-server

```bash
llama-server -m Qwen2.5-0.5B-Instruct-Q4_0.gguf -t 8 --host 127.0.0.1 --port 8080 --ctx-size 153600 --n-gpu-layers 0 --batch-size 512 --metrics --no-mmap
```

**Note:** Claude Code uses a long input context, so `--ctx-size` must be set high enough. This example uses 153600 because 15360 is not sufficient for this scenario.

### 5.4 Run Claude Code

Start Claude Code with the local model and run a simple greeting test.

```bash
claude --model qwen2.5:0.5b
```

![Claude Code with llama-server](../static/claude-llama1.png)

The initial greeting may take longer because the model prefill can exceed 17,000 tokens.

![Claude Code long prefill example](../static/claude-llama2.png)

Subsequent algorithm-generation tasks are noticeably faster, but output quality may still be constrained by the compact local model.

![Claude Code local algorithm example](../static/claude-llama3.png)
