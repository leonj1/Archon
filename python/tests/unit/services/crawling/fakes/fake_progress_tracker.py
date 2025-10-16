"""Fake progress tracker for testing crawl progress operations."""

from typing import Any


class FakeProgressTracker:
    """
    Fake progress tracker for testing.

    Tracks all method calls and maintains state for assertion in tests.
    """

    def __init__(self):
        """Initialize fake progress tracker."""
        self.state: dict[str, Any] = {
            "status": "initializing",
            "progress": 0,
            "log": "Starting...",
        }
        self.start_calls: list[dict[str, Any]] = []
        self.update_calls: list[dict[str, Any]] = []
        self.complete_calls: list[dict[str, Any]] = []
        self.error_calls: list[str] = []

    async def start(self, initial_data: dict[str, Any]) -> None:
        """
        Start progress tracking.

        Args:
            initial_data: Initial progress data
        """
        self.start_calls.append(initial_data.copy())
        self.state.update(initial_data)

    async def update(self, status: str, progress: int, log: str, **kwargs: Any) -> None:
        """
        Update progress state.

        Args:
            status: Current status
            progress: Progress percentage
            log: Log message
            **kwargs: Additional metadata
        """
        update_data = {"status": status, "progress": progress, "log": log, **kwargs}
        self.update_calls.append(update_data)
        self.state.update(update_data)

    async def complete(self, completion_data: dict[str, Any]) -> None:
        """
        Mark progress as complete.

        Args:
            completion_data: Completion metadata
        """
        self.complete_calls.append(completion_data.copy())
        self.state.update(completion_data)
        self.state["status"] = "completed"

    async def error(self, error_message: str) -> None:
        """
        Mark progress as failed.

        Args:
            error_message: Error description
        """
        self.error_calls.append(error_message)
        self.state["error"] = error_message
        self.state["status"] = "failed"

    def reset(self) -> None:
        """Clear all recorded calls and reset state."""
        self.start_calls.clear()
        self.update_calls.clear()
        self.complete_calls.clear()
        self.error_calls.clear()
        self.state = {
            "status": "initializing",
            "progress": 0,
            "log": "Starting...",
        }
