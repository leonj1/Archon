# Quick Reference: Running Recrawl Status Integration Tests

## Prerequisites Checklist

- [ ] Backend is running (`docker compose up -d` OR `cd python && uv run python -m src.server.main`)
- [ ] Backend is healthy: `curl http://localhost:8181/health`
- [ ] Embedding provider API key is configured (check `.env` file)
- [ ] Database exists: `ls -lh /home/jose/src/Archon/data/archon.db`
- [ ] Internet connectivity available

## Quick Commands

### Run All Tests (~3-7 minutes)
```bash
cd /home/jose/src/Archon
uv run pytest python/tests/integration/test_recrawl_status.py -v -s
```

### Run Core Bug Test Only (~60-120 seconds)
```bash
uv run pytest python/tests/integration/test_recrawl_status.py::test_recrawl_status_remains_completed -v -s
```

### Run Health Checks Only (~1 second)
```bash
uv run pytest python/tests/integration/test_recrawl_status.py -k "health or connection" -v -s
```

### Run with Markers
```bash
# All integration tests
uv run pytest python/tests/integration/test_recrawl_status.py -m integration -v -s

# Asyncio tests only
uv run pytest python/tests/integration/test_recrawl_status.py -m asyncio -v -s
```

## Expected Output (Success)

```
================================ test session starts =================================
collected 6 items

python/tests/integration/test_recrawl_status.py::test_backend_health PASSED
python/tests/integration/test_recrawl_status.py::test_database_connection PASSED
python/tests/integration/test_recrawl_status.py::test_initial_crawl_status_lifecycle PASSED
python/tests/integration/test_recrawl_status.py::test_recrawl_status_remains_completed PASSED
python/tests/integration/test_recrawl_status.py::test_multiple_recrawls_status_stability PASSED
python/tests/integration/test_recrawl_status.py::test_failed_crawl_sets_failed_status PASSED

============================== 6 passed in 142.35s ==============================
```

## Common Issues

### Backend Not Running
```
SKIPPED: Backend not available at http://localhost:8181
```
**Fix**: Start backend with `docker compose up -d archon-server`

### Database Not Found
```
SKIPPED: Database not found at /home/jose/src/Archon/data/archon.db
```
**Fix**: Check `SQLITE_PATH` environment variable or initialize database

### API Key Invalid
```
HTTPException: 401 Unauthorized - Invalid API key
```
**Fix**: Set `OPENAI_API_KEY` (or other provider) in `.env` file

### Timeout
```
TimeoutError: Recrawl did not complete within 120s
```
**Fix**: Increase timeout or check backend logs for errors

## Debugging

### View Backend Logs
```bash
# Docker
docker compose logs archon-server -f | grep -i "crawl_status"

# Local
tail -f logs/archon.log | grep -i "crawl_status"
```

### Check Database State
```bash
sqlite3 /home/jose/src/Archon/data/archon.db "
  SELECT
    source_id,
    title,
    json_extract(metadata, '$.crawl_status') as crawl_status
  FROM archon_sources
  ORDER BY created_at DESC
  LIMIT 5
"
```

### Run with Debug Logging
```bash
export LOGLEVEL=DEBUG
uv run pytest python/tests/integration/test_recrawl_status.py -v -s
```

## Test Breakdown

| Test | Purpose | Duration | Critical |
|------|---------|----------|----------|
| `test_backend_health` | Verify backend running | < 1s | ✓ |
| `test_database_connection` | Verify DB accessible | < 1s | ✓ |
| `test_initial_crawl_status_lifecycle` | Baseline test | ~30-60s | - |
| `test_recrawl_status_remains_completed` | **CORE BUG TEST** | ~60-120s | ✓✓✓ |
| `test_multiple_recrawls_status_stability` | Race conditions | ~120-240s | - |
| `test_failed_crawl_sets_failed_status` | Error handling | ~10-30s | - |

## Interpreting Results

### Test 2 PASSES → Bug is FIXED ✅
```
✅ TEST 2 PASSED: Recrawl status remains 'completed' (Bug is FIXED!)
```
All assertions passed:
- Database `crawl_status` = "completed"
- API `status` = "active"
- No user-facing issues

### Test 2 FAILS → Bug STILL EXISTS ❌
```
❌ BUG DETECTED: Database crawl_status should be 'completed' after recrawl,
got 'pending'. This is the bug described in INVESTIGATION_REPORT.md!
```
Apply fixes from `INVESTIGATION_REPORT.md`:
1. Add `crawl_status="pending"` in `document_storage_operations.py`
2. Set status at refresh start in `knowledge_api.py`
3. Add verification logging

## Post-Test Cleanup

### Remove Test Sources
```bash
sqlite3 /home/jose/src/Archon/data/archon.db "
  DELETE FROM archon_sources WHERE source_url = 'https://example.com'
"
```

### Or Use Fix Endpoint
```bash
curl -X POST http://localhost:8181/api/knowledge-items/fix-pending-statuses
```

## More Information

- Full documentation: `/home/jose/src/Archon/INTEGRATION_TEST.md`
- Test summary: `python/tests/integration/TEST_RECRAWL_STATUS_SUMMARY.md`
- Root cause analysis: `/home/jose/src/Archon/INVESTIGATION_REPORT.md`
