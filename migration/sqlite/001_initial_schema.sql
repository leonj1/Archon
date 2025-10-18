-- =====================================================
-- Archon SQLite Database Schema
-- =====================================================
-- This is a simplified version of the PostgreSQL schema
-- adapted for SQLite's capabilities
-- =====================================================

-- =====================================================
-- SECTION 1: MIGRATIONS TRACKING
-- =====================================================

CREATE TABLE IF NOT EXISTS archon_migrations (
    id TEXT PRIMARY KEY,
    version TEXT NOT NULL,
    migration_name TEXT NOT NULL,
    checksum TEXT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(version, migration_name)
);

-- =====================================================
-- SECTION 2: SETTINGS AND CREDENTIALS
-- =====================================================

CREATE TABLE IF NOT EXISTS archon_settings (
    id TEXT PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    value TEXT,
    encrypted_value TEXT,
    is_encrypted BOOLEAN DEFAULT 0,
    category TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for settings
CREATE INDEX IF NOT EXISTS idx_archon_settings_key ON archon_settings(key);
CREATE INDEX IF NOT EXISTS idx_archon_settings_category ON archon_settings(category);

-- =====================================================
-- SECTION 3: KNOWLEDGE BASE TABLES  
-- =====================================================

-- Sources table
CREATE TABLE IF NOT EXISTS archon_sources (
    source_id TEXT PRIMARY KEY,
    source_url TEXT,
    source_display_name TEXT,
    summary TEXT,
    total_word_count INTEGER DEFAULT 0,
    title TEXT,
    metadata TEXT DEFAULT '{}',  -- JSON stored as TEXT in SQLite
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for sources
CREATE INDEX IF NOT EXISTS idx_archon_sources_title ON archon_sources(title);
CREATE INDEX IF NOT EXISTS idx_archon_sources_url ON archon_sources(source_url);
CREATE INDEX IF NOT EXISTS idx_archon_sources_display_name ON archon_sources(source_display_name);

-- Documentation chunks table (simplified without vector columns)
CREATE TABLE IF NOT EXISTS archon_crawled_pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    chunk_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT DEFAULT '{}',
    source_id TEXT NOT NULL,
    page_id TEXT,
    -- Model tracking
    llm_chat_model TEXT,
    embedding_model TEXT,
    embedding_dimension INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Constraints
    UNIQUE(url, chunk_number),
    FOREIGN KEY (source_id) REFERENCES archon_sources(source_id) ON DELETE CASCADE
);

-- Indexes for crawled pages
CREATE INDEX IF NOT EXISTS idx_archon_crawled_pages_source_id ON archon_crawled_pages(source_id);
CREATE INDEX IF NOT EXISTS idx_archon_crawled_pages_page_id ON archon_crawled_pages(page_id);
CREATE INDEX IF NOT EXISTS idx_archon_crawled_pages_url ON archon_crawled_pages(url);

-- Code examples table
CREATE TABLE IF NOT EXISTS archon_code_examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    chunk_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    summary TEXT NOT NULL,
    metadata TEXT DEFAULT '{}',
    source_id TEXT NOT NULL,
    -- Model tracking
    llm_chat_model TEXT,
    embedding_model TEXT,
    embedding_dimension INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Constraints
    UNIQUE(url, chunk_number),
    FOREIGN KEY (source_id) REFERENCES archon_sources(source_id) ON DELETE CASCADE
);

-- Indexes for code examples
CREATE INDEX IF NOT EXISTS idx_archon_code_examples_source_id ON archon_code_examples(source_id);
CREATE INDEX IF NOT EXISTS idx_archon_code_examples_url ON archon_code_examples(url);

-- Page metadata table
CREATE TABLE IF NOT EXISTS archon_page_metadata (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    full_content TEXT NOT NULL,
    -- Section metadata
    section_title TEXT,
    section_order INTEGER DEFAULT 0,
    -- Statistics
    word_count INTEGER NOT NULL,
    char_count INTEGER NOT NULL,
    chunk_count INTEGER DEFAULT 0,
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Flexible metadata
    metadata TEXT DEFAULT '{}',
    -- Constraints
    FOREIGN KEY (source_id) REFERENCES archon_sources(source_id) ON DELETE CASCADE
);

-- Indexes for page metadata
CREATE INDEX IF NOT EXISTS idx_archon_page_metadata_source_id ON archon_page_metadata(source_id);
CREATE INDEX IF NOT EXISTS idx_archon_page_metadata_url ON archon_page_metadata(url);
CREATE INDEX IF NOT EXISTS idx_archon_page_metadata_section ON archon_page_metadata(source_id, section_title, section_order);

-- =====================================================
-- SECTION 4: PROJECTS AND TASKS
-- =====================================================

-- Projects table
CREATE TABLE IF NOT EXISTS archon_projects (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    docs TEXT DEFAULT '[]',
    features TEXT DEFAULT '[]',
    data TEXT DEFAULT '[]',
    github_repo TEXT,
    pinned BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for projects
CREATE INDEX IF NOT EXISTS idx_archon_projects_created_at ON archon_projects(created_at);
CREATE INDEX IF NOT EXISTS idx_archon_projects_pinned ON archon_projects(pinned);

-- Tasks table
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
    archived BOOLEAN DEFAULT 0,
    archived_at TIMESTAMP NULL,
    archived_by TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for tasks
CREATE INDEX IF NOT EXISTS idx_archon_tasks_project_id ON archon_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_status ON archon_tasks(status);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_assignee ON archon_tasks(assignee);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_order ON archon_tasks(task_order);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_priority ON archon_tasks(priority);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_archived ON archon_tasks(archived);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_parent ON archon_tasks(parent_task_id);

-- Project Sources junction table
CREATE TABLE IF NOT EXISTS archon_project_sources (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES archon_projects(id) ON DELETE CASCADE,
    source_id TEXT NOT NULL,
    linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT DEFAULT 'system',
    notes TEXT,
    UNIQUE(project_id, source_id)
);

-- Indexes for project sources
CREATE INDEX IF NOT EXISTS idx_archon_project_sources_project_id ON archon_project_sources(project_id);
CREATE INDEX IF NOT EXISTS idx_archon_project_sources_source_id ON archon_project_sources(source_id);

-- Document versions table
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Ensure we have either project_id OR task_id, not both
    CHECK (
        (project_id IS NOT NULL AND task_id IS NULL) OR
        (project_id IS NULL AND task_id IS NOT NULL)
    ),
    UNIQUE(project_id, task_id, field_name, version_number)
);

-- Indexes for document versions
CREATE INDEX IF NOT EXISTS idx_archon_document_versions_project_id ON archon_document_versions(project_id);
CREATE INDEX IF NOT EXISTS idx_archon_document_versions_task_id ON archon_document_versions(task_id);
CREATE INDEX IF NOT EXISTS idx_archon_document_versions_field_name ON archon_document_versions(field_name);

-- =====================================================
-- SECTION 5: PROMPTS TABLE
-- =====================================================

-- Prompts table for storing system prompts
CREATE TABLE IF NOT EXISTS archon_prompts (
    id TEXT PRIMARY KEY,
    prompt_name TEXT UNIQUE NOT NULL,
    prompt TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster prompt lookups
CREATE INDEX IF NOT EXISTS idx_archon_prompts_name ON archon_prompts(prompt_name);

-- =====================================================
-- SECTION 6: NOTES ON UPDATED_AT TIMESTAMPS
-- =====================================================

-- Note: SQLite doesn't support PostgreSQL-style functions like update_updated_at_column()
-- The updated_at fields are managed by the application layer in SQLite.
-- All repository methods (create, update, upsert) explicitly set updated_at = CURRENT_TIMESTAMP.
-- This ensures consistent timestamp handling across the application.

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================
