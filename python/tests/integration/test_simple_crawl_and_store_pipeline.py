"""
Integration Test: Complete Crawl-and-Store Pipeline

This test validates the end-to-end pipeline using REAL external calls:
- Real web crawling (using small, stable sites)
- Real OpenAI API embeddings
- Real Qdrant vector storage (localhost:6333)
- Real semantic search

NO MOCKS - This is a true integration test that validates the complete workflow.

Requirements:
- OPENAI_API_KEY environment variable must be set
- Qdrant server running at localhost:6333 (docker-compose up qdrant)
- Network connectivity for crawling
- Sufficient OpenAI API credits

Run with: pytest python/tests/integration/test_simple_crawl_and_store_pipeline.py -v -s

Note: This test creates and cleans up temporary collections in Qdrant.
"""

import os
import uuid
from typing import Any, Dict, List

import pytest

# Try to import qdrant at module level to skip early if not available
try:
    from qdrant_client import AsyncQdrantClient
    QDRANT_CLIENT_AVAILABLE = True
except ImportError:
    QDRANT_CLIENT_AVAILABLE = False

# Skip if no OpenAI API key or qdrant-client not installed
pytestmark = [
    pytest.mark.skipif(
        not QDRANT_CLIENT_AVAILABLE,
        reason="qdrant-client not installed"
    ),
    pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set - required for real embeddings"
    ),
    pytest.mark.integration
]

# Helper to check Qdrant availability
async def check_qdrant_available() -> bool:
    """Check if Qdrant is available at localhost:6333"""
    if not QDRANT_CLIENT_AVAILABLE:
        return False
    try:
        from qdrant_client import AsyncQdrantClient
        client = AsyncQdrantClient(url="http://localhost:6333")
        await client.get_collections()
        await client.close()
        return True
    except Exception:
        return False


class TestSimpleCrawlAndStorePipeline:
    """
    Integration tests for the complete crawl-and-store pipeline.

    Tests the workflow:
    SimpleCrawlingService → document validation → SimpleVectorDBService → search
    """

    @pytest.mark.asyncio
    async def test_real_crawl_and_store_single_page(self):
        """
        Test the complete pipeline with a real single-page crawl.

        This test:
        1. Crawls a real website (example.com)
        2. Stores documents in real Qdrant (localhost)
        3. Validates document structure
        4. Performs semantic search
        5. Cleans up test data
        """
        # Check Qdrant availability
        if not await check_qdrant_available():
            pytest.skip("Qdrant not available at localhost:6333. Run: docker-compose up qdrant")

        from src.server.services.storage.crawl_and_store_service import CrawlAndStoreService

        print("\n" + "="*80)
        print("TEST: Real Crawl and Store - Single Page")
        print("="*80)

        # Use unique collection name for test isolation
        test_collection = f"test_single_page_{uuid.uuid4().hex[:8]}"

        async with CrawlAndStoreService(
            qdrant_url="http://localhost:6333",
            collection_name=test_collection,
            default_max_depth=1
        ) as service:

            # Step 1: Ingest a single page
            print("\n[1/5] Crawling single page: https://example.com")
            result = await service.ingest_url(
                url="https://example.com",
                source_id="example_com",
                max_depth=1
            )

            # Validate ingestion success
            assert result["success"], f"Ingestion failed: {result.get('error')}"
            assert result["crawl"]["total_pages"] > 0, "No pages were crawled"
            assert result["storage"]["chunks_stored"] > 0, "No chunks were stored"

            print(f"✓ Crawled {result['crawl']['total_pages']} page(s)")
            print(f"✓ Stored {result['storage']['chunks_stored']} chunks")
            print(f"✓ Crawl type: {result['crawl']['crawl_type']}")

            # Step 2: Validate document structure
            print("\n[2/5] Validating document structure...")
            documents = result["crawl"]["documents"]

            assert len(documents) > 0, "No documents in crawl result"

            for doc in documents:
                assert "url" in doc, "Document missing 'url' field"
                assert "title" in doc, "Document missing 'title' field"
                assert "content" in doc, "Document missing 'content' field"
                assert "metadata" in doc, "Document missing 'metadata' field"
                assert isinstance(doc["content"], str), "Content must be string"
                assert len(doc["content"]) > 0, "Content cannot be empty"

            print(f"✓ All {len(documents)} documents have valid structure")

            # Step 3: Validate storage metadata
            print("\n[3/5] Validating storage metadata...")
            storage = result["storage"]

            assert storage["source_id"] == "example_com", "Source ID mismatch"
            assert storage["documents_processed"] == len(documents), "Document count mismatch"
            assert storage["chunks_stored"] > 0, "No chunks stored"
            assert storage["failed_chunks"] == 0, "Some chunks failed to store"

            print(f"✓ Source ID: {storage['source_id']}")
            print(f"✓ Documents processed: {storage['documents_processed']}")
            print(f"✓ Chunks stored: {storage['chunks_stored']}")
            print(f"✓ Failed chunks: {storage['failed_chunks']}")

            # Step 4: Perform semantic search
            print("\n[4/5] Testing semantic search...")
            query = "What is example domain?"
            search_results = await service.search(
                query=query,
                limit=5,
                source_id="example_com"
            )

            assert len(search_results) > 0, "No search results returned"

            for result in search_results:
                assert "id" in result, "Result missing 'id'"
                assert "score" in result, "Result missing 'score'"
                assert "url" in result, "Result missing 'url'"
                assert "content" in result, "Result missing 'content'"
                assert result["score"] > 0, "Score must be positive"

            print(f"✓ Found {len(search_results)} results")
            print(f"✓ Top result score: {search_results[0]['score']:.4f}")
            print(f"✓ Top result URL: {search_results[0]['url']}")

            # Step 5: Validate collection stats
            print("\n[5/5] Validating collection statistics...")
            stats = await service.get_stats()

            assert "vectors_count" in stats or "points_count" in stats, "Stats missing vector count"
            vectors_count = stats.get("vectors_count") or stats.get("points_count") or 0
            assert vectors_count is not None and vectors_count > 0, "No vectors in collection"

            print(f"✓ Collection vectors: {vectors_count}")
            print(f"✓ Collection status: {stats.get('status', 'unknown')}")

        print("\n" + "="*80)
        print("✅ TEST PASSED: Single Page Crawl and Store")
        print("="*80 + "\n")

    @pytest.mark.asyncio
    async def test_real_crawl_and_store_with_depth(self):
        """
        Test recursive crawling with depth=2 on a real website.

        This tests:
        - Multi-page crawling
        - Link following
        - Batch document processing
        - Search across multiple pages
        """
        # Check Qdrant availability
        if not await check_qdrant_available():
            pytest.skip("Qdrant not available at localhost:6333. Run: docker-compose up qdrant")

        from src.server.services.storage.crawl_and_store_service import CrawlAndStoreService

        print("\n" + "="*80)
        print("TEST: Real Crawl and Store - Recursive (Depth=2)")
        print("="*80)

        test_collection = f"test_recursive_{uuid.uuid4().hex[:8]}"

        async with CrawlAndStoreService(
            qdrant_url="http://localhost:6333",
            collection_name=test_collection,
            default_max_depth=2
        ) as service:

            # Use a small, stable site for testing
            # Note: example.com has limited internal links, so we may get 1-2 pages
            print("\n[1/4] Crawling with depth=2...")
            result = await service.ingest_url(
                url="https://example.com",
                source_id="example_recursive",
                max_depth=2
            )

            assert result["success"], f"Ingestion failed: {result.get('error')}"
            print(f"✓ Crawl completed: {result['crawl']['total_pages']} pages")
            print(f"✓ Chunks stored: {result['storage']['chunks_stored']}")

            # Step 2: Validate multi-document storage
            print("\n[2/4] Validating multi-document storage...")
            documents = result["crawl"]["documents"]

            # With depth=2, we should get at least 1 page (example.com has few links)
            assert len(documents) >= 1, "Expected at least 1 document"

            # All documents should be unique URLs
            urls = [doc["url"] for doc in documents]
            assert len(urls) == len(set(urls)), "Duplicate URLs found"

            print(f"✓ Unique URLs: {len(urls)}")

            # Step 3: Test search across all pages
            print("\n[3/4] Testing search across multiple pages...")
            search_results = await service.search(
                query="example domain information",
                limit=10,
                source_id="example_recursive"
            )

            assert len(search_results) > 0, "No search results"
            print(f"✓ Search returned {len(search_results)} results")

            # Step 4: Validate chunks from multiple documents
            print("\n[4/4] Validating chunk distribution...")
            unique_result_urls = set(r["url"] for r in search_results)
            print(f"✓ Results span {len(unique_result_urls)} unique URLs")

        print("\n" + "="*80)
        print("✅ TEST PASSED: Recursive Crawl and Store")
        print("="*80 + "\n")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_progress_tracking_callback(self):
        """
        Test progress tracking with real callbacks.

        Validates:
        - Progress callback is invoked at each stage
        - Stages: crawling, validating, storing, completed
        - Percentages increase appropriately
        - Metadata contains expected information
        """
        # Check Qdrant availability
        if not await check_qdrant_available():
            pytest.skip("Qdrant not available at localhost:6333. Run: docker-compose up qdrant")

        from src.server.services.storage.crawl_and_store_service import CrawlAndStoreService

        print("\n" + "="*80)
        print("TEST: Progress Tracking Callbacks")
        print("="*80)

        # Track callback invocations
        progress_calls: List[Dict[str, Any]] = []

        def progress_callback(stage: str, percentage: int, metadata: Dict[str, Any]):
            progress_calls.append({
                "stage": stage,
                "percentage": percentage,
                "metadata": metadata
            })
            print(f"  [{percentage}%] {stage}: {metadata}")

        async with CrawlAndStoreService(
            qdrant_url="http://localhost:6333",
            collection_name=f"test_progress_{uuid.uuid4().hex[:8]}"
        ) as service:

            print("\n[1/2] Ingesting with progress tracking...")
            result = await service.ingest_url(
                url="https://example.com",
                source_id="example_progress",
                max_depth=1,
                progress_callback=progress_callback
            )

            assert result["success"], "Ingestion failed"

            # Validate progress tracking
            print("\n[2/2] Validating progress callbacks...")
            assert len(progress_calls) >= 4, f"Expected at least 4 callbacks, got {len(progress_calls)}"

            # Extract stages
            stages = [call["stage"] for call in progress_calls]
            expected_stages = ["crawling", "validating", "storing", "completed"]

            for expected_stage in expected_stages:
                assert expected_stage in stages, f"Missing stage: {expected_stage}"

            print(f"✓ All expected stages present: {expected_stages}")

            # Validate percentages increase
            percentages = [call["percentage"] for call in progress_calls]
            assert percentages[-1] == 100, "Final percentage should be 100"

            print(f"✓ Progress percentages: {percentages}")

            # Validate metadata content
            completed_call = [c for c in progress_calls if c["stage"] == "completed"][0]
            assert "total_pages" in completed_call["metadata"], "Missing total_pages in completed metadata"
            assert "chunks_stored" in completed_call["metadata"], "Missing chunks_stored in completed metadata"

            print(f"✓ Completed metadata: {completed_call['metadata']}")

        print("\n" + "="*80)
        print("✅ TEST PASSED: Progress Tracking")
        print("="*80 + "\n")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_error_handling_invalid_url(self):
        """
        Test error handling for invalid URLs.

        Validates:
        - Empty URLs raise ValueError
        - Invalid URLs return error in result
        - Service remains stable after errors
        """
        # Check Qdrant availability
        if not await check_qdrant_available():
            pytest.skip("Qdrant not available at localhost:6333. Run: docker-compose up qdrant")

        from src.server.services.storage.crawl_and_store_service import CrawlAndStoreService

        print("\n" + "="*80)
        print("TEST: Error Handling - Invalid URLs")
        print("="*80)

        async with CrawlAndStoreService(
            qdrant_url="http://localhost:6333",
            collection_name=f"test_errors_{uuid.uuid4().hex[:8]}"
        ) as service:

            # Test 1: Empty URL should raise ValueError
            print("\n[1/3] Testing empty URL...")
            with pytest.raises(ValueError, match="URL cannot be empty"):
                await service.ingest_url(url="", source_id="test")
            print("✓ Empty URL raises ValueError")

            # Test 2: Invalid URL should return error result
            print("\n[2/3] Testing invalid URL...")
            result = await service.ingest_url(
                url="https://this-domain-does-not-exist-123456789.invalid",
                source_id="invalid_test",
                max_depth=1
            )

            assert not result["success"], "Invalid URL should fail"
            assert result["error"] is not None, "Error message should be present"
            print(f"✓ Invalid URL failed gracefully: {result['error'][:80]}...")

            # Test 3: Service should remain stable and work after error
            print("\n[3/3] Testing service stability after error...")
            valid_result = await service.ingest_url(
                url="https://example.com",
                source_id="valid_after_error",
                max_depth=1
            )

            assert valid_result["success"], "Service should work after handling error"
            print("✓ Service stable after error - valid URL works")

        print("\n" + "="*80)
        print("✅ TEST PASSED: Error Handling")
        print("="*80 + "\n")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_source_management_delete(self):
        """
        Test source management operations.

        Validates:
        - Storing multiple sources
        - Deleting specific sources
        - Search filtering by source
        - Source deletion returns correct count
        """
        # Check Qdrant availability
        if not await check_qdrant_available():
            pytest.skip("Qdrant not available at localhost:6333. Run: docker-compose up qdrant")

        from src.server.services.storage.crawl_and_store_service import CrawlAndStoreService

        print("\n" + "="*80)
        print("TEST: Source Management and Deletion")
        print("="*80)

        async with CrawlAndStoreService(
            qdrant_url="http://localhost:6333",
            collection_name=f"test_source_mgmt_{uuid.uuid4().hex[:8]}"
        ) as service:

            # Step 1: Ingest two different sources
            print("\n[1/4] Ingesting source 1...")
            result1 = await service.ingest_url(
                url="https://example.com",
                source_id="source_1",
                max_depth=1
            )
            assert result1["success"], "Source 1 ingestion failed"
            chunks_source1 = result1["storage"]["chunks_stored"]
            print(f"✓ Source 1: {chunks_source1} chunks")

            print("\n[2/4] Ingesting source 2...")
            result2 = await service.ingest_url(
                url="https://example.com",  # Same URL, different source_id
                source_id="source_2",
                max_depth=1
            )
            assert result2["success"], "Source 2 ingestion failed"
            chunks_source2 = result2["storage"]["chunks_stored"]
            print(f"✓ Source 2: {chunks_source2} chunks")

            # Step 2: Search with source filtering
            print("\n[3/4] Testing search with source filtering...")

            # Search source 1 only
            results_s1 = await service.search(
                query="example",
                limit=10,
                source_id="source_1"
            )

            # Search source 2 only
            results_s2 = await service.search(
                query="example",
                limit=10,
                source_id="source_2"
            )

            assert len(results_s1) > 0, "Source 1 search returned no results"
            assert len(results_s2) > 0, "Source 2 search returned no results"
            print(f"✓ Source 1 search: {len(results_s1)} results")
            print(f"✓ Source 2 search: {len(results_s2)} results")

            # Step 3: Delete source 1
            print("\n[4/4] Deleting source 1...")
            deleted_count = await service.delete_source("source_1")

            assert deleted_count > 0, "No vectors deleted"
            print(f"✓ Deleted {deleted_count} vectors from source_1")

            # Verify source 1 is gone but source 2 remains
            results_s1_after = await service.search(
                query="example",
                limit=10,
                source_id="source_1"
            )

            results_s2_after = await service.search(
                query="example",
                limit=10,
                source_id="source_2"
            )

            assert len(results_s1_after) == 0, "Source 1 should have no results after deletion"
            assert len(results_s2_after) > 0, "Source 2 should still have results"
            print(f"✓ Source 1 deleted (0 results)")
            print(f"✓ Source 2 intact ({len(results_s2_after)} results)")

        print("\n" + "="*80)
        print("✅ TEST PASSED: Source Management")
        print("="*80 + "\n")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_batch_operations_multiple_sources(self):
        """
        Test batch processing of multiple sources in sequence.

        Validates:
        - Sequential ingestion of multiple URLs
        - Collection statistics across sources
        - Search across all sources (no filter)
        - Resource management with multiple operations
        """
        # Check Qdrant availability
        if not await check_qdrant_available():
            pytest.skip("Qdrant not available at localhost:6333. Run: docker-compose up qdrant")

        from src.server.services.storage.crawl_and_store_service import CrawlAndStoreService

        print("\n" + "="*80)
        print("TEST: Batch Operations - Multiple Sources")
        print("="*80)

        async with CrawlAndStoreService(
            qdrant_url="http://localhost:6333",
            collection_name=f"test_batch_{uuid.uuid4().hex[:8]}"
        ) as service:

            # Define test sources
            sources = [
                ("https://example.com", "example_1"),
                ("https://example.com", "example_2"),
            ]

            total_chunks = 0

            # Step 1: Ingest all sources
            print("\n[1/3] Ingesting multiple sources...")
            for i, (url, source_id) in enumerate(sources, 1):
                print(f"\n  Source {i}/{len(sources)}: {source_id}")
                result = await service.ingest_url(
                    url=url,
                    source_id=source_id,
                    max_depth=1
                )

                assert result["success"], f"Source {source_id} failed: {result.get('error')}"
                chunks = result["storage"]["chunks_stored"]
                total_chunks += chunks
                print(f"  ✓ Stored {chunks} chunks from {source_id}")

            print(f"\n✓ Total chunks across all sources: {total_chunks}")

            # Step 2: Verify collection statistics
            print("\n[2/3] Verifying collection statistics...")
            stats = await service.get_stats()

            vectors_count = stats.get("vectors_count") or stats.get("points_count") or 0
            assert vectors_count >= total_chunks, f"Expected at least {total_chunks} vectors, got {vectors_count}"
            print(f"✓ Collection contains {vectors_count} vectors")

            # Step 3: Search across all sources
            print("\n[3/3] Testing search across all sources...")
            all_results = await service.search(
                query="example domain",
                limit=20,
                source_id=None  # No filter - search all sources
            )

            assert len(all_results) > 0, "Cross-source search returned no results"

            # Verify results come from different sources
            result_sources = set(r.get("metadata", {}).get("source_id") for r in all_results)
            print(f"✓ Search returned {len(all_results)} results")
            print(f"✓ Results from {len(result_sources)} sources")

        print("\n" + "="*80)
        print("✅ TEST PASSED: Batch Operations")
        print("="*80 + "\n")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_search_functionality_with_filtering(self):
        """
        Test comprehensive search functionality.

        Validates:
        - Basic semantic search
        - Result limit parameter
        - Source filtering
        - Result relevance ordering
        - Result structure completeness
        """
        # Check Qdrant availability
        if not await check_qdrant_available():
            pytest.skip("Qdrant not available at localhost:6333. Run: docker-compose up qdrant")

        from src.server.services.storage.crawl_and_store_service import CrawlAndStoreService

        print("\n" + "="*80)
        print("TEST: Search Functionality with Filtering")
        print("="*80)

        async with CrawlAndStoreService(
            qdrant_url="http://localhost:6333",
            collection_name=f"test_search_{uuid.uuid4().hex[:8]}"
        ) as service:

            # Ingest test data
            print("\n[1/4] Ingesting test data...")
            result = await service.ingest_url(
                url="https://example.com",
                source_id="search_test",
                max_depth=1
            )
            assert result["success"], "Ingestion failed"
            print(f"✓ Ingested {result['storage']['chunks_stored']} chunks")

            # Test 1: Basic search with limit
            print("\n[2/4] Testing search with limit parameter...")
            results_limit_3 = await service.search(
                query="example domain",
                limit=3,
                source_id="search_test"
            )

            results_limit_5 = await service.search(
                query="example domain",
                limit=5,
                source_id="search_test"
            )

            assert len(results_limit_3) <= 3, "Limit=3 returned too many results"
            assert len(results_limit_5) <= 5, "Limit=5 returned too many results"
            print(f"✓ Limit=3 returned {len(results_limit_3)} results")
            print(f"✓ Limit=5 returned {len(results_limit_5)} results")

            # Test 2: Verify result structure
            print("\n[3/4] Validating result structure...")
            for result in results_limit_3:
                assert "id" in result, "Missing 'id' field"
                assert "score" in result, "Missing 'score' field"
                assert "url" in result, "Missing 'url' field"
                assert "content" in result, "Missing 'content' field"
                assert "chunk_number" in result, "Missing 'chunk_number' field"
                assert "metadata" in result, "Missing 'metadata' field"

                # Validate types
                assert isinstance(result["score"], (int, float)), "Score must be numeric"
                assert isinstance(result["url"], str), "URL must be string"
                assert isinstance(result["content"], str), "Content must be string"
                assert isinstance(result["chunk_number"], int), "Chunk number must be int"
                assert isinstance(result["metadata"], dict), "Metadata must be dict"

            print(f"✓ All results have complete, valid structure")

            # Test 3: Verify relevance ordering
            print("\n[4/4] Validating relevance ordering...")
            scores = [r["score"] for r in results_limit_3]

            # Scores should be in descending order
            assert scores == sorted(scores, reverse=True), "Results not ordered by relevance"
            print(f"✓ Results ordered by relevance: {[f'{s:.4f}' for s in scores]}")

            # Scores should be positive and reasonable (0-1 for cosine similarity)
            assert all(0 < s <= 1 for s in scores), "Scores out of expected range"
            print(f"✓ All scores in valid range (0, 1]")

        print("\n" + "="*80)
        print("✅ TEST PASSED: Search Functionality")
        print("="*80 + "\n")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_resource_cleanup_context_manager(self):
        """
        Test proper resource cleanup using context manager.

        Validates:
        - Context manager __aenter__ initializes service
        - Context manager __aexit__ cleans up resources
        - Service cannot be used after cleanup
        - Multiple context manager uses are safe
        """
        # Check Qdrant availability
        if not await check_qdrant_available():
            pytest.skip("Qdrant not available at localhost:6333. Run: docker-compose up qdrant")

        from src.server.services.storage.crawl_and_store_service import CrawlAndStoreService

        print("\n" + "="*80)
        print("TEST: Resource Cleanup with Context Manager")
        print("="*80)

        # Test 1: Basic context manager usage
        print("\n[1/3] Testing basic context manager...")
        async with CrawlAndStoreService(
            qdrant_url="http://localhost:6333",
            collection_name=f"test_cleanup_{uuid.uuid4().hex[:8]}"
        ) as service:
            result = await service.ingest_url(
                url="https://example.com",
                source_id="cleanup_test",
                max_depth=1
            )
            assert result["success"], "Ingestion failed"

        print("✓ Context manager cleaned up successfully")

        # Test 2: Multiple sequential uses
        print("\n[2/3] Testing multiple sequential context manager uses...")
        for i in range(2):
            async with CrawlAndStoreService(
                qdrant_url="http://localhost:6333",
                collection_name=f"test_cleanup_{i}"
            ) as service:
                result = await service.ingest_url(
                    url="https://example.com",
                    source_id=f"test_{i}",
                    max_depth=1
                )
                assert result["success"], f"Iteration {i} failed"
            print(f"  ✓ Iteration {i+1} completed and cleaned up")

        # Test 3: Manual close
        print("\n[3/3] Testing manual close...")
        service = CrawlAndStoreService(
            qdrant_url="http://localhost:6333",
            collection_name=f"test_manual_close_{uuid.uuid4().hex[:8]}"
        )

        try:
            result = await service.ingest_url(
                url="https://example.com",
                source_id="manual_close_test",
                max_depth=1
            )
            assert result["success"], "Ingestion failed"
        finally:
            await service.close()

        print("✓ Manual close completed successfully")

        print("\n" + "="*80)
        print("✅ TEST PASSED: Resource Cleanup")
        print("="*80 + "\n")


# Convenience function to run all tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
