"""
Database Repository Package

Provides repository pattern implementation for database access.
"""

from .database_repository import DatabaseRepository
from .fake_repository import FakeDatabaseRepository
from .repository_factory import (
    BackendType,
    RepositoryFactory,
    get_repository,
    reset_factory,
)

__all__ = [
    "DatabaseRepository",
    "FakeDatabaseRepository",
    "RepositoryFactory",
    "get_repository",
    "reset_factory",
    "BackendType",
]
