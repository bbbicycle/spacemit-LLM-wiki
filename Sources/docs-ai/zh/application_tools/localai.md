---
sidebar_position: 6
---
# LocalAI

## 简介

LocalAI 是用于在本地运行 AI 模型的完整 AI 堆栈。它的设计是简单、高效和可访问的，提供一个兼容 OpenAI 的 API，允许用户在消费级硬件（包括 CPU 环境）上运行大型语言模型（LLM）、图像生成、语音转录等 AI 任务，同时保持用户的数据隐私和安全。

本文主要介绍如何在我们的 Bianbu 平台上从源码编译安装和使用 LocalAI，以及添加自定义的推理后端。

## 平台支持情况

|      平台 & 系统       |       是否支持     |
|-----------------------|-----------------------|
| K1 Buildroot          | ❌ 不支持               |
| K1 OpenHarmony     | ❌ 不支持              |
| K1 Bianbu LXQT/GNOME    | ✅ 支持             |
| K3 Buildroot          | ❌ 不支持              |
| K3 OpenHarmony     | ❌ 不支持              |
| K3 Bianbu LXQT/GNOME  | ✅ 支持                |

## 编译安装步骤

### 安装系统依赖

```bash
sudo apt update
sudo apt install cmake golang libgrpc-dev make protobuf-compiler-grpc python3-grpc-tools

# 卸载现有版本的protobuf
sudo apt-get remove --purge protobuf-compiler libprotobuf-dev
sudo apt-get autoremove
sudo rm /usr/local/bin/protoc          # 删除可执行文件
sudo rm -rf /usr/local/include/google  # 删除头文件
sudo rm -rf /usr/local/lib/libproto*   # 删除库文件
sudo rm -rf /usr/lib/protoc            # 其他可能路径

sudo apt-get install autoconf automake libtool curl make gcc-14 g++-14 unzip

# 切换到/usr/bin， 分别将
# gcc，g++，gcc-ar, gcc-nm, gcc-ranlib,
# riscv64-linux-gnu-gcc, riscv64-linux-gnu-gcc-ar, iscv64-linux-gnu-gcc-nm,
# riscv64-linux-gnu-gcc-ranlib, riscv64-linux-gnu-g++
# 删除，然后创建软链接指向相应的14版本
# 如
# sudo rm /usr/bin/gcc
# sudo ln -s /usr/bin/gcc-14 /usr/bin/gcc

# 下载protobuf源码进行编译安装
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

### 编译 LocalAI

下载我们的源码，根据下面操作进行编译

```bash
wget https://archive.spacemit.com/spacemit-ai/localai/localai.tar.gz
tar xvzf localai.tar.gz

# 切换到项目目录
cd localai

# 将Go工作目录下的bin文件夹添加到PATH环境变量中，确保可直接运行通过go install安装二进制的程序
# 编译过程中会使用到通过go install 安装的 protoc-gen-go 等工具
export PATH=$PATH:$(go env GOPATH)/bin

# 使用阿里云的代理，加速go模块下载
export GOPROXY=https://mirrors.aliyun.com/goproxy/,direct

# 进行编译
make build

# 如果编译遇到错误，处理完之后先 make clean 再 make build 重新编译

```

## 添加自定义推理后端

### 添加 RISC-V 加速的 llama.cpp 后端

我们内部对llamacpp进行了修改，使其支持RISC-V加速，并将其封装成grpc-server编译了一个二进制文件llama-cpp-riscv-spacemit，可通过下面的命令进行下载和部署。

```bash
cd backend/cpp/spacemit-llama-cpp
bash install.sh
```

执行**install.sh**脚本，会下载我们编译好的支持RISC-V加速的llamacpp-grpc-server 二进制文件和量化好的模型，自动添加到相关目录并创建配置文件。
回到项目的根目录，执行 **./local-ai --debug** ,则可启动LocalAI。
然后在浏览器打开 <http://localhost:8080/chat/> 进行测试。

如果在调用推理后端时，遇到下面的错误

    stderr llama-cpp-riscv-spacemit: error while loading shared libraries: libabsl_synchronization.so.20220623: cannot open shared object file: No such file or directory

则可以使用下面的命令进行处理

```bash
sudo apt install libabsl-dev
sudo ln -s /usr/lib/riscv64-linux-gnu/libabsl_synchronization.so /usr/lib/riscv64-linux-gnu/libabsl_synchronization.so.20220623
```

如果想使用我们的加速llamacpp后端推理其他模型，可

- 从<https://archive.spacemit.com/spacemit-ai/gguf/> 下载模型
- 从<https://archive.spacemit.com/spacemit-ai/modelfile/> 下载相应的modelfile
- 参考 **models/spacemit-qwen2.5-0.5b-instruct.yaml** 创建一个新模型的配置文件，注意配置文件中 model name和 stop words 和template 要使用新模型的内容，template部分可以参考modelfile的内容。

### 添加RISCV加速的ASR推理后端

项目代码位于 `backend/cpp/spacemit-asr-cpp`，可通过下面的命令进行部署和重启`local-ai`

```bash
cd backend/cpp/spacemit-asr-cpp
bash build.sh

cd ../../../
./local-ai --debug
```

然后可以通过下面的命令进行测试

```bash
# 事先准备好一个需要识别的音频文件 test.wav
curl -X POST http://localhost:8080/v1/audio/transcriptions \
    -H "Content-Type: multipart/form-data" \
    -F "file=@test.wav" \
    -F "model=sensevoicesmall-cpp"
```

### 添加C++版本的TTS推理后端

项目代码位于 `backend/cpp/matcha-tts-cpp`，可通过下面的命令进行部署和重启`local-ai`

```bash
cd backend/cpp/matcha-tts-cpp
bash build.sh

cd ../../../
./local-ai --debug
```

然后通过下面的命令进行测试

```bash
curl -X POST "http://localhost:8080/tts" \
     -H "Content-Type: application/json" \
     -d '{"input":"你好，今天天气怎么样","model":"matcha-tts-cpp"}' \
     -o output.wav 
```
