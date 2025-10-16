#!/bin/bash
# Setup script for crawl status investigation
# This script ensures Qdrant and required dependencies are available

set -e

echo "=========================================="
echo "Setting up Investigation Environment"
echo "=========================================="
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
# Suppress virtual environment path warning (it's harmless with uv run)
uv add claude-agent-sdk qdrant-client rich nest-asyncio 2>&1 | grep -v "does not match the project environment path" || true

# Check if Qdrant is running
echo "Checking Qdrant status..."
if ! curl -s http://localhost:6333/health > /dev/null 2>&1; then
    echo "Qdrant is not running. Starting Qdrant with Docker..."

    # Start Qdrant with Docker
    docker run -d \
        --name qdrant-archon \
        -p 6333:6333 \
        -p 6334:6334 \
        -v $(pwd)/../data/qdrant:/qdrant/storage \
        qdrant/qdrant:latest

    echo "Waiting for Qdrant to start..."
    sleep 5

    # Verify Qdrant is running
    if curl -s http://localhost:6333/health > /dev/null 2>&1; then
        echo "✓ Qdrant is running"
    else
        echo "✗ Failed to start Qdrant"
        exit 1
    fi
else
    echo "✓ Qdrant is already running"
fi

# Check if backend is running
echo "Checking Archon backend status..."
if ! curl -s http://localhost:8181/health > /dev/null 2>&1; then
    echo "⚠ Archon backend is not running"
    echo "Please start it with: make restart"
    echo ""
    read -p "Start backend now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd /home/jose/src/Archon
        make restart
    fi
else
    echo "✓ Archon backend is running"
fi

echo ""
echo "=========================================="
echo "Environment Setup Complete!"
echo "=========================================="
echo ""
echo "You can now run the investigation with:"
echo "  uv run python investigate_crawl_status.py"
echo ""
