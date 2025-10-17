"""
Apply MCP Usage Tracking Migration

This script applies the 002_mcp_usage_tracking.sql migration to the SQLite database.
Run this script to add the necessary tables for MCP analytics.

Usage:
    python -m src.server.scripts.apply_mcp_migration
"""

import asyncio
import os
import sys
from pathlib import Path

import aiosqlite
import logfire


async def apply_migration():
    """Apply the MCP usage tracking migration to the database."""
    # Get database path from environment or use default
    db_path = os.getenv("SQLITE_PATH") or os.getenv("ARCHON_SQLITE_PATH") or "/data/archon.db"

    logfire.info(f"Applying MCP usage tracking migration to database: {db_path}")

    # Get migration file path
    migration_file = Path(__file__).parent.parent.parent.parent.parent / "migration" / "sqlite" / "002_mcp_usage_tracking.sql"

    if not migration_file.exists():
        logfire.error(f"Migration file not found: {migration_file}")
        sys.exit(1)

    # Read migration SQL
    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    logfire.info(f"Read migration file: {migration_file}")

    # Apply migration
    try:
        async with aiosqlite.connect(db_path) as conn:
            # Execute migration statements
            statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]

            for i, statement in enumerate(statements, 1):
                try:
                    logfire.debug(f"Executing statement {i}/{len(statements)}")
                    await conn.execute(statement)
                    await conn.commit()
                except Exception as e:
                    logfire.error(f"Error executing statement {i}: {e}")
                    logfire.error(f"Statement: {statement[:100]}...")
                    raise

            logfire.info("✓ Migration applied successfully")

            # Verify tables were created
            cursor = await conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name LIKE 'archon_mcp_usage_%'
                ORDER BY name
            """)
            tables = await cursor.fetchall()

            if tables:
                logfire.info("✓ Created tables:")
                for table in tables:
                    logfire.info(f"  - {table[0]}")
            else:
                logfire.warning("⚠ No MCP usage tables found after migration")

            # Verify triggers were created
            cursor = await conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='trigger' AND name LIKE 'trg_mcp_%'
                ORDER BY name
            """)
            triggers = await cursor.fetchall()

            if triggers:
                logfire.info("✓ Created triggers:")
                for trigger in triggers:
                    logfire.info(f"  - {trigger[0]}")

    except Exception as e:
        logfire.error(f"Failed to apply migration: {e}", exc_info=True)
        sys.exit(1)

    logfire.info("=" * 50)
    logfire.info("MCP Usage Tracking is now enabled!")
    logfire.info("Analytics will be available at: http://localhost:3737/settings")
    logfire.info("=" * 50)


if __name__ == "__main__":
    asyncio.run(apply_migration())
