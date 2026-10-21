# 阶段 B 首轮复核与评测记录

执行日期：2026-10-21。基线：`7856b16de70df6e2d494bb09acb93529063c3206`。复核者：Codex，AI 定向来源复核，待人工终审；本轮未编译 SDK、烧录或运行板端模型。

首轮 12 项 diff 复核、7 篇 Journey 补来源、真实查询驱动优化及 20 题工具评测已落地。**阶段 B 本轮来源复核与处置验收完成**：用户于 2026-10-21 明确将两项 K3 Strap 问题标待确定、表示已同步开发并要求继续 B1 验收。两项技术结论仍 conflicted，按[后续勘误记录](k3_strap_pending.json)跟踪，不以阶段验收或 freshness 清零代替官方事实裁决。范围与勾选以 [PROJECT_PLAN.md](../../PROJECT_PLAN.md) 为准。

| 工作项 | 结果与证据 |
| --- | --- |
| B1：12 个 stale | [逐项记录](stale_reviews.json)含新旧 SHA、检查范围、正文结果与依赖检查；[精确 diff](source_diffs.patch)保留两份上游文件的完整差异。12 项均已定向复核，补齐 PMIC→K3 Journey 的入链复核登记；本轮验收与用户明确的延期处置见 [B1 验收记录](b1_acceptance.json)。 |
| B2：7 篇 Journey | [逐篇来源](journey_sources.json)记录固定版本、范围与限制；全部保留 partial / unverified / needs_review，不把来源覆盖当成全文核验。 |
| B3：查询驱动优化 | [首轮分析](query_review.json)、[别名前后真实工具结果](alias_replay.json)、[D1 落库审计](d1_audit.json)与[前](stats_before_audit.html)/[后](stats_after_audit.html)看板快照。 |
| B4：20 题 | [结果表](core_20_results.md)及[逐题 JSON](core_20_results.json)，覆盖 6 个 domain，每端 43 次调用、24 个固定来源片段，逐题 2～3 次。检索证据、固定来源、提示与双端一致性全部通过。 |

固定 Sources：docs-chip `2525ee3b68e0f4864f1bf12c8a59df040bf27e84`；docs-buildroot `163a8fccf8e7071f3177753d2e86e482e97970fe`；docs-product `bc640755145625cc20745f49861f82588863fca3`；docs-ai `2b3894e983a295ed0278bc625867e0c132e0e259`；docs-ros `808d02c1bd11cf0d4376555919bd61c90e38d853`。Sources 正文未修改。

## 实质修正

- K3 摄像输入为 12 Lanes，区分 SoC 总能力与 CoM260 载板引出；修正 CSI2/CSI3 时钟关系，不由物理输入数推导 ISP/AI 并发性能。
- 区分 K1 双 GMAC 与 K3 四 GMAC 的接口模式，保留 USB/PCIe Combo 限制；K3 CPU/DDR 按 V1.1 与 Buglist 合并供电、共用电源平面，不能套用 K1 磁珠通则。
- K3 Strap 追加对照硬件指南与数据手册，保留两类冲突；撤回单方面 SPI 电平结论，并明确下载模式须由 GPIO69 与 GPIO68 共同判断。上游已 fetch 至 `aae85ae4b2071543dfec41b533f97feefc303924`，相关原表未改变，见 [追加复核记录](completion_audit_followup.json)。
- Journey 修正包名、XSlim CLI、Buildroot 最终产物和 ROS 平台/版本条件，移除未确认的通用模型命令与板级性能承诺。
- 真实 `P1 P3 PMIC` 未命中通过补现有专题别名解决；I2C3 反馈转为现有 40Pin 专题中的资料缺口说明，不虚构时序图。评测还纠正 Muse Pi/Pro 旧规格表、板级专题误绑 MUSE Box 来源，以及 GPIO 工具版本的过度推断。

新鲜度由 47 current / 12 stale / 7 unknown 变为 **66 current / 0 stale / 0 unknown**，节点仍为 66（7 Journey、32 Atom、27 Evidence），原文索引仍为 1,231。它只说明已声明路径在该快照可判定；不是全库全文受监控、人工审核通过或性能实测。两篇 K3 Strap 节点保留 `conflicted`，未新增 approved。

## 后续官方勘误与其他开放事项

| 编号 | 事实与当前处理 | 负责人及后续动作 |
| --- | --- | --- |
| K3-STRAP-01（官方勘误待确定） | K3 指南 1.1.5 概述声称 5 脚，含 GPIO90；功能表却含 GPIO64/52、Strap0～5。英文版同样矛盾。K3 数据手册的 4 个 Boot Strap 仅覆盖启动选择，不能据此裁决完整系统配置清单。此外，指南对 GPIO66/65 写 10→SPI NOR、01→SPI NAND；同一固定 SHA 的数据手册 §2.11.2 写 10→SPI NAND、01→SPI NOR。两节点并列原表，不给确定的 SPI 接线或完整管脚清单。 | 用户已与开发同步修改；按明确安排单独跟踪，不阻塞本轮来源复核与处置验收。GitHub 相关原表修订后逐项复核、更新知识/评测并发布；争议接线结论继续待确定。详见 [跟踪记录](k3_strap_pending.json)。 |
| I2C3-TIMING-01 | Pi Pro 用户指南 7.3 确认 Pin27 SDA / Pin28 SCL，但没有该节板级时序、上拉/电容与测量条件。未声称反馈已修复或已关闭。 | 维护者协调板级硬件负责人补资料或实测，绑定板卡版本后再更新。 |
| INTERNAL-MTP-01 | 查询涉及内部采购/培训配置，公开 Wiki 无授权事实来源，保留未知。 | 维护者先确认授权资料、访问范围与负责人；本轮未读取工作区其他内部培训文档。 |
| 其他历史未核验项 | 热学 θJC/PL1/PL2、部分布线值、运行时性能等仍保留原有待核验说明。 | 按后续真实查询定向复核，不视为本轮全文审核范围。 |

## 统计与评测口径

2026-10-21T06:15:38Z 起审计前快照为 44 调用、2 个非成功、1 条 pending 反馈，统计全部保留日志；看板未给最早/最晚时间、会话关联或按路径聚合，不能冒充近 7 天指标、自然用户数或检索回退率。

唯一搜索 `stage-b-d1-audit-2026-10-21` 预期无结果，随后实际出现在看板，计数变为 45/3/1，证明本次查询写入与读取可用。它是人为审计流量，应从真实缺口排除；历史 44 条也无法精确拆分自然用户与旧 smoke。没有发送新反馈，未用假反馈验证写入。

20 题使用生产 Python 与 Worker 核心，无网络评测；原文由当前索引固定版本提供，并与题目所列历史固定 SHA 的片段比较，相关片段变化时要求复核判据。stale/unknown 为[真实 Git 基线节点回放](../../../evals/stage_b_replay_nodes.json)，不修改当前索引。参考答复是 AI 来源复核判据，**未调用独立问答模型，不能称为模型准确率**。

复现：

```bash
python3 -B scripts/eval_stage_b.py
# 结果写入 reports/stage_b/；需完整 Sources、Git 历史及 Node.js 24+
```

已接入部署 CI，结果作为 artifact 保存。每周 30 分钟人工流程见 [维护规范](../../MAINTENANCE.md)；K3 官方勘误的后续检查配置单独记于 [跟踪记录](k3_strap_pending.json)。

## 本地验证

双 lint、26 项构建器测试、6 项上游影响测试、11 项 Python 服务测试、4 项最小安装测试、Worker 运行回归、79 次真实索引跨端调用和状态提示比较、TypeScript、索引 `--check` 与 20 题评测通过。发布 ref、Actions 与线上独立 smoke 另记于 [首轮发布记录](release.json)；[此前追加修正发布记录](release_strap_followup.json)保留当次完整证据；本轮待确认标注与B1验收的发布证据在验证后归档。

追加修正已部署于 `d1b177725a221b77af1208de48310a19819b9580`：[Actions](https://github.com/bbbicycle/spacemit-LLM-wiki/actions/runs/39557662169) 与最小安装检查成功，独立 smoke 和 6 次定向内容查询通过，实读两份原表的固定片段与本地 hash 一致。双端来源为 `11b3b11a446cd313bd5d360471fb0085d2b3d964`，重复构建和索引提交后实际重建字节一致，`wiki_worktree_dirty:false`；该次发布时 B1 尚未验收；本轮按用户后续处置安排的验收见 [B1 记录](b1_acceptance.json)，官方冲突继续保留。
