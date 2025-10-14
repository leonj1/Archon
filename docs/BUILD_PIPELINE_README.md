# Vector DB Pipeline Builder - Orchestrated Workflow

## The Right Way: Single Script with Agent Communication

This is a **single Python script** that orchestrates 5 specialized agents to build your complete web crawling and vector database pipeline. Unlike the previous multi-script approach, this enables:

✅ **Real-time feedback** between agents
✅ **Inter-agent communication** and critique
✅ **Issue detection** before proceeding
✅ **Coordinated fixes** when problems are found
✅ **One conversation** with full context

## How It Works

```
┌──────────────────────────────────────────────┐
│      build_vectordb_pipeline.py              │
│      (Single Orchestrator Session)           │
└──────────────┬───────────────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Main Orchestrator   │◄─── Reviews each step
    │  (Coordinator Agent) │     Provides feedback
    └──────────┬───────────┘     Ensures quality
               │
    ┌──────────┼──────────────────┐
    ▼          ▼          ▼        ▼
┌─────────┐ ┌────────┐ ┌───────┐ ┌──────┐
│Agent 1  │ │Agent 2 │ │Agent 3│ │Agent │
│Crawling │→│VectorDB│→│Wrapper│→│ 4+5  │
│         │ │        │ │       │ │Tests │
└─────────┘ └────────┘ └───────┘ └──────┘
     ↓          ↓          ↓         ↓
   Review   Review     Review    Review
     ↓          ↓          ↓         ↓
  Feedback → Feedback → Feedback → Report
```

### Agent Communication Flow

1. **Agent 1** creates crawling service
   - Returns: Code + summary + suggestions for Agent 2

2. **Agent 2** receives Agent 1's work
   - Reviews crawling service output format
   - Flags compatibility issues
   - Creates vectordb service that matches

3. **Agent 3** receives both services
   - Reviews integration points
   - **Can request fixes if formats don't match**
   - Creates unified wrapper

4. **Agent 4** reviews all services
   - **Flags bugs if found**
   - Creates integration test
   - Reports concerns

5. **Agent 5** validates everything
   - Runs the test
   - **If test fails, explains why and suggests fixes**
   - Creates validation report

## Quick Start

### Prerequisites

```bash
# 1. Environment setup (.env file)
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx

# 2. Install dependencies
pip install claude-agent-sdk
cd python && uv sync --group all && cd ..

# 3. Start Qdrant (docker-compose)
./start_vectordb.sh
```

Qdrant will start automatically and persist data to `./qdrant_storage`.

### Run the Builder

```bash
# One command builds everything with feedback loops
python build_vectordb_pipeline.py --model sonnet
```

You'll see real-time output like:

```
→ Delegating to agent: crawling-service
🔧 Using tool: Read
🔧 Using tool: Write
✓ Operation completed

Agent feedback: "Created SimpleCrawlingService.
Suggestion for vectordb-service: Ensure input format expects
{url, content, title} structure."

→ Delegating to agent: vectordb-service
🔧 Using tool: Read
[Reading crawling service to verify format...]
✓ Format verified - proceeding with vectordb implementation

→ Delegating to agent: wrapper-service
🔧 Using tool: Read
[Checking integration between services...]
⚠️  Warning: Found potential issue with error handling
✓ Adding proper error propagation

→ Delegating to agent: integration-test
[Creating test with real external calls...]
✓ Test created - ready for validation

→ Delegating to agent: test-validator
🔧 Using tool: Bash
Running: pytest tests/integration/test_crawl_and_store_real.py
✓ TEST PASSED
✓ Validation report created
```

## Key Differences from Multi-Script Approach

| Old Approach (Multiple Scripts) | New Approach (Single Session) |
|--------------------------------|-------------------------------|
| 5 separate Python scripts | 1 orchestrated script |
| No inter-agent communication | Full agent feedback loops |
| Sequential without review | Review at each step |
| Issues found at the end | Issues caught early |
| Manual coordination | Automatic coordination |
| No context between agents | Shared context |

## What Makes This Better

### 1. Agent Feedback

```python
# Agent 2 reviewing Agent 1's work:
"I reviewed the crawling service. The output format uses 'content'
field but the vectordb service expects 'text' field. I've adapted
my implementation to match."
```

### 2. Early Issue Detection

```python
# Agent 3 finding integration issues:
"⚠️ WARNING: SimpleCrawlingService may return None on error, but
SimpleVectorDBService doesn't handle None input. Adding validation."
```

### 3. Bug Reports

```python
# Agent 4 finding bugs during test creation:
"🐛 BUG FOUND in SimpleVectorDBService line 45: Missing await
on async function. This will cause the test to fail.
Suggested fix: Add 'await' before chunk_text_async()"
```

### 4. Test Validation

```python
# Agent 5 running and analyzing:
"Test execution: FAILED
Reason: OpenAI API rate limit hit
Recommendation: Add retry logic with exponential backoff
Quality score: 7/10 (would be 9/10 with retry logic)"
```

## Agent Responsibilities

### Agent 1: Crawling Service
- **Input:** Project requirements
- **Output:** SimpleCrawlingService code
- **Feedback:** Suggestions for compatible vectordb service

### Agent 2: VectorDB Service
- **Input:** Crawling service code + requirements
- **Output:** SimpleVectorDBService code
- **Feedback:** Integration concerns, format compatibility

### Agent 3: Wrapper Service
- **Input:** Both services + requirements
- **Output:** CrawlAndStoreService code
- **Feedback:** Integration issues, suggested fixes

### Agent 4: Integration Test
- **Input:** All services + requirements
- **Output:** Real integration test
- **Feedback:** Bugs found, test coverage concerns

### Agent 5: Validator
- **Input:** All code + test
- **Output:** Validation report + quality score
- **Feedback:** Pass/fail, recommendations

## Expected Output

After running `build_vectordb_pipeline.py`, you get:

```
python/src/server/services/
├── simple_crawling_service.py      # Created by Agent 1
├── simple_vectordb_service.py      # Created by Agent 2
└── crawl_and_store_service.py      # Created by Agent 3

python/tests/integration/
├── test_crawl_and_store_real.py    # Created by Agent 4
└── VALIDATION_REPORT.md            # Created by Agent 5
```

**Plus:** Real-time feedback and issue detection throughout!

## Handling Feedback

The orchestrator coordinates fixes when issues are found:

```python
# Example interaction:
Orchestrator: "Agent 2, create vectordb service"
Agent 2: "⚠️ Found issue: Crawling service output doesn't include
          'metadata' field but we need it. Should we add it?"
Orchestrator: "Let me coordinate with Agent 1 to add metadata field"
Agent 1: "✓ Added metadata field to output"
Agent 2: "✓ Confirmed - proceeding with vectordb implementation"
```

## Troubleshooting

### Script hangs or no output

**Cause:** Agent waiting for user input or stuck in loop

**Solution:**
```bash
# Run with verbose output
python build_vectordb_pipeline.py --model sonnet 2>&1 | tee build.log
```

### Agents disagree on format

**Expected!** This is the feedback system working.

The orchestrator will:
1. Identify the disagreement
2. Coordinate a fix
3. Update the affected service
4. Continue building

### Test fails during validation

**Good!** Agent 5 will:
1. Analyze why it failed
2. Identify the bug
3. Suggest specific fixes
4. Update the validation report

You can then:
- Re-run with `python build_vectordb_pipeline.py` to rebuild with fixes
- Or manually apply suggested fixes

## Advanced Usage

### Custom Model Selection

```bash
# Use Opus for complex reasoning
python build_vectordb_pipeline.py --model opus

# Use Haiku for faster iteration
python build_vectordb_pipeline.py --model haiku
```

### Rebuilding Specific Components

The orchestrator maintains context, so you can:

```bash
# Re-run to rebuild with previous feedback
python build_vectordb_pipeline.py
```

The agents will see previous attempts and improve.

## Comparison: Single Session vs Multi-Script

### Multi-Script Approach (❌ Old)

```bash
# Run each agent separately
python create_vectordb_agents.py --agent crawling-service-builder
# Wait...
python create_vectordb_agents.py --agent vectordb-service-builder
# Wait...
python create_vectordb_agents.py --agent wrapper-service-builder
# Wait...
# Find bugs at the end
python create_vectordb_agents.py --agent test-validator
# Go back and fix manually
```

**Problems:**
- No feedback between steps
- Issues found too late
- Manual coordination required
- No context sharing

### Single Session Approach (✅ New)

```bash
# One command, full coordination
python build_vectordb_pipeline.py --model sonnet
```

**Benefits:**
- Automatic feedback loops
- Early issue detection
- Coordinated fixes
- Shared context
- Real-time progress

## Why This Approach?

Based on the Claude Code SDK examples (especially `6_subagents.py`), the recommended pattern is:

1. **One main client session** - Maintains context
2. **Subagents for specialization** - Each expert at their task
3. **Task tool for delegation** - Orchestrator coordinates
4. **Streaming responses** - Real-time feedback
5. **Shared context** - All agents see previous work

This matches how you'd work with a team:
- Project manager (orchestrator) coordinates
- Specialists (agents) do their work
- Regular check-ins (feedback loops)
- Course correction (fix issues early)
- Final review (validation)

## Next Steps

1. **Run it:**
   ```bash
   python build_vectordb_pipeline.py --model sonnet
   ```

2. **Watch the feedback:**
   See agents communicate and improve each other's work

3. **Review the output:**
   Check the validation report for quality assessment

4. **Use the services:**
   ```python
   from python.src.server.services.crawl_and_store_service import CrawlAndStoreService

   service = CrawlAndStoreService()
   result = await service.crawl_and_store("https://example.com")
   ```

## Support

**Script hangs?** Check that ANTHROPIC_API_KEY is set
**No output?** Add `-v` for verbose mode (future feature)
**Test fails?** Check Agent 5's validation report for specific issues

---

**This is the right way to use Claude Code Agent SDK for complex workflows!** 🚀
