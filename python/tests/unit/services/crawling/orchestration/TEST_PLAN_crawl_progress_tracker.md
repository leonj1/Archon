# Test Plan: CrawlProgressTracker

## Executive Summary

**Service**: `CrawlProgressTracker` (orchestration/crawl_progress_tracker.py)
**Testability Rating**: HIGH
**Lines of Code**: ~158
**External Dependencies**: 3 (ProgressTracker, ProgressMapper, handle_progress_update callback)
**Recommended Test Coverage**: 100% line, 100% branch

## 1. Function Purity Analysis

### Pure Functions

NONE - All functions involve I/O or state queries

### Impure Functions

#### `__init__(progress_tracker, progress_mapper, task_id, handle_progress_update)` (Lines 19-38)
- **Purity**: IMPURE (constructor with state initialization)
- **Side Effects**: Stores dependencies
- **External Dependencies**: ProgressTracker, ProgressMapper, callback function
- **Testability**: HIGH - Clean dependency injection

#### `async start(url: str)` (Lines 40-53)
- **Purity**: IMPURE (conditional I/O)
- **Side Effects**: Calls progress_tracker.start() if tracker exists
- **External Dependencies**: ProgressTracker
- **Testability**: HIGH - Simple delegation with null check

#### `async update_mapped(stage, stage_progress, message, **kwargs)` (Lines 55-77)
- **Purity**: IMPURE (progress mapping + callback)
- **Side Effects**:
  - Maps progress via progress_mapper
  - Calls handle_progress_update callback
- **External Dependencies**: ProgressMapper, callback function
- **Testability**: HIGH - Clear input/output with mapping

#### `async update_with_crawl_type(crawl_type: str)` (Lines 79-95)
- **Purity**: IMPURE (conditional I/O)
- **Side Effects**: Updates progress_tracker if it exists
- **External Dependencies**: ProgressTracker, ProgressMapper
- **Testability**: HIGH - Delegation with null check

#### `async update_with_source_id(source_id: str)` (Lines 97-117)
- **Purity**: IMPURE (conditional I/O)
- **Side Effects**:
  - Updates progress_tracker if it exists
  - Logs info
- **External Dependencies**: ProgressTracker, logger
- **Testability**: HIGH - Delegation with null check

#### `async complete(chunks_stored, code_examples_found, processed_pages, total_pages, source_id)` (Lines 119-147)
- **Purity**: IMPURE (conditional I/O)
- **Side Effects**: Calls progress_tracker.complete() if tracker exists
- **External Dependencies**: ProgressTracker
- **Testability**: HIGH - Delegation with null check

#### `async error(error_message: str)` (Lines 149-157)
- **Purity**: IMPURE (conditional I/O)
- **Side Effects**: Calls progress_tracker.error() if tracker exists
- **External Dependencies**: ProgressTracker
- **Testability**: HIGH - Delegation with null check

## 2. External Dependencies Analysis

### Progress Tracking Dependencies

#### `ProgressTracker` (Optional)
- **Usage**: HTTP polling progress updates
- **Methods Used**:
  - `start(data: dict)`
  - `update(status, progress, log, **kwargs)`
  - `complete(completion_data: dict)`
  - `error(error_message: str)`
  - `state: dict` (property access)
- **Interface Needed**: YES - `IProgressTracker` Protocol

#### `ProgressMapper`
- **Usage**: Map stage-specific progress to overall progress
- **Methods Used**:
  - `map_progress(stage: str, progress: int) -> int`
- **Interface Needed**: YES - `IProgressMapper` Protocol

#### `handle_progress_update: Callable[[str, dict], Awaitable[None]]`
- **Usage**: Handle progress update events
- **Signature**: `async def handle_progress_update(task_id: str, update: dict) -> None`
- **Interface Needed**: Simple callable, easy to mock

### Logging Dependencies

#### `logger`, `safe_logfire_info`
- **Usage**: Info logging
- **Methods Used**: `safe_logfire_info()`
- **Interface Needed**: NO - Not critical for logic

## 3. Testability Assessment

### Overall Testability: HIGH

**Strengths**:
1. Excellent dependency injection (all dependencies via constructor)
2. Clean separation of concerns (delegation pattern)
3. Consistent null checks for optional progress_tracker
4. Simple, focused methods with single responsibilities
5. No complex orchestration or business logic
6. Easy to test both with and without progress_tracker

**Weaknesses**:
1. None significant - well-designed for testability

**Testing Challenges**:
1. **Optional ProgressTracker**: Need to test both paths (with and without tracker)
2. **Async Methods**: Requires async test harness

### Recommended Refactoring for Testability

NONE - Code is already well-structured for testing

## 4. Interface Extraction Plan

### Core Protocols (Priority: HIGH)

#### `IProgressTracker`
```python
from typing import Protocol, Any, Optional

class IProgressTracker(Protocol):
    """Interface for progress tracking."""

    state: dict[str, Any]  # Property for reading state

    async def start(self, initial_data: dict[str, Any]) -> None:
        ...

    async def update(
        self, status: str, progress: int, log: str, **kwargs
    ) -> None:
        ...

    async def complete(self, completion_data: dict[str, Any]) -> None:
        ...

    async def error(self, error_message: str) -> None:
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

#### `IProgressUpdateHandler`
```python
from typing import Protocol, Any, Awaitable

class IProgressUpdateHandler(Protocol):
    """Interface for progress update handler."""

    async def __call__(self, task_id: str, update: dict[str, Any]) -> None:
        """Handle a progress update."""
        ...
```

### Fake Implementations

#### `FakeProgressTracker`
```python
class FakeProgressTracker:
    """Fake progress tracker for testing."""

    def __init__(self):
        self.state: dict[str, Any] = {
            "status": "initializing",
            "progress": 0,
            "log": "Starting...",
        }
        self.start_calls: list[dict] = []
        self.update_calls: list[dict] = []
        self.complete_calls: list[dict] = []
        self.error_calls: list[str] = []

    async def start(self, initial_data: dict[str, Any]) -> None:
        self.start_calls.append(initial_data.copy())
        self.state.update(initial_data)

    async def update(
        self, status: str, progress: int, log: str, **kwargs
    ) -> None:
        self.update_calls.append({
            "status": status,
            "progress": progress,
            "log": log,
            **kwargs
        })
        self.state.update({
            "status": status,
            "progress": progress,
            "log": log,
            **kwargs
        })

    async def complete(self, completion_data: dict[str, Any]) -> None:
        self.complete_calls.append(completion_data.copy())
        self.state.update(completion_data)

    async def error(self, error_message: str) -> None:
        self.error_calls.append(error_message)
        self.state["error"] = error_message
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
        return self._mappings.get((stage, progress), stage.hash() % 100 + progress)

    def set_mapping(self, stage: str, progress: int, mapped_value: int):
        """Set a specific mapping for testing."""
        self._mappings[(stage, progress)] = mapped_value
```

#### `FakeProgressUpdateHandler`
```python
class FakeProgressUpdateHandler:
    """Fake progress update handler for testing."""

    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    async def __call__(self, task_id: str, update: dict[str, Any]) -> None:
        self.calls.append((task_id, update.copy()))

    def was_called_with_task_id(self, task_id: str) -> bool:
        return any(call[0] == task_id for call in self.calls)

    def get_calls_for_task(self, task_id: str) -> list[dict]:
        return [call[1] for call in self.calls if call[0] == task_id]
```

## 5. Test Plan

### Test File Structure

```
tests/unit/services/crawling/orchestration/
├── test_crawl_progress_tracker.py
└── fakes/
    ├── fake_progress_tracker.py
    ├── fake_progress_mapper.py
    └── fake_progress_update_handler.py
```

### Test Scenarios

#### Constructor Tests

**Test: `test_init_with_all_dependencies`**
- Setup: Create all fakes
- Action: Initialize CrawlProgressTracker
- Expected: All dependencies assigned
- Type: Unit test with Fakes

**Test: `test_init_with_none_progress_tracker`**
- Setup: Create CrawlProgressTracker with progress_tracker=None
- Action: Initialize
- Expected: Tracker is None, other dependencies assigned
- Type: Unit test with Fakes

#### Start Tests - With Progress Tracker

**Test: `test_start_with_tracker`**
- Setup:
  - FakeProgressTracker
  - CrawlProgressTracker
- Action: Call start("https://example.com")
- Expected:
  - progress_tracker.start() called
  - Initial data includes: url, status="starting", progress=0, log
- Type: Unit test with Fake

**Test: `test_start_formats_initial_data_correctly`**
- Setup: FakeProgressTracker, CrawlProgressTracker
- Action: Call start("https://docs.python.org")
- Expected:
  - start_calls[0]["url"] = "https://docs.python.org"
  - start_calls[0]["status"] = "starting"
  - start_calls[0]["progress"] = 0
  - start_calls[0]["log"] = "Starting crawl of https://docs.python.org"
- Type: Unit test with Fake

#### Start Tests - Without Progress Tracker

**Test: `test_start_without_tracker`**
- Setup: CrawlProgressTracker with progress_tracker=None
- Action: Call start("https://example.com")
- Expected: No exception, method returns without error
- Type: Unit test

#### Update Mapped Tests - With Progress Tracker

**Test: `test_update_mapped_maps_progress`**
- Setup:
  - FakeProgressMapper (set mapping: "crawling", 50 -> 25)
  - FakeProgressUpdateHandler
  - CrawlProgressTracker
- Action: Call update_mapped("crawling", 50, "Crawling pages")
- Expected:
  - progress_mapper.map_progress("crawling", 50) called
  - handle_progress_update called with progress=25
- Type: Unit test with Fakes

**Test: `test_update_mapped_includes_all_data`**
- Setup: All fakes, CrawlProgressTracker
- Action: Call update_mapped("processing", 75, "Processing data", custom_field="value", pages=10)
- Expected:
  - handle_progress_update called with:
    - task_id
    - status="processing"
    - progress=<mapped>
    - log="Processing data"
    - message="Processing data"
    - custom_field="value"
    - pages=10
- Type: Unit test with Fakes

**Test: `test_update_mapped_with_zero_progress`**
- Setup: All fakes
- Action: Call update_mapped("starting", 0, "Starting...")
- Expected: progress_mapper.map_progress("starting", 0) called
- Type: Unit test with Fakes

**Test: `test_update_mapped_with_hundred_progress`**
- Setup: All fakes
- Action: Call update_mapped("completed", 100, "Done")
- Expected: progress_mapper.map_progress("completed", 100) called
- Type: Unit test with Fakes

#### Update Mapped Tests - Without Progress Tracker

**Test: `test_update_mapped_still_calls_handler_without_tracker`**
- Setup:
  - progress_tracker=None
  - FakeProgressMapper
  - FakeProgressUpdateHandler
  - CrawlProgressTracker
- Action: Call update_mapped("crawling", 50, "Message")
- Expected:
  - progress_mapper.map_progress() still called
  - handle_progress_update() still called
- Type: Unit test with Fakes

#### Update With Crawl Type Tests - With Progress Tracker

**Test: `test_update_with_crawl_type_updates_tracker`**
- Setup: FakeProgressTracker, FakeProgressMapper, CrawlProgressTracker
- Action: Call update_with_crawl_type("sitemap")
- Expected:
  - progress_tracker.update() called
  - status="crawling"
  - progress=<mapped for 100%>
  - log="Processing sitemap content"
  - crawl_type="sitemap"
- Type: Unit test with Fakes

**Test: `test_update_with_crawl_type_maps_to_crawling_stage`**
- Setup:
  - FakeProgressMapper (set mapping: "crawling", 100 -> 15)
  - FakeProgressTracker
  - CrawlProgressTracker
- Action: Call update_with_crawl_type("normal")
- Expected:
  - progress_mapper.map_progress("crawling", 100) called
  - progress_tracker.update() called with progress=15
- Type: Unit test with Fakes

**Test: `test_update_with_crawl_type_with_empty_string`**
- Setup: FakeProgressTracker, CrawlProgressTracker
- Action: Call update_with_crawl_type("")
- Expected:
  - Returns without calling tracker (early return on falsy crawl_type)
- Type: Unit test with Fake

**Test: `test_update_with_crawl_type_with_none`**
- Setup: FakeProgressTracker, CrawlProgressTracker
- Action: Call update_with_crawl_type(None)
- Expected: Returns without calling tracker
- Type: Unit test with Fake

#### Update With Crawl Type Tests - Without Progress Tracker

**Test: `test_update_with_crawl_type_without_tracker`**
- Setup: CrawlProgressTracker with progress_tracker=None
- Action: Call update_with_crawl_type("normal")
- Expected: No exception, early return
- Type: Unit test

#### Update With Source ID Tests - With Progress Tracker

**Test: `test_update_with_source_id_updates_tracker`**
- Setup: FakeProgressTracker, CrawlProgressTracker
- Action: Call update_with_source_id("src_12345")
- Expected:
  - progress_tracker.update() called
  - status=<current status from tracker.state>
  - progress=<current progress from tracker.state>
  - log=<current log from tracker.state>
  - source_id="src_12345"
- Type: Unit test with Fake

**Test: `test_update_with_source_id_preserves_existing_state`**
- Setup:
  - FakeProgressTracker with state: {status="processing", progress=50, log="Working"}
  - CrawlProgressTracker
- Action: Call update_with_source_id("src_99999")
- Expected:
  - update() called with status="processing", progress=50, log="Working"
  - source_id="src_99999" added to kwargs
- Type: Unit test with Fake

**Test: `test_update_with_source_id_logs_info`**
- Setup: FakeProgressTracker, CrawlProgressTracker
- Action: Call update_with_source_id("src_abc")
- Expected: Logs info message with task_id and source_id
- Type: Unit test with Fake (optional: capture logs)

**Test: `test_update_with_source_id_with_empty_string`**
- Setup: FakeProgressTracker, CrawlProgressTracker
- Action: Call update_with_source_id("")
- Expected: Returns without calling tracker (early return on falsy)
- Type: Unit test with Fake

**Test: `test_update_with_source_id_with_none`**
- Setup: FakeProgressTracker, CrawlProgressTracker
- Action: Call update_with_source_id(None)
- Expected: Returns without calling tracker
- Type: Unit test with Fake

#### Update With Source ID Tests - Without Progress Tracker

**Test: `test_update_with_source_id_without_tracker`**
- Setup: CrawlProgressTracker with progress_tracker=None
- Action: Call update_with_source_id("src_123")
- Expected: No exception, early return
- Type: Unit test

#### Complete Tests - With Progress Tracker

**Test: `test_complete_calls_tracker`**
- Setup: FakeProgressTracker, CrawlProgressTracker
- Action: Call complete(100, 5, 10, 10, "src_final")
- Expected:
  - progress_tracker.complete() called
  - completion_data includes: chunks_stored=100, code_examples_found=5, processed_pages=10, total_pages=10, sourceId="src_final", log="Crawl completed successfully!"
- Type: Unit test with Fake

**Test: `test_complete_with_zero_chunks`**
- Setup: FakeProgressTracker, CrawlProgressTracker
- Action: Call complete(0, 0, 5, 5, "src_empty")
- Expected: complete() called with all zeros
- Type: Unit test with Fake

**Test: `test_complete_with_partial_pages`**
- Setup: FakeProgressTracker, CrawlProgressTracker
- Action: Call complete(50, 2, 5, 10, "src_partial")
- Expected:
  - processed_pages=5
  - total_pages=10
- Type: Unit test with Fake

#### Complete Tests - Without Progress Tracker

**Test: `test_complete_without_tracker`**
- Setup: CrawlProgressTracker with progress_tracker=None
- Action: Call complete(100, 5, 10, 10, "src_123")
- Expected: No exception, early return
- Type: Unit test

#### Error Tests - With Progress Tracker

**Test: `test_error_calls_tracker`**
- Setup: FakeProgressTracker, CrawlProgressTracker
- Action: Call error("Crawl failed: Network error")
- Expected: progress_tracker.error() called with message
- Type: Unit test with Fake

**Test: `test_error_with_empty_message`**
- Setup: FakeProgressTracker, CrawlProgressTracker
- Action: Call error("")
- Expected: progress_tracker.error() called with ""
- Type: Unit test with Fake

**Test: `test_error_with_long_message`**
- Setup: FakeProgressTracker, CrawlProgressTracker
- Action: Call error("A" * 1000)
- Expected: progress_tracker.error() called with full message
- Type: Unit test with Fake

#### Error Tests - Without Progress Tracker

**Test: `test_error_without_tracker`**
- Setup: CrawlProgressTracker with progress_tracker=None
- Action: Call error("Some error")
- Expected: No exception, early return
- Type: Unit test

#### Integration Scenarios (realistic workflow)

**Test: `test_full_crawl_workflow`**
- Setup: All fakes, CrawlProgressTracker
- Action: Simulate full crawl:
  1. start("https://example.com")
  2. update_mapped("analyzing", 50, "Analyzing...")
  3. update_mapped("crawling", 25, "Crawling...", processed_pages=5, total_pages=20)
  4. update_with_crawl_type("normal")
  5. update_mapped("processing", 50, "Processing...")
  6. update_with_source_id("src_123")
  7. update_mapped("storing", 100, "Storing...")
  8. complete(100, 5, 20, 20, "src_123")
- Expected:
  - All methods called in order
  - progress_tracker has correct final state
  - handle_progress_update called multiple times
- Type: Unit test with Fakes

**Test: `test_crawl_workflow_with_error`**
- Setup: All fakes, CrawlProgressTracker
- Action: Simulate crawl with error:
  1. start("https://example.com")
  2. update_mapped("crawling", 50, "Crawling...")
  3. error("Crawl failed: Timeout")
- Expected:
  - progress_tracker.error() called
  - No complete() called
- Type: Unit test with Fakes

**Test: `test_workflow_without_tracker`**
- Setup: progress_tracker=None, other fakes
- Action: Run full workflow
- Expected:
  - No exceptions
  - handle_progress_update still called for update_mapped
- Type: Unit test with Fakes

#### Edge Cases

**Test: `test_update_mapped_with_very_long_message`**
- Setup: All fakes
- Action: Call update_mapped("stage", 50, "A" * 10000)
- Expected: Works correctly (no truncation)
- Type: Unit test with Fakes

**Test: `test_update_mapped_with_negative_progress`**
- Setup: All fakes
- Action: Call update_mapped("stage", -10, "Message")
- Expected: progress_mapper.map_progress("stage", -10) called (mapper handles validation)
- Type: Unit test with Fakes

**Test: `test_update_mapped_with_progress_over_hundred`**
- Setup: All fakes
- Action: Call update_mapped("stage", 150, "Message")
- Expected: progress_mapper.map_progress("stage", 150) called
- Type: Unit test with Fakes

**Test: `test_complete_with_negative_chunks`**
- Setup: FakeProgressTracker
- Action: Call complete(-5, 0, 10, 10, "src")
- Expected: Works (no validation in tracker itself)
- Type: Unit test with Fake

**Test: `test_update_with_source_id_with_unicode`**
- Setup: FakeProgressTracker
- Action: Call update_with_source_id("src_日本語")
- Expected: Works correctly (Unicode handled)
- Type: Unit test with Fake

### Fake Implementations Needed (Summary)

1. `FakeProgressTracker` - Tracks all method calls
2. `FakeProgressMapper` - Maps progress with configurable mappings
3. `FakeProgressUpdateHandler` - Tracks all progress update calls

### Coverage Goals

- **Line Coverage**: 100%
- **Branch Coverage**: 100%
- **Function Coverage**: 100%

### Priority Test Implementation Order

1. **Phase 1**: Constructor tests
2. **Phase 2**: start() tests (with and without tracker)
3. **Phase 3**: update_mapped() tests
4. **Phase 4**: update_with_crawl_type() tests
5. **Phase 5**: update_with_source_id() tests
6. **Phase 6**: complete() tests
7. **Phase 7**: error() tests
8. **Phase 8**: Integration workflows and edge cases

## 6. Test Data Requirements

### Task IDs
- "task-123", "task-abc", "task-test"

### URLs
- "https://example.com", "https://docs.python.org"

### Stages
- "starting", "analyzing", "crawling", "processing", "storing", "completed"

### Crawl Types
- "normal", "sitemap", "text_file", "link_collection_with_crawled_links"

### Source IDs
- "src_123", "src_abc", "src_final", "src_日本語"

### Progress Values
- 0, 25, 50, 75, 100, -10, 150

### Completion Data
```python
{
    "chunks_stored": 100,
    "code_examples_found": 5,
    "processed_pages": 10,
    "total_pages": 10,
    "sourceId": "src_123",
    "log": "Crawl completed successfully!"
}
```

## 7. Notes and Recommendations

### Critical Issues to Address Before Testing

NONE - Code is well-structured and ready for testing

### Testing Best Practices

1. **Async Tests**: Use pytest-asyncio
2. **With/Without Tracker**: Test both code paths for all methods
3. **State Verification**: Verify both method calls and state changes
4. **Fake Completeness**: Ensure FakeProgressTracker mimics real behavior

### Testing Patterns

#### Testing Optional Tracker Pattern
```python
@pytest.mark.asyncio
async def test_method_with_tracker():
    fake_tracker = FakeProgressTracker()
    tracker = CrawlProgressTracker(fake_tracker, ...)
    await tracker.some_method(...)
    assert len(fake_tracker.some_calls) > 0

@pytest.mark.asyncio
async def test_method_without_tracker():
    tracker = CrawlProgressTracker(None, ...)
    await tracker.some_method(...)  # Should not raise
```

### Future Improvements

1. **Validation**: Add input validation for progress values (0-100)
2. **State Transitions**: Validate state transitions (e.g., can't call complete after error)
3. **Metrics**: Track timing information (duration between updates)
4. **Batch Updates**: Support batching multiple updates efficiently

### Additional Test Utilities

#### Progress Update Assertion Helper
```python
def assert_progress_update_called_with(
    fake_handler: FakeProgressUpdateHandler,
    task_id: str,
    expected_status: str,
    expected_progress: int
):
    """Assert handler was called with specific values."""
    calls = fake_handler.get_calls_for_task(task_id)
    assert any(
        call["status"] == expected_status and call["progress"] == expected_progress
        for call in calls
    ), f"Handler not called with status={expected_status}, progress={expected_progress}"
```

#### Workflow Builder
```python
class CrawlWorkflowBuilder:
    """Helper to build test crawl workflows."""

    def __init__(self, tracker: CrawlProgressTracker):
        self.tracker = tracker

    async def standard_workflow(self, url: str, source_id: str):
        """Execute a standard crawl workflow."""
        await self.tracker.start(url)
        await self.tracker.update_mapped("crawling", 50, "Crawling...")
        await self.tracker.update_with_crawl_type("normal")
        await self.tracker.update_with_source_id(source_id)
        await self.tracker.complete(100, 5, 10, 10, source_id)
```
