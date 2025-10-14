# Test Fix Orchestrator - Architecture & Design

## Overview

The Test Fix Orchestrator is a sophisticated automated testing system that uses Claude's Agent SDK to orchestrate multiple specialized agents for fixing failing tests. This document explains the architecture, design decisions, and implementation patterns.

## System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                    Test Fix Orchestrator                        │
│                     (Main Coordinator)                          │
└────────────┬────────────────────────────────────┬───────────────┘
             │                                    │
             │                                    │
    ┌────────▼─────────┐                 ┌───────▼────────┐
    │  State Manager   │                 │ Backup Manager │
    │  (JSON Persist)  │                 │ (File Backups) │
    └────────┬─────────┘                 └───────┬────────┘
             │                                    │
             │                                    │
    ┌────────▼──────────────────────────────────▼─────────┐
    │              Claude SDK Client                      │
    │         (Agent Coordination Layer)                  │
    └────┬──────────┬──────────┬──────────┬───────────────┘
         │          │          │          │
         │          │          │          │
    ┌────▼───┐ ┌───▼────┐ ┌───▼────┐ ┌──▼────────┐
    │ Test   │ │ Test   │ │ Test   │ │ Validator │
    │ Runner │ │Analyzer│ │ Fixer  │ │   Agent   │
    │ Agent  │ │ Agent  │ │ Agent  │ │           │
    └────────┘ └────────┘ └────────┘ └───────────┘
```

### Component Breakdown

#### 1. Test Fix Orchestrator (Main Class)

**Responsibilities:**
- Overall workflow coordination
- Timeout management
- Progress tracking and display
- Report generation
- Main execution loop

**Key Methods:**
- `run()`: Main entry point and loop
- `run_test_suite()`: Execute full test suite
- `run_single_test()`: Execute individual test
- `parse_failing_tests()`: Extract failing test paths from pytest output
- `process_test()`: Handle complete fix cycle for one test
- `fix_test()`: Single fix attempt with all agents
- `generate_summary_report()`: Create markdown summary

**Design Pattern**: Orchestrator/Coordinator pattern
- Coordinates multiple agents without implementing logic
- Delegates specialized tasks to specialized agents
- Manages high-level workflow state

#### 2. State Manager

**Responsibilities:**
- Persist state to JSON for resume capability
- Track test statuses and attempts
- Maintain statistics
- Handle state transitions

**Data Model:**
```python
OrchestratorState
├── started_at: str
├── last_updated: str
├── tests: Dict[str, TestRecord]
│   ├── test_path: str
│   ├── status: TestStatus (enum)
│   ├── attempts: List[TestAttempt]
│   ├── current_attempt: int
│   ├── error_output: str
│   └── fixed_at: Optional[str]
├── total_tests: int
├── fixed_count: int
├── failed_count: int
└── skipped_count: int
```

**Key Features:**
- Atomic saves (write full state each time)
- Resume from any point
- No database required (JSON file)
- Human-readable state format

#### 3. Backup Manager

**Responsibilities:**
- Create file backups before modifications
- Restore files on rollback
- Generate diffs for reporting

**Design Decision**: File-based, not Git-based
- **Why**: Simpler, no Git assumptions
- **How**: Copy files to `.test_fix_backups/` with unique names
- **Rollback**: Copy backup back to original location
- **Naming**: `{test_name}_attempt_{number}_{filename}`

**Example Backup Flow:**
```
Original: tests/integration/test_foo.py
Attempt 1 Backup: .test_fix_backups/tests_integration_test_foo.py_attempt_1_test_foo.py
Attempt 2 Backup: .test_fix_backups/tests_integration_test_foo.py_attempt_2_test_foo.py
```

#### 4. Logger

**Responsibilities:**
- Structured logging to JSONL
- Rich console output
- Event categorization

**Log Levels:**
- `info`: General information
- `success`: Successful operations
- `warning`: Non-fatal issues
- `error`: Errors and failures

**Event Types:**
- `analysis_complete`: Test analysis finished
- `fix_applied`: Fix implementation completed
- `validation_result`: Validation outcome

**JSONL Format:**
```json
{"timestamp": "2025-01-14T20:30:00", "event_type": "info", "message": "..."}
{"timestamp": "2025-01-14T20:30:15", "event_type": "analysis_complete", "test": "...", "analysis": "..."}
```

## Agent Design

### Agent Coordination Pattern

The orchestrator uses **specialized agents** via Claude's Agent SDK:

```python
agents = {
    "test-runner": AgentDefinition(...),
    "test-analyzer": AgentDefinition(...),
    "test-fixer": AgentDefinition(...),
    "validator": AgentDefinition(...),
}
```

Each agent has:
- **Description**: What it does (for agent selection)
- **Prompt**: Detailed instructions and constraints
- **Model**: Which Claude model to use
- **Tools**: Which tools it can use (Read, Write, Bash, etc.)

### Agent 1: Test Runner

**Purpose**: Execute tests and parse output

**Tools**: `Bash`, `Read`, `Write`

**Workflow**:
1. Run `make test` via Bash
2. Capture stdout/stderr
3. Parse pytest output for failing tests
4. Return structured list of test paths

**Output Format**:
```json
[
  "tests/integration/test_sqlite_qdrant_crawl_mcp.py",
  "tests/integration/test_sqlite_qdrant_crawl_mcp_simple.py"
]
```

**Design Note**: Currently used at orchestrator level, could be delegated to agent in future versions.

### Agent 2: Test Analyzer

**Purpose**: Deep analysis of test failures

**Tools**: `Read`, `Grep`, `Glob`, `Write`

**Workflow**:
1. Read failing test file
2. Analyze error output
3. Identify root cause:
   - Import errors
   - Missing dependencies
   - Configuration issues
   - Database/fixture problems
   - Code logic errors
   - API changes
4. Provide recommendations

**Output Format**:
```markdown
## Root Cause
The test fails because the `CrawlingService` constructor signature changed...

## Evidence
- Line 45: `CrawlingService()` called with no arguments
- Error: "missing required argument 'db_repository'"

## Recommended Fix
1. Update test to pass `db_repository` parameter
2. Create mock repository in test fixture
3. Alternative: Use dependency injection pattern
```

**Critical Design Decision**: Focus on ROOT CAUSE, not symptoms
- Agent is prompted to look deeper than surface errors
- Must provide actionable recommendations
- Should consider multiple potential fixes

### Agent 3: Test Fixer

**Purpose**: Implement fixes based on analysis

**Tools**: `Read`, `Write`, `Edit`, `Grep`, `Glob`, `Bash`

**Workflow**:
1. Read test failure analysis
2. Read failing test file
3. **May also read/modify production code**
4. Implement minimal, targeted fixes
5. List all modified files
6. Explain changes

**Output Format**:
```markdown
## Changes Made

### Files Modified:
1. `tests/integration/test_sqlite_qdrant_crawl_mcp.py`
2. `python/src/server/services/crawling/crawling_service.py`

### Changes:

#### test_sqlite_qdrant_crawl_mcp.py
- Added mock repository fixture
- Updated service initialization to pass repository

#### crawling_service.py
- Made `db_repository` parameter optional with default
- Added backward compatibility

### Reasoning:
The test was failing because...
```

**Critical Feature**: Can modify production code
- **Why**: Tests may fail due to API changes in production code
- **Safety**: Minimal changes, backward compatible when possible
- **Validation**: Full test suite run catches regressions

### Agent 4: Validator

**Purpose**: Validate fixes and check for regressions

**Tools**: `Bash`, `Read`, `Write`

**Workflow**:
1. Run the specific fixed test
2. Check if it passes
3. Run full test suite
4. Check for new failures (regressions)
5. Report outcome

**Output Format**:
```markdown
## Validation Result: PASS

### Specific Test
- Test: `tests/integration/test_sqlite_qdrant_crawl_mcp.py`
- Result: ✅ PASSED

### Regression Check
- Full suite: `make test`
- New failures: None
- All tests passing: Yes

**Verdict**: PASS - Fix is valid and safe to keep
```

**Possible Verdicts**:
- `PASS`: Test fixed, no regressions
- `FAIL`: Test still failing
- `REGRESSION`: Test fixed but broke other tests (triggers rollback)

## Workflow & State Machine

### Test Status States

```
┌─────────┐
│ PENDING │  Initial state
└────┬────┘
     │
     ▼
┌──────────┐
│ANALYZING │  Test Analyzer agent working
└────┬─────┘
     │
     ▼
┌────────┐
│ FIXING │  Test Fixer agent working
└────┬───┘
     │
     ▼
┌───────────┐
│VALIDATING │  Validator agent checking
└─────┬─────┘
      │
      ├───────► [PASS] ───────┐
      │                       │
      ├───────► [FAIL] ────┐  │
      │                    │  │
      └───────► [REGRESSION]  │
                           │  │
                           ▼  ▼
                    ┌──────────┐
                    │  Retry?  │
                    └────┬─────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
              ▼          ▼          ▼
         Attempt 1   Attempt 2  Attempt 3
                         │
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
         ┌───────┐            ┌─────────┐
         │ FIXED │            │ SKIPPED │
         └───────┘            └─────────┘
```

### Main Loop Flow

```python
async def run():
    # 1. Initial test suite run
    failing_tests = run_test_suite()

    # 2. Process each test
    for test_path in failing_tests:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            # 2.1 Analyze
            analysis = test_analyzer_agent.analyze(test_path)

            # 2.2 Fix
            changes = test_fixer_agent.fix(test_path, analysis)

            # 2.3 Validate
            result = validator_agent.validate(test_path)

            # 2.4 Handle result
            if result == PASS:
                mark_fixed(test_path)
                break
            elif result == REGRESSION:
                rollback(test_path)
                # Try again with different approach
            else:  # FAIL
                if attempt == MAX_ATTEMPTS:
                    mark_skipped(test_path)
                # Otherwise retry

    # 3. Final validation
    final_results = run_test_suite()

    # 4. Generate report
    generate_summary_report()
```

## Key Design Decisions

### 1. Sequential vs Parallel Processing

**Decision**: Sequential (one test at a time)

**Reasoning**:
- Simpler state management
- Easier to debug
- Prevents test interference
- File modification conflicts avoided
- Better for initial version

**Future Enhancement**: Could parallelize tests in different directories

### 2. File-Based Backups vs Git

**Decision**: File-based backups in `.test_fix_backups/`

**Reasoning**:
- No Git assumptions (works in any environment)
- Simple implementation (copy files)
- Fast rollback (no Git operations)
- Clear rollback scope (specific files, specific attempts)
- No Git history pollution

**Tradeoff**: Less sophisticated than Git, but much simpler

### 3. State Persistence Strategy

**Decision**: Single JSON file with full state

**Reasoning**:
- Simple to implement
- Easy to inspect/debug
- Atomic writes (no partial states)
- Human-readable format
- No database setup required

**Tradeoff**: Not suitable for huge test suites (100s of tests)

**Alternative for Scale**: SQLite database with transactions

### 4. Agent Specialization

**Decision**: Four specialized agents instead of one general agent

**Reasoning**:
- **Context Isolation**: Each agent has focused context
- **Tool Isolation**: Only necessary tools per agent
- **Prompt Optimization**: Specific instructions per task
- **Parallelization Ready**: Could run analysis and validation in parallel
- **Easier Debugging**: Know which agent failed

**Tradeoff**: More complex coordination, but better results

### 5. Production Code Modification

**Decision**: Allow Test Fixer to modify production code

**Reasoning**:
- Tests may fail due to valid API changes
- Backward compatibility fixes needed
- Real-world scenario (not just test bugs)
- Regression detection prevents breaking changes

**Safety Measures**:
- Full test suite run after each fix
- Rollback on regressions
- Minimal, targeted changes only

### 6. Timeout Protection

**Decision**: 1-hour overall timeout with checks before each test

**Reasoning**:
- Prevents infinite loops
- Reasonable time for typical test suites
- Configurable for different needs
- Graceful exit (saves state)

**Implementation**:
```python
def check_timeout(self) -> bool:
    elapsed = time.time() - self.start_time
    return elapsed > self.timeout_seconds
```

### 7. Retry Logic

**Decision**: Max 3 attempts per test, different approach each time

**Reasoning**:
- **Attempt 1**: Initial fix based on analysis
- **Attempt 2**: Alternative approach after learning from failure
- **Attempt 3**: Final attempt with different strategy
- **After 3**: Mark as SKIPPED (human intervention needed)

**Implementation**: Each attempt gets fresh analysis and fix

## Performance Considerations

### Token Usage

**Optimization Strategies**:
- Use `sonnet` by default (balanced cost/performance)
- Allow `haiku` for simpler tests (in Config)
- Focused agent prompts (minimal context)
- Only read relevant files

**Estimated Costs** (per test):
- Analysis: ~2K tokens
- Fix: ~3K tokens
- Validation: ~1K tokens
- **Total per attempt**: ~6K tokens
- **Max per test**: ~18K tokens (3 attempts)

### Time Estimates

**Per Test** (typical):
- Analysis: 30-60 seconds
- Fix: 45-90 seconds
- Validation: 30-60 seconds
- **Total per attempt**: 2-4 minutes
- **Max per test**: 6-12 minutes

**For 10 failing tests**:
- Best case (all fix on attempt 1): 20-40 minutes
- Worst case (all 3 attempts): 60-120 minutes
- **With 1-hour timeout**: Will process ~5-10 tests

### Optimization Opportunities

1. **Parallel Validation**: Run full suite in background
2. **Batch Analysis**: Analyze similar tests together
3. **Smart Retry**: Skip obviously unfixable tests earlier
4. **Incremental Testing**: Only run affected tests
5. **Caching**: Cache analysis for similar failures

## Error Handling

### Failure Modes & Recovery

#### 1. Agent Timeout
- **Detection**: Agent takes too long
- **Recovery**: Cancel agent, count as failed attempt
- **Prevention**: Add timeout to agent calls (future)

#### 2. Invalid Agent Response
- **Detection**: Agent returns unexpected format
- **Recovery**: Log error, count as failed attempt
- **Prevention**: Better agent prompts with examples

#### 3. File System Errors
- **Detection**: Cannot read/write files
- **Recovery**: Log error, skip test
- **Prevention**: Check permissions before running

#### 4. Test Suite Hangs
- **Detection**: Test command doesn't return
- **Recovery**: Kill process, log error
- **Prevention**: Add timeout to subprocess calls

#### 5. Rollback Fails
- **Detection**: Backup file missing/corrupted
- **Recovery**: Log error, skip test
- **Prevention**: Verify backup creation

#### 6. State Corruption
- **Detection**: Cannot load state JSON
- **Recovery**: Start fresh, log error
- **Prevention**: Atomic writes, validation on load

### Logging Strategy

**Levels of Logging**:

1. **Console (Rich UI)**:
   - Progress updates
   - Status changes
   - Success/warning/error messages
   - Final statistics

2. **JSONL Log File**:
   - All events with timestamps
   - Structured data for analysis
   - Full agent responses
   - Error details

3. **State File**:
   - Current state snapshot
   - Attempt history
   - Statistics

4. **Summary Report**:
   - Human-readable markdown
   - Overview and details
   - Sharable with team

## Testing the Orchestrator

### Unit Testing Approach

**Mock Points**:
1. `subprocess` calls (test runner, test executor)
2. Agent SDK client (agent responses)
3. File system operations (backups, state)

**Test Cases**:
- State persistence and loading
- Test parsing logic
- Status transitions
- Retry logic
- Rollback mechanism
- Timeout handling
- Report generation

### Integration Testing

**Test Scenarios**:
1. **Happy Path**: All tests fix on first attempt
2. **Retry Path**: Some tests need 2-3 attempts
3. **Regression Path**: Fix causes regression, needs rollback
4. **Skip Path**: Test unfixable after 3 attempts
5. **Timeout Path**: Timeout triggers mid-process
6. **Resume Path**: Interrupted and resumed

### Example Test Structure

```python
def test_fix_test_happy_path():
    # Setup
    orchestrator = TestFixOrchestrator()
    mock_state = create_mock_state()
    orchestrator.state_manager.state = mock_state

    # Mock agent responses
    mock_analysis = "Root cause: import error"
    mock_fix = "Added import statement"
    mock_validation = "PASS"

    # Execute
    attempt = await orchestrator.fix_test("tests/test_foo.py", 1)

    # Assert
    assert attempt.validation_result == True
    assert "import" in attempt.changes_made[0]
```

## Future Enhancements

### High Priority

1. **Parallel Test Processing**
   - Process independent tests simultaneously
   - Requires file conflict detection
   - 3-5x speedup potential

2. **Smart Test Ordering**
   - Analyze test dependencies
   - Fix foundational tests first
   - May prevent cascading failures

3. **Incremental Testing**
   - Only run tests affected by changes
   - Much faster validation
   - Requires dependency analysis

### Medium Priority

4. **Agent Result Parsing**
   - Structured agent responses (JSON)
   - Better validation of agent output
   - More reliable automation

5. **Cost Tracking**
   - Track API costs per test
   - Budget constraints
   - Cost optimization suggestions

6. **Interactive Mode**
   - Pause for human review
   - Manual intervention option
   - Hybrid human/AI fixing

### Low Priority

7. **Web Dashboard**
   - Real-time progress visualization
   - Historical run analysis
   - Cost tracking UI

8. **Git Integration**
   - Optional Git-based rollback
   - Auto-commit after each fix
   - PR creation for fixes

9. **Multi-Language Support**
   - Support non-Python tests (Jest, JUnit, etc.)
   - Pluggable test runners
   - Language-specific agents

## Conclusion

The Test Fix Orchestrator demonstrates:

- **Agent Orchestration**: Coordinating multiple specialized agents
- **State Management**: Persistent, resumable workflows
- **Error Recovery**: Rollback and retry mechanisms
- **Safety**: Regression detection and protection
- **Production Ready**: Logging, monitoring, reporting

**Key Takeaway**: AI agents can handle complex, multi-step workflows when properly orchestrated with clear responsibilities, safety mechanisms, and human oversight capabilities.
