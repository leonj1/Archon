# Test Plan: CodeExamplesOrchestrator

## Executive Summary

**Service**: `CodeExamplesOrchestrator` (orchestration/code_examples_orchestrator.py)
**Testability Rating**: MEDIUM-HIGH
**Lines of Code**: ~165
**External Dependencies**: 4 (DocumentStorageOperations, credential_service, progress_mapper, cancellation_check)
**Recommended Test Coverage**: 100% line, 95%+ branch

## 1. Function Purity Analysis

### Pure Functions

NONE - All functions involve I/O, external service calls, or state queries

### Impure Functions

#### `__init__(doc_storage_ops, progress_mapper, cancellation_check)` (Lines 19-35)
- **Purity**: IMPURE (constructor with state initialization)
- **Side Effects**: Stores dependencies
- **External Dependencies**: DocumentStorageOperations, ProgressMapper, cancellation check function
- **Testability**: HIGH - Clean dependency injection

#### `async extract_code_examples(...)` (Lines 37-104)
- **Purity**: IMPURE (orchestration with multiple external calls)
- **Side Effects**:
  - Checks cancellation status
  - Gets LLM and embedding providers via credential service
  - Calls doc_storage_ops.extract_and_store_code_examples()
  - Updates progress via callback
  - Logs errors
- **External Dependencies**:
  - credential_service (global)
  - DocumentStorageOperations
  - Progress callback
- **Testability**: MEDIUM - Requires mocking multiple external services

#### `async _get_llm_provider(request: dict) -> str` (Lines 106-120)
- **Purity**: IMPURE (external service call with fallback)
- **Side Effects**:
  - Reads from request dict
  - Calls credential_service.get_active_provider()
  - Logs warnings on failure
  - Falls back to "openai"
- **External Dependencies**: credential_service
- **Testability**: HIGH - Clear input/output with exception handling

#### `async _get_embedding_provider() -> str | None` (Lines 122-133)
- **Purity**: IMPURE (external service call with exception handling)
- **Side Effects**:
  - Calls credential_service.get_active_provider("embedding")
  - Logs warnings on failure
  - Returns None on error
- **External Dependencies**: credential_service
- **Testability**: HIGH - Simple external call with error handling

#### `_create_progress_callback(...) -> Callable` (Lines 134-164)
- **Purity**: IMPURE (returns closure with side effects)
- **Side Effects**: Created callback updates progress via mapper and original callback
- **External Dependencies**: progress_mapper, progress_callback
- **Testability**: HIGH - Test closure behavior with mocks

## 2. External Dependencies Analysis

### Document Storage Dependencies

#### `DocumentStorageOperations`
- **Usage**: Code extraction and storage
- **Methods Used**:
  - `extract_and_store_code_examples(crawl_results, url_to_full_document, source_id, callback, cancellation_check, provider, embedding_provider)`
- **Interface Needed**: YES - `IDocumentStorageOperations` Protocol

### Credential Management Dependencies

#### `credential_service` (global singleton)
- **Usage**: Get active LLM and embedding providers
- **Methods Used**:
  - `get_active_provider("llm") -> dict`
  - `get_active_provider("embedding") -> dict`
- **Interface Needed**: YES - `ICredentialService` Protocol
- **Recommendation**: Inject as dependency instead of global import

### Progress Tracking Dependencies

#### `progress_mapper`
- **Usage**: Map raw progress to overall progress
- **Methods Used**:
  - `map_progress(stage: str, progress: int) -> int`
- **Interface Needed**: YES - `IProgressMapper` Protocol

#### `progress_callback: Callable[[dict], Awaitable[None]]`
- **Usage**: Report progress updates
- **Interface Needed**: YES - Protocol or mock

### Cancellation Dependencies

#### `cancellation_check: Callable[[], None]`
- **Usage**: Check if operation should be cancelled
- **Side Effects**: Raises exception if cancelled
- **Interface Needed**: Simple callable, easy to mock

### Logging Dependencies

#### `logger` (via logfire_config)
- **Usage**: Error logging
- **Methods Used**: `logger.error()`, `logger.warning()`
- **Interface Needed**: NO - Not critical for logic

## 3. Testability Assessment

### Overall Testability: MEDIUM-HIGH

**Strengths**:
1. Clean dependency injection for most components
2. Well-structured with helper methods (_get_llm_provider, etc.)
3. Clear separation of concerns (provider fetching, progress tracking, orchestration)
4. Good error handling with fallbacks
5. Handles edge case (extract_code_examples=False) early

**Weaknesses**:
1. **Global credential_service**: Direct import creates tight coupling
2. **Complex orchestration**: extract_code_examples coordinates multiple services
3. **Progress callback wrapping**: Creates nested closures

**Testing Challenges**:
1. **Global Credential Service**: Need to mock global import or inject dependency
2. **Async Operations**: Requires proper async test harness
3. **Progress Callback**: Need to verify closure behavior correctly
4. **Exception Handling**: Multiple exception paths to test

### Recommended Refactoring for Testability

#### Inject credential_service
```python
def __init__(
    self,
    doc_storage_ops: DocumentStorageOperations,
    progress_mapper,
    cancellation_check: Callable[[], None],
    credential_service = None,  # Add this
):
    self.doc_storage_ops = doc_storage_ops
    self.progress_mapper = progress_mapper
    self.cancellation_check = cancellation_check
    self.credential_service = credential_service or credential_service_module.credential_service
```

## 4. Interface Extraction Plan

### Core Protocols (Priority: HIGH)

#### `IDocumentStorageOperations`
```python
from typing import Protocol, Callable, Awaitable, Any, Optional

class IDocumentStorageOperations(Protocol):
    """Interface for document storage operations."""

    async def extract_and_store_code_examples(
        self,
        crawl_results: list[dict[str, Any]],
        url_to_full_document: dict[str, str],
        source_id: str,
        progress_callback: Optional[Callable[[dict], Awaitable[None]]],
        cancellation_check: Callable[[], None],
        provider: str,
        embedding_provider: Optional[str],
    ) -> int:
        """
        Extract and store code examples from crawl results.

        Returns:
            Number of code examples extracted and stored
        """
        ...
```

#### `ICredentialService`
```python
from typing import Protocol, Any

class ICredentialService(Protocol):
    """Interface for credential service."""

    async def get_active_provider(self, provider_type: str) -> dict[str, Any]:
        """
        Get active provider configuration.

        Args:
            provider_type: "llm" or "embedding"

        Returns:
            Dict with "provider" key and other config

        Raises:
            Exception if provider not configured
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

#### `IProgressCallback`
```python
from typing import Protocol, Any, Awaitable

class IProgressCallback(Protocol):
    """Interface for progress callbacks."""

    async def __call__(self, data: dict[str, Any]) -> None:
        """Send progress update."""
        ...
```

### Fake Implementations

#### `FakeDocumentStorageOperations`
```python
class FakeDocumentStorageOperations:
    """Fake document storage for testing."""

    def __init__(self, code_examples_count: int = 5, should_fail: bool = False):
        self.calls: list[dict[str, Any]] = []
        self.code_examples_count = code_examples_count
        self.should_fail = should_fail

    async def extract_and_store_code_examples(
        self, crawl_results, url_to_full_document, source_id,
        progress_callback, cancellation_check, provider, embedding_provider
    ) -> int:
        self.calls.append({
            "crawl_results": crawl_results,
            "url_to_full_document": url_to_full_document,
            "source_id": source_id,
            "progress_callback": progress_callback,
            "cancellation_check": cancellation_check,
            "provider": provider,
            "embedding_provider": embedding_provider,
        })

        if self.should_fail:
            raise RuntimeError("Code extraction failed")

        # Simulate progress updates
        if progress_callback:
            await progress_callback({
                "status": "code_extraction",
                "progress": 50,
                "log": "Extracting code examples...",
            })
            await progress_callback({
                "status": "code_extraction",
                "progress": 100,
                "log": f"Extracted {self.code_examples_count} code examples",
            })

        return self.code_examples_count

    def was_called(self) -> bool:
        return len(self.calls) > 0

    def call_count(self) -> int:
        return len(self.calls)
```

#### `FakeCredentialService`
```python
class FakeCredentialService:
    """Fake credential service for testing."""

    def __init__(self):
        self.providers: dict[str, dict[str, Any]] = {
            "llm": {"provider": "openai"},
            "embedding": {"provider": "openai"},
        }
        self.should_fail: dict[str, bool] = {}

    async def get_active_provider(self, provider_type: str) -> dict[str, Any]:
        if self.should_fail.get(provider_type, False):
            raise Exception(f"No {provider_type} provider configured")
        return self.providers.get(provider_type, {})

    def set_provider(self, provider_type: str, provider: str):
        """Helper to set provider for tests."""
        self.providers[provider_type] = {"provider": provider}

    def set_should_fail(self, provider_type: str, should_fail: bool):
        """Helper to simulate failure for tests."""
        self.should_fail[provider_type] = should_fail
```

#### `FakeProgressMapper`
```python
class FakeProgressMapper:
    """Fake progress mapper for testing."""

    def __init__(self):
        self.calls: list[tuple[str, int]] = []

    def map_progress(self, stage: str, progress: int) -> int:
        self.calls.append((stage, progress))
        # Simple mapping: just add stage offset
        stage_offsets = {
            "code_extraction": 40,
        }
        offset = stage_offsets.get(stage, 0)
        return offset + (progress // 2)  # Simple scaling

    def was_called_with(self, stage: str, progress: int) -> bool:
        return (stage, progress) in self.calls
```

#### `FakeProgressCallback`
```python
class FakeProgressCallback:
    """Fake progress callback for testing."""

    def __init__(self):
        self.calls: list[dict[str, Any]] = []

    async def __call__(self, data: dict[str, Any]) -> None:
        self.calls.append(data.copy())

    def call_count(self) -> int:
        return len(self.calls)

    def get_call(self, index: int) -> dict[str, Any]:
        return self.calls[index]
```

#### `FakeCancellationCheck`
```python
class FakeCancellationCheck:
    """Fake cancellation check for testing."""

    def __init__(self, is_cancelled: bool = False):
        self.is_cancelled = is_cancelled
        self.call_count = 0

    def __call__(self):
        self.call_count += 1
        if self.is_cancelled:
            raise asyncio.CancelledError("Operation cancelled")

    def cancel(self):
        """Mark as cancelled."""
        self.is_cancelled = True
```

## 5. Test Plan

### Test File Structure

```
tests/unit/services/crawling/orchestration/
├── test_code_examples_orchestrator.py
└── fakes/
    ├── fake_document_storage_operations.py
    ├── fake_credential_service.py
    ├── fake_progress_mapper.py
    ├── fake_progress_callback.py
    └── fake_cancellation_check.py
```

### Test Scenarios

#### Constructor Tests

**Test: `test_init_with_all_dependencies`**
- Setup: Create all fake dependencies
- Action: Initialize CodeExamplesOrchestrator
- Expected: All dependencies assigned correctly
- Type: Unit test with Fakes

#### Extract Code Examples Tests - Early Returns

**Test: `test_extract_code_examples_disabled_in_request`**
- Setup:
  - Request with extract_code_examples=False
  - CodeExamplesOrchestrator
- Action: Call extract_code_examples(request, ...)
- Expected:
  - Returns 0 immediately
  - No external calls made
- Type: Unit test

**Test: `test_extract_code_examples_missing_key_defaults_to_true`**
- Setup: Request without extract_code_examples key
- Action: Call extract_code_examples(request, ...)
- Expected: Proceeds with extraction (default True)
- Type: Unit test with Fakes

#### Extract Code Examples Tests - Cancellation

**Test: `test_extract_code_examples_checks_cancellation_early`**
- Setup:
  - FakeCancellationCheck(is_cancelled=True)
  - CodeExamplesOrchestrator
- Action: Call extract_code_examples(request, ...)
- Expected: asyncio.CancelledError raised immediately
- Type: Unit test

#### Extract Code Examples Tests - Provider Fetching

**Test: `test_extract_code_examples_gets_llm_provider_from_request`**
- Setup:
  - Request with provider="anthropic"
  - FakeCredentialService
  - CodeExamplesOrchestrator
- Action: Call extract_code_examples(request, ...)
- Expected: Uses "anthropic" provider from request
- Type: Unit test with Fakes

**Test: `test_extract_code_examples_gets_llm_provider_from_service`**
- Setup:
  - Request without provider key
  - FakeCredentialService with llm provider="openai"
  - CodeExamplesOrchestrator
- Action: Call extract_code_examples(request, ...)
- Expected: Gets provider from credential service
- Type: Unit test with Fakes

**Test: `test_extract_code_examples_gets_embedding_provider`**
- Setup:
  - FakeCredentialService with embedding provider="openai"
  - CodeExamplesOrchestrator
- Action: Call extract_code_examples(request, ...)
- Expected: Gets embedding provider from credential service
- Type: Unit test with Fakes

#### Extract Code Examples Tests - Success Path

**Test: `test_extract_code_examples_success`**
- Setup:
  - FakeDocumentStorageOperations returning 10 code examples
  - All other fakes
  - CodeExamplesOrchestrator
- Action: Call extract_code_examples(request, crawl_results, ...)
- Expected:
  - Returns 10
  - doc_storage_ops.extract_and_store_code_examples() called
  - Called with correct parameters (source_id, provider, embedding_provider)
- Type: Unit test with Fakes

**Test: `test_extract_code_examples_passes_all_parameters`**
- Setup: All fakes, CodeExamplesOrchestrator
- Action: Call extract_code_examples with specific parameters
- Expected:
  - crawl_results passed to storage
  - url_to_full_document passed
  - source_id passed
  - cancellation_check passed
  - provider passed
  - embedding_provider passed
- Type: Unit test with Fakes

**Test: `test_extract_code_examples_with_wrapped_callback`**
- Setup:
  - FakeProgressCallback
  - FakeProgressMapper
  - FakeDocumentStorageOperations
  - CodeExamplesOrchestrator
- Action: Call extract_code_examples with progress_callback
- Expected:
  - Wrapped callback created
  - Wrapped callback passed to doc_storage_ops
  - Wrapped callback maps progress correctly
- Type: Unit test with Fakes

#### Extract Code Examples Tests - Error Handling

**Test: `test_extract_code_examples_handles_runtime_error`**
- Setup:
  - FakeDocumentStorageOperations(should_fail=True)
  - FakeProgressCallback
  - CodeExamplesOrchestrator
- Action: Call extract_code_examples(request, ...)
- Expected:
  - RuntimeError caught
  - Returns 0
  - Logs error
  - Progress callback called with failure message
- Type: Unit test with Fakes

**Test: `test_extract_code_examples_error_reports_to_progress`**
- Setup:
  - FakeDocumentStorageOperations(should_fail=True)
  - FakeProgressCallback
  - CodeExamplesOrchestrator
- Action: Call extract_code_examples with progress_callback
- Expected:
  - Progress callback called with:
    - status="code_extraction"
    - progress=mapped(100)
    - log contains "Code extraction failed"
    - total_pages included
- Type: Unit test with Fakes

**Test: `test_extract_code_examples_error_without_progress_callback`**
- Setup:
  - FakeDocumentStorageOperations(should_fail=True)
  - CodeExamplesOrchestrator
- Action: Call extract_code_examples with progress_callback=None
- Expected:
  - Returns 0
  - No exception raised
  - Error logged
- Type: Unit test with Fakes

#### Get LLM Provider Tests

**Test: `test_get_llm_provider_from_request`**
- Setup: Request with provider="anthropic"
- Action: Call _get_llm_provider(request)
- Expected: Returns "anthropic"
- Type: Unit test

**Test: `test_get_llm_provider_from_credential_service`**
- Setup:
  - Request without provider
  - FakeCredentialService with llm provider="openai"
- Action: Call _get_llm_provider(request)
- Expected:
  - credential_service.get_active_provider("llm") called
  - Returns "openai"
- Type: Unit test with Fake

**Test: `test_get_llm_provider_credential_service_fails`**
- Setup:
  - Request without provider
  - FakeCredentialService that raises exception
- Action: Call _get_llm_provider(request)
- Expected:
  - Exception caught
  - Logs warning
  - Returns "openai" (default fallback)
- Type: Unit test with Fake

**Test: `test_get_llm_provider_credential_service_returns_empty_dict`**
- Setup:
  - Request without provider
  - FakeCredentialService returning {}
- Action: Call _get_llm_provider(request)
- Expected: Returns "openai" (fallback from empty dict.get("provider", "openai"))
- Type: Unit test with Fake

#### Get Embedding Provider Tests

**Test: `test_get_embedding_provider_success`**
- Setup: FakeCredentialService with embedding provider="openai"
- Action: Call _get_embedding_provider()
- Expected: Returns "openai"
- Type: Unit test with Fake

**Test: `test_get_embedding_provider_credential_service_fails`**
- Setup: FakeCredentialService that raises exception
- Action: Call _get_embedding_provider()
- Expected:
  - Exception caught
  - Logs warning
  - Returns None
- Type: Unit test with Fake

**Test: `test_get_embedding_provider_returns_none_on_missing_provider`**
- Setup: FakeCredentialService returning {"provider": None}
- Action: Call _get_embedding_provider()
- Expected: Returns None
- Type: Unit test with Fake

#### Create Progress Callback Tests

**Test: `test_create_progress_callback_maps_progress`**
- Setup:
  - FakeProgressCallback
  - FakeProgressMapper
  - CodeExamplesOrchestrator
- Action:
  - Create wrapped callback
  - Invoke with {"progress": 50, "status": "extracting"}
- Expected:
  - progress_mapper.map_progress("code_extraction", 50) called
  - Original callback called with mapped progress
- Type: Unit test with Fakes

**Test: `test_create_progress_callback_with_percentage_key`**
- Setup: FakeProgressCallback, FakeProgressMapper
- Action: Invoke wrapped callback with {"percentage": 75, "status": "extracting"}
- Expected:
  - progress_mapper.map_progress("code_extraction", 75) called
  - Original callback receives mapped progress
- Type: Unit test with Fakes

**Test: `test_create_progress_callback_defaults_to_zero_progress`**
- Setup: FakeProgressCallback, FakeProgressMapper
- Action: Invoke wrapped callback with {"status": "extracting"} (no progress/percentage)
- Expected: progress_mapper.map_progress("code_extraction", 0) called
- Type: Unit test with Fakes

**Test: `test_create_progress_callback_includes_total_pages`**
- Setup: FakeProgressCallback, total_pages=20
- Action: Create and invoke wrapped callback
- Expected:
  - Original callback receives data with total_pages=20
- Type: Unit test with Fakes

**Test: `test_create_progress_callback_preserves_other_fields`**
- Setup: FakeProgressCallback
- Action: Invoke with {"progress": 50, "custom_field": "value", "another": 123}
- Expected:
  - Original callback receives custom_field and another
  - Core fields (status, progress, log) set correctly
- Type: Unit test with Fakes

**Test: `test_create_progress_callback_with_none_callback`**
- Setup: progress_callback=None
- Action: Create wrapped callback (should still be callable)
- Expected: Wrapped callback created, does nothing when invoked
- Type: Unit test

#### Integration Scenarios

**Test: `test_full_extraction_workflow_with_progress`**
- Setup:
  - All fakes
  - FakeDocumentStorageOperations returning 15 examples
  - FakeProgressCallback
  - CodeExamplesOrchestrator
- Request: {"extract_code_examples": True}
- crawl_results: 10 pages
- Action: Call extract_code_examples
- Expected:
  1. Cancellation checked
  2. LLM provider fetched
  3. Embedding provider fetched
  4. Wrapped callback created
  5. doc_storage_ops called
  6. Progress updates mapped and forwarded
  7. Returns 15
- Type: Unit test with comprehensive Fakes

**Test: `test_extraction_with_anthropic_provider`**
- Setup:
  - Request with provider="anthropic"
  - FakeCredentialService
  - FakeDocumentStorageOperations
  - CodeExamplesOrchestrator
- Action: Call extract_code_examples
- Expected:
  - doc_storage_ops called with provider="anthropic"
- Type: Unit test with Fakes

**Test: `test_extraction_with_custom_embedding_provider`**
- Setup:
  - FakeCredentialService with embedding provider="voyage"
  - FakeDocumentStorageOperations
  - CodeExamplesOrchestrator
- Action: Call extract_code_examples
- Expected:
  - doc_storage_ops called with embedding_provider="voyage"
- Type: Unit test with Fakes

#### Edge Cases

**Test: `test_extract_code_examples_with_empty_crawl_results`**
- Setup: All fakes, CodeExamplesOrchestrator
- Action: Call extract_code_examples with crawl_results=[]
- Expected: Still attempts extraction (0 results is valid)
- Type: Unit test with Fakes

**Test: `test_extract_code_examples_with_zero_examples_found`**
- Setup: FakeDocumentStorageOperations returning 0
- Action: Call extract_code_examples
- Expected: Returns 0 (valid outcome)
- Type: Unit test with Fakes

**Test: `test_extract_code_examples_with_large_page_count`**
- Setup:
  - total_pages=1000
  - FakeDocumentStorageOperations
  - CodeExamplesOrchestrator
- Action: Call extract_code_examples
- Expected: Handles large page count correctly
- Type: Unit test with Fakes

**Test: `test_extract_code_examples_with_special_characters_in_source_id`**
- Setup: source_id="src_@#$%^&*()"
- Action: Call extract_code_examples
- Expected: Works correctly (no sanitization issues)
- Type: Unit test with Fakes

### Fake Implementations Needed (Summary)

1. `FakeDocumentStorageOperations` - Simulates code extraction
2. `FakeCredentialService` - Provides provider configurations
3. `FakeProgressMapper` - Maps progress values
4. `FakeProgressCallback` - Tracks progress updates
5. `FakeCancellationCheck` - Simulates cancellation

### Coverage Goals

- **Line Coverage**: 100%
- **Branch Coverage**: 95%+ (some error paths may be hard to trigger)
- **Function Coverage**: 100%

### Priority Test Implementation Order

1. **Phase 1**: Constructor and early return tests
2. **Phase 2**: Provider fetching tests (_get_llm_provider, _get_embedding_provider)
3. **Phase 3**: Success path (extract_code_examples with all Fakes)
4. **Phase 4**: Error handling (RuntimeError caught)
5. **Phase 5**: Progress callback wrapping (_create_progress_callback)
6. **Phase 6**: Cancellation tests
7. **Phase 7**: Integration workflows
8. **Phase 8**: Edge cases

## 6. Test Data Requirements

### Request Data
```python
{
    "extract_code_examples": True,  # or False
    "provider": "openai",  # optional
}
```

### Crawl Results
```python
[
    {"url": "https://example.com/page1", "markdown": "# Code\n```python\nprint('hello')\n```"},
    {"url": "https://example.com/page2", "markdown": "# More Code\n```js\nconsole.log('hi')\n```"},
]
```

### URL to Full Document Mapping
```python
{
    "https://example.com/page1": "Full document text for page 1",
    "https://example.com/page2": "Full document text for page 2",
}
```

### Provider Configurations
- LLM providers: "openai", "anthropic", "ollama"
- Embedding providers: "openai", "voyage", None

## 7. Notes and Recommendations

### Critical Issues to Address Before Testing

1. **Global credential_service**: Consider injecting as dependency for easier testing
2. **Progress Callback Complexity**: The nested wrapper adds complexity; consider simplifying

### Testing Best Practices

1. **Mock credential_service**: Use patch or inject fake
2. **Async Tests**: Use pytest-asyncio
3. **Progress Tracking**: Verify both call count and arguments
4. **Exception Handling**: Test all exception paths

### Mocking Strategy for credential_service

#### Option 1: Patch the import
```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_extract_code_examples():
    with patch('path.to.credential_service') as mock_cred:
        mock_cred.get_active_provider = AsyncMock(return_value={"provider": "openai"})
        # Test code
```

#### Option 2: Inject as dependency (recommended)
```python
# Refactor __init__ to accept credential_service
orchestrator = CodeExamplesOrchestrator(
    doc_storage_ops,
    progress_mapper,
    cancellation_check,
    credential_service=fake_cred_service
)
```

### Future Improvements

1. **Inject credential_service**: Make it a constructor parameter
2. **Simplify Progress Callback**: Consider reducing nesting complexity
3. **Configurable Defaults**: Allow customizing default provider
4. **Batch Extraction**: Support extracting code from multiple sources at once
