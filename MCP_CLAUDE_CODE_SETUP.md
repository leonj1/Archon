# Archon MCP Server Setup for Claude Code

This guide explains how to connect Archon's MCP server to Claude Code for enhanced AI-powered development.

## Problem Fixed

The original Archon MCP server used SSE (Server-Sent Events) transport, which is deprecated in Claude Code. Claude Code requires either **stdio** or **HTTP** transport for proper compatibility. Archon now defaults to the modern **streamable HTTP** transport so Claude Code CLI connects reliably.

## What Changed

1. **Added stdio transport support** to the MCP server (`mcp_server.py`)
2. **Created `.mcp.json` configuration** for Claude Code
3. **Updated logging** to use stderr in stdio mode (prevents protocol interference)
4. **Made transport configurable** via environment variable or command-line argument

## Setup Instructions

### Option 1: Local Python Installation (Recommended)

1. **Install Dependencies**
   ```bash
   cd python
   uv sync --group mcp
   # or with pip:
   pip install mcp==1.12.2 httpx pydantic python-dotenv supabase logfire fastapi
   ```

2. **Configure Environment**
   Create or update your `.env` file in the project root:
   ```env
   SUPABASE_URL=your-supabase-url
   SUPABASE_SERVICE_KEY=your-service-key
   OPENAI_API_KEY=your-openai-key  # Optional
   API_SERVICE_URL=http://localhost:8181  # Your Archon server URL
   ```

3. **Add MCP Server to Claude Code**

   The `.mcp.json` file has already been created in the project root. Claude Code should automatically detect it.

   If you need to manually configure the HTTP transport, you can use:
   ```bash
   claude mcp add --transport streamable-http archon http://localhost:8051/mcp
   ```

4. **Restart Claude Code**
   After configuration, restart Claude Code for the changes to take effect.

### Option 2: Docker Installation

If you prefer to use Docker, the configuration includes a Docker-based setup:

1. **Build the Docker Image**
   ```bash
   docker compose build archon-mcp
   ```

2. **Use the Docker Configuration**
   The `.mcp.json` includes an `archon-docker` server configuration that runs the MCP server in a container.

3. **Switch to Docker Config**
   Edit `.mcp.json` and rename `archon-docker` to `archon` (or add both).

## How It Works

### Transport Modes

The updated MCP server supports three transport modes:

1. **streamable-http** *(default)* - Modern HTTP transport supported by Claude Code CLI and other MCP clients
2. **stdio** - Uses stdin/stdout for communication
3. **sse** *(legacy)* - Server-Sent Events for older HTTP clients

Select a transport via:
- Command-line argument: `python mcp_server.py <streamable-http|stdio|sse>`
- Environment variable: `MCP_TRANSPORT=streamable-http`
- Default: `streamable-http`

### Logging Configuration

- **stdio mode**: Logs go to stderr to avoid interfering with the JSON-RPC protocol
- **sse mode**: Logs go to stdout as before
- All modes also log to `/tmp/mcp_server.log` if available

## Available MCP Tools

Once connected, Claude Code will have access to these Archon tools:

### Knowledge Base Tools
- `rag_search_knowledge_base` - Search your knowledge base
- `rag_search_code_examples` - Find code snippets
- `rag_get_available_sources` - List knowledge sources
- `rag_list_pages_for_source` - Browse documentation
- `rag_read_full_page` - Read complete pages

### Project Management
- `list_projects` - List, search, or get projects
- `manage_project` - Create, update, delete projects

### Task Management
- `list_tasks` - List, search, filter tasks
- `manage_task` - Create, update, delete tasks

### Document Management
- `list_documents` - List project documents
- `manage_document` - Manage documents

### Version Control
- `list_versions` - View version history
- `manage_version` - Create or restore versions

## Troubleshooting

### MCP Server Not Connecting

1. **Check Dependencies**
   ```bash
   python -c "import mcp; print(mcp.__version__)"
   ```
   Should show version 1.12.2

2. **Test Manually**
   ```bash
   cd python
   echo '{"jsonrpc":"2.0","id":1,"method":"initialize"}' | python src/mcp_server/mcp_server.py stdio
   ```
   You should see a JSON response with server capabilities.

3. **Check Logs**
   - Look at stderr output during startup
   - Check `/tmp/mcp_server.log` for detailed logs
   - In Claude Code, check the MCP connection status

### Environment Variables Not Loading

1. Ensure `.env` file is in the project root
2. Check file permissions
3. Verify variable names match exactly

### Windows-Specific Issues

On Windows (native, not WSL), you may need to:
1. Use full Python path in `.mcp.json`
2. Add `cmd /c` wrapper for better compatibility
3. Ensure Python is in your PATH

Example Windows configuration:
```json
{
  "mcpServers": {
    "archon": {
      "type": "stdio",
      "command": "cmd",
      "args": ["/c", "python", "python\\src\\mcp_server\\mcp_server.py", "stdio"],
      "env": { ... }
    }
  }
}
```

## Testing the Connection

1. **Start Claude Code** with the project directory open
2. **Check MCP Status** - Claude Code should show the MCP server as connected
3. **Test a Tool** - Try running a simple command like asking Claude to "list available knowledge sources using MCP"

## Development Notes

### Running Both Transports

For development, you can run:
- **Streamable HTTP mode** (port 8051): `docker compose up archon-mcp`
- **SSE mode**: `MCP_TRANSPORT=sse docker compose up archon-mcp`
- **stdio mode** (local): `python python/src/mcp_server/mcp_server.py stdio`

This allows testing both transports simultaneously.

### Extending the Server

To add new tools:
1. Create a new module in `python/src/mcp_server/features/`
2. Register tools using the `@mcp.tool()` decorator
3. Import and register in `mcp_server.py`

## Summary of Changes

### Files Modified
- `python/src/mcp_server/mcp_server.py` - Added stdio support, configurable transport
- `.mcp.json` - Created Claude Code configuration

### Files Added
- `python/src/mcp_server/mcp_server_stdio.py` - Standalone stdio version (optional)
- `MCP_CLAUDE_CODE_SETUP.md` - This documentation

### Key Improvements
- ✅ Claude Code compatibility via stdio transport
- ✅ Backward compatibility with existing SSE setup
- ✅ Proper logging separation for stdio mode
- ✅ Environment-based configuration
- ✅ Docker support included

## Support

If you encounter issues:
1. Check the logs in `/tmp/mcp_server.log`
2. Verify your environment variables are set correctly
3. Ensure all dependencies are installed
4. Try the manual test command above

For Claude Code specific issues, refer to:
- [Claude Code MCP Documentation](https://docs.claude.com/en/docs/claude-code/mcp)
- [MCP Specification](https://modelcontextprotocol.io/)
