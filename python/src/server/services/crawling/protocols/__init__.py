"""Protocol interfaces for crawling services."""

from .code_examples_orchestrator import ICodeExamplesOrchestrator
from .crawl_progress_tracker import ICrawlProgressTracker
from .crawl_strategies import (
    IBatchCrawlStrategy,
    IRecursiveCrawlStrategy,
    ISinglePageCrawlStrategy,
    ISitemapCrawlStrategy,
)
from .document_processing_orchestrator import IDocumentProcessingOrchestrator
from .heartbeat_manager import IHeartbeatManager
from .progress_callback import IProgressCallback
from .progress_mapper import IProgressMapper
from .progress_tracker import IProgressTracker
from .progress_update_handler import IProgressUpdateHandler
from .site_config import ISiteConfig
from .source_status_manager import ISourceStatusManager
from .storage_operations import IDocumentStorageOperations, IPageStorageOperations
from .time_source import ITimeSource
from .url_handler import IURLHandler
from .url_type_handler import IUrlTypeHandler

__all__ = [
    "ITimeSource",
    "IProgressCallback",
    "IProgressTracker",
    "IProgressMapper",
    "IProgressUpdateHandler",
    "IHeartbeatManager",
    "ISourceStatusManager",
    "ICrawlProgressTracker",
    "IDocumentProcessingOrchestrator",
    "ICodeExamplesOrchestrator",
    "IUrlTypeHandler",
    "IURLHandler",
    "ISiteConfig",
    "IBatchCrawlStrategy",
    "IRecursiveCrawlStrategy",
    "ISinglePageCrawlStrategy",
    "ISitemapCrawlStrategy",
    "IDocumentStorageOperations",
    "IPageStorageOperations",
]
