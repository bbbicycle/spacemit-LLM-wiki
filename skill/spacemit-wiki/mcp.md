# Spacemit Wiki MCP

通过 MCP 查询精炼知识与官方原始资料。仅接入 MCP 不会自动安装本 Skill；客户端也不会自动读取仓库的 `AGENTS.md`。完整规则需安装整个 Skill 目录。

## 接入

安装统一遵循 [INSTALL.md](https://github.com/bbbicycle/spacemit-LLM-wiki/blob/main/INSTALL.md) 和 [文件清单](https://github.com/bbbicycle/spacemit-LLM-wiki/blob/main/install/manifest.json)，按同一提交下载所需文件，保留已有客户端配置。两种方式都安装完整 Skill：

- **云端 `cloud`（默认）**：只安装 Skill 和远程 SSE 连接配置，不下载服务程序或索引。
- **本地 `local`**：安装 Skill、`mcp/server.py` 与 `mcp/data/wiki_graph.json`，用 Python 3.9+ 通过 stdio 运行；无需第三方 Python 包或 Sources。精炼正文在本地，官方原文仍可能联网获取。

公共 SSE 地址：`https://mcp.yao1302.xyz/sse`，不是 Streamable HTTP 端点。按客户端当前支持的远程 MCP 配置格式填写 URL，例如支持此格式的客户端可用：

```json
{
  "mcpServers": {
    "spacemit-wiki": {
      "url": "https://mcp.yao1302.xyz/sse"
    }
  }
}
```

配置格式及 SSE 支持取决于客户端版本。若客户端只支持本地 stdio，可按安装指南选择本地模式，用 Python 和脚本的绝对路径配置启动。验收需完成握手、`tools/list` 和实际查询；还应确认客户端已发现 Skill，未加载时说明刷新或新会话操作。工具参数以实际 schema 为准。

## 查询工具

| 工具 | 必需参数 | 用途 |
| :--- | :--- | :--- |
| `search_wiki` | `query` | 定位精炼文档；`domain` 可选。搜索摘要不能替代正文证据。 |
| `get_developer_journey` | `board_or_task` | 读取上手步骤。 |
| `read_knowledge_atom` | `atom_name` | 读取专题正文；当前无章节切片参数。 |
| `get_evidence_fact` | `spec_name` | 读取参数或事实表；仍需核对审核状态和适用条件。 |
| `get_graph_relations` | `node_name` | 需要时查看相关文档，不必每次调用。 |
| `search_raw_sources` | `query` | 定位官方原始文件；`submodule` 可选。 |
| `read_raw_source_file` | `file_path_or_url` | 读取已定位的原文；`start_line`、`end_line` 为可选的 1 起始行号。 |

Cloudflare 服务还可能提供 `report_wiki_issue`；这属于向维护者发送反馈，按用户授权调用，不是回答问题的必做步骤。

### 调用次序与范围

按问题直接取动线、专题或事实表，名称不明时先搜索。不要求逐层遍历。精炼证据缺失、冲突、过期或用户要求核实上游时可查询原文，不限于报错调试。

原文默认从第 1 行返回最多 200 行；只给 `start_line` 时也读取最多 200 行。显式 `end_line` 为包含在内的结束行，窗口超过 500 行时裁剪为 500 行；按返回的 `has_more` 和 `next_start_line` 续读。专题/事实工具返回正文，重复查询之前先复用会话中仍适用的内容。

### 缺少 Sources 的设备

- **远程 MCP 客户端**：不用克隆仓库或安装 Sources；精炼内容和原始目录索引由服务端提供，原文由服务端联网获取官方 GitHub 公开资源。
- **本地 stdio 服务**：需要仓库自带的 `mcp/data/wiki_graph.json`。本地 Sources 文件与索引 commit 一致且未修改时读取本地文件；否则按索引的固定 commit URL 联网获取。
- **只读文件清单**：原文请求仅支持索引收录的完整路径或 URL。已知文件的 `main` URL 会映射到索引固定 SHA，不任意读取其他 URL、路径或实时分支内容。
- **索引维护**：缺少、未初始化或有已跟踪文件修改的 Sources 时，构建失败并保留现有索引。`--if-changed` 先完成源版本和文档解析校验，仅内容或来源版本变化、索引缺失或双端不一致时才写入；无变化时保留原构建时间。
- 网络不可用、资源不可访问或仍无证据时说明限制，不补出不存在的内容。

### 结果解释

回答应给出文件/链接、适用代际和版本，保留返回中的审核状态、撤回、冲突、时效及使用范围。`needs_review` 表示待审核；既有知识结构和静态 lint 均不构成事实准确率保证。

原文返回 JSON：`source` 为索引固定 URL，`source_commit` 为对应 SHA，`origin` 表示 `local` 或 `github`；`total_lines`、`start_line`、`end_line` 说明范围，`content` 为该范围正文。`has_more` 为是否还有后续行，`next_start_line` 为续读起点，无后续时为 `null`。空文件返回空正文、`total_lines/end_line:0`；起点超过文件末尾时返回空正文和实际总行数，不再续读。节点名称有歧义时根据候选使用精确 ID。

节点结果另含 `freshness: current|stale|unknown`、`stale_paths`、`unknown_paths`、`checked_against_commit`（子模块到当前 SHA 的映射）及逐文件 `source_freshness`。新鲜度只表示已声明文件在历史版本与构建版本间是否变化；`current` 不等于事实已核验，`stale` 不改变 `verification_status`。Journey 的间接来源通过引用节点查询，无直接来源时为 `unknown`。
