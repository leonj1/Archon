#!/bin/bash
# run_all_vectordb_agents.sh
# Runs all Claude Code agents in sequence to build the complete pipeline

set -e  # Exit on error

echo "🤖 Starting Vector DB Pipeline Agent Build"
echo "=========================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "   Create .env with ANTHROPIC_API_KEY and OPENAI_API_KEY"
    exit 1
fi

if ! grep -q "ANTHROPIC_API_KEY" .env; then
    echo "❌ Error: ANTHROPIC_API_KEY not found in .env"
    exit 1
fi

if ! grep -q "OPENAI_API_KEY" .env; then
    echo "⚠️  Warning: OPENAI_API_KEY not found in .env"
    echo "   Integration tests will be skipped"
fi

# Check if Qdrant is running
if ! curl -s http://localhost:6333/collections > /dev/null 2>&1; then
    echo "⚠️  Warning: Qdrant not running on localhost:6333"
    echo "   Start with: docker run -p 6333:6333 qdrant/qdrant"
    echo "   Continuing anyway..."
fi

echo "✓ Prerequisites checked"
echo ""

# Define agents in order
AGENTS=(
    "crawling-service-builder"
    "vectordb-service-builder"
    "wrapper-service-builder"
    "integration-test-builder"
    "test-validator"
)

# Agent descriptions
declare -A DESCRIPTIONS
DESCRIPTIONS[crawling-service-builder]="SimpleCrawlingService (web crawling)"
DESCRIPTIONS[vectordb-service-builder]="SimpleVectorDBService (Qdrant storage)"
DESCRIPTIONS[wrapper-service-builder]="CrawlAndStoreService (unified wrapper)"
DESCRIPTIONS[integration-test-builder]="Integration test (real API calls)"
DESCRIPTIONS[test-validator]="Test validation & quality check"

# Run each agent
TOTAL=${#AGENTS[@]}
CURRENT=0

for agent in "${AGENTS[@]}"; do
    CURRENT=$((CURRENT + 1))
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Step $CURRENT/$TOTAL: ${DESCRIPTIONS[$agent]}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    python create_vectordb_agents.py --agent "$agent" --model sonnet

    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ $agent completed successfully"
    else
        echo ""
        echo "❌ $agent failed"
        exit 1
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 All agents completed successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Generated files:"
echo "  📄 python/src/server/services/simple_crawling_service.py"
echo "  📄 python/src/server/services/simple_vectordb_service.py"
echo "  📄 python/src/server/services/crawl_and_store_service.py"
echo "  📄 python/tests/integration/test_crawl_and_store_real.py"
echo "  📄 python/tests/integration/VALIDATION_REPORT.md"
echo ""
echo "Next steps:"
echo "  1. Review the generated code"
echo "  2. Run integration test: cd python && uv run pytest tests/integration/test_crawl_and_store_real.py -v"
echo "  3. Use the service in your application"
echo ""
