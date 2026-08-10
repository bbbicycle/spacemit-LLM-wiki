---
sidebar_position: 6
---
# LocalAI

## Overview

LocalAI is a self-hosted AI stack for running AI models locally. It exposes an OpenAI-compatible API, letting you run large language models (LLMs), image generation, speech transcription, and other AI workloads on consumer-grade hardware — including CPU-only environments — without sending data to external services.

This guide covers building and installing LocalAI from source on the Bianbu platform and adding custom inference backends.

## Platform Support

| Platform & OS | Supported |
|---|---|
| K1 Buildroot | ❌ No |
| K1 OpenHarmony | ❌ No |
| K1 Bianbu LXQT/GNOME | ✅ Yes |
| K3 Buildroot | ❌ No |
| K3 OpenHarmony | ❌ No |
| K3 Bianbu LXQT/GNOME | ✅ Yes |

## Build and Installation

### Install System Dependencies

```bash
sudo apt update
sudo apt install cmake golang libgrpc-dev make protobuf-compiler-grpc python3-grpc-tools

# Remove the existing protobuf installation
sudo apt-get remove --purge protobuf-compiler libprotobuf-dev
sudo apt-get autoremove
sudo rm /usr/local/bin/protoc          # Remove the protoc binary
sudo rm -rf /usr/local/include/google  # Remove header files
sudo rm -rf /usr/local/lib/libproto*   # Remove library files
sudo rm -rf /usr/lib/protoc            # Remove any other installation paths

sudo apt-get install autoconf automake libtool curl make gcc-14 g++-14 unzip

# In /usr/bin, remove the existing symlinks for:
# gcc, g++, gcc-ar, gcc-nm, gcc-ranlib,
# riscv64-linux-gnu-gcc, riscv64-linux-gnu-gcc-ar, riscv64-linux-gnu-gcc-nm,
# riscv64-linux-gnu-gcc-ranlib, riscv64-linux-gnu-g++
# and recreate them pointing to the corresponding gcc-14 versions.
# Example:
# sudo rm /usr/bin/gcc
# sudo ln -s /usr/bin/gcc-14 /usr/bin/gcc

# Download and build protobuf from source
wget https://github.com/protocolbuffers/protobuf/releases/download/v3.20.3/protobuf-cpp-3.20.3.tar.gz
tar xvzf protobuf-cpp-3.20.3.tar.gz 
cd protobuf-3.20.3/
cd cmake
cmake -DCMAKE_INSTALL_PREFIX=/usr/local .
cmake --build . --parallel 8
ctest --verbose
sudo cmake --install .
sudo ldconfig
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
cd ../../

sudo apt install libgrpc++-dev
```

### Build LocalAI

Download the source archive and build:

```bash
wget https://archive.spacemit.com/spacemit-ai/localai/localai.tar.gz
tar xvzf localai.tar.gz

# Change into the project directory
cd localai

# Add the Go workspace bin directory to PATH so that binaries installed
# via `go install` (e.g. protoc-gen-go) are available during the build
export PATH=$PATH:$(go env GOPATH)/bin

# Use the Aliyun mirror to speed up Go module downloads
export GOPROXY=https://mirrors.aliyun.com/goproxy/,direct

# Build
make build

# If the build fails, resolve the error, then run `make clean` before retrying

```

## Adding Custom Inference Backends

### Adding the RISC-V Accelerated llama.cpp Backend

SpacemiT maintains a fork of llama.cpp with RISC-V acceleration, packaged as a gRPC server binary named `llama-cpp-riscv-spacemit`. Run the following to download and deploy it:

```bash
cd backend/cpp/spacemit-llama-cpp
bash install.sh
```

`install.sh` downloads the pre-built RISC-V accelerated llamacpp-grpc-server binary and a quantized model, places them in the correct directories, and generates the required configuration file.

Return to the project root and start LocalAI:

```bash
./local-ai --debug
```

Open <http://localhost:8080/chat/> in a browser to verify the setup.

If the inference backend fails to start with the following error:

```
stderr llama-cpp-riscv-spacemit: error while loading shared libraries: libabsl_synchronization.so.20220623: cannot open shared object file: No such file or directory
```

resolve it by running:

```bash
sudo apt install libabsl-dev
sudo ln -s /usr/lib/riscv64-linux-gnu/libabsl_synchronization.so /usr/lib/riscv64-linux-gnu/libabsl_synchronization.so.20220623
```

To use the accelerated llama.cpp backend with other models:

1. Download a GGUF model from <https://archive.spacemit.com/spacemit-ai/gguf/>.
2. Download the corresponding model file from <https://archive.spacemit.com/spacemit-ai/modelfile/>.
3. Use `models/spacemit-qwen2.5-0.5b-instruct.yaml` as a template to create a configuration file for the new model. Update the model name, stop words, and chat template accordingly. The template content can be derived from the model file.

### Adding the RISC-V Accelerated ASR Backend

The source code is located at `backend/cpp/spacemit-asr-cpp`. Build the backend and restart `local-ai`:

```bash
cd backend/cpp/spacemit-asr-cpp
bash build.sh

cd ../../../
./local-ai --debug
```

Test the ASR endpoint:

```bash
# Prepare an audio file to transcribe, e.g. test.wav
curl -X POST http://localhost:8080/v1/audio/transcriptions \
    -H "Content-Type: multipart/form-data" \
    -F "file=@test.wav" \
    -F "model=sensevoicesmall-cpp"
```

### Adding the C++ TTS Backend

The source code is located at `backend/cpp/matcha-tts-cpp`. Build the backend and restart `local-ai`:

```bash
cd backend/cpp/matcha-tts-cpp
bash build.sh

cd ../../../
./local-ai --debug
```

Test the TTS endpoint:

```bash
curl -X POST "http://localhost:8080/tts" \
     -H "Content-Type: application/json" \
     -d '{"input":"Hello, what is the weather today?","model":"matcha-tts-cpp"}' \
     -o output.wav 
```
