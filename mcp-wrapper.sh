#!/bin/bash
# MCP Wrapper for Archon to work with Claude Code

# Force stdio transport mode and suppress logs to stderr
exec docker exec -i -e TRANSPORT=stdio -e LOG_LEVEL=ERROR Archon-MCP python -m src.mcp.mcp_server 2>/tmp/archon-mcp.log