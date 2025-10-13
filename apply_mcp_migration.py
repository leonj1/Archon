#!/usr/bin/env python3
"""
Directly apply MCP Analytics migration to SQLite
"""
import asyncio
import sqlite3
from pathlib import Path
import hashlib
import uuid
from datetime import datetime

async def main():
    """Apply the MCP analytics migration directly."""
    db_path = "data/archon.db"
    migration_file = Path("migration/sqlite/002_add_mcp_usage_tracking.sql")

    print(f"🔍 Database: {db_path}")
    print(f"📝 Migration: {migration_file}")

    # Check if already applied
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if already applied
    cursor.execute("""
        SELECT 1 FROM archon_migrations
        WHERE migration_name = '002_add_mcp_usage_tracking'
    """)

    if cursor.fetchone():
        print("\n✅ Migration already applied - skipping")
        conn.close()
        return

    # Read migration SQL
    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    # Calculate checksum
    checksum = hashlib.md5(migration_sql.encode()).hexdigest()

    print("\n🚀 Applying migration...")

    try:
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")

        # Split statements and execute
        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]

        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    conn.execute(statement)
                    print(f"   ✓ Statement {i}/{len(statements)}")
                except Exception as e:
                    print(f"   ✗ Statement {i} failed: {e}")
                    print(f"      SQL: {statement[:100]}...")

        # Record the migration
        conn.execute("""
            INSERT INTO archon_migrations (id, version, migration_name, checksum, applied_at)
            VALUES (?, ?, ?, ?, ?)
        """, [
            str(uuid.uuid4()),
            "0.2.0",
            "002_add_mcp_usage_tracking",
            checksum,
            datetime.utcnow().isoformat()
        ])

        conn.commit()
        print("\n✅ Migration applied successfully!")

        # Verify tables created
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name LIKE 'archon_mcp_usage%'
            ORDER BY name
        """)
        tables = cursor.fetchall()

        print("\n📊 MCP Analytics Tables Created:")
        for table in tables:
            print(f"    ✓ {table[0]}")

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='trigger' AND name LIKE 'trg_mcp_usage%'
            ORDER BY name
        """)
        triggers = cursor.fetchall()

        print("\n⚡ Triggers Created:")
        for trigger in triggers:
            print(f"    ✓ {trigger[0]}")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    asyncio.run(main())
