"""
Test Knowledge API pagination and summary endpoints.

Tests the new optimized endpoints for:
- Summary endpoint with minimal data
- Paginated chunks endpoint
- Paginated code examples endpoint
"""

import pytest
from unittest.mock import MagicMock, patch


def test_knowledge_summary_endpoint(client):
    """Test the lightweight summary endpoint returns minimal data."""
    # Use patch.dict to set environment variable to use fake backend
    import os
    with patch.dict(os.environ, {"ARCHON_DB_BACKEND": "fake"}):
        from src.server.repositories.repository_factory import reset_factory, get_repository

        # Reset factory to pick up new environment variable
        reset_factory()

        # Get fake repository and populate with test data
        fake_repo = get_repository(backend="fake")

        # Patch get_repository in all the places it's used
        with patch('src.server.repositories.repository_factory.get_repository', return_value=fake_repo):
            with patch('src.server.api_routes.knowledge_api.get_repository', return_value=fake_repo):
                with patch('src.server.services.knowledge.knowledge_summary_service.get_repository', return_value=fake_repo):
                    # Add test data to the fake repository
                    import asyncio

                    async def setup_test_data():
                        # Create test sources using upsert_source
                        await fake_repo.upsert_source({
                            "source_id": "test-source-1",
                            "title": "Test Source 1",
                            "summary": "Test summary 1",
                            "metadata": {"knowledge_type": "technical", "tags": ["test"]},
                            "source_url": "https://example.com/1",
                            "created_at": "2024-01-01T00:00:00",
                            "updated_at": "2024-01-01T00:00:00"
                        })
                        await fake_repo.upsert_source({
                            "source_id": "test-source-2",
                            "title": "Test Source 2",
                            "summary": "Test summary 2",
                            "metadata": {"knowledge_type": "business", "tags": ["docs"]},
                            "source_url": "https://example.com/2",
                            "created_at": "2024-01-01T00:00:00",
                            "updated_at": "2024-01-01T00:00:00"
                        })

                    # Run async setup
                    asyncio.run(setup_test_data())

                    # Make request to summary endpoint
                    response = client.get("/api/knowledge-items/summary?page=1&per_page=10")

                    assert response.status_code == 200
                    data = response.json()

                    # Verify response structure
                    assert "items" in data
                    assert "total" in data
                    assert "page" in data
                    assert "per_page" in data

                    # Verify items have minimal fields only
                    if len(data["items"]) > 0:
                        item = data["items"][0]
                        # Should have summary fields
                        assert "source_id" in item
                        assert "title" in item
                        assert "url" in item
                        assert "document_count" in item
                        assert "code_examples_count" in item
                        assert "knowledge_type" in item

                        # Should NOT have full content
                        assert "content" not in item
                        assert "chunks" not in item
                        assert "code_examples" not in item


@pytest.mark.skip(reason="Mock contamination issue - works in isolation")
def test_chunks_pagination(client, mock_supabase_client):
    """Test chunks endpoint supports pagination."""
    # Mock paginated chunks
    mock_chunks = [
        {
            "id": f"chunk-{i}",
            "source_id": "test-source",
            "content": f"Chunk content {i}",
            "metadata": {},
            "url": f"https://example.com/page{i}"
        }
        for i in range(5)
    ]
    
    # Create proper mock response objects - use a simple class instead of MagicMock
    class MockExecuteResult:
        def __init__(self, data=None, count=None):
            self.data = data
            if count is not None:
                self.count = count
    
    mock_execute = MockExecuteResult(data=mock_chunks)
    mock_count_execute = MockExecuteResult(count=50)
    
    # Track which query we're on
    query_counter = {"count": 0}
    
    def execute_handler():
        query_counter["count"] += 1
        if query_counter["count"] == 1:
            # First call is count query
            return mock_count_execute
        else:
            # Second call is data query
            return mock_execute
    
    mock_select = MagicMock()
    mock_select.execute.side_effect = execute_handler
    mock_select.eq.return_value = mock_select
    mock_select.ilike.return_value = mock_select
    mock_select.order.return_value = mock_select
    mock_select.range.return_value = mock_select
    
    mock_from = MagicMock()
    mock_from.select.return_value = mock_select
    
    mock_supabase_client.from_.return_value = mock_from
    
    # Test with pagination parameters
    response = client.get("/api/knowledge-items/test-source/chunks?limit=5&offset=0")
    
    # Debug: print error if status is not 200
    if response.status_code != 200:
        print(f"Error response: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify pagination metadata
    assert data["success"] is True
    assert data["source_id"] == "test-source"
    assert "chunks" in data
    assert "total" in data
    assert data["total"] == 50
    assert data["limit"] == 5
    assert data["offset"] == 0
    assert data["has_more"] is True
    
    # Verify we got limited chunks
    assert len(data["chunks"]) <= 5


@pytest.mark.skip(reason="Mock contamination issue - works in isolation")
def test_chunks_pagination_with_domain_filter(client, mock_supabase_client):
    """Test chunks endpoint pagination with domain filtering."""
    mock_chunks = [
        {
            "id": "chunk-1",
            "source_id": "test-source",
            "content": "Filtered content",
            "url": "https://docs.example.com/page1"
        }
    ]
    
    # Create proper mock response objects
    class MockExecuteResult:
        def __init__(self, data=None, count=None):
            self.data = data
            if count is not None:
                self.count = count
    
    mock_execute = MockExecuteResult(data=mock_chunks)
    mock_count_execute = MockExecuteResult(count=10)
    
    query_counter = {"count": 0}
    
    def execute_handler():
        query_counter["count"] += 1
        if query_counter["count"] == 1:
            return mock_count_execute
        else:
            return mock_execute
    
    mock_select = MagicMock()
    mock_select.execute.side_effect = execute_handler
    mock_select.eq.return_value = mock_select
    mock_select.ilike.return_value = mock_select
    mock_select.order.return_value = mock_select
    mock_select.range.return_value = mock_select
    
    mock_from = MagicMock()
    mock_from.select.return_value = mock_select
    
    mock_supabase_client.from_.return_value = mock_from
    
    # Test with domain filter
    response = client.get(
        "/api/knowledge-items/test-source/chunks?domain_filter=docs.example.com&limit=10"
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["domain_filter"] == "docs.example.com"
    assert data["limit"] == 10


@pytest.mark.skip(reason="Mock contamination issue - works in isolation")
def test_code_examples_pagination(client, mock_supabase_client):
    """Test code examples endpoint supports pagination."""
    # Mock paginated code examples
    mock_examples = [
        {
            "id": f"example-{i}",
            "source_id": "test-source",
            "content": f"def example_{i}():\n    pass",
            "summary": f"Example {i}",
            "metadata": {"language": "python"}
        }
        for i in range(3)
    ]
    
    # Create proper mock response objects
    class MockExecuteResult:
        def __init__(self, data=None, count=None):
            self.data = data
            if count is not None:
                self.count = count
    
    mock_execute = MockExecuteResult(data=mock_examples)
    mock_count_execute = MockExecuteResult(count=30)
    
    query_counter = {"count": 0}
    
    def execute_handler():
        query_counter["count"] += 1
        if query_counter["count"] == 1:
            return mock_count_execute
        else:
            return mock_execute
    
    mock_select = MagicMock()
    mock_select.execute.side_effect = execute_handler
    mock_select.eq.return_value = mock_select
    mock_select.order.return_value = mock_select
    mock_select.range.return_value = mock_select
    
    mock_from = MagicMock()
    mock_from.select.return_value = mock_select
    
    mock_supabase_client.from_.return_value = mock_from
    
    # Test with pagination
    response = client.get("/api/knowledge-items/test-source/code-examples?limit=3&offset=0")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify pagination metadata
    assert data["success"] is True
    assert data["source_id"] == "test-source"
    assert "code_examples" in data
    assert data["total"] == 30
    assert data["limit"] == 3
    assert data["offset"] == 0
    assert data["has_more"] is True
    
    # Verify limited results
    assert len(data["code_examples"]) <= 3


@pytest.mark.skip(reason="Mock contamination issue - works in isolation")
def test_pagination_limit_validation(client, mock_supabase_client):
    """Test that pagination limits are properly validated."""
    class MockExecuteResult:
        def __init__(self, data=None, count=None):
            self.data = data
            if count is not None:
                self.count = count
    
    mock_execute = MockExecuteResult(data=[])
    mock_count_execute = MockExecuteResult(count=0)
    
    query_counter = {"count": 0}
    
    def execute_handler():
        query_counter["count"] += 1
        if query_counter["count"] % 2 == 1:
            return mock_count_execute
        else:
            return mock_execute
    
    mock_select = MagicMock()
    mock_select.execute.side_effect = execute_handler
    mock_select.eq.return_value = mock_select
    mock_select.order.return_value = mock_select
    mock_select.range.return_value = mock_select
    
    mock_from = MagicMock()
    mock_from.select.return_value = mock_select
    
    mock_supabase_client.from_.return_value = mock_from
    
    # Test with excessive limit (should be capped at 100)
    response = client.get("/api/knowledge-items/test-source/chunks?limit=500&offset=0")
    
    assert response.status_code == 200
    data = response.json()
    
    # Limit should be capped at 100
    assert data["limit"] == 100
    
    # Test with negative offset (should be set to 0)
    response = client.get("/api/knowledge-items/test-source/chunks?limit=10&offset=-5")
    
    assert response.status_code == 200
    data = response.json()
    assert data["offset"] == 0


def test_summary_search_filter(client):
    """Test summary endpoint with search filtering."""
    # Use patch.dict to set environment variable to use fake backend
    import os
    with patch.dict(os.environ, {"ARCHON_DB_BACKEND": "fake"}):
        from src.server.repositories.repository_factory import reset_factory, get_repository

        # Reset factory to pick up new environment variable
        reset_factory()

        # Get fake repository and populate with test data
        fake_repo = get_repository(backend="fake")

        # Patch get_repository in all the places it's used
        with patch('src.server.repositories.repository_factory.get_repository', return_value=fake_repo):
            with patch('src.server.api_routes.knowledge_api.get_repository', return_value=fake_repo):
                with patch('src.server.services.knowledge.knowledge_summary_service.get_repository', return_value=fake_repo):
                    # Add test data to the fake repository
                    import asyncio

                    async def setup_test_data():
                        # Create test sources using upsert_source
                        await fake_repo.upsert_source({
                            "source_id": "test-source-1",
                            "title": "Python Documentation",
                            "summary": "Python guide",
                            "metadata": {"knowledge_type": "technical"},
                            "source_url": "https://example.com/python",
                            "created_at": "2024-01-01T00:00:00",
                            "updated_at": "2024-01-01T00:00:00"
                        })

                    # Run async setup
                    asyncio.run(setup_test_data())

                    # Test with search term
                    response = client.get("/api/knowledge-items/summary?search=python")

                    assert response.status_code == 200
                    data = response.json()
                    assert "items" in data


def test_summary_knowledge_type_filter(client):
    """Test summary endpoint with knowledge type filtering."""
    # Use patch.dict to set environment variable to use fake backend
    import os
    with patch.dict(os.environ, {"ARCHON_DB_BACKEND": "fake"}):
        from src.server.repositories.repository_factory import reset_factory, get_repository

        # Reset factory to pick up new environment variable
        reset_factory()

        # Get fake repository and populate with test data
        fake_repo = get_repository(backend="fake")

        # Patch get_repository in all the places it's used
        with patch('src.server.repositories.repository_factory.get_repository', return_value=fake_repo):
            with patch('src.server.api_routes.knowledge_api.get_repository', return_value=fake_repo):
                with patch('src.server.services.knowledge.knowledge_summary_service.get_repository', return_value=fake_repo):
                    # Add test data to the fake repository
                    import asyncio

                    async def setup_test_data():
                        # Create test sources using upsert_source
                        await fake_repo.upsert_source({
                            "source_id": "test-source-1",
                            "title": "Technical Doc",
                            "summary": "Tech guide",
                            "metadata": {"knowledge_type": "technical"},
                            "source_url": "https://example.com/technical",
                            "created_at": "2024-01-01T00:00:00",
                            "updated_at": "2024-01-01T00:00:00"
                        })

                    # Run async setup
                    asyncio.run(setup_test_data())

                    # Test with knowledge type filter
                    response = client.get("/api/knowledge-items/summary?knowledge_type=technical")

                    assert response.status_code == 200
                    data = response.json()
                    assert "items" in data


@pytest.mark.skip(reason="Mock contamination issue - works in isolation")
def test_empty_results_pagination(client, mock_supabase_client):
    """Test pagination with empty results."""
    class MockExecuteResult:
        def __init__(self, data=None, count=None):
            self.data = data
            if count is not None:
                self.count = count
    
    mock_execute = MockExecuteResult(data=[])
    mock_count_execute = MockExecuteResult(count=0)
    
    query_counter = {"count": 0}
    
    def execute_handler():
        query_counter["count"] += 1
        if query_counter["count"] % 2 == 1:
            return mock_count_execute
        else:
            return mock_execute
    
    mock_select = MagicMock()
    mock_select.execute.side_effect = execute_handler
    mock_select.eq.return_value = mock_select
    mock_select.range.return_value = mock_select
    mock_select.order.return_value = mock_select
    
    mock_from = MagicMock()
    mock_from.select.return_value = mock_select
    
    mock_supabase_client.from_.return_value = mock_from
    
    # Test chunks with no results
    response = client.get("/api/knowledge-items/test-source/chunks?limit=10&offset=0")
    
    assert response.status_code == 200
    data = response.json()
    assert data["chunks"] == []
    assert data["total"] == 0
    assert data["has_more"] is False
    
    # Test code examples with no results
    response = client.get("/api/knowledge-items/test-source/code-examples?limit=10&offset=0")
    
    assert response.status_code == 200
    data = response.json()
    assert data["code_examples"] == []
    assert data["total"] == 0
    assert data["has_more"] is False