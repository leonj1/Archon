"""Fake progress mapper for testing stage-based progress calculation."""


class FakeProgressMapper:
    """
    Fake progress mapper for testing.

    Allows configurable mappings for testing different progress scenarios.
    """

    def __init__(self):
        """Initialize fake progress mapper."""
        self.calls: list[tuple[str, int]] = []
        self._mappings: dict[tuple[str, int], int] = {}

    def map_progress(self, stage: str, progress: int) -> int:
        """
        Map stage-specific progress to overall progress.

        Args:
            stage: Processing stage name
            progress: Progress within the stage (0-100)

        Returns:
            Overall progress percentage (0-100)
        """
        self.calls.append((stage, progress))

        if (stage, progress) in self._mappings:
            return self._mappings[(stage, progress)]

        stage_offset = {
            "starting": 0,
            "analyzing": 10,
            "crawling": 20,
            "processing": 50,
            "storing": 80,
            "completed": 100,
        }.get(stage, 0)

        return min(100, stage_offset + (progress // 5))

    def set_mapping(self, stage: str, progress: int, mapped_value: int) -> None:
        """
        Set a specific mapping for testing.

        Args:
            stage: Stage name
            progress: Progress within stage
            mapped_value: Mapped overall progress value
        """
        self._mappings[(stage, progress)] = mapped_value

    def reset(self) -> None:
        """Clear all recorded calls and mappings."""
        self.calls.clear()
        self._mappings.clear()

    def was_called_with(self, stage: str, progress: int) -> bool:
        """
        Check if mapper was called with specific arguments.

        Args:
            stage: Expected stage
            progress: Expected progress

        Returns:
            True if mapper was called with these arguments
        """
        return (stage, progress) in self.calls
