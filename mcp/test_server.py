#!/usr/bin/env python3
"""Regression tests against the actual stdio server, with no network writes."""

import importlib.util
import io
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch, mock_open

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("wiki_server", ROOT / "mcp/server.py")
server = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(server)


def node(node_id, kind="evidence", **metadata):
    base = dict(id=node_id, title=node_id, type=kind, domain="test", status="needs_review",
                aliases=[], content="needle", summary="summary", outlinks=[], backlinks=[],
                target_audience=[])
    base.update(metadata)
    return base


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.wiki = server.SpacemitMCPServer()

    def call(self, tool, args):
        result = self.wiki.handle_tool_call(tool, args)
        self.assertFalse(result.get("isError"), result)
        return json.loads(result["content"][0]["text"])

    def test_wiki_ranking_and_stable_ties(self):
        self.wiki.nodes = {key: node(key) for key in ["incidental", "needle_second", "needle_first"]}
        result = self.call("search_wiki", {"query": "needle"})
        self.assertEqual([x["id"] for x in result], ["needle_second", "needle_first", "incidental"])
        self.assertEqual([x["score"] for x in result], [29.4, 29.4, 5.3])

    def test_raw_ranking_and_stable_ties(self):
        self.wiki.raw_sources = [dict(submodule="docs-chip", file_name=name, rel_path=name,
                                      repo_path=name, title=name, headers=[], summary="needle", raw_url=name)
                                 for name in ["incidental", "needle_second", "needle_first"]]
        result = self.call("search_raw_sources", {"query": "needle"})
        self.assertEqual([x["file_path"] for x in result], ["needle_second", "needle_first", "incidental"])

    def test_types_ambiguity_empty_and_alias_collisions(self):
        self.wiki.nodes = {"K3_journey": node("K3_journey", "developer_journey"),
                           "K3_fact_a": node("K3_fact_a"), "K3_fact_b": node("K3_fact_b")}
        for query in ["K3", "K3_journey", "", " ", ".md"]:
            with self.subTest(query=query):
                self.assertTrue(self.wiki.handle_tool_call("get_evidence_fact", {"spec_name": query}).get("isError"))
        self.assertEqual(self.call("get_evidence_fact", {"spec_name": "K3_fact_a.md"})["type"], "evidence")
        for item in self.wiki.nodes.values():
            item["aliases"] = ["shared"]
        self.assertTrue(self.wiki.handle_tool_call("get_evidence_fact", {"spec_name": "shared"}).get("isError"))

    def test_status_and_provenance_are_preserved(self):
        metadata = dict(verification_status="unverified", external_use=False,
                        source_file=["Sources/docs-chip/example.md"], source_commit="abc",
                        source_section="voltage", source_locator="example.md:10-20",
                        source_resolution="partial", source_note="measurement conditions need review",
                        source_checked_at="2026-10-13", source_related_file="Sources/docs-chip/related.md",
                        source_related_commit="def",
                        freshness="stale", stale_paths=["Sources/docs-chip/example.md"], unknown_paths=[],
                        checked_against_commit={"docs-chip": "new"}, source_freshness=[{"freshness": "stale"}],
                        metric_source_resolution="unresolved", thermal_source_resolution="unresolved",
                        chip="K3", product="test board", verified_at="2026-10-01", conflicts=["needs review"],
                        source_origin="GitHub", source_tier="tier_1", effective_until="2026-12-01")
        self.wiki.nodes = {"fact": node("fact", **metadata)}
        fact_res = self.call("get_evidence_fact", {"spec_name": "fact"})
        for key, value in dict(metadata, status="needs_review").items():
            self.assertEqual(fact_res[key], value)

        search_res = self.call("search_wiki", {"query": "fact"})[0]
        for key in ("id", "title", "type", "domain", "score", "status", "freshness", "verification_status", "summary", "hint"):
            self.assertIn(key, search_res)
        self.assertEqual(search_res["freshness"], "stale")
        self.assertEqual(search_res["verification_status"], "unverified")
        self.assertNotIn("source_freshness", search_res)
        self.assertNotIn("metric_source_resolution", search_res)
        self.assertNotIn("source_file", search_res)

    def test_multi_token_search_and_generation_anchor(self):
        self.wiki.nodes = {
            "k3_strap": node("k3_strap", title="K3 启动模式与 Strap 管脚配置", chip="K3"),
            "k1_strap": node("k1_strap", title="K1 启动模式与 Strap 管脚配置", chip="K1")
        }
        res_k3 = self.call("search_wiki", {"query": "K3 Strap 启动"})
        self.assertEqual(res_k3[0]["id"], "k3_strap")

        res_k1 = self.call("search_wiki", {"query": "K1 启动模式"})
        self.assertEqual(res_k1[0]["id"], "k1_strap")

    def test_self_describing_notices_and_search_hints_preserve_evidence(self):
        cases = json.loads((ROOT / "mcp/notice_cases.json").read_text())
        for case in cases:
            for kind, tool, parameter, content in [
                ("evidence", "get_evidence_fact", "spec_name", "full_table_content"),
                ("knowledge_atom", "read_knowledge_atom", "atom_name", "full_markdown_content"),
                ("developer_journey", "get_developer_journey", "board_or_task", "full_markdown_content"),
            ]:
                with self.subTest(case=case["id"], kind=kind):
                    item = node(case["id"], kind)
                    item.update(case["metadata"])
                    self.wiki.nodes = {item["id"]: item}
                    result = self.call(tool, {parameter: item["id"]})
                    self.assertEqual([n["code"] for n in result["agent_notice"]], case["codes"])
                    self.assertEqual(result[content], item["content"])
                    self.assertEqual(result["verification_status"], item["verification_status"])
                    summary = self.call("search_wiki", {"query": item["id"]})[0]
                    for code in case["codes"]:
                        self.assertIn(code, summary["hint"])
                    self.assertNotIn("agent_notice", summary)
                    if item["freshness"] == "stale":
                        self.assertEqual(result["agent_notice"][0]["source_paths"], item.get("stale_paths", []))

    def raw_fixture(self):
        item = dict(submodule="docs-ros", file_name="平台 概览.md", rel_path="docs-ros/zh/平台 概览.md",
                    repo_path="zh/平台 概览.md", source_commit="a" * 40,
                    raw_url="https://raw.githubusercontent.com/spacemit-com/docs-ros/" + "a" * 40 + "/zh/平台 概览.md")
        self.wiki.raw_sources = [item]
        return item

    def test_missing_local_source_uses_encoded_pinned_url(self):
        item = self.raw_fixture()
        with patch.object(self.wiki, "local_source_matches", return_value=False), \
                patch.object(server.urllib.request, "urlopen", return_value=io.BytesIO(b"one\ntwo\nthree\n")) as fetch:
            result = self.call("read_raw_source_file", {"file_path_or_url": item["raw_url"].replace("a" * 40, "main"), "start_line": 2, "end_line": 2})
            url = fetch.call_args[0][0].full_url
        self.assertIn("%20", url)
        self.assertIn("%E5%B9%B3", url)
        self.assertIn("/" + "a" * 40 + "/", url)
        self.assertEqual(result["content"], "two")
        self.assertEqual(result["source_commit"], "a" * 40)
        self.assertEqual(result["origin"], "github")

    def test_unknown_source_and_invalid_range_do_not_fetch(self):
        item = self.raw_fixture()
        cases = [{"file_path_or_url": "https://example.com/file"}, {"file_path_or_url": "../AGENTS.md"}]
        cases += [{"file_path_or_url": item["rel_path"], "start_line": value} for value in [0, -1, 1.5, True, None, "1"]]
        cases.append({"file_path_or_url": item["rel_path"], "start_line": 3, "end_line": 2})
        with patch.object(server.urllib.request, "urlopen") as fetch:
            for args in cases:
                with self.subTest(args=args):
                    self.assertTrue(self.wiki.handle_tool_call("read_raw_source_file", args).get("isError"))
            fetch.assert_not_called()

    def test_local_revision_and_dirty_file_check(self):
        item = self.raw_fixture()
        for revision, dirty, expected in [("a" * 40, "", True), ("b" * 40, "", False), ("a" * 40, " M file", False)]:
            results = [subprocess.CompletedProcess([], 0, revision, ""), subprocess.CompletedProcess([], 0, dirty, "")]
            with patch.object(server.os.path, "isfile", return_value=True), patch.object(server.subprocess, "run", side_effect=results):
                self.assertEqual(self.wiki.local_source_matches(item, "/fake/source"), expected)

    def test_default_page_and_continuation(self):
        item = self.raw_fixture()
        body = "\n".join(str(i) for i in range(1, 451)).encode()
        with patch.object(self.wiki, "local_source_matches", return_value=False), \
                patch.object(server.urllib.request, "urlopen", side_effect=lambda *a, **k: io.BytesIO(body)):
            result = self.call("read_raw_source_file", {"file_path_or_url": item["rel_path"]})
            self.assertEqual(len(result["content"].splitlines()), 200)
            self.assertEqual(result["end_line"], 200)
            self.assertTrue(result["has_more"])
            self.assertEqual(result["next_start_line"], 201)
            second = self.call("read_raw_source_file", dict(file_path_or_url=item["rel_path"], start_line=result["next_start_line"]))
            last = self.call("read_raw_source_file", dict(file_path_or_url=item["rel_path"], start_line=second["next_start_line"]))
        self.assertEqual(second["content"].splitlines()[0], "201")
        self.assertEqual(last["content"].splitlines(), [str(i) for i in range(401, 451)])
        self.assertFalse(last["has_more"])
        self.assertIsNone(last["next_start_line"])

    def test_explicit_window_is_capped_at_500_on_local_reads(self):
        item = self.raw_fixture()
        with patch.object(self.wiki, "local_source_matches", return_value=True), \
                patch("builtins.open", mock_open(read_data="line\n" * 1200)):
            for options in ({"start_line": 10, "end_line": 1200}, {"end_line": 1200}):
                result = self.call("read_raw_source_file", dict(file_path_or_url=item["rel_path"], **options))
                self.assertEqual(len(result["content"].splitlines()), 500)
                self.assertEqual(result["end_line"], options.get("start_line", 1) + 499)
                self.assertEqual(result["next_start_line"], result["end_line"] + 1)
                self.assertEqual(result["origin"], "local")

    def test_page_boundaries_empty_eof_and_line_endings(self):
        item = self.raw_fixture()
        cases = [("", {}, 0, 0, False), ("one\r\ntwo\rthree\n", {}, 3, 3, False),
                 ("line\n" * 200, {}, 200, 200, False),
                 ("line\n" * 201, {}, 200, 200, True),
                 ("one\ntwo\n", {"start_line": 3}, 0, 2, False),
                 ("line\n" * 800, {"start_line": 2, "end_line": 2}, 1, 2, True)]
        for body, options, count, end, has_more in cases:
            with self.subTest(options=options, length=len(body)), \
                    patch.object(self.wiki, "local_source_matches", return_value=False), \
                    patch.object(server.urllib.request, "urlopen", return_value=io.BytesIO(body.encode())):
                result = self.call("read_raw_source_file", dict(file_path_or_url=item["rel_path"], **options))
                self.assertEqual(len(result["content"].splitlines()), count)
                self.assertEqual(result["end_line"], end)
                self.assertEqual(result["has_more"], has_more)
                self.assertEqual(result["next_start_line"], end + 1 if has_more else None)


if __name__ == "__main__":
    unittest.main()
