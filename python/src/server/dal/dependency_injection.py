"""
Dependency Injection Container for Database Abstraction Layer

Provides centralized registration and resolution of repository dependencies.
Implements dependency injection pattern for clean architecture.
"""

import os
from typing import Dict, Type, Any, Optional
from enum import Enum

from .connection_manager import ConnectionManager, DatabaseType
from .repository_factory import RepositoryFactory, initialize_repository_factory
from .repositories.interfaces.base_repository import BaseRepository
from .repositories.interfaces.project_repository_interface import IProjectRepository
from .repositories.interfaces.task_repository_interface import ITaskRepository
from .repositories.interfaces.knowledge_repository_interface import IKnowledgeRepository
from .repositories.interfaces.settings_repository_interface import ISettingsRepository
from .repositories.interfaces.search_repository_interface import ISearchRepository

from ..config.logfire_config import search_logger


class RepositoryProvider:
    """
    Provides repository instances with dependency injection.
    Acts as a service locator for repository dependencies.
    """
    
    def __init__(self, repository_factory: RepositoryFactory):
        """
        Initialize repository provider with factory.
        
        Args:
            repository_factory: Repository factory instance
        """
        self._factory = repository_factory
    
    async def get_project_repository(self) -> IProjectRepository:
        """Get project repository instance."""
        return await self._factory.get_project_repository()
    
    async def get_task_repository(self) -> ITaskRepository:
        """Get task repository instance."""
        return await self._factory.get_task_repository()
    
    async def get_knowledge_repository(self) -> IKnowledgeRepository:
        """Get knowledge repository instance."""
        return await self._factory.get_knowledge_repository()
    
    async def get_settings_repository(self) -> ISettingsRepository:
        """Get settings repository instance."""
        return await self._factory.get_settings_repository()
    
    async def get_search_repository(self) -> ISearchRepository:
        """Get search repository instance."""
        return await self._factory.get_search_repository()
    
    @property
    def factory(self) -> RepositoryFactory:
        """Get the underlying repository factory."""
        return self._factory


class DependencyContainer:
    """
    Dependency injection container for managing service registration and resolution.
    Provides centralized configuration of all application dependencies.
    """
    
    def __init__(self):
        """Initialize dependency container."""
        self._connection_manager: Optional[ConnectionManager] = None
        self._repository_factory: Optional[RepositoryFactory] = None
        self._repository_provider: Optional[RepositoryProvider] = None
        self._initialized = False
    
    def configure_database(self, connection_manager: ConnectionManager) -> None:
        """
        Configure database connection manager.
        
        Args:
            connection_manager: Database connection manager instance
        """
        self._connection_manager = connection_manager
        search_logger.info("Database connection manager configured in DI container")
    
    def register_repository_implementations(self) -> None:
        """
        Register all repository implementations based on current database configuration.
        This method will dynamically load and register implementations.
        """
        if not self._connection_manager or not self._connection_manager.primary_pool:
            raise RuntimeError("Connection manager must be configured before registering repositories")
        
        if not self._repository_factory:
            self._repository_factory = initialize_repository_factory(self._connection_manager)
        
        # Get current database type
        db_type = self._connection_manager.primary_pool.config.database_type
        search_logger.info(f"Registering repository implementations for {db_type.value}")
        
        # Register repository implementations based on database type
        self._register_implementations_for_database(db_type)
        
        search_logger.info("Repository implementations registered successfully")
    
    def _register_implementations_for_database(self, database_type: DatabaseType) -> None:
        """
        Register repository implementations for a specific database type.
        
        Args:
            database_type: Target database type
        """
        # Try to import and register database-specific implementations
        try:
            if database_type == DatabaseType.SUPABASE:
                self._register_supabase_implementations()
            elif database_type == DatabaseType.POSTGRESQL:
                self._register_postgresql_implementations()
            elif database_type == DatabaseType.MYSQL:
                self._register_mysql_implementations()
            elif database_type == DatabaseType.SQLITE:
                self._register_sqlite_implementations()
            else:
                search_logger.warning(f"No specific implementations for {database_type.value}, using defaults")
                self._register_default_implementations()
        except ImportError as e:
            search_logger.warning(f"Failed to import {database_type.value} implementations: {e}")
            search_logger.info("Falling back to default implementations")
            self._register_default_implementations()
    
    def _register_supabase_implementations(self) -> None:
        """Register Supabase-specific repository implementations."""
        try:
            # Import Supabase repository implementations
            from .repositories.supabase.project_repository import SupabaseProjectRepository
            from .repositories.supabase.task_repository import SupabaseTaskRepository
            from .repositories.supabase.knowledge_repository import SupabaseKnowledgeRepository
            from .repositories.supabase.settings_repository import SupabaseSettingsRepository
            from .repositories.supabase.search_repository import SupabaseSearchRepository
            
            # Register implementations
            self._repository_factory.register_repository(
                IProjectRepository, DatabaseType.SUPABASE, SupabaseProjectRepository
            )
            self._repository_factory.register_repository(
                ITaskRepository, DatabaseType.SUPABASE, SupabaseTaskRepository
            )
            self._repository_factory.register_repository(
                IKnowledgeRepository, DatabaseType.SUPABASE, SupabaseKnowledgeRepository
            )
            self._repository_factory.register_repository(
                ISettingsRepository, DatabaseType.SUPABASE, SupabaseSettingsRepository
            )
            self._repository_factory.register_repository(
                ISearchRepository, DatabaseType.SUPABASE, SupabaseSearchRepository
            )
            
            search_logger.info("Supabase repository implementations registered")
            
        except ImportError as e:
            search_logger.warning(f"Supabase implementations not available: {e}")
            self._register_default_implementations()
    
    def _register_postgresql_implementations(self) -> None:
        """Register PostgreSQL-specific repository implementations."""
        try:
            # Import PostgreSQL repository implementations
            from .repositories.postgresql.project_repository import PostgreSQLProjectRepository
            from .repositories.postgresql.task_repository import PostgreSQLTaskRepository
            from .repositories.postgresql.knowledge_repository import PostgreSQLKnowledgeRepository
            from .repositories.postgresql.settings_repository import PostgreSQLSettingsRepository
            from .repositories.postgresql.search_repository import PostgreSQLSearchRepository
            
            # Register implementations
            self._repository_factory.register_repository(
                IProjectRepository, DatabaseType.POSTGRESQL, PostgreSQLProjectRepository
            )
            self._repository_factory.register_repository(
                ITaskRepository, DatabaseType.POSTGRESQL, PostgreSQLTaskRepository
            )
            self._repository_factory.register_repository(
                IKnowledgeRepository, DatabaseType.POSTGRESQL, PostgreSQLKnowledgeRepository
            )
            self._repository_factory.register_repository(
                ISettingsRepository, DatabaseType.POSTGRESQL, PostgreSQLSettingsRepository
            )
            self._repository_factory.register_repository(
                ISearchRepository, DatabaseType.POSTGRESQL, PostgreSQLSearchRepository
            )
            
            search_logger.info("PostgreSQL repository implementations registered")
            
        except ImportError as e:
            search_logger.warning(f"PostgreSQL implementations not available: {e}")
            self._register_default_implementations()
    
    def _register_mysql_implementations(self) -> None:
        """Register MySQL-specific repository implementations."""
        try:
            # Import MySQL repository implementations
            from .repositories.mysql.project_repository import MySQLProjectRepository
            from .repositories.mysql.task_repository import MySQLTaskRepository
            from .repositories.mysql.knowledge_repository import MySQLKnowledgeRepository
            from .repositories.mysql.settings_repository import MySQLSettingsRepository
            from .repositories.mysql.search_repository import MySQLSearchRepository
            
            # Register implementations
            self._repository_factory.register_repository(
                IProjectRepository, DatabaseType.MYSQL, MySQLProjectRepository
            )
            self._repository_factory.register_repository(
                ITaskRepository, DatabaseType.MYSQL, MySQLTaskRepository
            )
            self._repository_factory.register_repository(
                IKnowledgeRepository, DatabaseType.MYSQL, MySQLKnowledgeRepository
            )
            self._repository_factory.register_repository(
                ISettingsRepository, DatabaseType.MYSQL, MySQLSettingsRepository
            )
            self._repository_factory.register_repository(
                ISearchRepository, DatabaseType.MYSQL, MySQLSearchRepository
            )
            
            search_logger.info("MySQL repository implementations registered")
            
        except ImportError as e:
            search_logger.warning(f"MySQL implementations not available: {e}")
            self._register_default_implementations()
    
    def _register_sqlite_implementations(self) -> None:
        """Register SQLite-specific repository implementations."""
        try:
            # Import SQLite repository implementations
            from .repositories.sqlite.project_repository import SQLiteProjectRepository
            from .repositories.sqlite.task_repository import SQLiteTaskRepository
            from .repositories.sqlite.knowledge_repository import SQLiteKnowledgeRepository
            from .repositories.sqlite.settings_repository import SQLiteSettingsRepository
            from .repositories.sqlite.search_repository import SQLiteSearchRepository
            
            # Register implementations
            self._repository_factory.register_repository(
                IProjectRepository, DatabaseType.SQLITE, SQLiteProjectRepository
            )
            self._repository_factory.register_repository(
                ITaskRepository, DatabaseType.SQLITE, SQLiteTaskRepository
            )
            self._repository_factory.register_repository(
                IKnowledgeRepository, DatabaseType.SQLITE, SQLiteKnowledgeRepository
            )
            self._repository_factory.register_repository(
                ISettingsRepository, DatabaseType.SQLITE, SQLiteSettingsRepository
            )
            self._repository_factory.register_repository(
                ISearchRepository, DatabaseType.SQLITE, SQLiteSearchRepository
            )
            
            search_logger.info("SQLite repository implementations registered")
            
        except ImportError as e:
            search_logger.warning(f"SQLite implementations not available: {e}")
            self._register_default_implementations()
    
    def _register_default_implementations(self) -> None:
        """Register default/fallback repository implementations."""
        try:
            # For now, we'll use Supabase implementations as defaults
            # In a complete implementation, these would be generic implementations
            from .repositories.supabase.project_repository import SupabaseProjectRepository
            from .repositories.supabase.task_repository import SupabaseTaskRepository
            from .repositories.supabase.knowledge_repository import SupabaseKnowledgeRepository
            from .repositories.supabase.settings_repository import SupabaseSettingsRepository
            from .repositories.supabase.search_repository import SupabaseSearchRepository
            
            # Register as default implementations
            self._repository_factory.register_default_repository(IProjectRepository, SupabaseProjectRepository)
            self._repository_factory.register_default_repository(ITaskRepository, SupabaseTaskRepository)
            self._repository_factory.register_default_repository(IKnowledgeRepository, SupabaseKnowledgeRepository)
            self._repository_factory.register_default_repository(ISettingsRepository, SupabaseSettingsRepository)
            self._repository_factory.register_default_repository(ISearchRepository, SupabaseSearchRepository)
            
            search_logger.info("Default repository implementations registered")
            
        except ImportError as e:
            search_logger.error(f"Failed to register default implementations: {e}")
            raise RuntimeError(f"No repository implementations available: {e}")
    
    async def initialize(self) -> None:
        """Initialize the dependency container and all services."""
        if self._initialized:
            search_logger.info("Dependency container already initialized")
            return
        
        if not self._connection_manager:
            raise RuntimeError("Connection manager must be configured before initialization")
        
        # Initialize connection manager
        await self._connection_manager.initialize()
        search_logger.info("Connection manager initialized")
        
        # Register repository implementations
        self.register_repository_implementations()
        
        # Create repository provider
        self._repository_provider = RepositoryProvider(self._repository_factory)
        
        self._initialized = True
        search_logger.info("Dependency container initialized successfully")
    
    def get_connection_manager(self) -> ConnectionManager:
        """Get connection manager instance."""
        if not self._connection_manager:
            raise RuntimeError("Connection manager not configured")
        return self._connection_manager
    
    def get_repository_factory(self) -> RepositoryFactory:
        """Get repository factory instance."""
        if not self._repository_factory:
            raise RuntimeError("Repository factory not initialized")
        return self._repository_factory
    
    def get_repository_provider(self) -> RepositoryProvider:
        """Get repository provider instance."""
        if not self._repository_provider:
            raise RuntimeError("Repository provider not initialized")
        return self._repository_provider
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all container services.
        
        Returns:
            Health status of all services
        """
        status = {
            "container_initialized": self._initialized,
            "connection_manager": None,
            "repository_factory": None,
        }
        
        # Check connection manager
        if self._connection_manager:
            try:
                status["connection_manager"] = await self._connection_manager.health_check()
            except Exception as e:
                status["connection_manager"] = {"error": str(e)}
        
        # Check repository factory
        if self._repository_factory:
            try:
                status["repository_factory"] = await self._repository_factory.health_check()
            except Exception as e:
                status["repository_factory"] = {"error": str(e)}
        
        return status
    
    async def close(self) -> None:
        """Close and cleanup all container services."""
        if self._repository_factory:
            await self._repository_factory.clear_cache()
        
        if self._connection_manager:
            await self._connection_manager.close()
        
        self._initialized = False
        search_logger.info("Dependency container closed")


# Global dependency container instance
_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """
    Get the global dependency container instance.
    
    Returns:
        DependencyContainer instance
    """
    global _container
    if not _container:
        _container = DependencyContainer()
    return _container


def create_container_from_env() -> DependencyContainer:
    """
    Create and configure dependency container from environment variables.
    
    Returns:
        Configured DependencyContainer instance
    """
    container = get_container()
    
    # Configure connection manager from environment
    connection_manager = ConnectionManager.from_env()
    container.configure_database(connection_manager)
    
    search_logger.info("Dependency container created from environment")
    return container


async def initialize_dependencies() -> DependencyContainer:
    """
    Initialize all application dependencies.
    
    Returns:
        Initialized DependencyContainer instance
    """
    container = create_container_from_env()
    await container.initialize()
    return container


async def close_dependencies() -> None:
    """Close and cleanup all application dependencies."""
    global _container
    if _container:
        await _container.close()
        _container = None