# Database Migration Setup

The application has detected that your database is missing critical schema components (`source_url` and `source_display_name` columns). This guide provides three options to resolve this issue.

## Option 1: Enable Automatic Migration (Recommended)

This option allows the application to automatically apply schema changes on startup.

### Steps:

1. **Open your Supabase Dashboard**
   - Navigate to your project at [app.supabase.com](https://app.supabase.com)
   - Go to the **SQL Editor** section

2. **Create the migration functions**
   - Click "New Query"
   - Copy the entire contents of `/migration/create_migration_function.sql`
   - Paste into the query editor
   - Click "Run" to execute

3. **Restart the application**
   ```bash
   docker compose restart
   ```

4. **Verify**
   - The application will automatically apply the missing schema on startup
   - Check the logs: `docker logs archon-server`
   - You should see "Migration result: source_url columns added successfully"

## Option 2: Manual Migration (Quick Fix)

If you prefer to apply the schema changes manually:

### Steps:

1. **Open your Supabase Dashboard** → SQL Editor

2. **Run this SQL:**
   ```sql
   -- Add missing columns to archon_sources
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

   -- Create migration tracking table
   CREATE TABLE IF NOT EXISTS archon_migrations (
       id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
       version VARCHAR(50) NOT NULL,
       migration_name VARCHAR(255) NOT NULL,
       applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       checksum VARCHAR(32),
       UNIQUE(version, migration_name)
   );

   -- Record that we've applied the critical migration
   INSERT INTO archon_migrations (version, migration_name)
   VALUES ('0.1.0', '001_add_source_url_display_name')
   ON CONFLICT DO NOTHING;
   ```

3. **Restart the application**
   ```bash
   docker compose restart
   ```

## Option 3: Complete Schema Setup

For a fresh installation or to ensure all migrations are applied:

1. **Open your Supabase Dashboard** → SQL Editor

2. **Run the complete setup script**
   - Copy the entire contents of `/migration/complete_setup.sql`
   - Paste and run in SQL Editor

3. **This will:**
   - Create all required tables
   - Add all indexes
   - Set up the migration tracking system
   - Apply all 12 migrations

## Verification

After applying any option above, verify the schema is correct:

### Check columns exist:
```sql
SELECT 
    column_name,
    data_type 
FROM 
    information_schema.columns 
WHERE 
    table_name = 'archon_sources' 
    AND column_name IN ('source_url', 'source_display_name');
```

### Check migration status:
```bash
curl http://localhost:8181/api/migrations/status
```

### Check application health:
```bash
curl http://localhost:8181/health
```

## Troubleshooting

### Still seeing errors after migration?

1. **Clear Supabase cache:**
   - Sometimes Supabase caches the schema
   - Wait 1-2 minutes after running migrations
   - Or restart your Supabase project

2. **Check logs:**
   ```bash
   docker logs archon-server -f
   ```

3. **Verify RPC functions (if using Option 1):**
   ```sql
   SELECT proname 
   FROM pg_proc 
   WHERE proname IN ('ensure_source_url_columns', 'apply_schema_migration');
   ```

### Manual verification of schema:
```sql
-- List all columns in archon_sources
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'archon_sources'
ORDER BY ordinal_position;
```

## Why These Columns Are Critical

The `source_url` and `source_display_name` columns are essential for:

1. **source_url**: Stores the original URL that was crawled or uploaded
   - Used to display the source link in the UI
   - Required for re-crawling and updates
   - Links documents back to their origin

2. **source_display_name**: User-friendly name for the source
   - Shows readable names instead of IDs
   - Improves UI/UX in the knowledge base
   - Used in search results and navigation

Without these columns, the knowledge base features will fail with database errors.

## Next Steps

After fixing the schema:

1. **Re-crawl any existing sources** if needed
2. **Check the knowledge base** is displaying correctly
3. **Test adding new sources** to ensure writes work

## Support

If you continue to have issues:

1. Check `/docs/DATABASE_SETUP_REQUIRED.md` for additional details
2. Review the error logs carefully
3. Ensure your Supabase service key has the necessary permissions
4. Verify network connectivity to Supabase
