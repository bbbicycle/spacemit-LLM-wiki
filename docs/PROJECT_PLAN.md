# SpacemiT LLM Wiki 架构演进与近期执行计划

> 版本：v2.0
> 日期：2026-10-21
> 适用仓库：`spacemit-LLM-wiki`

## 1. 核心架构定调：Skill 与 MCP 应该以什么形式存在？

在完成现有基础建设与 P0/P1 后，本项目最核心的收敛原则是：**拒绝过早为假想需求造繁重基建，把全部精力集中在“数据准确性、服务自解释性、真实查询驱动闭环”上**。

### 1.1 MCP 与 Skill 的目标形态（职责彻底解耦）

> **核心公式：MCP 是“自带元数据的自解释数据服务（重服务端）”，Skill 是“极简、长期不动的检索行为契约（轻客户端）”。**

| 维度 | MCP 服务端 (`mcp-worker` / `mcp`) | 对外用户版 Skill (`skill/spacemit-wiki`) | 对内维护规范 (`Agent.md` + `docs/MAINTENANCE.md`) |
| :--- | :--- | :--- | :--- |
| **面向受众** | 所有接入知识库的 AI 客户端（Claude / Cursor / Gemini 等） | 终端开发者、FAE、商务与内部问答用户 | 仓库维护者及打开本仓库执行维护任务的编码 Agent |
| **承载内容** | 精炼节点 + 官方原文索引 + 新鲜度/核验状态；阶段 A 增加内联提示 | **仅保留 4 件事**：触发范围、三级检索漏斗、代际隔离与诚实回答纪律、只读边界 | `source_commit` 维护规则、Lint 检查项、`stale` 复核 SOP、Git 提交流程 |
| **更新频率** | Sources 与索引按现有 CI 自动同步；知识正文经维护者审阅后更新 | **极低频**，目标是不随知识内容更新而重装；协议或行为契约升级另行版本化 | 随仓库工程流演进按需调整 |
| **部署形态** | **云端 SSE 为主力**（`https://mcp.yao1302.xyz/sse`，未来平滑切至公司服务器）；本地 Python stdio 作精炼知识离线查询与 CI 契约校验兜底，原文可能需联网 | 按 `install/manifest.json` 下发到客户端识别的 Skill 目录 | 仅存在于 Git 仓库内，不下发给普通问答用户 |

#### 为什么要这样设计？
1. **让 MCP 返回结果“自解释”（Self-Describing Response）**：
   - 永远不要假设客户端一定安装了最新版本的 Skill，甚至不要假设客户端一定加载了 Skill。
   - 当 MCP 返回任何一个节点时，服务端应在返回结构中直接内联状态说明与行动指引（例如当 `freshness: "stale"` 时直接提示用 `read_raw_source_file` 核对索引固定版本原文；当 `status: "needs_review"` 时直接提醒标注待复核；当涉及 K1/K3 硬件参数时附带代际边界提醒）。即使客户端只连了 MCP 而没装 Skill，大模型看到 MCP 返回文本也能直接做出正确行为。
2. **让对外 Skill 彻底瘦身并冻结**：
   - 把具体硬件参数、易变产品清单、仓库文件路径和维护命令全部从对外 Skill 中剔除。Wiki 从 66 个节点涨到 300 个节点，或者后台从 Cloudflare 迁移到公司服务器，用户手里的 Skill **无需因知识或承载环境变化而修改行为规则**；服务地址在 MCP 配置中切换。

### 1.2 三条不可动摇的架构红线
1. **知识读写路径分离**：用户查询不改写知识库、用户文件或触发 Git 提交推送；知识修改由维护者经双重 Lint 与 diff 审阅后按授权发布。Worker 可异步记录查询日志；`report_wiki_issue` 是向维护者发送反馈的独立写操作，仅在用户明确授权时调用。
2. **精确事实层（Wiki）与非结构化检索层（未来公司 RAG）边界隔离**：芯片引脚、Strap 管脚、PMIC 电压容错率为零，绝不与普通文档混成无来源边界的统一向量库。
3. **以 Git 与单文件索引作为天然版本底座**：编译产物 `wiki_graph.json` 天然受 Git 版本控制，在公司服务器正式接手前，不脱离 Git 额外发明复杂的 `wiki-release/<version>/` 发布包目录体系。

## 2. 当前基线与阶段总览

### 2.1 当前已完成基线（截至 P1 收口）
- **知识规模**：66 个精炼节点（7 篇 `Developer_Journeys`、32 篇 `Knowledge_Atoms`、27 篇 `Evidence`）+ 5 大官方子模块共 1,231 篇 `Sources/` 原始资料索引。
- **P1 新鲜度与自愈闭环（已完成）**：
  - 全部 27 篇 Evidence 与 32 篇 Knowledge Atom 均已补齐 `source_file`、`source_commit`、`source_resolution`、`verification_status` 与 `source_checked_at`。
  - 索引 `v2.2.0` 支持按文件路径精确计算 `freshness`（当前基线：**47 个 `current`、12 个 `stale`、7 个无直接来源的 Journey 为 `unknown`**）。
  - `scripts/check_upstream_impact.py` 已支持持久基线 `docs/source_baseline.json` 及双链传递影响分析。
  - 本地 `mcp/server.py` 与云端 `mcp-worker/src/index.ts` 已对齐原文 200 行默认分页（最大窗口 500 行），且 Worker 已通过 `ctx.waitUntil` 实现 D1 查询日志与问题反馈的异步非阻塞写入。

P0 已完成的是接口与目标元数据模型定义，不表示未来 Gateway 字段已全量实现。P1 索引 v2.2.0 已有顶层构建字段；阶段 A 将索引升级为 v2.3.0，已实现确定性 `build_meta`、Worker `/health`、双端 `agent_notice` / 搜索 `hint` 及轻量 Skill v1。Worker 保留 `/stats` 和授权反馈 `report_wiki_issue`；线上状态以 `/health` 与部署 smoke 为准。

上述数量是当前仓库索引快照，不代表线上已部署版本或全库事实已经人工审核。P0 契约与 RACI 见 [MCP 接口契约](MCP_CONTRACT_V1.md)，P1 操作见 [新鲜度与维护闭环](FRESHNESS_MAINTENANCE.md)，历史记录见 [log.md](../log.md)。

### 2.2 演进路线图总览

| 阶段 | 名称 | 核心目标 | 当前状态 |
| :--- | :--- | :--- | :--- |
| **P0** | 冻结目标与接口 | 明确三层拓扑、7 大核心 MCP 工具与来源元数据模型 | **DONE** |
| **P1** | Wiki 新鲜度与自愈闭环 | 按文件路径检测 `stale`、固化上游影响基线与原文安全分页 | **DONE** |
| **阶段 A（原第二步）** | **MCP 自解释改造与对外 Skill 瘦身** | 用“索引内嵌 `build_meta` + `/health` 自检 + 结果内联提示 + 极简 Skill 冻结”替代繁重的 P2 打包基建 | **实现完成，部署验收中** |
| **阶段 B（原第三步）** | **存量来源复核与查询驱动迭代** | 逐项复核首轮 12 个 `stale`、为 7 个 Journey 补来源，目标有据清零；利用 Cloudflare D1 真实查询日志驱动专题扩充与评测 | **当前待执行（日常核心闭环）** |
| **P4** | 公司服务器承载 Wiki MCP | 在公司内部服务器运行独立 Wiki MCP 服务（灰度替代 Cloudflare） | 待公司服务器就绪后启动 |
| **P5** | 接入公司 RAG 与混合编排 | 在服务端通过 MCP Gateway 编排 Wiki 精确检索与公司 RAG（含 ACL 权限过滤） | 待公司 RAG 接口就绪后启动 |

## 3. 阶段 A（原第二步详细计划）：MCP 自解释改造、轻量版本溯源与对外 Skill 瘦身

> **核心目标**：以 1~2 天为初步工作量估计，完成版本可追溯、服务可自检、返回结果自解释与客户端 Skill 稳定化；不另建脱离 Git 的打包体系。以验收结果收口，不能用时间估计代替验证。

### A1. 索引顶层内嵌构建元信息（`build_meta`）与 `/health` 自检接口

不再单独维护 `wiki-release/<version>/manifest.json` 目录树，而是直接让 `wiki_graph.json` 成为自包含的版本化产物。

#### 1. 修改 `scripts/build_mcp_index.py`

两份索引继续保持字节一致；新增 `build_meta` 作为现有元数据的聚合视图，不另建 manifest。结构如下（统计由构建器计算）：

```json
{
  "version": "2.3.0",
  "build_meta": {
    "wiki_commit": "<索引输入/构建来源提交 SHA>",
    "sources_commits": {
      "docs-chip": "<SHA>",
      "docs-buildroot": "<SHA>",
      "docs-product": "<SHA>",
      "docs-ai": "<SHA>",
      "docs-ros": "<SHA>"
    },
    "content_sha256": "<内容哈希>",
    "counts": {
      "total_nodes": 66,
      "developer_journeys": 7,
      "knowledge_atoms": 32,
      "evidence": 27,
      "raw_sources": 1231
    },
    "freshness_summary": { "current": 47, "stale": 12, "unknown": 7 }
  }
}
```

确定性与兼容要求：

- 保留现有顶层字段及其兼容语义，新增聚合字段必须与其一致；记录五个 Sources 的完整固定 SHA 与内容哈希。
- `wiki_commit` 表示构建输入来源，不能要求等于“包含此索引的提交自身”。索引提交会改变 HEAD，不能因此每次重建又产生一次无意义 diff。按知识三层目录、Sources 和构建器的路径历史取最近一次输入提交；因此只提交索引或工程文档不会改变来源，清理输出后重建也可复现。同时记录实际部署 ref 于日志和 `/health.deployment_ref`，区分构建来源和部署版本。
- 入库索引不再使用每次变化的系统时间；兼容保留的 `generated_at` 使用固定构建来源提交时间，真实运行时间写 CI 日志。`wiki_worktree_dirty` 仅反映构建输入；正式发布先提交输入再重建索引，避免带未提交来源发布。
- `--if-changed` 的无变更保持策略与 `--check` 的只校验语义继续保留。验收还须实际重复构建比较文件字节，覆盖输入不变、仅提交索引、仅改工程文档及输入真正变化的场景，不能只运行 `--check` 证明确定性。

#### 2. 在 `mcp-worker/src/index.ts` 增加 `GET /health` 端点

正常加载并校验索引后返回 HTTP 200 与 JSON：

```json
{
  "status": "ok",
  "service": "spacemit-wiki-mcp",
  "version": "2.3.0",
  "build_meta": { "...": "已加载索引的构建元数据" },
  "d1_bound": true
}
```

- `/health` 暴露线上已加载索引的来源版本、内容哈希和 freshness 统计，不读取维护者本地 checkout。
- `d1_bound` **只表示存在绑定**，不证明表已初始化、查询或异步写入成功。D1 运营可用性另用实际查询/反馈核查，不以绑定标志代替；索引不可用不得仍返回 `ok`。
- 通过现有部署工作流手动 `ref` 入参或复用调用部署指定 Git ref；回退时重新部署目标 ref 对应的服务代码与索引（重建时使用其固定的五个 Sources 指针），再核对版本、哈希及工具 smoke test。Git revert 或本地 checkout 本身不会切换线上 Worker。

### A2. MCP 工具返回结果“自解释化”（Self-Describing Notices）

为了降低对客户端 Skill 的依赖，在 `mcp/server.py` 和 `mcp-worker/src/index.ts` 中编写统一的节点响应增强逻辑（`build_agent_notice(node)` / `buildAgentNotice(node)`）。

#### 1. 适用工具范围
- `get_developer_journey`
- `read_knowledge_atom`
- `get_evidence_fact`
- `search_wiki`（在摘要结果中保留 `freshness`、`verification_status`、`status` 与简短 `hint`）

#### 2. 自动生成内联 `agent_notice` 的规则
当上述工具返回节点详情时，除了返回现有的元数据头和 Markdown 正文外，根据节点状态自动拼接结构化的 `agent_notice` 提示块：

- **规则 1：上游变更预警（当 `node.freshness === "stale"` 时）**
  ```text
  [新鲜度预警 / STALE] 本节点依赖的上游源文件（<stale_paths>）在来源历史版本与本次索引固定快照之间发生变化。涉及寄存器、引脚、命令或电气参数时，请用 `read_raw_source_file` 核对索引固定版本原文，并说明节点待复核；若需尚未收录的最新上游，应由维护者同步核查。
  ```
- **规则 2：待复核状态提示（当 `node.verification_status !== "verified"` 或 `node.status === "needs_review"` 时）**
  ```text
  [核验状态提示] 本节点当前核验状态为 `<verification_status>`（文档状态：`<status>`）。向用户输出结论时请附带具体来源路径，并注明“待人工终审/需结合对应硬件版本核对”，勿表述为无条件审定结论。
  ```
- **规则 3：冲突状态强警告（当 `node.verification_status === "conflicted"` 时）**
  ```text
  [来源冲突警告 / CONFLICTED] 本节点记录的官方资料之间存在参数或表述冲突，请仔细阅读正文中的冲突说明并同时向用户列出不同来源的原始依据，严禁单方面掩盖冲突。
  ```
- **规则 4：硬件与芯片代际隔离提示（当 `node.domain` 属于芯片规格、硬件设计或 AI 算力时）**
  ```text
  [代际边界] 参数严格绑定来源注明的芯片代际、具体板型与硬件版本；接线前核对引脚、供电与电平，严禁跨产品套用。具体参数以当前节点证据为准。
  ```

对于 `freshness: unknown`，说明覆盖缺口或无法判断原因；`current` 仅说明声明文件在固定快照下无差异，不消除待核验、撤回或冲突提示。多种状态可同时成立，不能互相覆盖。

#### 3. 跨端一致性要求
- `mcp/server.py` 与 `mcp-worker/src/index.ts` 使用完全一致的字段名与判断逻辑。
- 在 Python 与 Worker 回归中覆盖 `stale`、`unknown`、`current + needs_review`、`unverified`、`conflicted` 及硬件边界场景；检查提示与原有正文/元数据兼容，并比较两端输出。

### A3. 对外 `skill/spacemit-wiki` 彻底瘦身与冻结（Skill v1 Freeze）

对 `skill/spacemit-wiki/` 目录下的所有文件进行一次全面盘点与“脱水”，将其冻结为**长期稳定的客户端行为契约**。

#### 1. 盘点并清理现有 Skill 内容
- **必须删除/移走的内容**（移入仓库内部 `docs/MAINTENANCE.md` 或直接删除）：
  - 任何维护者专用命令（如 `vault_linker_lint.py`、`build_mcp_index.py`、`check_upstream_impact.py`、`update_sources.sh`）。
  - 任何易随时间变化的统计数字（如“当前有 66 个节点、1,231 篇原文、12 个 stale”）。
  - 任何写死在 Skill 里的具体硬件参数长表（具体参数一律通过调用 MCP 获取，避免 Skill 与 MCP 数据双轨不一致）。
- **对外 `skill/spacemit-wiki/SKILL.md` 仅保留以下 4 个核心模块（控制在 80 行以内）**：
  1. **适用范围与触发红线**：凡涉及进迭时空（SpacemiT）、K1/K3 芯片、MUSE 系列开发板/终端、V100 服务器、Bianbu OS、Buildroot BSP、SpaceAI、ROS 2 的问题，必须优先调用 `spacemit-wiki` MCP 工具，严禁依赖模型预训练记忆猜测。
  2. **三级按需检索漏斗**：
     - **先定边界**：确认用户所问的芯片代际（K1 / K3 / V100）与具体板型；不明确时先追问或调 `search_wiki`。
     - **直达精炼层**：要操作步骤调 `get_developer_journey`；要模块机理/板级设计调 `read_knowledge_atom`；要引脚表/Strap/电气参数调 `get_evidence_fact`；探查上下游关联调 `get_graph_relations`。
     - **原文兜底与分页**：当精炼层未命中、节点提示 `stale` 或用户要求核对官方原文时，调用 `search_raw_sources` 与 `read_raw_source_file`（默认 200 行分页，按 `has_more` / `next_start_line` 续读）。
  3. **回答与证据纪律**：
     - 检查 MCP 返回的状态与适用条件；支持 `agent_notice` 时遵循其提示，旧服务未返回该可选字段时仍须按元数据核实。
     - 给出明确的来源文件路径或节点名称。
     - 发现断链、参数冲突或明显缺失时先说明缺口；仅经用户明确授权才调用 `report_wiki_issue`（Worker 支持）反馈，绝不自行编造或自动上报。
  4. **只读安全边界**：问答会话中绝不自动修改用户本地文件、不执行仓库同步或 Git 提交。

#### 2. 校验安装清单与最小安装测试
- 核对 `install/manifest.json` 中的 `skill.files` 列表是否与精简后的 `skill/spacemit-wiki/` 完全匹配。
- 运行 `python3 -B scripts/test_minimal_install.py`，确保云端模式与本地模式在无 `Sources/` 的独立临时目录中均能一键通过校验。

### A4. 双端 MCP 维护策略收敛

为了避免每次改动都在 Python 和 TypeScript 两端耗费双倍精力，明确以下工程纪律：
1. **云端 Worker（`mcp-worker/src/index.ts`）为主力生产端**：D1 日志、`/stats` 与 `report_wiki_issue` 已在 Worker 端维护；新增 `/health` 也只在 Worker 端维护，不要求 Python 复制运营能力。
2. **本地 Python（`mcp/server.py`）为纯标准库契约镜像**：维护 7 个核心检索工具的 stdio 协议支持，并在阶段 A 对齐 `agent_notice` 输出，不引入任何第三方 pip 依赖，作为精炼查询离线兜底与 CI 快速回归工具。原文读取仍需固定版本本地 Sources 或 GitHub，不能宣称无 Sources 时完整离线。

### 阶段 A 验收清单（完成后逐项打勾）
- [x] 两份索引新增一致的 `build_meta`，兼容顶层字段；重复构建字节一致、提交索引后不反复改写，`--check` 通过。
- [x] `mcp-worker/src/index.ts` 已支持 `GET /health` 并返回已加载索引的 `build_meta` 与 `d1_bound`，明确绑定不等于 D1 可用。
- [x] `mcp/server.py` 与 `mcp-worker/src/index.ts` 在返回节点时均已内联 `agent_notice`（覆盖 `stale`、`unverified/needs_review`、`conflicted` 与代际隔离提醒）。
- [x] `skill/spacemit-wiki/` 已清理全部维护指令与易变硬编码事实，冻结为稳定版。
- [ ] 双 lint、构建器、最小安装、Python/Worker 运行与跨端一致性回归及类型检查通过；部署后完成版本核对、核心搜索/事实读取及原文分页 smoke test，验证按 Git ref 重新部署的回退步骤。

## 4. 阶段 B（原第三步详细计划）：存量来源复核与查询驱动的内容迭代

> **核心目标**：把 P1 建好的工具链真正跑成一个省心的日常习惯——优先逐一处理当前 12 个 `stale` 节点，目标是在有证据的复核后清零（耗时取决于来源变更，不以期限换取批量刷新 SHA），再依靠 Cloudflare D1 收集到的真实查询数据（而非盲目全量编译）驱动知识库高价值扩充。

### B1. 首轮 P1 维护闭环实战：逐一复核当前 12 个 `stale` 节点

按“先硬件安全/原子参数（Evidence），后系统专题（Knowledge Atom）”的优先级，分批消化当前 12 个 `stale` 节点。

#### 步骤 1：导出当前 `stale` 待办队列与具体变更路径
在仓库根目录运行以下命令，生成清晰的复核清单：
```bash
python3 scripts/build_mcp_index.py --if-changed --freshness-report reports/freshness.json
python3 - <<'PY'
import json
report = json.load(open("reports/freshness.json", encoding="utf-8"))
print("=== Summary ===", report["summary"])
for n in report["nodes"]:
    if n["freshness"] == "stale":
        print(f"\n[{n['type']}] {n['id']}")
        for s in n.get("source_freshness", []):
            if s.get("freshness") == "stale":
                print(f"  - path: {s['source_file']}")
                print(f"    old_commit: {s['source_commit']} -> current_commit: {s['checked_against_commit']} ({s['reason']})")
PY
```

#### 步骤 2：逐条比对上游 Git Diff（区分“实质变更”与“文字微调”）
针对每个 `stale` 来源路径，在对应的 `Sources/<submodule>` 子模块中直接查看从旧 SHA 到当前 HEAD 的精确 diff：
```bash
# 示例：查看某个源文件在两个 commit 之间的真实改动
git -C Sources/docs-chip diff <old_commit>..HEAD -- <submodule_relative_path>
```
根据 diff 内容分为三种情况处理：
1. **情况 A：仅排版、标点、图片路径或无关章节微调，核心参数无变化**
   - 正文无需改动。
   - 仅将该节点 frontmatter 中对应来源的 `source_commit`（或 `source_related_commit` 对应下标项）更新为当前子模块 HEAD SHA，并更新实际检查日期 `source_checked_at`、`updated`，置 `status: needs_review`，记录核查范围。不能把定位或格式检查升级为全文事实核验。
2. **情况 B：上游修正了引脚定义、Strap 配置、电压参数、算力指标或编译命令**
   - 定向阅读上游该章节最新上下文，同步修改 `Evidence/` 或 `Knowledge_Atoms/` 正文表格与注意事项。
   - 若上游更正了历史错误，可在正文中简要保留勘误提示（避免用户被旧版手册误导）。
   - 更新对应来源的 `source_commit`、`source_checked_at` 与 `updated`；保持 `status: needs_review`。
   - 检查是否有上游 `Knowledge_Atoms` 或 `Developer_Journeys` 引用了该节点（可通过 `get_graph_relations` 或索引入链定位；`check_upstream_impact.py --cached` 可辅助查看基线之后的变化，但不替代旧 `source_commit` 到当前快照的 diff），如有连锁表述不一致一并修正。
3. **情况 C：上游源文件被删除、拆分或重命名迁移**
   - 在子模块中使用 `git -C Sources/<submodule> log --stat -n 5 -- <old_path>` 定位迁移后的新文件路径。
   - 确认新文件的产品、版本、章节与语义确实对应后，再更新路径及其 SHA，保留迁移记录；不能仅按文件名相似替换。若官方撤回且无替代来源，保留历史来源、撤回/冲突警告和待办，不为清零伪造可用来源。

#### 步骤 3：重建索引与校验（审阅每项复核证据）
每完成一批复核（建议每 4~6 个节点一批），执行标准校验闭环：
```bash
python3 vault_linker_lint.py
python3 scripts/lint_wiki_integrity.py
python3 scripts/build_mcp_index.py --if-changed --freshness-report reports/freshness.json
python3 scripts/build_mcp_index.py --check
```
按 [新鲜度维护流程](FRESHNESS_MAINTENANCE.md) 完成对应回归与 diff 审阅。目标是 `stale` 从 12 降为 0；无法解决的项须逐条记录原因、负责人/后续动作，保留真实状态。存在阻塞时该验收项保持未完成，不把“计数清零”当作事实已审核。

### B2. 为 7 篇 `Developer_Journeys` 补齐核心来源锚点

目前 7 篇上手向导在 `reports/freshness.json` 中显示为 `freshness: unknown`，因为它们只通过双链指向 `Knowledge_Atoms` / `Evidence`，自身 frontmatter 未填写 `source_file`。

#### 具体改造动作
为以下 7 篇向导优先绑定 1~2 个最核心的官方快速上手原文，并检查未覆盖的关键步骤是否还需补充来源（填入 `source_file`、`source_commit`、`source_section`、`source_resolution`、`verification_status`、`source_checked_at`）：
1. `Developer_Journeys/K1芯片开发快速上手向导.md`
2. `Developer_Journeys/K3芯片开发快速上手向导.md`
3. `Developer_Journeys/K3_Pico_开发板快速上手向导.md`
4. `Developer_Journeys/Muse_Pi_开发板快速上手向导.md`
5. `Developer_Journeys/Buildroot_SDK_快速编译与镜像生成向导.md`
6. `Developer_Journeys/SpaceAI_模型量化与端侧推理快速上手向导.md`
7. `Developer_Journeys/ROS2_机器人与具身智能快速上手向导.md`

- **收益与局限**：已声明的官方文件发生变化且同步重建后，对应 Journey 可进入 `stale` 队列。目标是 66 个节点均有可追溯的直接来源、在可判定时 `unknown: 0`；仅锚定 1~2 个文件不等于全文每个步骤均受监控，更不等于全库事实正确。来源只能覆盖部分步骤时保留 `partial / unverified / needs_review`，不能为消除 `unknown` 填入无关文件。

### B3. 基于 Cloudflare D1 真实查询日志的“按需扩展”工作流

不把 1,231 篇 `Sources/` 原文盲目编译成精炼节点，而是依靠 `mcp-worker` 已落地的 D1 数据库（`mcp_query_logs` 与 `mcp_issue_reports`）建立**每周 30 分钟的查询驱动迭代习惯**。

#### 1. 定期审阅 `/stats` 看板或 D1 聚合指标
重点关注以下三张清单：

| 观察指标 | SQL / 看板特征 | 对应的知识库维护动作 |
| :--- | :--- | :--- |
| **1. 零命中搜索词**<br>(`MISS_NO_RESULT`) | `tool_name IN ('search_wiki', 'get_developer_journey', 'read_knowledge_atom', 'get_evidence_fact') AND status = 'MISS_NO_RESULT'` | **情况 1（叫法差异）**：库内其实有该内容（例如用户搜 `MUSEPiPro`、`bianbu 2.0`、`x100`），直接把高频搜索词加进对应节点 frontmatter 的 `aliases` 列表中。<br>**情况 2（真实盲区）**：某款外设、接口或工具连续被搜到但无节点，从 `Sources/` 定向提炼 1 篇新的 Atom 或 Evidence。 |
| **2. 高频穿透原文**<br>(`read_raw_source_file`) | 某些 `Sources/docs-*` 路径被反复调用 `read_raw_source_file` | 作为候选缺口信号，先排除分页续读和用户主动核实；确认现有精炼节点缺少该原文中的关键实战表格后再提炼（如具体寄存器位定义、设备树配置片段或特定报错排障命令）。将该高频段落补充进对应 `Knowledge_Atom` 或新建 `Evidence`，减少后续问答的原文分页往返。 |
| **3. 用户授权的问题反馈**<br>(`mcp_issue_reports`) | 客户端经用户授权调用 `report_wiki_issue`，提交 `topic`、`description` 与可选 `issue_type`（`MISSING_DOC / INCORRECT_SPEC / BROKEN_LINK / SUGGESTION`） | 按硬件风险和复现证据排序工单：核对上游原文，修复对应节点并刷新索引。 |

`/stats` 与 D1 数据须先确认绑定、表结构和实际读写可用。异步写入采用尽力记录，工具接受反馈不等于已经核实或修复。当前日志缺少会话关联，原文调用次数不能直接当作“精炼检索回退率”；首轮记录时间窗口、调用次数/未命中口径与数据缺口，再决定是否需要扩展日志。

#### 2. 新建或扩充节点的准入标准
每次仅针对上述真实信号新增节点，且每个新节点必须同时满足：
- 解决至少 1 类真实未命中查询或高频原文回退问题；
- 包含完整的来源元数据（`source_file`、`source_commit`、`source_section` 等）；
- 遵守三层单向引用红线并挂载至 `index.md`；
- 通过 `vault_linker_lint.py` 与 `scripts/lint_wiki_integrity.py` 双重校验。

### B4. 建立 20 题核心回归评测集（Smoke & Accuracy Evals）

在维护端 `evals/` 与 `scripts/` 评测脚本中固化 20 道覆盖 6 大技术领域（`domain`）的高价值真题，用于检验“极简 Skill + 自解释 MCP”的实际表现：

| 题组 | 题数与候选主题 | `domain` 覆盖 |
| --- | --- | --- |
| 代际隔离与防混淆 | 4：K1/K3 CPU 与 ISA、AI 算力及测量条件、Dense/MoE 部署边界、Muse 系列与 K3 板型差异 | `chip_product_specs` |
| 硬件底线与电源安全 | 4：K1 Strap、K3 启动介质、PMIC 与板型配合、电平/供电与撤回勘误处理 | `hardware_schematic_design` |
| 管脚复用与外设调试 | 4：Muse Pi 排针、Pi Pro/CoM260 排针、PCIe/USB 复用限制、JTAG/串口调试条件 | `hardware_schematic_design`、`toolchain_debug_tools` |
| BSP、系统与安全启动 | 4：Buildroot 编译内核/U-Boot/打包、分区或 SecureBoot、Bianbu 版本与包安装、Bianbu GPIO 工具版本差异 | `bsp_kernel_drivers`、`bianbu_os_distribution` |
| SpaceAI 与 ROS 2 | 4：量化/框架支持、MoE 总参数与激活参数及内存边界、ROS 2 平台/发行版支持、传感器/SLAM/运动控制的支持与计划状态 | `edge_ai_robotics` |

每题记录问题、适用产品/版本、固定来源、预期命中或诚实未知行为、必要状态提示、实际结果与调用次数；算力和模型上限不写成脱离版本与测量条件的永久答案。在 20 题中安排 `stale`、`unknown`、冲突与待复核场景，确保 6 个 domain 均有明确题目。历史样例已移至维护端 `evals/legacy_skill_examples.json`，不视为已通过的 20 题报告；评测执行记录留在维护端，避免为每轮结果更新用户 Skill。

### 阶段 B 验收清单（完成后逐项打勾）

- [ ] 当前 12 个 `stale` 均有逐项 diff 复核记录；有据修正后目标为 0。未解决项明确列入阻塞清单，不能以批量刷新 SHA 通过验收。
- [ ] 7 篇 Journey 已补齐适用的直接来源与核验范围；目标 `unknown: 0`，不能据此宣称全库全文受监控或所有事实已审核。
- [ ] 已核查 `/stats` 或 D1 首轮真实数据并保留时间窗口、统计口径及维护依据，据此完成至少一轮 aliases 补充或节点优化。
- [ ] 20 题覆盖 6 个 domain，记录准确出处、适用边界、状态与诚实降级；普通问题以 1~3 次调用为目标，证据不足允许继续必要核查，不能为调用上限牺牲正确性。

## 5. 中远期储备阶段（P4 ~ P5：按需启动，当下不提前写代码）

以下阶段仅作为架构预留，确保当前设计与未来公司环境无缝衔接，但**在满足明确进入条件前不投入开发工时**：

### 5.1 P4：迁移或双活至公司内部服务器

- **进入条件**：阶段 A 能力与阶段 B 首轮评测可用；公司分配正式服务器/容器、网络入口、认证和运维负责人，明确要求独立承载 MCP。
- **落地方式**：复用同一 Git 版本的索引与检索契约，适配 Node.js 或 Python HTTP/SSE 服务。当前 Python 只有 stdio，加载 JSON 不等于已具备 HTTP/SSE、会话管理、认证、监控和回退能力，进入 P4 后按实际环境补齐。
- **原文供应**：精炼知识随索引提供；原文须使用对应固定 SHA 的联网获取或本地 Sources/镜像。要求完全离线时应配齐原文缓存，而非只部署索引。
- **验证与切换**：对比核心检索、元数据与分页；演练回退到已知 Git ref/旧入口，灰度稳定后再切换 MCP 地址。目标是用户 Skill 行为规则不变，连接地址单独更新；保留 Cloudflare 回退入口直到新服务稳定。

### 5.2 P5：服务端接入公司内部 RAG（MCP Gateway 模式）

- **进入条件**：公司 Wiki MCP 稳定；RAG API、数据范围、ACL、接口及冲突处理负责人明确。
- **客户端不感知双系统拼接**：公司服务端 MCP Gateway 编排 Wiki 精确检索、官方原文与公司 RAG，不由客户端拼接两个知识体系。
- **来源与权限隔离**：公开规格优先定位 Wiki 与官方原文，内部流程/客制项目定位 RAG；按产品、版本、权威性与授权勘误判断证据，内部板型或正式勘误可能与公开通用规格不同，不能采用“Wiki 永远覆盖 RAG”的全局优先级。无法裁决时并列来源并保留冲突。
- **ACL 先行**：无权限资料在重排及进入回答上下文之前排除，结果保留 `source_kind`、版本、权限范围、核验与 freshness 元数据；联合目标模型见 [MCP 接口契约](MCP_CONTRACT_V1.md)。
- **验收**：覆盖只命中 Wiki、只命中 RAG、跨域、权限隔离、冲突和单后端故障；RAG 故障时 Wiki 可独立工作，证据不足明确降级。

## 6. 近期明确“不做”的事（防发散清单）

1. **不另造 `wiki-release/<version>` 发布包目录与自定义回滚系统**。以 Git、双端一致索引和阶段 A 元数据溯源；线上回退仍需重新部署目标 ref，并核对版本与工具行为。
2. **不全量编译 Sources 为精炼节点**。按查询、反馈和已确认的关键缺口定向提炼。
3. **不做无人审阅的 AI 正文改写、事实来源 SHA/核验状态升级后自动发布**。保留已配置 CI 对 Sources 指针、索引、影响基线的自动提交推送，以及报告 artifact 和部署流程；这不代表事实已获人工批准。维护者完成内容修改与 diff 审阅后，按用户授权提交推送。
4. **不让问答自动修改知识库或发送反馈**。异步查询日志可由 Worker 记录；`report_wiki_issue` 必须有用户授权，不属于只读检索必经步骤。
5. **不提前编写假想公司 RAG adapter**。服务器与接口、权限边界就绪后再启动 P4/P5。

## 7. 近期执行顺序与文档职责

先 A1 版本溯源与自检，再 A2 双端响应提示、A3 Skill 瘦身和 A4 维护边界收敛；随后按 B1/B2 复核存量来源，完成 B3 首轮查询驱动优化与 B4 评测。B1/B2 可在阶段 A 期间开展，但不能把计划文档的更新视为代码、来源复核或 Skill 冻结已经完成。

- 本文件是阶段范围、状态和验收入口；旧 P2/P3 的近期范围由 A/B 替代，历史执行记录保留在 `log.md`。
- [MCP 接口契约](MCP_CONTRACT_V1.md) 区分现有 7 核心工具、Worker 运营扩展与未来联合元数据模型。
- [维护规范](MAINTENANCE.md) 和 [新鲜度维护流程](FRESHNESS_MAINTENANCE.md) 承载维护命令、状态更新和发布边界；普通用户按 [安装指南](../INSTALL.md) 接入，不执行仓库维护。
