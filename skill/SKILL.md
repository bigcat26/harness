---
name: agent-harness
description: 使用 Claude Code 实现长期运行的大型任务。参考 Anthropic 的 "Effective harnesses for long-running agents" 文章，通过增量开发、自动提交和进度追踪来管理复杂项目。
---

# Agent Harness

用于使用 Claude Code 运行长时间任务的工作流。

## 快速开始

### 1. 初始化项目

```bash
python3 <harness-path>/agent_harness.py <project-dir> --init "项目需求描述"
```

这会创建：
- `feature_list.json` - 功能列表
- `claude-progress.txt` - 进度追踪
- `CLAUDE.md` - 项目级规则
- 初始化 git

### 2. 运行任务

```bash
# 方式1: 自动循环运行（需要在新终端运行）
python3 -u <harness-path>/autorun.py <project-dir>

# 方式2: 手动交互
cd <project-dir>
claude --dangerously-skip-permissions
```

## 核心文件

| 文件 | 用途 |
|------|------|
| `feature_list.json` | 功能点列表，包含 ID、标题、描述、优先级 |
| `claude-progress.txt` | 进度摘要 |
| `CLAUDE.md` | Claude 自动加载的规则 |

## 工作流

1. **初始化**: 分析需求，拆分成功能点
2. **循环**:
   - 读取下一个未完成功能
   - Claude 实现
   - 自动 commit
   - 更新进度
3. **结束**: 所有功能完成

## 重要说明

- **不能在 Claude Code 窗口内运行 autorun.py**，需要在新终端运行
- 使用 `--dangerously-skip-permissions` 跳过权限确认
- 脚本会自动 commit 和更新进度文件
