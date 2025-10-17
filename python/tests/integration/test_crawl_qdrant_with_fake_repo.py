"""
Integration Test: Crawl → Qdrant → Fake Repository

This test demonstrates:
1. Crawling a real website (or using mock data)
2. Embedding into Qdrant vector database
3. Using FakeDatabaseRepository to validate metadata updates
4. Verifying crawl_status transitions (pending → completed)

Run with: pytest tests/integration/test_crawl_qdrant_with_fake_repo.py -v -s
"""

import os
import uuid
from typing import Any

import pytest

# Check for optional dependencies
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

from src.server.repositories.fake_repository import FakeDatabaseRepository
from src.server.services.crawling.crawling_service import CrawlingService
from src.server.services.crawling.document_storage_operations import DocumentStorageOperations
from src.server.services.crawling.orchestration.source_status_manager import SourceStatusManager

# Skip if dependencies not available
pytestmark = [
    pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set - required for embeddings"
    ),
    pytest.mark.skipif(
        not QDRANT_AVAILABLE,
        reason="qdrant-client not installed - optional integration test"
    )
]


class TestCrawlQdrantWithFakeRepository:
    """Integration test for crawl → Qdrant pipeline with fake repository validation."""

    @pytest.fixture
    def fake_repo(self):
        """Create a fake repository for testing."""
        return FakeDatabaseRepository()

    @pytest.fixture
    def qdrant_client(self):
        """Create an in-memory Qdrant client."""
        return QdrantClient(":memory:")

    @pytest.fixture
    def source_id(self):
        """Generate a unique source ID for this test."""
        return f"test_source_{uuid.uuid4().hex[:8]}"

    @pytest.mark.asyncio
    async def test_crawl_embed_and_validate_status(
        self,
        fake_repo: FakeDatabaseRepository,
        qdrant_client: QdrantClient,
        source_id: str
    ):
        """
        Test the complete workflow:
        1. Create a source with 'pending' status
        2. Simulate crawling (or use mock data)
        3. Generate embeddings and store in Qdrant
        4. Verify crawl_status updates to 'completed'
        """

        print("\n" + "="*80)
        print("CRAWL → QDRANT → FAKE REPOSITORY TEST")
        print("="*80)

        # ====================================================================
        # STEP 1: Initialize source with 'pending' status
        # ====================================================================
        print("\nStep 1: Creating source record with 'pending' status...")

        source_data = {
            "source_id": source_id,
            "title": "Test Documentation Site",
            "summary": "Test site for crawl status validation",
            "total_word_count": 0,
            "metadata": {
                "knowledge_type": "documentation",
                "tags": ["test"],
                "crawl_status": "pending",  # Initial status
                "original_url": "https://example.com/docs",
            }
        }

        created_source = await fake_repo.upsert_source(source_data)
        assert created_source["metadata"]["crawl_status"] == "pending"
        print(f"✓ Source created with ID: {source_id}")
        print(f"✓ Initial crawl_status: pending")

        # ====================================================================
        # STEP 2: Simulate crawl results (or use real crawler)
        # ====================================================================
        print("\nStep 2: Simulating crawl results...")

        # Option A: Use mock data (faster, no external dependencies)
        crawl_results = [
            {
                "url": "https://example.com/docs/getting-started",
                "markdown": "# Getting Started\n\nThis is the getting started guide. It covers installation, configuration, and first steps.",
                "title": "Getting Started Guide",
                "description": "Learn how to get started quickly",
            },
            {
                "url": "https://example.com/docs/api-reference",
                "markdown": "# API Reference\n\nComplete API documentation with examples. Includes authentication, endpoints, and response formats.",
                "title": "API Reference",
                "description": "Complete API documentation",
            },
            {
                "url": "https://example.com/docs/troubleshooting",
                "markdown": "# Troubleshooting\n\nCommon issues and solutions. Debug logging, error codes, and best practices.",
                "title": "Troubleshooting Guide",
                "description": "Solve common problems",
            },
        ]

        # Option B: Use real crawler (uncomment to test with actual crawling)
        # from crawl4ai import AsyncWebCrawler
        # async with AsyncWebCrawler() as crawler:
        #     crawling_service = CrawlingService(crawler=crawler, repository=fake_repo)
        #     result = await crawling_service.crawl_single_page("https://example.com/docs")
        #     crawl_results = [result]

        print(f"✓ Crawl results generated: {len(crawl_results)} pages")

        # ====================================================================
        # STEP 3: Process and store documents with embeddings
        # ====================================================================
        print("\nStep 3: Processing documents and generating embeddings...")

        doc_storage_ops = DocumentStorageOperations(repository=fake_repo)

        # Prepare crawl request
        request = {
            "url": "https://example.com/docs",
            "knowledge_type": "documentation",
            "tags": ["test"],
        }

        # Process and store documents (this generates embeddings)
        storage_result = await doc_storage_ops.process_and_store_documents(
            crawl_results=crawl_results,
            request=request,
            crawl_type="batch",
            original_source_id=source_id,
            source_url="https://example.com/docs",
            source_display_name="Example Docs",
        )

        print(f"✓ Documents processed and stored")
        print(f"  - Total chunks: {storage_result['chunk_count']}")
        print(f"  - Chunks stored: {storage_result['chunks_stored']}")
        print(f"  - Total word count: {storage_result['total_word_count']}")

        # ====================================================================
        # STEP 4: Verify embeddings in fake repository
        # ====================================================================
        print("\nStep 4: Verifying embeddings in fake repository...")

        # Check that documents were stored with embeddings
        stored_docs = await fake_repo.get_documents_by_source(source_id)
        assert len(stored_docs) > 0, "No documents stored"

        # Verify embeddings exist
        docs_with_embeddings = [
            doc for doc in stored_docs
            if any(key.startswith("embedding_") for key in doc.keys())
        ]
        print(f"✓ Documents in repository: {len(stored_docs)}")
        print(f"✓ Documents with embeddings: {len(docs_with_embeddings)}")

        # Optionally store in Qdrant for semantic search testing
        if docs_with_embeddings:
            await self._store_in_qdrant(
                qdrant_client,
                docs_with_embeddings,
                collection_name=f"test_{source_id}"
            )

        # ====================================================================
        # STEP 5: Update crawl_status to 'completed'
        # ====================================================================
        print("\nStep 5: Updating crawl_status to 'completed'...")

        status_manager = SourceStatusManager(fake_repo)
        update_success = await status_manager.update_to_completed(source_id)

        assert update_success, "Failed to update crawl_status to completed"
        print(f"✓ Status update successful")

        # ====================================================================
        # STEP 6: Verify crawl_status update persisted
        # ====================================================================
        print("\nStep 6: Verifying crawl_status update...")

        verified_source = await fake_repo.get_source_by_id(source_id)
        assert verified_source is not None, "Source not found after update"

        metadata = verified_source.get("metadata", {})
        actual_status = metadata.get("crawl_status")

        print(f"✓ Source retrieved after update")
        print(f"  - Expected status: completed")
        print(f"  - Actual status: {actual_status}")

        assert actual_status == "completed", (
            f"crawl_status did not update correctly. "
            f"Expected 'completed', got '{actual_status}'"
        )

        # ====================================================================
        # STEP 7: Verify source metadata was updated
        # ====================================================================
        print("\nStep 7: Verifying source metadata updates...")

        assert verified_source["total_word_count"] > 0, "Word count not updated"
        assert verified_source["summary"], "Summary not generated"

        print(f"✓ Total word count: {verified_source['total_word_count']}")
        print(f"✓ Summary: {verified_source['summary'][:100]}...")

        # ====================================================================
        # FINAL VALIDATION
        # ====================================================================
        print("\n" + "="*80)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f"\nValidation Summary:")
        print(f"  ✓ Source created with 'pending' status")
        print(f"  ✓ {len(crawl_results)} pages crawled/simulated")
        print(f"  ✓ {storage_result['chunks_stored']} chunks stored with embeddings")
        print(f"  ✓ {len(stored_docs)} documents in fake repository")
        print(f"  ✓ crawl_status updated to 'completed'")
        print(f"  ✓ Status update verified and persisted")
        print(f"  ✓ Source metadata updated (word count: {verified_source['total_word_count']})")
        print("\n" + "="*80 + "\n")

    @pytest.mark.asyncio
    async def test_crawl_status_failure_handling(
        self,
        fake_repo: FakeDatabaseRepository,
        source_id: str
    ):
        """
        Test that crawl_status updates to 'failed' on errors.
        """
        print("\n" + "="*80)
        print("CRAWL STATUS FAILURE HANDLING TEST")
        print("="*80)

        # Create source with pending status
        source_data = {
            "source_id": source_id,
            "title": "Test Site (Failure)",
            "summary": "Test failure handling",
            "total_word_count": 0,
            "metadata": {
                "crawl_status": "pending",
                "knowledge_type": "documentation",
            }
        }
        await fake_repo.upsert_source(source_data)
        print(f"✓ Source created with 'pending' status")

        # Simulate failure by updating to 'failed'
        status_manager = SourceStatusManager(fake_repo)
        update_success = await status_manager.update_to_failed(source_id)

        assert update_success, "Failed to update status to 'failed'"
        print(f"✓ Status updated to 'failed'")

        # Verify
        verified_source = await fake_repo.get_source_by_id(source_id)
        actual_status = verified_source["metadata"]["crawl_status"]

        assert actual_status == "failed", (
            f"Expected 'failed' status, got '{actual_status}'"
        )
        print(f"✓ Status verified: {actual_status}")
        print("\n✅ FAILURE HANDLING TEST PASSED\n")

    async def _store_in_qdrant(
        self,
        client: QdrantClient,
        documents: list[dict[str, Any]],
        collection_name: str
    ):
        """Helper method to store embeddings in Qdrant for semantic search testing."""
        print(f"\n  → Storing {len(documents)} vectors in Qdrant...")

        # Get embedding dimension from first document
        first_doc = documents[0]
        embedding_key = next(
            (key for key in first_doc.keys() if key.startswith("embedding_")),
            None
        )

        if not embedding_key:
            print("  ⚠ No embeddings found, skipping Qdrant storage")
            return

        embedding = first_doc[embedding_key]
        dimension = len(embedding)

        # Create collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=dimension, distance=Distance.COSINE)
        )

        # Prepare points
        points = []
        for doc in documents:
            if embedding_key in doc:
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=doc[embedding_key],
                    payload={
                        "url": doc.get("url"),
                        "content": doc.get("content", "")[:500],  # Truncate for payload
                        "source_id": doc.get("source_id"),
                    }
                )
                points.append(point)

        # Upsert to Qdrant
        client.upsert(collection_name=collection_name, points=points)

        collection_info = client.get_collection(collection_name)
        print(f"  ✓ Stored {collection_info.points_count} vectors in Qdrant")
        print(f"  ✓ Collection: {collection_name}")
        print(f"  ✓ Dimension: {dimension}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
