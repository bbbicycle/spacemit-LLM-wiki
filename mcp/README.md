# Spacemit LLM Wiki - 双层知识图谱 MCP Server (v2.1 index)

本项目提供了专为 **Spacemit 芯片与产品知识库** 定制的 MCP Server。
严格遵循 `Agent.md` 规范与 Anthropic MCP 协议，构建了 **“精炼知识图谱 + 原始资料源（Sources/）动态穿透”** 的双层知识服务架构。

**用户安装请先读 [INSTALL.md](../INSTALL.md)**：云端版安装完整 Skill＋远程 SSE 配置；本地版安装完整 Skill＋本目录的服务脚本和发布索引。两种方式均无需全量克隆项目。下方 Cloudflare 部署步骤面向服务维护者。

---

## 🛠️ 包含的 7 大 MCP Tools

| 层级 | 工具名称 | 功能说明 | 数据来源 |
| :--- | :--- | :--- | :--- |
| **精炼知识层** | **`search_wiki`** | 按关键词、别名、技术领域快速定位精炼节点 | 内存索引 |
| **精炼知识层** | **`get_developer_journey`** | 整篇获取板卡操作动线与双链（线） | 内存原子 |
| **精炼知识层** | **`read_knowledge_atom`** | 整篇无损获取驱动/外设/硬件设计专题档案（面） | 内存原子 |
| **精炼事实层** | **`get_evidence_fact`** | 直出结构化引脚复用表、Strap 配置、电气参数（点） | 内存原子 |
| **图谱拓扑层** | **`get_graph_relations`** | 顺着双链探索芯片与板卡的依赖出链和被引用入链 | 拓扑图谱 |
| **原始资料层** | **`search_raw_sources`** | 在已发布的原始芯片与产品手册清单中检索文件与章节 | 原始清单 |
| **原始资料层** | **`read_raw_source_file`** | 按需按索引 commit 拉取 GitHub 官方仓库的原始 Markdown/源码 | GitHub 动态拉取 |

---

## 🚀 部署到 Cloudflare Workers（仅需 3 步，完全免费）

### 准备条件
- 安装了 Node.js（v24+，运行 Worker 回归测试需要）
- 拥有一个免费的 [Cloudflare 账号](https://dash.cloudflare.com/)（无需信用卡）

### 步骤 1：生成/更新最新索引
在项目根目录运行：
```bash
python3 scripts/build_mcp_index.py
```
构建需完整初始化五个 Sources 子模块；2026-10-19 合并快照为 66 个精炼节点、1231 个原始文件。索引同时写入 Python 和 Worker，记录真实构建时间、内容哈希与源 commit。缺少或存在未提交改动的 Sources 时构建失败，已有索引保留。

```bash
git submodule update --init --recursive
python3 scripts/build_mcp_index.py
python3 scripts/build_mcp_index.py --check
```

### 步骤 2：登录并部署 Worker
```bash
cd mcp-worker
npm ci

# 1. 登录 Cloudflare（首次运行会在浏览器弹窗一键授权）
npx wrangler login

# 2. 一键发布上线
npx wrangler deploy
```

部署成功后，终端会打印出你的专属公开 URL，例如：
`https://spacemit-wiki-mcp.<你的子域名>.workers.dev/sse`

---

## 💻 外部开发者如何接入与使用？

按 [统一安装流程](../INSTALL.md) 与 [安装清单](../install/manifest.json) 选择一种方式，同时安装完整 Skill：

- **云端 `cloud`（推荐）**：配置 `https://mcp.yao1302.xyz/sse` 远程 SSE MCP；本地不安装服务程序、索引或 Python。
- **本地 `local`**：用 Python 3.9+ 运行 `mcp/server.py`，保留相邻的 `data/wiki_graph.json`；配置 stdio MCP，不需要部署 Worker。

客户端的 Skill 支持、SSE/stdio 支持及配置格式以其当前版本为准。安装后需验证真实 MCP 查询及客户端 Skill 加载，不把文件下载或 HTTP 200 当作接入成功。

## 维护者测试

最小安装测试不需要 Sources，其他回归按对应维护流程执行：

```bash
python3 -B scripts/test_minimal_install.py
python3 -B -m unittest discover -s mcp -p 'test_server.py'
python3 -B scripts/test_build_mcp_index.py
node --disable-warning=ExperimentalWarning mcp-worker/test_runtime.cjs
```


## 无 Sources 的消费模式与来源

云端客户端不需要下载 Sources。运行本地 Python MCP 需 Python 3.9+，运行文件仅 `mcp/server.py` 与同一提交发布的 `mcp/data/wiki_graph.json`；服务只依赖标准库：

```bash
python3 mcp/server.py
```

精炼正文内置在索引中。读取原文时只接受索引返回的完整路径或 raw URL；Python 优先使用匹配源 commit 且未修改的本地文件，否则回退 GitHub。中文和空格路径经过 URL 编码，回退固定源 commit，避免 `main` 漂移。响应包含 `source / source_commit / origin / total_lines / start_line / end_line / content`。网络不可用则明确返回错误。

`start_line / end_line` 为正整数，建议每次约 100～200 行。省略范围仍返回全文，本轮没有加入服务端硬预算。核验信息随节点返回：`status / verification_status / external_use / source_file / source_commit / source_section / verified_at / conflicts` 等；未核验条目不能当作对外性能保证。

公共索引过滤内部 tier 2/3、NDA、`publication:false` 或内部 visibility；`external_use:false` 的公开上游技术条目可用于定位待核验问题，不能作为已核准的对外结论。

## 同步与部署闭环

本地 `./update_sources.sh` 完成子模块更新后重建双端索引并跑检查。CI 的同步工作流将更新和索引一起提交，然后直接调用可复用的部署工作流，传入精确 commit；不依赖 `GITHUB_TOKEN` 推送触发第二个工作流。部署必须先通过生产 Python/Worker 回归测试、索引校验、链接/文本规则和 TypeScript 检查。

当前维护规范见 [MAINTENANCE.md](../docs/MAINTENANCE.md)。仅连接现有云端地址会使用已部署版本，本地修复需发布后才生效。
