"""Heartbeat manager protocol for periodic progress updates."""

from typing import Protocol


class IHeartbeatManager(Protocol):
    """Interface for managing heartbeat operations during crawling."""

    async def send_if_needed(self, stage: str, progress: int) -> None:
        """
        Send heartbeat if needed based on time elapsed.

        Args:
            stage: Current processing stage
            progress: Current progress percentage
        """
        ...
