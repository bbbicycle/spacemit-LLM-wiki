#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spacemit LLM Wiki - 上游变更影响分析工具 (Upstream Change Impact Analyzer)
功能：
  1. 对比子模块同步前后的 commit 差异，提取变更文件清单
  2. 扫描 Knowledge_Atoms/ 中所有知识原子对 Sources/ 的引用关系
  3. 构建"变更文件 → 受影响知识原子"的映射
  4. 检测无对应知识原子的新增/修改文件（潜在盲区）
  5. 生成结构化影响报告，辅助开发者决策
用法：
  python3 check_upstream_impact.py              # 对比当前子模块指针与远端最新
  python3 check_upstream_impact.py --cached      # 对比上次记录的指针与当前指针
"""

import os
import re
import sys
import subprocess
import json
from collections import defaultdict
from datetime import datetime

# ==============================================================================
# 配置
# ==============================================================================

VAULT_ROOT = os.path.dirname(os.path.abspath(__file__))

SUBMODULES = [
    "Sources/docs-chip",
    "Sources/docs-buildroot",
    "Sources/docs-product",
    "Sources/docs-ai",
    "Sources/docs-ros",
]

KNOWLEDGE_ATOMS_DIR = os.path.join(VAULT_ROOT, "Knowledge_Atoms")
EVIDENCE_DIR = os.path.join(VAULT_ROOT, "Evidence")
INDEX_FILE = os.path.join(VAULT_ROOT, "index.md")
POINTER_CACHE_FILE = os.path.join(VAULT_ROOT, ".last_synced_commits.json")

# 排除的文件模式 (CI/CD 配置、模板等不影响知识库的文件)
EXCLUDE_PATTERNS = [
    r"^\.github/",
    r"^\.gitignore$",
    r"^README\.md$",
    r"^LICENSE",
]

# ANSI 颜色
C_RESET  = "\033[0m"
C_RED    = "\033[1;31m"
C_GREEN  = "\033[1;32m"
C_YELLOW = "\033[1;33m"
C_BLUE   = "\033[1;34m"
C_CYAN   = "\033[1;36m"
C_BOLD   = "\033[1m"
C_DIM    = "\033[2m"

# ==============================================================================
# 工具函数
# ==============================================================================

def run_git(args, cwd=None):
    """执行 git 命令并返回 stdout"""
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd or VAULT_ROOT,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip(), result.returncode

def get_submodule_head(submodule_path):
    """获取子模块当前 HEAD commit hash"""
    full_path = os.path.join(VAULT_ROOT, submodule_path)
    if not os.path.isdir(full_path):
        return None
    out, rc = run_git(["rev-parse", "HEAD"], cwd=full_path)
    return out if rc == 0 else None

def get_submodule_remote_head(submodule_path):
    """获取子模块远端 origin/main 的最新 commit hash"""
    full_path = os.path.join(VAULT_ROOT, submodule_path)
    if not os.path.isdir(full_path):
        return None
    run_git(["fetch", "origin", "--quiet"], cwd=full_path)
    out, rc = run_git(["rev-parse", "origin/main"], cwd=full_path)
    return out if rc == 0 else None

def get_changed_files(submodule_path, old_commit, new_commit):
    """获取两个 commit 之间变更的文件列表 (含状态: A/M/D)"""
    full_path = os.path.join(VAULT_ROOT, submodule_path)
    out, rc = run_git(
        ["diff", "--name-status", old_commit, new_commit],
        cwd=full_path
    )
    if rc != 0 or not out:
        return []
    
    changes = []
    for line in out.split("\n"):
        if not line.strip():
            continue
        parts = line.split("\t", 1)
        if len(parts) == 2:
            status, filepath = parts
            changes.append((status[0], filepath))  # A/M/D/R
    return changes

def get_commit_count(submodule_path, old_commit, new_commit):
    """获取两个 commit 之间的提交数"""
    full_path = os.path.join(VAULT_ROOT, submodule_path)
    out, rc = run_git(
        ["rev-list", "--count", f"{old_commit}..{new_commit}"],
        cwd=full_path
    )
    return int(out) if rc == 0 and out.isdigit() else 0

def should_exclude(filepath):
    """判断文件是否应排除 (CI/CD 配置等)"""
    for pattern in EXCLUDE_PATTERNS:
        if re.match(pattern, filepath):
            return True
    return False

# ==============================================================================
# 核心：构建知识原子引用映射
# ==============================================================================

def build_reference_map():
    """
    扫描所有 Knowledge_Atoms/*.md 文件，提取其中引用的 Sources/ 路径，
    构建 { 'sources/相对路径' -> ['知识原子文件名', ...] } 映射表。
    """
    ref_map = defaultdict(set)  # source_path -> set of knowledge_atom names
    
    if not os.path.isdir(KNOWLEDGE_ATOMS_DIR):
        return ref_map
    
    # 匹配 Markdown 链接中的 Sources/ 路径
    # 支持: (../Sources/xxx), (Sources/xxx), (file:///path/Sources/xxx)
    patterns = [
        re.compile(r'\(\.\.\/Sources\/([^)#\s]+)'),     # ../Sources/xxx
        re.compile(r'\(Sources\/([^)#\s]+)'),            # Sources/xxx
        re.compile(r'\(file:\/\/\/[^)]*Sources\/([^)#\s]+)'),  # file:///path/Sources/xxx
    ]
    
    for fname in os.listdir(KNOWLEDGE_ATOMS_DIR):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(KNOWLEDGE_ATOMS_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue
        
        atom_name = fname.replace(".md", "")
        
        for pattern in patterns:
            for match in pattern.finditer(content):
                source_rel = match.group(1)
                # 去掉 URL 编码
                source_rel = source_rel.replace("%20", " ")
                ref_map[source_rel].add(atom_name)
    
    return ref_map

def find_affected_atoms(submodule_name, changed_file, ref_map):
    """
    给定一个变更文件，找到所有引用它的知识原子。
    submodule_name: 如 'docs-chip'
    changed_file: 子模块内的相对路径，如 'zh/key_stone/k3/k3_hw/k3_hw_faq.md'
    """
    # 构造完整的 Sources/ 相对路径
    full_source_path = f"{submodule_name}/{changed_file}"
    
    affected = set()
    
    # 精确匹配
    if full_source_path in ref_map:
        affected.update(ref_map[full_source_path])
    
    # 也检查带 URL 编码的路径
    encoded_path = full_source_path.replace(" ", "%20")
    if encoded_path in ref_map:
        affected.update(ref_map[encoded_path])
    
    # 模糊匹配：如果变更文件的目录下有 static/ 图片变更，
    # 查找引用同目录下其他文件的知识原子
    file_dir = os.path.dirname(full_source_path)
    if "/static/" in changed_file or changed_file.endswith((".png", ".jpg", ".svg", ".webp")):
        for source_path, atoms in ref_map.items():
            if source_path.startswith(file_dir + "/") or os.path.dirname(source_path) == file_dir:
                affected.update(atoms)
    
    return affected

# ==============================================================================
# 指针缓存管理
# ==============================================================================

def load_cached_pointers():
    """加载上次同步时记录的子模块 commit 指针"""
    if os.path.exists(POINTER_CACHE_FILE):
        try:
            with open(POINTER_CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_cached_pointers(pointers):
    """保存当前子模块 commit 指针"""
    with open(POINTER_CACHE_FILE, "w") as f:
        json.dump(pointers, f, indent=2)

# ==============================================================================
# 报告生成
# ==============================================================================

def generate_report(all_results, ref_map):
    """生成影响分析报告"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n{C_BLUE}{C_BOLD}{'='*65}{C_RESET}")
    print(f"{C_BLUE}{C_BOLD}   Spacemit LLM Wiki — 上游变更影响分析报告{C_RESET}")
    print(f"{C_BLUE}{C_BOLD}   生成时间: {timestamp}{C_RESET}")
    print(f"{C_BLUE}{C_BOLD}{'='*65}{C_RESET}\n")
    
    total_changes = 0
    total_affected = set()
    total_uncovered = []
    has_updates = False
    
    for submodule, result in all_results.items():
        if not result["changes"]:
            continue
        
        has_updates = True
        sub_name = os.path.basename(submodule)
        commit_count = result["commit_count"]
        changes = result["changes"]
        
        # 过滤掉应排除的文件
        content_changes = [(s, f) for s, f in changes if not should_exclude(f)]
        if not content_changes:
            continue
        
        total_changes += len(content_changes)
        
        print(f"{C_CYAN}{C_BOLD}📦 {sub_name} (+{commit_count} commits, {len(content_changes)} 文件变更){C_RESET}")
        print(f"   {C_DIM}{result['old_commit'][:8]}..{result['new_commit'][:8]}{C_RESET}\n")
        
        # 分类统计
        affected_map = {}  # file -> affected atoms
        uncovered = []     # 无对应知识原子的文件
        
        for status, filepath in content_changes:
            affected = find_affected_atoms(sub_name, filepath, ref_map)
            affected_map[filepath] = (status, affected)
            total_affected.update(affected)
            
            if not affected:
                uncovered.append((status, filepath))
                total_uncovered.append((sub_name, status, filepath))
        
        # 输出有对应知识原子的变更
        covered = [(f, s, a) for f, (s, a) in affected_map.items() if a]
        if covered:
            print(f"   {C_GREEN}✅ 已覆盖变更 ({len(covered)} 个文件 → {len(set().union(*[a for _, _, a in covered]))} 个知识原子):{C_RESET}")
            for filepath, status, atoms in covered:
                status_icon = {"A": "🆕", "M": "📝", "D": "🗑️"}.get(status, "❓")
                print(f"   {status_icon} {filepath}")
                for atom in sorted(atoms):
                    print(f"      └→ {C_YELLOW}{atom}{C_RESET}")
            print()
        
        # 输出无对应知识原子的变更
        if uncovered:
            print(f"   {C_RED}⚠️  未覆盖变更 ({len(uncovered)} 个文件无对应知识原子):{C_RESET}")
            for status, filepath in uncovered:
                status_icon = {"A": "🆕", "M": "📝", "D": "🗑️"}.get(status, "❓")
                print(f"   {status_icon} {C_DIM}{filepath}{C_RESET}")
            print()
        
        print(f"   {'─'*55}\n")
    
    if not has_updates:
        print(f"{C_GREEN}{C_BOLD}   🎉 所有子模块均已是最新版本，无需同步！{C_RESET}\n")
        return
    
    # 汇总
    print(f"{C_BOLD}{'='*65}{C_RESET}")
    print(f"{C_BOLD}   📊 汇总{C_RESET}")
    print(f"{C_BOLD}{'='*65}{C_RESET}")
    print(f"   • 总变更文件数: {C_BOLD}{total_changes}{C_RESET}")
    print(f"   • 受影响知识原子: {C_GREEN}{C_BOLD}{len(total_affected)}{C_RESET} 篇")
    
    if total_affected:
        print(f"\n   {C_GREEN}需要审查更新的知识原子:{C_RESET}")
        for atom in sorted(total_affected):
            print(f"   📄 {C_YELLOW}{atom}{C_RESET}")
    
    if total_uncovered:
        print(f"\n   {C_RED}未覆盖变更 ({len(total_uncovered)} 个文件无对应知识原子):{C_RESET}")
        new_files = [(s, f) for s, st, f in total_uncovered if st == "A"]
        mod_files = [(s, f) for s, st, f in total_uncovered if st != "A"]
        
        if new_files:
            print(f"   {C_RED}🆕 新增文件 (可能需要创建新知识原子):{C_RESET}")
            for sub, filepath in new_files:
                print(f"      • {sub}/{filepath}")
        
        if mod_files:
            md_mods = [(s, f) for s, f in mod_files if f.endswith(".md")]
            if md_mods:
                print(f"   {C_YELLOW}📝 修改的文档文件 (可能需要扩展现有知识原子):{C_RESET}")
                for sub, filepath in md_mods:
                    print(f"      • {sub}/{filepath}")
    
    print(f"\n{C_BLUE}{'='*65}{C_RESET}\n")

# ==============================================================================
# 主入口
# ==============================================================================

def main():
    use_cached = "--cached" in sys.argv
    fetch_only = "--fetch-only" in sys.argv
    save_pointers = "--save" in sys.argv
    
    print(f"\n{C_BLUE}{C_BOLD}=== Spacemit LLM Wiki 上游变更影响分析工具启动 ==={C_RESET}")
    print(f"{C_BLUE}工作目录: {VAULT_ROOT}{C_RESET}\n")
    
    # 第一步：构建知识原子引用映射
    print(f"{C_BLUE}[1/3] 正在扫描知识原子引用关系...{C_RESET}")
    ref_map = build_reference_map()
    unique_sources = len(ref_map)
    unique_atoms = len(set().union(*ref_map.values())) if ref_map else 0
    print(f"   ✓ 发现 {unique_sources} 个 Sources/ 引用 → {unique_atoms} 个知识原子\n")
    
    # 第二步：获取子模块变更
    print(f"{C_BLUE}[2/3] 正在检查子模块变更...{C_RESET}")
    
    cached_pointers = load_cached_pointers() if use_cached else {}
    current_pointers = {}
    all_results = {}
    
    for submodule in SUBMODULES:
        sub_name = os.path.basename(submodule)
        full_path = os.path.join(VAULT_ROOT, submodule)
        
        if not os.path.isdir(full_path):
            print(f"   ⚠️  {sub_name}: 子模块目录不存在，跳过")
            continue
        
        current_head = get_submodule_head(submodule)
        if not current_head:
            print(f"   ⚠️  {sub_name}: 无法获取当前 HEAD")
            continue
        
        current_pointers[submodule] = current_head
        
        if use_cached:
            old_commit = cached_pointers.get(submodule)
            new_commit = current_head
            if not old_commit:
                print(f"   ⚠️  {sub_name}: 无缓存指针记录，跳过")
                continue
        else:
            old_commit = current_head
            new_commit = get_submodule_remote_head(submodule)
            if not new_commit:
                print(f"   ⚠️  {sub_name}: 无法获取远端 HEAD")
                continue
        
        if old_commit == new_commit:
            print(f"   ✓ {sub_name}: 已是最新")
            all_results[submodule] = {"changes": [], "commit_count": 0,
                                       "old_commit": old_commit, "new_commit": new_commit}
            continue
        
        changes = get_changed_files(submodule, old_commit, new_commit)
        commit_count = get_commit_count(submodule, old_commit, new_commit)
        print(f"   📦 {sub_name}: {C_YELLOW}+{commit_count} commits, {len(changes)} 文件变更{C_RESET}")
        
        all_results[submodule] = {
            "changes": changes,
            "commit_count": commit_count,
            "old_commit": old_commit,
            "new_commit": new_commit,
        }
    
    print()
    
    # 第三步：生成影响报告
    print(f"{C_BLUE}[3/3] 正在生成影响分析报告...{C_RESET}")
    generate_report(all_results, ref_map)
    
    # 可选：保存当前指针
    if save_pointers:
        save_cached_pointers(current_pointers)
        print(f"{C_GREEN}✓ 已保存当前子模块指针到 {POINTER_CACHE_FILE}{C_RESET}\n")

if __name__ == "__main__":
    main()
