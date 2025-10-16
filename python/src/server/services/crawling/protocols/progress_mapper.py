"""Progress mapper protocol for stage-based progress calculation."""

from typing import Protocol


class IProgressMapper(Protocol):
    """Interface for progress mapping operations."""

    def map_progress(self, stage: str, progress: int) -> int:
        """
        Map stage-specific progress to overall progress.

        Args:
            stage: Processing stage name
            progress: Progress within the stage (0-100)

        Returns:
            Overall progress percentage (0-100)
        """
        ...
