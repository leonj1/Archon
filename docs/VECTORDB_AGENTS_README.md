# Vector Database Pipeline Agents

This document explains how to use the Claude Code Agent SDK to build a complete web crawling and vector database pipeline.

## Overview

The `create_vectordb_agents.py` script creates 5 specialized agents that work together to build a production-ready crawling and vector storage system:

```
┌─────────────────────────────────────────────────────────────┐
│                    Pipeline Architecture                     │
└─────────────────────────────────────────────────────────────┘

   1. SimpleCrawlingService          ─┐
      (Web Crawling)                   │
                                       ├─→ 3. CrawlAndStoreService
   2. SimpleVectorDBService           │      (Unified API)
      (Qdrant Storage)                ─┘

   4. Integration Test                5. Test Validator
      (Real API calls)                   (Quality Check)
```

## Prerequisites

### Environment Setup

1. **Install dependencies:**
   ```bash
   cd python
   uv sync --group all
   ```

2. **Environment variables (.env):**
   ```bash
   ANTHROPIC_API_KEY=your_anthropic_key_here
   OPENAI_API_KEY=your_openai_key_here
   QDRANT_URL=http://localhost:6333  # Optional, defaults to localhost
   ```

3. **Start Qdrant (if not running):**
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```

### Verify Setup

```bash
# Check Qdrant is running
curl http://localhost:6333/collections

# Check Python environment
cd python && uv run python --version
```

## The Five Agents

### Agent 1: Crawling Service Builder

**Purpose:** Creates `SimpleCrawlingService` class for web crawling

**What it creates:**
- File: `python/src/server/services/simple_crawling_service.py`
- Simplified crawling API that reuses existing codebase patterns
- Handles single pages, recursive crawling, and sitemaps
- Returns structured documents: `[{"url": str, "content": str, "title": str}]`

**Key features:**
- Analyzes existing `crawling_service.py` for patterns
- Async implementation with type hints
- Proper error handling and logging
- Under 300 lines of clean code

**Run it:**
```bash
python create_vectordb_agents.py --agent crawling-service-builder
```

---

### Agent 2: VectorDB Service Builder

**Purpose:** Creates `SimpleVectorDBService` class for Qdrant vector storage

**What it creates:**
- File: `python/src/server/services/simple_vectordb_service.py`
- Chunks documents into smaller pieces
- Generates embeddings using OpenAI API
- Stores vectors in Qdrant
- Returns statistics: `{"chunks_stored": int, "source_id": str}`

**Key features:**
- Reuses existing chunking and embedding logic
- Configurable chunk size (default: 5000 characters)
- Batch processing for efficiency
- Integration with existing `QdrantVectorService`

**Run it:**
```bash
python create_vectordb_agents.py --agent vectordb-service-builder
```

---

### Agent 3: Wrapper Service Builder

**Purpose:** Creates `CrawlAndStoreService` unified wrapper

**What it creates:**
- File: `python/src/server/services/crawl_and_store_service.py`
- Single API that combines crawling + storage
- Method: `async def crawl_and_store(url: str, **kwargs)`
- Returns complete results: `{"crawl": {...}, "storage": {...}, "success": bool}`

**Key features:**
- Composes both services via dependency injection
- Progress tracking and status updates
- Graceful error handling
- Easy-to-use API with minimal configuration

**Usage example:**
```python
service = CrawlAndStoreService()
result = await service.crawl_and_store(
    "https://example.com",
    max_depth=2,
    chunk_size=3000
)
```

**Run it:**
```bash
python create_vectordb_agents.py --agent wrapper-service-builder
```

---

### Agent 4: Integration Test Builder

**Purpose:** Creates real integration test with actual API calls

**What it creates:**
- File: `python/tests/integration/test_crawl_and_store_real.py`
- Tests complete pipeline with REAL external services:
  - Real crawling of https://github.com/The-Pocket/PocketFlow
  - Real OpenAI API calls for embeddings
  - Real Qdrant vector storage
- **NO MOCKS** - this is true integration testing

**Test structure:**
```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_real_crawl_and_store():
    """Real crawl, real embeddings, real storage"""
    # Arrange
    service = CrawlAndStoreService()

    # Act
    result = await service.crawl_and_store("https://github.com/The-Pocket/PocketFlow")

    # Assert
    assert result["success"] is True
    assert result["storage"]["chunks_stored"] > 0
    # ... more assertions

    # Cleanup
    # Delete test data from Qdrant
```

**Key features:**
- Uses real HTTP requests, real APIs, real storage
- Proper cleanup in teardown
- Skips if `OPENAI_API_KEY` not set
- Self-contained and idempotent

**Run it:**
```bash
python create_vectordb_agents.py --agent integration-test-builder
```

---

### Agent 5: Test Validator

**Purpose:** Validates the integration test and ensures quality

**What it does:**
1. Runs the integration test
2. Validates test implementation quality
3. Checks for anti-patterns
4. Creates validation report

**Validation checklist:**
- ✓ Test passes successfully
- ✓ Uses real external calls (no mocks)
- ✓ Proper cleanup logic
- ✓ Clear assertion messages
- ✓ `@pytest.mark.integration` marker present
- ✓ No hardcoded secrets
- ✓ No test pollution

**What it creates:**
- File: `python/tests/integration/VALIDATION_REPORT.md`
- Detailed validation report with:
  - Test execution summary
  - Confirmed behaviors
  - Recommendations for improvement
  - Confirmation that NO MOCKS are used

**Run it:**
```bash
python create_vectordb_agents.py --agent test-validator
```

---

## Usage

### Interactive Mode (Recommended)

Run the script without arguments to see an interactive menu:

```bash
python create_vectordb_agents.py
```

You'll see:
```
🤖 Vector DB Pipeline Agent Builder

Available agents:

  1️⃣  Create SimpleCrawlingService (web crawling)
  2️⃣  Create SimpleVectorDBService (Qdrant storage)
  3️⃣  Create CrawlAndStoreService (unified wrapper)
  4️⃣  Create integration test (real API calls)
  5️⃣  Validate test passes and check quality
  6️⃣  Exit

Select an agent to run [1]:
```

### Sequential Mode (Recommended Workflow)

Build the complete pipeline step-by-step:

```bash
# Step 1: Create crawling service
python create_vectordb_agents.py --agent crawling-service-builder

# Step 2: Create vector storage service
python create_vectordb_agents.py --agent vectordb-service-builder

# Step 3: Create unified wrapper
python create_vectordb_agents.py --agent wrapper-service-builder

# Step 4: Create integration test
python create_vectordb_agents.py --agent integration-test-builder

# Step 5: Validate everything works
python create_vectordb_agents.py --agent test-validator
```

### Running the Integration Test Manually

After all services are created:

```bash
cd python

# Run the integration test
uv run pytest tests/integration/test_crawl_and_store_real.py -v -s

# Run with markers
uv run pytest -m integration tests/integration/test_crawl_and_store_real.py
```

### Using the Unified Service

After all services are built, you can use the unified API:

```python
from python.src.server.services.crawl_and_store_service import CrawlAndStoreService

async def main():
    service = CrawlAndStoreService()

    result = await service.crawl_and_store(
        url="https://docs.python.org/3/library/asyncio.html",
        max_depth=2,
        chunk_size=5000
    )

    print(f"✓ Crawled {len(result['crawl']['documents'])} documents")
    print(f"✓ Stored {result['storage']['chunks_stored']} vector chunks")
    print(f"✓ Source ID: {result['storage']['source_id']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Architecture Decisions

### Why Separate Services?

1. **Crawling Service** - Can be used independently for just web scraping
2. **VectorDB Service** - Can be used to vectorize any documents, not just crawled ones
3. **Wrapper Service** - Provides convenience API while keeping components decoupled

### Why Real Integration Tests?

- **Confidence:** Tests prove the system works end-to-end with real dependencies
- **Early Detection:** Catches API changes, network issues, configuration problems
- **Documentation:** Integration tests serve as living documentation of the system
- **Production Parity:** Tests the actual code path that will run in production

### Why Use Claude Code Agents?

- **Context-Aware:** Agents analyze your existing codebase and follow patterns
- **Iterative:** Agents can read, write, test, and refine code
- **Best Practices:** Agents apply software engineering principles consistently
- **Time-Saving:** Automates boilerplate while maintaining code quality

## Expected File Structure

After running all agents, you'll have:

```
python/
├── src/
│   └── server/
│       └── services/
│           ├── simple_crawling_service.py      # Agent 1 output
│           ├── simple_vectordb_service.py      # Agent 2 output
│           └── crawl_and_store_service.py      # Agent 3 output
│
└── tests/
    └── integration/
        ├── test_crawl_and_store_real.py        # Agent 4 output
        └── VALIDATION_REPORT.md                # Agent 5 output
```

## Troubleshooting

### Agent Not Finding Files

**Issue:** Agent can't locate existing codebase files

**Solution:**
```bash
# Ensure you're in the project root
pwd  # Should show .../Archon

# Verify files exist
ls python/src/server/services/crawling/
```

### Integration Test Fails

**Issue:** Test fails with API errors

**Check:**
1. Is Qdrant running? `curl http://localhost:6333/collections`
2. Is `OPENAI_API_KEY` set? `echo $OPENAI_API_KEY`
3. Internet connection available?

**Run test with verbose output:**
```bash
cd python
uv run pytest tests/integration/test_crawl_and_store_real.py -v -s --log-cli-level=DEBUG
```

### Qdrant Connection Errors

**Issue:** Can't connect to Qdrant

**Solution:**
```bash
# Start Qdrant in Docker
docker run -d -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant

# Verify it's running
curl http://localhost:6333/collections
```

### OpenAI API Rate Limits

**Issue:** Test fails with rate limit errors

**Solution:**
- Wait a few seconds between test runs
- Reduce chunk size to generate fewer embeddings
- Use a higher-tier OpenAI API key

## Advanced Usage

### Customizing Agent Prompts

Edit `create_vectordb_agents.py` to modify agent behavior:

```python
# In create_agent_options()
agents={
    "crawling-service-builder": AgentDefinition(
        description="...",
        prompt="""
        YOUR CUSTOM INSTRUCTIONS HERE

        Additional requirements:
        - Use specific library X
        - Follow pattern Y
        """,
        model=model,
        tools=[...]
    )
}
```

### Using Different Models

```bash
# Use Claude Opus for more complex reasoning
python create_vectordb_agents.py --model opus --agent wrapper-service-builder

# Use Haiku for faster, simpler tasks
python create_vectordb_agents.py --model haiku --agent test-validator
```

### Running All Agents in Sequence

Create a bash script:

```bash
#!/bin/bash
# run_all_agents.sh

AGENTS=(
    "crawling-service-builder"
    "vectordb-service-builder"
    "wrapper-service-builder"
    "integration-test-builder"
    "test-validator"
)

for agent in "${AGENTS[@]}"; do
    echo "Running $agent..."
    python create_vectordb_agents.py --agent "$agent"
    echo "✓ $agent completed"
    echo "---"
done

echo "🎉 All agents completed!"
```

Then run:
```bash
chmod +x run_all_agents.sh
./run_all_agents.sh
```

## Next Steps

After successfully running all agents:

1. **Review the generated code** - Ensure it meets your requirements
2. **Run the integration test** - Verify everything works end-to-end
3. **Add to your API** - Expose the `CrawlAndStoreService` via FastAPI endpoints
4. **Create unit tests** - Add focused unit tests for edge cases
5. **Add monitoring** - Integrate with your logging/metrics system
6. **Deploy to production** - Use the validated service in your application

## Contributing

To add new agents to this pipeline:

1. Define a new `AgentDefinition` in `create_agent_options()`
2. Add the agent to the `agent_descriptions` dictionary
3. Add a prompt mapping in the `prompts` dictionary
4. Update this README with agent documentation

## License

This script is part of the Archon project and follows the same license.

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the Claude Code SDK docs: https://docs.claude.com/en/api/agent-sdk
- Check Archon project documentation

---

**Happy building! 🚀**
