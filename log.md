---
type: vault_log
title: "SpacemiT K3 芯片文档重构日志"
status: active
created: 2026-06-29
updated: 2026-06-29
---

# SpacemiT K3 芯片文档重构日志 (log.md)

> [!NOTE]
> 本文件用于记录 K3 芯片测试知识库的重构、清理和验证日志。

---

## [2026-06-29] ingest | 导入并清洗 K3 开源文档基础源
*   **数据源**：从 GitHub `spacemit-com/docs-chip` 递归抓取 `zh/key_stone/k3` 的核心文件。
*   **导入成果**：
    *   `Sources/docs-chip/zh/key_stone/k3/k3_docs/root_overview.md` (产品简介)
    *   `Sources/docs-chip/zh/key_stone/k3/k3_docs/k3_ds.md` (数据手册)
    *   `Sources/docs-chip/zh/key_stone/k3/k3_hw/k3_hw_design_guide.md` (硬件设计指南)
    *   `Sources/docs-chip/zh/key_stone/k3/k3_hw/k3_thermal_design.md` (热设计指南)
    *   `Sources/docs-chip/zh/key_stone/k3/k3_sw/k3_sdk_user_guide.md` (SDK 使用指南)
*   **处理策略**：通过 Python 脚本清洗了 `read_url_content` 抓取时附加的 HTTP 元数据，还原了最原始的 Markdown 内容。

## [2026-06-29] optimize | 初始化三层网状架构并构建试验性样板
*   **内务建设**：新建了 `index.md` 与 `log.md`。
*   **重构样板 A（热设计）**：
    *   新建原子证据：[[Evidence/k3_thermal_specs]] (提取自 `k3_thermal_design.md` 和 `k3_ds.md`)
    *   新建主题档案：[[Knowledge_Atoms/K3热设计与散热专题档案]] (串联热设计理论、物理参数与原始参考源)
*   **重构样板 B（AI与大模型）**：
    *   新建原子证据：[[Evidence/k3_ai_performance_data]] (提取自 `root_overview.md`)
    *   新建主题档案：[[Knowledge_Atoms/K3大模型本地推理与AI算力专题档案]] (串联算力参数、网络部署与原始参考源)
*   **重构样板 C（启动配置与 Strap Pins）**：
    *   新建原子证据：[[Evidence/k3_strap_pins_config]] (提取自 `k3_hw_design_guide.md`)
    *   新建主题档案：[[Knowledge_Atoms/K3启动模式与Strap管脚配置专题档案]] (串联 Strap Pins 管脚组合、上下拉设计与原始参考源)
*   **重构样板 D（场景旅程）**：
    *   新建快速上手向导：[[Developer_Journeys/K3芯片开发快速上手向导]] (串联热设计、启动配置与大模型部署)
*   **验证状态**：已成功运行本地数据一致性校验，发现并拦截了测试冲突数据。

## [2026-06-29] maintenance | 清理 URL 编码重名文件并建立 Agent 协作规范
*   **文件清理**：清理了由于链接编码问题在 `Developer_Journeys/` 目录下产生的重名文件 `K3%E8%8A%AF%E7%89%87%E5%BC%80%E5%8F%91%E5%BF%AB%E9%80%9F%E4%B8%8A%E6%89%8B%E5%90%91%E5%AF%BC.md`，将完整 5 步内容合并并覆盖至中文命名的 [[Developer_Journeys/K3芯片开发快速上手向导]]。
*   **建立规范**：在根目录下创建了 [[Agent|Spacemit LLM Wiki 运行与协作规范 (Agent.md)]]，定义了知识库在 LLM Wiki 模式下的定位、三层目录结构、YAML 元数据规范以及 Agent 的 Ingest/Talk/Lint 三大工作流，以指导后续人机协同更新。
*   **索引更新**：在 [[index]] 中补充了关于 `Agent.md` 的导航入口。
*   **元数据与数据优化**：
    *   将 [[Developer_Journeys/K3芯片开发快速上手向导]] 的 `type` 从 `deck_pattern` 修正为 `developer_journey`。
    *   将三个 `Knowledge_Atoms/` 主题档案的 `type` 从 `topic_dossier` 修正为 `knowledge_atom`。
    *   在 [[Evidence/k3_ai_performance_data]] 中删除了因自动生成笔误产生的物理上不合理的 `Qwen3-80B-A3B` 模型推理性能数据（该数据与 30B 数据完全一致，且已超出 K3 的 30B 本地运行上限）。

## [2026-06-29] ingest & optimize | 导入 K1 核心源并构建 K1 三层知识体系
*   **原始文件导入**：从 GitHub `spacemit-com/docs-chip` 的 `zh/key_stone/k1/` 目录递归抓取、清洗并分类保存了全部原始文档：
    *   `Sources/docs-chip/zh/key_stone/k1/k1_docs/`：产品简介、数据手册及用户手册。
    *   `Sources/docs-chip/zh/key_stone/k1/k1_hw/`：硬件设计指南、AVL 列表、验证 SOP、常见问题 FAQ、参考资源等。
    *   `Sources/docs-chip/zh/key_stone/k1/k1_sw/`：SDK 使用指南、软件常见问题 FAQ 等。
*   **图片下载与重构优化**：
    *   通过自研同步清洗脚本，下载了 K1 硬件文档引用的全部原理图和设计图图片（保存在 `k1_hw/static/` 目录下）。
    *   将原本无序的哈希乱码图片名称（例如 `XZHWbMYUNol3PuxGJWTcMh6Nnnb.jpg`）**批量重命名为具有明确技术含义的文件名**（例如 `k1_ddr_circuit.jpg`、`k1_reset_circuit.jpg`、`k1_pmic_circuit.jpg` 等共 51 张图片）。
    *   自动扫描并更新了 [k1_hw_design_guide.md](Sources/docs-chip/zh/key_stone/k1/k1_hw/k1_hw_design_guide.md) 中所有的图片引用链接，使其完美渲染并解决关系图谱中“乱码节点”的问题。
*   **构建 K1 三层架构**：
    *   **事实证据层 (Evidence)**：
        *   新建：[[Evidence/k1_thermal_specs]] (工作温度与 TDP 功耗)
        *   新建：[[Evidence/k1_ai_performance_data]] (50KDMIPS通用算力、2.0 TOPS AI算力与 1B 本地大模型推理数据)
        *   新建：[[Evidence/k1_strap_pins_config]] (六类 Strap 配置引脚电平与功能组合)
        *   新建：[[Evidence/k1_hardware_debug_parameters]] (提取自 FAQ 的阻抗要求、休眠功耗及调试电平数据)
    *   **主题档案层 (Knowledge Atoms)**：
        *   新建：[[Knowledge_Atoms/K1大模型本地推理与AI算力专题档案]] (X60双簇架构、TCM加速与零成本编程范式)
        *   新建：[[Knowledge_Atoms/K1启动模式与Strap管脚配置专题档案]] (上电采样、Strap 原理图设计规范)
        *   新建：[[Knowledge_Atoms/K1热设计与功耗专题档案]] (3W~5W 低功耗调压与极简散热方案)
        *   新建：[[Knowledge_Atoms/K1硬件外设接口与物理调试专题档案]] (串口/JTAG物理引脚与供电避坑设计)
        *   新建：[[Knowledge_Atoms/K1系统启动与分区配置专题档案]] (指定 ramfs 启动、自启脚本、its 固件合并与隐藏分区)
        *   新建：[[Knowledge_Atoms/K1驱动调试与设备控制专题档案]] (PD充电、DTS配置I2C、PWM 控制及 GPADC 电压采集)
    *   **开发者旅程层 (Developer Journeys)**：
        *   新建：[[Developer_Journeys/K1芯片开发快速上手向导]] (串联规格熟悉、功耗评估、Strap配置、SDK选择到大模型部署)

## [2026-06-29] optimize | 产品级全量外设、电源管理与开发板并网重构
*   **多媒体与高速外设解构**：
    *   **事实证据层 (Evidence)**：
        *   新建：[[Evidence/k1_k3_display_specs]] (K1与K3显示、硬解码分辨率与接口规格)
        *   新建：[[Evidence/k1_k3_camera_specs]] (CSI 通道与 ISP 并发极限规格)
        *   新建：[[Evidence/k1_k3_network_specs]] (以太网 GMAC 百兆兼容限值与无线参数)
        *   新建：[[Evidence/k1_k3_pcie_usb_specs]] (PCIe 拆分、USB复用与SATA桥接兼容列表)
        *   新建：[[Evidence/muse_pi_vs_pi_pro_specs]] (Muse Pi与Muse Pi Pro开发板级硬件规格对比表)
    *   **主题档案层 (Knowledge Atoms)**：
        *   新建：[[Knowledge_Atoms/K1_K3显示系统与多媒体输出专题档案]] (HDMI静电防护与电平转换、DSI背光与闲置引脚供电)
        *   新建：[[Knowledge_Atoms/K1_K3摄像系统与图像处理专题档案]] (MIPI CSI 走线阻抗、三摄/四摄并发及 DMA 绕行设计)
        *   新建：[[Knowledge_Atoms/K1_K3网络通信与千兆网口专题档案]] (双GMAC单双口设计、百兆PHY不兼容规避与无线SDIO联调)
        *   新建：[[Knowledge_Atoms/K1_K3高速外设接口专题档案]] (PCIe 2.1/3.0 通道分配红线、USB OTG及SATA免驱芯片)
        *   新建：[[Knowledge_Atoms/SpacemiT生态板卡与PMIC电源配合专题档案]] (K1/P1 远端反馈DVFS、P1 闹钟开机BUG避坑及开发板硬件差异编译适配)
*   **电源芯片原始文档并网**：将 PMIC P1/P1S 原始数据手册与 PCB 走线指南并网归档于 `Sources/`。
*   **索引维护**：更新了 [[index]]，挂载所有全新的通用外设专题、开发板对比专题及 PMIC 芯片原始文件。

## [2026-06-29] ingest & optimize | 全量原始文档整理与知识图谱系统化提炼
*   **知识库重命名与物理迁移**：
    *   将知识库目录从 `Spacemit_Docs_K3_Test` 正式重命名为 **`Spacemit LLM Wiki`**，移出 iCloud 目录并存放于本地个人主目录下 `/Users/bicycle/Spacemit LLM Wiki`，避免云端同步冲突。
    *   全局更新了所有 17 个文档中的 120 余处绝对路径链接，将其重定向为新的本地路径格式 `file:///Users/bicycle/Spacemit%20LLM%20Wiki/...`。
    *   在知识库根目录下创建了可双击直接运行的一键更新脚本 `双击更新文档.command`，方便手动一键拉取上游官方文档仓库 `spacemit-com/docs-chip` 的更新。
    *   对含有损坏及还原后多余字节的 `index.md` 进行了字节修复和编码清洗，使其符合 100% 规范的 UTF-8。
*   **文档系统化提炼成果**：
    *   **事实证据层 (Evidence)**：
        *   新建：[[Evidence/k1_material_avl_specs]] (存放 K1 平台经官方认证的 DDR/闪存及外设 AVL 器件选型清单与下载入口)
        *   新建：[[Evidence/p1_pmic_specs]] (提取自 P1 数据手册的各电压轨输出电压、电流极限、绝对最大额定值及引脚封装规格)
        *   新建：[[Evidence/p1s_pmic_specs]] (提取自 P1S 数据手册的各电压轨规格、NC 引脚说明及精简特性)
    *   **主题档案层 (Knowledge Atoms)**：
        *   新建：[[Knowledge_Atoms/K1_DDR_eMMC_AVL兼容性验证SOP专题档案]] (提炼自官方 SOP 的样机配置、商规/工规环境温测试矩阵、`memtester` 与 `fio` 压测指令及判定标准)
        *   新建：[[Knowledge_Atoms/K1软件开发与系统集成FAQ专题档案]] (提炼自 70KB FAQ 文件的多媒体与显示控制、无线网络与蓝牙软件栈部署、全系统性能压力测试指令、USB Gadget 与跨系统分区兼容性配置)
        *   修改：[[Knowledge_Atoms/K1系统启动与分区配置专题档案]] (并入开机自启脚本细节、长按 Power 键消抖与检测机制、U-Boot 阶段通过 DTS 预启电源轨如 `SWITCH_REG1` 的设计方法)
        *   修改：[[Knowledge_Atoms/K1驱动调试与设备控制专题档案]] (并入命令行 GPIO 控制、DTS 临界温控保护临界关机、Type-C 状态检测以及以太网 PHY 指示灯 LCR 寄存器自定义)
        *   修改：[[Knowledge_Atoms/SpacemiT生态板卡与PMIC电源配合专题档案]] (并入 P1/P1S PCB 布局布线规范如 Cin/Cout/SW 走线/FB 远端反馈网络，以及模拟 PHY 供电磁珠隔离红线与测流电阻短接合并规则)
    *   **架构索引与自检 (Lint & Log)**：
        *   更新 [[index]] 索引，挂载了所有全新的专题档案与事实证据节点，彻底清除了尾部的脏行与重复内容。
        *   完成了所有文档的格式与双链自检，确保无破损链接。

## [2026-06-30] ingest & optimize | 目录重构、链接双链化与生态产品文档并网重构
*   **链接双链化与失效路径重定向**：
    *   将库中所有形如 `file:///` 的本地文件绝对路径链接，批量安全重构为 Obsidian 标准的 `[[双向链接]]`（共修复了 17 个文件），从而彻底恢复了图谱连线。
    *   物理上将 `Sources/github_raw` 重命名为 `Sources/docs-chip`，与公司 GitHub 仓库 `docs-chip` 命名一致。
    *   批量重定向了所有指向已失效旧路径的链接，使它们准确指向 `Sources/docs-chip/zh/...` 下真实的物理文档（共修正了 20 个文件）。
*   **生态产品文档 (docs-product) 并网**：
    *   物理上将官方产品文档仓库 `spacemit-com/docs-product` 克隆至本地 `Sources/docs-product` 下。
    *   修改并升级了 [[Agent]] 协作规范，制定了产品文档在“线-面-点”架构中的定位，添加了“产品 ➡️ 芯片”的双链映射规范与自检工作流。
    *   **事实证据层 (Evidence)**：
        *   新建：[[Evidence/k3_pico_specs]] (提取 K3 Pico 规格、网络、存储及 EC 电气数据)
        *   新建：[[Evidence/k3_com260_specs]] (提取 K3 CoM260 核心板与参考载板物理参数)
    *   **主题档案层 (Knowledge Atoms)**：
        *   新建：[[Knowledge_Atoms/Muse_Pi_板级硬件设计专题]] (MUSE Pi/Pro 的 12V PD 供电规范、Strap 拨码启动与 JTAG/UART 调试复用)
        *   新建：[[Knowledge_Atoms/K3_Pico_板级硬件设计专题]] (K3 Pico 的双电源输入优先级、高速 M.2 动态带宽复用、RT24 实时控制直出及双显示逻辑)
        *   新建：[[Knowledge_Atoms/K3_COM260_板级硬件设计专题]] (K3 CoM260 开发套件的 12-Pin 多功能调试接口、CSI 多路复用配置及 DSI 屏线热插拔红线)
    *   **开发者上手动线 (Developer Journeys)**：
        *   新建：[[Developer_Journeys/Muse_Pi_开发板快速上手向导]] (MUSE Pi 系统烧录与首次启动配置，跑通本地 1B 语音模型部署)
        *   新建：[[Developer_Journeys/K3_Pico_开发板快速上手向导]] (K3 Pico 的全功能单线点亮步骤、U-Boot 与 UEFI 启动设置，使用统一内存跑通本地 8B/30B 大模型)
*   **索引注册与自检**：
    *   更新 [[index]] 索引，完整注册了上述新增的生态产品上手动线、板级硬件设计专题与事实数据。
    *   在 [[index]] 的“4. 原始参考源 (Sources)”中登记了 `docs-product` 旗下全部 10 个生态产品的原始文档双链，消除了所有未分类 of 孤立节点。

## [2026-07-02] maintenance | 引入本地 0-Token 拓扑自检工具并净化知识图谱
*   **工具引入**：在知识库根目录下新建了本地 0-Token 拓扑自检脚本 `vault_linker_lint.py`。该脚本基于图论算法和正则表达式，自动检查 YAML Frontmatter 格式与字段合规性校验“线-面-点”引用规则、并检测孤立节点和 `index.md` 挂载状态。
*   **图谱自检与净化**：
    *   首次运行脚本，成功扫出 14 处破损链接和越级引用错误。
    *   **修复特殊文件豁免**：在脚本中豁免了全局控制文件（`index.md`、`log.md`、`Agent.md`）对 `Developer_Journeys` 的拓扑反向引用检查。
    *   **净化说明示例**：对 `log.md` 和 `Agent.md` 里的概念解释和语法说明性质的“伪双向链接”增加了反引号包裹（如将 `[[双向链接]]`、`[[专题名称]]` 改为行内代码格式），防止其在 Obsidian 物理图谱中生成红色坏链垃圾节点。
    *   **重新运行自检**：43 个物理文档 100% 成功通过校验，链接关系彻底健康。

## [2026-08-10] ingest & optimize | 导入 SpacemiT Buildroot SDK 文档并重构构建与内核定制知识体系
*   **原始文件导入**：
    *   克隆 GitHub `spacemit-com/docs-buildroot` 仓库至本地 `Sources/docs-buildroot` 目录，包含 K1 与 K3 基于 Buildroot 构建的 SDK 全套原始指南。
*   **三层架构提炼与知识并网**：
    *   **事实证据层 (Evidence)**：
        *   新建：[[Evidence/buildroot_bsp_specs]] (提取 K1/K3 SDK 核心组件架构、Repo Manifest XML 版本映射、defconfig 方案矩阵及容器/宿主机依赖规格)
        *   新建：[[Evidence/buildroot_compilation_parameters]] (记录 SDK 源码 Repo 下载命令、第三方依赖包 `dl` 离线镜像拉取、Makefile 快捷构建命令表及镜像输出格式)
        *   新建：[[Evidence/esos_rcpu_firmware_specs]] (解构实时 RCPU 固件 `esos.elf` 职责、硬件模块初始化、HDMI Audio 中断转发以及内核启动死锁硬红线)
    *   **主题档案层 (Knowledge Atoms)**：
        *   新建：[[Knowledge_Atoms/Buildroot_嵌入式系统定制与内核编译专题档案]] (系统性串联 Buildroot 整体架构、Docker 容器构建、`make envconfig` 方案选择、`linux-menuconfig`/`uboot-menuconfig` 配置、`esos.elf` 依赖与镜像输出)
    *   **开发者上手动线 (Developer Journeys)**：
        *   新建：[[Developer_Journeys/Buildroot_SDK_快速编译与镜像生成向导]] (提供环境准备 $\rightarrow$ Repo 同步 $\rightarrow$ 交叉编译 $\rightarrow$ 镜像刻录与刷机调试的极简通关路线)
*   **架构索引与自检 (Index & Lint)**：
    *   更新 [[index]] 索引，完整挂载了所有 Buildroot 新节点及 Sources 原始文件索引。
    *   运行自检工具，完成全局 YAML Frontmatter 及图谱连线校验。

## [2026-08-10] ingest & optimize | 导入 SpacemiT ROS 2 & 机器人套件文档并重构具身智能知识体系
*   **原始文件导入**：
    *   导入 `docs-ros` 全套原始指南置于 `Sources/docs-ros/zh/`，涵盖 ROS 2 (Humble/Jazzy) 环境配置、micro-ROS 驱动总线与机器人应用。
*   **三层架构提炼与知识并网**：
    *   **事实证据层 (Evidence)**：
        *   新建：[[Evidence/ros2_platform_specs]] (记录 SpacemiT K1/K3 ROS 2 发行版、CycloneDDS/FastDDS 中间件调优、micro-ROS 串口接口及节点内存/CPU 资源占用)
        *   新建：[[Evidence/robot_hardware_specs]] (记录 Reachy Mini、LeRobot SO101 6-DoF 机械臂及 Linksee 移动机器人物理规格与 ACT/SmolVLA 具身模型推理参数)
    *   **主题档案层 (Knowledge Atoms)**：
        *   新建：[[Knowledge_Atoms/SpacemiT_ROS2_机器人与具身智能专题档案]] (系统性串联 ROS 2 架构、DDS 优化、micro-ROS 硬件桥接及 LeRobot/ACT 具身模型部署)
    *   **开发者上手动线 (Developer Journeys)**：
        *   新建：[[Developer_Journeys/ROS2_机器人与具身智能快速上手向导]] (提供准备 ROS 2 环境 $\rightarrow$ 硬件/micro-ROS 连接 $\rightarrow$ 端侧 LeRobot ACT 推理控制的极简通关路线)
*   **架构索引与自检 (Index & Lint)**：
    *   更新 [[index]] 索引，完整挂载了所有 ROS 2 新节点及 Sources 原始文件索引。
    *   运行自检工具，完成全局 YAML Frontmatter 及图谱连线校验。

## [2026-08-10] architecture & optimize | 全局面向未来拓展的 6 大前瞻技术模块架构重构与元数据标准化升级
*   **架构重构与标准升级**：
    *   在 [[Agent]] 协作规范中确立并标准化了 **6 大前瞻技术模块** 划分（芯片选型、硬件设计、BSP内核驱动、Bianbu OS、工具链调试、端侧 AI / 机器人），为后续持续并网 GitHub 仓（如 `docs-bianbu`, `docs-ai`, `toolchain`）奠定零阻碍可扩展基础。
    *   编写并执行 `update_wiki_domains.py` 自动化标注脚本，为全局 **41 个物理 Atom 与 Evidence 文件** 的 YAML Frontmatter 补全了 `domain` 与 `target_audience` 属性。
*   **工程师导读与排坑框增强**：
    *   为全量 Markdown 节点开篇统一注入了 `💡 工程师导读与排坑焦点` 提示框，明确标注该文档的目标工程师角色、适用研发阶段及核心避坑要点。
*   **全栈索引重构与 100% 拓扑校验**：
    *   重构了 [[index]] 全局导航网络，按 6 大技术模块将场景向导、主题档案、事实数据与 Sources 原始文件进行模块化挂载展示。
    *   运行自检脚本 `vault_linker_lint.py`，全局 **52 个物理 Markdown 文档** 0 警告、0 错误，拓扑健康度达到 100%。

## [2026-08-10] ingest & optimize | 导入 SpacemiT SpaceAI (docs-ai) 软件栈并提炼智算核同构量化与部署体系
*   **原始文件导入**：
    *   解压导入 GitHub `spacemit-com/docs-ai` 至 `Sources/docs-ai/zh/`，涵盖 AI CPU 同构架构理念、IME 矩阵扩展指令及 SpaceAI 计算软件栈。
*   **三层架构提炼与知识并网**：
    *   **事实证据层 (Evidence)**：
        *   新建：[[Evidence/space_ai_architecture_specs]] (提取 A60 智算核同构融合架构、256-bit Vector 1.0、IME 矩阵单元 4x8x4 及其 cpufp 实测 2.046 TOPS Int8 / 533.65 GFLOPS FP16 峰值性能)
        *   新建：[[Evidence/space_ai_software_stack_specs]] (记录 SpaceAI 软件栈多层级交付矩阵、ONNX Runtime `SpaceMITExecutionProvider` 参数、XSlim 模型量化与 Triton/vLLM 规格)
    *   **主题档案层 (Knowledge Atoms)**：
        *   新建：[[Knowledge_Atoms/SpaceAI_端侧大模型量化与部署专题档案]] (系统解构智算核同构原理、XSlim 工具链 PTQ/算子融合、ONNX Runtime EP 接入与 llama.cpp/vLLM 端侧部署)
    *   **开发者上手动线 (Developer Journeys)**：
        *   新建：[[Developer_Journeys/SpaceAI_模型量化与端侧推理快速上手向导]] (提供 ONNX 导出 $\rightarrow$ XSlim 量化校准 $\rightarrow$ ONNX Runtime EP 加速推理的极简通关路线)
*   **索引与自检 (Index & Lint)**：
    *   更新 [[index]] 索引，挂载至 **模块 6：端侧 AI 推理与机器人应用** 之下。
    *   全局运行 `vault_linker_lint.py` 拓扑自检，56 个物理 Markdown 文档 100% 成功通过校验。

## [2026-08-10] architecture & iomap | 多板卡硬件管脚 (IOMAP) 强制结构化提炼与 Agent 规范持久化升级
* **规范持久化升级**：
    * 更新 [[Agent|Agent.md]] 运行与协作规范，在 `Ingest` 工作流中新增 **硬件管脚与 IOMAP 强制结构化红线**，规定后续凡录入或更新包含扩展接口 (Header/Connector) 的板卡/芯片文档，Agent 必须强制将其转换为标准的结构化 Markdown 表格并创建 `*_IOMAP管脚映射专题` 知识原子。
* **硬件管脚结构化并网**：
    * 新建：[[Knowledge_Atoms/MUSE_Pi_26Pin_IOMAP管脚映射专题]] (解构 MUSE Pi 26-Pin 扩展双排插针定义、JTAG/UART/CAN0/SPI3 引脚映射及 DTS 设备树路由表)
    * 新建：[[Knowledge_Atoms/K3_CoM260_40Pin_IOMAP管脚映射专题]] (解构 K3 CoM260 40-Pin 标准扩展排针引脚定义、SPI/I2S/I2C 电平转换信号映射)
    * 新建：[[Knowledge_Atoms/K3_Pico_扩展接口管脚映射专题]] (解构 K3 Pico 26-Pin 与 36-Pin FPC 扩展连接器信号定义、GMAC-MII 网口与工业 CAN/SPI 映射)
* **知识图谱关联与索引更新**：
    * 分别更新 [[Knowledge_Atoms/Muse_Pi_板级硬件设计专题]]、[[Knowledge_Atoms/K3_COM260_板级硬件设计专题]] 及 [[Knowledge_Atoms/K3_Pico_板级硬件设计专题]]，建立向新 IOMAP 专题的双向链接。
    * 更新 [[index]] 索引树，挂载三大板卡的 IOMAP 结构化节点。






