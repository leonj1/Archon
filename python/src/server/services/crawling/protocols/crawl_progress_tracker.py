"""Crawl progress tracker protocol for orchestrator-level progress tracking."""

from typing import Any, Protocol


class ICrawlProgressTracker(Protocol):
    """Interface for tracking crawl progress with mapped stages."""

    @property
    def progress_tracker(self) -> Any:
        """
        Get underlying progress tracker.

        Returns:
            The underlying progress tracker instance
        """
        ...

    async def start(self, url: str) -> None:
        """
        Start progress tracking for a crawl.

        Args:
            url: The URL being crawled
        """
        ...

    async def update_mapped(
        self, stage: str, stage_progress: int, message: str, **kwargs: Any
    ) -> None:
        """
        Update progress with stage mapping.

        Args:
            stage: Current stage name
            stage_progress: Progress within stage (0-100)
            message: Progress message
            **kwargs: Additional metadata
        """
        ...

    async def update_with_crawl_type(self, crawl_type: str | None) -> None:
        """
        Update progress with detected crawl type.

        Args:
            crawl_type: The type of crawl (e.g., 'single_page', 'recursive'), or None
        """
        ...

    async def update_with_source_id(self, source_id: str | None) -> None:
        """
        Update progress with generated source ID.

        Args:
            source_id: The source identifier, or None
        """
        ...

    async def complete(
        self,
        chunks: int,
        code: int,
        processed: int,
        total: int,
        source_id: str,
    ) -> None:
        """
        Mark crawl as complete with summary data.

        Args:
            chunks: Number of chunks stored
            code: Number of code examples found
            processed: Number of pages processed
            total: Total number of pages
            source_id: The source identifier
        """
        ...

    async def error(self, message: str) -> None:
        """
        Mark crawl as failed with error message.

        Args:
            message: Error description
        """
        ...
