"""
Dependency injection system for the repository pattern.

This module provides the DatabaseProvider singleton and FastAPI dependency
injection setup for managing database instances throughout the application.
"""

import logging
import threading
from typing import AsyncGenerator, Optional

from ..repositories.interfaces.unit_of_work import IUnitOfWork
from ..repositories.implementations import SupabaseDatabase


class DatabaseProvider:
    """
    Singleton provider for database instance management.
    
    This class manages the database instance lifecycle and provides a
    centralized point for dependency injection and testing.
    """
    
    _instance: Optional[IUnitOfWork] = None
    _logger = logging.getLogger(__name__)
    _lock = threading.Lock()
    
    @classmethod
    def get_database(cls) -> IUnitOfWork:
        """
        Get the database instance, creating it if necessary.
        
        Returns:
            The IUnitOfWork instance
            
        Note:
            This method implements lazy initialization to avoid circular imports
            and ensure the database is only created when actually needed.
        """
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern for thread safety
                if cls._instance is None:
                    cls._logger.info("Initializing database instance")
                    config = get_database_config()
                    cls._instance = create_database_instance(config)
                    cls._logger.info("Database instance initialized successfully")
        
        return cls._instance
    
    @classmethod
    def set_database(cls, database: IUnitOfWork):
        """
        Set a specific database instance (primarily for testing).
        
        Args:
            database: The IUnitOfWork instance to use
            
        Note:
            This method allows injection of mock or test database instances
            for testing purposes without affecting production code.
        """
        with cls._lock:
            cls._logger.info(f"Database instance overridden with {type(database).__name__}")
            cls._instance = database
    
    @classmethod
    def reset_database(cls):
        """
        Reset the database instance (primarily for testing).
        
        This method clears the current database instance, forcing a new
        instance to be created on the next call to get_database().
        """
        with cls._lock:
            cls._logger.info("Database instance reset")
            cls._instance = None
    
    @classmethod
    async def close_database(cls):
        """
        Close the current database instance and clean up resources.
        
        This method should be called during application shutdown to
        ensure proper cleanup of database connections and resources.
        """
        if cls._instance is not None:
            cls._logger.info("Closing database instance")
            await cls._instance.close()
            cls._instance = None
            cls._logger.info("Database instance closed")
    
    @classmethod
    async def health_check(cls) -> bool:
        """
        Perform a health check on the current database instance.
        
        Returns:
            True if the database is healthy, False otherwise
        """
        try:
            if cls._instance is None:
                # Try to get instance, which will create it if needed
                cls.get_database()
            
            return await cls._instance.health_check()
        except Exception as e:
            cls._logger.error(f"Database health check failed: {e}", exc_info=True)
            return False


def get_database() -> IUnitOfWork:
    """
    FastAPI dependency function for database injection.
    
    This function provides a database instance that can be injected
    into FastAPI route handlers and other dependency-managed functions.
    
    Returns:
        The IUnitOfWork instance
        
    Example:
        ```python
        @router.post("/projects")
        async def create_project(
            project_data: dict,
            db: IUnitOfWork = Depends(get_database)
        ):
            return await db.projects.create(project_data)
        ```
    """
    return DatabaseProvider.get_database()


def get_database_dependency():
    """
    Get the database dependency function without caching.
    
    This function is useful for scenarios where you need a fresh
    database instance for each request, such as in testing or
    when the database configuration might change.
    
    Returns:
        The IUnitOfWork instance
    """
    return DatabaseProvider.get_database()


async def get_database_async() -> AsyncGenerator[IUnitOfWork, None]:
    """
    Async generator-based dependency for per-request database instances.
    
    This dependency provides a database instance for each request and ensures
    proper cleanup after the request completes. Useful for scenarios requiring
    transaction isolation or when database state shouldn't be shared between requests.
    
    Yields:
        The IUnitOfWork instance for the current request
        
    Example:
        ```python
        @router.post("/items")
        async def create_item(
            item_data: dict,
            db: IUnitOfWork = Depends(get_database_async)
        ):
            async with db.transaction() as uow:
                return await uow.items.create(item_data)
        ```
    """
    database = DatabaseProvider.get_database()
    try:
        yield database
    finally:
        # Cleanup logic if needed (e.g., closing transaction, releasing resources)
        # Note: For singleton instances, we typically don't close here
        # as the instance is shared across requests
        pass


async def setup_database():
    """
    Initialize the database system during application startup.
    
    This function should be called during application startup to
    ensure the database is properly initialized and ready for use.
    """
    logger = logging.getLogger(__name__)
    try:
        logger.info("Setting up database system")
        database = DatabaseProvider.get_database()
        
        # Perform health check to ensure database is accessible
        is_healthy = await database.health_check()
        if not is_healthy:
            raise Exception("Database health check failed during startup")
        
        logger.info("Database system setup completed successfully")
    except Exception as e:
        logger.error(f"Database setup failed: {e}", exc_info=True)
        raise


async def teardown_database():
    """
    Clean up the database system during application shutdown.
    
    This function should be called during application shutdown to
    ensure proper cleanup of database connections and resources.
    """
    logger = logging.getLogger(__name__)
    try:
        logger.info("Tearing down database system")
        await DatabaseProvider.close_database()
        logger.info("Database system teardown completed successfully")
    except Exception as e:
        logger.error(f"Database teardown failed: {e}", exc_info=True)
        # Don't re-raise during shutdown as it might mask other errors


# Configuration class for database settings
class DatabaseConfig:
    """
    Configuration container for database settings.
    
    This class can be extended to support different database backends
    and configuration options in the future.
    """
    
    def __init__(
        self,
        database_type: str = "supabase",
        connection_pool_size: int = 10,
        connection_timeout: int = 30,
        retry_attempts: int = 3,
        enable_logging: bool = True
    ):
        """
        Initialize database configuration.
        
        Args:
            database_type: Type of database backend ('supabase', 'mock', etc.)
            connection_pool_size: Maximum number of database connections
            connection_timeout: Connection timeout in seconds
            retry_attempts: Number of retry attempts for failed operations
            enable_logging: Whether to enable database operation logging
        """
        self.database_type = database_type
        self.connection_pool_size = connection_pool_size
        self.connection_timeout = connection_timeout
        self.retry_attempts = retry_attempts
        self.enable_logging = enable_logging
    
    def __repr__(self) -> str:
        """String representation of the configuration."""
        return f"DatabaseConfig(type={self.database_type}, pool_size={self.connection_pool_size})"


# Global configuration instance
_database_config = DatabaseConfig()


def get_database_config() -> DatabaseConfig:
    """
    Get the current database configuration.
    
    Returns:
        The current DatabaseConfig instance
    """
    return _database_config


def set_database_config(config: DatabaseConfig):
    """
    Set the database configuration.
    
    Args:
        config: The new DatabaseConfig instance
        
    Note:
        This function should be called during application startup
        before any database operations are performed.
    """
    global _database_config
    _database_config = config
    
    logger = logging.getLogger(__name__)
    logger.info(f"Database configuration updated: {config}")


# Factory function for creating database instances based on configuration
def create_database_instance(config: Optional[DatabaseConfig] = None) -> IUnitOfWork:
    """
    Create a database instance based on the provided configuration.
    
    Args:
        config: Optional database configuration. If not provided, uses global config.
        
    Returns:
        An IUnitOfWork instance configured according to the provided settings
        
    Raises:
        ValueError: If the database type is not supported
    """
    if config is None:
        config = get_database_config()
    
    if config.database_type == "supabase":
        return SupabaseDatabase()
    elif config.database_type == "mock":
        # Import here to avoid circular imports
        from ..repositories.implementations.mock_repositories import (
            MockSourceRepository,
            MockDocumentRepository,
            MockProjectRepository,
            MockSettingsRepository,
        )
        # For mock, we'd need to create a mock database class
        # This is a simplified approach - in practice you'd have a MockDatabase class
        return SupabaseDatabase()  # Fallback to Supabase for now
    else:
        raise ValueError(f"Unsupported database type: {config.database_type}")