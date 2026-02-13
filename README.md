# Long-Running Agent Harness 使用指南

基于 [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) 实现。

## 概述

这个 harness 让你能够用 Claude Code 运行大型长期任务，通过以下方式：

- **增量进度**: 每次只做一个功能
- **清洁状态**: 完成后提交 git，保持代码可部署
- **自动追踪**: 自动记录进度，无需人工管理

---

## 快速开始

### 1. 初始化项目

```bash
python3 agent_harness.py ~/work/manga --init "创建一个程序，可以读取文本文件，从内容设计出漫画分镜..."
```

这会创建：
- `feature_list.json` - 详细功能列表
- `claude-progress.txt` - 进度追踪
- `init.sh` - 环境启动脚本
- `requirements.txt` / `README.md` - 项目基础文件
- 初始化 git 仓库

### 2. 运行任务（三选一）

#### 方式 1：手动交互（推荐首次）

```bash
cd ~/work/manga
claude --dangerously-skip-permissions
```

告诉 Claude "开始工作"即可。你可以直接交互，观察它如何实现功能。

#### 方式 2：自动循环运行

```bash
python3 autorun.py ~/work/manga
```

全自动运行流程：
1. 读取下一个未完成的功能
2. 调用 Claude 实现
3. 自动 git commit
4. 更新进度文件
5. 重复直到全部完成

按 `Ctrl+C` 可随时停止。

#### 方式 3：交互式选择

```bash
./start-harness.sh ~/work/manga
```

弹出菜单选择：手动 / 自动 / Subagent 模式。

---

## 核心文件说明

| 文件 | 用途 |
|------|------|
| `feature_list.json` | 所有功能点列表，包含 ID、标题、描述、优先级、依赖 |
| `claude-progress.txt` | 当前进度摘要（人类可读） |
| `CLAUDE.md` | Claude 自动加载的规则 |
| `init.sh` | 启动开发环境脚本 |

---

## 工作流程

```
┌─────────────────────────────────────────────┐
│  初始化                                      │
│  python harness.py --init "需求描述"        │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│  会话开始                                    │
│  1. 读取 claude-progress.txt              │
│  2. 读取 feature_list.json                 │
│  3. 选择一个功能                            │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│  实现功能                                    │
│  - 编写代码                                 │
│  - 测试验证                                 │
│  - 确保清洁状态                             │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│  会话结束                                    │
│  - git add && git commit                   │
│  - 更新 feature_list.json (done: true)     │
│  - 更新 claude-progress.txt                │
└─────────────────────────────────────────────┘
```

---

## 无干预运行

使用 `--dangerously-skip-permissions` 跳过所有权限确认：

```bash
claude --dangerously-skip-permissions
```

或配置项目级权限 `.claude.json`：

```json
{
  "permissions": {
    "allow": ["Bash(git:*)", "Bash(npm:*)", "Write", "Read", "Edit"]
  }
}
```

---

## 使用技巧

1. **分小任务**: 功能拆得越细，进展越明显
2. **频繁提交**: 每次完成一个小功能就 commit
3. **检查状态**: 用 `git log --oneline` 查看做了什么
4. **中断恢复**: 任何时候运行 `claude`，它会读取进度文件继续

---

## 文件结构

```
harness/
├── agent_harness.py       # 项目初始化工具
├── autorun.py            # 自动循环运行脚本
├── start-harness.sh      # 交互式启动脚本
├── harness_system_prompt.md  # 系统级 prompt
├── .claude.json          # 项目级权限配置
└── README.md

project/
├── CLAUDE.md             # ← 项目自动加载
├── feature_list.json    # 功能列表
├── claude-progress.txt  # 进度追踪
├── init.sh              # 启动脚本
├── requirements.txt
├── README.md
└── src/                 # 你的代码
```

---

## 运行示例

```bash
# 1. 初始化项目
python3 agent_harness.py ~/work/manga --init "创建一个漫画生成器..."

# 2. 查看生成的功能列表
cat ~/work/manga/feature_list.json

# 3. 开始自动运行
python3 autorun.py ~/work/manga

# 或手动交互
cd ~/work/manga && claude --dangerously-skip-permissions

# 4. 查看进度
git log --oneline
cat ~/work/manga/claude-progress.txt
```
