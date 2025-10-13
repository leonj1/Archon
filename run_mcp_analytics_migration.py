#!/usr/bin/env python3
"""
Run MCP Analytics Migration for SQLite
"""
import asyncio
import sys
from pathlib import Path

# Add python/src to path
sys.path.insert(0, str(Path(__file__).parent / "python" / "src"))

from server.services.sqlite_migration_service import SQLiteMigrationService

async def main():
    """Run the MCP analytics migration."""
    db_path = "data/archon.db"

    print(f"🔍 Checking database: {db_path}")

    # Initialize migration service
    service = SQLiteMigrationService(db_path)

    # Check current health
    health = await service.check_database_health()

    print("\n📊 Database Health Status:")
    print(f"  Database exists: {health['database_exists']}")
    print(f"  Migrations table: {health['migrations_table_exists']}")
    print(f"  Applied migrations: {len(health['applied_migrations'])}")
    print(f"  Pending migrations: {len(health['pending_migrations'])}")

    if health['pending_migrations']:
        print(f"\n📝 Pending migrations to apply:")
        for migration in health['pending_migrations']:
            print(f"    - {migration}")

    # Apply pending migrations
    if health['pending_migrations']:
        print("\n🚀 Applying pending migrations...")
        applied_count = await service.apply_migrations()
        print(f"✅ Successfully applied {applied_count} migration(s)")
    else:
        print("\n✅ No pending migrations - database is up to date")

    # Check health again
    health = await service.check_database_health()

    if health['is_healthy']:
        print("\n🎉 Database is healthy and ready!")
    else:
        print("\n⚠️  Database health check failed")
        print(f"Missing tables: {[k for k, v in health['required_tables'].items() if not v]}")

    # Verify MCP analytics tables exist
    import aiosqlite
    async with aiosqlite.connect(db_path) as conn:
        cursor = await conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name LIKE 'archon_mcp_usage%'
            ORDER BY name
        """)
        mcp_tables = await cursor.fetchall()

        if mcp_tables:
            print("\n📊 MCP Analytics Tables:")
            for table in mcp_tables:
                print(f"    ✓ {table[0]}")
        else:
            print("\n⚠️  No MCP analytics tables found")

if __name__ == "__main__":
    asyncio.run(main())
