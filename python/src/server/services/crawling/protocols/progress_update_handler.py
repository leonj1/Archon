"""Progress update handler protocol."""

from typing import Any, Protocol


class IProgressUpdateHandler(Protocol):
    """Interface for progress update handling."""

    async def __call__(self, task_id: str, update: dict[str, Any]) -> None:
        """
        Handle a progress update.

        Args:
            task_id: Task identifier
            update: Progress update data
        """
        ...
