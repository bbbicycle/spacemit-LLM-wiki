/**
 * Spacemit LLM Wiki - Cloudflare Worker 生产级 MCP Server (v2.3 自解释知识服务)
 * 严格遵循 MCP 官方标准 SSE 协议与 Agent.md 规范
 * 
 * 核心功能：
 * 1. 双层知识图谱与原始 Sources 穿透检索 (8 大 MCP Tools)
 * 2. 接入 Cloudflare D1 数据库：自动记录问题种类、热门词云与【错误/未命中盲区】
 * 3. 开放可视化数据统计与错误反馈看板：GET /stats
 */

import wikiData from "./data/wiki_graph.json";

export interface Env {
  DB?: D1Database;
  DEPLOYMENT_REF?: string;
}

export interface ExecutionContext {
  waitUntil(promise: Promise<any>): void;
  passThroughOnException(): void;
}

interface WikiNode {
  id: string;
  title: string;
  type: string;
  domain: string;
  status: string;
  aliases: string[];
  target_audience: string[];
  outlinks: string[];
  backlinks: string[];
  summary: string;
  content: string;
  freshness?: string;
  verification_status?: string;
  stale_paths?: string[];
  unknown_paths?: string[];
  external_use?: boolean;
}

interface RawSourceItem {
  submodule: string;
  file_name: string;
  rel_path: string;
  repo_path: string;
  title: string;
  headers: string[];
  summary: string;
  raw_url: string;
  source_commit?: string;
}

const nodes = wikiData.nodes as Record<string, WikiNode>;
const rawSources = (wikiData.raw_sources || []) as RawSourceItem[];

const SYSTEM_INSTRUCTIONS = `
你是 Spacemit 芯片与产品知识库专家，严格遵守以下规范：
1. 知识库采用【线-面-点】三层拓扑：
   - 快速上手/操作通关动线 -> 优先调用 get_developer_journey
   - 芯片外设驱动/技术专题 -> 调用 read_knowledge_atom (整篇无损上下文)
   - 引脚复用/寄存器/电气参数 -> 调用 get_evidence_fact (精准数据表)
   - 上下游依赖关系 -> 调用 get_graph_relations
2. 复用已加载且仍适用的证据；名称不明确时先 search_wiki，不强制逐层遍历。摘要仅供定位，具体结论需正文支持。
3. 缺失、冲突、过期或用户要求复核时，可 search_raw_sources 后 read_raw_source_file，默认返回 200 行，显式范围最多 500 行；按 has_more / next_start_line 续读。
4. 普通问答以 1～3 次调用为目标；核心结论及关键参数已有支持即可停止，必要核实可继续。
5. 区分芯片代际、板型和版本，引用来源并保留待审核/撤回/过期状态；verification_status 非 verified 时不得称为已核验；needs_review 表示尚未人工审核，deprecated 表示不作当前有效依据；来源已定位不等于事实已核验。freshness:current 仅表示已声明文件未变化，stale 需要复核，unknown 表示无法判断。external_use:false 的内容不得用于对外承诺。未知不猜测，歧义时使用候选的精确 ID。
6. 遵循节点 agent_notice 和搜索 hint；原文读取索引固定版本，不代表实时上游。问答不自动写库或上报反馈；反馈须由用户授权。
`;

const DEFAULT_RAW_LINES = 200;
const MAX_RAW_LINES = 500;

const TOOLS = [
  {
    name: "search_wiki",
    description: "【精炼层】按关键词、别名或技术领域搜索 Spacemit 提炼知识库，返回最相关的专题/动线/事实节点",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "搜索关键词（如 'Muse Pi', '千兆网', 'K1 Strap', 'PMIC'）" },
        domain: { type: "string", description: "可选的技术领域过滤", enum: ["chip_product_specs", "hardware_schematic_design", "bsp_kernel_drivers", "bianbu_os_distribution", "toolchain_debug_tools", "edge_ai_robotics"] }
      },
      required: ["query"]
    }
  },
  {
    name: "get_developer_journey",
    description: "【动线/线】整篇获取特定硬件板卡或任务的极简上手动线，包含完整通关步骤及引用的专题双链",
    inputSchema: {
      type: "object",
      properties: {
        board_or_task: { type: "string", description: "板卡或任务名称（如 'muse_pi', 'k3_pico', 'buildroot'）" }
      },
      required: ["board_or_task"]
    }
  },
  {
    name: "read_knowledge_atom",
    description: "【专题/面】整篇获取特定技术专题档案（零切片），完整保留原理、配置步骤与技术上下文",
    inputSchema: {
      type: "object",
      properties: {
        atom_name: { type: "string", description: "专题名称或别名（如 '千兆网口', '热设计', 'PMIC电源', 'IOMAP'）" }
      },
      required: ["atom_name"]
    }
  },
  {
    name: "get_evidence_fact",
    description: "【事实/点】获取精准的底层事实数据（引脚映射表、电气参数、Strap配置、寄存器），100% 结构化无截断",
    inputSchema: {
      type: "object",
      properties: {
        spec_name: { type: "string", description: "事实证据名称（如 'k1_strap_pins_config', 'p1_pmic_specs'）" }
      },
      required: ["spec_name"]
    }
  },
  {
    name: "get_graph_relations",
    description: "【图谱拓扑】查询节点的出链（依赖的底层知识）与入链（被哪些上手动线引用），支持顺藤摸瓜探索",
    inputSchema: {
      type: "object",
      properties: {
        node_name: { type: "string", description: "节点名称或别名" }
      },
      required: ["node_name"]
    }
  },
  {
    name: "search_raw_sources",
    description: "【原始资料层】搜索 Sources 原始芯片手册、驱动文档和板级设计清单，返回匹配文件路径与章节大纲",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "搜索关键词或符号（如 'uart fifo', 'gmac dts', 'dwc3 pcie'）" },
        submodule: { type: "string", description: "可选的子模块过滤", enum: ["docs-chip", "docs-product", "docs-buildroot", "docs-ai", "docs-ros"] }
      },
      required: ["query"]
    }
  },
  {
    name: "read_raw_source_file",
    description: "【原始资料穿透】从 GitHub 读取已索引的原始资料，默认读取 200 行，显式范围最多 500 行，返回续读位置",
    inputSchema: {
      type: "object",
      properties: {
        file_path_or_url: { type: "string", description: "原始文件相对路径（如 'docs-chip/zh/soc/uart.md'）或 raw_url" },
        start_line: { type: "integer", minimum: 1, description: "起始行号，默认 1" },
        end_line: { type: "integer", minimum: 1, description: "包含在内的结束行号，省略则读取 200 行，单次最多 500 行" }
      },
      required: ["file_path_or_url"]
    }
  },
  {
    name: "report_wiki_issue",
    description: "【错误与盲区反馈】向 Spacemit 知识库维护者提交文档错误、参数存疑或缺失的知识盲区，记录至云端数据库",
    inputSchema: {
      type: "object",
      properties: {
        topic: { type: "string", description: "涉及的板卡、芯片或技术主题（如 'Muse Pi', 'K1 PMIC'）" },
        issue_type: { type: "string", description: "问题分类", enum: ["MISSING_DOC", "INCORRECT_SPEC", "BROKEN_LINK", "SUGGESTION"] },
        description: { type: "string", description: "具体问题描述或希望补充的技术细节" }
      },
      required: ["topic", "description"]
    }
  }
];

const activeSessions = new Map<string, (data: string) => void>();

function requiredText(value: unknown, label: string): string {
  if (typeof value !== "string" || !value.trim()) throw new Error(`${label} 必须是非空字符串`);
  return value.trim();
}

function resolveNodeId(nameOrAlias: string, expectedType?: string): string | null {
  let q = requiredText(nameOrAlias, "节点名称").toLowerCase();
  if (q.endsWith(".md")) q = q.slice(0, -3);
  requiredText(q, "节点名称");
  const entries = Object.entries(nodes);
  const exactIds = entries.filter(([id]) => id.toLowerCase() === q);
  const exact = exactIds.length ? exactIds : entries.filter(([, node]) => node.title.toLowerCase() === q || (node.aliases || []).some(a => a.toLowerCase() === q));
  let candidates = exact.length ? exact : entries.filter(([id, node]) => id.toLowerCase().includes(q) || node.title.toLowerCase().includes(q) || (node.aliases || []).some(a => a.toLowerCase().includes(q)));
  if (exact.length && expectedType && !exact.some(([, node]) => node.type === expectedType)) {
    throw new Error(`节点类型不匹配，需要 ${expectedType}；请使用对应工具读取 ${exact[0][0]}`);
  }
  candidates = candidates.filter(([, node]) => !expectedType || node.type === expectedType);
  if (candidates.length > 1) {
    const choices = candidates.slice(0, 8).map(([id, node]) => ({ id, title: node.title, type: node.type }));
    throw new Error(`匹配多个节点，请确认芯片/产品并使用精确 ID：${JSON.stringify(choices)}`);
  }
  return candidates[0]?.[0] || null;
}

function resolveRawSource(target: string): RawSourceItem {
  const cleanPath = target.replace(/^Sources\//, "");
  let matches = rawSources.filter(item => item.rel_path === cleanPath || item.raw_url === target);
  if (!matches.length && target.startsWith("https://")) {
    const url = new URL(target);
    if (url.host === "raw.githubusercontent.com" && !url.search && !url.hash) {
      const path = decodeURIComponent(url.pathname);
      matches = rawSources.filter(item => path === `/spacemit-com/${item.submodule}/main/${item.repo_path}` || path === decodeURIComponent(new URL(item.raw_url).pathname));
    }
  }
  if (matches.length !== 1) throw new Error("源文件不在已索引清单中；请先 search_raw_sources 并使用返回的完整 file_path 或 raw_url");
  return matches[0];
}

function rawReadOptions(args: any) {
  for (const key of ["start_line", "end_line"]) {
    if (key in args && (!Number.isSafeInteger(args[key]) || args[key] < 1)) throw new Error(`${key} 必须是正整数`);
  }
  const options = { start_line: args.start_line ?? 1, end_line: args.end_line };
  if (options.end_line !== undefined && options.end_line < options.start_line) throw new Error("end_line 不得小于 start_line");
  options.end_line = Math.min(options.end_line ?? options.start_line + DEFAULT_RAW_LINES - 1, options.start_line + MAX_RAW_LINES - 1);
  return options;
}

function nodeMetadata(node: WikiNode) {
  const fields = ["id", "type", "status", "verification_status", "external_use", "publication", "source_file", "source_commit", "source_section", "source_locator", "source_resolution", "source_note", "source_checked_at", "source_related_file", "source_related_commit", "freshness", "stale_paths", "unknown_paths", "checked_against_commit", "source_freshness", "metric_source_resolution", "thermal_source_resolution", "chip", "product", "verified_at", "conflicts", "source_origin", "source_tier", "effective_until", "superseded_by", "updated"];
  return Object.fromEntries(fields.filter(field => field in node).map(field => [field, (node as any)[field]]));
}

interface AgentNotice {
  code: string;
  message: string;
  source_paths?: string[];
}

function buildAgentNotice(node: WikiNode): AgentNotice[] {
  const notices: AgentNotice[] = [];
  const add = (code: string, message: string, paths?: string[]) => {
    notices.push({ code, message, ...(paths !== undefined ? { source_paths: paths } : {}) });
  };
  const freshness = node.freshness ?? "unknown";
  if (freshness === "stale") {
    add("STALE", "声明来源在历史版本与索引固定快照之间已变化；用 read_raw_source_file 核对固定版本原文，说明节点待复核。实时上游需维护者另行同步核查。", node.stale_paths ?? []);
  } else if (freshness === "unknown") {
    add("UNKNOWN", "来源覆盖不完整或历史版本无法判断；核对 source_freshness 与原文，明确证据缺口，不能声称内容最新或已经核验。", node.unknown_paths ?? []);
  }
  const verification = node.verification_status ?? "unverified";
  if (verification === "conflicted") {
    add("CONFLICTED", "来源存在冲突；并列原始依据与适用版本，保留冲突说明，不自行择一或掩盖差异。");
  } else if (verification !== "verified") {
    add("UNVERIFIED", "事实尚未完成核验；引用具体来源并说明待复核，不表述为已审定结论。");
  }
  if (node.status === "needs_review") {
    add("NEEDS_REVIEW", "文档待人工终审；事实核验与人工批准独立，current 或 verified 均不代表 approved。");
  }
  if (node.status === "deprecated") {
    add("DEPRECATED", "文档已废弃或撤回；保留历史与替代来源，不作为当前有效依据。");
  }
  if (node.external_use === false) {
    add("EXTERNAL_USE_RESTRICTED", "此条目不能用于对外事实承诺；访问公开资料不等于规格已获批准。");
  }
  if (["chip_product_specs", "hardware_schematic_design", "edge_ai_robotics"].includes(node.domain)) {
    add("GENERATION_BOUNDARY", "参数绑定来源注明的芯片代际、板型与软硬件版本；接线前核对引脚、供电和电平，性能需保留测试条件，严禁跨产品套用。");
  }
  return notices;
}

function searchHint(node: WikiNode): string {
  return buildAgentNotice(node).map(notice => notice.code).join(" / ") || "按来源与适用版本核对正文。";
}

// Match the builder's UTF-8 JSON (sort_keys=True, default separators). Sorting
// by code point also agrees for supplementary Unicode characters in aliases.
function canonicalJson(value: any): string {
  if (Array.isArray(value)) return "[" + value.map(canonicalJson).join(", ") + "]";
  if (value !== null && typeof value === "object") {
    const keys = Object.keys(value).sort((a, b) => {
      const left = Array.from(a, c => c.codePointAt(0)!);
      const right = Array.from(b, c => c.codePointAt(0)!);
      for (let i = 0; i < Math.min(left.length, right.length); i++) {
        if (left[i] !== right[i]) return left[i] - right[i];
      }
      return left.length - right.length;
    });
    return "{" + keys.map(key => JSON.stringify(key) + ": " + canonicalJson(value[key])).join(", ") + "}";
  }
  return JSON.stringify(value);
}

async function validateLoadedIndex(): Promise<boolean> {
  const data: any = wikiData;
  const meta = data.build_meta;
  const sha = (value: unknown) => typeof value === "string" && /^(?:[a-f0-9]{40}|[a-f0-9]{64})$/.test(value);
  if (!meta || !sha(data.wiki_commit) || !/^[a-f0-9]{64}$/.test(data.content_sha256 ?? "")) return false;
  if (!data.nodes || !Array.isArray(data.raw_sources) || !data.aliases || !data.source_versions) return false;
  if (canonicalJson(Object.keys(data.source_versions).sort()) !== canonicalJson(
    ["docs-ai", "docs-buildroot", "docs-chip", "docs-product", "docs-ros"])) return false;
  if (!Object.values(data.source_versions).every(sha)) return false;
  const entries = Object.values(data.nodes) as WikiNode[];
  if (!entries.length || !data.raw_sources.length) return false;
  const counts = {
    total_nodes: entries.length,
    developer_journeys: entries.filter(n => n.type === "developer_journey").length,
    knowledge_atoms: entries.filter(n => n.type === "knowledge_atom").length,
    evidence: entries.filter(n => n.type === "evidence").length,
    raw_sources: data.raw_sources.length,
  };
  const freshness = Object.fromEntries(["current", "stale", "unknown"].map(state =>
    [state, entries.filter(n => n.freshness === state).length]));
  if (counts.total_nodes !== counts.developer_journeys + counts.knowledge_atoms + counts.evidence ||
      counts.total_nodes !== freshness.current + freshness.stale + freshness.unknown ||
      data.total_nodes !== counts.total_nodes || data.total_raw_sources !== counts.raw_sources) return false;
  if (canonicalJson(meta.counts) !== canonicalJson(counts) ||
      canonicalJson(meta.freshness_summary) !== canonicalJson(freshness) ||
      canonicalJson(meta.sources_commits) !== canonicalJson(data.source_versions)) return false;
  if (["wiki_commit", "generated_at", "wiki_worktree_dirty", "content_sha256"].some(key => meta[key] !== data[key])) return false;
  if (typeof data.wiki_worktree_dirty !== "boolean" || !Number.isFinite(Date.parse(data.generated_at))) return false;
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(canonicalJson({
    nodes: data.nodes, raw_sources: data.raw_sources,
  })));
  return Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, "0")).join("") === data.content_sha256;
}

let loadedIndexValidation: Promise<boolean> | undefined;

// 自动识别问题技术分类
function categorizeQuery(toolName: string, queryStr: string): string {
  const q = (queryStr || "").toLowerCase();
  if (toolName === "get_developer_journey" || q.includes("上手") || q.includes("动线") || q.includes("quickstart")) return "开发板上手动线";
  if (q.includes("pin") || q.includes("引脚") || q.includes("iomap") || q.includes("strap") || q.includes("电路") || q.includes("pcb")) return "硬件引脚与电路设计";
  if (q.includes("gmac") || q.includes("网口") || q.includes("uart") || q.includes("dts") || q.includes("驱动") || q.includes("kernel") || q.includes("buildroot")) return "BSP与内核驱动";
  if (q.includes("pmic") || q.includes("电源") || q.includes("功耗") || q.includes("热设计") || q.includes("散")) return "电源与热设计";
  if (q.includes("ai") || q.includes("量化") || q.includes("llm") || q.includes("ros") || q.includes("模型")) return "端侧AI与机器人";
  if (toolName === "search_raw_sources" || toolName === "read_raw_source_file") return "原始手册源码穿透";
  return "综合技术查询";
}

// 记录到 D1 数据库
async function logQueryToD1(env: Env, log: {
  tool_name: string;
  query_text: string;
  category: string;
  status: string;
  matched_id?: string;
  error_message?: string;
  country?: string;
  city?: string;
}) {
  if (!env.DB) return;
  try {
    await env.DB.prepare(
      `INSERT INTO mcp_query_logs (tool_name, query_text, category, status, matched_id, error_message, client_country, client_city)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(
      log.tool_name,
      log.query_text || "",
      log.category,
      log.status,
      log.matched_id || "",
      log.error_message || "",
      log.country || "Unknown",
      log.city || "Unknown"
    ).run();
  } catch (err) {
    console.error("D1 log error:", err);
  }
}

function recordQueryLog(env: Env, log: Parameters<typeof logQueryToD1>[1], ctx?: ExecutionContext) {
  const p = logQueryToD1(env, log);
  if (ctx && typeof ctx.waitUntil === "function") {
    ctx.waitUntil(p);
  }
}


async function handleToolCall(name: string, args: any, env: Env, cfData?: any, ctx?: ExecutionContext) {
  let status = "SUCCESS";
  let matchedId = "";
  let errorMsg = "";
  const queryStr = JSON.stringify(args);
  const category = categorizeQuery(name, queryStr);

  try {
    if (!args || typeof args !== "object" || Array.isArray(args)) throw new Error("工具参数必须是对象");
    if (name === "search_wiki") {
      const q = requiredText(args.query, "query").toLowerCase();
      const domain = args.domain;
      const results = [];

      for (const [nodeId, node] of Object.entries(nodes)) {
        if (domain && node.domain !== domain) continue;
        let score = 0;
        if (node.title.toLowerCase().includes(q) || nodeId.toLowerCase().includes(q)) score += 10;
        for (const a of node.aliases || []) {
          if (a.toLowerCase().includes(q)) { score += 8; break; }
        }
        if (node.content.toLowerCase().includes(q)) score += 3;

        if (score > 0) {
          results.push({
            ...nodeMetadata(node),
            score,
            id: nodeId,
            title: node.title,
            type: node.type,
            domain: node.domain,
            summary: Array.from(node.summary).slice(0, 150).join("") + "...",
            hint: searchHint(node)
          });
        }
      }

      results.sort((a, b) => b.score - a.score);
      if (results.length === 0) {
        status = "MISS_NO_RESULT"; // 标记为未命中盲区
      } else {
        matchedId = results[0].id;
      }

      recordQueryLog(env, { tool_name: name, query_text: args.query, category, status, matched_id: matchedId, country: cfData?.country, city: cfData?.city }, ctx);
      return { content: [{ type: "text", text: JSON.stringify(results.slice(0, 5), null, 2) }] };
    }

    if (name === "get_developer_journey") {
      const nodeId = resolveNodeId(args.board_or_task, "developer_journey");
      if (!nodeId || !nodes[nodeId]) {
        status = "MISS_NO_RESULT";
        recordQueryLog(env, { tool_name: name, query_text: args.board_or_task, category, status, error_message: "未找到动线", country: cfData?.country, city: cfData?.city }, ctx);
        return { isError: true, content: [{ type: "text", text: `未找到相关动线: ${args.board_or_task}` }] };
      }
      const node = nodes[nodeId];
      matchedId = nodeId;
      recordQueryLog(env, { tool_name: name, query_text: args.board_or_task, category, status, matched_id: matchedId, country: cfData?.country, city: cfData?.city }, ctx);
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            ...nodeMetadata(node),
            title: node.title,
            type: node.type,
            target_audience: node.target_audience,
            referenced_atoms: node.outlinks,
            agent_notice: buildAgentNotice(node),
            full_markdown_content: node.content
          }, null, 2)
        }]
      };
    }

    if (name === "read_knowledge_atom") {
      const nodeId = resolveNodeId(args.atom_name, "knowledge_atom");
      if (!nodeId || !nodes[nodeId]) {
        status = "MISS_NO_RESULT";
        recordQueryLog(env, { tool_name: name, query_text: args.atom_name, category, status, error_message: "未找到专题", country: cfData?.country, city: cfData?.city }, ctx);
        return { isError: true, content: [{ type: "text", text: `未找到专题档案: ${args.atom_name}` }] };
      }
      const node = nodes[nodeId];
      matchedId = nodeId;
      recordQueryLog(env, { tool_name: name, query_text: args.atom_name, category, status, matched_id: matchedId, country: cfData?.country, city: cfData?.city }, ctx);
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            ...nodeMetadata(node),
            title: node.title,
            domain: node.domain,
            status: node.status,
            referenced_evidence: node.outlinks,
            agent_notice: buildAgentNotice(node),
            full_markdown_content: node.content
          }, null, 2)
        }]
      };
    }

    if (name === "get_evidence_fact") {
      const nodeId = resolveNodeId(args.spec_name, "evidence");
      if (!nodeId || !nodes[nodeId]) {
        status = "MISS_NO_RESULT";
        recordQueryLog(env, { tool_name: name, query_text: args.spec_name, category, status, error_message: "未找到事实数据", country: cfData?.country, city: cfData?.city }, ctx);
        return { isError: true, content: [{ type: "text", text: `未找到事实数据: ${args.spec_name}` }] };
      }
      const node = nodes[nodeId];
      matchedId = nodeId;
      recordQueryLog(env, { tool_name: name, query_text: args.spec_name, category, status, matched_id: matchedId, country: cfData?.country, city: cfData?.city }, ctx);
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            ...nodeMetadata(node),
            title: node.title,
            type: node.type,
            agent_notice: buildAgentNotice(node),
            full_table_content: node.content
          }, null, 2)
        }]
      };
    }

    if (name === "get_graph_relations") {
      const nodeId = resolveNodeId(args.node_name || "");
      if (!nodeId || !nodes[nodeId]) {
        status = "MISS_NO_RESULT";
        recordQueryLog(env, { tool_name: name, query_text: args.node_name, category, status, error_message: "未找到节点", country: cfData?.country, city: cfData?.city }, ctx);
        return { isError: true, content: [{ type: "text", text: `未找到节点: ${args.node_name}` }] };
      }
      const node = nodes[nodeId];
      matchedId = nodeId;
      recordQueryLog(env, { tool_name: name, query_text: args.node_name, category, status, matched_id: matchedId, country: cfData?.country, city: cfData?.city }, ctx);
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            ...nodeMetadata(node),
            node_id: nodeId,
            title: node.title,
            type: node.type,
            outlinks: node.outlinks.filter(o => nodes[o]).map(o => ({ id: o, title: nodes[o].title, type: nodes[o].type })),
            backlinks: node.backlinks.filter(b => nodes[b]).map(b => ({ id: b, title: nodes[b].title, type: nodes[b].type }))
          }, null, 2)
        }]
      };
    }

    if (name === "search_raw_sources") {
      const q = requiredText(args.query, "query").toLowerCase();
      const sub = args.submodule;
      const matches = [];

      for (const item of rawSources) {
        if (sub && item.submodule !== sub) continue;
        let score = 0;
        if (item.title.toLowerCase().includes(q) || item.file_name.toLowerCase().includes(q)) score += 10;
        if (item.rel_path.toLowerCase().includes(q)) score += 6;
        for (const h of item.headers) {
          if (h.toLowerCase().includes(q)) { score += 5; break; }
        }
        if (item.summary.toLowerCase().includes(q)) score += 2;

        if (score > 0) {
          matches.push({
            score,
            submodule: item.submodule,
            file_path: item.rel_path,
            title: item.title,
            headers: item.headers,
            source_commit: item.source_commit ?? null,
            raw_url: item.raw_url
          });
        }
      }

      matches.sort((a, b) => b.score - a.score);
      if (matches.length === 0) status = "MISS_NO_RESULT";
      else matchedId = matches[0].file_path;

      recordQueryLog(env, { tool_name: name, query_text: args.query, category, status, matched_id: matchedId, country: cfData?.country, city: cfData?.city }, ctx);
      return { content: [{ type: "text", text: JSON.stringify(matches.slice(0, 8), null, 2) }] };
    }

    if (name === "read_raw_source_file") {
      const target = requiredText(args.file_path_or_url, "file_path_or_url");
      const options = rawReadOptions(args);
      const item = resolveRawSource(target);
      const targetUrl = new URL(item.raw_url).href;

      try {
        const resp = await fetch(targetUrl, {
          headers: { "User-Agent": "Spacemit-MCP-Worker" }
        });
        if (!resp.ok) {
          status = "ERROR";
          errorMsg = `HTTP ${resp.status}`;
          recordQueryLog(env, { tool_name: name, query_text: args.file_path_or_url, category, status, error_message: errorMsg, country: cfData?.country, city: cfData?.city }, ctx);
          return { isError: true, content: [{ type: "text", text: `无法从 GitHub 获取源文件 (${resp.status}): ${targetUrl}` }] };
        }
        const rawText = await resp.text();
        const lines = rawText === "" ? [] : rawText.split(/\r\n|[\n\r\v\f\x1c-\x1e\x85\u2028\u2029]/);
        if (lines.length && lines[lines.length - 1] === "") lines.pop();
        const start = options.start_line - 1;
        const end = Math.min(lines.length, options.end_line);
        const hasMore = end < lines.length;

        matchedId = targetUrl;
        recordQueryLog(env, { tool_name: name, query_text: args.file_path_or_url, category, status, matched_id: matchedId, country: cfData?.country, city: cfData?.city }, ctx);
        return {
          content: [{
            type: "text",
            text: JSON.stringify({ source: item.raw_url, source_commit: item.source_commit ?? null,
              origin: "github", total_lines: lines.length, start_line: start + 1,
              end_line: end, has_more: hasMore, next_start_line: hasMore ? end + 1 : null, content: lines.slice(start, end).join("\n") }, null, 2)
          }]
        };
      } catch (e: any) {
        status = "ERROR";
        errorMsg = e.message;
        recordQueryLog(env, { tool_name: name, query_text: args.file_path_or_url, category, status, error_message: errorMsg, country: cfData?.country, city: cfData?.city }, ctx);
        return { isError: true, content: [{ type: "text", text: `请求 GitHub 失败: ${e.message}` }] };
      }
    }

    // 8. report_wiki_issue (主动反馈)
    if (name === "report_wiki_issue") {
      const topic = args.topic || "General";
      const issueType = args.issue_type || "MISSING_DOC";
      const desc = args.description || "";

      if (env.DB) {
        const issuePromise = env.DB.prepare(
          `INSERT INTO mcp_issue_reports (topic, issue_type, description, reported_by) VALUES (?, ?, ?, 'developer_ai')`
        ).bind(topic, issueType, desc).run().catch(err => console.error("D1 issue report error:", err));
        if (ctx && typeof ctx.waitUntil === "function") {
          ctx.waitUntil(issuePromise);
        } else {
          await issuePromise;
        }
      }

      recordQueryLog(env, { tool_name: name, query_text: `${topic}: ${desc}`, category: "错误与反馈提交", status: "SUCCESS", country: cfData?.country, city: cfData?.city }, ctx);
      return {
        content: [{
          type: "text",
          text: `✅ 感谢反馈！关于【${topic}】的问题已成功记录至 Spacemit 知识库维护后台，管理员将进行核实与补充。`
        }]
      };
    }

    return { isError: true, content: [{ type: "text", text: `未知工具: ${name}` }] };
  } catch (globalErr: any) {
    recordQueryLog(env, { tool_name: name, query_text: queryStr, category, status: "ERROR", error_message: globalErr.message, country: cfData?.country, city: cfData?.city }, ctx);
    return { isError: true, content: [{ type: "text", text: `执行异常: ${globalErr.message}` }] };
  }
}

async function handleJsonRpc(body: any, env: Env, cfData?: any, ctx?: ExecutionContext): Promise<any> {
  const { jsonrpc, id, method, params } = body;
  if (method === "initialize") {
    return {
      jsonrpc: "2.0",
      id,
      result: {
        protocolVersion: "2024-11-05",
        capabilities: { tools: {} },
        serverInfo: { name: "spacemit-wiki-mcp", version: wikiData.version },
        instructions: SYSTEM_INSTRUCTIONS
      }
    };
  }
  if (method === "tools/list") {
    return {
      jsonrpc: "2.0",
      id,
      result: { tools: TOOLS }
    };
  }
  if (method === "tools/call") {
    const result = await handleToolCall(params.name, params.arguments || {}, env, cfData, ctx);
    return {
      jsonrpc: "2.0",
      id,
      result
    };
  }
  if (method === "notifications/initialized" || method === "notifications/cancelled") {
    return null;
  }
  if (method === "ping") {
    return { jsonrpc: "2.0", id, result: {} };
  }
  return {
    jsonrpc: "2.0",
    id,
    error: { code: -32601, message: "Method not found" }
  };
}

// 渲染可视化统计与错误监控看板 (/stats)
async function renderStatsDashboard(env: Env): Promise<Response> {
  if (!env.DB) {
    return new Response(`
      <html><head><meta charset="utf-8"><title>Spacemit MCP Stats</title></head>
      <body style="font-family: sans-serif; padding: 40px; text-align: center;">
        <h2>📊 Spacemit MCP 监控看板</h2>
        <p style="color: #666;">Cloudflare D1 数据库尚未绑定。绑定后即可查看实时问题统计与错误盲区监控。</p>
      </body></html>
    `, { headers: { "Content-Type": "text/html; charset=utf-8" } });
  }

  // 1. 统计总数与成功率
  const totalQueries = await env.DB.prepare("SELECT COUNT(*) as count FROM mcp_query_logs").first<any>();
  const missCount = await env.DB.prepare("SELECT COUNT(*) as count FROM mcp_query_logs WHERE status != 'SUCCESS'").first<any>();
  const pendingIssues = await env.DB.prepare("SELECT COUNT(*) as count FROM mcp_issue_reports WHERE status = 'pending'").first<any>();

  // 2. 分类占比 Top
  const categories = await env.DB.prepare(
    "SELECT category, COUNT(*) as count FROM mcp_query_logs GROUP BY category ORDER BY count DESC LIMIT 6"
  ).all<any>();

  // 3. 错误与未命中盲区 Top 10 (核心价值)
  const missedQueries = await env.DB.prepare(
    "SELECT query_text, tool_name, status, error_message, timestamp FROM mcp_query_logs WHERE status != 'SUCCESS' ORDER BY id DESC LIMIT 15"
  ).all<any>();

  // 4. 用户/AI 主动反馈列表
  const issues = await env.DB.prepare(
    "SELECT topic, issue_type, description, timestamp FROM mcp_issue_reports ORDER BY id DESC LIMIT 10"
  ).all<any>();

  const html = `
  <!DOCTYPE html>
  <html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spacemit LLM Wiki - MCP 查询分析与错误盲区看板</title>
    <style>
      :root { --primary: #2563eb; --danger: #dc2626; --warning: #d97706; --bg: #f8fafc; --card: #ffffff; }
      body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: #1e293b; margin: 0; padding: 24px; }
      .container { max-width: 1100px; margin: 0 auto; }
      .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
      .title { font-size: 24px; font-weight: bold; color: #0f172a; }
      .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }
      .card { background: var(--card); border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
      .metric-value { font-size: 32px; font-weight: bold; margin-top: 8px; }
      .metric-title { font-size: 14px; color: #64748b; font-weight: 500; }
      .section-title { font-size: 18px; font-weight: bold; margin: 24px 0 12px; display: flex; align-items: center; gap: 8px; }
      table { width: 100%; border-collapse: collapse; background: var(--card); border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
      th, td { padding: 12px 16px; text-align: left; font-size: 14px; border-bottom: 1px solid #f1f5f9; }
      th { background: #f8fafc; color: #475569; font-weight: 600; }
      .tag { display: inline-block; padding: 3px 8px; border-radius: 6px; font-size: 12px; font-weight: 500; }
      .tag-miss { background: #fee2e2; color: #991b1b; }
      .tag-error { background: #fef3c7; color: #92400e; }
      .tag-cat { background: #e0f2fe; color: #0369a1; }
      .footer { margin-top: 40px; text-align: center; font-size: 13px; color: #94a3b8; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <div>
          <div class="title">🚀 Spacemit LLM Wiki - MCP 实时监控与错误反馈</div>
          <div style="color: #64748b; font-size: 14px; margin-top: 4px;">双层知识图谱 (mcp.yao1302.xyz) 运行分析</div>
        </div>
        <div style="font-size: 13px; background: #dcfce7; color: #166534; padding: 6px 12px; border-radius: 20px; font-weight: 600;">● 服务在线</div>
      </div>

      <div class="grid">
        <div class="card">
          <div class="metric-title">总查询调用次数</div>
          <div class="metric-value" style="color: var(--primary);">${totalQueries?.count || 0}</div>
        </div>
        <div class="card">
          <div class="metric-title">错误与未命中盲区数</div>
          <div class="metric-value" style="color: var(--danger);">${missCount?.count || 0}</div>
        </div>
        <div class="card">
          <div class="metric-title">待处理反馈与纠错</div>
          <div class="metric-value" style="color: var(--warning);">${pendingIssues?.count || 0}</div>
        </div>
      </div>

      <div class="section-title">📊 咨询问题分类热度分布</div>
      <table>
        <thead><tr><th>问题分类领域</th><th>咨询占比 / 次数</th></tr></thead>
        <tbody>
          ${(categories.results || []).map((c: any) => `
            <tr>
              <td><span class="tag tag-cat">${c.category}</span></td>
              <td><strong>${c.count}</strong> 次</td>
            </tr>
          `).join('') || '<tr><td colspan="2" style="text-align:center; color:#94a3b8;">暂无数据</td></tr>'}
        </tbody>
      </table>

      <div class="section-title" style="color: #b91c1c;">🚨 错误与未命中盲区记录 (知识库反哺依据)</div>
      <table>
        <thead><tr><th>时间</th><th>搜索关键词 / 目标</th><th>调用工具</th><th>状态与原因</th></tr></thead>
        <tbody>
          ${(missedQueries.results || []).map((m: any) => `
            <tr>
              <td style="color:#64748b;">${m.timestamp}</td>
              <td><code>${m.query_text || '无参数'}</code></td>
              <td>${m.tool_name}</td>
              <td><span class="tag ${m.status === 'ERROR' ? 'tag-error' : 'tag-miss'}">${m.status}: ${m.error_message || '无搜索结果'}</span></td>
            </tr>
          `).join('') || '<tr><td colspan="4" style="text-align:center; color:#94a3b8;">暂无错误记录，知识库运行良好！</td></tr>'}
        </tbody>
      </table>

      <div class="section-title" style="color: #0369a1;">💡 开发者与 AI 主动上报的反馈/纠错</div>
      <table>
        <thead><tr><th>时间</th><th>主题</th><th>分类</th><th>具体反馈内容</th></tr></thead>
        <tbody>
          ${(issues.results || []).map((i: any) => `
            <tr>
              <td style="color:#64748b;">${i.timestamp}</td>
              <td><strong>${i.topic}</strong></td>
              <td><span class="tag tag-cat">${i.issue_type}</span></td>
              <td>${i.description}</td>
            </tr>
          `).join('') || '<tr><td colspan="4" style="text-align:center; color:#94a3b8;">暂无主动反馈记录</td></tr>'}
        </tbody>
      </table>

      <div class="footer">Spacemit LLM Wiki · Powered by Cloudflare Workers & D1</div>
    </div>
  </body>
  </html>
  `;

  return new Response(html, {
    headers: { "Content-Type": "text/html; charset=utf-8" }
  });
}

export default {
  async fetch(request: Request, env: Env, ctx?: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    const cf = (request as any).cf;

    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
      "Access-Control-Max-Age": "86400"
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    if (url.pathname === "/health") {
      const headers = { ...corsHeaders, "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" };
      if (request.method !== "GET") return new Response(JSON.stringify({ error: "Method not allowed" }), {
        status: 405, headers: { ...headers, Allow: "GET, OPTIONS" },
      });
      // The bundled index is immutable for this Worker version. Validate once;
      // health is index readiness, not an assertion that D1 writes succeeded.
      loadedIndexValidation ??= validateLoadedIndex().catch(() => false);
      const valid = await loadedIndexValidation;
      return new Response(JSON.stringify({
        status: valid ? "ok" : "error",
        service: "spacemit-wiki-mcp",
        version: wikiData.version,
        build_meta: (wikiData as any).build_meta ?? null,
        deployment_ref: env.DEPLOYMENT_REF ?? null,
        d1_bound: !!env.DB,
        ...(!valid ? { error: "Loaded index failed validation" } : {}),
      }), { status: valid ? 200 : 503, headers });
    }

    // 访问可视化监控看板 /stats
    if (url.pathname === "/stats") {
      return renderStatsDashboard(env);
    }

    // 1. GET /sse：建立标准 SSE 长连接
    if (url.pathname === "/sse" || url.pathname === "/") {
      if (request.method === "GET") {
        const sessionId = crypto.randomUUID();
        const { readable, writable } = new TransformStream();
        const writer = writable.getWriter();
        const encoder = new TextEncoder();

        const sendEvent = (event: string, data: string) => {
          try {
            writer.write(encoder.encode(`event: ${event}\ndata: ${data}\n\n`));
          } catch (_) {}
        };

        activeSessions.set(sessionId, (payload: string) => {
          sendEvent("message", payload);
        });

        const endpointUrl = `${url.origin}/messages?sessionId=${sessionId}`;
        sendEvent("endpoint", endpointUrl);

        const keepAliveInterval = setInterval(() => {
          sendEvent("ping", "{}");
        }, 30000);

        request.signal.addEventListener("abort", () => {
          clearInterval(keepAliveInterval);
          activeSessions.delete(sessionId);
          try { writer.close(); } catch (_) {}
        });

        return new Response(readable, {
          headers: {
            ...corsHeaders,
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive"
          }
        });
      }
    }

    // 2. POST /messages 或 POST /：处理客户端发来的 JSON-RPC 请求
    if (request.method === "POST") {
      const sessionId = url.searchParams.get("sessionId") || "";
      try {
        const body = await request.json();
        const responseData = await handleJsonRpc(body, env, cf, ctx);

        if (responseData) {
          const stringified = JSON.stringify(responseData);
          const sseSender = activeSessions.get(sessionId);
          if (sseSender) {
            sseSender(stringified);
          }
          return new Response(stringified, {
            headers: {
              ...corsHeaders,
              "Content-Type": "application/json"
            }
          });
        }
        return new Response(null, { status: 202, headers: corsHeaders });
      } catch (err: any) {
        return new Response(JSON.stringify({ jsonrpc: "2.0", error: { code: -32700, message: "Parse error" } }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      }
    }

    return new Response(`Spacemit LLM Wiki MCP Server ${wikiData.version} is running! Health: /health, Stats: /stats, SSE: /sse`, {
      headers: { ...corsHeaders, "Content-Type": "text/plain; charset=utf-8" }
    });
  }
};
