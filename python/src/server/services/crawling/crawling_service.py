"""
Crawling Service Module for Archon RAG

This module combines crawling functionality and orchestration.
It handles web crawling operations including single page crawling,
batch crawling, recursive crawling, and overall orchestration with progress tracking.
"""

import asyncio
import uuid
from collections.abc import Awaitable, Callable
from typing import Any, Optional

from ...config.logfire_config import get_logger, safe_logfire_error, safe_logfire_info
from ...repositories.database_repository import DatabaseRepository
from ...repositories.repository_factory import get_repository
from ...utils.progress.progress_tracker import ProgressTracker

# Import strategies
# Import operations
from .document_storage_operations import DocumentStorageOperations
from .helpers.site_config import SiteConfig

# Import helpers
from .helpers.url_handler import URLHandler

# Import orchestration components
from .orchestration import (
    CodeExamplesOrchestrator,
    CrawlProgressTracker,
    DocumentProcessingOrchestrator,
    HeartbeatManager,
    SourceStatusManager,
    UrlTypeHandler,
)
from .page_storage_operations import PageStorageOperations
from .progress_mapper import ProgressMapper
from .strategies.batch import BatchCrawlStrategy
from .strategies.recursive import RecursiveCrawlStrategy
from .strategies.single_page import SinglePageCrawlStrategy
from .strategies.sitemap import SitemapCrawlStrategy

logger = get_logger(__name__)

# Global registry to track active orchestration services for cancellation support
_active_orchestrations: dict[str, "CrawlingService"] = {}
_orchestration_lock: asyncio.Lock | None = None

def _ensure_orchestration_lock() -> asyncio.Lock:
    global _orchestration_lock
    if _orchestration_lock is None:
        _orchestration_lock = asyncio.Lock()
    return _orchestration_lock

async def get_active_orchestration(progress_id: str) -> Optional["CrawlingService"]:
    """Get an active orchestration service by progress ID."""
    lock = _ensure_orchestration_lock()
    async with lock:
        return _active_orchestrations.get(progress_id)

async def register_orchestration(progress_id: str, orchestration: "CrawlingService"):
    """Register an active orchestration service."""
    lock = _ensure_orchestration_lock()
    async with lock:
        _active_orchestrations[progress_id] = orchestration

async def unregister_orchestration(progress_id: str):
    """Unregister an orchestration service."""
    lock = _ensure_orchestration_lock()
    async with lock:
        _active_orchestrations.pop(progress_id, None)

class CrawlingService:
    """
    Service class for web crawling and orchestration operations.
    Combines functionality from both CrawlingService and CrawlOrchestrationService.
    """

    def __init__(self, crawler=None, repository: DatabaseRepository | None = None, progress_id=None):
        """
        Initialize the crawling service.

        Args:
            crawler: The Crawl4AI crawler instance
            repository: DatabaseRepository instance. If None, it will be created via get_repository().
            progress_id: Optional progress ID for HTTP polling updates
        """
        self.crawler = crawler

        # Initialize repository following the standard pattern
        self.repository = repository if repository is not None else get_repository()

        self.progress_id = progress_id
        self.progress_tracker = None

        # Initialize helpers
        self.url_handler = URLHandler()
        self.site_config = SiteConfig()
        self.markdown_generator = self.site_config.get_markdown_generator()
        self.link_pruning_markdown_generator = self.site_config.get_link_pruning_markdown_generator()

        # Initialize strategies
        self.batch_strategy = BatchCrawlStrategy(crawler, self.link_pruning_markdown_generator)
        self.recursive_strategy = RecursiveCrawlStrategy(crawler, self.link_pruning_markdown_generator)
        self.single_page_strategy = SinglePageCrawlStrategy(crawler, self.markdown_generator)
        self.sitemap_strategy = SitemapCrawlStrategy()

        # Initialize operations with repository
        self.doc_storage_ops = DocumentStorageOperations(repository=self.repository)
        self.page_storage_ops = PageStorageOperations(repository=self.repository)

        # Track progress state across all stages to prevent UI resets
        self.progress_state = {"progressId": self.progress_id} if self.progress_id else {}
        # Initialize progress mapper to prevent backwards jumps
        self.progress_mapper = ProgressMapper()
        # Cancellation support
        self._cancelled = False

    def set_progress_id(self, progress_id: str):
        """Set the progress ID for HTTP polling updates."""
        self.progress_id = progress_id
        if self.progress_id:
            self.progress_state = {"progressId": self.progress_id}
            # Initialize progress tracker for HTTP polling
            self.progress_tracker = ProgressTracker(progress_id, operation_type="crawl")

    def cancel(self):
        """Cancel the crawl operation."""
        self._cancelled = True
        safe_logfire_info(f"Crawl operation cancelled | progress_id={self.progress_id}")

    def is_cancelled(self) -> bool:
        """Check if the crawl operation has been cancelled."""
        return self._cancelled

    def _check_cancellation(self):
        """Check if cancelled and raise an exception if so."""
        if self._cancelled:
            raise asyncio.CancelledError("Crawl operation was cancelled by user")

    async def _create_crawl_progress_callback(
        self, base_status: str
    ) -> Callable[[str, int, str], Awaitable[None]]:
        """Create a progress callback for crawling operations.

        Args:
            base_status: The base status to use for progress updates

        Returns:
            Async callback function with signature (status: str, progress: int, message: str, **kwargs) -> None
        """
        async def callback(status: str, progress: int, message: str, **kwargs):
            if self.progress_tracker:
                # Debug log what we're receiving
                safe_logfire_info(
                    f"Progress callback received | status={status} | progress={progress} | "
                    f"total_pages={kwargs.get('total_pages', 'N/A')} | processed_pages={kwargs.get('processed_pages', 'N/A')} | "
                    f"kwargs_keys={list(kwargs.keys())}"
                )

                # Map the progress to the overall progress range
                mapped_progress = self.progress_mapper.map_progress(base_status, progress)

                # Update progress via tracker (stores in memory for HTTP polling)
                await self.progress_tracker.update(
                    status=base_status,
                    progress=mapped_progress,
                    log=message,
                    **kwargs
                )
                safe_logfire_info(
                    f"Updated crawl progress | progress_id={self.progress_id} | status={base_status} | "
                    f"raw_progress={progress} | mapped_progress={mapped_progress} | "
                    f"total_pages={kwargs.get('total_pages', 'N/A')} | processed_pages={kwargs.get('processed_pages', 'N/A')}"
                )

        return callback

    async def _handle_progress_update(self, task_id: str, update: dict[str, Any]) -> None:
        """
        Handle progress updates from background task.

        Args:
            task_id: The task ID for the progress update
            update: Dictionary containing progress update data
        """
        if self.progress_tracker:
            # Update progress via tracker for HTTP polling
            await self.progress_tracker.update(
                status=update.get("status", "processing"),
                progress=update.get("progress", update.get("percentage", 0)),  # Support both for compatibility
                log=update.get("log", "Processing..."),
                **{k: v for k, v in update.items() if k not in ["status", "progress", "percentage", "log"]}
            )

    # Simple delegation methods for backward compatibility
    async def crawl_single_page(self, url: str, retry_count: int = 3) -> dict[str, Any]:
        """Crawl a single web page."""
        return await self.single_page_strategy.crawl_single_page(
            url,
            self.url_handler.transform_github_url,
            self.site_config.is_documentation_site,
            retry_count,
        )

    async def crawl_markdown_file(
        self, url: str, progress_callback: Callable[[str, int, str], Awaitable[None]] | None = None
    ) -> list[dict[str, Any]]:
        """Crawl a .txt or markdown file."""
        return await self.single_page_strategy.crawl_markdown_file(
            url,
            self.url_handler.transform_github_url,
            progress_callback,
        )

    def parse_sitemap(self, sitemap_url: str) -> list[str]:
        """Parse a sitemap and extract URLs."""
        return self.sitemap_strategy.parse_sitemap(sitemap_url, self._check_cancellation)

    async def crawl_batch_with_progress(
        self,
        urls: list[str],
        max_concurrent: int | None = None,
        progress_callback: Callable[[str, int, str], Awaitable[None]] | None = None,
        link_text_fallbacks: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        """Batch crawl multiple URLs in parallel."""
        return await self.batch_strategy.crawl_batch_with_progress(
            urls,
            self.url_handler.transform_github_url,
            self.site_config.is_documentation_site,
            max_concurrent,
            progress_callback,
            self._check_cancellation,  # Pass cancellation check
            link_text_fallbacks,  # Pass link text fallbacks
        )

    async def crawl_recursive_with_progress(
        self,
        start_urls: list[str],
        max_depth: int = 3,
        max_concurrent: int | None = None,
        progress_callback: Callable[[str, int, str], Awaitable[None]] | None = None,
    ) -> list[dict[str, Any]]:
        """Recursively crawl internal links from start URLs."""
        return await self.recursive_strategy.crawl_recursive_with_progress(
            start_urls,
            self.url_handler.transform_github_url,
            self.site_config.is_documentation_site,
            max_depth,
            max_concurrent,
            progress_callback,
            self._check_cancellation,  # Pass cancellation check
        )

    # Orchestration methods
    async def orchestrate_crawl(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Main orchestration method - non-blocking using asyncio.create_task.

        Args:
            request: The crawl request containing url, knowledge_type, tags, max_depth, etc.

        Returns:
            Dict containing task_id, status, and the asyncio task reference
        """
        url = str(request.get("url", ""))
        safe_logfire_info(f"Starting background crawl orchestration | url={url}")

        # Create task ID
        task_id = self.progress_id or str(uuid.uuid4())

        # Register this orchestration service for cancellation support
        if self.progress_id:
            await register_orchestration(self.progress_id, self)

        # Start the crawl as an async task in the main event loop
        # Store the task reference for proper cancellation
        crawl_task = asyncio.create_task(self._async_orchestrate_crawl(request, task_id))

        # Set a name for the task to help with debugging
        if self.progress_id:
            crawl_task.set_name(f"crawl_{self.progress_id}")

        # Return immediately with task reference
        return {
            "task_id": task_id,
            "status": "started",
            "message": f"Crawl operation started for {url}",
            "progress_id": self.progress_id,
            "task": crawl_task,  # Return the actual task for proper cancellation
        }

    async def _async_orchestrate_crawl(self, request: dict[str, Any], task_id: str):
        """
        Async orchestration that runs in the main event loop.
        Now significantly simplified by delegating to specialized orchestration services.
        """
        # Initialize orchestration helpers
        heartbeat_mgr = HeartbeatManager(
            interval=30.0,
            progress_callback=self._create_heartbeat_callback(task_id),
        )

        source_status_mgr = SourceStatusManager(self.repository)

        progress_tracker = CrawlProgressTracker(
            self.progress_tracker,
            self.progress_mapper,
            task_id,
            self._handle_progress_update,
        )

        doc_processor = DocumentProcessingOrchestrator(
            self.doc_storage_ops,
            self.progress_mapper,
            self.progress_tracker,
        )

        code_orchestrator = CodeExamplesOrchestrator(
            self.doc_storage_ops,
            self.progress_mapper,
            self._check_cancellation,
        )

        url_type_handler = UrlTypeHandler(
            self.url_handler,
            self.crawl_markdown_file,
            self.parse_sitemap,
            self.crawl_batch_with_progress,
            self.crawl_recursive_with_progress,
            self._is_self_link,
        )

        try:
            url = str(request.get("url", ""))
            safe_logfire_info(f"Starting async crawl orchestration | url={url} | task_id={task_id}")

            # Start progress tracking
            await progress_tracker.start(url)

            # Generate source identifiers
            original_source_id = self.url_handler.generate_unique_source_id(url)
            source_display_name = self.url_handler.extract_display_name(url)
            safe_logfire_info(
                f"Generated unique source_id '{original_source_id}' and display name '{source_display_name}' from URL '{url}'"
            )

            # Initial progress
            await progress_tracker.update_mapped(
                "starting", 100, f"Starting crawl of {url}", current_url=url
            )

            # Check for cancellation
            self._check_cancellation()

            # Analyzing stage
            await progress_tracker.update_mapped(
                "analyzing", 50, f"Analyzing URL type for {url}",
                total_pages=1, processed_pages=0
            )

            # Detect URL type and perform crawl
            crawl_results, crawl_type = await url_type_handler.crawl_by_type(
                url,
                request,
                progress_callback=await self._create_crawl_progress_callback("crawling"),
            )

            # Update progress with crawl type
            await progress_tracker.update_with_crawl_type(crawl_type)

            # Check for cancellation and send heartbeat
            self._check_cancellation()
            await heartbeat_mgr.send_if_needed(
                self.progress_mapper.get_current_stage(),
                self.progress_mapper.get_current_progress()
            )

            if not crawl_results:
                raise ValueError("No content was crawled from the provided URL")

            # Processing stage
            await progress_tracker.update_mapped("processing", 50, "Processing crawled content")
            self._check_cancellation()

            # Process and store documents
            storage_results = await doc_processor.process_and_store(
                crawl_results,
                request,
                crawl_type,
                original_source_id,
                self._check_cancellation,
                url,
                source_display_name,
            )

            # Update progress with source_id
            await progress_tracker.update_with_source_id(storage_results.get("source_id"))

            # Check cancellation and send heartbeat
            self._check_cancellation()
            await heartbeat_mgr.send_if_needed(
                self.progress_mapper.get_current_stage(),
                self.progress_mapper.get_current_progress()
            )

            # Extract code examples if requested
            total_pages = len(crawl_results)
            actual_chunks_stored = storage_results.get("chunks_stored", 0)

            code_examples_count = 0
            if actual_chunks_stored > 0:
                await progress_tracker.update_mapped(
                    "code_extraction", 0, "Starting code extraction..."
                )

                code_examples_count = await code_orchestrator.extract_code_examples(
                    request,
                    crawl_results,
                    storage_results["url_to_full_document"],
                    storage_results["source_id"],
                    self.progress_tracker.update if self.progress_tracker else None,
                    total_pages,
                )

                # Check cancellation and send heartbeat
                self._check_cancellation()
                await heartbeat_mgr.send_if_needed(
                    self.progress_mapper.get_current_stage(),
                    self.progress_mapper.get_current_progress()
                )

            # Finalization
            await progress_tracker.update_mapped(
                "finalization", 50, "Finalizing crawl results...",
                chunks_stored=actual_chunks_stored,
                code_examples_found=code_examples_count,
            )

            # Complete progress tracking
            await progress_tracker.update_mapped(
                "completed", 100,
                f"Crawl completed: {actual_chunks_stored} chunks, {code_examples_count} code examples",
                chunks_stored=actual_chunks_stored,
                code_examples_found=code_examples_count,
                processed_pages=len(crawl_results),
                total_pages=len(crawl_results),
            )

            # Mark as completed in progress tracker
            await progress_tracker.complete(
                actual_chunks_stored,
                code_examples_count,
                len(crawl_results),
                len(crawl_results),
                storage_results.get("source_id", ""),
            )

            # Update source status to completed
            source_id = storage_results.get("source_id")
            if source_id:
                await source_status_mgr.update_to_completed(source_id)

            # Unregister after successful completion
            if self.progress_id:
                await unregister_orchestration(self.progress_id)
                safe_logfire_info(
                    f"Unregister orchestration service after completion | progress_id={self.progress_id}"
                )

        except asyncio.CancelledError:
            safe_logfire_info(f"Crawl operation cancelled | progress_id={self.progress_id}")
            cancelled_progress = self.progress_mapper.map_progress("cancelled", 0)
            await self._handle_progress_update(
                task_id,
                {
                    "status": "cancelled",
                    "progress": cancelled_progress,
                    "log": "Crawl operation was cancelled by user",
                },
            )
            if self.progress_id:
                await unregister_orchestration(self.progress_id)
                safe_logfire_info(
                    f"Unregistered orchestration service on cancellation | progress_id={self.progress_id}"
                )

        except Exception as e:
            logger.error("Async crawl orchestration failed", exc_info=True)
            safe_logfire_error(f"Async crawl orchestration failed | error={str(e)}")

            error_message = f"Crawl failed: {str(e)}"
            error_progress = self.progress_mapper.map_progress("error", 0)
            await self._handle_progress_update(
                task_id,
                {
                    "status": "error",
                    "progress": error_progress,
                    "log": error_message,
                    "error": str(e),
                },
            )

            # Mark error in progress tracker
            await progress_tracker.error(error_message)

            # Update source status to failed
            source_id = self.progress_state.get("source_id")
            if source_id:
                await source_status_mgr.update_to_failed(source_id)

            # Unregister on error
            if self.progress_id:
                await unregister_orchestration(self.progress_id)
                safe_logfire_info(
                    f"Unregistered orchestration service on error | progress_id={self.progress_id}"
                )

    def _create_heartbeat_callback(self, task_id: str):
        """Create a callback for heartbeat progress updates."""
        async def callback(stage: str, data: dict[str, Any]):
            await self._handle_progress_update(
                task_id,
                {
                    "status": stage,
                    **data,
                },
            )
        return callback

    def _is_self_link(self, link: str, base_url: str) -> bool:
        """
        Check if a link is a self-referential link to the base URL.
        Handles query parameters, fragments, trailing slashes, and normalizes
        scheme/host/ports for accurate comparison.

        Args:
            link: The link to check
            base_url: The base URL to compare against

        Returns:
            True if the link is self-referential, False otherwise
        """
        try:
            from urllib.parse import urlparse

            def _core(u: str) -> str:
                p = urlparse(u)
                scheme = (p.scheme or "http").lower()
                host = (p.hostname or "").lower()
                port = p.port
                if (scheme == "http" and port in (None, 80)) or (scheme == "https" and port in (None, 443)):
                    port_part = ""
                else:
                    port_part = f":{port}" if port else ""
                path = p.path.rstrip("/")
                return f"{scheme}://{host}{port_part}{path}"

            return _core(link) == _core(base_url)
        except Exception as e:
            logger.warning(f"Error checking if link is self-referential: {e}", exc_info=True)
            # Fallback to simple string comparison
            return link.rstrip('/') == base_url.rstrip('/')

# Alias for backward compatibility
CrawlOrchestrationService = CrawlingService
