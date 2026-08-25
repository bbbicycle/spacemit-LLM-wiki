/**
 * Spacemit LLM Wiki - Cloudflare Worker MCP Server (v2.0 双层知识图谱架构)
 * 严格遵循 Agent.md 规范与 Anthropic MCP 协议
 * 
 * 核心设计：
 * 1. 精炼知识图谱层 (60 篇)：Journeys (线) -> Atoms (面) -> Evidence (点) 零切片直出
 * 2. 原始资料源清单层 (1052 篇)：Sources/docs-* 动态穿透至 GitHub Raw 实时拉取
 */

import wikiData from "./data/wiki_graph.json";

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
}

const nodes = wikiData.nodes as Record<string, WikiNode>;
const aliases = wikiData.aliases as Record<string, string>;
const rawSources = (wikiData.raw_sources || []) as RawSourceItem[];

const SYSTEM_INSTRUCTIONS = `
你是 Spacemit 芯片与产品知识库专家，严格遵守以下规范：
1. 知识库采用【线-面-点】三层拓扑：
   - 快速上手/操作通关动线 -> 优先调用 get_developer_journey
   - 芯片外设驱动/技术专题 -> 调用 read_knowledge_atom (整篇无损上下文)
   - 引脚复用/寄存器/电气参数 -> 调用 get_evidence_fact (精准数据表)
   - 上下游依赖关系 -> 调用 get_graph_relations
2. 严禁编造：若精炼原子库中未收录冷门细节，请调用 search_raw_sources 与 read_raw_source_file 穿透查询 1052 篇 Sources 原始芯片与产品手册。
`;

// 工具定义列表 (MCP Specification)
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
    description: "【原始资料层】在 1052 篇 Sources 原始芯片手册、驱动文档和板级设计源码清单中搜索，返回匹配文件路径与章节大纲",
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
    description: "【原始资料穿透】从 GitHub 官方仓库按需实时拉取原始 Markdown/源码章节，支持行范围读取",
    inputSchema: {
      type: "object",
      properties: {
        file_path_or_url: { type: "string", description: "原始文件相对路径（如 'docs-chip/zh/soc/uart.md'）或 raw_url" },
        start_line: { type: "number", description: "可选的起始行号 (1-indexed)" },
        end_line: { type: "number", description: "可选的结束行号" }
      },
      required: ["file_path_or_url"]
    }
  }
];

function resolveNodeId(nameOrAlias: string): string | null {
  let q = nameOrAlias.trim().toLowerCase();
  if (q.endsWith(".md")) q = q.slice(0, -3);

  for (const k of Object.keys(nodes)) {
    if (k.toLowerCase() === q) return k;
  }
  if (aliases[q]) return aliases[q];

  for (const [k, v] of Object.entries(nodes)) {
    if (k.toLowerCase().includes(q) || v.title.toLowerCase().includes(q)) return k;
  }
  for (const [alias, nodeId] of Object.entries(aliases)) {
    if (alias.includes(q)) return nodeId;
  }
  return null;
}

async function handleToolCall(name: string, args: any) {
  // 1. search_wiki
  if (name === "search_wiki") {
    const q = (args.query || "").toLowerCase();
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
          id: nodeId,
          title: node.title,
          type: node.type,
          domain: node.domain,
          summary: node.summary.slice(0, 150) + "..."
        });
      }
    }
    return { content: [{ type: "text", text: JSON.stringify(results.slice(0, 5), null, 2) }] };
  }

  // 2. get_developer_journey
  if (name === "get_developer_journey") {
    const nodeId = resolveNodeId(args.board_or_task || "");
    if (!nodeId || !nodes[nodeId]) return { isError: true, content: [{ type: "text", text: `未找到相关动线: ${args.board_or_task}` }] };
    const node = nodes[nodeId];
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          title: node.title,
          type: node.type,
          target_audience: node.target_audience,
          referenced_atoms: node.outlinks,
          full_markdown_content: node.content
        }, null, 2)
      }]
    };
  }

  // 3. read_knowledge_atom
  if (name === "read_knowledge_atom") {
    const nodeId = resolveNodeId(args.atom_name || "");
    if (!nodeId || !nodes[nodeId]) return { isError: true, content: [{ type: "text", text: `未找到专题档案: ${args.atom_name}` }] };
    const node = nodes[nodeId];
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          title: node.title,
          domain: node.domain,
          status: node.status,
          referenced_evidence: node.outlinks,
          full_markdown_content: node.content
        }, null, 2)
      }]
    };
  }

  // 4. get_evidence_fact
  if (name === "get_evidence_fact") {
    const nodeId = resolveNodeId(args.spec_name || "");
    if (!nodeId || !nodes[nodeId]) return { isError: true, content: [{ type: "text", text: `未找到事实数据: ${args.spec_name}` }] };
    const node = nodes[nodeId];
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          title: node.title,
          type: "evidence",
          full_table_content: node.content
        }, null, 2)
      }]
    };
  }

  // 5. get_graph_relations
  if (name === "get_graph_relations") {
    const nodeId = resolveNodeId(args.node_name || "");
    if (!nodeId || !nodes[nodeId]) return { isError: true, content: [{ type: "text", text: `未找到节点: ${args.node_name}` }] };
    const node = nodes[nodeId];
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          node_id: nodeId,
          title: node.title,
          type: node.type,
          outlinks: node.outlinks.filter(o => nodes[o]).map(o => ({ id: o, title: nodes[o].title, type: nodes[o].type })),
          backlinks: node.backlinks.filter(b => nodes[b]).map(b => ({ id: b, title: nodes[b].title, type: nodes[b].type }))
        }, null, 2)
      }]
    };
  }

  // 6. search_raw_sources (新增)
  if (name === "search_raw_sources") {
    const q = (args.query || "").toLowerCase();
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
          submodule: item.submodule,
          file_path: item.rel_path,
          title: item.title,
          headers: item.headers,
          raw_url: item.raw_url
        });
      }
    }
    return { content: [{ type: "text", text: JSON.stringify(matches.slice(0, 8), null, 2) }] };
  }

  // 7. read_raw_source_file (新增：按需从 GitHub Raw 实时读取)
  if (name === "read_raw_source_file") {
    let targetUrl = args.file_path_or_url || "";
    if (!targetUrl.startsWith("http")) {
      // 路径转换
      const cleanPath = targetUrl.replace(/^Sources\//, "");
      const matched = rawSources.find(s => s.rel_path === cleanPath || s.rel_path.endsWith(cleanPath));
      if (matched) {
        targetUrl = matched.raw_url;
      } else {
        const parts = cleanPath.split("/");
        const sub = parts[0];
        const rest = parts.slice(1).join("/");
        targetUrl = `https://raw.githubusercontent.com/spacemit-com/${sub}/main/${rest}`;
      }
    }

    try {
      const resp = await fetch(targetUrl, {
        headers: { "User-Agent": "Spacemit-MCP-Worker" }
      });
      if (!resp.ok) {
        return { isError: true, content: [{ type: "text", text: `无法从 GitHub 获取源文件 (${resp.status}): ${targetUrl}` }] };
      }
      const rawText = await resp.text();
      let lines = rawText.split("\n");

      if (args.start_line || args.end_line) {
        const start = Math.max(1, args.start_line || 1) - 1;
        const end = args.end_line ? Math.min(lines.length, args.end_line) : lines.length;
        lines = lines.slice(start, end);
      }

      return {
        content: [{
          type: "text",
          text: `[Source: ${targetUrl}]\n\n` + lines.join("\n")
        }]
      };
    } catch (e: any) {
      return { isError: true, content: [{ type: "text", text: `请求 GitHub 失败: ${e.message}` }] };
    }
  }

  return { isError: true, content: [{ type: "text", text: `未知工具: ${name}` }] };
}

// JSON-RPC 消息分发器
async function handleJsonRpc(body: any): Promise<any> {
  const { jsonrpc, id, method, params } = body;
  if (method === "initialize") {
    return {
      jsonrpc: "2.0",
      id,
      result: {
        protocolVersion: "2024-11-05",
        capabilities: { tools: {} },
        serverInfo: { name: "spacemit-wiki-mcp", version: "2.0.0" },
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
    const result = await handleToolCall(params.name, params.arguments || {});
    return {
      jsonrpc: "2.0",
      id,
      result
    };
  }
  if (method === "notifications/initialized") {
    return null;
  }
  return {
    jsonrpc: "2.0",
    id,
    error: { code: -32601, message: "Method not found" }
  };
}

export default {
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);

    // 跨域处理 (CORS)
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type"
        }
      });
    }

    // 1. SSE 模式 (用于 Claude Desktop / Cursor 连接)
    if (url.pathname === "/sse" || url.pathname === "/") {
      if (request.method === "GET") {
        const { readable, writable } = new TransformStream();
        const writer = writable.getWriter();
        const encoder = new TextEncoder();

        writer.write(encoder.encode(`event: endpoint\ndata: ${url.origin}/messages\n\n`));

        return new Response(readable, {
          headers: {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
          }
        });
      }
    }

    // 2. HTTP POST JSON-RPC 消息处理
    if (request.method === "POST") {
      try {
        const body = await request.json();
        const responseData = await handleJsonRpc(body);
        if (!responseData) {
          return new Response(null, { status: 204 });
        }
        return new Response(JSON.stringify(responseData), {
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
          }
        });
      } catch (err: any) {
        return new Response(JSON.stringify({ jsonrpc: "2.0", error: { code: -32700, message: "Parse error" } }), {
          status: 400,
          headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
        });
      }
    }

    return new Response("Spacemit LLM Wiki MCP Server v2.0 is running! Endpoint: /sse or POST /", {
      headers: { "Content-Type": "text/plain; charset=utf-8" }
    });
  }
};
