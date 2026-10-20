---
name: spacemit-wiki
description: "查询 Spacemit（进迭时空）K1/K3 芯片、Muse Pi/K3 Pico/CoM260 开发板、Bianbu OS、SpaceAI 和 ROS2 技术资料。使用 spacemit-wiki MCP 检索规格、引脚、驱动和部署证据；缺失或冲突时定向核实官方公开原文。"
user-invocable: false
---

# Spacemit Wiki Copilot

按问题直接获取所需证据，复用已加载内容。具体芯片规格、引脚和性能结论必须有资料支持；规则文件中的示例不能替代证据。

## 接入状态

云端与本地 MCP 提供相同的 7 个核心查询工具，按客户端实际可用工具调用；无需在问答前重新安装或探测用户是否下载了整库。Skill 已加载不代表 MCP 已连接。用户请求安装或修复接入时，按 [mcp.md](./mcp.md) 的安装入口处理，默认云端、可选本地，保留用户已选模式；普通问答不自动更改客户端配置。

## 查询流程

1. 明确芯片代际、板型、软硬件版本和任务。已有上下文足够且适用时直接回答。
2. 选择下面的工具；名称不明时先搜索。层级用于组织知识，无需依次读完动线、专题和事实表。
3. 摘要用于定位，具体结论查正文。工具返回后检查证据是否覆盖问题；足够即停。
4. 精炼正文缺失、冲突、过期，或用户要求核实上游时，允许定向查询官方原文；无需先有报错堆栈。
5. 普通问答以 1～3 次调用为目标。额外调用应解决明确缺口，预算不能替代必要核实。

| 需求 | 工具 |
| :--- | :--- |
| 开箱、烧录、构建步骤 | `get_developer_journey` |
| 驱动、外设、设计与部署专题 | `read_knowledge_atom` |
| 引脚、电气、寄存器或性能数据 | `get_evidence_fact` |
| 不确定文档名称 | `search_wiki` |
| 需要查看相关文档 | `get_graph_relations` |
| 精炼证据不足，定位原始文件 | `search_raw_sources` |
| 核实已定位原文 | `read_raw_source_file` |

## 读取与兜底

- 原文默认返回 200 行，显式 `start_line`、`end_line` 范围最多 500 行；按 `has_more`、`next_start_line` 按需续读。MCP 参数以实际 schema 为准；本地大专题按相关章节读取。
- 不整库读取 `Sources/` 或 JSON 索引，不跨 Sources 全盘递归输出搜索结果。先定位文件，再限定范围读取。
- MCP 不可用时，在本地 `Developer_Journeys/`、`Knowledge_Atoms/`、`Evidence/` 定向查找；缺少 Sources 时按已知路径获取 `spacemit-com` 官方 GitHub 仓库同源公开资料。联网失败或资料仍缺失时明确说明。

## 证据与回答

- 区分 K1/K3、芯片规格与板卡实现。引脚接线、供电和实测性能需核对适用版本。
- 引用文档名称或链接及适用条件；保留 `needs_review`、撤回、冲突和过期提示，不能把待审核内容当作已核准事实。
- MoE 模型应同时说明总参数和实际激活参数；速度应带模型、精度、设备和测试条件，不能推导成所有模型的保证。
- 结论先行，参数用于支持结论；不要求每次回答都增加类比或深入阅读邀请。
- 公开回答只使用允许对外公开的资料。问答不自动写库、提交、推送或上报反馈；按用户授权执行维护或反馈操作。

## 按需参考

- [mcp.md](./mcp.md)：配置与参数契约。
- [rules/search-efficiency.md](./rules/search-efficiency.md)：证据升级、范围读取与兜底。
- [rules/generational.md](./rules/generational.md)：代际和模型性能核实。
- [rules/hardware-safety.md](./rules/hardware-safety.md)：涉及接线、供电时核实。
- [rules/system-baseline.md](./rules/system-baseline.md)：涉及系统、固件和 GPIO 时核实。
- [evals/evals.json](./evals/evals.json)：示例问答检查清单，不能作为事实来源或已通过的测试报告。
