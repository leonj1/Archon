-- Migration: MCP Usage Analytics
-- Description: Add tables for tracking MCP tool usage and analytics
-- Created: 2025-01-17

-- ============================================
-- Main Events Table
-- ============================================
CREATE TABLE IF NOT EXISTS archon_mcp_usage_events (
    id TEXT PRIMARY KEY,
    tool_name TEXT NOT NULL,
    tool_category TEXT NOT NULL,
    session_id TEXT,
    client_type TEXT DEFAULT 'unknown',
    request_metadata TEXT,
    source_id TEXT,
    query_text TEXT,
    match_count INTEGER,
    response_time_ms INTEGER NOT NULL DEFAULT 0,
    success INTEGER NOT NULL DEFAULT 1,
    error_type TEXT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_mcp_events_timestamp ON archon_mcp_usage_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_mcp_events_tool_name ON archon_mcp_usage_events(tool_name);
CREATE INDEX IF NOT EXISTS idx_mcp_events_tool_category ON archon_mcp_usage_events(tool_category);
CREATE INDEX IF NOT EXISTS idx_mcp_events_session ON archon_mcp_usage_events(session_id);
CREATE INDEX IF NOT EXISTS idx_mcp_events_source ON archon_mcp_usage_events(source_id);
CREATE INDEX IF NOT EXISTS idx_mcp_events_success ON archon_mcp_usage_events(success);

-- ============================================
-- Hourly Aggregation Table
-- ============================================
CREATE TABLE IF NOT EXISTS archon_mcp_usage_hourly (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hour_bucket DATETIME NOT NULL,
    tool_name TEXT NOT NULL,
    tool_category TEXT NOT NULL,
    call_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    avg_response_time_ms INTEGER NOT NULL DEFAULT 0,
    unique_sessions INTEGER NOT NULL DEFAULT 0,
    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(hour_bucket, tool_name)
);

-- Index for fast hourly queries
CREATE INDEX IF NOT EXISTS idx_mcp_hourly_bucket ON archon_mcp_usage_hourly(hour_bucket DESC);
CREATE INDEX IF NOT EXISTS idx_mcp_hourly_category ON archon_mcp_usage_hourly(tool_category);

-- ============================================
-- Daily Aggregation Table
-- ============================================
CREATE TABLE IF NOT EXISTS archon_mcp_usage_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_bucket DATE NOT NULL,
    tool_name TEXT NOT NULL,
    tool_category TEXT NOT NULL,
    call_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    avg_response_time_ms INTEGER NOT NULL DEFAULT 0,
    unique_sessions INTEGER NOT NULL DEFAULT 0,
    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date_bucket, tool_name)
);

-- Index for fast daily queries
CREATE INDEX IF NOT EXISTS idx_mcp_daily_bucket ON archon_mcp_usage_daily(date_bucket DESC);
CREATE INDEX IF NOT EXISTS idx_mcp_daily_category ON archon_mcp_usage_daily(tool_category);

-- ============================================
-- Triggers for Automatic Aggregation
-- ============================================

-- Trigger to update hourly aggregation when new event is inserted
CREATE TRIGGER IF NOT EXISTS trg_mcp_events_hourly_insert
AFTER INSERT ON archon_mcp_usage_events
BEGIN
    INSERT INTO archon_mcp_usage_hourly (
        hour_bucket,
        tool_name,
        tool_category,
        call_count,
        error_count,
        avg_response_time_ms,
        unique_sessions,
        last_updated
    )
    VALUES (
        datetime(strftime('%Y-%m-%d %H:00:00', NEW.timestamp)),
        NEW.tool_name,
        NEW.tool_category,
        1,
        CASE WHEN NEW.success = 0 THEN 1 ELSE 0 END,
        NEW.response_time_ms,
        1,
        CURRENT_TIMESTAMP
    )
    ON CONFLICT(hour_bucket, tool_name) DO UPDATE SET
        call_count = call_count + 1,
        error_count = error_count + CASE WHEN NEW.success = 0 THEN 1 ELSE 0 END,
        avg_response_time_ms = (
            (COALESCE(avg_response_time_ms, 0) * call_count + NEW.response_time_ms) / (call_count + 1)
        ),
        last_updated = CURRENT_TIMESTAMP;
END;

-- Trigger to update daily aggregation when new event is inserted
CREATE TRIGGER IF NOT EXISTS trg_mcp_events_daily_insert
AFTER INSERT ON archon_mcp_usage_events
BEGIN
    INSERT INTO archon_mcp_usage_daily (
        date_bucket,
        tool_name,
        tool_category,
        call_count,
        error_count,
        avg_response_time_ms,
        unique_sessions,
        last_updated
    )
    VALUES (
        date(NEW.timestamp),
        NEW.tool_name,
        NEW.tool_category,
        1,
        CASE WHEN NEW.success = 0 THEN 1 ELSE 0 END,
        NEW.response_time_ms,
        1,
        CURRENT_TIMESTAMP
    )
    ON CONFLICT(date_bucket, tool_name) DO UPDATE SET
        call_count = call_count + 1,
        error_count = error_count + CASE WHEN NEW.success = 0 THEN 1 ELSE 0 END,
        avg_response_time_ms = (
            (COALESCE(avg_response_time_ms, 0) * call_count + NEW.response_time_ms) / (call_count + 1)
        ),
        last_updated = CURRENT_TIMESTAMP;
END;

-- ============================================
-- Cleanup Policy
-- ============================================

-- Create trigger to automatically clean up old events (180 days retention)
CREATE TRIGGER IF NOT EXISTS trg_mcp_events_cleanup
AFTER INSERT ON archon_mcp_usage_events
BEGIN
    DELETE FROM archon_mcp_usage_events
    WHERE timestamp < datetime('now', '-180 days');

    DELETE FROM archon_mcp_usage_hourly
    WHERE hour_bucket < datetime('now', '-180 days');

    DELETE FROM archon_mcp_usage_daily
    WHERE date_bucket < date('now', '-180 days');
END;
