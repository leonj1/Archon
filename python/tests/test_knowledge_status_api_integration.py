"""
Integration tests for Knowledge Status API Endpoint.

These tests validate that the /api/knowledge-items endpoint returns the correct
top-level status field that the UI expects. This complements the service-layer
tests in test_knowledge_status_mapping.py by testing the full HTTP request/response cycle.

The critical requirement: The UI needs top-level `status` field with correct values:
- crawl_status="pending" → status="processing"
- crawl_status="completed" → status="active"
- crawl_status="failed" → status="error"

Bug fixed: Previously the API returned status=null at top level, causing UI to show
"Completed" for all sources. Now the top-level status field is correctly populated.
"""

import pytest
from unittest.mock import MagicMock


class TestKnowledgeStatusAPIEndpoint:
    """Tests for the /api/knowledge-items endpoint status field."""

    def test_api_returns_top_level_status_for_pending(self, client, mock_supabase_client):
        """
        Test that API returns top-level status='processing' for pending sources.

        This is the critical bug fix test: Previously API returned status=null,
        causing UI to show incorrect "Completed" badge for pending sources.
        """
        # Mock the sources table to return a pending source
        mock_sources_data = [{
            "source_id": "test-pending",
            "title": "Pending Source",
            "summary": "Test pending",
            "metadata": {
                "knowledge_type": "technical",
                "crawl_status": "pending"
            },
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }]

        # Mock URL data
        mock_urls_data = [{
            "source_id": "test-pending",
            "url": "https://example.com/pending"
        }]

        # Set up query counter to track which query we're on
        query_state = {"count": 0}

        def mock_execute():
            """Return different data based on query sequence."""
            query_state["count"] += 1
            result = MagicMock()
            result.error = None

            if query_state["count"] == 1:
                # Count query for sources
                result.count = 1
                result.data = None
            elif query_state["count"] == 2:
                # Main sources query
                result.data = mock_sources_data
                result.count = None
            elif query_state["count"] == 3:
                # URLs batch query
                result.data = mock_urls_data
                result.count = None
            else:
                # Document/code counts - return 0 for pending
                result.count = 0
                result.data = None

            return result

        # Set up mock chaining
        mock_select = MagicMock()
        mock_select.execute = mock_execute
        mock_select.eq = MagicMock(return_value=mock_select)
        mock_select.in_ = MagicMock(return_value=mock_select)
        mock_select.range = MagicMock(return_value=mock_select)
        mock_select.order = MagicMock(return_value=mock_select)

        mock_from = MagicMock()
        mock_from.select = MagicMock(return_value=mock_select)

        mock_supabase_client.from_ = MagicMock(return_value=mock_from)

        # Call the API endpoint
        response = client.get("/api/knowledge-items")

        # Validate response
        assert response.status_code == 200, f"API returned {response.status_code}: {response.text}"

        data = response.json()
        assert "items" in data, "Response missing 'items' field"
        assert len(data["items"]) > 0, "No items returned"

        item = data["items"][0]

        # CRITICAL: Top-level status must be present and correct
        assert "status" in item, "Missing top-level 'status' field (BUG: null status)"
        assert item["status"] == "processing", \
            f"Expected status='processing' for pending source, got '{item['status']}'"

        # Verify metadata also has correct status
        assert "metadata" in item
        assert item["metadata"]["status"] == "processing"
        assert item["metadata"]["crawl_status"] == "pending"

    def test_api_returns_top_level_status_for_completed(self, client, mock_supabase_client):
        """Test that API returns top-level status='active' for completed sources."""
        # Mock completed source
        mock_sources_data = [{
            "source_id": "test-completed",
            "title": "Completed Source",
            "summary": "Test completed",
            "metadata": {
                "knowledge_type": "technical",
                "crawl_status": "completed"
            },
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }]

        mock_urls_data = [{
            "source_id": "test-completed",
            "url": "https://example.com/completed"
        }]

        query_state = {"count": 0}

        def mock_execute():
            query_state["count"] += 1
            result = MagicMock()
            result.error = None

            if query_state["count"] == 1:
                result.count = 1
                result.data = None
            elif query_state["count"] == 2:
                result.data = mock_sources_data
                result.count = None
            elif query_state["count"] == 3:
                result.data = mock_urls_data
                result.count = None
            else:
                # Return positive counts for completed source
                result.count = 5
                result.data = None

            return result

        mock_select = MagicMock()
        mock_select.execute = mock_execute
        mock_select.eq = MagicMock(return_value=mock_select)
        mock_select.in_ = MagicMock(return_value=mock_select)
        mock_select.range = MagicMock(return_value=mock_select)
        mock_select.order = MagicMock(return_value=mock_select)

        mock_from = MagicMock()
        mock_from.select = MagicMock(return_value=mock_select)
        mock_supabase_client.from_ = MagicMock(return_value=mock_from)

        response = client.get("/api/knowledge-items")

        assert response.status_code == 200
        data = response.json()
        item = data["items"][0]

        # Verify top-level status
        assert item["status"] == "active", \
            f"Expected status='active' for completed source, got '{item['status']}'"
        assert item["metadata"]["crawl_status"] == "completed"

    def test_api_returns_top_level_status_for_failed(self, client, mock_supabase_client):
        """Test that API returns top-level status='error' for failed sources."""
        mock_sources_data = [{
            "source_id": "test-failed",
            "title": "Failed Source",
            "summary": "Test failed",
            "metadata": {
                "knowledge_type": "technical",
                "crawl_status": "failed",
                "error_message": "Crawl failed"
            },
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }]

        mock_urls_data = [{
            "source_id": "test-failed",
            "url": "https://example.com/failed"
        }]

        query_state = {"count": 0}

        def mock_execute():
            query_state["count"] += 1
            result = MagicMock()
            result.error = None

            if query_state["count"] == 1:
                result.count = 1
                result.data = None
            elif query_state["count"] == 2:
                result.data = mock_sources_data
                result.count = None
            elif query_state["count"] == 3:
                result.data = mock_urls_data
                result.count = None
            else:
                result.count = 0  # Failed source has no documents
                result.data = None

            return result

        mock_select = MagicMock()
        mock_select.execute = mock_execute
        mock_select.eq = MagicMock(return_value=mock_select)
        mock_select.in_ = MagicMock(return_value=mock_select)
        mock_select.range = MagicMock(return_value=mock_select)
        mock_select.order = MagicMock(return_value=mock_select)

        mock_from = MagicMock()
        mock_from.select = MagicMock(return_value=mock_select)
        mock_supabase_client.from_ = MagicMock(return_value=mock_from)

        response = client.get("/api/knowledge-items")

        assert response.status_code == 200
        data = response.json()
        item = data["items"][0]

        # Verify top-level status
        assert item["status"] == "error", \
            f"Expected status='error' for failed source, got '{item['status']}'"
        assert item["metadata"]["crawl_status"] == "failed"

    def test_api_response_structure_matches_typescript_interface(self, client, mock_supabase_client):
        """
        Validate that API response matches the TypeScript KnowledgeItem interface.

        This ensures the API contract matches what the UI expects.
        """
        mock_sources_data = [{
            "source_id": "test-structure",
            "title": "Structure Test",
            "summary": "Test structure",
            "metadata": {
                "knowledge_type": "technical",
                "crawl_status": "completed"
            },
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }]

        mock_urls_data = [{
            "source_id": "test-structure",
            "url": "https://example.com/structure"
        }]

        query_state = {"count": 0}

        def mock_execute():
            query_state["count"] += 1
            result = MagicMock()
            result.error = None

            if query_state["count"] == 1:
                result.count = 1
                result.data = None
            elif query_state["count"] == 2:
                result.data = mock_sources_data
                result.count = None
            elif query_state["count"] == 3:
                result.data = mock_urls_data
                result.count = None
            else:
                result.count = 5
                result.data = None

            return result

        mock_select = MagicMock()
        mock_select.execute = mock_execute
        mock_select.eq = MagicMock(return_value=mock_select)
        mock_select.in_ = MagicMock(return_value=mock_select)
        mock_select.range = MagicMock(return_value=mock_select)
        mock_select.order = MagicMock(return_value=mock_select)

        mock_from = MagicMock()
        mock_from.select = MagicMock(return_value=mock_select)
        mock_supabase_client.from_ = MagicMock(return_value=mock_from)

        response = client.get("/api/knowledge-items")

        assert response.status_code == 200
        data = response.json()
        item = data["items"][0]

        # Verify required top-level fields per KnowledgeItem interface
        required_fields = [
            "id",           # source_id
            "title",
            "url",
            "source_id",
            "source_type",
            "knowledge_type",
            "status",       # CRITICAL: top-level status field
            "document_count",
            "code_examples_count",
            "metadata",
            "created_at",
            "updated_at"
        ]

        for field in required_fields:
            assert field in item, f"Missing required field: {field}"

        # Verify status is not null
        assert item["status"] is not None, "Status field is null (BUG)"
        assert item["status"] in ["active", "processing", "error"], \
            f"Invalid status value: {item['status']}"
