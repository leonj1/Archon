"""
Example tests for KnowledgeItemService using FakeDatabaseRepository

This is a simplified example showing how to test the KnowledgeItemService.
Note: The actual service still has some Supabase dependencies that need refactoring,
but this demonstrates the pattern for testing with FakeDatabaseRepository.
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
# BASIC SOURCE OPERATIONS
# ========================================================================


@pytest.mark.asyncio
async def test_get_available_sources_empty(knowledge_service):
    """Test getting available sources when there are none."""
    result = await knowledge_service.get_available_sources()

    assert result["success"] is True
    assert result["sources"] == []
    assert result["count"] == 0


@pytest.mark.asyncio
async def test_get_available_sources_with_data(knowledge_service, repository):
    """Test getting available sources with data."""
    # Pre-populate sources in repository
    await repository.upsert_source({
        "source_id": "source-1",
        "title": "Python Documentation",
        "summary": "Official Python docs",
        "metadata": {"knowledge_type": "technical"},
        "total_words": 50000,
        "update_frequency": 7
    })

    await repository.upsert_source({
        "source_id": "source-2",
        "title": "Django Tutorial",
        "summary": "Web framework guide",
        "metadata": {"knowledge_type": "technical"},
        "total_words": 30000,
        "update_frequency": 30
    })

    # Get sources
    result = await knowledge_service.get_available_sources()

    assert result["success"] is True
    assert len(result["sources"]) == 2
    assert result["count"] == 2

    # Check source structure
    source_titles = [s["title"] for s in result["sources"]]
    assert "Python Documentation" in source_titles
    assert "Django Tutorial" in source_titles


@pytest.mark.asyncio
async def test_source_with_metadata(knowledge_service, repository):
    """Test that source metadata is properly retrieved."""
    # Create source with metadata
    await repository.upsert_source({
        "source_id": "test-source",
        "title": "Test Documentation",
        "summary": "A test source",
        "metadata": {
            "knowledge_type": "business",
            "tags": ["test", "documentation"],
            "custom_field": "custom_value"
        },
        "total_words": 10000,
        "update_frequency": 14
    })

    # Get sources
    result = await knowledge_service.get_available_sources()

    assert result["success"] is True
    source = result["sources"][0]

    assert source["source_id"] == "test-source"
    assert source["title"] == "Test Documentation"
    assert source["metadata"]["knowledge_type"] == "business"
    assert "test" in source["metadata"]["tags"]
    assert source["update_frequency"] == 14


# ========================================================================
# SOURCE TYPE DETERMINATION TESTS
# ========================================================================


def test_determine_source_type_from_metadata(knowledge_service):
    """Test source type determination from metadata."""
    metadata = {"source_type": "documentation"}
    url = "https://example.com/docs"

    source_type = knowledge_service._determine_source_type(metadata, url)

    assert source_type == "documentation"


def test_determine_source_type_from_file_url(knowledge_service):
    """Test source type determination from file:// URL."""
    metadata = {}
    url = "file:///path/to/document.pdf"

    source_type = knowledge_service._determine_source_type(metadata, url)

    assert source_type == "file"


def test_determine_source_type_from_http_url(knowledge_service):
    """Test source type determination from HTTP URL."""
    metadata = {}
    url = "https://docs.python.org"

    source_type = knowledge_service._determine_source_type(metadata, url)

    assert source_type == "url"


# ========================================================================
# UPDATE ITEM TESTS (Limited - needs service refactoring)
# ========================================================================


@pytest.mark.asyncio
@pytest.mark.skip(reason="Service still uses direct Supabase calls - needs refactoring")
async def test_update_item_title(knowledge_service, repository):
    """
    Test updating a knowledge item's title.

    Note: This test is skipped because the service still uses direct Supabase
    calls. Once the service is fully refactored to use the repository pattern,
    this test can be enabled.
    """
    # Create source
    await repository.upsert_source({
        "source_id": "test-source",
        "title": "Old Title",
        "metadata": {}
    })

    # Update title
    success, result = await knowledge_service.update_item(
        source_id="test-source",
        updates={"title": "New Title"}
    )

    assert success
    assert result["source_id"] == "test-source"

    # Verify update
    source = await repository.get_source_by_id("test-source")
    assert source["title"] == "New Title"


# ========================================================================
# FILTER TESTS
# ========================================================================


def test_filter_by_search(knowledge_service):
    """Test filtering items by search term."""
    items = [
        {
            "title": "Python Documentation",
            "metadata": {
                "description": "Official Python docs",
                "tags": ["python", "programming"]
            }
        },
        {
            "title": "Django Tutorial",
            "metadata": {
                "description": "Web framework guide",
                "tags": ["django", "web"]
            }
        },
        {
            "title": "Flask Guide",
            "metadata": {
                "description": "Lightweight Python framework",
                "tags": ["flask", "python"]
            }
        }
    ]

    # Search for "python"
    filtered = knowledge_service._filter_by_search(items, "python")

    assert len(filtered) == 2
    titles = [item["title"] for item in filtered]
    assert "Python Documentation" in titles
    assert "Flask Guide" in titles


def test_filter_by_knowledge_type(knowledge_service):
    """Test filtering items by knowledge type."""
    items = [
        {
            "title": "Technical Doc",
            "metadata": {"knowledge_type": "technical"}
        },
        {
            "title": "Business Doc",
            "metadata": {"knowledge_type": "business"}
        },
        {
            "title": "Another Technical",
            "metadata": {"knowledge_type": "technical"}
        }
    ]

    # Filter for technical
    filtered = knowledge_service._filter_by_knowledge_type(items, "technical")

    assert len(filtered) == 2
    for item in filtered:
        assert item["metadata"]["knowledge_type"] == "technical"


# ========================================================================
# NOTES FOR FUTURE REFACTORING
# ========================================================================


"""
TODO: Once KnowledgeItemService is fully refactored to use repository pattern:

1. Add tests for list_items() with pagination
2. Add tests for get_item() by source_id
3. Add tests for update_item() metadata updates
4. Add tests for delete operations (if implemented)
5. Add tests for document chunks retrieval
6. Add tests for code examples retrieval

Current blockers:
- list_items() still uses self.supabase directly for queries
- get_item() uses self.supabase for fetching data
- update_item() uses self.supabase.table() calls

Once these are refactored to use self.repository methods, tests can be
written following the same pattern as TaskService and ProjectService tests.
"""
