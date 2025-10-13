# MCP Usage Analytics Migration (v0.2.0)

## Overview

This migration adds comprehensive usage analytics for the MCP server, enabling tracking of all tool invocations with time-series data storage and aggregated views for dashboard displays.

## Files

- `001_add_mcp_usage_tracking.sql` - Main migration SQL file
- `../run_mcp_migration.py` - Python script for automated migration (requires direct PostgreSQL access)
- `../test_mcp_schema.py` - Schema validation and testing script

## Migration Steps

### Option 1: Supabase SQL Editor (Recommended)

1. **Open Supabase Dashboard**
   - Go to: https://supabase.com/dashboard/project/myfibwvuphkskjrzbaam
   - Navigate to: SQL Editor → New Query

2. **Copy and Execute Migration SQL**
   ```bash
   cat migration/0.2.0/001_add_mcp_usage_tracking.sql
   ```
   - Copy the entire contents
   - Paste into Supabase SQL Editor
   - Click "Run" or press Ctrl+Enter

3. **Verify Migration**
   ```bash
   docker compose exec archon-server python /app/migration/test_mcp_schema.py
   ```

### Option 2: Direct PostgreSQL Connection (Advanced)

If you have the database password (not the service_role key):

1. **Set Database Password**
   ```bash
   export SUPABASE_DB_PASSWORD="your-database-password"
   ```

2. **Run Migration Script**
   ```bash
   docker compose exec archon-server python /app/migration/run_mcp_migration.py
   ```

### Option 3: Supabase CLI (If Available)

```bash
supabase db push --db-url "postgresql://postgres:PASSWORD@db.myfibwvuphkskjrzbaam.supabase.co:5432/postgres"
```

## What Gets Created

### Tables

1. **`archon_mcp_usage_events`** - Main time-series events table
   - Stores all MCP tool invocations
   - Includes computed columns for aggregation (`hour_bucket`, `date_bucket`)
   - 180-day retention policy

### Materialized Views

1. **`archon_mcp_usage_hourly`** - Hourly aggregated metrics
   - Pre-computed statistics per hour
   - Fast queries for recent usage trends

2. **`archon_mcp_usage_daily`** - Daily aggregated metrics
   - Pre-computed daily statistics
   - Long-term trend analysis

### Functions

1. **`cleanup_mcp_usage_events()`** - Data retention cleanup
   - Deletes events older than 180 days
   - Should be run daily via cron

2. **`refresh_mcp_usage_views()`** - Refresh materialized views
   - Updates hourly and daily aggregations
   - Should be run every 5-15 minutes

3. **`get_mcp_usage_summary(time_range_hours)`** - Usage summary helper
   - Returns aggregated statistics for dashboard

### Indexes

- Time-based indexes for fast queries
- Composite indexes for common query patterns
- GIN index for JSONB metadata searches

### Row Level Security (RLS)

- Service role has full access
- Authenticated users have read-only access

## Post-Migration Tasks

### 1. Verify Schema (Required)

Run the test script to verify everything works:

```bash
docker compose exec archon-server python /app/migration/test_mcp_schema.py
```

Expected output:
```
✅ Table exists with 0 rows
✅ Test data inserted successfully
✅ Computed columns working
✅ Views are accessible
🎉 Schema testing completed!
```

### 2. Set Up Scheduled Jobs (Recommended)

#### Option A: pg_cron (If Available in Supabase)

```sql
-- Refresh materialized views every 15 minutes
SELECT cron.schedule(
    'refresh-mcp-usage-views',
    '*/15 * * * *',
    $$ SELECT refresh_mcp_usage_views(); $$
);

-- Cleanup old events daily at 2 AM
SELECT cron.schedule(
    'cleanup-mcp-usage-events',
    '0 2 * * *',
    $$ SELECT cleanup_mcp_usage_events(); $$
);
```

#### Option B: External Cron Jobs

Create API endpoints and call them via cron:

```bash
# Add to crontab
*/15 * * * * curl -X POST http://localhost:8181/api/mcp-analytics/refresh-views
0 2 * * * curl -X POST http://localhost:8181/api/mcp-analytics/cleanup
```

#### Option C: Application Scheduler

Use Python APScheduler or similar in the backend.

### 3. Monitor Usage

The usage tracking is automatically enabled via the middleware decorator on all MCP tools:

```python
@usage_tracker.track_tool('tool_name', 'category')
async def tool_function(...):
    # Tool implementation
```

Currently tracking:
- 5 RAG tools (category='rag')
- 2 Project tools (category='project')
- 2 Task tools (category='task')
- 2 Document tools (category='document')
- 2 Version tools (category='version')
- 1 Feature tool (category='feature')

Total: **14 MCP tools** fully instrumented

## Verification Queries

### Check Recent Events

```sql
SELECT
    tool_name,
    tool_category,
    response_time_ms,
    success,
    timestamp
FROM archon_mcp_usage_events
ORDER BY timestamp DESC
LIMIT 10;
```

### View Hourly Aggregations

```sql
SELECT
    hour_bucket,
    tool_category,
    SUM(call_count) as total_calls,
    AVG(avg_response_time_ms) as avg_response_time
FROM archon_mcp_usage_hourly
WHERE hour_bucket >= NOW() - INTERVAL '24 hours'
GROUP BY hour_bucket, tool_category
ORDER BY hour_bucket DESC;
```

### Get Usage Summary

```sql
SELECT * FROM get_mcp_usage_summary(24);  -- Last 24 hours
```

### Check Materialized View Status

```sql
SELECT
    schemaname,
    matviewname,
    last_refresh
FROM pg_stat_user_tables
WHERE schemaname = 'public'
AND tablename LIKE 'archon_mcp_usage_%';
```

## Troubleshooting

### Table Already Exists Error

The migration uses `IF NOT EXISTS` clauses, so it's safe to run multiple times. If you get conflicts:

```sql
-- Check existing structure
\d archon_mcp_usage_events

-- Drop and recreate if needed (CAUTION: data loss)
DROP TABLE IF EXISTS archon_mcp_usage_events CASCADE;
-- Then re-run migration
```

### Materialized Views Not Refreshing

Manually refresh:

```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY archon_mcp_usage_hourly;
REFRESH MATERIALIZED VIEW CONCURRENTLY archon_mcp_usage_daily;
```

### No Data Appearing

1. Check if MCP server is running: `docker compose ps archon-mcp`
2. Check middleware is enabled: Look for tracking logs
3. Verify table permissions: Check RLS policies
4. Test manual insert: Use test script

### Network Unreachable (Docker)

The Docker container may not have external network access. Use Supabase SQL Editor instead of Python scripts for direct database operations.

## Migration Rollback

To remove the MCP usage tracking:

```sql
-- Drop materialized views
DROP MATERIALIZED VIEW IF EXISTS archon_mcp_usage_daily;
DROP MATERIALIZED VIEW IF EXISTS archon_mcp_usage_hourly;

-- Drop functions
DROP FUNCTION IF EXISTS get_mcp_usage_summary(int);
DROP FUNCTION IF EXISTS refresh_mcp_usage_views();
DROP FUNCTION IF EXISTS cleanup_mcp_usage_events();

-- Drop table
DROP TABLE IF EXISTS archon_mcp_usage_events;

-- Remove migration record
DELETE FROM archon_migrations
WHERE version = '0.2.0'
AND migration_name = '001_add_mcp_usage_tracking';
```

## Next Phase: Analytics API

After verifying the migration works:

1. Create analytics API routes (`python/src/server/api_routes/mcp_analytics_api.py`)
2. Implement frontend services (`archon-ui-main/src/features/mcp/services/`)
3. Build UI components with charts
4. Add to Settings page

See: `/home/jose/src/Archon/PRPs/MCP_USAGE_ANALYTICS_SPEC.md` for full implementation plan.
