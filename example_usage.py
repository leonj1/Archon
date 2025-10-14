"""
Example Usage: CrawlAndStoreService

This file demonstrates how to use the unified service once it's been created by the agents.

Run this AFTER all agents have completed successfully.
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def example_basic_usage():
    """Basic usage: Crawl a single URL and store in Qdrant."""
    print("\n" + "="*60)
    print("Example 1: Basic Single URL Crawl")
    print("="*60 + "\n")

    # Import the service (created by agent 3)
    from python.src.server.services.crawl_and_store_service import CrawlAndStoreService

    # Create service instance
    service = CrawlAndStoreService()

    # Crawl and store a single documentation page
    url = "https://docs.python.org/3/library/asyncio.html"
    print(f"Crawling: {url}")

    result = await service.crawl_and_store(url)

    # Display results
    print(f"\n✓ Success: {result['success']}")
    print(f"\nCrawl Stats:")
    print(f"  - Documents crawled: {len(result['crawl']['documents'])}")
    print(f"  - Total pages: {result['crawl'].get('total_pages', 'N/A')}")

    print(f"\nStorage Stats:")
    print(f"  - Chunks stored: {result['storage']['chunks_stored']}")
    print(f"  - Source ID: {result['storage']['source_id']}")


async def example_recursive_crawl():
    """Recursive crawl with depth limit."""
    print("\n" + "="*60)
    print("Example 2: Recursive Crawl (max_depth=2)")
    print("="*60 + "\n")

    from python.src.server.services.crawl_and_store_service import CrawlAndStoreService

    service = CrawlAndStoreService()

    # Crawl with depth=2 to follow internal links
    url = "https://docs.pydantic.dev/"
    print(f"Recursively crawling: {url} (depth=2)")

    result = await service.crawl_and_store(
        url,
        max_depth=2,
        chunk_size=3000  # Smaller chunks
    )

    print(f"\n✓ Crawled {len(result['crawl']['documents'])} pages")
    print(f"✓ Stored {result['storage']['chunks_stored']} vector chunks")


async def example_custom_source_id():
    """Use a custom source ID for organization."""
    print("\n" + "="*60)
    print("Example 3: Custom Source ID")
    print("="*60 + "\n")

    from python.src.server.services.crawl_and_store_service import CrawlAndStoreService

    service = CrawlAndStoreService()

    url = "https://fastapi.tiangolo.com/"
    custom_source_id = "fastapi-docs-2024"

    print(f"Crawling: {url}")
    print(f"Source ID: {custom_source_id}")

    result = await service.crawl_and_store(
        url,
        source_id=custom_source_id
    )

    print(f"\n✓ Stored under source ID: {result['storage']['source_id']}")
    print(f"✓ {result['storage']['chunks_stored']} chunks in vector database")


async def example_error_handling():
    """Demonstrate error handling."""
    print("\n" + "="*60)
    print("Example 4: Error Handling")
    print("="*60 + "\n")

    from python.src.server.services.crawl_and_store_service import CrawlAndStoreService

    service = CrawlAndStoreService()

    # Try crawling an invalid URL
    bad_url = "https://this-site-does-not-exist-12345.com"
    print(f"Attempting to crawl invalid URL: {bad_url}")

    try:
        result = await service.crawl_and_store(bad_url)

        if not result['success']:
            print(f"\n✗ Crawl failed as expected")
            print(f"Error details: {result.get('error', 'Unknown error')}")
        else:
            print(f"\n✓ Unexpectedly succeeded")
    except Exception as e:
        print(f"\n✗ Exception raised (expected): {type(e).__name__}")
        print(f"   Message: {str(e)}")


async def example_search_vectors():
    """Search the stored vectors (demonstrates retrieval)."""
    print("\n" + "="*60)
    print("Example 5: Searching Stored Vectors")
    print("="*60 + "\n")

    # First, store some data
    from python.src.server.services.crawl_and_store_service import CrawlAndStoreService

    service = CrawlAndStoreService()

    url = "https://docs.python.org/3/library/asyncio-task.html"
    print(f"Step 1: Crawling and storing {url}")

    result = await service.crawl_and_store(url)
    source_id = result['storage']['source_id']

    print(f"✓ Stored {result['storage']['chunks_stored']} chunks")

    # Now search the vectors
    print(f"\nStep 2: Searching for 'asyncio coroutines'")

    from python.src.server.services.simple_vectordb_service import SimpleVectorDBService

    vectordb = SimpleVectorDBService()

    # Generate query embedding
    from python.src.server.services.embeddings.embedding_service import create_embeddings_batch

    query = "How do I create asyncio coroutines in Python?"
    query_result = await create_embeddings_batch([query])
    query_embedding = query_result.embeddings[0]

    # Search
    search_results = await vectordb.search_similar(
        query_embedding=query_embedding,
        limit=3,
        source_filter=source_id
    )

    print(f"\nFound {len(search_results)} relevant chunks:")
    for i, result in enumerate(search_results, 1):
        print(f"\n  Result {i}:")
        print(f"    Score: {result['score']:.4f}")
        print(f"    URL: {result['url']}")
        print(f"    Content preview: {result['content'][:100]}...")


async def main():
    """Run all examples."""
    print("\n" + "🚀 " + "="*56)
    print("    CrawlAndStoreService Usage Examples")
    print("="*60 + "\n")

    print("Prerequisites:")
    print("  ✓ Qdrant running on localhost:6333")
    print("  ✓ OPENAI_API_KEY set in environment")
    print("  ✓ All agent services created")
    print()

    # Check prerequisites
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set in environment")
        return

    try:
        import requests
        response = requests.get("http://localhost:6333/collections", timeout=2)
        if response.status_code != 200:
            print("❌ Error: Qdrant not responding correctly")
            return
    except Exception as e:
        print(f"❌ Error: Cannot connect to Qdrant - {e}")
        print("   Start with: docker run -p 6333:6333 qdrant/qdrant")
        return

    # Run examples
    try:
        await example_basic_usage()
        await asyncio.sleep(1)

        await example_recursive_crawl()
        await asyncio.sleep(1)

        await example_custom_source_id()
        await asyncio.sleep(1)

        await example_error_handling()
        await asyncio.sleep(1)

        await example_search_vectors()

    except ImportError as e:
        print(f"\n❌ Error: Could not import service - {e}")
        print("   Run the agents first: python create_vectordb_agents.py")
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print("✓ Examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
