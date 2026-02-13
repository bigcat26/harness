#!/bin/bash
# 后台运行 autorun

LOG_FILE="$HOME/autorun-$(date +%Y%m%d-%H%M%S).log"

echo "Starting autorun in background..."
echo "Log file: $LOG_FILE"
echo "Press Ctrl+C to stop"

# 解除 Claude Code 环境变量限制
unset CLAUDECODE

# 后台运行
python3 -u /Users/chris/Desktop/work/harness/autorun.py "$@" > "$LOG_FILE" 2>&1 &

PID=$!
echo "PID: $PID"
echo "Run 'tail -f $LOG_FILE' to see output"
