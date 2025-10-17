"""
Unit Test: Crawl Status Management with Fake Repository

This test validates crawl_status metadata updates WITHOUT external dependencies.
Uses mocked embeddings and in-memory fake repository.

Run with: pytest tests/unit/test_crawl_status_with_fake_repo.py -v
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.server.repositories.fake_repository import FakeDatabaseRepository
from src.server.services.crawling.document_storage_operations import DocumentStorageOperations
from src.server.services.crawling.orchestration.source_status_manager import SourceStatusManager
from src.server.services.embeddings.embedding_service import EmbeddingBatchResult


class TestCrawlStatusWithFakeRepository:
    """Unit tests for crawl status management using fake repository."""

    @pytest.fixture
    def fake_repo(self):
        """Create a fake repository for testing."""
        return FakeDatabaseRepository()

    @pytest.fixture
    def source_id(self):
        """Generate a unique source ID for this test."""
        return f"test_source_{uuid.uuid4().hex[:8]}"

    @pytest.fixture
    def mock_embeddings(self):
        """Create mock embeddings (1536-dimensional vectors)."""
        def create_mock_embedding():
            # Return a fake 1536-dimensional embedding
            return [0.1] * 1536

        return create_mock_embedding

    @pytest.mark.asyncio
    async def test_source_status_lifecycle(
        self,
        fake_repo: FakeDatabaseRepository,
        source_id: str
    ):
        """
        Test the complete lifecycle of source crawl_status:
        1. Create source with 'pending' status
        2. Update to 'completed'
        3. Verify persistence
        """

        # ====================================================================
        # STEP 1: Create source with 'pending' status
        # ====================================================================
        source_data = {
            "source_id": source_id,
            "title": "Test Documentation",
            "summary": "Initial summary",
            "total_word_count": 0,
            "metadata": {
                "knowledge_type": "documentation",
                "crawl_status": "pending",  # Initial state
                "tags": ["test"],
            }
        }

        created_source = await fake_repo.upsert_source(source_data)
        assert created_source is not None
        assert created_source["metadata"]["crawl_status"] == "pending"

        # ====================================================================
        # STEP 2: Update to 'completed'
        # ====================================================================
        status_manager = SourceStatusManager(fake_repo)
        update_success = await status_manager.update_to_completed(source_id)

        assert update_success, "Failed to update crawl_status to 'completed'"

        # ====================================================================
        # STEP 3: Verify the update persisted
        # ====================================================================
        verified_source = await fake_repo.get_source_by_id(source_id)
        assert verified_source is not None

        metadata = verified_source.get("metadata", {})
        actual_status = metadata.get("crawl_status")

        assert actual_status == "completed", (
            f"Expected 'completed', got '{actual_status}'"
        )

    @pytest.mark.asyncio
    async def test_source_status_failure(
        self,
        fake_repo: FakeDatabaseRepository,
        source_id: str
    ):
        """
        Test that crawl_status updates to 'failed' on errors.
        """

        # Create source with pending status
        source_data = {
            "source_id": source_id,
            "title": "Test Site",
            "summary": "Test",
            "total_word_count": 0,
            "metadata": {
                "crawl_status": "pending",
                "knowledge_type": "documentation",
            }
        }
        await fake_repo.upsert_source(source_data)

        # Update to failed
        status_manager = SourceStatusManager(fake_repo)
        update_success = await status_manager.update_to_failed(source_id)

        assert update_success

        # Verify
        verified_source = await fake_repo.get_source_by_id(source_id)
        assert verified_source["metadata"]["crawl_status"] == "failed"

    @pytest.mark.asyncio
    async def test_document_storage_with_fake_repo(
        self,
        fake_repo: FakeDatabaseRepository,
        source_id: str,
        mock_embeddings
    ):
        """
        Test document storage workflow with mocked embeddings.
        Validates that documents are stored with correct source_id.
        """

        # ====================================================================
        # STEP 1: Create source
        # ====================================================================
        source_data = {
            "source_id": source_id,
            "title": "Test Docs",
            "summary": "Test documentation site",
            "total_word_count": 0,
            "metadata": {
                "crawl_status": "pending",
                "knowledge_type": "documentation",
            }
        }
        await fake_repo.upsert_source(source_data)

        # ====================================================================
        # STEP 2: Prepare mock crawl results
        # ====================================================================
        crawl_results = [
            {
                "url": "https://example.com/page1",
                "markdown": "# Page 1\n\nThis is the first page with some content.",
                "title": "Page 1",
                "description": "First page",
            },
            {
                "url": "https://example.com/page2",
                "markdown": "# Page 2\n\nThis is the second page with more content.",
                "title": "Page 2",
                "description": "Second page",
            },
        ]

        # ====================================================================
        # STEP 3: Mock the embedding service
        # ====================================================================
        with patch(
            "src.server.services.storage.document_storage_service.create_embeddings_batch"
        ) as mock_create_embeddings:

            # Create mock result with fake embeddings
            def create_mock_result(texts, **kwargs):
                result = EmbeddingBatchResult()
                for text in texts:
                    result.add_success(mock_embeddings(), text)
                return result

            mock_create_embeddings.side_effect = create_mock_result

            # ====================================================================
            # STEP 4: Process and store documents
            # ====================================================================
            doc_storage_ops = DocumentStorageOperations(repository=fake_repo)

            request = {
                "url": "https://example.com",
                "knowledge_type": "documentation",
                "tags": ["test"],
            }

            storage_result = await doc_storage_ops.process_and_store_documents(
                crawl_results=crawl_results,
                request=request,
                crawl_type="batch",
                original_source_id=source_id,
                source_url="https://example.com",
            )

            # ====================================================================
            # STEP 5: Verify storage results
            # ====================================================================
            assert storage_result["chunks_stored"] > 0
            assert storage_result["chunk_count"] > 0
            assert storage_result["source_id"] == source_id

            # ====================================================================
            # STEP 6: Verify documents in fake repository
            # ====================================================================
            stored_docs = await fake_repo.get_documents_by_source(source_id)
            assert len(stored_docs) > 0

            # Verify all documents have the correct source_id
            for doc in stored_docs:
                assert doc.get("source_id") == source_id

            # Verify embeddings were stored
            docs_with_embeddings = [
                doc for doc in stored_docs
                if any(key.startswith("embedding_") for key in doc.keys())
            ]
            assert len(docs_with_embeddings) > 0

    @pytest.mark.asyncio
    async def test_source_not_found_handling(
        self,
        fake_repo: FakeDatabaseRepository
    ):
        """
        Test that status updates handle missing sources gracefully.
        """
        non_existent_source_id = "non_existent_source"

        status_manager = SourceStatusManager(fake_repo)

        # Should return False for non-existent source
        update_success = await status_manager.update_to_completed(non_existent_source_id)
        assert not update_success

        update_success = await status_manager.update_to_failed(non_existent_source_id)
        assert not update_success

    @pytest.mark.asyncio
    async def test_crawl_status_transitions(
        self,
        fake_repo: FakeDatabaseRepository,
        source_id: str
    ):
        """
        Test multiple status transitions:
        pending → completed → (re-crawl) → pending → failed
        """

        # Create source
        source_data = {
            "source_id": source_id,
            "title": "Test",
            "summary": "Test",
            "total_word_count": 0,
            "metadata": {"crawl_status": "pending"}
        }
        await fake_repo.upsert_source(source_data)

        status_manager = SourceStatusManager(fake_repo)

        # Transition: pending → completed
        await status_manager.update_to_completed(source_id)
        source = await fake_repo.get_source_by_id(source_id)
        assert source["metadata"]["crawl_status"] == "completed"

        # Transition: completed → pending (re-crawl)
        await fake_repo.update_source_metadata(
            source_id,
            {"crawl_status": "pending"}
        )
        source = await fake_repo.get_source_by_id(source_id)
        assert source["metadata"]["crawl_status"] == "pending"

        # Transition: pending → failed
        await status_manager.update_to_failed(source_id)
        source = await fake_repo.get_source_by_id(source_id)
        assert source["metadata"]["crawl_status"] == "failed"

    @pytest.mark.asyncio
    async def test_concurrent_source_operations(
        self,
        fake_repo: FakeDatabaseRepository
    ):
        """
        Test that fake repository handles concurrent operations correctly.
        """
        import asyncio

        # Create multiple sources
        source_ids = [f"source_{i}" for i in range(5)]

        async def create_and_update(source_id: str):
            # Create
            await fake_repo.upsert_source({
                "source_id": source_id,
                "title": f"Source {source_id}",
                "summary": "Test",
                "total_word_count": 0,
                "metadata": {"crawl_status": "pending"}
            })

            # Update
            status_manager = SourceStatusManager(fake_repo)
            await status_manager.update_to_completed(source_id)

            # Verify
            source = await fake_repo.get_source_by_id(source_id)
            return source["metadata"]["crawl_status"]

        # Run concurrently
        results = await asyncio.gather(*[
            create_and_update(sid) for sid in source_ids
        ])

        # All should be completed
        assert all(status == "completed" for status in results)

        # Verify all sources exist
        all_sources = await fake_repo.list_sources()
        assert len(all_sources) >= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
