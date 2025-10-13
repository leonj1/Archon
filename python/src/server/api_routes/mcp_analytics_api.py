"""
MCP Analytics API endpoints for Archon

Handles:
- Hourly analytics from aggregation tables
- Daily analytics from aggregation tables
- 24-hour summary from raw events
"""

import os
from datetime import UTC, datetime, timedelta

import aiosqlite
from fastapi import APIRouter, Header, HTTPException, Query, Response
from fastapi import status as http_status

from ..config.logfire_config import get_logger
from ..utils.etag_utils import check_etag, generate_etag

logger = get_logger(__name__)

router = APIRouter(prefix="/api/mcp/analytics", tags=["mcp-analytics"])

def get_db_path() -> str:
    """Get the SQLite database path from environment or default."""
    # Check for SQLITE_PATH or ARCHON_SQLITE_PATH environment variables
    db_path = os.getenv("SQLITE_PATH") or os.getenv("ARCHON_SQLITE_PATH") or "/data/archon.db"
    logger.debug(f"Using database path: {db_path}")
    return db_path


@router.get("/hourly")
async def get_hourly_analytics(
    response: Response,
    hours: int = Query(default=24, ge=1, le=168, description="Number of hours to retrieve (1-168)"),
    if_none_match: str | None = Header(None),
):
    """
    Get hourly MCP usage analytics from aggregation table.

    Args:
        hours: Number of hours to look back (1-168, default 24)

    Returns:
        Array of hourly analytics with tool usage counts
    """
    try:
        logger.debug(f"Getting hourly analytics | hours={hours} | etag={if_none_match}")

        # Calculate start time
        start_time = datetime.now(UTC) - timedelta(hours=hours)

        # Query SQLite database
        db_path = get_db_path()
        async with aiosqlite.connect(db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(
                """
                SELECT *
                FROM archon_mcp_usage_hourly
                WHERE hour_bucket >= ?
                ORDER BY hour_bucket DESC
                """,
                (start_time.isoformat(),)
            )
            rows = await cursor.fetchall()
            analytics_data = [dict(row) for row in rows]

        # Generate ETag from stable data
        etag_data = {
            "analytics": analytics_data,
            "count": len(analytics_data),
            "hours": hours,
        }
        current_etag = generate_etag(etag_data)

        # Check if client's ETag matches
        if check_etag(if_none_match, current_etag):
            response.status_code = http_status.HTTP_304_NOT_MODIFIED
            response.headers["ETag"] = current_etag
            response.headers["Cache-Control"] = "no-cache, must-revalidate"
            logger.debug(f"Hourly analytics unchanged, returning 304 | etag={current_etag}")
            return None

        # Set headers for successful response
        response.headers["ETag"] = current_etag
        response.headers["Last-Modified"] = datetime.now(UTC).isoformat()
        response.headers["Cache-Control"] = "no-cache, must-revalidate"

        logger.debug(
            f"Hourly analytics retrieved | count={len(analytics_data)} | hours={hours} | etag={current_etag}"
        )

        return {
            "success": True,
            "data": analytics_data,
            "count": len(analytics_data),
            "period": {
                "hours": hours,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now(UTC).isoformat(),
            },
        }

    except Exception as e:
        logger.error(f"Failed to get hourly analytics | error={str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Failed to retrieve hourly analytics: {str(e)}"},
        ) from None


@router.get("/daily")
async def get_daily_analytics(
    response: Response,
    days: int = Query(default=7, ge=1, le=180, description="Number of days to retrieve (1-180)"),
    if_none_match: str | None = Header(None),
):
    """
    Get daily MCP usage analytics from aggregation table.

    Args:
        days: Number of days to look back (1-180, default 7)

    Returns:
        Array of daily analytics with tool usage counts
    """
    try:
        logger.debug(f"Getting daily analytics | days={days} | etag={if_none_match}")

        # Calculate start date
        start_date = (datetime.now(UTC) - timedelta(days=days)).date()

        # Query SQLite database
        db_path = get_db_path()
        async with aiosqlite.connect(db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(
                """
                SELECT *
                FROM archon_mcp_usage_daily
                WHERE date_bucket >= ?
                ORDER BY date_bucket DESC
                """,
                (start_date.isoformat(),)
            )
            rows = await cursor.fetchall()
            analytics_data = [dict(row) for row in rows]

        # Generate ETag from stable data
        etag_data = {
            "analytics": analytics_data,
            "count": len(analytics_data),
            "days": days,
        }
        current_etag = generate_etag(etag_data)

        # Check if client's ETag matches
        if check_etag(if_none_match, current_etag):
            response.status_code = http_status.HTTP_304_NOT_MODIFIED
            response.headers["ETag"] = current_etag
            response.headers["Cache-Control"] = "no-cache, must-revalidate"
            logger.debug(f"Daily analytics unchanged, returning 304 | etag={current_etag}")
            return None

        # Set headers for successful response
        response.headers["ETag"] = current_etag
        response.headers["Last-Modified"] = datetime.now(UTC).isoformat()
        response.headers["Cache-Control"] = "no-cache, must-revalidate"

        logger.debug(
            f"Daily analytics retrieved | count={len(analytics_data)} | days={days} | etag={current_etag}"
        )

        return {
            "success": True,
            "data": analytics_data,
            "count": len(analytics_data),
            "period": {
                "days": days,
                "start_date": start_date.isoformat(),
                "end_date": datetime.now(UTC).date().isoformat(),
            },
        }

    except Exception as e:
        logger.error(f"Failed to get daily analytics | error={str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Failed to retrieve daily analytics: {str(e)}"},
        ) from None


@router.get("/summary")
async def get_24h_summary(
    response: Response,
    if_none_match: str | None = Header(None),
):
    """
    Get 24-hour summary from raw MCP usage events.

    Returns:
        Summary statistics for the last 24 hours including:
        - Total events
        - Unique tools used
        - Success/error counts
        - Tool usage breakdown
    """
    try:
        logger.debug(f"Getting 24h summary | etag={if_none_match}")

        # Calculate 24 hours ago
        start_time = datetime.now(UTC) - timedelta(hours=24)

        # Query SQLite database
        db_path = get_db_path()
        async with aiosqlite.connect(db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(
                """
                SELECT *
                FROM archon_mcp_usage_events
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                """,
                (start_time.isoformat(),)
            )
            rows = await cursor.fetchall()
            events = [dict(row) for row in rows]

        # Calculate summary statistics
        total_events = len(events)
        unique_tools = len({event.get("tool_name") for event in events if event.get("tool_name")})
        success_count = sum(1 for event in events if event.get("success") == 1)
        error_count = sum(1 for event in events if event.get("success") == 0)

        # Tool usage breakdown
        tool_usage = {}
        for event in events:
            tool_name = event.get("tool_name")
            if tool_name:
                if tool_name not in tool_usage:
                    tool_usage[tool_name] = {"count": 0, "success": 0, "error": 0}
                tool_usage[tool_name]["count"] += 1
                if event.get("success") == 1:
                    tool_usage[tool_name]["success"] += 1
                elif event.get("success") == 0:
                    tool_usage[tool_name]["error"] += 1

        # Sort tools by usage count
        sorted_tools = sorted(
            [{"tool_name": k, **v} for k, v in tool_usage.items()],
            key=lambda x: x["count"],
            reverse=True,
        )

        summary_data = {
            "total_events": total_events,
            "unique_tools": unique_tools,
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": round(success_count / total_events * 100, 2) if total_events > 0 else 0,
            "tool_usage": sorted_tools,
        }

        # Generate ETag from stable data
        etag_data = {
            "summary": summary_data,
            "period_start": start_time.isoformat(),
        }
        current_etag = generate_etag(etag_data)

        # Check if client's ETag matches
        if check_etag(if_none_match, current_etag):
            response.status_code = http_status.HTTP_304_NOT_MODIFIED
            response.headers["ETag"] = current_etag
            response.headers["Cache-Control"] = "no-cache, must-revalidate"
            logger.debug(f"24h summary unchanged, returning 304 | etag={current_etag}")
            return None

        # Set headers for successful response
        response.headers["ETag"] = current_etag
        response.headers["Last-Modified"] = datetime.now(UTC).isoformat()
        response.headers["Cache-Control"] = "no-cache, must-revalidate"

        logger.debug(
            f"24h summary retrieved | total_events={total_events} | unique_tools={unique_tools} | etag={current_etag}"
        )

        return {
            "success": True,
            "summary": summary_data,
            "period": {
                "hours": 24,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now(UTC).isoformat(),
            },
        }

    except Exception as e:
        logger.error(f"Failed to get 24h summary | error={str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Failed to retrieve 24h summary: {str(e)}"},
        ) from None


@router.get("/knowledge-bases")
async def get_knowledge_base_analytics(
    response: Response,
    hours: int = Query(default=24, ge=1, le=168, description="Number of hours to look back (1-168)"),
    if_none_match: str | None = Header(None),
):
    """
    Get knowledge base usage statistics by joining MCP events with sources.

    Returns top 10 knowledge bases by query count, including:
    - source_id, source_name
    - query_count, unique_queries
    - avg_response_time_ms, success_rate
    - percentage_of_total

    Args:
        hours: Number of hours to look back (1-168, default 24)

    Returns:
        JSON with knowledge base analytics for the specified time period
    """
    try:
        logger.debug(f"Getting knowledge base analytics | hours={hours} | etag={if_none_match}")

        # Calculate start time
        start_time = datetime.now(UTC) - timedelta(hours=hours)

        # Query SQLite database
        db_path = get_db_path()
        async with aiosqlite.connect(db_path) as conn:
            conn.row_factory = aiosqlite.Row

            # Get knowledge base statistics
            cursor = await conn.execute(
                """
                SELECT
                    e.source_id,
                    COALESCE(s.source_display_name, s.title, s.source_url, e.source_id) as source_name,
                    COUNT(*) as query_count,
                    COUNT(DISTINCT e.query_text) as unique_queries,
                    CAST(AVG(e.response_time_ms) AS INTEGER) as avg_response_time_ms,
                    ROUND(AVG(CASE WHEN e.success = 1 THEN 100.0 ELSE 0.0 END), 1) as success_rate
                FROM archon_mcp_usage_events e
                LEFT JOIN archon_sources s ON e.source_id = s.source_id
                WHERE e.timestamp >= ?
                  AND e.source_id IS NOT NULL
                GROUP BY e.source_id, source_name
                ORDER BY query_count DESC
                LIMIT 10
                """,
                (start_time.isoformat(),),
            )
            rows = await cursor.fetchall()
            kb_data = [dict(row) for row in rows]

            # Calculate total queries for percentage
            total_queries = sum(item["query_count"] for item in kb_data)

            # Add percentage_of_total to each item
            for item in kb_data:
                item["percentage_of_total"] = (
                    round((item["query_count"] / total_queries) * 100, 1) if total_queries > 0 else 0.0
                )

        # Handle empty state
        if not kb_data:
            logger.debug("No knowledge base queries found in time range")
            response_data = {
                "success": True,
                "data": [],
                "total_queries": 0,
                "period": {
                    "hours": hours,
                    "start_time": start_time.isoformat(),
                    "end_time": datetime.now(UTC).isoformat(),
                },
            }

            # Generate ETag for empty state
            current_etag = generate_etag(response_data)

            # Check if client's ETag matches
            if check_etag(if_none_match, current_etag):
                response.status_code = http_status.HTTP_304_NOT_MODIFIED
                response.headers["ETag"] = current_etag
                response.headers["Cache-Control"] = "no-cache, must-revalidate"
                logger.debug(f"Knowledge base analytics unchanged (empty), returning 304 | etag={current_etag}")
                return None

            # Set headers for empty state
            response.headers["ETag"] = current_etag
            response.headers["Last-Modified"] = datetime.now(UTC).isoformat()
            response.headers["Cache-Control"] = "no-cache, must-revalidate"

            return response_data

        # Generate ETag from stable data
        etag_data = {
            "kb_analytics": kb_data,
            "total_queries": total_queries,
            "hours": hours,
        }
        current_etag = generate_etag(etag_data)

        # Check if client's ETag matches
        if check_etag(if_none_match, current_etag):
            response.status_code = http_status.HTTP_304_NOT_MODIFIED
            response.headers["ETag"] = current_etag
            response.headers["Cache-Control"] = "no-cache, must-revalidate"
            logger.debug(f"Knowledge base analytics unchanged, returning 304 | etag={current_etag}")
            return None

        # Set headers for successful response
        response.headers["ETag"] = current_etag
        response.headers["Last-Modified"] = datetime.now(UTC).isoformat()
        response.headers["Cache-Control"] = "no-cache, must-revalidate"

        logger.debug(
            f"Knowledge base analytics retrieved | count={len(kb_data)} | total_queries={total_queries} | hours={hours} | etag={current_etag}"
        )

        return {
            "success": True,
            "data": kb_data,
            "total_queries": total_queries,
            "period": {
                "hours": hours,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now(UTC).isoformat(),
            },
        }

    except Exception as e:
        logger.error(f"Failed to get knowledge base analytics | error={str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Failed to retrieve knowledge base analytics: {str(e)}"},
        ) from None


@router.post("/refresh-views")
async def refresh_aggregation_tables():
    """
    Refresh aggregation tables (no-op for SQLite with automatic triggers).

    SQLite version uses triggers to automatically update hourly and daily
    aggregation tables, so manual refresh is not needed. This endpoint
    exists for API compatibility.

    Returns:
        Success status
    """
    return {
        "success": True,
        "message": "Aggregation tables are automatically updated via triggers (no manual refresh needed)",
        "refreshed_at": datetime.now(UTC).isoformat(),
    }
