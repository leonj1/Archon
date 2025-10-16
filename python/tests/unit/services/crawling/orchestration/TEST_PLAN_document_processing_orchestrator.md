# Test Plan: DocumentProcessingOrchestrator

## Executive Summary

**Service**: `DocumentProcessingOrchestrator` (orchestration/document_processing_orchestrator.py)
**Testability Rating**: HIGH
**Lines of Code**: ~156
**External Dependencies**: 3 (DocumentStorageOperations, progress_mapper, progress_tracker)
**Recommended Test Coverage**: 100% line, 100% branch

## 1. Function Purity Analysis

### Pure Functions

#### `_should_log_progress(status, progress, last_logged_progress)` (Lines 112-131)
- **Purity**: PURE (deterministic decision logic)
- **Side Effects**: None
- **Deterministic**: Yes - same inputs always produce same output
- **Testability**: HIGH - Simple boolean logic, no dependencies

### Impure Functions

#### `__init__(doc_storage_ops, progress_mapper, progress_tracker)` (Lines 18-34)
- **Purity**: IMPURE (constructor with state initialization)
- **Side Effects**: Stores dependencies
- **External Dependencies**: DocumentStorageOperations, ProgressMapper, ProgressTracker
- **Testability**: HIGH - Clean dependency injection

#### `async process_and_store(...)` (Lines 36-110)
- **Purity**: IMPURE (orchestration with I/O)
- **Side Effects**:
  - Creates and uses progress callback
  - Calls doc_storage_ops.process_and_store_documents()
  - Validates storage results
  - Logs progress milestones
- **External Dependencies**: DocumentStorageOperations, ProgressMapper, ProgressTracker
- **Testability**: HIGH - Well-structured with clear separation

#### `_validate_storage_results(storage_results, source_url)` (Lines 133-156)
- **Purity**: IMPURE (validation with exception raising)
- **Side Effects**:
  - Raises ValueError on validation failure
  - Logs errors
- **External Dependencies**: Logger
- **Testability**: HIGH - Clear input/output with exception

## 2. External Dependencies Analysis

### Document Storage Dependencies

#### `DocumentStorageOperations`
- **Usage**: Process and store documents with embeddings
- **Methods Used**:
  - `process_and_store_documents(crawl_results, request, crawl_type, original_source_id, callback, cancellation_check, source_url, source_display_name, url_to_page_id)`
- **Interface Needed**: YES - `IDocumentStorageOperations` Protocol

### Progress Tracking Dependencies

#### `progress_mapper`
- **Usage**: Map stage-specific progress to overall progress
- **Methods Used**:
  - `map_progress(stage: str, progress: int) -> int`
- **Interface Needed**: YES - `IProgressMapper` Protocol

#### `progress_tracker` (Optional)
- **Usage**: HTTP polling progress updates
- **Methods Used**:
  - `update(status, progress, log, **kwargs)`
- **Interface Needed**: YES - `IProgressTracker` Protocol

### Logging Dependencies

#### `logger`, `safe_logfire_info`, `safe_logfire_error`
- **Usage**: Progress logging and error reporting
- **Methods Used**: Various logging functions
- **Interface Needed**: NO - Not critical for logic

## 3. Testability Assessment

### Overall Testability: HIGH

**Strengths**:
1. Excellent dependency injection
2. Pure function `_should_log_progress` is easily testable
3. Clear separation of concerns (progress callback, validation)
4. Private methods are well-encapsulated
5. Consistent error handling with validation
6. Progress callback is a local closure, well-tested via behavior

**Weaknesses**:
1. Progress callback closure captures `last_logged_progress` - need to test via side effects

**Testing Challenges**:
1. **Progress Callback Closure**: Need to verify logging behavior via captured logs or mock
2. **Async Operations**: Requires async test harness
3. **Validation Logic**: Need to test both success and failure paths

### Recommended Refactoring for Testability

NONE - Code is already well-structured for testing

## 4. Interface Extraction Plan

### Core Protocols (Priority: HIGH)

#### `IDocumentStorageOperations`
```python
from typing import Protocol, Callable, Awaitable, Any, Optional

class IDocumentStorageOperations(Protocol):
    """Interface for document storage operations."""

    async def process_and_store_documents(
        self,
        crawl_results: list[dict[str, Any]],
        request: dict[str, Any],
        crawl_type: str,
        original_source_id: str,
        progress_callback: Optional[Callable[[str, int, str], Awaitable[None]]],
        cancellation_check: Callable[[], None],
        source_url: str,
        source_display_name: str,
        url_to_page_id: Optional[dict[str, str]],
    ) -> dict[str, Any]:
        """
        Process and store documents with embeddings.

        Returns:
            Dict with keys: chunks_stored, chunk_count, source_id, url_to_full_document
        """
        ...
```

#### `IProgressMapper`
```python
from typing import Protocol

class IProgressMapper(Protocol):
    """Interface for progress mapping."""

    def map_progress(self, stage: str, progress: int) -> int:
        """Map stage-specific progress to overall progress."""
        ...
```

#### `IProgressTracker`
```python
from typing import Protocol, Any

class IProgressTracker(Protocol):
    """Interface for progress tracking."""

    async def update(
        self, status: str, progress: int, log: str, **kwargs
    ) -> None:
        """Update progress."""
        ...
```

### Fake Implementations

#### `FakeDocumentStorageOperations`
```python
class FakeDocumentStorageOperations:
    """Fake document storage for testing."""

    def __init__(
        self,
        chunks_stored: int = 10,
        chunk_count: int = 10,
        source_id: str = "src_123",
        should_fail: bool = False
    ):
        self.calls: list[dict[str, Any]] = []
        self.chunks_stored = chunks_stored
        self.chunk_count = chunk_count
        self.source_id = source_id
        self.should_fail = should_fail
        self.progress_updates: list[dict[str, Any]] = []

    async def process_and_store_documents(
        self, crawl_results, request, crawl_type, original_source_id,
        progress_callback, cancellation_check, source_url, source_display_name,
        url_to_page_id
    ) -> dict[str, Any]:
        self.calls.append({
            "crawl_results": crawl_results,
            "request": request,
            "crawl_type": crawl_type,
            "original_source_id": original_source_id,
            "progress_callback": progress_callback,
            "cancellation_check": cancellation_check,
            "source_url": source_url,
            "source_display_name": source_display_name,
            "url_to_page_id": url_to_page_id,
        })

        if self.should_fail:
            raise Exception("Storage failed")

        # Simulate progress updates
        if progress_callback:
            await progress_callback("document_storage", 0, "Starting storage...")
            self.progress_updates.append({"progress": 0})

            await progress_callback("document_storage", 50, "Processing chunks...")
            self.progress_updates.append({"progress": 50})

            await progress_callback("document_storage", 100, "Storage complete")
            self.progress_updates.append({"progress": 100})

        return {
            "chunks_stored": self.chunks_stored,
            "chunk_count": self.chunk_count,
            "source_id": self.source_id,
            "url_to_full_document": {
                "https://example.com/page1": "Full doc 1",
                "https://example.com/page2": "Full doc 2",
            }
        }

    def was_called(self) -> bool:
        return len(self.calls) > 0
```

#### `FakeProgressMapper`
```python
class FakeProgressMapper:
    """Fake progress mapper for testing."""

    def __init__(self):
        self.calls: list[tuple[str, int]] = []
        self._mappings: dict[tuple[str, int], int] = {}

    def map_progress(self, stage: str, progress: int) -> int:
        self.calls.append((stage, progress))
        # Return pre-configured mapping or simple calculation
        key = (stage, progress)
        if key in self._mappings:
            return self._mappings[key]
        # Default: document_storage at 25-40, so map roughly
        return 25 + (progress * 15 // 100)

    def set_mapping(self, stage: str, progress: int, mapped_value: int):
        """Set a specific mapping for testing."""
        self._mappings[(stage, progress)] = mapped_value
```

#### `FakeProgressTracker`
```python
class FakeProgressTracker:
    """Fake progress tracker for testing."""

    def __init__(self):
        self.update_calls: list[dict[str, Any]] = []

    async def update(
        self, status: str, progress: int, log: str, **kwargs
    ) -> None:
        self.update_calls.append({
            "status": status,
            "progress": progress,
            "log": log,
            **kwargs
        })

    def get_update_count(self) -> int:
        return len(self.update_calls)

    def get_update(self, index: int) -> dict[str, Any]:
        return self.update_calls[index]
```

## 5. Test Plan

### Test File Structure

```
tests/unit/services/crawling/orchestration/
├── test_document_processing_orchestrator.py
└── fakes/
    ├── fake_document_storage_operations.py
    ├── fake_progress_mapper.py
    └── fake_progress_tracker.py
```

### Test Scenarios

#### Constructor Tests

**Test: `test_init_with_all_dependencies`**
- Setup: Create all fakes
- Action: Initialize DocumentProcessingOrchestrator
- Expected: All dependencies assigned
- Type: Unit test with Fakes

#### Should Log Progress Tests (Pure Function)

**Test: `test_should_log_progress_status_change`**
- Setup: DocumentProcessingOrchestrator
- Action: Call _should_log_progress("starting", 50, 50)
- Expected: Returns True (status != "document_storage")
- Type: Pure unit test

**Test: `test_should_log_progress_completion`**
- Setup: DocumentProcessingOrchestrator
- Action: Call _should_log_progress("document_storage", 100, 95)
- Expected: Returns True (progress == 100)
- Type: Pure unit test

**Test: `test_should_log_progress_start`**
- Setup: DocumentProcessingOrchestrator
- Action: Call _should_log_progress("document_storage", 0, 10)
- Expected: Returns True (progress == 0)
- Type: Pure unit test

**Test: `test_should_log_progress_five_percent_threshold`**
- Setup: DocumentProcessingOrchestrator
- Action: Call _should_log_progress("document_storage", 55, 50)
- Expected: Returns True (abs(55 - 50) >= 5)
- Type: Pure unit test

**Test: `test_should_log_progress_below_threshold`**
- Setup: DocumentProcessingOrchestrator
- Action: Call _should_log_progress("document_storage", 53, 50)
- Expected: Returns False (abs(53 - 50) < 5)
- Type: Pure unit test

**Test: `test_should_log_progress_exactly_five_percent`**
- Setup: DocumentProcessingOrchestrator
- Action: Call _should_log_progress("document_storage", 55, 50)
- Expected: Returns True (abs(55 - 50) == 5)
- Type: Pure unit test

**Test: `test_should_log_progress_backwards_change`**
- Setup: DocumentProcessingOrchestrator
- Action: Call _should_log_progress("document_storage", 45, 50)
- Expected: Returns True (abs(45 - 50) >= 5)
- Type: Pure unit test

#### Process and Store Tests - Success Path

**Test: `test_process_and_store_success`**
- Setup:
  - FakeDocumentStorageOperations returning success
  - All other fakes
  - DocumentProcessingOrchestrator
- Action: Call process_and_store(crawl_results, request, ...)
- Expected:
  - Returns storage_results dict
  - storage_results["chunks_stored"] = 10
  - storage_results["source_id"] = "src_123"
  - No exception raised
- Type: Unit test with Fakes

**Test: `test_process_and_store_passes_all_parameters`**
- Setup: All fakes, DocumentProcessingOrchestrator
- Action: Call process_and_store with specific parameters
- Expected:
  - doc_storage_ops.process_and_store_documents() called
  - All parameters passed correctly:
    - crawl_results
    - request
    - crawl_type
    - original_source_id
    - callback (created by orchestrator)
    - cancellation_check
    - source_url
    - source_display_name
    - url_to_page_id=None
- Type: Unit test with Fakes

**Test: `test_process_and_store_creates_progress_callback`**
- Setup: All fakes, DocumentProcessingOrchestrator
- Action: Call process_and_store
- Expected:
  - Progress callback created
  - Callback passed to doc_storage_ops
  - Callback is not None
- Type: Unit test with Fakes

#### Process and Store Tests - Progress Callback Behavior

**Test: `test_progress_callback_logs_significant_milestones`**
- Setup:
  - FakeDocumentStorageOperations (simulates progress updates)
  - FakeProgressTracker
  - DocumentProcessingOrchestrator
- Action: Call process_and_store
- Expected:
  - Progress at 0% logged
  - Progress at 50% may or may not be logged (depends on threshold)
  - Progress at 100% logged
  - Verify via caplog or mock
- Type: Unit test with Fakes (may need caplog)

**Test: `test_progress_callback_maps_progress`**
- Setup:
  - FakeDocumentStorageOperations
  - FakeProgressMapper (set specific mappings)
  - FakeProgressTracker
  - DocumentProcessingOrchestrator
- Action: Call process_and_store
- Expected:
  - progress_mapper.map_progress("document_storage", X) called
  - progress_tracker.update() called with mapped values
- Type: Unit test with Fakes

**Test: `test_progress_callback_includes_total_pages`**
- Setup: All fakes, crawl_results with 5 pages
- Action: Call process_and_store
- Expected:
  - progress_tracker.update() calls include total_pages=5
- Type: Unit test with Fakes

**Test: `test_progress_callback_without_progress_tracker`**
- Setup:
  - FakeDocumentStorageOperations
  - FakeProgressMapper
  - progress_tracker=None
  - DocumentProcessingOrchestrator
- Action: Call process_and_store
- Expected:
  - No exception
  - Callback still created and works
  - Mapping still happens
- Type: Unit test with Fakes

#### Process and Store Tests - Validation

**Test: `test_process_and_store_validation_success`**
- Setup:
  - FakeDocumentStorageOperations: chunks_stored=10, chunk_count=10
  - DocumentProcessingOrchestrator
- Action: Call process_and_store
- Expected:
  - _validate_storage_results called
  - No exception raised
  - Returns storage_results
- Type: Unit test with Fakes

**Test: `test_process_and_store_validation_fails_zero_chunks_stored`**
- Setup:
  - FakeDocumentStorageOperations: chunks_stored=0, chunk_count=10
  - DocumentProcessingOrchestrator
- Action: Call process_and_store
- Expected:
  - ValueError raised
  - Error message: "Failed to store documents: 10 chunks processed but 0 stored"
- Type: Unit test with Fakes

**Test: `test_process_and_store_validation_allows_zero_chunk_count`**
- Setup:
  - FakeDocumentStorageOperations: chunks_stored=0, chunk_count=0
  - DocumentProcessingOrchestrator
- Action: Call process_and_store
- Expected:
  - No exception (valid case: no chunks to store)
  - Returns storage_results
- Type: Unit test with Fakes

#### Validate Storage Results Tests

**Test: `test_validate_storage_results_success`**
- Setup: DocumentProcessingOrchestrator
- Storage Results: {"chunks_stored": 10, "chunk_count": 10}
- Action: Call _validate_storage_results(storage_results, "https://example.com")
- Expected: No exception
- Type: Unit test

**Test: `test_validate_storage_results_both_zero_allowed`**
- Setup: DocumentProcessingOrchestrator
- Storage Results: {"chunks_stored": 0, "chunk_count": 0}
- Action: Call _validate_storage_results(storage_results, "https://example.com")
- Expected: No exception
- Type: Unit test

**Test: `test_validate_storage_results_fails_mismatch`**
- Setup: DocumentProcessingOrchestrator
- Storage Results: {"chunks_stored": 0, "chunk_count": 15}
- Action: Call _validate_storage_results(storage_results, "https://example.com")
- Expected:
  - ValueError raised
  - Error message includes: "15 chunks processed but 0 stored"
  - Error message includes: "url=https://example.com"
- Type: Unit test

**Test: `test_validate_storage_results_partial_storage_allowed`**
- Setup: DocumentProcessingOrchestrator
- Storage Results: {"chunks_stored": 5, "chunk_count": 10}
- Action: Call _validate_storage_results(storage_results, "https://example.com")
- Expected: No exception (5 > 0, so validation passes)
- Type: Unit test

**Test: `test_validate_storage_results_missing_chunks_stored_key`**
- Setup: DocumentProcessingOrchestrator
- Storage Results: {"chunk_count": 10}
- Action: Call _validate_storage_results(storage_results, "https://example.com")
- Expected:
  - ValueError raised (chunks_stored defaults to 0 via .get())
- Type: Unit test

**Test: `test_validate_storage_results_missing_chunk_count_key`**
- Setup: DocumentProcessingOrchestrator
- Storage Results: {"chunks_stored": 10}
- Action: Call _validate_storage_results(storage_results, "https://example.com")
- Expected: No exception (chunk_count defaults to 0 via .get(), 0 > 0 is False)
- Type: Unit test

#### Integration Scenarios

**Test: `test_full_document_processing_workflow`**
- Setup:
  - All fakes
  - crawl_results: 3 pages
  - request: {"key": "value"}
  - DocumentProcessingOrchestrator
- Action: Call process_and_store with full parameters
- Expected:
  1. Progress callback created
  2. doc_storage_ops.process_and_store_documents() called
  3. Progress updates mapped and forwarded
  4. Validation passes
  5. Returns storage_results with correct keys
- Type: Unit test with comprehensive Fakes

**Test: `test_document_processing_with_no_chunks`**
- Setup:
  - FakeDocumentStorageOperations: chunks_stored=0, chunk_count=0
  - DocumentProcessingOrchestrator
- Action: Call process_and_store
- Expected:
  - Returns storage_results
  - Validation passes (0 chunks is valid)
- Type: Unit test with Fakes

**Test: `test_document_processing_with_large_page_count`**
- Setup:
  - crawl_results: 100 pages
  - FakeDocumentStorageOperations
  - DocumentProcessingOrchestrator
- Action: Call process_and_store
- Expected:
  - total_pages=100 passed in callbacks
  - Works correctly with large count
- Type: Unit test with Fakes

#### Edge Cases

**Test: `test_process_and_store_with_empty_crawl_results`**
- Setup: All fakes, crawl_results=[]
- Action: Call process_and_store
- Expected: Still works (0 pages is valid)
- Type: Unit test with Fakes

**Test: `test_process_and_store_with_special_characters_in_url`**
- Setup: source_url="https://example.com/文档"
- Action: Call process_and_store
- Expected: Works correctly (Unicode URL handled)
- Type: Unit test with Fakes

**Test: `test_process_and_store_with_very_long_source_id`**
- Setup: original_source_id="a" * 1000
- Action: Call process_and_store
- Expected: Works correctly
- Type: Unit test with Fakes

**Test: `test_validate_storage_results_with_very_large_chunk_count`**
- Setup: storage_results={"chunks_stored": 1000000, "chunk_count": 1000000}
- Action: Call _validate_storage_results
- Expected: No exception
- Type: Unit test

**Test: `test_progress_callback_filters_rapid_updates`**
- Setup:
  - Simulate rapid progress updates (every 1%)
  - FakeProgressTracker
  - DocumentProcessingOrchestrator
- Action: Trigger many progress updates via doc_storage_ops
- Expected:
  - Not all updates logged (filtered by _should_log_progress)
  - Only significant milestones logged (0%, 5%, 10%, etc.)
- Type: Unit test with Fakes (may need custom FakeDocumentStorageOperations)

### Fake Implementations Needed (Summary)

1. `FakeDocumentStorageOperations` - Simulates document storage with configurable results
2. `FakeProgressMapper` - Maps progress values
3. `FakeProgressTracker` - Tracks progress updates

### Coverage Goals

- **Line Coverage**: 100%
- **Branch Coverage**: 100%
- **Function Coverage**: 100%

### Priority Test Implementation Order

1. **Phase 1**: Constructor tests
2. **Phase 2**: Pure function tests (_should_log_progress)
3. **Phase 3**: Success path (process_and_store)
4. **Phase 4**: Validation tests (_validate_storage_results)
5. **Phase 5**: Progress callback behavior
6. **Phase 6**: Integration workflows
7. **Phase 7**: Edge cases

## 6. Test Data Requirements

### Crawl Results
```python
[
    {"url": "https://example.com/page1", "markdown": "Content 1"},
    {"url": "https://example.com/page2", "markdown": "Content 2"},
    {"url": "https://example.com/page3", "markdown": "Content 3"},
]
```

### Request
```python
{
    "knowledge_type": "documentation",
    "tags": ["python"],
    "max_depth": 2,
}
```

### Storage Results
```python
{
    "chunks_stored": 10,
    "chunk_count": 10,
    "source_id": "src_123",
    "url_to_full_document": {
        "https://example.com/page1": "Full doc 1",
        "https://example.com/page2": "Full doc 2",
    }
}
```

### Progress Values
- 0, 5, 10, 25, 50, 75, 90, 95, 100

### Crawl Types
- "normal", "sitemap", "text_file"

### Source URLs
- "https://example.com", "https://docs.python.org", "https://example.com/文档"

## 7. Notes and Recommendations

### Critical Issues to Address Before Testing

NONE - Code is well-structured and ready for testing

### Testing Best Practices

1. **Async Tests**: Use pytest-asyncio
2. **Pure Function First**: Test _should_log_progress thoroughly (it's pure)
3. **Callback Testing**: Verify progress callback behavior via FakeProgressTracker
4. **Validation Edge Cases**: Test all branches of validation logic
5. **Logging Verification**: Use caplog if testing log output

### Testing Patterns

#### Testing Progress Callback Closure
```python
@pytest.mark.asyncio
async def test_progress_callback_behavior():
    fake_storage = FakeDocumentStorageOperations()
    fake_tracker = FakeProgressTracker()
    orchestrator = DocumentProcessingOrchestrator(fake_storage, mapper, fake_tracker)

    await orchestrator.process_and_store(...)

    # Verify progress tracker was called
    assert fake_tracker.get_update_count() > 0

    # Verify specific progress updates
    first_update = fake_tracker.get_update(0)
    assert first_update["status"] == "document_storage"
```

### Future Improvements

1. **Configurable Logging Threshold**: Make 5% threshold configurable
2. **Progress Callback Extraction**: Extract callback creation to separate method for easier testing
3. **Validation Configuration**: Allow disabling validation for testing/debugging
4. **Retry Logic**: Add retry mechanism for transient storage failures
5. **Metrics Collection**: Track storage performance metrics (time, throughput)

### Additional Test Utilities

#### Storage Results Builder
```python
def build_storage_results(
    chunks_stored: int = 10,
    chunk_count: int = 10,
    source_id: str = "src_test",
    url_to_full_document: Optional[dict] = None
) -> dict:
    """Build test storage results."""
    return {
        "chunks_stored": chunks_stored,
        "chunk_count": chunk_count,
        "source_id": source_id,
        "url_to_full_document": url_to_full_document or {},
    }
```

#### Progress Update Simulator
```python
class ProgressUpdateSimulator:
    """Simulate realistic progress update sequences."""

    @staticmethod
    async def simulate_gradual_progress(
        callback: Callable,
        steps: int = 10
    ):
        """Simulate gradual progress from 0 to 100."""
        for i in range(steps + 1):
            progress = int((i / steps) * 100)
            await callback("document_storage", progress, f"Progress {progress}%")
```
