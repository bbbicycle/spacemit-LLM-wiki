# Spacemit LLM Wiki & 产品技术知识库
> **Spacemit LLM Wiki - Long-term LLM Knowledge Vault & Product Specification Knowledge Base for Spacemit RISC-V Ecosystem**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://www.python.org/)
[![Lint & Topology](https://img.shields.io/badge/Lint-Vault%20Linker%20Pass-brightgreen.svg)](vault_linker_lint.py)
[![CI/CD Pipeline](https://img.shields.io/badge/CI%2FCD-Auto%20Sync-orange.svg)](.github/workflows/sync_sources.yml)

[中文文档](#中文文档) | [English Documentation](#english-documentation)

---

<a name="中文文档"></a>
## 📖 中文文档

### 1. 项目简介 (Project Overview)

**Spacemit LLM Wiki** 是专为 **进迭时空 (Spacemit)** RISC-V 芯片（K1 / K3）、全系 12 款官方硬件产品与生态终端（MUSE Pi / K3 Pico-ITX / CoM260 / MUSE Book 笔记本 / MUSE Box 迷你主机 / MUSE Paper 墨水屏 / MUSE Card / MUSE Shelf / RV2768 集群 / RISC-V Labkit 实验箱等）及边缘侧软硬件生态（Buildroot BSP / Bianbu OS / SpaceAI 大模型推理 / ROS 2 具身智能）打造的**高密度、长效 LLM 知识库与外部记忆体**。

本知识库采用 **Obsidian 双链网络** 与 **线-面-点三层架构 +“产品生态矩阵 (L0/L1) 与技术机理内核 (L2~L5)”正交双轨拓扑** 设计，具备双重优势：
- **人类可读性**：工程师与商务团队可通过产品家族全景图谱、树状索引与工程师导读框精准浏览、选型与定位排坑指南。
- **AI 检索优化 (RAG-Friendly)**：基于 `Agent.md` **AI 检索效能优先原则**，严格规范 YAML Frontmatter 元数据、`domain` 领域划分与代际隔离围栏，实现平均 1 跳直达、零切片无损上下文与 75% 的 Token 降噪节约。

---

### 2. 🌐 Model Context Protocol (MCP) 云端服务接入

外部开发者**无需克隆代码库、无需本地安装 Python/Obsidian**，即可在 **Cursor、Claude Desktop、Antigravity、Windsurf** 等现代 AI 开发环境中直接连接并消费本知识库！

* **官方公共 MCP SSE 服务端点**：
  👉 `https://mcp.yao1302.xyz/sse`

#### 2.1 客户端一键配置

* **Cursor IDE 配置**：
  在 Cursor 设置中进入 `Features -> MCP Servers -> Add New MCP Server`：
  - **Name**: `spacemit`
  - **Type**: `sse`
  - **URL**: `https://mcp.yao1302.xyz/sse`

* **Claude Desktop 配置** (`claude_desktop_config.json`)：
  ```json
  {
    "mcpServers": {
      "spacemit-wiki": {
        "url": "https://mcp.yao1302.xyz/sse"
      }
    }
  }
  ```

#### 2.2 核心 7 大零切片 MCP 工具

| 层级 | 工具名称 | 功能描述 |
| :--- | :--- | :--- |
| **精炼知识层** | `search_wiki` | 按关键词、别名或技术领域搜索精炼知识库 |
| **精炼知识层** | `get_developer_journey` | 整篇获取开发板通关动线与步骤（线） |
| **精炼知识层** | `read_knowledge_atom` | 整篇获取产品系统与驱动/外设等专题档案（面，零切片） |
| **精炼事实层** | `get_evidence_fact` | 直出结构化引脚表、Strap 配置、电气参数（点，100% 精确） |
| **图谱拓扑层** | `get_graph_relations` | 顺着双链探索依赖出链与被引用入链 |
| **原始资料层** | `search_raw_sources` | 在 1180 篇 Sources 原始芯片/产品手册清单中检索 |
| **原始资料层** | `read_raw_source_file` | 按需实时穿透拉取 GitHub 官方仓库的原始 Markdown/源码 |

---

### 3. 🏛️ 项目架构与目录布局 (Architecture & Directory Layout)

#### 3.1 三层拓扑关系 (Three-Tier Topology)

知识库严格遵循 **单向引用红线**，划分为三个递进层次：

```
+-----------------------------------------------------------------------------------+
|                            Developer Journeys (上手步骤线)                          |
|  - 场景驱动的通关指南 (如 K1 芯片开发上手、Buildroot SDK 快速编译向导)                |
+-----------------------------------------------------------------------------------+
                                          |
                                          v (只能向下引用)
+-----------------------------------------------------------------------------------+
|                             Knowledge Atoms (知识面档案)                           |
|  - 结构化的模块技术文档 (如 K1/K3 电源配合、Strap Pins 配置、MIPI CSI 摄像系统)       |
+-----------------------------------------------------------------------------------+
                                          |
                                          v (只能向下引用)
+-----------------------------------------------------------------------------------+
|                               Evidence (数据事实点)                                |
|  - 绝对原子的物理规格与硬件参数 (如 p1_pmic_specs.md, k1_thermal_specs.md)            |
+-----------------------------------------------------------------------------------+
```

- **三层引用红线规则**：
  1. `Developer_Journeys` 只能引用 `Knowledge_Atoms` 或 `Evidence`，**严禁**嵌套引用其他 Journeys。
  2. `Knowledge_Atoms` 可引用其他 `Knowledge_Atoms` 或 `Evidence`。
  3. `Evidence` 必须保持绝对原子性，**严禁**向上引用 `Knowledge_Atoms` 或 `Developer_Journeys`。
  4. 任何普通文档**严禁反向引用** `Developer_Journeys`。

#### 3.2 目录树状布局 (Directory Tree)

```text
Spacemit LLM Wiki/
├── Developer_Journeys/         # [线] 开发者上手向导 (7 篇极简通关动线)
├── Knowledge_Atoms/            # [面] 核心技术专题档案 (31 篇: 产品系统档案 + 跨品技术机理双轨)
├── Evidence/                   # [点] 物理规格与硬件参数事实表 (27 篇 100% 结构化数据点)
├── Sources/                    # 进迭时空官方 Git 子模块源码与文档库
│   ├── docs-chip/              # K1/K3 芯片手册 Submodule
│   ├── docs-buildroot/         # Buildroot SDK 构建文档 Submodule
│   ├── docs-product/           # 板级与硬件设计 Submodule
│   ├── docs-ai/                # SpaceAI 模型量化与部署 Submodule
│   └── docs-ros/               # ROS2 机器人与具身智能 Submodule
├── static/                     # 静态资源、硬件电路原理图与引脚定义图
├── scripts/                    # 自动化与工程化维护脚本
│   ├── check_upstream_impact.py# 上游变更影响精准分析工具
│   ├── build_mcp_index.py      # 双层 MCP 索引构建与打包脚本
│   └── lint_wiki_integrity.py  # 事实完整性与防拼凑质检工具
├── mcp/                        # 本地 Stdio MCP Server (Python)
├── mcp-worker/                 # 云端 Serverless MCP Worker (Cloudflare)
├── index.md                    # 知识图谱全局索引与动线入口
├── log.md                      # 知识库版本演进与改动履历
├── Agent.md                    # AI Agent 运行、检索与协作规范
├── update_sources.sh           # 跨平台子模块一键同步 Shell 脚本
├── 双击更新文档.command         # macOS 专属一键同步桌面可执行脚本
├── vault_linker_lint.py        # 拓扑结构、Domain 字段及配图死链自动化校验工具
└── .github/workflows/          # CI/CD 自动化流水线
    └── sync_sources.yml        # 每日定时同步与双重 Lint 校验 GitHub Action
```

---

### 4. 🚀 快速开始 (Quick Start)

#### 3.1 仓库克隆与 Submodule 初始化

本知识库依赖进迭时空官方 5 大文档仓库作为 Sources 源。在克隆项目时，推荐使用 `--recursive` 参数一次性拉取全量子模块：

```bash
# 推荐：递归克隆主仓库及所有官方 Sources 子模块
git clone --recursive https://github.com/bbbicycle/spacemit-LLM-wiki.git
cd spacemit-LLM-wiki
```

若您在克隆时未使用 `--recursive`，可通过以下命令手动初始化并更新子模块：

```bash
# 已有仓库初始化并拉取子模块内容
git submodule update --init --recursive
```

---

### 5. 🔄 子模块与文档同步脚本 (Source Document Sync Scripts)

为了保持 Wiki 内容与进迭时空官方 Upstream 文档仓库持续同步，项目提供了跨平台同步工具：

#### 5.1 跨平台 Bash 脚本 (`update_sources.sh`)

可在 Linux / macOS / WSL 环境直接运行该脚本，自动遍历同步 `Sources/` 目录下的 5 个子模块：

```bash
# 赋予执行权限并运行同步
chmod +x update_sources.sh
./update_sources.sh
```

#### 5.2 macOS 一键双击同步 (`双击更新文档.command`)

在 macOS 系统中，工程师可以直接在 Finder 中双击 `双击更新文档.command` 文件。脚本将自动打开 Terminal 窗口并调用 `./update_sources.sh` 完成同步，同步完成后将在 5 秒后优雅关闭窗口。

---

### 6. 🔍 拓扑结构与事实完整性双重质检 (Dual-Layer Quality Lint)

项目内置了两套自动化 Python 校验脚本，兼顾图谱物理健康与技术事实真确性：

#### 6.1 图拓扑与静态配图校验 (`vault_linker_lint.py`)

在 Python 3 环境下直接运行：

```bash
python3 vault_linker_lint.py
```

*   **6 大前瞻技术领域 (`domain`) 校验**：严格校验 Frontmatter 的 `domain` 必填枚举值。
*   **Frontmatter 必填字段校验**：校验 `type`、`title`、`status`、`domain` 四大核心元数据。
*   **Obsidian 双链 `[[...]]` 破损检测**：支持物理文件名、`title` 映射与 `aliases` 别名库寻路。
*   **静态配图防死链校验**：扫描 Markdown 中所有图片引用，确认 `static/` 物理文件存在且 PNG 魔数结构完好。
*   **三层拓扑红线校验**：拦截越级引用（如 Evidence 向上引用 Atom/Journey）。
*   **孤立节点与索引挂载率**：拦截入度为 0 的孤立节点。

#### 6.2 事实完整性与防拼凑质检 (`scripts/lint_wiki_integrity.py`)

针对 LLM 知识库可能存在的代际混淆与概念虚构，提供高精度静态 AST 语义质检：

```bash
python3 scripts/lint_wiki_integrity.py
```

*   **代际混淆拦截**：严禁使用“SpacemiT 芯片”泛称并列绑定特定代际的专有性能指标（如将 2.0 TOPS 与 60 TOPS 混为一谈）。
*   **伪概念拦截**：拦截“VLA 原生支持”等将高阶算法架构与底层硬件指令混为一谈的伪概念。
*   **模型架构透明度**：提及 30B 大模型时，强制要求明确标注 MoE 架构与实际激活参数（Active 3B）。
*   **夸大宣发过滤**：拦截“支持所有主流大模型”等脱离嵌入式物理内存边界的过度承诺。

---

### 7. 🤖 CI/CD 自动同步逻辑 (Automation Pipeline)

GitHub Actions 工作流位于 `.github/workflows/sync_sources.yml`。

#### 7.1 运行机制与触发条件
- **定时触发**：每天 UTC 00:00 (北京时间 08:00) 自动触发。
- **手动触发**：支持在 GitHub 仓库 Actions 页面通过 `workflow_dispatch` 手动一键执行。

#### 7.2 CI/CD 执行步骤
1. **Checkout Submodules**：使用 `actions/checkout@v4` 递归拉取最新 Repository 与 Submodules。
2. **Execute Sync**：调用 `./update_sources.sh` 拉取并合并官方 upstream 分支变更。
3. **Run Linker Lint**：运行 `python3 vault_linker_lint.py` 进行 100% 拓扑与 Domain 校验。
4. **Run Integrity Lint**：运行 `python3 scripts/lint_wiki_integrity.py` 进行技术事实防幻觉校验。
5. **Auto Commit & Push**：若检测到源文件更新，使用 `github-actions[bot]` 自动提交改动并推送至主分支。

---

---

<a name="english-documentation"></a>
## 🇬🇧 English Documentation

### 1. Project Overview

**Spacemit LLM Wiki** is a high-density, long-term external memory and knowledge vault tailored for **Spacemit** RISC-V SoCs (K1 / K3), full-spectrum 12 official hardware products & ecosystem terminals (MUSE Pi, K3 Pico-ITX, CoM260, MUSE Book laptop, MUSE Box mini PC, MUSE Paper e-ink tablet, MUSE Card, MUSE Shelf, RV2768 cluster, RISC-V Labkit, etc.), and edge software/hardware stack (Buildroot BSP, Bianbu OS, SpaceAI LLM inference, and ROS 2 robotics).

Built upon **Obsidian Wikilinks**, a **Three-Tier Topology (Journeys - Atoms - Evidence)** and an **Orthogonal Dual-Track (Product Matrix L0/L1 + Technology Mechanism L2-L5)** architecture, it provides:
- **Human Readability**: Ecosystem portfolio trees, clear developer quick-start paths, modular topic archives, and inline tips for debugging.
- **AI/RAG Optimization**: Guided by the `Agent.md` **AI-First Retrieval & Accuracy Principle**, it enforces strict YAML Frontmatter metadata, 6 domain taxonomy classifications, and generational physical boundaries, achieving 1-hop precision and 75% token economy.

---

### 2. 🌐 Model Context Protocol (MCP) Cloud Service

External developers can directly consume this knowledge base in modern AI IDEs (**Cursor, Claude Desktop, Antigravity, Windsurf**) without cloning the repository or installing local environments:

* **Official Public MCP SSE Endpoint**:
  👉 `https://mcp.yao1302.xyz/sse`

#### Client Configuration

* **Cursor IDE**:
  `Settings -> Features -> MCP Servers -> Add New MCP Server`:
  - **Name**: `spacemit`
  - **Type**: `sse`
  - **URL**: `https://mcp.yao1302.xyz/sse`

* **Claude Desktop** (`claude_desktop_config.json`):
  ```json
  {
    "mcpServers": {
      "spacemit-wiki": {
        "url": "https://mcp.yao1302.xyz/sse"
      }
    }
  }
  ```

---

### 2. Quick Start & Submodule Setup

To clone the repository with all 5 Spacemit official source submodules:

```bash
git clone --recursive https://github.com/bbbicycle/spacemit-LLM-wiki.git
cd spacemit-LLM-wiki
```

If already cloned without submodules:

```bash
git submodule update --init --recursive
```

---

### 3. Synchronization & Automated Linting

#### Source Update Scripts
- **Linux / macOS Bash**: Run `./update_sources.sh` to pull the latest upstream source submodules.
- **macOS Desktop Shortcut**: Double-click `双击更新文档.command` to run the sync script in a pop-up terminal window.

#### Topology & Domain Linter
Run the local python validator:

```bash
python3 vault_linker_lint.py
```

The script validates:
1. **6 Tech Domains (`domain`)**:
   - `chip_product_specs`: Chip selection, TDP, package, thermal, AVL.
   - `hardware_schematic_design`: Schematics, Strap Pins, PMIC, DTS, pin mapping.
   - `bsp_kernel_drivers`: Buildroot, U-Boot, OpenSBI, drivers, esos.elf.
   - `bianbu_os_distribution`: Bianbu OS, Linux distribution, software packages.
   - `toolchain_debug_tools`: GCC/LLVM toolchain, JTAG, serial debug, physical debugging.
   - `edge_ai_robotics`: SpaceAI quantization, LLM inference, ROS 2, micro-ROS.
2. **Required Frontmatter**: `type`, `title`, `status`, `domain`.
3. **Wikilink Integrity**: Checks all `[[...]]` links with basename, title, and alias fallback.
4. **Static Image Protection**: Ensures image files exist, are non-zero size, and have intact PNG binary headers.
5. **Topology Rules**: Prevents illegal upward or reverse referencing across layers.

---

### 4. License & Contribution

This project is licensed under the Apache 2.0 License. Contributions, domain expansions, and documentation updates are welcome via GitHub Pull Requests!
