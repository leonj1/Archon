"""Source status manager protocol for updating crawl source status."""

from typing import Protocol


class ISourceStatusManager(Protocol):
    """Interface for managing knowledge source status updates."""

    async def update_to_completed(self, source_id: str) -> None:
        """
        Update source status to completed.

        Args:
            source_id: The source identifier to update
        """
        ...

    async def update_to_failed(self, source_id: str) -> None:
        """
        Update source status to failed.

        Args:
            source_id: The source identifier to update
        """
        ...
