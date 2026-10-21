---
name: spacemit-wiki
description: "查询进迭时空（SpacemiT）K1/K3/V100、MUSE 系列与开发板、Bianbu OS、Buildroot BSP、SpaceAI 和 ROS 2 的规格、引脚、驱动与部署资料，通过 spacemit-wiki MCP 获取带来源和状态的证据。"
---

# SpacemiT Wiki · 检索行为契约 v1

## 1. 适用范围与接入

涉及 SpacemiT 芯片、板卡、系统、工具链或端侧 AI 时，优先调用 `spacemit-wiki` MCP，不能用模型记忆猜测具体规格或命令。
Skill 不等于 MCP 已连接；工具参数以实际 schema 为准。仅在用户要求安装或修复接入时读取 [接入说明](mcp.md)，普通问答不改配置。

## 2. 按需检索漏斗

1. 明确芯片代际、具体板型、软硬件版本和任务；名称不明用 `search_wiki`，必要时向用户澄清。
2. 直达精炼正文：步骤用 `get_developer_journey`，技术专题用 `read_knowledge_atom`，引脚/电气/性能事实用 `get_evidence_fact`；需要依赖关系时用 `get_graph_relations`。摘要只用于定位，无需机械遍历每层。
3. 精炼证据缺失、冲突、`stale/unknown` 或用户要求核实原文时，用 `search_raw_sources` 定位，再用 `read_raw_source_file` 定向读取。默认 200 行、显式范围最多 500 行，按 `has_more / next_start_line` 续读。原文固定于索引版本，不保证实时上游。

复用已加载且仍适用的证据。普通问题以 1～3 次调用为目标，证据不足继续必要核实；核心结论已获支持即停止。不读取整库或完整索引来回答单个问题。

## 3. 回答与证据纪律

- 遵循返回的 `agent_notice` 和 `hint`，结合元数据及正文核实；旧服务没有可选提示字段时也须检查状态。
- 引用来源文件或节点及适用条件。`current` 只代表声明来源在固定快照下无变化；`verified` 不等于人工批准，`needs_review` 须说明待终审；保留撤回、冲突、过期和使用范围提示。
- 参数绑定芯片代际、板型和版本。接线核对物理 Pin、信号/GPIO 编号、连接方向、供电和电平；命令核对 OS、SDK、内核和工具版本，不能跨平台套用。
- 性能需注明模型、精度、设备和测量条件；Dense/MoE、总参数和激活参数分别说明，不能从算力推断模型保证。
- `external_use:false` 不用于对外事实承诺；遵守资料访问权限。证据不足或 MCP 不可用时说明限制，仅用已确认适用的证据，无法确认就说明未知，不编造。
- 发现缺失或错误先说明；仅经用户明确授权，且服务提供该工具时，才调用 `report_wiki_issue` 反馈。接受反馈不等于已持久化或修复。

## 4. 只读边界

问答不自动修改用户文件、知识库或客户端配置，不执行仓库同步、Git 提交推送或发送反馈。维护须有独立任务授权；查询日志可由服务端记录。
