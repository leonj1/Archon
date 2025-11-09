"""Unit tests for memory management tools."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import Context

from src.mcp_server.features.memory.memory_tools import register_memory_tools


@pytest.fixture
def mock_mcp():
    """Create a mock MCP server for testing."""
    mock = MagicMock()
    # Store registered tools
    mock._tools = {}

    def tool_decorator():
        def decorator(func):
            mock._tools[func.__name__] = func
            return func

        return decorator

    mock.tool = tool_decorator
    return mock


@pytest.fixture
def mock_context():
    """Create a mock context for testing."""
    return MagicMock(spec=Context)


# ========================================================================
# FIND_MEMORY TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_find_memory_by_exact_key_success(mock_mcp, mock_context):
    """Test finding memory by exact key match."""
    register_memory_tools(mock_mcp)

    find_memory = mock_mcp._tools.get("find_memory")
    assert find_memory is not None, "find_memory tool not registered"

    # Mock HTTP response for exact key retrieval
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "memory": {
            "id": "mem-123",
            "memory_key": "auth_pattern_jwt",
            "memory_content": "Use JWT tokens for authentication",
            "memory_type": "pattern",
            "tags": ["auth", "security"],
            "metadata": {"source": "documentation"},
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }
    }

    with patch("src.mcp_server.features.memory.memory_tools.httpx.AsyncClient") as mock_client:
        mock_async_client = AsyncMock()
        mock_async_client.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_async_client

        result = await find_memory(mock_context, key="auth_pattern_jwt")

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["memory"]["memory_key"] == "auth_pattern_jwt"
        assert result_data["memory"]["memory_type"] == "pattern"
        assert "auth" in result_data["memory"]["tags"]


@pytest.mark.asyncio
async def test_find_memory_by_search_query(mock_mcp, mock_context):
    """Test searching memories by query."""
    register_memory_tools(mock_mcp)

    find_memory = mock_mcp._tools.get("find_memory")

    # Mock HTTP response for search
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "memories": [
            {
                "id": "mem-1",
                "memory_key": "cors_fix",
                "memory_content": "Enable CORS headers",
                "memory_type": "solution",
            },
            {
                "id": "mem-2",
                "memory_key": "cors_config",
                "memory_content": "CORS configuration",
                "memory_type": "pattern",
            },
        ],
        "count": 2,
    }

    with patch("src.mcp_server.features.memory.memory_tools.httpx.AsyncClient") as mock_client:
        mock_async_client = AsyncMock()
        mock_async_client.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_async_client

        result = await find_memory(mock_context, query="cors")

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["count"] == 2
        assert len(result_data["memories"]) == 2


@pytest.mark.asyncio
async def test_find_memory_by_tags(mock_mcp, mock_context):
    """Test searching memories by tags."""
    register_memory_tools(mock_mcp)

    find_memory = mock_mcp._tools.get("find_memory")

    # Mock HTTP response for tag search
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "memories": [
            {
                "id": "mem-1",
                "memory_key": "auth_jwt",
                "memory_content": "JWT authentication",
                "tags": ["auth", "security"],
            }
        ],
        "count": 1,
    }

    with patch("src.mcp_server.features.memory.memory_tools.httpx.AsyncClient") as mock_client:
        mock_async_client = AsyncMock()
        mock_async_client.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_async_client

        result = await find_memory(mock_context, tags=["auth", "security"])

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["count"] == 1
        assert "auth" in result_data["memories"][0]["tags"]


@pytest.mark.asyncio
async def test_find_memory_not_found(mock_mcp, mock_context):
    """Test finding non-existent memory."""
    register_memory_tools(mock_mcp)

    find_memory = mock_mcp._tools.get("find_memory")

    # Mock 404 response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Memory not found"

    with patch("src.mcp_server.features.memory.memory_tools.httpx.AsyncClient") as mock_client:
        mock_async_client = AsyncMock()
        mock_async_client.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_async_client

        result = await find_memory(mock_context, key="nonexistent_key")

        result_data = json.loads(result)
        assert result_data["success"] is False
        assert "error" in result_data
        assert isinstance(result_data["error"], dict)
        assert result_data["error"]["type"] == "not_found"


# ========================================================================
# MANAGE_MEMORY TESTS - STORE ACTION
# ========================================================================


@pytest.mark.asyncio
async def test_manage_memory_store_success(mock_mcp, mock_context):
    """Test storing a new memory."""
    register_memory_tools(mock_mcp)

    manage_memory = mock_mcp._tools.get("manage_memory")
    assert manage_memory is not None, "manage_memory tool not registered"

    # Mock HTTP response for store
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "memory_id": "mem-456",
        "memory_key": "new_pattern",
        "action": "created",
        "message": "Memory created successfully",
    }

    with patch("src.mcp_server.features.memory.memory_tools.httpx.AsyncClient") as mock_client:
        mock_async_client = AsyncMock()
        mock_async_client.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_async_client

        result = await manage_memory(
            mock_context,
            action="store",
            key="new_pattern",
            content="This is a new pattern",
            type="pattern",
            tags=["test", "pattern"],
        )

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["memory_id"] == "mem-456"
        assert result_data["action"] == "created"


@pytest.mark.asyncio
async def test_manage_memory_store_update_existing(mock_mcp, mock_context):
    """Test updating an existing memory."""
    register_memory_tools(mock_mcp)

    manage_memory = mock_mcp._tools.get("manage_memory")

    # Mock HTTP response for update
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "memory_id": "mem-789",
        "memory_key": "existing_pattern",
        "action": "updated",
        "message": "Memory updated successfully",
    }

    with patch("src.mcp_server.features.memory.memory_tools.httpx.AsyncClient") as mock_client:
        mock_async_client = AsyncMock()
        mock_async_client.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_async_client

        result = await manage_memory(
            mock_context,
            action="store",
            key="existing_pattern",
            content="Updated content",
        )

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["action"] == "updated"


@pytest.mark.asyncio
async def test_manage_memory_store_with_metadata(mock_mcp, mock_context):
    """Test storing memory with metadata."""
    register_memory_tools(mock_mcp)

    manage_memory = mock_mcp._tools.get("manage_memory")

    # Mock HTTP response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "memory_id": "mem-meta",
        "memory_key": "meta_test",
        "action": "created",
        "message": "Memory created successfully",
    }

    with patch("src.mcp_server.features.memory.memory_tools.httpx.AsyncClient") as mock_client:
        mock_async_client = AsyncMock()
        mock_async_client.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_async_client

        metadata = {"source": "documentation", "priority": "high"}
        result = await manage_memory(
            mock_context,
            action="store",
            key="meta_test",
            content="Test with metadata",
            metadata=metadata,
        )

        result_data = json.loads(result)
        assert result_data["success"] is True


@pytest.mark.asyncio
async def test_manage_memory_store_invalid_type(mock_mcp, mock_context):
    """Test storing memory with invalid type."""
    register_memory_tools(mock_mcp)

    manage_memory = mock_mcp._tools.get("manage_memory")

    # Mock 400 response for validation error
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "memory_type must be one of {'pattern', 'solution', 'api', 'architecture', 'learning'}"

    with patch("src.mcp_server.features.memory.memory_tools.httpx.AsyncClient") as mock_client:
        mock_async_client = AsyncMock()
        mock_async_client.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_async_client

        result = await manage_memory(
            mock_context,
            action="store",
            key="invalid_test",
            content="Test content",
            type="invalid_type",
        )

        result_data = json.loads(result)
        assert result_data["success"] is False
        assert "error" in result_data


# ========================================================================
# MANAGE_MEMORY TESTS - DELETE ACTION
# ========================================================================


@pytest.mark.asyncio
async def test_manage_memory_delete_success(mock_mcp, mock_context):
    """Test deleting a memory."""
    register_memory_tools(mock_mcp)

    manage_memory = mock_mcp._tools.get("manage_memory")

    # Mock HTTP response for delete
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "message": "Memory deleted successfully",
    }

    with patch("src.mcp_server.features.memory.memory_tools.httpx.AsyncClient") as mock_client:
        mock_async_client = AsyncMock()
        mock_async_client.delete.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_async_client

        result = await manage_memory(
            mock_context,
            action="delete",
            memory_id="mem-to-delete",
        )

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert "deleted successfully" in result_data["message"]


@pytest.mark.asyncio
async def test_manage_memory_delete_not_found(mock_mcp, mock_context):
    """Test deleting non-existent memory."""
    register_memory_tools(mock_mcp)

    manage_memory = mock_mcp._tools.get("manage_memory")

    # Mock 404 response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Memory not found"

    with patch("src.mcp_server.features.memory.memory_tools.httpx.AsyncClient") as mock_client:
        mock_async_client = AsyncMock()
        mock_async_client.delete.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_async_client

        result = await manage_memory(
            mock_context,
            action="delete",
            memory_id="nonexistent-id",
        )

        result_data = json.loads(result)
        assert result_data["success"] is False
        assert "error" in result_data
        assert isinstance(result_data["error"], dict)


@pytest.mark.asyncio
async def test_manage_memory_invalid_action(mock_mcp, mock_context):
    """Test manage_memory with invalid action."""
    register_memory_tools(mock_mcp)

    manage_memory = mock_mcp._tools.get("manage_memory")

    # Mock 400 response
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Invalid action"

    with patch("src.mcp_server.features.memory.memory_tools.httpx.AsyncClient") as mock_client:
        mock_async_client = AsyncMock()
        mock_async_client.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_async_client

        result = await manage_memory(
            mock_context,
            action="invalid_action",
            key="test_key",
            content="test",
        )

        result_data = json.loads(result)
        assert result_data["success"] is False
        assert "error" in result_data


# ========================================================================
# EDGE CASES AND ERROR HANDLING
# ========================================================================


@pytest.mark.asyncio
async def test_find_memory_session_scoped(mock_mcp, mock_context):
    """Test finding memories scoped to a specific session."""
    register_memory_tools(mock_mcp)

    find_memory = mock_mcp._tools.get("find_memory")

    # Mock HTTP response for session-scoped search
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "memories": [
            {
                "id": "mem-session",
                "memory_key": "session_memory",
                "memory_content": "Session-specific data",
                "session_id": "session-123",
            }
        ],
        "count": 1,
    }

    with patch("src.mcp_server.features.memory.memory_tools.httpx.AsyncClient") as mock_client:
        mock_async_client = AsyncMock()
        mock_async_client.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_async_client

        result = await find_memory(
            mock_context,
            query="session",
            session_id="session-123",
        )

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["memories"][0]["session_id"] == "session-123"


@pytest.mark.asyncio
async def test_find_memory_with_match_count(mock_mcp, mock_context):
    """Test finding memories with custom match_count limit."""
    register_memory_tools(mock_mcp)

    find_memory = mock_mcp._tools.get("find_memory")

    # Mock HTTP response with limited results
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "memories": [
            {"id": "mem-1", "memory_key": "key1", "memory_content": "Content 1"},
            {"id": "mem-2", "memory_key": "key2", "memory_content": "Content 2"},
        ],
        "count": 2,
    }

    with patch("src.mcp_server.features.memory.memory_tools.httpx.AsyncClient") as mock_client:
        mock_async_client = AsyncMock()
        mock_async_client.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_async_client

        result = await find_memory(
            mock_context,
            query="test",
            match_count=2,
        )

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert len(result_data["memories"]) <= 2
