#!/bin/bash
# Wrapper script for MCP stdio server debugging
exec docker exec -i archon-mcp python -m src.mcp_server.mcp_server_stdio
