"""Fake crawl progress tracker for testing orchestrator-level progress."""

from typing import Any


class FakeCrawlProgressTracker:
    """
    Fake crawl progress tracker for testing.

    Simulates the crawl-specific progress tracker used by AsyncCrawlOrchestrator.
    """

    def __init__(self):
        """Initialize fake crawl progress tracker."""
        self.progress_tracker = self  # Self-reference for compatibility
        self.start_calls: list[str] = []
        self.update_mapped_calls: list[dict[str, Any]] = []
        self.update_crawl_type_calls: list[str] = []
        self.update_source_id_calls: list[str] = []
        self.complete_calls: list[dict[str, Any]] = []
        self.error_calls: list[str] = []
        self.update_calls: list[dict[str, Any]] = []  # For underlying tracker

    async def start(self, url: str) -> None:
        """Record start call."""
        self.start_calls.append(url)

    async def update_mapped(
        self, stage: str, progress: int, message: str, **kwargs: Any
    ) -> None:
        """Record mapped update call."""
        self.update_mapped_calls.append({
            "stage": stage,
            "progress": progress,
            "message": message,
            **kwargs
        })

    async def update_with_crawl_type(self, crawl_type: str) -> None:
        """Record crawl type update."""
        self.update_crawl_type_calls.append(crawl_type)

    async def update_with_source_id(self, source_id: str) -> None:
        """Record source ID update."""
        self.update_source_id_calls.append(source_id)

    async def complete(
        self,
        chunks: int,
        code: int,
        processed: int,
        total: int,
        source_id: str,
    ) -> None:
        """Record completion call."""
        self.complete_calls.append({
            "chunks": chunks,
            "code": code,
            "processed": processed,
            "total": total,
            "source_id": source_id,
        })

    async def error(self, message: str) -> None:
        """Record error call."""
        self.error_calls.append(message)

    async def update(self, status: str, progress: int, log: str, **kwargs: Any) -> None:
        """Record underlying tracker update (for code extraction callback)."""
        self.update_calls.append({
            "status": status,
            "progress": progress,
            "log": log,
            **kwargs
        })

    def reset(self) -> None:
        """Clear all recorded calls."""
        self.start_calls.clear()
        self.update_mapped_calls.clear()
        self.update_crawl_type_calls.clear()
        self.update_source_id_calls.clear()
        self.complete_calls.clear()
        self.error_calls.clear()
        self.update_calls.clear()
