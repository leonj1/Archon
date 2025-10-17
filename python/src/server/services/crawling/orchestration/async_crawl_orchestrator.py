"""
Async Crawl Orchestrator

Main orchestration logic for async crawling operations with progress tracking.
"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, NotRequired, TypedDict

from ....config.logfire_config import get_logger, safe_logfire_error, safe_logfire_info
from ..protocols import (
    ICodeExamplesOrchestrator,
    ICrawlProgressTracker,
    IDocumentProcessingOrchestrator,
    IHeartbeatManager,
    IProgressMapper,
    IProgressUpdateHandler,
    ISourceStatusManager,
    IURLHandler,
    IUrlTypeHandler,
)

logger = get_logger(__name__)


class ProgressState(TypedDict, total=False):
    """State dictionary for tracking progress information."""
    progressId: str
    source_id: str


class ProgressUpdate(TypedDict):
    """Progress update data structure."""
    status: str
    progress: int
    log: str
    error: NotRequired[str]


@dataclass
class CrawlOrchestrationConfig:
    """Configuration for async crawl orchestration."""
    heartbeat_mgr: IHeartbeatManager
    source_status_mgr: ISourceStatusManager
    progress_tracker: ICrawlProgressTracker
    doc_processor: IDocumentProcessingOrchestrator
    code_orchestrator: ICodeExamplesOrchestrator
    url_type_handler: IUrlTypeHandler
    url_handler: IURLHandler
    progress_mapper: IProgressMapper
    progress_state: ProgressState
    cancellation_check: Callable[[], None]
    create_crawl_progress_callback: Callable[[str], Awaitable[Callable[[str, int, str], Awaitable[None]]]]
    handle_progress_update: IProgressUpdateHandler
    progress_id: str | None = None


class AsyncCrawlOrchestrator:
    """Orchestrates the async crawl workflow with all stages."""

    def __init__(self, config: CrawlOrchestrationConfig):
        """
        Initialize the async crawl orchestrator.

        Args:
            config: Configuration object containing all dependencies
        """
        self.heartbeat_mgr = config.heartbeat_mgr
        self.source_status_mgr = config.source_status_mgr
        self.progress_tracker = config.progress_tracker
        self.doc_processor = config.doc_processor
        self.code_orchestrator = config.code_orchestrator
        self.url_type_handler = config.url_type_handler
        self.url_handler = config.url_handler
        self.progress_mapper = config.progress_mapper
        self.progress_state = config.progress_state
        self.cancellation_check = config.cancellation_check
        self.create_crawl_progress_callback = config.create_crawl_progress_callback
        self.handle_progress_update = config.handle_progress_update
        self.progress_id = config.progress_id

    async def orchestrate(self, request: dict[str, Any], task_id: str):
        """
        Main async orchestration workflow.

        Args:
            request: The crawl request containing url, knowledge_type, tags, max_depth, etc.
            task_id: The task ID for this orchestration
        """
        try:
            await self._execute_crawl_workflow(request, task_id)
        except Exception as e:
            await self._handle_error(e, task_id)
            raise

    async def _execute_crawl_workflow(self, request: dict[str, Any], task_id: str):
        """Execute the main crawl workflow stages."""
        url = str(request.get("url", ""))
        safe_logfire_info(f"Starting async crawl orchestration | url={url} | task_id={task_id}")

        # Initialize crawl
        await self._initialize_crawl(url)

        # Perform crawl
        crawl_results, crawl_type = await self._perform_crawl(url, request)

        if not crawl_results:
            raise ValueError("No content was crawled from the provided URL")

        # Process documents
        storage_results = await self._process_documents(
            crawl_results, request, crawl_type, url
        )

        # Extract code examples
        code_examples_count = await self._extract_code_examples(
            request, crawl_results, storage_results, len(crawl_results)
        )

        # Finalize crawl
        await self._finalize_crawl(
            storage_results, code_examples_count, len(crawl_results)
        )

    async def _initialize_crawl(self, url: str):
        """Initialize crawl with source identifiers and initial progress."""
        await self.progress_tracker.start(url)

        original_source_id = self.url_handler.generate_unique_source_id(url)
        source_display_name = self.url_handler.extract_display_name(url)
        safe_logfire_info(
            f"Generated unique source_id '{original_source_id}' and display name '{source_display_name}' from URL '{url}'"
        )

        await self.progress_tracker.update_mapped(
            "starting", 100, f"Starting crawl of {url}", current_url=url
        )

        self.cancellation_check()

    async def _perform_crawl(self, url: str, request: dict[str, Any]):
        """Perform the crawl operation and return results."""
        await self.progress_tracker.update_mapped(
            "analyzing", 50, f"Analyzing URL type for {url}",
            total_pages=1, processed_pages=0
        )

        crawl_results, crawl_type = await self.url_type_handler.crawl_by_type(
            url,
            request,
            progress_callback=await self.create_crawl_progress_callback("crawling"),
        )

        await self.progress_tracker.update_with_crawl_type(crawl_type)
        self.cancellation_check()
        await self._send_heartbeat()

        return crawl_results, crawl_type

    async def _process_documents(
        self,
        crawl_results: list[dict[str, Any]],
        request: dict[str, Any],
        crawl_type: str,
        url: str,
    ) -> dict[str, Any]:
        """Process and store crawled documents."""
        await self.progress_tracker.update_mapped("processing", 50, "Processing crawled content")
        self.cancellation_check()

        original_source_id = self.url_handler.generate_unique_source_id(url)
        source_display_name = self.url_handler.extract_display_name(url)

        storage_results = await self.doc_processor.process_and_store(
            crawl_results,
            request,
            crawl_type,
            original_source_id,
            self.cancellation_check,
            url,
            source_display_name,
        )

        await self.progress_tracker.update_with_source_id(storage_results.get("source_id"))
        self.cancellation_check()
        await self._send_heartbeat()

        return storage_results

    async def _extract_code_examples(
        self,
        request: dict[str, Any],
        crawl_results: list[dict[str, Any]],
        storage_results: dict[str, Any],
        total_pages: int,
    ) -> int:
        """Extract code examples if requested."""
        actual_chunks_stored = storage_results.get("chunks_stored", 0)

        if actual_chunks_stored == 0:
            return 0

        await self.progress_tracker.update_mapped(
            "code_extraction", 0, "Starting code extraction..."
        )

        code_examples_count = await self.code_orchestrator.extract_code_examples(
            request,
            crawl_results,
            storage_results["url_to_full_document"],
            storage_results["source_id"],
            self.progress_tracker.progress_tracker.update if self.progress_tracker.progress_tracker else None,
            total_pages,
        )

        self.cancellation_check()
        await self._send_heartbeat()

        return code_examples_count

    async def _finalize_crawl(
        self,
        storage_results: dict[str, Any],
        code_examples_count: int,
        total_pages: int,
    ):
        """Finalize the crawl with progress updates and status changes."""
        actual_chunks_stored = storage_results.get("chunks_stored", 0)

        await self._update_finalization_progress(actual_chunks_stored, code_examples_count)
        await self._update_completion_progress(actual_chunks_stored, code_examples_count, total_pages)
        await self._complete_progress_tracker(storage_results, code_examples_count, total_pages, actual_chunks_stored)
        await self._update_source_status(storage_results)

    async def _update_finalization_progress(self, chunks_stored: int, code_examples: int):
        """Update progress for finalization stage."""
        await self.progress_tracker.update_mapped(
            "finalization", 50, "Finalizing crawl results...",
            chunks_stored=chunks_stored,
            code_examples_found=code_examples,
        )

    async def _update_completion_progress(self, chunks_stored: int, code_examples: int, total_pages: int):
        """Update progress for completion stage."""
        await self.progress_tracker.update_mapped(
            "completed", 100,
            f"Crawl completed: {chunks_stored} chunks, {code_examples} code examples",
            chunks_stored=chunks_stored,
            code_examples_found=code_examples,
            processed_pages=total_pages,
            total_pages=total_pages,
        )

    async def _complete_progress_tracker(
        self,
        storage_results: dict[str, Any],
        code_examples: int,
        total_pages: int,
        chunks_stored: int,
    ):
        """Mark crawl as complete in progress tracker."""
        await self.progress_tracker.complete(
            chunks_stored,
            code_examples,
            total_pages,
            total_pages,
            storage_results.get("source_id", ""),
        )

    async def _update_source_status(self, storage_results: dict[str, Any]):
        """Update source status to completed."""
        source_id = storage_results.get("source_id")
        if source_id:
            await self.source_status_mgr.update_to_completed(source_id)

    async def _send_heartbeat(self):
        """Send heartbeat if needed."""
        await self.heartbeat_mgr.send_if_needed(
            self.progress_mapper.get_current_stage(),
            self.progress_mapper.get_current_progress()
        )

    async def _handle_error(self, error: Exception, task_id: str):
        """
        Handle errors during orchestration.

        Args:
            error: The exception that occurred
            task_id: The task ID for this orchestration
        """
        logger.error("Async crawl orchestration failed", exc_info=True)
        safe_logfire_error(f"Async crawl orchestration failed | error={str(error)}")

        error_message = f"Crawl failed: {str(error)}"
        error_progress = self.progress_mapper.map_progress("error", 0)
        await self.handle_progress_update(
            task_id,
            {
                "status": "error",
                "progress": error_progress,
                "log": error_message,
                "error": str(error),
            },
        )

        await self.progress_tracker.error(error_message)

        source_id = self.progress_state.get("source_id")
        if source_id:
            await self.source_status_mgr.update_to_failed(source_id)
