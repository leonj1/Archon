-- =====================================================
-- IMMEDIATE FIX FOR MISSING COLUMNS
-- Run this in Supabase Dashboard SQL Editor NOW
-- =====================================================

-- 1. Add the missing columns to archon_sources
ALTER TABLE archon_sources 
ADD COLUMN IF NOT EXISTS source_url TEXT,
ADD COLUMN IF NOT EXISTS source_display_name TEXT;

-- 2. Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_archon_sources_url ON archon_sources(source_url);
CREATE INDEX IF NOT EXISTS idx_archon_sources_display_name ON archon_sources(source_display_name);

-- 3. Backfill data for existing records
UPDATE archon_sources 
SET 
    source_url = COALESCE(source_url, source_id),
    source_display_name = COALESCE(source_display_name, source_id)
WHERE source_url IS NULL OR source_display_name IS NULL;

-- 4. Create migration tracking table
CREATE TABLE IF NOT EXISTS archon_migrations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    version VARCHAR(50) NOT NULL,
    migration_name VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    checksum VARCHAR(32),
    UNIQUE(version, migration_name)
);

-- 5. Record that we've applied this migration
INSERT INTO archon_migrations (version, migration_name)
VALUES ('0.1.0', '001_add_source_url_display_name')
ON CONFLICT DO NOTHING;

-- =====================================================
-- DONE! Restart your containers after running this:
-- docker compose restart
-- =====================================================
