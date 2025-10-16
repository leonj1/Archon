"""Protocol interfaces for crawling services."""

from .time_source import ITimeSource
from .progress_callback import IProgressCallback
from .progress_tracker import IProgressTracker
from .progress_mapper import IProgressMapper
from .progress_update_handler import IProgressUpdateHandler

__all__ = [
    "ITimeSource",
    "IProgressCallback",
    "IProgressTracker",
    "IProgressMapper",
    "IProgressUpdateHandler",
]
