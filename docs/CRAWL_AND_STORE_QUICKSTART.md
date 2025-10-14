# CrawlAndStoreService Quick Start Guide

## TL;DR

```python
from server.services.storage.crawl_and_store_service import CrawlAndStoreService

async with CrawlAndStoreService() as service:
    # Ingest documentation
    result = await service.ingest_url(
        url="https://docs.example.com",
        source_id="example_docs",
        max_depth=2
    )

    # Search
    results = await service.search("how to authenticate?")
```

---

## Installation & Setup

### 1. Ensure Dependencies Are Running

```bash
# Start Qdrant (required for vector storage)
docker compose up -d qdrant

# Verify Qdrant is running
curl http://localhost:6333/collections
```

### 2. Set Environment Variables

```bash
# OpenAI API key (required for embeddings)
export OPENAI_API_KEY="sk-..."

# Optional: Custom Qdrant URL
export QDRANT_URL="http://localhost:6333"
```

---

## Basic Usage

### Example 1: Simple Ingestion

```python
from server.services.storage.crawl_and_store_service import ingest_url

# One-liner ingestion
result = await ingest_url(
    url="https://docs.python.org",
    source_id="python_docs",
    max_depth=2
)

if result["success"]:
    print(f"✓ Stored {result['storage']['chunks_stored']} chunks")
else:
    print(f"✗ Failed: {result['error']}")
```

### Example 2: With Context Manager

```python
from server.services.storage.crawl_and_store_service import CrawlAndStoreService

async with CrawlAndStoreService() as service:
    # Ingest
    result = await service.ingest_url(
        url="https://fastapi.tiangolo.com",
        source_id="fastapi_docs",
        max_depth=3
    )

    # Search
    results = await service.search(
        query="dependency injection",
        limit=5,
        source_id="fastapi_docs"
    )

    for result in results:
        print(f"{result['title']}: {result['score']:.2f}")
```

### Example 3: Batch Processing

```python
async with CrawlAndStoreService() as service:
    sources = [
        ("https://docs.python.org", "python_docs", 2),
        ("https://pydantic-docs.helpmanual.io", "pydantic_docs", 2),
    ]

    for url, source_id, depth in sources:
        result = await service.ingest_url(url, source_id, depth)
        print(f"{source_id}: {result['storage']['chunks_stored']} chunks")
```

---

## API Reference

### Initialize Service

```python
service = CrawlAndStoreService(
    qdrant_url="http://localhost:6333",      # Qdrant server
    collection_name="my_knowledge_base",     # Collection name
    default_max_depth=2,                     # Default crawl depth
    default_chunk_size=800,                  # Chunk size (chars)
    chunk_overlap=100                        # Overlap (chars)
)
```

### Ingest URL

```python
result = await service.ingest_url(
    url="https://example.com",               # Required: URL to crawl
    source_id="example_docs",                # Optional: auto-generated if None
    max_depth=2,                             # Optional: crawl depth (1=single page)
    chunk_size=800,                          # Optional: override chunk size
    max_concurrent=10,                       # Optional: concurrent requests
    progress_callback=callback_func          # Optional: progress tracking
)

# Result format:
{
    "success": bool,
    "crawl": {
        "documents": List[Dict],
        "total_pages": int,
        "crawl_type": str
    },
    "storage": {
        "chunks_stored": int,
        "source_id": str,
        "documents_processed": int,
        "failed_chunks": int
    },
    "error": str | None
}
```

### Search

```python
results = await service.search(
    query="authentication methods",          # Required: search query
    limit=5,                                 # Optional: max results
    source_id="example_docs"                 # Optional: filter by source
)

# Result format:
[
    {
        "id": str,
        "score": float,
        "url": str,
        "title": str,
        "content": str,
        "chunk_number": int,
        "metadata": dict
    }
]
```

### Delete Source

```python
deleted_count = await service.delete_source("old_docs")
print(f"Deleted {deleted_count} vectors")
```

### Get Stats

```python
stats = await service.get_stats()
print(f"Vectors: {stats.get('vectors_count', 0)}")
```

---

## Progress Tracking

### Simple Progress Callback

```python
def progress_callback(stage: str, percentage: int, metadata: dict):
    """
    Stages: "crawling", "validating", "storing", "completed"
    Percentage: 0-100
    Metadata: Stage-specific info
    """
    print(f"[{percentage:3d}%] {stage.upper()}: {metadata}")

async with CrawlAndStoreService() as service:
    result = await service.ingest_url(
        url="https://example.com",
        progress_callback=progress_callback
    )
```

### Async Progress Callback

```python
async def async_progress_callback(stage: str, percentage: int, metadata: dict):
    # Send to monitoring system
    await monitoring_service.report_progress(stage, percentage)

result = await service.ingest_url(
    url="https://example.com",
    progress_callback=async_progress_callback
)
```

---

## Error Handling

### Pattern 1: Check Success Flag

```python
result = await service.ingest_url("https://example.com", "example")

if result["success"]:
    print(f"Success: {result['storage']['chunks_stored']} chunks")
else:
    print(f"Failed: {result['error']}")
    # Handle failure (retry, log, alert, etc.)
```

### Pattern 2: Try-Except for Critical Errors

```python
try:
    result = await service.ingest_url("https://example.com", "example")
except ValueError as e:
    # URL validation error
    print(f"Invalid input: {e}")
except RuntimeError as e:
    # Service initialization or critical connection error
    print(f"Critical error: {e}")
```

### Pattern 3: Batch with Error Tolerance

```python
async with CrawlAndStoreService() as service:
    successful = []
    failed = []

    for url, source_id in urls:
        try:
            result = await service.ingest_url(url, source_id)
            if result["success"]:
                successful.append(source_id)
            else:
                failed.append((source_id, result["error"]))
        except Exception as e:
            failed.append((source_id, str(e)))

    print(f"Successful: {len(successful)}, Failed: {len(failed)}")
```

---

## Configuration

### Custom Chunking

```python
# Larger chunks for long-form content
service = CrawlAndStoreService(
    default_chunk_size=1200,  # 300 tokens approx
    chunk_overlap=200         # 50 tokens approx
)
```

### Custom Collection

```python
# Separate collections for different purposes
service = CrawlAndStoreService(
    collection_name="technical_docs"
)
```

### Custom Qdrant

```python
# Remote Qdrant instance
service = CrawlAndStoreService(
    qdrant_url="http://qdrant.example.com:6333"
)
```

---

## Performance Tips

### 1. Crawl Depth

```python
# Faster: Single page
result = await service.ingest_url(url, max_depth=1)

# Slower: Deep crawl
result = await service.ingest_url(url, max_depth=5)
```

### 2. Concurrent Requests

```python
# Faster crawling (if target site allows)
result = await service.ingest_url(
    url="https://example.com",
    max_concurrent=20  # Default: 10
)
```

### 3. Chunk Size

```python
# Fewer chunks = faster embedding generation
service = CrawlAndStoreService(default_chunk_size=1200)
```

### 4. Parallel Sources

```python
import asyncio

async with CrawlAndStoreService() as service:
    tasks = [
        service.ingest_url(url1, "source1"),
        service.ingest_url(url2, "source2"),
        service.ingest_url(url3, "source3"),
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
```

---

## Troubleshooting

### Issue: "Failed to initialize CrawlAndStoreService"

**Cause**: Qdrant not running or wrong URL

**Fix**:
```bash
# Check Qdrant
curl http://localhost:6333/collections

# Start if needed
docker compose up -d qdrant
```

### Issue: "Embedding generation failed"

**Cause**: Missing or invalid OpenAI API key

**Fix**:
```bash
export OPENAI_API_KEY="sk-..."
```

### Issue: "No documents were crawled from the URL"

**Cause**: Invalid URL, site blocking, or no content

**Fix**:
- Verify URL is accessible
- Check if site blocks bots
- Try single page first (max_depth=1)

### Issue: "No chunks were successfully stored"

**Cause**: Content too short or all chunks failed embedding

**Fix**:
- Check document content length
- Review logs for embedding errors
- Verify OpenAI API quota

---

## Production Checklist

- [ ] Qdrant deployed and accessible
- [ ] OpenAI API key configured
- [ ] Monitoring for progress callbacks
- [ ] Error alerting configured
- [ ] Rate limiting considered
- [ ] Backup strategy for Qdrant
- [ ] Resource limits set (memory, CPU)
- [ ] Integration tests passing
- [ ] Performance baseline established

---

## Common Patterns

### Pattern: Update Documentation

```python
async with CrawlAndStoreService() as service:
    # Delete old version
    await service.delete_source("docs_v1")

    # Ingest new version
    result = await service.ingest_url(
        "https://docs.example.com/v2/",
        source_id="docs_v2",
        max_depth=3
    )
```

### Pattern: Multi-Source Search

```python
async with CrawlAndStoreService() as service:
    # Ingest multiple sources
    await service.ingest_url("https://docs.python.org", "python")
    await service.ingest_url("https://fastapi.tiangolo.com", "fastapi")

    # Search across all sources
    results = await service.search("async functions")
```

### Pattern: Source-Specific Search

```python
# Search only in specific source
results = await service.search(
    query="dependency injection",
    source_id="fastapi"  # Only search FastAPI docs
)
```

---

## File Locations

- **Service**: `/home/jose/src/Archon/python/src/server/services/storage/crawl_and_store_service.py`
- **Examples**: `/home/jose/src/Archon/python/src/server/services/storage/crawl_and_store_example.py`
- **Full Report**: `/home/jose/src/Archon/CRAWL_AND_STORE_SERVICE_REPORT.md`

---

## Support

For detailed implementation notes, see:
- Full report: `CRAWL_AND_STORE_SERVICE_REPORT.md`
- Integration analysis: `SIMPLE_VECTORDB_INTEGRATION.md`
- Example code: `crawl_and_store_example.py` (9 examples)
