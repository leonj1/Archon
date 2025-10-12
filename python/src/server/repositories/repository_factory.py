"""
Repository Factory

Provides centralized management of repository instances with support for
different database backends (Supabase, Fake for testing, future SQLite, etc.).

Usage:
    # Get the default configured repository
    from repositories import get_repository
    repo = get_repository()

    # For testing, use the fake repository
    from repositories import get_repository
    repo = get_repository(backend="fake")

    # In services, inject the repository
    class MyService:
        def __init__(self, repository: DatabaseRepository = None):
            self.repository = repository or get_repository()

Configuration:
    Set ARCHON_DB_BACKEND environment variable to choose backend:
    - "supabase" (default): Production Supabase backend
    - "fake": In-memory fake repository for testing
    - "sqlite": Future SQLite backend (not yet implemented)
"""

import os
from typing import Literal, Optional

from ..config.logfire_config import get_logger
from ..utils import get_supabase_client
from .database_repository import DatabaseRepository
from .fake_repository import FakeDatabaseRepository
from .supabase_repository import SupabaseDatabaseRepository

logger = get_logger(__name__)

BackendType = Literal["supabase", "fake", "sqlite"]


class RepositoryFactory:
    """
    Singleton factory for managing repository instances.

    Provides a centralized way to obtain repository instances with support
    for different backends and test mode configuration.
    """

    _instance: Optional["RepositoryFactory"] = None
    _repository: Optional[DatabaseRepository] = None
    _backend: Optional[BackendType] = None

    def __new__(cls) -> "RepositoryFactory":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_repository(
        self, backend: Optional[BackendType] = None
    ) -> DatabaseRepository:
        """
        Get a repository instance for the specified backend.

        Args:
            backend: Database backend to use. If None, uses ARCHON_DB_BACKEND
                    environment variable or defaults to "supabase"

        Returns:
            DatabaseRepository instance configured for the specified backend

        Raises:
            ValueError: If backend is not recognized
            RuntimeError: If backend initialization fails

        Examples:
            # Use default backend (from env or supabase)
            repo = factory.get_repository()

            # Use fake backend for testing
            repo = factory.get_repository(backend="fake")

            # Use specific backend
            repo = factory.get_repository(backend="supabase")
        """
        # Determine which backend to use
        if backend is None:
            backend = self._get_backend_from_env()

        # If we already have a repository for this backend, return it
        if self._repository is not None and self._backend == backend:
            return self._repository

        # Create new repository for requested backend
        logger.info(f"Initializing repository with backend: {backend}")

        if backend == "supabase":
            self._repository = self._create_supabase_repository()
        elif backend == "fake":
            self._repository = self._create_fake_repository()
        elif backend == "sqlite":
            raise NotImplementedError(
                "SQLite backend is not yet implemented. "
                "Use 'supabase' or 'fake' backend instead."
            )
        else:
            raise ValueError(
                f"Unknown backend: {backend}. "
                f"Supported backends: supabase, fake, sqlite"
            )

        self._backend = backend
        logger.info(f"Repository initialized successfully with backend: {backend}")
        return self._repository

    def reset(self) -> None:
        """
        Reset the factory state.

        Useful for testing to ensure clean state between tests.
        Clears the cached repository instance.
        """
        self._repository = None
        self._backend = None
        logger.debug("Repository factory reset")

    @staticmethod
    def _get_backend_from_env() -> BackendType:
        """
        Get backend type from environment variable.

        Returns:
            Backend type from ARCHON_DB_BACKEND or "supabase" as default
        """
        backend = os.getenv("ARCHON_DB_BACKEND", "supabase").lower()

        # Validate the backend value
        valid_backends = ("supabase", "fake", "sqlite")
        if backend not in valid_backends:
            logger.warning(
                f"Invalid ARCHON_DB_BACKEND value: {backend}. "
                f"Defaulting to 'supabase'. Valid options: {', '.join(valid_backends)}"
            )
            return "supabase"

        return backend  # type: ignore

    @staticmethod
    def _create_supabase_repository() -> SupabaseDatabaseRepository:
        """
        Create a Supabase repository instance.

        Returns:
            Configured SupabaseDatabaseRepository

        Raises:
            RuntimeError: If Supabase client initialization fails
        """
        try:
            supabase_client = get_supabase_client()
            return SupabaseDatabaseRepository(supabase_client)
        except Exception as e:
            logger.error(f"Failed to initialize Supabase repository: {e}")
            raise RuntimeError(
                f"Failed to initialize Supabase repository: {e}. "
                f"Ensure SUPABASE_URL and SUPABASE_SERVICE_KEY are set correctly."
            ) from e

    @staticmethod
    def _create_fake_repository() -> FakeDatabaseRepository:
        """
        Create a fake repository instance for testing.

        Returns:
            Configured FakeDatabaseRepository
        """
        return FakeDatabaseRepository()


# Global factory instance
_factory = RepositoryFactory()


def get_repository(backend: Optional[BackendType] = None) -> DatabaseRepository:
    """
    Get the global repository instance.

    This is the primary function to use for obtaining repository instances
    throughout the application.

    Args:
        backend: Optional backend type. If None, uses ARCHON_DB_BACKEND
                environment variable or defaults to "supabase"

    Returns:
        DatabaseRepository instance

    Raises:
        ValueError: If backend is not recognized
        RuntimeError: If backend initialization fails

    Examples:
        # In services - use default backend
        from repositories import get_repository

        class MyService:
            def __init__(self, repository: DatabaseRepository = None):
                self.repository = repository or get_repository()

        # In tests - use fake backend
        def test_my_service():
            repo = get_repository(backend="fake")
            service = MyService(repository=repo)
            # ... test code ...

        # Force specific backend
        repo = get_repository(backend="supabase")
    """
    return _factory.get_repository(backend)


def reset_factory() -> None:
    """
    Reset the global factory state.

    Useful for testing to ensure clean state between tests.
    This clears the cached repository instance.

    Example:
        def test_something():
            reset_factory()  # Start with clean state
            repo = get_repository(backend="fake")
            # ... test code ...
    """
    _factory.reset()


__all__ = [
    "RepositoryFactory",
    "get_repository",
    "reset_factory",
    "BackendType",
]
