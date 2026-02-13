#!/usr/bin/env python3
"""
Long-Running Agent Harness for Claude Code

Based on Anthropic's "Effective harnesses for long-running agents"
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from datetime import datetime


class AgentHarness:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.progress_file = self.project_dir / "claude-progress.txt"
        self.feature_file = self.project_dir / "feature_list.json"
        self.init_script = self.project_dir / "init.sh"

    def initialize(self, user_spec: str):
        """Run initializer agent to set up the environment"""
        print("=" * 60)
        print("INITIALIZER AGENT: Setting up environment")
        print("=" * 60)

        # Use Claude to parse features from user spec
        print("\nAnalyzing requirements with Claude...")
        features = self._parse_features_with_claude(user_spec)

        print(f"\nIdentified {len(features)} features:")
        for f in features:
            print(f"  - {f['description']}")

        # Write feature list
        self._write_feature_list(features)

        # Create init script template
        self._write_init_script()

        # Create initial progress file
        self._write_progress_file(features, status="initialized")

        # Initialize git
        self._init_git()

        # Create basic project structure
        self._create_project_structure()

        print("\n" + "=" * 60)
        print("Environment initialized!")
        print("=" * 60)
        print(f"  - Feature list: {self.feature_file}")
        print(f"  - Progress file: {self.progress_file}")
        print(f"  - Init script: {self.init_script}")
        print("\nNow run: claude")

    def _parse_features_with_claude(self, user_spec: str) -> list:
        """Use Claude to expand user spec into detailed feature list"""

        prompt = f"""You are a product manager. Given the following user requirement, break it down into specific, actionable features.

For each feature, provide:
1. A clear title
2. A detailed description
3. Priority (high/medium/low)
4. Dependencies (what other features must be done first)

User requirement:
{user_spec}

Output ONLY a JSON array of features, no other text. Format:
[
  {{
    "id": 1,
    "title": "Feature title",
    "description": "Detailed description",
    "priority": "high|medium|low",
    "dependencies": []
  }}
]"""

        # Call Claude API via claude CLI
        result = subprocess.run(
            ["claude", "-p", "--dangerously-skip-permissions", prompt],
            capture_output=True,
            text=True,
            input="\n"
        )

        # Try to parse JSON from output
        output = result.stdout
        # Find JSON array in output
        start = output.find('[')
        end = output.rfind(']') + 1

        if start != -1 and end > start:
            try:
                features = json.loads(output[start:end])
                # Add done: false to each
                for f in features:
                    f["done"] = False
                return features
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")

        # Fallback: create reasonable features based on the spec
        print("\nUsing intelligent fallback for feature list...")
        return self._create_intelligent_features(user_spec)

    def _create_intelligent_features(self, spec: str) -> list:
        """Create features based on keywords in the spec"""

        features = []
        spec_lower = spec.lower()

        # Common features for this type of app
        all_features = [
            {
                "id": 1,
                "title": "Text File Reader",
                "description": "Read and parse text files (stories, novels) from the filesystem",
                "priority": "high",
                "dependencies": []
            },
            {
                "id": 2,
                "title": "Story Parser & Chunking",
                "description": "Parse story content into scenes, dialogues, and narrative elements",
                "priority": "high",
                "dependencies": [1]
            },
            {
                "id": 3,
                "title": "Comic Storyboard Generator",
                "description": "Design comic panel layouts from story content, output as Mermaid diagrams",
                "priority": "high",
                "dependencies": [2]
            },
            {
                "id": 4,
                "title": "Character Detection & Management",
                "description": "Identify and track characters, their appearances, and dialogue",
                "priority": "high",
                "dependencies": [2]
            },
            {
                "id": 5,
                "title": "Image Prompt Generator",
                "description": "Generate detailed image prompts for each comic panel based on scene description",
                "priority": "high",
                "dependencies": [3, 4]
            },
            {
                "id": 6,
                "title": "Image Generation Integration",
                "description": "Call third-party image generation APIs (DALL-E, Midjourney, Stable Diffusion) to create comic panels",
                "priority": "high",
                "dependencies": [5]
            },
            {
                "id": 7,
                "title": "Text-to-Speech Integration",
                "description": "Convert character dialogues to audio using TTS APIs",
                "priority": "high",
                "dependencies": [4]
            },
            {
                "id": 8,
                "title": "Audio-Visual Sync",
                "description": "Synchronize audio narration with comic panel display timing",
                "priority": "medium",
                "dependencies": [6, 7]
            },
            {
                "id": 9,
                "title": "Comic Book Export",
                "description": "Export final有声漫画 as PDF, HTML, or video format",
                "priority": "medium",
                "dependencies": [6, 7, 8]
            },
            {
                "id": 10,
                "title": "UI/Frontend Interface",
                "description": "User interface for uploading text, viewing storyboard, and managing generation",
                "priority": "medium",
                "dependencies": [3]
            }
        ]

        # Simple keyword matching to filter relevant features
        keywords = {
            "read": [1], "text": [1], "file": [1], "story": [1, 2], "novel": [1, 2],
            "comic": [3, 4, 6, 9], "mermaid": [3], "storyboard": [3], "panel": [3],
            "character": [4], "dialogue": [4], "prompt": [5], "image": [6],
            "audio": [7], "tts": [7], "speech": [7], "sound": [7],
            "有声": [7, 8, 9], "video": [9], "export": [9], "generate": [6, 7],
            "interface": [10], "ui": [10], "frontend": [10]
        }

        selected_ids = set()
        for keyword, feature_ids in keywords.items():
            if keyword in spec_lower:
                selected_ids.update(feature_ids)

        # Always include core features if nothing matched
        if not selected_ids:
            return all_features[:5]

        features = [f for f in all_features if f["id"] in selected_ids]

        # Reassign IDs and handle dependencies
        id_map = {}
        for i, f in enumerate(features, 1):
            old_id = f["id"]
            f["id"] = i
            id_map[old_id] = i

        for f in features:
            f["dependencies"] = [id_map[d] for d in f["dependencies"] if d in id_map]

        return features

    def _write_feature_list(self, features: list):
        self.feature_file.write_text(json.dumps(features, indent=2))

    def _write_init_script(self, content=None):
        if content is None:
            content = '''#!/bin/bash
# Initialize development environment

echo "Setting up manga generation project..."

# Install dependencies (uncomment as needed)
# pip install -r requirements.txt
# npm install

# Start development server (example)
# python main.py

echo "Environment ready!"
'''
        self.init_script.write_text(content)
        os.chmod(self.init_script, 0o755)

    def _write_progress_file(self, features: list, status: str):
        lines = [
            f"# Project Progress - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"# Status: {status}",
            "",
            "## Completed",
            "",
            "## In Progress",
            "",
            "## Pending",
        ]
        for f in features:
            checkbox = "[x]" if f.get("done", False) else "[ ]"
            lines.append(f"- {checkbox} [{f['priority'].upper()}] {f['title']}: {f['description']}")

        self.progress_file.write_text("\n".join(lines))

    def _init_git(self):
        os.chdir(self.project_dir)
        # Check if already a git repo
        if (self.project_dir / ".git").exists():
            return

        subprocess.run(["git", "init"], capture_output=True)
        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit: project setup"], capture_output=True)

    def _create_project_structure(self):
        """Create basic project structure"""

        # Create requirements.txt
        req_file = self.project_dir / "requirements.txt"
        if not req_file.exists():
            req_file.write_text("""# Core dependencies
anthropic>=0.18.0
requests>=2.31.0
python-dotenv>=1.0.0

# For PDF export
reportlab>=4.0.0

# For UI (optional)
flask>=3.0.0
""")

        # Create README
        readme_file = self.project_dir / "README.md"
        if not readme_file.exists():
            readme_file.write_text("""# Manga Generator Project

Generated by Claude Code Long-Running Agent Harness.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py --input your_story.txt
```
""")

    def start_session(self):
        """Start a coding agent session"""
        print("=" * 60)
        print("CODING AGENT: Starting session")
        print("=" * 60)

        # Show current status
        if self.progress_file.exists():
            print("\nCurrent progress:")
            print(self.progress_file.read_text())

        # Show pending features
        if self.feature_file.exists():
            features = json.loads(self.feature_file.read_text())
            pending = [f for f in features if not f.get("done", False)]
            print(f"\n{len(pending)} pending features")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python agent_harness.py <project-dir> --init 'user spec'")
        print("  python agent_harness.py <project-dir> --status")
        sys.exit(1)

    project_dir = sys.argv[1]
    harness = AgentHarness(project_dir)

    if "--init" in sys.argv:
        idx = sys.argv.index("--init")
        user_spec = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "No spec provided"
        harness.initialize(user_spec)
    elif "--status" in sys.argv:
        harness.start_session()
    else:
        print("Unknown command. Use --init or --status")
        sys.exit(1)


if __name__ == "__main__":
    main()
