"""
Example usage of CrawlAndStoreService

This file demonstrates various usage patterns for the unified crawl-and-store pipeline.
"""

import asyncio
from typing import Any, Dict

from .crawl_and_store_service import CrawlAndStoreService, ingest_url


# Example 1: Basic usage with context manager
async def example_basic_usage():
    """
    Basic example: Crawl and store a single URL.
    """
    print("\n=== Example 1: Basic Usage ===")

    async with CrawlAndStoreService() as service:
        result = await service.ingest_url(
            url="https://example.com",
            source_id="example_docs",
            max_depth=2
        )

        if result["success"]:
            print(f"✓ Success!")
            print(f"  Pages crawled: {result['crawl']['total_pages']}")
            print(f"  Chunks stored: {result['storage']['chunks_stored']}")
            print(f"  Failed chunks: {result['storage']['failed_chunks']}")
        else:
            print(f"✗ Failed: {result['error']}")


# Example 2: With progress tracking
async def example_with_progress():
    """
    Example with progress callback for long-running operations.
    """
    print("\n=== Example 2: Progress Tracking ===")

    def progress_callback(stage: str, percentage: int, metadata: Dict[str, Any]):
        """Progress callback that prints status updates."""
        print(f"[{percentage:3d}%] {stage.upper()}: {metadata}")

    async with CrawlAndStoreService() as service:
        result = await service.ingest_url(
            url="https://fastapi.tiangolo.com/tutorial/",
            source_id="fastapi_tutorial",
            max_depth=2,
            progress_callback=progress_callback
        )

        print(f"\nFinal result: {result['success']}")


# Example 3: Batch processing multiple sources
async def example_batch_processing():
    """
    Example: Ingest multiple documentation sources in sequence.
    """
    print("\n=== Example 3: Batch Processing ===")

    sources = [
        ("https://docs.python.org/3/library/", "python_stdlib", 2),
        ("https://pydantic-docs.helpmanual.io/", "pydantic_docs", 2),
        ("https://www.sqlalchemy.org/docs/", "sqlalchemy_docs", 1),
    ]

    async with CrawlAndStoreService(collection_name="my_tech_docs") as service:
        results = []

        for url, source_id, max_depth in sources:
            print(f"\nIngesting: {source_id} from {url}")

            result = await service.ingest_url(
                url=url,
                source_id=source_id,
                max_depth=max_depth
            )

            results.append({
                "source_id": source_id,
                "success": result["success"],
                "pages": result["crawl"]["total_pages"],
                "chunks": result["storage"]["chunks_stored"]
            })

        # Print summary
        print("\n=== Ingestion Summary ===")
        for res in results:
            status = "✓" if res["success"] else "✗"
            print(f"{status} {res['source_id']}: {res['pages']} pages, {res['chunks']} chunks")

        # Get collection stats
        stats = await service.get_stats()
        print(f"\nTotal vectors in collection: {stats.get('vectors_count', 0)}")


# Example 4: Search after ingestion
async def example_ingest_and_search():
    """
    Example: Ingest a source and immediately search it.
    """
    print("\n=== Example 4: Ingest and Search ===")

    async with CrawlAndStoreService() as service:
        # Ingest
        result = await service.ingest_url(
            url="https://docs.pydantic.dev/latest/",
            source_id="pydantic_v2",
            max_depth=2
        )

        if result["success"]:
            print(f"✓ Ingested {result['storage']['chunks_stored']} chunks\n")

            # Search within this source
            search_results = await service.search(
                query="How do I validate data with Pydantic?",
                limit=3,
                source_id="pydantic_v2"
            )

            print(f"Search results: {len(search_results)} found\n")

            for i, res in enumerate(search_results, 1):
                print(f"{i}. Score: {res['score']:.3f}")
                print(f"   Title: {res['title']}")
                print(f"   URL: {res['url']}")
                print(f"   Content: {res['content'][:150]}...")
                print()


# Example 5: Error handling
async def example_error_handling():
    """
    Example: Robust error handling for production use.
    """
    print("\n=== Example 5: Error Handling ===")

    async with CrawlAndStoreService() as service:
        urls_to_ingest = [
            ("https://valid-docs.example.com", "valid_docs"),
            ("https://invalid-url-that-doesnt-exist.com", "invalid_docs"),
            ("https://another-valid-site.com", "another_docs"),
        ]

        successful = []
        failed = []

        for url, source_id in urls_to_ingest:
            try:
                result = await service.ingest_url(
                    url=url,
                    source_id=source_id,
                    max_depth=1
                )

                if result["success"]:
                    successful.append(source_id)
                    print(f"✓ {source_id}: {result['storage']['chunks_stored']} chunks")
                else:
                    failed.append((source_id, result["error"]))
                    print(f"✗ {source_id}: {result['error']}")

            except Exception as e:
                failed.append((source_id, str(e)))
                print(f"✗ {source_id}: Exception - {str(e)}")

        # Summary
        print(f"\nSuccessful: {len(successful)}")
        print(f"Failed: {len(failed)}")


# Example 6: Using convenience function
async def example_convenience_function():
    """
    Example: One-liner ingestion with convenience function.
    """
    print("\n=== Example 6: Convenience Function ===")

    result = await ingest_url(
        url="https://www.python.org/dev/peps/pep-0008/",
        source_id="pep8",
        max_depth=1
    )

    if result["success"]:
        print(f"✓ Ingested PEP 8 documentation")
        print(f"  Chunks: {result['storage']['chunks_stored']}")
    else:
        print(f"✗ Failed: {result['error']}")


# Example 7: Custom configuration
async def example_custom_config():
    """
    Example: Custom Qdrant URL and chunking configuration.
    """
    print("\n=== Example 7: Custom Configuration ===")

    # Custom settings for larger documents
    service = CrawlAndStoreService(
        qdrant_url="http://localhost:6333",
        collection_name="large_docs",
        default_max_depth=3,
        default_chunk_size=1200,  # Larger chunks
        chunk_overlap=200          # More overlap
    )

    async with service:
        result = await service.ingest_url(
            url="https://longform-content.example.com",
            source_id="longform"
        )

        print(f"Result: {result['success']}")


# Example 8: Source management
async def example_source_management():
    """
    Example: Managing sources - update, delete, get stats.
    """
    print("\n=== Example 8: Source Management ===")

    async with CrawlAndStoreService() as service:
        # Ingest initial version
        print("Ingesting v1...")
        result = await service.ingest_url(
            url="https://docs.example.com/v1/",
            source_id="example_v1",
            max_depth=2
        )
        print(f"v1: {result['storage']['chunks_stored']} chunks")

        # Later, update to v2 (delete old, ingest new)
        print("\nUpdating to v2...")
        deleted = await service.delete_source("example_v1")
        print(f"Deleted {deleted} old chunks")

        result = await service.ingest_url(
            url="https://docs.example.com/v2/",
            source_id="example_v2",
            max_depth=2
        )
        print(f"v2: {result['storage']['chunks_stored']} chunks")

        # Get stats
        stats = await service.get_stats()
        print(f"\nCollection stats: {stats}")


# Example 9: Real-world production pattern
async def example_production_pattern():
    """
    Example: Production-ready pattern with comprehensive monitoring.
    """
    print("\n=== Example 9: Production Pattern ===")

    import time

    start_time = time.time()
    metrics = {
        "total_pages": 0,
        "total_chunks": 0,
        "failed_sources": []
    }

    def progress_callback(stage: str, percentage: int, metadata: Dict[str, Any]):
        """Log progress to monitoring system."""
        # In production, send to Datadog, Prometheus, etc.
        print(f"[METRIC] stage={stage} progress={percentage}% metadata={metadata}")

    async with CrawlAndStoreService() as service:
        sources = [
            "https://docs.python.org/3/",
            "https://fastapi.tiangolo.com/",
            "https://pydantic-docs.helpmanual.io/",
        ]

        for url in sources:
            try:
                source_id = service._generate_source_id(url)

                result = await service.ingest_url(
                    url=url,
                    source_id=source_id,
                    max_depth=2,
                    progress_callback=progress_callback
                )

                if result["success"]:
                    metrics["total_pages"] += result["crawl"]["total_pages"]
                    metrics["total_chunks"] += result["storage"]["chunks_stored"]
                else:
                    metrics["failed_sources"].append({
                        "url": url,
                        "error": result["error"]
                    })

            except Exception as e:
                metrics["failed_sources"].append({
                    "url": url,
                    "error": str(e)
                })

        # Report metrics
        duration = time.time() - start_time
        print(f"\n=== Metrics Report ===")
        print(f"Duration: {duration:.2f}s")
        print(f"Pages ingested: {metrics['total_pages']}")
        print(f"Chunks stored: {metrics['total_chunks']}")
        print(f"Failed sources: {len(metrics['failed_sources'])}")

        if metrics["failed_sources"]:
            print("\nFailures:")
            for failure in metrics["failed_sources"]:
                print(f"  - {failure['url']}: {failure['error']}")


# Main runner
async def main():
    """
    Run all examples (comment out as needed).
    """
    print("CrawlAndStoreService Examples")
    print("=" * 50)

    # Uncomment the examples you want to run:

    # await example_basic_usage()
    # await example_with_progress()
    # await example_batch_processing()
    # await example_ingest_and_search()
    # await example_error_handling()
    # await example_convenience_function()
    # await example_custom_config()
    # await example_source_management()
    # await example_production_pattern()

    print("\n=== Examples Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
