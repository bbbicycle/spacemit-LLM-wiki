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
from datetime import datetime

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

    def test_build_records_input_commit_time_pins_and_metadata(self):
        evidence = self.root / "Evidence" / "evidence.md"
        self.write_document(evidence, extra=(
            "verification_status: unverified\nexternal_use: false\n"
            "source_file: Sources/docs-chip/hardware 中文.md\nsource_section: Boot\n"
            "verified_at: 2026-01-01\nchip: K1\nconflicts: pending\n"
        ))
        payload = self.build()
        timestamp = datetime.fromisoformat(payload["generated_at"])
        self.assertEqual(int(timestamp.timestamp()), int(git(self.root, "show", "-s", "--format=%ct", payload["wiki_commit"])))
        self.assertEqual(payload["build_meta"]["wiki_commit"], payload["wiki_commit"])
        self.assertEqual(payload["build_meta"]["content_sha256"], payload["content_sha256"])
        self.assertEqual(payload["build_meta"]["counts"], dict(total_nodes=3, developer_journeys=1, knowledge_atoms=1, evidence=1, raw_sources=5))
        self.assertEqual(payload["build_meta"]["freshness_summary"], dict(current=0, stale=0, unknown=3))
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

    def commit_inputs(self):
        git(self.root, "add", "Developer_Journeys", "Knowledge_Atoms", "Evidence", "Sources")
        git(self.root, "commit", "-qm", "indexed inputs")

    def test_repeated_builds_and_output_or_docs_commits_are_byte_identical(self):
        self.commit_inputs()
        payload = self.build()
        self.assertFalse(payload["wiki_worktree_dirty"])
        original = self.snapshot()
        for if_changed in (False, True):
            self.build(if_changed=if_changed)
            self.assertEqual(self.snapshot(), original)
        git(self.root, "add", "mcp", "mcp-worker")
        git(self.root, "commit", "-qm", "generated indexes")
        (self.root / "README.md").write_text("operational documentation changed\n", encoding="utf-8")
        self.build()
        self.assertEqual(self.snapshot(), original)
        git(self.root, "add", "README.md")
        git(self.root, "commit", "-qm", "docs only")
        self.build()
        self.assertEqual(self.snapshot(), original)
        self.assertNotEqual(payload["wiki_commit"], git(self.root, "rev-parse", "HEAD"))
        with contextlib.redirect_stdout(io.StringIO()):
            builder.check_indexes(str(self.root))
        # A clean checkout with no preexisting output must reproduce the bytes.
        for path in builder.index_paths(str(self.root)):
            Path(path).unlink()
        self.build()
        self.assertEqual(self.snapshot(), original)

    def test_input_changes_update_provenance_and_dirty_scope(self):
        self.commit_inputs()
        first = self.build()
        self.write_document(self.root / "Evidence/evidence.md", body="revised fact")
        dirty = self.build()
        self.assertTrue(dirty["wiki_worktree_dirty"])
        self.assertNotEqual(first["content_sha256"], dirty["content_sha256"])
        self.commit_inputs()
        clean = self.build()
        self.assertFalse(clean["wiki_worktree_dirty"])
        self.assertNotEqual(first["wiki_commit"], clean["wiki_commit"])
        self.assertEqual(clean["content_sha256"], dirty["content_sha256"])
        self.build()
        self.assertEqual(*self.snapshot())

    def test_check_rejects_forged_metadata_without_writing(self):
        payload = self.build()
        payload["build_meta"]["counts"]["evidence"] += 1
        with contextlib.redirect_stdout(io.StringIO()):
            builder.write_indexes(str(self.root), payload)
        before = self.snapshot()
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(ValueError, "build_meta"):
            builder.check_indexes(str(self.root))
        self.assertEqual(self.snapshot(), before)
        self.build(if_changed=True)
        self.assertEqual(self.build()["build_meta"]["counts"]["evidence"], 1)

    def test_if_changed_rewrites_when_document_content_changes(self):
        self.build()
        original = self.snapshot()
        document = self.root / "Evidence" / "evidence.md"
        document.write_text(document.read_text(encoding="utf-8").replace("Public fact", "Updated fact"), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            builder.build_graph(str(self.root), if_changed=True)
        self.assertNotEqual(self.snapshot(), original)
        self.assertIn("Updated fact", self.snapshot()[0].decode("utf-8"))

    def source_metadata(self, **extra):
        return dict(source_file="Sources/docs-chip/hardware 中文.md",
                    source_commit=self.commits["docs-chip"], verification_status="verified", **extra)

    def change_source(self, name, content="changed", delete=False):
        source = self.root / "Sources" / "docs-chip"
        if delete:
            git(source, "rm", name)
        else:
            (source / name).write_text(content, encoding="utf-8")
            git(source, "add", name)
        git(source, "commit", "-qm", "update")
        return builder.source_versions(str(self.root))

    def freshness(self, metadata, versions=None):
        return builder.calculate_freshness(metadata, str(self.root), versions or self.commits)

    def test_freshness_unchanged_file_at_new_module_commit_is_current(self):
        versions = self.change_source("unrelated.md")
        result = self.freshness(self.source_metadata(), versions)
        self.assertEqual(result["freshness"], "current")
        self.assertEqual(result["stale_paths"], [])
        self.assertEqual(result["checked_against_commit"], {"docs-chip": versions["docs-chip"]})

    def test_freshness_changed_file_is_stale_without_changing_verification(self):
        metadata = self.source_metadata()
        versions = self.change_source("hardware 中文.md")
        self.write_document(self.root / "Evidence" / "evidence.md", extra="".join(f"{k}: {v}\n" for k, v in metadata.items()))
        node = self.build()["nodes"]["evidence"]
        self.assertEqual(node["freshness"], "stale")
        self.assertEqual(node["stale_paths"], [metadata["source_file"]])
        self.assertEqual(node["verification_status"], "verified")
        self.assertEqual(node["source_commit"], self.commits["docs-chip"])

    def test_freshness_deleted_file_is_stale(self):
        versions = self.change_source("hardware 中文.md", delete=True)
        self.assertEqual(self.freshness(self.source_metadata(), versions)["freshness"], "stale")

    def test_freshness_unavailable_history_and_missing_baseline_are_unknown(self):
        for value in ({}, dict(source_file="Sources/docs-chip/hardware 中文.md"),
                      dict(source_file="Sources/docs-chip/hardware 中文.md", source_commit="f" * 40),
                      dict(source_file="Sources/docs-chip/missing.md", source_commit=self.commits["docs-chip"]),
                      dict(source_file="../private.md", source_commit=self.commits["docs-chip"])):
            with self.subTest(metadata=value):
                self.assertEqual(self.freshness(value)["freshness"], "unknown")

    def test_freshness_related_sources_use_their_own_revisions(self):
        related = "Sources/docs-chip/related.md"
        versions = self.change_source("related.md", "initial")
        metadata = self.source_metadata(source_related_file=[related], source_related_commit=[versions["docs-chip"]])
        versions = self.change_source("related.md", "new fact")
        result = self.freshness(metadata, versions)
        self.assertEqual(result["freshness"], "stale")
        self.assertEqual(result["stale_paths"], [related])
        self.assertEqual(result["source_freshness"][0]["freshness"], "current")

    def test_missing_related_revision_does_not_inherit_primary_revision(self):
        metadata = self.source_metadata(source_related_file="Sources/docs-chip/hardware 中文.md")
        result = self.freshness(metadata)
        self.assertEqual(result["freshness"], "unknown")
        self.assertEqual(result["unknown_paths"], [metadata["source_file"]])

    def test_source_lists_are_parsed_and_report_contains_maintenance_queue(self):
        self.write_document(self.root / "Evidence" / "evidence.md", extra=(
            'source_file:\n  - "Sources/docs-chip/hardware 中文.md"\n'
            f'source_commit: ["{self.commits["docs-chip"]}"]\n'
            'source_related_file: ["Sources/docs-ai/hardware 中文.md"]\n'
            f'source_related_commit: ["{self.commits["docs-ai"]}"]\n'
        ))
        self.change_source("hardware 中文.md")
        payload = self.build()
        report = builder.freshness_report(payload)
        self.assertEqual(report["summary"], dict(current=0, stale=1, unknown=2))
        self.assertEqual(report["nodes"][2]["id"], "evidence")


if __name__ == "__main__":
    unittest.main()
