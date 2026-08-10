---
sidebar_position: 7
---

# Open-WebUI

**Open-WebUI** (formerly Ollama WebUI) is an open-source, self-hostable web management tool designed for locally deployed or privately hosted large language models (LLMs). Its primary goal is to provide an interaction experience similar to ChatGPT while also supporting offline operation and extensive customization.

## Platform Support

| Platform & System | Support |
| --- | --- |
| K1 Buildroot | ❌ Not supported |
| K1 OpenHarmony | ❌ Not supported |
| K1 Bianbu LXQT/GNOME | ✅ Supported |
| K3 Buildroot | ❌ Not supported |
| K3 OpenHarmony | ❌ Not supported |
| K3 Bianbu LXQT/GNOME | ❌ Not supported |

## Installation

To simplify the process of using large language models on K1, we provide an Open-WebUI `.deb` package for K1 that can be installed with a single command:

> **Note:** The system version must be **2.1.1** or later.

```shell
sudo apt update
sudo apt install openwebui
```

Wait for the installation to finish.

## Usage

Right-click the `openwebui` desktop icon and select **Allow Launching** to start using it.

![Open-WebUI desktop icon](../static/openwebui.png)

For detailed usage instructions, refer to the [OpenWebUI User Guide](https://forum.spacemit.com/t/topic/185).

## Create a Model (Optional)

This `.deb` package includes `openwebui` and an `ollama` container image. You only need to access the `ollama` container to download and create a model. The following is an example workflow. 
First, enter the container:

```shell
sudo docker exec -it ollama bash
```

```shell
apt update
apt install wget vim
cd /root
wget https://modelscope.cn/models/second-state/Qwen2.5-0.5B-Instruct-GGUF/resolve/master/Qwen2.5-0.5B-Instruct-Q4_0.gguf
wget https://archive.spacemit.com/spacemit-ai/modelfile/qwen2.5:0.5b.modelfile
ollama create qwen2.5:0.5b -f qwen2.5:0.5b.modelfile
```

Then restart the `ollama` container and reopen Open-WebUI to use the accelerated model:

```shell
sudo docker restart ollama
```
