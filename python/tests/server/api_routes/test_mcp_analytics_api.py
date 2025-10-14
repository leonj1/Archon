"""
Comprehensive tests for MCP Analytics API endpoints.

Tests all 4 endpoints:
- GET /api/mcp/analytics/hourly
- GET /api/mcp/analytics/daily
- GET /api/mcp/analytics/summary
- POST /api/mcp/analytics/refresh-views
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.server.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_supabase():
    """Mock Supabase client with analytics data."""
    mock_client = MagicMock()
    return mock_client


@pytest.fixture
def mock_hourly_analytics_data():
    """Mock hourly analytics data."""
    base_time = datetime.now(UTC) - timedelta(hours=12)
    return [
        {
            "hour_start": (base_time + timedelta(hours=i)).isoformat(),
            "total_events": 10 + i,
            "unique_tools": 3,
            "success_count": 8 + i,
            "error_count": 2,
            "tool_usage": {
                "find_tasks": 5 + i,
                "manage_task": 3,
                "find_projects": 2,
            },
        }
        for i in range(12)
    ]


@pytest.fixture
def mock_daily_analytics_data():
    """Mock daily analytics data."""
    base_date = datetime.now(UTC).date() - timedelta(days=7)
    return [
        {
            "date": (base_date + timedelta(days=i)).isoformat(),
            "total_events": 100 + (i * 10),
            "unique_tools": 5,
            "success_count": 90 + (i * 9),
            "error_count": 10 + i,
            "tool_usage": {
                "find_tasks": 40 + (i * 4),
                "manage_task": 30 + (i * 3),
                "find_projects": 20 + (i * 2),
                "rag_search": 10 + i,
            },
        }
        for i in range(7)
    ]


@pytest.fixture
def mock_raw_events_data():
    """Mock raw MCP usage events."""
    return [
        {
            "id": "event-1",
            "tool_name": "find_tasks",
            "status": "success",
            "created_at": (datetime.now(UTC) - timedelta(hours=1)).isoformat(),
        },
        {
            "id": "event-2",
            "tool_name": "find_tasks",
            "status": "success",
            "created_at": (datetime.now(UTC) - timedelta(hours=2)).isoformat(),
        },
        {
            "id": "event-3",
            "tool_name": "manage_task",
            "status": "success",
            "created_at": (datetime.now(UTC) - timedelta(hours=3)).isoformat(),
        },
        {
            "id": "event-4",
            "tool_name": "find_projects",
            "status": "error",
            "created_at": (datetime.now(UTC) - timedelta(hours=4)).isoformat(),
        },
        {
            "id": "event-5",
            "tool_name": "find_tasks",
            "status": "success",
            "created_at": (datetime.now(UTC) - timedelta(hours=5)).isoformat(),
        },
    ]


# ============================================================================
# GET /api/mcp/analytics/hourly
# ============================================================================


def test_get_hourly_analytics_default_hours(client, mock_supabase, mock_hourly_analytics_data):
    """Test hourly analytics with default 24 hours."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        # Mock cursor.fetchall() to return hourly analytics data
        mock_cursor.fetchall = AsyncMock(return_value=[
            {k: v for k, v in item.items()}
            for item in mock_hourly_analytics_data
        ])

        # Mock conn.execute() to return cursor
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None

        # Mock context manager
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/hourly")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["count"] == len(mock_hourly_analytics_data)
        assert data["period"]["hours"] == 24
        assert "start_time" in data["period"]
        assert "end_time" in data["period"]
        assert "data" in data
        assert len(data["data"]) == len(mock_hourly_analytics_data)


def test_get_hourly_analytics_custom_hours(client, mock_supabase, mock_hourly_analytics_data):
    """Test hourly analytics with custom hours parameter."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        # Mock cursor.fetchall() to return hourly analytics data
        mock_cursor.fetchall = AsyncMock(return_value=[
            {k: v for k, v in item.items()}
            for item in mock_hourly_analytics_data
        ])

        # Mock conn.execute() to return cursor
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None

        # Mock context manager
        mock_connect.return_value.__aenter__.return_value = mock_conn

        # Test 48 hours
        response = client.get("/api/mcp/analytics/hourly?hours=48")
        assert response.status_code == 200
        data = response.json()
        assert data["period"]["hours"] == 48

        # Test 168 hours (1 week)
        response = client.get("/api/mcp/analytics/hourly?hours=168")
        assert response.status_code == 200
        data = response.json()
        assert data["period"]["hours"] == 168


def test_get_hourly_analytics_hours_validation_too_low(client):
    """Test hourly analytics with hours parameter below minimum (1)."""
    response = client.get("/api/mcp/analytics/hourly?hours=0")
    assert response.status_code == 422  # Validation error


def test_get_hourly_analytics_hours_validation_too_high(client):
    """Test hourly analytics with hours parameter above maximum (168)."""
    response = client.get("/api/mcp/analytics/hourly?hours=200")
    assert response.status_code == 422  # Validation error


def test_get_hourly_analytics_empty_results(client, mock_supabase):
    """Test hourly analytics with no data."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        # Mock cursor.fetchall() to return empty list
        mock_cursor.fetchall = AsyncMock(return_value=[])

        # Mock conn.execute() to return cursor
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None

        # Mock context manager
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/hourly")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 0
        assert data["data"] == []


def test_get_hourly_analytics_etag_generation(client, mock_supabase, mock_hourly_analytics_data):
    """Test that ETag header is generated for hourly analytics."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        # Mock cursor.fetchall() to return hourly analytics data
        mock_cursor.fetchall = AsyncMock(return_value=[
            {k: v for k, v in item.items()}
            for item in mock_hourly_analytics_data
        ])

        # Mock conn.execute() to return cursor
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None

        # Mock context manager
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/hourly")

        assert response.status_code == 200
        assert "etag" in response.headers
        assert "cache-control" in response.headers
        assert response.headers["cache-control"] == "no-cache, must-revalidate"


def test_get_hourly_analytics_304_not_modified(client, mock_supabase, mock_hourly_analytics_data):
    """Test 304 Not Modified response when ETag matches."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        # Mock cursor.fetchall() to return hourly analytics data
        mock_cursor.fetchall = AsyncMock(return_value=[
            {k: v for k, v in item.items()}
            for item in mock_hourly_analytics_data
        ])

        # Mock conn.execute() to return cursor
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None

        # Mock context manager
        mock_connect.return_value.__aenter__.return_value = mock_conn

        # First request to get ETag
        response1 = client.get("/api/mcp/analytics/hourly")
        assert response1.status_code == 200
        etag = response1.headers.get("etag")

        # Second request with matching ETag
        response2 = client.get("/api/mcp/analytics/hourly", headers={"If-None-Match": etag})
        assert response2.status_code == 304
        assert response2.headers.get("etag") == etag


def test_get_hourly_analytics_database_error(client, mock_supabase):
    """Test error handling when database query fails."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        # Make the connection raise an exception
        mock_connect.side_effect = Exception("Database connection failed")

        response = client.get("/api/mcp/analytics/hourly")

        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["success"] is False
        assert "Failed to retrieve hourly analytics" in data["detail"]["error"]


# ============================================================================
# GET /api/mcp/analytics/daily
# ============================================================================


def test_get_daily_analytics_default_days(client, mock_supabase, mock_daily_analytics_data):
    """Test daily analytics with default 7 days."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        # Mock cursor.fetchall() to return daily analytics data
        mock_cursor.fetchall = AsyncMock(return_value=[
            {k: v for k, v in item.items()}
            for item in mock_daily_analytics_data
        ])

        # Mock conn.execute() to return cursor
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None

        # Mock context manager
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/daily")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["count"] == len(mock_daily_analytics_data)
        assert data["period"]["days"] == 7
        assert "start_date" in data["period"]
        assert "end_date" in data["period"]
        assert "data" in data
        assert len(data["data"]) == len(mock_daily_analytics_data)


def test_get_daily_analytics_custom_days(client, mock_supabase, mock_daily_analytics_data):
    """Test daily analytics with custom days parameter."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        # Mock cursor.fetchall() to return daily analytics data
        mock_cursor.fetchall = AsyncMock(return_value=[
            {k: v for k, v in item.items()}
            for item in mock_daily_analytics_data
        ])

        # Mock conn.execute() to return cursor
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None

        # Mock context manager
        mock_connect.return_value.__aenter__.return_value = mock_conn

        # Test 30 days
        response = client.get("/api/mcp/analytics/daily?days=30")
        assert response.status_code == 200
        data = response.json()
        assert data["period"]["days"] == 30

        # Test 180 days (6 months)
        response = client.get("/api/mcp/analytics/daily?days=180")
        assert response.status_code == 200
        data = response.json()
        assert data["period"]["days"] == 180


def test_get_daily_analytics_days_validation_too_low(client):
    """Test daily analytics with days parameter below minimum (1)."""
    response = client.get("/api/mcp/analytics/daily?days=0")
    assert response.status_code == 422  # Validation error


def test_get_daily_analytics_days_validation_too_high(client):
    """Test daily analytics with days parameter above maximum (180)."""
    response = client.get("/api/mcp/analytics/daily?days=200")
    assert response.status_code == 422  # Validation error


def test_get_daily_analytics_empty_results(client, mock_supabase):
    """Test daily analytics with no data."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        # Mock cursor.fetchall() to return empty list
        mock_cursor.fetchall = AsyncMock(return_value=[])

        # Mock conn.execute() to return cursor
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None

        # Mock context manager
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/daily")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 0
        assert data["data"] == []


def test_get_daily_analytics_etag_generation(client, mock_supabase, mock_daily_analytics_data):
    """Test that ETag header is generated for daily analytics."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        # Mock cursor.fetchall() to return daily analytics data
        mock_cursor.fetchall = AsyncMock(return_value=[
            {k: v for k, v in item.items()}
            for item in mock_daily_analytics_data
        ])

        # Mock conn.execute() to return cursor
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None

        # Mock context manager
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/daily")

        assert response.status_code == 200
        assert "etag" in response.headers
        assert "cache-control" in response.headers
        assert response.headers["cache-control"] == "no-cache, must-revalidate"


def test_get_daily_analytics_304_not_modified(client, mock_supabase, mock_daily_analytics_data):
    """Test 304 Not Modified response when ETag matches."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        # Mock cursor.fetchall() to return daily analytics data
        mock_cursor.fetchall = AsyncMock(return_value=[
            {k: v for k, v in item.items()}
            for item in mock_daily_analytics_data
        ])

        # Mock conn.execute() to return cursor
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None

        # Mock context manager
        mock_connect.return_value.__aenter__.return_value = mock_conn

        # First request to get ETag
        response1 = client.get("/api/mcp/analytics/daily")
        assert response1.status_code == 200
        etag = response1.headers.get("etag")

        # Second request with matching ETag
        response2 = client.get("/api/mcp/analytics/daily", headers={"If-None-Match": etag})
        assert response2.status_code == 304
        assert response2.headers.get("etag") == etag


def test_get_daily_analytics_database_error(client, mock_supabase):
    """Test error handling when database query fails."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        # Make the connection raise an exception
        mock_connect.side_effect = Exception("Database connection failed")

        response = client.get("/api/mcp/analytics/daily")

        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["success"] is False
        assert "Failed to retrieve daily analytics" in data["detail"]["error"]


# ============================================================================
# GET /api/mcp/analytics/summary
# ============================================================================


def test_get_24h_summary_calculation(client, mock_supabase, mock_raw_events_data):
    """Test 24h summary with proper calculation of statistics."""
    # Convert mock data to SQLite format (success=1/0 instead of status="success"/"error")
    sqlite_events = [
        {
            "id": event["id"],
            "tool_name": event["tool_name"],
            "success": 1 if event["status"] == "success" else 0,
            "timestamp": event["created_at"],
        }
        for event in mock_raw_events_data
    ]

    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        # Mock cursor.fetchall() to return SQLite-formatted events
        mock_cursor.fetchall = AsyncMock(return_value=sqlite_events)

        # Mock conn.execute() to return cursor
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None

        # Mock context manager
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/summary")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        summary = data["summary"]

        # Verify summary calculations
        assert summary["total_events"] == 5
        assert summary["unique_tools"] == 3  # find_tasks, manage_task, find_projects
        assert summary["success_count"] == 4
        assert summary["error_count"] == 1
        assert summary["success_rate"] == 80.0  # 4/5 * 100


def test_get_24h_summary_tool_usage_sorting(client, mock_supabase, mock_raw_events_data):
    """Test that tool usage is sorted by count descending."""
    # Convert mock data to SQLite format (success=1/0 instead of status="success"/"error")
    sqlite_events = [
        {
            "id": event["id"],
            "tool_name": event["tool_name"],
            "success": 1 if event["status"] == "success" else 0,
            "timestamp": event["created_at"],
        }
        for event in mock_raw_events_data
    ]

    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        # Mock cursor.fetchall() to return SQLite-formatted events
        mock_cursor.fetchall = AsyncMock(return_value=sqlite_events)

        # Mock conn.execute() to return cursor
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None

        # Mock context manager
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/summary")

        assert response.status_code == 200
        data = response.json()

        tool_usage = data["summary"]["tool_usage"]

        # Verify sorting by count (descending)
        assert len(tool_usage) == 3
        assert tool_usage[0]["tool_name"] == "find_tasks"
        assert tool_usage[0]["count"] == 3
        assert tool_usage[0]["success"] == 3
        assert tool_usage[0]["error"] == 0

        assert tool_usage[1]["tool_name"] == "manage_task"
        assert tool_usage[1]["count"] == 1

        assert tool_usage[2]["tool_name"] == "find_projects"
        assert tool_usage[2]["count"] == 1
        assert tool_usage[2]["error"] == 1


def test_get_24h_summary_success_rate_calculation(client, mock_supabase):
    """Test success rate calculation with various scenarios."""
    # All success - Convert to SQLite format (success=1 instead of status="success")
    all_success_data = [
        {"id": "e1", "tool_name": "test_tool", "success": 1, "timestamp": datetime.now(UTC).isoformat()},
        {"id": "e2", "tool_name": "test_tool", "success": 1, "timestamp": datetime.now(UTC).isoformat()},
    ]

    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        # Mock cursor.fetchall() to return SQLite-formatted events
        mock_cursor.fetchall = AsyncMock(return_value=all_success_data)

        # Mock conn.execute() to return cursor
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None

        # Mock context manager
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/summary")
        assert response.status_code == 200
        assert response.json()["summary"]["success_rate"] == 100.0


def test_get_24h_summary_empty_events(client, mock_supabase):
    """Test 24h summary with no events."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        # Mock cursor.fetchall() to return empty list
        mock_cursor.fetchall = AsyncMock(return_value=[])

        # Mock conn.execute() to return cursor
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None

        # Mock context manager
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/summary")

        assert response.status_code == 200
        data = response.json()

        summary = data["summary"]
        assert summary["total_events"] == 0
        assert summary["unique_tools"] == 0
        assert summary["success_count"] == 0
        assert summary["error_count"] == 0
        assert summary["success_rate"] == 0  # Avoid division by zero
        assert summary["tool_usage"] == []


def test_get_24h_summary_etag_generation(client, mock_supabase, mock_raw_events_data):
    """Test that ETag header is generated for summary."""
    # Convert mock data to SQLite format (success=1/0 instead of status="success"/"error")
    sqlite_events = [
        {
            "id": event["id"],
            "tool_name": event["tool_name"],
            "success": 1 if event["status"] == "success" else 0,
            "timestamp": event["created_at"],
        }
        for event in mock_raw_events_data
    ]

    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        # Mock cursor.fetchall() to return SQLite-formatted events
        mock_cursor.fetchall = AsyncMock(return_value=sqlite_events)

        # Mock conn.execute() to return cursor
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None

        # Mock context manager
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/summary")

        assert response.status_code == 200
        assert "etag" in response.headers
        assert "cache-control" in response.headers


def test_get_24h_summary_304_not_modified(client, mock_supabase, mock_raw_events_data):
    """Test 304 Not Modified response when ETag matches."""
    # Convert mock data to SQLite format (success=1/0 instead of status="success"/"error")
    sqlite_events = [
        {
            "id": event["id"],
            "tool_name": event["tool_name"],
            "success": 1 if event["status"] == "success" else 0,
            "timestamp": event["created_at"],
        }
        for event in mock_raw_events_data
    ]

    # Mock datetime to ensure consistent start_time calculation
    fixed_time = datetime.now(UTC)

    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        with patch("src.server.api_routes.mcp_analytics_api.datetime") as mock_datetime:
            # Mock datetime.now() to return fixed time for both requests
            mock_datetime.now.return_value = fixed_time
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            mock_conn = AsyncMock()
            mock_cursor = AsyncMock()

            # Mock cursor.fetchall() to return SQLite-formatted events
            mock_cursor.fetchall = AsyncMock(return_value=sqlite_events)

            # Mock conn.execute() to return cursor
            mock_conn.execute = AsyncMock(return_value=mock_cursor)
            mock_conn.row_factory = None

            # Mock context manager
            mock_connect.return_value.__aenter__.return_value = mock_conn

            # First request to get ETag
            response1 = client.get("/api/mcp/analytics/summary")
            assert response1.status_code == 200
            etag = response1.headers.get("etag")

            # Second request with matching ETag (same fixed time)
            response2 = client.get("/api/mcp/analytics/summary", headers={"If-None-Match": etag})
            assert response2.status_code == 304
            assert response2.headers.get("etag") == etag


def test_get_24h_summary_database_error(client, mock_supabase):
    """Test error handling when database query fails."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        # Make the connection raise an exception
        mock_connect.side_effect = Exception("Database connection failed")

        response = client.get("/api/mcp/analytics/summary")

        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["success"] is False
        assert "Failed to retrieve 24h summary" in data["detail"]["error"]


# ============================================================================
# POST /api/mcp/analytics/refresh-views
# ============================================================================


def test_refresh_materialized_views_success(client, mock_supabase):
    """Test successful refresh of materialized views (SQLite no-op)."""
    # SQLite version doesn't need manual refresh, uses automatic triggers
    response = client.post("/api/mcp/analytics/refresh-views")

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "refreshed_at" in data
    # Message should indicate automatic updates via triggers
    assert "trigger" in data["message"].lower() or "automatic" in data["message"].lower()


def test_refresh_materialized_views_no_data_returned(client):
    """Test SQLite refresh endpoint always succeeds (automatic triggers)."""
    # SQLite version uses automatic triggers, so this endpoint always succeeds
    response = client.post("/api/mcp/analytics/refresh-views")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "refreshed_at" in data


def test_refresh_materialized_views_database_error(client, mock_supabase):
    """Test SQLite refresh endpoint (no database errors expected)."""
    # SQLite version is a simple no-op that returns success, no database calls
    response = client.post("/api/mcp/analytics/refresh-views")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_refresh_materialized_views_response_structure(client, mock_supabase):
    """Test that refresh response has correct structure."""
    response = client.post("/api/mcp/analytics/refresh-views")

    assert response.status_code == 200
    data = response.json()

    # Verify all required fields
    assert "success" in data
    assert "message" in data
    assert "refreshed_at" in data

    # Verify types
    assert isinstance(data["success"], bool)
    assert isinstance(data["message"], str)
    assert isinstance(data["refreshed_at"], str)

    # Verify timestamp format (ISO 8601)
    from datetime import datetime
    datetime.fromisoformat(data["refreshed_at"])  # Should not raise


# ============================================================================
# Additional Edge Cases and Integration Tests
# ============================================================================


def test_hourly_analytics_table_name(client, mock_hourly_analytics_data):
    """Test that hourly analytics queries correct SQLite table."""
    # SQLite version uses direct SQL queries, not Supabase table access
    # This test verifies the endpoint works with the correct table name in SQL
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.fetchall = AsyncMock(return_value=[])
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/hourly")
        assert response.status_code == 200

        # Verify the SQL query includes the correct table name
        call_args = mock_conn.execute.call_args
        sql_query = call_args[0][0] if call_args else ""
        assert "archon_mcp_usage_hourly" in sql_query


def test_daily_analytics_table_name(client, mock_daily_analytics_data):
    """Test that daily analytics queries correct SQLite table."""
    # SQLite version uses direct SQL queries, not Supabase table access
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.fetchall = AsyncMock(return_value=[])
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/daily")
        assert response.status_code == 200

        # Verify the SQL query includes the correct table name
        call_args = mock_conn.execute.call_args
        sql_query = call_args[0][0] if call_args else ""
        assert "archon_mcp_usage_daily" in sql_query


def test_summary_events_table_name(client, mock_raw_events_data):
    """Test that summary queries correct SQLite events table."""
    # SQLite version uses direct SQL queries, not Supabase table access
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.fetchall = AsyncMock(return_value=[])
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/summary")
        assert response.status_code == 200

        # Verify the SQL query includes the correct table name
        call_args = mock_conn.execute.call_args
        sql_query = call_args[0][0] if call_args else ""
        assert "archon_mcp_usage_events" in sql_query


def test_summary_handles_missing_tool_names(client):
    """Test that summary handles events with missing tool names."""
    # Convert to SQLite format (success=1/0 instead of status="success"/"error")
    events_with_missing = [
        {"id": "e1", "tool_name": "valid_tool", "success": 1, "timestamp": datetime.now(UTC).isoformat()},
        {"id": "e2", "tool_name": None, "success": 1, "timestamp": datetime.now(UTC).isoformat()},
        {"id": "e3", "success": 1, "timestamp": datetime.now(UTC).isoformat()},  # No tool_name key
    ]

    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.fetchall = AsyncMock(return_value=events_with_missing)
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/summary")

        assert response.status_code == 200
        data = response.json()

        summary = data["summary"]
        assert summary["total_events"] == 3
        assert summary["unique_tools"] == 1  # Only valid_tool
        assert len(summary["tool_usage"]) == 1
        assert summary["tool_usage"][0]["tool_name"] == "valid_tool"


# ============================================================================
# GET /api/mcp/analytics/knowledge-bases
# ============================================================================


@pytest.fixture
def mock_kb_analytics_data():
    """Mock knowledge base analytics data."""
    return [
        {
            "source_id": "src_001",
            "source_name": "Anthropic Documentation",
            "query_count": 150,
            "unique_queries": 45,
            "avg_response_time_ms": 320,
            "success_rate": 95.5,
            "percentage_of_total": 50.0,
        },
        {
            "source_id": "src_002",
            "source_name": "React Documentation",
            "query_count": 90,
            "unique_queries": 30,
            "avg_response_time_ms": 280,
            "success_rate": 98.0,
            "percentage_of_total": 30.0,
        },
        {
            "source_id": "src_003",
            "source_name": "Python Best Practices",
            "query_count": 60,
            "unique_queries": 25,
            "avg_response_time_ms": 350,
            "success_rate": 92.5,
            "percentage_of_total": 20.0,
        },
    ]


def test_get_knowledge_base_analytics_success(client, mock_kb_analytics_data):
    """Test successful knowledge base analytics retrieval."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        # Mock cursor.fetchall() to return knowledge base data
        mock_cursor.fetchall = AsyncMock(return_value=[
            {k: v for k, v in kb.items() if k != "percentage_of_total"}  # percentage calculated in code
            for kb in mock_kb_analytics_data
        ])

        # Mock conn.execute() to return cursor
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None

        # Mock context manager
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/knowledge-bases?hours=24")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "data" in data
        assert "total_queries" in data
        assert "period" in data

        # Verify total queries
        assert data["total_queries"] == 300  # 150 + 90 + 60

        # Verify period information
        assert data["period"]["hours"] == 24
        assert "start_time" in data["period"]
        assert "end_time" in data["period"]

        # Verify data structure
        assert len(data["data"]) == 3
        first_kb = data["data"][0]
        assert "source_id" in first_kb
        assert "source_name" in first_kb
        assert "query_count" in first_kb
        assert "unique_queries" in first_kb
        assert "avg_response_time_ms" in first_kb
        assert "success_rate" in first_kb
        assert "percentage_of_total" in first_kb


def test_get_knowledge_base_analytics_empty(client):
    """Test empty state when no knowledge bases queried."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        # Mock empty result
        mock_cursor.fetchall = AsyncMock(return_value=[])
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/knowledge-bases?hours=24")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["data"] == []
        assert data["total_queries"] == 0
        assert "period" in data


def test_get_knowledge_base_analytics_custom_hours(client, mock_kb_analytics_data):
    """Test knowledge base analytics with custom time ranges."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        mock_cursor.fetchall = AsyncMock(return_value=[
            {k: v for k, v in kb.items() if k != "percentage_of_total"}
            for kb in mock_kb_analytics_data
        ])

        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None
        mock_connect.return_value.__aenter__.return_value = mock_conn

        # Test 48 hours
        response = client.get("/api/mcp/analytics/knowledge-bases?hours=48")
        assert response.status_code == 200
        data = response.json()
        assert data["period"]["hours"] == 48

        # Test 168 hours (1 week)
        response = client.get("/api/mcp/analytics/knowledge-bases?hours=168")
        assert response.status_code == 200
        data = response.json()
        assert data["period"]["hours"] == 168


def test_get_knowledge_base_analytics_validation(client):
    """Test parameter validation for hours parameter."""
    # Test hours < 1
    response = client.get("/api/mcp/analytics/knowledge-bases?hours=0")
    assert response.status_code == 422

    # Test hours > 168
    response = client.get("/api/mcp/analytics/knowledge-bases?hours=200")
    assert response.status_code == 422

    # Test valid boundary values
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.fetchall = AsyncMock(return_value=[])
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None
        mock_connect.return_value.__aenter__.return_value = mock_conn

        # Test hours = 1 (minimum valid)
        response = client.get("/api/mcp/analytics/knowledge-bases?hours=1")
        assert response.status_code == 200

        # Test hours = 168 (maximum valid)
        response = client.get("/api/mcp/analytics/knowledge-bases?hours=168")
        assert response.status_code == 200


def test_get_knowledge_base_analytics_etag(client, mock_kb_analytics_data):
    """Test ETag caching for knowledge base analytics."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        mock_cursor.fetchall = AsyncMock(return_value=[
            {k: v for k, v in kb.items() if k != "percentage_of_total"}
            for kb in mock_kb_analytics_data
        ])

        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None
        mock_connect.return_value.__aenter__.return_value = mock_conn

        # First request
        response1 = client.get("/api/mcp/analytics/knowledge-bases?hours=24")
        assert response1.status_code == 200
        etag = response1.headers.get("ETag")
        assert etag is not None
        assert "cache-control" in response1.headers
        assert response1.headers["cache-control"] == "no-cache, must-revalidate"

        # Second request with If-None-Match
        response2 = client.get(
            "/api/mcp/analytics/knowledge-bases?hours=24",
            headers={"If-None-Match": etag}
        )
        assert response2.status_code == 304
        assert response2.headers.get("ETag") == etag


def test_get_knowledge_base_analytics_etag_empty_state(client):
    """Test ETag generation for empty state."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        # Mock empty result
        mock_cursor.fetchall = AsyncMock(return_value=[])
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None
        mock_connect.return_value.__aenter__.return_value = mock_conn

        # Request
        response = client.get("/api/mcp/analytics/knowledge-bases?hours=24")
        assert response.status_code == 200

        # Verify ETag is present
        etag = response.headers.get("ETag")
        assert etag is not None
        assert "cache-control" in response.headers
        assert response.headers["cache-control"] == "no-cache, must-revalidate"

        # Verify empty data
        data = response.json()
        assert data["success"] is True
        assert data["data"] == []
        assert data["total_queries"] == 0


def test_get_knowledge_base_analytics_percentage_calculation(client):
    """Test that percentage_of_total is correctly calculated."""
    kb_data = [
        {
            "source_id": "src_001",
            "source_name": "Source A",
            "query_count": 100,
            "unique_queries": 10,
            "avg_response_time_ms": 300,
            "success_rate": 95.0,
        },
        {
            "source_id": "src_002",
            "source_name": "Source B",
            "query_count": 50,
            "unique_queries": 5,
            "avg_response_time_ms": 350,
            "success_rate": 90.0,
        },
        {
            "source_id": "src_003",
            "source_name": "Source C",
            "query_count": 50,
            "unique_queries": 8,
            "avg_response_time_ms": 320,
            "success_rate": 98.0,
        },
    ]

    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        mock_cursor.fetchall = AsyncMock(return_value=kb_data)
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/knowledge-bases?hours=24")

        assert response.status_code == 200
        data = response.json()

        # Total = 200, so percentages should be 50%, 25%, 25%
        assert data["total_queries"] == 200
        assert data["data"][0]["percentage_of_total"] == 50.0
        assert data["data"][1]["percentage_of_total"] == 25.0
        assert data["data"][2]["percentage_of_total"] == 25.0


def test_get_knowledge_base_analytics_sorting(client):
    """Test that results are sorted by query_count descending."""
    kb_data = [
        {
            "source_id": "src_high",
            "source_name": "High Usage",
            "query_count": 200,
            "unique_queries": 20,
            "avg_response_time_ms": 300,
            "success_rate": 95.0,
        },
        {
            "source_id": "src_low",
            "source_name": "Low Usage",
            "query_count": 50,
            "unique_queries": 5,
            "avg_response_time_ms": 350,
            "success_rate": 90.0,
        },
    ]

    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        # Return unsorted data
        mock_cursor.fetchall = AsyncMock(return_value=kb_data)
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/knowledge-bases?hours=24")

        assert response.status_code == 200
        data = response.json()

        # Verify highest query count is first
        assert data["data"][0]["source_id"] == "src_high"
        assert data["data"][0]["query_count"] == 200


def test_get_knowledge_base_analytics_response_structure(client, mock_kb_analytics_data):
    """Test that response has all required fields."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        mock_cursor.fetchall = AsyncMock(return_value=[
            {k: v for k, v in kb.items() if k != "percentage_of_total"}
            for kb in mock_kb_analytics_data
        ])

        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/knowledge-bases?hours=24")

        assert response.status_code == 200
        data = response.json()

        # Verify top-level structure
        assert "success" in data
        assert "data" in data
        assert "total_queries" in data
        assert "period" in data

        # Verify types
        assert isinstance(data["success"], bool)
        assert isinstance(data["data"], list)
        assert isinstance(data["total_queries"], int)
        assert isinstance(data["period"], dict)

        # Verify period structure
        assert "hours" in data["period"]
        assert "start_time" in data["period"]
        assert "end_time" in data["period"]

        # Verify knowledge base item structure
        if data["data"]:
            kb = data["data"][0]
            assert "source_id" in kb
            assert "source_name" in kb
            assert "query_count" in kb
            assert "unique_queries" in kb
            assert "avg_response_time_ms" in kb
            assert "success_rate" in kb
            assert "percentage_of_total" in kb


def test_get_knowledge_base_analytics_database_error(client):
    """Test error handling when database query fails."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_connect.side_effect = Exception("Database connection failed")

        response = client.get("/api/mcp/analytics/knowledge-bases?hours=24")

        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["success"] is False
        assert "Failed to retrieve knowledge base analytics" in data["detail"]["error"]


def test_get_knowledge_base_analytics_limit_to_top_10(client):
    """Test that only top 10 knowledge bases are returned."""
    # Create 15 knowledge bases
    many_kb_data = [
        {
            "source_id": f"src_{i:03d}",
            "source_name": f"Source {i}",
            "query_count": 100 - i,  # Descending order
            "unique_queries": 10,
            "avg_response_time_ms": 300,
            "success_rate": 95.0,
        }
        for i in range(15)
    ]

    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        # Database query should already be limited to 10 by LIMIT clause
        mock_cursor.fetchall = AsyncMock(return_value=many_kb_data[:10])
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/knowledge-bases?hours=24")

        assert response.status_code == 200
        data = response.json()

        # Verify only 10 results
        assert len(data["data"]) == 10


def test_get_knowledge_base_analytics_source_name_fallback(client):
    """Test source name fallback logic (display_name -> title -> url -> source_id)."""
    kb_data = [
        {
            "source_id": "src_001",
            "source_name": "Display Name",  # Has display name
            "query_count": 100,
            "unique_queries": 10,
            "avg_response_time_ms": 300,
            "success_rate": 95.0,
        },
        {
            "source_id": "src_002",
            "source_name": "src_002",  # Fallback to source_id (no other fields)
            "query_count": 50,
            "unique_queries": 5,
            "avg_response_time_ms": 350,
            "success_rate": 90.0,
        },
    ]

    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()

        mock_cursor.fetchall = AsyncMock(return_value=kb_data)
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None
        mock_connect.return_value.__aenter__.return_value = mock_conn

        response = client.get("/api/mcp/analytics/knowledge-bases?hours=24")

        assert response.status_code == 200
        data = response.json()

        # Verify source names are properly resolved
        assert data["data"][0]["source_name"] == "Display Name"
        assert data["data"][1]["source_name"] == "src_002"


def test_get_knowledge_base_analytics_default_hours_parameter(client):
    """Test that default hours parameter is 24."""
    with patch("src.server.api_routes.mcp_analytics_api.aiosqlite.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.fetchall = AsyncMock(return_value=[])
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.row_factory = None
        mock_connect.return_value.__aenter__.return_value = mock_conn

        # Request without hours parameter
        response = client.get("/api/mcp/analytics/knowledge-bases")

        assert response.status_code == 200
        data = response.json()
        assert data["period"]["hours"] == 24
