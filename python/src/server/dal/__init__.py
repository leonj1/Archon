"""
Database Abstraction Layer (DAL) for Archon V2

This module provides a unified interface for database operations across
multiple database backends including Supabase, PostgreSQL, MySQL, and SQLite.
Includes repository factory and dependency injection for clean architecture.
"""

from .connection_manager import ConnectionManager, DatabaseType
from .interfaces import IDatabase, IVectorStore, QueryResult, VectorSearchResult
from .query_builder import QueryBuilder, query
from .repository_factory import (
    RepositoryFactory,
    RepositoryRegistry,
    get_repository_factory,
    initialize_repository_factory,
    close_repository_factory,
)
from .dependency_injection import (
    DependencyContainer,
    RepositoryProvider,
    get_container,
    create_container_from_env,
    initialize_dependencies,
    close_dependencies,
)

__all__ = [
    # Core interfaces and connection management
    "ConnectionManager",
    "DatabaseType",
    "IDatabase",
    "IVectorStore",
    "QueryResult",
    "VectorSearchResult",
    "QueryBuilder",
    "query",
    # Repository factory and registry
    "RepositoryFactory",
    "RepositoryRegistry",
    "get_repository_factory",
    "initialize_repository_factory",
    "close_repository_factory",
    # Dependency injection
    "DependencyContainer",
    "RepositoryProvider",
    "get_container",
    "create_container_from_env",
    "initialize_dependencies",
    "close_dependencies",
]