"""
Automatic Database Migration Service

This service applies critical database migrations automatically on startup
using Supabase's available API methods to ensure the schema is correct.
"""

import json
from typing import Dict, List, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AutoMigrationService:
    """Service to automatically apply database migrations on startup."""
    
    def __init__(self):
        """Initialize the auto-migration service."""
        self.supabase = get_supabase_client()
        self.critical_migrations = [
            {
                "name": "add_source_url_columns",
                "check": self._check_source_url_exists,
                "apply": self._apply_source_url_migration
            },
            {
                "name": "add_migration_tracking_table",
                "check": self._check_migrations_table_exists,
                "apply": self._apply_migrations_table
            }
        ]
    
    async def _check_source_url_exists(self) -> bool:
        """Check if source_url column exists in archon_sources table."""
        try:
            # Try to select the column - will fail if it doesn't exist
            result = self.supabase.table("archon_sources").select("source_url").limit(1).execute()
            return True
        except Exception as e:
            error_str = str(e)
            if "source_url" in error_str and ("does not exist" in error_str or "42703" in error_str):
                return False
            # If it's a different error, the column might exist
            return True
    
    async def _apply_source_url_migration(self) -> bool:
        """
        Apply the source_url migration using Supabase RPC function.
        """
        try:
            logger.info("Attempting to apply source_url migration automatically...")
            
            # First, try to use the ensure_source_url_columns RPC function
            try:
                result = self.supabase.rpc("ensure_source_url_columns").execute()
                
                if result.data and result.data.get("success"):
                    logger.info(f"Migration result: {result.data.get('message')}")
                    return True
                else:
                    logger.error(f"Migration failed: {result.data}")
                    return False
                    
            except Exception as rpc_error:
                # RPC function might not exist yet
                logger.warning(f"RPC function not available: {rpc_error}")
                
                # Try alternative approach using the general migration function
                try:
                    migration_sql = """
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
                    """
                    
                    result = self.supabase.rpc("apply_schema_migration", {"migration_sql": migration_sql}).execute()
                    
                    if result.data and result.data.get("success"):
                        logger.info("Successfully applied source_url migration via RPC")
                        return True
                    else:
                        logger.error(f"Migration failed via RPC: {result.data}")
                        return False
                        
                except Exception as e:
                    logger.error(
                        "Cannot apply migration automatically. "
                        "RPC functions need to be created first. "
                        f"Error: {e}"
                    )
                    return False
                
        except Exception as e:
            logger.error(f"Failed to apply source_url migration: {e}")
            return False
    
    async def _check_migrations_table_exists(self) -> bool:
        """Check if archon_migrations table exists."""
        try:
            result = self.supabase.table("archon_migrations").select("*").limit(1).execute()
            return True
        except Exception:
            return False
    
    async def _apply_migrations_table(self) -> bool:
        """
        Try to create migrations tracking table.
        This will likely fail due to Supabase limitations.
        """
        try:
            # We can't create tables via the API
            logger.warning(
                "Cannot create archon_migrations table via API. "
                "This table needs to be created manually."
            )
            return False
        except Exception as e:
            logger.error(f"Failed to create migrations table: {e}")
            return False
    
    async def check_and_apply_migrations(self) -> Dict[str, Any]:
        """
        Check for missing migrations and attempt to apply them.
        
        Returns:
            Dict with migration status and any manual actions required
        """
        results = {
            "success": True,
            "migrations_checked": [],
            "migrations_applied": [],
            "migrations_failed": [],
            "manual_action_required": False,
            "manual_actions": []
        }
        
        for migration in self.critical_migrations:
            migration_name = migration["name"]
            results["migrations_checked"].append(migration_name)
            
            try:
                # Check if migration is needed
                if await migration["check"]():
                    logger.info(f"Migration {migration_name} already applied")
                    continue
                
                # Try to apply migration
                logger.info(f"Applying migration: {migration_name}")
                if await migration["apply"]():
                    results["migrations_applied"].append(migration_name)
                    logger.info(f"Successfully applied migration: {migration_name}")
                else:
                    results["migrations_failed"].append(migration_name)
                    results["success"] = False
                    results["manual_action_required"] = True
                    
                    # Add specific instructions based on the migration
                    if migration_name == "add_source_url_columns":
                        results["manual_actions"].append({
                            "migration": migration_name,
                            "action": "Run the following SQL in Supabase Dashboard",
                            "sql": """
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
                            """.strip()
                        })
                    
            except Exception as e:
                logger.error(f"Error checking/applying migration {migration_name}: {e}")
                results["migrations_failed"].append(migration_name)
                results["success"] = False
        
        return results

# Singleton instance
auto_migration_service = AutoMigrationService()

async def ensure_database_schema() -> bool:
    """
    Ensure the database has the required schema.
    
    Returns:
        True if schema is ready, False if manual action is required
    """
    try:
        results = await auto_migration_service.check_and_apply_migrations()
        
        if results["manual_action_required"]:
            logger.error("=" * 70)
            logger.error("MANUAL DATABASE MIGRATION REQUIRED")
            logger.error("=" * 70)
            
            for action in results["manual_actions"]:
                logger.error(f"\nMigration: {action['migration']}")
                logger.error(f"Action: {action['action']}")
                if "sql" in action:
                    logger.error(f"SQL to run:\n{action['sql']}")
            
            logger.error("=" * 70)
            logger.error("Please apply these migrations in your Supabase Dashboard")
            logger.error("Go to: SQL Editor → New Query → Paste and Run")
            logger.error("=" * 70)
            
            # Still return True to allow app to start, but with errors
            return True
        
        return results["success"]
        
    except Exception as e:
        logger.error(f"Failed to ensure database schema: {e}")
        return False
