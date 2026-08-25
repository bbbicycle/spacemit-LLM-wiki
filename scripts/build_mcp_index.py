#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spacemit LLM Wiki - MCP 双层知识图谱与源文件索引构建器
包含：
1. 第一层（精炼知识图谱）：Developer_Journeys (线)、Knowledge_Atoms (面)、Evidence (点) 完整正文与拓扑双链
2. 第二层（原始资料源清单）：扫描 Sources/docs-* 提取所有原始文档的路径、章节大纲、标题及 GitHub Raw URL 映射
3. 输出紧凑的 JSON 索引至 mcp/data/wiki_graph.json 并同步至 Worker 工程
"""

import os
import re
import json
import shutil

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIRS = {
    "developer_journey": os.path.join(ROOT_DIR, "Developer_Journeys"),
    "knowledge_atom": os.path.join(ROOT_DIR, "Knowledge_Atoms"),
    "evidence": os.path.join(ROOT_DIR, "Evidence")
}
SOURCES_DIR = os.path.join(ROOT_DIR, "Sources")

MCP_DATA_DIR = os.path.join(ROOT_DIR, "mcp", "data")
MCP_WORKER_DATA_DIR = os.path.join(ROOT_DIR, "mcp-worker", "src", "data")
OUTPUT_JSON_PATH = os.path.join(MCP_DATA_DIR, "wiki_graph.json")

# Submodule 仓库映射
SUBMODULE_REPOS = {
    "docs-chip": "https://github.com/spacemit-com/docs-chip",
    "docs-buildroot": "https://github.com/spacemit-com/docs-buildroot",
    "docs-product": "https://github.com/spacemit-com/docs-product",
    "docs-ai": "https://github.com/spacemit-com/docs-ai",
    "docs-ros": "https://github.com/spacemit-com/docs-ros"
}


def parse_frontmatter(file_path):
    """解析 Markdown 文件的 YAML frontmatter 和正文"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return {}, "", f"读取失败: {e}"

    lines = content.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, content, ""

    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        return {}, content, "Frontmatter 未闭合"

    fm_lines = lines[1:end_idx]
    body = "".join(lines[end_idx + 1:]).strip()

    frontmatter = {}
    current_key = None

    for line in fm_lines:
        line_strip = line.strip()
        if not line_strip or line_strip.startswith("#"):
            continue

        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            value = parts[1].strip()

            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]

            if key in ["aliases", "target_audience"]:
                if value.startswith("[") and value.endswith("]"):
                    items = [x.strip() for x in value[1:-1].split(",") if x.strip()]
                    clean_items = []
                    for it in items:
                        if (it.startswith('"') and it.endswith('"')) or (it.startswith("'") and it.endswith("'")):
                            it = it[1:-1]
                        clean_items.append(it)
                    frontmatter[key] = clean_items
                else:
                    frontmatter[key] = [value] if value else []
                current_key = key
            else:
                frontmatter[key] = value
                current_key = key
        elif line_strip.startswith("- ") and current_key in ["aliases", "target_audience"]:
            val = line_strip[2:].strip()
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            if current_key in frontmatter and isinstance(frontmatter[current_key], list):
                frontmatter[current_key].append(val)
            else:
                frontmatter[current_key] = [val]

    return frontmatter, body, ""


def extract_wikilinks(text):
    """提取 Markdown 正文中的 [[目标|别名]] 链接"""
    pattern = r'\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]'
    matches = re.findall(pattern, text)
    links = []
    for m in matches:
        clean_target = os.path.basename(m.strip().replace("\\", "/"))
        if clean_target.endswith(".md"):
            clean_target = clean_target[:-3]
        if clean_target and clean_target not in links:
            links.append(clean_target)
    return links


def scan_raw_sources():
    """扫描 Sources/ 原始资料层，生成轻量目录清单与章节大纲"""
    raw_sources = []
    if not os.path.exists(SOURCES_DIR):
        return raw_sources

    for sub_name in sorted(os.listdir(SOURCES_DIR)):
        sub_path = os.path.join(SOURCES_DIR, sub_name)
        if not os.path.isdir(sub_path) or sub_name.startswith("."):
            continue

        for root, dirs, files in os.walk(sub_path):
            # 过滤隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for fname in sorted(files):
                if not (fname.endswith(".md") or fname.endswith(".rst") or fname.endswith(".txt")):
                    continue

                full_path = os.path.join(root, fname)
                rel_to_sub = os.path.relpath(full_path, sub_path)
                rel_to_sources = os.path.relpath(full_path, SOURCES_DIR)

                # 提取文档标题和章节大纲
                title = fname
                headers = []
                summary = ""
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                    for line in lines:
                        line_s = line.strip()
                        if line_s.startswith("# ") and title == fname:
                            title = line_s[2:].strip()
                        elif line_s.startswith("## ") or line_s.startswith("### "):
                            headers.append(line_s.lstrip("#").strip())
                        elif not summary and line_s and not line_s.startswith("#") and not line_s.startswith("-") and not line_s.startswith("<"):
                            summary = line_s[:150]
                except Exception:
                    pass

                raw_sources.append({
                    "submodule": sub_name,
                    "file_name": fname,
                    "rel_path": rel_to_sources,
                    "repo_path": rel_to_sub,
                    "title": title,
                    "headers": headers[:10],  # 最多保留前 10 个核心小节标题
                    "summary": summary,
                    "raw_url": f"https://raw.githubusercontent.com/spacemit-com/{sub_name}/main/{rel_to_sub}"
                })

    return raw_sources


def build_graph():
    print("=" * 60)
    print("🚀 开始构建 Spacemit LLM Wiki 双层 MCP 拓扑索引...")
    print("=" * 60)

    nodes = {}
    name_to_id = {}
    alias_map = {}

    # 1. 扫描精炼三层架构文档 (Journeys / Atoms / Evidence)
    for doc_type, dir_path in TARGET_DIRS.items():
        if not os.path.exists(dir_path):
            print(f"⚠️ 目录不存在: {dir_path}")
            continue

        for fname in sorted(os.listdir(dir_path)):
            if not fname.endswith(".md"):
                continue

            fpath = os.path.join(dir_path, fname)
            node_id = fname[:-3]
            fm, body, err = parse_frontmatter(fpath)
            if err:
                print(f"⚠️ 解析警告 [{fname}]: {err}")

            title = fm.get("title", node_id)
            domain = fm.get("domain", "general")
            aliases = fm.get("aliases", [])
            status = fm.get("status", "approved")
            target_audience = fm.get("target_audience", [])

            outlinks = extract_wikilinks(body)

            nodes[node_id] = {
                "id": node_id,
                "title": title,
                "type": doc_type,
                "domain": domain,
                "status": status,
                "aliases": aliases,
                "target_audience": target_audience,
                "outlinks": outlinks,
                "backlinks": [],
                "summary": body[:300].replace("\n", " ").strip(),
                "content": body  # 完整 Markdown 正文，保留无损表格和步骤
            }

            name_to_id[node_id.lower()] = node_id
            name_to_id[title.lower()] = node_id

            for a in aliases:
                alias_map[a.lower()] = node_id

    # 2. 构建反向链接拓扑 (Backlinks)
    for node_id, data in nodes.items():
        for out in data["outlinks"]:
            target_id = None
            out_lower = out.lower()
            if out_lower in name_to_id:
                target_id = name_to_id[out_lower]
            elif out_lower in alias_map:
                target_id = alias_map[out_lower]

            if target_id and target_id in nodes:
                if node_id not in nodes[target_id]["backlinks"]:
                    nodes[target_id]["backlinks"].append(node_id)

    # 3. 扫描第二层：Sources 原始资料层
    raw_sources = scan_raw_sources()

    journeys_cnt = sum(1 for n in nodes.values() if n["type"] == "developer_journey")
    atoms_cnt = sum(1 for n in nodes.values() if n["type"] == "knowledge_atom")
    evidence_cnt = sum(1 for n in nodes.values() if n["type"] == "evidence")
    total_links = sum(len(n["outlinks"]) for n in nodes.values())

    print(f"✅ 第一层（精炼知识图谱）提取完成: 共 {len(nodes)} 个语义原子")
    print(f"   ├─ 🚗 Developer_Journeys (动线/线): {journeys_cnt} 篇")
    print(f"   ├─ 📦 Knowledge_Atoms    (专题/面): {atoms_cnt} 篇")
    print(f"   ├─ 🔬 Evidence           (事实/点): {evidence_cnt} 篇")
    print(f"   └─ 🔗 拓扑双链总数: {total_links} 条")
    print(f"✅ 第二层（原始资料源清单）提取完成: 共 {len(raw_sources)} 篇原始官方手册")

    index_payload = {
        "version": "2.0.0",
        "generated_at": "2026-08-25",
        "total_nodes": len(nodes),
        "total_raw_sources": len(raw_sources),
        "nodes": nodes,
        "aliases": alias_map,
        "raw_sources": raw_sources
    }

    # 保存到 mcp/data/
    os.makedirs(MCP_DATA_DIR, exist_ok=True)
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(index_payload, f, ensure_ascii=False, indent=2)
    print(f"💾 拓扑索引已保存至: {OUTPUT_JSON_PATH} ({os.path.getsize(OUTPUT_JSON_PATH) / 1024:.1f} KB)")

    # 同步至 Worker 目录
    os.makedirs(MCP_WORKER_DATA_DIR, exist_ok=True)
    worker_target = os.path.join(MCP_WORKER_DATA_DIR, "wiki_graph.json")
    shutil.copyfile(OUTPUT_JSON_PATH, worker_target)
    print(f"💾 同步至 Worker 目录: {worker_target}")
    print("=" * 60)
    return index_payload


if __name__ == "__main__":
    build_graph()
