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
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    chunk_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT DEFAULT '{}',
    source_id TEXT NOT NULL,
    page_id TEXT,
    llm_chat_model TEXT,
    embedding_model TEXT,
    embedding_dimension INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(url, chunk_number),
    FOREIGN KEY (source_id) REFERENCES archon_sources(source_id) ON DELETE CASCADE
);

-- Indexes for archon_crawled_pages
CREATE INDEX IF NOT EXISTS idx_archon_crawled_pages_source_id ON archon_crawled_pages(source_id);
CREATE INDEX IF NOT EXISTS idx_archon_crawled_pages_page_id ON archon_crawled_pages(page_id);
CREATE INDEX IF NOT EXISTS idx_archon_crawled_pages_url ON archon_crawled_pages(url);

-- archon_code_examples table
CREATE TABLE IF NOT EXISTS archon_code_examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    chunk_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    summary TEXT NOT NULL,
    metadata TEXT DEFAULT '{}',
    source_id TEXT NOT NULL,
    llm_chat_model TEXT,
    embedding_model TEXT,
    embedding_dimension INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(url, chunk_number),
    FOREIGN KEY (source_id) REFERENCES archon_sources(source_id) ON DELETE CASCADE
);

-- Indexes for archon_code_examples
CREATE INDEX IF NOT EXISTS idx_archon_code_examples_source_id ON archon_code_examples(source_id);
CREATE INDEX IF NOT EXISTS idx_archon_code_examples_url ON archon_code_examples(url);

-- archon_page_metadata table
CREATE TABLE IF NOT EXISTS archon_page_metadata (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    full_content TEXT NOT NULL,
    section_title TEXT,
    section_order INTEGER DEFAULT 0,
    word_count INTEGER NOT NULL,
    char_count INTEGER NOT NULL,
    chunk_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    metadata TEXT DEFAULT '{}',
    FOREIGN KEY (source_id) REFERENCES archon_sources(source_id) ON DELETE CASCADE
);

-- Indexes for archon_page_metadata
CREATE INDEX IF NOT EXISTS idx_archon_page_metadata_source_id ON archon_page_metadata(source_id);
CREATE INDEX IF NOT EXISTS idx_archon_page_metadata_url ON archon_page_metadata(url);
CREATE INDEX IF NOT EXISTS idx_archon_page_metadata_section ON archon_page_metadata(source_id, section_title, section_order);

-- archon_projects table
CREATE TABLE IF NOT EXISTS archon_projects (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    docs TEXT DEFAULT '[]',
    features TEXT DEFAULT '[]',
    data TEXT DEFAULT '[]',
    github_repo TEXT,
    pinned INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Indexes for archon_projects
CREATE INDEX IF NOT EXISTS idx_archon_projects_created_at ON archon_projects(created_at);
CREATE INDEX IF NOT EXISTS idx_archon_projects_pinned ON archon_projects(pinned);

-- archon_tasks table
CREATE TABLE IF NOT EXISTS archon_tasks (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES archon_projects(id) ON DELETE CASCADE,
    parent_task_id TEXT REFERENCES archon_tasks(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    status TEXT DEFAULT 'todo' CHECK (status IN ('todo', 'doing', 'review', 'done')),
    assignee TEXT DEFAULT 'User' CHECK (assignee IS NOT NULL AND assignee != ''),
    task_order INTEGER DEFAULT 0,
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    feature TEXT,
    sources TEXT DEFAULT '[]',
    code_examples TEXT DEFAULT '[]',
    archived INTEGER DEFAULT 0,
    archived_at TEXT NULL,
    archived_by TEXT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Indexes for archon_tasks
CREATE INDEX IF NOT EXISTS idx_archon_tasks_project_id ON archon_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_status ON archon_tasks(status);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_assignee ON archon_tasks(assignee);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_order ON archon_tasks(task_order);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_priority ON archon_tasks(priority);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_archived ON archon_tasks(archived);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_parent ON archon_tasks(parent_task_id);

-- archon_project_sources table (many-to-many)
CREATE TABLE IF NOT EXISTS archon_project_sources (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES archon_projects(id) ON DELETE CASCADE,
    source_id TEXT NOT NULL,
    linked_at TEXT DEFAULT (datetime('now')),
    created_by TEXT DEFAULT 'system',
    notes TEXT,
    UNIQUE(project_id, source_id)
);

-- Indexes for archon_project_sources
CREATE INDEX IF NOT EXISTS idx_archon_project_sources_project_id ON archon_project_sources(project_id);
CREATE INDEX IF NOT EXISTS idx_archon_project_sources_source_id ON archon_project_sources(source_id);

-- archon_document_versions table
CREATE TABLE IF NOT EXISTS archon_document_versions (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES archon_projects(id) ON DELETE CASCADE,
    task_id TEXT REFERENCES archon_tasks(id) ON DELETE CASCADE,
    field_name TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    change_summary TEXT,
    change_type TEXT DEFAULT 'update',
    document_id TEXT,
    created_by TEXT DEFAULT 'system',
    created_at TEXT DEFAULT (datetime('now')),
    CHECK (
        (project_id IS NOT NULL AND task_id IS NULL) OR
        (project_id IS NULL AND task_id IS NOT NULL)
    ),
    UNIQUE(project_id, task_id, field_name, version_number)
);

-- Indexes for archon_document_versions
CREATE INDEX IF NOT EXISTS idx_archon_document_versions_project_id ON archon_document_versions(project_id);
CREATE INDEX IF NOT EXISTS idx_archon_document_versions_task_id ON archon_document_versions(task_id);
CREATE INDEX IF NOT EXISTS idx_archon_document_versions_field_name ON archon_document_versions(field_name);

-- Record this migration
INSERT INTO archon_migrations (version, migration_name)
VALUES ('1.0.0', 'V001__initial_schema');
