# MCP Usage Analytics Migration Instructions

## Problem
The MCP Usage Analytics feature requires database tables that don't exist yet:
- `archon_mcp_usage_events`
- `archon_mcp_usage_hourly` (materialized view)
- `archon_mcp_usage_daily` (materialized view)

## Solution: Manual SQL Execution via Supabase Dashboard

Since direct PostgreSQL connection is not available, you need to run the migration SQL manually:

### Step-by-Step Instructions

1. **Open Supabase Dashboard**
   - Go to: https://supabase.com/dashboard
   - Select your project: `myfibwvuphkskjrzbaam`

2. **Navigate to SQL Editor**
   - Click "SQL Editor" in the left sidebar
   - Click "New Query" button

3. **Copy the Migration SQL**
   - Open the file: `migration/0.2.0/001_add_mcp_usage_tracking.sql`
   - Copy the entire contents (295 lines)

4. **Execute the Migration**
   - Paste the SQL into the SQL Editor
   - Click "Run" or press `Ctrl/Cmd + Enter`
   - Wait for execution to complete

5. **Verify Success**
   - You should see messages like:
     - Tables created
     - Indexes created
     - Materialized views created
     - Functions created

6. **Refresh Your Archon UI**
   - Go back to Settings → MCP Usage Analytics
   - The analytics dashboard should now load properly

## What the Migration Creates

- **Main Table**: `archon_mcp_usage_events` - Stores all MCP tool invocations
- **Hourly View**: `archon_mcp_usage_hourly` - Pre-aggregated hourly statistics
- **Daily View**: `archon_mcp_usage_daily` - Pre-aggregated daily statistics
- **Functions**: Cleanup and refresh functions for maintenance
- **Policies**: Row-level security policies for access control

## Expected Duration
- Migration execution: ~5-10 seconds
- First data population: Immediate (as MCP tools are used)
- View refresh: Automatic every 15 minutes

## Troubleshooting

### If you get permission errors:
- Ensure you're logged in to the correct Supabase project
- Verify you have admin access to the project

### If tables already exist:
- The migration uses `IF NOT EXISTS` clauses
- Safe to re-run if needed

### If migration fails partway:
- Note which statement failed
- You can run the remaining statements individually
- Most statements are idempotent (safe to re-run)

## Alternative: SQL Command Line

If you prefer command line, you can also use the Supabase CLI:

```bash
# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref myfibwvuphkskjrzbaam

# Run the migration
supabase db push --file migration/0.2.0/001_add_mcp_usage_tracking.sql
```

## After Migration

The analytics will start capturing data immediately. You can:
- View hourly/daily usage in the Settings page
- See which MCP tools are most used
- Monitor response times and error rates
- Track unique sessions and categories

## Need Help?

If you encounter issues:
1. Check the Supabase dashboard logs
2. Verify network connectivity to Supabase
3. Ensure SUPABASE_SERVICE_KEY has sufficient permissions
4. Contact support with error messages
