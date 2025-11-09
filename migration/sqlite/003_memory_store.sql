-- Migration: Memory Store
-- Description: Add tables for storing and retrieving AI memory/knowledge across sessions
-- Created: 2025-11-09

-- ============================================
-- Main Memory Table
-- ============================================
CREATE TABLE IF NOT EXISTS archon_mcp_memories (
    id TEXT PRIMARY KEY,
    memory_key TEXT NOT NULL UNIQUE,
    memory_content TEXT NOT NULL,
    memory_type TEXT NOT NULL DEFAULT 'learning',
    session_id TEXT,
    tags TEXT,
    metadata TEXT,
    embedding BLOB,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast queries (memory_key already indexed via UNIQUE constraint)
CREATE INDEX IF NOT EXISTS idx_memory_type ON archon_mcp_memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_memory_session ON archon_mcp_memories(session_id);
CREATE INDEX IF NOT EXISTS idx_memory_created ON archon_mcp_memories(created_at DESC);

-- ============================================
-- Memory Usage Statistics Table
-- ============================================
CREATE TABLE IF NOT EXISTS archon_mcp_memory_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id TEXT NOT NULL,
    access_count INTEGER NOT NULL DEFAULT 0,
    last_accessed DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (memory_id) REFERENCES archon_mcp_memories(id) ON DELETE CASCADE,
    UNIQUE(memory_id)
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_memory_stats_accessed ON archon_mcp_memory_stats(last_accessed DESC);
CREATE INDEX IF NOT EXISTS idx_memory_stats_count ON archon_mcp_memory_stats(access_count DESC);

-- ============================================
-- Triggers for Automatic Maintenance
-- ============================================

-- Trigger to update updated_at timestamp on memory updates
CREATE TRIGGER IF NOT EXISTS trg_memory_updated_at
AFTER UPDATE ON archon_mcp_memories
BEGIN
    UPDATE archon_mcp_memories
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- Trigger to track memory access statistics
CREATE TRIGGER IF NOT EXISTS trg_memory_access_stats
AFTER UPDATE ON archon_mcp_memory_stats
BEGIN
    UPDATE archon_mcp_memory_stats
    SET last_accessed = CURRENT_TIMESTAMP
    WHERE memory_id = NEW.memory_id;
END;

-- ============================================
-- Cleanup Policy
-- ============================================

-- Create trigger to automatically clean up old memories (90 days retention)
-- This keeps the memory store fresh and relevant
CREATE TRIGGER IF NOT EXISTS trg_memory_cleanup
AFTER INSERT ON archon_mcp_memories
BEGIN
    DELETE FROM archon_mcp_memories
    WHERE created_at < datetime('now', '-90 days')
    AND session_id IS NULL;  -- Only clean up non-session-scoped memories

    DELETE FROM archon_mcp_memories
    WHERE created_at < datetime('now', '-30 days')
    AND session_id IS NOT NULL;  -- Session-scoped memories expire faster

    DELETE FROM archon_mcp_memory_stats
    WHERE memory_id NOT IN (SELECT id FROM archon_mcp_memories);
END;
