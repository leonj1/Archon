"""
Client Manager Service

Manages database and API client connections.
Provides backward compatibility while transitioning to DAL.
"""

import os
import re
from typing import Optional

from supabase import Client, create_client

from ..config.logfire_config import search_logger
from ..dal import ConnectionManager, DatabaseType
from ..dal.adapters import SupabaseAdapter, MySQLAdapter, PostgreSQLAdapter

# Global connection manager instance
_connection_manager: Optional[ConnectionManager] = None


def get_supabase_client() -> Client:
    """
    Get a Supabase client instance.
    
    This function maintains backward compatibility with existing code.
    New code should use get_connection_manager() instead.

    Returns:
        Supabase client instance
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables"
        )

    try:
        # Let Supabase handle connection pooling internally
        client = create_client(url, key)

        # Extract project ID from URL for logging purposes only
        match = re.match(r"https://([^.]+)\.supabase\.co", url)
        if match:
            project_id = match.group(1)
            search_logger.info(f"Supabase client initialized - project_id={project_id}")

        return client
    except Exception as e:
        search_logger.error(f"Failed to create Supabase client: {e}")
        raise


def get_connection_manager() -> ConnectionManager:
    """
    Get the connection manager for database abstraction layer.
    
    This is the preferred method for new code.
    
    Returns:
        ConnectionManager instance
    """
    global _connection_manager
    if not _connection_manager:
        # Detect database type from environment
        db_type = os.getenv("DATABASE_TYPE", "supabase").lower()
        
        # Register appropriate adapter based on DATABASE_TYPE
        if db_type == "mysql":
            ConnectionManager.register_adapter(DatabaseType.MYSQL, MySQLAdapter)
            search_logger.info("Registering MySQL adapter")
        elif db_type == "postgresql":
            # Register PostgreSQL adapter
            ConnectionManager.register_adapter(DatabaseType.POSTGRESQL, PostgreSQLAdapter)
            search_logger.info("Registering PostgreSQL adapter")
        else:
            # Default to Supabase for backward compatibility
            ConnectionManager.register_adapter(DatabaseType.SUPABASE, SupabaseAdapter)
            search_logger.info("Registering Supabase adapter (default)")
        
        # Create connection manager from environment
        _connection_manager = ConnectionManager.from_env()
        
        search_logger.info(f"Connection manager initialized with {db_type} adapter")
    
    return _connection_manager


async def initialize_database():
    """
    Initialize database connections.
    Should be called on application startup.
    """
    manager = get_connection_manager()
    await manager.initialize()
    search_logger.info("Database connections initialized")


async def close_database():
    """
    Close all database connections.
    Should be called on application shutdown.
    """
    global _connection_manager
    if _connection_manager:
        await _connection_manager.close()
        _connection_manager = None
        search_logger.info("Database connections closed")
