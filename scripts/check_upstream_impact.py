#!/usr/bin/env python3
"""按已保存基线或远端版本分析上游变更，同时输出 JSON 和可读报告。"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

# 也支持通过 importlib 加载脚本的离线回归测试。
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_mcp_index import SUBMODULE_REPOS, extract_wikilinks, normalize_source_path, parse_frontmatter, source_references

VAULT_ROOT = Path(__file__).resolve().parents[1]
SUBMODULES = ["Sources/" + name for name in SUBMODULE_REPOS]
BASELINE_PATH = "docs/source_baseline.json"


def git(root, module, *args):
    directory = Path(root) / module
    if not (directory / ".git").exists():
        raise ValueError(f"{module} 未初始化")
    result = subprocess.run(["git", "-C", str(directory), *args], capture_output=True, text=True)
    if result.returncode:
        raise ValueError(f"{module}: git {args[0]} 失败: {result.stderr.strip()}")
    return result.stdout


def current_pointers(root):
    return {module: git(root, module, "rev-parse", "HEAD").strip() for module in SUBMODULES}


def save_pointers(path, pointers):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        temporary = handle.name
        json.dump(pointers, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    try:
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_pointers(path):
    pointers = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(pointers, dict) or any(
        key not in SUBMODULES or not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value)
        for key, value in pointers.items()
    ):
        raise ValueError("基线必须是 Sources 子模块到完整 commit SHA 的 JSON 对象")
    return pointers


def body_source_paths(body):
    targets = re.findall(r"\[[^\]\n]*\]\(\s*(<[^>]+>|[^)\n]+)\)", body)
    targets += re.findall(r"\[\[([^\]\n]+)\]\]", body)
    paths = set()
    for target in targets:
        if target.startswith("<") and ">" in target:
            target = target[1:target.index(">")]
        else:
            target = re.split(r"\s+[\"']", target, maxsplit=1)[0]
        path = normalize_source_path(target)
        if path:
            paths.add(path)
    return paths


def build_reference_map(root=VAULT_ROOT):
    """Sources 直接关系 + Journey/Atom/Evidence 双链的传递影响。"""
    documents, names = {}, defaultdict(set)
    for folder in ("Developer_Journeys", "Knowledge_Atoms", "Evidence"):
        for path in sorted((Path(root) / folder).rglob("*.md")):
            metadata, body, error = parse_frontmatter(path)
            if error:
                raise ValueError(f"{path}: {error}")
            node = path.relative_to(root).as_posix()
            documents[node] = (metadata, body)
            for name in (path.stem, metadata.get("title", ""), *metadata.get("aliases", [])):
                names[name.lower()].add(node)
    references, dependents = defaultdict(set), defaultdict(set)
    for node, (metadata, body) in documents.items():
        paths = {path for path, _ in source_references(metadata)} | body_source_paths(body)
        for path in paths:
            references[path].add(node)
        for name in extract_wikilinks(body):
            for target in names.get(name.lower(), ()):
                dependents[target].add(node)
    for nodes in references.values():
        pending = list(nodes)
        while pending:
            for dependent in dependents[pending.pop()]:
                if dependent not in nodes:
                    nodes.add(dependent)
                    pending.append(dependent)
    return references


def get_changed_files(root, module, old_commit, new_commit):
    # Renames are D+A so the old and new paths both participate in impact analysis.
    fields = git(root, module, "diff", "--no-renames", "--name-status", "-z", old_commit, new_commit, "--").split("\0")
    return [(fields[i], fields[i + 1]) for i in range(0, len(fields) - 1, 2)]


def empty_report():
    return {"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "baseline_initialized": False, "submodules": {}, "changed_files": [],
            "affected_nodes": [], "uncovered_files": [], "deleted_files": [], "errors": []}


def analyze(root, old, new, references):
    report = empty_report()
    affected = set()
    for module in SUBMODULES:
        previous, current = old.get(module), new.get(module)
        if not previous or not current:
            report["errors"].append(f"{module}: 缺少基线或目标 commit，不能判断变更")
            continue
        try:
            changes = get_changed_files(root, module, previous, current)
            count = int(git(root, module, "rev-list", "--count", f"{previous}..{current}").strip())
        except ValueError as error:
            report["errors"].append(str(error))
            continue
        report["submodules"][module] = dict(old_commit=previous, new_commit=current, commit_count=count, changed_files=len(changes))
        for status, relative in changes:
            path = module + "/" + relative
            nodes = sorted(references.get(path, ()))
            affected.update(nodes)
            report["changed_files"].append(dict(status=status, path=path, affected_nodes=nodes))
            if not nodes:
                report["uncovered_files"].append(path)
            if status == "D":
                report["deleted_files"].append(path)
    report["affected_nodes"] = sorted(affected)
    return report


def human_report(report, stream=sys.stdout):
    print("SpacemiT Wiki — 上游变更影响报告", file=stream)
    if report["baseline_initialized"]:
        print("首次运行：已保存当前子模块基线；后续运行将对比该基线。", file=stream)
    for module, versions in report["submodules"].items():
        print(f"{module}: {versions['old_commit'][:8]}..{versions['new_commit'][:8]}，{versions['changed_files']} 个文件", file=stream)
    for change in report["changed_files"]:
        print(f"  {change['status']} {change['path']}", file=stream)
        for node in change["affected_nodes"]:
            print(f"    → {node}", file=stream)
    print(f"共 {len(report['changed_files'])} 个变更文件，影响 {len(report['affected_nodes'])} 个节点，"
          f"未覆盖 {len(report['uncovered_files'])} 个，删除 {len(report['deleted_files'])} 个。", file=stream)
    for error in report["errors"]:
        print("错误：" + error, file=stream)


def emit_report(report, destination, root):
    human_report(report, sys.stderr if destination == "-" else sys.stdout)
    if destination:
        encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if destination == "-":
            print(encoded, end="")
        else:
            output = root / destination
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(encoded, encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cached", action="store_true", help="比较已保存基线与当前 checkout，不联网")
    parser.add_argument("--save", action="store_true", help="分析成功后将当前 checkout 保存为下次基线")
    parser.add_argument("--init-baseline", action="store_true", help="只在基线不存在时初始化，供同步前调用")
    parser.add_argument("--baseline", default=BASELINE_PATH, help="基线 JSON 路径，相对仓库根目录")
    parser.add_argument("--json", metavar="PATH", help="写入结构化报告；- 表示 stdout，可读报告转到 stderr")
    args = parser.parse_args(argv)
    baseline = VAULT_ROOT / args.baseline
    try:
        current = current_pointers(VAULT_ROOT)
        initialized = not baseline.exists()
        if initialized:
            save_pointers(baseline, current)
        old = load_pointers(baseline)
        if args.init_baseline:
            print("已初始化基线" if initialized else "保留已有基线")
            return 0
        target = current
        if not args.cached:
            old, target = current, {}
            for module in SUBMODULES:
                git(VAULT_ROOT, module, "fetch", "origin", "--quiet")
                remote_ref = git(VAULT_ROOT, module, "symbolic-ref", "refs/remotes/origin/HEAD").strip()
                target[module] = git(VAULT_ROOT, module, "rev-parse", remote_ref).strip()
        report = analyze(VAULT_ROOT, old, target, build_reference_map(VAULT_ROOT))
        report["baseline_initialized"] = initialized
        emit_report(report, args.json, VAULT_ROOT)
        if report["errors"]:
            return 1
        if args.save:
            save_pointers(baseline, current)
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        report = empty_report()
        report["errors"].append(str(error))
        try:
            emit_report(report, args.json, VAULT_ROOT)
        except OSError as output_error:
            print(f"影响报告写入失败：{output_error}；原始错误：{error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
