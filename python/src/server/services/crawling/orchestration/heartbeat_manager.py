"""
Heartbeat Manager for Crawl Orchestration

Manages periodic heartbeat signals to keep progress tracking alive during long operations.
"""

import asyncio

from ....config.logfire_config import get_logger
from ..protocols.progress_callback import IProgressCallback
from ..protocols.time_source import ITimeSource

logger = get_logger(__name__)


class HeartbeatManager:
    """Manages heartbeat signals for long-running crawl operations."""

    def __init__(
        self,
        interval: float = 30.0,
        progress_callback: IProgressCallback | None = None,
        time_source: ITimeSource | None = None,
    ):
        """
        Initialize the heartbeat manager.

        Args:
            interval: Heartbeat interval in seconds (default: 30.0)
            progress_callback: Callback to send heartbeat updates
            time_source: Time source for retrieving current time (default: asyncio event loop time)
        """
        self.interval = interval
        self.progress_callback = progress_callback
        self.time_source = time_source or (lambda: asyncio.get_event_loop().time())
        self.last_heartbeat = self.time_source()

    async def send_if_needed(self, current_stage: str, current_progress: int):
        """
        Send heartbeat if enough time has elapsed since last heartbeat.

        Args:
            current_stage: Current processing stage
            current_progress: Current progress percentage
        """
        if not self.progress_callback:
            return

        current_time = self.time_source()
        if current_time - self.last_heartbeat >= self.interval:
            await self.progress_callback(
                current_stage,
                {
                    "progress": current_progress,
                    "heartbeat": True,
                    "log": "Background task still running...",
                    "message": "Processing...",
                },
            )
            self.last_heartbeat = current_time

    def reset(self):
        """Reset the heartbeat timer."""
        self.last_heartbeat = self.time_source()
