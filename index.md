---
type: vault_index
title: "Spacemit LLM Wiki · 6大前瞻技术领域全栈索引"
status: approved
created: 2026-06-29
updated: 2026-08-10
aliases: [index, index.md, 索引, 全局索引]
---

# Spacemit LLM Wiki · 全栈索引网络

> [!NOTE]
> 本索引专为 **SpacemiT K1 / K3 处理器、PMIC 伴随电源芯片及生态开发板** 打造，全面解构芯片选型、电路设计、BSP 内核、Bianbu OS 生态、编译工具链及端侧 AI / 机器人应用。
> 知识库采用 **“线 - 面 - 点” 三层解构架构** 并按 **6 大前瞻技术领域** 归类展示：
> 1. **开发者旅程 (Developer Journeys - 线)**：任务驱动的极简通关上手向导。
> 2. **主题档案 (Knowledge Atoms - 面)**：软硬融合的排坑避坑与技术专题。
> 3. **事实证据 (Evidence - 点)**：芯片级物理参数、寄存器与测试数据。
> 4. **原始参考源 (Sources)**：GitHub 官方仓原始对照文件。

---

## 🔹 模块 1：芯片选型与产品物理规格 (Chip & Product Specs)
*面向产品选型、功耗评估与物理接口极限等研发生命周期前期视角。*

### 开发者上手向导
*   [[Developer_Journeys/K1芯片开发快速上手向导]] —— 帮助开发者从评估功耗、设计配置到跑通本地 1B 大模型的极简通关动线。
*   [[Developer_Journeys/K3芯片开发快速上手向导]] —— 帮助开发者从了解规格、设计散热到跑通本地大模型的极简通关动线。

### 主题档案 (Knowledge Atoms)
*   [[Knowledge_Atoms/K1热设计与功耗专题档案]] —— 汇总 K1 芯片 3W ~ 5W 超低 TDP 功耗、DVFS 调压与极简被动散热。
*   [[Knowledge_Atoms/K3热设计与散热专题档案]] —— 汇总 K3 芯片热学特性、结温限制与硬件散热设计指南。⚠️ 官方已撤回 `k3_thermal_design.md`。
*   [[Knowledge_Atoms/K3_RV2768_集群服务器专题档案]] —— �ᥰ 汇总基于 K3 处理器的 2U 768核 RISC-V 集群服务器架构、Redfish API 与计算节点管理。

### 事实证据与硬数据 (Evidence)
*   [[Evidence/k1_thermal_specs]] —— K1 芯片工作温度与 3W ~ 5W TDP 参数。
*   [[Evidence/k3_thermal_specs]] —— K3 芯片的热阻、最大功耗与极限结温参数。
*   [[Evidence/k1_material_avl_specs]] —— K1 平台经官方验证可量产的 DDR、闪存及外设厂商物料清单 (AVL)。
*   [[Evidence/k1_k3_display_specs]] —— K1 与 K3 芯片显示输出、编解码与接口极限分辨率。
*   [[Evidence/k1_k3_camera_specs]] —— K1 与 K3 芯片 MIPI CSI 通道组合与 ISP 并发处理规格。
*   [[Evidence/k1_k3_network_specs]] —— K1 与 K3 芯片以太网 MAC 控制器与无线 SDIO 通道电气参数。
*   [[Evidence/k1_k3_pcie_usb_specs]] —— K1 与 K3 芯片 PCIe 通道拆分、USB 接口及 SATA 桥接兼容型号。
*   [[Evidence/muse_pi_vs_pi_pro_specs]] —— 生态硬件开发板 Muse Pi 与 Muse Pi Pro 在主控、外设接口、音频 PA 等物理参数对比表。
*   [[Evidence/k3_pico_specs]] —— K3 Pico-ITX 迷你计算机的处理器、本地存储、万兆光网等核心硬件参数。
*   [[Evidence/k3_com260_specs]] —— K3 CoM260 开发套件核心板及参考载板的详细硬件规格数据。

---

## 🔹 模块 2：硬件电路设计与 PCB 避坑 (Hardware & PCB Design)
*面向原理图设计、PCB Layout 走线、Strap 引脚与 PMIC 电源网阻抗要点。*

### 开发者上手向导
*   [[Developer_Journeys/Muse_Pi_开发板快速上手向导]] —— 帮助开发者快速上手 MUSE Pi/Pro，完成系统烧录与硬件引脚调试。
*   [[Developer_Journeys/K3_Pico_开发板快速上手向导]] —— 帮助开发者熟悉 K3 Pico-ITX 迷你计算机，掌握单线点亮与电源优先级设计。

### 主题档案 (Knowledge Atoms)
*   [[Knowledge_Atoms/K1启动模式与Strap管脚配置专题档案]] —— 汇总 K1 芯片上电采样、Strap 硬件配置阻值与调试 JTAG 路由。
*   [[Knowledge_Atoms/K3启动模式与Strap管脚配置专题档案]] —— 汇总 K3 芯片 Strap 管脚配置、启动介质选择与硬件上下拉设计要求。
*   [[Knowledge_Atoms/SpacemiT生态板卡与PMIC电源配合专题档案]] —— 汇总 K1/P1 与 K3/P1S 电源轨配合、动态反馈调压以及 SW/FB PCB 布局走线。
*   [[Knowledge_Atoms/K1_K3显示系统与多媒体输出专题档案]] —— 汇总 HDMI/DSI 接口设计、电平转换、防静电与多媒体硬件规范。
*   [[Knowledge_Atoms/K1_K3摄像系统与图像处理专题档案]] —— 汇总 MIPI CSI 100Ω 差分走线等长、三摄/四摄并发与 DTS 通道绑定。
*   [[Knowledge_Atoms/K1_K3网络通信与千兆网口专题档案]] —— 汇总双路 GMAC 以太网、百兆 PHY 兼容限值及 Wi-Fi/BT 模组联调。
*   [[Knowledge_Atoms/K1_K3高速外设接口专题档案]] —— 汇总 PCIe 2.1/3.0 通道拆分限制、USB 主从切换与外部 SATA 扩展。
*   [[Knowledge_Atoms/Muse_Pi_板级硬件设计专题]] —— 汇总 MUSE Pi/Pro 开发板的 USB-PD 供电规范、Strap 拨码启动与 JTAG/UART 调试复用设计。
    *   [[Knowledge_Atoms/MUSE_Pi_26Pin_IOMAP管脚映射专题]] —— 汇总 MUSE Pi 26-Pin 扩展双排插针定义、JTAG/UART/CAN0/SPI3 引脚映射及 DTS 设备树路由表。
    *   [[Knowledge_Atoms/MUSE_Pi_Pro_40Pin_IOMAP管脚映射专题]] —— 汇总 MUSE Pi Pro 40-Pin 扩展双排插针定义、彩色功能定义与外设复用表。
*   [[Knowledge_Atoms/K3_Pico_板级硬件设计专题]] —— 汇总 K3 Pico 迷你主板的双电源输入优先级、高速 M.2 带宽复用、RT24 实时控制直出及双显示逻辑。
    *   [[Knowledge_Atoms/K3_Pico_扩展接口管脚映射专题]] —— 汇总 K3 Pico 26-Pin 与 36-Pin FPC 扩展连接器信号定义、GMAC-MII 网口与工业 CAN/SPI 映射。
*   [[Knowledge_Atoms/K3_COM260_板级硬件设计专题]] —— 汇总 K3 CoM260 开发套件的 12-Pin 多功能调试排针、CSI 摄像头多链路复用配置及 DSI 屏线热插拔红线。
    *   [[Knowledge_Atoms/K3_CoM260_40Pin_IOMAP管脚映射专题]] —— 汇总 K3 CoM260 40-Pin 标准扩展排针引脚定义、SPI/I2S/I2C 电平转换信号映射。

### 事实证据 (Evidence)
*   [[Evidence/k1_strap_pins_config]] —— K1 芯片六类 Strap 管脚物理连接与 JTAG 路由组合。
*   [[Evidence/k3_strap_pins_config]] —— K3 芯片五类 Strap Pins 配置管脚与电平功能组合。
*   [[Evidence/p1_pmic_specs]] —— Power Stone P1 PMIC 芯片各电轨输出电压、电流极限及引脚定义。
*   [[Evidence/p1s_pmic_specs]] —— Power Stone P1S PMIC 芯片电轨规格及精简引脚定义。

---

## 🔹 模块 3：BSP、Bootloader 与内核驱动 (BSP, Kernel & Drivers)
*面向 OpenSBI、U-Boot、Linux Kernel 6.6/6.18、Buildroot SDK 编译与 DTS 驱动移植。*

### 开发者上手向导
*   [[Developer_Journeys/Buildroot_SDK_快速编译与镜像生成向导]] —— 帮助开发者从环境依赖准备、repo 代码拉取到容器/宿主机编译和镜像生成上板。

### 主题档案 (Knowledge Atoms)
*   [[Knowledge_Atoms/Buildroot_嵌入式系统定制与内核编译专题档案]] —— 汇总 SpacemiT K1/K3 Buildroot SDK 架构、Repo 版本分支表、Make 指令、esos.elf 启动红线与软硬件中间件。
*   [[Knowledge_Atoms/K1系统启动与分区配置专题档案]] —— 汇总 K1 芯片 ramfs 调试启动、自启脚本、U-Boot与OpenSBI合并及隐藏分区配置。
*   [[Knowledge_Atoms/K1驱动调试与设备控制专题档案]] —— 汇总 K1 芯片 PD 充电、DTS 启用 I2C、PWM 控制及 GPADC 采集调试方法。
*   [[Knowledge_Atoms/K1_DDR_eMMC_AVL兼容性验证SOP专题档案]] —— 汇总 LPDDR4x 与 eMMC 兼容性测试、温箱压测及判定标准。
*   [[Knowledge_Atoms/K3安全启动SecureBoot开发专题档案]] —— �ᥰ 汇总 K3 芯片安全启动信任链架构、eFuse 不可逆烧录约束、FIT 签名容器与密钥管理规范。

### 事实证据 (Evidence)
*   [[Evidence/buildroot_bsp_specs]] —— K1 与 K3 Buildroot SDK 核心组件、Repo 版本分支映射表与宿主机/Docker 依赖规格。
*   [[Evidence/buildroot_compilation_parameters]] —— Buildroot repo 拉取、离线第三方 dl 镜像地址与 Makefile 快捷指令对比。
*   [[Evidence/esos_rcpu_firmware_specs]] —— RCPU (Real-Time CPU) `esos.elf` 固件规格、软硬件职责与启动硬依赖规则。

---

## 🔹 模块 4：Bianbu OS 系统与软件生态 (Bianbu OS & System Distribution)
*面向 Bianbu OS 刷机镜像、包管理、桌面/服务端环境、图形驱动与系统集成。*

### 主题档案 (Knowledge Atoms)
*   [[Knowledge_Atoms/K1软件开发与系统集成FAQ专题档案]] —— 汇总多媒体显示、网络栈部署、性能压测与 OTG 等系统集成疑难解答。

---

## 🔹 模块 5：工具链、调试与编译支持 (Toolchains, Debug & Tools)
*面向 RISC-V Vector 1.0 工具链、Titan Flasher 刷机与 JTAG/UART 物理调试。*

### 事实证据与排坑参数 (Evidence)
*   [[Evidence/k1_hardware_debug_parameters]] —— K1 芯片阻抗要求、休眠功耗、RTC精度及调试接口规范。

### 主题档案 (Knowledge Atoms)
*   [[Knowledge_Atoms/K1硬件外设接口与物理调试专题档案]] —— 汇总 K1 芯片调试串口/JTAG物理接口定义与供电避坑原则。

---

## 🔹 模块 6：端侧 AI 推理与机器人应用 (Edge AI & Embodied Robotics)
*面向 SpaceAI 软件栈、llama.cpp IME 矢量加速、ONNX Runtime / vLLM 部署与 ROS 2 具身应用。*

### 开发者上手向导
*   [[Developer_Journeys/SpaceAI_模型量化与端侧推理快速上手向导]] —— 帮助开发者从模型导出、XSlim 量化校准到使用 SpaceMIT EP 跑通端侧 AI 加速。
*   [[Developer_Journeys/ROS2_机器人与具身智能快速上手向导]] —— 帮助开发者从准备 ROS 2 环境、连接 micro-ROS/硬件到部署 LeRobot ACT 模仿学习与 Reachy Mini 交互。

### 主题档案 (Knowledge Atoms)
*   [[Knowledge_Atoms/SpaceAI_端侧大模型量化与部署专题档案]] —— 汇总 SpacemiT A60 智算核同构架构、XSlim 模型量化、ONNX Runtime EP 接入及 vLLM/llama.cpp 部署。
*   [[Knowledge_Atoms/K1大模型本地推理与AI算力专题档案]] —— 汇总 K1 芯片双簇 X60 架构、2.0 TOPS AI 算力与 1B 大模型端侧部署、llama.cpp IME 编译标志。
*   [[Knowledge_Atoms/K3大模型本地推理与AI算力专题档案]] —— 汇总 K3 芯片大模型本地运行速度、算力指标及软硬件融合部署方案。
*   [[Knowledge_Atoms/SpacemiT_ROS2_机器人与具身智能专题档案]] —— 汇总 SpacemiT K1/K3 平台 ROS 2 Humble/Jazzy 环境、DDS 调优、micro-ROS 串口/硬件总线桥接及 LeRobot/ACT 具身模型部署。

### 事实证据 (Evidence)
*   [[Evidence/space_ai_architecture_specs]] —— SpacemiT A60 智算核 (AI CPU) 同构融合架构、IME 矩阵扩展规格 (4x8x4) 与 cpufp 实测算力 (2.046 TOPS)。
*   [[Evidence/space_ai_software_stack_specs]] —— SpaceAI 软件栈全景、SpaceMITExecutionProvider 接口、XSlim 模型量化工具链参数与算子支持规格。
*   [[Evidence/k1_ai_performance_data]] —— K1 芯片通用 50KDMIPS、2.0 TOPS 算力与 1B 大模型实测、A100 AI Core 与安全引擎规格。
*   [[Evidence/k3_ai_performance_data]] —— K3 芯片在 AI 算力与主流大模型本地推理的实测数据。
*   [[Evidence/ros2_platform_specs]] —— SpacemiT K1/K3 平台 ROS 2 发行版支持、DDS 中间件网络调优、micro-ROS 接口及节点资源开销。
*   [[Evidence/robot_hardware_specs]] —— Reachy Mini、LeRobot SO101 机械臂、Linksee 移动机器人物理规格及端侧 ACT/SmolVLA 模仿学习模型数据。

---

## 4. 原始参考源 (Sources)
*只作为底层事实出处，不作为日常知识入口。*

### SpaceAI 计算软件栈与工具链 (docs-ai)
*   [SpaceAI 设计理念与同构智算核（原始文件）](Sources/docs-ai/zh/architecture/concept.md)
*   [Matrix 扩展指令集（原始文件）](Sources/docs-ai/zh/architecture/instruction.md)
*   [AI 计算软件栈总览（原始文件）](Sources/docs-ai/zh/compute_stack/ai_compute_stack.md)

### ROS 2 机器人与具身智能套件 (docs-ros)
*   [SpacemiT ROS 2 & 具身智能机器人套件简介（原始文件）](Sources/docs-ros/zh/root_overview.md)
*   [ROS 2 环境搭建与底层接口配置指南（原始文件）](Sources/docs-ros/zh/ros2_bsp.md)
*   [具身智能与机器人示例应用指南（原始文件）](Sources/docs-ros/zh/robot_applications.md)

### Buildroot SDK 嵌入式构建 (docs-buildroot)
*   [Buildroot SDK 概述（原始文件）](Sources/docs-buildroot/zh/root_overview.md)
*   [K1 Buildroot 简介（原始文件）](Sources/docs-buildroot/zh/k1_buildroot/intro.md)
*   [K1 Buildroot 源码下载与编译指南（原始文件）](Sources/docs-buildroot/zh/k1_buildroot/source.md)
*   [K3 Buildroot 简介（原始文件）](Sources/docs-buildroot/zh/k3_buildroot/intro.md)
*   [K3 Buildroot 源码下载与编译指南（原始文件）](Sources/docs-buildroot/zh/k3_buildroot/source.md)
*   [K3 安全启动开发指南（原始文件）](Sources/docs-buildroot/zh/k3_buildroot/device/secureboot.md)

### K1 芯片系列 (docs-chip)
*   [K1 产品简介（原始文件）](Sources/docs-chip/zh/key_stone/k1/k1_docs/root_overview.md)
*   [K1 数据手册（原始文件）](Sources/docs-chip/zh/key_stone/k1/k1_docs/k1_ds.md)
*   [K1 硬件设计指南（原始文件）](Sources/docs-chip/zh/key_stone/k1/k1_hw/k1_hw_design_guide.md)
*   [K1 硬件 AVL 列表（原始文件）](Sources/docs-chip/zh/key_stone/k1/k1_hw/k1_hw_avl.md)
*   [K1 硬件 AVL 验证 SOP（原始文件）](Sources/docs-chip/zh/key_stone/k1/k1_hw/avl_veri_sop.md)
*   [K1 硬件常见问题 FAQ（原始文件）](Sources/docs-chip/zh/key_stone/k1/k1_hw/k1_hw_faq.md)
*   [K1 硬件参考资源（原始文件）](Sources/docs-chip/zh/key_stone/k1/k1_hw/k1_hw_resources.md)
*   [K1 SDK 使用指南（原始文件）](Sources/docs-chip/zh/key_stone/k1/k1_sw/k1_sdk_user_guide.md)
*   [K1 软件常见问题 FAQ（原始文件）](Sources/docs-chip/zh/key_stone/k1/k1_sw/k1_sw_faq.md)

### K3 芯片系列 (docs-chip)
*   [K3 产品简介（原始文件）](Sources/docs-chip/zh/key_stone/k3/k3_docs/root_overview.md)
*   [K3 数据手册（原始文件）](Sources/docs-chip/zh/key_stone/k3/k3_docs/k3_ds.md)
*   [K3 硬件设计指南（原始文件）](Sources/docs-chip/zh/key_stone/k3/k3_hw/k3_hw_design_guide.md)
*   ~~[K3 热设计指南（原始文件）](Sources/docs-chip/zh/key_stone/k3/k3_hw/k3_thermal_design.md)~~ **⚠️ 官方已于 2026-08 撤回**
*   [K3 SDK 使用指南（原始文件）](Sources/docs-chip/zh/key_stone/k3/k3_sw/k3_sdk_user_guide.md)
*   [K3 硬件资源下载 (v2.1)](Sources/docs-chip/en/key_stone/k3/k3_hw/k3_hw_resources.md)
*   [K3 硬件 FAQ（原始文件）](Sources/docs-chip/zh/key_stone/k3/k3_hw/k3_hw_faq.md)

### 伴随电源系列 (Power Stone PMIC)
*   [P1 产品简介（原始文件）](Sources/docs-chip/zh/power_stone/p1/p1_docs/root_overview.md)
*   [P1 硬件设计指南（原始文件）](Sources/docs-chip/zh/power_stone/p1/p1_hw/p1_pcb_guide.md)
*   [P1S 产品简介（原始文件）](Sources/docs-chip/zh/power_stone/p1s/p1s_docs/root_overview.md)
*   [P1S 数据手册（原始文件）](Sources/docs-chip/zh/power_stone/p1s/p1s_docs/p1s_ds.md)

### 生态产品与终端系列 (docs-product)
*   **MUSE Pi 开发板**：[产品简介](Sources/docs-product/zh/k1_muse_pi/root_overview.md) · [用户使用指南](Sources/docs-product/zh/k1_muse_pi/pi_user_guide.md) · [硬件设计资源](Sources/docs-product/zh/k1_muse_pi/pi_hw.md)
*   **MUSE Pi Pro 开发板**：[产品简介](Sources/docs-product/zh/k1_muse_pi_pro/root_overview.md) · [用户使用指南](Sources/docs-product/zh/k1_muse_pi_pro/pi_pro_user_guide.md) · [硬件设计资源](Sources/docs-product/zh/k1_muse_pi_pro/pi_pro_hw.md)
*   **K3 Pico 迷你计算机**：[产品简介](Sources/docs-product/zh/k3_pico/root_overview.md) · [用户使用指南](Sources/docs-product/zh/k3_pico/pico_user_guide.md) · [硬件设计资源](Sources/docs-product/zh/k3_pico/pico_hw_resources.md)
*   **K3 CoM260 开发套件**：[产品简介](Sources/docs-product/zh/k3_com260/root_overview.md) · [用户使用指南](Sources/docs-product/zh/k3_com260/com260_user_guide.md) · [硬件设计资源](Sources/docs-product/zh/k3_com260/com260_hw_resources.md) · [核心板数据手册](Sources/docs-product/zh/k3_com260/com260_ds.md)
*   **MUSE Card 计算卡**：[产品简介](Sources/docs-product/zh/k1_muse_card/root_overview.md) · [用户使用指南](Sources/docs-product/zh/k1_muse_card/card_user_guide.md) · [硬件设计资源](Sources/docs-product/zh/k1_muse_card/card_hw.md)
*   **MUSE Book 笔记本**：[产品简介](Sources/docs-product/zh/k1_muse_book/root_overview.md) · [用户使用指南](Sources/docs-product/zh/k1_muse_book/book_user_guide.md) · [硬件设计资源](Sources/docs-product/zh/k1_muse_book/book_hw.md)
*   **MUSE Paper 墨水屏**：[产品简介](Sources/docs-product/zh/k1_muse_paper/root_overview.md) · [用户使用指南](Sources/docs-product/zh/k1_muse_paper/paper_user_guide.md) · [硬件设计资源](Sources/docs-product/zh/k1_muse_paper/paper_hw.md)
*   **MUSE Box 迷你主机**：[产品简介](Sources/docs-product/zh/k1_muse_box/root_overview.md) · [用户使用指南](Sources/docs-product/zh/k1_muse_box/box_user_guide.md)
*   **MUSE Shelf 实验架**：[产品简介](Sources/docs-product/zh/k1_muse_shelf/root_overview.md)
*   **RISC-V Labkit 实验箱**：[产品简介](Sources/docs-product/zh/k1_riscv_labkit/root_overview.md)
*   **K3 RV2768 集群服务器**：[产品简介](Sources/docs-product/zh/k3_rv2768/root_overview.md) · [技术白皮书](Sources/docs-product/zh/k3_rv2768/rv2768_white_paper.md) · [Redfish 接口说明](Sources/docs-product/zh/k3_rv2768/rv2768_redfish.md)
*   **售后服务规范**：[售后服务说明](Sources/docs-product/zh/service.md)

---

## 5. 规则与日志
*   [[Agent]] —— 知识库运行与 AI Agent 协作规范。
*   [[log]] —— 重构与维护日志。
