"""
Example Usage: SimpleVectorDBService Integration

This example demonstrates how to use SimpleVectorDBService with SimpleCrawlingService
to crawl websites and store them in Qdrant vector database.
"""

import asyncio
from simple_vectordb_service import SimpleVectorDBService, store_crawled_documents
from ..simple_crawling_service import SimpleCrawlingService, crawl_url


async def example_basic_workflow():
    """
    Basic workflow: Crawl a website and store in vector database.
    """
    print("=== Basic Workflow Example ===\n")

    # Step 1: Crawl a website
    print("1. Crawling website...")
    documents = await crawl_url("https://docs.python.org/3/tutorial/", max_depth=2)
    print(f"   Crawled {len(documents)} documents\n")

    # Step 2: Store in vector database
    print("2. Storing in Qdrant...")
    result = await store_crawled_documents(
        documents=documents,
        source_id="python_tutorial"
    )

    print(f"   Stored {result['chunks_stored']} chunks")
    print(f"   From {result['documents_processed']} documents")
    print(f"   Failed chunks: {result['failed_chunks']}\n")


async def example_with_service_management():
    """
    Advanced workflow with explicit service management and search.
    """
    print("=== Advanced Workflow Example ===\n")

    # Initialize services
    crawler = SimpleCrawlingService()
    vectordb = SimpleVectorDBService(
        qdrant_url="http://localhost:6333",
        collection_name="my_docs",
        chunk_size=800,
        chunk_overlap=100
    )

    try:
        # Step 1: Crawl multiple sources
        print("1. Crawling multiple sources...")

        docs1 = await crawler.crawl("https://fastapi.tiangolo.com/", max_depth=1)
        print(f"   - FastAPI docs: {len(docs1)} pages")

        docs2 = await crawler.crawl("https://www.python.org/dev/peps/pep-0008/", max_depth=1)
        print(f"   - PEP 8: {len(docs2)} pages\n")

        # Step 2: Store each source separately
        print("2. Storing in vector database...")

        result1 = await vectordb.store_documents(docs1, source_id="fastapi_docs")
        print(f"   - FastAPI: {result1['chunks_stored']} chunks")

        result2 = await vectordb.store_documents(docs2, source_id="pep8")
        print(f"   - PEP 8: {result2['chunks_stored']} chunks\n")

        # Step 3: Get collection stats
        print("3. Collection statistics:")
        stats = await vectordb.get_stats()
        print(f"   - Vectors: {stats.get('vectors_count', 0)}")
        print(f"   - Status: {stats.get('status', 'unknown')}\n")

        # Step 4: Search for content
        print("4. Searching for content...")

        # Search across all sources
        results = await vectordb.search(
            query="How do I define API routes?",
            limit=3
        )

        print("   Results (all sources):")
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result['title']} (score: {result['score']:.3f})")
            print(f"      URL: {result['url']}")
            print(f"      Content preview: {result['content'][:100]}...\n")

        # Search within specific source
        results = await vectordb.search(
            query="naming conventions",
            limit=3,
            source_id="pep8"
        )

        print("   Results (PEP 8 only):")
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result['title']} (score: {result['score']:.3f})")
            print(f"      Content preview: {result['content'][:100]}...\n")

        # Step 5: Delete a source
        print("5. Cleaning up...")
        deleted = await vectordb.delete_by_source("pep8")
        print(f"   Deleted {deleted} vectors for source 'pep8'\n")

    finally:
        # Always clean up
        await crawler.close()
        await vectordb.close()
        print("Services closed successfully")


async def example_error_handling():
    """
    Demonstrate error handling and validation.
    """
    print("=== Error Handling Example ===\n")

    vectordb = SimpleVectorDBService()

    try:
        # Test with invalid document format
        print("1. Testing with invalid document format...")
        try:
            invalid_docs = [
                {"url": "http://example.com"}  # Missing 'title' and 'content'
            ]
            await vectordb.store_documents(invalid_docs, "test")
        except ValueError as e:
            print(f"   ✓ Caught expected error: {e}\n")

        # Test with empty content
        print("2. Testing with empty content...")
        empty_docs = [
            {
                "url": "http://example.com",
                "title": "Empty Doc",
                "content": "",  # Empty content
                "metadata": {}
            }
        ]
        result = await vectordb.store_documents(empty_docs, "test")
        print(f"   ✓ Handled gracefully: {result['chunks_stored']} chunks stored\n")

        # Test with empty search query
        print("3. Testing with empty search query...")
        try:
            await vectordb.search("")
        except ValueError as e:
            print(f"   ✓ Caught expected error: {e}\n")

    finally:
        await vectordb.close()


async def example_custom_chunking():
    """
    Demonstrate custom chunking parameters.
    """
    print("=== Custom Chunking Example ===\n")

    # Create service with custom chunk settings
    vectordb = SimpleVectorDBService(
        collection_name="custom_chunks",
        chunk_size=1024,  # Larger chunks (~256 tokens)
        chunk_overlap=200  # More overlap for better context
    )

    try:
        # Crawl and store with custom chunking
        docs = await crawl_url("https://example.com")

        result = await vectordb.store_documents(
            documents=docs,
            source_id="example_com",
            chunk_size=512  # Override instance setting
        )

        print(f"Stored {result['chunks_stored']} chunks with custom settings")

    finally:
        await vectordb.close()


async def example_batch_processing():
    """
    Demonstrate processing multiple sources in parallel.
    """
    print("=== Batch Processing Example ===\n")

    crawler = SimpleCrawlingService()
    vectordb = SimpleVectorDBService(collection_name="batch_docs")

    try:
        # Define multiple sources to crawl
        sources = [
            ("https://docs.python.org/3/tutorial/", "python_tutorial"),
            ("https://fastapi.tiangolo.com/", "fastapi_docs"),
            ("https://www.sqlalchemy.org/", "sqlalchemy_docs")
        ]

        # Crawl all sources concurrently
        print("1. Crawling sources concurrently...")
        crawl_tasks = [
            crawler.crawl(url, max_depth=1)
            for url, _ in sources
        ]
        all_docs = await asyncio.gather(*crawl_tasks, return_exceptions=True)

        # Store each successfully crawled source
        print("2. Storing documents...\n")
        for i, (docs, (url, source_id)) in enumerate(zip(all_docs, sources)):
            if isinstance(docs, Exception):
                print(f"   ✗ Failed to crawl {url}: {docs}")
                continue

            result = await vectordb.store_documents(docs, source_id)
            print(f"   ✓ {source_id}: {result['chunks_stored']} chunks")

        print(f"\n3. Final statistics:")
        stats = await vectordb.get_stats()
        print(f"   Total vectors: {stats.get('vectors_count', 0)}")

    finally:
        await crawler.close()
        await vectordb.close()


# Run examples
if __name__ == "__main__":
    print("SimpleVectorDBService Examples\n")
    print("=" * 50 + "\n")

    # Run basic workflow
    asyncio.run(example_basic_workflow())

    # Uncomment to run other examples:
    # asyncio.run(example_with_service_management())
    # asyncio.run(example_error_handling())
    # asyncio.run(example_custom_chunking())
    # asyncio.run(example_batch_processing())
