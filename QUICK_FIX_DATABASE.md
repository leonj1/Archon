# 🔴 QUICK FIX - DATABASE ERROR

Your database is missing the `source_url` column. Fix it in 2 minutes:

## Steps:

### 1. Open Supabase Dashboard
Go to: https://app.supabase.com → Your Project → **SQL Editor**

### 2. Run This SQL
Click "New Query", paste ALL of this, then click "Run":

```sql
ALTER TABLE archon_sources 
ADD COLUMN IF NOT EXISTS source_url TEXT,
ADD COLUMN IF NOT EXISTS source_display_name TEXT;

CREATE INDEX IF NOT EXISTS idx_archon_sources_url ON archon_sources(source_url);
CREATE INDEX IF NOT EXISTS idx_archon_sources_display_name ON archon_sources(source_display_name);

UPDATE archon_sources 
SET 
    source_url = COALESCE(source_url, source_id),
    source_display_name = COALESCE(source_display_name, source_id)
WHERE source_url IS NULL OR source_display_name IS NULL;
```

### 3. Restart Containers
```bash
docker compose restart
```

## That's it! ✅

The error should be gone after these 3 steps.

---

## Alternative: Enable Auto-Migration (Optional)

To prevent this in the future, also run `/migration/create_migration_function.sql` in Supabase.
This enables automatic schema fixes on startup.
