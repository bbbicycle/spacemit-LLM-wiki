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
import argparse
import hashlib
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from urllib.parse import quote, unquote, urlsplit
from pathlib import PurePosixPath

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIRS = {
    "developer_journey": os.path.join(ROOT_DIR, "Developer_Journeys"),
    "knowledge_atom": os.path.join(ROOT_DIR, "Knowledge_Atoms"),
    "evidence": os.path.join(ROOT_DIR, "Evidence")
}
# Submodule 仓库映射
SUBMODULE_REPOS = {
    "docs-chip": "https://github.com/spacemit-com/docs-chip",
    "docs-buildroot": "https://github.com/spacemit-com/docs-buildroot",
    "docs-product": "https://github.com/spacemit-com/docs-product",
    "docs-ai": "https://github.com/spacemit-com/docs-ai",
    "docs-ros": "https://github.com/spacemit-com/docs-ros"
}


def parse_scalar(value):
    """Parse the supported single-line YAML scalar subset; reject other syntax."""
    value = value.strip()
    if not value or value.startswith("#"):
        return ""
    if value[0] in "\"'":
        pattern = r'"(?:[^"\\]|\\.)*"' if value[0] == '"' else r"'(?:[^']|'')*'"
        match = re.match(pattern, value)
        if not match or (value[match.end():].strip() and not value[match.end():].strip().startswith("#")):
            raise ValueError("引号标量未闭合或包含额外内容")
        quoted = match.group()
        if quoted[0] == '"':
            try:
                return json.loads(quoted)
            except json.JSONDecodeError as exc:
                raise ValueError("双引号标量仅支持 JSON 兼容转义") from exc
        return quoted[1:-1].replace("''", "'")
    value = re.split(r"\s+#", value, maxsplit=1)[0].rstrip()
    if value[0] in "|>[{&*!%@`" or value in ("---", "..."):
        raise ValueError("不支持块标量、嵌套结构、锚点或 YAML 标签")
    if re.search(r":(?:\s|$)", value) or value.startswith(("- ", "? ")):
        raise ValueError("不支持嵌套 mapping 或 sequence")
    return value


def parse_inline_list(value):
    """Parse aliases/audience lists, preserving commas within quoted items."""
    items = []
    remaining = value[1:].lstrip()
    while not remaining.startswith("]"):
        if not remaining:
            raise ValueError("列表未闭合")
        if remaining[0] in "\"'":
            pattern = r'"(?:[^"\\]|\\.)*"' if remaining[0] == '"' else r"'(?:[^']|'')*'"
            match = re.match(pattern, remaining)
            if not match:
                raise ValueError("列表引号未闭合")
            item, remaining = match.group(), remaining[match.end():].lstrip()
        else:
            match = re.match(r"[^,\]]+", remaining)
            if not match:
                raise ValueError("列表包含空项")
            item, remaining = match.group().strip(), remaining[match.end():].lstrip()
            if re.search(r"\s+#", item):
                raise ValueError("列表内部不支持行内注释")
        items.append(parse_scalar(item))
        if remaining.startswith(","):
            remaining = remaining[1:].lstrip()
        elif not remaining.startswith("]"):
            raise ValueError("列表项之间必须使用逗号")
    trailing = remaining[1:].strip()
    if trailing and not trailing.startswith("#"):
        raise ValueError("列表末尾包含额外内容")
    return items


def parse_frontmatter(file_path):
    """Parse flat frontmatter without silently flattening unsupported YAML.

    Supported: top-level scalars, aliases/audience and source path/revision
    lists (inline or block), comments and empty values. Unsupported YAML aborts publication.
    """
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
        if lines[i].rstrip("\r\n") == "---":
            end_idx = i
            break

    if end_idx == -1:
        return {}, content, "Frontmatter 未闭合"

    fm_lines = lines[1:end_idx]
    body = "".join(lines[end_idx + 1:]).strip()

    frontmatter = {}
    list_key = None
    list_indent = None

    for line_number, line in enumerate(fm_lines, start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            entry = re.match(r"^( *)- (.+?)\s*$", line)
            if entry and list_key:
                indent = len(entry.group(1))
                if list_indent is not None and indent != list_indent:
                    raise ValueError("多行列表的缩进必须一致")
                list_indent = indent
                frontmatter[list_key].append(parse_scalar(entry.group(2)))
                continue
            if line[0].isspace():
                raise ValueError("不支持缩进 mapping 或多行标量")
            match = re.match(r"^([A-Za-z_][A-Za-z_0-9-]*):(?:\s+(.*)|\s*)$", line.rstrip("\r\n"))
            if not match:
                raise ValueError("必须使用顶层 key: value；不支持 YAML 复杂结构")
            key, value = match.group(1), (match.group(2) or "").strip()
            if key in frontmatter:
                raise ValueError(f"重复的顶层字段: {key}")
            list_key, list_indent = None, None
            if key in ("aliases", "target_audience") or (key in (
                "source_file", "source_commit", "source_related_file", "source_related_commit"
            ) and (not value or value.startswith("["))):
                if value.startswith("["):
                    frontmatter[key] = parse_inline_list(value)
                else:
                    scalar = parse_scalar(value)
                    frontmatter[key] = [scalar] if scalar else []
                    if not scalar:
                        list_key = key
            else:
                frontmatter[key] = parse_scalar(value)
        except ValueError as exc:
            return {}, body, f"Frontmatter 第 {line_number} 行: {exc}"

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


def is_public_document(frontmatter):
    """公共 MCP 不发布内部审批、现场反馈、NDA 或明确标为非公开的资料。

    external_use:false 单独表示事实未核验，仍保留并透传其核验状态。
    """
    def policy_value(key):
        return str(frontmatter.get(key, "")).split(" #", 1)[0].strip().strip("\"'").lower()

    tier = policy_value("source_tier")
    if tier.startswith(("tier_2", "tier_3")):
        return False
    if policy_value("price_nature") == "nda_confidential":
        return False
    if policy_value("publication") in ("false", "no", "off", "0", "private", "internal", "confidential"):
        return False
    if policy_value("visibility") in ("private", "internal", "confidential"):
        return False
    return True


def git_output(directory, *args):
    result = subprocess.run(
        ["git", "-C", directory, *args], check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def normalize_source_path(value):
    """Normalize source metadata, Markdown targets and Obsidian source links."""
    value = unquote(str(value).strip().strip('<>')).replace("\\", "/")
    value = value.split("|", 1)[0].split("#", 1)[0]
    if value.startswith(("https://", "http://")):
        url = urlsplit(value)
        if url.netloc not in ("github.com", "raw.githubusercontent.com"):
            return None
        parts = url.path.strip("/").split("/")
        if len(parts) < 4 or parts[0] != "spacemit-com" or parts[1] not in SUBMODULE_REPOS:
            return None
        offset = 4 if url.netloc == "github.com" and parts[2] == "blob" else 3
        if url.netloc == "github.com" and offset != 4:
            return None
        value = "Sources/" + parts[1] + "/" + "/".join(parts[offset:])
    elif "Sources/" in value:
        value = value[value.index("Sources/"):]
    else:
        value = "Sources/" + value
    parts = PurePosixPath(value).parts
    if len(parts) < 3 or parts[0] != "Sources" or parts[1] not in SUBMODULE_REPOS or ".." in parts:
        return None
    return "/".join(parts)


def source_references(metadata):
    """Scalar or parallel flat lists; never guess a missing revision."""
    references = []
    for prefix in ("source", "source_related"):
        paths = metadata.get(prefix + "_file", [])
        commits = metadata.get(prefix + "_commit", [])
        paths = paths if isinstance(paths, list) else [paths]
        commits = commits if isinstance(commits, list) else [commits]
        for i, path in enumerate(paths):
            if not path:
                continue
            commit = commits[i] if i < len(commits) else None
            references.append((normalize_source_path(path) or str(path), commit))
    return list(dict.fromkeys(references))


def calculate_freshness(metadata, root_dir, versions, cache=None):
    """Compare each cited path at its own revision, independently of verification."""
    cache = cache if cache is not None else {}
    results = []
    checked = {}
    for path, commit in source_references(metadata):
        normalized = normalize_source_path(path)
        parts = normalized.split("/", 2) if normalized else []
        current = versions.get(parts[1]) if parts else None
        if current:
            checked[parts[1]] = current
        key = (path, commit, current)
        if key not in cache:
            state, reason = "unknown", "missing_or_invalid_source_revision"
            if current and isinstance(commit, str) and re.fullmatch(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}", commit):
                module = os.path.join(root_dir, "Sources", parts[1])
                try:
                    # A missing historical file cannot establish a reliable baseline.
                    git_output(module, "cat-file", "-e", f"{commit}^{{commit}}")
                    if git_output(module, "cat-file", "-t", f"{commit}:{parts[2]}") != "blob":
                        raise ValueError("source_file 必须指向文件")
                    diff = subprocess.run(
                        ["git", "-C", module, "diff", "--quiet", commit, current, "--", parts[2]],
                        capture_output=True,
                    )
                    if diff.returncode in (0, 1):
                        state = "stale" if diff.returncode else "current"
                        reason = "source_file_changed" if diff.returncode else "source_file_unchanged"
                    else:
                        reason = "source_diff_unavailable"
                except (OSError, ValueError, subprocess.CalledProcessError):
                    reason = "historical_source_unavailable"
            cache[key] = (state, reason)
        state, reason = cache[key]
        results.append(dict(source_file=path, source_commit=commit, checked_against_commit=current,
                            freshness=state, reason=reason))
    states = {item["freshness"] for item in results}
    freshness = "stale" if "stale" in states else "unknown" if not states or "unknown" in states else "current"
    return dict(freshness=freshness, stale_paths=sorted({x["source_file"] for x in results if x["freshness"] == "stale"}),
                unknown_paths=sorted({x["source_file"] for x in results if x["freshness"] == "unknown"}),
                checked_against_commit=checked, source_freshness=results)


def freshness_report(payload):
    nodes = payload["nodes"]
    return {
        "schema_version": 1,
        "source_versions": payload["source_versions"],
        "summary": {state: sum(n["freshness"] == state for n in nodes.values()) for state in ("current", "stale", "unknown")},
        "nodes": [{k: n[k] for k in ("id", "type", "title", "freshness", "stale_paths", "unknown_paths",
                                    "checked_against_commit", "source_freshness")} for n in nodes.values() if n["freshness"] != "current"],
    }


def source_versions(root_dir):
    """拒绝缺失、未初始化或有本地修改的 Sources，避免覆盖有效索引。"""
    versions = {}
    for sub_name in SUBMODULE_REPOS:
        sub_path = os.path.join(root_dir, "Sources", sub_name)
        if not os.path.exists(os.path.join(sub_path, ".git")):
            raise ValueError(
                f"Sources/{sub_name} 未初始化；已有索引保持不变。"
                "请先运行 git submodule update --init --recursive。"
            )
        if os.path.realpath(git_output(sub_path, "rev-parse", "--show-toplevel")) != os.path.realpath(sub_path):
            raise ValueError(f"Sources/{sub_name} 不是独立的 Git 子模块")
        if git_output(sub_path, "status", "--porcelain", "--untracked-files=no"):
            raise ValueError(f"Sources/{sub_name} 含未提交修改，无法生成对应 commit 的可靠索引")
        versions[sub_name] = git_output(sub_path, "rev-parse", "HEAD")
    return versions


def scan_raw_sources(root_dir=ROOT_DIR, versions=None):
    """扫描 Sources/ 原始资料层，生成轻量目录清单与章节大纲"""
    raw_sources = []
    sources_dir = os.path.join(root_dir, "Sources")
    versions = versions if versions is not None else source_versions(root_dir)

    for sub_name in sorted(SUBMODULE_REPOS):
        sub_path = os.path.join(sources_dir, sub_name)
        module_count = 0
        tracked_files = set(git_output(sub_path, "ls-files", "-z").split("\0"))

        for root, dirs, files in os.walk(sub_path):
            # 过滤隐藏目录
            dirs[:] = sorted(d for d in dirs if not d.startswith("."))

            for fname in sorted(files):
                if not (fname.endswith(".md") or fname.endswith(".rst") or fname.endswith(".txt")):
                    continue

                full_path = os.path.join(root, fname)
                rel_to_sub = os.path.relpath(full_path, sub_path).replace(os.sep, "/")
                if rel_to_sub not in tracked_files:
                    continue
                rel_to_sources = os.path.relpath(full_path, sources_dir).replace(os.sep, "/")

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
                except OSError as exc:
                    raise ValueError(f"无法读取 Sources/{rel_to_sources}: {exc}") from exc

                raw_sources.append({
                    "submodule": sub_name,
                    "file_name": fname,
                    "rel_path": rel_to_sources,
                    "repo_path": rel_to_sub,
                    "title": title,
                    "headers": headers[:10],  # 最多保留前 10 个核心小节标题
                    "summary": summary,
                    "source_commit": versions[sub_name],
                    "raw_url": f"https://raw.githubusercontent.com/spacemit-com/{sub_name}/{versions[sub_name]}/{quote(rel_to_sub, safe='/')}"
                })
                module_count += 1
        if not module_count:
            raise ValueError(f"Sources/{sub_name} 没有可索引的已提交文档；已有索引保持不变")

    return raw_sources


def build_graph(root_dir=ROOT_DIR, write_outputs=True, if_changed=False):
    print("=" * 60)
    print("🚀 开始构建 Spacemit LLM Wiki 双层 MCP 拓扑索引...")
    print("=" * 60)

    nodes = {}
    name_to_id = {}
    alias_map = {}
    private_names = set()
    versions = source_versions(root_dir)
    freshness_cache = {}

    # 1. 扫描精炼三层架构文档 (Journeys / Atoms / Evidence)
    for doc_type, default_path in TARGET_DIRS.items():
        dir_path = os.path.join(root_dir, os.path.basename(default_path))
        if not os.path.exists(dir_path):
            raise ValueError(f"精炼目录不存在: {dir_path}")

        for fname in sorted(os.listdir(dir_path)):
            if not fname.endswith(".md"):
                continue

            fpath = os.path.join(dir_path, fname)
            node_id = fname[:-3]
            fm, body, err = parse_frontmatter(fpath)
            if err:
                raise ValueError(f"文档解析失败 [{fname}]: {err}")

            title = fm.get("title", node_id)
            domain = fm.get("domain", "general")
            aliases = fm.get("aliases", [])
            status = fm.get("status", "needs_review")
            target_audience = fm.get("target_audience", [])

            if not is_public_document(fm):
                private_names.update(name.lower() for name in [node_id, title, *aliases])
                continue

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
            # 保留出处、版本、核验、冲突及产品适用范围等全部元数据，避免响应丢失限定条件。
            for key, value in fm.items():
                if key not in nodes[node_id]:
                    nodes[node_id][key] = value
            if "external_use" in fm:
                nodes[node_id]["external_use"] = fm["external_use"].lower() == "true"
            if "publication" in fm and fm["publication"].lower() in ("true", "false"):
                nodes[node_id]["publication"] = fm["publication"].lower() == "true"
            nodes[node_id].update(calculate_freshness(fm, root_dir, versions, freshness_cache))

            name_to_id[node_id.lower()] = node_id
            name_to_id[title.lower()] = node_id

            for a in aliases:
                alias_map[a.lower()] = node_id

    # 2. 构建反向链接拓扑 (Backlinks)
    for node_id, data in nodes.items():
        for out in data["outlinks"]:
            if out.lower() in private_names:
                raise ValueError(f"公开文档 {node_id} 引用了非公开节点；请先移除公开引用或提供可公开来源")
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
    raw_sources = scan_raw_sources(root_dir, versions)

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
        "version": "2.2.0",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "wiki_commit": git_output(root_dir, "rev-parse", "HEAD"),
        "wiki_worktree_dirty": bool(git_output(root_dir, "status", "--porcelain", "--untracked-files=no")),
        "source_versions": versions,
        "total_nodes": len(nodes),
        "total_raw_sources": len(raw_sources),
        "nodes": nodes,
        "aliases": alias_map,
        "raw_sources": raw_sources
    }
    index_payload["content_sha256"] = hashlib.sha256(
        json.dumps({"nodes": nodes, "raw_sources": raw_sources}, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()

    if write_outputs:
        if if_changed and indexes_unchanged(root_dir, index_payload):
            print("✅ 索引内容与来源版本无变化，保留现有文件及构建时间")
            with open(index_paths(root_dir)[0], encoding="utf-8") as f:
                return json.load(f)
        write_indexes(root_dir, index_payload)
    print("=" * 60)
    return index_payload


def index_paths(root_dir):
    return [
        os.path.join(root_dir, "mcp", "data", "wiki_graph.json"),
        os.path.join(root_dir, "mcp-worker", "src", "data", "wiki_graph.json")
    ]


CONTENT_FIELDS = ("version", "source_versions", "total_nodes", "total_raw_sources", "nodes", "aliases", "raw_sources", "content_sha256")


def indexes_unchanged(root_dir, expected):
    """Ignore build provenance churn while checking both published copies."""
    try:
        copies = []
        for path in index_paths(root_dir):
            with open(path, encoding="utf-8") as f:
                copies.append(json.load(f))
        if copies[0] != copies[1] or not isinstance(copies[0], dict):
            return False
        timestamp = datetime.fromisoformat(copies[0]["generated_at"])
        if timestamp.tzinfo is None:
            return False
        return all(copies[0].get(key) == expected[key] for key in CONTENT_FIELDS)
    except (OSError, ValueError, KeyError, TypeError):
        return False


def write_indexes(root_dir, payload):
    # 输入校验、序列化和临时文件写入全部成功后，才替换现有索引。
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    pending = []
    try:
        for path in index_paths(root_dir):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=os.path.dirname(path), delete=False) as f:
                pending.append((f.name, path))
                f.write(encoded)
        for temporary, path in pending:
            os.replace(temporary, path)
            print(f"💾 拓扑索引已保存至: {path} ({len(encoded.encode('utf-8')) / 1024:.1f} KB)")
    finally:
        for temporary, _ in pending:
            if os.path.exists(temporary):
                os.unlink(temporary)


def check_indexes(root_dir=ROOT_DIR):
    """验证两个索引完全一致，且其正文、源清单与当前 checkout 相符。"""
    with open(index_paths(root_dir)[0], encoding="utf-8") as f:
        payload = json.load(f)
    with open(index_paths(root_dir)[1], encoding="utf-8") as f:
        worker_payload = json.load(f)
    if payload != worker_payload:
        raise ValueError("本地与 Worker 索引不一致，请重建索引")
    generated_at = datetime.fromisoformat(payload["generated_at"])
    if generated_at.tzinfo is None:
        raise ValueError("索引构建时间缺少时区")
    expected = build_graph(root_dir, write_outputs=False)
    for key in CONTENT_FIELDS:
        if payload.get(key) != expected[key]:
            raise ValueError(f"索引字段 {key} 已过期，请重建索引")
    print("✅ 本地与 Worker 索引一致，正文、源清单及固定 commit 校验通过")
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="只校验已有索引，不写入文件")
    mode.add_argument("--if-changed", action="store_true", help="完成输入校验后，仅内容或来源版本变化时写入索引")
    parser.add_argument("--freshness-report", metavar="PATH", help="额外输出 stale/unknown 节点的 JSON 维护队列")
    args = parser.parse_args()
    try:
        payload = check_indexes() if args.check else build_graph(if_changed=args.if_changed)
        if args.freshness_report:
            os.makedirs(os.path.dirname(os.path.abspath(args.freshness_report)), exist_ok=True)
            with open(args.freshness_report, "w", encoding="utf-8") as report:
                json.dump(freshness_report(payload), report, ensure_ascii=False, indent=2)
                report.write("\n")
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"❌ 索引构建/校验失败: {exc}", file=sys.stderr)
        sys.exit(1)
