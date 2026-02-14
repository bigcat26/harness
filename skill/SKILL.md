---
name: agent-harness
description: 使用 Claude Code 实现长期运行的大型任务。通过增量开发、自动提交和进度追踪来管理复杂项目。
---

# Agent Harness

用于使用 Claude Code 运行长时间任务的工作流。

## 概述

这个 skill 将大型任务拆分为多个小功能点，逐个实现，每次完成后自动提交并记录进度。

## 初始化任务

告诉我你的项目需求，例如：

> "帮我创建一个可以读取文本故事并生成有声漫画的程序"

我将帮你：
1. 分析需求，拆分成具体功能点
2. 创建 `feature_list.json`
3. 创建 `claude-progress.txt`
4. 初始化 git 仓库
5. 引导你开始第一个功能

## 继续任务

如果任务中断，想继续时：

```bash
# 在新终端运行
cd <项目目录>
claude --print --dangerously-skip-permissions << 'EOF'
继续工作：
1. 读取 feature_list.json 查看当前进度
2. 实现下一个未完成的功能
3. 完成后 git commit
4. 更新 feature_list.json 标记完成
EOF
```

## 核心文件

项目会自动创建以下文件：

| 文件 | 用途 |
|------|------|
| `feature_list.json` | 功能点列表，包含 ID、标题、描述、优先级 |
| `claude-progress.txt` | 进度摘要 |
| `CLAUDE.md` | 项目级规则 |

## 工作流

1. **初始化**: 我帮你拆分功能，创建文件
2. **实现**: 你用 claude 实现功能
3. **提交**: 完成后 commit 并更新进度
4. **继续**: 重复直到完成

## 重要说明

- 需要在新终端运行 claude（不能在 Claude Code 窗口内运行）
- 使用 `--dangerously-skip-permissions` 跳过权限确认
- 使用 `--print` 模式让 claude 执行完自动退出

现在，告诉我你的项目需求是什么？
