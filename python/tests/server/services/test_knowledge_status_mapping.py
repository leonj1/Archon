"""
Tests for Knowledge Item Status Mapping

Validates that crawl_status correctly maps to frontend status when:
- A crawl is initiated (pending → processing)
- A crawl completes successfully (completed → active)
- A crawl fails (failed → error)
"""

import pytest

from src.server.repositories import FakeDatabaseRepository
from src.server.services.knowledge.knowledge_item_service import KnowledgeItemService


@pytest.fixture
def repository():
    """Create a fresh in-memory repository for each test."""
    return FakeDatabaseRepository()


@pytest.fixture
def knowledge_service(repository):
    """Create a KnowledgeItemService with the fake repository."""
    return KnowledgeItemService(repository=repository)


# ========================================================================
# STATUS MAPPING TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_pending_crawl_status_maps_to_processing(knowledge_service, repository):
    """
    Test that crawl_status='pending' maps to status='processing'.

    This represents a source that has been added but not yet crawled.
    """
    # Create source with pending crawl status
    await repository.upsert_source({
        "source_id": "test-pending-source",
        "title": "Test Pending Source",
        "summary": "A source waiting to be crawled",
        "source_url": "https://example.com/docs",
        "metadata": {
            "knowledge_type": "technical",
            "crawl_status": "pending",
            "tags": ["test"]
        },
        "total_word_count": 0,
    })

    # Get the item via list_items (which includes status mapping)
    result = await knowledge_service.list_items(page=1, per_page=10)

    assert len(result["items"]) == 1
    item = result["items"][0]

    # Verify top-level status field
    assert item["status"] == "processing", \
        "crawl_status='pending' should map to status='processing'"

    # Verify metadata also has correct status
    assert item["metadata"]["status"] == "processing"
    assert item["metadata"]["crawl_status"] == "pending"


@pytest.mark.asyncio
async def test_completed_crawl_status_maps_to_active(knowledge_service, repository):
    """
    Test that crawl_status='completed' maps to status='active'.

    This represents a source that has been successfully crawled.
    """
    # Create source with completed crawl status
    await repository.upsert_source({
        "source_id": "test-completed-source",
        "title": "Test Completed Source",
        "summary": "A successfully crawled source",
        "source_url": "https://example.com/docs",
        "metadata": {
            "knowledge_type": "technical",
            "crawl_status": "completed",
            "tags": ["test"]
        },
        "total_word_count": 5000,
    })

    # Add some crawled pages to simulate actual content
    await repository.insert_crawled_page({
        "source_id": "test-completed-source",
        "url": "https://example.com/docs/page1",
        "content": "Page content",
        "metadata": {}
    })

    # Get the item
    result = await knowledge_service.list_items(page=1, per_page=10)

    assert len(result["items"]) == 1
    item = result["items"][0]

    # Verify top-level status field
    assert item["status"] == "active", \
        "crawl_status='completed' should map to status='active'"

    # Verify metadata
    assert item["metadata"]["status"] == "active"
    assert item["metadata"]["crawl_status"] == "completed"
    assert item["document_count"] > 0, "Completed source should have documents"


@pytest.mark.asyncio
async def test_failed_crawl_status_maps_to_error(knowledge_service, repository):
    """
    Test that crawl_status='failed' maps to status='error'.

    This represents a source where crawling encountered an error.
    """
    # Create source with failed crawl status
    await repository.upsert_source({
        "source_id": "test-failed-source",
        "title": "Test Failed Source",
        "summary": "A source that failed to crawl",
        "source_url": "https://example.com/broken",
        "metadata": {
            "knowledge_type": "technical",
            "crawl_status": "failed",
            "error_message": "Connection timeout",
            "tags": ["test"]
        },
        "total_word_count": 0,
    })

    # Get the item
    result = await knowledge_service.list_items(page=1, per_page=10)

    assert len(result["items"]) == 1
    item = result["items"][0]

    # Verify top-level status field
    assert item["status"] == "error", \
        "crawl_status='failed' should map to status='error'"

    # Verify metadata
    assert item["metadata"]["status"] == "error"
    assert item["metadata"]["crawl_status"] == "failed"
    assert item["document_count"] == 0, "Failed source should have no documents"


@pytest.mark.asyncio
async def test_missing_crawl_status_defaults_to_processing(knowledge_service, repository):
    """
    Test that missing crawl_status defaults to status='processing'.

    For backward compatibility with sources that don't have crawl_status set.
    """
    # Create source without crawl_status
    await repository.upsert_source({
        "source_id": "test-legacy-source",
        "title": "Test Legacy Source",
        "summary": "A source without crawl_status",
        "source_url": "https://example.com/legacy",
        "metadata": {
            "knowledge_type": "technical",
            "tags": ["test"]
            # Note: no crawl_status field
        },
        "total_word_count": 0,
    })

    # Get the item
    result = await knowledge_service.list_items(page=1, per_page=10)

    assert len(result["items"]) == 1
    item = result["items"][0]

    # Verify it defaults to processing
    assert item["status"] == "processing", \
        "Missing crawl_status should default to status='processing'"

    # Verify metadata has the default
    assert item["metadata"]["status"] == "processing"
    assert item["metadata"]["crawl_status"] == "pending"


# ========================================================================
# STATUS UPDATE LIFECYCLE TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_status_update_lifecycle_pending_to_completed(knowledge_service, repository):
    """
    Test the complete lifecycle: pending → processing → completed → active.

    Simulates:
    1. Creating a source (crawl_status: pending)
    2. Starting a crawl (still pending)
    3. Completing the crawl (crawl_status: completed)
    4. Verifying status changes to active
    """
    source_id = "test-lifecycle-source"

    # Step 1: Create source with pending status
    await repository.upsert_source({
        "source_id": source_id,
        "title": "Lifecycle Test Source",
        "summary": "Testing status lifecycle",
        "source_url": "https://example.com/lifecycle",
        "metadata": {
            "knowledge_type": "technical",
            "crawl_status": "pending"
        },
        "total_word_count": 0,
    })

    # Verify initial state: pending → processing
    result = await knowledge_service.list_items()
    item = result["items"][0]
    assert item["status"] == "processing"
    assert item["metadata"]["crawl_status"] == "pending"

    # Step 2: Simulate crawl completion - update crawl_status
    await repository.upsert_source({
        "source_id": source_id,
        "title": "Lifecycle Test Source",
        "summary": "Testing status lifecycle",
        "source_url": "https://example.com/lifecycle",
        "metadata": {
            "knowledge_type": "technical",
            "crawl_status": "completed"  # Updated!
        },
        "total_word_count": 10000,
    })

    # Add crawled content
    await repository.insert_crawled_page({
        "source_id": source_id,
        "url": "https://example.com/lifecycle/page1",
        "content": "Page content here",
        "metadata": {}
    })

    # Step 3: Verify final state: completed → active
    result = await knowledge_service.list_items()
    item = result["items"][0]

    assert item["status"] == "active", \
        "After crawl completion, status should be 'active'"
    assert item["metadata"]["crawl_status"] == "completed"
    assert item["document_count"] > 0
    assert item["metadata"]["word_count"] == 10000


@pytest.mark.asyncio
async def test_status_update_lifecycle_pending_to_failed(knowledge_service, repository):
    """
    Test the failure lifecycle: pending → processing → failed → error.

    Simulates:
    1. Creating a source (crawl_status: pending)
    2. Crawl fails (crawl_status: failed)
    3. Verifying status changes to error
    """
    source_id = "test-failure-source"

    # Step 1: Create source with pending status
    await repository.upsert_source({
        "source_id": source_id,
        "title": "Failure Test Source",
        "summary": "Testing failure lifecycle",
        "source_url": "https://example.com/broken",
        "metadata": {
            "knowledge_type": "technical",
            "crawl_status": "pending"
        },
        "total_word_count": 0,
    })

    # Verify initial state
    result = await knowledge_service.list_items()
    item = result["items"][0]
    assert item["status"] == "processing"

    # Step 2: Simulate crawl failure
    await repository.upsert_source({
        "source_id": source_id,
        "title": "Failure Test Source",
        "summary": "Testing failure lifecycle",
        "source_url": "https://example.com/broken",
        "metadata": {
            "knowledge_type": "technical",
            "crawl_status": "failed",  # Failed!
            "error_message": "404 Not Found"
        },
        "total_word_count": 0,
    })

    # Step 3: Verify error state
    result = await knowledge_service.list_items()
    item = result["items"][0]

    assert item["status"] == "error", \
        "After crawl failure, status should be 'error'"
    assert item["metadata"]["crawl_status"] == "failed"
    assert item["document_count"] == 0


# ========================================================================
# MULTIPLE SOURCES WITH DIFFERENT STATUSES
# ========================================================================


@pytest.mark.asyncio
async def test_multiple_sources_different_statuses(knowledge_service, repository):
    """
    Test that multiple sources with different crawl_status values
    all get correctly mapped to their respective status values.
    """
    # Create sources with different statuses
    sources = [
        {
            "source_id": "source-pending",
            "title": "Pending Source",
            "metadata": {"crawl_status": "pending"},
            "total_word_count": 0,
        },
        {
            "source_id": "source-completed",
            "title": "Completed Source",
            "metadata": {"crawl_status": "completed"},
            "total_word_count": 5000,
        },
        {
            "source_id": "source-failed",
            "title": "Failed Source",
            "metadata": {"crawl_status": "failed"},
            "total_word_count": 0,
        },
    ]

    for source_data in sources:
        await repository.upsert_source({
            **source_data,
            "summary": f"Test {source_data['title']}",
            "source_url": f"https://example.com/{source_data['source_id']}",
        })

    # Add a page for the completed source
    await repository.insert_crawled_page({
        "source_id": "source-completed",
        "url": "https://example.com/page1",
        "content": "Content",
        "metadata": {}
    })

    # Get all items
    result = await knowledge_service.list_items(per_page=10)

    assert len(result["items"]) == 3

    # Find each source and verify status mapping
    items_by_id = {item["source_id"]: item for item in result["items"]}

    # Pending source
    pending = items_by_id["source-pending"]
    assert pending["status"] == "processing"
    assert pending["metadata"]["crawl_status"] == "pending"

    # Completed source
    completed = items_by_id["source-completed"]
    assert completed["status"] == "active"
    assert completed["metadata"]["crawl_status"] == "completed"
    assert completed["document_count"] > 0

    # Failed source
    failed = items_by_id["source-failed"]
    assert failed["status"] == "error"
    assert failed["metadata"]["crawl_status"] == "failed"
    assert failed["document_count"] == 0


# ========================================================================
# GET SINGLE ITEM STATUS MAPPING
# ========================================================================


@pytest.mark.asyncio
async def test_get_item_returns_correct_status(knowledge_service, repository):
    """
    Test that get_item() (single item retrieval) also correctly maps status.
    """
    # Create a completed source
    await repository.upsert_source({
        "source_id": "single-item-test",
        "title": "Single Item Test",
        "summary": "Test single item retrieval",
        "source_url": "https://example.com/single",
        "metadata": {
            "knowledge_type": "technical",
            "crawl_status": "completed"
        },
        "total_word_count": 3000,
    })

    # Add a page
    await repository.insert_crawled_page({
        "source_id": "single-item-test",
        "url": "https://example.com/single/page1",
        "content": "Page content",
        "metadata": {}
    })

    # Get single item
    item = await knowledge_service.get_item("single-item-test")

    assert item is not None
    assert item["status"] == "active", \
        "get_item() should also map crawl_status to status"
    assert item["metadata"]["crawl_status"] == "completed"
    assert item["document_count"] > 0


# ========================================================================
# UPDATE ITEM STATUS TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_update_item_can_change_crawl_status(knowledge_service, repository):
    """
    Test that update_item() can update crawl_status and the status mapping
    reflects the change.
    """
    # Create a pending source
    await repository.upsert_source({
        "source_id": "update-status-test",
        "title": "Update Status Test",
        "summary": "Test status updates",
        "source_url": "https://example.com/update",
        "metadata": {
            "knowledge_type": "technical",
            "crawl_status": "pending"
        },
        "total_word_count": 0,
    })

    # Verify initial state
    result = await knowledge_service.list_items()
    item = result["items"][0]
    assert item["status"] == "processing"

    # Update crawl_status to completed
    success, update_result = await knowledge_service.update_item(
        source_id="update-status-test",
        updates={"crawl_status": "completed"}
    )

    assert success, "Update should succeed"

    # Verify updated state
    result = await knowledge_service.list_items()
    item = result["items"][0]

    assert item["status"] == "active", \
        "After updating crawl_status to 'completed', status should be 'active'"
    assert item["metadata"]["crawl_status"] == "completed"


@pytest.mark.asyncio
async def test_update_item_can_mark_as_failed(knowledge_service, repository):
    """
    Test that update_item() can mark a source as failed.
    """
    # Create a pending source
    await repository.upsert_source({
        "source_id": "mark-failed-test",
        "title": "Mark Failed Test",
        "summary": "Test failure marking",
        "source_url": "https://example.com/fail",
        "metadata": {
            "knowledge_type": "technical",
            "crawl_status": "pending"
        },
        "total_word_count": 0,
    })

    # Mark as failed
    success, update_result = await knowledge_service.update_item(
        source_id="mark-failed-test",
        updates={
            "crawl_status": "failed",
            "description": "Crawl failed due to network error"
        }
    )

    assert success

    # Verify error state
    result = await knowledge_service.list_items()
    item = result["items"][0]

    assert item["status"] == "error"
    assert item["metadata"]["crawl_status"] == "failed"
    assert "failed" in item["metadata"]["description"].lower()
