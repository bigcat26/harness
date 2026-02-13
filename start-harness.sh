#!/bin/bash
# Start Long-Running Agent Harness

set -e

PROJECT_DIR="${1:-.}"

echo "=========================================="
echo "Claude Code Long-Running Agent Harness"
echo "=========================================="
echo "Project: $PROJECT_DIR"
echo ""

cd "$PROJECT_DIR"

# Check if project is initialized
if [ ! -f "feature_list.json" ]; then
    echo "Error: Project not initialized."
    echo "Run: python3 agent_harness.py $PROJECT_DIR --init 'your requirements'"
    exit 1
fi

# Show current status
echo "Current features:"
cat feature_list.json | python3 -m json.tool | head -30

echo ""
echo "=========================================="
echo "Choose mode:"
echo "=========================================="
echo "1) Manual mode - interact with Claude directly"
echo "2) Auto mode  - Claude runs automatically (one feature at a time)"
echo "3) Subagent mode - Claude manages subagents"
echo ""
read -p "Enter choice (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "Starting Claude in manual mode..."
        echo "Tell Claude to read CLAUDE.md for harness rules"
        echo ""
        claude --dangerously-skip-permissions
        ;;
    2)
        echo ""
        echo "Starting Auto-Run Harness..."
        echo "Press Ctrl+C to stop"
        echo ""
        python3 ../agent_harness.py/autorun.py .
        ;;
    3)
        echo ""
        echo "Starting Claude with subagent instructions..."
        claude --dangerously-skip-permissions --append-system-prompt "$(cat ../harness_system_prompt.md)"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
