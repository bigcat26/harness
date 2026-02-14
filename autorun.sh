#!/bin/bash
# Auto-run harness: 循环执行 claude 直到所有任务完成

# 用法: ./autorun.sh <项目目录>
# 必须在新的终端窗口运行（不能在 Claude Code 窗口内）

PROJECT_DIR="${1:-.}"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "Error: Directory $PROJECT_DIR not found"
    exit 1
fi

cd "$PROJECT_DIR"

echo "=========================================="
echo "Auto-Run Harness"
echo "=========================================="
echo "Project: $(pwd)"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

ITERATION=0

while true; do
    ITERATION=$((ITERATION + 1))
    echo ""
    echo "=========================================="
    echo "ITERATION $ITERATION"
    echo "=========================================="

    # 检查是否所有功能都已完成
    if [ -f "feature_list.json" ]; then
        # 使用 python 检查是否还有未完成的功能
        REMAINING=$(python3 -c "
import json
import sys
with open('feature_list.json') as f:
    features = json.load(f)
pending = [f for f in features if not f.get('done', False)]
print(len(pending))
" 2>/dev/null)

        if [ "$REMAINING" = "0" ] || [ -z "$REMAINING" ]; then
            echo ""
            echo "✅ All features completed!"
            break
        fi

        # 显示下一个功能
        NEXT=$(python3 -c "
import json
with open('feature_list.json') as f:
    features = json.load(f)
for f in features:
    if not f.get('done', False):
        print(f\"{f['id']}. {f['title']}\")
        print(f\"   {f['description'][:60]}...\")
        break
" 2>/dev/null)

        echo "Remaining: $REMAINING features"
        echo "Next: $NEXT"
    else
        echo "Error: feature_list.json not found"
        exit 1
    fi

    echo ""
    echo "Running Claude..."

    # 创建临时 prompt 文件
    PROMPT_FILE=".prompt_temp.txt"

    cat > "$PROMPT_FILE" << 'PROMPT_END'
You are working on an incremental development task.

## Current Status
Read feature_list.json to see what needs to be done.

## Task
Implement ONE feature at a time:
1. Read feature_list.json and choose the highest priority incomplete feature
2. Implement it with clean, production-ready code
3. Test to ensure it works

## Completion Signal
When done, respond with exactly:
- "FEATURE_COMPLETE" if there are more features to do
- "ALL_TASKS_COMPLETE" if ALL features are now done

After responding, the harness will automatically:
- Commit your changes to git
- Update feature_list.json to mark the feature as done
- Continue with the next feature
PROMPT_END

    # 运行 claude，实时显示输出
    cat "$PROMPT_FILE" | claude --print --dangerously-skip-permissions 2>&1

    # 删除 prompt 文件
    rm -f "$PROMPT_FILE"

    # 检查是否完成了所有任务
    # 读取 feature_list.json 检查状态
    if [ -f "feature_list.json" ]; then
        REMAINING_AFTER=$(python3 -c "
import json
with open('feature_list.json') as f:
    features = json.load(f)
pending = [f for f in features if not f.get('done', False)]
print(len(pending))
" 2>/dev/null)

        if [ "$REMAINING_AFTER" = "0" ] || [ -z "$REMAINING_AFTER" ]; then
            echo ""
            echo "✅ All features completed!"
            break
        fi
    fi

    echo ""
    echo "Feature completed, continuing to next..."
    sleep 1

done

echo ""
echo "=========================================="
echo "AUTO-RUN COMPLETE"
echo "=========================================="
echo "Total iterations: $ITERATION"
