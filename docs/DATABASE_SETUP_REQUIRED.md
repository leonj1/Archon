# DATABASE SETUP REQUIRED

The application is detecting missing database columns (`source_url` and `source_display_name`). 

## Option 1: Enable Auto-Migration (Recommended)

To enable automatic schema migration on startup:

1. **Open Supabase Dashboard** → SQL Editor
2. **Create a new query**
3. **Copy and paste** the contents of `/migration/create_migration_function.sql`
4. **Run the query**

This will create RPC functions that allow the application to automatically apply schema changes on startup.

After creating these functions, simply **restart the application**:
```bash
docker compose restart
```

The application will automatically apply the missing migrations.

## Option 2: Apply Migrations Manually

If you prefer to apply the migrations manually:

1. **Open Supabase Dashboard** → SQL Editor
2. **Create a new query**
3. **Copy and paste** the contents of `/APPLY_MIGRATIONS_NOW.sql`
4. **Run the query**

## Option 3: Full Setup (Complete Reset)

For a complete schema setup:

1. **Open Supabase Dashboard** → SQL Editor
2. **Create a new query**
3. **Copy and paste** the contents of `/migration/complete_setup.sql`
4. **Run the query**

## Verification

After applying any of the above options, you can verify the schema is correct:

```sql
-- Check if columns exist
SELECT 
    column_name,
    data_type 
FROM 
    information_schema.columns 
WHERE 
    table_name = 'archon_sources' 
    AND column_name IN ('source_url', 'source_display_name');
```

You should see both columns listed.

## Why This Is Needed

The application requires these columns to:
- Track the original URL of crawled sources
- Display user-friendly names for sources
- Properly link documents back to their source

Without these columns, the knowledge base features will not work correctly.
