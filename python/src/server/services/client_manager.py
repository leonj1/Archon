"""
Client Manager Service

Manages database connections, repository factory, and dependency injection.
Provides both legacy API client access and modern repository-based data access.

Key Features:
- Legacy Supabase client access (get_supabase_client)
- Modern repository pattern access (get_repository_provider)
- Dependency injection container (get_dependency_container)
- Configuration-based database selection via DATABASE_TYPE environment variable
- Comprehensive health checking for all services

Database Selection:
Set DATABASE_TYPE environment variable to one of: supabase, postgresql, mysql, sqlite
Default: supabase (for backward compatibility)
"""

import os
import re
from typing import Optional

from supabase import Client, create_client

from ..config.logfire_config import search_logger
from ..dal import (
    ConnectionManager,
    DatabaseType,
    DependencyContainer,
    RepositoryProvider,
    get_container,
    initialize_dependencies,
    close_dependencies,
)
from ..dal.adapters import SupabaseAdapter, MySQLAdapter, PostgreSQLAdapter

# Global instances
_connection_manager: Optional[ConnectionManager] = None
_dependency_container: Optional[DependencyContainer] = None
_repository_provider: Optional[RepositoryProvider] = None


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


def get_repository_provider() -> RepositoryProvider:
    """
    Get the repository provider for dependency injection.
    
    This is the preferred method for accessing repositories.
    
    Returns:
        RepositoryProvider instance
        
    Raises:
        RuntimeError: If dependency container is not initialized
    """
    global _repository_provider
    if not _repository_provider:
        # Initialize dependencies automatically if not done
        import asyncio
        asyncio.create_task(_ensure_dependencies_initialized())
        
        # Get the container
        container = get_container()
        if not container:
            raise RuntimeError("Dependency container not available")
        
        _repository_provider = container.get_repository_provider()
    
    return _repository_provider


async def _ensure_dependencies_initialized():
    """Ensure dependencies are initialized (internal helper)."""
    global _dependency_container
    if not _dependency_container:
        _dependency_container = await initialize_dependencies()


def get_dependency_container() -> DependencyContainer:
    """
    Get the dependency injection container.
    
    Returns:
        DependencyContainer instance
    """
    global _dependency_container
    if not _dependency_container:
        _dependency_container = get_container()
        
        # Configure with existing connection manager if available
        if _connection_manager:
            _dependency_container.configure_database(_connection_manager)
    
    return _dependency_container


async def initialize_database():
    """
    Initialize database connections and dependency injection.
    Should be called on application startup.
    """
    global _dependency_container, _repository_provider
    
    try:
        # Initialize the dependency container and all services
        _dependency_container = await initialize_dependencies()
        _repository_provider = _dependency_container.get_repository_provider()
        
        # Also initialize legacy connection manager for backward compatibility
        manager = get_connection_manager()
        await manager.initialize()
        
        search_logger.info("Database connections and repositories initialized successfully")
        
    except Exception as e:
        search_logger.error(f"Failed to initialize database services: {e}")
        raise


async def close_database():
    """
    Close all database connections and cleanup dependencies.
    Should be called on application shutdown.
    """
    global _connection_manager, _dependency_container, _repository_provider
    
    try:
        # Close dependency container first
        if _dependency_container:
            await _dependency_container.close()
            _dependency_container = None
        
        # Close legacy connection manager
        if _connection_manager:
            await _connection_manager.close()
            _connection_manager = None
        
        # Clear repository provider
        _repository_provider = None
        
        # Close global dependencies
        await close_dependencies()
        
        search_logger.info("Database connections and dependencies closed")
        
    except Exception as e:
        search_logger.error(f"Error during database cleanup: {e}")
        raise


async def get_health_status() -> dict:
    """
    Get comprehensive health status of all database services.
    
    Returns:
        Dictionary containing health status of all components
    """
    status = {
        "connection_manager": None,
        "dependency_container": None,
        "repository_provider": "not_initialized",
        "legacy_supabase": None,
    }
    
    # Check legacy connection manager
    if _connection_manager:
        try:
            status["connection_manager"] = await _connection_manager.health_check()
        except Exception as e:
            status["connection_manager"] = {"error": str(e)}
    
    # Check dependency container
    if _dependency_container:
        try:
            status["dependency_container"] = await _dependency_container.health_check()
        except Exception as e:
            status["dependency_container"] = {"error": str(e)}
    
    # Check repository provider
    if _repository_provider:
        status["repository_provider"] = "initialized"
    
    # Check legacy Supabase client
    try:
        get_supabase_client()
        status["legacy_supabase"] = {"healthy": True}
    except Exception as e:
        status["legacy_supabase"] = {"healthy": False, "error": str(e)}
    
    return status
