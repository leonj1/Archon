# Test Plan: Crawling Services

## Overview

This test plan covers comprehensive testing for four core crawling service modules:
1. `CrawlingService` - Main orchestration and service coordination
2. `AsyncCrawlOrchestrator` - Async workflow execution
3. `ProgressCallbackFactory` - Progress callback creation
4. `UrlValidator` - URL validation utilities

All tests will be written using pytest with async support and will follow the established patterns in the codebase.

---

## 1. CrawlingService (`crawling_service.py`)

### 1.1 Purity Analysis

| Function | Type | Reason | Testability |
|----------|------|--------|-------------|
| `__init__` | Impure | Creates dependencies, initializes state | Needs injection |
| `_init_helpers` | Impure | Creates helper instances | Needs mocking |
| `_init_strategies` | Impure | Creates strategy instances | Needs mocking |
| `_init_operations` | Impure | Creates storage operations | Needs repository mock |
| `_init_progress_state` | Pure | Only manipulates instance state | Easy to test |
| `set_progress_id` | Impure | Creates ProgressTracker | Needs fake |
| `cancel` | Pure | Sets boolean flag | Easy to test |
| `is_cancelled` | Pure | Returns boolean | Easy to test |
| `_check_cancellation` | Pure | Conditional exception | Easy to test |
| `_create_crawl_progress_callback` | Impure | Async I/O, creates factory | Needs fake |
| `_handle_progress_update` | Impure | Async I/O, updates tracker | Needs fake |
| `crawl_single_page` | Impure | Delegates to strategy | Needs mock |
| `crawl_markdown_file` | Impure | Delegates to strategy | Needs mock |
| `parse_sitemap` | Pure | Delegates to strategy | Needs mock |
| `crawl_batch_with_progress` | Impure | Async delegation | Needs mock |
| `crawl_recursive_with_progress` | Impure | Async delegation | Needs mock |
| `orchestrate_crawl` | Impure | Creates async tasks, registers | Complex integration |
| `_register_orchestration` | Impure | Global state mutation | Needs testing |
| `_create_crawl_task` | Impure | Creates asyncio task | Needs testing |
| `_build_orchestration_response` | Pure | Builds dict | Easy to test |
| `_async_orchestrate_crawl` | Impure | Full orchestration workflow | Complex integration |
| `_create_orchestration_config` | Pure | Creates dataclass | Easy to test |
| `_unregister_on_success` | Impure | Global state mutation | Needs testing |
| `_handle_cancellation` | Impure | Async progress updates | Needs fake |
| `_unregister_on_error` | Impure | Global state mutation | Needs testing |
| `_create_heartbeat_callback` | Pure | Returns closure | Easy to test |
| `_is_self_link` | Pure | Delegates to UrlValidator | Easy to test |

### 1.2 External Dependencies

#### Required Interfaces

1. **ICrawler** (Crawl4AI crawler)
   - Purpose: Web crawling operations
   - Methods: Used by strategies (not directly by service)
   - Fake: Not directly needed (strategies mocked)

2. **IDatabaseRepository** (Already exists as Protocol)
   - Purpose: Database operations
   - Methods: All methods from `DatabaseRepository` ABC
   - Fake: `FakeDatabaseRepository` (needs creation)

3. **IProgressTracker** (Needs Protocol)
   - Purpose: Progress tracking for HTTP polling
   - Methods:
     - `async start(initial_data: dict) -> None`
     - `async update(status: str, progress: int, log: str, **kwargs) -> None`
     - `async complete(completion_data: dict) -> None`
     - `async error(error_message: str) -> None`
   - Fake: `FakeProgressTracker` (already exists)

4. **IProgressMapper** (Needs Protocol)
   - Purpose: Map stage progress to overall progress
   - Methods:
     - `map_progress(stage: str, stage_progress: float) -> int`
     - `get_current_stage() -> str`
     - `get_current_progress() -> int`
   - Fake: `FakeProgressMapper` (already exists)

5. **IURLHandler** (Needs Protocol)
   - Purpose: URL transformation and manipulation
   - Methods:
     - `transform_github_url(url: str) -> str`
     - `generate_unique_source_id(url: str) -> str`
     - `extract_display_name(url: str) -> str`
   - Fake: `FakeURLHandler` (needs creation)

6. **ISiteConfig** (Needs Protocol)
   - Purpose: Site configuration and markdown generation
   - Methods:
     - `is_documentation_site(url: str) -> bool`
     - `get_markdown_generator() -> Any`
     - `get_link_pruning_markdown_generator() -> Any`
   - Fake: `FakeSiteConfig` (needs creation)

7. **Crawling Strategies** (Need Protocols)
   - IBatchCrawlStrategy, IRecursiveCrawlStrategy, ISinglePageCrawlStrategy, ISitemapCrawlStrategy
   - Methods: Strategy-specific crawling methods
   - Fake: Mock via dependency injection

8. **Storage Operations** (Need Protocols)
   - IDocumentStorageOperations, IPageStorageOperations
   - Methods: Storage-specific methods
   - Fake: Mock via dependency injection

### 1.3 Interface Extraction Plan

#### IProgressTracker Protocol
```python
# Location: python/src/server/services/crawling/protocols/progress_tracker_protocol.py
from typing import Protocol, Any

class IProgressTracker(Protocol):
    """Protocol for progress tracking operations."""

    async def start(self, initial_data: dict[str, Any]) -> None:
        """Start progress tracking with initial data."""
        ...

    async def update(self, status: str, progress: int, log: str, **kwargs: Any) -> None:
        """Update progress with status, progress percentage, and log message."""
        ...

    async def complete(self, completion_data: dict[str, Any]) -> None:
        """Mark progress as completed with optional completion data."""
        ...

    async def error(self, error_message: str) -> None:
        """Mark progress as failed with error message."""
        ...
```

#### IProgressMapper Protocol
```python
# Location: python/src/server/services/crawling/protocols/progress_mapper_protocol.py
from typing import Protocol

class IProgressMapper(Protocol):
    """Protocol for mapping stage progress to overall progress."""

    def map_progress(self, stage: str, stage_progress: float) -> int:
        """Map stage-specific progress to overall progress percentage."""
        ...

    def get_current_stage(self) -> str:
        """Get the current stage name."""
        ...

    def get_current_progress(self) -> int:
        """Get the current overall progress percentage."""
        ...
```

#### IURLHandler Protocol
```python
# Location: python/src/server/services/crawling/protocols/url_handler_protocol.py
from typing import Protocol

class IURLHandler(Protocol):
    """Protocol for URL handling operations."""

    def transform_github_url(self, url: str) -> str:
        """Transform GitHub URLs to raw content URLs."""
        ...

    def generate_unique_source_id(self, url: str) -> str:
        """Generate a unique source ID from URL."""
        ...

    def extract_display_name(self, url: str) -> str:
        """Extract a display name from URL."""
        ...
```

#### ISiteConfig Protocol
```python
# Location: python/src/server/services/crawling/protocols/site_config_protocol.py
from typing import Protocol, Any

class ISiteConfig(Protocol):
    """Protocol for site configuration operations."""

    def is_documentation_site(self, url: str) -> bool:
        """Check if URL is a documentation site."""
        ...

    def get_markdown_generator(self) -> Any:
        """Get markdown generator for standard content."""
        ...

    def get_link_pruning_markdown_generator(self) -> Any:
        """Get markdown generator with link pruning."""
        ...
```

### 1.4 Fake Implementations Required

1. **FakeDatabaseRepository**
   - In-memory storage using dictionaries
   - Implements all DatabaseRepository methods
   - Tracks method calls for assertions
   - Location: `tests/unit/services/crawling/fakes/fake_database_repository.py`

2. **FakeURLHandler**
   - Returns predictable source IDs
   - Simple display name extraction
   - No-op GitHub URL transformation for testing
   - Location: `tests/unit/services/crawling/fakes/fake_url_handler.py`

3. **FakeSiteConfig**
   - Configurable documentation site detection
   - Returns fake markdown generators
   - Location: `tests/unit/services/crawling/fakes/fake_site_config.py`

4. **FakeCrawlStrategy** (Base)
   - Returns configurable crawl results
   - Tracks invocations
   - Location: `tests/unit/services/crawling/fakes/fake_crawl_strategy.py`

5. **FakeStorageOperations**
   - In-memory storage tracking
   - Returns configurable results
   - Location: `tests/unit/services/crawling/fakes/fake_storage_operations.py`

### 1.5 Test Scenarios

#### Test Class: TestCrawlingServiceConstructor
- `test_init_with_defaults` - Constructor with no args
- `test_init_with_crawler` - Constructor with crawler
- `test_init_with_repository` - Constructor with repository
- `test_init_with_progress_id` - Constructor with progress ID
- `test_init_creates_helpers` - Verify helpers initialized
- `test_init_creates_strategies` - Verify strategies initialized
- `test_init_creates_operations` - Verify operations initialized
- `test_init_creates_progress_state` - Verify progress state initialized

#### Test Class: TestCrawlingServiceProgressTracking
- `test_set_progress_id` - Setting progress ID
- `test_set_progress_id_creates_tracker` - Tracker creation
- `test_create_crawl_progress_callback` - Callback creation
- `test_handle_progress_update_with_tracker` - Progress updates with tracker
- `test_handle_progress_update_without_tracker` - Progress updates without tracker

#### Test Class: TestCrawlingServiceCancellation
- `test_cancel_sets_flag` - Cancel sets cancelled flag
- `test_is_cancelled_returns_false_initially` - Initial state
- `test_is_cancelled_returns_true_after_cancel` - After cancel
- `test_check_cancellation_raises_when_cancelled` - Exception on cancel
- `test_check_cancellation_no_error_when_not_cancelled` - No error when active

#### Test Class: TestCrawlingServiceDelegationMethods
- `test_crawl_single_page_delegates_to_strategy` - Single page delegation
- `test_crawl_markdown_file_delegates_to_strategy` - Markdown file delegation
- `test_parse_sitemap_delegates_to_strategy` - Sitemap delegation
- `test_crawl_batch_with_progress_delegates_to_strategy` - Batch delegation
- `test_crawl_recursive_with_progress_delegates_to_strategy` - Recursive delegation
- `test_delegation_passes_cancellation_check` - Cancellation check passed

#### Test Class: TestCrawlingServiceOrchestration
- `test_orchestrate_crawl_returns_response` - Response structure
- `test_orchestrate_crawl_creates_task` - Task creation
- `test_orchestrate_crawl_registers_service` - Service registration
- `test_orchestrate_crawl_with_progress_id` - With progress ID
- `test_orchestrate_crawl_without_progress_id` - Without progress ID
- `test_create_orchestration_config` - Config creation
- `test_build_orchestration_response` - Response building

#### Test Class: TestCrawlingServiceOrchestrationWorkflow
- `test_async_orchestrate_crawl_success` - Successful workflow
- `test_async_orchestrate_crawl_with_cancellation` - Cancelled workflow
- `test_async_orchestrate_crawl_with_error` - Error handling
- `test_async_orchestrate_crawl_unregisters_on_success` - Cleanup on success
- `test_async_orchestrate_crawl_unregisters_on_error` - Cleanup on error
- `test_async_orchestrate_crawl_unregisters_on_cancellation` - Cleanup on cancel

#### Test Class: TestCrawlingServiceHelperMethods
- `test_is_self_link_delegates_to_validator` - Delegation to UrlValidator
- `test_create_heartbeat_callback` - Heartbeat callback creation
- `test_heartbeat_callback_invocation` - Callback invocation

#### Test Class: TestCrawlingServiceGlobalRegistry
- `test_get_active_orchestration` - Retrieve active orchestration
- `test_register_orchestration` - Register orchestration
- `test_unregister_orchestration` - Unregister orchestration
- `test_ensure_orchestration_lock` - Lock creation

#### Test Class: TestCrawlingServiceIntegration
- `test_full_crawl_workflow` - End-to-end workflow
- `test_concurrent_orchestrations` - Multiple concurrent crawls
- `test_crawl_with_code_extraction` - Full workflow with code extraction
- `test_crawl_error_recovery` - Error handling and recovery

### 1.6 Coverage Target

- **Lines**: 100%
- **Branches**: 100%
- **Functions**: 100%
- **Integration**: Full workflow coverage

---

## 2. AsyncCrawlOrchestrator (`async_crawl_orchestrator.py`)

### 2.1 Purity Analysis

| Function | Type | Reason | Testability |
|----------|------|--------|-------------|
| `__init__` | Pure | Only assigns config fields | Easy to test |
| `orchestrate` | Impure | Async workflow coordination | Integration test |
| `_execute_crawl_workflow` | Impure | Async workflow stages | Integration test |
| `_initialize_crawl` | Impure | Async progress tracking | Needs fake |
| `_perform_crawl` | Impure | Async crawling operations | Needs fake |
| `_process_documents` | Impure | Async document processing | Needs fake |
| `_extract_code_examples` | Impure | Async code extraction | Needs fake |
| `_finalize_crawl` | Impure | Async finalization | Needs fake |
| `_update_finalization_progress` | Impure | Async progress update | Needs fake |
| `_update_completion_progress` | Impure | Async progress update | Needs fake |
| `_complete_progress_tracker` | Impure | Async progress completion | Needs fake |
| `_update_source_status` | Impure | Async database update | Needs fake |
| `_send_heartbeat` | Impure | Async heartbeat | Needs fake |
| `_handle_error` | Impure | Async error handling | Needs fake |

### 2.2 External Dependencies

#### Required Interfaces

1. **IHeartbeatManager** (Needs Protocol)
   - Methods:
     - `async send_if_needed(stage: str, progress: int) -> None`
   - Fake: `FakeHeartbeatManager` (needs creation)

2. **ISourceStatusManager** (Needs Protocol)
   - Methods:
     - `async update_to_completed(source_id: str) -> None`
     - `async update_to_failed(source_id: str) -> None`
   - Fake: `FakeSourceStatusManager` (needs creation)

3. **ICrawlProgressTracker** (Needs Protocol)
   - Methods:
     - `async start(url: str) -> None`
     - `async update_mapped(stage: str, progress: int, message: str, **kwargs) -> None`
     - `async update_with_crawl_type(crawl_type: str) -> None`
     - `async update_with_source_id(source_id: str) -> None`
     - `async complete(chunks: int, code: int, processed: int, total: int, source_id: str) -> None`
     - `async error(message: str) -> None`
   - Fake: `FakeCrawlProgressTracker` (needs creation)

4. **IDocumentProcessingOrchestrator** (Needs Protocol)
   - Methods:
     - `async process_and_store(...) -> dict[str, Any]`
   - Fake: `FakeDocumentProcessingOrchestrator` (needs creation)

5. **ICodeExamplesOrchestrator** (Needs Protocol)
   - Methods:
     - `async extract_code_examples(...) -> int`
   - Fake: `FakeCodeExamplesOrchestrator` (needs creation)

6. **IUrlTypeHandler** (Needs Protocol)
   - Methods:
     - `async crawl_by_type(...) -> tuple[list[dict], str]`
   - Fake: `FakeUrlTypeHandler` (needs creation)

### 2.3 Test Scenarios

#### Test Class: TestAsyncCrawlOrchestratorConstructor
- `test_init_stores_config_fields` - All config fields stored
- `test_init_with_minimal_config` - Minimal config
- `test_init_with_full_config` - Full config with all dependencies

#### Test Class: TestAsyncCrawlOrchestratorInitializeStage
- `test_initialize_crawl_starts_progress` - Progress tracking started
- `test_initialize_crawl_generates_source_id` - Source ID generation
- `test_initialize_crawl_updates_progress` - Initial progress update
- `test_initialize_crawl_checks_cancellation` - Cancellation check
- `test_initialize_crawl_with_cancellation` - Cancellation during init

#### Test Class: TestAsyncCrawlOrchestratorPerformCrawlStage
- `test_perform_crawl_updates_progress` - Progress updates
- `test_perform_crawl_calls_url_type_handler` - URL type handler invoked
- `test_perform_crawl_updates_crawl_type` - Crawl type updated
- `test_perform_crawl_sends_heartbeat` - Heartbeat sent
- `test_perform_crawl_checks_cancellation` - Cancellation check
- `test_perform_crawl_with_progress_callback` - Callback passed

#### Test Class: TestAsyncCrawlOrchestratorProcessDocumentsStage
- `test_process_documents_updates_progress` - Progress updates
- `test_process_documents_invokes_processor` - Processor invoked
- `test_process_documents_updates_source_id` - Source ID updated
- `test_process_documents_sends_heartbeat` - Heartbeat sent
- `test_process_documents_checks_cancellation` - Cancellation check
- `test_process_documents_with_empty_results` - Empty results handling

#### Test Class: TestAsyncCrawlOrchestratorCodeExtractionStage
- `test_extract_code_examples_updates_progress` - Progress updates
- `test_extract_code_examples_invokes_orchestrator` - Code orchestrator invoked
- `test_extract_code_examples_sends_heartbeat` - Heartbeat sent
- `test_extract_code_examples_checks_cancellation` - Cancellation check
- `test_extract_code_examples_with_zero_chunks` - Zero chunks stored
- `test_extract_code_examples_returns_count` - Code count returned

#### Test Class: TestAsyncCrawlOrchestratorFinalizeStage
- `test_finalize_crawl_updates_all_progress` - All progress updates
- `test_finalize_crawl_completes_tracker` - Tracker completion
- `test_finalize_crawl_updates_source_status` - Source status updated
- `test_finalize_crawl_with_code_examples` - With code examples
- `test_finalize_crawl_without_code_examples` - Without code examples

#### Test Class: TestAsyncCrawlOrchestratorErrorHandling
- `test_handle_error_logs_error` - Error logging
- `test_handle_error_updates_progress` - Progress error update
- `test_handle_error_updates_source_status` - Source status updated
- `test_handle_error_with_source_id` - With source ID
- `test_handle_error_without_source_id` - Without source ID

#### Test Class: TestAsyncCrawlOrchestratorFullWorkflow
- `test_orchestrate_success_workflow` - Full success path
- `test_orchestrate_with_cancellation` - Cancellation during workflow
- `test_orchestrate_with_error` - Error during workflow
- `test_orchestrate_no_content_error` - No content error
- `test_orchestrate_multiple_stages` - Multiple stage transitions

### 2.4 Coverage Target

- **Lines**: 100%
- **Branches**: 100%
- **Functions**: 100%

---

## 3. ProgressCallbackFactory (`progress_callback_factory.py`)

### 3.1 Purity Analysis

| Function | Type | Reason | Testability |
|----------|------|--------|-------------|
| `__init__` | Pure | Only assigns fields | Easy to test |
| `create_callback` | Impure | Returns async closure | Needs integration |
| `callback` (closure) | Impure | Async progress updates | Needs fake |
| `_log_callback_received` | Pure | Logging only | Easy to test |
| `_log_progress_updated` | Pure | Logging only | Easy to test |

### 3.2 External Dependencies

Already covered by IProgressTracker and IProgressMapper protocols.

### 3.3 Test Scenarios

#### Test Class: TestProgressCallbackFactoryConstructor
- `test_init_stores_dependencies` - Dependencies stored
- `test_init_with_none_tracker` - None tracker allowed
- `test_init_with_none_progress_id` - None progress ID allowed

#### Test Class: TestProgressCallbackFactoryCreateCallback
- `test_create_callback_returns_callable` - Returns callable
- `test_create_callback_is_async` - Callback is async

#### Test Class: TestProgressCallbackFactoryCallbackInvocation
- `test_callback_updates_tracker` - Tracker updated
- `test_callback_maps_progress` - Progress mapped
- `test_callback_with_kwargs` - Extra kwargs passed
- `test_callback_without_tracker` - No-op without tracker
- `test_callback_logs_received` - Callback received logged
- `test_callback_logs_updated` - Progress updated logged

#### Test Class: TestProgressCallbackFactoryProgressMapping
- `test_callback_maps_with_base_status` - Base status used for mapping
- `test_callback_preserves_status` - Original status preserved
- `test_callback_raw_vs_mapped_progress` - Raw vs mapped values

#### Test Class: TestProgressCallbackFactoryEdgeCases
- `test_callback_with_zero_progress` - Zero progress
- `test_callback_with_hundred_progress` - 100% progress
- `test_callback_with_empty_message` - Empty message
- `test_callback_with_special_characters` - Special characters in message

### 3.4 Coverage Target

- **Lines**: 100%
- **Branches**: 100%
- **Functions**: 100%

---

## 4. UrlValidator (`url_validator.py`)

### 4.1 Purity Analysis

| Function | Type | Reason | Testability |
|----------|------|--------|-------------|
| `is_self_link` | Pure | Deterministic URL comparison | Easy to test |
| `_compare_normalized_urls` | Pure | URL parsing and comparison | Easy to test |
| `_normalize_url` | Pure | String manipulation | Easy to test |
| `_get_port_part` | Pure | Conditional string building | Easy to test |
| `_fallback_comparison` | Pure | String comparison | Easy to test |

### 4.2 External Dependencies

**None** - This is a pure utility class with no external dependencies.

### 4.3 Test Scenarios

#### Test Class: TestUrlValidatorSelfLinkDetection
- `test_is_self_link_identical_urls` - Identical URLs
- `test_is_self_link_with_trailing_slash` - Trailing slash handling
- `test_is_self_link_with_fragment` - Fragment differences
- `test_is_self_link_with_query_params` - Query parameter differences
- `test_is_self_link_different_domains` - Different domains
- `test_is_self_link_different_paths` - Different paths

#### Test Class: TestUrlValidatorNormalization
- `test_normalize_url_lowercase_scheme` - Scheme normalization
- `test_normalize_url_lowercase_host` - Host normalization
- `test_normalize_url_removes_trailing_slash` - Trailing slash removal
- `test_normalize_url_default_http_port` - HTTP default port
- `test_normalize_url_default_https_port` - HTTPS default port
- `test_normalize_url_custom_port` - Custom port preservation
- `test_normalize_url_no_scheme` - Missing scheme handling

#### Test Class: TestUrlValidatorPortHandling
- `test_get_port_part_http_default` - HTTP port 80 omitted
- `test_get_port_part_https_default` - HTTPS port 443 omitted
- `test_get_port_part_custom_port` - Custom port included
- `test_get_port_part_none_port` - None port handling

#### Test Class: TestUrlValidatorFallback
- `test_fallback_comparison_identical` - Identical URLs
- `test_fallback_comparison_trailing_slash` - Trailing slash differences
- `test_fallback_comparison_different_urls` - Different URLs

#### Test Class: TestUrlValidatorErrorHandling
- `test_is_self_link_invalid_link` - Invalid link URL
- `test_is_self_link_invalid_base` - Invalid base URL
- `test_is_self_link_both_invalid` - Both URLs invalid
- `test_is_self_link_exception_uses_fallback` - Exception triggers fallback

#### Test Class: TestUrlValidatorEdgeCases
- `test_is_self_link_empty_strings` - Empty string handling
- `test_is_self_link_whitespace` - Whitespace handling
- `test_is_self_link_unicode_urls` - Unicode characters
- `test_is_self_link_case_sensitivity` - Case sensitivity

#### Test Class: TestUrlValidatorRealWorldScenarios
- `test_is_self_link_github_urls` - GitHub URL variations
- `test_is_self_link_documentation_sites` - Documentation site patterns
- `test_is_self_link_api_endpoints` - API endpoint variations
- `test_is_self_link_localhost` - Localhost variations

### 4.4 Coverage Target

- **Lines**: 100%
- **Branches**: 100%
- **Functions**: 100%

---

## Test Infrastructure Requirements

### Required Fake Implementations

1. **FakeDatabaseRepository**
   - Implements: `DatabaseRepository` ABC
   - Features: In-memory storage, call tracking
   - Location: `tests/unit/services/crawling/fakes/fake_database_repository.py`

2. **FakeURLHandler**
   - Implements: `IURLHandler` Protocol
   - Features: Predictable transformations, call tracking
   - Location: `tests/unit/services/crawling/fakes/fake_url_handler.py`

3. **FakeSiteConfig**
   - Implements: `ISiteConfig` Protocol
   - Features: Configurable site detection, fake generators
   - Location: `tests/unit/services/crawling/fakes/fake_site_config.py`

4. **FakeHeartbeatManager**
   - Implements: `IHeartbeatManager` Protocol
   - Features: Call tracking, no-op heartbeats
   - Location: `tests/unit/services/crawling/fakes/fake_heartbeat_manager.py`

5. **FakeSourceStatusManager**
   - Implements: `ISourceStatusManager` Protocol
   - Features: Status tracking, call recording
   - Location: `tests/unit/services/crawling/fakes/fake_source_status_manager.py`

6. **FakeCrawlProgressTracker**
   - Implements: `ICrawlProgressTracker` Protocol
   - Features: State tracking, all progress methods
   - Location: `tests/unit/services/crawling/fakes/fake_crawl_progress_tracker.py`

7. **FakeDocumentProcessingOrchestrator**
   - Implements: `IDocumentProcessingOrchestrator` Protocol
   - Features: Configurable results, call tracking
   - Location: `tests/unit/services/crawling/fakes/fake_document_processing_orchestrator.py`

8. **FakeCodeExamplesOrchestrator**
   - Implements: `ICodeExamplesOrchestrator` Protocol
   - Features: Configurable code count, call tracking
   - Location: `tests/unit/services/crawling/fakes/fake_code_examples_orchestrator.py`

9. **FakeUrlTypeHandler**
   - Implements: `IUrlTypeHandler` Protocol
   - Features: Configurable crawl results, type detection
   - Location: `tests/unit/services/crawling/fakes/fake_url_type_handler.py`

10. **FakeCrawlStrategy** (Base class for strategy fakes)
    - Purpose: Base for all crawl strategy fakes
    - Location: `tests/unit/services/crawling/fakes/fake_crawl_strategy.py`

11. **FakeStorageOperations**
    - Purpose: Mock document and page storage
    - Location: `tests/unit/services/crawling/fakes/fake_storage_operations.py`

### Required Protocol Definitions

All protocols should be defined in: `python/src/server/services/crawling/protocols/`

1. `progress_tracker_protocol.py` - IProgressTracker
2. `progress_mapper_protocol.py` - IProgressMapper
3. `url_handler_protocol.py` - IURLHandler
4. `site_config_protocol.py` - ISiteConfig
5. `heartbeat_manager_protocol.py` - IHeartbeatManager
6. `source_status_manager_protocol.py` - ISourceStatusManager
7. `crawl_progress_tracker_protocol.py` - ICrawlProgressTracker
8. `document_processing_orchestrator_protocol.py` - IDocumentProcessingOrchestrator
9. `code_examples_orchestrator_protocol.py` - ICodeExamplesOrchestrator
10. `url_type_handler_protocol.py` - IUrlTypeHandler
11. `crawl_strategy_protocol.py` - ICrawlStrategy (base)
12. `storage_operations_protocol.py` - IStorageOperations

### Test File Organization

```
tests/
└── unit/
    └── services/
        └── crawling/
            ├── fakes/
            │   ├── __init__.py
            │   ├── fake_database_repository.py
            │   ├── fake_url_handler.py
            │   ├── fake_site_config.py
            │   ├── fake_heartbeat_manager.py
            │   ├── fake_source_status_manager.py
            │   ├── fake_crawl_progress_tracker.py
            │   ├── fake_document_processing_orchestrator.py
            │   ├── fake_code_examples_orchestrator.py
            │   ├── fake_url_type_handler.py
            │   ├── fake_crawl_strategy.py
            │   ├── fake_storage_operations.py
            │   ├── fake_progress_callback.py (exists)
            │   ├── fake_progress_mapper.py (exists)
            │   ├── fake_progress_tracker.py (exists)
            │   ├── fake_progress_update_handler.py (exists)
            │   └── fake_time_source.py (exists)
            ├── test_crawling_service.py
            ├── test_async_crawl_orchestrator.py
            ├── test_progress_callback_factory.py
            └── test_url_validator.py
```

---

## Test Execution Strategy

### Phase 1: Pure Functions (Simplest)
1. UrlValidator (all methods pure)
2. CrawlingService pure methods (cancel, is_cancelled, _check_cancellation, _build_orchestration_response, _create_heartbeat_callback, _is_self_link)
3. AsyncCrawlOrchestrator constructor
4. ProgressCallbackFactory constructor and logging methods

### Phase 2: Protocol & Fake Creation
1. Define all Protocol interfaces
2. Implement all Fake classes
3. Update fakes/__init__.py with exports
4. Write tests for Fake implementations

### Phase 3: Service Methods with Mocks
1. CrawlingService initialization methods
2. CrawlingService delegation methods
3. ProgressCallbackFactory callback creation and invocation
4. AsyncCrawlOrchestrator individual stage methods

### Phase 4: Integration Tests
1. CrawlingService orchestration workflow
2. AsyncCrawlOrchestrator full workflow
3. End-to-end scenarios with cancellation
4. Error handling and recovery

### Phase 5: Edge Cases & Stress Tests
1. Concurrent operations
2. Cancellation at every stage
3. Error injection at each step
4. Resource cleanup verification

---

## Testing Patterns & Best Practices

### 1. Arrange-Act-Assert Pattern
```python
@pytest.mark.asyncio
async def test_example():
    # Arrange
    fake_tracker = FakeProgressTracker()
    service = CrawlingService(repository=fake_repo, progress_id="test-123")

    # Act
    result = await service.some_method()

    # Assert
    assert result is not None
    assert fake_tracker.update_calls[0]["status"] == "expected"
```

### 2. Fake Verification Pattern
```python
def test_method_invokes_dependency():
    fake_dep = FakeDependency()
    service = Service(dependency=fake_dep)

    service.method()

    assert fake_dep.call_count() == 1
    assert fake_dep.last_call_args() == expected_args
```

### 3. Error Injection Pattern
```python
@pytest.mark.asyncio
async def test_error_handling():
    fake_dep = FakeDependency()
    fake_dep.configure_to_fail(ValueError("Test error"))
    service = Service(dependency=fake_dep)

    with pytest.raises(ValueError, match="Test error"):
        await service.method()
```

### 4. Cancellation Testing Pattern
```python
@pytest.mark.asyncio
async def test_cancellation():
    service = CrawlingService()
    service.cancel()

    with pytest.raises(asyncio.CancelledError):
        await service.some_async_method()
```

### 5. Progress Tracking Verification
```python
@pytest.mark.asyncio
async def test_progress_updates():
    fake_tracker = FakeProgressTracker()
    service = Service(tracker=fake_tracker)

    await service.method()

    assert fake_tracker.start_calls[0] == {"url": "test"}
    assert fake_tracker.update_calls[0]["status"] == "processing"
    assert fake_tracker.complete_calls[0] == {"result": "success"}
```

---

## Success Criteria

1. **Code Coverage**
   - Line coverage: 100%
   - Branch coverage: 100%
   - Function coverage: 100%

2. **Test Quality**
   - All public methods tested
   - All error paths tested
   - All cancellation points tested
   - All edge cases covered

3. **Test Independence**
   - No test depends on another test
   - Tests can run in any order
   - No shared state between tests

4. **Test Speed**
   - All unit tests complete in < 5 seconds
   - Integration tests complete in < 30 seconds
   - No real I/O or network calls

5. **Test Maintainability**
   - Clear test names describing behavior
   - Minimal setup/teardown
   - Fakes reusable across tests
   - Protocol interfaces enforce contracts

---

## Estimated Test Count

- **CrawlingService**: ~50 tests
- **AsyncCrawlOrchestrator**: ~35 tests
- **ProgressCallbackFactory**: ~15 tests
- **UrlValidator**: ~30 tests
- **Total**: ~130 tests

---

## Notes

1. **Existing Fakes**: The codebase already has FakeProgressTracker, FakeProgressMapper, FakeProgressCallback, FakeProgressUpdateHandler, and FakeTimeSource. These should be reused.

2. **Protocol Pattern**: All external dependencies should have Protocol definitions to enable proper type checking and Fake implementation.

3. **Async Testing**: All async methods must use `@pytest.mark.asyncio` decorator and proper async/await syntax.

4. **Global State**: The CrawlingService uses global registry (_active_orchestrations). Tests must properly clean up to avoid test pollution.

5. **Cancellation**: Cancellation testing is critical. Every async operation should be tested with cancellation at various points.

6. **Progress Mapping**: The ProgressMapper has complex stage-to-progress mapping logic. Tests should verify the mapping is monotonic (never goes backwards).

7. **Error Recovery**: The orchestration workflow has multiple try-catch blocks. Tests should inject errors at each stage and verify proper cleanup.

8. **Repository Pattern**: The DatabaseRepository is already an ABC, so FakeDatabaseRepository should implement all abstract methods.

9. **Strategy Pattern**: The crawling strategies are currently concrete classes. Consider creating Protocol interfaces for better testability.

10. **Logging**: The services use logfire extensively. Logging can be verified via log capture or mocked logfire calls.
