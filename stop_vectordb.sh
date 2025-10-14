#!/bin/bash
# stop_vectordb.sh
# Stops Qdrant vector database

set -e

echo "🛑 Stopping Qdrant Vector Database"
echo "===================================="
echo ""

# Check if docker-compose is available
if ! docker compose version &> /dev/null; then
    echo "❌ Error: docker-compose is not available"
    exit 1
fi

# Stop Qdrant
echo "🐳 Stopping Qdrant container..."
docker compose -f docker-compose.vectordb.yml down

echo ""
echo "✅ Qdrant stopped"
echo ""
echo "💡 Data is still persisted in ./qdrant_storage"
echo "   To delete all data: rm -rf qdrant_storage"
echo ""
echo "To start again:"
echo "   ./start_vectordb.sh"
echo ""
