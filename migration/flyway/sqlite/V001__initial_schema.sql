-- V001: Initial SQLite Schema
-- Creates all required tables for Archon

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- archon_migrations table for tracking migrations
CREATE TABLE IF NOT EXISTS archon_migrations (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    version TEXT NOT NULL,
    migration_name TEXT NOT NULL,
    applied_at TEXT DEFAULT (datetime('now')),
    checksum TEXT,
    UNIQUE(version, migration_name)
);

-- archon_settings table
CREATE TABLE IF NOT EXISTS archon_settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    description TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- archon_sources table (with source_url from the start!)
CREATE TABLE IF NOT EXISTS archon_sources (
    source_id TEXT PRIMARY KEY,
    source_url TEXT,
    source_display_name TEXT,
    summary TEXT,
    total_word_count INTEGER DEFAULT 0,
    title TEXT,
    metadata TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Indexes for archon_sources
CREATE INDEX IF NOT EXISTS idx_archon_sources_url ON archon_sources(source_url);
CREATE INDEX IF NOT EXISTS idx_archon_sources_display_name ON archon_sources(source_display_name);
CREATE INDEX IF NOT EXISTS idx_archon_sources_created_at ON archon_sources(created_at);
CREATE INDEX IF NOT EXISTS idx_archon_sources_updated_at ON archon_sources(updated_at);

-- archon_crawled_pages table
CREATE TABLE IF NOT EXISTS archon_crawled_pages (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    source_id TEXT,
    url TEXT NOT NULL,
    chunk_number INTEGER DEFAULT 0,
    content TEXT,
    metadata TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (source_id) REFERENCES archon_sources(source_id) ON DELETE CASCADE
);

-- Indexes for archon_crawled_pages
CREATE INDEX IF NOT EXISTS idx_archon_crawled_pages_source_id ON archon_crawled_pages(source_id);
CREATE INDEX IF NOT EXISTS idx_archon_crawled_pages_url ON archon_crawled_pages(url);

-- archon_code_examples table
CREATE TABLE IF NOT EXISTS archon_code_examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    title TEXT,
    summary TEXT,
    language TEXT,
    code TEXT NOT NULL,
    relevance_score REAL DEFAULT 0.5,
    url TEXT,
    metadata TEXT DEFAULT '{}',
    FOREIGN KEY (source_id) REFERENCES archon_sources(source_id) ON DELETE CASCADE
);

-- Indexes for archon_code_examples (skip if table doesn't have the column yet)
CREATE INDEX IF NOT EXISTS idx_archon_code_examples_source_id ON archon_code_examples(source_id);

-- archon_page_metadata table
CREATE TABLE IF NOT EXISTS archon_page_metadata (
    id TEXT PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    section_title TEXT,
    word_count INTEGER DEFAULT 0
);

-- archon_projects table
CREATE TABLE IF NOT EXISTS archon_projects (
    project_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',
    features TEXT DEFAULT '[]',
    metadata TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- archon_tasks table
CREATE TABLE IF NOT EXISTS archon_tasks (
    task_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    project_id TEXT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'todo',
    task_order INTEGER DEFAULT 0,
    priority TEXT DEFAULT 'medium',
    assignee TEXT DEFAULT 'User',
    metadata TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    completed_at TEXT,
    FOREIGN KEY (project_id) REFERENCES archon_projects(project_id) ON DELETE CASCADE
);

-- archon_project_sources table (many-to-many)
CREATE TABLE IF NOT EXISTS archon_project_sources (
    project_id TEXT,
    source_id TEXT,
    PRIMARY KEY (project_id, source_id),
    FOREIGN KEY (project_id) REFERENCES archon_projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES archon_sources(source_id) ON DELETE CASCADE
);

-- archon_document_versions table
CREATE TABLE IF NOT EXISTS archon_document_versions (
    version_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    document_id TEXT NOT NULL,
    document_type TEXT NOT NULL,
    version_number INTEGER DEFAULT 1,
    content TEXT,
    metadata TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now'))
);

-- Record this migration
INSERT INTO archon_migrations (version, migration_name)
VALUES ('1.0.0', 'V001__initial_schema');
