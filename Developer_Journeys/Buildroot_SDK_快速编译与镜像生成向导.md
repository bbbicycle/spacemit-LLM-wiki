---
type: developer_journey
title: "Buildroot SDK 快速编译与镜像生成向导"
status: needs_review
created: 2026-08-10
updated: 2026-08-10
aliases: [Buildroot_SDK_快速编译与镜像生成向导, Buildroot Quick Start Guide]
---

# Buildroot SDK 快速编译与镜像生成向导

本上手向导提供从环境配置、源码获取、工程编译到烧录镜像生成的极简通关动线，帮助开发者快速在 SpacemiT K1 / K3 芯片与生态开发板上跑通基于 Buildroot 的 Linux 操作系统。

---

## 🗺️ 通关路线图

```mermaid
graph LR
    Step1[1. 环境准备] --> Step2[2. 源码与依赖同步]
    Step2 --> Step3[3. 方案配置与编译]
    Step3 --> Step4[4. 镜像生成与烧录]
```

---

## 步骤 1：准备开发环境与安装依赖

推荐使用 **Ubuntu 20.04 / 22.04 LTS**，或任何已安装 Docker CE 的 Linux 系统。

```bash
# 安装基础构建依赖项
sudo apt-get update
sudo apt-get install -y git build-essential cpio unzip rsync file bc wget python3 python-is-python3 libncurses5-dev libssl-dev dosfstools mtools u-boot-tools flex bison python3-pip
sudo pip3 install pyyaml
```

详细环境依赖与 Docker 容器要求请参考 [[Evidence/buildroot_bsp_specs|Buildroot 宿主机与容器依赖规格]]。

---

## 步骤 2：使用 Repo 同步 SDK 源码

获取 Google `repo` 工具并完成拉取（以 K1 v2.2 及 K3 v1.0 分支为例）：

```bash
# 1. 初始化工作目录
mkdir ~/buildroot-sdk && cd ~/buildroot-sdk

# 2. 从 GitHub 拉取 Manifest 源码清单
repo init -u git@github.com:spacemit-com/manifests.git -b main -m k1-bl-v2.2.y.xml

# 3. 同步全量源码
repo sync
repo start k1-bl-v2.2.y --all

# 4. (可选) 预下载第三方依赖包加速编译
wget -c -r -nv -np -nH -R "index.html*" http://archive.spacemit.com/buildroot/dl/
```

源码分支与版本对应关系请查阅 [[Evidence/buildroot_bsp_specs|Repo 版本分支映射表]]。

---

## 步骤 3：选择方案并开始交叉编译

进入 SDK 根目录，使用配置菜单或快捷命令开始构建：

### 方式 A：交互式选择编译（推荐首次使用）

```bash
make envconfig
```
* **针对 K1 全功能开发板**：输入 `5` (`spacemit_k1_v2_defconfig`) 并回车。
* **针对 K1 硬实时控制**：输入 `4` (`spacemit_k1_rt_defconfig`) 并回车。
* **针对 K3 开发板**：输入 `2` (`spacemit_k3_defconfig`) 并回车。

### 方式 B：无交互命令行快捷构建

```bash
# 直接编译 K1 v2 全功能方案
make k1_v2-build

# 直接编译 K3 方案
make k3-build
```

更多内核 `menuconfig` 及单包重编译指令请查阅 [[Evidence/buildroot_compilation_parameters|Make 快捷编译指令表]] 与 [[Knowledge_Atoms/Buildroot_嵌入式系统定制与内核编译专题档案|Buildroot 嵌入式系统定制与内核编译专题档案]]。

---

## 步骤 4：镜像产物获取与烧录

编译完成后，构建系统会自动生成刷机镜像并输出到 `output/<solution>/images/` 目录：

1. **Titan Flasher 固件刷写**：
   定位至 `output/k1_v2/images/buildroot-k1_v2.zip` 压缩包，使用 SpacemiT 官方 Titan Flasher 工具解压或直接连接线刷。
2. **MicroSD 卡直接刻录**：
   定位至 `output/k1_v2/images/sdcard.img`，在 Linux 宿主机上执行 `dd` 命令：
   ```bash
   sudo dd if=output/k1_v2/images/sdcard.img of=/dev/sdX bs=1M status=progress conv=fsync
   ```

硬件引脚复用与线刷/卡刷调试步骤请参阅 [[Knowledge_Atoms/Muse_Pi_板级硬件设计专题|Muse Pi 板级硬件设计专题]]。
