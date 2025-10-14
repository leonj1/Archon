# SQLite + Qdrant Integration Test

## Overview

This integration test demonstrates the complete end-to-end workflow for Archon's hybrid storage architecture:

1. **Crawling**: Web crawling using Crawl4AI (PocketFlow GitHub repository)
2. **Metadata Storage**: SQLite repository for structured data and relationships
3. **Vector Storage**: Qdrant for semantic search with embeddings
4. **Search**: MCP-style search combining SQL metadata with vector similarity

## Architecture

```
┌─────────────────┐
│   Web Crawling  │  (Crawl4AI)
└────────┬────────┘
         │
         ├─────────────────────────────────┐
         │                                 │
         v                                 v
┌─────────────────┐              ┌─────────────────┐
│  SQLite Storage │              │ Embedding Gen   │
│   (Metadata)    │              │    (OpenAI)     │
└─────────────────┘              └────────┬────────┘
                                          │
                                          v
                                 ┌─────────────────┐
                                 │ Qdrant Storage  │
                                 │   (Vectors)     │
                                 └─────────────────┘
                                          │
                                          v
                                 ┌─────────────────┐
                                 │  Semantic Search │
                                 │   (MCP Tools)    │
                                 └─────────────────┘
```

## Requirements

### Environment Variables

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### Dependencies

Install required packages:

```bash
cd python
uv sync --group all
```

This installs:
- `qdrant-client>=1.7.0` - Qdrant vector database client
- `aiosqlite>=0.17.0` - Async SQLite support
- `openai>=1.71.0` - OpenAI embeddings
- `crawl4ai==0.7.4` - Web crawling
- Test dependencies (pytest, pytest-asyncio, etc.)

### Qdrant Setup

#### Option 1: In-Memory Mode (Default for Tests)

The test uses in-memory Qdrant by default - no setup required.

#### Option 2: Docker (For Production Testing)

```bash
docker run -d -p 6333:6333 qdrant/qdrant:latest
```

Then modify the test to use `url="http://localhost:6333"` instead of `url=":memory:"`.

## Running the Test

### Run the Full Integration Test

```bash
# From the python/ directory
uv run pytest tests/integration/test_sqlite_qdrant_crawl_mcp.py -v -s

# Or run directly
uv run python -m pytest tests/integration/test_sqlite_qdrant_crawl_mcp.py -v -s
```

### Run Specific Test Cases

```bash
# Only the full workflow test
uv run pytest tests/integration/test_sqlite_qdrant_crawl_mcp.py::TestSQLiteQdrantCrawlMCP::test_full_crawl_storage_search_workflow -v -s

# Only Qdrant lifecycle test
uv run pytest tests/integration/test_sqlite_qdrant_crawl_mcp.py::TestSQLiteQdrantCrawlMCP::test_qdrant_collection_lifecycle -v -s

# Only SQLite operations test
uv run pytest tests/integration/test_sqlite_qdrant_crawl_mcp.py::TestSQLiteQdrantCrawlMCP::test_sqlite_repository_basic_operations -v -s
```

### Test Output

The test provides detailed console output showing each step:

```
================================================================================
STEP 1: Crawling PocketFlow GitHub Repository
================================================================================
✓ Crawl started: task_id=..., status=started
✓ Crawl completed successfully

================================================================================
STEP 2: Validating SQLite Storage
================================================================================
✓ Found 1 source(s) in SQLite
✓ Source ID: src_...
✓ Found 15 document chunk(s) in SQLite

📄 Sample Document:
  - URL: https://github.com/The-Pocket/PocketFlow
  - Chunk #: 0
  - Content preview: PocketFlow is a...

================================================================================
STEP 3: Generating Embeddings and Storing in Qdrant
================================================================================
✓ Preparing 15 documents for embedding...
✓ Generating embeddings (this may take a moment)...
✓ Generated 15 embeddings
✓ Embedding dimension: 1536 (expected: 1536)
✓ Storing embeddings in Qdrant...
✓ Stored 15 vectors in Qdrant

📊 Qdrant Collection Stats:
  - Name: test_archon_docs
  - Vectors count: 15
  - Points count: 15
  - Status: green

================================================================================
STEP 4: Performing Semantic Search
================================================================================
🔍 Query: 'what is PocketFlow about?'
✓ Generated query embedding (dim: 1536)
✓ Found 3 relevant results

🎯 Search Results:
  Result #1:
    - Score: 0.8523
    - URL: https://github.com/The-Pocket/PocketFlow
    - Chunk: #0
    - Preview: PocketFlow is a...

================================================================================
STEP 5: MCP-Style Search Validation
================================================================================
✓ MCP would see 1 available source(s)
✓ MCP would return 3 enriched results
✓ MCP response structure validated

================================================================================
✅ INTEGRATION TEST COMPLETED SUCCESSFULLY
================================================================================

Summary:
  - Crawled URL: https://github.com/The-Pocket/PocketFlow
  - SQLite Documents: 15
  - Qdrant Vectors: 15
  - Search Results: 3
  - MCP Results: 3
  - Top Result Score: 0.8523
```

## Test Components

### 1. Crawling Service

Uses `CrawlingService` with SQLite repository to crawl the PocketFlow GitHub repository:
- Max depth: 1 (configurable)
- Code extraction: Disabled for speed (configurable)
- Storage: SQLite for metadata

### 2. SQLite Repository

Stores:
- **Sources**: Knowledge source metadata
- **Documents**: Chunked content with URLs and metadata
- **Code Examples**: Extracted code snippets (if enabled)

### 3. Qdrant Vector Service

Stores:
- **Embeddings**: 1536-dimensional vectors (OpenAI text-embedding-3-small)
- **Payload**: Document metadata for filtering
- **Index**: Cosine similarity search

### 4. Embedding Service

Generates embeddings using OpenAI:
- Model: `text-embedding-3-small`
- Dimension: 1536
- Batch processing supported

### 5. MCP-Style Search

Simulates MCP tool behavior:
1. List available sources (SQLite)
2. Generate query embedding (OpenAI)
3. Search vectors (Qdrant)
4. Enrich results with full metadata (SQLite)
5. Return formatted results

## Troubleshooting

### Test Timeout

The test has a 5-minute timeout. If it fails with timeout:
- Check network connectivity for crawling
- Verify OpenAI API key is valid
- Reduce `max_depth` in the crawl request

### Embedding Errors

If embedding generation fails:
```
AssertionError: Embedding count mismatch
```

Check:
- OPENAI_API_KEY is set and valid
- OpenAI API is accessible
- Rate limits are not exceeded

### Qdrant Connection Issues

If using Docker Qdrant and getting connection errors:
```bash
# Check Qdrant is running
docker ps | grep qdrant

# Check Qdrant health
curl http://localhost:6333/health
```

### SQLite Issues

If database initialization fails:
- Check write permissions in temp directory
- Verify `aiosqlite` is installed
- Check schema migration files exist

## Performance Notes

- **Crawling**: ~10-30 seconds depending on depth and page count
- **Embedding Generation**: ~2-5 seconds per batch of 10 documents
- **Vector Storage**: <1 second for typical document counts
- **Search**: <100ms for typical queries

## Extending the Test

### Test Different URLs

Modify the `target_url` in the test:

```python
target_url = "https://docs.your-site.com"  # Your URL here
```

### Adjust Crawl Depth

Increase `max_depth` for deeper crawling (slower):

```python
crawl_request = {
    "url": target_url,
    "max_depth": 3,  # Crawl 3 levels deep
    ...
}
```

### Enable Code Extraction

Enable code example extraction:

```python
crawl_request = {
    "url": target_url,
    "extract_code_examples": True,  # Extract code blocks
    ...
}
```

### Use Production Qdrant

Modify the `qdrant_service` fixture:

```python
@pytest.fixture
async def qdrant_service():
    service = QdrantVectorService(
        url="http://localhost:6333",  # Production Qdrant
        collection_name="test_archon_docs"
    )
    yield service
    await service.close()
```

## Integration with Archon

This test architecture can be integrated into Archon's production code:

1. **Repository Pattern**: Already using `DatabaseRepository` interface
2. **Vector Service**: Add `QdrantVectorService` alongside existing storage services
3. **Hybrid Search**: Combine SQLite metadata queries with Qdrant vector search
4. **MCP Tools**: Extend RAG tools to support Qdrant backend

See `src/server/services/storage/qdrant_vector_service.py` for the production-ready service implementation.
