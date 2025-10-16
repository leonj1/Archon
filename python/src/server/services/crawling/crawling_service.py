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
from .helpers.url_validator import UrlValidator

# Import orchestration components
from .orchestration import (
    AsyncCrawlOrchestrator,
    CodeExamplesOrchestrator,
    CrawlOrchestrationConfig,
    CrawlProgressTracker,
    DocumentProcessingOrchestrator,
    HeartbeatManager,
    ProgressCallbackFactory,
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
        self.repository = repository if repository is not None else get_repository()
        self.progress_id = progress_id
        self.progress_tracker = None

        self._init_helpers()
        self._init_strategies(crawler)
        self._init_operations()
        self._init_progress_state()

    def _init_helpers(self):
        """Initialize helper objects."""
        self.url_handler = URLHandler()
        self.site_config = SiteConfig()
        self.markdown_generator = self.site_config.get_markdown_generator()
        self.link_pruning_markdown_generator = self.site_config.get_link_pruning_markdown_generator()

    def _init_strategies(self, crawler):
        """Initialize crawling strategies."""
        self.batch_strategy = BatchCrawlStrategy(crawler, self.link_pruning_markdown_generator)
        self.recursive_strategy = RecursiveCrawlStrategy(crawler, self.link_pruning_markdown_generator)
        self.single_page_strategy = SinglePageCrawlStrategy(crawler, self.markdown_generator)
        self.sitemap_strategy = SitemapCrawlStrategy()

    def _init_operations(self):
        """Initialize storage operations."""
        self.doc_storage_ops = DocumentStorageOperations(repository=self.repository)
        self.page_storage_ops = PageStorageOperations(repository=self.repository)

    def _init_progress_state(self):
        """Initialize progress tracking state."""
        self.progress_state = {"progressId": self.progress_id} if self.progress_id else {}
        self.progress_mapper = ProgressMapper()
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
        factory = ProgressCallbackFactory(
            self.progress_tracker,
            self.progress_mapper,
            self.progress_id,
        )
        return await factory.create_callback(base_status)

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

        task_id = self.progress_id or str(uuid.uuid4())
        await self._register_orchestration()

        crawl_task = self._create_crawl_task(request, task_id)

        return self._build_orchestration_response(task_id, url, crawl_task)

    async def _register_orchestration(self):
        """Register orchestration service for cancellation support."""
        if self.progress_id:
            await register_orchestration(self.progress_id, self)

    def _create_crawl_task(self, request: dict[str, Any], task_id: str):
        """Create and configure the crawl task."""
        crawl_task = asyncio.create_task(self._async_orchestrate_crawl(request, task_id))

        if self.progress_id:
            crawl_task.set_name(f"crawl_{self.progress_id}")

        return crawl_task

    def _build_orchestration_response(self, task_id: str, url: str, crawl_task) -> dict[str, Any]:
        """Build the orchestration response dictionary."""
        return {
            "task_id": task_id,
            "status": "started",
            "message": f"Crawl operation started for {url}",
            "progress_id": self.progress_id,
            "task": crawl_task,
        }

    async def _async_orchestrate_crawl(self, request: dict[str, Any], task_id: str):
        """
        Async orchestration that runs in the main event loop.
        Delegated to AsyncCrawlOrchestrator for cleaner separation of concerns.
        """
        config = self._create_orchestration_config(task_id)
        orchestrator = AsyncCrawlOrchestrator(config)

        try:
            await orchestrator.orchestrate(request, task_id)
            await self._unregister_on_success()

        except asyncio.CancelledError:
            await self._handle_cancellation(task_id)

        except Exception:
            await self._unregister_on_error()

    def _create_orchestration_config(self, task_id: str) -> CrawlOrchestrationConfig:
        """Create configuration for orchestrator."""
        return CrawlOrchestrationConfig(
            heartbeat_mgr=HeartbeatManager(30.0, self._create_heartbeat_callback(task_id)),
            source_status_mgr=SourceStatusManager(self.repository),
            progress_tracker=CrawlProgressTracker(
                self.progress_tracker, self.progress_mapper, task_id, self._handle_progress_update
            ),
            doc_processor=DocumentProcessingOrchestrator(
                self.doc_storage_ops, self.progress_mapper, self.progress_tracker
            ),
            code_orchestrator=CodeExamplesOrchestrator(
                self.doc_storage_ops, self.progress_mapper, self._check_cancellation
            ),
            url_type_handler=UrlTypeHandler(
                self.url_handler, self.crawl_markdown_file, self.parse_sitemap,
                self.crawl_batch_with_progress, self.crawl_recursive_with_progress, self._is_self_link
            ),
            url_handler=self.url_handler,
            progress_mapper=self.progress_mapper,
            progress_state=self.progress_state,
            cancellation_check=self._check_cancellation,
            create_crawl_progress_callback=self._create_crawl_progress_callback,
            handle_progress_update=self._handle_progress_update,
            progress_id=self.progress_id,
        )

    async def _unregister_on_success(self):
        """Unregister orchestration after successful completion."""
        if self.progress_id:
            await unregister_orchestration(self.progress_id)
            safe_logfire_info(
                f"Unregister orchestration service after completion | progress_id={self.progress_id}"
            )

    async def _handle_cancellation(self, task_id: str):
        """Handle cancellation of orchestration."""
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

    async def _unregister_on_error(self):
        """Unregister orchestration after error."""
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
        Delegates to UrlValidator for the actual validation logic.

        Args:
            link: The link to check
            base_url: The base URL to compare against

        Returns:
            True if the link is self-referential, False otherwise
        """
        return UrlValidator.is_self_link(link, base_url)

# Alias for backward compatibility
CrawlOrchestrationService = CrawlingService
