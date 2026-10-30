#!/usr/bin/env python3
"""Keep source-sync evaluations strict about content, tolerant of line movement."""
import unittest
from unittest.mock import patch

import eval_stage_b as evaluation


class SourceExcerptTests(unittest.TestCase):
    excerpt = "## Boot\n01 = SPI NOR\n10 = SPI NAND"

    def test_revision_rows_can_move_an_unchanged_excerpt(self):
        blob = "# Guide\nNew revision row\n\n" + self.excerpt + "\n\nNext section\n"
        self.assertEqual(evaluation.relocate_excerpt(
            blob, self.excerpt, evaluation.digest(self.excerpt)), (4, 6))

    def test_changed_boot_mapping_still_blocks_release(self):
        blob = self.excerpt.replace("01 = SPI NOR", "01 = SPI NAND")
        with self.assertRaisesRegex(ValueError, "changed or disappeared"):
            evaluation.relocate_excerpt(blob, self.excerpt, evaluation.digest(self.excerpt))

    def test_duplicate_excerpt_requires_review(self):
        blob = self.excerpt + "\n\n" + self.excerpt
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            evaluation.relocate_excerpt(blob, self.excerpt, evaluation.digest(self.excerpt))

    def test_invalid_reference_hash_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "digest"):
            evaluation.relocate_excerpt(self.excerpt, self.excerpt, "0" * 64)

    def test_call_uses_index_commit_and_records_both_locations(self):
        source_file = "Sources/docs-chip/guide.md"
        call = {
            "name": "read_raw_source_file",
            "arguments": {"file_path_or_url": source_file, "start_line": 1, "end_line": 3},
            "expect": {"source_file": source_file,
                       "reference_excerpt_sha256": evaluation.digest(self.excerpt)},
        }
        citation = {"path": source_file, "commit": "reviewed", "start_line": 1,
                    "end_line": 3, "excerpt_sha256": evaluation.digest(self.excerpt)}
        sources = [{"rel_path": "docs-chip/guide.md", "source_commit": "index-pinned"}]
        with patch.object(evaluation, "git", side_effect=[self.excerpt, "New revision\n" + self.excerpt]) as git:
            resolved, check = evaluation.resolve_raw_call(call, [citation], sources)
        self.assertEqual(git.call_args_list[0].args, ("show", "reviewed:guide.md"))
        self.assertEqual(git.call_args_list[1].args, ("show", "index-pinned:guide.md"))
        self.assertEqual((resolved["arguments"]["start_line"], resolved["arguments"]["end_line"]), (2, 4))
        self.assertEqual(call["arguments"]["start_line"], 1)
        self.assertEqual(check["reference_start_line"], 1)
        self.assertEqual(check["source_commit"], "index-pinned")
        self.assertTrue(check["relocated"])


if __name__ == "__main__":
    unittest.main()
