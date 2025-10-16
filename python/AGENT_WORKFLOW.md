# Agent Investigation Workflow

## Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INITIATES                          │
│                  ./run_investigation.sh                         │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ENVIRONMENT CHECKS                           │
│  ✓ Backend running (localhost:8181)                            │
│  ✓ Qdrant running (localhost:6333)                             │
│  ✓ SQLite configured                                            │
│  ✓ API keys present                                             │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MAIN SCRIPT LAUNCHES                          │
│             investigate_crawl_status.py                         │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
                    ┌─────────┴─────────┐
                    │   AGENT ROUTER    │
                    │  (ClaudeSDKClient) │
                    └─────────┬─────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                                   │
            ▼                                   ▼
┌─────────────────────────┐         ┌─────────────────────────┐
│  INVESTIGATOR AGENT     │         │   TEST WRITER AGENT     │
│  (Sequential Order)     │         │   (After Investigation) │
└───────────┬─────────────┘         └──────────┬──────────────┘
            │                                  │
            ▼                                  │
┌───────────────────────┐                      │
│ 1. Read Code          │                      │
│    - crawling_service │                      │
│    - source_mgmt      │                      │
│    - repository       │                      │
└──────────┬────────────┘                      │
           │                                   │
           ▼                                   │
┌───────────────────────┐                      │
│ 2. Search Patterns    │                      │
│    Grep: crawl_status │                      │
│    Find all locations │                      │
└──────────┬────────────┘                      │
           │                                   │
           ▼                                   │
┌───────────────────────┐                      │
│ 3. Trigger Test Crawl │                      │
│    curl_backend:      │                      │
│    POST /crawl        │                      │
│    URL: go.dev/doc    │                      │
└──────────┬────────────┘                      │
           │                                   │
           ▼                                   │
┌───────────────────────┐                      │
│ 4. Wait & Monitor     │                      │
│    Sleep 30 seconds   │                      │
│    Check progress     │                      │
└──────────┬────────────┘                      │
           │                                   │
           ▼                                   │
┌───────────────────────┐                      │
│ 5. Check Database     │                      │
│    check_db_status()  │                      │
│    Query metadata     │                      │
│    Verify crawl_status│                      │
└──────────┬────────────┘                      │
           │                                   │
           ▼                                   │
┌───────────────────────┐                      │
│ 6. Check Vector DB    │                      │
│    check_qdrant()     │                      │
│    Verify embeddings  │                      │
└──────────┬────────────┘                      │
           │                                   │
           ▼                                   │
┌───────────────────────┐                      │
│ 7. Analyze Results    │                      │
│    Expected vs Actual │                      │
│    Identify bug       │                      │
└──────────┬────────────┘                      │
           │                                   │
           ▼                                   │
┌───────────────────────┐                      │
│ 8. Write Report       │                      │
│    Create markdown    │                      │
│    Code flow diagram  │                      │
│    Root cause         │                      │
│    Recommended fix    │                      │
└──────────┬────────────┘                      │
           │                                   │
           │    CRAWL_STATUS_                 │
           │    INVESTIGATION.md              │
           │                                   │
           └───────────────┬───────────────────┘
                           │
                           ▼
                  ┌────────────────────┐
                  │  Test Writer Reads │
                  │  Investigation     │
                  │  Report            │
                  └────────┬───────────┘
                           │
                           ▼
                  ┌────────────────────┐
                  │ 1. Analyze Existing│
                  │    Test Patterns   │
                  └────────┬───────────┘
                           │
                           ▼
                  ┌────────────────────┐
                  │ 2. Create Test File│
                  │    - Setup/Teardown│
                  │    - Test fixtures │
                  └────────┬───────────┘
                           │
                           ▼
                  ┌────────────────────┐
                  │ 3. Write Test Cases│
                  │    - Initiation    │
                  │    - Completion    │
                  │    - API Response  │
                  │    - DB Persistence│
                  └────────┬───────────┘
                           │
                           ▼
                  ┌────────────────────┐
                  │ 4. Implement Tests │
                  │    - Real crawls   │
                  │    - Curl calls    │
                  │    - DB queries    │
                  └────────┬───────────┘
                           │
                           ▼
                  ┌────────────────────┐
                  │ 5. Run Tests       │
                  │    pytest -v       │
                  └────────┬───────────┘
                           │
                           ▼
                  ┌────────────────────┐
                  │ 6. Fix Failures    │
                  │    Edit tests      │
                  │    Re-run          │
                  └────────┬───────────┘
                           │
                           │
                           │  test_crawl_status_
                           │  integration.py
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OUTPUTS GENERATED                          │
│                                                                 │
│  1. Investigation Report (CRAWL_STATUS_INVESTIGATION.md)       │
│     - Code analysis                                             │
│     - Root cause                                                │
│     - Recommended fixes                                         │
│                                                                 │
│  2. Integration Tests (test_crawl_status_integration.py)       │
│     - Real crawl tests                                          │
│     - Database validation                                       │
│     - API contract tests                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Tool Usage Flow

### Investigator Agent Tools

```
┌──────────────────┐
│  Code Analysis   │
├──────────────────┤
│ Read             │ → Read service files
│ Grep             │ → Search for patterns
│ Glob             │ → Find files
│ Bash             │ → Execute commands
└──────────────────┘

┌──────────────────┐
│ Live Testing     │
├──────────────────┤
│ curl_backend     │ → Trigger crawls
│ restart_backend  │ → Restart services
└──────────────────┘

┌──────────────────┐
│  Data Validation │
├──────────────────┤
│ check_db_status  │ → Query SQLite
│ check_qdrant     │ → Inspect vectors
└──────────────────┘

┌──────────────────┐
│   Reporting      │
├──────────────────┤
│ Write            │ → Create report
│ Edit             │ → Update content
└──────────────────┘
```

### Test Writer Agent Tools

```
┌──────────────────┐
│  Code Review     │
├──────────────────┤
│ Read             │ → Read patterns
│ Grep             │ → Find examples
└──────────────────┘

┌──────────────────┐
│  Test Creation   │
├──────────────────┤
│ Write            │ → Create tests
│ Edit             │ → Modify tests
└──────────────────┘

┌──────────────────┐
│  Validation      │
├──────────────────┤
│ Bash             │ → Run pytest
│ curl_backend     │ → Test APIs
│ check_db_status  │ → Verify data
└──────────────────┘
```

## Data Flow

### Input Data Sources

```
┌─────────────────┐
│ Code Repository │ → Read by agents
├─────────────────┤
│ - Services      │
│ - Controllers   │
│ - Repositories  │
└─────────────────┘

┌─────────────────┐
│ Running Backend │ → Queried by agents
├─────────────────┤
│ - REST API      │
│ - Endpoints     │
└─────────────────┘

┌─────────────────┐
│ SQLite Database │ → Inspected by agents
├─────────────────┤
│ - sources table │
│ - metadata      │
│ - crawl_status  │
└─────────────────┘

┌─────────────────┐
│ Qdrant VectorDB │ → Validated by agents
├─────────────────┤
│ - Collections   │
│ - Embeddings    │
│ - Points        │
└─────────────────┘
```

### Output Artifacts

```
┌──────────────────────────────────────┐
│  Investigation Report                │
├──────────────────────────────────────┤
│  File: CRAWL_STATUS_INVESTIGATION.md │
│                                      │
│  Contents:                           │
│  • Code flow diagram                 │
│  • All crawl_status assignments      │
│  • Expected behavior                 │
│  • Actual behavior observed          │
│  • Root cause analysis               │
│  • Bug location (file:line)          │
│  • Recommended fix                   │
│  • Additional findings               │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  Integration Tests                   │
├──────────────────────────────────────┤
│  File: test_crawl_status_integ.py    │
│                                      │
│  Test Cases:                         │
│  ✓ Crawl initiation (pending)        │
│  ✓ Crawl completion (completed)      │
│  ✓ API status mapping (active)       │
│  ✓ Database persistence              │
│                                      │
│  Features:                           │
│  • Real HTTP calls                   │
│  • Actual crawl of go.dev/doc        │
│  • SQLite queries                    │
│  • Qdrant validation                 │
│  • Setup/teardown                    │
│  • No mocking                        │
└──────────────────────────────────────┘
```

## Execution Timeline

```
Time  │ Phase          │ Agent         │ Activity
──────┼────────────────┼───────────────┼──────────────────────────
00:00 │ Setup          │ System        │ Environment checks
00:10 │ Launch         │ Main Script   │ Initialize SDK client
00:20 │ Investigation  │ Investigator  │ Read code files
00:40 │ Investigation  │ Investigator  │ Search for patterns
01:00 │ Investigation  │ Investigator  │ Trigger test crawl
01:05 │ Investigation  │ Investigator  │ Monitor crawl progress
01:35 │ Investigation  │ Investigator  │ Query database
01:45 │ Investigation  │ Investigator  │ Check Qdrant
01:55 │ Investigation  │ Investigator  │ Analyze results
02:10 │ Investigation  │ Investigator  │ Write report
02:20 │ Test Creation  │ Test Writer   │ Read report
02:30 │ Test Creation  │ Test Writer   │ Analyze patterns
02:50 │ Test Creation  │ Test Writer   │ Write tests
03:20 │ Test Creation  │ Test Writer   │ Run tests
03:40 │ Test Creation  │ Test Writer   │ Fix failures
04:00 │ Complete       │ System        │ Display results
```

## Error Handling

```
┌─────────────────────────────────────────┐
│  Agent Error Recovery                   │
├─────────────────────────────────────────┤
│                                         │
│  Backend Down                           │
│  → restart_backend tool                 │
│  → Retry operation                      │
│                                         │
│  Database Locked                        │
│  → Wait and retry                       │
│  → Report in investigation              │
│                                         │
│  Qdrant Not Running                     │
│  → Note in report                       │
│  → Continue with partial data           │
│                                         │
│  Crawl Timeout                          │
│  → Extend wait time                     │
│  → Check progress endpoint              │
│                                         │
│  Test Failures                          │
│  → Analyze failure                      │
│  → Edit test code                       │
│  → Re-run                               │
│                                         │
└─────────────────────────────────────────┘
```

## Key Design Principles

### 1. Agent Isolation
- Each agent has separate context
- Tools scoped per agent
- Communication via file outputs
- No shared state

### 2. No Mocking
- Real crawls of https://go.dev/doc
- Actual HTTP calls to backend
- Real database queries
- Real vector storage

### 3. Tool-Based Architecture
- Agents use tools, not direct code
- Tools encapsulate operations
- MCP server provides tools
- Clean separation of concerns

### 4. Autonomous Operation
- Agents work independently
- No human intervention needed
- Self-correcting (retry logic)
- Complete investigation cycle

### 5. Production Alignment
- Uses same .env as backend
- Same database (SQLite)
- Same vector DB (Qdrant)
- Same API endpoints

## Usage Examples

### Basic Investigation
```bash
cd /home/jose/src/Archon/python
./run_investigation.sh
```

### Manual Step-by-Step
```bash
# 1. Verify setup
./verify_investigation_setup.sh

# 2. Run investigation
uv run python investigate_crawl_status.py

# 3. Read report
cat /home/jose/src/Archon/CRAWL_STATUS_INVESTIGATION.md

# 4. Run tests
uv run pytest tests/integration/test_crawl_status_integration.py -v
```

### Custom Investigation
```python
# Modify investigate_crawl_status.py
# Change agent prompts, tools, or workflow
# Add new agents for additional analysis
```

## Success Criteria

Investigation is successful when:

- ✓ Both agents complete without errors
- ✓ Investigation report is created
- ✓ Integration tests are created
- ✓ Tests can run and pass/fail meaningfully
- ✓ Root cause is identified
- ✓ Recommended fix is provided

## Next Steps After Investigation

1. **Review** investigation report
2. **Understand** root cause
3. **Apply** recommended fix
4. **Run** integration tests
5. **Verify** fix works
6. **Commit** changes (code + tests)
