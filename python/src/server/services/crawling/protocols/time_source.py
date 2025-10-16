"""Time source protocol for testable time-dependent operations."""

from typing import Protocol


class ITimeSource(Protocol):
    """Interface for time source operations."""

    def __call__(self) -> float:
        """
        Get current monotonic time.

        Returns:
            Current time in seconds as a float
        """
        ...
