#!/bin/bash
# Quick start script for Test Fix Orchestrator

set -e

echo "🤖 Test Fix Orchestrator - Quick Start"
echo "======================================="
echo ""

# Check for required dependencies
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.12+"
    exit 1
fi

# Check for required Python packages
echo "📦 Checking dependencies..."
python3 -c "import claude_agent_sdk" 2>/dev/null || {
    echo "❌ claude-agent-sdk not found."
    echo "Install with: pip install claude-agent-sdk"
    echo "Or with uv: uv add claude-agent-sdk"
    exit 1
}

python3 -c "import rich" 2>/dev/null || {
    echo "❌ rich not found."
    echo "Install with: pip install rich"
    echo "Or with uv: uv add rich"
    exit 1
}

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    if [ ! -f .env ]; then
        echo "⚠️  Warning: ANTHROPIC_API_KEY not found in environment or .env file"
        echo "Please set your API key before running."
        exit 1
    fi
fi

echo "✅ All dependencies found"
echo ""

# Check for previous state
if [ -f "test_fix_state.json" ]; then
    echo "📁 Found previous state file: test_fix_state.json"
    echo ""
    read -p "Resume from previous run? (y/n): " resume
    if [ "$resume" != "y" ]; then
        echo "🗑️  Removing previous state..."
        rm -f test_fix_state.json
        rm -f test_fix_log.jsonl
        rm -rf .test_fix_backups
    fi
fi

echo ""
echo "🚀 Starting Test Fix Orchestrator..."
echo "   - Max attempts per test: 3"
echo "   - Timeout: 1 hour"
echo "   - Test command: make test"
echo ""
echo "Press Ctrl+C to stop (progress will be saved)"
echo ""

# Run the orchestrator
if command -v uv &> /dev/null; then
    echo "Using uv..."
    uv run python test_fix_orchestrator.py
else
    echo "Using python..."
    python3 test_fix_orchestrator.py
fi

# Show results
echo ""
echo "✨ Orchestrator completed!"
echo ""

if [ -f "TEST_FIX_SUMMARY.md" ]; then
    echo "📊 Summary Report:"
    echo "=================="
    head -n 20 TEST_FIX_SUMMARY.md
    echo ""
    echo "Full report: TEST_FIX_SUMMARY.md"
fi

if [ -f "test_fix_state.json" ]; then
    echo ""
    echo "📈 Final Statistics:"
    echo "==================="
    python3 -c "import json; s=json.load(open('test_fix_state.json')); print(f\"Total: {s['total_tests']}, Fixed: {s['fixed_count']}, Skipped: {s['skipped_count']}\")"
fi
