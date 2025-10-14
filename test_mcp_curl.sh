#!/bin/bash

echo "Testing MCP Server on Main Branch"
echo "===================================="

# Step 1: Initialize
echo -e "\n1. Initializing MCP connection..."
INIT_RESPONSE=$(curl -s -X POST http://192.168.1.162:8051/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -D /tmp/mcp_headers.txt \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}')

SESSION_ID=$(grep -i "mcp-session-id:" /tmp/mcp_headers.txt | cut -d' ' -f2 | tr -d '\r\n')
echo "Session ID: $SESSION_ID"
echo "Response: $INIT_RESPONSE"

# Step 2: Call health_check tool
echo -e "\n2. Calling health_check tool..."
HEALTH_RESPONSE=$(curl -s -X POST http://192.168.1.162:8051/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "health_check", "arguments": {}}}')

echo "Response: $HEALTH_RESPONSE"

# Step 3: Call rag_get_available_sources tool
echo -e "\n3. Calling rag_get_available_sources tool..."
RAG_RESPONSE=$(curl -s -X POST http://192.168.1.162:8051/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "rag_get_available_sources", "arguments": {}}}')

echo "Response: $RAG_RESPONSE"

echo -e "\n===================================="
echo "Test Complete!"
