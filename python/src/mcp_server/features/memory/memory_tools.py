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
    @usage_tracker.track_tool('find_memory', 'memory')
    async def find_memory(
        ctx: Context,
        key: str | None = None,
        query: str | None = None,
        type: str | None = None,
        tags: list[str] | None = None,
        session_id: str | None = None,
        match_count: int = 5,
    ) -> str:
        """
        Find and retrieve stored memories by exact key or search.

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
            find_memory(key="fastapi_jwt_middleware")

            # Search by query
            find_memory(query="authentication", type="pattern", match_count=3)

            # Filter by tags
            find_memory(tags=["cors", "debugging"], match_count=5)
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
            return MCPErrorFormatter.from_exception(e, "find memory")
        except Exception as e:
            logger.error(f"Error finding memory: {e}", exc_info=True)
            return MCPErrorFormatter.from_exception(e, "find memory")

    @mcp.tool()
    @usage_tracker.track_tool('manage_memory', 'memory')
    async def manage_memory(
        ctx: Context,
        action: str,
        key: str | None = None,
        content: str | None = None,
        type: str = "learning",
        tags: list[str] | None = None,
        session_id: str | None = None,
        metadata: dict | None = None,
        memory_id: str | None = None,
    ) -> str:
        """
        Manage memories with actions: store or delete.

        Args:
            action: "store" | "delete"
            key: Unique identifier for the memory (required for store)
            content: The actual knowledge/pattern to store (required for store)
            type: Category - "pattern" | "solution" | "api" | "architecture" | "learning"
            tags: List of tags for filtering (e.g., ["authentication", "jwt"])
            session_id: Optional session ID to scope memory
            metadata: Additional context as key-value pairs
            memory_id: UUID of memory to delete (required for delete)

        Returns:
            JSON string with structure:
            - success: bool - Operation success status
            - memory_id: str - UUID of stored/deleted memory
            - memory_key: str - The key used
            - action: str - "created", "updated", or "deleted"
            - message: str - Success/error message

        Examples:
            # Store a memory
            manage_memory(
                action="store",
                key="fastapi_jwt_middleware",
                content="Use @app.middleware decorator with request.state for JWT validation...",
                type="pattern",
                tags=["authentication", "fastapi", "jwt"]
            )

            # Delete a memory
            manage_memory(action="delete", memory_id="uuid-here")
        """
        try:
            api_url = get_api_url()
            timeout = get_default_timeout()

            async with httpx.AsyncClient(timeout=timeout) as client:
                if action == "store":
                    if not key:
                        return MCPErrorFormatter.format_error(
                            "validation_error",
                            "key required for store action"
                        )
                    if not content:
                        return MCPErrorFormatter.format_error(
                            "validation_error",
                            "content required for store action"
                        )

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

                elif action == "delete":
                    if not memory_id:
                        return MCPErrorFormatter.format_error(
                            "validation_error",
                            "memory_id required for delete action"
                        )

                    response = await client.delete(
                        urljoin(api_url, f"/api/memory/{memory_id}")
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "message": result.get("message"),
                            "memory_key": result.get("memory_key"),
                        }, indent=2)
                    else:
                        return MCPErrorFormatter.from_http_error(response, "delete memory")

                else:
                    return MCPErrorFormatter.format_error(
                        "invalid_action",
                        f"Unknown action: {action}"
                    )

        except httpx.RequestError as e:
            return MCPErrorFormatter.from_exception(e, f"{action} memory")
        except Exception as e:
            logger.error(f"Error managing memory ({action}): {e}", exc_info=True)
            return MCPErrorFormatter.from_exception(e, f"{action} memory")

    # Log successful registration
    logger.info("✓ Memory tools registered (HTTP-based version)")
