#!/usr/bin/env python3
"""Verify manifest-only cloud/local installations without Sources or network access."""

import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
CORE_TOOLS = {
    "search_wiki", "get_developer_journey", "read_knowledge_atom",
    "get_evidence_fact", "get_graph_relations", "search_raw_sources",
    "read_raw_source_file",
}


def safe_path(base, relative):
    """Accept canonical repository-relative paths and keep symlinks within base."""
    if not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative:
        raise ValueError(f"Not a relative install path: {relative!r}")
    path = PurePosixPath(relative)
    if path.is_absolute() or any(part in ("", ".", "..") for part in relative.split("/")):
        raise ValueError(f"Unsafe install path: {relative!r}")
    resolved = (base / path).resolve()
    if not resolved.is_relative_to(base.resolve()):
        raise ValueError(f"Install path escapes its directory: {relative!r}")
    return resolved


def install_files(manifest, mode):
    skill = manifest["skill"]
    skill_dir = safe_path(ROOT, skill["source_dir"])
    files = [safe_path(skill_dir, name) for name in skill["files"]]
    files.extend(safe_path(ROOT, name) for name in manifest["modes"][mode]["runtime_files"])
    return files


def copy_install(manifest, mode, destination):
    for source in install_files(manifest, mode):
        relative = source.relative_to(ROOT)
        target = safe_path(destination, relative.as_posix())
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


class MinimalInstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "install/manifest.json").read_text(encoding="utf-8"))

    def test_manifest_covers_complete_skill_and_two_minimal_modes(self):
        manifest = self.manifest
        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(manifest["default_mode"], "cloud")
        self.assertEqual(set(manifest["modes"]), {"cloud", "local"})
        self.assertEqual(set(manifest["core_tools"]), CORE_TOOLS)
        self.assertEqual(len(manifest["core_tools"]), len(CORE_TOOLS))
        skill = manifest["skill"]
        self.assertEqual(skill["name"], "spacemit-wiki")
        skill_dir = safe_path(ROOT, skill["source_dir"])
        actual = {path.relative_to(skill_dir).as_posix() for path in skill_dir.rglob("*") if path.is_file()}
        self.assertEqual(set(skill["files"]), actual)
        self.assertEqual(len(skill["files"]), len(actual), "Duplicate Skill file entries")
        self.assertIn("SKILL.md", actual)
        cloud, local = manifest["modes"]["cloud"], manifest["modes"]["local"]
        self.assertEqual(cloud["transport"], "sse")
        self.assertEqual(cloud["url"], "https://mcp.yao1302.xyz/sse")
        self.assertEqual(cloud["runtime_files"], [])
        self.assertEqual(local["transport"], "stdio")
        self.assertEqual(local["python_min"], "3.9")
        self.assertEqual(local["entrypoint"], "mcp/server.py")
        self.assertEqual(set(local["runtime_files"]), {"mcp/server.py", "mcp/data/wiki_graph.json"})
        self.assertEqual(len(local["runtime_files"]), 2)
        for mode in ("cloud", "local"):
            for source in install_files(manifest, mode):
                self.assertTrue(source.is_file(), f"Missing install file: {source}")

    def test_install_paths_cannot_escape(self):
        for name in ("", "/tmp/file", "../file", "data/../../file", "data/./file", "data//file", "C:/file", "data\\file"):
            with self.subTest(path=name), self.assertRaises(ValueError):
                safe_path(ROOT, name)
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory) / "install"
            base.mkdir()
            (base / "outside").symlink_to(Path(directory), target_is_directory=True)
            with self.assertRaises(ValueError):
                safe_path(base, "outside/file")

    def test_cloud_contains_only_complete_self_contained_skill(self):
        with tempfile.TemporaryDirectory(prefix="spacemit-cloud-") as directory:
            installed = Path(directory)
            copy_install(self.manifest, "cloud", installed)
            actual = {path.relative_to(installed).as_posix() for path in installed.rglob("*") if path.is_file()}
            expected = {path.relative_to(ROOT).as_posix() for path in install_files(self.manifest, "cloud")}
            self.assertEqual(actual, expected)
            self.assertFalse((installed / "mcp").exists())
            self.assertFalse((installed / "Sources").exists())
            skill_dir = safe_path(installed, self.manifest["skill"]["source_dir"])
            for document in skill_dir.rglob("*.md"):
                text = document.read_text(encoding="utf-8")
                for target in re.findall(r"\[[^\]]*\]\(<?([^\s)>]+)>?(?:\s+[^)]*)?\)", text):
                    url = urlsplit(target)
                    self.assertNotEqual(url.scheme, "file", f"Local machine link in {document.name}: {target}")
                    if url.scheme or url.netloc or not url.path:
                        continue
                    reference = (document.parent / unquote(url.path)).resolve()
                    self.assertTrue(reference.is_relative_to(skill_dir), f"Nonportable Skill reference in {document.name}: {target}")
                    self.assertTrue(reference.is_file(), f"Unresolved Skill reference in {document.name}: {target}")

    def test_local_stdio_runs_from_minimal_install_without_network(self):
        with tempfile.TemporaryDirectory(prefix="spacemit-local-") as directory:
            installed = Path(directory)
            copy_install(self.manifest, "local", installed)
            self.assertFalse((installed / "Sources").exists())
            entrypoint = safe_path(installed, self.manifest["modes"]["local"]["entrypoint"])
            requests = [
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
                    "protocolVersion": "2024-11-05", "capabilities": {},
                    "clientInfo": {"name": "minimal-install-check", "version": "1.0"},
                }},
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
                    "name": "search_wiki", "arguments": {"query": "Muse Pi"},
                }},
                {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {
                    "name": "get_evidence_fact", "arguments": {"spec_name": "muse_pi_vs_pi_pro_specs"},
                }},
            ]
            # Run the actual server in a child process, blocking socket creation so
            # hidden dependencies on online services cannot make this check pass.
            launcher = """import runpy, socket, sys, urllib.request
def deny_network(*args, **kwargs):
    raise RuntimeError("Network is disabled for the minimal-install check")
socket.socket = deny_network
socket.create_connection = deny_network
runpy.run_path(sys.argv[1], run_name="__main__")
"""
            result = subprocess.run(
                [sys.executable, "-I", "-B", "-c", launcher, str(entrypoint)],
                input="".join(json.dumps(request) + "\n" for request in requests),
                cwd=installed, capture_output=True, text=True, timeout=15,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            responses = [json.loads(line) for line in result.stdout.splitlines()]
            self.assertEqual([response.get("id") for response in responses], [1, 2, 3, 4])
            for response in responses:
                self.assertEqual(response["jsonrpc"], "2.0")
                self.assertNotIn("error", response)
            self.assertEqual(responses[0]["result"]["protocolVersion"], "2024-11-05")
            self.assertEqual({tool["name"] for tool in responses[1]["result"]["tools"]}, CORE_TOOLS)
            for response in responses[2:]:
                self.assertFalse(response["result"].get("isError"), response)
            search = json.loads(responses[2]["result"]["content"][0]["text"])
            self.assertTrue(search, "Minimal install cannot search its bundled index")
            fact = json.loads(responses[3]["result"]["content"][0]["text"])
            self.assertEqual(fact["type"], "evidence")
            self.assertTrue(fact["full_table_content"].strip(), "Minimal install cannot read evidence content")


if __name__ == "__main__":
    unittest.main()
