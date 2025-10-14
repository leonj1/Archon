#!/bin/bash
# start_vectordb.sh
# Starts Qdrant vector database using docker-compose

set -e

echo "🚀 Starting Qdrant Vector Database"
echo "===================================="
echo ""

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "   Install from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is available
if ! docker compose version &> /dev/null; then
    echo "❌ Error: docker-compose is not available"
    echo "   Make sure you have Docker Compose V2 installed"
    exit 1
fi

# Create qdrant_storage directory if it doesn't exist
if [ ! -d "qdrant_storage" ]; then
    echo "📁 Creating qdrant_storage directory..."
    mkdir -p qdrant_storage
fi

# Start Qdrant
echo "🐳 Starting Qdrant container..."
docker compose -f docker-compose.vectordb.yml up -d

# Wait for health check
echo ""
echo "⏳ Waiting for Qdrant to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:6333/collections > /dev/null 2>&1; then
        echo ""
        echo "✅ Qdrant is ready!"
        echo ""
        echo "📊 Service Information:"
        echo "   REST API:  http://localhost:6333"
        echo "   gRPC API:  localhost:6334"
        echo "   Web UI:    http://localhost:6333/dashboard"
        echo ""
        echo "📁 Data persisted to: ./qdrant_storage"
        echo ""
        echo "To stop Qdrant:"
        echo "   docker compose -f docker-compose.vectordb.yml down"
        echo ""
        echo "To view logs:"
        echo "   docker compose -f docker-compose.vectordb.yml logs -f"
        echo ""
        exit 0
    fi
    sleep 1
done

echo ""
echo "⚠️  Warning: Qdrant took longer than expected to start"
echo "   Check status: docker compose -f docker-compose.vectordb.yml ps"
echo "   View logs: docker compose -f docker-compose.vectordb.yml logs"
exit 1
