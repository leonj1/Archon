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

    def get_current_stage(self) -> str:
        """
        Get the current stage name.

        Returns:
            Current stage name
        """
        ...

    def get_current_progress(self) -> int:
        """
        Get the current overall progress percentage.

        Returns:
            Current progress percentage (0-100)
        """
        ...
