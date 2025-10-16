"""
Unit tests for AsyncCrawlOrchestrator

Tests async crawl orchestration workflow with all stages and error handling.
"""

import pytest
from src.server.services.crawling.orchestration.async_crawl_orchestrator import (
    AsyncCrawlOrchestrator,
    CrawlOrchestrationConfig,
)
from tests.unit.services.crawling.fakes import (
    FakeHeartbeatManager,
    FakeSourceStatusManager,
    FakeCrawlProgressTracker,
    FakeDocumentProcessingOrchestrator,
    FakeCodeExamplesOrchestrator,
    FakeUrlTypeHandler,
    FakeURLHandler,
    FakeProgressMapper,
)


class TestAsyncCrawlOrchestratorConstructor:
    """Test constructor and initialization."""

    def test_init_stores_config_fields(self):
        """Test that constructor stores all config fields."""
        fake_heartbeat = FakeHeartbeatManager()
        fake_status_mgr = FakeSourceStatusManager()
        fake_progress_tracker = FakeCrawlProgressTracker()
        fake_doc_processor = FakeDocumentProcessingOrchestrator()
        fake_code_orchestrator = FakeCodeExamplesOrchestrator()
        fake_url_type_handler = FakeUrlTypeHandler()
        fake_url_handler = FakeURLHandler()
        fake_progress_mapper = FakeProgressMapper()
        
        def cancellation_check():
            pass
        
        async def create_callback(stage: str):
            async def callback(status: str, progress: int, message: str):
                pass
            return callback
        
        async def handle_progress(task_id: str, update: dict):
            pass
        
        config = CrawlOrchestrationConfig(
            heartbeat_mgr=fake_heartbeat,
            source_status_mgr=fake_status_mgr,
            progress_tracker=fake_progress_tracker,
            doc_processor=fake_doc_processor,
            code_orchestrator=fake_code_orchestrator,
            url_type_handler=fake_url_type_handler,
            url_handler=fake_url_handler,
            progress_mapper=fake_progress_mapper,
            progress_state={},
            cancellation_check=cancellation_check,
            create_crawl_progress_callback=create_callback,
            handle_progress_update=handle_progress,
            progress_id="test-progress-id",
        )
        
        orchestrator = AsyncCrawlOrchestrator(config)
        
        assert orchestrator.heartbeat_mgr is fake_heartbeat
        assert orchestrator.source_status_mgr is fake_status_mgr
        assert orchestrator.progress_tracker is fake_progress_tracker
        assert orchestrator.doc_processor is fake_doc_processor
        assert orchestrator.code_orchestrator is fake_code_orchestrator
        assert orchestrator.url_type_handler is fake_url_type_handler
        assert orchestrator.url_handler is fake_url_handler
        assert orchestrator.progress_mapper is fake_progress_mapper
        assert orchestrator.progress_id == "test-progress-id"


class TestAsyncCrawlOrchestratorInitializeStage:
    """Test initialization stage."""

    @pytest.mark.asyncio
    async def test_initialize_crawl_starts_progress(self):
        """Test that initialization starts progress tracking."""
        config = create_test_config()
        orchestrator = AsyncCrawlOrchestrator(config)
        
        await orchestrator._initialize_crawl("https://example.com")
        
        assert len(config.progress_tracker.start_calls) == 1
        assert config.progress_tracker.start_calls[0] == "https://example.com"

    @pytest.mark.asyncio
    async def test_initialize_crawl_generates_source_id(self):
        """Test that initialization generates source ID."""
        config = create_test_config()
        orchestrator = AsyncCrawlOrchestrator(config)
        
        await orchestrator._initialize_crawl("https://example.com")
        
        assert len(config.url_handler.generate_id_calls) == 1
        assert config.url_handler.generate_id_calls[0] == "https://example.com"

    @pytest.mark.asyncio
    async def test_initialize_crawl_updates_progress(self):
        """Test that initialization updates progress."""
        config = create_test_config()
        orchestrator = AsyncCrawlOrchestrator(config)
        
        await orchestrator._initialize_crawl("https://example.com")
        
        assert len(config.progress_tracker.update_mapped_calls) == 1
        update = config.progress_tracker.update_mapped_calls[0]
        assert update["stage"] == "starting"
        assert update["progress"] == 100

    @pytest.mark.asyncio
    async def test_initialize_crawl_checks_cancellation(self):
        """Test that initialization checks for cancellation."""
        config = create_test_config()
        config.cancellation_check = lambda: exec('raise Exception("Cancelled")')
        orchestrator = AsyncCrawlOrchestrator(config)
        
        with pytest.raises(Exception, match="Cancelled"):
            await orchestrator._initialize_crawl("https://example.com")


class TestAsyncCrawlOrchestratorPerformCrawlStage:
    """Test perform crawl stage."""

    @pytest.mark.asyncio
    async def test_perform_crawl_updates_progress(self):
        """Test that crawl stage updates progress."""
        config = create_test_config()
        orchestrator = AsyncCrawlOrchestrator(config)
        
        await orchestrator._perform_crawl("https://example.com", {"url": "https://example.com"})
        
        # Check for analyzing progress update
        analyzing_updates = [
            u for u in config.progress_tracker.update_mapped_calls 
            if u["stage"] == "analyzing"
        ]
        assert len(analyzing_updates) == 1

    @pytest.mark.asyncio
    async def test_perform_crawl_calls_url_type_handler(self):
        """Test that crawl stage calls URL type handler."""
        config = create_test_config()
        orchestrator = AsyncCrawlOrchestrator(config)
        
        await orchestrator._perform_crawl("https://example.com", {"url": "https://example.com"})
        
        assert len(config.url_type_handler.crawl_calls) == 1
        call = config.url_type_handler.crawl_calls[0]
        assert call["url"] == "https://example.com"

    @pytest.mark.asyncio
    async def test_perform_crawl_updates_crawl_type(self):
        """Test that crawl stage updates crawl type."""
        config = create_test_config()
        config.url_type_handler.set_results(
            [{"url": "https://example.com", "markdown": "# Test"}],
            "recursive"
        )
        orchestrator = AsyncCrawlOrchestrator(config)
        
        await orchestrator._perform_crawl("https://example.com", {"url": "https://example.com"})
        
        assert len(config.progress_tracker.update_crawl_type_calls) == 1
        assert config.progress_tracker.update_crawl_type_calls[0] == "recursive"

    @pytest.mark.asyncio
    async def test_perform_crawl_sends_heartbeat(self):
        """Test that crawl stage sends heartbeat."""
        config = create_test_config()
        orchestrator = AsyncCrawlOrchestrator(config)
        
        await orchestrator._perform_crawl("https://example.com", {"url": "https://example.com"})
        
        assert len(config.heartbeat_mgr.heartbeat_calls) == 1


class TestAsyncCrawlOrchestratorProcessDocumentsStage:
    """Test process documents stage."""

    @pytest.mark.asyncio
    async def test_process_documents_updates_progress(self):
        """Test that document processing updates progress."""
        config = create_test_config()
        orchestrator = AsyncCrawlOrchestrator(config)
        crawl_results = [{"url": "https://example.com", "markdown": "# Test"}]
        
        await orchestrator._process_documents(
            crawl_results,
            {"url": "https://example.com"},
            "single_page",
            "https://example.com"
        )
        
        processing_updates = [
            u for u in config.progress_tracker.update_mapped_calls 
            if u["stage"] == "processing"
        ]
        assert len(processing_updates) == 1

    @pytest.mark.asyncio
    async def test_process_documents_invokes_processor(self):
        """Test that document processing invokes processor."""
        config = create_test_config()
        orchestrator = AsyncCrawlOrchestrator(config)
        crawl_results = [{"url": "https://example.com", "markdown": "# Test"}]
        
        await orchestrator._process_documents(
            crawl_results,
            {"url": "https://example.com"},
            "single_page",
            "https://example.com"
        )
        
        assert len(config.doc_processor.process_calls) == 1

    @pytest.mark.asyncio
    async def test_process_documents_updates_source_id(self):
        """Test that document processing updates source ID."""
        config = create_test_config()
        config.doc_processor.set_result(source_id="processed-source-id")
        orchestrator = AsyncCrawlOrchestrator(config)
        crawl_results = [{"url": "https://example.com", "markdown": "# Test"}]
        
        await orchestrator._process_documents(
            crawl_results,
            {"url": "https://example.com"},
            "single_page",
            "https://example.com"
        )
        
        assert len(config.progress_tracker.update_source_id_calls) == 1
        assert config.progress_tracker.update_source_id_calls[0] == "processed-source-id"


class TestAsyncCrawlOrchestratorCodeExtractionStage:
    """Test code extraction stage."""

    @pytest.mark.asyncio
    async def test_extract_code_examples_with_zero_chunks(self):
        """Test that code extraction returns 0 when no chunks stored."""
        config = create_test_config()
        config.doc_processor.set_result(chunks_stored=0)
        orchestrator = AsyncCrawlOrchestrator(config)
        
        storage_results = {"chunks_stored": 0, "url_to_full_document": {}}
        code_count = await orchestrator._extract_code_examples(
            {"url": "https://example.com"},
            [],
            storage_results,
            1
        )
        
        assert code_count == 0
        assert len(config.code_orchestrator.extract_calls) == 0

    @pytest.mark.asyncio
    async def test_extract_code_examples_updates_progress(self):
        """Test that code extraction updates progress."""
        config = create_test_config()
        orchestrator = AsyncCrawlOrchestrator(config)
        
        storage_results = {"chunks_stored": 10, "url_to_full_document": {}, "source_id": "src-id"}
        await orchestrator._extract_code_examples(
            {"url": "https://example.com"},
            [{"url": "https://example.com", "markdown": "# Test"}],
            storage_results,
            1
        )
        
        code_updates = [
            u for u in config.progress_tracker.update_mapped_calls 
            if u["stage"] == "code_extraction"
        ]
        assert len(code_updates) == 1

    @pytest.mark.asyncio
    async def test_extract_code_examples_invokes_orchestrator(self):
        """Test that code extraction invokes code orchestrator."""
        config = create_test_config()
        config.code_orchestrator.set_code_count(7)
        orchestrator = AsyncCrawlOrchestrator(config)
        
        storage_results = {"chunks_stored": 10, "url_to_full_document": {}, "source_id": "src-id"}
        code_count = await orchestrator._extract_code_examples(
            {"url": "https://example.com"},
            [{"url": "https://example.com", "markdown": "# Test"}],
            storage_results,
            1
        )
        
        assert code_count == 7
        assert len(config.code_orchestrator.extract_calls) == 1


class TestAsyncCrawlOrchestratorFinalizeStage:
    """Test finalize stage."""

    @pytest.mark.asyncio
    async def test_finalize_crawl_updates_all_progress(self):
        """Test that finalization updates all progress stages."""
        config = create_test_config()
        orchestrator = AsyncCrawlOrchestrator(config)
        
        storage_results = {"source_id": "src-id", "chunks_stored": 10, "url_to_full_document": {}}
        await orchestrator._finalize_crawl(storage_results, 5, 10)
        
        # Should have finalization and completion updates
        finalization_updates = [
            u for u in config.progress_tracker.update_mapped_calls 
            if u["stage"] == "finalization"
        ]
        completion_updates = [
            u for u in config.progress_tracker.update_mapped_calls 
            if u["stage"] == "completed"
        ]
        
        assert len(finalization_updates) == 1
        assert len(completion_updates) == 1

    @pytest.mark.asyncio
    async def test_finalize_crawl_completes_tracker(self):
        """Test that finalization completes progress tracker."""
        config = create_test_config()
        orchestrator = AsyncCrawlOrchestrator(config)
        
        storage_results = {"source_id": "src-id", "chunks_stored": 10, "url_to_full_document": {}}
        await orchestrator._finalize_crawl(storage_results, 5, 10)
        
        assert len(config.progress_tracker.complete_calls) == 1
        complete_call = config.progress_tracker.complete_calls[0]
        assert complete_call["chunks"] == 10
        assert complete_call["code"] == 5
        assert complete_call["source_id"] == "src-id"

    @pytest.mark.asyncio
    async def test_finalize_crawl_updates_source_status(self):
        """Test that finalization updates source status."""
        config = create_test_config()
        orchestrator = AsyncCrawlOrchestrator(config)
        
        storage_results = {"source_id": "src-id", "chunks_stored": 10, "url_to_full_document": {}}
        await orchestrator._finalize_crawl(storage_results, 5, 10)
        
        assert config.source_status_mgr.was_completed("src-id")


class TestAsyncCrawlOrchestratorErrorHandling:
    """Test error handling."""

    @pytest.mark.asyncio
    async def test_handle_error_updates_progress(self):
        """Test that error handler updates progress."""
        config = create_test_config()
        orchestrator = AsyncCrawlOrchestrator(config)
        
        error = ValueError("Test error")
        await orchestrator._handle_error(error, "task-123")
        
        assert len(config.progress_tracker.error_calls) == 1
        assert "Test error" in config.progress_tracker.error_calls[0]

    @pytest.mark.asyncio
    async def test_handle_error_with_source_id(self):
        """Test error handling with source ID in state."""
        config = create_test_config()
        config.progress_state["source_id"] = "src-id"
        orchestrator = AsyncCrawlOrchestrator(config)
        
        error = ValueError("Test error")
        await orchestrator._handle_error(error, "task-123")
        
        assert config.source_status_mgr.was_failed("src-id")

    @pytest.mark.asyncio
    async def test_handle_error_without_source_id(self):
        """Test error handling without source ID."""
        config = create_test_config()
        orchestrator = AsyncCrawlOrchestrator(config)
        
        error = ValueError("Test error")
        await orchestrator._handle_error(error, "task-123")
        
        # Should not fail even without source_id
        assert len(config.source_status_mgr.failed_sources) == 0


class TestAsyncCrawlOrchestratorFullWorkflow:
    """Test full orchestration workflow."""

    @pytest.mark.asyncio
    async def test_orchestrate_success_workflow(self):
        """Test successful orchestration workflow."""
        config = create_test_config()
        config.url_type_handler.set_results(
            [{"url": "https://example.com", "markdown": "# Test Content"}],
            "single_page"
        )
        config.doc_processor.set_result(
            source_id="final-source-id",
            chunks_stored=15,
            url_to_full_document={"https://example.com": "Full content"}
        )
        config.code_orchestrator.set_code_count(8)
        
        orchestrator = AsyncCrawlOrchestrator(config)
        
        request = {"url": "https://example.com"}
        await orchestrator.orchestrate(request, "task-123")
        
        # Verify all stages completed
        assert len(config.progress_tracker.start_calls) == 1
        assert len(config.url_type_handler.crawl_calls) == 1
        assert len(config.doc_processor.process_calls) == 1
        assert len(config.code_orchestrator.extract_calls) == 1
        assert len(config.progress_tracker.complete_calls) == 1
        assert config.source_status_mgr.was_completed("final-source-id")

    @pytest.mark.asyncio
    async def test_orchestrate_with_error(self):
        """Test orchestration with error during workflow."""
        config = create_test_config()
        config.url_type_handler.configure_failure(ValueError("Crawl failed"))
        
        orchestrator = AsyncCrawlOrchestrator(config)
        
        request = {"url": "https://example.com"}
        with pytest.raises(ValueError, match="Crawl failed"):
            await orchestrator.orchestrate(request, "task-123")
        
        # Verify error was handled
        assert len(config.progress_tracker.error_calls) == 1

    @pytest.mark.asyncio
    async def test_orchestrate_no_content_error(self):
        """Test orchestration with no content crawled."""
        config = create_test_config()
        config.url_type_handler.set_results([], "single_page")
        
        orchestrator = AsyncCrawlOrchestrator(config)
        
        request = {"url": "https://example.com"}
        with pytest.raises(ValueError, match="No content was crawled"):
            await orchestrator.orchestrate(request, "task-123")


# Helper function to create test config
def create_test_config():
    """Create a test configuration with all fakes."""
    fake_heartbeat = FakeHeartbeatManager()
    fake_status_mgr = FakeSourceStatusManager()
    fake_progress_tracker = FakeCrawlProgressTracker()
    fake_doc_processor = FakeDocumentProcessingOrchestrator()
    fake_code_orchestrator = FakeCodeExamplesOrchestrator()
    fake_url_type_handler = FakeUrlTypeHandler()
    fake_url_handler = FakeURLHandler()
    fake_progress_mapper = FakeProgressMapper()
    progress_state = {}
    
    def cancellation_check():
        pass
    
    async def create_callback(stage: str):
        async def callback(status: str, progress: int, message: str, **kwargs):
            pass
        return callback
    
    async def handle_progress(task_id: str, update: dict):
        pass
    
    config = CrawlOrchestrationConfig(
        heartbeat_mgr=fake_heartbeat,
        source_status_mgr=fake_status_mgr,
        progress_tracker=fake_progress_tracker,
        doc_processor=fake_doc_processor,
        code_orchestrator=fake_code_orchestrator,
        url_type_handler=fake_url_type_handler,
        url_handler=fake_url_handler,
        progress_mapper=fake_progress_mapper,
        progress_state=progress_state,
        cancellation_check=cancellation_check,
        create_crawl_progress_callback=create_callback,
        handle_progress_update=handle_progress,
        progress_id="test-progress-id",
    )
    
    return config
