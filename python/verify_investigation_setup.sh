#!/bin/bash
# Verify that the investigation system is properly set up

echo "═══════════════════════════════════════════════════════════════"
echo "  Verifying Agent Investigation System Setup"
echo "═══════════════════════════════════════════════════════════════"
echo ""

PASS=0
FAIL=0

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo "✓ Found: $1"
        PASS=$((PASS + 1))
        return 0
    else
        echo "✗ Missing: $1"
        FAIL=$((FAIL + 1))
        return 1
    fi
}

# Function to check file is executable
check_executable() {
    if [ -x "$1" ]; then
        echo "✓ Executable: $1"
        PASS=$((PASS + 1))
        return 0
    else
        echo "✗ Not executable: $1"
        FAIL=$((FAIL + 1))
        return 1
    fi
}

# Function to check service is running
check_service() {
    local url=$1
    local name=$2
    if curl -s "$url" > /dev/null 2>&1; then
        echo "✓ Running: $name ($url)"
        PASS=$((PASS + 1))
        return 0
    else
        echo "✗ Not running: $name ($url)"
        FAIL=$((FAIL + 1))
        return 1
    fi
}

echo "Checking required files..."
echo ""

check_file "/home/jose/src/Archon/python/investigate_crawl_status.py"
check_file "/home/jose/src/Archon/python/setup_investigation_env.sh"
check_file "/home/jose/src/Archon/python/run_investigation.sh"
check_file "/home/jose/src/Archon/python/verify_investigation_setup.sh"
check_file "/home/jose/src/Archon/python/INVESTIGATION_README.md"
check_file "/home/jose/src/Archon/AGENT_INVESTIGATION_SUMMARY.md"

echo ""
echo "Checking file permissions..."
echo ""

check_executable "/home/jose/src/Archon/python/investigate_crawl_status.py"
check_executable "/home/jose/src/Archon/python/setup_investigation_env.sh"
check_executable "/home/jose/src/Archon/python/run_investigation.sh"
check_executable "/home/jose/src/Archon/python/verify_investigation_setup.sh"

echo ""
echo "Checking required services..."
echo ""

check_service "http://localhost:8181/health" "Archon Backend"
check_service "http://localhost:6333/health" "Qdrant Vector DB"

echo ""
echo "Checking environment variables..."
echo ""

if [ -f "/home/jose/src/Archon/.env" ]; then
    echo "✓ Found .env file"
    PASS=$((PASS + 1))

    if grep -q "DATABASE_TYPE=sqlite" /home/jose/src/Archon/.env; then
        echo "✓ DATABASE_TYPE configured for SQLite"
        PASS=$((PASS + 1))
    else
        echo "✗ DATABASE_TYPE not set to sqlite"
        FAIL=$((FAIL + 1))
    fi

    if grep -q "SQLITE_PATH" /home/jose/src/Archon/.env; then
        echo "✓ SQLITE_PATH configured"
        PASS=$((PASS + 1))
    else
        echo "✗ SQLITE_PATH not configured"
        FAIL=$((FAIL + 1))
    fi

    if grep -q "OPENAI_API_KEY" /home/jose/src/Archon/.env; then
        echo "✓ OPENAI_API_KEY configured"
        PASS=$((PASS + 1))
    else
        echo "⚠ OPENAI_API_KEY not in .env (check environment)"
        # Don't count as failure - might be in environment
    fi
else
    echo "✗ .env file not found"
    FAIL=$((FAIL + 1))
fi

# Check for ANTHROPIC_API_KEY in environment
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✓ ANTHROPIC_API_KEY set in environment"
    PASS=$((PASS + 1))
else
    echo "⚠ ANTHROPIC_API_KEY not in environment (check .env)"
fi

echo ""
echo "Checking Python dependencies..."
echo ""

if command -v uv &> /dev/null; then
    echo "✓ uv package manager installed"
    PASS=$((PASS + 1))

    # Suppress virtual environment path warning (harmless with uv run)
    if uv pip list 2>&1 | grep -v "does not match the project environment path" | grep -q "claude-agent-sdk"; then
        echo "✓ claude-agent-sdk installed"
        PASS=$((PASS + 1))
    else
        echo "✗ claude-agent-sdk not installed"
        echo "  Run: uv add claude-agent-sdk"
        FAIL=$((FAIL + 1))
    fi

    if uv pip list 2>&1 | grep -v "does not match the project environment path" | grep -q "qdrant-client"; then
        echo "✓ qdrant-client installed"
        PASS=$((PASS + 1))
    else
        echo "✗ qdrant-client not installed"
        echo "  Run: uv add qdrant-client"
        FAIL=$((FAIL + 1))
    fi

    if uv pip list 2>&1 | grep -v "does not match the project environment path" | grep -q "rich"; then
        echo "✓ rich installed"
        PASS=$((PASS + 1))
    else
        echo "✗ rich not installed"
        echo "  Run: uv add rich"
        FAIL=$((FAIL + 1))
    fi
else
    echo "✗ uv not installed"
    echo "  Install from: https://github.com/astral-sh/uv"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Verification Results"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✓ All checks passed! System is ready."
    echo ""
    echo "Run the investigation with:"
    echo "  cd /home/jose/src/Archon/python"
    echo "  ./run_investigation.sh"
    echo ""
    exit 0
else
    echo "✗ Some checks failed. Please fix the issues above."
    echo ""
    echo "Quick fixes:"
    echo "  1. Install dependencies:"
    echo "     ./setup_investigation_env.sh"
    echo ""
    echo "  2. Start backend:"
    echo "     cd /home/jose/src/Archon && make restart"
    echo ""
    echo "  3. Start Qdrant:"
    echo "     docker run -d --name qdrant-archon -p 6333:6333 qdrant/qdrant:latest"
    echo ""
    exit 1
fi
