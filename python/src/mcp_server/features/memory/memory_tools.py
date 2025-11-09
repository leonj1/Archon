"""
Memory Management Tools for Archon MCP Server

This module provides tools for storing and retrieving AI memories across sessions.
Memories are contextual knowledge, patterns, and learnings that can be persisted.
"""

import json
import logging
from urllib.parse import urljoin

import httpx
from mcp.server.fastmcp import Context, FastMCP

from src.mcp_server.middleware import usage_tracker
from src.mcp_server.utils.error_handling import MCPErrorFormatter
from src.mcp_server.utils.timeout_config import get_default_timeout
from src.server.config.service_discovery import get_api_url

logger = logging.getLogger(__name__)


def register_memory_tools(mcp: FastMCP):
    """Register memory management tools with the MCP server."""

    @mcp.tool()
    @usage_tracker.track_tool('store_memory', 'memory')
    async def store_memory(
        ctx: Context,
        key: str,
        content: str,
        type: str = "learning",
        tags: list[str] | None = None,
        session_id: str | None = None,
        metadata: dict | None = None,
    ) -> str:
        """
        Store knowledge, patterns, or learnings in memory for future recall.

        Use this to persist important discoveries, patterns, solutions, or architectural
        decisions that should be remembered across sessions.

        Args:
            key: Unique identifier for the memory (e.g., "auth_jwt_pattern", "cors_fix_solution")
            content: The actual knowledge/pattern to store (be detailed and specific)
            type: Category - "pattern" | "solution" | "api" | "architecture" | "learning" (default: "learning")
            tags: List of tags for filtering (e.g., ["authentication", "jwt", "middleware"])
            session_id: Optional session ID to scope memory to current session
            metadata: Additional context as key-value pairs

        Returns:
            JSON string with structure:
            - success: bool - Operation success status
            - memory_id: str - UUID of stored memory
            - memory_key: str - The key used
            - action: str - "created" or "updated"
            - message: str - Success/error message

        Examples:
            store_memory(
                key="fastapi_jwt_middleware",
                content="Use @app.middleware decorator with request.state for JWT validation...",
                type="pattern",
                tags=["authentication", "fastapi", "jwt"]
            )

            store_memory(
                key="cors_error_fix",
                content="CORS issues resolved by adding credentials=true to middleware config",
                type="solution",
                tags=["cors", "debugging"]
            )
        """
        try:
            api_url = get_api_url()
            timeout = get_default_timeout()

            async with httpx.AsyncClient(timeout=timeout) as client:
                request_data = {
                    "memory_key": key,
                    "memory_content": content,
                    "memory_type": type,
                    "tags": tags,
                    "session_id": session_id,
                    "metadata": metadata,
                }

                response = await client.post(
                    urljoin(api_url, "/api/memory/store"),
                    json=request_data
                )

                if response.status_code == 200:
                    result = response.json()
                    return json.dumps({
                        "success": True,
                        "memory_id": result.get("memory_id"),
                        "memory_key": result.get("memory_key"),
                        "action": result.get("action"),
                        "message": result.get("message"),
                    }, indent=2)
                else:
                    return MCPErrorFormatter.from_http_error(response, "store memory")

        except httpx.RequestError as e:
            return MCPErrorFormatter.from_exception(e, "store memory")
        except Exception as e:
            logger.error(f"Error storing memory: {e}", exc_info=True)
            return MCPErrorFormatter.from_exception(e, "store memory")

    @mcp.tool()
    @usage_tracker.track_tool('retrieve_memory', 'memory')
    async def retrieve_memory(
        ctx: Context,
        key: str | None = None,
        query: str | None = None,
        type: str | None = None,
        tags: list[str] | None = None,
        session_id: str | None = None,
        match_count: int = 5,
    ) -> str:
        """
        Retrieve stored memories by exact key or search.

        Use this to recall previously stored knowledge, patterns, or solutions.
        Provide either a key for exact match, or query/filters for search.

        Args:
            key: Exact memory key to retrieve (e.g., "auth_jwt_pattern")
            query: Text query for search (e.g., "authentication patterns")
            type: Filter by type - "pattern" | "solution" | "api" | "architecture" | "learning"
            tags: Filter by tags (e.g., ["jwt", "authentication"])
            session_id: Filter by session ID
            match_count: Maximum results for search (default: 5)

        Returns:
            JSON string with structure:
            - success: bool - Operation success status
            - memory: dict - Single memory object (if using key)
            - memories: list[dict] - Array of memories (if using search)
            - count: int - Number of results (for search)
            - error: str|null - Error description if failed

        Examples:
            # Exact retrieval
            retrieve_memory(key="fastapi_jwt_middleware")

            # Search by query
            retrieve_memory(query="authentication", type="pattern", match_count=3)

            # Filter by tags
            retrieve_memory(tags=["cors", "debugging"], match_count=5)
        """
        try:
            api_url = get_api_url()
            timeout = get_default_timeout()

            async with httpx.AsyncClient(timeout=timeout) as client:
                # Exact key retrieval
                if key:
                    response = await client.get(
                        urljoin(api_url, f"/api/memory/retrieve/{key}")
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "memory": result.get("memory"),
                            "error": None,
                        }, indent=2)
                    elif response.status_code == 404:
                        return MCPErrorFormatter.format_error(
                            error_type="not_found",
                            message=f"Memory not found: {key}",
                            suggestion="Check the memory key spelling or use search to find similar memories",
                            http_status=404,
                        )
                    else:
                        return MCPErrorFormatter.from_http_error(response, "retrieve memory")

                # Search mode
                else:
                    request_data = {
                        "query": query,
                        "memory_type": type,
                        "tags": tags,
                        "session_id": session_id,
                        "match_count": match_count,
                    }

                    response = await client.post(
                        urljoin(api_url, "/api/memory/search"),
                        json=request_data
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "memories": result.get("memories", []),
                            "count": result.get("count", 0),
                            "query": result.get("query"),
                            "filters": result.get("filters", {}),
                            "error": None,
                        }, indent=2)
                    else:
                        return MCPErrorFormatter.from_http_error(response, "search memories")

        except httpx.RequestError as e:
            return MCPErrorFormatter.from_exception(e, "retrieve memory")
        except Exception as e:
            logger.error(f"Error retrieving memory: {e}", exc_info=True)
            return MCPErrorFormatter.from_exception(e, "retrieve memory")

    # Log successful registration
    logger.info("✓ Memory tools registered (HTTP-based version)")
