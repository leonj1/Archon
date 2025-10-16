"""Progress tracker protocol for crawl operations."""

from typing import Any, Protocol


class IProgressTracker(Protocol):
    """Interface for progress tracking operations."""

    @property
    def state(self) -> dict[str, Any]:
        """
        Get current progress state.

        Returns:
            Dictionary containing status, progress, log, and other metadata
        """
        ...

    async def start(self, initial_data: dict[str, Any]) -> None:
        """
        Start progress tracking with initial data.

        Args:
            initial_data: Initial progress data
        """
        ...

    async def update(self, status: str, progress: int, log: str, **kwargs: Any) -> None:
        """
        Update progress state.

        Args:
            status: Current status
            progress: Progress percentage (0-100)
            log: Log message
            **kwargs: Additional metadata
        """
        ...

    async def complete(self, completion_data: dict[str, Any]) -> None:
        """
        Mark progress as complete.

        Args:
            completion_data: Completion metadata
        """
        ...

    async def error(self, error_message: str) -> None:
        """
        Mark progress as failed.

        Args:
            error_message: Error description
        """
        ...
