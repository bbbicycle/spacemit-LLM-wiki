#!/usr/bin/env bash
# ==============================================================================
# Spacemit LLM Wiki - 跨平台子模块文档一键同步脚本
# 功能：定位项目根目录，遍历并同步 5 个 Spacemit 官方文档 Git 子模块
# ==============================================================================

set -euo pipefail

# 获取当前脚本所在绝对路径并切换到项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Terminal 颜色格式定义
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    BLUE='\033[0;34m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    BOLD='\033[1m'
    NC='\033[0m' # No Color
else
    GREEN=''
    BLUE=''
    RED=''
    YELLOW=''
    BOLD=''
    NC=''
fi

# 错误拦截钩子函数
on_error() {
    local exit_code=$?
    local line_no=$1
    echo -e "\n${RED}${BOLD}[ERROR] 脚本在第 ${line_no} 行执行失败，退出码: ${exit_code}${NC}" >&2
    exit "$exit_code"
}

trap 'on_error $LINENO' ERR

echo -e "${BLUE}${BOLD}=====================================================${NC}"
echo -e "${BLUE}${BOLD}   Spacemit LLM Wiki - 子模块源文档一键同步程序     ${NC}"
echo -e "${BLUE}${BOLD}=====================================================${NC}"
echo -e "${BLUE}[INFO] 项目根目录: ${SCRIPT_DIR}${NC}\n"

# 检查 Git 仓库有效性
if [ ! -d ".git" ] && [ ! -f ".git" ]; then
    echo -e "${RED}[ERROR] 当前目录不是有效的 Git 仓库！${NC}" >&2
    exit 1
fi

# 定义 5 个 Spacemit 官方子模块
SUBMODULES=(
    "Sources/docs-chip"
    "Sources/docs-buildroot"
    "Sources/docs-product"
    "Sources/docs-ai"
    "Sources/docs-ros"
)

echo -e "${BLUE}[1/2] 正在初始化并同步 .gitmodules 配置...${NC}"
git submodule sync --recursive
git submodule init

TOTAL=${#SUBMODULES[@]}
echo -e "\n${BLUE}[2/2] 开始遍历更新 ${TOTAL} 个 Spacemit 官方文档子模块...${NC}"

COUNT=0
FAILED_MODULES=()

for SUB in "${SUBMODULES[@]}"; do
    COUNT=$((COUNT + 1))
    echo -e "\n${BLUE}[${COUNT}/${TOTAL}] 正在同步子模块: ${BOLD}${SUB}${NC} ..."
    
    if git submodule update --remote --merge "$SUB"; then
        echo -e "${GREEN}✓ ${SUB} 同步成功！${NC}"
    else
        echo -e "${RED}✗ ${SUB} 同步失败！${NC}" >&2
        FAILED_MODULES+=("$SUB")
    fi
done

if [ ${#FAILED_MODULES[@]} -ne 0 ]; then
    echo -e "\n${RED}${BOLD}=====================================================${NC}"
    echo -e "${RED}${BOLD}   [警告] 以下子模块同步失败:                        ${NC}"
    for FAILED in "${FAILED_MODULES[@]}"; do
        echo -e "${RED}   - ${FAILED}${NC}"
    done
    echo -e "${RED}${BOLD}=====================================================${NC}"
    exit 1
fi

echo -e "\n${GREEN}${BOLD}=====================================================${NC}"
echo -e "${GREEN}${BOLD}   🎉 所有子模块 (${TOTAL}/${TOTAL}) 已成功同步至最新 upstream！ ${NC}"
echo -e "${GREEN}${BOLD}=====================================================${NC}"
