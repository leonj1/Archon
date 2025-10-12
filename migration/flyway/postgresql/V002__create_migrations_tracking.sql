-- V002: Create archon_migrations table for application-level migration tracking
-- This is separate from Flyway's own tracking table

CREATE TABLE IF NOT EXISTS archon_migrations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    version VARCHAR(50) NOT NULL,
    migration_name VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    checksum VARCHAR(32),
    UNIQUE(version, migration_name)
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_archon_migrations_version 
ON archon_migrations(version);

-- Insert record for the source_url migration
INSERT INTO archon_migrations (version, migration_name)
VALUES ('0.1.0', '001_add_source_url_display_name')
ON CONFLICT (version, migration_name) DO NOTHING;
