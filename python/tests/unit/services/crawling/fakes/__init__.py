"""Fake implementations for testing crawling services."""

from .fake_time_source import FakeTimeSource
from .fake_progress_callback import FakeProgressCallback
from .fake_progress_tracker import FakeProgressTracker
from .fake_progress_mapper import FakeProgressMapper
from .fake_progress_update_handler import FakeProgressUpdateHandler

__all__ = [
    "FakeTimeSource",
    "FakeProgressCallback",
    "FakeProgressTracker",
    "FakeProgressMapper",
    "FakeProgressUpdateHandler",
]
