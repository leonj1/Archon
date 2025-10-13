# MCP Analytics Materialized View Refresh

## Overview

The MCP analytics system uses PostgreSQL materialized views (`archon_mcp_usage_hourly` and `archon_mcp_usage_daily`) for fast query performance. These views need to be refreshed periodically to show up-to-date analytics data.

## Refresh Endpoint

A manual refresh endpoint is available:

```bash
POST /api/mcp/analytics/refresh-views
```

This endpoint calls the PostgreSQL function `refresh_mcp_usage_views()` which refreshes both materialized views concurrently.

## Refresh Options

### Option A: Manual Refresh (Current Implementation)

Call the refresh endpoint manually when needed:

```bash
curl -X POST http://localhost:8181/api/mcp/analytics/refresh-views
```

**Pros**:
- Simple implementation
- No additional dependencies
- Full control over refresh timing

**Cons**:
- Requires manual intervention
- Not automatic

---

### Option B: Supabase Edge Function (Recommended for Production)

Create a Supabase Edge Function that calls the refresh endpoint on a schedule.

**Step 1: Create Edge Function**

File: `supabase/functions/refresh-mcp-views/index.ts`

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

serve(async (req) => {
  try {
    // Call the refresh endpoint
    const response = await fetch("http://archon-server:8181/api/mcp/analytics/refresh-views", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();

    return new Response(
      JSON.stringify({
        success: true,
        message: "Materialized views refreshed successfully",
        data,
      }),
      {
        headers: { "Content-Type": "application/json" },
        status: 200,
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({
        success: false,
        error: error.message,
      }),
      {
        headers: { "Content-Type": "application/json" },
        status: 500,
      }
    );
  }
});
```

**Step 2: Deploy Edge Function**

```bash
supabase functions deploy refresh-mcp-views
```

**Step 3: Schedule with Supabase Cron**

Use Supabase's built-in cron scheduling (if available in your plan) or use external cron service to call the Edge Function every 15 minutes.

**Pros**:
- Serverless and scalable
- Integrated with Supabase
- No additional infrastructure

**Cons**:
- Requires Supabase Edge Functions setup
- May have cold start delays

---

### Option C: pg_cron Extension

If `pg_cron` extension is available in your Supabase instance, schedule directly in PostgreSQL:

```sql
-- Run in Supabase SQL Editor
SELECT cron.schedule(
    'refresh-mcp-usage-views',
    '*/15 * * * *',  -- Every 15 minutes
    $$ SELECT refresh_mcp_usage_views(); $$
);
```

**Check if pg_cron is available**:
```sql
SELECT * FROM pg_extension WHERE extname = 'pg_cron';
```

**Pros**:
- Native PostgreSQL solution
- Very reliable
- Low overhead

**Cons**:
- Requires pg_cron extension
- May not be available in all Supabase tiers

---

### Option D: Python APScheduler (Backend-based)

Add scheduling to the FastAPI application using APScheduler.

**Step 1: Install APScheduler**

```bash
cd python
uv add apscheduler
```

**Step 2: Create Scheduler Module**

File: `python/src/server/scheduler/mcp_refresh_job.py`

```python
"""
MCP Analytics Materialized View Refresh Scheduler

Automatically refreshes materialized views every 15 minutes.
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from ..config.database import get_supabase_client

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def refresh_materialized_views():
    """Refresh MCP usage analytics materialized views."""
    try:
        logger.info("Starting scheduled materialized view refresh...")

        supabase = get_supabase_client()

        # Call the PostgreSQL refresh function
        result = supabase.rpc("refresh_mcp_usage_views").execute()

        logger.info(
            f"Materialized views refreshed successfully: {result.data}"
        )

    except Exception as e:
        logger.error(f"Failed to refresh materialized views: {e}", exc_info=True)


def start_scheduler():
    """Start the APScheduler for materialized view refresh."""
    # Schedule refresh every 15 minutes
    scheduler.add_job(
        refresh_materialized_views,
        CronTrigger(minute="*/15"),  # Every 15 minutes
        id="refresh_mcp_views",
        name="Refresh MCP Usage Analytics Views",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("MCP analytics refresh scheduler started (every 15 minutes)")


def stop_scheduler():
    """Stop the scheduler gracefully."""
    scheduler.shutdown()
    logger.info("MCP analytics refresh scheduler stopped")
```

**Step 3: Integrate with FastAPI Startup**

In `python/src/server/main.py`:

```python
from .scheduler.mcp_refresh_job import start_scheduler, stop_scheduler

@app.on_event("startup")
async def startup_event():
    # ... existing startup code ...
    start_scheduler()
    logger.info("Started MCP analytics refresh scheduler")

@app.on_event("shutdown")
async def shutdown_event():
    # ... existing shutdown code ...
    stop_scheduler()
    logger.info("Stopped MCP analytics refresh scheduler")
```

**Pros**:
- Fully integrated with application
- No external dependencies
- Easy to configure and monitor

**Cons**:
- Runs in application process
- Requires application to be running
- Adds dependency to backend

---

## Recommendation

### For Development
Use **Option A (Manual Refresh)** - Call the endpoint when needed during development.

### For Production
Choose based on your infrastructure:

1. **If using Supabase extensively**: Use **Option B (Edge Function)**
2. **If pg_cron is available**: Use **Option C (pg_cron)** - Most reliable
3. **If you want application-integrated**: Use **Option D (APScheduler)**

## Current Status

✅ **Implemented**: Manual refresh endpoint (POST /api/mcp/analytics/refresh-views)

⏳ **Pending**: Automatic refresh scheduling (choose one of the options above)

## Testing Refresh

### Verify Views Exist

```sql
SELECT
    schemaname,
    matviewname,
    ispopulated
FROM pg_matviews
WHERE matviewname IN ('archon_mcp_usage_hourly', 'archon_mcp_usage_daily');
```

### Manual Refresh Test

```bash
# Call refresh endpoint
curl -X POST http://localhost:8181/api/mcp/analytics/refresh-views

# Expected response:
{
  "success": true,
  "message": "Materialized views refreshed successfully",
  "refreshed_at": "2025-01-13T..."
}
```

### Check View Data

```sql
-- Check hourly view
SELECT COUNT(*) FROM archon_mcp_usage_hourly;

-- Check recent data
SELECT
    hour_bucket,
    tool_category,
    SUM(call_count) as total_calls
FROM archon_mcp_usage_hourly
WHERE hour_bucket >= NOW() - INTERVAL '24 hours'
GROUP BY hour_bucket, tool_category
ORDER BY hour_bucket DESC
LIMIT 10;
```

## Monitoring

### Check Last Refresh Time

Unfortunately, PostgreSQL materialized views don't track last refresh time natively. Consider:

1. **Application-level tracking**: Log refresh times in application logs
2. **Custom tracking table**: Create a table to track refresh operations
3. **Monitor view size**: Check row counts to ensure views are updating

### Create Refresh Tracking Table (Optional)

```sql
CREATE TABLE IF NOT EXISTS archon_mcp_view_refresh_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    view_name TEXT NOT NULL,
    refreshed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    success BOOLEAN NOT NULL DEFAULT true,
    error_message TEXT
);

-- Modify refresh function to log
CREATE OR REPLACE FUNCTION refresh_mcp_usage_views()
RETURNS TABLE(view_name TEXT, refresh_status TEXT) AS $$
BEGIN
    -- Refresh hourly view
    BEGIN
        REFRESH MATERIALIZED VIEW CONCURRENTLY archon_mcp_usage_hourly;
        INSERT INTO archon_mcp_view_refresh_log (view_name, success)
        VALUES ('archon_mcp_usage_hourly', true);
        RETURN QUERY SELECT 'archon_mcp_usage_hourly'::TEXT, 'success'::TEXT;
    EXCEPTION WHEN OTHERS THEN
        INSERT INTO archon_mcp_view_refresh_log (view_name, success, error_message)
        VALUES ('archon_mcp_usage_hourly', false, SQLERRM);
        RETURN QUERY SELECT 'archon_mcp_usage_hourly'::TEXT, SQLERRM::TEXT;
    END;

    -- Refresh daily view
    BEGIN
        REFRESH MATERIALIZED VIEW CONCURRENTLY archon_mcp_usage_daily;
        INSERT INTO archon_mcp_view_refresh_log (view_name, success)
        VALUES ('archon_mcp_usage_daily', true);
        RETURN QUERY SELECT 'archon_mcp_usage_daily'::TEXT, 'success'::TEXT;
    EXCEPTION WHEN OTHERS THEN
        INSERT INTO archon_mcp_view_refresh_log (view_name, success, error_message)
        VALUES ('archon_mcp_usage_daily', false, SQLERRM);
        RETURN QUERY SELECT 'archon_mcp_usage_daily'::TEXT, SQLERRM::TEXT;
    END;
END;
$$ LANGUAGE plpgsql;
```

## Troubleshooting

### Views Not Refreshing

1. Check if refresh function exists:
```sql
SELECT proname FROM pg_proc WHERE proname = 'refresh_mcp_usage_views';
```

2. Test function manually:
```sql
SELECT * FROM refresh_mcp_usage_views();
```

3. Check for lock conflicts:
```sql
SELECT * FROM pg_locks WHERE relation = 'archon_mcp_usage_hourly'::regclass;
```

### Performance Issues

If refresh takes too long:

1. **Use CONCURRENTLY**: Already implemented to avoid locking
2. **Reduce window**: Adjust 180-day window if too large
3. **Add indexes**: Ensure proper indexes on base table
4. **Partial refresh**: Consider refreshing only recent data

## Next Steps

1. Choose a refresh strategy based on your environment
2. Implement chosen option
3. Test refresh mechanism
4. Monitor view freshness
5. Set up alerting for refresh failures
