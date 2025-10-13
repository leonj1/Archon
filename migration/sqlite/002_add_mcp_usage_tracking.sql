-- =====================================================
-- Add MCP Usage Tracking Tables (SQLite)
-- =====================================================
-- SQLite-compatible version of MCP usage analytics
-- =====================================================

-- =====================================================
-- 1. MAIN USAGE EVENTS TABLE (Time-Series Data)
-- =====================================================

CREATE TABLE IF NOT EXISTS archon_mcp_usage_events (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),

    -- MCP tool metadata
    tool_name TEXT NOT NULL,
    tool_category TEXT NOT NULL,

    -- Session context
    session_id TEXT,
    client_type TEXT,

    -- Request details
    request_metadata TEXT DEFAULT '{}',
    source_id TEXT,
    query_text TEXT,
    match_count INTEGER,

    -- Response metadata
    response_time_ms INTEGER,
    success INTEGER NOT NULL DEFAULT 1,
    error_type TEXT,

    -- Aggregation helpers (stored as computed values)
    hour_bucket TEXT,
    date_bucket TEXT
);

-- Create indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_mcp_usage_timestamp ON archon_mcp_usage_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_mcp_usage_hour_bucket ON archon_mcp_usage_events(hour_bucket DESC);
CREATE INDEX IF NOT EXISTS idx_mcp_usage_date_bucket ON archon_mcp_usage_events(date_bucket DESC);
CREATE INDEX IF NOT EXISTS idx_mcp_usage_tool_name ON archon_mcp_usage_events(tool_name);
CREATE INDEX IF NOT EXISTS idx_mcp_usage_category ON archon_mcp_usage_events(tool_category);
CREATE INDEX IF NOT EXISTS idx_mcp_usage_session ON archon_mcp_usage_events(session_id) WHERE session_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_mcp_usage_source_id ON archon_mcp_usage_events(source_id) WHERE source_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_mcp_usage_timestamp_category ON archon_mcp_usage_events(timestamp DESC, tool_category);

-- =====================================================
-- 2. HOURLY AGGREGATIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS archon_mcp_usage_hourly (
    hour_bucket TEXT NOT NULL,
    tool_category TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    call_count INTEGER DEFAULT 0,
    avg_response_time_ms REAL DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    unique_sessions INTEGER DEFAULT 0,
    first_call_at TEXT,
    last_call_at TEXT,
    PRIMARY KEY (hour_bucket, tool_category, tool_name)
);

CREATE INDEX IF NOT EXISTS idx_mcp_usage_hourly_hour ON archon_mcp_usage_hourly(hour_bucket DESC);
CREATE INDEX IF NOT EXISTS idx_mcp_usage_hourly_category ON archon_mcp_usage_hourly(tool_category);

-- =====================================================
-- 3. DAILY AGGREGATIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS archon_mcp_usage_daily (
    date_bucket TEXT NOT NULL,
    tool_category TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    call_count INTEGER DEFAULT 0,
    avg_response_time_ms REAL DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    unique_sessions INTEGER DEFAULT 0,
    first_call_at TEXT,
    last_call_at TEXT,
    PRIMARY KEY (date_bucket, tool_category, tool_name)
);

CREATE INDEX IF NOT EXISTS idx_mcp_usage_daily_date ON archon_mcp_usage_daily(date_bucket DESC);
CREATE INDEX IF NOT EXISTS idx_mcp_usage_daily_category ON archon_mcp_usage_daily(tool_category);

-- =====================================================
-- 4. TRIGGER TO AUTO-POPULATE hour_bucket and date_bucket
-- =====================================================

CREATE TRIGGER IF NOT EXISTS trg_mcp_usage_compute_buckets
AFTER INSERT ON archon_mcp_usage_events
FOR EACH ROW
BEGIN
    UPDATE archon_mcp_usage_events
    SET
        hour_bucket = datetime(NEW.timestamp, 'start of hour'),
        date_bucket = date(NEW.timestamp)
    WHERE id = NEW.id;
END;

-- =====================================================
-- 5. TRIGGER TO AUTO-UPDATE HOURLY AGGREGATIONS
-- =====================================================

CREATE TRIGGER IF NOT EXISTS trg_mcp_usage_update_hourly
AFTER INSERT ON archon_mcp_usage_events
FOR EACH ROW
WHEN NEW.hour_bucket IS NOT NULL
BEGIN
    INSERT INTO archon_mcp_usage_hourly (
        hour_bucket, tool_category, tool_name, call_count,
        avg_response_time_ms, error_count, unique_sessions,
        first_call_at, last_call_at
    )
    SELECT
        NEW.hour_bucket,
        NEW.tool_category,
        NEW.tool_name,
        1,
        COALESCE(NEW.response_time_ms, 0),
        CASE WHEN NEW.success = 0 THEN 1 ELSE 0 END,
        1,
        NEW.timestamp,
        NEW.timestamp
    WHERE NOT EXISTS (
        SELECT 1 FROM archon_mcp_usage_hourly
        WHERE hour_bucket = NEW.hour_bucket
        AND tool_category = NEW.tool_category
        AND tool_name = NEW.tool_name
    );

    UPDATE archon_mcp_usage_hourly
    SET
        call_count = call_count + 1,
        avg_response_time_ms = (
            (avg_response_time_ms * call_count + COALESCE(NEW.response_time_ms, 0)) / (call_count + 1.0)
        ),
        error_count = error_count + CASE WHEN NEW.success = 0 THEN 1 ELSE 0 END,
        last_call_at = NEW.timestamp,
        unique_sessions = (
            SELECT COUNT(DISTINCT session_id)
            FROM archon_mcp_usage_events
            WHERE hour_bucket = NEW.hour_bucket
            AND tool_category = NEW.tool_category
            AND tool_name = NEW.tool_name
        )
    WHERE hour_bucket = NEW.hour_bucket
    AND tool_category = NEW.tool_category
    AND tool_name = NEW.tool_name;
END;

-- =====================================================
-- 6. TRIGGER TO AUTO-UPDATE DAILY AGGREGATIONS
-- =====================================================

CREATE TRIGGER IF NOT EXISTS trg_mcp_usage_update_daily
AFTER INSERT ON archon_mcp_usage_events
FOR EACH ROW
WHEN NEW.date_bucket IS NOT NULL
BEGIN
    INSERT INTO archon_mcp_usage_daily (
        date_bucket, tool_category, tool_name, call_count,
        avg_response_time_ms, error_count, unique_sessions,
        first_call_at, last_call_at
    )
    SELECT
        NEW.date_bucket,
        NEW.tool_category,
        NEW.tool_name,
        1,
        COALESCE(NEW.response_time_ms, 0),
        CASE WHEN NEW.success = 0 THEN 1 ELSE 0 END,
        1,
        NEW.timestamp,
        NEW.timestamp
    WHERE NOT EXISTS (
        SELECT 1 FROM archon_mcp_usage_daily
        WHERE date_bucket = NEW.date_bucket
        AND tool_category = NEW.tool_category
        AND tool_name = NEW.tool_name
    );

    UPDATE archon_mcp_usage_daily
    SET
        call_count = call_count + 1,
        avg_response_time_ms = (
            (avg_response_time_ms * call_count + COALESCE(NEW.response_time_ms, 0)) / (call_count + 1.0)
        ),
        error_count = error_count + CASE WHEN NEW.success = 0 THEN 1 ELSE 0 END,
        last_call_at = NEW.timestamp,
        unique_sessions = (
            SELECT COUNT(DISTINCT session_id)
            FROM archon_mcp_usage_events
            WHERE date_bucket = NEW.date_bucket
            AND tool_category = NEW.tool_category
            AND tool_name = NEW.tool_name
        )
    WHERE date_bucket = NEW.date_bucket
    AND tool_category = NEW.tool_category
    AND tool_name = NEW.tool_name;
END;
