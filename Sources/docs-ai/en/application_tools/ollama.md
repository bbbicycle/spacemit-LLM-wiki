---
sidebar_position: 5
---

# Ollama

**Ollama** is an open-source, cross-platform tool for running large language models (LLMs) locally. It streamlines the deployment, management, and inference workflow for LLMs, letting you run pre-trained models such as LLaMA and DeepSeek directly on a personal device or edge server with a single command — no cloud service or high-end GPU required.

## Platform Support

| Platform & OS | Supported |
|---|---|
| K1 Buildroot | ❌ Not supported |
| K1 OpenHarmony | ❌ Not supported |
| K1 Bianbu LXQT/GNOME | ✅ Supported |
| K3 Buildroot | ❌ Not supported |
| K3 OpenHarmony | ❌ Not supported |
| K3 Bianbu LXQT/GNOME | ❌ Acceleration not supported |

## Installation

```shell
sudo apt update
sudo apt install spacemit-ollama-toolkit
```

Verify the installation:

```shell
ollama list
```

A header line reading `NAME  ID  SIZE  MODIFIED` confirms a successful installation.

Verify the version (0.0.8 or later is required):

```shell
sudo apt show spacemit-ollama-toolkit
```

Version 0.0.8 or later is required to support the new model formats and direct-pull functionality.

## Downloading Models

### Option 1: Direct Pull (Recommended — requires v0.0.8+)

Starting with `spacemit-ollama-toolkit` v0.0.8, the **q4_K_M** and **q4_1** model formats are supported. Use `ollama pull` to download a q4_K_M model directly from the Ollama registry with hardware acceleration enabled:

```shell
# Pull a q4_K_M model directly (recommended)
ollama pull qwen3:0.6b
```

### Option 2: Build a Model Manually

**q4_0** models also deliver good performance on the K1 board. To use this approach, find a GGUF model on ModelScope, download the q4_0 quantized variant to your board or MUSEBook, and build it with Ollama.

Example:

```shell
sudo apt install wget
wget https://modelscope.cn/models/second-state/Qwen2.5-0.5B-Instruct-GGUF/resolve/master/Qwen2.5-0.5B-Instruct-Q4_0.gguf ~/
wget https://archive.spacemit.com/spacemit-ai/modelfile/qwen2.5:0.5b.modelfile ~/
cd ~/
ollama create qwen2.5:0.5b -f qwen2.5:0.5b.modelfile
```

## Usage

```shell
# Run a directly pulled model
ollama run qwen3:0.6b

# Or run a manually built model
ollama run qwen2.5:0.5b
```
