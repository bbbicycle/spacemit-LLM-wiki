# Spacemit Wiki MCP Server

`spacemit-wiki` MCP 服务为 AI Agent 提供了访问进迭时空 (Spacemit) RISC-V 芯片、生态板卡及完整边缘 AI 软件栈的高密度知识库与 1000+ 篇官方原始手册的只读数据通道。

---

## Endpoint & Setup

* **官方公共 SSE 服务端点**：`https://mcp.yao1302.xyz/sse`

客户端配置文件路径速查：

| 编辑器 / 客户端 | 配置文件路径 |
| :--- | :--- |
| **Cursor** | `.cursor/mcp.json` 或 `Settings -> Features -> MCP Servers` |
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) |
| **VS Code** | `.vscode/mcp.json` |
| **Antigravity** | `~/.gemini/antigravity/mcp/` |
| **Windsurf** | `mcp_config.json` |

### 标准 JSON 配置

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

## Tools Reference

> **Tip:** MCP 工具专为“零切片 (Zero-Chunking)”高密度上下文设计。`read_knowledge_atom` 与 `get_developer_journey` 会返回完整无截断的工程 Markdown，加载一次后请在多轮对话中复用上下文，避免重复调用。

### 1. `search_wiki`
按关键词、别名或 6 大技术领域模糊搜索精炼知识库。
* **Input**:
  * `query` (string, required): 搜索关键词（如 `"Muse Pi"`, `"千兆网"`, `"K1 Strap"`, `"PMIC"`）。
  * `domain` (string, optional): 领域过滤，可选值：`chip_product_specs`, `hardware_schematic_design`, `bsp_kernel_drivers`, `bianbu_os_distribution`, `toolchain_debug_tools`, `edge_ai_robotics`。
* **Output**: 返回最相关的 5 个节点列表，仅包含标题、类型、Domain 及 150 字卡片摘要。

### 2. `get_developer_journey`
【动线/线】整篇获取特定硬件板卡或核心任务的极简上手动线。
* **Input**:
  * `board_or_task` (string, required): 板卡或任务标识（如 `"muse_pi"`, `"k3_pico"`, `"buildroot"`）。
* **Output**: 完整上手步骤 Markdown，包含引用的专题档案双链与关键检查点。

### 3. `read_knowledge_atom`
【专题/面】整篇获取特定技术专题档案（零切片无损上下文）。
* **Input**:
  * `atom_name` (string, required): 专题名称或别名（如 `"千兆网口"`, `"热设计"`, `"PMIC电源"`, `"IOMAP"`）。
* **Output**: 完整技术专题 Markdown，包含原理、电路走线避坑、DTS 配置与调试排障指南。

### 4. `get_evidence_fact`
【事实/点】获取 100% 结构化的底层物理数据与电气参数。
* **Input**:
  * `spec_name` (string, required): 事实数据表名（如 `"k1_strap_pins_config"`, `"p1_pmic_specs"`, `"k1_k3_network_specs"`）。
* **Output**: 绝对准确的引脚映射表、Strap 电阻配置表、寄存器定义或热阻数据。

### 5. `get_graph_relations`
【图谱拓扑】顺着双链探索特定节点的上下游软硬件依赖关系。
* **Input**:
  * `node_name` (string, required): 节点名称或别名。
* **Output**: 该节点的 `outlinks`（依赖的底层知识）与 `backlinks`（被哪些上层动线/专题引用）。

### 6. `search_raw_sources`
【原始资料层】在 1052 篇官方芯片手册、驱动文档和板级设计源码清单中检索。
* **Input**:
  * `query` (string, required): 搜索关键词或函数符号（如 `"uart fifo"`, `"gmac dts"`, `"dwc3 pcie"`）。
  * `submodule` (string, optional): 子模块过滤：`docs-chip`, `docs-product`, `docs-buildroot`, `docs-ai`, `docs-ros`。
* **Output**: 匹配到的官方原始 Markdown 文件路径、章节大纲与 Raw GitHub 链接。

### 7. `read_raw_source_file`
【原始资料穿透】从本地或 GitHub 官方仓库按需实时拉取原始 Markdown/源码章节。
* **Input**:
  * `file_path_or_url` (string, required): 原始文件相对路径（如 `"docs-chip/zh/soc/uart.md"`）或 raw_url。
  * `start_line` (number, optional): 起始行号 (1-indexed)。
  * `end_line` (number, optional): 结束行号。
* **Output**: 指定范围的官方芯片手册原始文本。
