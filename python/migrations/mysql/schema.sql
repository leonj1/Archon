-- MySQL Schema for Archon
-- Compatible with the existing Supabase schema

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS archon_vector_index;
DROP TABLE IF EXISTS archon_code_examples;
DROP TABLE IF EXISTS archon_crawled_pages;
DROP TABLE IF EXISTS archon_tasks;
DROP TABLE IF EXISTS archon_projects;
DROP TABLE IF EXISTS archon_sources;

-- Core tables
CREATE TABLE archon_sources (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    url TEXT,
    title TEXT,
    source_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    metadata JSON,
    error_message TEXT,
    crawled_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_created (created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE archon_crawled_pages (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    source_id CHAR(36),
    url TEXT NOT NULL,
    title TEXT,
    content LONGTEXT,
    chunk_index INT DEFAULT 0,
    total_chunks INT DEFAULT 1,
    metadata JSON,
    embedding BLOB,  -- Store as binary, 1536 * 4 bytes for float32
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES archon_sources(id) ON DELETE CASCADE,
    INDEX idx_source (source_id),
    INDEX idx_created (created_at DESC),
    FULLTEXT INDEX idx_content (title, content)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE archon_code_examples (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    source_id CHAR(36),
    file_path TEXT,
    function_name TEXT,
    class_name TEXT,
    code_snippet TEXT,
    language VARCHAR(50),
    summary TEXT,
    metadata JSON,
    embedding BLOB,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES archon_sources(id) ON DELETE CASCADE,
    INDEX idx_source (source_id),
    INDEX idx_language (language)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE archon_projects (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    title TEXT NOT NULL,
    description TEXT,
    github_repo TEXT,
    docs JSON,
    features JSON,
    data JSON,
    prd JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_created (created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE archon_tasks (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    project_id CHAR(36),
    parent_task_id CHAR(36),
    title TEXT NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'todo',
    assignee VARCHAR(100) DEFAULT 'User',
    task_order INT DEFAULT 0,
    feature VARCHAR(100),
    sources JSON,
    code_examples JSON,
    archived BOOLEAN DEFAULT FALSE,
    archived_at DATETIME,
    archived_by VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES archon_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_task_id) REFERENCES archon_tasks(id) ON DELETE CASCADE,
    INDEX idx_project (project_id),
    INDEX idx_status (status),
    INDEX idx_order (task_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- External vector index table for MySQL
-- Since MySQL doesn't have native vector support, we track vector operations externally
CREATE TABLE archon_vector_index (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    table_name VARCHAR(50) NOT NULL,
    record_id CHAR(36) NOT NULL,
    vector_dimension INT DEFAULT 1536,
    vector_service VARCHAR(50) DEFAULT 'local',
    external_id VARCHAR(255),
    metadata JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_table_record (table_name, record_id),
    INDEX idx_external (external_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert some test data
INSERT INTO archon_sources (id, url, title, source_type, status) VALUES
    ('test-source-001', 'https://example.com', 'Test Source', 'website', 'completed'),
    ('test-source-002', 'https://docs.example.com', 'Documentation', 'documentation', 'pending');

INSERT INTO archon_projects (id, title, description, docs, features) VALUES
    ('test-project-001', 'Test Project', 'A test project for MySQL verification', '[]', '{}');