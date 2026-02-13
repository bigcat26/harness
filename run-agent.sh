#!/bin/bash
# 完全无干预的 Claude Code 自动化运行脚本

set -e

PROJECT_DIR="${1:-.}"

echo "=========================================="
echo "Long-Running Agent Harness - Automated"
echo "=========================================="
echo "Project: $PROJECT_DIR"
echo ""

cd "$PROJECT_DIR"

# 显示当前状态
echo "Current progress:"
if [ -f claude-progress.txt ]; then
    head -20 claude-progress.txt
fi

echo ""
echo "Starting Claude Code in automated mode..."
echo ""

# 使用以下参数实现无干预：
# --dangerously-skip-permissions: 跳过所有权限确认
# --permission-mode=bypassPermissions: 绕过权限检查
# --print: 非交互模式
# -t: 设置允许的工具

exec claude \
    --dangerously-skip-permissions \
    --permission-mode=bypassPermissions \
    --allowed-tools "Bash,Read,Write,Edit,Glob,Grep,Task" \
    --append-system-prompt "$(cat harness_system_prompt.md)"
