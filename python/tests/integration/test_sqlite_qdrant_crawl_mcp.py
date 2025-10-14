"""
Integration Test: SQLite + Qdrant + Crawling + MCP Search

This test demonstrates the complete end-to-end flow:
1. Crawl website (PocketFlow GitHub repo)
2. Store metadata in SQLite using repository interface
3. Generate embeddings and store in Qdrant
4. Validate document counts
5. Use MCP client to search the knowledge base

Requirements:
- OPENAI_API_KEY environment variable must be set
- Qdrant must be running on localhost:6333 (or use in-memory mode)
"""

import os
import tempfile
from pathlib import Path

import pytest
from crawl4ai import AsyncWebCrawler

from src.server.repositories.sqlite_repository import SQLiteDatabaseRepository
from src.server.services.crawling.crawling_service import CrawlingService
from src.server.services.embeddings.embedding_service import create_embeddings_batch

# Check for optional dependencies
try:
    import qdrant_client
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

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


@pytest.fixture
async def temp_db_path():
    """Create a temporary SQLite database file."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    yield db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
async def sqlite_repository(temp_db_path):
    """Create and initialize SQLite repository."""
    repo = SQLiteDatabaseRepository(db_path=temp_db_path)

    # Manually create tables instead of using migration file
    async with repo._get_connection(skip_init=True) as conn:
        # Create essential tables for the test
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS archon_sources (
                source_id TEXT PRIMARY KEY,
                source_url TEXT,
                source_display_name TEXT,
                summary TEXT,
                title TEXT,
                metadata TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS archon_crawled_pages (
                id TEXT PRIMARY KEY,
                url TEXT,
                chunk_number INTEGER,
                content TEXT,
                metadata TEXT,
                source_id TEXT,
                created_at TEXT,
                FOREIGN KEY (source_id) REFERENCES archon_sources(source_id)
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS archon_page_metadata (
                id TEXT PRIMARY KEY,
                url TEXT,
                section_title TEXT,
                word_count INTEGER,
                source_id TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Add settings table for credential service
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS archon_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                description TEXT,
                updated_at TEXT
            )
        """)

        # Insert OpenAI API key into settings if available
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            import json
            from datetime import datetime
            await conn.execute("""
                INSERT OR REPLACE INTO archon_settings (key, value, updated_at)
                VALUES (?, ?, ?)
            """, ("OPENAI_API_KEY", json.dumps(openai_key), datetime.now().isoformat()))

        await conn.commit()

    # Mark as initialized to skip further initialization attempts
    repo._initialized = True

    yield repo

    # No explicit cleanup needed - file will be deleted by temp_db_path fixture


@pytest.fixture
def qdrant_service():
    """Create Qdrant vector service (in-memory mode for testing)."""
    # Use in-memory Qdrant for testing (synchronous client)
    from qdrant_client import QdrantClient

    # Create in-memory Qdrant client
    client = QdrantClient(location=":memory:")
    collection_name = "test_archon_docs"

    # Create a wrapper that mimics QdrantVectorService interface
    class InMemoryQdrantService:
        def __init__(self, client, collection_name):
            self.client = client
            self.collection_name = collection_name
            self.embedding_dimension = 1536

        async def ensure_collection(self, dimension=1536):
            """Ensure collection exists."""
            from qdrant_client.models import Distance, VectorParams

            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)

            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=dimension, distance=Distance.COSINE)
                )

        async def store_embeddings(self, documents, embeddings):
            """Store document embeddings in Qdrant."""
            import uuid
            from qdrant_client.models import PointStruct

            points = []
            for doc, embedding in zip(documents, embeddings):
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "document_id": doc.get("id"),
                        "url": doc.get("url"),
                        "content": doc.get("content"),
                        "chunk_number": doc.get("chunk_number", 0),
                        "source_id": doc.get("source_id"),
                    }
                )
                points.append(point)

            # Ensure collection exists
            await self.ensure_collection(dimension=len(embeddings[0]))

            # Upsert points
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            return [p.id for p in points]

        async def search_similar(self, query_embedding, limit=5, source_filter=None):
            """Search for similar documents using vector similarity."""
            # Build filter if source_filter provided
            query_filter = None
            if source_filter:
                from qdrant_client.models import Filter, FieldCondition, MatchValue

                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="source_id",
                            match=MatchValue(value=source_filter)
                        )
                    ]
                )

            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter=query_filter
            )

            # Convert to expected format
            results = []
            for result in search_results:
                results.append({
                    "document_id": result.payload.get("document_id"),
                    "url": result.payload.get("url"),
                    "content": result.payload.get("content"),
                    "chunk_number": result.payload.get("chunk_number"),
                    "source_id": result.payload.get("source_id"),
                    "score": result.score
                })

            return results

        async def get_collection_info(self):
            """Get collection information."""
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status.value if hasattr(info.status, 'value') else str(info.status)
            }

    service = InMemoryQdrantService(client, collection_name)

    yield service

    # Cleanup - delete collection
    try:
        client.delete_collection(collection_name)
    except:
        pass


@pytest.fixture
async def crawler():
    """Create Crawl4AI crawler instance."""
    async with AsyncWebCrawler(verbose=False) as crawler_instance:
        yield crawler_instance


@pytest.fixture
async def crawling_service(crawler, sqlite_repository):
    """Create crawling service with SQLite repository."""
    service = CrawlingService(
        crawler=crawler,
        repository=sqlite_repository,
        progress_id=None  # No progress tracking for test
    )
    return service


class TestSQLiteQdrantCrawlMCP:
    """Integration tests for SQLite + Qdrant + Crawling + MCP workflow."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(300)  # 5 minute timeout for crawling
    async def test_full_crawl_storage_search_workflow(
        self,
        crawling_service: CrawlingService,
        sqlite_repository: SQLiteDatabaseRepository,
        qdrant_service
    ):
        """
        Test complete workflow: crawl → SQLite → Qdrant → search.

        This test:
        1. Crawls PocketFlow GitHub repository
        2. Stores metadata in SQLite
        3. Generates embeddings and stores in Qdrant
        4. Validates document counts
        5. Performs semantic search via Qdrant
        """

        # Step 1: Crawl the PocketFlow GitHub repository
        print("\n" + "="*80)
        print("STEP 1: Crawling PocketFlow GitHub Repository")
        print("="*80)

        target_url = "https://github.com/The-Pocket/PocketFlow"
        crawl_request = {
            "url": target_url,
            "knowledge_type": "documentation",
            "tags": ["github", "pocketflow", "test"],
            "max_depth": 1,  # Limit depth for faster testing
            "extract_code_examples": False,  # Disable for faster testing
        }

        # Perform crawl (non-blocking)
        result = await crawling_service.orchestrate_crawl(crawl_request)
        print(f"✓ Crawl started: task_id={result['task_id']}, status={result['status']}")

        # Wait for crawl task to complete
        crawl_task = result.get("task")
        if crawl_task:
            try:
                await crawl_task
                print("✓ Crawl completed successfully")
            except Exception as e:
                pytest.fail(f"Crawl failed: {e}")

        # Step 2: Verify data in SQLite
        print("\n" + "="*80)
        print("STEP 2: Validating SQLite Storage")
        print("="*80)

        # Get all sources
        sources = await sqlite_repository.list_sources()
        assert len(sources) > 0, "No sources found in SQLite"
        print(f"✓ Found {len(sources)} source(s) in SQLite")

        # Get the crawled source
        source = sources[0]
        source_id = source.get("source_id")
        print(f"✓ Source ID: {source_id}")
        print(f"✓ Source URL: {source.get('source_url')}")
        print(f"✓ Source Name: {source.get('source_display_name')}")

        # Get documents for this source
        documents = await sqlite_repository.get_documents_by_source(source_id)
        assert len(documents) > 0, "No documents found for source"
        print(f"✓ Found {len(documents)} document chunk(s) in SQLite")

        # Display sample document
        if documents:
            sample_doc = documents[0]
            print(f"\n📄 Sample Document:")
            print(f"  - URL: {sample_doc.get('url')}")
            print(f"  - Chunk #: {sample_doc.get('chunk_number')}")
            print(f"  - Content preview: {sample_doc.get('content', '')[:100]}...")

        # Step 3: Generate embeddings and store in Qdrant
        print("\n" + "="*80)
        print("STEP 3: Generating Embeddings and Storing in Qdrant")
        print("="*80)

        # Prepare document texts for embedding
        doc_texts = [doc.get("content", "") for doc in documents]
        print(f"✓ Preparing {len(doc_texts)} documents for embedding...")

        # Generate embeddings using OpenAI
        print("✓ Generating embeddings (this may take a moment)...")
        batch_result = await create_embeddings_batch(texts=doc_texts)
        embeddings = batch_result.embeddings

        assert len(embeddings) == len(documents), f"Embedding count mismatch: {len(embeddings)} vs {len(documents)}"
        print(f"✓ Generated {len(embeddings)} embeddings")
        print(f"✓ Embedding dimension: {len(embeddings[0])} (expected: 1536)")

        if batch_result.has_failures:
            print(f"⚠️  Warning: {batch_result.failure_count} embeddings failed")
            for failure in batch_result.failed_items[:3]:  # Show first 3 failures
                print(f"   - {failure.get('error_type')}: {failure.get('error')}")

        # Store in Qdrant
        print("✓ Storing embeddings in Qdrant...")
        point_ids = await qdrant_service.store_embeddings(
            documents=documents,
            embeddings=embeddings
        )
        assert len(point_ids) == len(documents), "Point ID count mismatch"
        print(f"✓ Stored {len(point_ids)} vectors in Qdrant")

        # Verify Qdrant collection
        collection_info = await qdrant_service.get_collection_info()
        print(f"\n📊 Qdrant Collection Stats:")
        print(f"  - Name: {collection_info['name']}")
        print(f"  - Vectors count: {collection_info['vectors_count']}")
        print(f"  - Points count: {collection_info['points_count']}")
        print(f"  - Status: {collection_info['status']}")

        assert collection_info['points_count'] == len(documents), "Qdrant point count mismatch"

        # Step 4: Perform semantic search
        print("\n" + "="*80)
        print("STEP 4: Performing Semantic Search")
        print("="*80)

        # Test query
        test_query = "what is PocketFlow about?"
        print(f"🔍 Query: '{test_query}'")

        # Generate query embedding
        query_batch_result = await create_embeddings_batch(texts=[test_query])
        assert len(query_batch_result.embeddings) > 0, "Failed to generate query embedding"
        query_embedding = query_batch_result.embeddings[0]
        print(f"✓ Generated query embedding (dim: {len(query_embedding)})")

        # Search Qdrant
        search_results = await qdrant_service.search_similar(
            query_embedding=query_embedding,
            limit=3,
            source_filter=source_id
        )

        assert len(search_results) > 0, "No search results found"
        print(f"✓ Found {len(search_results)} relevant results")

        # Display search results
        print(f"\n🎯 Search Results:")
        for i, result in enumerate(search_results, 1):
            print(f"\n  Result #{i}:")
            print(f"    - Score: {result['score']:.4f}")
            print(f"    - URL: {result['url']}")
            print(f"    - Chunk: #{result['chunk_number']}")
            print(f"    - Preview: {result['content'][:150]}...")

        # Step 5: Validate MCP-style search (simulated)
        print("\n" + "="*80)
        print("STEP 5: MCP-Style Search Validation")
        print("="*80)

        # Simulate what MCP tool would do:
        # 1. Get available sources
        sources_list = await sqlite_repository.list_sources()
        print(f"✓ MCP would see {len(sources_list)} available source(s)")

        # 2. Search for documents (combining SQLite metadata + Qdrant vectors)
        mcp_search_results = []
        for search_result in search_results:
            # Get full document from SQLite
            doc_id = search_result['document_id']
            full_doc = await sqlite_repository.get_document_by_id(doc_id)

            if full_doc:
                mcp_search_results.append({
                    "url": full_doc.get("url"),
                    "content": full_doc.get("content"),
                    "similarity_score": search_result['score'],
                    "chunk_number": full_doc.get("chunk_number"),
                    "source_id": full_doc.get("source_id"),
                })

        print(f"✓ MCP would return {len(mcp_search_results)} enriched results")

        # Validate MCP response structure
        for result in mcp_search_results:
            assert "url" in result, "MCP result missing 'url'"
            assert "content" in result, "MCP result missing 'content'"
            assert "similarity_score" in result, "MCP result missing 'similarity_score'"
            assert result['similarity_score'] > 0, "Invalid similarity score"

        print("✓ MCP response structure validated")

        # Final Summary
        print("\n" + "="*80)
        print("✅ INTEGRATION TEST COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f"\nSummary:")
        print(f"  - Crawled URL: {target_url}")
        print(f"  - SQLite Documents: {len(documents)}")
        print(f"  - Qdrant Vectors: {collection_info['points_count']}")
        print(f"  - Search Results: {len(search_results)}")
        print(f"  - MCP Results: {len(mcp_search_results)}")
        print(f"  - Top Result Score: {search_results[0]['score']:.4f}")
        print("\n" + "="*80 + "\n")

    @pytest.mark.asyncio
    async def test_qdrant_collection_lifecycle(self, qdrant_service):
        """Test Qdrant collection creation and management."""

        # Ensure collection exists
        await qdrant_service.ensure_collection(dimension=1536)

        # Get collection info
        info = await qdrant_service.get_collection_info()
        assert info['name'] == qdrant_service.collection_name
        assert info['status'] in ['green', 'yellow', 'unknown']

        print(f"✓ Collection '{info['name']}' is ready (status: {info['status']})")

    @pytest.mark.asyncio
    async def test_sqlite_repository_basic_operations(
        self,
        sqlite_repository: SQLiteDatabaseRepository
    ):
        """Test basic SQLite repository operations."""

        # Test source creation
        source_data = {
            "source_id": "test_src_001",
            "source_url": "https://example.com/test",
            "source_display_name": "Test Source",
            "summary": "Test summary",
            "title": "Test Title",
        }

        created_source = await sqlite_repository.upsert_source(source_data)
        assert created_source['source_id'] == "test_src_001"
        print(f"✓ Created test source: {created_source['source_id']}")

        # Test document insertion
        doc_data = {
            "id": "test_doc_001",
            "url": "https://example.com/test",
            "chunk_number": 0,
            "content": "This is a test document for validation.",
            "metadata": {"test": True},
            "source_id": "test_src_001",
        }

        created_doc = await sqlite_repository.insert_document(doc_data)
        assert created_doc['id'] == "test_doc_001"
        print(f"✓ Created test document: {created_doc['id']}")

        # Test retrieval
        retrieved_doc = await sqlite_repository.get_document_by_id("test_doc_001")
        assert retrieved_doc is not None
        assert retrieved_doc['content'] == doc_data['content']
        print(f"✓ Retrieved document successfully")

        # Test cleanup
        deleted_count = await sqlite_repository.delete_documents_by_source("test_src_001")
        assert deleted_count > 0
        print(f"✓ Cleaned up {deleted_count} document(s)")


if __name__ == "__main__":
    # Allow running the test directly with: python -m pytest test_sqlite_qdrant_crawl_mcp.py -v -s
    pytest.main([__file__, "-v", "-s"])
