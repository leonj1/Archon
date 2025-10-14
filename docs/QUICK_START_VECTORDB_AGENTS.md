# Quick Start: Vector DB Pipeline Agents

Get up and running in 5 minutes.

## 1. Prerequisites (2 minutes)

```bash
# Install dependencies
cd python
uv sync --group all
cd ..

# Install Claude Code SDK
pip install claude-agent-sdk

# Start Qdrant (docker-compose)
./start_vectordb.sh
```

## 2. Environment Setup (1 minute)

Create `.env` file in project root:

```bash
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx
QDRANT_URL=http://localhost:6333
```

## 3. Run All Agents (2 minutes)

### Option A: Automated (Recommended)

```bash
./run_all_vectordb_agents.sh
```

This will create all 5 services sequentially.

### Option B: Interactive

```bash
python create_vectordb_agents.py
# Select agents 1-5 in order
```

### Option C: Manual

```bash
# Run each agent individually
python create_vectordb_agents.py --agent crawling-service-builder
python create_vectordb_agents.py --agent vectordb-service-builder
python create_vectordb_agents.py --agent wrapper-service-builder
python create_vectordb_agents.py --agent integration-test-builder
python create_vectordb_agents.py --agent test-validator
```

## 4. Verify Setup (30 seconds)

```bash
# Run the integration test
cd python
uv run pytest tests/integration/test_crawl_and_store_real.py -v

# If it passes, you're ready to go! 🎉
```

## 5. Use the Service (1 minute)

```python
# example.py
import asyncio
from python.src.server.services.crawl_and_store_service import CrawlAndStoreService

async def main():
    service = CrawlAndStoreService()
    result = await service.crawl_and_store("https://docs.python.org/3/")
    print(f"Stored {result['storage']['chunks_stored']} chunks!")

asyncio.run(main())
```

## Troubleshooting

### "Module not found"
```bash
# Ensure you're in project root
pwd  # Should show .../Archon
```

### "Can't connect to Qdrant"
```bash
# Start Qdrant
./start_vectordb.sh

# Check if running
curl http://localhost:6333/collections

# Check container status
docker compose -f docker-compose.vectordb.yml ps

# View logs
docker compose -f docker-compose.vectordb.yml logs -f
```

### "OpenAI API key not found"
```bash
# Check environment
echo $OPENAI_API_KEY

# Or add to .env file
echo "OPENAI_API_KEY=sk-xxx" >> .env
```

## What Gets Created

After running all agents:

```
python/src/server/services/
├── simple_crawling_service.py       # Web crawler
├── simple_vectordb_service.py       # Qdrant storage
└── crawl_and_store_service.py       # Unified API

python/tests/integration/
├── test_crawl_and_store_real.py     # Integration test
└── VALIDATION_REPORT.md             # Test validation
```

## Next Steps

- ✅ Review generated code
- ✅ Run `python example_usage.py` for examples
- ✅ Add to your FastAPI endpoints
- ✅ Deploy to production

## Full Documentation

See `VECTORDB_AGENTS_README.md` for detailed documentation.

---

**Total setup time: ~5 minutes** ⚡
