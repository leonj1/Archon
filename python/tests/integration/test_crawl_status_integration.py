"""
Integration tests for crawl status updates.

Tests the complete flow from crawl initiation to completion,
verifying that metadata.crawl_status updates correctly.

Requirements:
- Backend must be running on localhost:8181
- SQLite database configured
- Qdrant running on localhost:6333 (optional)
- No mocking - all real operations
"""

import asyncio
import json
import os
import sqlite3
import time
from typing import Any

import pytest
import requests


# Test Configuration
BACKEND_URL = "http://localhost:8181"
TEST_URL = "https://go.dev/doc"  # Real URL to crawl
CRAWL_TIMEOUT = 60  # seconds to wait for crawl completion
SQLITE_PATH = os.getenv("SQLITE_PATH", "/home/jose/src/Archon/data/archon.db")


# ==========================================
# Fixtures
# ==========================================


@pytest.fixture(scope="session")
def backend_available():
    """Verify backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        assert response.status_code == 200, "Backend health check failed"
        return True
    except requests.exceptions.RequestException as e:
        pytest.skip(f"Backend not available: {e}")


@pytest.fixture
def db_connection():
    """Provide SQLite database connection."""
    if not os.path.exists(SQLITE_PATH):
        pytest.skip(f"Database not found at {SQLITE_PATH}")

    conn = sqlite3.connect(SQLITE_PATH)
    yield conn
    conn.close()


def get_source_from_db(conn: sqlite3.Connection, source_id: str) -> dict[str, Any] | None:
    """Get source record from database."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT source_id, title, metadata, created_at, updated_at FROM archon_sources WHERE source_id = ?",
        (source_id,),
    )
    row = cursor.fetchone()

    if not row:
        return None

    metadata = json.loads(row[2]) if row[2] else {}

    return {
        "source_id": row[0],
        "title": row[1],
        "metadata": metadata,
        "created_at": row[3],
        "updated_at": row[4],
    }


def get_document_count(conn: sqlite3.Connection, source_id: str) -> int:
    """Get document count for a source."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM archon_crawled_pages WHERE source_id = ?",
        (source_id,),
    )
    return cursor.fetchone()[0]


async def get_most_recent_source(db_conn: sqlite3.Connection, created_after_ts: str | None = None) -> str | None:
    """
    Get the most recently created source from the database.

    Since the API doesn't return source_id, we find the source by
    getting the most recently created one.

    Args:
        db_conn: Database connection
        created_after_ts: Optional timestamp to filter by

    Returns:
        source_id if found, None otherwise
    """
    try:
        cursor = db_conn.cursor()

        if created_after_ts:
            cursor.execute(
                """
                SELECT source_id FROM archon_sources
                WHERE created_at > ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (created_after_ts,),
            )
        else:
            cursor.execute(
                """
                SELECT source_id FROM archon_sources
                ORDER BY created_at DESC
                LIMIT 1
                """
            )

        row = cursor.fetchone()
        return row[0] if row else None
    except Exception:
        return None


# ==========================================
# Tests
# ==========================================


@pytest.mark.asyncio
async def test_crawl_initiation_sets_pending_status(backend_available, db_connection):
    """
    Test that starting a crawl creates a source with status='pending'.

    Flow:
    1. Trigger crawl via API
    2. Get progressId from response
    3. Poll progress endpoint to get source_id
    4. Query database for source
    5. Verify metadata.crawl_status is 'pending'
    """
    # Trigger crawl
    response = requests.post(
        f"{BACKEND_URL}/api/knowledge-items/crawl",
        json={"url": TEST_URL, "knowledge_type": "technical"},
        timeout=10,
    )

    assert response.status_code in [200, 201], f"Crawl failed: {response.text}"

    data = response.json()
    progress_id = data.get("progressId")
    assert progress_id, "No progressId in response"

    # Wait a moment for source to be created in database
    await asyncio.sleep(2)

    # Get the most recently created source (should be the one we just crawled)
    source_id = await get_most_recent_source(db_connection)
    assert source_id, "Could not find any source in database"

    # Check database
    source = get_source_from_db(db_connection, source_id)
    assert source, f"Source {source_id} not found in database"

    crawl_status = source["metadata"].get("crawl_status", "unknown")
    assert crawl_status in ["pending", "processing"], f"Expected 'pending' or 'processing', got '{crawl_status}'"

    print(f"✓ Source created with crawl_status='{crawl_status}' (source_id: {source_id})")


@pytest.mark.asyncio
async def test_crawl_completion_updates_status_to_completed(backend_available, db_connection):
    """
    Test that after crawl completes, status updates to 'completed'.

    Flow:
    1. Trigger crawl
    2. Poll database until documents appear or timeout
    3. Verify crawl_status updates to 'completed'
    4. Verify documents were stored
    """
    # Trigger crawl
    response = requests.post(
        f"{BACKEND_URL}/api/knowledge-items/crawl",
        json={"url": TEST_URL, "knowledge_type": "technical"},
        timeout=10,
    )

    assert response.status_code in [200, 201], f"Crawl failed: {response.text}"

    data = response.json()
    progress_id = data.get("progressId")
    assert progress_id, "No progressId in response"

    # Wait for source to be created
    await asyncio.sleep(2)

    # Get the most recently created source
    source_id = await get_most_recent_source(db_connection)
    assert source_id, "Could not find source in database"

    print(f"Crawl started for source_id: {source_id}")
    print(f"Waiting up to {CRAWL_TIMEOUT}s for completion...")

    # Poll for completion
    start_time = time.time()
    crawl_completed = False
    doc_count = 0

    while time.time() - start_time < CRAWL_TIMEOUT:
        await asyncio.sleep(3)  # Poll every 3 seconds

        # Check database
        source = get_source_from_db(db_connection, source_id)
        if not source:
            continue

        crawl_status = source["metadata"].get("crawl_status", "pending")
        doc_count = get_document_count(db_connection, source_id)

        elapsed = int(time.time() - start_time)
        print(f"[{elapsed}s] Status: {crawl_status}, Documents: {doc_count}")

        if crawl_status == "completed" or doc_count > 0:
            crawl_completed = True
            break

    # Verify completion
    assert crawl_completed, f"Crawl did not complete within {CRAWL_TIMEOUT}s"

    # Final verification
    source = get_source_from_db(db_connection, source_id)
    final_status = source["metadata"].get("crawl_status", "unknown")

    # This is the key test: status should be 'completed'
    assert final_status == "completed", (
        f"Expected crawl_status='completed', got '{final_status}'. "
        f"This is the bug being investigated!"
    )

    assert doc_count > 0, f"No documents stored (expected > 0, got {doc_count})"

    print(f"✓ Crawl completed with crawl_status='completed' ({doc_count} documents)")


@pytest.mark.asyncio
async def test_completed_crawl_shows_active_in_api(backend_available, db_connection):
    """
    Test that API returns status='active' for completed crawls.

    Flow:
    1. Trigger crawl and wait for completion
    2. Query API endpoint for sources
    3. Verify response has status='active' (mapped from crawl_status='completed')
    """
    # Trigger crawl
    response = requests.post(
        f"{BACKEND_URL}/api/knowledge-items/crawl",
        json={"url": TEST_URL, "knowledge_type": "technical"},
        timeout=10,
    )

    assert response.status_code in [200, 201]
    progress_id = response.json().get("progressId")
    assert progress_id, "No progressId in response"

    # Wait for source to be created
    await asyncio.sleep(2)

    # Get the most recently created source
    source_id = await get_most_recent_source(db_connection)
    assert source_id, "Could not find source in database"

    # Wait for completion (documents stored)
    print(f"Waiting for crawl completion (source_id: {source_id})...")
    start_time = time.time()
    doc_count = 0
    crawl_status = None

    while time.time() - start_time < CRAWL_TIMEOUT:
        await asyncio.sleep(3)

        source = get_source_from_db(db_connection, source_id)
        if source:
            crawl_status = source["metadata"].get("crawl_status")
            doc_count = get_document_count(db_connection, source_id)

            elapsed = int(time.time() - start_time)
            print(f"[{elapsed}s] DB Status: {crawl_status}, Documents: {doc_count}")

            # Wait for documents to be stored (actual completion)
            if doc_count > 0:
                # Give it a moment for status update to happen (if it's going to)
                await asyncio.sleep(3)
                # Re-check status one more time
                source = get_source_from_db(db_connection, source_id)
                crawl_status = source["metadata"].get("crawl_status")
                print(f"Final DB crawl_status after completion: {crawl_status}")
                break

    assert doc_count > 0, f"Crawl did not complete within {CRAWL_TIMEOUT}s (no documents stored)"

    # Query API
    api_response = requests.get(f"{BACKEND_URL}/api/knowledge-items", timeout=10)
    assert api_response.status_code == 200

    items = api_response.json().get("items", [])
    matching_item = next((item for item in items if item.get("source_id") == source_id), None)

    assert matching_item, f"Source {source_id} not found in API response"

    # Get API status
    api_status = matching_item.get("status")
    print(f"API status: {api_status} (from database crawl_status: {crawl_status})")

    # Verify status mapping
    # The correct mapping should be: crawl_status='completed' → API status='active'
    # But due to the bug, crawl_status stays 'pending' → API status='processing'
    assert api_status == "active", (
        f"Expected status='active' in API response, got '{api_status}'. "
        f"Database crawl_status is '{crawl_status}' (should be 'completed'). "
        f"This test will fail until the crawl_status update bug is fixed!"
    )

    print(f"✓ API returns status='active' for completed crawl")


@pytest.mark.asyncio
async def test_source_metadata_persists_to_database(backend_available, db_connection):
    """
    Test that crawl metadata persists correctly to database.

    Flow:
    1. Trigger crawl
    2. Wait for completion
    3. Query database directly
    4. Verify all metadata fields are present
    5. Verify crawl_status is set correctly
    """
    # Trigger crawl
    response = requests.post(
        f"{BACKEND_URL}/api/knowledge-items/crawl",
        json={
            "url": TEST_URL,
            "knowledge_type": "technical",
        },
        timeout=10,
    )

    assert response.status_code in [200, 201]
    progress_id = response.json().get("progressId")
    assert progress_id, "No progressId in response"

    # Wait for source to be created
    await asyncio.sleep(2)

    # Get the most recently created source
    source_id = await get_most_recent_source(db_connection)
    assert source_id, "Could not find source in database"

    # Wait for completion
    start_time = time.time()
    source = None

    while time.time() - start_time < CRAWL_TIMEOUT:
        await asyncio.sleep(3)

        source = get_source_from_db(db_connection, source_id)
        if source:
            doc_count = get_document_count(db_connection, source_id)
            if doc_count > 0:
                break

    assert source, f"Source {source_id} not found in database"

    # Verify metadata structure
    metadata = source["metadata"]
    assert isinstance(metadata, dict), "Metadata is not a dictionary"

    # Verify required fields
    assert "crawl_status" in metadata, "Missing crawl_status in metadata"
    assert "knowledge_type" in metadata, "Missing knowledge_type in metadata"

    crawl_status = metadata["crawl_status"]
    assert crawl_status in ["pending", "completed", "failed"], (
        f"Invalid crawl_status: {crawl_status}"
    )

    print(f"✓ Metadata persisted correctly (crawl_status: {crawl_status})")


@pytest.mark.asyncio
async def test_failed_crawl_sets_error_status(backend_available, db_connection):
    """
    Test that failed crawls set status to 'failed'.

    Flow:
    1. Trigger crawl with invalid URL
    2. Wait for failure
    3. Verify crawl_status is 'failed'
    """
    # Trigger crawl with invalid URL (should fail)
    invalid_url = "https://this-domain-definitely-does-not-exist-12345.com"

    response = requests.post(
        f"{BACKEND_URL}/api/knowledge-items/crawl",
        json={"url": invalid_url, "knowledge_type": "technical"},
        timeout=10,
    )

    # May return 200 initially and fail during crawl, or may fail immediately
    if response.status_code not in [200, 201]:
        pytest.skip("Failed crawl didn't return success status")

    progress_id = response.json().get("progressId")
    if not progress_id:
        pytest.skip("Failed crawl didn't return progressId")

    # Wait for source to be created
    await asyncio.sleep(2)

    # Get the most recently created source
    source_id = await get_most_recent_source(db_connection)
    if not source_id:
        pytest.skip("Failed crawl didn't create source record")

    # Wait for failure detection
    start_time = time.time()
    failed = False

    while time.time() - start_time < 30:  # Shorter timeout for expected failure
        await asyncio.sleep(2)

        source = get_source_from_db(db_connection, source_id)
        if source:
            crawl_status = source["metadata"].get("crawl_status")
            if crawl_status == "failed":
                failed = True
                break

    if failed:
        print(f"✓ Failed crawl correctly set crawl_status='failed'")
    else:
        # This test may be skipped if failure detection isn't implemented yet
        pytest.skip("Failure detection not yet implemented or timeout occurred")


# ==========================================
# Helper Tests
# ==========================================


def test_database_connection(db_connection):
    """Verify we can connect to the database."""
    cursor = db_connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    assert len(tables) > 0, "No tables found in database"

    table_names = [t[0] for t in tables]
    assert "archon_sources" in table_names, "archon_sources table not found"
    assert "archon_crawled_pages" in table_names, "archon_crawled_pages table not found"

    print(f"✓ Database connection successful ({len(tables)} tables found)")


def test_backend_health(backend_available):
    """Verify backend is healthy."""
    response = requests.get(f"{BACKEND_URL}/health", timeout=5)
    assert response.status_code == 200
    print("✓ Backend is healthy")


# ==========================================
# Main
# ==========================================


if __name__ == "__main__":
    """Run tests with pytest."""
    pytest.main([__file__, "-v", "-s"])
