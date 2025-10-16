"""
Crawl Progress Tracker

Manages progress updates with mapping and progress state tracking.
"""

from typing import Any, Callable, Awaitable, Optional

from ....config.logfire_config import get_logger, safe_logfire_info
from ....utils.progress.progress_tracker import ProgressTracker
from ..progress_mapper import ProgressMapper

logger = get_logger(__name__)


class CrawlProgressTracker:
    """Manages progress updates with stage mapping for crawl operations."""

    def __init__(
        self,
        progress_tracker: Optional[ProgressTracker],
        progress_mapper: ProgressMapper,
        task_id: str,
        handle_progress_update: Callable[[str, dict[str, Any]], Awaitable[None]],
    ):
        """
        Initialize the crawl progress tracker.

        Args:
            progress_tracker: Progress tracker instance (may be None)
            progress_mapper: Progress mapper for stage mapping
            task_id: Task ID for progress updates
            handle_progress_update: Callback to handle progress updates
        """
        self.progress_tracker = progress_tracker
        self.progress_mapper = progress_mapper
        self.task_id = task_id
        self.handle_progress_update = handle_progress_update

    async def start(self, url: str):
        """
        Start progress tracking.

        Args:
            url: The URL being crawled
        """
        if self.progress_tracker:
            await self.progress_tracker.start({
                "url": url,
                "status": "starting",
                "progress": 0,
                "log": f"Starting crawl of {url}",
            })

    async def update_mapped(
        self, stage: str, stage_progress: int, message: str, **kwargs
    ):
        """
        Update progress with stage mapping.

        Args:
            stage: Processing stage name
            stage_progress: Progress within the stage (0-100)
            message: Progress message
            **kwargs: Additional metadata
        """
        overall_progress = self.progress_mapper.map_progress(stage, stage_progress)
        await self.handle_progress_update(
            self.task_id,
            {
                "status": stage,
                "progress": overall_progress,
                "log": message,
                "message": message,
                **kwargs,
            },
        )

    async def update_with_crawl_type(self, crawl_type: str):
        """
        Update progress tracker with crawl type information.

        Args:
            crawl_type: Type of crawl being performed
        """
        if not self.progress_tracker or not crawl_type:
            return

        mapped_progress = self.progress_mapper.map_progress("crawling", 100)
        await self.progress_tracker.update(
            status="crawling",
            progress=mapped_progress,
            log=f"Processing {crawl_type} content",
            crawl_type=crawl_type,
        )

    async def update_with_source_id(self, source_id: str):
        """
        Update progress tracker with source ID.

        Args:
            source_id: The source ID created during document storage
        """
        if not self.progress_tracker or not source_id:
            return

        await self.progress_tracker.update(
            status=self.progress_tracker.state.get("status", "document_storage"),
            progress=self.progress_tracker.state.get("progress", 0),
            log=self.progress_tracker.state.get("log", "Processing documents"),
            source_id=source_id,
        )

        safe_logfire_info(
            f"Updated progress tracker with source_id | task_id={self.task_id} | "
            f"source_id={source_id}"
        )

    async def complete(
        self,
        chunks_stored: int,
        code_examples_found: int,
        processed_pages: int,
        total_pages: int,
        source_id: str,
    ):
        """
        Mark crawl as completed.

        Args:
            chunks_stored: Number of document chunks stored
            code_examples_found: Number of code examples extracted
            processed_pages: Number of pages processed
            total_pages: Total number of pages
            source_id: Source ID
        """
        if not self.progress_tracker:
            return

        await self.progress_tracker.complete({
            "chunks_stored": chunks_stored,
            "code_examples_found": code_examples_found,
            "processed_pages": processed_pages,
            "total_pages": total_pages,
            "sourceId": source_id,
            "log": "Crawl completed successfully!",
        })

    async def error(self, error_message: str):
        """
        Mark crawl as failed.

        Args:
            error_message: Error message describing the failure
        """
        if self.progress_tracker:
            await self.progress_tracker.error(error_message)
