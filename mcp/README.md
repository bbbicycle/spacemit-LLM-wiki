# Spacemit LLM Wiki - 双层知识图谱 MCP Server (v2.0)

本项目提供了专为 **Spacemit 芯片与产品知识库** 定制的 MCP Server。
严格遵循 `Agent.md` 规范与 Anthropic MCP 协议，构建了 **“精炼知识图谱 + 原始资料源（Sources/）动态穿透”** 的双层知识服务架构。

---

## 🛠️ 包含的 7 大 MCP Tools

| 层级 | 工具名称 | 功能说明 | 数据来源 |
| :--- | :--- | :--- | :--- |
| **精炼知识层** | **`search_wiki`** | 按关键词、别名、技术领域快速定位精炼节点 | 内存索引 |
| **精炼知识层** | **`get_developer_journey`** | 整篇获取板卡操作动线与双链（线） | 内存原子 |
| **精炼知识层** | **`read_knowledge_atom`** | 整篇无损获取驱动/外设/硬件设计专题档案（面） | 内存原子 |
| **精炼事实层** | **`get_evidence_fact`** | 直出结构化引脚复用表、Strap 配置、电气参数（点） | 内存原子 |
| **图谱拓扑层** | **`get_graph_relations`** | 顺着双链探索芯片与板卡的依赖出链和被引用入链 | 拓扑图谱 |
| **原始资料层** | **`search_raw_sources`** | 在 1052 篇原始芯片与产品手册清单中检索文件与章节 | 原始清单 |
| **原始资料层** | **`read_raw_source_file`** | 按需实时穿透拉取 GitHub 官方仓库的原始 Markdown/源码 | GitHub 动态拉取 |

---

## 🚀 部署到 Cloudflare Workers（仅需 3 步，完全免费）

### 准备条件
- 安装了 Node.js（v18+）
- 拥有一个免费的 [Cloudflare 账号](https://dash.cloudflare.com/)（无需信用卡）

### 步骤 1：生成/更新最新索引
在项目根目录运行：
```bash
python3 scripts/build_mcp_index.py
```
*(自动解析 60 篇精炼文档与 1052 篇 Sources 原始文档大纲，生成 `mcp-worker/src/data/wiki_graph.json`)*

### 步骤 2：登录并部署 Worker
```bash
cd mcp-worker

# 1. 登录 Cloudflare（首次运行会在浏览器弹窗一键授权）
npx wrangler login

# 2. 一键发布上线
npx wrangler deploy
```

部署成功后，终端会打印出你的专属公开 URL，例如：
`https://spacemit-wiki-mcp.<你的子域名>.workers.dev/sse`

---

## 💻 外部开发者如何接入与使用？

外部开发者**无需 clone 仓库、无需安装任何环境**，只需在他们的 AI 工具中配置这个 URL：

### 1. Cursor IDE 配置
在 Cursor 的 `Settings -> Features -> MCP Servers` 中点击 **Add New MCP Server**：
* **Name**: `spacemit-wiki`
* **Type**: `sse`
* **URL**: `https://spacemit-wiki-mcp.<你的子域名>.workers.dev/sse`

### 2. Claude Desktop 配置
在 `claude_desktop_config.json` 中添加：
```json
{
  "mcpServers": {
    "spacemit-wiki": {
      "url": "https://spacemit-wiki-mcp.<你的子域名>.workers.dev/sse"
    }
  }
}
```

### 3. 本地免云端测试（Python）
如果你想在本地直接运行测试：
```bash
python3 mcp/test_navigation.py
```
