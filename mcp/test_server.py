#!/usr/bin/env python3
"""Regression tests against the actual stdio server, with no network writes."""

import importlib.util
import io
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("wiki_server", ROOT / "mcp/server.py")
server = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(server)


def node(node_id, kind="evidence", **metadata):
    return dict(id=node_id, title=node_id, type=kind, domain="test", status="needs_review",
                aliases=[], content="needle", summary="summary", outlinks=[], backlinks=[],
                target_audience=[], **metadata)


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
        self.assertEqual([x["score"] for x in result], [13, 13, 3])

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
                        metric_source_resolution="unresolved", thermal_source_resolution="unresolved",
                        chip="K3", product="test board", verified_at="2026-10-01", conflicts=["needs review"],
                        source_origin="GitHub", source_tier="tier_1", effective_until="2026-12-01")
        self.wiki.nodes = {"fact": node("fact", **metadata)}
        results = [self.call("get_evidence_fact", {"spec_name": "fact"}),
                   self.call("search_wiki", {"query": "fact"})[0]]
        for result in results:
            for key, value in dict(metadata, status="needs_review").items():
                self.assertEqual(result[key], value)

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

    def test_no_range_keeps_full_read_compatibility(self):
        item = self.raw_fixture()
        body = ("line\n" * 300).encode()
        with patch.object(self.wiki, "local_source_matches", return_value=False), \
                patch.object(server.urllib.request, "urlopen", return_value=io.BytesIO(body)):
            result = self.call("read_raw_source_file", {"file_path_or_url": item["rel_path"]})
        self.assertEqual(len(result["content"].splitlines()), 300)


if __name__ == "__main__":
    unittest.main()
