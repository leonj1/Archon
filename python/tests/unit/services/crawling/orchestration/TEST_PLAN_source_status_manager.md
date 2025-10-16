# Test Plan: SourceStatusManager

## Executive Summary

**Service**: `SourceStatusManager` (orchestration/source_status_manager.py)
**Testability Rating**: HIGH
**Lines of Code**: ~141
**External Dependencies**: 3 (DatabaseRepository, update_source_info, logger)
**Recommended Test Coverage**: 100% line, 100% branch

## 1. Function Purity Analysis

### Pure Functions

NONE - All functions involve I/O or external service calls

### Impure Functions

#### `__init__(repository: DatabaseRepository)` (Lines 18-25)
- **Purity**: IMPURE (constructor with state initialization)
- **Side Effects**: Stores repository reference
- **External Dependencies**: DatabaseRepository
- **Testability**: HIGH - Simple dependency injection

#### `async update_to_completed(source_id: str) -> bool` (Lines 27-65)
- **Purity**: IMPURE (database I/O + external service call)
- **Side Effects**:
  - Reads source from repository
  - Updates source via `update_source_info`
  - Verifies update via `_verify_status_update`
  - Logs info and errors
- **External Dependencies**:
  - DatabaseRepository
  - `update_source_info` from source_management_service
- **Testability**: MEDIUM - Requires mocking repository and service function

#### `async update_to_failed(source_id: Optional[str]) -> bool` (Lines 67-100)
- **Purity**: IMPURE (database I/O + external service call)
- **Side Effects**:
  - Reads source from repository
  - Updates source via `update_source_info`
  - Logs info and warnings
- **External Dependencies**:
  - DatabaseRepository
  - `update_source_info` from source_management_service
- **Testability**: MEDIUM - Requires mocking repository and service function

#### `async _verify_status_update(source_id: str, expected_status: str) -> bool` (Lines 102-140)
- **Purity**: IMPURE (database I/O)
- **Side Effects**:
  - Reads source from repository
  - Logs info and errors
- **External Dependencies**: DatabaseRepository
- **Testability**: HIGH - Simple database read with validation logic

## 2. External Dependencies Analysis

### Database Dependencies

#### `DatabaseRepository`
- **Usage**: Data persistence for source status updates
- **Methods Used**:
  - `get_source_by_id(source_id: str) -> Optional[dict]`
- **Interface Needed**: YES - `IDatabaseRepository` Protocol

### Service Dependencies

#### `update_source_info` (from source_management_service)
- **Usage**: Update source metadata including crawl_status
- **Signature**: `async def update_source_info(repository, source_id, summary, word_count, crawl_status)`
- **Interface Needed**: YES - Mock this function or abstract it
- **Recommendation**: Inject as dependency or use Protocol

### Logging Dependencies

#### `logger` (via logfire_config)
- **Usage**: Error and info logging
- **Methods Used**: `logger.error()`, `logger.warning()`
- **Side Effects**: Observable but not affecting return values
- **Interface Needed**: NO - Not critical for unit tests

#### `safe_logfire_info`, `safe_logfire_error`
- **Usage**: Safe logging wrappers
- **Interface Needed**: NO - Can be mocked if needed

## 3. Testability Assessment

### Overall Testability: HIGH

**Strengths**:
1. Clean dependency injection via constructor
2. Clear separation of concerns (update vs verify)
3. Simple boolean return values for easy assertions
4. Private verification method is well-encapsulated
5. Handles edge cases (None source_id, missing source)

**Weaknesses**:
1. Direct import and call of `update_source_info` creates tight coupling
2. No interface abstraction for the service function
3. Verification logic embedded in update_to_completed (could be optional)

**Testing Challenges**:
1. **External Service Call**: `update_source_info` needs to be mocked or abstracted
2. **Async Methods**: Requires proper async test harness
3. **Logging Verification**: If testing logging side effects, need to capture logs

### Recommended Refactoring for Testability

#### Option 1: Inject update_source_info as dependency
```python
def __init__(
    self,
    repository: DatabaseRepository,
    update_source_info_func: Optional[Callable] = None
):
    self.repository = repository
    self.update_source_info = update_source_info_func or update_source_info
```

#### Option 2: Create ISourceUpdater Protocol
```python
class ISourceUpdater(Protocol):
    async def update_source_info(
        self, repository, source_id, summary, word_count, crawl_status
    ) -> None:
        ...
```

## 4. Interface Extraction Plan

### Core Protocols (Priority: HIGH)

#### `IDatabaseRepository`
```python
from typing import Protocol, Optional, Any

class IDatabaseRepository(Protocol):
    """Interface for database repository operations."""

    async def get_source_by_id(self, source_id: str) -> Optional[dict[str, Any]]:
        """
        Get source by ID.

        Returns:
            Source dict with keys: summary, total_word_count, metadata
            None if source not found
        """
        ...
```

#### `ISourceUpdater`
```python
from typing import Protocol

class ISourceUpdater(Protocol):
    """Interface for source update operations."""

    async def __call__(
        self,
        repository: Any,
        source_id: str,
        summary: str,
        word_count: int,
        crawl_status: str,
    ) -> None:
        """Update source information including crawl status."""
        ...
```

### Fake Implementations

#### `FakeDatabaseRepository`
```python
class FakeDatabaseRepository:
    """Fake database repository for testing."""

    def __init__(self):
        self.sources: dict[str, dict[str, Any]] = {}

    async def get_source_by_id(self, source_id: str) -> Optional[dict[str, Any]]:
        return self.sources.get(source_id)

    def add_source(self, source_id: str, source_data: dict[str, Any]):
        """Helper to add test data."""
        self.sources[source_id] = source_data

    def clear(self):
        """Clear all sources."""
        self.sources.clear()
```

#### `FakeSourceUpdater`
```python
class FakeSourceUpdater:
    """Fake source updater for testing."""

    def __init__(self, should_fail: bool = False):
        self.calls: list[dict[str, Any]] = []
        self.should_fail = should_fail

    async def __call__(
        self,
        repository: Any,
        source_id: str,
        summary: str,
        word_count: int,
        crawl_status: str,
    ) -> None:
        self.calls.append({
            "repository": repository,
            "source_id": source_id,
            "summary": summary,
            "word_count": word_count,
            "crawl_status": crawl_status,
        })

        if self.should_fail:
            raise Exception("Fake update failure")

        # Simulate updating the repository
        if hasattr(repository, 'sources') and source_id in repository.sources:
            repository.sources[source_id]["metadata"]["crawl_status"] = crawl_status

    def was_called_with(self, source_id: str, crawl_status: str) -> bool:
        return any(
            call["source_id"] == source_id and call["crawl_status"] == crawl_status
            for call in self.calls
        )

    def call_count(self) -> int:
        return len(self.calls)
```

## 5. Test Plan

### Test File Structure

```
tests/unit/services/crawling/orchestration/
├── test_source_status_manager.py
└── fakes/
    ├── fake_database_repository.py
    └── fake_source_updater.py
```

### Test Scenarios

#### Constructor Tests

**Test: `test_init_with_repository`**
- Setup: Create FakeDatabaseRepository
- Action: Initialize SourceStatusManager(repository)
- Expected: repository assigned
- Type: Unit test with Fake

#### Update to Completed Tests - Success Path

**Test: `test_update_to_completed_success`**
- Setup:
  - FakeDatabaseRepository with source "src_123"
  - Source has: summary="Test", total_word_count=100, metadata={"crawl_status": "in_progress"}
  - FakeSourceUpdater
  - SourceStatusManager
- Action: Call update_to_completed("src_123")
- Expected:
  - Returns True
  - update_source_info called with crawl_status="completed"
  - Source metadata.crawl_status = "completed"
- Type: Unit test with Fakes

**Test: `test_update_to_completed_verifies_update`**
- Setup: FakeDatabaseRepository, FakeSourceUpdater, SourceStatusManager
- Action: Call update_to_completed("src_123")
- Expected: _verify_status_update called (verified by final status check)
- Type: Unit test with Fakes

**Test: `test_update_to_completed_preserves_existing_metadata`**
- Setup:
  - Source with: summary="Docs", total_word_count=500, metadata={...}
  - FakeSourceUpdater
- Action: Call update_to_completed("src_123")
- Expected: update_source_info called with existing summary and word_count
- Type: Unit test with Fakes

#### Update to Completed Tests - Error Cases

**Test: `test_update_to_completed_source_not_found`**
- Setup:
  - FakeDatabaseRepository (empty)
  - SourceStatusManager
- Action: Call update_to_completed("nonexistent")
- Expected:
  - Returns False
  - Logs error "Source not found for status update"
- Type: Unit test with Fake

**Test: `test_update_to_completed_update_service_fails`**
- Setup:
  - FakeDatabaseRepository with source
  - FakeSourceUpdater(should_fail=True)
  - SourceStatusManager with fake updater
- Action: Call update_to_completed("src_123")
- Expected:
  - Returns False
  - Exception caught
  - Logs "Failed to update source crawl_status"
- Type: Unit test with Fakes

**Test: `test_update_to_completed_verification_fails`**
- Setup:
  - FakeDatabaseRepository with source
  - FakeSourceUpdater that doesn't actually update the source
  - SourceStatusManager
- Action: Call update_to_completed("src_123")
- Expected:
  - Returns False
  - Logs "crawl_status update failed to persist"
- Type: Unit test with Fakes

#### Update to Failed Tests - Success Path

**Test: `test_update_to_failed_success`**
- Setup:
  - FakeDatabaseRepository with source "src_456"
  - Source has: summary="Test", total_word_count=100, metadata={"crawl_status": "in_progress"}
  - FakeSourceUpdater
  - SourceStatusManager
- Action: Call update_to_failed("src_456")
- Expected:
  - Returns True
  - update_source_info called with crawl_status="failed"
  - Logs "Updated source crawl_status to failed"
- Type: Unit test with Fakes

**Test: `test_update_to_failed_with_none_source_id`**
- Setup: SourceStatusManager
- Action: Call update_to_failed(None)
- Expected: Returns False (early return)
- Type: Unit test

**Test: `test_update_to_failed_with_empty_source_id`**
- Setup: SourceStatusManager
- Action: Call update_to_failed("")
- Expected: Returns False (falsy check)
- Type: Unit test

#### Update to Failed Tests - Error Cases

**Test: `test_update_to_failed_source_not_found`**
- Setup:
  - FakeDatabaseRepository (empty)
  - SourceStatusManager
- Action: Call update_to_failed("nonexistent")
- Expected: Returns False
- Type: Unit test with Fake

**Test: `test_update_to_failed_update_service_fails`**
- Setup:
  - FakeDatabaseRepository with source
  - FakeSourceUpdater(should_fail=True)
  - SourceStatusManager
- Action: Call update_to_failed("src_456")
- Expected:
  - Returns False
  - Exception caught
  - Logs "Failed to update source crawl_status on error"
- Type: Unit test with Fakes

#### Verify Status Update Tests - Success

**Test: `test_verify_status_update_success`**
- Setup:
  - FakeDatabaseRepository with source "src_123"
  - Source metadata.crawl_status = "completed"
  - SourceStatusManager
- Action: Call _verify_status_update("src_123", "completed")
- Expected:
  - Returns True
  - Logs "Verified crawl_status after update"
- Type: Unit test with Fake

**Test: `test_verify_status_update_matches_expected`**
- Setup: FakeDatabaseRepository with source, crawl_status="failed"
- Action: Call _verify_status_update("src_123", "failed")
- Expected: Returns True
- Type: Unit test with Fake

#### Verify Status Update Tests - Failure

**Test: `test_verify_status_update_source_not_found`**
- Setup: FakeDatabaseRepository (empty)
- Action: Call _verify_status_update("nonexistent", "completed")
- Expected:
  - Returns False
  - Logs "CRITICAL: Failed to verify source after update"
- Type: Unit test with Fake

**Test: `test_verify_status_update_status_mismatch`**
- Setup:
  - FakeDatabaseRepository with source
  - Source metadata.crawl_status = "in_progress"
- Action: Call _verify_status_update("src_123", "completed")
- Expected:
  - Returns False
  - Logs "CRITICAL: crawl_status update failed to persist"
- Type: Unit test with Fake

**Test: `test_verify_status_update_missing_metadata`**
- Setup:
  - FakeDatabaseRepository with source
  - Source has no metadata key
- Action: Call _verify_status_update("src_123", "completed")
- Expected:
  - Returns False
  - verified_status = "MISSING"
  - Logs mismatch error
- Type: Unit test with Fake

**Test: `test_verify_status_update_missing_crawl_status_in_metadata`**
- Setup:
  - FakeDatabaseRepository with source
  - Source metadata exists but no crawl_status key
- Action: Call _verify_status_update("src_123", "completed")
- Expected:
  - Returns False
  - verified_status = "MISSING"
- Type: Unit test with Fake

#### Integration Scenarios (full workflow tests)

**Test: `test_full_success_workflow_completed`**
- Setup:
  - FakeDatabaseRepository with source "src_789"
  - Source: summary="Python Docs", word_count=1000, crawl_status="in_progress"
  - FakeSourceUpdater (working correctly)
  - SourceStatusManager
- Action: Call update_to_completed("src_789")
- Expected:
  - get_source_by_id called once for initial read
  - update_source_info called with correct params
  - get_source_by_id called second time for verification
  - Returns True
- Type: Unit test with Fakes

**Test: `test_full_success_workflow_failed`**
- Setup:
  - FakeDatabaseRepository with source
  - FakeSourceUpdater
  - SourceStatusManager
- Action: Call update_to_failed("src_789")
- Expected:
  - get_source_by_id called once
  - update_source_info called with crawl_status="failed"
  - Returns True
- Type: Unit test with Fakes

**Test: `test_sequential_status_updates`**
- Setup:
  - FakeDatabaseRepository with source "src_999"
  - Initial crawl_status: "pending"
  - FakeSourceUpdater
  - SourceStatusManager
- Action:
  1. Update crawl_status to "in_progress" (manually)
  2. Call update_to_completed("src_999")
  3. Verify status is "completed"
- Expected: Each update persists correctly
- Type: Unit test with Fakes

**Test: `test_update_to_completed_then_to_failed`**
- Setup:
  - FakeDatabaseRepository with source
  - FakeSourceUpdater
  - SourceStatusManager
- Action:
  1. Call update_to_completed("src_123") - succeeds
  2. Manually change status to "in_progress"
  3. Call update_to_failed("src_123") - succeeds
- Expected: Both updates work independently
- Type: Unit test with Fakes

#### Edge Cases

**Test: `test_update_to_completed_with_missing_summary`**
- Setup:
  - FakeDatabaseRepository with source
  - Source has no "summary" key
  - FakeSourceUpdater
- Action: Call update_to_completed("src_123")
- Expected:
  - Uses "" as default summary
  - update_source_info called with summary=""
- Type: Unit test with Fakes

**Test: `test_update_to_completed_with_missing_word_count`**
- Setup:
  - FakeDatabaseRepository with source
  - Source has no "total_word_count" key
  - FakeSourceUpdater
- Action: Call update_to_completed("src_123")
- Expected:
  - Uses 0 as default word_count
  - update_source_info called with word_count=0
- Type: Unit test with Fakes

**Test: `test_update_to_failed_with_special_characters_in_source_id`**
- Setup: FakeDatabaseRepository with source "src_@#$%"
- Action: Call update_to_failed("src_@#$%")
- Expected: Works correctly (no sanitization issues)
- Type: Unit test with Fake

**Test: `test_verify_status_update_with_unicode_status`**
- Setup: FakeDatabaseRepository with source, crawl_status="完成" (Chinese)
- Action: Call _verify_status_update("src_123", "完成")
- Expected: Returns True (Unicode handled correctly)
- Type: Unit test with Fake

#### Concurrency and Race Conditions (if applicable)

**Test: `test_concurrent_updates_to_same_source`**
- Setup:
  - FakeDatabaseRepository with source
  - FakeSourceUpdater tracking call order
  - SourceStatusManager
- Action: Launch 2 concurrent update_to_completed calls
- Expected: Both complete without errors (though one may fail verification)
- Type: Unit test with asyncio.gather

**Test: `test_update_during_verification`**
- Setup:
  - FakeDatabaseRepository that changes status between reads
  - SourceStatusManager
- Action: Call update_to_completed
- Expected: Verification fails (detects inconsistency)
- Type: Unit test with Fake simulating race condition

### Fake Implementations Needed

#### `FakeDatabaseRepository`
- In-memory storage for sources
- Methods: `get_source_by_id`, helper `add_source`, `clear`
- Location: `tests/unit/services/crawling/orchestration/fakes/fake_database_repository.py`

#### `FakeSourceUpdater`
- Tracks all update_source_info calls
- Can simulate failures
- Methods: `__call__`, `was_called_with`, `call_count`
- Location: `tests/unit/services/crawling/orchestration/fakes/fake_source_updater.py`

### Coverage Goals

- **Line Coverage**: 100%
- **Branch Coverage**: 100%
- **Function Coverage**: 100%

### Priority Test Implementation Order

1. **Phase 1**: Constructor tests
2. **Phase 2**: update_to_completed success path
3. **Phase 3**: update_to_completed error cases
4. **Phase 4**: update_to_failed success and error cases
5. **Phase 5**: _verify_status_update (all cases)
6. **Phase 6**: Integration workflows
7. **Phase 7**: Edge cases
8. **Phase 8**: Concurrency tests (optional)

## 6. Test Data Requirements

### Source IDs
- Valid: "src_123", "src_456", "src_789", "src_999"
- Invalid: "nonexistent", None, ""
- Edge cases: "src_@#$%"

### Source Data Structure
```python
{
    "summary": "Documentation for Python library",
    "total_word_count": 1000,
    "metadata": {
        "crawl_status": "in_progress",  # or "completed", "failed", "pending"
        # other metadata...
    }
}
```

### Crawl Status Values
- "pending"
- "in_progress"
- "completed"
- "failed"

## 7. Notes and Recommendations

### Critical Issues to Address Before Testing

1. **Tight Coupling**: `update_source_info` is imported directly. Consider:
   - Inject as dependency via constructor
   - Create Protocol interface for source updater
   - Mock the import in tests

### Testing Best Practices

1. **Async Tests**: Use pytest-asyncio with proper event loop management
2. **Fake Repository**: Ensure FakeDatabaseRepository accurately simulates real repository behavior
3. **Logging Verification**: If testing log output, use caplog fixture
4. **Exception Handling**: Test both caught and uncaught exception scenarios

### Mocking Strategy for `update_source_info`

#### Option 1: Mock the import (if not refactoring)
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_update_to_completed_success():
    with patch('path.to.update_source_info', new_callable=AsyncMock) as mock_update:
        # Test code here
        pass
```

#### Option 2: Inject dependency (recommended)
```python
# In SourceStatusManager.__init__
def __init__(self, repository, update_func=None):
    self.repository = repository
    self.update_source_info = update_func or update_source_info
```

Then in tests:
```python
fake_updater = FakeSourceUpdater()
manager = SourceStatusManager(fake_repo, update_func=fake_updater)
```

### Future Improvements

1. **Optional Verification**: Make verification opt-in rather than automatic
2. **Batch Updates**: Support updating multiple sources at once
3. **Status Transition Validation**: Ensure valid status transitions (e.g., can't go from "completed" to "in_progress")
4. **Retry Logic**: Add retry mechanism for transient failures

### Additional Test Utilities

#### Source Builder Helper
```python
def build_test_source(
    summary: str = "Test Summary",
    word_count: int = 100,
    crawl_status: str = "in_progress",
    **metadata_extras
) -> dict:
    """Build a test source dictionary."""
    return {
        "summary": summary,
        "total_word_count": word_count,
        "metadata": {
            "crawl_status": crawl_status,
            **metadata_extras
        }
    }
```

#### Assertion Helpers
```python
def assert_updater_called_with_status(
    fake_updater: FakeSourceUpdater,
    source_id: str,
    expected_status: str
):
    """Assert updater was called with specific status."""
    assert fake_updater.was_called_with(source_id, expected_status), \
        f"Updater not called with source_id={source_id}, status={expected_status}"
```
