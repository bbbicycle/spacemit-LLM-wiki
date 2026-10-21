# 将 SpacemiT 知识库接入 AI

本页同时供用户和代为安装的 AI 阅读。普通用户默认选择云端；需要在自己电脑运行 MCP 时选择本地。两种方式都安装完整 `spacemit-wiki` Skill，均无需克隆整个项目。

| 方式 | 安装内容 | 运行条件 |
| --- | --- | --- |
| **云端 `cloud`（推荐）** | 完整 Skill＋远程 SSE MCP 配置 | 客户端支持 Skill 和远程 SSE MCP；查询需要联网 |
| **本地 `local`** | 完整 Skill＋`mcp/server.py`＋`mcp/data/wiki_graph.json`＋本地 stdio MCP 配置 | 客户端支持 Skill 和 stdio MCP；Python 3.9+，推荐 3.11+ |

Skill 提供检索、核实和回答规则，MCP 提供知识查询工具。安装其中一个不会自动安装另一个。本地模式的精炼知识正文已包含在发布索引中；读取未安装的官方原文仍需联网，不能称为完整离线版。

Worker 是生产端，Python 本地服务是纯标准库的 7 核心工具契约镜像，不提供 D1 运营能力。知识更新通常只更新服务端或本地发布索引；MCP 连接地址与 Skill 行为规则分开配置，迁移服务时先更新连接配置。

## 复制给 AI

将下面内容发给支持本地文件操作与客户端配置的 AI 助手；需要本地模式时把 `cloud` 改为 `local`。普通网页聊天可能只能指导配置。

```text
请帮我安装 SpacemiT 知识库，接入模式：cloud（云端；需要本地运行时改成 local）。
仓库：https://github.com/bbbicycle/spacemit-LLM-wiki
请先读取 https://github.com/bbbicycle/spacemit-LLM-wiki/blob/main/INSTALL.md，按其中流程和 install/manifest.json 识别当前客户端、按需安装完整 Skill 及所选模式所需文件或配置。
保留已有客户端配置；完成后验证 Skill 是否已加载、MCP 能否实际查询，并报告结果。如缺少操作权限或客户端支持，请给出最少手动步骤。
```

## 安装流程

### 1. 确认当前客户端与模式

- 使用用户指定的 `cloud` 或 `local`；未指定时默认 `cloud`。
- 识别操作系统、AI 客户端及版本、Skill 安装目录和 MCP 配置方式。目录与格式以该客户端实际支持的方式为准，不把当前工作目录或任意新建目录当作 Skill 的可发现目录。
- 当前环境不能确定目标客户端时，只询问这一必要信息；不要求用户重复选择已经指定的模式。
- 检查 Skill 与所选 MCP transport 的支持。远程地址目前是 **SSE**，不能把 `/sse` 当作 Streamable HTTP 端点。云端客户端不支持 SSE 时，说明缺口并建议用户选择本地；不要默默安装额外桥接产品或切换模式。
- 具备相应权限时完成当前客户端的安装与配置。缺少本地操作权限、客户端需登录或需手工添加连接时，给出该客户端最少的剩余操作，不把下载完成等同于已经接入。

### 2. 固定一个版本，按清单下载

仓库地址为 `https://github.com/bbbicycle/spacemit-LLM-wiki`，默认分支为 `main`。安装文件清单是 [install/manifest.json](install/manifest.json)。

1. 先解析用户指定的版本；未指定则使用 `main` 的完整 commit SHA。可读取 `https://api.github.com/repos/bbbicycle/spacemit-LLM-wiki/commits/main` 的 `sha`，也可在已有 Git 环境中执行 `git ls-remote https://github.com/bbbicycle/spacemit-LLM-wiki.git refs/heads/main`。均不需要克隆。
2. 从 `https://raw.githubusercontent.com/bbbicycle/spacemit-LLM-wiki/<SHA>/INSTALL.md` 与同一 SHA 的 `install/manifest.json` 读取对应版本的说明和清单。`<SHA>` 必须替换为实际解析出的完整提交号。
3. 检查 `schema_version`、所选模式及相对文件路径。所有下载均使用同一个 SHA，避免安装途中分支更新造成文件混用。
4. 对 `skill.files` 的每个相对路径，从 `<SHA>/<skill.source_dir>/<文件路径>` 获取文件，保留其在 `spacemit-wiki/` 内的目录结构。先在临时目录下载完整并核对文件，再安装到客户端识别的 Skill 目录。
5. 只有 `local` 才下载 `modes.local.runtime_files`，保留清单中的路径结构；`cloud` 不下载任何本地 MCP 运行文件。

使用现有的下载或文件工具即可，云端用户不需要为了下载而安装 Git、Python、Node.js 或 Obsidian。下载文件内容应来自 raw 地址，不把 GitHub 网页 HTML 保存成 `SKILL.md` 或脚本。

安装范围不包含 `Sources/`、子模块、Worker、整库 Markdown 或维护脚本。不要全量 clone、递归初始化子模块或运行 `build_mcp_index.py`。完整 Skill v1 仅含清单中的 `SKILL.md`、`README.md` 和 `mcp.md`，不能只复制入口文件；旧安装的 `rules/`、`evals/` 已退出新版清单，不再作为查询规则加载。

已有同名 Skill 或本地 MCP 时，先识别当前安装与用户修改，保留备份和非本安装管理的文件；存在冲突时向用户说明具体冲突。已安装且验证可用时复用，不为重复安装而改动配置。后续更新本地版时，Skill、服务脚本和发布索引仍取自同一提交，不在用户设备重新构建索引。

### 3. 配置所选模式

只修改用户选定的客户端与作用域，合并现有 MCP 配置，保留其他服务、Skill 和用户设置。通过客户端支持的设置界面、配置文件或命令操作；不假定所有客户端使用同一文件格式。

**云端 `cloud`**

配置一个名为 `spacemit-wiki` 的远程 SSE MCP 连接，URL 为清单中的 `modes.cloud.url`：

```text
名称：spacemit-wiki
传输方式：SSE
地址：https://mcp.yao1302.xyz/sse
```

云端客户端只安装 Skill、保存远程连接配置。服务程序与知识索引由远端运行，不在用户电脑部署 Worker。云端查询使用已部署的数据版本，与本次下载 Skill 的 GitHub 提交不必相同；需要核实版本时保留工具返回的来源和 commit 信息。

**本地 `local`**

确认 Python 版本；`mcp/server.py` 只依赖标准库，无需 `pip install`。保持以下运行目录：

```text
<运行目录>/
└── mcp/
    ├── server.py
    └── data/
        └── wiki_graph.json
```

配置一个名为 `spacemit-wiki` 的 stdio MCP 连接：用已确认可运行的 Python **绝对路径**作为命令，以 `server.py` 的**绝对路径**作为参数。下列是使用 `mcpServers` 格式的客户端配置示意，路径需按当前电脑替换；其他客户端需转换为其实际格式：

```json
{
  "mcpServers": {
    "spacemit-wiki": {
      "command": "/absolute/path/to/python3",
      "args": ["/absolute/path/to/runtime/mcp/server.py"]
    }
  }
}
```

不依赖当前工作目录。不要把 Python 命令和脚本路径拼成一条带空格的 `command` 字符串。客户端会启动服务，无需让用户另开一个长期运行的终端。

### 4. 验证接入

分别核对以下结果，尚未验证的项目明确保留为待完成：

1. **Skill 文件完整**：清单内文件均已安装，相对引用可用，位于该客户端识别的目录。
2. **MCP 实际可用**：通过真实 MCP 连接完成 `initialize`、`notifications/initialized` 与 `tools/list`，确认返回清单中的 7 个核心工具；云端有额外反馈工具也正常。不能只以 URL 返回 HTTP 200 判断成功。
3. **查询可用**：执行 `search_wiki({"query":"Muse Pi"})`，再执行 `get_evidence_fact({"spec_name":"muse_pi_vs_pi_pro_specs"})`，确认返回搜索结果和非空正文；保留正文中的审核状态，不因测试成功就宣称技术事实已审核。这两次调用不要求下载官方原文。
4. **客户端已加载**：核对当前客户端是否发现 Skill 和 MCP。需要重启、刷新或新会话时，明确操作；独立启动本地服务测试通过不代表当前客户端已加载。

最后报告所选模式、下载的 commit SHA、Skill 安装位置、MCP 配置位置、查询验证结果及剩余操作。不自动开启后台更新或向维护者发送反馈。

## 维护者检查

新增或删除 Skill 配套文件时，同步更新安装清单。无需将清单中的运行时文件改成全项目目录，也无需因日常知识索引更新而重写清单。最小安装检查会在不初始化 Sources 的独立目录中验证两种模式：

```bash
python3 -B scripts/test_minimal_install.py
```

仓库维护、Sources 同步和云端部署见 [维护规范](docs/MAINTENANCE.md)，不是用户安装步骤。

按 [项目计划 v2.0](docs/PROJECT_PLAN.md)，阶段 A 已将 Skill v1 精简为 3 个文件，新增服务端 `build_meta`、`/health`、`agent_notice` 与搜索 `hint`。健康接口用于核对线上索引、哈希和部署版本，`d1_bound` 仅表示绑定存在；安装验收仍须完成真实 MCP 握手与查询，不能仅以健康响应代替。
