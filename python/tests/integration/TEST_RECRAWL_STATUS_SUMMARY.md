# Recrawl Status Integration Test Summary

## Files Created

### 1. Test File
**Location**: `python/tests/integration/test_recrawl_status.py`

**Purpose**: Comprehensive integration test suite that reproduces the recrawl status bug using REAL services (no mocks).

**Test Coverage**:
- ✅ `test_backend_health()` - Verify backend is running
- ✅ `test_database_connection()` - Verify database is accessible
- ✅ `test_initial_crawl_status_lifecycle()` - Baseline test for initial crawl
- ✅ `test_recrawl_status_remains_completed()` - **CORE BUG TEST**
- ✅ `test_multiple_recrawls_status_stability()` - Race condition test
- ✅ `test_failed_crawl_sets_failed_status()` - Error handling test

### 2. Documentation
**Location**: `/home/jose/src/Archon/INTEGRATION_TEST.md`

**Contents**:
- Test strategy and rationale
- Why we use real services (no mocks)
- Environment requirements
- How to run tests
- Expected test duration
- How to interpret results
- Debugging guide
- Example output

## Quick Start

### Prerequisites

1. **Backend Running**:
   ```bash
   docker compose up -d archon-server
   # OR
   cd python && uv run python -m src.server.main
   ```

2. **Environment Variables**:
   ```bash
   # .env file
   OPENAI_API_KEY=sk-...  # Or other embedding provider
   ```

3. **Database Ready**:
   - SQLite: `data/archon.db` exists with schema
   - OR Supabase: Configured in `.env`

### Run Tests

```bash
# Full suite (6 tests, ~3-7 minutes)
uv run pytest python/tests/integration/test_recrawl_status.py -v -s

# Core bug test only (~60-120 seconds)
uv run pytest python/tests/integration/test_recrawl_status.py::test_recrawl_status_remains_completed -v -s

# Quick verification (just health checks)
uv run pytest python/tests/integration/test_recrawl_status.py -k "health or connection" -v -s
```

## Test Strategy

### Why Real Services?

The bug is a **data persistence and timing issue** that ONLY occurs in real conditions:

1. **Race Conditions**: Document storage vs status updates happen concurrently
2. **Metadata Merge**: Repository may not properly merge nested fields
3. **Missing Initialization**: Field never gets created during source creation
4. **Async Timing**: Background tasks complete at unpredictable times

**Mocks would hide the bug** by bypassing the exact code paths where it occurs.

### What We Test

1. **Database State**: Direct SQLite queries to verify `metadata.crawl_status`
2. **API Responses**: Check `/api/knowledge-items/summary` for status mapping
3. **Progress Tracking**: Poll `/api/crawl-progress/{progress_id}` for real-time status
4. **Document Persistence**: Verify crawled pages are stored
5. **Status Transitions**: Track status changes through complete lifecycle

## Expected Results

### If Bug is FIXED

```
✅ TEST 2 PASSED: Recrawl status remains 'completed' (Bug is FIXED!)

CRITICAL ASSERTIONS (Testing for bug):
✓ PASS: Database crawl_status is 'completed'
✓ PASS: API crawl_status is 'completed'
✓ PASS: API status is 'active' (correct mapping)
✓ PASS: 3 documents persisted
```

### If Bug STILL EXISTS

```
❌ BUG DETECTED: Database crawl_status should be 'completed' after recrawl,
got 'pending'. This is the bug described in INVESTIGATION_REPORT.md!

AssertionError: Database crawl_status should be 'completed' after recrawl,
got 'pending'. This is the bug described in INVESTIGATION_REPORT.md!
```

## Test Architecture

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  TEST: test_recrawl_status_remains_completed()                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Initial Crawl                                          │
│  POST /api/knowledge-items/crawl                                │
│  → Poll /api/crawl-progress/{progress_id}                       │
│  → Wait for status="completed"                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: Verify Initial Status                                  │
│  • Query SQLite: SELECT metadata FROM archon_sources            │
│  • Assert: crawl_status = "completed"                           │
│  • Query API: GET /api/knowledge-items/summary                  │
│  • Assert: status = "active"                                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Trigger Recrawl                                        │
│  POST /api/knowledge-items/{source_id}/refresh                  │
│  → Returns new progress_id                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: Wait for Recrawl Completion                            │
│  → Poll /api/crawl-progress/{recrawl_progress_id}               │
│  → Wait for status="completed"                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: CRITICAL ASSERTIONS (Bug Test)                         │
│  • Query SQLite: SELECT metadata FROM archon_sources            │
│  • Assert: crawl_status = "completed" ⚠️ May fail if bug exists │
│  • Query API: GET /api/knowledge-items/summary                  │
│  • Assert: status = "active" ⚠️ May be "processing" if bug exists│
│  • Verify documents persisted                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Helper Functions

- `wait_for_crawl_completion()` - Smart polling with timeout
- `get_source_from_db()` - Direct SQLite query
- `get_source_by_id_from_api()` - API query
- `get_document_count()` - Count crawled pages

## Key Test Parameters

```python
TEST_URL = "https://example.com"           # Fast, reliable test URL
INITIAL_CRAWL_TIMEOUT = 120                # 2 minutes
RECRAWL_TIMEOUT = 120                      # 2 minutes
POLL_INTERVAL = 3                          # Poll every 3 seconds
```

## Integration Points

The test exercises these real system components:

1. **API Endpoints**:
   - `POST /api/knowledge-items/crawl`
   - `POST /api/knowledge-items/{source_id}/refresh`
   - `GET /api/crawl-progress/{progress_id}`
   - `GET /api/knowledge-items/summary`

2. **Services**:
   - `CrawlingService` - Orchestrates crawl
   - `DocumentStorageService` - Stores crawled content
   - `SourceManagementService` - Updates source metadata
   - `KnowledgeSummaryService` - Provides API responses
   - `ProgressTracker` - Tracks operation status

3. **Database**:
   - `archon_sources` table - Source records with metadata
   - `archon_crawled_pages` table - Crawled documents
   - JSON metadata field - Contains `crawl_status`

4. **Background Tasks**:
   - Async crawl orchestration
   - Document processing
   - Status updates

## Debugging

### Check Logs

```bash
# Backend logs
docker compose logs archon-server -f | grep -i "crawl_status"

# Look for:
# ✓ "Updated source crawl_status to completed"
# ✗ "Failed to update source crawl_status"
```

### Check Database

```bash
sqlite3 data/archon.db "
  SELECT
    source_id,
    title,
    json_extract(metadata, '$.crawl_status') as crawl_status,
    datetime(created_at) as created,
    datetime(updated_at) as updated
  FROM archon_sources
  WHERE source_url = 'https://example.com'
  ORDER BY created_at DESC
  LIMIT 5
"
```

### Run Single Test with Debug

```bash
# Add print statements in test
uv run pytest python/tests/integration/test_recrawl_status.py::test_recrawl_status_remains_completed -v -s

# With logging
LOGLEVEL=DEBUG uv run pytest python/tests/integration/test_recrawl_status.py -v -s
```

## Cleanup

Tests create real data. Clean up with:

```bash
# Delete test sources
sqlite3 data/archon.db "
  DELETE FROM archon_sources
  WHERE source_url = 'https://example.com'
"

# Or use fix endpoint
curl -X POST http://localhost:8181/api/knowledge-items/fix-pending-statuses
```

## Next Steps

1. **Run the tests** to verify they work
2. **If tests PASS**: Bug is already fixed, document the fix
3. **If tests FAIL**: Bug is reproduced, proceed with fixes from INVESTIGATION_REPORT.md
4. **After fix**: Re-run tests to verify fix works

## Related Files

- `INVESTIGATION_REPORT.md` - Root cause analysis
- `INTEGRATION_TEST.md` - Detailed test documentation
- `python/tests/integration/test_crawl_status_integration.py` - Similar test (may have overlap)
- `python/src/server/services/crawling/crawling_service.py` - Lines 580-599 (status update logic)
- `python/src/server/services/source_management_service.py` - Line 285-287 (conditional update)

## Success Criteria

- ✅ All 6 tests pass
- ✅ Test 2 (core bug test) passes consistently
- ✅ Test 3 (multiple recrawls) shows stable status
- ✅ Test 4 (error handling) works correctly
- ✅ Tests complete in < 10 minutes
- ✅ No manual cleanup needed

## Contribution

When fixing the bug:

1. Run tests BEFORE fix to confirm they fail
2. Implement fix per INVESTIGATION_REPORT.md
3. Run tests AFTER fix to confirm they pass
4. Commit with test results in PR description

Example commit message:
```
fix: Set crawl_status during source creation and refresh

- Add crawl_status="pending" in document_storage_operations.py
- Set crawl_status="pending" at refresh start in knowledge_api.py
- Add verification logging in crawling_service.py

Tests: All integration tests pass
- test_recrawl_status_remains_completed: PASS
- test_multiple_recrawls_status_stability: PASS
- test_failed_crawl_sets_failed_status: PASS

Fixes bug where status showed "Pending" after successful recrawl.
See INVESTIGATION_REPORT.md for root cause analysis.
```
