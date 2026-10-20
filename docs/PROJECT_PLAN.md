# SpacemiT Wiki → 公司服务器 + RAG 项目完整计划

> 版本：v1.1
> 日期：2026-10-20
> 适用仓库：`spacemit-LLM-wiki`

## 1. 项目目标

把当前的 SpacemiT 独立 Wiki 演进为一套可迁移、可审计、可接入公司 RAG 的知识服务：

```text
官方 Sources / 公司内部资料
          ↓
同步、编译、校验、评测、版本化发布
          ↓
公司服务器
  ├─ Wiki 精确知识层
  ├─ 原始资料层
  ├─ 公司 RAG 检索层
  ├─ 权限、来源、冲突和新鲜度编排
  └─ MCP Gateway
          ↓
用户 Agent + 稳定 Skill
```

最终要求：

1. Wiki 内容更新主要发生在服务器侧，用户端不因内容变化而更新 Skill。
2. Wiki 精确检索和公司 RAG 保持独立来源与权限边界，由 MCP Gateway 统一编排。
3. 用户 Agent 获得可引用、可追溯、带版本和核验状态的证据。
4. Cloudflare Worker 可以被公司服务器替换，客户端 MCP 契约尽量保持兼容。
5. 查询不会自动修改 Wiki、提交代码、推送发布或写入内部知识库。

## 2. 当前基线

当前仓库已经具备这些能力：

- 66 个精炼节点：7 个 Journey、32 个 Knowledge Atom、27 个 Evidence。
- 1,231 个官方原始资料索引。
- `scripts/build_mcp_index.py` 生成本地 MCP 索引和 Worker 索引。
- `mcp/server.py` 提供本地 stdio MCP 服务。
- `mcp-worker/` 提供 Cloudflare Worker MCP 服务。
- 原始资料索引已经记录 `source_commit`，本地来源版本不匹配时可回退到固定 commit 原文。
- GitHub Actions 已经负责 Sources 同步、索引构建、校验和部署。
- 当前测试基线：索引构建测试、MCP 测试和索引一致性检查通过。

当前需要补强的地方：

- 只有部分节点有完整的 `source_file/source_commit` 元数据。
- 上游影响分析主要依赖显式 Markdown 路径，尚不能覆盖所有来源关系。
- 过期检测需要按“具体源文件在两个 commit 之间是否变化”判断，不能只比较子模块 HEAD。
- `read_raw_source_file` 目前默认可返回全文，需要增加服务端分页上限。
- `SKILL.md` 和规则文件仍包含部分易变事实，应逐步把事实权威移回服务器返回结果。
- `check_upstream_impact.py --cached` 没有缓存时会跳过分析，需要建立稳定的基线记录机制。

## 3. 不变的架构原则

### 3.1 Wiki 与公司 RAG 的关系

Wiki 和公司 RAG 是两个检索后端：

- Wiki 负责官方、结构化、精确、可追溯的芯片和产品知识。
- 公司 RAG 负责内部文档、项目资料、流程和企业上下文。
- 两者不能在索引层混成无来源的统一向量库。
- 服务器必须保留来源类型、文档版本、权限范围、核验状态和更新时间。

### 3.2 写入路径与查询路径分离

```text
写入路径：资料 → 同步 → 编译 → 校验 → 评测 → 版本化发布
查询路径：Agent → MCP → 权限过滤 → Wiki/RAG 检索 → 证据编排 → Agent
```

用户查询不触发自动写库。维护动作由维护者明确触发，并经过 diff 和检查。

### 3.3 Skill 保持稳定和轻量

用户版 Skill 只保留：

- 工具选择和查询顺序；
- 代际、版本和适用范围检查；
- 来源、核验状态和新鲜度的回答要求；
- MCP 异常时的诚实降级规则；
- 不编造、不自动写库的行为边界。

具体芯片参数、性能数字、来源 commit、内部流程和易变规则进入服务器 Wiki/RAG，不在用户 Skill 中重复维护。

另外保留一个只给维护者使用的维护 Skill，用于 stale 节点处理、原文核实、Wiki 修改和发布检查。

## 4. 阶段总览

| 阶段 | 名称 | 目标 | 是否接公司 RAG |
|---|---|---|---|
| P0 | 冻结目标与接口 | 确定目标架构、数据模型和 MCP 兼容边界 | 否 |
| P1 | Wiki 新鲜度与自愈闭环 | 让上游变化可发现、可定位、可审核 | 否 |
| P2 | MCP 与发布工程化 | 让 Wiki 可脱离 Cloudflare 独立部署 | 否 |
| P3 | 查询驱动扩展与评测 | 用真实问题扩展 Wiki，并建立质量指标 | 否 |
| P4 | 公司服务器承载 Wiki | 将 Wiki 构建产物和 MCP 服务迁移到公司环境 | 否，先只迁 Wiki |
| P5 | 接入公司 RAG | 在服务器侧增加 RAG 适配器和混合检索编排 | 是 |
| P6 | 切换生产入口 | 用户端切换到公司 MCP Gateway，按需下线 Cloudflare | 已完成 |
| P7 | 长期运营 | 版本、权限、回滚、评测和维护责任固定化 | 持续 |

## 5. P0：冻结目标与接口

### 目标

在写代码前固定数据边界和服务边界，避免未来接入公司 RAG 时重写客户端。

### 工作项

1. 记录目标架构和责任边界。
2. 确定 MCP 工具兼容策略：保留现有 7 个核心工具的语义，新增能力采用兼容新增工具或版本字段。
3. 定义统一结果元数据：

   ```json
   {
     "source_kind": "wiki|company_rag|raw_source",
     "source_id": "...",
     "source_version": "...",
     "verification_status": "verified|unverified|conflicted",
     "freshness": "current|stale|unknown",
     "external_use": true,
     "access_scope": "public|internal|restricted"
   }
   ```

4. 定义服务器部署形态：构建作业、索引存储、MCP 查询服务、监控和回滚位置。
5. 确定公司 RAG 的接口负责人、权限边界和资料范围，但暂不接入运行链路。

### 产物

- 本计划文档。
- MCP 接口契约 v1。
- Wiki/RAG 结果元数据契约 v1。
- 责任矩阵：你、公司服务器维护者、RAG 维护者、客户端用户。

### 验收标准

- 可以画出从源资料到 Agent 的完整数据流。
- 可以说明每个结果来自 Wiki、原始资料还是公司 RAG。
- 未来替换 Cloudflare 时不需要修改工具的核心语义。

## 6. P1：Wiki 新鲜度与自愈闭环

### 目标

先把独立 Wiki 的准确性和维护成本降下来。

### 工作项

#### 6.1 补齐来源元数据

对所有 Evidence 和有事实依据的 Knowledge Atom，补齐：

- `source_file`
- `source_commit`
- `source_section` 或 `source_locator`
- `source_resolution`
- `verification_status`
- `source_checked_at`
- `verified_at`（只有实际完成事实复核时填写）

Journey 可以通过引用的 Atom/Evidence 间接获得来源，但关键步骤仍应保留原始出处。

#### 6.2 增加按文件路径的过期检测

在 `scripts/build_mcp_index.py` 中增加独立的 freshness 计算：

```text
节点 source_file 的 source_commit
        ↓
比较该文件在 old_commit..current_commit 的 diff
        ↓
未变化：current
已变化：stale
无法判断：unknown
```

建议新增字段：

```json
{
  "freshness": "stale",
  "stale_paths": ["Sources/docs-chip/.../file.md"],
  "checked_against_commit": "..."
}
```

不要把 freshness 直接写入 `verification_status`。上游变化表示需要复核，不代表事实一定错误。

#### 6.3 修复影响分析工具

升级 `scripts/check_upstream_impact.py`：

- 支持 frontmatter 中的 `source_file` 和 `source_related_file`；
- 支持 Markdown 链接、Wiki 双链和来源元数据三种关系；
- 首次运行自动保存当前子模块 commit 基线；
- 后续运行输出变更文件、受影响节点、未覆盖文件和删除文件；
- 报告使用 JSON 结构，便于 Agent 或 CI 消费；
- 保留人类可读报告。

#### 6.4 给原文读取加安全分页

同步修改：

- `mcp/server.py`
- `mcp-worker/src/index.ts`
- MCP schema
- `skill/spacemit-wiki/mcp.md`
- 测试

默认最多返回 200 行，返回 `has_more` 和 `next_start_line`。显式范围也应有最大窗口，避免单次请求读取超大文件。

#### 6.5 固化维护者工作流

维护者命令应支持：

```text
检查 stale 节点
→ 读取对应最新原文
→ 修改 Knowledge_Atoms / Evidence
→ 刷新 source_commit 和 source_checked_at
→ 标记 needs_review
→ 运行 lint、测试和索引检查
→ 查看 git diff
→ 人工确认后提交
```

### 产物

- freshness 字段和 stale 报告。
- 可靠的上游影响分析报告。
- 原文分页读取。
- 维护者操作说明或维护者 Skill。
- 至少 5 个 freshness 和分页回归测试。

### 验收标准

- 修改一个被节点引用的源文件时，该节点被标记为 `stale`。
- 只修改同一子模块的无关文件时，不会让所有节点变 stale。
- stale 节点可以被维护者按路径定位和复核。
- 原文读取默认不会返回整篇超长文件。
- 当前两份索引完全一致，所有测试通过。

### P1 执行记录（2026-10-20）

- **工程状态：已完成**。所有 27 篇 Evidence 与 32 篇 Knowledge Atom 具备必需来源字段；多文件来源使用路径与 SHA 平行列表。保留原有事实核验结果，新补定位的专题保持 `unverified / partial / needs_review`。
- 索引 v2.2.0 增加按文件计算的 `freshness`、`stale_paths`、`unknown_paths`、`checked_against_commit` 与逐来源 `source_freshness`，不覆盖核验状态。
- `check_upstream_impact.py` 支持三种直接来源关系和双链传递影响，自动初始化可提交基线 `docs/source_baseline.json`，同时输出 JSON、可读报告、未覆盖与删除路径；错误返回非零且不推进已有基线。
- Python 与 Worker 原文工具默认最多 200 行，显式窗口最多 500 行，返回 `has_more / next_start_line`；两端 schema、Skill 和维护说明已对齐。
- 同步脚本与 CI 保存 freshness 和影响报告，来源字段 lint 与离线回归覆盖文件变化、无关变化、删除、历史缺失、补充来源、首次基线、分页与跨端一致性。
- 当前构建为 66 个节点 / 1,231 篇原文：47 个 `current`、12 个 `stale`、7 个无直接来源的 Journey 为 `unknown`。已有 stale 保留为待复核队列，不通过批量刷新 SHA 消除。事实逐项复核与人工批准仍按维护流程执行。
- 操作与结果契约见 [新鲜度与维护闭环](FRESHNESS_MAINTENANCE.md)，派生报告位于 `reports/freshness.json` 和 `reports/upstream-impact.json`，CI 提供对应 artifact。

## 7. P2：MCP 与发布工程化

### 目标

让 Wiki 从 Cloudflare Worker 中独立出来，具备公司服务器可直接承载的发布包。

### 工作项

1. 把 Wiki 构建结果定义为版本化 artifact：

   ```text
   wiki-release/<version>/wiki_graph.json
   wiki-release/<version>/manifest.json
   wiki-release/<version>/eval-report.json
   ```

2. `manifest.json` 记录：

   - Wiki commit；
   - 五个 Sources commit；
   - 构建时间；
   - 内容 hash；
   - 测试结果；
   - 可公开范围。

3. 把构建与查询解耦：

   - CI 或服务器构建作业负责同步、编译和校验；
   - 查询服务只加载已经发布的 artifact；
   - 发布使用原子切换；
   - 保留上一版本用于回滚。

4. 为本地 Python MCP 和 Worker MCP 统一输出字段。
5. 增加健康检查：

   - 当前 Wiki 版本；
   - Sources 版本；
   - 索引 hash；
   - 构建时间；
   - 最近一次测试结果。

6. 增加部署前 smoke test：

   - `search_wiki("Muse Pi")`；
   - `get_evidence_fact("muse_pi_vs_pi_pro_specs")`；
   - `search_raw_sources(...)`；
   - 有范围的 `read_raw_source_file(...)`。

### 产物

- MCP contract v1。
- 版本化 Wiki artifact。
- 发布和回滚脚本。
- 健康检查接口。
- 部署 smoke test。

### 验收标准

- 不需要 Cloudflare Worker 也能启动完整 Wiki MCP 服务。
- 查询服务不依赖用户当前工作目录。
- 可以在两个 Wiki 版本之间原子切换和回滚。
- 本地服务、Worker 服务和未来公司服务对同一个 artifact 返回一致结果。

## 8. P3：查询驱动扩展与评测

### 目标

用实际使用数据决定 Wiki 扩展方向，而不是批量编译全部原始文档。

### 工作项

1. 统计查询日志：

   - Wiki 命中率；
   - 原始资料回退率；
   - 未命中问题；
   - 重复查询主题；
   - stale 节点被访问次数；
   - 用户反馈问题。

2. 每个新节点都要记录：

   - 触发问题；
   - 原始来源；
   - 适用产品和版本；
   - 核验状态；
   - 是否解决了一个重复问题。

3. 扩充 `evals.json`，按领域覆盖：

   - K1/K3 代际隔离；
   - Strap、JTAG、供电等安全问题；
   - IOMAP 和驱动问题；
   - Buildroot/Bianbu；
   - SpaceAI/ROS2；
   - stale 和冲突处理。

4. 建立回归评测：每次 Wiki 发布都运行。
5. 记录人工抽检结果，不把工具命中等同于事实正确。

### 验收标准

- 连续两个发布周期都有可比较的评测结果。
- 新节点来自真实问题或明确盲区。
- 可以看到原始资料回退率是否下降。
- 关键安全问题没有因为扩展节点而失去来源和状态。

## 9. P4：公司服务器先承载 Wiki

### 进入条件

- P1 的 freshness 和维护闭环通过验收。
- P2 的 artifact、MCP 契约、健康检查和回滚可用。
- P3 至少有一轮真实查询评测。
- 公司服务器具备部署、日志、备份和访问控制条件。

### 工作项

1. 在公司服务器部署 Wiki 构建作业。
2. 部署 Wiki MCP 查询服务。
3. 让服务器直接消费版本化 artifact。
4. 接入公司统一认证或至少建立明确的访问控制。
5. 加入服务监控：延迟、错误率、未命中率、版本和索引 hash。
6. 使用灰度方式验证：

   ```text
   本地 MCP → Cloudflare MCP → 公司 Wiki MCP
   ```

7. 保留 Cloudflare 作为回退入口，直到公司服务连续稳定运行。

### 验收标准

- 公司服务器可以独立运行 Wiki MCP。
- 同一问题在本地、Cloudflare 和公司服务器返回的来源与状态一致。
- 公司服务器故障时可以回退到旧版本或临时入口。
- 用户不需要因为 Wiki 内容更新而重新安装 Skill。

## 10. P5：接入公司 RAG

### 进入条件

- 公司 Wiki MCP 已经稳定运行。
- 公司 RAG 已明确数据范围、权限模型和接口负责人。
- 可以区分公开、内部和受限资料。
- 已建立 Wiki 与公司 RAG 的来源优先级和冲突处理规则。

### 推荐接入方式

不要让客户端 Skill 分别调用两个系统。由公司 MCP Gateway 统一编排：

```text
Agent
  ↓
MCP Gateway
  ├─ Wiki exact retrieval
  ├─ Wiki raw-source retrieval
  ├─ Company RAG retrieval
  ├─ ACL filtering
  ├─ authority/freshness/conflict resolution
  └─ unified evidence response
```

### 工作项

1. 编写公司 RAG adapter，不改动 Wiki 的来源模型。
2. 定义查询路由：

   - 芯片规格、引脚、官方文档：优先 Wiki；
   - 内部流程、项目经验、内部设计资料：优先公司 RAG；
   - 跨域问题：两者都查，由服务器合并；
   - 证据不足：明确返回缺口，不用模型记忆补全。

3. 定义来源优先级。建议按问题类型和版本判断，不使用简单的全局优先级。
4. 强制执行 ACL：先过滤无权访问的文档，再进入重排和回答上下文。
5. 统一结果字段：来源、版本、权限范围、核验状态、更新时间、冲突状态。
6. 新增混合检索评测：

   - 只应命中 Wiki 的问题；
   - 只应命中公司 RAG 的问题；
   - 两者都有资料的问题；
   - 权限隔离问题；
   - 冲突和过期问题。

7. 观察一个完整周期后，再决定是否扩大 RAG 的资料范围。

### 验收标准

- 无权限的公司文档不会出现在检索结果或回答上下文。
- 官方 Wiki 事实不会被无来源的内部片段覆盖。
- 混合检索结果可以解释每条结论来自哪个后端。
- RAG 不可用时，Wiki 仍可独立工作。
- Wiki 不可用时，系统会明确降级，不伪装成完整答案。

## 11. P6：切换生产入口

### 工作项

1. 为公司 MCP Gateway 配置稳定域名和版本策略。
2. 在用户 Agent 中切换 MCP 地址。
3. 保持用户版 Skill 不变或只更新服务地址配置。
4. 进行小范围内测。
5. 观察错误率、延迟、未命中率、权限错误和用户反馈。
6. 连续稳定后，再下线或降级 Cloudflare Worker。

### 验收标准

- 内测用户无需重新编写 Skill。
- 公司服务器可独立完成 Wiki + RAG 查询。
- Cloudflare 下线不会造成数据或索引丢失。
- 有明确的回退入口和回退步骤。

## 12. P7：长期运营机制

### 日常

- 自动同步官方 Sources。
- 生成 freshness 和影响报告。
- 构建并校验 Wiki artifact。
- 发现 stale 节点后进入维护队列。
- 记录查询未命中和用户反馈。

### 每周

- 处理高频 stale 节点。
- 处理高频未命中问题。
- 复查 RAG 权限错误和冲突结果。
- 抽检关键硬件安全结论。

### 每月

- 发布 Wiki 质量报告。
- 更新评测集。
- 复盘 Wiki 命中率、原始资料回退率和用户满意度。
- 清理无效来源、过期索引和重复节点。
- 检查 Skill 与 MCP contract 的兼容性。

## 13. 近期执行顺序

接下来按下面顺序推进，不要跳到公司 RAG 接入：

### 第 1 批：来源与过期闭环

1. 补齐 Evidence 的来源元数据。
2. 实现按文件路径的 freshness 检测。
3. 升级 `check_upstream_impact.py`。
4. 增加 stale 报告和维护者处理说明。

### 第 2 批：读取安全与契约稳定

5. 给本地和 Worker 的原文读取增加 200 行默认上限。
6. 增加 `has_more`、`next_start_line` 和最大窗口测试。
7. 对齐本地 MCP、Worker MCP 和文档中的返回结构。
8. 固定 MCP contract v1。

### 第 3 批：发布工程化

9. 生成版本化 Wiki artifact 和 manifest。
10. 增加健康检查、smoke test 和上一版本回滚。
11. 让构建作业和查询服务分离。
12. 写公司服务器部署说明，但暂不迁移生产流量。

### 第 4 批：查询驱动增长

13. 建立未命中和原始资料回退统计。
14. 扩展真实问题评测集。
15. 每次沉淀一个真实问题对应的新节点或节点修订。

### 第 5 批：服务器迁移与 RAG 准备

16. 在公司服务器先部署 Wiki-only MCP。
17. 稳定运行后再对接公司 RAG adapter。
18. 完成 ACL、来源优先级、冲突处理和混合评测。
19. 最后切换用户端 MCP 入口。

## 14. 明确暂不做的事情

- 暂不接公司 RAG 生产链路。
- 暂不把 1,231 篇原始资料全部编译成精炼节点。
- 暂不做无人工审核的自动改写、提交和推送。
- 暂不让用户查询直接写入 Wiki 或公司 RAG。
- 暂不把 Wiki 和公司 RAG 混成没有来源边界的向量库。
- 暂不因为未来要上公司服务器而提前放弃 Cloudflare。

## 15. 项目完成定义

项目达到目标，需要同时满足：

1. Wiki 有稳定的来源、freshness、核验和回滚机制。
2. Wiki 可以独立部署在公司服务器上。
3. 公司 RAG 通过服务器端 adapter 接入，而不是由客户端自行拼接。
4. MCP 返回统一、可引用、带权限和版本信息的证据。
5. 用户端 Skill 对 Wiki 内容更新保持稳定。
6. 用户查询不会越权、编造或无提示地混合不同来源。
7. Cloudflare 可以被替换而不改变知识模型和用户使用方式。
