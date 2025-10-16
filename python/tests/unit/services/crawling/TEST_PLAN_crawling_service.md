# Test Plan: CrawlingService

## Executive Summary

**Service**: `CrawlingService` (crawling_service.py)
**Testability Rating**: MEDIUM
**Lines of Code**: ~568
**External Dependencies**: 12 major dependencies
**Recommended Test Coverage**: 100% line, 95%+ branch

## 1. Function Purity Analysis

### Pure Functions

#### `_is_self_link(link: str, base_url: str) -> bool` (Lines 532-564)
- **Purity**: PURE (with exception handling fallback)
- **Side Effects**: None (logging via logger.warning is observable but doesn't affect return value)
- **Deterministic**: Yes - same inputs always produce same output
- **Testability**: HIGH - Simple unit test with various URL patterns
- **Dependencies**: Only standard library `urllib.parse`

### Impure Functions

#### `__init__(crawler, repository, progress_id)` (Lines 79-118)
- **Purity**: IMPURE (constructor with state initialization)
- **Side Effects**:
  - Creates repository instance via `get_repository()` if None
  - Initializes multiple strategy objects
  - Creates URLHandler, SiteConfig instances
- **External Dependencies**: DatabaseRepository, various strategy classes
- **Testability**: MEDIUM - Requires interface abstraction for repository

#### `set_progress_id(progress_id: str)` (Lines 119-126)
- **Purity**: IMPURE (state mutation)
- **Side Effects**: Mutates instance state, creates ProgressTracker
- **Testability**: HIGH - Simple state mutation test

#### `cancel()` (Lines 127-130)
- **Purity**: IMPURE (state mutation)
- **Side Effects**: Sets `_cancelled` flag, logs info
- **Testability**: HIGH - Simple state mutation test

#### `is_cancelled() -> bool` (Lines 132-134)
- **Purity**: PURE (read-only accessor)
- **Side Effects**: None
- **Testability**: HIGH - Simple state read test

#### `_check_cancellation()` (Lines 136-139)
- **Purity**: IMPURE (raises exception based on state)
- **Side Effects**: Raises `asyncio.CancelledError` if cancelled
- **Testability**: HIGH - Test both cancelled and not-cancelled states

#### `async _create_crawl_progress_callback(base_status: str)` (Lines 141-177)
- **Purity**: IMPURE (returns closure with side effects)
- **Side Effects**: Callback updates progress_tracker, logs info
- **Testability**: MEDIUM - Requires mocking progress_tracker

#### `async _handle_progress_update(task_id: str, update: dict)` (Lines 179-194)
- **Purity**: IMPURE (I/O via progress_tracker)
- **Side Effects**: Updates progress_tracker state
- **Testability**: MEDIUM - Requires mocking progress_tracker

#### `async crawl_single_page(url: str, retry_count: int)` (Lines 197-204)
- **Purity**: IMPURE (delegates to strategy)
- **Side Effects**: Network I/O via SinglePageCrawlStrategy
- **Testability**: HIGH - Delegate pattern, mock strategy

#### `async crawl_markdown_file(url: str, progress_callback)` (Lines 206-214)
- **Purity**: IMPURE (delegates to strategy)
- **Side Effects**: Network I/O via SinglePageCrawlStrategy
- **Testability**: HIGH - Delegate pattern, mock strategy

#### `parse_sitemap(sitemap_url: str) -> list[str]` (Lines 216-218)
- **Purity**: IMPURE (delegates to strategy)
- **Side Effects**: Network I/O via SitemapCrawlStrategy
- **Testability**: HIGH - Delegate pattern, mock strategy

#### `async crawl_batch_with_progress(urls, max_concurrent, progress_callback, link_text_fallbacks)` (Lines 220-236)
- **Purity**: IMPURE (delegates to strategy)
- **Side Effects**: Network I/O via BatchCrawlStrategy
- **Testability**: HIGH - Delegate pattern, mock strategy

#### `async crawl_recursive_with_progress(start_urls, max_depth, max_concurrent, progress_callback)` (Lines 238-254)
- **Purity**: IMPURE (delegates to strategy)
- **Side Effects**: Network I/O via RecursiveCrawlStrategy
- **Testability**: HIGH - Delegate pattern, mock strategy

#### `async orchestrate_crawl(request: dict)` (Lines 257-292)
- **Purity**: IMPURE (orchestration with background task)
- **Side Effects**:
  - Registers orchestration in global registry
  - Creates asyncio.Task for background processing
  - Updates global `_active_orchestrations` dict
- **Testability**: MEDIUM - Requires registry isolation for tests

#### `async _async_orchestrate_crawl(request: dict, task_id: str)` (Lines 294-518)
- **Purity**: IMPURE (complex orchestration)
- **Side Effects**:
  - Creates multiple orchestrator instances
  - Updates progress tracker
  - Calls multiple external services
  - Updates database via repository
  - Unregisters from global registry
- **Testability**: LOW - Complex orchestration with many dependencies
- **Recommendation**: Break into smaller functions or use orchestrator pattern

#### `_create_heartbeat_callback(task_id: str)` (Lines 520-530)
- **Purity**: IMPURE (returns closure with side effects)
- **Side Effects**: Callback updates progress via `_handle_progress_update`
- **Testability**: HIGH - Test closure behavior with mock

### Global Functions

#### `_ensure_orchestration_lock() -> asyncio.Lock` (Lines 49-53)
- **Purity**: IMPURE (global state initialization)
- **Side Effects**: Creates global lock on first call
- **Testability**: LOW - Global state is problematic for parallel tests

#### `async get_active_orchestration(progress_id: str)` (Lines 55-59)
- **Purity**: IMPURE (global state access)
- **Side Effects**: Reads from global `_active_orchestrations`
- **Testability**: MEDIUM - Requires global state isolation

#### `async register_orchestration(progress_id: str, orchestration)` (Lines 61-65)
- **Purity**: IMPURE (global state mutation)
- **Side Effects**: Writes to global `_active_orchestrations`
- **Testability**: MEDIUM - Requires global state isolation

#### `async unregister_orchestration(progress_id: str)` (Lines 67-71)
- **Purity**: IMPURE (global state mutation)
- **Side Effects**: Removes from global `_active_orchestrations`
- **Testability**: MEDIUM - Requires global state isolation

## 2. External Dependencies Analysis

### Database Dependencies

#### `DatabaseRepository` (via `repositories.database_repository`)
- **Usage**: Data persistence for sources, documents, pages
- **Methods Used**:
  - `get_source_by_id(source_id: str)`
  - Various insert/update methods (via doc_storage_ops, page_storage_ops)
- **Interface Needed**: YES - `IDatabaseRepository` Protocol

#### `get_repository()` (via `repositories.repository_factory`)
- **Usage**: Factory function to create repository instances
- **Interface Needed**: YES - Mock factory function

### Network/Crawler Dependencies

#### `crawler` (Crawl4AI instance)
- **Usage**: Web crawling operations
- **Methods Used**: Various crawling methods (delegated to strategies)
- **Interface Needed**: YES - `IWebCrawler` Protocol

### Strategy Dependencies

#### `BatchCrawlStrategy`
- **Usage**: Batch crawling of multiple URLs
- **Methods Used**: `crawl_batch_with_progress()`
- **Interface Needed**: YES - `IBatchCrawlStrategy` Protocol

#### `RecursiveCrawlStrategy`
- **Usage**: Recursive crawling with depth limits
- **Methods Used**: `crawl_recursive_with_progress()`
- **Interface Needed**: YES - `IRecursiveCrawlStrategy` Protocol

#### `SinglePageCrawlStrategy`
- **Usage**: Single page and markdown file crawling
- **Methods Used**: `crawl_single_page()`, `crawl_markdown_file()`
- **Interface Needed**: YES - `ISinglePageCrawlStrategy` Protocol

#### `SitemapCrawlStrategy`
- **Usage**: Sitemap parsing
- **Methods Used**: `parse_sitemap()`
- **Interface Needed**: YES - `ISitemapCrawlStrategy` Protocol

### Operations Dependencies

#### `DocumentStorageOperations`
- **Usage**: Document processing and storage
- **Methods Used**: `process_and_store_documents()`, `extract_and_store_code_examples()`
- **Interface Needed**: YES - `IDocumentStorageOperations` Protocol

#### `PageStorageOperations`
- **Usage**: Page storage operations
- **Methods Used**: Various page storage methods
- **Interface Needed**: YES - `IPageStorageOperations` Protocol

### Helper Dependencies

#### `URLHandler`
- **Usage**: URL transformations and validations
- **Methods Used**:
  - `transform_github_url(url: str)`
  - `generate_unique_source_id(url: str)`
  - `extract_display_name(url: str)`
- **Interface Needed**: YES - `IURLHandler` Protocol

#### `SiteConfig`
- **Usage**: Site-specific configuration
- **Methods Used**:
  - `get_markdown_generator()`
  - `get_link_pruning_markdown_generator()`
  - `is_documentation_site(url: str)`
- **Interface Needed**: YES - `ISiteConfig` Protocol

### Progress Tracking Dependencies

#### `ProgressTracker`
- **Usage**: HTTP polling progress updates
- **Methods Used**: `start()`, `update()`, `complete()`, `error()`
- **Interface Needed**: YES - `IProgressTracker` Protocol

#### `ProgressMapper`
- **Usage**: Progress range mapping
- **Methods Used**: `map_progress()`, `get_current_stage()`, `get_current_progress()`
- **Interface Needed**: YES - `IProgressMapper` Protocol (or use concrete class)

### Orchestration Dependencies

#### `HeartbeatManager`
- **Usage**: Periodic heartbeat signals
- **Methods Used**: `send_if_needed()`
- **Interface Needed**: YES - `IHeartbeatManager` Protocol

#### `SourceStatusManager`
- **Usage**: Source status updates
- **Methods Used**: `update_to_completed()`, `update_to_failed()`
- **Interface Needed**: YES - `ISourceStatusManager` Protocol

#### `CrawlProgressTracker`
- **Usage**: Crawl-specific progress tracking
- **Methods Used**: `start()`, `update_mapped()`, `update_with_crawl_type()`, etc.
- **Interface Needed**: YES - `ICrawlProgressTracker` Protocol

#### `DocumentProcessingOrchestrator`
- **Usage**: Document processing orchestration
- **Methods Used**: `process_and_store()`
- **Interface Needed**: YES - `IDocumentProcessingOrchestrator` Protocol

#### `CodeExamplesOrchestrator`
- **Usage**: Code extraction orchestration
- **Methods Used**: `extract_code_examples()`
- **Interface Needed**: YES - `ICodeExamplesOrchestrator` Protocol

#### `UrlTypeHandler`
- **Usage**: URL type detection and routing
- **Methods Used**: `crawl_by_type()`
- **Interface Needed**: YES - `IUrlTypeHandler` Protocol

## 3. Testability Assessment

### Overall Testability: MEDIUM

**Strengths**:
1. Delegate pattern for crawling strategies makes unit testing easier
2. Most methods have clear single responsibilities
3. Pure function `_is_self_link` is easily testable
4. Constructor allows dependency injection

**Weaknesses**:
1. `_async_orchestrate_crawl` is 224 lines and coordinates 12+ dependencies
2. Global state (`_active_orchestrations`, `_orchestration_lock`) complicates parallel testing
3. Deep nesting of orchestration calls makes mocking complex
4. No interface abstractions currently defined

**Testing Challenges**:
1. **Global State Management**: The global `_active_orchestrations` dictionary requires careful setup/teardown in tests
2. **Async Complexity**: Many async methods with background tasks require proper async test harness
3. **Progress Tracking**: Progress callbacks and state tracking need careful mocking
4. **Orchestration Complexity**: `_async_orchestrate_crawl` coordinates many services, requiring extensive mocking

### Recommended Refactoring for Testability

1. **Extract Global State to Class**: Move `_active_orchestrations` into a registry class
2. **Interface Extraction**: Define Protocol interfaces for all external dependencies
3. **Break Down Large Methods**: Split `_async_orchestrate_crawl` into smaller, testable functions
4. **Dependency Injection**: Pass all dependencies via constructor (already done well)

## 4. Interface Extraction Plan

### Core Protocols (Priority: HIGH)

#### `IDatabaseRepository`
```python
from typing import Protocol, Optional, Any

class IDatabaseRepository(Protocol):
    """Interface for database repository operations."""

    async def get_source_by_id(self, source_id: str) -> Optional[dict[str, Any]]:
        """Get source by ID."""
        ...

    # Add other methods as needed
```

#### `IWebCrawler`
```python
from typing import Protocol

class IWebCrawler(Protocol):
    """Interface for web crawler."""

    # Define methods based on actual Crawl4AI usage
    # Note: May need to inspect strategy implementations
```

#### `ICrawlStrategy`
```python
from typing import Protocol, Callable, Awaitable, Any

class ISinglePageCrawlStrategy(Protocol):
    """Interface for single page crawling."""

    async def crawl_single_page(
        self, url: str, transform_url: Callable, is_doc_site: Callable,
        retry_count: int
    ) -> dict[str, Any]:
        ...

    async def crawl_markdown_file(
        self, url: str, transform_url: Callable,
        progress_callback: Optional[Callable]
    ) -> list[dict[str, Any]]:
        ...

class IBatchCrawlStrategy(Protocol):
    """Interface for batch crawling."""

    async def crawl_batch_with_progress(
        self, urls: list[str], transform_url: Callable, is_doc_site: Callable,
        max_concurrent: Optional[int], progress_callback: Optional[Callable],
        check_cancellation: Callable, link_text_fallbacks: Optional[dict[str, str]]
    ) -> list[dict[str, Any]]:
        ...

class IRecursiveCrawlStrategy(Protocol):
    """Interface for recursive crawling."""

    async def crawl_recursive_with_progress(
        self, start_urls: list[str], transform_url: Callable, is_doc_site: Callable,
        max_depth: int, max_concurrent: Optional[int],
        progress_callback: Optional[Callable], check_cancellation: Callable
    ) -> list[dict[str, Any]]:
        ...

class ISitemapCrawlStrategy(Protocol):
    """Interface for sitemap parsing."""

    def parse_sitemap(
        self, sitemap_url: str, check_cancellation: Callable
    ) -> list[str]:
        ...
```

#### `IDocumentStorageOperations`
```python
from typing import Protocol, Callable, Awaitable, Any, Optional

class IDocumentStorageOperations(Protocol):
    """Interface for document storage operations."""

    async def process_and_store_documents(
        self, crawl_results: list[dict], request: dict, crawl_type: str,
        original_source_id: str, progress_callback: Optional[Callable],
        cancellation_check: Callable, source_url: str, source_display_name: str,
        url_to_page_id: Optional[dict]
    ) -> dict[str, Any]:
        ...

    async def extract_and_store_code_examples(
        self, crawl_results: list[dict], url_to_full_document: dict[str, str],
        source_id: str, progress_callback: Optional[Callable],
        cancellation_check: Callable, provider: str, embedding_provider: Optional[str]
    ) -> int:
        ...
```

#### `IProgressTracker`
```python
from typing import Protocol, Any, Optional

class IProgressTracker(Protocol):
    """Interface for progress tracking."""

    progress_id: str
    state: dict[str, Any]

    async def start(self, initial_data: Optional[dict[str, Any]] = None) -> None:
        ...

    async def update(
        self, status: str, progress: int, log: str, **kwargs
    ) -> None:
        ...

    async def complete(self, completion_data: Optional[dict[str, Any]] = None) -> None:
        ...

    async def error(
        self, error_message: str, error_details: Optional[dict[str, Any]] = None
    ) -> None:
        ...
```

#### `IOrchestrationRegistry`
```python
from typing import Protocol, Optional

class IOrchestrationRegistry(Protocol):
    """Interface for managing active orchestrations."""

    async def register(self, progress_id: str, service: Any) -> None:
        ...

    async def unregister(self, progress_id: str) -> None:
        ...

    async def get(self, progress_id: str) -> Optional[Any]:
        ...
```

### Helper Protocols (Priority: MEDIUM)

#### `IURLHandler`
```python
from typing import Protocol

class IURLHandler(Protocol):
    """Interface for URL operations."""

    @staticmethod
    def transform_github_url(url: str) -> str:
        ...

    @staticmethod
    def generate_unique_source_id(url: str) -> str:
        ...

    @staticmethod
    def extract_display_name(url: str) -> str:
        ...
```

#### `ISiteConfig`
```python
from typing import Protocol, Any

class ISiteConfig(Protocol):
    """Interface for site configuration."""

    def get_markdown_generator(self) -> Any:
        ...

    def get_link_pruning_markdown_generator(self) -> Any:
        ...

    def is_documentation_site(self, url: str) -> bool:
        ...
```

### Orchestrator Protocols (Priority: HIGH)

All orchestrator interfaces should be defined based on the actual orchestrator classes analyzed separately.

## 5. Test Plan

### Test File Structure

```
tests/unit/services/crawling/
├── test_crawling_service.py          # Main service tests
├── test_crawling_service_helpers.py  # Pure function tests
├── test_crawling_service_registry.py # Global state tests
└── fakes/
    ├── fake_database_repository.py
    ├── fake_crawl_strategies.py
    ├── fake_progress_tracker.py
    └── fake_orchestrators.py
```

### Test Scenarios

#### Pure Function Tests

**Test: `test_is_self_link_exact_match`**
- Input: link="https://example.com", base_url="https://example.com"
- Expected: True
- Type: Pure unit test

**Test: `test_is_self_link_trailing_slash`**
- Input: link="https://example.com/", base_url="https://example.com"
- Expected: True
- Type: Pure unit test

**Test: `test_is_self_link_query_params`**
- Input: link="https://example.com?foo=bar", base_url="https://example.com"
- Expected: True (query params ignored)
- Type: Pure unit test

**Test: `test_is_self_link_fragment`**
- Input: link="https://example.com#section", base_url="https://example.com"
- Expected: True (fragments ignored)
- Type: Pure unit test

**Test: `test_is_self_link_different_scheme`**
- Input: link="http://example.com", base_url="https://example.com"
- Expected: True (scheme normalized)
- Type: Pure unit test

**Test: `test_is_self_link_default_ports`**
- Input: link="https://example.com:443", base_url="https://example.com"
- Expected: True (default ports removed)
- Type: Pure unit test

**Test: `test_is_self_link_different_domain`**
- Input: link="https://other.com", base_url="https://example.com"
- Expected: False
- Type: Pure unit test

**Test: `test_is_self_link_different_path`**
- Input: link="https://example.com/page", base_url="https://example.com"
- Expected: False
- Type: Pure unit test

**Test: `test_is_self_link_error_handling`**
- Input: link="not-a-url", base_url="https://example.com"
- Expected: False (fallback to simple comparison)
- Type: Pure unit test

#### Constructor Tests

**Test: `test_init_with_all_dependencies`**
- Setup: Create fake crawler, repository, progress_id
- Action: Initialize CrawlingService
- Expected: All dependencies assigned correctly
- Type: Unit test with Fakes

**Test: `test_init_without_repository_creates_one`**
- Setup: Create fake crawler, no repository
- Action: Initialize CrawlingService
- Expected: Repository created via get_repository()
- Type: Unit test with mock factory

**Test: `test_init_without_progress_id`**
- Setup: Create fake crawler, repository
- Action: Initialize CrawlingService without progress_id
- Expected: progress_tracker is None
- Type: Unit test with Fakes

#### State Management Tests

**Test: `test_set_progress_id`**
- Setup: Create service
- Action: Call set_progress_id("test-id")
- Expected: progress_id set, ProgressTracker created
- Type: Unit test with Fakes

**Test: `test_cancel_sets_flag`**
- Setup: Create service
- Action: Call cancel()
- Expected: _cancelled is True
- Type: Unit test with Fakes

**Test: `test_is_cancelled_returns_false_initially`**
- Setup: Create service
- Action: Call is_cancelled()
- Expected: False
- Type: Unit test

**Test: `test_is_cancelled_returns_true_after_cancel`**
- Setup: Create service, call cancel()
- Action: Call is_cancelled()
- Expected: True
- Type: Unit test

**Test: `test_check_cancellation_raises_when_cancelled`**
- Setup: Create service, call cancel()
- Action: Call _check_cancellation()
- Expected: asyncio.CancelledError raised
- Type: Unit test

**Test: `test_check_cancellation_no_raise_when_not_cancelled`**
- Setup: Create service
- Action: Call _check_cancellation()
- Expected: No exception
- Type: Unit test

#### Strategy Delegation Tests

**Test: `test_crawl_single_page_delegates_to_strategy`**
- Setup: Create service with FakeSinglePageCrawlStrategy
- Action: Call crawl_single_page("https://example.com")
- Expected: Strategy called with correct arguments
- Type: Unit test with Fake

**Test: `test_crawl_markdown_file_delegates_to_strategy`**
- Setup: Create service with FakeSinglePageCrawlStrategy
- Action: Call crawl_markdown_file("https://example.com/doc.md")
- Expected: Strategy called with correct arguments
- Type: Unit test with Fake

**Test: `test_parse_sitemap_delegates_to_strategy`**
- Setup: Create service with FakeSitemapCrawlStrategy
- Action: Call parse_sitemap("https://example.com/sitemap.xml")
- Expected: Strategy called, cancellation check passed
- Type: Unit test with Fake

**Test: `test_crawl_batch_with_progress_delegates_to_strategy`**
- Setup: Create service with FakeBatchCrawlStrategy
- Action: Call crawl_batch_with_progress(["url1", "url2"])
- Expected: Strategy called with all parameters
- Type: Unit test with Fake

**Test: `test_crawl_recursive_with_progress_delegates_to_strategy`**
- Setup: Create service with FakeRecursiveCrawlStrategy
- Action: Call crawl_recursive_with_progress(["https://example.com"])
- Expected: Strategy called with max_depth, cancellation check
- Type: Unit test with Fake

#### Progress Callback Tests

**Test: `test_create_crawl_progress_callback_updates_tracker`**
- Setup: Create service with FakeProgressTracker
- Action: Create callback, invoke it with progress data
- Expected: ProgressTracker.update() called with mapped progress
- Type: Unit test with Fake

**Test: `test_create_crawl_progress_callback_maps_progress`**
- Setup: Create service with FakeProgressMapper
- Action: Create callback for "crawling", invoke with progress=50
- Expected: map_progress("crawling", 50) called
- Type: Unit test with Fake

**Test: `test_handle_progress_update_forwards_to_tracker`**
- Setup: Create service with FakeProgressTracker
- Action: Call _handle_progress_update("task-1", {...})
- Expected: ProgressTracker.update() called
- Type: Unit test with Fake

#### Orchestration Tests

**Test: `test_orchestrate_crawl_creates_task`**
- Setup: Create service with all Fakes
- Action: Call orchestrate_crawl({"url": "https://example.com"})
- Expected: asyncio.Task created, returns task_id
- Type: Unit test with Fakes

**Test: `test_orchestrate_crawl_registers_service`**
- Setup: Create service, set progress_id
- Action: Call orchestrate_crawl({...})
- Expected: Service registered in global registry
- Type: Unit test with registry isolation

**Test: `test_orchestrate_crawl_generates_task_id`**
- Setup: Create service without progress_id
- Action: Call orchestrate_crawl({...})
- Expected: UUID task_id generated
- Type: Unit test

**Test: `test_async_orchestrate_crawl_success_flow`**
- Setup: Create service with all Fakes returning success
- Action: Call _async_orchestrate_crawl(request, task_id), await
- Expected:
  - HeartbeatManager called
  - UrlTypeHandler.crawl_by_type() called
  - DocumentProcessingOrchestrator.process_and_store() called
  - CodeExamplesOrchestrator.extract_code_examples() called
  - SourceStatusManager.update_to_completed() called
  - Unregistered from registry
- Type: Unit test with extensive Fakes

**Test: `test_async_orchestrate_crawl_handles_cancellation`**
- Setup: Create service, call cancel() before orchestration
- Action: Call _async_orchestrate_crawl(), await
- Expected:
  - asyncio.CancelledError caught
  - Progress updated to "cancelled"
  - Unregistered from registry
- Type: Unit test with Fakes

**Test: `test_async_orchestrate_crawl_handles_errors`**
- Setup: Create service with Fake that raises exception
- Action: Call _async_orchestrate_crawl(), await
- Expected:
  - Exception caught
  - Progress updated to "error"
  - SourceStatusManager.update_to_failed() called
  - Unregistered from registry
- Type: Unit test with Fakes

**Test: `test_async_orchestrate_crawl_validates_crawl_results`**
- Setup: Create service with UrlTypeHandler returning empty results
- Action: Call _async_orchestrate_crawl(), await
- Expected: ValueError("No content was crawled") raised
- Type: Unit test with Fakes

#### Registry Function Tests

**Test: `test_register_orchestration`**
- Setup: Create service
- Action: Call register_orchestration("test-id", service)
- Expected: Service stored in _active_orchestrations
- Type: Unit test with registry isolation

**Test: `test_unregister_orchestration`**
- Setup: Register a service
- Action: Call unregister_orchestration("test-id")
- Expected: Service removed from _active_orchestrations
- Type: Unit test with registry isolation

**Test: `test_get_active_orchestration`**
- Setup: Register a service
- Action: Call get_active_orchestration("test-id")
- Expected: Service returned
- Type: Unit test with registry isolation

**Test: `test_get_active_orchestration_not_found`**
- Setup: Empty registry
- Action: Call get_active_orchestration("nonexistent")
- Expected: None returned
- Type: Unit test with registry isolation

#### Edge Cases

**Test: `test_orchestrate_crawl_with_empty_url`**
- Setup: Create service
- Action: Call orchestrate_crawl({"url": ""})
- Expected: Task created, but _async_orchestrate_crawl will fail gracefully
- Type: Unit test

**Test: `test_crawl_single_page_with_invalid_url`**
- Setup: Create service with strategy that handles errors
- Action: Call crawl_single_page("not-a-url")
- Expected: Exception propagated or handled by strategy
- Type: Unit test with Fake

**Test: `test_progress_callback_with_none_tracker`**
- Setup: Create service without progress_id
- Action: Create callback, invoke it
- Expected: No exception, callback does nothing
- Type: Unit test

#### Integration Scenarios (Unit tests with multiple Fakes)

**Test: `test_full_crawl_workflow_single_page`**
- Setup: Create service with all Fakes
- Request: {"url": "https://example.com", "max_depth": 1}
- Expected:
  1. URL type detected as "normal"
  2. Recursive crawl with depth=1
  3. Documents processed and stored
  4. Code examples extracted
  5. Source status updated to "completed"
- Type: Unit test with comprehensive Fakes

**Test: `test_full_crawl_workflow_sitemap`**
- Setup: Create service with Fake returning sitemap URLs
- Request: {"url": "https://example.com/sitemap.xml"}
- Expected:
  1. URL type detected as "sitemap"
  2. Sitemap parsed to URLs
  3. Batch crawl of URLs
  4. Documents stored
- Type: Unit test with Fakes

**Test: `test_full_crawl_workflow_markdown_file`**
- Setup: Create service with Fake returning markdown content
- Request: {"url": "https://example.com/llms.txt"}
- Expected:
  1. URL type detected as "text_file"
  2. Markdown file crawled
  3. Single document stored
- Type: Unit test with Fakes

### Fake Implementations Needed

#### `FakeDatabaseRepository`
- In-memory storage for sources, documents, pages
- Methods: get_source_by_id, insert_source, update_source

#### `FakeSinglePageCrawlStrategy`
- Returns mock crawl result for single page
- Returns mock markdown content for files

#### `FakeBatchCrawlStrategy`
- Returns mock crawl results for batch URLs
- Tracks cancellation checks

#### `FakeRecursiveCrawlStrategy`
- Returns mock crawl results with depth tracking
- Tracks cancellation checks

#### `FakeSitemapCrawlStrategy`
- Returns list of mock URLs from sitemap
- Tracks cancellation checks

#### `FakeDocumentStorageOperations`
- Returns mock storage results (chunks_stored, source_id, etc.)
- Tracks method calls

#### `FakePageStorageOperations`
- Mock page storage operations

#### `FakeProgressTracker`
- Stores update calls in list
- Provides state getter

#### `FakeProgressMapper`
- Returns mock mapped progress values
- Tracks stage transitions

#### `FakeURLHandler`
- Returns mock source IDs and display names
- Static methods implementation

#### `FakeSiteConfig`
- Returns mock markdown generators
- Returns mock is_documentation_site results

#### `FakeHeartbeatManager`
- Tracks send_if_needed calls

#### `FakeSourceStatusManager`
- Tracks status update calls

#### `FakeCrawlProgressTracker`
- Tracks progress updates

#### `FakeDocumentProcessingOrchestrator`
- Returns mock storage results

#### `FakeCodeExamplesOrchestrator`
- Returns mock code examples count

#### `FakeUrlTypeHandler`
- Returns mock crawl results and type

### Coverage Goals

- **Line Coverage**: 100%
- **Branch Coverage**: 95%+
- **Function Coverage**: 100%

### Priority Test Implementation Order

1. **Phase 1**: Pure functions (_is_self_link)
2. **Phase 2**: Constructor and state management
3. **Phase 3**: Strategy delegation methods
4. **Phase 4**: Progress callback creation and handling
5. **Phase 5**: Registry functions (with isolation)
6. **Phase 6**: Orchestration (orchestrate_crawl)
7. **Phase 7**: Full orchestration workflow (_async_orchestrate_crawl)
8. **Phase 8**: Edge cases and error handling

## 6. Test Data Requirements

### Mock URLs
- Simple URL: "https://example.com"
- Sitemap URL: "https://example.com/sitemap.xml"
- Markdown file: "https://example.com/llms.txt"
- GitHub URL: "https://github.com/user/repo/blob/main/README.md"

### Mock Crawl Results
```python
MOCK_CRAWL_RESULT = {
    "url": "https://example.com",
    "markdown": "# Example\nContent here",
    "html": "<html>...</html>",
    "success": True,
}
```

### Mock Request
```python
MOCK_REQUEST = {
    "url": "https://example.com",
    "knowledge_type": "documentation",
    "tags": ["python"],
    "max_depth": 2,
    "max_concurrent": 5,
    "extract_code_examples": True,
}
```

## 7. Notes and Recommendations

### Critical Issues to Address Before Testing

1. **Global State**: Consider refactoring `_active_orchestrations` into an injectable registry class
2. **Large Method**: `_async_orchestrate_crawl` (224 lines) should be broken down
3. **Async Lock Initialization**: `_ensure_orchestration_lock()` creates global state on first call

### Testing Best Practices

1. **Async Test Harness**: Use pytest-asyncio with proper event loop management
2. **Registry Isolation**: Clear global `_active_orchestrations` in teardown
3. **Progress Tracker Mock**: Ensure FakeProgressTracker matches interface exactly
4. **Cancellation Testing**: Test cancellation at various points in orchestration

### Future Improvements

1. Extract orchestration logic into smaller, composable functions
2. Define Protocol interfaces for all dependencies
3. Move global state into dependency-injected registry
4. Consider separating orchestration concerns from crawling concerns
