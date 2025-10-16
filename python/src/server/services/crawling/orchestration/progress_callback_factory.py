"""
Progress Callback Factory

Creates progress callbacks for crawling operations with proper mapping and tracking.
"""

from collections.abc import Awaitable, Callable
from typing import Any

from ....config.logfire_config import safe_logfire_info


class ProgressCallbackFactory:
    """Factory for creating progress callbacks with proper mapping."""

    def __init__(
        self,
        progress_tracker: Any,
        progress_mapper: Any,
        progress_id: str | None,
    ):
        """
        Initialize the progress callback factory.

        Args:
            progress_tracker: ProgressTracker instance for HTTP polling
            progress_mapper: ProgressMapper for mapping progress values
            progress_id: Optional progress ID for tracking
        """
        self.progress_tracker = progress_tracker
        self.progress_mapper = progress_mapper
        self.progress_id = progress_id

    async def create_callback(
        self, base_status: str
    ) -> Callable[[str, int, str], Awaitable[None]]:
        """
        Create a progress callback for crawling operations.

        Args:
            base_status: The base status to use for progress updates

        Returns:
            Async callback function with signature (status: str, progress: int, message: str, **kwargs) -> None
        """
        async def callback(status: str, progress: int, message: str, **kwargs):
            if not self.progress_tracker:
                return

            self._log_callback_received(status, progress, kwargs)

            mapped_progress = self.progress_mapper.map_progress(base_status, progress)

            await self.progress_tracker.update(
                status=base_status,
                progress=mapped_progress,
                log=message,
                **kwargs
            )

            self._log_progress_updated(base_status, progress, mapped_progress, kwargs)

        return callback

    def _log_callback_received(self, status: str, progress: int, kwargs: dict[str, Any]):
        """Log when callback is received."""
        safe_logfire_info(
            f"Progress callback received | status={status} | progress={progress} | "
            f"total_pages={kwargs.get('total_pages', 'N/A')} | processed_pages={kwargs.get('processed_pages', 'N/A')} | "
            f"kwargs_keys={list(kwargs.keys())}"
        )

    def _log_progress_updated(self, base_status: str, raw_progress: int, mapped_progress: int, kwargs: dict[str, Any]):
        """Log when progress is updated."""
        safe_logfire_info(
            f"Updated crawl progress | progress_id={self.progress_id} | status={base_status} | "
            f"raw_progress={raw_progress} | mapped_progress={mapped_progress} | "
            f"total_pages={kwargs.get('total_pages', 'N/A')} | processed_pages={kwargs.get('processed_pages', 'N/A')}"
        )
