---
type: developer_journey
title: "Buildroot SDK 快速编译与镜像生成向导"
status: needs_review
created: 2026-08-10
updated: 2026-10-21
aliases: [Buildroot_SDK_快速编译与镜像生成向导, Buildroot Quick Start Guide]
domain: bsp_kernel_drivers
source_file: "Sources/docs-buildroot/zh/k1_buildroot/source.md"
source_commit: "163a8fccf8e7071f3177753d2e86e482e97970fe"
source_section: "K1/K3 源码指南 开发环境/版本分支/下载代码/交叉编译/打包产物"
source_resolution: partial
verification_status: unverified
source_checked_at: 2026-10-21
source_note: "覆盖两代 manifest、容器构建、方案选择与产物名；未实际下载 SDK、编译或刷写硬件。 本轮为来源与关键步骤定向核对，未在实物执行；关联节点保留各自核验状态。"
source_related_file: ["Sources/docs-buildroot/zh/k3_buildroot/source.md"]
source_related_commit: ["163a8fccf8e7071f3177753d2e86e482e97970fe"]
---
# Buildroot SDK 快速编译与镜像生成向导

先选择 K1 或 K3，使用各自的 [K1 源码指南](../Sources/docs-buildroot/zh/k1_buildroot/source.md) / [K3 源码指南](../Sources/docs-buildroot/zh/k3_buildroot/source.md)。以下示例绑定 K1 v2.2 与 K3 v1.0，不跨版本套用。

## 1. 准备环境

官方推荐 Ubuntu 20.04 或更新 LTS，以及足够的内存/SSD。K1 Buildroot 2.2.7 起与 K3 SDK 默认在容器构建，按原文安装 Docker CE；选择宿主机构建时才按对应系统安装原文依赖。不要把旧版 `sudo pip3` 示例当作所有新版 Ubuntu 的通用安装方式。

## 2. 获取对应清单

安装 repo 并配置 GitHub SSH 后，分别在独立工作目录执行相应示例：

```bash
# K1 v2.2
repo init -u git@github.com:spacemit-com/manifests.git -b main -m k1-bl-v2.2.y.xml
repo sync
repo start k1-bl-v2.2.y --all
```

```bash
# K3 v1.0：不要复用 K1 清单
repo init -u git@github.com:spacemit-com/manifests.git -b main -m k3-br-v1.0.y.xml
repo sync
repo start k3-br-v1.0.y --all
```

版本矩阵参见 [[Evidence/buildroot_bsp_specs]]，实际清单以所选 SDK 发布版本为准。

## 3. 方案选择与编译

首次执行 `make envconfig`，按显示的名称选择：K1 示例 `spacemit_k1_v2_defconfig`，K3 示例 `spacemit_k3_defconfig`。菜单编号随版本变化，不能只记固定编号。支持新命令的分支可查 `make help` 后使用 `make k1_v2-build` / `make k3-build`；旧命令环境与新命令不兼容时按原文迁移。

内核、U-Boot、单包和打包参数参见 [[Evidence/buildroot_compilation_parameters]] 与 [[Knowledge_Atoms/Buildroot_嵌入式系统定制与内核编译专题档案]]，不要把两代快捷命令混用。

当前两份源码指南的已选方案示例使用 `make linux-menuconfig` 配置内核，`make linux-update-defconfig` 保存；U-Boot 对应 `make uboot-menuconfig` 与 `make uboot-update-defconfig`。带 `<solution>-` 前缀的快捷形式和单包命令须以该分支 `make help` 为准，配置完成仍需重新构建和打包，不能把打开菜单当作镜像已生成。

## 4. 检查产物再烧录

K1 示例输出 `output/k1_v2/images/buildroot-k1_v2.zip` 和 `buildroot-k1_v2-sdcard.img`；旧稿笼统的 `sdcard.img` 不是该日志中的最终文件名。K3 官方日志示例为 `/k3/images/Buildroot-k3-20260425142457-sdcard.img` 及对应 ZIP；实际输出目录、时间戳与大小写以该次打包日志为准。

zip 按 Titan/fastboot 指南使用；SD 镜像按所选板型烧录，确认设备名、介质和备份后操作。先检查目标板的启动与供电条件，参见 [[Knowledge_Atoms/Muse_Pi_板级硬件设计专题]]；本次文档复核没有执行刷写。
