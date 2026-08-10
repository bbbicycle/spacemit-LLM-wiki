
sidebar_position: 9

# Hermes Agent (Cloud Compute)

**Hermes Agent** is an open-source AI agent framework that supports multiple LLM providers. It offers capabilities such as tool calling, scheduled tasks, MCP protocol support, and web access, and can be used from a terminal CLI or integrated into messaging platforms such as Telegram and Discord.

## Platform Support

| Platform & OS         | Supported |
| --------------------- | --------- |
| K1 Buildroot          | ❌ No     |
| K1 OpenHarmony        | ❌ No     |
| K1 Bianbu LXQT/GNOME  | ✅ Yes    |
| K3 Buildroot          | ❌ No     |
| K3 OpenHarmony        | ❌ No     |
| K3 Bianbu LXQT/GNOME  | ✅ Yes    |

## Installation

### Option 1: `apt` Installation (Recommended)

Install it directly through `apt` on Bianbu OS:

```bash
sudo apt update
sudo apt install hermes-agent
```

After installation, you can run the `hermes` command directly without any additional environment configuration.
![Hermes Agent interface](../static/hermes/hermes-agent.png)

### Option 2: Source Installation (For Developers)

This method is intended for users who need to modify the codebase or contribute to development.

#### Prerequisites

- Python 3.11+ (uv will download it automatically)
- `libffi8` (runtime library, included in the system)
- `libffi-dev` headers (must be extracted manually, see below)

#### 1. Clone the Repository

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
```

#### 2. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

#### 3. Extract `libffi-dev` Headers

Building `cffi` and `cryptography` on `riscv64` requires `ffi.h`, but the system includes only the runtime library and not the header files. Use `apt-get download` to fetch the `.deb` package without installing it or requiring `sudo`, then extract the headers with `dpkg-deb -x`:

```bash
apt-get download libffi-dev
mkdir -p /tmp/libffi-dev
dpkg-deb -x libffi-dev_*.deb /tmp/libffi-dev
```

> `/tmp/libffi-dev` is removed after a reboot. If you need to reinstall dependencies, run this step again. Existing virtual environments are not affected.

#### 4. Create a Virtual Environment and Install Dependencies

```bash
cd hermes-agent

export PKG_CONFIG_PATH="/tmp/libffi-dev/usr/lib/riscv64-linux-gnu/pkgconfig:$PKG_CONFIG_PATH"
export C_INCLUDE_PATH="/tmp/libffi-dev/usr/include/riscv64-linux-gnu:$C_INCLUDE_PATH"
export CPATH="/tmp/libffi-dev/usr/include/riscv64-linux-gnu:$CPATH"
export LIBRARY_PATH="/tmp/libffi-dev/usr/lib/riscv64-linux-gnu:$LIBRARY_PATH"

uv venv venv --python 3.11
source venv/bin/activate

uv pip install -e ".[cron,cli,dev,mcp,web]"
```

> The `voice` and `messaging` extras have limitations on `riscv64`. See [Unavailable Features](#unavailable-features) for details.

## Configuration

### 1. Configure the API Key

Edit `~/.hermes/.env` (generated automatically on first run, or create it manually). The following example uses the MiniMax China endpoint.

```env
MINIMAX_CN_API_KEY=your_key_here
MINIMAX_CN_BASE_URL=https://api.minimaxi.com/v1
```

For a source installation, you can also edit the `.env` file directly under the project directory:

```bash
cp .env.example .env
```

### 2. Configure the Model

Edit `~/.hermes/config.yaml` (generated automatically on first run, or create it manually):

```yaml
model:
  default: MiniMax-M2.7-highspeed
  provider: custom
  base_url: https://api.minimaxi.com/v1
  api_mode: chat_completions

custom_providers:
- name: minimax-cn
  base_url: https://api.minimaxi.com/v1
  api_key: your_key_here
  api_mode: chat_completions
  model: MiniMax-M2.7-highspeed
```

> The MiniMax API accepts only the plain model name, for example `MiniMax-M2.7-highspeed`. Provider-prefixed formats such as `minimax-cn/MiniMax-M2.7-highspeed` are not supported.

## Start the Agent

For an **`apt` installation**, run:

```bash
hermes
```

For a **source installation**, activate the virtual environment each time you open a new terminal:

```bash
cd hermes-agent
source venv/bin/activate
./hermes
```

## Supported LLM Providers

Set the corresponding key in `.env` to switch providers.

| Provider          | Environment Variable   |
| ----------------- | ---------------------- |
| OpenRouter        | `OPENROUTER_API_KEY`   |
| Google Gemini     | `GOOGLE_API_KEY`       |
| Kimi / Moonshot   | `KIMI_API_KEY`         |
| MiniMax (Global)  | `MINIMAX_API_KEY`      |
| MiniMax (China)   | `MINIMAX_CN_API_KEY`   |
| GLM / z.ai        | `GLM_API_KEY`          |
| Hugging Face      | `HF_TOKEN`             |

## Unavailable Features

The following features are currently unavailable because of `riscv64` platform limitations:

| Feature                        | Reason                                                                               |
| ------------------------------ | ------------------------------------------------------------------------------------ |
| `voice` (speech recognition)   | `ctranslate2` has no `riscv64` wheel; `faster-whisper` depends on it                |
| Local STT (speech-to-text)     | Same as above                                                                        |
| `messaging` Discord encryption | `pynacl` depends on `cffi` and is skipped because `libffi` headers are unavailable   |

### Messaging Feature (Optional)

The `messaging` feature allows Hermes Agent to connect to messaging platforms such as Telegram, Discord, Slack, WhatsApp, Signal, and Matrix. After configuring the bot token for the target platform, you can interact with the agent directly from those applications.

To enable it in a source installation, first set the `libffi` environment variables, and then install it separately:

```bash
export PKG_CONFIG_PATH="/tmp/libffi-dev/usr/lib/riscv64-linux-gnu/pkgconfig:$PKG_CONFIG_PATH"
export LIBRARY_PATH="/tmp/libffi-dev/usr/lib/riscv64-linux-gnu:$LIBRARY_PATH"
export CPATH="/tmp/libffi-dev/usr/include/riscv64-linux-gnu:$CPATH"
source venv/bin/activate
uv pip install -e ".[messaging]"
```

Start the messaging gateway:

```bash
./hermes gateway
```
