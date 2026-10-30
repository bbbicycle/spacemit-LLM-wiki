#!/usr/bin/env python3
"""Run the 20 source-grounded retrieval/notice cases on both production cores.

This evaluates available evidence and tool contracts, not a model's generated
answers. Requires initialized Sources, Git history and Node.js 24+; no network.
"""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DOMAINS = {
    "chip_product_specs", "hardware_schematic_design", "bsp_kernel_drivers",
    "bianbu_os_distribution", "toolchain_debug_tools", "edge_ai_robotics",
}


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def git(*args, cwd=ROOT):
    return subprocess.check_output(["git", *args], cwd=cwd, text=True)


def normalize(result, tool):
    value = json.loads(result["content"][0]["text"])
    if tool == "read_raw_source_file":
        value.pop("origin", None)  # local pinned source versus Worker fetch
    return value


def relocate_excerpt(blob, excerpt, expected_digest):
    """Allow line movement, while requiring the entire reviewed excerpt verbatim."""
    if digest(excerpt) != expected_digest:
        raise ValueError("Reviewed citation digest does not match its pinned excerpt")
    lines, reference = blob.splitlines(), excerpt.split("\n")
    matches = [i for i in range(len(lines) - len(reference) + 1)
               if lines[i:i + len(reference)] == reference]
    if not matches:
        raise ValueError("Reviewed source excerpt changed or disappeared; review the source and rubric")
    if len(matches) != 1:
        raise ValueError("Reviewed source excerpt is ambiguous; narrow the citation")
    return matches[0] + 1, matches[0] + len(reference)


def resolve_raw_call(call, citations, raw_sources):
    """Locate the reviewed citation in the source version pinned by today's index."""
    expected = call["expect"]
    if "source_file" not in expected:
        return call, None
    args = call["arguments"]
    citations = [c for c in citations if c["path"] == expected["source_file"]
                 and c["start_line"] == args["start_line"] and c["end_line"] == args["end_line"]
                 and c["excerpt_sha256"] == expected["reference_excerpt_sha256"]]
    if len(citations) != 1:
        raise ValueError("Raw-source call must identify exactly one reviewed citation")
    citation = citations[0]
    item = next(s for s in raw_sources if "Sources/" + s["rel_path"] == citation["path"])
    module_name, repo_path = citation["path"].removeprefix("Sources/").split("/", 1)
    source_root = ROOT / "Sources" / module_name
    original = git("show", citation["commit"] + ":" + repo_path, cwd=source_root)
    excerpt = "\n".join(original.splitlines()[citation["start_line"] - 1:citation["end_line"]])
    current = git("show", item["source_commit"] + ":" + repo_path, cwd=source_root)
    start, end = relocate_excerpt(current, excerpt, citation["excerpt_sha256"])
    resolved = deepcopy(call)
    resolved["arguments"].update(start_line=start, end_line=end)
    return resolved, {
        "source_file": citation["path"], "reference_commit": citation["commit"],
        "source_commit": item["source_commit"], "reference_start_line": citation["start_line"],
        "reference_end_line": citation["end_line"], "start_line": start, "end_line": end,
        "relocated": (start, end) != (citation["start_line"], citation["end_line"]),
        "excerpt_sha256": citation["excerpt_sha256"],
    }


def run(output):
    suite = json.loads((ROOT / "evals/stage_b_core_20.json").read_text())
    cases = suite["cases"]
    assert len(cases) == 20 and len({c["id"] for c in cases}) == 20
    assert {c["domain"] for c in cases} == DOMAINS
    data = json.loads((ROOT / "mcp/data/wiki_graph.json").read_text())
    fixture = json.loads((ROOT / suite["replay_fixture"]).read_text())
    historical = json.loads(git("show", fixture["baseline"] + ":mcp/data/wiki_graph.json"))
    for node_id, node in fixture["nodes"].items():
        assert historical["nodes"][node_id] == node, "Replay must match real Git baseline"
    spec = importlib.util.spec_from_file_location("stage_b_server", ROOT / "mcp/server.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    server = module.SpacemitMCPServer()
    requests, python, context, source_checks = [], [], [], []
    citation_results = {}
    for case in cases:
        assert all(case.get(k) for k in ("question", "product_version", "reference_answer", "citations", "calls"))
        for citation in case["citations"]:
            module_name, repo_path = citation["path"].removeprefix("Sources/").split("/", 1)
            blob = git("show", citation["commit"] + ":" + repo_path, cwd=ROOT / "Sources" / module_name)
            lines = blob.splitlines()
            excerpt = "\n".join(lines[citation["start_line"] - 1:citation["end_line"]])
            assert digest(excerpt) == citation["excerpt_sha256"], citation
            citation_results[citation["path"] + ":" + str(citation["start_line"])] = "pinned excerpt checked"
        for call in case["calls"]:
            try:
                call, source_check = resolve_raw_call(call, case["citations"], data["raw_sources"])
            except (ValueError, KeyError, StopIteration, subprocess.CalledProcessError) as exc:
                source_check = {"error": str(exc) or type(exc).__name__,
                                "source_file": call["expect"].get("source_file")}
            replay = call.get("replay_node")
            server.nodes = dict(data["nodes"])
            if replay:
                server.nodes[replay] = fixture["nodes"][replay]
            result = server.handle_tool_call(call["name"], call["arguments"])
            requests.append(call)
            python.append(result)
            context.append(case["id"])
            source_checks.append(source_check)
    worker = json.loads(subprocess.check_output(
        ["node", "--disable-warning=ExperimentalWarning", str(ROOT / "scripts/eval_stage_b_worker.cjs")],
        input=json.dumps({"calls": requests, "fixture": fixture}), cwd=ROOT, text=True,
    ))
    assert len(worker) == len(requests)
    rows = {case["id"]: {**case, "actual": [], "failures": []} for case in cases}
    for call, py, cf, case_id, source_check in zip(requests, python, worker, context, source_checks):
        row = rows[case_id]
        try:
            assert not (source_check or {}).get("error"), source_check
            assert not py.get("isError"), py
            assert not cf.get("isError"), cf
            actual = normalize(py, call["name"])
            assert normalize(cf, call["name"]) == actual, "Python/Worker mismatch"
            text = json.dumps(actual, ensure_ascii=False)
            expected = call["expect"]
            for part in expected.get("contains", []):
                assert part in text, "Missing evidence: " + part
            for part in expected.get("not_contains", []):
                assert part not in text, "Unexpected assertion: " + part
            if expected.get("empty"):
                assert actual == [], "Expected honest miss"
            codes = [n["code"] for n in actual.get("agent_notice", [])] if isinstance(actual, dict) else []
            assert set(expected.get("notices", [])) <= set(codes), codes
            assert not set(expected.get("not_notices", [])) & set(codes), codes
            for key, value in expected.get("metadata", {}).items():
                assert actual.get(key) == value, (key, actual.get(key), value)
            if "source_file" in expected:
                item = next(s for s in data["raw_sources"] if "Sources/" + s["rel_path"] == expected["source_file"])
                assert actual["source_commit"] == item["source_commit"], "Must read the index-pinned source"
                assert digest(actual["content"]) == expected["reference_excerpt_sha256"], "Source excerpt changed; review the pinned rubric before updating it"
            # Preserve exact matched evidence and notices, plus a digest of the
            # full result; do not duplicate entire node bodies in the report.
            row["actual"].append({
                "tool": call["name"], "arguments": call["arguments"],
                "mode": "historical replay" if call.get("replay_node") else "current index",
                "python_worker_equal": True, "matched_evidence": expected.get("contains", []),
                "notice_codes": codes, "empty": actual == [],
                "response_sha256": digest(text),
                "source_check": source_check,
                "metadata": {k: actual[k] for k in ("freshness", "verification_status", "status", "source_commit", "start_line", "end_line") if isinstance(actual, dict) and k in actual},
            })
        except (AssertionError, KeyError, ValueError) as exc:
            row["failures"].append(f"{call['name']} {call['arguments']}: {exc}")
    results = list(rows.values())
    for row in results:
        row["tool_calls_per_backend"] = len(row["calls"])
        row["passed"] = not row["failures"]
    report = {
        "evaluation": "retrieval evidence / metadata / notices / pinned sources / Python-Worker parity",
        "limitations": "No independent LLM answer generation or scoring; reference answers are AI source-review rubrics, not measured model accuracy. No hardware execution.",
        "suite_sha256": digest((ROOT / "evals/stage_b_core_20.json").read_text()),
        "content_sha256": data["build_meta"]["content_sha256"],
        "replay_baseline": fixture["baseline"], "domains": sorted(DOMAINS),
        "passed": sum(r["passed"] for r in results), "total": len(results),
        "tool_calls_per_backend": len(requests), "pinned_excerpts_checked": len(citation_results),
        "results": results,
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "core_20_results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    md = ["# 阶段 B：20 题工具与来源评测", "", f"通过 {report['passed']}/20；覆盖 6 个 domain；每端 {len(requests)} 次工具调用。", "", "验证检索证据、固定来源、状态提示和双端一致性；参考答复是本轮 AI 的来源审核判据。未运行独立问答模型，不代表模型准确率，也未实物执行。stale/unknown 使用真实 Git 基线回放，不改变当前线上索引。", "", "| 题号 | 问题 | domain | 调用/端 | 实际结果 |", "| --- | --- | --- | ---: | --- |"]
    for r in results:
        md.append(f"| {r['id']} | {r['question']} | {r['domain']} | {len(r['calls'])} | {'通过' if r['passed'] else '失败：' + str(r['failures'])} |")
    md += ["", "逐题固定 SHA、行范围、适用版本、参考答复、实际匹配证据和 notice 见 [完整 JSON](core_20_results.json)。", ""]
    (output / "core_20_results.md").write_text("\n".join(md))
    print(json.dumps({k: report[k] for k in ("passed", "total", "tool_calls_per_backend", "pinned_excerpts_checked")}, ensure_ascii=False))
    for row in results:
        if not row["passed"]:
            print(row["id"], row["failures"], file=sys.stderr)
    return report["passed"] == 20


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "reports/stage_b")
    args = parser.parse_args()
    sys.exit(0 if run(args.output) else 1)
