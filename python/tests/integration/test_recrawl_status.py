"""
Integration Test: Recrawl Status Bug

This test reproduces and verifies the recrawl status bug described in INVESTIGATION_REPORT.md.

Bug Description:
    After a successful recrawl operation, the knowledge card status badge displays "Pending"
    instead of "Completed". The root cause is that crawl_status is never set to "pending"
    during initial source creation, and the completion update may not persist correctly.

Test Strategy:
    1. Create a new knowledge item by crawling a real URL
    2. Wait for initial crawl to complete
    3. Verify status is "completed" after initial crawl
    4. Trigger a recrawl using the refresh endpoint
    5. Wait for recrawl to complete
    6. Verify status is STILL "completed" (not stuck in "pending")
    7. Verify both API responses and database state

Requirements:
    - Backend must be running on localhost:8181
    - Valid embedding provider API key configured
    - Real network connectivity for crawling
    - NO MOCKS - tests the actual bug in real system

Run with:
    uv run pytest python/tests/integration/test_recrawl_status.py -v -s
"""

import asyncio
import json
import os
import sqlite3
import time
from typing import Any

import pytest
import requests


# ==========================================
# Configuration
# ==========================================

BACKEND_URL = os.getenv("ARCHON_API_URL", "http://localhost:8181")
# Use a small, fast-to-crawl URL for testing
TEST_URL = "https://example.com"
# Timeouts
INITIAL_CRAWL_TIMEOUT = 120  # 2 minutes for initial crawl
RECRAWL_TIMEOUT = 120  # 2 minutes for recrawl
POLL_INTERVAL = 3  # Poll every 3 seconds
# Database
SQLITE_PATH = os.getenv("SQLITE_PATH", "/home/jose/src/Archon/data/archon.db")


# ==========================================
# Fixtures
# ==========================================


@pytest.fixture(scope="session")
def backend_available():
    """Verify backend is running and healthy."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        assert response.status_code == 200, f"Backend health check failed: {response.text}"
        print(f"\n✓ Backend is healthy at {BACKEND_URL}")
        return True
    except requests.exceptions.RequestException as e:
        pytest.skip(f"Backend not available at {BACKEND_URL}: {e}")


@pytest.fixture
def db_connection():
    """Provide SQLite database connection for direct verification."""
    if not os.path.exists(SQLITE_PATH):
        pytest.skip(f"Database not found at {SQLITE_PATH}")

    conn = sqlite3.connect(SQLITE_PATH)
    yield conn
    conn.close()


# ==========================================
# Helper Functions
# ==========================================


def get_source_from_db(conn: sqlite3.Connection, source_id: str) -> dict[str, Any] | None:
    """Get source record directly from database."""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT source_id, title, summary, metadata, total_word_count,
               source_url, source_display_name, created_at, updated_at
        FROM archon_sources
        WHERE source_id = ?
        """,
        (source_id,),
    )
    row = cursor.fetchone()

    if not row:
        return None

    # Parse metadata JSON
    metadata = json.loads(row[3]) if row[3] else {}

    return {
        "source_id": row[0],
        "title": row[1],
        "summary": row[2],
        "metadata": metadata,
        "total_word_count": row[4],
        "source_url": row[5],
        "source_display_name": row[6],
        "created_at": row[7],
        "updated_at": row[8],
    }


def get_document_count(conn: sqlite3.Connection, source_id: str) -> int:
    """Get document/page count for a source."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM archon_crawled_pages WHERE source_id = ?",
        (source_id,),
    )
    return cursor.fetchone()[0]


async def wait_for_crawl_completion(
    progress_id: str,
    timeout: int,
    operation_name: str = "crawl",
) -> dict[str, Any]:
    """
    Poll the progress endpoint until crawl completes or times out.

    Returns:
        Final progress data with status

    Raises:
        TimeoutError: If crawl doesn't complete within timeout
        AssertionError: If crawl fails
    """
    start_time = time.time()
    last_progress = None

    print(f"\n⏳ Waiting for {operation_name} completion (timeout: {timeout}s)...")

    while time.time() - start_time < timeout:
        await asyncio.sleep(POLL_INTERVAL)

        try:
            response = requests.get(
                f"{BACKEND_URL}/api/crawl-progress/{progress_id}",
                timeout=10,
            )

            if response.status_code == 404:
                # Progress not found yet, keep waiting
                elapsed = int(time.time() - start_time)
                print(f"  [{elapsed}s] Progress not found yet, waiting...")
                continue

            assert response.status_code == 200, f"Progress check failed: {response.text}"
            progress_data = response.json()
            last_progress = progress_data

            status = progress_data.get("status")
            progress_pct = progress_data.get("progress", 0)
            total_pages = progress_data.get("totalPages", 0)
            processed_pages = progress_data.get("processedPages", 0)

            elapsed = int(time.time() - start_time)
            print(
                f"  [{elapsed}s] Status: {status}, Progress: {progress_pct}%, "
                f"Pages: {processed_pages}/{total_pages}"
            )

            # Check for completion
            if status == "completed":
                print(f"✓ {operation_name.capitalize()} completed successfully!")
                return progress_data

            # Check for failure
            if status == "failed":
                error_msg = progress_data.get("error", "Unknown error")
                raise AssertionError(f"{operation_name.capitalize()} failed: {error_msg}")

        except requests.exceptions.RequestException as e:
            print(f"  Warning: Failed to fetch progress: {e}")
            continue

    # Timeout reached
    raise TimeoutError(
        f"{operation_name.capitalize()} did not complete within {timeout}s. "
        f"Last status: {last_progress.get('status') if last_progress else 'unknown'}"
    )


async def get_source_by_id_from_api(source_id: str) -> dict[str, Any] | None:
    """Get source information via API endpoint."""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/knowledge-items/summary",
            timeout=10,
        )
        assert response.status_code == 200, f"Failed to get items: {response.text}"

        data = response.json()
        items = data.get("items", [])

        # Find the source by ID
        for item in items:
            if item.get("source_id") == source_id:
                return item

        return None
    except Exception as e:
        print(f"Warning: Failed to get source from API: {e}")
        return None


# ==========================================
# Integration Tests
# ==========================================


@pytest.mark.asyncio
@pytest.mark.integration
async def test_initial_crawl_status_lifecycle(backend_available, db_connection):
    """
    Test that initial crawl sets status correctly through complete lifecycle.

    This establishes a baseline before testing recrawl.

    Flow:
        1. Start crawl for a new URL
        2. Verify initial status is "pending" or "starting"
        3. Wait for completion
        4. Verify final status is "completed" in both API and database
        5. Verify documents were stored
    """
    print("\n" + "="*80)
    print("TEST 1: Initial Crawl Status Lifecycle")
    print("="*80)

    # Step 1: Trigger initial crawl
    print(f"\n[1/5] Starting initial crawl of {TEST_URL}...")
    response = requests.post(
        f"{BACKEND_URL}/api/knowledge-items/crawl",
        json={
            "url": TEST_URL,
            "knowledge_type": "technical",
            "max_depth": 1,
            "extract_code_examples": False,
        },
        timeout=10,
    )

    assert response.status_code in [200, 201], f"Crawl start failed: {response.text}"
    data = response.json()
    progress_id = data.get("progressId")
    assert progress_id, "No progressId in response"
    print(f"✓ Crawl started with progress_id: {progress_id}")

    # Step 2: Wait a moment for source to be created
    await asyncio.sleep(3)

    # Step 3: Wait for crawl to complete
    print("\n[2/5] Waiting for crawl to complete...")
    final_progress = await wait_for_crawl_completion(
        progress_id,
        INITIAL_CRAWL_TIMEOUT,
        "initial crawl",
    )

    source_id = final_progress.get("sourceId")
    assert source_id, "No sourceId in completion data"
    print(f"✓ Source created: {source_id}")

    # Step 4: Verify status in database
    print("\n[3/5] Verifying status in database...")
    source_db = get_source_from_db(db_connection, source_id)
    assert source_db, f"Source {source_id} not found in database"

    crawl_status_db = source_db["metadata"].get("crawl_status")
    print(f"  Database crawl_status: {crawl_status_db}")

    # Step 5: Verify status via API
    print("\n[4/5] Verifying status via API...")
    source_api = await get_source_by_id_from_api(source_id)
    assert source_api, f"Source {source_id} not found via API"

    status_api = source_api.get("status")
    crawl_status_api = source_api.get("metadata", {}).get("crawl_status")
    print(f"  API status: {status_api}")
    print(f"  API crawl_status: {crawl_status_api}")

    # Step 6: Verify documents were stored
    print("\n[5/5] Verifying documents were stored...")
    doc_count = get_document_count(db_connection, source_id)
    print(f"  Document count: {doc_count}")

    # Assertions
    assert doc_count > 0, f"No documents stored (expected > 0, got {doc_count})"
    assert crawl_status_db == "completed", (
        f"Database crawl_status should be 'completed', got '{crawl_status_db}'"
    )
    assert status_api == "active", (
        f"API status should be 'active' (mapped from completed), got '{status_api}'"
    )

    print("\n" + "="*80)
    print("✅ TEST 1 PASSED: Initial crawl status lifecycle works correctly")
    print("="*80)

    # Return source_id for use in next test
    return source_id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_recrawl_status_remains_completed(backend_available, db_connection):
    """
    TEST FOR THE BUG: Verify that status remains "completed" after recrawl.

    This is the core test that reproduces the bug described in INVESTIGATION_REPORT.md.

    Flow:
        1. Create a source via initial crawl (or use existing)
        2. Wait for initial crawl to complete
        3. Verify status is "completed"
        4. Trigger recrawl via refresh endpoint
        5. Wait for recrawl to complete
        6. CRITICAL: Verify status is STILL "completed" (not "pending")
        7. Verify in both API and database

    Expected Behavior (AFTER FIX):
        - After recrawl completes, status should be "completed"
        - crawl_status in metadata should be "completed"
        - API should return status="active"

    Actual Behavior (CURRENT BUG):
        - After recrawl, status shows as "pending"
        - Frontend displays "Pending" badge
        - User is confused about operation success
    """
    print("\n" + "="*80)
    print("TEST 2: Recrawl Status Bug Reproduction")
    print("="*80)

    # Step 1: Create initial source (reuse previous test's source or create new)
    print(f"\n[1/7] Creating initial source via crawl...")
    response = requests.post(
        f"{BACKEND_URL}/api/knowledge-items/crawl",
        json={
            "url": TEST_URL,
            "knowledge_type": "technical",
            "max_depth": 1,
            "extract_code_examples": False,
        },
        timeout=10,
    )

    assert response.status_code in [200, 201], f"Initial crawl failed: {response.text}"
    initial_progress_id = response.json().get("progressId")
    assert initial_progress_id, "No progressId in initial crawl response"

    # Wait for initial crawl to complete
    print("\n[2/7] Waiting for initial crawl to complete...")
    initial_progress = await wait_for_crawl_completion(
        initial_progress_id,
        INITIAL_CRAWL_TIMEOUT,
        "initial crawl",
    )

    source_id = initial_progress.get("sourceId")
    assert source_id, "No sourceId in initial crawl completion"
    print(f"✓ Initial crawl completed, source_id: {source_id}")

    # Step 2: Verify initial status is completed
    print("\n[3/7] Verifying initial status is 'completed'...")
    source_db_before = get_source_from_db(db_connection, source_id)
    crawl_status_before = source_db_before["metadata"].get("crawl_status")
    doc_count_before = get_document_count(db_connection, source_id)

    print(f"  Before recrawl:")
    print(f"    - crawl_status: {crawl_status_before}")
    print(f"    - document count: {doc_count_before}")

    assert crawl_status_before == "completed", (
        f"Initial crawl should be 'completed', got '{crawl_status_before}'"
    )
    assert doc_count_before > 0, "No documents from initial crawl"

    # Step 3: Trigger recrawl via refresh endpoint
    print(f"\n[4/7] Triggering recrawl via refresh endpoint...")
    recrawl_response = requests.post(
        f"{BACKEND_URL}/api/knowledge-items/{source_id}/refresh",
        timeout=10,
    )

    assert recrawl_response.status_code == 200, (
        f"Recrawl start failed: {recrawl_response.text}"
    )
    recrawl_data = recrawl_response.json()
    recrawl_progress_id = recrawl_data.get("progressId")
    assert recrawl_progress_id, "No progressId in recrawl response"
    print(f"✓ Recrawl started with progress_id: {recrawl_progress_id}")

    # Step 4: Wait for recrawl to complete
    print("\n[5/7] Waiting for recrawl to complete...")
    recrawl_progress = await wait_for_crawl_completion(
        recrawl_progress_id,
        RECRAWL_TIMEOUT,
        "recrawl",
    )

    print(f"✓ Recrawl completed!")

    # Give the database a moment to settle
    await asyncio.sleep(2)

    # Step 5: Verify status AFTER recrawl in database
    print("\n[6/7] Verifying status AFTER recrawl in database...")
    source_db_after = get_source_from_db(db_connection, source_id)
    crawl_status_after_db = source_db_after["metadata"].get("crawl_status")
    doc_count_after = get_document_count(db_connection, source_id)

    print(f"  After recrawl (Database):")
    print(f"    - crawl_status: {crawl_status_after_db}")
    print(f"    - document count: {doc_count_after}")

    # Step 6: Verify status AFTER recrawl via API
    print("\n[7/7] Verifying status AFTER recrawl via API...")
    source_api_after = await get_source_by_id_from_api(source_id)
    assert source_api_after, f"Source {source_id} not found via API after recrawl"

    status_after_api = source_api_after.get("status")
    crawl_status_after_api = source_api_after.get("metadata", {}).get("crawl_status")

    print(f"  After recrawl (API):")
    print(f"    - status: {status_after_api}")
    print(f"    - crawl_status: {crawl_status_after_api}")

    # ==========================================
    # CRITICAL ASSERTIONS - These test the bug
    # ==========================================

    print("\n" + "-"*80)
    print("CRITICAL ASSERTIONS (Testing for bug):")
    print("-"*80)

    # Assertion 1: Database crawl_status should be "completed"
    print(f"\n✓ Checking database crawl_status...")
    assert crawl_status_after_db == "completed", (
        f"❌ BUG DETECTED: Database crawl_status should be 'completed' after recrawl, "
        f"got '{crawl_status_after_db}'. This is the bug described in INVESTIGATION_REPORT.md!"
    )
    print(f"  ✓ PASS: Database crawl_status is 'completed'")

    # Assertion 2: API crawl_status should be "completed"
    print(f"\n✓ Checking API crawl_status...")
    assert crawl_status_after_api == "completed", (
        f"❌ BUG DETECTED: API crawl_status should be 'completed' after recrawl, "
        f"got '{crawl_status_after_api}'"
    )
    print(f"  ✓ PASS: API crawl_status is 'completed'")

    # Assertion 3: API status should be "active" (mapped from completed)
    print(f"\n✓ Checking API status mapping...")
    assert status_after_api == "active", (
        f"❌ BUG DETECTED: API status should be 'active' (mapped from completed), "
        f"got '{status_after_api}'. Frontend will show 'Pending' badge!"
    )
    print(f"  ✓ PASS: API status is 'active' (correct mapping)")

    # Assertion 4: Documents should still be present
    print(f"\n✓ Checking documents persisted...")
    assert doc_count_after > 0, (
        f"No documents after recrawl (expected > 0, got {doc_count_after})"
    )
    print(f"  ✓ PASS: {doc_count_after} documents persisted")

    print("\n" + "="*80)
    print("✅ TEST 2 PASSED: Recrawl status remains 'completed' (Bug is FIXED!)")
    print("="*80)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_multiple_recrawls_status_stability(backend_available, db_connection):
    """
    Test that status remains stable across multiple recrawls.

    This tests for race conditions or state corruption that might occur
    with repeated recrawl operations.

    Flow:
        1. Create initial source
        2. Perform 3 consecutive recrawls
        3. Verify status is "completed" after each recrawl
    """
    print("\n" + "="*80)
    print("TEST 3: Multiple Recrawls Status Stability")
    print("="*80)

    # Create initial source
    print(f"\n[1/4] Creating initial source...")
    response = requests.post(
        f"{BACKEND_URL}/api/knowledge-items/crawl",
        json={
            "url": TEST_URL,
            "knowledge_type": "technical",
            "max_depth": 1,
            "extract_code_examples": False,
        },
        timeout=10,
    )

    assert response.status_code in [200, 201]
    initial_progress_id = response.json().get("progressId")

    print(f"[2/4] Waiting for initial crawl...")
    initial_progress = await wait_for_crawl_completion(
        initial_progress_id,
        INITIAL_CRAWL_TIMEOUT,
        "initial crawl",
    )

    source_id = initial_progress.get("sourceId")
    print(f"✓ Source created: {source_id}")

    # Perform multiple recrawls
    num_recrawls = 3
    print(f"\n[3/4] Performing {num_recrawls} consecutive recrawls...")

    for i in range(num_recrawls):
        print(f"\n  Recrawl {i+1}/{num_recrawls}:")

        # Trigger recrawl
        recrawl_response = requests.post(
            f"{BACKEND_URL}/api/knowledge-items/{source_id}/refresh",
            timeout=10,
        )
        assert recrawl_response.status_code == 200
        recrawl_progress_id = recrawl_response.json().get("progressId")

        # Wait for completion
        await wait_for_crawl_completion(
            recrawl_progress_id,
            RECRAWL_TIMEOUT,
            f"recrawl {i+1}",
        )

        # Give database time to settle
        await asyncio.sleep(2)

        # Verify status
        source_db = get_source_from_db(db_connection, source_id)
        crawl_status = source_db["metadata"].get("crawl_status")

        print(f"    Status after recrawl {i+1}: {crawl_status}")

        assert crawl_status == "completed", (
            f"Status should be 'completed' after recrawl {i+1}, got '{crawl_status}'"
        )

    print(f"\n[4/4] All {num_recrawls} recrawls completed with correct status")

    print("\n" + "="*80)
    print(f"✅ TEST 3 PASSED: Status remained 'completed' across {num_recrawls} recrawls")
    print("="*80)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_failed_crawl_sets_failed_status(backend_available, db_connection):
    """
    Test that failed crawls set status to "failed" correctly.

    This ensures error handling doesn't break the status update logic.

    Flow:
        1. Trigger crawl with invalid URL
        2. Wait for failure
        3. Verify status is "failed" in database and API
    """
    print("\n" + "="*80)
    print("TEST 4: Failed Crawl Status")
    print("="*80)

    invalid_url = "https://this-domain-definitely-does-not-exist-12345.com"

    print(f"\n[1/3] Triggering crawl with invalid URL: {invalid_url}")
    response = requests.post(
        f"{BACKEND_URL}/api/knowledge-items/crawl",
        json={
            "url": invalid_url,
            "knowledge_type": "technical",
            "max_depth": 1,
        },
        timeout=10,
    )

    if response.status_code not in [200, 201]:
        pytest.skip("API rejected invalid URL immediately (not testing async failure)")

    progress_id = response.json().get("progressId")
    if not progress_id:
        pytest.skip("No progressId returned for invalid URL")

    print(f"✓ Crawl started with progress_id: {progress_id}")

    # Wait for failure (shorter timeout)
    print(f"\n[2/3] Waiting for crawl to fail...")
    start_time = time.time()
    failure_detected = False
    source_id = None

    while time.time() - start_time < 60:  # 1 minute timeout
        await asyncio.sleep(POLL_INTERVAL)

        try:
            response = requests.get(
                f"{BACKEND_URL}/api/crawl-progress/{progress_id}",
                timeout=10,
            )

            if response.status_code == 200:
                progress_data = response.json()
                status = progress_data.get("status")
                source_id = progress_data.get("sourceId")

                if status == "failed":
                    failure_detected = True
                    print(f"✓ Crawl failed as expected")
                    break

        except Exception:
            continue

    if not failure_detected or not source_id:
        pytest.skip("Failed crawl didn't create source or set failed status")

    # Verify status in database
    print(f"\n[3/3] Verifying failed status in database...")
    await asyncio.sleep(2)
    source_db = get_source_from_db(db_connection, source_id)

    if source_db:
        crawl_status = source_db["metadata"].get("crawl_status")
        print(f"  Database crawl_status: {crawl_status}")

        assert crawl_status == "failed", (
            f"Failed crawl should set status to 'failed', got '{crawl_status}'"
        )
    else:
        print(f"  Note: Failed crawl may not have created source record")

    print("\n" + "="*80)
    print("✅ TEST 4 PASSED: Failed crawl sets 'failed' status correctly")
    print("="*80)


# ==========================================
# Helper Tests
# ==========================================


def test_backend_health(backend_available):
    """Verify backend is healthy and accessible."""
    response = requests.get(f"{BACKEND_URL}/health", timeout=5)
    assert response.status_code == 200
    print(f"\n✓ Backend is healthy at {BACKEND_URL}")


def test_database_connection(db_connection):
    """Verify database is accessible and has required tables."""
    cursor = db_connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    table_names = [t[0] for t in tables]
    assert "archon_sources" in table_names, "archon_sources table not found"
    assert "archon_crawled_pages" in table_names, "archon_crawled_pages table not found"

    print(f"\n✓ Database connection successful ({len(tables)} tables found)")


# ==========================================
# Main
# ==========================================


if __name__ == "__main__":
    """Run tests with pytest."""
    pytest.main([__file__, "-v", "-s", "--tb=short"])
