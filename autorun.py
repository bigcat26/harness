#!/usr/bin/env python3
"""
Auto-Run Agent Harness for Claude Code

实时显示输出，自动循环运行所有功能
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime


class AutoRunHarness:
    def __init__(self, project_dir: str):
        # 解析真实路径
        self.project_dir = Path(os.path.expanduser(project_dir)).resolve()
        self.feature_file = self.project_dir / "feature_list.json"
        self.max_iterations = 100
        print(f"Project directory: {self.project_dir}")

    def run(self):
        """Main loop: run Claude until all features are done"""

        print("=" * 60)
        print("AUTO-RUN HARNESS: Starting")
        print("=" * 60)
        print(f"Project: {self.project_dir}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        for iteration in range(1, self.max_iterations + 1):
            print(f"\n{'='*50}")
            print(f"ITERATION {iteration}")
            print(f"{'='*50}")

            # Check if all features are done
            features = self._load_features()
            pending = [f for f in features if not f.get("done", False)]

            if not pending:
                print("\n✅ All features completed!")
                break

            print(f"Remaining: {len(pending)} features")
            print(f"Next: {pending[0]['title']}")
            print()

            # Run Claude for one feature
            success = self._run_claude_for_feature(pending[0])

            if success:
                print(f"\n✓ Feature '{pending[0]['title']}' completed")
            else:
                print(f"\n⚠️ Failed or no changes for '{pending[0]['title']}'")

            # Small delay between iterations
            time.sleep(2)

        self._print_summary()

    def _load_feature_list(self) -> dict:
        """加载完整的 feature list（包含 project_context 和 features）"""
        if not self.feature_file.exists():
            print(f"Error: {self.feature_file} not found")
            return {"project_context": {}, "features": []}
        return json.loads(self.feature_file.read_text())

    def _load_features(self) -> list:
        """仅加载 features 列表（向后兼容）"""
        data = self._load_feature_list()
        # 兼容旧格式（直接是数组）和新格式（包含 project_context）
        if isinstance(data, list):
            return data
        return data.get("features", [])

    def _run_claude_for_feature(self, feature: dict) -> bool:
        """Run Claude once to implement one feature"""

        # Build the prompt
        prompt = self._build_feature_prompt(feature)

        print("-" * 40)
        print("Running Claude...")
        print("-" * 40)
        sys.stdout.flush()

        try:
            # Write prompt to a temp file
            prompt_file = self.project_dir / ".prompt.txt"
            prompt_file.write_text(prompt)

            # 捕获输出以检测信号，同时实时显示
            process = subprocess.Popen(
                ["bash", "-c", f'cat "{prompt_file}" | claude --print --dangerously-skip-permissions'],
                cwd=str(self.project_dir),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1  # 行缓冲
            )

            # 实时显示输出并收集用于信号检测
            output_lines = []
            for line in process.stdout:
                print(line, end='')  # 实时显示
                output_lines.append(line)
                sys.stdout.flush()

            # Wait for completion
            return_code = process.wait()

            # Remove prompt file
            prompt_file.unlink(missing_ok=True)

            if return_code != 0:
                print(f"\nError: Claude exited with code {return_code}")
                return False

            # 检测输出信号
            output_text = ''.join(output_lines)
            signal = self._detect_completion_signal(output_text)
            
            if signal == "FEATURE_BLOCKED":
                print("\n⚠️  Feature is BLOCKED - requires human intervention")
                print("Pausing automation. Please resolve the issue and restart.")
                sys.exit(0)
            elif signal == "FEATURE_FAILED":
                print("\n❌ Feature FAILED - encountered unresolvable error")
                print("Skipping this feature and continuing...")
                return False
            elif signal == "FEATURE_COMPLETE":
                print("\n✓ Feature COMPLETE")
                # After Claude finishes, commit the progress
                self._commit_progress(feature)
                return True
            else:
                print("\n⚠️  No completion signal detected, assuming success")
                self._commit_progress(feature)
                return True

        except Exception as e:
            print(f"\nException: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _detect_completion_signal(self, output: str) -> str:
        """检测 Claude 输出中的完成信号"""
        # 检查最后 2000 个字符（信号通常在输出末尾）
        tail = output[-2000:] if len(output) > 2000 else output
        
        if "FEATURE_BLOCKED" in tail:
            return "FEATURE_BLOCKED"
        elif "FEATURE_FAILED" in tail:
            return "FEATURE_FAILED"
        elif "FEATURE_COMPLETE" in tail:
            return "FEATURE_COMPLETE"
        else:
            return "UNKNOWN"

    def _build_feature_prompt(self, feature: dict) -> str:
        """动态构建 feature prompt，包含项目背景信息"""

        data = self._load_feature_list()

        # 兼容旧格式（直接是数组）和新格式（包含 project_context 和 features）
        if isinstance(data, list):
            # 旧格式：直接是 features 数组
            context = {}
        else:
            # 新格式：包含 project_context
            context = data.get("project_context", {})
        
        # 构建项目背景部分
        project_info = ""
        if context:
            project_info = f"""## 项目背景

- **项目名称**: {context.get('name', 'Unknown')}
- **描述**: {context.get('description', '')}
- **技术栈**: {context.get('tech_stack', '')}
- **架构**: {context.get('architecture', '')}
- **开发方法**: {context.get('development_approach', '')}

"""
            
            # 添加代码规范
            standards = context.get('code_standards', [])
            if standards:
                project_info += "## 代码规范\n\n"
                for std in standards:
                    project_info += f"- {std}\n"
                project_info += "\n"
        
        # 构建完整 prompt
        return f"""你是一个增量开发代理，专注于实现单个功能。

{project_info}## 当前任务: {feature['title']}

{feature['description']}

## 执行步骤

1. 查看项目结构和当前状态
2. 实现 ONLY 这个功能 - 不要实现其他功能
3. 编写清晰、生产级别的代码，包含适当的错误处理
4. 如果需要测试，运行测试确保功能正常
5. 确保代码无明显 bug

## 完成信号

完成后，请在响应中输出以下信号之一：
- "FEATURE_COMPLETE" - 功能已完成
- "FEATURE_BLOCKED" - 需要人工干预才能继续
- "FEATURE_FAILED" - 遇到无法解决的错误

注意：不需要关注整体项目是否完成，只需专注当前功能。
"""

    def _commit_progress(self, feature: dict):
        """Commit the completed feature"""

        os.chdir(self.project_dir)

        # Add files
        subprocess.run(["git", "add", "-A"], capture_output=True)

        # Check if there are changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        )

        if result.stdout.strip():
            # Commit
            commit_msg = f"feat: {feature['title']}"
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                capture_output=True
            )
            print(f"\n✓ Committed: {commit_msg}")
        else:
            print("\n✓ No changes to commit")

        # Update progress file
        self._update_progress(feature)

    def _update_progress(self, completed_feature: dict):
        """Mark feature as done in feature_list.json"""

        data = self._load_feature_list()
        features = data.get("features", data if isinstance(data, list) else [])

        for f in features:
            if f['id'] == completed_feature['id']:
                f['done'] = True

        # 保存回文件（保持新旧格式兼容）
        if isinstance(data, list):
            self.feature_file.write_text(json.dumps(features, indent=2, ensure_ascii=False))
        else:
            data['features'] = features
            self.feature_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))


    def _print_summary(self):
        """Print final summary"""
        features = self._load_features()
        completed = len([f for f in features if f.get("done", False)])
        total = len(features)

        print("\n" + "=" * 60)
        print("AUTO-RUN COMPLETE")
        print("=" * 60)
        print(f"Completed: {completed}/{total} features")

        if completed < total:
            remaining = [f['title'] for f in features if not f.get("done", False)]
            print("\nRemaining:")
            for title in remaining:
                print(f"  - {title}")
        
        # 显示进度摘要
        print("\n" + "=" * 60)
        print("PROGRESS SUMMARY")
        print("=" * 60)
        for f in features:
            status = "✓" if f.get("done") else "○"
            print(f"{status} [{f['id']}] {f['title']}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python autorun.py <project-dir>")
        print("\nThis will run Claude Code automatically until all features are done.")
        print("Press Ctrl+C to stop at any time.")
        sys.exit(1)

    project_dir = sys.argv[1]

    print(f"Starting auto-run harness for: {project_dir}")
    print("Press Ctrl+C to stop\n")

    try:
        harness = AutoRunHarness(project_dir)
        harness.run()
    except KeyboardInterrupt:
        print("\n\nStopped by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
