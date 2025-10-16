# Crawl Status Investigation Script

This directory contains a Python script that uses Claude Code SDK agents to investigate why `metadata.crawl_status` doesn't update to 'completed' after crawling finishes.

## Overview

The investigation uses two specialized AI agents:

### 1. Investigator Agent
**Purpose**: Analyze the backend code to identify why crawl status doesn't update

**Capabilities**:
- Reads and analyzes crawling service code
- Searches for all places where `crawl_status` is set
- Triggers test crawls via API
- Queries SQLite database to verify status
- Checks Qdrant vector database
- Produces detailed investigation report

**Tools**:
- Code reading (Read, Grep, Glob)
- Backend validation (curl_backend)
- Database inspection (check_database_status)
- Vector DB inspection (check_qdrant_collections)

### 2. Test Writer Agent
**Purpose**: Create comprehensive integration tests for the crawl flow

**Capabilities**:
- Reads investigation report
- Creates pytest integration tests
- Tests use **real** crawling (no mocks) of https://go.dev/doc
- Validates status transitions in SQLite
- Verifies API responses
- Uses actual backend HTTP calls

**Tools**:
- File operations (Read, Write, Edit)
- Backend testing (curl_backend, restart_backend)
- Database validation (check_database_status)

## Requirements

### Environment Variables
The script reads from `.env` file in `/home/jose/src/Archon/.env`:
- `DATABASE_TYPE=sqlite`
- `SQLITE_PATH=/app/data/archon.db` (or local path)
- `OPENAI_API_KEY` (for Claude SDK)
- Backend ports: 8181 (server), 6333 (Qdrant)

### Dependencies
- `claude-agent-sdk` - For AI agents
- `qdrant-client` - For vector database
- `rich` - For terminal output
- `nest-asyncio` - For async support
- `python-dotenv` - For environment variables

### Running Services
- Archon backend server (port 8181)
- Qdrant vector database (port 6333)
- SQLite database accessible

## Setup

### 1. Install Dependencies
```bash
cd /home/jose/src/Archon/python
./setup_investigation_env.sh
```

This will:
- Install Python dependencies via `uv`
- Start Qdrant if not running
- Verify backend is running
- Prompt to start backend if needed

### 2. Verify Environment
```bash
# Check backend is running
curl http://localhost:8181/health

# Check Qdrant is running
curl http://localhost:6333/health

# Verify .env file exists
cat /home/jose/src/Archon/.env | grep DATABASE_TYPE
```

## Usage

### Run Full Investigation
```bash
cd /home/jose/src/Archon/python
uv run python investigate_crawl_status.py
```

This will:
1. Launch the Investigator Agent to analyze code
2. Trigger a test crawl of https://go.dev/doc
3. Check database for status updates
4. Generate investigation report
5. Launch the Test Writer Agent
6. Create integration tests
7. Run the tests to validate

### Expected Output Files

#### 1. Investigation Report
**Location**: `/home/jose/src/Archon/CRAWL_STATUS_INVESTIGATION.md`

**Contents**:
- Code flow diagram
- Where `crawl_status` should be updated
- Why the update isn't happening
- Root cause analysis
- Recommended fixes

#### 2. Integration Tests
**Location**: `/home/jose/src/Archon/python/tests/integration/test_crawl_status_integration.py`

**Test Cases**:
- `test_crawl_initiation_sets_pending_status` - Verify new crawls start as 'pending'
- `test_crawl_completion_updates_status_to_completed` - Verify status updates on completion
- `test_completed_crawl_shows_active_in_api` - Verify API returns 'active' status
- `test_source_metadata_persists_to_database` - Verify database persistence

### Run Tests Manually
```bash
cd /home/jose/src/Archon/python
uv run pytest tests/integration/test_crawl_status_integration.py -v
```

## How It Works

### Phase 1: Investigation
1. Investigator agent reads `src/server/services/crawling/crawling_service.py`
2. Searches for all `crawl_status` assignments
3. Identifies the status update flow
4. Triggers a real crawl via POST `/api/knowledge/crawl`
5. Waits for completion (30 seconds)
6. Queries SQLite database to check actual status
7. Compares expected vs actual behavior
8. Documents findings in investigation report

### Phase 2: Test Creation
1. Test Writer reads the investigation report
2. Analyzes existing test patterns
3. Creates integration tests with:
   - Real HTTP calls (no mocking)
   - Actual crawl of https://go.dev/doc
   - SQLite database queries
   - Qdrant vector storage validation
   - Status transition verification
4. Runs tests to validate they work
5. Fixes any test failures

### Phase 3: Validation
The integration tests validate:
- ✓ Crawl initiation creates source with `crawl_status: 'pending'`
- ✓ Crawl completion updates to `crawl_status: 'completed'`
- ✓ API endpoint returns `status: 'active'` for completed sources
- ✓ Database persists the correct metadata
- ✓ Qdrant contains the document embeddings

## Custom Tools

The script provides custom MCP tools for the agents:

### `restart_backend`
Executes `make restart` to restart Archon services.

### `curl_backend`
Makes HTTP requests to the running backend.
- Parameters: `endpoint`, `method`, `data`
- Example: `curl_backend(endpoint="/api/knowledge/crawl", method="POST", data='{"url":"https://go.dev/doc"}')`

### `check_database_status`
Queries SQLite to inspect source metadata.
- Parameters: `source_id` (optional)
- Returns: source_id, title, crawl_status, metadata

### `check_qdrant_collections`
Inspects Qdrant collections and point counts.
- Returns: collection names, point counts, vector dimensions

## Debugging

### Enable Verbose Output
Edit `investigate_crawl_status.py` and set:
```python
options = ClaudeAgentOptions(
    model="sonnet-4",
    permission_mode="prompt",  # Changed from "acceptEdits" to prompt for each action
    ...
)
```

### View Agent Thinking
The script uses Rich console output to show:
- Agent messages (cyan panels for Investigator)
- Test output (green panels for Test Writer)
- Control flow (blue panels)
- System messages (yellow panels)

### Check Logs
```bash
# Backend logs
docker compose logs -f archon-server

# Qdrant logs
docker logs -f qdrant-archon
```

### Manual Database Inspection
```python
import sqlite3
import json

conn = sqlite3.connect('/home/jose/src/Archon/data/archon.db')
cursor = conn.cursor()
cursor.execute("SELECT source_id, title, metadata FROM sources")
for row in cursor.fetchall():
    metadata = json.loads(row[2])
    print(f"{row[1]}: {metadata.get('crawl_status', 'unknown')}")
conn.close()
```

## Architecture

### Agent Isolation
- Each agent has its own context and tools
- Agents communicate via file outputs (investigation report)
- Main script orchestrates agent execution

### Tool Design
Custom tools are implemented as:
1. Python async functions with `@tool` decorator
2. Packaged into an SDK MCP server
3. Provided to agents via `mcp_servers` configuration

### No Mocking Philosophy
Per requirements:
- **Real crawls**: Actually fetches https://go.dev/doc
- **Real database**: Queries actual SQLite database
- **Real backend**: Makes HTTP calls to localhost:8181
- **Real vectors**: Stores embeddings in Qdrant

This ensures tests reflect production behavior.

## Troubleshooting

### "VIRTUAL_ENV does not match" warning
This warning is harmless and can be ignored:
```
warning: `VIRTUAL_ENV=/home/jose/src/Archon/.venv` does not match the project environment path `.venv`
```

**Cause**: The parent directory has a `.venv` that's set in `VIRTUAL_ENV`, but the `python/` subdirectory has its own environment.

**Solution**: Use `uv run` which handles this automatically. All scripts use `uv run` so the warning is suppressed.

**Alternative**: If you want to eliminate the warning entirely:
```bash
unset VIRTUAL_ENV
cd /home/jose/src/Archon/python
uv run python investigate_crawl_status.py
```

### "ModuleNotFoundError: No module named 'claude_agent_sdk'"
Dependencies not installed.

**Solution**:
```bash
cd /home/jose/src/Archon/python
uv add claude-agent-sdk qdrant-client rich nest-asyncio
```

Or run the setup script:
```bash
./setup_investigation_env.sh
```

Verify imports work:
```bash
uv run python test_investigation_imports.py
```

### "Qdrant not running"
```bash
docker run -d --name qdrant-archon -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest
```

### "Backend not responding"
```bash
cd /home/jose/src/Archon
make restart
```

### "SQLite database not found"
Check `.env` for correct `SQLITE_PATH` or create database:
```bash
mkdir -p /home/jose/src/Archon/data
# Database will be created on first backend start
```

### Quick Import Test
Before running the full investigation, test that everything is set up:
```bash
uv run python test_investigation_imports.py
```

This will verify:
- All packages are installed
- Imports work correctly
- Tool creation works
- Agent options can be created

### Tests fail with connection errors
Ensure backend is running and accessible:
```bash
curl http://localhost:8181/health
```

## Next Steps

After running the investigation:

1. **Review the investigation report** at `/home/jose/src/Archon/CRAWL_STATUS_INVESTIGATION.md`
2. **Check the integration tests** at `tests/integration/test_crawl_status_integration.py`
3. **Fix the identified bug** based on the report's recommendations
4. **Re-run tests** to verify the fix works
5. **Commit both the fix and the tests**

## Example Run

```bash
$ cd /home/jose/src/Archon/python
$ ./setup_investigation_env.sh
Installing Python dependencies...
✓ Qdrant is already running
✓ Archon backend is running
Environment Setup Complete!

$ uv run python investigate_crawl_status.py
┌─────────────────────────────────────────────┐
│ System                                      │
│                                             │
│ Initializing Crawl Status Investigation    │
│ Goal: Investigate why metadata.crawl_status │
│ doesn't update to 'completed'               │
│ Environment: SQLite + Qdrant + Live Backend│
│ Test URL: https://go.dev/doc                │
└─────────────────────────────────────────────┘

[... investigation output ...]

Investigation Complete!

Check the following files:
- /home/jose/src/Archon/CRAWL_STATUS_INVESTIGATION.md
- /home/jose/src/Archon/python/tests/integration/test_crawl_status_integration.py
```

## License

This investigation script is part of the Archon project.
