"""
Database Abstraction Layer (DAL) for Archon V2

This module provides a unified interface for database operations across
multiple database backends including Supabase, PostgreSQL, MySQL, and SQLite.
"""

from .connection_manager import ConnectionManager, DatabaseType
from .interfaces import IDatabase, IVectorStore, QueryResult, VectorSearchResult
from .query_builder import QueryBuilder, query

__all__ = [
    "ConnectionManager",
    "DatabaseType",
    "IDatabase",
    "IVectorStore",
    "QueryResult",
    "VectorSearchResult",
    "QueryBuilder",
    "query",
]