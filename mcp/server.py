#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spacemit LLM Wiki - 本地标准 MCP Stdio Server (零依赖，支持 Antigravity / Cursor / Claude Desktop)
基于标准 JSON-RPC 2.0 over Stdio 协议
"""

import sys
import json
import os
import subprocess
import urllib.parse
import urllib.request

INDEX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "wiki_graph.json")

SYSTEM_INSTRUCTIONS = """
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
6. 问答不自动写库或上报反馈；反馈须由用户授权。
"""

DEFAULT_RAW_LINES = 200
MAX_RAW_LINES = 500

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
        "description": "【原始资料层】搜索 Sources 原始芯片手册、驱动文档和板级设计清单，返回匹配文件路径与章节大纲",
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
        "description": "【原始资料穿透】从本地或 GitHub 读取已索引的原始资料，默认读取 200 行，显式范围最多 500 行，返回续读位置",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path_or_url": {"type": "string", "description": "原始文件相对路径（如 'docs-chip/zh/soc/uart.md'）或 raw_url"},
                "start_line": {"type": "integer", "minimum": 1, "description": "起始行号，默认 1"},
                "end_line": {"type": "integer", "minimum": 1, "description": "包含在内的结束行号，省略则读取 200 行，单次最多 500 行"}
            },
            "required": ["file_path_or_url"]
        }
    }
]


def required_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} 必须是非空字符串")
    return value.strip()


def raw_read_options(args):
    values = {}
    for name in ("start_line", "end_line"):
        if name in args:
            value = args[name]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not value >= 1 or value > 9007199254740991 or int(value) != value:
                raise ValueError(f"{name} 必须是正整数")
            values[name] = int(value)
    values.setdefault("start_line", 1)
    if values.get("end_line", values["start_line"]) < values["start_line"]:
        raise ValueError("end_line 不得小于 start_line")
    values.setdefault("end_line", values["start_line"] + DEFAULT_RAW_LINES - 1)
    values["end_line"] = min(values["end_line"], values["start_line"] + MAX_RAW_LINES - 1)
    return values


def node_metadata(node):
    fields = ("id", "type", "status", "verification_status", "external_use", "publication", "source_file", "source_commit", "source_section", "source_locator", "source_resolution", "source_note", "source_checked_at", "source_related_file", "source_related_commit", "freshness", "stale_paths", "unknown_paths", "checked_against_commit", "source_freshness", "metric_source_resolution", "thermal_source_resolution", "chip", "product", "verified_at", "conflicts", "source_origin", "source_tier", "effective_until", "superseded_by", "updated")
    return {field: node[field] for field in fields if field in node}


class SpacemitMCPServer:
    def __init__(self):
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.nodes = self.data["nodes"]
        self.aliases = self.data["aliases"]
        self.raw_sources = self.data.get("raw_sources", [])

    def resolve_node_id(self, name_or_alias: str, expected_type=None):
        query = required_text(name_or_alias, "节点名称").lower()
        if query.endswith(".md"):
            query = query[:-3]
        required_text(query, "节点名称")
        # Exact IDs take precedence over names; aliases are checked on each node
        # so duplicate aliases cannot silently overwrite one another.
        exact_ids = [k for k in self.nodes if k.lower() == query]
        exact = exact_ids or [k for k, n in self.nodes.items() if query == n["title"].lower() or any(query == a.lower() for a in n.get("aliases", []))]
        candidates = exact or [k for k, n in self.nodes.items() if query in k.lower() or query in n["title"].lower() or any(query in a.lower() for a in n.get("aliases", []))]
        if exact and expected_type and not any(self.nodes[k]["type"] == expected_type for k in exact):
            raise ValueError(f"节点类型不匹配，需要 {expected_type}；请使用对应工具读取 {exact[0]}")
        candidates = [k for k in candidates if not expected_type or self.nodes[k]["type"] == expected_type]
        if len(candidates) > 1:
            choices = [{"id": k, "title": self.nodes[k]["title"], "type": self.nodes[k]["type"]} for k in candidates[:8]]
            raise ValueError("匹配多个节点，请确认芯片/产品并使用精确 ID：" + json.dumps(choices, ensure_ascii=False))
        return candidates[0] if candidates else None

    def resolve_raw_source(self, target):
        clean_path = target.removeprefix("Sources/")
        matches = [s for s in self.raw_sources if s["rel_path"] == clean_path or s["raw_url"] == target]
        if not matches and target.startswith("https://"):
            url = urllib.parse.urlsplit(target)
            path = urllib.parse.unquote(url.path)
            if url.netloc == "raw.githubusercontent.com" and not url.query and not url.fragment:
                for item in self.raw_sources:
                    main_path = f"/spacemit-com/{item['submodule']}/main/{item['repo_path']}"
                    if path == main_path or path == urllib.parse.unquote(urllib.parse.urlsplit(item["raw_url"]).path):
                        matches.append(item)
        if len(matches) != 1:
            raise ValueError("源文件不在已索引清单中；请先 search_raw_sources 并使用返回的完整 file_path 或 raw_url")
        return matches[0]

    def local_source_matches(self, item, local_path):
        if not os.path.isfile(local_path):
            return False
        expected_commit = item.get("source_commit")
        if not expected_commit:
            return True  # Compatibility with older indexes without a pinned revision.
        module_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Sources", item["submodule"])
        try:
            revision = subprocess.run(["git", "-C", module_path, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5, check=True).stdout.strip()
            dirty = subprocess.run(["git", "-C", module_path, "status", "--porcelain", "--", item["repo_path"]], capture_output=True, text=True, timeout=5, check=True).stdout.strip()
            return revision == expected_commit and not dirty
        except (OSError, subprocess.SubprocessError):
            return False

    def handle_tool_call(self, name: str, args: dict):
        try:
            if not isinstance(args, dict):
                raise ValueError("工具参数必须是对象")
            return self._handle_tool_call(name, args)
        except (ValueError, TypeError, OSError) as error:
            return {"isError": True, "content": [{"type": "text", "text": str(error)}]}

    def _handle_tool_call(self, name: str, args: dict):
        if name == "search_wiki":
            q = required_text(args.get("query"), "query").lower()
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
                        **node_metadata(node),
                        "score": score,
                        "id": node_id,
                        "title": node["title"],
                        "type": node["type"],
                        "domain": node["domain"],
                        "summary": node["summary"][:150] + "..."
                    })
            results.sort(key=lambda result: result["score"], reverse=True)
            return {"content": [{"type": "text", "text": json.dumps(results[:5], ensure_ascii=False, indent=2)}]}

        if name == "get_developer_journey":
            node_id = self.resolve_node_id(args.get("board_or_task", ""), "developer_journey")
            if not node_id or node_id not in self.nodes:
                return {"isError": True, "content": [{"type": "text", "text": f"未找到相关动线: {args.get('board_or_task')}"}]}
            node = self.nodes[node_id]
            return {"content": [{"type": "text", "text": json.dumps({
                **node_metadata(node),
                "title": node["title"],
                "type": node["type"],
                "target_audience": node["target_audience"],
                "referenced_atoms": node["outlinks"],
                "full_markdown_content": node["content"]
            }, ensure_ascii=False, indent=2)}]}

        if name == "read_knowledge_atom":
            node_id = self.resolve_node_id(args.get("atom_name", ""), "knowledge_atom")
            if not node_id or node_id not in self.nodes:
                return {"isError": True, "content": [{"type": "text", "text": f"未找到专题档案: {args.get('atom_name')}"}]}
            node = self.nodes[node_id]
            return {"content": [{"type": "text", "text": json.dumps({
                **node_metadata(node),
                "title": node["title"],
                "domain": node["domain"],
                "status": node["status"],
                "referenced_evidence": node["outlinks"],
                "full_markdown_content": node["content"]
            }, ensure_ascii=False, indent=2)}]}

        if name == "get_evidence_fact":
            node_id = self.resolve_node_id(args.get("spec_name", ""), "evidence")
            if not node_id or node_id not in self.nodes:
                return {"isError": True, "content": [{"type": "text", "text": f"未找到事实数据: {args.get('spec_name')}"}]}
            node = self.nodes[node_id]
            return {"content": [{"type": "text", "text": json.dumps({
                **node_metadata(node),
                "title": node["title"],
                "type": node["type"],
                "status": node["status"],
                "full_table_content": node["content"]
            }, ensure_ascii=False, indent=2)}]}

        if name == "get_graph_relations":
            node_id = self.resolve_node_id(args.get("node_name", ""))
            if not node_id or node_id not in self.nodes:
                return {"isError": True, "content": [{"type": "text", "text": f"未找到节点: {args.get('node_name')}"}]}
            node = self.nodes[node_id]
            return {"content": [{"type": "text", "text": json.dumps({
                "node_id": node_id,
                **node_metadata(node),
                "title": node["title"],
                "type": node["type"],
                "outlinks": [{"id": o, "title": self.nodes[o]["title"], "type": self.nodes[o]["type"]} for o in node["outlinks"] if o in self.nodes],
                "backlinks": [{"id": b, "title": self.nodes[b]["title"], "type": self.nodes[b]["type"]} for b in node["backlinks"] if b in self.nodes]
            }, ensure_ascii=False, indent=2)}]}

        if name == "search_raw_sources":
            q = required_text(args.get("query"), "query").lower()
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
                        "score": score,
                        "submodule": item["submodule"],
                        "file_path": item["rel_path"],
                        "title": item["title"],
                        "headers": item["headers"],
                        "source_commit": item.get("source_commit"),
                        "raw_url": item["raw_url"]
                    })
            matches.sort(key=lambda result: result["score"], reverse=True)
            return {"content": [{"type": "text", "text": json.dumps(matches[:8], ensure_ascii=False, indent=2)}]}

        if name == "read_raw_source_file":
            target = required_text(args.get("file_path_or_url"), "file_path_or_url")
            options = raw_read_options(args)
            item = self.resolve_raw_source(target)
            local_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Sources", item["rel_path"])
            origin = "local"
            if self.local_source_matches(item, local_path):
                with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
                    raw_text = f.read()
            else:
                origin = "github"
                target_url = urllib.parse.quote(item["raw_url"], safe=":/%?=&#+@")
                try:
                    req = urllib.request.Request(target_url, headers={"User-Agent": "Spacemit-MCP"})
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        raw_text = resp.read().decode("utf-8")
                except Exception as e:
                    return {"isError": True, "content": [{"type": "text", "text": f"无法读取源文件: {e}"}]}

            lines = raw_text.splitlines()
            start = options["start_line"] - 1
            end = min(len(lines), options["end_line"])
            has_more = end < len(lines)
            excerpt = {"source": item["raw_url"], "source_commit": item.get("source_commit"),
                       "origin": origin, "total_lines": len(lines), "start_line": start + 1,
                       "end_line": end, "has_more": has_more,
                       "next_start_line": end + 1 if has_more else None, "content": "\n".join(lines[start:end])}
            return {"content": [{"type": "text", "text": json.dumps(excerpt, ensure_ascii=False, indent=2)}]}

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
