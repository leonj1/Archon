"""Progress callback protocol for heartbeat updates."""

from typing import Any, Protocol


class IProgressCallback(Protocol):
    """Interface for progress callback operations."""

    async def __call__(self, stage: str, data: dict[str, Any]) -> None:
        """
        Send progress update.

        Args:
            stage: Current processing stage
            data: Progress data including progress percentage and metadata
        """
        ...
