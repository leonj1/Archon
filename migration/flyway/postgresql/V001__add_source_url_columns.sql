-- V001: Add source_url and source_display_name columns to archon_sources
-- This is the critical migration that was missing

-- Add columns if they don't exist
ALTER TABLE archon_sources 
ADD COLUMN IF NOT EXISTS source_url TEXT,
ADD COLUMN IF NOT EXISTS source_display_name TEXT;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_archon_sources_url 
ON archon_sources(source_url);

CREATE INDEX IF NOT EXISTS idx_archon_sources_display_name 
ON archon_sources(source_display_name);

-- Backfill existing data
UPDATE archon_sources 
SET 
    source_url = COALESCE(source_url, source_id),
    source_display_name = COALESCE(source_display_name, source_id)
WHERE source_url IS NULL OR source_display_name IS NULL;
