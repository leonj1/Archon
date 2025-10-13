#!/usr/bin/env python3
"""
Run MCP Usage Analytics Migration

This script runs the MCP usage tracking migration against the Supabase PostgreSQL database.
Uses asyncpg for direct database access.
"""
import asyncio
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import asyncpg


async def run_migration():
    """Execute the MCP usage analytics migration."""
    print("🚀 Starting MCP usage analytics migration...")

    # Read migration SQL file
    migration_file = Path(__file__).parent / "0.2.0" / "001_add_mcp_usage_tracking.sql"

    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        sys.exit(1)

    print(f"📄 Reading migration file: {migration_file}")
    with open(migration_file, "r") as f:
        sql = f.read()

    # Get Supabase connection details from environment
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        sys.exit(1)

    # Parse project ID from Supabase URL
    # Format: https://xxxxx.supabase.co
    parsed = urlparse(supabase_url)
    project_id = parsed.hostname.split('.')[0] if parsed.hostname else None

    if not project_id:
        print(f"❌ Could not parse project ID from SUPABASE_URL: {supabase_url}")
        sys.exit(1)

    # Construct PostgreSQL connection string for Supabase
    # Supabase uses: db.<project-id>.supabase.co:5432
    # Password is the service role key (or database password if available)
    db_password = os.getenv("SUPABASE_DB_PASSWORD", supabase_key)
    db_host = os.getenv("SUPABASE_DB_HOST", f"db.{project_id}.supabase.co")
    db_port = os.getenv("SUPABASE_DB_PORT", "5432")
    db_name = os.getenv("SUPABASE_DB_NAME", "postgres")
    db_user = os.getenv("SUPABASE_DB_USER", "postgres")

    print(f"\n📡 Connecting to PostgreSQL:")
    print(f"   Host: {db_host}")
    print(f"   Port: {db_port}")
    print(f"   Database: {db_name}")
    print(f"   User: {db_user}")

    try:
        # Connect to PostgreSQL
        conn = await asyncpg.connect(
            host=db_host,
            port=int(db_port),
            database=db_name,
            user=db_user,
            password=db_password,
            ssl='require'  # Supabase requires SSL
        )
        print("✅ Connected to Supabase PostgreSQL")

        # Execute the migration SQL
        print("\n⚙️  Executing migration SQL...")

        # Execute the entire SQL script
        # asyncpg can handle multi-statement SQL
        await conn.execute(sql)

        print("✅ Migration executed successfully!")

        # Verify tables were created
        print("\n🔍 Verifying migration...")

        # Check if main table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'archon_mcp_usage_events'
            );
        """)

        if table_exists:
            print("   ✓ Table 'archon_mcp_usage_events' created")

            # Check row count
            count = await conn.fetchval("SELECT COUNT(*) FROM archon_mcp_usage_events")
            print(f"   ✓ Current row count: {count}")
        else:
            print("   ✗ Table 'archon_mcp_usage_events' not found")

        # Check if materialized views exist
        views = await conn.fetch("""
            SELECT matviewname FROM pg_matviews
            WHERE schemaname = 'public'
            AND matviewname LIKE 'archon_mcp_usage_%'
        """)

        if views:
            print(f"   ✓ Materialized views created: {', '.join(v['matviewname'] for v in views)}")
        else:
            print("   ✗ No materialized views found")

        # Check if migration was recorded
        migration_recorded = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM archon_migrations
                WHERE version = '0.2.0'
                AND migration_name = '001_add_mcp_usage_tracking'
            );
        """)

        if migration_recorded:
            print("   ✓ Migration recorded in archon_migrations table")
        else:
            print("   ⚠️  Migration not recorded in archon_migrations table")

        # Close connection
        await conn.close()
        print("\n🎉 Migration completed successfully!")

    except asyncpg.exceptions.PostgresError as e:
        print(f"\n❌ PostgreSQL error: {e}")
        print(f"   Error code: {e.sqlstate}")
        sys.exit(1)
    except ConnectionError as e:
        print(f"\n❌ Connection error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Check if SUPABASE_DB_PASSWORD is set (different from SUPABASE_SERVICE_KEY)")
        print("   2. Verify network access to Supabase database")
        print("   3. Check if IP is allowlisted in Supabase dashboard")
        print("   4. Try using Supabase SQL Editor directly")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_migration())
