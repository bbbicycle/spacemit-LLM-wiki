#!/usr/bin/env python3
"""用临时 Git 仓库验证基线、来源关系、传递影响与删除/重命名。"""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from check_upstream_impact import analyze, build_reference_map, current_pointers, main, SUBMODULES
from test_build_mcp_index import git


class ImpactTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for module in SUBMODULES:
            directory = self.root / module
            directory.mkdir(parents=True)
            git(directory, 'init', '-q')
            for name in ('事实 中文.md', 'related.md', 'uncovered.md'):
                (directory / name).write_text('# initial\n', encoding='utf-8')
            git(directory, 'add', '.')
            git(directory, 'commit', '-qm', 'initial')
        self.old = current_pointers(self.root)
        for folder in ('Developer_Journeys', 'Knowledge_Atoms', 'Evidence'):
            (self.root / folder).mkdir()

    def write(self, path, text):
        (self.root / path).write_text(text, encoding='utf-8')

    def update(self, callback):
        directory = self.root / 'Sources/docs-chip'
        callback(directory)
        git(directory, 'add', '-A')
        git(directory, 'commit', '-qm', 'update')
        return current_pointers(self.root)

    def run_cli(self, *args):
        with patch('check_upstream_impact.VAULT_ROOT', self.root), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return main(list(args))

    def test_three_source_relations_and_transitive_journey(self):
        self.write('Evidence/fact.md', '---\nsource_file: Sources/docs-chip/事实 中文.md\nsource_related_file: [Sources/docs-chip/related.md]\n---\n')
        self.write('Knowledge_Atoms/md.md', '[source](<../Sources/docs-chip/事实 中文.md#section> "标题")')
        self.write('Knowledge_Atoms/wiki.md', '[[Sources/docs-chip/事实 中文.md#section|出处]]')
        self.write('Knowledge_Atoms/dependent.md', '[[Evidence/fact|证据]]')
        self.write('Developer_Journeys/journey.md', '[[dependent]]')
        references = build_reference_map(self.root)
        self.assertEqual(references['Sources/docs-chip/事实 中文.md'], {
            'Evidence/fact.md', 'Knowledge_Atoms/md.md', 'Knowledge_Atoms/wiki.md',
            'Knowledge_Atoms/dependent.md', 'Developer_Journeys/journey.md'})
        self.assertIn('Developer_Journeys/journey.md', references['Sources/docs-chip/related.md'])

    def test_first_run_persists_baseline_then_reports_changes_until_saved(self):
        self.assertEqual(self.run_cli('--cached', '--json', 'reports/impact.json'), 0)
        baseline = self.root / 'docs/source_baseline.json'
        self.assertEqual(json.loads(baseline.read_text()), self.old)
        self.assertTrue(json.loads((self.root / 'reports/impact.json').read_text())['baseline_initialized'])
        self.update(lambda path: (path / 'uncovered.md').write_text('new fact'))
        for _ in range(2):
            self.assertEqual(self.run_cli('--cached', '--json', 'reports/impact.json'), 0)
            report = json.loads((self.root / 'reports/impact.json').read_text())
            self.assertEqual(report['uncovered_files'], ['Sources/docs-chip/uncovered.md'])
            self.assertFalse(report['baseline_initialized'])
            self.assertEqual(json.loads(baseline.read_text()), self.old)
        self.assertEqual(self.run_cli('--cached', '--save'), 0)
        self.assertEqual(json.loads(baseline.read_text()), current_pointers(self.root))

    def test_deleted_and_renamed_paths_remain_visible_with_chinese_names(self):
        self.write('Evidence/fact.md', '---\nsource_file: Sources/docs-chip/事实 中文.md\n---\n')
        def rename(path):
            (path / '事实 中文.md').rename(path / 'renamed.md')
            (path / 'uncovered.md').unlink()
        new = self.update(rename)
        report = analyze(self.root, self.old, new, build_reference_map(self.root))
        self.assertEqual(report['deleted_files'], ['Sources/docs-chip/uncovered.md', 'Sources/docs-chip/事实 中文.md'])
        self.assertEqual(report['affected_nodes'], ['Evidence/fact.md'])
        self.assertIn(dict(status='A', path='Sources/docs-chip/renamed.md', affected_nodes=[]), report['changed_files'])
        self.assertEqual(report['errors'], [])

    def test_initialization_does_not_overwrite_existing_baseline(self):
        self.assertEqual(self.run_cli('--init-baseline'), 0)
        self.update(lambda path: (path / 'related.md').write_text('changed'))
        self.assertEqual(self.run_cli('--init-baseline'), 0)
        self.assertEqual(json.loads((self.root / 'docs/source_baseline.json').read_text()), self.old)

    def test_invalid_or_unavailable_baseline_fails_without_advancing_it(self):
        self.assertEqual(self.run_cli('--init-baseline'), 0)
        baseline = self.root / 'docs/source_baseline.json'
        for content in ('broken', json.dumps(dict(self.old, **{'Sources/docs-chip': 'f' * 40}))):
            baseline.write_text(content)
            self.assertEqual(self.run_cli('--cached', '--save', '--json', 'reports/errors.json'), 1)
            self.assertEqual(baseline.read_text(), content)
        report = json.loads((self.root / 'reports/errors.json').read_text())
        self.assertTrue(report['errors'])

    def test_github_pinned_urls_and_cyclic_links_are_bounded(self):
        url = 'https://github.com/spacemit-com/docs-chip/blob/' + self.old['Sources/docs-chip'] + '/事实%20中文.md'
        self.write('Evidence/fact.md', f'[官方]({url})')
        self.write('Knowledge_Atoms/a.md', '[[fact]] [[b]]')
        self.write('Knowledge_Atoms/b.md', '[[a]]')
        self.assertEqual(len(build_reference_map(self.root)['Sources/docs-chip/事实 中文.md']), 3)


if __name__ == '__main__':
    unittest.main()
