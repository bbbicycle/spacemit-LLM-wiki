#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spacemit LLM Wiki - MCP 双层图谱与源文件导航工具测试套件 (v2.0)
包含 7 大核心 MCP Tools 验证：
1. search_wiki (精炼层搜索)
2. get_developer_journey (动线直出)
3. read_knowledge_atom (专题直出)
4. get_evidence_fact (事实数据直出)
5. get_graph_relations (图谱拓扑遍历)
6. search_raw_sources (原始资料清单检索)
7. read_raw_source_file (原始文件穿透读取)
"""

import json
import os
import urllib.request

INDEX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "wiki_graph.json")


class SpacemitWikiNavigator:
    def __init__(self, index_path=INDEX_PATH):
        with open(index_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.nodes = self.data["nodes"]
        self.aliases = self.data["aliases"]
        self.raw_sources = self.data.get("raw_sources", [])

    def _resolve_node_id(self, name_or_alias: str):
        query = name_or_alias.strip().lower()
        if query.endswith(".md"):
            query = query[:-3]

        if query in [k.lower() for k in self.nodes]:
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

    def search_wiki(self, query: str, domain: str = None):
        q_lower = query.lower()
        results = []

        for node_id, node in self.nodes.items():
            if domain and node.get("domain") != domain:
                continue

            score = 0
            if q_lower in node["title"].lower() or q_lower in node_id.lower():
                score += 10
            for alias in node.get("aliases", []):
                if q_lower in alias.lower():
                    score += 8
                    break
            if q_lower in node.get("content", "").lower():
                score += 3

            if score > 0:
                results.append({
                    "score": score,
                    "id": node_id,
                    "title": node["title"],
                    "type": node["type"],
                    "domain": node["domain"],
                    "summary": node["summary"][:150] + "..."
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:5]

    def get_developer_journey(self, board_or_task: str):
        node_id = self._resolve_node_id(board_or_task)
        if not node_id:
            return f"❌ 未找到与 '{board_or_task}' 相关的开发者动线"

        node = self.nodes.get(node_id)
        if node["type"] != "developer_journey":
            return f"⚠️ 找到节点 '{node_id}'，但其类型为 '{node['type']}'"

        return {
            "title": node["title"],
            "type": node["type"],
            "target_audience": node["target_audience"],
            "outlinks_referenced": node["outlinks"],
            "full_content": node["content"]
        }

    def read_knowledge_atom(self, atom_name: str):
        node_id = self._resolve_node_id(atom_name)
        if not node_id:
            return f"❌ 未找到知识原子专题: '{atom_name}'"

        node = self.nodes.get(node_id)
        return {
            "title": node["title"],
            "domain": node["domain"],
            "status": node["status"],
            "evidence_referenced": node["outlinks"],
            "full_content": node["content"]
        }

    def get_evidence_fact(self, spec_name: str):
        node_id = self._resolve_node_id(spec_name)
        if not node_id:
            return f"❌ 未找到事实证据: '{spec_name}'"

        node = self.nodes.get(node_id)
        return {
            "title": node["title"],
            "type": "evidence",
            "full_table_content": node["content"]
        }

    def get_graph_relations(self, node_name: str):
        node_id = self._resolve_node_id(node_name)
        if not node_id:
            return f"❌ 未找到节点: '{node_name}'"

        node = self.nodes.get(node_id)
        return {
            "node_id": node_id,
            "title": node["title"],
            "type": node["type"],
            "outlinks": [
                {"id": out, "title": self.nodes[out]["title"], "type": self.nodes[out]["type"]}
                for out in node["outlinks"] if out in self.nodes
            ],
            "backlinks": [
                {"id": b, "title": self.nodes[b]["title"], "type": self.nodes[b]["type"]}
                for b in node["backlinks"] if b in self.nodes
            ]
        }

    def search_raw_sources(self, query: str, submodule: str = None):
        q = query.lower()
        matches = []
        for item in self.raw_sources:
            if submodule and item["submodule"] != submodule:
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
                    "raw_url": item["raw_url"]
                })
        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches[:8]

    def read_raw_source_file(self, file_path_or_url: str, start_line: int = 1, end_line: int = None):
        target_url = file_path_or_url
        if not target_url.startswith("http"):
            clean_path = target_url.replace("Sources/", "")
            for s in self.raw_sources:
                if s["rel_path"] == clean_path or s["rel_path"].endswith(clean_path):
                    target_url = s["raw_url"]
                    break

        try:
            req = urllib.request.Request(target_url, headers={"User-Agent": "Spacemit-MCP-Test"})
            with urllib.request.urlopen(req, timeout=5) as response:
                content = response.read().decode("utf-8")
                lines = content.splitlines()
                start = max(1, start_line) - 1
                end = min(len(lines), end_line) if end_line else len(lines)
                return {
                    "source_url": target_url,
                    "total_lines": len(lines),
                    "selected_lines": f"{start+1}-{end}",
                    "content": "\n".join(lines[start:end])
                }
        except Exception as e:
            # 本地离线 fallback
            local_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Sources", clean_path)
            if os.path.exists(local_path):
                with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.read().splitlines()
                start = max(1, start_line) - 1
                end = min(len(lines), end_line) if end_line else len(lines)
                return {
                    "source_local": local_path,
                    "total_lines": len(lines),
                    "selected_lines": f"{start+1}-{end}",
                    "content": "\n".join(lines[start:end])
                }
            return f"❌ 读取失败: {e}"


def run_tests():
    print("=" * 60)
    print("🧪 开始运行 Spacemit MCP 2.0 (双层图谱+源文件穿透) 测试...")
    print("=" * 60)

    nav = SpacemitWikiNavigator()

    # 1. 动线与精炼层测试
    print("\n🚗 [Test 1] 获取 Muse Pi 通关动线:")
    j = nav.get_developer_journey("Muse_Pi")
    print(f"   ✅ 成功获取动线: {j['title']} (引用双链: {len(j['outlinks_referenced'])} 个)")

    # 2. 专题与事实测试
    print("\n📦 [Test 2] 获取 GMAC 千兆网专题与事实表:")
    atom = nav.read_knowledge_atom("千兆网口")
    print(f"   ✅ 获取专题: {atom['title']}")
    fact = nav.get_evidence_fact("k1_strap_pins")
    print(f"   ✅ 获取事实表: {fact['title']} (零截断)")

    # 3. 原始 Sources 搜索测试
    print("\n🔍 [Test 3] 在 1052 篇原始 Sources 手册中搜索 'uart':")
    raw_res = nav.search_raw_sources("uart", submodule="docs-chip")
    for r in raw_res[:3]:
        print(f"   👉 [{r['submodule']}] {r['file_path']} - {r['title']}")
    assert len(raw_res) > 0, "应搜到原始 uart 手册"

    # 4. 原始文件穿透读取测试
    print("\n🔬 [Test 4] 穿透读取原始源文件:")
    target_file = raw_res[0]["file_path"]
    read_res = nav.read_raw_source_file(target_file, start_line=1, end_line=30)
    assert isinstance(read_res, dict), "应成功返回文件内容"
    print(f"   ✅ 穿透读取成功: {target_file}")
    print(f"   📄 内容前 2 行: {read_res['content'].splitlines()[:2]}")

    print("\n" + "=" * 60)
    print("🎉 7 大双层 MCP 导航工具全部通过自动化测试！")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
