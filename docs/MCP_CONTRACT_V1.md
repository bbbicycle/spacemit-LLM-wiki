# Spacemit MCP 接口与联合结果元数据契约 (v1)

> 状态：**已冻结 (Frozen)** · 版本：**v1.0** · 适用阶段：**P0 及后续演进**  
> 关联主计划：[docs/PROJECT_PLAN.md](PROJECT_PLAN.md) · 新鲜度维护：[docs/FRESHNESS_MAINTENANCE.md](FRESHNESS_MAINTENANCE.md)

---

## 1. 契约目标与兼容性原则

本契约作为 Spacemit LLM Wiki 向公司服务器及未来 RAG 体系演进的**最高接口准则**。任何针对 MCP 服务端、网关（Gateway）或底层检索实现的升级，必须严格遵守以下兼容性原则：

1. **客户端零修改原则 (Client Stability)**：
   * 消费端 AI 助手安装的标准 Skill（`spacemit-wiki`）不应因服务器端接入公司 RAG、迁移物理服务器或更新知识内容而被迫更新或修改调用逻辑。
   * **7 大核心 MCP 工具** 的工具名称（`name`）、输入参数字段（`inputSchema`）以及核心响应结构保持长期向后兼容。
2. **渐进增强与版本字段 (Non-breaking Evolution)**：
   * 扩展新能力时，优先通过在现有响应 JSON 中增加非必填可选字段实现，或通过新增独立工具提供，严禁修改已有工具的原生返回语义。
3. **双端平权与解耦 (Transport & Platform Neutral)**：
   * 本契约同时约束本地 Stdio 服务（`mcp/server.py`）、Cloudflare Worker（`mcp-worker/`）以及未来部署于公司内部服务器的集中式 MCP Gateway。
   * 同一份知识图谱发布包在不同运行时上调用相同的工具与参数，必须产生完全一致的结果。

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
* **定位**：按需从本地工作区或官方远程仓库读取原始手册/源码片段。严格执行**安全分页限制**，杜绝大文件打爆 Agent 上下文。
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

## 3. 联合结果元数据契约 (Wiki & 公司 RAG)

为保证未来从纯 Wiki 模式平滑演进至“Wiki 精确层 + 公司 RAG 检索层”混合编排架构，所有查询结果的元数据必须遵循统一的字段契约：

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
| **`verification_status`**| `string` | `"verified"` \| `"unverified"` \| `"conflicted"` | **事实核验状态**。<br>• `verified`：经研发专家人工核验并签署；<br>• `unverified`：AI 自动生成或来源待确认；<br>• `conflicted`：与其它上游或勘误存在明确冲突。 |
| **`freshness`** | `string` | `"current"` \| `"stale"` \| `"unknown"` | **来源文件时效性**。<br>• `current`：引用的源文件在当前最新 commit 无变化；<br>• `stale`：引用的源文件已发生变更，待复核；<br>• `unknown`：无直接声明来源或无法判断。 |
| **`external_use`** | `boolean`| `true` \| `false` | **是否可对外承诺**。为 `false` 的技术事实仅限内部研发参考，严禁作为对外技术规格保证。 |
| **`access_scope`** | `string` | `"public"` \| `"internal"` \| `"restricted"` | **访问权限边界**。<br>• `public`：公开生态资料；<br>• `internal`：公司内部员工可见；<br>• `restricted`：涉密项目受限资料。 |
| **`effective_until`** | `string` | ISO 日期或 `null` | 价格、样片测试等时效性参数的有效期截止日。 |

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
* [x] **向后兼容性已保障**：未来迁移公司服务器或接入 RAG 时，保持 7 大核心工具命名与入参契约不变。
* [x] **联合元数据模型已固化**：明确规定了 `source_kind`、`access_scope` 等跨库编排字段。
