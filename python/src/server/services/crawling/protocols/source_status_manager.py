"""Source status manager protocol for updating crawl source status."""

from typing import Protocol


class ISourceStatusManager(Protocol):
    """Interface for managing knowledge source status updates."""

    async def update_to_completed(self, source_id: str) -> bool:
        """
        Update source status to completed.

        Args:
            source_id: The source identifier to update

        Returns:
            True if update was successful and verified, False otherwise
        """
        ...

    async def update_to_failed(self, source_id: str | None) -> bool:
        """
        Update source status to failed.

        Args:
            source_id: The source identifier to update (optional)

        Returns:
            True if update was successful, False otherwise
        """
        ...
