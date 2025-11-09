# Memory Management Feature

## Overview

The Memory Management feature provides MCP tools for storing and retrieving contextual knowledge, patterns, and learnings across AI sessions. This complements the existing RAG search by providing a dedicated memory layer for session-specific insights.

## Architecture

### Database Layer (SQLite)
- **Table**: `archon_mcp_memories` - Stores memory records
- **Table**: `archon_mcp_memory_stats` - Tracks access statistics
- **Migration**: `migration/sqlite/003_memory_store.sql`

### Backend Services
- **Service**: `python/src/server/services/memory_service.py`
- **API Routes**: `python/src/server/api_routes/memory_api.py`
- **Endpoints**:
  - `POST /api/memory/store` - Store or update memory
  - `GET /api/memory/retrieve/{key}` - Retrieve by exact key
  - `POST /api/memory/search` - Search memories
  - `GET /api/memory/list` - List all memories
  - `DELETE /api/memory/{id}` - Delete memory

### MCP Tools
- **Location**: `python/src/mcp_server/features/memory/memory_tools.py`
- **Tools**:
  - `store_memory` - Store knowledge for future recall
  - `retrieve_memory` - Retrieve by key or search

## Usage Examples

### Store Memory
```python
# From MCP client (Claude Code, Cursor, etc.)
store_memory(
    key="fastapi_jwt_middleware",
    content="Use @app.middleware decorator with request.state for JWT validation. Store decoded token in request.state.user for access in route handlers.",
    type="pattern",
    tags=["authentication", "fastapi", "jwt", "middleware"]
)
```

### Retrieve by Key
```python
retrieve_memory(key="fastapi_jwt_middleware")
```

### Search Memories
```python
# Search by query
retrieve_memory(
    query="authentication",
    type="pattern",
    tags=["jwt"],
    match_count=3
)
```

## Memory Types

- `pattern` - Code patterns and best practices
- `solution` - Bug fixes and problem solutions
- `api` - API discoveries and usage patterns
- `architecture` - Architectural decisions
- `learning` - General learnings (default)

## Data Retention

- **Global memories**: 90 days
- **Session-scoped memories**: 30 days
- Automatic cleanup via SQLite triggers

## Testing

Tests are located in:
- `python/tests/server/services/test_memory_service.py`

Run tests:
```bash
cd python
uv run pytest tests/server/services/test_memory_service.py -v
```

## Integration

The memory tools are automatically registered with the MCP server and available to all connected AI IDEs:
- Claude Code
- Cursor
- Windsurf
- Any MCP-compatible client

## Usage Tracking

All memory operations are tracked via the usage tracking middleware and visible in the MCP Usage Analytics dashboard.
