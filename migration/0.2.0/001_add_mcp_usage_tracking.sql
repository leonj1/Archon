-- =====================================================
-- Add MCP Usage Tracking Tables
-- =====================================================
-- This migration adds comprehensive usage analytics for the MCP server.
--
-- Features:
-- - Time-series event storage with 180-day retention
-- - Hourly and daily aggregated views for fast queries
-- - Automatic data cleanup function
-- - Session and tool metadata tracking
-- =====================================================

-- =====================================================
-- 1. MAIN USAGE EVENTS TABLE (Time-Series Data)
-- =====================================================

CREATE TABLE IF NOT EXISTS archon_mcp_usage_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- MCP tool metadata
    tool_name TEXT NOT NULL,
    tool_category TEXT NOT NULL, -- 'rag', 'project', 'task', 'document', 'health', 'version', 'feature'

    -- Session context
    session_id TEXT,
    client_type TEXT, -- 'claude-code', 'cursor', 'windsurf', 'unknown'

    -- Request details
    request_metadata JSONB DEFAULT '{}'::jsonb, -- Flexible JSON for tool-specific data
    source_id TEXT, -- For RAG queries
    query_text TEXT, -- For search operations (first 500 chars)
    match_count INT, -- For RAG queries

    -- Response metadata
    response_time_ms INT, -- Time taken to process
    success BOOLEAN NOT NULL DEFAULT true,
    error_type TEXT, -- If failed

    -- Aggregation helpers (computed columns for efficient querying)
    hour_bucket TIMESTAMPTZ GENERATED ALWAYS AS (date_trunc('hour', timestamp)) STORED,
    date_bucket DATE GENERATED ALWAYS AS (DATE(timestamp)) STORED
);

-- Add comments to document the table structure
COMMENT ON TABLE archon_mcp_usage_events IS 'Time-series storage for all MCP tool invocations with 180-day retention';
COMMENT ON COLUMN archon_mcp_usage_events.tool_name IS 'Name of the MCP tool (e.g., rag_search_knowledge_base)';
COMMENT ON COLUMN archon_mcp_usage_events.tool_category IS 'Category for grouping: rag, project, task, document, health, version, feature';
COMMENT ON COLUMN archon_mcp_usage_events.session_id IS 'Session identifier for tracking connected clients';
COMMENT ON COLUMN archon_mcp_usage_events.client_type IS 'Type of client: claude-code, cursor, windsurf, unknown';
COMMENT ON COLUMN archon_mcp_usage_events.request_metadata IS 'Flexible JSONB for tool-specific request parameters';
COMMENT ON COLUMN archon_mcp_usage_events.source_id IS 'Knowledge base source ID for RAG queries';
COMMENT ON COLUMN archon_mcp_usage_events.query_text IS 'Search query text (truncated to 500 chars)';
COMMENT ON COLUMN archon_mcp_usage_events.response_time_ms IS 'Request processing time in milliseconds';
COMMENT ON COLUMN archon_mcp_usage_events.hour_bucket IS 'Computed column: timestamp truncated to hour for aggregation';
COMMENT ON COLUMN archon_mcp_usage_events.date_bucket IS 'Computed column: timestamp truncated to date for aggregation';

-- =====================================================
-- 2. INDEXES FOR FAST TIME-SERIES QUERIES
-- =====================================================

-- Primary time-based index (most important for time-series queries)
CREATE INDEX IF NOT EXISTS idx_mcp_usage_timestamp ON archon_mcp_usage_events(timestamp DESC);

-- Aggregation helper indexes
CREATE INDEX IF NOT EXISTS idx_mcp_usage_hour_bucket ON archon_mcp_usage_events(hour_bucket DESC);
CREATE INDEX IF NOT EXISTS idx_mcp_usage_date_bucket ON archon_mcp_usage_events(date_bucket DESC);

-- Filter indexes
CREATE INDEX IF NOT EXISTS idx_mcp_usage_tool_name ON archon_mcp_usage_events(tool_name);
CREATE INDEX IF NOT EXISTS idx_mcp_usage_category ON archon_mcp_usage_events(tool_category);
CREATE INDEX IF NOT EXISTS idx_mcp_usage_session ON archon_mcp_usage_events(session_id) WHERE session_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_mcp_usage_source_id ON archon_mcp_usage_events(source_id) WHERE source_id IS NOT NULL;

-- Composite index for common query pattern (time range + category)
CREATE INDEX IF NOT EXISTS idx_mcp_usage_timestamp_category ON archon_mcp_usage_events(timestamp DESC, tool_category);

-- JSONB index for metadata queries
CREATE INDEX IF NOT EXISTS idx_mcp_usage_request_metadata ON archon_mcp_usage_events USING GIN(request_metadata);

-- =====================================================
-- 3. MATERIALIZED VIEW: HOURLY AGGREGATIONS
-- =====================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS archon_mcp_usage_hourly AS
SELECT
    hour_bucket,
    tool_category,
    tool_name,
    COUNT(*) as call_count,
    ROUND(AVG(response_time_ms)::numeric, 2) as avg_response_time_ms,
    COUNT(*) FILTER (WHERE success = false) as error_count,
    COUNT(DISTINCT session_id) as unique_sessions,
    MIN(timestamp) as first_call_at,
    MAX(timestamp) as last_call_at
FROM archon_mcp_usage_events
WHERE timestamp >= NOW() - INTERVAL '180 days'
GROUP BY hour_bucket, tool_category, tool_name;

-- Unique index to support CONCURRENTLY refresh
CREATE UNIQUE INDEX IF NOT EXISTS idx_mcp_usage_hourly_unique
ON archon_mcp_usage_hourly(hour_bucket, tool_category, tool_name);

-- Regular indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_mcp_usage_hourly_hour ON archon_mcp_usage_hourly(hour_bucket DESC);
CREATE INDEX IF NOT EXISTS idx_mcp_usage_hourly_category ON archon_mcp_usage_hourly(tool_category);

COMMENT ON MATERIALIZED VIEW archon_mcp_usage_hourly IS 'Hourly aggregated MCP usage metrics for fast dashboard queries (180-day window)';

-- =====================================================
-- 4. MATERIALIZED VIEW: DAILY AGGREGATIONS
-- =====================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS archon_mcp_usage_daily AS
SELECT
    date_bucket,
    tool_category,
    tool_name,
    COUNT(*) as call_count,
    ROUND(AVG(response_time_ms)::numeric, 2) as avg_response_time_ms,
    COUNT(*) FILTER (WHERE success = false) as error_count,
    COUNT(DISTINCT session_id) as unique_sessions,
    MIN(timestamp) as first_call_at,
    MAX(timestamp) as last_call_at
FROM archon_mcp_usage_events
WHERE timestamp >= NOW() - INTERVAL '180 days'
GROUP BY date_bucket, tool_category, tool_name;

-- Unique index to support CONCURRENTLY refresh
CREATE UNIQUE INDEX IF NOT EXISTS idx_mcp_usage_daily_unique
ON archon_mcp_usage_daily(date_bucket, tool_category, tool_name);

-- Regular indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_mcp_usage_daily_date ON archon_mcp_usage_daily(date_bucket DESC);
CREATE INDEX IF NOT EXISTS idx_mcp_usage_daily_category ON archon_mcp_usage_daily(tool_category);

COMMENT ON MATERIALIZED VIEW archon_mcp_usage_daily IS 'Daily aggregated MCP usage metrics for long-term trend analysis (180-day window)';

-- =====================================================
-- 5. DATA RETENTION: CLEANUP FUNCTION
-- =====================================================

CREATE OR REPLACE FUNCTION cleanup_mcp_usage_events()
RETURNS TABLE(deleted_count BIGINT) AS $$
DECLARE
    rows_deleted BIGINT;
BEGIN
    -- Delete events older than 180 days
    DELETE FROM archon_mcp_usage_events
    WHERE timestamp < NOW() - INTERVAL '180 days';

    GET DIAGNOSTICS rows_deleted = ROW_COUNT;

    -- Log the cleanup
    RAISE NOTICE 'Cleaned up % MCP usage events older than 180 days', rows_deleted;

    RETURN QUERY SELECT rows_deleted;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_mcp_usage_events IS 'Deletes MCP usage events older than 180 days. Should be run daily via scheduled job.';

-- =====================================================
-- 6. MATERIALIZED VIEW REFRESH FUNCTION
-- =====================================================

CREATE OR REPLACE FUNCTION refresh_mcp_usage_views()
RETURNS TABLE(view_name TEXT, refresh_status TEXT) AS $$
BEGIN
    -- Refresh hourly view
    BEGIN
        REFRESH MATERIALIZED VIEW CONCURRENTLY archon_mcp_usage_hourly;
        RETURN QUERY SELECT 'archon_mcp_usage_hourly'::TEXT, 'success'::TEXT;
    EXCEPTION WHEN OTHERS THEN
        RETURN QUERY SELECT 'archon_mcp_usage_hourly'::TEXT, SQLERRM::TEXT;
    END;

    -- Refresh daily view
    BEGIN
        REFRESH MATERIALIZED VIEW CONCURRENTLY archon_mcp_usage_daily;
        RETURN QUERY SELECT 'archon_mcp_usage_daily'::TEXT, 'success'::TEXT;
    EXCEPTION WHEN OTHERS THEN
        RETURN QUERY SELECT 'archon_mcp_usage_daily'::TEXT, SQLERRM::TEXT;
    END;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION refresh_mcp_usage_views IS 'Refreshes materialized views for MCP usage aggregations. Should be run every 5-15 minutes.';

-- =====================================================
-- 7. HELPER FUNCTION: GET USAGE SUMMARY
-- =====================================================

CREATE OR REPLACE FUNCTION get_mcp_usage_summary(time_range_hours INT DEFAULT 24)
RETURNS TABLE(
    total_calls BIGINT,
    successful_calls BIGINT,
    failed_calls BIGINT,
    success_rate NUMERIC,
    unique_sessions BIGINT,
    avg_response_time_ms NUMERIC,
    most_used_tool TEXT,
    most_used_category TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH stats AS (
        SELECT
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE success = true) as successful,
            COUNT(*) FILTER (WHERE success = false) as failed,
            COUNT(DISTINCT session_id) as sessions,
            ROUND(AVG(response_time_ms)::numeric, 2) as avg_time
        FROM archon_mcp_usage_events
        WHERE timestamp >= NOW() - (time_range_hours || ' hours')::INTERVAL
    ),
    top_tool AS (
        SELECT tool_name
        FROM archon_mcp_usage_events
        WHERE timestamp >= NOW() - (time_range_hours || ' hours')::INTERVAL
        GROUP BY tool_name
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ),
    top_category AS (
        SELECT tool_category
        FROM archon_mcp_usage_events
        WHERE timestamp >= NOW() - (time_range_hours || ' hours')::INTERVAL
        GROUP BY tool_category
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )
    SELECT
        stats.total,
        stats.successful,
        stats.failed,
        CASE WHEN stats.total > 0
            THEN ROUND((stats.successful::numeric / stats.total::numeric) * 100, 2)
            ELSE 0
        END,
        stats.sessions,
        stats.avg_time,
        top_tool.tool_name,
        top_category.tool_category
    FROM stats, top_tool, top_category;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_mcp_usage_summary IS 'Returns summary statistics for MCP usage over specified time range (default: 24 hours)';

-- =====================================================
-- 8. ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Enable RLS on usage events table
ALTER TABLE archon_mcp_usage_events ENABLE ROW LEVEL SECURITY;

-- Service role has full access
CREATE POLICY "Allow service role full access to archon_mcp_usage_events"
ON archon_mcp_usage_events
FOR ALL USING (auth.role() = 'service_role');

-- Authenticated users can read usage data (for analytics dashboard)
CREATE POLICY "Allow authenticated users to read archon_mcp_usage_events"
ON archon_mcp_usage_events
FOR SELECT TO authenticated
USING (true);

-- =====================================================
-- 9. RECORD MIGRATION APPLICATION
-- =====================================================

INSERT INTO archon_migrations (version, migration_name)
VALUES ('0.2.0', '001_add_mcp_usage_tracking')
ON CONFLICT (version, migration_name) DO NOTHING;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================
--
-- Next steps:
-- 1. Set up scheduled job to run cleanup_mcp_usage_events() daily
--    Example: SELECT cron.schedule('cleanup-mcp-usage', '0 2 * * *', 'SELECT cleanup_mcp_usage_events();');
--
-- 2. Set up scheduled job to refresh materialized views every 15 minutes
--    Example: SELECT cron.schedule('refresh-mcp-views', '*/15 * * * *', 'SELECT refresh_mcp_usage_views();');
--
-- 3. Monitor table growth and adjust retention period if needed
--
-- Note: If pg_cron is not available in your Supabase instance, you can:
-- - Use Supabase Edge Functions with scheduled triggers
-- - Run cleanup manually from your application's scheduled tasks
-- - Use external cron jobs that call your API endpoints
-- =====================================================
