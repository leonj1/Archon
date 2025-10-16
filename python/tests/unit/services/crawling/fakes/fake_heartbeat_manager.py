"""Fake heartbeat manager for testing."""

from typing import Any


class FakeHeartbeatManager:
    """
    Fake heartbeat manager for testing.

    Tracks all heartbeat calls for assertion in tests.
    """

    def __init__(self):
        """Initialize fake heartbeat manager."""
        self.heartbeat_calls: list[dict[str, Any]] = []

    async def send_if_needed(self, stage: str, progress: int) -> None:
        """
        Record heartbeat call.

        Args:
            stage: Current processing stage
            progress: Current progress percentage
        """
        self.heartbeat_calls.append({"stage": stage, "progress": progress})

    def get_call_count(self) -> int:
        """Get number of heartbeat calls made."""
        return len(self.heartbeat_calls)

    def get_last_call(self) -> dict[str, Any] | None:
        """Get the last heartbeat call, or None if no calls made."""
        return self.heartbeat_calls[-1] if self.heartbeat_calls else None

    def reset(self) -> None:
        """Clear all recorded calls."""
        self.heartbeat_calls.clear()
