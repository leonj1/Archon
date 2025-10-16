# Test Plan: HeartbeatManager

## Executive Summary

**Service**: `HeartbeatManager` (orchestration/heartbeat_manager.py)
**Testability Rating**: HIGH
**Lines of Code**: ~61
**External Dependencies**: 2 (asyncio, logger)
**Recommended Test Coverage**: 100% line, 100% branch

## 1. Function Purity Analysis

### Pure Functions

NONE - All functions have side effects (time-based or I/O operations)

### Impure Functions

#### `__init__(interval: float, progress_callback)` (Lines 18-32)
- **Purity**: IMPURE (constructor with state initialization)
- **Side Effects**:
  - Stores interval and progress_callback
  - Calls `asyncio.get_event_loop().time()` to initialize timestamp
- **External Dependencies**: asyncio event loop
- **Testability**: HIGH - Simple state initialization

#### `async send_if_needed(current_stage: str, current_progress: int)` (Lines 34-56)
- **Purity**: IMPURE (time-based conditional I/O)
- **Side Effects**:
  - Reads current time from event loop
  - Conditionally calls progress_callback
  - Updates last_heartbeat timestamp
- **External Dependencies**: asyncio event loop, progress_callback
- **Testability**: HIGH - Time-based logic can be tested with time manipulation

#### `reset()` (Lines 58-60)
- **Purity**: IMPURE (state mutation)
- **Side Effects**: Resets last_heartbeat to current time
- **External Dependencies**: asyncio event loop
- **Testability**: HIGH - Simple state mutation

## 2. External Dependencies Analysis

### Time Dependencies

#### `asyncio.get_event_loop().time()`
- **Usage**: Get monotonic time for heartbeat intervals
- **Methods Used**: `time()`
- **Interface Needed**: YES - Mock time source for deterministic testing
- **Recommendation**: Inject time source via constructor for testability

### Callback Dependencies

#### `progress_callback: Callable[[str, dict[str, Any]], Awaitable[None]]`
- **Usage**: Send heartbeat updates
- **Methods Used**: Called as async function with stage and data
- **Interface Needed**: YES - `IProgressCallback` Protocol

### Logging Dependencies

#### `logger` (via logfire_config)
- **Usage**: Logging (not actually used in current code)
- **Methods Used**: None currently
- **Interface Needed**: NO - Not used in logic

## 3. Testability Assessment

### Overall Testability: HIGH

**Strengths**:
1. Small, focused class with single responsibility
2. Clear separation of concerns (time checking vs callback invocation)
3. Simple state management (only last_heartbeat timestamp)
4. No complex dependencies or external I/O (except callback)
5. Pure time-based logic that can be tested deterministically

**Weaknesses**:
1. Direct dependency on `asyncio.get_event_loop().time()` makes time manipulation needed for tests
2. Progress callback is async, requiring async test harness

**Testing Challenges**:
1. **Time-Based Logic**: Need to control time to test interval behavior
2. **Async Callback**: Need proper async testing setup

### Recommended Refactoring for Testability

1. **Inject Time Source**: Add optional `time_source: Callable[[], float]` parameter to constructor
2. **Default Time Source**: Use `lambda: asyncio.get_event_loop().time()` as default

Example refactoring:
```python
def __init__(
    self,
    interval: float = 30.0,
    progress_callback: Callable[[str, dict[str, Any]], Awaitable[None]] | None = None,
    time_source: Callable[[], float] | None = None,
):
    self.interval = interval
    self.progress_callback = progress_callback
    self.time_source = time_source or (lambda: asyncio.get_event_loop().time())
    self.last_heartbeat = self.time_source()
```

This would make testing trivial with a fake time source.

## 4. Interface Extraction Plan

### Core Protocols (Priority: HIGH)

#### `IProgressCallback`
```python
from typing import Protocol, Any, Awaitable

class IProgressCallback(Protocol):
    """Interface for progress callback."""

    async def __call__(self, stage: str, data: dict[str, Any]) -> None:
        """Send progress update."""
        ...
```

#### `ITimeSource`
```python
from typing import Protocol

class ITimeSource(Protocol):
    """Interface for time source."""

    def __call__(self) -> float:
        """Get current monotonic time."""
        ...
```

### Fake Implementations

#### `FakeTimeSource`
```python
class FakeTimeSource:
    """Fake time source for deterministic testing."""

    def __init__(self, initial_time: float = 0.0):
        self._current_time = initial_time

    def __call__(self) -> float:
        return self._current_time

    def advance(self, seconds: float):
        """Advance time by specified seconds."""
        self._current_time += seconds

    def set_time(self, time: float):
        """Set absolute time."""
        self._current_time = time
```

#### `FakeProgressCallback`
```python
class FakeProgressCallback:
    """Fake progress callback for testing."""

    def __init__(self):
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def __call__(self, stage: str, data: dict[str, Any]) -> None:
        self.calls.append((stage, data))

    def was_called_with(self, stage: str, data: dict[str, Any]) -> bool:
        """Check if callback was called with specific arguments."""
        return (stage, data) in self.calls

    def call_count(self) -> int:
        """Get number of times callback was called."""
        return len(self.calls)
```

## 5. Test Plan

### Test File Structure

```
tests/unit/services/crawling/orchestration/
├── test_heartbeat_manager.py
└── fakes/
    ├── fake_time_source.py
    └── fake_progress_callback.py
```

### Test Scenarios

#### Constructor Tests

**Test: `test_init_with_default_interval`**
- Setup: Create HeartbeatManager()
- Expected: interval = 30.0, progress_callback = None
- Type: Pure unit test

**Test: `test_init_with_custom_interval`**
- Setup: Create HeartbeatManager(interval=60.0)
- Expected: interval = 60.0
- Type: Pure unit test

**Test: `test_init_with_callback`**
- Setup: Create fake callback, HeartbeatManager(progress_callback=callback)
- Expected: progress_callback assigned
- Type: Unit test with Fake

**Test: `test_init_sets_initial_timestamp`**
- Setup: Create HeartbeatManager with FakeTimeSource(100.0)
- Expected: last_heartbeat = 100.0
- Type: Unit test with Fake

#### Send If Needed Tests - No Callback

**Test: `test_send_if_needed_no_callback_no_error`**
- Setup: Create HeartbeatManager with no callback
- Action: Call send_if_needed("stage", 50)
- Expected: No exception, no callback invoked
- Type: Unit test

#### Send If Needed Tests - Interval Not Elapsed

**Test: `test_send_if_needed_interval_not_elapsed`**
- Setup:
  - FakeTimeSource at t=0
  - FakeProgressCallback
  - HeartbeatManager(interval=30.0)
  - Advance time to t=15 (15 seconds elapsed, < 30)
- Action: Call send_if_needed("crawling", 50)
- Expected: Callback NOT invoked, last_heartbeat unchanged
- Type: Unit test with Fakes

**Test: `test_send_if_needed_just_before_interval`**
- Setup:
  - FakeTimeSource at t=0
  - FakeProgressCallback
  - HeartbeatManager(interval=30.0)
  - Advance time to t=29.9 (29.9 seconds elapsed, < 30)
- Action: Call send_if_needed("crawling", 75)
- Expected: Callback NOT invoked
- Type: Unit test with Fakes

#### Send If Needed Tests - Interval Elapsed

**Test: `test_send_if_needed_exact_interval`**
- Setup:
  - FakeTimeSource at t=0
  - FakeProgressCallback
  - HeartbeatManager(interval=30.0)
  - Advance time to t=30.0 (exactly 30 seconds)
- Action: Call send_if_needed("crawling", 50)
- Expected:
  - Callback invoked with ("crawling", {...})
  - last_heartbeat updated to 30.0
- Type: Unit test with Fakes

**Test: `test_send_if_needed_interval_exceeded`**
- Setup:
  - FakeTimeSource at t=0
  - FakeProgressCallback
  - HeartbeatManager(interval=30.0)
  - Advance time to t=45.0 (45 seconds elapsed, > 30)
- Action: Call send_if_needed("processing", 75)
- Expected:
  - Callback invoked
  - last_heartbeat updated to 45.0
- Type: Unit test with Fakes

**Test: `test_send_if_needed_very_long_interval`**
- Setup:
  - FakeTimeSource at t=0
  - FakeProgressCallback
  - HeartbeatManager(interval=30.0)
  - Advance time to t=300.0 (5 minutes elapsed)
- Action: Call send_if_needed("finalization", 100)
- Expected: Callback invoked, last_heartbeat = 300.0
- Type: Unit test with Fakes

#### Send If Needed Tests - Callback Parameters

**Test: `test_send_if_needed_callback_receives_correct_stage`**
- Setup: Create HeartbeatManager with FakeProgressCallback, advance time
- Action: Call send_if_needed("analyzing", 25)
- Expected: Callback called with stage="analyzing"
- Type: Unit test with Fake

**Test: `test_send_if_needed_callback_receives_progress`**
- Setup: Create HeartbeatManager with FakeProgressCallback, advance time
- Action: Call send_if_needed("crawling", 50)
- Expected: Callback data contains "progress": 50
- Type: Unit test with Fake

**Test: `test_send_if_needed_callback_receives_heartbeat_flag`**
- Setup: Create HeartbeatManager with FakeProgressCallback, advance time
- Action: Call send_if_needed("crawling", 50)
- Expected: Callback data contains "heartbeat": True
- Type: Unit test with Fake

**Test: `test_send_if_needed_callback_receives_log_message`**
- Setup: Create HeartbeatManager with FakeProgressCallback, advance time
- Action: Call send_if_needed("crawling", 50)
- Expected: Callback data contains "log": "Background task still running..."
- Type: Unit test with Fake

**Test: `test_send_if_needed_callback_receives_message`**
- Setup: Create HeartbeatManager with FakeProgressCallback, advance time
- Action: Call send_if_needed("crawling", 50)
- Expected: Callback data contains "message": "Processing..."
- Type: Unit test with Fake

#### Send If Needed Tests - Multiple Calls

**Test: `test_send_if_needed_multiple_calls_within_interval`**
- Setup:
  - FakeTimeSource at t=0
  - FakeProgressCallback
  - HeartbeatManager(interval=30.0)
- Action:
  - Advance to t=10, call send_if_needed("stage1", 25)
  - Advance to t=20, call send_if_needed("stage2", 50)
  - Advance to t=25, call send_if_needed("stage3", 75)
- Expected:
  - Callback invoked 0 times (none reached interval)
- Type: Unit test with Fakes

**Test: `test_send_if_needed_multiple_calls_crossing_intervals`**
- Setup:
  - FakeTimeSource at t=0
  - FakeProgressCallback
  - HeartbeatManager(interval=30.0)
- Action:
  - Advance to t=35, call send_if_needed("stage1", 25)
  - Advance to t=40, call send_if_needed("stage2", 50)
  - Advance to t=70, call send_if_needed("stage3", 75)
- Expected:
  - First call: Callback invoked (35 >= 30), last_heartbeat = 35
  - Second call: Callback NOT invoked (40 - 35 = 5 < 30)
  - Third call: Callback invoked (70 - 35 = 35 >= 30), last_heartbeat = 70
- Type: Unit test with Fakes

**Test: `test_send_if_needed_alternating_stages`**
- Setup:
  - FakeTimeSource at t=0
  - FakeProgressCallback
  - HeartbeatManager(interval=10.0)
- Action:
  - Advance to t=11, call send_if_needed("crawling", 25)
  - Advance to t=22, call send_if_needed("processing", 50)
  - Advance to t=33, call send_if_needed("storing", 75)
- Expected:
  - Three callbacks invoked with different stages
- Type: Unit test with Fakes

#### Reset Tests

**Test: `test_reset_updates_timestamp`**
- Setup:
  - FakeTimeSource at t=0
  - HeartbeatManager
  - Advance to t=50
- Action: Call reset()
- Expected: last_heartbeat = 50
- Type: Unit test with Fake

**Test: `test_reset_prevents_immediate_heartbeat`**
- Setup:
  - FakeTimeSource at t=0
  - FakeProgressCallback
  - HeartbeatManager(interval=30.0)
  - Advance to t=50 (heartbeat would trigger)
  - Call reset() (resets to t=50)
  - Advance to t=60 (only 10 seconds since reset)
- Action: Call send_if_needed("stage", 50)
- Expected: Callback NOT invoked (60 - 50 = 10 < 30)
- Type: Unit test with Fakes

**Test: `test_reset_after_heartbeat_sent`**
- Setup:
  - FakeTimeSource at t=0
  - FakeProgressCallback
  - HeartbeatManager(interval=30.0)
  - Advance to t=35, call send_if_needed() - heartbeat sent
  - Advance to t=40, call reset()
  - Advance to t=50 (only 10 seconds since reset)
- Action: Call send_if_needed("stage", 75)
- Expected: Callback NOT invoked
- Type: Unit test with Fakes

#### Edge Cases

**Test: `test_send_if_needed_with_zero_interval`**
- Setup:
  - FakeTimeSource at t=0
  - FakeProgressCallback
  - HeartbeatManager(interval=0.0)
- Action: Call send_if_needed("stage", 50) immediately
- Expected: Callback invoked (0 elapsed >= 0 interval)
- Type: Unit test with Fakes

**Test: `test_send_if_needed_with_negative_interval`**
- Setup:
  - FakeTimeSource at t=0
  - FakeProgressCallback
  - HeartbeatManager(interval=-10.0)
- Action: Call send_if_needed("stage", 50)
- Expected: Callback invoked (any elapsed time >= negative interval)
- Type: Unit test with Fakes (edge case for robustness)

**Test: `test_send_if_needed_with_very_large_interval`**
- Setup:
  - FakeTimeSource at t=0
  - FakeProgressCallback
  - HeartbeatManager(interval=86400.0)  # 24 hours
  - Advance to t=3600 (1 hour)
- Action: Call send_if_needed("stage", 50)
- Expected: Callback NOT invoked (1 hour < 24 hours)
- Type: Unit test with Fakes

**Test: `test_send_if_needed_with_progress_zero`**
- Setup: HeartbeatManager with FakeProgressCallback, advance time
- Action: Call send_if_needed("starting", 0)
- Expected: Callback invoked with progress=0
- Type: Unit test with Fake

**Test: `test_send_if_needed_with_progress_hundred`**
- Setup: HeartbeatManager with FakeProgressCallback, advance time
- Action: Call send_if_needed("completed", 100)
- Expected: Callback invoked with progress=100
- Type: Unit test with Fake

**Test: `test_send_if_needed_with_empty_stage`**
- Setup: HeartbeatManager with FakeProgressCallback, advance time
- Action: Call send_if_needed("", 50)
- Expected: Callback invoked with stage=""
- Type: Unit test with Fake

#### Integration Scenarios (with realistic time sequences)

**Test: `test_typical_crawl_heartbeat_sequence`**
- Setup:
  - FakeTimeSource at t=0
  - FakeProgressCallback
  - HeartbeatManager(interval=30.0)
- Action: Simulate typical crawl with heartbeats at:
  - t=5: send_if_needed("analyzing", 5) - no heartbeat
  - t=20: send_if_needed("crawling", 25) - no heartbeat
  - t=35: send_if_needed("crawling", 50) - heartbeat sent
  - t=50: send_if_needed("processing", 70) - no heartbeat
  - t=68: send_if_needed("storing", 90) - heartbeat sent
- Expected: 2 heartbeats sent at t=35 and t=68
- Type: Unit test with Fakes

**Test: `test_rapid_progress_updates_limited_heartbeats`**
- Setup:
  - FakeTimeSource at t=0
  - FakeProgressCallback
  - HeartbeatManager(interval=30.0)
- Action: Simulate rapid progress updates every 5 seconds for 100 seconds
- Expected: Only ~3 heartbeats sent (at ~30s, ~60s, ~90s intervals)
- Type: Unit test with Fakes

### Fake Implementations Needed

#### `FakeTimeSource`
- Allows manual time control for deterministic testing
- Methods: `__call__()`, `advance(seconds)`, `set_time(time)`
- Location: `tests/unit/services/crawling/orchestration/fakes/fake_time_source.py`

#### `FakeProgressCallback`
- Tracks all callback invocations
- Methods: `__call__(stage, data)`, `was_called_with()`, `call_count()`
- Location: `tests/unit/services/crawling/orchestration/fakes/fake_progress_callback.py`

### Coverage Goals

- **Line Coverage**: 100%
- **Branch Coverage**: 100%
- **Function Coverage**: 100%

### Priority Test Implementation Order

1. **Phase 1**: Constructor tests
2. **Phase 2**: send_if_needed with no callback
3. **Phase 3**: send_if_needed with interval not elapsed
4. **Phase 4**: send_if_needed with interval elapsed
5. **Phase 5**: send_if_needed callback parameters validation
6. **Phase 6**: Multiple calls across intervals
7. **Phase 7**: Reset functionality
8. **Phase 8**: Edge cases and integration scenarios

## 6. Test Data Requirements

### Time Values
- Initial time: 0.0
- Typical interval: 30.0 seconds
- Test intervals: 10.0, 30.0, 60.0, 86400.0 seconds

### Stage Values
- "starting", "analyzing", "crawling", "processing", "storing", "completed"

### Progress Values
- 0, 25, 50, 75, 100

### Expected Callback Data Structure
```python
{
    "progress": 50,
    "heartbeat": True,
    "log": "Background task still running...",
    "message": "Processing...",
}
```

## 7. Notes and Recommendations

### Critical Issues to Address Before Testing

NONE - Code is well-structured and testable as-is. Optional improvement would be time source injection.

### Testing Best Practices

1. **Use FakeTimeSource**: Provides deterministic time control
2. **Async Tests**: Use pytest-asyncio for async test harness
3. **Callback Verification**: Always verify both call count and arguments
4. **Time Sequences**: Test realistic time sequences, not just single calls

### Future Improvements

1. **Optional Time Source Injection**: Add `time_source` parameter to constructor for easier testing
2. **Configurable Callback Data**: Allow customization of heartbeat message/log
3. **Max Heartbeat Count**: Optional limit to prevent excessive heartbeats in long-running operations

### Additional Test Utilities

#### Time Manipulation Helpers
```python
@contextmanager
def advance_time(fake_time: FakeTimeSource, seconds: float):
    """Context manager to advance time and restore."""
    original = fake_time()
    fake_time.advance(seconds)
    try:
        yield
    finally:
        fake_time.set_time(original)
```

#### Callback Assertion Helpers
```python
def assert_callback_called_with_data(
    fake_callback: FakeProgressCallback,
    stage: str,
    expected_data: dict[str, Any]
):
    """Assert callback was called with specific stage and data."""
    assert any(
        call[0] == stage and call[1] == expected_data
        for call in fake_callback.calls
    ), f"Callback not called with stage={stage} and data={expected_data}"
```
