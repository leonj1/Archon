# 🚀 Vector DB Pipeline Builder - START HERE

## What Is This?

A **Claude Code Agent SDK** system that orchestrates 5 specialized AI agents to build a production-ready web crawling and vector database pipeline with **real-time feedback loops** between agents.

## ⭐ Two Approaches Available

### 🎯 Recommended: Single Orchestrated Session (NEW!)

**File:** `build_vectordb_pipeline.py`

One command that runs all agents with inter-agent communication:
- Agents review each other's work
- Early issue detection and fixes
- Real-time feedback and coordination
- Shared context between agents

```bash
python build_vectordb_pipeline.py --model sonnet
```

**Read:** `BUILD_PIPELINE_README.md` for details

### 📦 Alternative: Multi-Script Approach (Original)

**Files:** `create_vectordb_agents.py` + `run_all_vectordb_agents.sh`

Sequential execution of separate agents:
- Each agent runs independently
- No inter-agent feedback
- Issues found at the end
- Manual coordination needed

```bash
./run_all_vectordb_agents.sh
```

**Read:** `VECTORDB_AGENTS_README.md` for details

---

## Quick Comparison

| Feature | Single Session (NEW) | Multi-Script (Original) |
|---------|---------------------|------------------------|
| **Feedback loops** | ✅ Yes | ❌ No |
| **Early issue detection** | ✅ Yes | ❌ No |
| **Agent communication** | ✅ Yes | ❌ No |
| **Coordinated fixes** | ✅ Yes | ❌ Manual |
| **Real-time progress** | ✅ Yes | ⚠️ Limited |
| **Context sharing** | ✅ Yes | ❌ No |
| **Commands to run** | 1 | 5+ |

**Recommendation:** Use `build_vectordb_pipeline.py` (single session) for better results!

## 📦 What You Get

5 specialized AI agents that build:

1. **Web Crawling Service** - Extracts content from any URL
2. **Vector Storage Service** - Chunks and stores in Qdrant
3. **Unified Wrapper Service** - Simple API combining both
4. **Integration Test** - Real test with actual APIs (no mocks)
5. **Test Validator** - Ensures quality and correctness

**Total:** ~720 lines of production-ready Python code, automatically generated.

## ⚡ Quick Start (3 minutes)

### Step 1: Prerequisites (1 min)

```bash
# Install Python dependencies
cd python && uv sync --group all && cd ..

# Install Claude SDK
pip install claude-agent-sdk

# Start Qdrant (automatically via docker-compose)
./start_vectordb.sh

# Set environment variables in .env
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx
```

**Note:** Qdrant data persists in `./qdrant_storage` directory.

### Step 2: Build Pipeline (1 min)

```bash
# Single command with feedback loops (RECOMMENDED)
python build_vectordb_pipeline.py --model sonnet
```

Watch as agents:
- Build services with real-time feedback
- Review each other's work
- Catch and fix issues early
- Validate the complete pipeline

### Step 3: Use It (30 sec)

```python
import asyncio
from python.src.server.services.crawl_and_store_service import CrawlAndStoreService

async def main():
    service = CrawlAndStoreService()
    result = await service.crawl_and_store("https://example.com")
    print(f"Stored {result['storage']['chunks_stored']} chunks!")

asyncio.run(main())
```

## 📚 Documentation

| File | Purpose | When to Read |
|------|---------|--------------|
| **BUILD_PIPELINE_README.md** | ⭐ Single session guide (NEW!) | **Read this first for recommended approach** |
| **build_vectordb_pipeline.py** | ⭐ Orchestrated builder (NEW!) | **Run this for best results** |
| **QUICK_START_VECTORDB_AGENTS.md** | Multi-script quick setup | For sequential approach |
| **VECTORDB_AGENTS_README.md** | Multi-script full docs | For detailed sequential approach |
| **VECTORDB_AGENTS_SUMMARY.md** | Project summary | High-level overview |
| **VECTORDB_AGENTS_ARCHITECTURE.txt** | Visual diagrams | Understand architecture |
| **example_usage.py** | 5 working examples | See it in action |
| **create_vectordb_agents.py** | Multi-script orchestrator | Sequential approach |
| **run_all_vectordb_agents.sh** | Sequential automation | Run all scripts in order |

## 🎯 What Gets Created

After running agents, you'll have:

```
python/src/server/services/
├── simple_crawling_service.py      # Web crawler
├── simple_vectordb_service.py      # Qdrant storage
└── crawl_and_store_service.py      # Unified API

python/tests/integration/
├── test_crawl_and_store_real.py    # Integration test
└── VALIDATION_REPORT.md            # Test validation
```

## 🔑 Key Features

✅ **Zero Manual Coding** - Agents write all the code
✅ **Follows Your Patterns** - Analyzes existing codebase
✅ **Production Ready** - Error handling, logging, type hints
✅ **Real Testing** - Integration tests with actual APIs
✅ **Quality Validated** - Automated quality checks
✅ **Well Documented** - Comprehensive docstrings

## 🏗️ Architecture

```
URL Input
    ↓
CrawlAndStoreService (Unified API)
    ↓
┌────────────────┬────────────────┐
SimpleCrawling   SimpleVectorDB
Service          Service
    ↓                ↓
Web Pages        Embeddings
    ↓                ↓
Documents        Qdrant
```

## 🚦 Common Commands

### Recommended: Single Session Approach

```bash
# Build everything with feedback loops (RECOMMENDED)
python build_vectordb_pipeline.py --model sonnet

# Use different Claude model
python build_vectordb_pipeline.py --model opus  # More reasoning
python build_vectordb_pipeline.py --model haiku # Faster

# Try the generated services
python example_usage.py

# Check if Qdrant is running
curl http://localhost:6333/collections
```

### Alternative: Multi-Script Approach

```bash
# Run all agents sequentially (no feedback)
./run_all_vectordb_agents.sh

# Run specific agent individually
python create_vectordb_agents.py --agent crawling-service-builder

# Run integration test manually
cd python && uv run pytest tests/integration/test_crawl_and_store_real.py -v
```

## ❓ Troubleshooting

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

# Or check status
docker compose -f docker-compose.vectordb.yml ps
```

### "API key not found"
```bash
# Add to .env file
echo "OPENAI_API_KEY=sk-xxx" >> .env
```

## 📖 Read Next

1. **Want feedback loops?** → Read `BUILD_PIPELINE_README.md` ⭐ (RECOMMENDED)
2. **Prefer sequential?** → Read `QUICK_START_VECTORDB_AGENTS.md`
3. **Want full details?** → Read `VECTORDB_AGENTS_README.md`
4. **Visual learner?** → Open `VECTORDB_AGENTS_ARCHITECTURE.txt`
5. **Code examples?** → Run `python example_usage.py`

## 🎉 Success Criteria

You'll know it's working when:

✅ All 5 agents run successfully
✅ Integration test passes
✅ You can crawl a URL and store vectors
✅ Qdrant contains your vectors

## 💡 Pro Tips

- **Use automated mode** - `./run_all_vectordb_agents.sh` runs everything
- **Start with examples** - `python example_usage.py` shows real usage
- **Read validation report** - `VALIDATION_REPORT.md` confirms quality
- **Customize prompts** - Edit `create_vectordb_agents.py` to tweak agents

## 🆘 Need Help?

1. Check troubleshooting section above
2. Read `VECTORDB_AGENTS_README.md` (comprehensive)
3. Review examples in `example_usage.py`
4. Check that Qdrant is running: `curl http://localhost:6333/collections`

## 🚀 Next Steps After Setup

1. ✅ Review the generated code
2. ✅ Run `python example_usage.py` to see it in action
3. ✅ Integrate into your FastAPI endpoints
4. ✅ Deploy to production

---

**Ready to build?**

```bash
# Recommended: Single session with feedback
python build_vectordb_pipeline.py --model sonnet

# Alternative: Sequential without feedback
./run_all_vectordb_agents.sh
```

---

**Questions?** Read `BUILD_PIPELINE_README.md` (single session) or `VECTORDB_AGENTS_README.md` (multi-script).

**Examples?** Run `python example_usage.py` to see 5 different use cases.

**Architecture?** Open `VECTORDB_AGENTS_ARCHITECTURE.txt` for visual diagrams.
