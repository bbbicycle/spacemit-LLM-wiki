---
sidebar_position: 3
---

# SPEECH SDK 

> **注：** 临时版本，后续统一到AI SDK

**Speech Model SDK** （简称 `sm-sdk`）是一个集成多种语音处理技术的综合性AI语音服务平台，提供语音活动检测（VAD）、语音识别(ASR)、机器翻译（Translation）、语音合成(TTS)、关键词检测(KWS)、说话人分离（Diarization）等功能于一体的统一解决方案。

## 平台支持情况

|      平台 & 系统       |       是否支持     |
|-----------------------|-----------------------|
| K1 Buildroot          | ❌ 不支持               |
| K1 OpenHarmony     | ❌ 不支持              |
| K1 Bianbu LXQT/GNOME    | ❌ 不支持             |
| K3 Buildroot          | ❌ 不支持              |
| K3 OpenHarmony     | ❌ 不支持              |
| K3 Bianbu LXQT/GNOME  | ✅ 支持                |

## ✨ 核心特性

### 🔍 **语音活动检测（VAD）**
- **片段切分**：在连续音频流中识别语音与静音区间。
- **流式友好**：支持按音频块持续处理，适合实时场景。

### 🎤 **语音识别（ASR）**
- **实时流式识别**: 支持低延迟的实时语音转文字
- **多语言支持**：覆盖中文、英文、日文、韩文、粤语等语言。

### 🌐 **机器翻译（Translation）**
- **实时流式翻译**: 支持低延迟的实时机器翻译
- **多语言支持**：支持中文、英文、日文、韩文、西班牙语等语言。

### 🔊 **语音合成（TTS）**
- **高质量合成**: 自然流畅的语音输出
- **多语言支持**: 中文和英文语音合成
- **可调参数**: 支持语速、音调等参数调节

### 🎯 **关键词检测（KWS）**
- **实时唤醒**: 支持自定义关键词的实时检测
- **低功耗**: 优化的检测算法，适合长时间运行
- **可配置阈值**: 灵活的检测敏感度设置

### 👥 **说话人分离（Diarization）**
- **多说话人场景支持**：为识别结果附加说话人身份标签。
- **可与 ASR 串联**：在流水线中可与转写结果联动输出说话人标签。

## 模型列表

`CPU核心` 一列反映模型默认运行在 K3 的哪类核心上。

| 类别 | 当前默认配置 | 可选实现 | 默认线程数 | CPU核心 | SpacemiT EP 加速 |
| --- | --- | --- | --- | --- | --- |
| VAD | `ten_vad` | `ten` / `silero` | 1 | X100 | 未支持 |
| ASR | `sensevoice` | `sensevoice` / `qwen3asr` | 2 / 4 | X100 / A100 | 支持 |
| Translation | `hy-mt-1.5` | `hy-mt-1.5` / `marian` | 4 / 1 | A100 / X100 | 支持 / 未支持 |
| TTS | `matcha` | `matcha` / `vits` | 2 | X100 | 支持 / 未支持 |
| KWS | `wenetspeech` | `wenetspeech` | 1 | X100 | 未支持 |
| Diarization | `eres2net` | `eres2net` | 1 | X100 | 支持 |

## 🚀 快速开始

`sm-sdk` 当前提供两种使用方式：

- **从源码使用**：适合开发、调试、定制流水线和直接集成。
- **从系统服务使用**：适合在 Bianbu 系统中以服务方式统一管理。

### 安装依赖

1. **安装 `python`**

    ```bash
    sudo apt update
    sudo apt install python
    ```

2. **安装 `llama-server`**

    `HY-MT-1.5` 和 `Qwen3-ASR` 依赖本地 `llama-server`。如果仅使用 ONNX 模型链路，可跳过此步骤。

    Bianbu：

    ```bash
    sudo apt update
    sudo apt install llama.cpp-tools-spacemit
    ```

    Ubuntu：

    ```bash
    sudo apt update
    sudo apt install -y build-essential cmake git libcurl4-openssl-dev

    git clone https://github.com/ggml-org/llama.cpp.git
    cd llama.cpp

    cmake -B build -S . -DGGML_CURL=ON -DCMAKE_INSTALL_PREFIX=$HOME/.local
    cmake --build build -j$(nproc)
    cmake --install build

    export PATH="$HOME/.local/bin:$PATH"
    ```

    如需长期生效，可将以下命令写入 shell 配置文件：

    ```bash
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
    ```


### 从源码使用

源码方式当前面向以下环境：

- **Bianbu / RISC-V 环境**
- **Ubuntu / X86-64 环境**

1. **创建虚拟环境**

    ```bash
    cd path/to/sm-sdk
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc

    uv venv --python 3.13
    source .venv/bin/activate
    ```

2. **安装依赖**

    Ubuntu：

    ```bash
    uv pip install .
    ```

    Bianbu：

    ```bash
    export UV_EXTRA_INDEX_URL=https://git.spacemit.com/api/v4/projects/33/packages/pypi/simple
    export UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple
    uv pip install .
    UV_EXTRA_INDEX_URL= uv pip install sherpa-onnx==1.13.1 --index-url https://git.spacemit.com/api/v4/projects/81/packages/pypi/simple --no-cache-dir
    ```

3. **准备模型**

    Ubuntu 环境下，默认 ONNX 模型通常会在组件初始化时按配置自动下载。
    >注：Qwen3-ASR尚未适配在Ubuntu上运行

    Bianbu需要下载我们提前用 [xslim](https://github.com/spacemit-com/xslim) 量化好的模型包，同时也支持按配置自动下载未加速的开源模型。

    ```bash
    cd path/to/sm-sdk
    wget https://archive.spacemit.com/spacemit-ai/yumeet/yumeet_models.tar.gz
    tar -xf yumeet_models.tar.gz
    ```

4. **启动服务**

    ```bash
    python main.py --start-server
    ```

### 从系统服务使用

系统服务使用方式当前仅面向 Bianbu 环境。

1. **安装服务**

    首次安装 `sm-sdk` 时会自动准备所需模型文件（约 3 GB ）：

    ```bash
    sudo apt update
    sudo apt install sm-sdk
    ```

2. **启动服务**

    `apt install sm-sdk` 后服务通常会自动启动；如需手动管理，可使用 `systemctl`：

    ```bash
    sudo systemctl start sm-sdk.service
    sudo systemctl stop sm-sdk.service
    sudo systemctl restart sm-sdk.service
    sudo systemctl status sm-sdk.service
    ```

3. **查看日志**

    ```bash
    journalctl -u sm-sdk.service
    ```

### 其他

除主服务外，部分模型后端会在本机额外拉起独立进程并占用单独端口，但对外业务入口通常仍建议统一使用主服务：

| 服务 | 默认端口 | 说明 |
| --- | --- | --- |
| 主服务 | `8060` | 主入口，提供 HTTP API 、 WebSocket API 和 FastAPI |
| `HY-MT-1.5` 模型服务 | `8062` | 由翻译引擎按需启动的本地 `llama-server` 服务 |
| `Qwen3-ASR` 模型服务 | `8063` | 由 `Qwen3-ASR` 引擎按需启动的本地 `llama-server` 服务 |

## 服务配置

两种 sm-sdk 的使用方式均通过配置文件控制模型选择、流水线开关和服务参数。

配置目录默认按以下顺序解析：

```bash
# 优先使用环境变量
$SM_SDK_CONFIG_DIR

# 源码运行时默认目录
./config/

# 系统服务常用目录
/etc/sm-sdk/

# 兜底目录
/var/lib/sm-sdk/config/
```

模型目录默认按以下顺序解析：

```bash
$SM_SDK_MODEL_DIR
./models/
/var/lib/sm-sdk/models/
```

当前仓库中的配置文件及作用如下：

- `asr.yaml`：语音识别模型类型、模型名称、线程数、推理 provider 与识别相关参数。
- `audio_stream.yaml`：音频输入的基础采样率配置，其他组件会复用该采样率。
- `diarization.yaml`：说话人分离模型与相似度阈值等参数。
- `keywords.txt`：关键词检测的关键词清单。
- `kws.yaml`：关键词检测模型与阈值、重复检测间隔等参数。
- `pipeline.yaml`：流水线级开关，例如是否启用翻译、TTS、标点恢复、KWS、说话人分离。
- `server.yaml`：FastAPI 服务监听地址、端口、worker 数量等参数。
- `terms.json`：术语纠正规则，用于纠正 ASR 结果中的专有名词或常见误识别。
- `translation.yaml`：翻译模型配置，包括 `llama-server` 路径、端口、上下文长度、线程数等。
- `tts.yaml`：语音合成模型配置，包括语言、线程数、provider 等。
- `vad.yaml`：语音活动检测模型与分段阈值配置。

配置变更后，需要重新启动服务使其生效：

```bash
# 从源码使用
python main.py --start-server

# 从系统服务使用
sudo systemctl restart sm-sdk.service
```

## 服务调用

### WebSocket

当前实时流式接口地址为：

```text
ws://<host>:<port>/ws/stream
```

协议要点如下：

1. 建立连接后，服务端会先返回 `ready` 状态消息。
2. 客户端按块发送 **16kHz、单声道、PCM16** 原始音频字节流。
3. 服务端会持续返回转写结果（`transcript`）或关键词检测结果（`kws`）。
4. 客户端可发送控制消息动态开关 STT、KWS 与翻译。
5. 客户端发送 `{"type": "finish"}` 后，服务端返回结束消息并关闭本轮处理。

典型消息格式如下。

**服务就绪消息**

```json
{
    "type": "status",
    "status": "ready",
    "message": "Ready to receive audio"
}
```

**转写结果消息**

```json
{
    "type": "transcript",
    "segment": {
        "text": "你好，世界",
        "speaker_id": 0,
        "speaker_label": "Speaker",
        "start_time": 0.0,
        "end_time": 1.2,
        "language": "zh",
        "translation": "Hello, world",
        "is_final": true,
        "is_pseudo": false
    },
    "is_final": true,
    "timestamp": 1710000000.0
}
```

**关键词检测消息**

```json
{
    "type": "kws",
    "segment": {
        "keyword": "小迭小迭",
        "confidence": 1.0,
        "start_time": 2.1,
        "end_time": 2.5
    },
    "timestamp": 1710000000.0
}
```

**控制消息**

```json
{
    "type": "control",
    "enable_stt": true,
    "enable_kws": false,
    "enable_translation": true
}
```

**结束消息**

```json
{
    "type": "finish"
}
```

> 说明：当前服务端会以**单例会话**方式工作；当会话被其他 WebSocket 或 REST 请求占用时，新的连接可能收到错误消息并被拒绝。

### HTTP

启动主服务后，可通过以下地址查看 OpenAPI 文档：

```text
http://localhost:8060/docs
```

当前可用的主要 HTTP 接口如下：

| 方法 | 路径 | 请求类型 | 说明 |
| --- | --- | --- | --- |
| `POST` | `/v1/components/load` | `application/json` | 初始化当前配置启用的语音组件 |
| `POST` | `/v1/components/release` | `application/json` | 释放当前已加载的语音组件 |
| `POST` | `/v1/audio/transcriptions` | `multipart/form-data` | 上传音频文件并返回转写结果 |
| `POST` | `/v1/audio/translate` | `application/json` | 输入文本并返回翻译结果 |
| `POST` | `/v1/audio/speech` | `application/json` | 输入文本并返回语音音频 |
| `POST` | `/v1/audio/pipeline` | `multipart/form-data` | 一次性执行 ASR → Diarization → Translation → TTS（按配置启用） |

#### 1. 加载语音组件

```bash
curl -X POST http://localhost:8060/v1/components/load
```

- 当全局单例会话空闲且服务状态为 ready 时，按当前配置初始化语音组件。
- 若组件已初始化，接口会直接返回成功状态。

#### 2. 释放语音组件

```bash
curl -X POST http://localhost:8060/v1/components/release
```

- 当全局单例会话空闲时，释放当前已加载的语音组件。
- 若组件已处于释放状态，接口会返回成功并提示无需重复释放。

#### 3. 文件转写

```bash
curl -X POST http://localhost:8060/v1/audio/transcriptions \
    -F "file=@audio.wav" \
    -F "model=asr" \
    -F "response_format=json"
```

- `response_format=json`：返回 JSON，包含 `text` 与 `segments`。
- `response_format=text`：仅返回纯文本转写结果。

#### 4. 文本翻译

```bash
curl -X POST http://localhost:8060/v1/audio/translate \
    -H "Content-Type: application/json" \
    -d '{
        "text": "你好，欢迎使用 Speech SDK。"
    }'
```

- 请求体中的 `text` 为必填字段。
- 返回 JSON，包含原始文本 `text` 与翻译结果 `translated_text`。

#### 5. 文本转语音

```bash
curl -X POST http://localhost:8060/v1/audio/speech \
    -H "Content-Type: application/json" \
    -d '{
        "input": "你好，欢迎使用 Speech SDK。",
        "response_format": "wav",
        "speed": 1.0,
        "speaker_id": 0
    }' \
    --output output.wav
```

- `response_format` 当前支持 `wav` 和 `mp3`。
- `speed` 取值范围由接口限制为 `0.25 ~ 4.0`。

#### 6. 音频完整流水线

```bash
curl -X POST http://localhost:8060/v1/audio/pipeline \
    -F "file=@audio.wav" \
    -F "model=asr" \
    -F "response_format=json" \
    -F "speed=1.0" \
    -F "speaker_id=0"
```

- `response_format=json`：返回转写文本、翻译文本、分段信息与耗时统计。
- `response_format=wav`：当翻译和 TTS 都实际执行成功时，直接返回合成后的 WAV 音频。

### 源码调用

#### 1. 通过 `SpeechPipeline` 调用语音流水线

以下示例展示如何使用 `_on_audio_chunk` 手动向流水线送入音频块：

```python
import numpy as np

from src.base.config import load_session_config
from src.core.pipeline import SpeechPipeline


config = load_session_config()
pipeline = SpeechPipeline(config)
pipeline.initialize()


def on_segment(segment):
    print(segment.model_dump())


pipeline.add_callback(on_segment)

pcm16 = open("audio.pcm", "rb").read()
chunk = np.frombuffer(pcm16, dtype=np.int16).astype(np.float32) / 32768.0

pipeline._on_audio_chunk(chunk)
pipeline.flush()
pipeline.reset()
```

说明：

- `_on_audio_chunk` 的输入应为 `float32` 单声道波形。
- 如果输入不是 `16kHz`，建议先在业务侧完成重采样。
- `flush()` 用于在输入结束后强制输出剩余缓冲结果。

#### 2. 通过 `SpeechComponentManager` 直接调用模型

以下示例展示如何直接调用已初始化的组件，而不经过完整流水线：

```python
import soundfile as sf

from src.base.config import load_session_config
from src.core.speech_components import SpeechComponentManager


audio, sample_rate = sf.read("audio.wav", dtype="float32")
if audio.ndim > 1:
    audio = audio.mean(axis=1)

config = load_session_config()
components = SpeechComponentManager()
components.configure(config)
components.initialize_all()

asr_result = components.asr.recognize(audio)
print(asr_result.text)

if components.translation is not None:
    translated = components.translation.translate(
            asr_result.text,
            source_lang=asr_result.language,
    )
    print(translated)
```

这种方式适合在应用内部按需组合能力，例如：

- 仅调用 ASR；
- 先做 ASR，再单独做翻译；
- 直接对指定文本调用 TTS，而不经过语音输入链路。

## 源码获取

在 Bianbu 环境中，可以直接通过 `apt` 获取 `sm-sdk` 的源码包。

### 1. 配置 `apt` 源

确认 `/etc/apt/sources.list.d/bianbu.sources` 中的 `Types` 同时包含 `deb` 和 `deb-src`：

```text
Types: deb deb-src
URIs: https://archive.spacemit.com/bianbu4/
Suites: resolute resolute-security resolute-updates resolute-backports resolute-porting resolute-customization
Components: main universe restricted multiverse
```

如果当前只有 `deb`，需要补充 `deb-src` 后再更新索引：

```bash
sudo apt update
```

### 2. 下载源码包

完成源配置后，可直接下载 `sm-sdk` 源码包：

```bash
mkdir -p ~/Workspace/sm-sdk-src
cd ~/Workspace/sm-sdk-src
apt source sm-sdk
```

执行完成后，当前目录下通常会生成 `.dsc`、原始压缩包以及解压后的源码目录，可用于查看 Debian 打包文件和源码内容。

## 📁 项目架构

```text
sm-sdk/
├── main.py                    # 启动入口
├── src/                       # 核心实现
│   ├── server.py              # FastAPI 服务入口
│   ├── api/                   # HTTP / WebSocket 接口
│   ├── base/                  # 配置与基础数据结构
│   ├── core/                  # 语音流水线与组件管理
│   ├── models/                # 各类模型引擎实现
│   └── utils/                 # 下载、音频、消息等工具模块
├── config/                    # 运行时配置文件
├── docs/                      # 项目内部说明文档
├── models/                    # 本地模型目录
├── debian/                    # Debian / Bianbu 打包文件
└── benchmark/                 # 性能测试与结果记录
```

主要模块职责：

- `src/api/`：对外暴露 HTTP 与 WebSocket 接口。
- `src/core/`：负责流水线编排、伪流式输出、组件生命周期管理。
- `src/models/`：封装各类模型引擎的初始化、推理与重置逻辑。
- `config/`：作为运行行为的单一配置入口，控制能力开关与模型选择。
- `examples/`：提供面向使用者的调用样例，可作为二次开发参考。