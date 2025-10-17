"""
Tests for MCP Usage Tracking Middleware

Validates that MCP tool usage is properly tracked and stored in the database.
"""

import os
import tempfile
from datetime import datetime

import aiosqlite
import pytest

from src.mcp_server.middleware.usage_tracker import MCPUsageTracker


@pytest.fixture
async def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = f.name

    # Initialize database with MCP usage tracking tables
    async with aiosqlite.connect(db_path) as conn:
        # Read and apply the MCP usage tracking migration
        migration_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "migration/sqlite/002_mcp_usage_tracking.sql"
        )

        with open(migration_path, 'r') as f:
            migration_sql = f.read()

        statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]
        for statement in statements:
            await conn.execute(statement)
            await conn.commit()

    yield db_path

    # Cleanup
    try:
        os.unlink(db_path)
    except:
        pass


@pytest.mark.asyncio
async def test_usage_tracker_initialization(temp_db):
    """Test that MCPUsageTracker initializes correctly."""
    tracker = MCPUsageTracker()
    tracker.db_path = temp_db

    assert tracker.db_path == temp_db
    assert tracker._enabled is True
    assert tracker._client_type == "unknown"


@pytest.mark.asyncio
async def test_track_tool_usage_inserts_event(temp_db):
    """Test that tracking a tool usage inserts an event into the database."""
    tracker = MCPUsageTracker()
    tracker.db_path = temp_db
    tracker.set_session_context("test-session-123", "claude-code")

    # Track a tool usage
    await tracker.track_tool_usage(
        tool_name="rag_search_knowledge_base",
        tool_category="rag",
        request_data={"query": "test query", "match_count": 5},
        response_time_ms=150,
        success=True
    )

    # Verify the event was inserted
    async with aiosqlite.connect(temp_db) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("""
            SELECT * FROM archon_mcp_usage_events
            WHERE tool_name = 'rag_search_knowledge_base'
        """)
        row = await cursor.fetchone()

        assert row is not None
        assert row["tool_name"] == "rag_search_knowledge_base"
        assert row["tool_category"] == "rag"
        assert row["session_id"] == "test-session-123"
        assert row["client_type"] == "claude-code"
        assert row["response_time_ms"] == 150
        assert row["success"] == 1


@pytest.mark.asyncio
async def test_track_tool_usage_with_error(temp_db):
    """Test tracking a failed tool invocation."""
    tracker = MCPUsageTracker()
    tracker.db_path = temp_db

    await tracker.track_tool_usage(
        tool_name="rag_search_knowledge_base",
        tool_category="rag",
        request_data={"query": "test"},
        response_time_ms=50,
        success=False,
        error_type="ValueError"
    )

    # Verify error was recorded
    async with aiosqlite.connect(temp_db) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("""
            SELECT * FROM archon_mcp_usage_events
            WHERE success = 0
        """)
        row = await cursor.fetchone()

        assert row is not None
        assert row["success"] == 0
        assert row["error_type"] == "ValueError"


@pytest.mark.asyncio
async def test_hourly_aggregation_trigger(temp_db):
    """Test that inserting events triggers hourly aggregation."""
    tracker = MCPUsageTracker()
    tracker.db_path = temp_db

    # Track multiple events
    for i in range(3):
        await tracker.track_tool_usage(
            tool_name="find_projects",
            tool_category="project",
            request_data={},
            response_time_ms=100 + (i * 10),
            success=True
        )

    # Verify hourly aggregation was created
    async with aiosqlite.connect(temp_db) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("""
            SELECT * FROM archon_mcp_usage_hourly
            WHERE tool_name = 'find_projects'
        """)
        row = await cursor.fetchone()

        assert row is not None
        assert row["call_count"] == 3
        assert row["error_count"] == 0
        assert row["tool_category"] == "project"


@pytest.mark.asyncio
async def test_daily_aggregation_trigger(temp_db):
    """Test that inserting events triggers daily aggregation."""
    tracker = MCPUsageTracker()
    tracker.db_path = temp_db

    # Track an event
    await tracker.track_tool_usage(
        tool_name="manage_task",
        tool_category="task",
        request_data={"action": "create"},
        response_time_ms=200,
        success=True
    )

    # Verify daily aggregation was created
    async with aiosqlite.connect(temp_db) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("""
            SELECT * FROM archon_mcp_usage_daily
            WHERE tool_name = 'manage_task'
        """)
        row = await cursor.fetchone()

        assert row is not None
        assert row["call_count"] == 1
        assert row["tool_category"] == "task"


@pytest.mark.asyncio
async def test_tracker_can_be_disabled(temp_db):
    """Test that tracking can be disabled."""
    tracker = MCPUsageTracker()
    tracker.db_path = temp_db
    tracker.disable()

    # Track a tool usage
    await tracker.track_tool_usage(
        tool_name="rag_search_knowledge_base",
        tool_category="rag",
        request_data={},
        response_time_ms=150,
        success=True
    )

    # Verify no event was inserted
    async with aiosqlite.connect(temp_db) as conn:
        cursor = await conn.execute("SELECT COUNT(*) as count FROM archon_mcp_usage_events")
        row = await cursor.fetchone()
        assert row[0] == 0


@pytest.mark.asyncio
async def test_query_truncation(temp_db):
    """Test that long query text is truncated to 500 characters."""
    tracker = MCPUsageTracker()
    tracker.db_path = temp_db

    long_query = "a" * 600  # 600 characters

    await tracker.track_tool_usage(
        tool_name="rag_search_knowledge_base",
        tool_category="rag",
        request_data={"query": long_query},
        response_time_ms=150,
        success=True
    )

    # Verify query was truncated
    async with aiosqlite.connect(temp_db) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("""
            SELECT query_text FROM archon_mcp_usage_events
        """)
        row = await cursor.fetchone()

        assert row is not None
        assert len(row["query_text"]) == 500
        assert row["query_text"] == "a" * 500


@pytest.mark.asyncio
async def test_metadata_extraction(temp_db):
    """Test that relevant metadata is extracted from requests."""
    tracker = MCPUsageTracker()
    tracker.db_path = temp_db

    await tracker.track_tool_usage(
        tool_name="rag_search_knowledge_base",
        tool_category="rag",
        request_data={
            "query": "test query",
            "source_id": "src_123",
            "match_count": 10
        },
        response_time_ms=150,
        success=True
    )

    # Verify metadata was extracted
    async with aiosqlite.connect(temp_db) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("""
            SELECT * FROM archon_mcp_usage_events
        """)
        row = await cursor.fetchone()

        assert row is not None
        assert row["source_id"] == "src_123"
        assert row["query_text"] == "test query"
        assert row["match_count"] == 10


@pytest.mark.asyncio
async def test_response_time_calculation(temp_db):
    """Test that average response time is calculated correctly."""
    tracker = MCPUsageTracker()
    tracker.db_path = temp_db

    # Track three events with different response times
    await tracker.track_tool_usage("test_tool", "test", {}, response_time_ms=100, success=True)
    await tracker.track_tool_usage("test_tool", "test", {}, response_time_ms=200, success=True)
    await tracker.track_tool_usage("test_tool", "test", {}, response_time_ms=300, success=True)

    # Verify average was calculated
    async with aiosqlite.connect(temp_db) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("""
            SELECT avg_response_time_ms FROM archon_mcp_usage_hourly
            WHERE tool_name = 'test_tool'
        """)
        row = await cursor.fetchone()

        assert row is not None
        # Average should be 200
        assert row["avg_response_time_ms"] == 200
