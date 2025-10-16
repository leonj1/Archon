"""Fake progress callback for testing heartbeat operations."""

from typing import Any


class FakeProgressCallback:
    """
    Fake progress callback for testing.

    Tracks all callback invocations for assertion in tests.
    """

    def __init__(self):
        """Initialize fake progress callback."""
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def __call__(self, stage: str, data: dict[str, Any]) -> None:
        """
        Record callback invocation.

        Args:
            stage: Processing stage
            data: Progress data
        """
        self.calls.append((stage, data))

    def was_called_with(self, stage: str, data: dict[str, Any]) -> bool:
        """
        Check if callback was called with specific arguments.

        Args:
            stage: Expected stage
            data: Expected data

        Returns:
            True if callback was called with these arguments
        """
        return (stage, data) in self.calls

    def call_count(self) -> int:
        """
        Get number of times callback was called.

        Returns:
            Number of callback invocations
        """
        return len(self.calls)

    def get_calls(self) -> list[tuple[str, dict[str, Any]]]:
        """
        Get all recorded calls.

        Returns:
            List of (stage, data) tuples
        """
        return self.calls.copy()

    def reset(self) -> None:
        """Clear all recorded calls."""
        self.calls.clear()

    def last_call(self) -> tuple[str, dict[str, Any]] | None:
        """
        Get the most recent call.

        Returns:
            Last (stage, data) tuple or None if no calls
        """
        return self.calls[-1] if self.calls else None
