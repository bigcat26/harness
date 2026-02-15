---
name: agent-harness
description: 使用 Claude Code 实现长期运行的大型任务。通过增量开发、自动提交和进度追踪来管理复杂项目。
---

# Agent Harness

用于使用 Claude Code 运行长时间任务的工作流。

## 概述

这个 skill 将大型任务拆分为多个小功能点，逐个实现，每次完成后自动提交并记录进度。

---

## 场景 1: 从 0 开始新项目

告诉我你的项目需求，例如：

> "帮我创建一个可以读取文本故事并生成有声漫画的程序"

我将帮你：
1. 分析需求，拆分成具体功能点
2. 创建必要的文件
3. 初始化 git 仓库
4. 引导你开始第一个功能

---

## 场景 2: 已有项目执行长期任务

如果你有一个已有项目，想用特定 skill 执行任务：

### 步骤 1: 创建 feature_list.json

手动创建或让我帮你创建：

```json
[
  {
    "id": 1,
    "title": "任务名称",
    "description": "详细描述这个任务要做什么",
    "priority": "high",
    "dependencies": [],
    "done": false,
    "skill": "skill-name"  // 可选：指定使用的 skill
  }
]
```

### 步骤 2: 运行 autorun.sh

```bash
cd <项目目录>
./autorun.sh
```

---

## 自动循环运行（推荐）

### 步骤 1: 创建脚本

在项目目录创建 `autorun.sh`：

```bash
cat > autorun.sh << 'SCRIPT_END'
#!/bin/bash
# Auto-run harness: 循环执行 claude 直到所有任务完成

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
echo ""

ITERATION=0

while true; do
    ITERATION=$((ITERATION + 1))
    echo ""
    echo "=========================================="
    echo "ITERATION $ITERATION"
    echo "=========================================="

    # 检查是否所有功能都已完成
    REMAINING=$(python3 -c '
import json
with open("feature_list.json") as f:
    features = json.load(f)
pending = [f for f in features if not f.get("done", False)]
print(len(pending))
' 2>/dev/null)

    if [ "$REMAINING" = "0" ] || [ -z "$REMAINING" ]; then
        echo ""
        echo "All features completed!"
        break
    fi

    # 显示下一个功能
    echo "Remaining: $REMAINING features"

    python3 -c '
import json
with open("feature_list.json") as f:
    features = json.load(f)
for f in features:
    if not f.get("done", False):
        print(f"Next: {f[\"id\"]}. {f[\"title\"]}")
        skill = f.get("skill", "")
        if skill:
            print(f"   Skill: {skill}")
        print(f"   {f[\"description\"][:80]}...")
        break
' 2>/dev/null

    echo ""
    echo "Running Claude..."

    # 获取当前任务的 skill
    CURRENT_SKILL=$(python3 -c '
import json
with open("feature_list.json") as f:
    features = json.load(f)
for f in features:
    if not f.get("done", False):
        print(f.get("skill", ""))
        break
' 2>/dev/null)

    # 构建 claude 命令
    if [ -n "$CURRENT_SKILL" ]; then
        CLAUDE_CMD="claude --print --dangerously-skip-permissions --add-skill $CURRENT_SKILL"
    else
        CLAUDE_CMD="claude --print --dangerously-skip-permissions"
    fi

    # 运行 claude
    $CLAUDE_CMD << 'CLAUDE_END'
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

After responding, the harness will automatically commit your changes and update progress.
CLAUDE_END

    # 检查是否所有功能都已完成
    REMAINING_AFTER=$(python3 -c '
import json
with open("feature_list.json") as f:
    features = json.load(f)
pending = [f for f in features if not f.get("done", False)]
print(len(pending))
' 2>/dev/null)

    if [ "$REMAINING_AFTER" = "0" ] || [ -z "$REMAINING_AFTER" ]; then
        echo ""
        echo "All features completed!"
        break
    fi

    echo ""
    echo "Feature completed, continuing to next..."
    sleep 1

done

echo ""
echo "=========================================="
echo "AUTO-RUN COMPLETE"
echo "=========================================="
SCRIPT_END

chmod +x autorun.sh
```

### 步骤 2: 运行脚本

```bash
# 在新终端运行
cd <项目目录>
./autorun.sh
```

---

## 核心文件格式

### 1. feature_list.json

```json
[
  {
    "id": 1,
    "title": "功能标题",
    "description": "详细描述这个功能要做什么",
    "priority": "high",
    "dependencies": [],
    "done": false,
    "skill": "skill-name"  // 可选：指定使用的 skill
  }
]
```

### 2. claude-progress.txt

```markdown
# Project Progress - 2026-02-14 10:00
# Status: In Progress

## Completed
- [x] 功能1

## Pending
- [ ] 功能2: 描述
```

### 3. CLAUDE.md

```markdown
# CLAUDE.md - 项目规则

你是一个增量工作代理。

## 规则
1. 每次只实现一个功能
2. 完成后 git commit
3. 更新 feature_list.json 标记 done: true

## 结束信号
- "FEATURE_COMPLETE": 还有更多功能
- "ALL_TASKS_COMPLETE": 全部完成
```

---

## 重要说明

- 需要在新终端运行脚本（不能在 Claude Code 窗口内运行）
- 脚本会自动 commit 和更新进度文件
- 检测到 "ALL_TASKS_COMPLETE" 时自动停止
- 可在 feature_list.json 中指定 `skill` 字段使用特定 skill

---

现在，告诉我你的项目需求是什么？
