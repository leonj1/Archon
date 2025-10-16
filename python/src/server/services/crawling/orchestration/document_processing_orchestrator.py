"""
Document Processing Orchestrator

Coordinates document storage with progress tracking and validation.
"""

from collections.abc import Callable
from typing import Any

from ....config.logfire_config import get_logger, safe_logfire_error, safe_logfire_info
from ..document_storage_operations import DocumentStorageOperations

logger = get_logger(__name__)


class DocumentProcessingOrchestrator:
    """Orchestrates document processing and storage with progress tracking."""

    def __init__(
        self,
        doc_storage_ops: DocumentStorageOperations,
        progress_mapper,
        progress_tracker,
    ):
        """
        Initialize the document processing orchestrator.

        Args:
            doc_storage_ops: Document storage operations instance
            progress_mapper: Progress mapper for tracking
            progress_tracker: Progress tracker instance
        """
        self.doc_storage_ops = doc_storage_ops
        self.progress_mapper = progress_mapper
        self.progress_tracker = progress_tracker

    async def process_and_store(
        self,
        crawl_results: list[dict[str, Any]],
        request: dict[str, Any],
        crawl_type: str,
        original_source_id: str,
        cancellation_check: Callable[[], None],
        source_url: str,
        source_display_name: str,
    ) -> dict[str, Any]:
        """
        Process and store documents with progress tracking and validation.

        Args:
            crawl_results: Crawled pages data
            request: Original crawl request
            crawl_type: Type of crawl performed
            original_source_id: Generated source ID
            cancellation_check: Function to check if operation is cancelled
            source_url: Original source URL
            source_display_name: Display name for source

        Returns:
            Storage results dictionary

        Raises:
            ValueError: If document storage fails validation
        """
        total_pages = len(crawl_results)
        last_logged_progress = 0

        # Create progress callback
        async def doc_storage_callback(
            status: str, progress: int, message: str, **kwargs
        ):
            nonlocal last_logged_progress

            # Log significant progress milestones
            if self._should_log_progress(status, progress, last_logged_progress):
                safe_logfire_info(
                    f"Document storage progress: {progress}% | status={status} | "
                    f"message={message[:50]}..." + ("..." if len(message) > 50 else "")
                )
                last_logged_progress = progress

            if self.progress_tracker:
                mapped_progress = self.progress_mapper.map_progress(
                    "document_storage", progress
                )

                await self.progress_tracker.update(
                    status="document_storage",
                    progress=mapped_progress,
                    log=message,
                    total_pages=total_pages,
                    **kwargs,
                )

        # Process and store documents
        storage_results = await self.doc_storage_ops.process_and_store_documents(
            crawl_results,
            request,
            crawl_type,
            original_source_id,
            doc_storage_callback,
            cancellation_check,
            source_url=source_url,
            source_display_name=source_display_name,
            url_to_page_id=None,
        )

        # Validate storage results
        self._validate_storage_results(storage_results, source_url)

        return storage_results

    def _should_log_progress(
        self, status: str, progress: int, last_logged_progress: int
    ) -> bool:
        """
        Determine if progress should be logged.

        Args:
            status: Current status
            progress: Current progress percentage
            last_logged_progress: Last logged progress percentage

        Returns:
            True if progress should be logged
        """
        return (
            status != "document_storage"  # Status changes
            or progress == 100  # Completion
            or progress == 0  # Start
            or abs(progress - last_logged_progress) >= 5  # 5% progress changes
        )

    def _validate_storage_results(
        self, storage_results: dict[str, Any], source_url: str
    ):
        """
        Validate that documents were actually stored.

        Args:
            storage_results: Storage results to validate
            source_url: Source URL for error messages

        Raises:
            ValueError: If validation fails
        """
        actual_chunks_stored = storage_results.get("chunks_stored", 0)
        chunk_count = storage_results.get("chunk_count", 0)

        if chunk_count > 0 and actual_chunks_stored == 0:
            error_msg = (
                f"Failed to store documents: {chunk_count} chunks processed but 0 stored "
                f"| url={source_url}"
            )
            safe_logfire_error(error_msg)
            raise ValueError(error_msg)
