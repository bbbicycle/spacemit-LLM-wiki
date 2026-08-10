#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spacemit LLM Wiki - 图拓扑自检工具 (Vault Topology Linter)
功能：
1. YAML Frontmatter 格式与字段合规性校验
2. 破损链接检测 (Wikilinks 存在性检查，支持 aliases 别名和 title 映射)
3. 知识图谱三层架构拓扑规则校验 (线-面-点 引用合规性)
4. 孤立节点检测 (Orphan Nodes)
5. index.md 索引挂载覆盖率校验
"""

import os
import re
import sys

# ANSI 颜色高亮
COLOR_RESET = "\033[0m"
COLOR_RED = "\033[1;31m"
COLOR_GREEN = "\033[1;32m"
COLOR_YELLOW = "\033[1;33m"
COLOR_BLUE = "\033[1;34m"
COLOR_CYAN = "\033[1;36m"
COLOR_WHITE = "\033[1;37m"

# 简易 Frontmatter 解析器 (不依赖外部 yaml 库，保证脚本在任何 python3 环境下开箱即用)
def parse_frontmatter(file_path):
    frontmatter = {}
    content = ""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        return None, f"无法读取文件: {e}"

    if len(lines) < 2 or not lines[0].strip() == "---":
        return None, "缺失 YAML Frontmatter 标识 (---)"

    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        return None, "YAML Frontmatter 未闭合 (缺失结尾的 ---)"

    fm_lines = lines[1:end_idx]
    content_lines = lines[end_idx+1:]
    content = "".join(content_lines)

    # 简单解析 YAML 键值对
    current_key = None
    for line in fm_lines:
        line_strip = line.strip()
        if not line_strip or line_strip.startswith("#"):
            continue
        
        # 处理别名列表的简化解析 (形如 aliases: [a, b, c] 或列表形式)
        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            value = parts[1].strip()
            
            # 去除可能的外围引号
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]

            if key == "aliases":
                # 解析 aliases: [a, b, c]
                if value.startswith("[") and value.endswith("]"):
                    items = [x.strip() for x in value[1:-1].split(",") if x.strip()]
                    # 去除子元素可能带有的引号
                    processed_items = []
                    for item in items:
                        if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
                            item = item[1:-1]
                        processed_items.append(item)
                    frontmatter[key] = processed_items
                else:
                    frontmatter[key] = [value] if value else []
            else:
                frontmatter[key] = value
                current_key = key
        elif line.startswith("- ") and current_key == "aliases":
            # 处理多行列表
            val = line[2:].strip()
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            if "aliases" not in frontmatter:
                frontmatter["aliases"] = []
            frontmatter["aliases"].append(val)

    # 必填字段默认值处理
    if "aliases" not in frontmatter:
        frontmatter["aliases"] = []

    return frontmatter, content


class VaultLinter:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.directories = {
            "developer_journey": "Developer_Journeys",
            "knowledge_atom": "Knowledge_Atoms",
            "evidence": "Evidence"
        }
        
        self.nodes = {}       # file_rel_path -> {fm, content, type, title, aliases, status, links}
        self.alias_map = {}   # alias_name -> list of file_rel_paths
        self.title_map = {}   # title_name -> file_rel_path
        self.basename_map = {} # basename -> file_rel_path
        
        self.errors = []
        self.warnings = []

    def log_error(self, file_rel_path, message, line_num=None):
        loc = f"{file_rel_path}:{line_num}" if line_num else file_rel_path
        self.errors.append((loc, message))

    def log_warning(self, file_rel_path, message, line_num=None):
        loc = f"{file_rel_path}:{line_num}" if line_num else file_rel_path
        self.warnings.append((loc, message))

    def scan_vault(self):
        # 1. 扫描三大核心目录下的 Markdown 文件
        for doc_type, dir_name in self.directories.items():
            dir_path = os.path.join(self.root_dir, dir_name)
            if not os.path.exists(dir_path):
                self.log_warning(dir_name, f"目录不存在，跳过扫描")
                continue

            for root, _, files in os.walk(dir_path):
                for file in files:
                    if not file.endswith(".md"):
                        continue
                    
                    file_abs_path = os.path.join(root, file)
                    file_rel_path = os.path.relpath(file_abs_path, self.root_dir)
                    basename = os.path.splitext(file)[0]
                    
                    fm, content = parse_frontmatter(file_abs_path)
                    if fm is None:
                        self.log_error(file_rel_path, f"Frontmatter 解析失败: {content}")
                        continue
                    
                    # 校验 YAML 关键字段
                    required_fields = ["type", "title", "status"]
                    for field in required_fields:
                        if field not in fm or not fm[field]:
                            self.log_error(file_rel_path, f"缺失必填 Frontmatter 字段: {field}")
                    
                    # 校验类型是否符合目录规范
                    expected_type = doc_type
                    actual_type = fm.get("type")
                    if actual_type != expected_type:
                        self.log_error(file_rel_path, f"类型声明冲突: 目录期望为 '{expected_type}'，实际声明为 '{actual_type}'")

                    # 校验状态值是否合法
                    valid_statuses = ["draft", "needs_review", "approved", "deprecated"]
                    status = fm.get("status")
                    if status and status not in valid_statuses:
                        self.log_error(file_rel_path, f"不合法的 status 值: '{status}'，必须为 {valid_statuses} 之一")

                    title = fm.get("title", basename)
                    aliases = fm.get("aliases", [])
                    
                    self.nodes[file_rel_path] = {
                        "path": file_rel_path,
                        "type": actual_type or doc_type,
                        "title": title,
                        "aliases": aliases,
                        "status": status,
                        "content": content,
                        "links": []
                    }

                    # 构建映射库，用于双链解析
                    self.basename_map[basename] = file_rel_path
                    self.title_map[title] = file_rel_path
                    for alias in aliases:
                        if alias not in self.alias_map:
                            self.alias_map[alias] = []
                        self.alias_map[alias].append(file_rel_path)

        # 2. 扫描 index.md、log.md 和 Agent.md
        for special_file in ["index.md", "log.md", "Agent.md"]:
            file_abs_path = os.path.join(self.root_dir, special_file)
            if os.path.exists(file_abs_path):
                fm, content = parse_frontmatter(file_abs_path)
                if fm is None:
                    # index.md/log.md/Agent.md 缺失或解析失败不属于严重拓扑错误，报 Warning
                    self.log_warning(special_file, f"Frontmatter 解析失败或缺失: {content}")
                    fm = {}
                    with open(file_abs_path, "r", encoding="utf-8") as f:
                        content = f.read()
                
                # 特殊处理：全局控制文档 (如 Agent.md)
                title = fm.get("title", special_file)
                aliases = fm.get("aliases", [])
                
                self.nodes[special_file] = {
                    "path": special_file,
                    "type": "special",
                    "title": title,
                    "aliases": aliases,
                    "status": fm.get("status"),
                    "content": content,
                    "links": []
                }
                basename = os.path.splitext(special_file)[0]
                self.basename_map[basename] = special_file
                self.title_map[title] = special_file
                for alias in aliases:
                    if alias not in self.alias_map:
                        self.alias_map[alias] = []
                    self.alias_map[alias].append(special_file)

    def extract_links(self):
        # 匹配 Obsidian [[wikilink]] 双链
        # 匹配 [[链接目标]] 或 [[链接目标|显示名称]] 或 [[链接目标#章节]]
        link_pattern = re.compile(r"\[\[(.*?)\]\]")
        
        for file_rel_path, node in self.nodes.items():
            content = node["content"]
            lines = content.split("\n")
            
            in_code_block = False
            for line_idx, line in enumerate(lines):
                line_num = line_idx + 1
                line_strip = line.strip()
                
                # 检测多行代码块的开始和结束 (以 ``` 或 ~~~ 开头)
                if line_strip.startswith("```") or line_strip.startswith("~~~"):
                    in_code_block = not in_code_block
                    continue
                
                # 如果当前行在代码块中，跳过双链解析
                if in_code_block:
                    continue
                
                # 移出行内被反引号包裹的行内代码 (如 `[[双链]]`)，防止其被错配
                clean_line = re.sub(r'`[^`]+`', '', line)
                
                matches = link_pattern.findall(clean_line)
                for match in matches:
                    # 1. 剥离显示名称管道符: [[target|display]] -> target
                    target = match.split("|")[0].strip()
                    # 2. 剥离章节锚点: [[target#section]] -> target
                    target = target.split("#")[0].strip()
                    
                    if not target:
                        continue
                        
                    node["links"].append({
                        "raw": match,
                        "target": target,
                        "line": line_num
                    })

    def validate_links_and_topology(self):
        # 提取 index.md 中挂载的所有链接，用于覆盖率检查
        indexed_files = set()
        index_node = self.nodes.get("index.md")
        if index_node:
            for link in index_node["links"]:
                resolved = self.resolve_link_target(link["target"])
                if resolved:
                    indexed_files.add(resolved)

        for file_rel_path, node in self.nodes.items():
            # 排除 index.md 和 log.md 自身的拓扑规则检查
            if node["type"] == "special":
                continue

            # 统计入度，用于 Orphan 检查
            node["in_degree"] = 0

        # 解析与校验链接
        for file_rel_path, node in self.nodes.items():
            for link in node["links"]:
                target_raw = link["target"]
                line_num = link["line"]
                
                # 排除指向特殊网页超链接、邮件或静态资源的链接校验
                if target_raw.startswith("http") or target_raw.startswith("mailto:") or target_raw.endswith((".png", ".jpg", ".jpeg", ".gif", ".pdf", ".command")):
                    continue

                resolved_path = self.resolve_link_target(target_raw)
                
                if not resolved_path:
                    self.log_error(file_rel_path, f"破损链接: [[{link['raw']}]] 找不到对应的物理文件或别名", line_num)
                    continue

                # 记录成功解析的物理链接
                link["resolved_path"] = resolved_path
                
                # 统计入度 (排除自引用)
                if resolved_path in self.nodes and resolved_path != file_rel_path:
                    if "in_degree" not in self.nodes[resolved_path]:
                        self.nodes[resolved_path]["in_degree"] = 0
                    self.nodes[resolved_path]["in_degree"] += 1

                # 进行三层拓扑引用红线校验
                self.check_topology_rule(file_rel_path, node, resolved_path, link)

        # 校验孤立节点 (Orphan Nodes) 与 索引覆盖率
        for file_rel_path, node in self.nodes.items():
            if node["type"] == "special":
                continue
            
            # 1. 孤立节点校验 (排除 index.md 指向它，入度依然为 0 的情况)
            in_degree = node.get("in_degree", 0)
            if in_degree == 0:
                self.log_warning(file_rel_path, f"孤立节点 (Orphan Node): 没有任何其他文档引用它")

            # 2. 检查是否在 index.md 中挂载
            if file_rel_path not in indexed_files:
                self.log_warning(file_rel_path, f"未在 index.md 中注册挂载")

    def resolve_link_target(self, target_str):
        # 1. 尝试直接通过相对路径解析（Obsidian 支持带子目录的链接，如 Knowledge_Atoms/文件名）
        # 归一化路径，去除后缀进行匹配
        target_clean = target_str.replace("\\", "/")
        if target_clean.endswith(".md"):
            target_clean = target_clean[:-3]
            
        for path in self.nodes.keys():
            path_clean = path.replace("\\", "/")
            if path_clean.endswith(".md"):
                path_clean = path_clean[:-3]
            if path_clean == target_clean or path_clean.endswith("/" + target_clean):
                return path

        # 2. 尝试纯文件名 (Basename) 匹配
        basename = os.path.basename(target_clean)
        if basename in self.basename_map:
            return self.basename_map[basename]

        # 3. 尝试标题 (Title) 匹配
        if target_str in self.title_map:
            return self.title_map[target_str]

        # 4. 尝试别名 (Alias) 匹配
        if target_str in self.alias_map:
            # 如果别名匹配到多个文件，返回第一个，并在警告中提示多重映射
            matched_paths = self.alias_map[target_str]
            if len(matched_paths) > 1:
                pass # 可在此报 Warning，暂只返回首个
            return matched_paths[0]

        return None

    def check_topology_rule(self, src_path, src_node, dest_path, link):
        dest_node = self.nodes.get(dest_path)
        if not dest_node:
            return
        
        src_type = src_node["type"]
        dest_type = dest_node["type"]
        line_num = link["line"]

        # 全局特殊文件 (index.md, log.md, Agent.md) 不受拓扑引用规则红线限制
        if src_type == "special":
            return

        # 红线一：任何普通文件绝不能反向引用 Developer_Journeys (步骤线)
        if dest_type == "developer_journey":
            self.log_error(src_path, f"违规越级引用: 节点反向引用了上手动线 [[{link['raw']}]] ({dest_type})", line_num)
            return

        # 红线二：Evidence (数据点) 必须保持绝对原子，严禁向上引用任何知识面 (Atom) 或线 (Journey)
        if src_type == "evidence":
            if dest_type in ["knowledge_atom", "developer_journey"]:
                self.log_error(src_path, f"违规越级引用: 原子数据 Evidence 向上引用了 [[{link['raw']}]] ({dest_type})", line_num)
            return

        # 红线三：Developer_Journeys (步骤线) 只能引用 Atoms 或 Evidence，不能嵌套引用 Journeys（红线一已拦截）
        # 目前允许 Atom 引用 Atom，以及 Atom 引用 Evidence


def main():
    # 自动定位到 Spacemit LLM Wiki 目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"{COLOR_CYAN}=== Spacemit LLM Wiki 图拓扑自检启动 ==={COLOR_RESET}")
    print(f"工作目录: {COLOR_WHITE}{script_dir}{COLOR_RESET}\n")

    linter = VaultLinter(script_dir)
    
    # 扫描与提取
    linter.scan_vault()
    linter.extract_links()
    
    # 核心校验
    linter.validate_links_and_topology()
    
    # 打印警告 (Warnings)
    if linter.warnings:
        print(f"{COLOR_YELLOW}[WARNINGS] 发现 {len(linter.warnings)} 个结构优化警告:{COLOR_RESET}")
        for loc, msg in linter.warnings:
            print(f"  ⚠️  {COLOR_WHITE}{loc}{COLOR_RESET}: {msg}")
        print()

    # 打印错误 (Errors)
    if linter.errors:
        print(f"{COLOR_RED}[ERRORS] 发现 {len(linter.errors)} 个严重规则冲突错误:{COLOR_RESET}")
        for loc, msg in linter.errors:
            print(f"  ❌  {COLOR_RED}{loc}{COLOR_RESET}: {msg}")
        print()
        
        print(f"{COLOR_RED}❌ 自检失败！请修正上述严重错误后重新校验。{COLOR_RESET}")
        sys.exit(1)
    else:
        print(f"{COLOR_GREEN}==== 恭喜！Spacemit LLM Wiki 拓扑自检 100% 通过！ ===={COLOR_RESET}")
        print(f"成功扫描 {len(linter.nodes)} 个物理文档，链接关系完全健康。")
        sys.exit(0)


if __name__ == "__main__":
    main()
