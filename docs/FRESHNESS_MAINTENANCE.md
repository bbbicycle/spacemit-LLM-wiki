# Wiki 新鲜度与维护闭环（P1）

来源版本、新鲜度和事实核验是三个独立维度。构建与查询不会自动改写知识正文或把事实升级为已核验；维护者根据报告定向复核，再按授权提交和发布。

P1 工具链已完成；当前 [项目计划 v2.0](PROJECT_PLAN.md) 的阶段 B 已完成首轮 12 项来源 diff 复核、7 篇 Journey 补来源与查询评测；K3 Strap 清单与 SPI NOR/NAND 电平映射的官方冲突仍阻塞 B1 验收，见 [审计记录](reviews/stage_b_2026-10-21/README.md)。阶段 A 的响应提示与 Worker 健康接口已完成并通过部署验收；提示用于解释状态，不替代本页的事实复核流程，线上版本以 `/health` 为准。

## 来源记录

所有 Evidence 和包含事实的 Knowledge Atom 必填：

```yaml
source_file: "Sources/docs-chip/zh/key_stone/k1/k1_hw/k1_hw_design_guide.md"
source_commit: "完整的历史 commit SHA"
source_section: "明确的章节名称" # 或 source_locator，至少一个
source_resolution: partial     # resolved / partial / unresolved
verification_status: unverified # verified / unverified / conflicted
source_checked_at: 2026-10-20
status: needs_review
```

`source_checked_at` 表示来源定位检查日期。只有实际完成事实复核时填写或更新 `verified_at`，不能因补字段或更新 SHA 自动填写。`source_resolution:resolved` 只表示定位成功，不能替代 `verification_status:verified`。本批次保留已有历史事实核验记录，新补来源的专题维持 `unverified / partial / needs_review`。

多文件用 `source_related_file` / `source_related_commit` 的等长列表，按位置一一对应；`source_file` / `source_commit` 也支持等长列表。单文件可用标量。补充来源跨子模块时，必须填写该子模块自己的 SHA，不继承主来源版本。构建器支持这些顶层列表，不支持嵌套 YAML。

Journey 可通过双链访问 Atom/Evidence 的来源；没有直接来源时，其自身 freshness 为 `unknown`。关键操作步骤应直接声明原始出处。不得把整条 Journey 的无来源状态解释成所有引用均已过期。

阶段 B 已为现有 7 篇 Journey 补充直接来源，按关键步骤补充必要的其他出处并记录核验范围，详见 [逐篇记录](reviews/stage_b_2026-10-21/journey_sources.json)。只锚定少数文件不能证明全文都受新鲜度监控；覆盖不足保持 `partial / unverified / needs_review`，不填无关来源来消除 `unknown`。

## 构建与定位 stale 节点

```bash
python3 scripts/build_mcp_index.py --if-changed --freshness-report reports/freshness.json
python3 scripts/build_mcp_index.py --check
```

构建要求完整、已初始化且没有已跟踪修改的 Sources；缺失时保留现有发布索引。`reports/` 是不提交的派生产物，CI 将报告上传为 artifact。

每个节点及 MCP 查询结果包含：

| 字段 | 含义 |
| --- | --- |
| `freshness` | 已声明来源文件的聚合新鲜度：`current / stale / unknown` |
| `stale_paths` | 相对仓库根目录的已变化来源路径 |
| `unknown_paths` | 无法判断的来源路径；没有直接来源时可为空 |
| `checked_against_commit` | 本次构建中所检查的子模块名称到当前 SHA 的映射 |
| `source_freshness` | 每份来源的历史 SHA、检查目标 SHA、新鲜度和原因 |

对每份来源，先确认历史 commit 和文件可读取，再执行该路径的 `git diff --quiet old current -- path`。无变化为 `current`，修改、删除或移走为 `stale`；历史不存在、路径无效、版本缺失或 diff 失败为 `unknown`。聚合时 `stale` 优先于 `unknown`，所有声明来源可判断且均无变化才为 `current`。同一子模块的无关文件变化不影响该节点。

这只比较声明文件在两个快照的差异，不保证文件内所有事实均已复核，也不推断未声明的外部来源。文件曾改动又完整还原时，两个快照无差异，结果为 `current`。新鲜度不覆盖 `verification_status`、`status` 或 `external_use`。

查看维护队列，不必读取完整索引正文：

```bash
python3 - <<'PY'
import json
report = json.load(open('reports/freshness.json', encoding='utf-8'))
print(report['summary'])
for node in report['nodes']:
    print(node['id'], node['freshness'], node['stale_paths'], node['unknown_paths'])
PY
```

## 上游影响分析与持久基线

```bash
# 不联网：首次运行自动保存当前基线，以后比较上次基线与当前 checkout
python3 scripts/check_upstream_impact.py --cached --json reports/upstream-impact.json
# 只输出 JSON 到 stdout；可读报告仍输出到 stderr
python3 scripts/check_upstream_impact.py --cached --json - > reports/upstream-impact.json
# 核查或同步成功后，推进基线；未给 --save 的检查不会吞掉待处理变化
python3 scripts/check_upstream_impact.py --cached --save --json reports/upstream-impact.json
```

默认基线为随仓库提交的 `docs/source_baseline.json`，也可用 `--baseline PATH` 指定。该文件替代旧的、被忽略的 `.last_synced_commits.json`，使 CI 的新 checkout 也能比较上一次同步版本。首次建基线不意味着历史节点已复核，历史欠账由独立 freshness 队列保留。

不加 `--cached` 时，工具 fetch 并比较本地 HEAD 和远端默认分支；不切换子模块、不改知识正文。`--init-baseline` 仅在文件缺失时初始化，适合同步前调用。基线损坏、子模块缺失或历史 diff 不可读时返回非零，不能把分析失败报告成“没有变化”，也不推进已有基线。

JSON 包含 `submodules`（old/new SHA）、`changed_files`（状态、完整路径、受影响节点）、`affected_nodes`、`uncovered_files`、`deleted_files` 和 `errors`。Markdown 链接、指向 Sources 的 Wiki 双链、frontmatter 主/补充来源均参与映射；Atom/Evidence 的变化会沿双链传递到依赖它们的节点与 Journey。重命名按删除旧路径和新增新路径报告。未覆盖文件是待评估盲区，不要求批量编译为新节点。

`update_sources.sh` 在同步前补建缺失基线，成功同步、构建和 lint 后生成两个报告并推进基线；失败时保留错误信息。来源影响基线已推进不等于 stale 队列已清空。

## 逐条复核流程

1. 从 `stale_paths` 和 `source_freshness` 定位来源，确认芯片代际、产品、版本及核验范围；`unknown` 先补齐历史对象或正确出处。
2. 使用 `search_raw_sources` 查找最新构建收录的对应文件，再按范围 `read_raw_source_file`。它读取索引固定 commit；查看尚未构建的最新上游时，维护者需先同步 Sources 并重建，或在本地定向查看当前文件。删除的旧文件使用历史 commit 查看，保留撤回警告和替代来源。
3. 比对新旧章节，修改对应 Knowledge Atom / Evidence。保留冲突、测量条件、版本范围及历史未核验项；不自动改写硬件安全结论。
4. 对**实际检查过的来源**更新对应 `source_commit`（或补充来源列表中的该项）与 `source_checked_at`，设置 `status:needs_review` 和 `updated`。其余来源 SHA 不批量刷新。只有已逐项复核且证据充分，才按实际范围更新 `verification_status` 与 `verified_at`；AI 不设置 `status:approved`。
5. 重建索引、运行以下校验并查看 diff。新增节点挂载 `index.md`，重大更新记录 `log.md`。

复核时按变更类型分别处理：

| 变更类型 | 处理与记录 |
| --- | --- |
| 排版、图片路径或无关章节变化 | 确认声明范围的事实未变后，仅更新已检查来源的 SHA、检查日期和文档更新日期，置 `needs_review`；保留核查说明，不升级未检查事实。 |
| 参数、接线、命令或适用条件变化 | 阅读新旧章节上下文，修正正文并检查依赖节点与 Journey，保留勘误和未解决冲突；按实际复核范围更新核验记录，等待人工终审。 |
| 删除、拆分、迁移或撤回 | 用历史 diff/log 定位；新路径须确认产品、版本及语义对应，再改路径/SHA。无可用替代时保留历史来源与撤回警告，将事项列为阻塞。 |

P1 历史基线为 47 current、12 stale、7 unknown；本轮逐项复核后为 66 current、0 stale、0 unknown。K3 Strap 两节点保持 conflicted，B1 验收仍未完成；不能把 freshness 清零当作冲突消失。无法判定的项保持真实状态并记录原因、负责人/后续动作；不能批量刷新 SHA 使报告清零。`stale: 0 / unknown: 0` 仅说明声明来源在该构建快照下可判定，不代表全文正确或 `status: approved`。`check_upstream_impact.py --cached` 比较持久基线，不一定保留所有旧 stale 的变化，逐条复核仍须使用节点自己的历史 `source_commit`。

```bash
python3 vault_linker_lint.py
python3 scripts/lint_wiki_integrity.py
python3 -B scripts/test_build_mcp_index.py
python3 -B scripts/test_upstream_impact.py
python3 -B -m unittest discover -s mcp -p 'test_server.py'
python3 scripts/build_mcp_index.py --if-changed --freshness-report reports/freshness.json
python3 scripts/build_mcp_index.py --check
(cd mcp-worker && npx tsc --noEmit)
node --disable-warning=ExperimentalWarning mcp-worker/test_runtime.cjs
node --disable-warning=ExperimentalWarning mcp-worker/test_index_runtime.cjs
python3 -B scripts/eval_stage_b.py
git diff --check
git diff --stat
# 定向查看刚修改的节点、脚本及来源 SHA，审阅后按用户授权提交
```

Worker 测试需要 Node 22.13+（CI 使用 Node 24）；类型检查需要先在 `mcp-worker` 执行 `npm ci`。维护记录和检查通过不等于人工批准；提交与推送依据当前用户授权或既有自动化配置。

已配置 CI 可自动同步 Sources、提交索引和影响基线并部署；不自动替维护者改写知识正文、刷新事实来源 SHA 或升级核验状态。线上回退需重新部署指定 Git ref 并核对索引与核心调用，不能只执行 Git revert。

## 原文分页契约

两端 `read_raw_source_file` 使用相同语义，现有参数名不变：

- `start_line` 默认为 1，`end_line` 为包含在内的行号；均需为正安全整数，结束行不能小于起始行。
- 不给结束行时，最多返回 200 行。显式窗口超过 500 行时，裁剪到从起点开始的 500 行。
- `total_lines` 是整份文件的行数，`start_line` 是请求起点，`end_line` 是实际结束行；`content` 是本次正文。
- `has_more:true` 时，用 `next_start_line` 作为后续起点；末页为 `false / null`。这表示文件还有行，与用户指定结束行无关。
- 空文件返回空正文、`total_lines:0 / end_line:0`；起点越过末尾时返回空正文、实际总行数作为 `end_line`，`has_more:false / next_start_line:null`。
- `source`、`source_commit` 仍指向索引的固定版本，`origin` 是 `local` 或 `github`。分页限制返回正文；服务端当前仍读取完整文件以统计总行数。

例如首次返回 `start_line:1 / end_line:200 / has_more:true / next_start_line:201`，下一次仅设置 `start_line:201` 即可。精炼专题和事实工具保留整篇读取语义。
