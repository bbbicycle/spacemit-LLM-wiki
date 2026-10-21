---
type: vault_agent
title: "Spacemit LLM Wiki Agent 入口"
status: needs_review
created: 2026-06-29
updated: 2026-10-21
aliases: [Agent, Agent.md, AGENTS, AGENTS.md, 运行与协作规范]
---

# Agent 入口

`AGENTS.md` 链接到本文件。目标是用足够证据回答问题，减少无关读取。

## 查询

1. 复用会话中已有且仍适用的证据。先明确芯片代际、板型和版本；参数不可跨产品套用。
2. 按意图直接选工具：步骤用 `get_developer_journey`，专题用 `read_knowledge_atom`，参数用 `get_evidence_fact`；名称不明时先 `search_wiki`。无需逐层遍历图谱。
3. 摘要只用于定位；具体结论应有正文证据。证据缺失、冲突、过期或用户要求核实上游时，允许 `search_raw_sources` 后定向读取原文，不要求先有报错日志。
4. 原文默认返回 200 行，显式 `start_line`、`end_line` 范围最多 500 行；按 `has_more`、`next_start_line` 按需续读。本地大专题按章节读取，MCP 按实际参数调用。不得一次读取全部 `Sources/`、整个 JSON 索引或递归输出全库正文。
5. 本地兜底先在 `Developer_Journeys/`、`Knowledge_Atoms/`、`Evidence/` 定向查找；先列文件、再限范围读取。Sources 只读，限定子模块和文件。联网兜底只用官方同源公开资料。
6. 核心结论和关键参数得到支持即停止；普通问答以 1～3 次调用为目标，证据不足可继续必要核实。无记录时说明未知，不猜测。

## 回答

给出出处及适用条件。`needs_review` 不是已审核结论；说明冲突、撤回或过期状态。硬件接线和性能数字需核实来源。公开回答只引用可对外使用的资料，价格需检查有效期。

## 维护

仅在编辑、录入、同步或审计时按需读取 [维护规范](docs/MAINTENANCE.md)。问答不自动写库、提交或推送；维护按用户授权执行。

阶段范围与验收以 [项目计划](docs/PROJECT_PLAN.md) 为准。P0/P1 已完成，阶段 A/B 待执行；计划中的 `build_meta`、`/health`、`agent_notice` 和 Skill 冻结不能当作已上线能力。用户 Skill 承载稳定查询规则，维护命令留在仓库内部；Worker 负责生产运营，Python 保持 7 核心工具契约镜像。

知识正文以中文为主，新增或修改后标记 `needs_review`。链接方向：Journey → Atom/Evidence；Atom → Atom/Evidence；Evidence 不向上引用，普通知识节点不引用 Journey。重大更新同步索引和日志，并执行相关检查。
