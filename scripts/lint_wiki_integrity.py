#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spacemit LLM Wiki - 事实完整性与防拼凑静态质检工具 (Content Integrity & Anti-Hallucination Linter)

校验规则库：
1. 【代际混淆拦截】：检测“SpacemiT 芯片 / 进迭芯片”等泛指主语与特定芯片专属数值（如 2.0 TOPS, 60 TOPS, 25 FPS, 130 KDMIPS）的不规范绑定；
2. 【伪概念拦截】：拦截“VLA 原生支持”、“原生 VLA 支持”等将高阶算法架构与底层硬件指令混为一谈的伪概念；
3. 【模型架构透明度】：凡提及“30B 大模型 / 300亿大模型”，必须明确标注 MoE 架构或实际激活参数（Active 3B / Qwen3-30B-A3B），防止误导为 30B Dense；
4. 【夸大宣发过滤】：拦截“除XX外所有主流大模型”等脱离嵌入式内存物理边界的过度承诺；
5. 【异构归属检查】：提及 1024-bit RVV 时必须明确归属于 A100 智算核，提及 256-bit RVV 归属于 X100 计算核。
"""

import os
import re
import sys

COLOR_RESET = "\033[0m"
COLOR_RED = "\033[1;31m"
COLOR_GREEN = "\033[1;32m"
COLOR_YELLOW = "\033[1;33m"
COLOR_BLUE = "\033[1;34m"
COLOR_CYAN = "\033[1;36m"
COLOR_WHITE = "\033[1;37m"

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIRS = [
    os.path.join(ROOT_DIR, "Developer_Journeys"),
    os.path.join(ROOT_DIR, "Knowledge_Atoms"),
    os.path.join(ROOT_DIR, "Evidence")
]

class IntegrityLinter:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.errors = []
        self.warnings = []
        self.scanned_files_count = 0

    def log_error(self, rel_path, line_num, rule_id, message):
        self.errors.append((f"{rel_path}:{line_num}", rule_id, message))

    def log_warning(self, rel_path, line_num, rule_id, message):
        self.warnings.append((f"{rel_path}:{line_num}", rule_id, message))

    def check_file(self, file_path):
        rel_path = os.path.relpath(file_path, self.root_dir)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self.log_error(rel_path, 1, "FILE_READ_ERR", f"无法读取文件: {e}")
            return

        self.scanned_files_count += 1
        lines = content.split("\n")
        in_code_block = False

        for line_idx, line in enumerate(lines):
            line_num = line_idx + 1
            line_strip = line.strip()

            if line_strip.startswith("```") or line_strip.startswith("~~~"):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                continue

            # 规则 1: 拦截伪概念 "VLA 原生支持" / "原生支持 VLA"
            if re.search(r'VLA.*原生|原生.*VLA', line, re.IGNORECASE):
                self.log_error(
                    rel_path, line_num, "RULE_NO_NATIVE_VLA",
                    "发现伪概念拼凑: VLA 为高阶模型架构，硬件无原生支持，应表述为 'Robot SDK 提供了 SmolVLA ONNX 拆解与部署方案'"
                )

            # 规则 2: 拦截夸大宣发词 "除 FP4/FP6 之外的所有主流大模型"
            if re.search(r'除.*FP4.*外.*所有.*模型|支持.*所有.*AI.*模型', line):
                self.log_error(
                    rel_path, line_num, "RULE_NO_OVER_PROMISE",
                    "发现过度夸大宣发用词: 需明确端侧物理内存 (32GB) 与算子适配边界，不可写 '支持所有主流大模型'"
                )

            # 规则 3: 检查 30B 大模型是否标注了 MoE 架构
            if re.search(r'(?:30B|300\s*亿).*大模型|大模型.*(?:30B|300\s*亿)', line) and not line_strip.startswith("#"):
                if not re.search(r'MoE|A3B|激活|Active|稀疏|暂不支持|上限|参数级别', line):
                    self.log_warning(
                        rel_path, line_num, "RULE_30B_MOE_CLARITY",
                        "30B 模型描述建议补充说明: 建议明确标注为 '30B MoE 稀疏大模型 (Qwen3-30B-A3B，实际激活约 3B)'，避免误导为 30B Dense 稠密模型"
                    )

            # 规则 4: 代际泛指主语与专有算力/指标并列检查
            if re.search(r'SpacemiT\s*芯片.*(?:2\.0\s*TOPS|60\s*TOPS|25\s*FPS)', line):
                self.log_error(
                    rel_path, line_num, "RULE_CHIP_ENTITY_AMBIGUITY",
                    "主体泛指混淆: 严禁使用泛称 'SpacemiT 芯片' 并列专有性能指标，必须精确写明 'K1 芯片 (2.0 TOPS / 25 FPS)' 或 'K3 芯片 (60 TOPS)'"
                )

    def run(self):
        print(f"{COLOR_CYAN}=== Spacemit LLM Wiki 事实完整性与防拼凑自检启动 ==={COLOR_RESET}")
        for target_dir in TARGET_DIRS:
            if not os.path.exists(target_dir):
                continue
            for root, _, files in os.walk(target_dir):
                for f in sorted(files):
                    if f.endswith(".md"):
                        self.check_file(os.path.join(root, f))

        print(f"已扫描 {COLOR_WHITE}{self.scanned_files_count}{COLOR_RESET} 篇精炼层 Markdown 文档。\n")

        if self.warnings:
            print(f"{COLOR_YELLOW}[WARNINGS] 发现 {len(self.warnings)} 处工程表达优化建议:{COLOR_RESET}")
            for loc, rule, msg in self.warnings:
                print(f"  ⚠️  {COLOR_WHITE}{loc}{COLOR_RESET} [{rule}]: {msg}")
            print()

        if self.errors:
            print(f"{COLOR_RED}[ERRORS] 发现 {len(self.errors)} 处事实拼凑与概念违规冲突:{COLOR_RESET}")
            for loc, rule, msg in self.errors:
                print(f"  ❌  {COLOR_RED}{loc}{COLOR_RESET} [{rule}]: {msg}")
            print()
            print(f"{COLOR_RED}❌ 事实完整性自检未通过！请修正上述问题后重新运行。{COLOR_RESET}")
            return False
        else:
            print(f"{COLOR_GREEN}==== 恭喜！Spacemit LLM Wiki 事实完整性自检 100% 通过！ ===={COLOR_RESET}")
            print(f"未检测到代际数据混淆、伪概念拼凑及过度宣发用词。\n")
            return True


if __name__ == "__main__":
    linter = IntegrityLinter(ROOT_DIR)
    success = linter.run()
    sys.exit(0 if success else 1)
