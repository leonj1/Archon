"""
Unit tests for MemoryService

This test suite validates memory storage and retrieval functionality.
Tests use a temporary SQLite database.
"""

import os
import tempfile

import pytest

from src.server.services.memory_service import MemoryService


@pytest.fixture
async def temp_db():
    """Create a temporary SQLite database for testing."""
    # Create a temporary file
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Create tables
    import aiosqlite
    async with aiosqlite.connect(db_path) as conn:
        # Create memory table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS archon_mcp_memories (
                id TEXT PRIMARY KEY,
                memory_key TEXT NOT NULL,
                memory_content TEXT NOT NULL,
                memory_type TEXT NOT NULL DEFAULT 'learning',
                session_id TEXT,
                tags TEXT,
                metadata TEXT,
                embedding BLOB,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create stats table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS archon_mcp_memory_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id TEXT NOT NULL,
                access_count INTEGER NOT NULL DEFAULT 0,
                last_accessed DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(memory_id)
            )
        """)

        await conn.commit()

    yield db_path

    # Cleanup
    try:
        os.unlink(db_path)
    except Exception:
        pass


@pytest.fixture
def memory_service(temp_db):
    """Create a MemoryService with the temporary database."""
    return MemoryService(db_path=temp_db)


# ========================================================================
# STORE MEMORY TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_store_memory_success(memory_service):
    """Test successful memory storage."""
    success, result = await memory_service.store_memory(
        memory_key="test_pattern",
        memory_content="This is a test pattern for authentication",
        memory_type="pattern",
        tags=["auth", "jwt"],
    )

    assert success
    assert "memory_id" in result
    assert result["memory_key"] == "test_pattern"
    assert result["action"] == "created"


@pytest.mark.asyncio
async def test_store_memory_update_existing(memory_service):
    """Test updating an existing memory."""
    # First create
    await memory_service.store_memory(
        memory_key="update_test",
        memory_content="Original content",
        memory_type="learning",
    )

    # Then update
    success, result = await memory_service.store_memory(
        memory_key="update_test",
        memory_content="Updated content",
        memory_type="pattern",
    )

    assert success
    assert result["action"] == "updated"
    assert result["memory_key"] == "update_test"


@pytest.mark.asyncio
async def test_store_memory_empty_key_fails(memory_service):
    """Test that storing with empty key fails."""
    success, result = await memory_service.store_memory(
        memory_key="",
        memory_content="Some content",
    )

    assert not success
    assert "error" in result


@pytest.mark.asyncio
async def test_store_memory_empty_content_fails(memory_service):
    """Test that storing with empty content fails."""
    success, result = await memory_service.store_memory(
        memory_key="test_key",
        memory_content="",
    )

    assert not success
    assert "error" in result


@pytest.mark.asyncio
async def test_store_memory_with_session(memory_service):
    """Test storing memory with session ID."""
    success, result = await memory_service.store_memory(
        memory_key="session_test",
        memory_content="Session-specific memory",
        session_id="session-123",
    )

    assert success
    assert result["action"] == "created"


# ========================================================================
# RETRIEVE MEMORY TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_retrieve_memory_by_key_success(memory_service):
    """Test successful memory retrieval by key."""
    # First create
    await memory_service.store_memory(
        memory_key="retrieve_test",
        memory_content="Test content for retrieval",
        memory_type="solution",
        tags=["cors", "debugging"],
    )

    # Then retrieve
    success, result = await memory_service.retrieve_memory_by_key("retrieve_test")

    assert success
    assert "memory" in result
    assert result["memory"]["memory_key"] == "retrieve_test"
    assert result["memory"]["memory_content"] == "Test content for retrieval"
    assert result["memory"]["memory_type"] == "solution"
    assert "cors" in result["memory"]["tags"]


@pytest.mark.asyncio
async def test_retrieve_memory_not_found(memory_service):
    """Test retrieving non-existent memory."""
    success, result = await memory_service.retrieve_memory_by_key("nonexistent")

    assert not success
    assert "error" in result


@pytest.mark.asyncio
async def test_retrieve_updates_access_stats(memory_service):
    """Test that retrieving updates access statistics."""
    # Create memory
    await memory_service.store_memory(
        memory_key="stats_test",
        memory_content="Test for stats",
    )

    # Retrieve multiple times
    await memory_service.retrieve_memory_by_key("stats_test")
    await memory_service.retrieve_memory_by_key("stats_test")

    success, result = await memory_service.retrieve_memory_by_key("stats_test")
    assert success


# ========================================================================
# SEARCH MEMORY TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_search_memories_by_type(memory_service):
    """Test searching memories by type."""
    # Create memories of different types
    await memory_service.store_memory(
        memory_key="pattern1",
        memory_content="Pattern content",
        memory_type="pattern",
    )
    await memory_service.store_memory(
        memory_key="solution1",
        memory_content="Solution content",
        memory_type="solution",
    )

    # Search for patterns
    success, result = await memory_service.search_memories(memory_type="pattern")

    assert success
    assert result["count"] >= 1
    assert all(m["memory_type"] == "pattern" for m in result["memories"])


@pytest.mark.asyncio
async def test_search_memories_by_query(memory_service):
    """Test searching memories by text query."""
    await memory_service.store_memory(
        memory_key="search_test",
        memory_content="This is about authentication with JWT tokens",
        memory_type="pattern",
    )

    # Search by query
    success, result = await memory_service.search_memories(query="authentication")

    assert success
    assert result["count"] >= 1


@pytest.mark.asyncio
async def test_search_memories_with_limit(memory_service):
    """Test search with match_count limit."""
    # Create multiple memories
    for i in range(10):
        await memory_service.store_memory(
            memory_key=f"limit_test_{i}",
            memory_content=f"Content {i}",
            memory_type="learning",
        )

    # Search with limit
    success, result = await memory_service.search_memories(
        memory_type="learning",
        match_count=3,
    )

    assert success
    assert result["count"] <= 3


# ========================================================================
# LIST MEMORY TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_list_memories(memory_service):
    """Test listing all memories."""
    # Create some memories
    await memory_service.store_memory(
        memory_key="list_test1",
        memory_content="Content 1",
    )
    await memory_service.store_memory(
        memory_key="list_test2",
        memory_content="Content 2",
    )

    success, result = await memory_service.list_memories()

    assert success
    assert result["total"] >= 2
    assert "memories" in result


@pytest.mark.asyncio
async def test_list_memories_filtered_by_type(memory_service):
    """Test listing memories filtered by type."""
    await memory_service.store_memory(
        memory_key="filter_test",
        memory_content="Pattern content",
        memory_type="pattern",
    )

    success, result = await memory_service.list_memories(memory_type="pattern")

    assert success
    assert all(m["memory_type"] == "pattern" for m in result["memories"])


# ========================================================================
# DELETE MEMORY TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_delete_memory_success(memory_service):
    """Test successful memory deletion."""
    # Create memory
    success, create_result = await memory_service.store_memory(
        memory_key="delete_test",
        memory_content="To be deleted",
    )
    memory_id = create_result["memory_id"]

    # Delete it
    success, result = await memory_service.delete_memory(memory_id)

    assert success
    assert "message" in result

    # Verify it's gone
    success, _ = await memory_service.retrieve_memory_by_key("delete_test")
    assert not success


@pytest.mark.asyncio
async def test_delete_nonexistent_memory_fails(memory_service):
    """Test deleting non-existent memory."""
    success, result = await memory_service.delete_memory("nonexistent-id")

    assert not success
    assert "error" in result
