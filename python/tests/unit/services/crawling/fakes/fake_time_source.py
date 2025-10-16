"""Fake time source for deterministic testing."""


class FakeTimeSource:
    """
    Fake time source for deterministic testing.

    Allows manual control of time progression for testing time-dependent logic.
    """

    def __init__(self, initial_time: float = 0.0):
        """
        Initialize fake time source.

        Args:
            initial_time: Starting time value (default: 0.0)
        """
        self._current_time = initial_time

    def __call__(self) -> float:
        """
        Get current time.

        Returns:
            Current time value
        """
        return self._current_time

    def advance(self, seconds: float) -> None:
        """
        Advance time by specified seconds.

        Args:
            seconds: Number of seconds to advance
        """
        self._current_time += seconds

    def set_time(self, time: float) -> None:
        """
        Set absolute time.

        Args:
            time: Time value to set
        """
        self._current_time = time
