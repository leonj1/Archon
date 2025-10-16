# Integration Test: Recrawl Status Bug

## Overview

This document describes the comprehensive integration test suite for the recrawl status bug described in `INVESTIGATION_REPORT.md`.

## Test Strategy

### Why Real Services (No Mocks)?

The recrawl status bug is a **data persistence and timing issue** that can only be reproduced in a real environment with:

1. **Real Database Operations**: The bug involves metadata updates that may not persist correctly due to:
   - Race conditions between document storage and status updates
   - Metadata merge issues in the repository layer
   - Missing field initialization during source creation

2. **Real Async Operations**: The crawling service runs background tasks that:
   - Create sources asynchronously
   - Process documents in batches
   - Update status at different stages
   - Race conditions only occur with real timing

3. **Real HTTP Polling**: The frontend polls for progress updates:
   - We need to test the actual polling mechanism
   - Status transitions must be verified through the real API
   - Cache behavior affects what the user sees

4. **Real Network Crawling**: We need to verify:
   - Actual crawl completion triggers status updates
   - Document storage happens correctly
   - The complete flow from HTTP request to database persistence

**Mocks would hide the bug** by bypassing the actual code paths where the issue occurs.

## Test Suite

### Test 1: Initial Crawl Status Lifecycle

**Purpose**: Establish baseline behavior before testing recrawl.

**Flow**:
1. Start crawl for a new URL
2. Poll progress endpoint until completion
3. Verify status is "completed" in both API and database
4. Verify documents were stored

**Expected Result**: Status should be "completed" after successful crawl.

**Why This Test**:
- Validates that the test infrastructure works
- Establishes baseline for comparison
- May also fail if initial crawl has the same bug

### Test 2: Recrawl Status Bug Reproduction (CORE TEST)

**Purpose**: Reproduce the exact bug described in INVESTIGATION_REPORT.md.

**Flow**:
1. Create source via initial crawl
2. Wait for completion and verify status is "completed"
3. Trigger recrawl using `/api/knowledge-items/{source_id}/refresh`
4. Poll progress endpoint until recrawl completes
5. **CRITICAL**: Verify status is STILL "completed" (not "pending")
6. Verify in both database and API responses

**Expected Result (AFTER FIX)**:
- Database `metadata.crawl_status` = "completed"
- API `status` = "active" (mapped from completed)
- Frontend shows "Completed" badge (green checkmark)

**Actual Result (CURRENT BUG)**:
- Database `metadata.crawl_status` = "pending" (or missing)
- API `status` = "processing" (mapped from pending)
- Frontend shows "Pending" badge (yellow clock)

**Why This Test**:
- This is the exact bug users are experiencing
- Tests the complete recrawl flow end-to-end
- Verifies both database and API consistency

### Test 3: Multiple Recrawls Status Stability

**Purpose**: Test for race conditions or state corruption with repeated recrawls.

**Flow**:
1. Create initial source
2. Perform 3 consecutive recrawls
3. Verify status is "completed" after EACH recrawl

**Expected Result**: Status should remain stable across multiple operations.

**Why This Test**:
- Race conditions may only appear with repeated operations
- Tests for state corruption or accumulation of bugs
- Validates fix doesn't break under repeated use

### Test 4: Failed Crawl Status

**Purpose**: Ensure error handling doesn't break status updates.

**Flow**:
1. Trigger crawl with invalid URL
2. Wait for failure
3. Verify status is "failed"

**Expected Result**: Failed crawls should set status to "failed" correctly.

**Why This Test**:
- Error path must also update status correctly
- Validates fix doesn't break error handling
- Tests defensive programming

## Environment Requirements

### Backend Services

1. **Archon Backend Running**:
   ```bash
   docker compose up -d archon-server
   # OR
   cd python && uv run python -m src.server.main
   ```
   - Must be accessible at `http://localhost:8181`
   - Health check: `curl http://localhost:8181/health`

2. **Database**:
   - SQLite: `data/archon.db` must exist with schema
   - OR Supabase: Must be configured in `.env`

3. **Embedding Provider**:
   - Valid API key must be configured (OpenAI, Ollama, etc.)
   - Test will fail immediately if API key is invalid

### Environment Variables

Required:
```bash
# In .env file or environment
ARCHON_API_URL=http://localhost:8181  # Optional, defaults to localhost:8181
SQLITE_PATH=/path/to/archon.db        # Optional, defaults to data/archon.db

# Embedding provider (one of):
OPENAI_API_KEY=sk-...                 # For OpenAI
# OR
OLLAMA_BASE_URL=http://localhost:11434  # For Ollama
```

### Network Requirements

- Internet connectivity required (tests crawl https://example.com)
- Firewall must allow outbound HTTPS
- DNS resolution must work

## Running the Tests

### Full Test Suite

```bash
# From project root
uv run pytest python/tests/integration/test_recrawl_status.py -v -s

# Or with full paths
uv run pytest /home/jose/src/Archon/python/tests/integration/test_recrawl_status.py -v -s
```

### Individual Tests

```bash
# Run specific test
uv run pytest python/tests/integration/test_recrawl_status.py::test_recrawl_status_remains_completed -v -s

# Run only bug reproduction test
uv run pytest python/tests/integration/test_recrawl_status.py -k "recrawl_status_remains" -v -s
```

### With Markers

```bash
# Run all integration tests
uv run pytest python/tests/integration/ -m integration -v -s

# Skip slow tests
uv run pytest python/tests/integration/test_recrawl_status.py -m "not slow" -v -s
```

## Expected Test Duration

- **Test 1** (Initial Crawl): ~30-60 seconds
- **Test 2** (Recrawl Bug): ~60-120 seconds (includes initial crawl + recrawl)
- **Test 3** (Multiple Recrawls): ~120-240 seconds (3 recrawls)
- **Test 4** (Failed Crawl): ~10-30 seconds

**Total Suite Duration**: ~3-7 minutes

The tests use `example.com` which is small and fast to crawl. Real documentation sites would take much longer.

## Interpreting Test Results

### Success (Bug is Fixed)

```
✅ TEST 2 PASSED: Recrawl status remains 'completed' (Bug is FIXED!)
```

All assertions pass:
- Database `crawl_status` = "completed"
- API `status` = "active"
- Documents persisted correctly

### Failure (Bug Still Exists)

```
❌ BUG DETECTED: Database crawl_status should be 'completed' after recrawl,
got 'pending'. This is the bug described in INVESTIGATION_REPORT.md!
```

The test will fail with clear error messages indicating:
- What value was expected
- What value was actually found
- Which assertion failed (database vs API)

### Timeout

```
TimeoutError: Recrawl did not complete within 120s.
Last status: processing
```

Possible causes:
- Crawl is genuinely slow (increase timeout)
- Crawl is stuck (bug in crawling service)
- Network issues
- Backend crashed

### Skip

```
SKIPPED: Backend not available at http://localhost:8181
```

Environment requirements not met:
- Backend not running
- Database not accessible
- API key not configured

## Test Output Example

```
================================ test session starts =================================
platform linux -- Python 3.12.0, pytest-8.0.0

collected 6 items

python/tests/integration/test_recrawl_status.py::test_backend_health
✓ Backend is healthy at http://localhost:8181
PASSED

python/tests/integration/test_recrawl_status.py::test_database_connection
✓ Database connection successful (15 tables found)
PASSED

python/tests/integration/test_recrawl_status.py::test_initial_crawl_status_lifecycle
================================================================================
TEST 1: Initial Crawl Status Lifecycle
================================================================================

[1/5] Starting initial crawl of https://example.com...
✓ Crawl started with progress_id: a1b2c3d4-e5f6-7890-abcd-ef1234567890

[2/5] Waiting for crawl to complete...
⏳ Waiting for initial crawl completion (timeout: 120s)...
  [3s] Status: starting, Progress: 5%, Pages: 0/0
  [6s] Status: crawling, Progress: 30%, Pages: 1/1
  [9s] Status: processing, Progress: 60%, Pages: 1/1
  [12s] Status: completed, Progress: 100%, Pages: 1/1
✓ Initial crawl completed successfully!
✓ Source created: src_example_com_abc123

[3/5] Verifying status in database...
  Database crawl_status: completed

[4/5] Verifying status via API...
  API status: active
  API crawl_status: completed

[5/5] Verifying documents were stored...
  Document count: 3

================================================================================
✅ TEST 1 PASSED: Initial crawl status lifecycle works correctly
================================================================================
PASSED

python/tests/integration/test_recrawl_status.py::test_recrawl_status_remains_completed
================================================================================
TEST 2: Recrawl Status Bug Reproduction
================================================================================

[1/7] Creating initial source via crawl...

[2/7] Waiting for initial crawl to complete...
⏳ Waiting for initial crawl completion (timeout: 120s)...
  [3s] Status: starting, Progress: 5%, Pages: 0/0
  [6s] Status: crawling, Progress: 30%, Pages: 1/1
  [9s] Status: completed, Progress: 100%, Pages: 1/1
✓ Initial crawl completed successfully!
✓ Initial crawl completed, source_id: src_example_com_def456

[3/7] Verifying initial status is 'completed'...
  Before recrawl:
    - crawl_status: completed
    - document count: 3

[4/7] Triggering recrawl via refresh endpoint...
✓ Recrawl started with progress_id: b2c3d4e5-f6g7-8901-bcde-fg2345678901

[5/7] Waiting for recrawl to complete...
⏳ Waiting for recrawl completion (timeout: 120s)...
  [3s] Status: starting, Progress: 5%, Pages: 0/0
  [6s] Status: crawling, Progress: 30%, Pages: 1/1
  [9s] Status: completed, Progress: 100%, Pages: 1/1
✓ Recrawl completed!

[6/7] Verifying status AFTER recrawl in database...
  After recrawl (Database):
    - crawl_status: completed
    - document count: 3

[7/7] Verifying status AFTER recrawl via API...
  After recrawl (API):
    - status: active
    - crawl_status: completed

--------------------------------------------------------------------------------
CRITICAL ASSERTIONS (Testing for bug):
--------------------------------------------------------------------------------

✓ Checking database crawl_status...
  ✓ PASS: Database crawl_status is 'completed'

✓ Checking API crawl_status...
  ✓ PASS: API crawl_status is 'completed'

✓ Checking API status mapping...
  ✓ PASS: API status is 'active' (correct mapping)

✓ Checking documents persisted...
  ✓ PASS: 3 documents persisted

================================================================================
✅ TEST 2 PASSED: Recrawl status remains 'completed' (Bug is FIXED!)
================================================================================
PASSED

============================== 6 passed in 142.35s ==============================
```

## Debugging Test Failures

### Check Backend Logs

```bash
# Docker logs
docker compose logs archon-server -f

# Local logs
tail -f logs/archon.log
```

Look for:
- `"Updated source crawl_status to completed"` - Status update executed
- `"Failed to update source crawl_status"` - Status update failed
- `"Verified crawl_status after update"` - Verification logging (if implemented)

### Check Database Directly

```bash
sqlite3 data/archon.db

# Check source status
SELECT source_id, title, json_extract(metadata, '$.crawl_status') as crawl_status
FROM archon_sources
ORDER BY created_at DESC
LIMIT 5;

# Check documents
SELECT source_id, COUNT(*) as doc_count
FROM archon_crawled_pages
GROUP BY source_id;
```

### Enable Debug Logging

In `python/src/server/config/logfire_config.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Test with Real URL

Change `TEST_URL` in the test file:
```python
TEST_URL = "https://docs.python.org/3/tutorial/index.html"
```

This will take longer but tests with real documentation.

## Implementation Notes

### Polling Strategy

The test uses **smart polling**:
- Poll interval: 3 seconds
- Timeout: 120 seconds (2 minutes)
- Handles 404 (progress not found yet)
- Detects completion, failure, and timeout

### Database Access

Tests access SQLite database directly:
- Reads from `archon_sources` table
- Parses JSON metadata
- Counts documents in `archon_crawled_pages`
- Validates data consistency

### Cleanup

Tests create real sources in the database. You may want to clean up:

```bash
# Delete test sources
sqlite3 data/archon.db "DELETE FROM archon_sources WHERE source_url = 'https://example.com'"
```

Or use the fix endpoint:
```bash
curl -X POST http://localhost:8181/api/knowledge-items/fix-pending-statuses
```

## Future Enhancements

1. **Parallel Recrawls**: Test concurrent recrawls on same source
2. **Large Documents**: Test with documentation sites (longer duration)
3. **Failure Scenarios**: Test network failures during recrawl
4. **Status Transitions**: Record all status transitions for analysis
5. **Performance Metrics**: Measure recrawl duration and compare to initial crawl

## Related Documentation

- `INVESTIGATION_REPORT.md` - Root cause analysis of the bug
- `python/tests/integration/README_SQLITE_QDRANT.md` - Integration test patterns
- `PRPs/ai_docs/ARCHITECTURE.md` - System architecture overview

## Contact

If tests fail or you need help:
1. Check backend logs for errors
2. Verify environment variables
3. Ensure backend is running and healthy
4. Check database exists and has schema
5. Verify API key is valid
