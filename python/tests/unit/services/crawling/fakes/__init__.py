"""Fake implementations for testing crawling services."""

from .fake_time_source import FakeTimeSource
from .fake_progress_callback import FakeProgressCallback
from .fake_progress_tracker import FakeProgressTracker
from .fake_progress_mapper import FakeProgressMapper
from .fake_progress_update_handler import FakeProgressUpdateHandler
from .fake_heartbeat_manager import FakeHeartbeatManager
from .fake_source_status_manager import FakeSourceStatusManager
from .fake_crawl_progress_tracker import FakeCrawlProgressTracker
from .fake_document_processing_orchestrator import FakeDocumentProcessingOrchestrator
from .fake_code_examples_orchestrator import FakeCodeExamplesOrchestrator
from .fake_url_type_handler import FakeUrlTypeHandler
from .fake_url_handler import FakeURLHandler
from .fake_site_config import FakeSiteConfig
from .fake_crawl_strategies import (
    FakeBatchCrawlStrategy,
    FakeRecursiveCrawlStrategy,
    FakeSinglePageCrawlStrategy,
    FakeSitemapCrawlStrategy,
)
from .fake_storage_operations import (
    FakeDocumentStorageOperations,
    FakePageStorageOperations,
)

__all__ = [
    "FakeTimeSource",
    "FakeProgressCallback",
    "FakeProgressTracker",
    "FakeProgressMapper",
    "FakeProgressUpdateHandler",
    "FakeHeartbeatManager",
    "FakeSourceStatusManager",
    "FakeCrawlProgressTracker",
    "FakeDocumentProcessingOrchestrator",
    "FakeCodeExamplesOrchestrator",
    "FakeUrlTypeHandler",
    "FakeURLHandler",
    "FakeSiteConfig",
    "FakeBatchCrawlStrategy",
    "FakeRecursiveCrawlStrategy",
    "FakeSinglePageCrawlStrategy",
    "FakeSitemapCrawlStrategy",
    "FakeDocumentStorageOperations",
    "FakePageStorageOperations",
]
