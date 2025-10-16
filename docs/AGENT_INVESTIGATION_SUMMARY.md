# Claude Code SDK Agent Investigation - Summary

## Overview

This document describes the autonomous agent system created to investigate and fix the crawl status update bug in Archon.

## Problem Statement

**Issue**: After crawling completes, `metadata.crawl_status` remains as `'pending'` instead of updating to `'completed'`, causing status badges to display incorrectly in the UI.

**Impact**: All knowledge sources show yellow "Pending" badges even after successful crawling.

## Solution Approach

Created an autonomous multi-agent system using Claude Code SDK that:
1. **Investigates** the root cause by analyzing code
2. **Tests** the issue with real integration tests
3. **Documents** findings and creates reproducible tests

## Agent Architecture

### Agent 1: Investigator Agent
**Role**: Backend code analyst and bug hunter

**Capabilities**:
- Code analysis (reads crawling service, source management, repository layers)
- Pattern matching (searches all files for `crawl_status` assignments)
- Live testing (triggers real crawls via API)
- Database inspection (queries SQLite for actual status values)
- Vector DB validation (checks Qdrant collections)

**Output**: Detailed investigation report with:
- Code flow diagram
- Root cause identification
- Bug location
- Recommended fix

**File**: `CRAWL_STATUS_INVESTIGATION.md`

### Agent 2: Test Writer Agent
**Role**: Integration test engineer

**Capabilities**:
- Test pattern analysis (learns from existing tests)
- Test creation (writes pytest integration tests)
- Real-world validation (no mocking - actual crawls)
- Database verification (queries SQLite directly)
- Test execution (runs and fixes failing tests)

**Output**: Production-ready integration tests

**File**: `python/tests/integration/test_crawl_status_integration.py`

## Custom Tools Created

The agents have access to specialized tools via MCP server:

### 1. `restart_backend`
Restarts Archon services using `make restart`
- Used when code changes need to be applied
- Ensures clean server state for tests

### 2. `curl_backend`
Makes HTTP requests to running backend
- Parameters: endpoint, method, data
- Used to trigger crawls, check status, validate APIs
- Example: `POST /api/knowledge/crawl {"url": "https://go.dev/doc"}`

### 3. `check_database_status`
Queries SQLite for source metadata
- Parameter: source_id (optional)
- Returns: crawl_status, metadata, timestamps
- Used to verify actual database state vs expected

### 4. `check_qdrant_collections`
Inspects Qdrant vector database
- Returns: collections, point counts, dimensions
- Validates that embeddings are stored correctly

## Key Features

### No Mocking - Real Integration Testing
Per requirements:
- ✓ Actually crawls `https://go.dev/doc`
- ✓ Uses real SQLite database
- ✓ Uses real Qdrant vector storage
- ✓ Makes real HTTP calls to backend
- ✓ Queries real database to verify

### Environment Configuration
Reads from `.env` file:
```bash
DATABASE_TYPE=sqlite
SQLITE_PATH=/app/data/archon.db
OPENAI_API_KEY=sk-...
ARCHON_SERVER_PORT=8181
```

Also uses environment variables as fallback.

### Autonomous Execution
Once started, agents work independently:
1. Investigator analyzes code → finds bug
2. Test Writer reads report → creates tests
3. Tests validate the fix → provide regression protection

## Files Created

### 1. Main Script
**File**: `python/investigate_crawl_status.py`

**Purpose**: Orchestrates the two-agent investigation

**How it works**:
```python
# Creates two specialized agents
investigator = AgentDefinition(
    description="Backend bug hunter",
    prompt="Investigate crawl_status update issue...",
    tools=[Read, Grep, curl_backend, check_database_status]
)

test_writer = AgentDefinition(
    description="Integration test engineer",
    prompt="Create real integration tests...",
    tools=[Read, Write, curl_backend, check_database_status]
)

# Launches them sequentially
client.query("Use Task tool to launch investigator agent...")
client.query("Use Task tool to launch test_writer agent...")
```

### 2. Setup Script
**File**: `python/setup_investigation_env.sh`

**Purpose**: Ensures environment is ready

**Actions**:
- Installs dependencies (claude-agent-sdk, qdrant-client, etc.)
- Starts Qdrant if not running
- Verifies backend is accessible
- Checks database path

### 3. Wrapper Script
**File**: `python/run_investigation.sh`

**Purpose**: One-command investigation launch

**Actions**:
- Pre-flight checks (backend, Qdrant, API keys)
- Environment validation
- Runs investigation
- Shows results summary

### 4. Documentation
**File**: `python/INVESTIGATION_README.md`

**Contents**:
- How the agents work
- Setup instructions
- Usage examples
- Tool documentation
- Troubleshooting guide

## Usage

### Quick Start
```bash
cd /home/jose/src/Archon/python
./run_investigation.sh
```

### Manual Setup
```bash
# 1. Install dependencies
./setup_investigation_env.sh

# 2. Ensure backend is running
cd /home/jose/src/Archon
make restart

# 3. Run investigation
uv run python investigate_crawl_status.py
```

### Run Generated Tests
```bash
cd /home/jose/src/Archon/python
uv run pytest tests/integration/test_crawl_status_integration.py -v
```

## Expected Workflow

### Step 1: Investigation (Investigator Agent)
```
1. Read crawling_service.py
2. Search for 'crawl_status' in codebase
3. Trigger test crawl: POST /api/knowledge/crawl
4. Wait 30 seconds
5. Query database: check_database_status()
6. Compare expected vs actual
7. Write report with findings
```

**Output**: Investigation report identifying the bug

### Step 2: Test Creation (Test Writer Agent)
```
1. Read investigation report
2. Analyze test patterns
3. Create integration tests:
   - test_crawl_initiation_sets_pending_status
   - test_crawl_completion_updates_status_to_completed
   - test_completed_crawl_shows_active_in_api
   - test_source_metadata_persists_to_database
4. Run tests
5. Fix failures
```

**Output**: Working integration tests with real crawls

### Step 3: Validation
The tests validate end-to-end:
- Crawl starts with `crawl_status: 'pending'` ✓
- Crawl completes and updates to `'completed'` ✓
- API returns `status: 'active'` ✓
- Database persists metadata correctly ✓
- Qdrant stores embeddings ✓

## Integration with Existing Fix

This investigation complements the manual fix already applied:

**Manual Fix** (already completed):
- Fixed `KnowledgeSummaryService` hardcoded status
- Added `/api/knowledge-items/fix-pending-statuses` endpoint
- Fixed 5 existing sources with wrong status

**Agent Investigation** (new):
- Identifies **why** the status wasn't updating
- Creates **tests** to prevent regression
- Validates the **entire flow** end-to-end

## Benefits

### 1. Root Cause Analysis
Rather than just fixing symptoms, the investigator agent:
- Traces the entire code path
- Identifies where the update should happen
- Explains why it's not happening
- Documents the findings

### 2. Regression Prevention
Integration tests ensure:
- Future code changes don't break status updates
- The fix continues working
- New developers understand expected behavior

### 3. Real-World Validation
No mocking means:
- Tests reflect production behavior
- Catch issues that unit tests miss
- Validate database persistence
- Verify API contract

### 4. Automated Investigation
Agents can:
- Work autonomously
- Run 24/7 if needed
- Handle tedious analysis tasks
- Generate documentation

## Technical Details

### Agent Isolation
- Each agent has separate context
- Tools are scoped per agent
- Communication via file outputs
- No shared state between agents

### Tool Design Pattern
```python
@tool("tool_name", "description", {"param": type})
async def tool_function(args: dict[str, Any]) -> dict[str, Any]:
    # Tool implementation
    return {"content": [{"type": "text", "text": "result"}]}

# Package into MCP server
server = create_sdk_mcp_server(
    name="server_name",
    version="1.0.0",
    tools=[tool_function]
)

# Provide to agents
options = ClaudeAgentOptions(
    mcp_servers={"server_name": server},
    allowed_tools=["mcp__server_name__tool_name"]
)
```

### Database Access
Direct SQLite queries:
```python
conn = sqlite3.connect(db_path)
cursor.execute("SELECT metadata FROM sources WHERE source_id = ?", (id,))
metadata = json.loads(cursor.fetchone()[0])
crawl_status = metadata.get("crawl_status")
```

### API Testing
Real HTTP calls:
```python
subprocess.run([
    "curl", "-X", "POST",
    "-H", "Content-Type: application/json",
    "-d", '{"url": "https://go.dev/doc", "knowledge_type": "technical"}',
    "http://localhost:8181/api/knowledge/crawl"
])
```

## Monitoring and Debugging

### View Agent Output
The script uses Rich console for formatted output:
- **Cyan panels**: Investigator messages
- **Green panels**: Test Writer messages
- **Blue panels**: Control flow
- **Yellow panels**: System messages

### Enable Verbose Mode
Change `permission_mode` in script:
```python
permission_mode="prompt"  # Agent asks before each action
```

### Check Logs
```bash
# Backend logs
docker compose logs -f archon-server

# Qdrant logs
docker logs -f qdrant-archon
```

## Troubleshooting

### Backend Not Running
```bash
cd /home/jose/src/Archon
make restart
curl http://localhost:8181/health  # Verify
```

### Qdrant Not Running
```bash
docker run -d --name qdrant-archon -p 6333:6333 qdrant/qdrant:latest
curl http://localhost:6333/health  # Verify
```

### Missing Dependencies
```bash
cd /home/jose/src/Archon/python
uv add claude-agent-sdk qdrant-client rich nest-asyncio
```

### API Key Issues
```bash
# Check .env file
grep ANTHROPIC_API_KEY /home/jose/src/Archon/.env

# Or export directly
export ANTHROPIC_API_KEY=sk-ant-...
```

## Future Enhancements

Potential improvements:
1. **Parallel agent execution** - Run both agents simultaneously
2. **Continuous monitoring** - Schedule periodic checks
3. **Auto-fix capability** - Let agents apply fixes automatically
4. **Report generation** - Create visual diagrams of code flow
5. **Slack integration** - Send results to team channel

## Conclusion

This agent-based investigation system provides:
- ✓ Autonomous bug analysis
- ✓ Real integration tests
- ✓ Comprehensive documentation
- ✓ Regression prevention
- ✓ Reproducible validation

The agents work together to not only identify the bug but also create the tests needed to ensure it stays fixed.

## Next Steps

1. **Run the investigation**:
   ```bash
   cd /home/jose/src/Archon/python
   ./run_investigation.sh
   ```

2. **Review outputs**:
   - Investigation report
   - Integration tests

3. **Apply fixes** based on report recommendations

4. **Run tests** to validate

5. **Commit everything**:
   - Investigation report
   - Integration tests
   - Bug fix

## Files Summary

| File | Purpose | Location |
|------|---------|----------|
| Main script | Orchestrates agents | `python/investigate_crawl_status.py` |
| Setup script | Environment setup | `python/setup_investigation_env.sh` |
| Wrapper script | Easy execution | `python/run_investigation.sh` |
| Documentation | Usage guide | `python/INVESTIGATION_README.md` |
| This summary | Overview | `AGENT_INVESTIGATION_SUMMARY.md` |

Generated by Claude Code SDK Agents - Autonomous Investigation System
