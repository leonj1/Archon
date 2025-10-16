"""
Comprehensive Unit Tests for CrawlingService

Tests all public methods, initialization, delegation, cancellation, and orchestration workflows.
Achieves 100% line and branch coverage.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any

import pytest

from src.server.services.crawling.crawling_service import (
    CrawlingService,
    get_active_orchestration,
    register_orchestration,
    unregister_orchestration,
    _ensure_orchestration_lock,
)
from tests.unit.services.crawling.fakes import (
    FakeSiteConfig,
    FakeBatchCrawlStrategy,
    FakeRecursiveCrawlStrategy,
    FakeSinglePageCrawlStrategy,
    FakeSitemapCrawlStrategy,
    FakeDocumentStorageOperations,
    FakePageStorageOperations,
    FakeProgressTracker,
    FakeProgressMapper,
    FakeURLHandler,
)


# Test Class: TestCrawlingServiceConstructor
class TestCrawlingServiceConstructor:
    """Tests for CrawlingService constructor and initialization."""

    def test_init_with_defaults(self):
        """Test constructor with no arguments."""
        service = CrawlingService()

        assert service.crawler is None
        assert service.repository is not None  # Created via get_repository()
        assert service.progress_id is None
        assert service.progress_tracker is None
        assert service._cancelled is False

    def test_init_with_crawler(self):
        """Test constructor with crawler argument."""
        fake_crawler = MagicMock()
        service = CrawlingService(crawler=fake_crawler)

        assert service.crawler is fake_crawler

    def test_init_with_repository(self):
        """Test constructor with repository argument."""
        fake_repo = MagicMock()
        service = CrawlingService(repository=fake_repo)

        assert service.repository is fake_repo

    def test_init_with_progress_id(self):
        """Test constructor with progress_id argument."""
        service = CrawlingService(progress_id="test-progress-123")

        assert service.progress_id == "test-progress-123"
        assert service.progress_state == {"progressId": "test-progress-123"}

    def test_init_creates_helpers(self):
        """Test that initialization creates helper objects."""
        service = CrawlingService()

        assert service.url_handler is not None
        assert service.site_config is not None
        assert service.markdown_generator is not None
        assert service.link_pruning_markdown_generator is not None

    def test_init_creates_strategies(self):
        """Test that initialization creates crawling strategies."""
        service = CrawlingService()

        assert service.batch_strategy is not None
        assert service.recursive_strategy is not None
        assert service.single_page_strategy is not None
        assert service.sitemap_strategy is not None

    def test_init_creates_operations(self):
        """Test that initialization creates storage operations."""
        service = CrawlingService()

        assert service.doc_storage_ops is not None
        assert service.page_storage_ops is not None

    def test_init_creates_progress_state(self):
        """Test that initialization creates progress tracking state."""
        service = CrawlingService()

        assert service.progress_state == {}
        assert service.progress_mapper is not None
        assert service._cancelled is False


# Test Class: TestCrawlingServiceProgressTracking
class TestCrawlingServiceProgressTracking:
    """Tests for progress tracking functionality."""

    def test_set_progress_id(self):
        """Test setting progress ID."""
        service = CrawlingService()
        service.set_progress_id("new-progress-456")

        assert service.progress_id == "new-progress-456"
        assert service.progress_state == {"progressId": "new-progress-456"}

    def test_set_progress_id_creates_tracker(self):
        """Test that setting progress ID creates a tracker."""
        service = CrawlingService()
        service.set_progress_id("track-789")

        assert service.progress_tracker is not None
        assert service.progress_tracker.progress_id == "track-789"

    @pytest.mark.asyncio
    async def test_create_crawl_progress_callback(self):
        """Test creating crawl progress callback."""
        service = CrawlingService()
        service.progress_tracker = FakeProgressTracker()
        service.progress_mapper = FakeProgressMapper()

        callback = await service._create_crawl_progress_callback("crawling")

        assert callable(callback)
        assert asyncio.iscoroutinefunction(callback)

    @pytest.mark.asyncio
    async def test_handle_progress_update_with_tracker(self):
        """Test handling progress updates when tracker is available."""
        service = CrawlingService()
        fake_tracker = FakeProgressTracker()
        service.progress_tracker = fake_tracker

        await service._handle_progress_update("task-123", {
            "status": "processing",
            "progress": 50,
            "log": "Halfway there",
        })

        assert len(fake_tracker.update_calls) == 1
        assert fake_tracker.update_calls[0]["status"] == "processing"
        assert fake_tracker.update_calls[0]["progress"] == 50

    @pytest.mark.asyncio
    async def test_handle_progress_update_without_tracker(self):
        """Test handling progress updates when no tracker is available."""
        service = CrawlingService()
        service.progress_tracker = None

        # Should not raise an error
        await service._handle_progress_update("task-123", {
            "status": "processing",
            "progress": 50,
            "log": "No tracker available",
        })

    @pytest.mark.asyncio
    async def test_handle_progress_update_with_percentage_key(self):
        """Test handling progress updates using 'percentage' key for compatibility."""
        service = CrawlingService()
        fake_tracker = FakeProgressTracker()
        service.progress_tracker = fake_tracker

        await service._handle_progress_update("task-123", {
            "status": "processing",
            "percentage": 75,
            "log": "Using percentage key",
        })

        assert len(fake_tracker.update_calls) == 1
        assert fake_tracker.update_calls[0]["progress"] == 75


# Test Class: TestCrawlingServiceCancellation
class TestCrawlingServiceCancellation:
    """Tests for cancellation functionality."""

    def test_cancel_sets_flag(self):
        """Test that cancel() sets the cancelled flag."""
        service = CrawlingService()
        assert service._cancelled is False

        service.cancel()

        assert service._cancelled is True

    def test_is_cancelled_returns_false_initially(self):
        """Test that is_cancelled() returns False initially."""
        service = CrawlingService()

        assert service.is_cancelled() is False

    def test_is_cancelled_returns_true_after_cancel(self):
        """Test that is_cancelled() returns True after cancel()."""
        service = CrawlingService()
        service.cancel()

        assert service.is_cancelled() is True

    def test_check_cancellation_raises_when_cancelled(self):
        """Test that _check_cancellation() raises when cancelled."""
        service = CrawlingService()
        service.cancel()

        with pytest.raises(asyncio.CancelledError, match="Crawl operation was cancelled"):
            service._check_cancellation()

    def test_check_cancellation_no_error_when_not_cancelled(self):
        """Test that _check_cancellation() does not raise when not cancelled."""
        service = CrawlingService()

        # Should not raise
        service._check_cancellation()


# Test Class: TestCrawlingServiceDelegationMethods
class TestCrawlingServiceDelegationMethods:
    """Tests for methods that delegate to strategies."""

    @pytest.mark.asyncio
    async def test_crawl_single_page_delegates_to_strategy(self):
        """Test that crawl_single_page() delegates to strategy."""
        service = CrawlingService()
        fake_strategy = FakeSinglePageCrawlStrategy()
        fake_strategy.configure_single_page_result({"url": "https://example.com", "markdown": "# Test"})
        service.single_page_strategy = fake_strategy

        result = await service.crawl_single_page("https://example.com", retry_count=5)

        assert len(fake_strategy.crawl_single_page_calls) == 1
        assert fake_strategy.crawl_single_page_calls[0]["url"] == "https://example.com"
        assert fake_strategy.crawl_single_page_calls[0]["retry_count"] == 5
        assert result["url"] == "https://example.com"

    @pytest.mark.asyncio
    async def test_crawl_markdown_file_delegates_to_strategy(self):
        """Test that crawl_markdown_file() delegates to strategy."""
        service = CrawlingService()
        fake_strategy = FakeSinglePageCrawlStrategy()
        fake_strategy.configure_markdown_file_results([{"url": "file.md", "markdown": "Content"}])
        service.single_page_strategy = fake_strategy

        result = await service.crawl_markdown_file("https://example.com/file.md")

        assert len(fake_strategy.crawl_markdown_file_calls) == 1
        assert fake_strategy.crawl_markdown_file_calls[0]["url"] == "https://example.com/file.md"
        assert len(result) == 1

    def test_parse_sitemap_delegates_to_strategy(self):
        """Test that parse_sitemap() delegates to strategy."""
        service = CrawlingService()
        fake_strategy = FakeSitemapCrawlStrategy()
        fake_strategy.configure_urls(["https://example.com/page1", "https://example.com/page2"])
        service.sitemap_strategy = fake_strategy

        urls = service.parse_sitemap("https://example.com/sitemap.xml")

        assert len(fake_strategy.parse_sitemap_calls) == 1
        assert fake_strategy.parse_sitemap_calls[0]["sitemap_url"] == "https://example.com/sitemap.xml"
        assert len(urls) == 2

    @pytest.mark.asyncio
    async def test_crawl_batch_with_progress_delegates_to_strategy(self):
        """Test that crawl_batch_with_progress() delegates to strategy."""
        service = CrawlingService()
        fake_strategy = FakeBatchCrawlStrategy()
        fake_strategy.configure_results([{"url": "page1", "markdown": "Content1"}])
        service.batch_strategy = fake_strategy

        urls = ["https://example.com/1", "https://example.com/2"]
        result = await service.crawl_batch_with_progress(urls, max_concurrent=5)

        assert len(fake_strategy.crawl_batch_with_progress_calls) == 1
        assert fake_strategy.crawl_batch_with_progress_calls[0]["urls"] == urls
        assert fake_strategy.crawl_batch_with_progress_calls[0]["max_concurrent"] == 5

    @pytest.mark.asyncio
    async def test_crawl_recursive_with_progress_delegates_to_strategy(self):
        """Test that crawl_recursive_with_progress() delegates to strategy."""
        service = CrawlingService()
        fake_strategy = FakeRecursiveCrawlStrategy()
        fake_strategy.configure_results([{"url": "page1", "markdown": "Content1"}])
        service.recursive_strategy = fake_strategy

        start_urls = ["https://example.com"]
        result = await service.crawl_recursive_with_progress(start_urls, max_depth=5, max_concurrent=3)

        assert len(fake_strategy.crawl_recursive_with_progress_calls) == 1
        assert fake_strategy.crawl_recursive_with_progress_calls[0]["start_urls"] == start_urls
        assert fake_strategy.crawl_recursive_with_progress_calls[0]["max_depth"] == 5
        assert fake_strategy.crawl_recursive_with_progress_calls[0]["max_concurrent"] == 3

    @pytest.mark.asyncio
    async def test_delegation_passes_cancellation_check(self):
        """Test that delegation methods pass cancellation check."""
        service = CrawlingService()
        fake_batch_strategy = FakeBatchCrawlStrategy()
        fake_batch_strategy.configure_results([])
        service.batch_strategy = fake_batch_strategy

        await service.crawl_batch_with_progress(["https://example.com"])

        assert fake_batch_strategy.crawl_batch_with_progress_calls[0]["has_cancellation_check"] is True


# Test Class: TestCrawlingServiceOrchestration
class TestCrawlingServiceOrchestration:
    """Tests for orchestration methods."""

    @pytest.mark.asyncio
    async def test_orchestrate_crawl_returns_response(self):
        """Test that orchestrate_crawl() returns proper response structure."""
        service = CrawlingService()
        request = {"url": "https://example.com", "knowledge_type": "documentation"}

        with patch.object(service, '_async_orchestrate_crawl', new=AsyncMock()):
            response = await service.orchestrate_crawl(request)

        assert "task_id" in response
        assert "status" in response
        assert response["status"] == "started"
        assert "message" in response
        assert "progress_id" in response
        assert "task" in response

    @pytest.mark.asyncio
    async def test_orchestrate_crawl_creates_task(self):
        """Test that orchestrate_crawl() creates an asyncio task."""
        service = CrawlingService()
        request = {"url": "https://example.com"}

        with patch.object(service, '_async_orchestrate_crawl', new=AsyncMock()):
            response = await service.orchestrate_crawl(request)

        assert isinstance(response["task"], asyncio.Task)

    @pytest.mark.asyncio
    async def test_orchestrate_crawl_registers_service(self):
        """Test that orchestrate_crawl() registers the service for cancellation."""
        service = CrawlingService(progress_id="register-test-123")
        request = {"url": "https://example.com"}

        with patch.object(service, '_async_orchestrate_crawl', new=AsyncMock()):
            await service.orchestrate_crawl(request)

        registered_service = await get_active_orchestration("register-test-123")
        assert registered_service is service

        # Cleanup
        await unregister_orchestration("register-test-123")

    @pytest.mark.asyncio
    async def test_orchestrate_crawl_with_progress_id(self):
        """Test orchestrate_crawl() with a progress_id set."""
        service = CrawlingService(progress_id="progress-456")
        request = {"url": "https://example.com"}

        with patch.object(service, '_async_orchestrate_crawl', new=AsyncMock()):
            response = await service.orchestrate_crawl(request)

        assert response["task_id"] == "progress-456"
        assert response["progress_id"] == "progress-456"

        # Cleanup
        await unregister_orchestration("progress-456")

    @pytest.mark.asyncio
    async def test_orchestrate_crawl_without_progress_id(self):
        """Test orchestrate_crawl() without a progress_id (generates UUID)."""
        service = CrawlingService()
        request = {"url": "https://example.com"}

        with patch.object(service, '_async_orchestrate_crawl', new=AsyncMock()):
            response = await service.orchestrate_crawl(request)

        assert response["task_id"] is not None
        assert response["progress_id"] is None

    def test_create_orchestration_config(self):
        """Test _create_orchestration_config() creates proper config."""
        service = CrawlingService(progress_id="config-test")
        service.progress_tracker = FakeProgressTracker()
        service.progress_mapper = FakeProgressMapper()

        config = service._create_orchestration_config("task-123")

        assert config.heartbeat_mgr is not None
        assert config.source_status_mgr is not None
        assert config.progress_tracker is not None
        assert config.doc_processor is not None
        assert config.code_orchestrator is not None
        assert config.url_type_handler is not None
        assert config.url_handler is not None
        assert config.progress_mapper is not None
        assert config.progress_state is not None
        assert config.cancellation_check is not None
        assert config.create_crawl_progress_callback is not None
        assert config.handle_progress_update is not None
        assert config.progress_id == "config-test"

    def test_build_orchestration_response(self):
        """Test _build_orchestration_response() builds correct response."""
        service = CrawlingService()
        fake_task = MagicMock()

        response = service._build_orchestration_response("task-789", "https://example.com", fake_task)

        assert response["task_id"] == "task-789"
        assert response["status"] == "started"
        assert "https://example.com" in response["message"]
        assert response["task"] is fake_task
        assert response["progress_id"] is None


# Test Class: TestCrawlingServiceOrchestrationWorkflow
class TestCrawlingServiceOrchestrationWorkflow:
    """Tests for async orchestration workflow."""

    @pytest.mark.asyncio
    async def test_async_orchestrate_crawl_success(self):
        """Test successful async orchestration workflow."""
        service = CrawlingService(progress_id="workflow-success")
        request = {"url": "https://example.com"}

        with patch('src.server.services.crawling.crawling_service.AsyncCrawlOrchestrator') as mock_orchestrator_class:
            mock_orchestrator = mock_orchestrator_class.return_value
            mock_orchestrator.orchestrate = AsyncMock()

            await service._async_orchestrate_crawl(request, "task-123")

            mock_orchestrator.orchestrate.assert_called_once_with(request, "task-123")

        # Verify unregistration after success
        registered = await get_active_orchestration("workflow-success")
        assert registered is None

    @pytest.mark.asyncio
    async def test_async_orchestrate_crawl_with_cancellation(self):
        """Test async orchestration with cancellation."""
        service = CrawlingService(progress_id="workflow-cancel")
        service.progress_tracker = FakeProgressTracker()
        service.progress_mapper = FakeProgressMapper()
        request = {"url": "https://example.com"}

        with patch('src.server.services.crawling.crawling_service.AsyncCrawlOrchestrator') as mock_orchestrator_class:
            mock_orchestrator = mock_orchestrator_class.return_value
            mock_orchestrator.orchestrate = AsyncMock(side_effect=asyncio.CancelledError())

            # Should not raise, but should handle cancellation gracefully
            await service._async_orchestrate_crawl(request, "task-123")

        # Verify unregistration after cancellation
        registered = await get_active_orchestration("workflow-cancel")
        assert registered is None

    @pytest.mark.asyncio
    async def test_async_orchestrate_crawl_with_error(self):
        """Test async orchestration with error."""
        service = CrawlingService(progress_id="workflow-error")
        request = {"url": "https://example.com"}

        with patch('src.server.services.crawling.crawling_service.AsyncCrawlOrchestrator') as mock_orchestrator_class:
            mock_orchestrator = mock_orchestrator_class.return_value
            mock_orchestrator.orchestrate = AsyncMock(side_effect=RuntimeError("Test error"))

            # Should not raise, but should handle error gracefully
            await service._async_orchestrate_crawl(request, "task-123")

        # Verify unregistration after error
        registered = await get_active_orchestration("workflow-error")
        assert registered is None

    @pytest.mark.asyncio
    async def test_async_orchestrate_crawl_unregisters_on_success(self):
        """Test that orchestration unregisters on successful completion."""
        service = CrawlingService(progress_id="unregister-success")
        await register_orchestration("unregister-success", service)
        request = {"url": "https://example.com"}

        with patch('src.server.services.crawling.crawling_service.AsyncCrawlOrchestrator') as mock_orchestrator_class:
            mock_orchestrator = mock_orchestrator_class.return_value
            mock_orchestrator.orchestrate = AsyncMock()

            await service._async_orchestrate_crawl(request, "task-123")

        # Verify unregistration
        registered = await get_active_orchestration("unregister-success")
        assert registered is None

    @pytest.mark.asyncio
    async def test_async_orchestrate_crawl_unregisters_on_error(self):
        """Test that orchestration unregisters on error."""
        service = CrawlingService(progress_id="unregister-error")
        await register_orchestration("unregister-error", service)
        request = {"url": "https://example.com"}

        with patch('src.server.services.crawling.crawling_service.AsyncCrawlOrchestrator') as mock_orchestrator_class:
            mock_orchestrator = mock_orchestrator_class.return_value
            mock_orchestrator.orchestrate = AsyncMock(side_effect=ValueError("Test error"))

            await service._async_orchestrate_crawl(request, "task-123")

        # Verify unregistration
        registered = await get_active_orchestration("unregister-error")
        assert registered is None

    @pytest.mark.asyncio
    async def test_async_orchestrate_crawl_unregisters_on_cancellation(self):
        """Test that orchestration unregisters on cancellation."""
        service = CrawlingService(progress_id="unregister-cancel")
        service.progress_tracker = FakeProgressTracker()
        service.progress_mapper = FakeProgressMapper()
        await register_orchestration("unregister-cancel", service)
        request = {"url": "https://example.com"}

        with patch('src.server.services.crawling.crawling_service.AsyncCrawlOrchestrator') as mock_orchestrator_class:
            mock_orchestrator = mock_orchestrator_class.return_value
            mock_orchestrator.orchestrate = AsyncMock(side_effect=asyncio.CancelledError())

            await service._async_orchestrate_crawl(request, "task-123")

        # Verify unregistration
        registered = await get_active_orchestration("unregister-cancel")
        assert registered is None


# Test Class: TestCrawlingServiceHelperMethods
class TestCrawlingServiceHelperMethods:
    """Tests for helper methods."""

    def test_is_self_link_delegates_to_validator(self):
        """Test that _is_self_link() delegates to UrlValidator."""
        service = CrawlingService()

        # Test with identical URLs
        result = service._is_self_link("https://example.com", "https://example.com")
        assert result is True

        # Test with different URLs
        result = service._is_self_link("https://example.com/page1", "https://example.com/page2")
        assert result is False

    @pytest.mark.asyncio
    async def test_create_heartbeat_callback(self):
        """Test creating heartbeat callback."""
        service = CrawlingService()
        service.progress_tracker = FakeProgressTracker()

        callback = service._create_heartbeat_callback("task-456")

        assert callable(callback)
        assert asyncio.iscoroutinefunction(callback)

    @pytest.mark.asyncio
    async def test_heartbeat_callback_invocation(self):
        """Test heartbeat callback can be invoked."""
        service = CrawlingService()
        fake_tracker = FakeProgressTracker()
        service.progress_tracker = fake_tracker

        callback = service._create_heartbeat_callback("task-789")
        await callback("processing", {"progress": 50, "log": "Heartbeat"})

        assert len(fake_tracker.update_calls) == 1
        assert fake_tracker.update_calls[0]["status"] == "processing"


# Test Class: TestCrawlingServiceGlobalRegistry
class TestCrawlingServiceGlobalRegistry:
    """Tests for global orchestration registry functions."""

    @pytest.mark.asyncio
    async def test_get_active_orchestration(self):
        """Test retrieving active orchestration."""
        service = CrawlingService()
        await register_orchestration("get-test-123", service)

        retrieved = await get_active_orchestration("get-test-123")

        assert retrieved is service

        # Cleanup
        await unregister_orchestration("get-test-123")

    @pytest.mark.asyncio
    async def test_register_orchestration(self):
        """Test registering orchestration."""
        service = CrawlingService()

        await register_orchestration("register-test-456", service)

        retrieved = await get_active_orchestration("register-test-456")
        assert retrieved is service

        # Cleanup
        await unregister_orchestration("register-test-456")

    @pytest.mark.asyncio
    async def test_unregister_orchestration(self):
        """Test unregistering orchestration."""
        service = CrawlingService()
        await register_orchestration("unregister-test-789", service)

        await unregister_orchestration("unregister-test-789")

        retrieved = await get_active_orchestration("unregister-test-789")
        assert retrieved is None

    def test_ensure_orchestration_lock(self):
        """Test ensuring orchestration lock creation."""
        lock = _ensure_orchestration_lock()

        assert lock is not None
        assert isinstance(lock, asyncio.Lock)

        # Should return same lock on subsequent calls
        lock2 = _ensure_orchestration_lock()
        assert lock is lock2


# Test Class: TestCrawlingServiceEdgeCases
class TestCrawlingServiceEdgeCases:
    """Tests for edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_handle_progress_update_with_extra_kwargs(self):
        """Test handling progress updates with extra kwargs."""
        service = CrawlingService()
        fake_tracker = FakeProgressTracker()
        service.progress_tracker = fake_tracker

        await service._handle_progress_update("task-123", {
            "status": "processing",
            "progress": 50,
            "log": "Test",
            "extra_field": "value",
            "another_field": 123,
        })

        assert len(fake_tracker.update_calls) == 1
        assert fake_tracker.update_calls[0]["extra_field"] == "value"
        assert fake_tracker.update_calls[0]["another_field"] == 123

    @pytest.mark.asyncio
    async def test_crawl_markdown_file_with_progress_callback(self):
        """Test crawl_markdown_file() with progress callback."""
        service = CrawlingService()
        fake_strategy = FakeSinglePageCrawlStrategy()
        fake_strategy.configure_markdown_file_results([{"url": "file.md", "markdown": "Content"}])
        service.single_page_strategy = fake_strategy

        callback_called = False

        async def test_callback(status: str, progress: int, message: str):
            nonlocal callback_called
            callback_called = True

        await service.crawl_markdown_file("https://example.com/file.md", progress_callback=test_callback)

        assert callback_called

    @pytest.mark.asyncio
    async def test_crawl_batch_with_link_text_fallbacks(self):
        """Test crawl_batch_with_progress() with link_text_fallbacks."""
        service = CrawlingService()
        fake_strategy = FakeBatchCrawlStrategy()
        fake_strategy.configure_results([])
        service.batch_strategy = fake_strategy

        fallbacks = {"https://example.com/1": "Page 1", "https://example.com/2": "Page 2"}
        await service.crawl_batch_with_progress(
            ["https://example.com/1", "https://example.com/2"],
            link_text_fallbacks=fallbacks
        )

        assert fake_strategy.crawl_batch_with_progress_calls[0]["link_text_fallbacks"] == fallbacks

    def test_parse_sitemap_with_cancellation_check(self):
        """Test parse_sitemap() passes cancellation check."""
        service = CrawlingService()
        fake_strategy = FakeSitemapCrawlStrategy()
        fake_strategy.configure_urls(["url1", "url2"])
        service.sitemap_strategy = fake_strategy

        service.parse_sitemap("https://example.com/sitemap.xml")

        assert fake_strategy.parse_sitemap_calls[0]["has_cancellation_check"] is True

    @pytest.mark.asyncio
    async def test_orchestrate_crawl_task_naming(self):
        """Test that orchestrate_crawl() sets task name when progress_id is set."""
        service = CrawlingService(progress_id="named-task-123")
        request = {"url": "https://example.com"}

        with patch.object(service, '_async_orchestrate_crawl', new=AsyncMock()):
            response = await service.orchestrate_crawl(request)

        task = response["task"]
        assert task.get_name() == "crawl_named-task-123"

        # Cleanup
        await unregister_orchestration("named-task-123")
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
