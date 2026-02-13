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
        self.progress_file = self.project_dir / "claude-progress.txt"
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

    def _load_features(self) -> list:
        if not self.feature_file.exists():
            print(f"Error: {self.feature_file} not found")
            return []
        return json.loads(self.feature_file.read_text())

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

            # 直接继承父进程的stdio，实现实时输出
            # 使用 bash -c 来执行管道命令
            process = subprocess.Popen(
                ["bash", "-c", f'cat "{prompt_file}" | claude --print --dangerously-skip-permissions'],
                cwd=str(self.project_dir),
                stdin=subprocess.DEVNULL,  # 不需要stdin
                stdout=None,  # 继承父进程stdout
                stderr=None,  # 继承父进程stderr
            )

            # Wait for completion
            return_code = process.wait()

            # Remove prompt file
            prompt_file.unlink(missing_ok=True)

            if return_code != 0:
                print(f"Error: Claude exited with code {return_code}")
                return False

            # After Claude finishes, commit the progress
            self._commit_progress(feature)
            return True

        except Exception as e:
            print(f"Exception: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _build_feature_prompt(self, feature: dict) -> str:
        """Build prompt for implementing a specific feature"""

        return f"""You are working on a manga generation project.

## Current Task: {feature['title']}

{feature['description']}

## Instructions

1. Read the current project structure:
   ls -la
   cat claude-progress.txt
   cat feature_list.json

2. Implement ONLY this feature - do NOT work on other features

3. Write clean, production-ready code with proper error handling

4. After implementation:
   - Run tests if available
   - Ensure code is bug-free

5. IMPORTANT: When done, respond with "FEATURE_COMPLETE" to signal completion.
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
        """Mark feature as done in progress file"""

        features = self._load_features()

        for f in features:
            if f['id'] == completed_feature['id']:
                f['done'] = True

        self.feature_file.write_text(json.dumps(features, indent=2))

        # Update progress.txt
        self._update_progress_txt(features)

    def _update_progress_txt(self, features: list):
        """Update the readable progress file"""

        lines = [
            f"# Project Progress - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "# Status: In Progress",
            "",
            "## Completed",
        ]

        for f in features:
            if f.get("done"):
                lines.append(f"- [x] {f['title']}")

        lines.extend(["", "## Pending"])

        for f in features:
            if not f.get("done"):
                lines.append(f"- [ ] {f['title']}")

        self.progress_file.write_text("\n".join(lines))

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
            for f in remaining:
                print(f"  - {f}")


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
