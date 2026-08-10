---
type: evidence
title: "SpacemiT Buildroot 编译指令、镜像生成与离线包下载参数规格"
status: needs_review
created: 2026-08-10
updated: 2026-08-10
aliases: [buildroot_compilation_parameters, Buildroot Make Parameters, Buildroot Commands Specs]
domain: bsp_kernel_drivers
target_audience: [BSP 工程师, CI/CD 工程师]
---

# SpacemiT Buildroot 编译指令、镜像生成与离线包下载参数规格

> [!TIP]
> **💡 工程师导读与排坑焦点**：存放 repo 源码同步、第三方 dl 包离线镜像与 Makefile 快捷构建命令。
> **目标读者**：`BSP 工程师 / CI/CD 工程师` | **技术领域**：`bsp_kernel_drivers`

本文档记录基于 SpacemiT Buildroot SDK 进行源码获取、快捷 Make 编译命令、镜像生成输出规范及第三方离线 dl 缓存镜像库的物理参数。

---

## 1. Repo 源码下载与分支管理指令

### K1 SDK (v2.2 推荐)

```bash
# 从 GitHub 拉取源码表
mkdir ~/buildroot-sdk-2.2 && cd ~/buildroot-sdk-2.2
repo init -u git@github.com:spacemit-com/manifests.git -b main -m k1-bl-v2.2.y.xml
repo sync
repo start k1-bl-v2.2.y --all
```

### K3 SDK (v1.0 推荐)

```bash
# 从 GitHub 拉取源码表
mkdir ~/k3-buildroot-sdk-1.0 && cd ~/k3-buildroot-sdk-1.0
repo init -u git@github.com:spacemit-com/manifests.git -b main -m k3-br-v1.0.y.xml
repo sync
repo start k3-br-v1.0.y --all
```

---

## 2. 离线第三方软件包 (dl) 镜像同步

为了避免因为 GitHub / GNU 官方服务器网络拥塞导致编译中断，可提前预下载全量第三方依赖包并置于 Buildroot `dl/` 目录：

```bash
# 官方预先打包的离线依赖镜像拉取命令
wget -c -r -nv -np -nH -R "index.html*" http://archive.spacemit.com/buildroot/dl/
```

---

## 3. Make 快捷构建指令集对比表

| 指令类别 | 命令名称 | 参数 / 例子 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **经典配置菜单** | `make envconfig` | - | 交互式选择配置方案（推荐首次完整编译使用） |
| **快捷完整构建** | `make <solution>-build` | `make k1_v2-build`<br>`make k3-build` | 直接编译指定方案（无需通过菜单交互） |
| **内核菜单配置** | `make <solution>-linux-menuconfig` | `make k1_v2-linux-menuconfig` | 打开 Linux 内核图形化 `menuconfig` 界面 |
| **U-Boot 菜单配置**| `make <solution>-uboot-menuconfig` | `make k1_v2-uboot-menuconfig` | 打开 Bootloader U-Boot 图形化配置界面 |
| **BusyBox 配置** | `make <solution>-busybox-menuconfig`| `make k1_v2-busybox-menuconfig`| 打开 BusyBox 工具箱工具菜单 |
| **单包重编译** | `make <solution>-pkg` | `make k1_v2-pkg PKG=mpp` | 单独重新编译特定软件包（如 mpp / drm-test） |
| **进入容器 Shell**| `make <solution>-shell` | `make k1_v2-shell` | 进入当前方案专属的 Docker 构建容器 |
| **清理编译产物** | `make <solution>-clean` | `make k1_v2-clean` | 清理特定方案的 output 输出产物 |

---

## 4. 镜像输出产物与格式规格

编译完成后，生成镜像存放于根目录 `output/<solution>/images/` 路径下：

| 镜像文件名 | 交付格式 | 适用于工具 / 场景 |
| :--- | :--- | :--- |
| `buildroot-<solution>.zip` | `.zip` 压缩包 | **Titan Flasher 刷机工具**，解压后亦可用 `fastboot` 刷入 eMMC |
| `sdcard.img` | `.img` raw 物理镜像 | 使用 `dd` 或 Etcher / Rufus 直接刻录至 **SD 卡 / MicroSD 卡** 启动 |
| `bootinfo_sd.bin` / `FSBL.bin` | `.bin` 固件分区 | 包含 MBR 引导分区头与第一阶段 Bootloader |

官方预编译体验镜像下载入口：[http://archive.spacemit.com/image/k1/version/bianbu-linux/](http://archive.spacemit.com/image/k1/version/bianbu-linux/)。
