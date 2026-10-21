# MCP 接入与参数参考

仅在安装、修复连接或确认参数时读取。Skill 提供检索规则，MCP 提供数据；安装其中一个不会自动安装另一个。

## 接入

按 [安装指南](https://github.com/bbbicycle/spacemit-LLM-wiki/blob/main/INSTALL.md) 和 [文件清单](https://github.com/bbbicycle/spacemit-LLM-wiki/blob/main/install/manifest.json) 选择模式、固定一个提交下载完整 Skill，合并已有配置。连接地址从清单获取，不写入行为规则。

- 云端（默认）：完整 Skill + 远程 SSE 连接，客户端需支持 SSE；不能将 SSE 地址当作 Streamable HTTP。
- 本地：完整 Skill + 清单所列 Python 服务和索引，使用 stdio，Python 3.9+ 且无需第三方包。精炼正文可离线查询，官方原文仍可能联网获取。

配置格式以客户端实际版本为准；验证 Skill 发现、MCP 握手、`tools/list` 与实际查询，需要刷新/新会话时明确说明。维护与重建不属于用户安装步骤。

## 核心工具

| 工具 | 必填参数 | 可选参数 |
| --- | --- | --- |
| `search_wiki` | `query` | `domain` |
| `get_developer_journey` | `board_or_task` | — |
| `read_knowledge_atom` | `atom_name` | — |
| `get_evidence_fact` | `spec_name` | — |
| `get_graph_relations` | `node_name` | — |
| `search_raw_sources` | `query` | `submodule` |
| `read_raw_source_file` | `file_path_or_url` | `start_line`、`end_line` |

参数及枚举以实际工具 schema 为准。原文仅接受服务索引中的路径或 URL；默认 200 行、显式窗口最多 500 行，末页 `has_more:false / next_start_line:null`。返回 `source / source_commit` 是固定版本，`origin` 区分本地与远程读取，不能据此声称实时上游。

Worker 可另提供 `report_wiki_issue`，仅经用户授权调用；参数为 `topic`、`description` 和可选 `issue_type`。Python 仅有核心检索工具，缺少反馈工具不影响问答。

节点详情的 `agent_notice` 是 `{code, message, source_paths?}` 数组；搜索 `hint` 概括状态，具体结论仍需正文。保留新鲜度、核验、人工审核、访问及对外使用范围的独立含义，不能互相替代。
