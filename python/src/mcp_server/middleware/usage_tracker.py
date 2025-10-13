"""
MCP Usage Tracking Middleware

Captures all MCP tool invocations and stores usage metrics in SQLite time-series database.
This middleware provides automatic tracking with minimal overhead (< 10ms per request).

Usage:
    from src.mcp_server.middleware import usage_tracker

    @usage_tracker.track_tool('rag_search_knowledge_base', 'rag')
    async def rag_search_knowledge_base(ctx: Context, query: str, ...):
        # Your tool implementation
        ...
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Optional

import aiosqlite

from src.server.config.logfire_config import get_logger, safe_span

logger = get_logger(__name__)


class MCPUsageTracker:
    """
    Tracks MCP tool usage and stores metrics in SQLite time-series database.

    This class provides automatic usage tracking through a decorator pattern,
    recording tool invocations, response times, and metadata without blocking
    tool execution.
    """

    def __init__(self):
        """Initialize the usage tracker with SQLite database path."""
        self.db_path = os.getenv("SQLITE_PATH") or os.getenv("ARCHON_SQLITE_PATH") or "/data/archon.db"
        self._session_id: Optional[str] = None
        self._client_type: str = "unknown"
        self._enabled: bool = True  # Can be disabled for testing
        logger.debug(f"Initialized MCPUsageTracker with database: {self.db_path}")

    def set_session_context(self, session_id: str, client_type: str = "unknown"):
        """
        Set session context for usage tracking.

        Args:
            session_id: Unique session identifier
            client_type: Type of client (claude-code, cursor, windsurf, unknown)
        """
        self._session_id = session_id
        self._client_type = client_type
        logger.debug(f"Set MCP session context: {session_id} ({client_type})")

    def enable(self):
        """Enable usage tracking."""
        self._enabled = True
        logger.info("MCP usage tracking enabled")

    def disable(self):
        """Disable usage tracking (useful for testing)."""
        self._enabled = False
        logger.info("MCP usage tracking disabled")

    async def track_tool_usage(
        self,
        tool_name: str,
        tool_category: str,
        request_data: dict[str, Any],
        response_data: Optional[Any] = None,
        response_time_ms: int = 0,
        success: bool = True,
        error_type: Optional[str] = None,
    ):
        """
        Record a tool usage event in the SQLite database.

        This method is fire-and-forget to avoid blocking tool execution.
        Any errors during tracking are logged but don't affect the tool.

        Args:
            tool_name: Name of the MCP tool (e.g., 'rag_search_knowledge_base')
            tool_category: Category (rag, project, task, document, health, version, feature)
            request_data: Request parameters dictionary
            response_data: Response data (optional, not stored in DB)
            response_time_ms: Time taken in milliseconds
            success: Whether the operation succeeded
            error_type: Error type if failed
        """
        if not self._enabled:
            return

        try:
            # Extract relevant metadata from request
            source_id = request_data.get("source_id") or request_data.get("source")
            query_text = request_data.get("query", "")

            # Truncate query text to 500 characters
            if query_text and len(query_text) > 500:
                query_text = query_text[:500]

            match_count = request_data.get("match_count")

            # Insert into SQLite database
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute(
                    """
                    INSERT INTO archon_mcp_usage_events (
                        id, tool_name, tool_category, session_id, client_type,
                        request_metadata, source_id, query_text, match_count,
                        response_time_ms, success, error_type
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid.uuid4()),
                        tool_name,
                        tool_category,
                        self._session_id,
                        self._client_type,
                        json.dumps(request_data),
                        source_id,
                        query_text if query_text else None,
                        match_count,
                        response_time_ms,
                        1 if success else 0,  # SQLite uses INTEGER for boolean
                        error_type,
                    ),
                )
                await conn.commit()

            logger.debug(
                f"Tracked MCP tool usage: {tool_name} "
                f"({response_time_ms}ms, {'success' if success else 'failed'})"
            )

        except Exception as e:
            # Never fail tool execution due to tracking errors
            # Just log the error and continue
            logger.error(f"Failed to track MCP usage: {e}", exc_info=True)

    def track_tool(self, tool_name: str, tool_category: str):
        """
        Decorator to automatically track tool usage.

        This decorator wraps MCP tool functions to automatically record:
        - Tool invocations
        - Response times
        - Success/failure status
        - Request parameters

        Usage:
            @usage_tracker.track_tool('rag_search_knowledge_base', 'rag')
            async def rag_search_knowledge_base(ctx: Context, query: str, ...):
                # Your tool implementation
                ...

        Args:
            tool_name: Name of the tool (should match function name)
            tool_category: Category for grouping (rag, project, task, etc.)

        Returns:
            Decorated function that tracks usage
        """

        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                error_type = None
                response_data = None

                try:
                    # Execute the tool
                    with safe_span(
                        f"mcp_tool_{tool_name}",
                        tool_name=tool_name,
                        tool_category=tool_category,
                    ):
                        result = await func(*args, **kwargs)
                        response_data = result
                        return result

                except Exception as e:
                    success = False
                    error_type = type(e).__name__
                    raise  # Re-raise to preserve original error handling

                finally:
                    # Calculate response time
                    response_time_ms = int((time.time() - start_time) * 1000)

                    # Extract request data from kwargs (skip internal parameters)
                    request_data = {k: v for k, v in kwargs.items() if not k.startswith("_") and k != "ctx"}

                    # Track usage asynchronously (non-blocking)
                    try:
                        await self.track_tool_usage(
                            tool_name=tool_name,
                            tool_category=tool_category,
                            request_data=request_data,
                            response_data=response_data,
                            response_time_ms=response_time_ms,
                            success=success,
                            error_type=error_type,
                        )
                    except Exception as tracking_error:
                        # Tracking should never break tool execution
                        logger.error(f"Usage tracking failed: {tracking_error}")

            return wrapper

        return decorator


# Global tracker instance
# This is the primary interface for usage tracking across the MCP server
usage_tracker = MCPUsageTracker()
