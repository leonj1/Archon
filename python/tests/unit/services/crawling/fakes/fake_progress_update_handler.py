"""Fake progress update handler for testing."""

from typing import Any


class FakeProgressUpdateHandler:
    """
    Fake progress update handler for testing.

    Tracks all progress update calls for assertion in tests.
    """

    def __init__(self):
        """Initialize fake progress update handler."""
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def __call__(self, task_id: str, update: dict[str, Any]) -> None:
        """
        Handle a progress update.

        Args:
            task_id: Task identifier
            update: Progress update data
        """
        self.calls.append((task_id, update.copy()))

    def was_called_with_task_id(self, task_id: str) -> bool:
        """
        Check if handler was called with specific task ID.

        Args:
            task_id: Expected task ID

        Returns:
            True if handler was called with this task ID
        """
        return any(call[0] == task_id for call in self.calls)

    def get_calls_for_task(self, task_id: str) -> list[dict[str, Any]]:
        """
        Get all calls for a specific task.

        Args:
            task_id: Task ID to filter by

        Returns:
            List of update dictionaries for the task
        """
        return [call[1] for call in self.calls if call[0] == task_id]

    def last_call(self) -> tuple[str, dict[str, Any]] | None:
        """
        Get the most recent call.

        Returns:
            Last (task_id, update) tuple or None if no calls
        """
        return self.calls[-1] if self.calls else None

    def call_count(self) -> int:
        """
        Get number of times handler was called.

        Returns:
            Number of handler invocations
        """
        return len(self.calls)

    def reset(self) -> None:
        """Clear all recorded calls."""
        self.calls.clear()
