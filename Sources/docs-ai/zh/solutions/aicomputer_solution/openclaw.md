sidebar_position: 8

# OpenClaw(云端算力)

## 环境要求

- 平台: Linux RISC-V 64
- Node.js: >= 22.12.0
- 包管理器: pnpm 10.23.0
- 硬件：进迭时空 K1 或 K3 开发板

## 平台支持情况

|      平台 & 系统       |       是否支持     |
|-----------------------|-----------------------|
| K1 Buildroot          | ❌ 不支持              |
| K1 OpenHarmony     | ❌ 不支持              |
| K1 Bianbu LXQT/GNOME    | ✅ 支持            |
| K3 Buildroot          | ❌ 不支持              |
| K3 OpenHarmony    | ❌ 不支持              |
| K3 Bianbu LXQT/GNOME  | ✅ 支持                |

## 普通用户安装 OpenClaw 步骤

### 1. 安装 nvm，用于 node version 的管理

```
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
```

![alt text](../static/image-1.png)

如果 nvm 找不到，执行以下面的命令：

```
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
source ~/.bashrc
```

### 2. 下载 npm 安装包 (如果你需要通过文件安装)
如果你通过 https://www.npmjs.com/package 安装，可以不下载安装文件。

点击下载：[npm安装包](https://archive.spacemit.com/spacemit-ai/openclaw/openclaw-2026.3.8.1.tgz)

![alt text](../static/image.png)

### 3. 安装 nodejs22

对于 K3 开发板：

```
NVM_NODEJS_ORG_MIRROR=https://archive.spacemit.com/nodejs/k3 nvm install 22
```

对于 K1 开发板：

```
NVM_NODEJS_ORG_MIRROR=https://archive.spacemit.com/nodejs/k1 nvm install 22
```

输入：
```
nvm use 22
```

### 4. 安装 openclaw

##### OpenClaw 的二种安装方式:

执行以下命令，通过 npm 源安装 OpenClaw
```
npm i -g --legacy-peer-deps @dengxifeng/openclaw --force --registry=https://registry.npmjs.org/
```


通过下载的npm包安装
```
npm install -g --legacy-peer-deps ./openclaw-2026.3.8.1.tgz
```

### 5. 配置 openclaw

执行以下命令开始配置
```
openclaw onboard
``` 

安装结束后，开始配置 openclaw，以下为使用 Kimi 模型 的配置示例
![alt text](../static/image-2.png)

配置完成后，终端将输出一个带 Token 的本地访问地址，例如：

```
http://127.0.0.1:18789/#token=7229793a7a0a32ff206ab91230ac991221c84301dc3447e6
```

在浏览器中打开该链接即可访问 OpenClaw Web UI

后面token是在配置结束后，控制台显示的那行
![alt text](../static/image-3.png)

## 开发者用户 构建安装、二次开发 openclaw

### 代码仓库

[https://github.com/SpaceX-mit/openclaw-riscv64](https://github.com/SpaceX-mit/openclaw-riscv64)

### 指南

[https://github.com/SpaceX-mit/openclaw-riscv64/blob/main/BUILD_RUN_GUIDE.md](https://github.com/SpaceX-mit/openclaw-riscv64/blob/main/BUILD_RUN_GUIDE.md)

[https://github.com/SpaceX-mit/openclaw-riscv64/blob/main/PACKAGE_BUILD_COMPLETE.md](https://github.com/SpaceX-mit/openclaw-riscv64/blob/main/PACKAGE_BUILD_COMPLETE.md)

## 官方参考
[https://github.com/openclaw/openclaw](https://github.com/openclaw/openclaw)
[https://www.openclawcenter.com/](https://www.openclawcenter.com/)
