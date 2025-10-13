"""
Comprehensive tests for MCP Analytics API endpoints.

Tests all 4 endpoints:
- GET /api/mcp/analytics/hourly
- GET /api/mcp/analytics/daily
- GET /api/mcp/analytics/summary
- POST /api/mcp/analytics/refresh-views
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

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
    mock_result = MagicMock()
    mock_result.data = mock_hourly_analytics_data

    mock_query = MagicMock()
    mock_query.select.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_query

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
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
    mock_result = MagicMock()
    mock_result.data = mock_hourly_analytics_data

    mock_query = MagicMock()
    mock_query.select.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_query

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
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
    mock_result = MagicMock()
    mock_result.data = []

    mock_query = MagicMock()
    mock_query.select.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_query

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
        response = client.get("/api/mcp/analytics/hourly")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 0
        assert data["data"] == []


def test_get_hourly_analytics_etag_generation(client, mock_supabase, mock_hourly_analytics_data):
    """Test that ETag header is generated for hourly analytics."""
    mock_result = MagicMock()
    mock_result.data = mock_hourly_analytics_data

    mock_query = MagicMock()
    mock_query.select.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_query

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
        response = client.get("/api/mcp/analytics/hourly")

        assert response.status_code == 200
        assert "etag" in response.headers
        assert "cache-control" in response.headers
        assert response.headers["cache-control"] == "no-cache, must-revalidate"


def test_get_hourly_analytics_304_not_modified(client, mock_supabase, mock_hourly_analytics_data):
    """Test 304 Not Modified response when ETag matches."""
    mock_result = MagicMock()
    mock_result.data = mock_hourly_analytics_data

    mock_query = MagicMock()
    mock_query.select.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_query

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
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
    mock_supabase.table.side_effect = Exception("Database connection failed")

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
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
    mock_result = MagicMock()
    mock_result.data = mock_daily_analytics_data

    mock_query = MagicMock()
    mock_query.select.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_query

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
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
    mock_result = MagicMock()
    mock_result.data = mock_daily_analytics_data

    mock_query = MagicMock()
    mock_query.select.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_query

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
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
    mock_result = MagicMock()
    mock_result.data = []

    mock_query = MagicMock()
    mock_query.select.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_query

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
        response = client.get("/api/mcp/analytics/daily")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 0
        assert data["data"] == []


def test_get_daily_analytics_etag_generation(client, mock_supabase, mock_daily_analytics_data):
    """Test that ETag header is generated for daily analytics."""
    mock_result = MagicMock()
    mock_result.data = mock_daily_analytics_data

    mock_query = MagicMock()
    mock_query.select.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_query

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
        response = client.get("/api/mcp/analytics/daily")

        assert response.status_code == 200
        assert "etag" in response.headers
        assert "cache-control" in response.headers
        assert response.headers["cache-control"] == "no-cache, must-revalidate"


def test_get_daily_analytics_304_not_modified(client, mock_supabase, mock_daily_analytics_data):
    """Test 304 Not Modified response when ETag matches."""
    mock_result = MagicMock()
    mock_result.data = mock_daily_analytics_data

    mock_query = MagicMock()
    mock_query.select.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_query

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
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
    mock_supabase.table.side_effect = Exception("Database connection failed")

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
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
    mock_result = MagicMock()
    mock_result.data = mock_raw_events_data

    mock_query = MagicMock()
    mock_query.select.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_query

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
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
    mock_result = MagicMock()
    mock_result.data = mock_raw_events_data

    mock_query = MagicMock()
    mock_query.select.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_query

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
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
    # All success
    all_success_data = [
        {"id": "e1", "tool_name": "test_tool", "status": "success", "created_at": datetime.now(UTC).isoformat()},
        {"id": "e2", "tool_name": "test_tool", "status": "success", "created_at": datetime.now(UTC).isoformat()},
    ]

    mock_result = MagicMock()
    mock_result.data = all_success_data

    mock_query = MagicMock()
    mock_query.select.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_query

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
        response = client.get("/api/mcp/analytics/summary")
        assert response.status_code == 200
        assert response.json()["summary"]["success_rate"] == 100.0


def test_get_24h_summary_empty_events(client, mock_supabase):
    """Test 24h summary with no events."""
    mock_result = MagicMock()
    mock_result.data = []

    mock_query = MagicMock()
    mock_query.select.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_query

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
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
    mock_result = MagicMock()
    mock_result.data = mock_raw_events_data

    mock_query = MagicMock()
    mock_query.select.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_query

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
        response = client.get("/api/mcp/analytics/summary")

        assert response.status_code == 200
        assert "etag" in response.headers
        assert "cache-control" in response.headers


def test_get_24h_summary_304_not_modified(client, mock_supabase, mock_raw_events_data):
    """Test 304 Not Modified response when ETag matches."""
    mock_result = MagicMock()
    mock_result.data = mock_raw_events_data

    mock_query = MagicMock()
    mock_query.select.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_query

    # Mock datetime to ensure consistent start_time calculation
    fixed_time = datetime.now(UTC)

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
        with patch("src.server.api_routes.mcp_analytics_api.datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_time
            mock_datetime.utcnow.return_value = fixed_time.replace(tzinfo=None)

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
    mock_supabase.table.side_effect = Exception("Database connection failed")

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
        response = client.get("/api/mcp/analytics/summary")

        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["success"] is False
        assert "Failed to retrieve 24h summary" in data["detail"]["error"]


# ============================================================================
# POST /api/mcp/analytics/refresh-views
# ============================================================================


def test_refresh_materialized_views_success(client, mock_supabase):
    """Test successful refresh of materialized views."""
    mock_result = MagicMock()
    mock_result.data = {"status": "success"}

    mock_supabase.rpc.return_value.execute.return_value = mock_result

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
        response = client.post("/api/mcp/analytics/refresh-views")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["message"] == "Materialized views refreshed successfully"
        assert "refreshed_at" in data

        # Verify RPC was called
        mock_supabase.rpc.assert_called_once_with("refresh_mcp_usage_views")


def test_refresh_materialized_views_no_data_returned(client, mock_supabase):
    """Test error when refresh returns no data."""
    mock_result = MagicMock()
    mock_result.data = None

    mock_supabase.rpc.return_value.execute.return_value = mock_result

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
        response = client.post("/api/mcp/analytics/refresh-views")

        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["success"] is False
        assert "Failed to refresh materialized views - no data returned" in data["detail"]["error"]


def test_refresh_materialized_views_database_error(client, mock_supabase):
    """Test error handling when database RPC fails."""
    mock_supabase.rpc.side_effect = Exception("RPC function not found")

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
        response = client.post("/api/mcp/analytics/refresh-views")

        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["success"] is False
        assert "Failed to refresh materialized views" in data["detail"]["error"]


def test_refresh_materialized_views_response_structure(client, mock_supabase):
    """Test that refresh response has correct structure."""
    mock_result = MagicMock()
    mock_result.data = {"status": "success"}

    mock_supabase.rpc.return_value.execute.return_value = mock_result

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
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


def test_hourly_analytics_table_name(client, mock_supabase, mock_hourly_analytics_data):
    """Test that hourly analytics queries correct table."""
    mock_result = MagicMock()
    mock_result.data = mock_hourly_analytics_data

    mock_query = MagicMock()
    mock_query.select.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_query

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
        client.get("/api/mcp/analytics/hourly")

        # Verify correct table was accessed
        mock_supabase.table.assert_called_once_with("archon_mcp_usage_hourly")


def test_daily_analytics_table_name(client, mock_supabase, mock_daily_analytics_data):
    """Test that daily analytics queries correct table."""
    mock_result = MagicMock()
    mock_result.data = mock_daily_analytics_data

    mock_query = MagicMock()
    mock_query.select.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_query

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
        client.get("/api/mcp/analytics/daily")

        # Verify correct table was accessed
        mock_supabase.table.assert_called_once_with("archon_mcp_usage_daily")


def test_summary_events_table_name(client, mock_supabase, mock_raw_events_data):
    """Test that summary queries correct events table."""
    mock_result = MagicMock()
    mock_result.data = mock_raw_events_data

    mock_query = MagicMock()
    mock_query.select.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_query

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
        client.get("/api/mcp/analytics/summary")

        # Verify correct table was accessed
        mock_supabase.table.assert_called_once_with("archon_mcp_usage_events")


def test_summary_handles_missing_tool_names(client, mock_supabase):
    """Test that summary handles events with missing tool names."""
    events_with_missing = [
        {"id": "e1", "tool_name": "valid_tool", "status": "success", "created_at": datetime.now(UTC).isoformat()},
        {"id": "e2", "tool_name": None, "status": "success", "created_at": datetime.now(UTC).isoformat()},
        {"id": "e3", "status": "success", "created_at": datetime.now(UTC).isoformat()},  # No tool_name key
    ]

    mock_result = MagicMock()
    mock_result.data = events_with_missing

    mock_query = MagicMock()
    mock_query.select.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
    mock_supabase.table.return_value = mock_query

    with patch("src.server.api_routes.mcp_analytics_api.get_supabase_client", return_value=mock_supabase):
        response = client.get("/api/mcp/analytics/summary")

        assert response.status_code == 200
        data = response.json()

        summary = data["summary"]
        assert summary["total_events"] == 3
        assert summary["unique_tools"] == 1  # Only valid_tool
        assert len(summary["tool_usage"]) == 1
        assert summary["tool_usage"][0]["tool_name"] == "valid_tool"
