"""
Repository Factory for Database Abstraction Layer

Provides centralized repository creation with dependency injection pattern.
Manages repository instances and their database dependencies based on configuration.
"""

import asyncio
from typing import Dict, Any, Type, TypeVar, Generic, Optional, Union
from contextlib import asynccontextmanager

from .connection_manager import ConnectionManager, DatabaseType
from .interfaces import IDatabase
from .repositories.interfaces.base_repository import BaseRepository
from .repositories.interfaces.project_repository_interface import IProjectRepository
from .repositories.interfaces.task_repository_interface import ITaskRepository
from .repositories.interfaces.knowledge_repository_interface import IKnowledgeRepository
from .repositories.interfaces.settings_repository_interface import ISettingsRepository
from .repositories.interfaces.search_repository_interface import ISearchRepository

# Type variables for repository interfaces
R = TypeVar('R', bound=BaseRepository)


class RepositoryRegistry:
    """
    Registry for repository implementations mapped to database types.
    Supports dependency injection by registering concrete implementations.
    """
    
    def __init__(self):
        # Maps repository interface to database-specific implementations
        # Format: {RepositoryInterface: {DatabaseType: ImplementationClass}}
        self._registrations: Dict[Type[BaseRepository], Dict[DatabaseType, Type[BaseRepository]]] = {}
        
        # Default implementations fallback
        self._default_implementations: Dict[Type[BaseRepository], Type[BaseRepository]] = {}
    
    def register(
        self,
        repository_interface: Type[R],
        database_type: DatabaseType,
        implementation: Type[R]
    ) -> None:
        """
        Register a repository implementation for a specific database type.
        
        Args:
            repository_interface: Repository interface class
            database_type: Target database type
            implementation: Concrete implementation class
        """
        if repository_interface not in self._registrations:
            self._registrations[repository_interface] = {}
        
        self._registrations[repository_interface][database_type] = implementation
    
    def register_default(
        self,
        repository_interface: Type[R],
        implementation: Type[R]
    ) -> None:
        """
        Register a default implementation for a repository interface.
        Used as fallback when no database-specific implementation is found.
        
        Args:
            repository_interface: Repository interface class
            implementation: Default implementation class
        """
        self._default_implementations[repository_interface] = implementation
    
    def get_implementation(
        self,
        repository_interface: Type[R],
        database_type: DatabaseType
    ) -> Optional[Type[R]]:
        """
        Get the registered implementation for a repository interface and database type.
        
        Args:
            repository_interface: Repository interface class
            database_type: Target database type
            
        Returns:
            Implementation class if found, None otherwise
        """
        # Try database-specific implementation first
        if repository_interface in self._registrations:
            db_implementations = self._registrations[repository_interface]
            if database_type in db_implementations:
                return db_implementations[database_type]
        
        # Fallback to default implementation
        return self._default_implementations.get(repository_interface)
    
    def list_registered(self) -> Dict[str, Dict[str, str]]:
        """
        List all registered implementations for debugging.
        
        Returns:
            Dictionary mapping interface names to database implementations
        """
        result = {}
        
        for interface, db_implementations in self._registrations.items():
            interface_name = interface.__name__
            result[interface_name] = {}
            
            for db_type, implementation in db_implementations.items():
                result[interface_name][db_type.value] = implementation.__name__
        
        # Add default implementations
        for interface, implementation in self._default_implementations.items():
            interface_name = interface.__name__
            if interface_name not in result:
                result[interface_name] = {}
            result[interface_name]["default"] = implementation.__name__
        
        return result


class RepositoryFactory:
    """
    Factory for creating repository instances with proper database dependencies.
    Implements dependency injection pattern for repository management.
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """
        Initialize repository factory with connection manager.
        
        Args:
            connection_manager: Database connection manager instance
        """
        self._connection_manager = connection_manager
        self._registry = RepositoryRegistry()
        self._repository_cache: Dict[str, BaseRepository] = {}
        self._lock = asyncio.Lock()
    
    @property
    def registry(self) -> RepositoryRegistry:
        """Get the repository registry."""
        return self._registry
    
    def register_repository(
        self,
        repository_interface: Type[R],
        database_type: DatabaseType,
        implementation: Type[R]
    ) -> None:
        """
        Register a repository implementation for dependency injection.
        
        Args:
            repository_interface: Repository interface class
            database_type: Target database type
            implementation: Concrete implementation class
        """
        self._registry.register(repository_interface, database_type, implementation)
    
    def register_default_repository(
        self,
        repository_interface: Type[R],
        implementation: Type[R]
    ) -> None:
        """
        Register a default repository implementation.
        
        Args:
            repository_interface: Repository interface class
            implementation: Default implementation class
        """
        self._registry.register_default(repository_interface, implementation)
    
    async def create_repository(
        self,
        repository_interface: Type[R],
        table_name: str,
        database_type: Optional[DatabaseType] = None,
        use_cache: bool = True
    ) -> R:
        """
        Create a repository instance with dependency injection.
        
        Args:
            repository_interface: Repository interface class to create
            table_name: Database table name for the repository
            database_type: Override database type (uses primary if None)
            use_cache: Whether to use cached instances
            
        Returns:
            Repository instance
            
        Raises:
            ValueError: If no implementation is registered for the interface
            RuntimeError: If connection manager is not initialized
        """
        # Determine database type
        if database_type is None:
            # Get primary database type from connection manager
            if not self._connection_manager.primary_pool:
                raise RuntimeError("Connection manager not initialized")
            database_type = self._connection_manager.primary_pool.config.database_type
        
        # Create cache key
        cache_key = f"{repository_interface.__name__}_{table_name}_{database_type.value}"
        
        # Check cache first
        if use_cache and cache_key in self._repository_cache:
            return self._repository_cache[cache_key]
        
        # Get implementation from registry
        implementation_class = self._registry.get_implementation(repository_interface, database_type)
        if not implementation_class:
            raise ValueError(
                f"No implementation registered for {repository_interface.__name__} "
                f"with database type {database_type.value}"
            )
        
        # Get database connection
        async with self._connection_manager.get_primary() as database:
            # Create repository instance
            repository = implementation_class(database, table_name)
            
            # Cache the instance if requested
            if use_cache:
                async with self._lock:
                    self._repository_cache[cache_key] = repository
            
            return repository
    
    @asynccontextmanager
    async def get_repository(
        self,
        repository_interface: Type[R],
        table_name: str,
        database_type: Optional[DatabaseType] = None
    ):
        """
        Context manager for repository instances with proper resource management.
        
        Args:
            repository_interface: Repository interface class
            table_name: Database table name
            database_type: Override database type
            
        Yields:
            Repository instance
        """
        repository = await self.create_repository(
            repository_interface, 
            table_name, 
            database_type, 
            use_cache=False
        )
        try:
            yield repository
        finally:
            # Cleanup if needed (for non-cached instances)
            pass
    
    async def get_project_repository(self) -> IProjectRepository:
        """Get project repository instance."""
        return await self.create_repository(IProjectRepository, "projects")
    
    async def get_task_repository(self) -> ITaskRepository:
        """Get task repository instance."""
        return await self.create_repository(ITaskRepository, "tasks")
    
    async def get_knowledge_repository(self) -> IKnowledgeRepository:
        """Get knowledge repository instance."""
        return await self.create_repository(IKnowledgeRepository, "documents")
    
    async def get_settings_repository(self) -> ISettingsRepository:
        """Get settings repository instance."""
        return await self.create_repository(ISettingsRepository, "settings")
    
    async def get_search_repository(self) -> ISearchRepository:
        """Get search repository instance."""
        return await self.create_repository(ISearchRepository, "search_index")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on repository factory and cached repositories.
        
        Returns:
            Health status information
        """
        status = {
            "factory_initialized": True,
            "connection_manager_healthy": False,
            "cached_repositories": len(self._repository_cache),
            "registered_implementations": self._registry.list_registered(),
            "repository_health": {}
        }
        
        # Check connection manager health
        try:
            cm_health = await self._connection_manager.health_check()
            status["connection_manager_healthy"] = cm_health.get("primary", {}).get("healthy", False)
        except Exception as e:
            status["connection_manager_error"] = str(e)
        
        # Check cached repository health
        async with self._lock:
            for cache_key, repository in self._repository_cache.items():
                try:
                    status["repository_health"][cache_key] = await repository.health_check()
                except Exception as e:
                    status["repository_health"][cache_key] = False
        
        return status
    
    async def clear_cache(self) -> None:
        """Clear the repository cache."""
        async with self._lock:
            self._repository_cache.clear()
    
    def get_registry_info(self) -> Dict[str, Any]:
        """
        Get information about registered repository implementations.
        
        Returns:
            Registry information for debugging
        """
        return {
            "registered_implementations": self._registry.list_registered(),
            "cached_repositories": list(self._repository_cache.keys()),
            "connection_manager_type": (
                self._connection_manager.primary_pool.config.database_type.value
                if self._connection_manager.primary_pool
                else "not_initialized"
            )
        }


# Global repository factory instance
_repository_factory: Optional[RepositoryFactory] = None


def get_repository_factory() -> RepositoryFactory:
    """
    Get the global repository factory instance.
    
    Returns:
        RepositoryFactory instance
        
    Raises:
        RuntimeError: If factory is not initialized
    """
    global _repository_factory
    if not _repository_factory:
        raise RuntimeError(
            "Repository factory not initialized. Call initialize_repository_factory() first."
        )
    return _repository_factory


def initialize_repository_factory(connection_manager: ConnectionManager) -> RepositoryFactory:
    """
    Initialize the global repository factory.
    
    Args:
        connection_manager: Database connection manager
        
    Returns:
        Initialized RepositoryFactory instance
    """
    global _repository_factory
    if not _repository_factory:
        _repository_factory = RepositoryFactory(connection_manager)
    return _repository_factory


async def close_repository_factory() -> None:
    """Close and cleanup the repository factory."""
    global _repository_factory
    if _repository_factory:
        await _repository_factory.clear_cache()
        _repository_factory = None