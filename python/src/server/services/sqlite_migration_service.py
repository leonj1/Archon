"""
SQLite-specific migration service that handles database initialization.
"""

import asyncio
import hashlib
import sqlite3
from pathlib import Path
from typing import List, Optional

import aiosqlite
import logfire

from ..repositories.sqlite_repository import SQLiteDatabaseRepository

class SQLiteMigrationService:
    """Service for managing SQLite database migrations and initialization."""
    
    def __init__(self, db_path: str = "archon.db"):
        """
        Initialize SQLite migration service.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.migrations_dir = Path("migration/sqlite")
        
        # Create migrations directory if it doesn't exist
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
    
    async def initialize_database(self) -> bool:
        """
        Initialize the SQLite database with required schema.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Create database file if it doesn't exist
            db_file = Path(self.db_path)
            if not db_file.exists():
                logfire.info(f"Creating new SQLite database: {self.db_path}")
                db_file.touch()
            
            # Apply all migrations
            applied_count = await self.apply_migrations()
            
            logfire.info(f"Database initialized. Applied {applied_count} migrations.")
            return True
            
        except Exception as e:
            logfire.error(f"Failed to initialize SQLite database: {e}")
            return False
    
    async def apply_migrations(self) -> int:
        """
        Apply all pending SQLite migrations.
        
        Returns:
            Number of migrations applied
        """
        applied_count = 0
        
        async with aiosqlite.connect(self.db_path) as conn:
            # Enable foreign keys for this connection
            await conn.execute("PRAGMA foreign_keys = ON")
            
            # Get list of migration files
            migration_files = sorted(self.migrations_dir.glob("*.sql"))
            
            for migration_file in migration_files:
                try:
                    # Read migration content
                    with open(migration_file, 'r', encoding='utf-8') as f:
                        migration_sql = f.read()
                    
                    # Calculate checksum
                    checksum = hashlib.md5(migration_sql.encode()).hexdigest()
                    
                    # Extract migration name
                    migration_name = migration_file.stem
                    
                    # Check if already applied
                    if await self._is_migration_applied(conn, migration_name):
                        logfire.debug(f"Migration {migration_name} already applied, skipping")
                        continue
                    
                    # Apply the migration
                    logfire.info(f"Applying migration: {migration_name}")
                    
                    # SQLite doesn't support multiple statements in one execute
                    # Split by semicolon and execute each statement
                    statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
                    
                    for statement in statements:
                        if statement:
                            await conn.execute(statement)
                    
                    # Record the migration
                    await self._record_migration(conn, migration_name, checksum)
                    
                    await conn.commit()
                    applied_count += 1
                    
                    logfire.info(f"Successfully applied migration: {migration_name}")
                    
                except Exception as e:
                    logfire.error(f"Failed to apply migration {migration_file.name}: {e}")
                    await conn.rollback()
                    raise
        
        return applied_count
    
    async def _is_migration_applied(
        self, conn: aiosqlite.Connection, migration_name: str
    ) -> bool:
        """
        Check if a migration has already been applied.
        
        Args:
            conn: Database connection
            migration_name: Name of the migration
            
        Returns:
            True if applied, False otherwise
        """
        try:
            # First check if migrations table exists
            cursor = await conn.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='archon_migrations'
                """
            )
            if not await cursor.fetchone():
                return False
            
            # Check if this specific migration is recorded
            cursor = await conn.execute(
                "SELECT 1 FROM archon_migrations WHERE migration_name = ?",
                [migration_name]
            )
            return await cursor.fetchone() is not None
            
        except Exception:
            return False
    
    async def _record_migration(
        self, conn: aiosqlite.Connection, migration_name: str, checksum: str
    ) -> None:
        """
        Record a successful migration.
        
        Args:
            conn: Database connection
            migration_name: Name of the migration
            checksum: MD5 checksum of migration content
        """
        import uuid
        from datetime import datetime
        
        await conn.execute(
            """
            INSERT INTO archon_migrations (id, version, migration_name, checksum, applied_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                str(uuid.uuid4()),
                "1.0.0",  # Version can be extracted from migration file name if needed
                migration_name,
                checksum,
                datetime.utcnow().isoformat()
            ]
        )
    
    async def check_database_health(self) -> dict:
        """
        Check SQLite database health and schema status.
        
        Returns:
            Dictionary with health check results
        """
        health_status = {
            "database_exists": False,
            "migrations_table_exists": False,
            "required_tables": {},
            "applied_migrations": [],
            "pending_migrations": [],
            "is_healthy": False
        }
        
        try:
            # Check if database file exists
            db_file = Path(self.db_path)
            health_status["database_exists"] = db_file.exists()
            
            if not health_status["database_exists"]:
                return health_status
            
            async with aiosqlite.connect(self.db_path) as conn:
                # Check for migrations table
                cursor = await conn.execute(
                    """
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='archon_migrations'
                    """
                )
                health_status["migrations_table_exists"] = await cursor.fetchone() is not None
                
                # Check for required tables
                required_tables = [
                    'archon_settings',
                    'archon_sources', 
                    'archon_crawled_pages',
                    'archon_code_examples',
                    'archon_page_metadata',
                    'archon_projects',
                    'archon_tasks',
                    'archon_project_sources',
                    'archon_document_versions'
                ]
                
                for table in required_tables:
                    cursor = await conn.execute(
                        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
                    )
                    health_status["required_tables"][table] = await cursor.fetchone() is not None
                
                # Get applied migrations
                if health_status["migrations_table_exists"]:
                    cursor = await conn.execute(
                        "SELECT migration_name FROM archon_migrations ORDER BY applied_at"
                    )
                    rows = await cursor.fetchall()
                    health_status["applied_migrations"] = [row[0] for row in rows]
                
                # Check for pending migrations
                migration_files = sorted(self.migrations_dir.glob("*.sql"))
                all_migrations = [f.stem for f in migration_files]
                health_status["pending_migrations"] = [
                    m for m in all_migrations 
                    if m not in health_status["applied_migrations"]
                ]
                
                # Overall health check
                health_status["is_healthy"] = (
                    health_status["database_exists"] and
                    health_status["migrations_table_exists"] and
                    all(health_status["required_tables"].values()) and
                    len(health_status["pending_migrations"]) == 0
                )
            
        except Exception as e:
            logfire.error(f"Database health check failed: {e}")
            health_status["error"] = str(e)
        
        return health_status

async def ensure_sqlite_database(db_path: str = "archon.db") -> bool:
    """
    Convenience function to ensure SQLite database is properly initialized.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        True if database is ready, False otherwise
    """
    service = SQLiteMigrationService(db_path)
    
    # Check health first
    health = await service.check_database_health()
    
    if health["is_healthy"]:
        logfire.info("SQLite database is healthy, no initialization needed")
        return True
    
    # Initialize if needed
    logfire.info("SQLite database needs initialization")
    return await service.initialize_database()
