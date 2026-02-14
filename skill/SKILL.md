---
name: agent-harness
description: 使用 Claude Code 实现长期运行的大型任务。通过增量开发、自动提交和进度追踪来管理复杂项目。
---

# Agent Harness

用于使用 Claude Code 运行长时间任务的工作流。

## 概述

这个 skill 将大型任务拆分为多个小功能点，逐个实现，每次完成后自动提交并记录进度。

---

## 初始化任务

告诉我你的项目需求，例如：

> "帮我创建一个可以读取文本故事并生成有声漫画的程序"

我将帮你：
1. 分析需求，拆分成具体功能点
2. 创建必要的文件
3. 初始化 git 仓库
4. 引导你开始第一个功能

---

## 自动循环运行（推荐）

使用 `autorun.sh` 脚本自动循环执行所有任务：

```bash
# 在新终端运行
cd <项目目录>
/path/to/autorun.sh .
```

**工作原理**：
1. 脚本读取 `feature_list.json`
2. 选择优先级最高的未完成功能
3. 调用 claude 实现
4. claude 输出 "FEATURE_COMPLETE" 或 "ALL_TASKS_COMPLETE"
5. 脚本 commit 并更新进度
6. 继续下一个功能
7. 所有功能完成后自动退出

**结束信号**：
- `FEATURE_COMPLETE`: 还有更多功能，继续下一轮
- `ALL_TASKS_COMPLETE`: 所有功能已完成，停止循环

---

## 核心文件格式

### 1. feature_list.json

功能列表文件，JSON 格式：

```json
[
  {
    "id": 1,
    "title": "功能标题",
    "description": "详细描述这个功能要做什么",
    "priority": "high",
    "dependencies": [],
    "done": false
  },
  {
    "id": 2,
    "title": "另一个功能",
    "description": "依赖功能1完成后才能开始",
    "priority": "medium",
    "dependencies": [1],
    "done": false
  }
]
```

**字段说明**：
- `id`: 唯一标识
- `title`: 功能名称（简短）
- `description`: 详细描述
- `priority`: high | medium | low
- `dependencies`: 依赖的其他功能 ID 数组
- `done`: 是否已完成

### 2. claude-progress.txt

进度追踪文件，Markdown 格式：

```markdown
# Project Progress - 2026-02-14 10:00
# Status: In Progress

## Completed
- [x] 功能1标题
- [x] 功能2标题

## Pending
- [ ] 功能3标题: 详细描述
- [ ] 功能4标题: 详细描述
```

### 3. CLAUDE.md

项目级规则文件，Markdown 格式：

```markdown
# CLAUDE.md - 项目规则

你是一个增量工作代理。

## 规则

1. 每次只实现一个功能
2. 完成后 git commit
3. 更新 feature_list.json 标记 done: true

## 结束信号

完成当前功能后：
- 如果还有更多功能 → 输出 "FEATURE_COMPLETE"
- 如果所有功能都完成 → 输出 "ALL_TASKS_COMPLETE"

## 工作流

### 会话开始
- 读取 feature_list.json
- 选择优先级最高的未完成功能

### 会话结束
- git add -A && git commit -m "feat: 功能名称"
- 更新 feature_list.json 的 done 字段
- 输出结束信号
```

---

## 手动运行（可选）

如果不使用自动脚本，也可以手动运行：

```bash
cd <项目目录>
claude --print --dangerously-skip-permissions
```

然后告诉我"继续下一个功能"，我会帮你查看进度并引导。

---

## 工作流

1. **初始化**: 我帮你拆分功能，创建文件
2. **运行**: 使用 autorun.sh 自动循环运行
3. **完成**: 所有功能完成后自动停止

---

## 重要说明

- 需要在新终端运行脚本（不能在 Claude Code 窗口内运行）
- 脚本会自动 commit 和更新进度文件
- 检测到 "ALL_TASKS_COMPLETE" 时自动停止

---

现在，告诉我你的项目需求是什么？
