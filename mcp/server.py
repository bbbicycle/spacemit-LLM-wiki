#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spacemit LLM Wiki - 本地标准 MCP Stdio Server (零依赖，支持 Antigravity / Cursor / Claude Desktop)
基于标准 JSON-RPC 2.0 over Stdio 协议
"""

import sys
import json
import os
import urllib.request

INDEX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "wiki_graph.json")

SYSTEM_INSTRUCTIONS = """
你是 Spacemit 芯片与产品知识库专家，严格遵守以下规范：
1. 知识库采用【线-面-点】三层拓扑：
   - 快速上手/操作通关动线 -> 优先调用 get_developer_journey
   - 芯片外设驱动/技术专题 -> 调用 read_knowledge_atom (整篇无损上下文)
   - 引脚复用/寄存器/电气参数 -> 调用 get_evidence_fact (精准数据表)
   - 上下游依赖关系 -> 调用 get_graph_relations
2. 严禁编造：若精炼原子库中未收录冷门细节，请调用 search_raw_sources 与 read_raw_source_file 穿透查询 1052 篇 Sources 原始手册。
"""

TOOLS = [
    {
        "name": "search_wiki",
        "description": "【精炼层】按关键词、别名或技术领域搜索 Spacemit 提炼知识库，返回最相关的专题/动线/事实节点",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词（如 'Muse Pi', '千兆网', 'K1 Strap', 'PMIC'）"},
                "domain": {"type": "string", "description": "可选的技术领域过滤", "enum": ["chip_product_specs", "hardware_schematic_design", "bsp_kernel_drivers", "bianbu_os_distribution", "toolchain_debug_tools", "edge_ai_robotics"]}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_developer_journey",
        "description": "【动线/线】整篇获取特定硬件板卡或任务的极简上手动线，包含完整通关步骤及引用的专题双链",
        "inputSchema": {
            "type": "object",
            "properties": {
                "board_or_task": {"type": "string", "description": "板卡或任务名称（如 'muse_pi', 'k3_pico', 'buildroot'）"}
            },
            "required": ["board_or_task"]
        }
    },
    {
        "name": "read_knowledge_atom",
        "description": "【专题/面】整篇获取特定技术专题档案（零切片），完整保留原理、配置步骤与技术上下文",
        "inputSchema": {
            "type": "object",
            "properties": {
                "atom_name": {"type": "string", "description": "专题名称或别名（如 '千兆网口', '热设计', 'PMIC电源', 'IOMAP'）"}
            },
            "required": ["atom_name"]
        }
    },
    {
        "name": "get_evidence_fact",
        "description": "【事实/点】获取精准的底层事实数据（引脚映射表、电气参数、Strap配置、寄存器），100% 结构化无截断",
        "inputSchema": {
            "type": "object",
            "properties": {
                "spec_name": {"type": "string", "description": "事实证据名称（如 'k1_strap_pins_config', 'p1_pmic_specs'）"}
            },
            "required": ["spec_name"]
        }
    },
    {
        "name": "get_graph_relations",
        "description": "【图谱拓扑】查询节点的出链（依赖的底层知识）与入链（被哪些上手动线引用），支持顺藤摸瓜探索",
        "inputSchema": {
            "type": "object",
            "properties": {
                "node_name": {"type": "string", "description": "节点名称或别名"}
            },
            "required": ["node_name"]
        }
    },
    {
        "name": "search_raw_sources",
        "description": "【原始资料层】在 1052 篇 Sources 原始芯片手册、驱动文档和板级设计源码清单中搜索，返回匹配文件路径与章节大纲",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词或符号（如 'uart fifo', 'gmac dts', 'dwc3 pcie'）"},
                "submodule": {"type": "string", "description": "可选的子模块过滤", "enum": ["docs-chip", "docs-product", "docs-buildroot", "docs-ai", "docs-ros"]}
            },
            "required": ["query"]
        }
    },
    {
        "name": "read_raw_source_file",
        "description": "【原始资料穿透】从本地或 GitHub 官方仓库按需实时拉取原始 Markdown/源码章节，支持行范围读取",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path_or_url": {"type": "string", "description": "原始文件相对路径（如 'docs-chip/zh/soc/uart.md'）或 raw_url"},
                "start_line": {"type": "number", "description": "可选的起始行号 (1-indexed)"},
                "end_line": {"type": "number", "description": "可选的结束行号"}
            },
            "required": ["file_path_or_url"]
        }
    }
]


class SpacemitMCPServer:
    def __init__(self):
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.nodes = self.data["nodes"]
        self.aliases = self.data["aliases"]
        self.raw_sources = self.data.get("raw_sources", [])

    def resolve_node_id(self, name_or_alias: str):
        query = name_or_alias.strip().lower()
        if query.endswith(".md"):
            query = query[:-3]
        for k in self.nodes:
            if k.lower() == query:
                return k
        if query in self.aliases:
            return self.aliases[query]
        for k, v in self.nodes.items():
            if query in k.lower() or query in v["title"].lower():
                return k
        for alias, node_id in self.aliases.items():
            if query in alias:
                return node_id
        return None

    def handle_tool_call(self, name: str, args: dict):
        if name == "search_wiki":
            q = args.get("query", "").lower()
            domain = args.get("domain")
            results = []
            for node_id, node in self.nodes.items():
                if domain and node.get("domain") != domain:
                    continue
                score = 0
                if q in node["title"].lower() or q in node_id.lower():
                    score += 10
                for a in node.get("aliases", []):
                    if q in a.lower():
                        score += 8
                        break
                if q in node.get("content", "").lower():
                    score += 3
                if score > 0:
                    results.append({
                        "id": node_id,
                        "title": node["title"],
                        "type": node["type"],
                        "domain": node["domain"],
                        "summary": node["summary"][:150] + "..."
                    })
            return {"content": [{"type": "text", "text": json.dumps(results[:5], ensure_ascii=False, indent=2)}]}

        if name == "get_developer_journey":
            node_id = self.resolve_node_id(args.get("board_or_task", ""))
            if not node_id or node_id not in self.nodes:
                return {"isError": True, "content": [{"type": "text", "text": f"未找到相关动线: {args.get('board_or_task')}"}]}
            node = self.nodes[node_id]
            return {"content": [{"type": "text", "text": json.dumps({
                "title": node["title"],
                "type": node["type"],
                "target_audience": node["target_audience"],
                "referenced_atoms": node["outlinks"],
                "full_markdown_content": node["content"]
            }, ensure_ascii=False, indent=2)}]}

        if name == "read_knowledge_atom":
            node_id = self.resolve_node_id(args.get("atom_name", ""))
            if not node_id or node_id not in self.nodes:
                return {"isError": True, "content": [{"type": "text", "text": f"未找到专题档案: {args.get('atom_name')}"}]}
            node = self.nodes[node_id]
            return {"content": [{"type": "text", "text": json.dumps({
                "title": node["title"],
                "domain": node["domain"],
                "status": node["status"],
                "referenced_evidence": node["outlinks"],
                "full_markdown_content": node["content"]
            }, ensure_ascii=False, indent=2)}]}

        if name == "get_evidence_fact":
            node_id = self.resolve_node_id(args.get("spec_name", ""))
            if not node_id or node_id not in self.nodes:
                return {"isError": True, "content": [{"type": "text", "text": f"未找到事实数据: {args.get('spec_name')}"}]}
            node = self.nodes[node_id]
            return {"content": [{"type": "text", "text": json.dumps({
                "title": node["title"],
                "type": "evidence",
                "full_table_content": node["content"]
            }, ensure_ascii=False, indent=2)}]}

        if name == "get_graph_relations":
            node_id = self.resolve_node_id(args.get("node_name", ""))
            if not node_id or node_id not in self.nodes:
                return {"isError": True, "content": [{"type": "text", "text": f"未找到节点: {args.get('node_name')}"}]}
            node = self.nodes[node_id]
            return {"content": [{"type": "text", "text": json.dumps({
                "node_id": node_id,
                "title": node["title"],
                "type": node["type"],
                "outlinks": [{"id": o, "title": self.nodes[o]["title"], "type": self.nodes[o]["type"]} for o in node["outlinks"] if o in self.nodes],
                "backlinks": [{"id": b, "title": self.nodes[b]["title"], "type": self.nodes[b]["type"]} for b in node["backlinks"] if b in self.nodes]
            }, ensure_ascii=False, indent=2)}]}

        if name == "search_raw_sources":
            q = args.get("query", "").lower()
            sub = args.get("submodule")
            matches = []
            for item in self.raw_sources:
                if sub and item["submodule"] != sub:
                    continue
                score = 0
                if q in item["title"].lower() or q in item["file_name"].lower():
                    score += 10
                if q in item["rel_path"].lower():
                    score += 6
                for h in item["headers"]:
                    if q in h.lower():
                        score += 5
                        break
                if q in item.get("summary", "").lower():
                    score += 2
                if score > 0:
                    matches.append({
                        "submodule": item["submodule"],
                        "file_path": item["rel_path"],
                        "title": item["title"],
                        "headers": item["headers"],
                        "raw_url": item["raw_url"]
                    })
            return {"content": [{"type": "text", "text": json.dumps(matches[:8], ensure_ascii=False, indent=2)}]}

        if name == "read_raw_source_file":
            target = args.get("file_path_or_url", "")
            clean_path = target.replace("Sources/", "")
            local_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Sources", clean_path)
            lines = []
            if os.path.exists(local_path):
                with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.read().splitlines()
            else:
                target_url = target
                if not target_url.startswith("http"):
                    for s in self.raw_sources:
                        if s["rel_path"] == clean_path or s["rel_path"].endswith(clean_path):
                            target_url = s["raw_url"]
                            break
                try:
                    req = urllib.request.Request(target_url, headers={"User-Agent": "Spacemit-MCP"})
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        lines = resp.read().decode("utf-8").splitlines()
                except Exception as e:
                    return {"isError": True, "content": [{"type": "text", "text": f"无法读取源文件: {e}"}]}

            start = max(1, args.get("start_line", 1)) - 1
            end = min(len(lines), args["end_line"]) if "end_line" in args and args["end_line"] else len(lines)
            return {"content": [{"type": "text", "text": f"[Source: {target}]\n\n" + "\n".join(lines[start:end])}]}

        return {"isError": True, "content": [{"type": "text", "text": f"未知工具: {name}"}]}

    def run(self):
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except Exception:
                continue

            msg_id = msg.get("id")
            method = msg.get("method")
            params = msg.get("params", {})

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "spacemit-wiki-mcp", "version": "2.0.0"},
                        "instructions": SYSTEM_INSTRUCTIONS
                    }
                }
                sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"tools": TOOLS}
                }
                sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()
            elif method == "tools/call":
                res = self.handle_tool_call(params.get("name", ""), params.get("arguments", {}))
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": res
                }
                sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()
            elif method == "notifications/initialized":
                pass
            elif msg_id is not None:
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": "Method not found"}
                }
                sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    server = SpacemitMCPServer()
    server.run()
