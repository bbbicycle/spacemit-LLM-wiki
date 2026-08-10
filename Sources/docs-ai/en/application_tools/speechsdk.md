---
sidebar_position: 3
---

# Speech SDK

> Note: This is a temporary version and will be consolidated into the AI SDK in a future release.

**Speech Model SDK** (`sm-sdk`) is a comprehensive AI speech service platform that brings together multiple speech processing technologies in a single unified solution: Voice Activity Detection (VAD), Automatic Speech Recognition (ASR), Machine Translation, Text-to-Speech (TTS), Keyword Spotting (KWS), and Speaker Diarization.

## Platform Support

| Platform & OS | Supported |
|---|---|
| K1 Buildroot | ❌ No |
| K1 OpenHarmony | ❌ No |
| K1 Bianbu LXQT/GNOME | ❌ No |
| K3 Buildroot | ❌ No |
| K3 OpenHarmony | ❌ No |
| K3 Bianbu LXQT/GNOME | ✅ Yes |

## ✨ Key Features

### 🔍 **Voice Activity Detection (VAD)**
- **Segment splitting**: Detects speech and silence boundaries within a continuous audio stream.
- **Stream-friendly**: Chunk-based processing designed for real-time use cases.

### 🎤 **Automatic Speech Recognition (ASR)**
- **Real-time streaming**: Low-latency speech-to-text transcription.
- **Multi-language support**: Chinese, English, Japanese, Korean, Cantonese, and more.

### 🌐 **Machine Translation**
- **Real-time streaming**: Low-latency machine translation.
- **Multi-language support**: Chinese, English, Japanese, Korean, Spanish, and more.

### 🔊 **Text-to-Speech (TTS)**
- **High-quality synthesis**: Natural, fluent speech output.
- **Multi-language support**: Chinese and English.
- **Adjustable parameters**: Configurable speech rate, pitch, and more.

### 🎯 **Keyword Spotting (KWS)**
- **Real-time wake-word detection**: Custom keyword detection with minimal latency.
- **Low power consumption**: Optimized algorithm suited for always-on, long-running deployments.
- **Configurable threshold**: Adjustable detection sensitivity.

### 👥 **Speaker Diarization**
- **Multi-speaker support**: Tags each segment of a transcription with a speaker identity label.
- **ASR pipeline integration**: Chains directly with ASR output to produce speaker-labeled transcripts.

## Model List

The **CPU Core** column shows which core type on K3 each model targets by default.

| Category | Default | Alternatives | Default Threads | CPU Core | SpacemiT EP Acceleration |
| --- | --- | --- | --- | --- | --- |
| VAD | `ten_vad` | `ten` / `silero` | 1 | X100 | Not supported |
| ASR | `sensevoice` | `sensevoice` / `qwen3asr` | 2 / 4 | X100 / A100 | Supported |
| Translation | `hy-mt-1.5` | `hy-mt-1.5` / `marian` | 4 / 1 | A100 / X100 | Supported / Not supported |
| TTS | `matcha` | `matcha` / `vits` | 2 | X100 | Supported / Not supported |
| KWS | `wenetspeech` | `wenetspeech` | 1 | X100 | Not supported |
| Diarization | `eres2net` | `eres2net` | 1 | X100 | Supported |

## 🚀 Quick Start

`sm-sdk` supports two usage modes:

- **From source**: Recommended for development, debugging, custom pipeline work, and direct embedding.
- **As a system service**: Recommended for production deployments on Bianbu systems.

### Install Dependencies

1. **Install `python`**

    ```bash
    sudo apt update
    sudo apt install python
    ```

2. **Install `llama-server`**

    `HY-MT-1.5` and `Qwen3-ASR` require a local `llama-server`. Skip this step if you are only using the ONNX model path.

    Bianbu:

    ```bash
    sudo apt update
    sudo apt install llama.cpp-tools-spacemit
    ```

    Ubuntu:

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

    To persist this across sessions, add the following line to your shell profile:

    ```bash
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
    ```


### From Source

The source-based mode currently targets the following environments:

- **Bianbu / RISC-V**
- **Ubuntu / x86-64**

1. **Create a virtual environment**

    ```bash
    cd path/to/sm-sdk
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc

    uv venv --python 3.13
    source .venv/bin/activate
    ```

2. **Install dependencies**

    Ubuntu:

    ```bash
    uv pip install .
    ```

    Bianbu:

    ```bash
    export UV_EXTRA_INDEX_URL=https://git.spacemit.com/api/v4/projects/33/packages/pypi/simple
    export UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple
    uv pip install .
    UV_EXTRA_INDEX_URL= uv pip install sherpa-onnx==1.13.1 --index-url https://git.spacemit.com/api/v4/projects/81/packages/pypi/simple --no-cache-dir
    ```

3. **Prepare models**

    On Ubuntu, default ONNX models are downloaded automatically during component initialization according to the active configuration.
    > Note: Qwen3-ASR is not yet supported on Ubuntu.

    On Bianbu, download the pre-quantized model package (produced with [xslim](https://github.com/spacemit-com/xslim)). Unaccelerated open-source models can also be downloaded automatically via configuration.

    ```bash
    cd path/to/sm-sdk
    wget https://archive.spacemit.com/spacemit-ai/yumeet/yumeet_models.tar.gz
    tar -xf yumeet_models.tar.gz
    ```

4. **Start the service**

    ```bash
    python main.py --start-server
    ```

### As a System Service

The system service mode currently targets Bianbu environments only.

1. **Install the service**

    Required model files (~3 GB) are downloaded and prepared automatically on first install:

    ```bash
    sudo apt update
    sudo apt install sm-sdk
    ```

2. **Manage the service**

    The service starts automatically after `apt install sm-sdk`. Use `systemctl` for manual lifecycle management:

    ```bash
    sudo systemctl start sm-sdk.service
    sudo systemctl stop sm-sdk.service
    sudo systemctl restart sm-sdk.service
    sudo systemctl status sm-sdk.service
    ```

3. **View logs**

    ```bash
    journalctl -u sm-sdk.service
    ```

### Additional Notes

Some model backends launch independent processes on dedicated ports. The main service remains the recommended entry point for all external traffic:

| Service | Default Port | Description |
| --- | --- | --- |
| Main service | `8060` | Primary entry point — HTTP API, WebSocket API, and FastAPI docs |
| `HY-MT-1.5` model service | `8062` | Local `llama-server` started on demand by the translation engine |
| `Qwen3-ASR` model service | `8063` | Local `llama-server` started on demand by the Qwen3-ASR engine |

## Service Configuration

Both usage modes are driven by configuration files that control model selection, pipeline feature toggles, and service parameters.

The configuration directory is resolved in the following priority order:

```bash
# Environment variable takes highest priority
$SM_SDK_CONFIG_DIR

# Default directory when running from source
./config/

# Common directory for system service installations
/etc/sm-sdk/

# Fallback directory
/var/lib/sm-sdk/config/
```

The model directory is resolved in the following priority order:

```bash
$SM_SDK_MODEL_DIR
./models/
/var/lib/sm-sdk/models/
```

Configuration files and their roles:

- `asr.yaml`: ASR model type, model name, thread count, inference provider, and recognition parameters.
- `audio_stream.yaml`: Base sample rate for audio input; reused by other components.
- `diarization.yaml`: Speaker diarization model and similarity threshold parameters.
- `keywords.txt`: Keyword list for keyword spotting.
- `kws.yaml`: KWS model, detection threshold, and repeat-detection interval.
- `pipeline.yaml`: Pipeline-level feature flags — controls whether translation, TTS, punctuation restoration, KWS, and diarization are active.
- `server.yaml`: FastAPI service listen address, port, and worker count.
- `terms.json`: Post-processing correction rules for proper nouns and common ASR misrecognitions.
- `translation.yaml`: Translation model configuration, including `llama-server` path, port, context length, and thread count.
- `tts.yaml`: TTS model configuration, including language, thread count, and provider.
- `vad.yaml`: VAD model and segmentation threshold configuration.

After changing any configuration file, restart the service for the changes to take effect:

```bash
# From source
python main.py --start-server

# As a system service
sudo systemctl restart sm-sdk.service
```

## API Reference

### WebSocket

The real-time streaming endpoint is:

```text
ws://<host>:<port>/ws/stream
```

Protocol overview:

1. Once the connection is established, the server sends a `ready` status message.
2. The client sends raw audio as a continuous byte stream in **16 kHz, mono, PCM16** format.
3. The server emits transcription results (`transcript`) or keyword detection events (`kws`) as they become available.
4. The client may send control messages at any time to enable or disable STT, KWS, and translation.
5. When the client sends `{"type": "finish"}`, the server flushes any remaining output, sends a termination message, and closes the session.

Message formats:

**Server ready message**

```json
{
    "type": "status",
    "status": "ready",
    "message": "Ready to receive audio"
}
```

**Transcription result message**

```json
{
    "type": "transcript",
    "segment": {
        "text": "Hello, world",
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

**Keyword detection message**

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

**Control message**

```json
{
    "type": "control",
    "enable_stt": true,
    "enable_kws": false,
    "enable_translation": true
}
```

**Finish message**

```json
{
    "type": "finish"
}
```

> **Note:** The server operates in **singleton session** mode. If the session is already held by another WebSocket or REST request, new connections will receive an error response and be rejected.

### HTTP

Once the main service is running, interactive API documentation (Swagger UI) is available at:

```text
http://localhost:8060/docs
```

Available HTTP endpoints:

| Method | Path | Content-Type | Description |
| --- | --- | --- | --- |
| `POST` | `/v1/components/load` | `application/json` | Initialize the speech components enabled in the current configuration |
| `POST` | `/v1/components/release` | `application/json` | Release the currently loaded speech components |
| `POST` | `/v1/audio/transcriptions` | `multipart/form-data` | Upload an audio file and return the transcription result |
| `POST` | `/v1/audio/translate` | `application/json` | Submit text and return the translation result |
| `POST` | `/v1/audio/speech` | `application/json` | Submit text and return synthesized audio |
| `POST` | `/v1/audio/pipeline` | `multipart/form-data` | Run the full pipeline: ASR → Diarization → Translation → TTS (as configured) |

#### 1. Load Speech Components

```bash
curl -X POST http://localhost:8060/v1/components/load
```

- Initializes all speech components defined in the active configuration, provided the singleton session is idle and the service is in `ready` state.
- Returns success immediately if the components are already loaded.

#### 2. Release Speech Components

```bash
curl -X POST http://localhost:8060/v1/components/release
```

- Unloads all currently loaded speech components, provided the singleton session is idle.
- Returns success with an informational message if the components are already unloaded.

#### 3. File Transcription

```bash
curl -X POST http://localhost:8060/v1/audio/transcriptions \
    -F "file=@audio.wav" \
    -F "model=asr" \
    -F "response_format=json"
```

- `response_format=json`: Returns a JSON object containing `text` and `segments`.
- `response_format=text`: Returns the transcription as plain text.

#### 4. Text Translation

```bash
curl -X POST http://localhost:8060/v1/audio/translate \
    -H "Content-Type: application/json" \
    -d '{
        "text": "Hello, welcome to Speech SDK."
    }'
```

- The `text` field is required.
- Returns a JSON object with the original `text` and the `translated_text`.

#### 5. Text-to-Speech

```bash
curl -X POST http://localhost:8060/v1/audio/speech \
    -H "Content-Type: application/json" \
    -d '{
        "input": "Hello, welcome to Speech SDK.",
        "response_format": "wav",
        "speed": 1.0,
        "speaker_id": 0
    }' \
    --output output.wav
```

- `response_format`: `wav` or `mp3`.
- `speed`: valid range is `0.25` – `4.0`.

#### 6. Full Audio Pipeline

```bash
curl -X POST http://localhost:8060/v1/audio/pipeline \
    -F "file=@audio.wav" \
    -F "model=asr" \
    -F "response_format=json" \
    -F "speed=1.0" \
    -F "speaker_id=0"
```

- `response_format=json`: Returns transcription, translation, per-segment details, and timing statistics.
- `response_format=wav`: Returns synthesized WAV audio directly, provided both translation and TTS complete successfully.

### Programmatic Usage

#### 1. Using `SpeechPipeline` for the Speech Pipeline

The following example demonstrates how to push audio chunks into the pipeline manually using `_on_audio_chunk`:

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

Notes:

- `_on_audio_chunk` expects a `float32` mono waveform as input.
- If the audio is not at `16 kHz`, resample it before passing it to the pipeline.
- Call `flush()` after the last chunk to force any buffered output to be emitted.

#### 2. Using `SpeechComponentManager` to Call Models Directly

The following example demonstrates how to call initialized components directly, without going through the full pipeline:

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

This is useful when you want to compose only the capabilities your application needs, for example:

- Running ASR alone.
- Running ASR and then invoking translation as a separate step.
- Synthesizing speech from a text string directly, without any audio input.

## Source Code Download

On Bianbu, the `sm-sdk` source package can be retrieved directly via `apt`.

### 1. Configure the `apt` Source

Confirm that `/etc/apt/sources.list.d/bianbu.sources` includes both `deb` and `deb-src` under `Types`:

```text
Types: deb deb-src
URIs: https://archive.spacemit.com/bianbu4/
Suites: resolute resolute-security resolute-updates resolute-backports resolute-porting resolute-customization
Components: main universe restricted multiverse
```

If only `deb` is present, add `deb-src` and then update the package index:

```bash
sudo apt update
```

### 2. Download the Source Package

Once the source is configured, download the `sm-sdk` source package:

```bash
mkdir -p ~/Workspace/sm-sdk-src
cd ~/Workspace/sm-sdk-src
apt source sm-sdk
```

After this completes, the directory will contain a `.dsc` file, the original compressed archive, and the extracted source tree, which you can use to inspect the Debian packaging files and source code.

## 📁 Project Structure

```text
sm-sdk/
├── main.py                    # Entry point
├── src/                       # Core implementation
│   ├── server.py              # FastAPI service entry point
│   ├── api/                   # HTTP / WebSocket interfaces
│   ├── base/                  # Configuration and base data structures
│   ├── core/                  # Speech pipeline and component management
│   ├── models/                # Model engine implementations
│   └── utils/                 # Download, audio, messaging, and other utilities
├── config/                    # Runtime configuration files
├── docs/                      # Internal project documentation
├── models/                    # Local model directory
├── debian/                    # Debian / Bianbu packaging files
└── benchmark/                 # Performance benchmarks and results
```

Module responsibilities:

- `src/api/`: HTTP and WebSocket interface layer exposed to external clients.
- `src/core/`: Pipeline orchestration, pseudo-streaming output, and component lifecycle management.
- `src/models/`: Per-engine initialization, inference, and reset logic.
- `config/`: The single source of truth for runtime behavior — feature flags and model selection.
- `examples/`: End-user code samples and a starting point for custom integrations.