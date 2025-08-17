-- PostgreSQL Schema for Archon
-- With pgvector support for embeddings

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS archon_code_examples CASCADE;
DROP TABLE IF EXISTS archon_crawled_pages CASCADE;
DROP TABLE IF EXISTS archon_tasks CASCADE;
DROP TABLE IF EXISTS archon_projects CASCADE;
DROP TABLE IF EXISTS archon_sources CASCADE;

-- Core tables
CREATE TABLE archon_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url TEXT,
    title TEXT,
    source_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    metadata JSONB DEFAULT '{}',
    error_message TEXT,
    crawled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE archon_crawled_pages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES archon_sources(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    title TEXT,
    content TEXT,
    chunk_index INTEGER DEFAULT 0,
    total_chunks INTEGER DEFAULT 1,
    metadata JSONB DEFAULT '{}',
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE archon_code_examples (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES archon_sources(id) ON DELETE CASCADE,
    file_path TEXT,
    function_name TEXT,
    class_name TEXT,
    code_snippet TEXT,
    language VARCHAR(50),
    summary TEXT,
    metadata JSONB DEFAULT '{}',
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE archon_projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    github_repo TEXT,
    docs JSONB DEFAULT '[]',
    features JSONB DEFAULT '{}',
    data JSONB DEFAULT '{}',
    prd JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE archon_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES archon_projects(id) ON DELETE CASCADE,
    parent_task_id UUID REFERENCES archon_tasks(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'todo',
    assignee VARCHAR(100) DEFAULT 'User',
    task_order INTEGER DEFAULT 0,
    feature VARCHAR(100),
    sources JSONB DEFAULT '[]',
    code_examples JSONB DEFAULT '[]',
    archived BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMP WITH TIME ZONE,
    archived_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_sources_status ON archon_sources(status);
CREATE INDEX idx_sources_created ON archon_sources(created_at DESC);
CREATE INDEX idx_crawled_source ON archon_crawled_pages(source_id);
CREATE INDEX idx_crawled_embedding ON archon_crawled_pages USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_code_embedding ON archon_code_examples USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_tasks_project ON archon_tasks(project_id);
CREATE INDEX idx_tasks_status ON archon_tasks(status);
CREATE INDEX idx_projects_created ON archon_projects(created_at DESC);

-- Update triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_archon_sources_updated_at BEFORE UPDATE ON archon_sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_archon_crawled_pages_updated_at BEFORE UPDATE ON archon_crawled_pages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_archon_projects_updated_at BEFORE UPDATE ON archon_projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_archon_tasks_updated_at BEFORE UPDATE ON archon_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert test data
INSERT INTO archon_sources (id, url, title, source_type, status) VALUES
    ('550e8400-e29b-41d4-a716-446655440000', 'https://example.com', 'Test Source', 'website', 'completed'),
    ('550e8400-e29b-41d4-a716-446655440001', 'https://docs.example.com', 'Documentation', 'documentation', 'pending');

INSERT INTO archon_projects (id, title, description, docs, features) VALUES
    ('660e8400-e29b-41d4-a716-446655440000', 'Test Project', 'A test project for PostgreSQL verification', '[]', '{}');