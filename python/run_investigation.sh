#!/bin/bash
# Wrapper script to run crawl status investigation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      Archon Crawl Status Investigation Tool                   ║"
echo "║      Using Claude Code SDK Agents                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if setup has been run (suppress venv path warning)
if ! uv pip list 2>&1 | grep -q claude-agent-sdk; then
    echo "⚠ Dependencies not installed. Running setup..."
    ./setup_investigation_env.sh
fi

# Check environment
echo "Checking environment..."
echo ""

# Check .env file
if [ ! -f "/home/jose/src/Archon/.env" ]; then
    echo "✗ .env file not found at /home/jose/src/Archon/.env"
    exit 1
fi
echo "✓ .env file found"

# Check backend
if curl -s http://localhost:8181/health > /dev/null 2>&1; then
    echo "✓ Archon backend is running (port 8181)"
else
    echo "✗ Archon backend is NOT running"
    echo "  Start it with: cd /home/jose/src/Archon && make restart"
    exit 1
fi

# Check Qdrant
if curl -s http://localhost:6333/health > /dev/null 2>&1; then
    echo "✓ Qdrant is running (port 6333)"
else
    echo "⚠ Qdrant is NOT running - starting it now..."
    docker run -d \
        --name qdrant-archon \
        -p 6333:6333 \
        -p 6334:6334 \
        -v $(pwd)/../data/qdrant:/qdrant/storage \
        qdrant/qdrant:latest 2>/dev/null || echo "  (Qdrant may already be running)"

    sleep 3

    if curl -s http://localhost:6333/health > /dev/null 2>&1; then
        echo "✓ Qdrant started successfully"
    else
        echo "✗ Failed to start Qdrant"
        exit 1
    fi
fi

# Check ANTHROPIC_API_KEY
if [ -z "$ANTHROPIC_API_KEY" ]; then
    # Try to load from .env
    export $(grep -v '^#' /home/jose/src/Archon/.env | xargs)
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo ""
    echo "✗ ANTHROPIC_API_KEY not set"
    echo "  Set it in .env file or export it:"
    echo "  export ANTHROPIC_API_KEY=your-key-here"
    exit 1
fi
echo "✓ ANTHROPIC_API_KEY is set"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Starting Investigation..."
echo "════════════════════════════════════════════════════════════════"
echo ""

# Run the investigation (uv run handles virtual environment automatically)
# The VIRTUAL_ENV warning is harmless and can be ignored
uv run python investigate_crawl_status.py 2>&1 | grep -v "does not match the project environment path"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Investigation complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Generated files:"
echo "  1. Investigation Report:"
echo "     /home/jose/src/Archon/CRAWL_STATUS_INVESTIGATION.md"
echo ""
echo "  2. Integration Tests:"
echo "     /home/jose/src/Archon/python/tests/integration/test_crawl_status_integration.py"
echo ""
echo "Run tests with:"
echo "  cd /home/jose/src/Archon/python"
echo "  uv run pytest tests/integration/test_crawl_status_integration.py -v"
echo ""
