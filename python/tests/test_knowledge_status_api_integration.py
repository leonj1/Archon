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

import asyncio
import os

import pytest
from unittest.mock import patch


def test_api_returns_top_level_status_for_pending(client):
    """
    Test that API returns top-level status='processing' for pending sources.

    This is the critical bug fix test: Previously API returned status=null,
    causing UI to show incorrect "Completed" badge for pending sources.
    """
    with patch.dict(os.environ, {"ARCHON_DB_BACKEND": "fake"}):
        from src.server.repositories.repository_factory import (
            reset_factory,
            get_repository,
        )

        # Reset factory to pick up new environment variable
        reset_factory()

        # Get fake repository instance
        fake_repo = get_repository(backend="fake")

        # Patch get_repository everywhere to return the same instance
        with patch(
            "src.server.repositories.repository_factory.get_repository",
            return_value=fake_repo,
        ):
            with patch(
                "src.server.api_routes.knowledge_api.get_repository",
                return_value=fake_repo,
            ):
                with patch(
                    "src.server.services.knowledge.knowledge_item_service.get_repository",
                    return_value=fake_repo,
                ):

                    # Populate test data directly in the fake repository
                    async def setup_test_data():
                        await fake_repo.upsert_source(
                            {
                                "source_id": "test-pending",
                                "title": "Pending Source",
                                "summary": "Test pending",
                                "metadata": {
                                    "knowledge_type": "technical",
                                    "crawl_status": "pending",
                                },
                                "source_url": "https://example.com/pending",
                                "created_at": "2024-01-01T00:00:00",
                                "updated_at": "2024-01-01T00:00:00",
                            }
                        )

                        # Add crawled page for URL data
                        await fake_repo.insert_crawled_page(
                            {
                                "source_id": "test-pending",
                                "url": "https://example.com/pending",
                                "title": "Pending Page",
                                "content": "Test content",
                                "metadata": {},
                                "created_at": "2024-01-01T00:00:00",
                            }
                        )

                    # Run async setup
                    asyncio.run(setup_test_data())

                    # Call the API endpoint
                    response = client.get("/api/knowledge-items")

                    # Validate response
                    assert (
                        response.status_code == 200
                    ), f"API returned {response.status_code}: {response.text}"

                    data = response.json()
                    assert "items" in data, "Response missing 'items' field"
                    assert len(data["items"]) > 0, "No items returned"

                    item = data["items"][0]

                    # CRITICAL: Top-level status must be present and correct
                    assert (
                        "status" in item
                    ), "Missing top-level 'status' field (BUG: null status)"
                    assert (
                        item["status"] == "processing"
                    ), f"Expected status='processing' for pending source, got '{item['status']}'"

                    # Verify metadata also has correct status
                    assert "metadata" in item
                    assert item["metadata"]["status"] == "processing"
                    assert item["metadata"]["crawl_status"] == "pending"


def test_api_returns_top_level_status_for_completed(client):
    """Test that API returns top-level status='active' for completed sources."""
    with patch.dict(os.environ, {"ARCHON_DB_BACKEND": "fake"}):
        from src.server.repositories.repository_factory import (
            reset_factory,
            get_repository,
        )

        reset_factory()
        fake_repo = get_repository(backend="fake")

        with patch(
            "src.server.repositories.repository_factory.get_repository",
            return_value=fake_repo,
        ):
            with patch(
                "src.server.api_routes.knowledge_api.get_repository",
                return_value=fake_repo,
            ):
                with patch(
                    "src.server.services.knowledge.knowledge_item_service.get_repository",
                    return_value=fake_repo,
                ):

                    async def setup_test_data():
                        await fake_repo.upsert_source(
                            {
                                "source_id": "test-completed",
                                "title": "Completed Source",
                                "summary": "Test completed",
                                "metadata": {
                                    "knowledge_type": "technical",
                                    "crawl_status": "completed",
                                },
                                "source_url": "https://example.com/completed",
                                "created_at": "2024-01-01T00:00:00",
                                "updated_at": "2024-01-01T00:00:00",
                            }
                        )

                        await fake_repo.insert_crawled_page(
                            {
                                "source_id": "test-completed",
                                "url": "https://example.com/completed",
                                "title": "Completed Page",
                                "content": "Test content",
                                "metadata": {},
                                "created_at": "2024-01-01T00:00:00",
                            }
                        )

                        # Add some documents to make it "active"
                        for i in range(5):
                            await fake_repo.insert_document(
                                {
                                    "source_id": "test-completed",
                                    "content": f"Document {i}",
                                    "embedding": [0.1] * 1536,  # Fake embedding
                                    "metadata": {},
                                    "url": f"https://example.com/completed#{i}",
                                    "created_at": "2024-01-01T00:00:00",
                                }
                            )

                    asyncio.run(setup_test_data())

                    response = client.get("/api/knowledge-items")

                    assert response.status_code == 200
                    data = response.json()
                    item = data["items"][0]

                    # Verify top-level status
                    assert (
                        item["status"] == "active"
                    ), f"Expected status='active' for completed source, got '{item['status']}'"
                    assert item["metadata"]["crawl_status"] == "completed"


def test_api_returns_top_level_status_for_failed(client):
    """Test that API returns top-level status='error' for failed sources."""
    with patch.dict(os.environ, {"ARCHON_DB_BACKEND": "fake"}):
        from src.server.repositories.repository_factory import (
            reset_factory,
            get_repository,
        )

        reset_factory()
        fake_repo = get_repository(backend="fake")

        with patch(
            "src.server.repositories.repository_factory.get_repository",
            return_value=fake_repo,
        ):
            with patch(
                "src.server.api_routes.knowledge_api.get_repository",
                return_value=fake_repo,
            ):
                with patch(
                    "src.server.services.knowledge.knowledge_item_service.get_repository",
                    return_value=fake_repo,
                ):

                    async def setup_test_data():
                        await fake_repo.upsert_source(
                            {
                                "source_id": "test-failed",
                                "title": "Failed Source",
                                "summary": "Test failed",
                                "metadata": {
                                    "knowledge_type": "technical",
                                    "crawl_status": "failed",
                                    "error_message": "Crawl failed",
                                },
                                "source_url": "https://example.com/failed",
                                "created_at": "2024-01-01T00:00:00",
                                "updated_at": "2024-01-01T00:00:00",
                            }
                        )

                        await fake_repo.insert_crawled_page(
                            {
                                "source_id": "test-failed",
                                "url": "https://example.com/failed",
                                "title": "Failed Page",
                                "content": "Test content",
                                "metadata": {},
                                "created_at": "2024-01-01T00:00:00",
                            }
                        )

                    asyncio.run(setup_test_data())

                    response = client.get("/api/knowledge-items")

                    assert response.status_code == 200
                    data = response.json()
                    item = data["items"][0]

                    # Verify top-level status
                    assert (
                        item["status"] == "error"
                    ), f"Expected status='error' for failed source, got '{item['status']}'"
                    assert item["metadata"]["crawl_status"] == "failed"


def test_api_response_structure_matches_typescript_interface(client):
    """
    Validate that API response matches the TypeScript KnowledgeItem interface.

    This ensures the API contract matches what the UI expects.
    """
    with patch.dict(os.environ, {"ARCHON_DB_BACKEND": "fake"}):
        from src.server.repositories.repository_factory import (
            reset_factory,
            get_repository,
        )

        reset_factory()
        fake_repo = get_repository(backend="fake")

        with patch(
            "src.server.repositories.repository_factory.get_repository",
            return_value=fake_repo,
        ):
            with patch(
                "src.server.api_routes.knowledge_api.get_repository",
                return_value=fake_repo,
            ):
                with patch(
                    "src.server.services.knowledge.knowledge_item_service.get_repository",
                    return_value=fake_repo,
                ):

                    async def setup_test_data():
                        await fake_repo.upsert_source(
                            {
                                "source_id": "test-structure",
                                "title": "Structure Test",
                                "summary": "Test structure",
                                "metadata": {
                                    "knowledge_type": "technical",
                                    "crawl_status": "completed",
                                },
                                "source_url": "https://example.com/structure",
                                "created_at": "2024-01-01T00:00:00",
                                "updated_at": "2024-01-01T00:00:00",
                            }
                        )

                        await fake_repo.insert_crawled_page(
                            {
                                "source_id": "test-structure",
                                "url": "https://example.com/structure",
                                "title": "Structure Page",
                                "content": "Test content",
                                "metadata": {},
                                "created_at": "2024-01-01T00:00:00",
                            }
                        )

                        # Add documents
                        for i in range(5):
                            await fake_repo.insert_document(
                                {
                                    "source_id": "test-structure",
                                    "content": f"Document {i}",
                                    "embedding": [0.1] * 1536,
                                    "metadata": {},
                                    "url": f"https://example.com/structure#{i}",
                                    "created_at": "2024-01-01T00:00:00",
                                }
                            )

                    asyncio.run(setup_test_data())

                    response = client.get("/api/knowledge-items")

                    assert response.status_code == 200
                    data = response.json()
                    item = data["items"][0]

                    # Verify required top-level fields per KnowledgeItem interface
                    required_fields = [
                        "id",  # source_id
                        "title",
                        "url",
                        "source_id",
                        "source_type",
                        "knowledge_type",
                        "status",  # CRITICAL: top-level status field
                        "document_count",
                        "code_examples_count",
                        "metadata",
                        "created_at",
                        "updated_at",
                    ]

                    for field in required_fields:
                        assert field in item, f"Missing required field: {field}"

                    # Verify status is not null
                    assert item["status"] is not None, "Status field is null (BUG)"
                    assert item["status"] in [
                        "active",
                        "processing",
                        "error",
                    ], f"Invalid status value: {item['status']}"
