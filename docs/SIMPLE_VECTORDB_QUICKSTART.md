# SimpleVectorDBService Quick Start

## Installation Complete ✅

**File Created**: `/home/jose/src/Archon/python/src/server/services/storage/simple_vectordb_service.py`

**Lines of Code**: 685 (including documentation)

---

## Quick Usage

### Basic Example
```python
from server.services.simple_crawling_service import crawl_url
from server.services.storage.simple_vectordb_service import store_crawled_documents

# 1. Crawl a website
docs = await crawl_url("https://docs.python.org", max_depth=2)

# 2. Store in vector database
result = await store_crawled_documents(
    documents=docs,
    source_id="python_docs"
)

print(f"Stored {result['chunks_stored']} chunks")
```

### Advanced Example with Search
```python
from server.services.storage.simple_vectordb_service import SimpleVectorDBService

# Initialize
vectordb = SimpleVectorDBService(
    qdrant_url="http://localhost:6333",
    collection_name="my_docs"
)

try:
    # Store documents
    result = await vectordb.store_documents(crawled_docs, "my_source")

    # Search
    results = await vectordb.search(
        query="How do I authenticate?",
        limit=5
    )

    for r in results:
        print(f"{r['title']}: {r['content'][:100]}...")

finally:
    await vectordb.close()
```

---

## API Reference

### Constructor
```python
SimpleVectorDBService(
    qdrant_url: str = "http://localhost:6333",
    collection_name: str = "archon_simple_docs",
    chunk_size: int = 800,        # ~200 tokens
    chunk_overlap: int = 100      # ~25 tokens
)
```

### Primary Methods

#### store_documents()
```python
await vectordb.store_documents(
    documents: List[Dict],  # From SimpleCrawlingService
    source_id: str,         # Unique source identifier
    chunk_size: int = None  # Optional override
) -> Dict[str, Any]
```

**Returns**:
```python
{
    "chunks_stored": 42,
    "source_id": "my_source",
    "documents_processed": 10,
    "failed_chunks": 0
}
```

#### search()
```python
await vectordb.search(
    query: str,              # Search query
    limit: int = 5,          # Max results
    source_id: str = None    # Optional filter
) -> List[Dict[str, Any]]
```

**Returns**:
```python
[
    {
        "id": "uuid",
        "score": 0.89,
        "url": "https://...",
        "title": "Page Title",
        "content": "chunk text...",
        "chunk_number": 0,
        "metadata": {...}
    }
]
```

#### delete_by_source()
```python
deleted_count = await vectordb.delete_by_source("source_id")
```

#### get_stats()
```python
stats = await vectordb.get_stats()
# Returns: {"vectors_count": 100, "status": "green", ...}
```

---

## Document Format

**SimpleCrawlingService Output** (100% compatible):
```python
{
    "url": "https://example.com/page",
    "title": "Page Title",
    "content": "Markdown formatted content...",
    "metadata": {
        "content_length": 5000,
        "crawl_type": "recursive",
        "links": {...},
        "depth": 1
    }
}
```

---

## Dependencies

**Required Services**:
- Qdrant server running on localhost:6333 (or custom URL)
- OpenAI API key configured (for embeddings)

**Python Packages**:
- `qdrant-client` (via QdrantVectorService)
- `openai` (via embedding_service)
- `asyncio` (standard library)
- `uuid` (standard library)

---

## Configuration

### Chunk Size
- **Default**: 800 chars (~200 tokens)
- **Range**: 400-2000 chars recommended
- **Overlap**: 100 chars default (maintains context)

### Collection Name
- **Default**: `"archon_simple_docs"`
- **Custom**: Pass to constructor

### Qdrant URL
- **Default**: `"http://localhost:6333"`
- **Docker**: Use container name or `host.docker.internal`

---

## Error Handling

All methods raise clear exceptions:

```python
try:
    result = await vectordb.store_documents(docs, "source")
except ValueError as e:
    # Invalid document format
    print(f"Validation error: {e}")
except RuntimeError as e:
    # Storage or API failure
    print(f"Runtime error: {e}")
```

---

## Performance Notes

### Chunking
- **Speed**: ~1ms per document for typical sizes
- **Memory**: Linear with document count

### Embeddings
- **Bottleneck**: OpenAI API rate limits
- **Batch size**: 100 (automatic)
- **Rate limiting**: Handled automatically

### Qdrant Storage
- **Speed**: Single batch upsert per store_documents() call
- **Network**: Local deployment recommended

---

## Complete Example

```python
import asyncio
from server.services.simple_crawling_service import SimpleCrawlingService
from server.services.storage.simple_vectordb_service import SimpleVectorDBService

async def main():
    # Initialize services
    crawler = SimpleCrawlingService()
    vectordb = SimpleVectorDBService(
        collection_name="python_docs"
    )

    try:
        # 1. Crawl website
        print("Crawling...")
        docs = await crawler.crawl(
            "https://docs.python.org/3/tutorial/",
            max_depth=2
        )
        print(f"Crawled {len(docs)} pages")

        # 2. Store in vector database
        print("Storing...")
        result = await vectordb.store_documents(
            documents=docs,
            source_id="python_tutorial"
        )
        print(f"Stored {result['chunks_stored']} chunks")

        # 3. Search
        print("Searching...")
        results = await vectordb.search(
            query="How do I define functions?",
            limit=3
        )

        for i, r in enumerate(results, 1):
            print(f"\n{i}. {r['title']}")
            print(f"   Score: {r['score']:.3f}")
            print(f"   Content: {r['content'][:100]}...")

    finally:
        # Cleanup
        await crawler.close()
        await vectordb.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Next Steps

1. **Test with your data**:
   ```bash
   cd /home/jose/src/Archon/python
   python -m src.server.services.storage.simple_vectordb_example
   ```

2. **Create wrapper service** (see SIMPLE_VECTORDB_INTEGRATION.md)

3. **Add tests**:
   - Unit tests for chunking
   - Integration tests with Qdrant
   - End-to-end crawl-to-search tests

4. **Enhancements**:
   - URL-based deduplication (see recommendations)
   - Token counting with tiktoken
   - Progress tracking for long operations

---

## Troubleshooting

### Qdrant Connection Error
```bash
# Start Qdrant with Docker
docker run -p 6333:6333 qdrant/qdrant
```

### OpenAI API Errors
```bash
# Check API key
echo $OPENAI_API_KEY

# Or set in code
import os
os.environ["OPENAI_API_KEY"] = "sk-..."
```

### Empty Search Results
- Check that documents were stored: `await vectordb.get_stats()`
- Verify source_id matches
- Try broader query terms

---

## Full Documentation

See `/home/jose/src/Archon/SIMPLE_VECTORDB_INTEGRATION.md` for:
- Detailed compatibility analysis
- Performance benchmarks
- Architecture decisions
- Known issues and recommendations
- Wrapper service design
