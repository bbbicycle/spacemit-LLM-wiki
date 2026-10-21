# Spacemit MCP 接口与联合结果元数据契约 (v1)

> 状态：**7 核心工具兼容契约与目标元数据模型已冻结** · 版本：**v1.0** · 更新：**2026-10-21**
> 关联主计划：[docs/PROJECT_PLAN.md](PROJECT_PLAN.md) · 新鲜度维护：[docs/FRESHNESS_MAINTENANCE.md](FRESHNESS_MAINTENANCE.md)

冻结的是工具语义与演进边界，不表示未来字段均已实现。阶段 A 的 `build_meta`、`/health`、`agent_notice` / `hint` 与轻量 Skill v1 已完成并通过部署验收；线上以健康接口验证，阶段 B 首轮复核、查询优化与 20 题工具评测已落地，B1 按 2026-10-21 用户安排完成来源复核与处置验收，两项 K3 Strap 官方勘误单独跟踪、技术结论仍待确定，工具契约未扩展。

---

## 1. 契约目标与兼容性原则

本契约作为 Spacemit LLM Wiki 向公司服务器及未来 RAG 体系演进的**最高接口准则**。任何针对 MCP 服务端、网关（Gateway）或底层检索实现的升级，必须严格遵守以下兼容性原则：

1. **客户端零修改原则 (Client Stability)**：
   * 消费端 AI 助手安装的标准 Skill（`spacemit-wiki`）不应因服务器端接入公司 RAG、迁移物理服务器或更新知识内容而被迫更新或修改调用逻辑。
   * **7 大核心 MCP 工具** 的工具名称（`name`）、输入参数字段（`inputSchema`）以及核心响应结构保持长期向后兼容。
2. **渐进增强与版本字段 (Non-breaking Evolution)**：
   * 扩展新能力时，优先通过在现有响应 JSON 中增加非必填可选字段实现，或通过新增独立工具提供，严禁修改已有工具的原生返回语义。
3. **核心工具契约一致与运行职责分离**：
   * 本契约同时约束本地 Stdio 服务（`mcp/server.py`）、Cloudflare Worker（`mcp-worker/`）以及未来部署于公司内部服务器的集中式 MCP Gateway。
   * Worker 是生产端；Python 是纯标准库的 7 核心工具契约镜像，用于精炼知识离线查询和 CI，不复制 D1 日志、反馈与 HTTP 运维端点。
   * 使用同一 Git 版本的索引时，相同核心调用的正文、来源版本、核验状态、分页和错误语义应一致。原文 `origin` 可因本地读取或 GitHub 获取而不同；不要求运行环境字段逐字相同。
   * 索引继续由 Git 管理，不要求独立 `wiki-release/<version>` 发布包。回退需要重新部署目标 ref 并核对线上版本，不能以本地 Git revert 代替。

---

## 2. 7 大核心 MCP 工具规范

所有运行时必须完整实现以下 7 个核心工具。

### 2.1 精炼知识层工具

#### 1. `search_wiki`（关键词与领域搜索）
* **定位**：检索提炼知识图谱（动线、专题、事实），获取高相关性候选节点列表。
* **参数**：
  ```json
  {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "搜索关键词（如 'Muse Pi', '千兆网', 'K1 Strap', 'PMIC'）" },
      "domain": {
        "type": "string",
        "description": "可选的技术领域过滤",
        "enum": [
          "chip_product_specs",
          "hardware_schematic_design",
          "bsp_kernel_drivers",
          "bianbu_os_distribution",
          "toolchain_debug_tools",
          "edge_ai_robotics"
        ]
      }
    },
    "required": ["query"]
  }
  ```
* **响应格式**：返回得分 Top 5 的节点数组，每个节点包含基础信息、摘要及元数据。

#### 2. `get_developer_journey`（上手动线整篇读取）
* **定位**：获取特定开发板或任务的极简上手向导（线），包含任务顺序、关键步骤及专题双链。
* **参数**：
  ```json
  {
    "type": "object",
    "properties": {
      "board_or_task": { "type": "string", "description": "板卡或任务名称（如 'muse_pi', 'k3_pico', 'buildroot'）" }
    },
    "required": ["board_or_task"]
  }
  ```
* **响应格式**：返回包含 `title`、`type: "developer_journey"`、`target_audience`、`referenced_atoms` 以及完整 Markdown 正文 `full_markdown_content` 的 JSON。

#### 3. `read_knowledge_atom`（专题档案零切片读取）
* **定位**：获取特定软硬件技术专题的完整档案（面），零切片保留设计原理、避坑指南与底层事实双链。
* **参数**：
  ```json
  {
    "type": "object",
    "properties": {
      "atom_name": { "type": "string", "description": "专题名称或别名（如 '千兆网口', '热设计', 'PMIC电源', 'IOMAP'）" }
    },
    "required": ["atom_name"]
  }
  ```
* **响应格式**：返回包含 `title`、`domain`、`status`、`referenced_evidence` 以及完整专题 Markdown `full_markdown_content` 的 JSON。

#### 4. `get_evidence_fact`（结构化数据事实读取）
* **定位**：获取底层物理事实、Strap 配置、引脚映射表、电气参数与 AVL 物料表（点），100% 结构化无截断。
* **参数**：
  ```json
  {
    "type": "object",
    "properties": {
      "spec_name": { "type": "string", "description": "事实证据名称（如 'k1_strap_pins_config', 'p1_pmic_specs'）" }
    },
    "required": ["spec_name"]
  }
  ```
* **响应格式**：返回包含 `title`、`type: "evidence"`、`status` 以及完整无损表格内容 `full_table_content` 的 JSON。

#### 5. `get_graph_relations`（图谱拓扑依赖探测）
* **定位**：查询指定节点的底层依赖（出链 outlinks）与被引用场景（入链 backlinks），支持顺藤摸瓜。
* **参数**：
  ```json
  {
    "type": "object",
    "properties": {
      "node_name": { "type": "string", "description": "节点名称或别名" }
    },
    "required": ["node_name"]
  }
  ```
* **响应格式**：返回包含当前节点元数据、`outlinks` 数组（依赖的下层节点）以及 `backlinks` 数组（上层引用节点）的 JSON。

---

### 2.2 原始资料层工具（Sources 穿透）

#### 6. `search_raw_sources`（原始手册检索）
* **定位**：在 5 大官方子模块（`docs-chip`, `docs-product`, `docs-buildroot`, `docs-ai`, `docs-ros`）中搜索原始文件路径与章节大纲。
* **参数**：
  ```json
  {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "搜索关键词或符号（如 'uart fifo', 'gmac dts', 'dwc3 pcie'）" },
      "submodule": {
        "type": "string",
        "description": "可选的子模块过滤",
        "enum": ["docs-chip", "docs-product", "docs-buildroot", "docs-ai", "docs-ros"]
      }
    },
    "required": ["query"]
  }
  ```
* **响应格式**：返回匹配度 Top 8 的原始文件清单（含相对路径、固定 `source_commit`、章节标题与 `raw_url`）。

#### 7. `read_raw_source_file`（安全分页原文穿透）
* **定位**：按索引固定 `source_commit` 从匹配版本的本地工作区或官方远程仓库读取原始手册/源码片段，不追踪实时 `main`。严格执行**安全分页限制**，杜绝大文件打爆 Agent 上下文。
* **参数**：
  ```json
  {
    "type": "object",
    "properties": {
      "file_path_or_url": { "type": "string", "description": "原始文件相对路径（如 'docs-chip/zh/soc/uart.md'）或 raw_url" },
      "start_line": { "type": "integer", "minimum": 1, "description": "起始行号，默认 1" },
      "end_line": { "type": "integer", "minimum": 1, "description": "包含在内的结束行号，默认读取 200 行，单次显式请求最多 500 行" }
    },
    "required": ["file_path_or_url"]
  }
  ```
* **安全分页约束**：
  * 默认读取窗口为 **200 行**；单次请求最大跨度限制为 **500 行**；
  * `end_line` 小于 `start_line` 必须抛出错误；超出实际行数时自动夹止于 EOF；
  * 响应必须显式包含分页指示：
    ```json
    {
      "source": "https://raw.githubusercontent.com/...",
      "source_commit": "15254b1cfe339c1863d8edf8137a337681fb2780",
      "origin": "local|github",
      "total_lines": 420,
      "start_line": 1,
      "end_line": 200,
      "has_more": true,
      "next_start_line": 201,
      "content": "..."
    }
    ```

---

### 2.3 Worker 运营扩展与反馈边界

Worker 目前另有 `/stats`、异步 D1 查询日志和 `report_wiki_issue`；它们不属于 7 核心检索工具的跨端必选能力。

`report_wiki_issue` 的必填参数为 `topic`、`description`，可选 `issue_type` 枚举为 `MISSING_DOC / INCORRECT_SPEC / BROKEN_LINK / SUGGESTION`（省略时当前默认 `MISSING_DOC`）。这是向维护者发送反馈的写操作，必须有用户明确授权；发现缺口时先诚实说明，不能自动上报。当前采用异步尽力写入，返回接受信息不能证明 D1 已成功持久化，也不表示问题已经核实或修复。

只读查询指不改写知识库或用户文件、不触发提交推送；Worker 可记录查询日志。Worker `/health` 的 `d1_bound` 仅表示绑定存在，不能代替实际数据库可用性检查。

---

## 3. 联合结果元数据契约 (Wiki & 公司 RAG)

以下是面向未来“Wiki 精确层 + 公司 RAG 检索层”的**目标模型**，供 Gateway 兼容扩展时遵循，不能当作当前每个工具已返回的字段清单。

当前精炼节点已按存在性透传 `id / type / status / verification_status / external_use`、来源路径/SHA/定位/检查日期、`freshness / stale_paths / unknown_paths / checked_against_commit / source_freshness` 等字段；原文查询返回文件路径、固定来源 SHA 和分页信息。`source_kind / source_id / source_version / access_scope` 尚未在当前两端统一提供。未来补齐时使用可选字段或适配层，保留原字段兼容，不要求客户端提前依赖它们。

目标示例：

```json
{
  "source_kind": "wiki",
  "source_id": "k1_strap_pins_config",
  "source_version": "1ea15a766287024a5bb7b548850826e3525a80dc",
  "verification_status": "unverified",
  "freshness": "current",
  "external_use": false,
  "access_scope": "public",
  "effective_until": null
}
```

### 3.1 字段枚举与语义规范

| 字段名 | 类型 | 取值范围 / 枚举 | 语义约束与解释 |
| :--- | :--- | :--- | :--- |
| **`source_kind`** | `string` | `"wiki"` \| `"company_rag"` \| `"raw_source"` | **证据来源种类**。<br>• `wiki`：官方提炼精炼层；<br>• `company_rag`：公司内部资料/项目记录；<br>• `raw_source`：官方只读手册源码。 |
| **`source_id`** | `string` | 字符串 | 节点唯一 ID、文件相对路径或企业文档唯一索引标识。 |
| **`source_version`** | `string` | Commit SHA / 版本号 | 证据所基于的数据版本快照，支持完整溯源。 |
| **`verification_status`**| `string` | `"verified"` \| `"unverified"` \| `"conflicted"` | **事实核验状态**。<br>• `verified`：已对声明范围的事实与来源进行复核，有对应记录；<br>• `unverified`：事实尚未完成复核或依据不足；<br>• `conflicted`：来源或勘误存在明确冲突。此字段不等于人工批准 `status: approved`。 |
| **`freshness`** | `string` | `"current"` \| `"stale"` \| `"unknown"` | **声明来源文件的快照差异**。<br>• `current`：历史来源与本次构建固定的 Sources 快照之间无差异；<br>• `stale`：声明文件发生变更，待复核；<br>• `unknown`：无直接声明来源或无法判断。不代表实时上游或全文事实正确性。 |
| **`external_use`** | `boolean`| `true` \| `false` | **是否可用于对外事实承诺**。为 `false` 时不得作为对外技术规格保证；公开待核验资料仍可按权限访问并说明限制，此字段不等于 `access_scope: internal`。 |
| **`access_scope`** | `string` | `"public"` \| `"internal"` \| `"restricted"` | **访问权限边界**。<br>• `public`：公开生态资料；<br>• `internal`：公司内部员工可见；<br>• `restricted`：涉密项目受限资料。 |
| **`effective_until`** | `string` | ISO 日期或 `null` | 价格、样片测试等时效性参数的有效期截止日。 |

`source_resolution` 记录出处是否定位，`verification_status` 记录事实核验，`status` 记录文档审批，三者独立。`publication` / visibility 等现有公共索引过滤规则继续生效；不能用 `external_use` 代替访问控制。

未来 Gateway 在重排及进入回答上下文前执行 ACL。来源裁决结合产品、版本、权威性和授权勘误，不使用 Wiki 永远覆盖 RAG 的全局优先级；无法裁决时并列来源和冲突。

---

## 4. 四方责任矩阵 (RACI)

为保证知识库从本地个人维护走向企业级生产运营，明确各角色的权责边界：

| 职责环节 | Wiki 维护者 (你/核心维护者) | 公司服务器维护者 (运维/平台) | 公司 RAG 维护者 (AI/数据团队) | 客户端用户 (工程师/开发者) |
| :--- | :---: | :---: | :---: | :---: |
| **目标架构与规范制定** | **Accountable (主导)** | Consulted (协商) | Consulted (协商) | Informed (知晓) |
| **精炼知识编写与双链拓扑**| **Responsible (执行)** | Informed (知晓) | Informed (知晓) | Consulted (反馈需求) |
| **上游子模块同步与 Freshness 审计**| **Responsible (执行)** | Informed (知晓) | Informed (知晓) | Informed (知晓) |
| **MCP Gateway 部署与高可用监控**| Consulted (协助) | **Accountable (主导)** | Responsible (配合) | Informed (使用) |
| **公司内部资料向量化与 ACL 权限** | Informed (知晓) | Consulted (鉴权) | **Accountable (主导)** | Informed (知晓) |
| **混合检索编排与来源冲突裁决**| **Responsible (Wiki侧)**| Informed (知晓) | **Responsible (RAG侧)**| Consulted (提交盲区) |
| **Skill 安装与客户端查询合规**| Consulted (指引) | Informed (知晓) | Informed (知晓) | **Responsible (执行)** |

---

## 5. 验收与状态确认

* [x] **数据流边界已清晰**：官方资料 $\rightarrow$ Wiki 精炼图谱 $\rightarrow$ MCP 查询 $\rightarrow$ Agent 决策闭环已完成定义。
* [x] **向后兼容边界已定义**：未来迁移公司服务器或接入 RAG 时，保持 7 大核心工具命名、入参与核心语义。
* [x] **联合目标模型已固化**：明确 `source_kind`、`access_scope` 等跨库编排字段，当前实现情况见第 3 节。
* [x] **阶段 A 扩展实现**：确定性 `build_meta`、Worker `/health`、双端节点 `agent_notice` 与搜索 `hint`，兼容现有响应；Skill 瘦身与安装验收。
* [ ] **公司 Gateway 接入**：P4/P5 条件就绪后再实现 HTTP/SSE 承载、认证、联合字段与 ACL，不随本契约文档更新宣称上线。


## 6. 阶段 A 兼容扩展（v2.3.0）

三个精炼正文工具新增可选 `agent_notice` 数组，每项包含稳定 `code`、中文 `message` 及可选 `source_paths`；搜索新增短 `hint`，继续返回原有状态与来源。原正文、参数与分页语义不变，提示不替代证据。

提示 code：`STALE / UNKNOWN / CONFLICTED / UNVERIFIED / NEEDS_REVIEW / DEPRECATED / EXTERNAL_USE_RESTRICTED / GENERATION_BOUNDARY`。同一节点可同时包含多个提醒；`current + needs_review` 仍须提示待终审，`conflicted` 不能被普通待核验提醒盖掉。两端对相同节点生成相同结构。

`GET /health` 是 Worker 运营接口：索引完整性通过返回 200/`ok`，失败返回 503/`error`；响应含索引 `version / build_meta`、可选部署配置 `deployment_ref`（未配置为 null）及 `d1_bound`。`build_meta` 与顶层构建字段一致，聚合 counts、freshness、五份 Sources SHA 和内容哈希。构建来源 SHA/时间由最近一次输入提交确定，实际部署 ref 单独记录；详见 [维护规范](MAINTENANCE.md)。这不扩展 Python 的 7 核心工具清单，不宣称联合 Gateway 字段已经落地。
