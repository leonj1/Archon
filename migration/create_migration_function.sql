-- =====================================================
-- Create RPC Function for Automatic Schema Migration
-- =====================================================
-- This function allows the application to apply schema changes
-- programmatically during startup
--
-- SECURITY NOTE: This function should only be accessible by
-- the service role key, never by public/anon users
-- =====================================================

-- Create the migration function
CREATE OR REPLACE FUNCTION apply_schema_migration(migration_sql TEXT)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    result JSON;
BEGIN
    -- Only allow service role to execute this function
    IF auth.role() != 'service_role' THEN
        RAISE EXCEPTION 'Unauthorized: Only service role can apply migrations';
    END IF;
    
    -- Execute the migration SQL
    EXECUTE migration_sql;
    
    -- Return success
    result = json_build_object(
        'success', true,
        'message', 'Migration applied successfully'
    );
    
    RETURN result;
    
EXCEPTION
    WHEN OTHERS THEN
        -- Return error details
        result = json_build_object(
            'success', false,
            'error', SQLERRM,
            'detail', SQLSTATE
        );
        RETURN result;
END;
$$;

-- Grant execute permission only to service role
REVOKE ALL ON FUNCTION apply_schema_migration(TEXT) FROM PUBLIC;
REVOKE ALL ON FUNCTION apply_schema_migration(TEXT) FROM anon;
REVOKE ALL ON FUNCTION apply_schema_migration(TEXT) FROM authenticated;
GRANT EXECUTE ON FUNCTION apply_schema_migration(TEXT) TO service_role;

-- Create a safer function specifically for adding source_url columns
CREATE OR REPLACE FUNCTION ensure_source_url_columns()
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    result JSON;
    column_exists BOOLEAN;
BEGIN
    -- Check if source_url column exists
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'archon_sources' 
        AND column_name = 'source_url'
    ) INTO column_exists;
    
    IF NOT column_exists THEN
        -- Add source_url column
        ALTER TABLE archon_sources 
        ADD COLUMN source_url TEXT;
        
        -- Add source_display_name column if it doesn't exist
        ALTER TABLE archon_sources 
        ADD COLUMN IF NOT EXISTS source_display_name TEXT;
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_archon_sources_url 
        ON archon_sources(source_url);
        
        CREATE INDEX IF NOT EXISTS idx_archon_sources_display_name 
        ON archon_sources(source_display_name);
        
        -- Backfill data
        UPDATE archon_sources 
        SET 
            source_url = COALESCE(source_url, source_id),
            source_display_name = COALESCE(source_display_name, source_id)
        WHERE source_url IS NULL OR source_display_name IS NULL;
        
        result = json_build_object(
            'success', true,
            'message', 'source_url columns added successfully',
            'columns_added', true
        );
    ELSE
        result = json_build_object(
            'success', true,
            'message', 'source_url columns already exist',
            'columns_added', false
        );
    END IF;
    
    RETURN result;
    
EXCEPTION
    WHEN OTHERS THEN
        result = json_build_object(
            'success', false,
            'error', SQLERRM,
            'detail', SQLSTATE
        );
        RETURN result;
END;
$$;

-- Grant execute permission to service role and authenticated users
REVOKE ALL ON FUNCTION ensure_source_url_columns() FROM PUBLIC;
REVOKE ALL ON FUNCTION ensure_source_url_columns() FROM anon;
GRANT EXECUTE ON FUNCTION ensure_source_url_columns() TO service_role;
GRANT EXECUTE ON FUNCTION ensure_source_url_columns() TO authenticated;

-- Create function to check schema status
CREATE OR REPLACE FUNCTION check_schema_status()
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    result JSON;
    source_url_exists BOOLEAN;
    display_name_exists BOOLEAN;
    migrations_table_exists BOOLEAN;
BEGIN
    -- Check for source_url column
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'archon_sources' 
        AND column_name = 'source_url'
    ) INTO source_url_exists;
    
    -- Check for source_display_name column
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'archon_sources' 
        AND column_name = 'source_display_name'
    ) INTO display_name_exists;
    
    -- Check for migrations table
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_name = 'archon_migrations'
    ) INTO migrations_table_exists;
    
    result = json_build_object(
        'source_url_exists', source_url_exists,
        'source_display_name_exists', display_name_exists,
        'migrations_table_exists', migrations_table_exists,
        'schema_complete', source_url_exists AND display_name_exists
    );
    
    RETURN result;
END;
$$;

-- Grant execute permission to service role and authenticated
REVOKE ALL ON FUNCTION check_schema_status() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION check_schema_status() TO anon;
GRANT EXECUTE ON FUNCTION check_schema_status() TO authenticated;
GRANT EXECUTE ON FUNCTION check_schema_status() TO service_role;

-- =====================================================
-- IMPORTANT: Run this SQL in your Supabase Dashboard
-- to enable automatic schema migration on startup
-- =====================================================
