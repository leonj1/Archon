"""
Unit tests for ProgressCallbackFactory

Tests progress callback creation and invocation with proper mapping and tracking.
"""

import pytest
from src.server.services.crawling.orchestration.progress_callback_factory import (
    ProgressCallbackFactory,
)
from tests.unit.services.crawling.fakes.fake_progress_tracker import FakeProgressTracker
from tests.unit.services.crawling.fakes.fake_progress_mapper import FakeProgressMapper


class TestProgressCallbackFactoryConstructor:
    """Test constructor and initialization."""

    def test_init_stores_dependencies(self):
        """Test that constructor stores all dependencies."""
        fake_tracker = FakeProgressTracker()
        fake_mapper = FakeProgressMapper()
        progress_id = "test-progress-id"

        factory = ProgressCallbackFactory(
            progress_tracker=fake_tracker,
            progress_mapper=fake_mapper,
            progress_id=progress_id,
        )

        assert factory.progress_tracker is fake_tracker
        assert factory.progress_mapper is fake_mapper
        assert factory.progress_id == progress_id

    def test_init_with_none_tracker(self):
        """Test that None tracker is allowed."""
        fake_mapper = FakeProgressMapper()

        factory = ProgressCallbackFactory(
            progress_tracker=None,
            progress_mapper=fake_mapper,
            progress_id=None,
        )

        assert factory.progress_tracker is None
        assert factory.progress_mapper is fake_mapper
        assert factory.progress_id is None

    def test_init_with_none_progress_id(self):
        """Test that None progress ID is allowed."""
        fake_tracker = FakeProgressTracker()
        fake_mapper = FakeProgressMapper()

        factory = ProgressCallbackFactory(
            progress_tracker=fake_tracker,
            progress_mapper=fake_mapper,
            progress_id=None,
        )

        assert factory.progress_tracker is fake_tracker
        assert factory.progress_mapper is fake_mapper
        assert factory.progress_id is None


class TestProgressCallbackFactoryCreateCallback:
    """Test callback creation."""

    @pytest.mark.asyncio
    async def test_create_callback_returns_callable(self):
        """Test that create_callback returns a callable."""
        fake_tracker = FakeProgressTracker()
        fake_mapper = FakeProgressMapper()

        factory = ProgressCallbackFactory(
            progress_tracker=fake_tracker,
            progress_mapper=fake_mapper,
            progress_id="test-id",
        )

        callback = await factory.create_callback("crawling")

        assert callable(callback)

    @pytest.mark.asyncio
    async def test_create_callback_is_async(self):
        """Test that created callback is async."""
        import inspect

        fake_tracker = FakeProgressTracker()
        fake_mapper = FakeProgressMapper()

        factory = ProgressCallbackFactory(
            progress_tracker=fake_tracker,
            progress_mapper=fake_mapper,
            progress_id="test-id",
        )

        callback = await factory.create_callback("crawling")

        assert inspect.iscoroutinefunction(callback)


class TestProgressCallbackFactoryCallbackInvocation:
    """Test callback invocation behavior."""

    @pytest.mark.asyncio
    async def test_callback_updates_tracker(self):
        """Test that callback updates the progress tracker."""
        fake_tracker = FakeProgressTracker()
        fake_mapper = FakeProgressMapper()
        fake_mapper.set_mapping("crawling", 50, 45)

        factory = ProgressCallbackFactory(
            progress_tracker=fake_tracker,
            progress_mapper=fake_mapper,
            progress_id="test-id",
        )

        callback = await factory.create_callback("crawling")
        await callback("processing", 50, "Test message")

        assert len(fake_tracker.update_calls) == 1
        assert fake_tracker.update_calls[0]["status"] == "crawling"
        assert fake_tracker.update_calls[0]["progress"] == 45
        assert fake_tracker.update_calls[0]["log"] == "Test message"

    @pytest.mark.asyncio
    async def test_callback_maps_progress(self):
        """Test that callback uses mapper to map progress."""
        fake_tracker = FakeProgressTracker()
        fake_mapper = FakeProgressMapper()

        factory = ProgressCallbackFactory(
            progress_tracker=fake_tracker,
            progress_mapper=fake_mapper,
            progress_id="test-id",
        )

        callback = await factory.create_callback("processing")
        await callback("stage_status", 60, "Processing data")

        assert len(fake_mapper.calls) == 1
        assert fake_mapper.calls[0] == ("processing", 60)

    @pytest.mark.asyncio
    async def test_callback_with_kwargs(self):
        """Test that callback passes extra kwargs to tracker."""
        fake_tracker = FakeProgressTracker()
        fake_mapper = FakeProgressMapper()

        factory = ProgressCallbackFactory(
            progress_tracker=fake_tracker,
            progress_mapper=fake_mapper,
            progress_id="test-id",
        )

        callback = await factory.create_callback("crawling")
        await callback(
            "status",
            75,
            "Message",
            total_pages=100,
            processed_pages=75,
            custom_field="value",
        )

        assert len(fake_tracker.update_calls) == 1
        update_call = fake_tracker.update_calls[0]
        assert update_call["total_pages"] == 100
        assert update_call["processed_pages"] == 75
        assert update_call["custom_field"] == "value"

    @pytest.mark.asyncio
    async def test_callback_without_tracker(self):
        """Test that callback is a no-op when tracker is None."""
        fake_mapper = FakeProgressMapper()

        factory = ProgressCallbackFactory(
            progress_tracker=None,
            progress_mapper=fake_mapper,
            progress_id=None,
        )

        callback = await factory.create_callback("crawling")
        await callback("status", 50, "Message")

        # Should not raise an exception, and mapper should not be called
        assert len(fake_mapper.calls) == 0


class TestProgressCallbackFactoryProgressMapping:
    """Test progress mapping behavior."""

    @pytest.mark.asyncio
    async def test_callback_maps_with_base_status(self):
        """Test that callback uses base status for mapping, not callback status."""
        fake_tracker = FakeProgressTracker()
        fake_mapper = FakeProgressMapper()
        fake_mapper.set_mapping("processing", 50, 70)

        factory = ProgressCallbackFactory(
            progress_tracker=fake_tracker,
            progress_mapper=fake_mapper,
            progress_id="test-id",
        )

        callback = await factory.create_callback("processing")
        await callback("different_status", 50, "Message")

        # Mapper should be called with base_status, not callback status
        assert fake_mapper.calls[0] == ("processing", 50)
        # Tracker should be updated with base_status, not callback status
        assert fake_tracker.update_calls[0]["status"] == "processing"

    @pytest.mark.asyncio
    async def test_callback_preserves_status(self):
        """Test that callback preserves the base status in updates."""
        fake_tracker = FakeProgressTracker()
        fake_mapper = FakeProgressMapper()

        factory = ProgressCallbackFactory(
            progress_tracker=fake_tracker,
            progress_mapper=fake_mapper,
            progress_id="test-id",
        )

        callback = await factory.create_callback("storing")
        await callback("ignored_status", 80, "Storing data")

        assert fake_tracker.update_calls[0]["status"] == "storing"

    @pytest.mark.asyncio
    async def test_callback_raw_vs_mapped_progress(self):
        """Test that raw progress is mapped before passing to tracker."""
        fake_tracker = FakeProgressTracker()
        fake_mapper = FakeProgressMapper()
        # Set explicit mapping
        fake_mapper.set_mapping("crawling", 100, 50)

        factory = ProgressCallbackFactory(
            progress_tracker=fake_tracker,
            progress_mapper=fake_mapper,
            progress_id="test-id",
        )

        callback = await factory.create_callback("crawling")
        await callback("status", 100, "Complete")

        # Raw progress is 100, but mapped to 50
        assert fake_tracker.update_calls[0]["progress"] == 50


class TestProgressCallbackFactoryEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_callback_with_zero_progress(self):
        """Test callback with zero progress."""
        fake_tracker = FakeProgressTracker()
        fake_mapper = FakeProgressMapper()

        factory = ProgressCallbackFactory(
            progress_tracker=fake_tracker,
            progress_mapper=fake_mapper,
            progress_id="test-id",
        )

        callback = await factory.create_callback("starting")
        await callback("status", 0, "Starting...")

        assert fake_tracker.update_calls[0]["progress"] >= 0

    @pytest.mark.asyncio
    async def test_callback_with_hundred_progress(self):
        """Test callback with 100% progress."""
        fake_tracker = FakeProgressTracker()
        fake_mapper = FakeProgressMapper()

        factory = ProgressCallbackFactory(
            progress_tracker=fake_tracker,
            progress_mapper=fake_mapper,
            progress_id="test-id",
        )

        callback = await factory.create_callback("completed")
        await callback("status", 100, "Done")

        assert fake_tracker.update_calls[0]["progress"] <= 100

    @pytest.mark.asyncio
    async def test_callback_with_empty_message(self):
        """Test callback with empty message."""
        fake_tracker = FakeProgressTracker()
        fake_mapper = FakeProgressMapper()

        factory = ProgressCallbackFactory(
            progress_tracker=fake_tracker,
            progress_mapper=fake_mapper,
            progress_id="test-id",
        )

        callback = await factory.create_callback("processing")
        await callback("status", 50, "")

        assert fake_tracker.update_calls[0]["log"] == ""

    @pytest.mark.asyncio
    async def test_callback_with_special_characters(self):
        """Test callback with special characters in message."""
        fake_tracker = FakeProgressTracker()
        fake_mapper = FakeProgressMapper()

        factory = ProgressCallbackFactory(
            progress_tracker=fake_tracker,
            progress_mapper=fake_mapper,
            progress_id="test-id",
        )

        callback = await factory.create_callback("processing")
        message = "Processing: 50% complete! @#$%^&*()"
        await callback("status", 50, message)

        assert fake_tracker.update_calls[0]["log"] == message

    @pytest.mark.asyncio
    async def test_callback_multiple_invocations(self):
        """Test that callback can be invoked multiple times."""
        fake_tracker = FakeProgressTracker()
        fake_mapper = FakeProgressMapper()

        factory = ProgressCallbackFactory(
            progress_tracker=fake_tracker,
            progress_mapper=fake_mapper,
            progress_id="test-id",
        )

        callback = await factory.create_callback("crawling")

        await callback("status1", 10, "Message 1")
        await callback("status2", 50, "Message 2")
        await callback("status3", 90, "Message 3")

        assert len(fake_tracker.update_calls) == 3
        assert fake_tracker.update_calls[0]["log"] == "Message 1"
        assert fake_tracker.update_calls[1]["log"] == "Message 2"
        assert fake_tracker.update_calls[2]["log"] == "Message 3"

    @pytest.mark.asyncio
    async def test_callback_with_unicode_message(self):
        """Test callback with Unicode characters in message."""
        fake_tracker = FakeProgressTracker()
        fake_mapper = FakeProgressMapper()

        factory = ProgressCallbackFactory(
            progress_tracker=fake_tracker,
            progress_mapper=fake_mapper,
            progress_id="test-id",
        )

        callback = await factory.create_callback("processing")
        message = "Processing: 文件处理中... 🚀"
        await callback("status", 50, message)

        assert fake_tracker.update_calls[0]["log"] == message

    @pytest.mark.asyncio
    async def test_multiple_callbacks_from_same_factory(self):
        """Test creating multiple callbacks from the same factory."""
        fake_tracker = FakeProgressTracker()
        fake_mapper = FakeProgressMapper()

        factory = ProgressCallbackFactory(
            progress_tracker=fake_tracker,
            progress_mapper=fake_mapper,
            progress_id="test-id",
        )

        callback1 = await factory.create_callback("stage1")
        callback2 = await factory.create_callback("stage2")

        await callback1("status", 25, "Stage 1 progress")
        await callback2("status", 75, "Stage 2 progress")

        assert len(fake_tracker.update_calls) == 2
        assert fake_tracker.update_calls[0]["status"] == "stage1"
        assert fake_tracker.update_calls[1]["status"] == "stage2"
