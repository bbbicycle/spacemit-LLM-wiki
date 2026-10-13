#!/usr/bin/env python3
"""Exercise the production builder using isolated local Git fixtures; no network."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone

spec = importlib.util.spec_from_file_location("build_mcp_index", Path(__file__).with_name("build_mcp_index.py"))
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def git(path, *args):
    return subprocess.run(
        ["git", "-C", str(path), "-c", "user.name=Index Test", "-c", "user.email=index-test@example.invalid", *args],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


class BuilderTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        git(self.root, "init", "-q")
        (self.root / "README.md").write_text("index fixture\n", encoding="utf-8")
        git(self.root, "add", "README.md")
        git(self.root, "commit", "-qm", "fixture")
        self.commits = {}
        for name in builder.SUBMODULE_REPOS:
            source = self.root / "Sources" / name
            source.mkdir(parents=True)
            git(source, "init", "-q")
            (source / "hardware 中文.md").write_text("# Hardware\n\n## Boot\n\nfixture fact\n", encoding="utf-8")
            git(source, "add", ".")
            git(source, "commit", "-qm", "source fixture")
            self.commits[name] = git(source, "rev-parse", "HEAD")
        for doc_type, default in builder.TARGET_DIRS.items():
            folder = self.root / Path(default).name
            folder.mkdir()
            self.write_document(folder / f"{doc_type}.md", doc_type)

    def write_document(self, path, doc_type="evidence", extra="", body="Public fact"):
        path.write_text(
            f"---\ntype: {doc_type}\ntitle: {path.stem}\nstatus: needs_review\n"
            f"domain: chip_product_specs\naliases: [{path.stem} alias]\n{extra}---\n# {path.stem}\n\n{body}\n",
            encoding="utf-8",
        )

    def build(self, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return builder.build_graph(str(self.root), **kwargs)

    def snapshot(self):
        return [Path(path).read_bytes() for path in builder.index_paths(str(self.root))]

    def test_build_records_real_time_commit_pins_and_metadata(self):
        evidence = self.root / "Evidence" / "evidence.md"
        self.write_document(evidence, extra=(
            "verification_status: unverified\nexternal_use: false\n"
            "source_file: Sources/docs-chip/hardware 中文.md\nsource_section: Boot\n"
            "verified_at: 2026-01-01\nchip: K1\nconflicts: pending\n"
        ))
        before = datetime.now(timezone.utc).replace(microsecond=0)
        payload = self.build()
        timestamp = datetime.fromisoformat(payload["generated_at"])
        self.assertLessEqual(before, timestamp)
        self.assertLessEqual(timestamp, datetime.now(timezone.utc))
        self.assertEqual(payload["source_versions"], self.commits)
        self.assertEqual(payload["wiki_commit"], git(self.root, "rev-parse", "HEAD"))
        self.assertEqual(len(payload["raw_sources"]), 5)
        for item in payload["raw_sources"]:
            self.assertEqual(item["source_commit"], self.commits[item["submodule"]])
            self.assertIn(f"/{item['source_commit']}/", item["raw_url"])
            self.assertTrue(item["raw_url"].endswith("hardware%20%E4%B8%AD%E6%96%87.md"))
        node = payload["nodes"]["evidence"]
        self.assertIs(node["external_use"], False)
        self.assertEqual(node["verification_status"], "unverified")
        self.assertEqual(node["source_section"], "Boot")
        self.assertEqual(node["conflicts"], "pending")
        self.assertEqual(node["chip"], "K1")
        self.assertEqual(*self.snapshot())
        with contextlib.redirect_stdout(io.StringIO()):
            builder.check_indexes(str(self.root))

    def test_missing_sources_preserves_both_existing_indexes(self):
        self.build()
        original = self.snapshot()
        shutil.rmtree(self.root / "Sources")
        for if_changed in (False, True):
            with self.assertRaisesRegex(ValueError, "未初始化"):
                self.build(if_changed=if_changed)
            self.assertEqual(self.snapshot(), original)

    def test_uninitialized_module_cannot_inherit_parent_git_repository(self):
        self.build()
        original = self.snapshot()
        shutil.rmtree(self.root / "Sources" / "docs-chip" / ".git")
        with self.assertRaisesRegex(ValueError, "未初始化"):
            self.build()
        self.assertEqual(self.snapshot(), original)

    def test_dirty_and_empty_modules_preserve_indexes(self):
        self.build()
        original = self.snapshot()
        source = self.root / "Sources" / "docs-chip"
        document = source / "hardware 中文.md"
        document.write_text("changed data", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "未提交修改"):
            self.build()
        self.assertEqual(self.snapshot(), original)
        git(source, "rm", "-f", document.name)
        git(source, "commit", "-qm", "empty source")
        with self.assertRaisesRegex(ValueError, "没有可索引"):
            self.build()
        self.assertEqual(self.snapshot(), original)

    def test_untracked_source_documents_are_not_advertised_at_commit_url(self):
        (self.root / "Sources" / "docs-chip" / "local.md").write_text("local only", encoding="utf-8")
        payload = self.build()
        self.assertFalse(any(item["file_name"] == "local.md" for item in payload["raw_sources"]))

    def test_private_documents_are_excluded_but_unverified_facts_remain(self):
        policies = [
            "source_tier: tier_2_internal_approved\n",
            "source_tier: tier_3_field_feedback\n",
            "price_nature: nda_confidential\n",
            "publication: false\n",
            "visibility: internal\n",
            "publication: false # internal review\n",
            "price_nature: nda_confidential # business terms\n",
        ]
        for index, policy in enumerate(policies):
            self.write_document(self.root / "Evidence" / f"private_{index}.md", extra=policy, body="DO_NOT_PUBLISH")
        self.write_document(self.root / "Evidence" / "evidence.md", extra="verification_status: unverified\nexternal_use: false\n")
        payload = self.build()
        encoded = json.dumps(payload)
        self.assertNotIn("DO_NOT_PUBLISH", encoded)
        self.assertNotIn("private_", encoded)
        self.assertIn("evidence", payload["nodes"])

    def test_public_reference_to_private_document_blocks_publication(self):
        self.build()
        original = self.snapshot()
        self.write_document(self.root / "Evidence" / "private.md", extra="publication: false\n")
        self.write_document(self.root / "Knowledge_Atoms" / "knowledge_atom.md", "knowledge_atom", body="See [[Evidence/private]].")
        with self.assertRaisesRegex(ValueError, "引用了非公开节点"):
            self.build()
        self.assertEqual(self.snapshot(), original)

    def assert_invalid_frontmatter_preserves_indexes(self, fields):
        self.build()
        original = self.snapshot()
        self.write_document(self.root / "Evidence" / "private.md", extra=fields, body="DO_NOT_PUBLISH")
        for if_changed in (False, True):
            with self.assertRaisesRegex(ValueError, "Frontmatter"):
                self.build(if_changed=if_changed)
            self.assertEqual(self.snapshot(), original)

    def test_folded_publication_policy_cannot_bypass_filter(self):
        self.assert_invalid_frontmatter_preserves_indexes("publication: >-\n  false\n")

    def test_folded_internal_source_tier_cannot_bypass_filter(self):
        self.assert_invalid_frontmatter_preserves_indexes("source_tier: >-\n  tier_2_internal_approved\n")

    def test_nested_policy_cannot_override_top_level_publication(self):
        self.assert_invalid_frontmatter_preserves_indexes("publication: false\nexample:\n  publication: true\n")

    def test_duplicate_top_level_policy_aborts_without_replacing_indexes(self):
        self.assert_invalid_frontmatter_preserves_indexes("publication: false\npublication: true\n")

    def test_supported_flat_frontmatter_preserves_lists_comments_and_empty_values(self):
        document = self.root / "Evidence" / "evidence.md"
        document.write_text(
            '---\ntype: evidence\ntitle: "Quoted # title" # comment\n'
            'status: needs_review\nexternal_use: true # reviewed\nsource_note:\n'
            'aliases:\n  - "Name, one"\n  - \'Author\'\'s label\' # comment\n'
            'target_audience: ["PCB, layout", Software] # comment\n'
            'source_origin: https://github.com/spacemit-com/docs-chip\n'
            '---\nPublic fact\n', encoding="utf-8",
        )
        payload = self.build()
        node = payload["nodes"]["evidence"]
        self.assertEqual(node["aliases"], ["Name, one", "Author's label"])
        self.assertEqual(node["target_audience"], ["PCB, layout", "Software"])
        self.assertEqual(node["title"], "Quoted # title")
        self.assertIs(node["external_use"], True)
        self.assertEqual(node["source_note"], "")
        self.assertEqual(node["source_origin"], "https://github.com/spacemit-com/docs-chip")

    def test_check_detects_stale_content_and_never_writes(self):
        self.build()
        original = self.snapshot()
        self.write_document(self.root / "Evidence" / "evidence.md", body="updated fact")
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(ValueError, "nodes 已过期"):
            builder.check_indexes(str(self.root))
        self.assertEqual(self.snapshot(), original)

    def test_check_detects_source_commit_changes(self):
        self.build()
        original = self.snapshot()
        source = self.root / "Sources" / "docs-ai"
        (source / "hardware 中文.md").write_text("# Updated hardware\n", encoding="utf-8")
        git(source, "add", ".")
        git(source, "commit", "-qm", "source update")
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(ValueError, "source_versions 已过期"):
            builder.check_indexes(str(self.root))
        self.assertEqual(self.snapshot(), original)

    def test_check_detects_divergent_worker_index(self):
        self.build()
        worker = Path(builder.index_paths(str(self.root))[1])
        payload = json.loads(worker.read_text(encoding="utf-8"))
        payload["nodes"]["evidence"]["content"] = "stale Worker content"
        worker.write_text(json.dumps(payload), encoding="utf-8")
        original = self.snapshot()
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(ValueError, "不一致"):
            builder.check_indexes(str(self.root))
        self.assertEqual(self.snapshot(), original)

    def test_if_changed_preserves_bytes_when_content_is_unchanged(self):
        payload = self.build()
        payload["generated_at"] = "2020-01-01T00:00:00+00:00"
        payload["wiki_commit"] = "previous-build-commit"
        payload["wiki_worktree_dirty"] = not payload["wiki_worktree_dirty"]
        with contextlib.redirect_stdout(io.StringIO()):
            builder.write_indexes(str(self.root), payload)
        original = self.snapshot()
        with contextlib.redirect_stdout(io.StringIO()):
            builder.build_graph(str(self.root), if_changed=True)
        self.assertEqual(self.snapshot(), original)

    def test_if_changed_rewrites_when_document_content_changes(self):
        self.build()
        original = self.snapshot()
        document = self.root / "Evidence" / "evidence.md"
        document.write_text(document.read_text(encoding="utf-8").replace("Public fact", "Updated fact"), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            builder.build_graph(str(self.root), if_changed=True)
        self.assertNotEqual(self.snapshot(), original)
        self.assertIn("Updated fact", self.snapshot()[0].decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
