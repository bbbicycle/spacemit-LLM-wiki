---
type: knowledge_atom
title: "Spacemit K1 生态终端与教学实验套件专题档案"
domain: chip_product_specs
target_audience: [产品经理, 解决方案架构师, 市场销售, 高校教师, 嵌入式开发者]
status: "needs_review"
created: 2026-10-07
updated: "2026-10-20"
aliases: [K1生态终端, MuseBook, MuseBox, MuseCard, MusePaper, MuseShelf, RISCV实验箱, k1_terminal_products, K1衍生硬件]
source_file: "Sources/docs-product/zh/k1_series/k1_muse_paper/root_overview.md"
source_commit: "8c851807f2c54e8ba54d568b268100ca727d0777"
source_locator: "K1 MUSE Paper 简介；特性；产品规格；合作与采购咨询"
source_resolution: "partial"
verification_status: "unverified"
source_checked_at: "2026-10-20"
source_note: "本次仅定位已有引用对应的文件与章节，未对正文全部事实逐项复核；引用的 Evidence 保留各自历史版本与核验状态。"
source_origin: "https://github.com/spacemit-com/docs-product"
source_related_file: ["Sources/docs-product/zh/k1_series/k1_muse_book/root_overview.md", "Sources/docs-product/zh/k1_series/k1_muse_box/root_overview.md", "Sources/docs-product/zh/k1_series/k1_muse_card/root_overview.md", "Sources/docs-product/zh/k1_series/k1_muse_shelf/root_overview.md", "Sources/docs-product/zh/k1_series/k1_riscv_labkit/root_overview.md", "Sources/docs-chip/zh/key_stone/k1/k1_docs/root_overview.md"]
source_related_commit: ["8c851807f2c54e8ba54d568b268100ca727d0777", "8c851807f2c54e8ba54d568b268100ca727d0777", "8c851807f2c54e8ba54d568b268100ca727d0777", "8c851807f2c54e8ba54d568b268100ca727d0777", "8c851807f2c54e8ba54d568b268100ca727d0777", "1ea15a766287024a5bb7b548850826e3525a80dc"]
---

# Spacemit K1 生态终端与教学实验套件专题档案

> [!NOTE]
> **💡 业务与技术导读**：
> 本文系统梳理了围绕 **Spacemit K1 / M1 八核低功耗计算平台** 打造的 6 款官方生态终端与实验套件，覆盖**个人便携设备（笔记本/平板）、桌面整机（Mini-ITX）、边缘扩展卡、云算力服务器及高校教学实验箱**。
> 帮助开发者、政企客户与教育工作者快速掌握各终端的形态特点、杀手级功能与适用边界。

---

## 1. 个人便携计算与整机终端

### 1.1 MUSE Book：全球首款量产 RISC-V 笔记本电脑
* **定位画像**：为全球 RISC-V 极客、开源开发者和科研人员打造的原生硬件级便携开发本。
* **核心杀手级特点**：
  1. **原生开发闭环**：摆脱 QEMU 模拟器漫长卡顿，直接在真机上运行 Bianbu Desktop、GCC、Python、VSCode 与 Chromium。
  2. **轻薄便携与长续航**：14.1 英寸 1080P IPS 高清屏，铝合金超薄机身，采用 38 Wh / 7.6 V 电池，支持 PD 3.0 快充；续航随负载与配置变化。
  3. **标准扩容能力**：官方规格为 128 / 256 / 512 GB NVMe SSD，并支持 UHS-II TF 扩展。
* **适用场景**：高校计算机系学生日常编程、RISC-V 开源社区代码调试、移动 Linux 办公。

### 1.2 MUSE Box：Mini-ITX 迷你整机
* **定位画像**：标准 PC 形态的紧凑型 RISC-V 桌面小主机，主打“超静音、极低功耗、全接口”。
* **核心杀手级特点**：
  1. **无风扇设计**：官方简介提供低功耗、无风扇的产品定位；不推断整机实测功耗或电费。
  2. **双千兆网口与 HDMI**：规格表列出两路 RJ45 和 HDMI 1080P@60Hz，可用于轻量网络与桌面场景；未据此承诺 DP 或双屏异显。
  3. **标准 Mini-ITX 生态**：兼容标准工业机箱与桌面摆放，支持 Bianbu Desktop、Ubuntu、OpenKylin、Deepin。
* **适用场景**：家庭私有云存储、家庭自动化网关、极客桌面开发机、工业控制现场前置机。

### 1.3 MUSE Paper：RISC-V OpenHarmony 开发者平板
* **定位**：基于 K1 + P1 与 OpenHarmony 的开发者平板，面向工业和行业定制。
* **硬件配置**：10.95 寸 LCD、1200 × 1920；8 / 16 GB LPDDR4X；128 / 256 GB eMMC；7000 mAh 电池、18 W 快充。
* **软件与图形**：特性章节标注 OpenHarmony 5.0 / Linux 6.6，GPU/V2D 加速、DE 多图层渲染与 VPU 解码。
* **核验**：此前的「10.3 寸墨水屏、4 / 8 GB、64 GB」为 Wiki 整理错误，已按 [[Evidence/k1_terminal_products_specs|固定版本官方规格与出处]] 更正。

---

## 2. 算力扩展、集群机架与教学实验套件

### 2.1 MUSE Card：双 NVMe 微型计算卡
* **定位画像**：一张名片大小（85×56mm）的高密度存储与视觉扩展 SBC。
* **核心杀手级特点**：
  1. **板载双 M.2 NVMe 槽位**：在掌心尺寸内集成 2 个 M.2 2242 M-Key NVMe SSD 接口，读写吞吐远超传统 TF 卡或 eMMC。
  2. **双路 4-lane MIPI CSI 视觉输入**：支持高带宽并发视频采集，搭配 2.0 TOPS AI 算力可本地实现轻量 YOLO 目标检测。
* **适用场景**：便携式超小微 NAS、无人机吊舱前置视觉处理、移动侦测边缘节点。

### 2.2 MUSE Shelf：80 节点 RISC-V 云算力实验架
* **定位画像**：2U 标准机架式高密服务器，为全球开发者提供即开即用的远程 RISC-V 云端实例。
* **核心杀手级特点**：
  1. **80 颗处理器物理高密集成**：单台 2U 机箱内集成 80 颗 K1 八核芯片（共 640 个物理核心），采用 2/4 模块化刀片设计。
  2. **进迭云平台智能运维**：支持远程桌面投屏（VNC/RDP）、远程 SSH、WEB IDE、一键 Fastboot 批量刷机与远程上下电控制。
* **适用场景**：企业级 RISC-V 远程研发中心、开源软件自动化 CI/CD 编译测试农场、高校云端算力实验室。

### 2.3 RISC-V Labkit：嵌入式与 AI 高校教学实验箱
* **定位画像**：面向高校计算机体系结构、微机原理、操作系统与嵌入式 AI 课程的综合教学平台。
* **核心杀手级特点**：
  1. **一体化集成与可拆卸模块化**：内置 10.1 英寸 IPS 触摸屏，核心板与底板分离设计，标配丰富实验转接线与保护箱体。
  2. **积木式丰富外设生态**：支持温湿度传感器、步进电机、指纹识别、轻量机械臂、无线通信等十余种标准教学模块插拔。
  3. **教材与百余实验配套**：提供涵盖汇编指令、FreeRTOS、Linux 驱动、SpaceAI 模型推理等 100+ 完整教学实验例程。
* **适用场景**：高校电子工程、计算机学院实验教学，嵌入式大赛实训平台。

---

## 3. 选型与采购决策对比

| 产品名称 | 形态特点 | 是否需要外接屏幕 | 存储能力 | 典型适合谁买？ |
| :--- | :--- | :---: | :--- | :--- |
| **MUSE Book** | 笔记本 | 否 (14.1寸 IPS) | 128 / 256 / 512 GB NVMe + TF | 学生、个人极客，随时随地移动开发 |
| **MUSE Box** | 桌面主机 | 是 (需接显示器) | 32 GB eMMC + NVMe / SATA | 极客极客、家庭运维、工业控制箱集成 |
| **MUSE Paper**| LCD 平板 | 否 (10.95寸 LCD) | 128 / 256 GB eMMC | OpenHarmony 应用开发与行业定制 |
| **MUSE Card** | 裸板/亚克力 | 是 (通过HDMI/网络)| **双 M.2 NVMe 固态** | 做微型 NAS、边缘视觉盒子的工程师 |
| **MUSE Shelf**| 2U 服务器 | 否 (全远程云化) | 80 节点分布式存储 | 企业研发中心、开源基金会、高校算力云平台 |
| **RISC-V Labkit**| 实验箱 | 否 (自带10.1寸触屏)| eMMC + M.2 NVMe | 高校院系实验室、职业技术学院、培训机构 |

---

## 4. 关联事实参数与底座技术

* 详尽硬件参数表：[[Evidence/k1_terminal_products_specs|K1 生态衍生终端与实验套件物理规格参数]]
* 芯片级物理特性：[[Evidence/k1_thermal_specs|K1 芯片功耗与热学参数]]
* 电源方案配合：[[Knowledge_Atoms/SpacemiT生态板卡与PMIC电源配合专题档案|生态板卡与PMIC配合专题]]
* 芯片快速上手：参阅全局索引 [[index]] 中的 K1 开发者上手向导板块
