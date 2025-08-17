-- PostgreSQL Functions for Vector Similarity Search

-- Function for searching crawled pages
CREATE OR REPLACE FUNCTION match_archon_crawled_pages(
    query_embedding vector(1536),
    match_count INT DEFAULT 10,
    filter JSONB DEFAULT '{}'::jsonb
)
RETURNS TABLE (
    id UUID,
    source_id UUID,
    url TEXT,
    title TEXT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cp.id,
        cp.source_id,
        cp.url,
        cp.title,
        cp.content,
        cp.metadata,
        1 - (cp.embedding <=> query_embedding) AS similarity
    FROM archon_crawled_pages cp
    WHERE 
        cp.embedding IS NOT NULL
        AND (filter IS NULL OR filter = '{}'::jsonb OR cp.metadata @> filter)
    ORDER BY cp.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Function for searching code examples
CREATE OR REPLACE FUNCTION match_archon_code_examples(
    query_embedding vector(1536),
    match_count INT DEFAULT 10,
    filter JSONB DEFAULT '{}'::jsonb
)
RETURNS TABLE (
    id UUID,
    source_id UUID,
    file_path TEXT,
    function_name TEXT,
    code_snippet TEXT,
    summary TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ce.id,
        ce.source_id,
        ce.file_path,
        ce.function_name,
        ce.code_snippet,
        ce.summary,
        ce.metadata,
        1 - (ce.embedding <=> query_embedding) AS similarity
    FROM archon_code_examples ce
    WHERE 
        ce.embedding IS NOT NULL
        AND (filter IS NULL OR filter = '{}'::jsonb OR ce.metadata @> filter)
    ORDER BY ce.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;