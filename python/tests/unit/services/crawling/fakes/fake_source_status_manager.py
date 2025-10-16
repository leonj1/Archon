"""Fake source status manager for testing."""


class FakeSourceStatusManager:
    """
    Fake source status manager for testing.

    Tracks all status update calls for assertion in tests.
    """

    def __init__(self):
        """Initialize fake source status manager."""
        self.completed_sources: list[str] = []
        self.failed_sources: list[str] = []

    async def update_to_completed(self, source_id: str) -> None:
        """
        Record completion status update.

        Args:
            source_id: The source identifier
        """
        self.completed_sources.append(source_id)

    async def update_to_failed(self, source_id: str) -> None:
        """
        Record failure status update.

        Args:
            source_id: The source identifier
        """
        self.failed_sources.append(source_id)

    def was_completed(self, source_id: str) -> bool:
        """Check if source was marked as completed."""
        return source_id in self.completed_sources

    def was_failed(self, source_id: str) -> bool:
        """Check if source was marked as failed."""
        return source_id in self.failed_sources

    def reset(self) -> None:
        """Clear all recorded calls."""
        self.completed_sources.clear()
        self.failed_sources.clear()
