# Test Fix Orchestrator

Automated test fixing using Claude Agent SDK with specialized agents for identifying, analyzing, fixing, and validating test failures.

## Features

### ✅ Core Capabilities

- **Automated Test Fixing**: Runs full test suite, identifies failures, and fixes them automatically
- **State Persistence**: Save/resume progress via JSON state file
- **Smart Retry Logic**: Max 3 attempts per test with intelligent failure analysis
- **Timeout Protection**: 1-hour overall timeout to prevent runaway execution
- **Rollback Safety**: File-based rollback when fixes cause regressions
- **Production Code Fixes**: Can fix production code when tests fail due to API changes
- **Comprehensive Logging**: Structured JSONL logs for all operations
- **Progress Tracking**: Real-time progress display with Rich UI
- **Summary Reports**: Markdown report of all fixes and attempts

### 🤖 Specialized Agents

1. **Test Runner Agent**: Executes test suite and parses pytest output
2. **Test Analyzer Agent**: Deep root cause analysis of test failures
3. **Test Fixer Agent**: Implements fixes based on analysis (can modify production code)
4. **Validator Agent**: Validates fixes and checks for regressions

## Installation

### Prerequisites

```bash
# Install Claude Agent SDK
pip install claude-agent-sdk

# Or with uv (recommended for this project)
uv add claude-agent-sdk

# Install dependencies
pip install rich python-dotenv
# or
uv add rich python-dotenv
```

### Environment Setup

Ensure your `.env` file contains:

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

### Basic Usage

```bash
# Run the orchestrator
python test_fix_orchestrator.py

# Or with uv
uv run python test_fix_orchestrator.py
```

The orchestrator will:
1. Run `make test` to identify failing tests
2. Process each failing test sequentially
3. Attempt up to 3 fixes per test
4. Generate a summary report

### Resume from Interruption

If interrupted (Ctrl+C or timeout), simply run again:

```bash
python test_fix_orchestrator.py
```

The orchestrator will load `test_fix_state.json` and continue where it left off.

### Start Fresh

To ignore previous state and start over:

```bash
# Remove state file
rm test_fix_state.json

# Run orchestrator
python test_fix_orchestrator.py
```

## Configuration

Edit the `Config` class in `test_fix_orchestrator.py`:

```python
class Config:
    MAX_ATTEMPTS_PER_TEST = 3      # Max attempts per test
    TIMEOUT_HOURS = 1              # Overall timeout
    STATE_FILE = "test_fix_state.json"
    LOG_FILE = "test_fix_log.jsonl"
    SUMMARY_FILE = "TEST_FIX_SUMMARY.md"
    BACKUP_DIR = ".test_fix_backups"
    TEST_COMMAND = "make test"     # Command to run tests
    MODEL = "sonnet"               # Claude model to use
```

## Output Files

### State File: `test_fix_state.json`

Persistent state with:
- All test records
- Attempt history
- Current progress
- Statistics

Example structure:
```json
{
  "started_at": "2025-01-14T20:30:00",
  "last_updated": "2025-01-14T21:00:00",
  "tests": {
    "tests/integration/test_foo.py": {
      "status": "fixed",
      "attempts": [...],
      "fixed_at": "2025-01-14T20:45:00"
    }
  },
  "total_tests": 10,
  "fixed_count": 8,
  "skipped_count": 2
}
```

### Log File: `test_fix_log.jsonl`

Structured logs in JSON Lines format:

```json
{"timestamp": "2025-01-14T20:30:00", "event_type": "info", "message": "Starting orchestrator"}
{"timestamp": "2025-01-14T20:30:15", "event_type": "analysis_complete", "test": "tests/test_foo.py", "analysis": "..."}
{"timestamp": "2025-01-14T20:31:00", "event_type": "fix_applied", "test": "tests/test_foo.py", "changes": "..."}
```

### Summary Report: `TEST_FIX_SUMMARY.md`

Markdown report with:
- Overview statistics
- Detailed results per test
- All attempt details
- Fix summaries

### Backups: `.test_fix_backups/`

File backups for rollback:
- Named with test path and attempt number
- Preserved for all modification attempts
- Used for rollback on regression

## How It Works

### Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    Test Fix Orchestrator                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Run Test Suite │ ◄── make test
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Parse Failures  │ ◄── Extract test paths
                    └─────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  For Each Failing Test (Sequential)     │
        └─────────────────────────────────────────┘
                              │
          ┌───────────────────┴───────────────────┐
          │                                       │
          ▼                                       ▼
    ┌──────────┐                          ┌──────────┐
    │ Attempt 1│                          │ Attempt 2│
    └──────────┘                          └──────────┘
          │                                       │
          ▼                                       ▼
    ┌─────────────┐                        (Repeat up to
    │  1. Analyze │                         3 attempts)
    └─────────────┘
          │
          ▼
    ┌─────────────┐
    │   2. Fix    │ ◄── May fix production code
    └─────────────┘
          │
          ▼
    ┌─────────────┐
    │ 3. Validate │
    └─────────────┘
          │
          ▼
    ┌─────────────┐
    │   Pass?     │
    └─────────────┘
      │         │
      │ YES     │ NO
      ▼         ▼
   [FIXED]   [RETRY or SKIP]
```

### Agent Coordination

Each test goes through this pipeline:

1. **Test Runner Agent**
   - Executes `make test`
   - Parses pytest output
   - Extracts failing test paths

2. **Test Analyzer Agent** (per test)
   - Reads test file
   - Analyzes error output
   - Identifies root cause
   - Recommends fix approach

3. **Test Fixer Agent** (per test)
   - Implements recommended fixes
   - Can modify production code if needed
   - Makes minimal, targeted changes
   - Lists all modified files

4. **Validator Agent** (per test)
   - Runs the fixed test
   - Checks for regressions (runs full suite)
   - Reports PASS/FAIL/REGRESSION
   - Triggers rollback if regression detected

### Rollback Mechanism

When a fix causes regressions:

1. **Detection**: Validator agent runs full test suite after fix
2. **Backup**: Original files backed up before each attempt
3. **Restore**: Files restored from `.test_fix_backups/`
4. **Retry**: Next attempt uses different approach

**No Git Required**: Rollback uses file-based backups only.

### Timeout Protection

- **Overall Timeout**: 1 hour (configurable)
- **Check Points**: Before each test processing
- **Graceful Exit**: Saves state and generates report on timeout

### Retry Logic

Per test:
- **Attempt 1**: Initial fix based on analysis
- **Attempt 2**: Alternative approach if first fails
- **Attempt 3**: Final attempt with different strategy
- **After 3 Failures**: Mark as SKIPPED with reason

### State Transitions

```
PENDING → ANALYZING → FIXING → VALIDATING → FIXED
                                           → FAILED (retry)
                                           → SKIPPED (after 3 attempts)
```

## Advanced Usage

### Production Code Fixes

The Test Fixer Agent can modify production code when tests fail due to API changes:

**Example Scenario**: Test fails because a function signature changed

```python
# Test expects:
result = calculate_total(items, tax_rate)

# But function now requires:
result = calculate_total(items, tax_rate, discount)
```

The agent will:
1. Detect the signature mismatch
2. Update the production code or test appropriately
3. Ensure backward compatibility if possible

### Handling Dependencies

When fixing Test A breaks Test B:

1. Validator detects the regression
2. Changes are rolled back
3. Next attempt considers the dependency
4. May fix both tests together or adjust approach

### Custom Test Commands

Modify the test command in `Config`:

```python
class Config:
    TEST_COMMAND = "cd python && uv run pytest tests/ -v"
```

### Different Models

Use different Claude models:

```python
class Config:
    MODEL = "haiku"  # Faster, cheaper
    # or
    MODEL = "sonnet"  # Default, balanced
    # or
    MODEL = "opus"  # Most capable
```

## Monitoring Progress

### Real-Time Display

The orchestrator shows:
- Current test being processed
- Attempt number
- Status transitions
- Live progress table

### Log Analysis

Query the JSONL log:

```bash
# Show all errors
jq 'select(.event_type == "error")' test_fix_log.jsonl

# Show fixes applied
jq 'select(.event_type == "fix_applied")' test_fix_log.jsonl

# Show successful fixes
jq 'select(.event_type == "success")' test_fix_log.jsonl
```

### Check State

```bash
# Pretty print current state
jq '.' test_fix_state.json

# Count by status
jq '.tests | map(.status) | group_by(.) | map({status: .[0], count: length})' test_fix_state.json
```

## Troubleshooting

### Orchestrator Hangs

- Check agent logs in console
- Look for stuck Bash commands
- Verify test command works manually
- Increase timeout if needed

### All Fixes Fail

- Review analysis in logs
- Check if environmental issue (missing deps)
- Verify Anthropic API key is valid
- Check model rate limits

### Regressions Keep Happening

- Tests may have hidden dependencies
- Consider fixing in different order
- May need manual intervention
- Check if database state is shared

### State File Corrupted

```bash
# Backup corrupted state
mv test_fix_state.json test_fix_state.json.backup

# Start fresh
python test_fix_orchestrator.py
```

## Best Practices

1. **Run in Clean Environment**: Ensure no other processes modifying files
2. **Commit Before Running**: Have a clean git state for easy recovery
3. **Monitor First Run**: Watch the first few fixes to ensure quality
4. **Review Summary**: Always review the generated summary report
5. **Validate Manually**: Run full test suite after orchestrator completes

## Limitations

- **Sequential Processing**: Fixes one test at a time (not parallel)
- **Context Window**: Very large test files may hit token limits
- **Environmental Issues**: Cannot fix missing dependencies or config
- **Flaky Tests**: May not fix intermittent failures
- **Complex Dependencies**: Multi-file dependencies may require multiple attempts

## Examples

### Example Output

```
╭────────────────────────────────────────────╮
│      Test Fix Orchestrator                 │
│ Max attempts per test: 3                   │
│ Timeout: 1 hour(s)                         │
╰────────────────────────────────────────────╯

ℹ️  Running test suite: make test
ℹ️  Found 5 failing tests

┏━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric       ┃ Count ┃
┡━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Tests  │ 5     │
│ Fixed        │ 0     │
│ Failed       │ 0     │
│ Skipped      │ 0     │
│ Elapsed      │ 00:00 │
└──────────────┴───────┘

============================================================
Processing: tests/integration/test_sqlite_qdrant_crawl_mcp.py
============================================================

ℹ️  Fixing test tests/integration/test_sqlite_qdrant_crawl_mcp.py (attempt 1/3)
✅ Test tests/integration/test_sqlite_qdrant_crawl_mcp.py fixed successfully!

┏━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric       ┃ Count ┃
┡━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Tests  │ 5     │
│ Fixed        │ 1     │
│ Failed       │ 0     │
│ Skipped      │ 0     │
│ Elapsed      │ 02:15 │
└──────────────┴───────┘

...
```

### Example Summary Report

See `TEST_FIX_SUMMARY.md` after running:

```markdown
# Test Fix Summary Report

**Generated:** 2025-01-14 21:00:00
**Started:** 2025-01-14T20:30:00
**Duration:** 0:30:00

## Overview

- **Total Tests:** 5
- **Fixed:** 3 ✅
- **Failed:** 0 ❌
- **Skipped:** 2 ⏭️

## Detailed Results

### tests/integration/test_sqlite_qdrant_crawl_mcp.py

**Status:** fixed
**Attempts:** 1
**Fixed at:** 2025-01-14T20:35:00

#### Attempts:

**Attempt 1** (2025-01-14T20:32:00):
- **Result:** ✅ PASS

---
```

## Contributing

To extend the orchestrator:

1. **Add New Agents**: Define in `create_agent_options()`
2. **Custom Parsing**: Modify `parse_failing_tests()`
3. **Different Test Runners**: Change `TEST_COMMAND` and parsing logic
4. **Enhanced Analysis**: Improve agent prompts

## License

Same as parent project (Archon).

## Support

For issues:
- Check logs: `test_fix_log.jsonl`
- Review state: `test_fix_state.json`
- See summary: `TEST_FIX_SUMMARY.md`
- Check backups: `.test_fix_backups/`
