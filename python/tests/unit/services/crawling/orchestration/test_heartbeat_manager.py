"""Comprehensive unit tests for HeartbeatManager."""

import pytest
from src.server.services.crawling.orchestration.heartbeat_manager import HeartbeatManager
from tests.unit.services.crawling.fakes import FakeTimeSource, FakeProgressCallback


class TestHeartbeatManagerConstructor:
    """Tests for HeartbeatManager constructor."""

    def test_init_with_default_interval(self):
        """Test initialization with default interval."""
        manager = HeartbeatManager()

        assert manager.interval == 30.0
        assert manager.progress_callback is None

    def test_init_with_custom_interval(self):
        """Test initialization with custom interval."""
        manager = HeartbeatManager(interval=60.0)

        assert manager.interval == 60.0

    def test_init_with_callback(self):
        """Test initialization with progress callback."""
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(progress_callback=fake_callback)

        assert manager.progress_callback is fake_callback

    def test_init_sets_initial_timestamp(self):
        """Test that initialization sets initial timestamp from time source."""
        fake_time = FakeTimeSource(100.0)
        manager = HeartbeatManager(time_source=fake_time)

        assert manager.last_heartbeat == 100.0


class TestSendIfNeededNoCallback:
    """Tests for send_if_needed with no callback."""

    @pytest.mark.asyncio
    async def test_send_if_needed_no_callback_no_error(self):
        """Test that send_if_needed with no callback does not raise error."""
        fake_time = FakeTimeSource(0.0)
        manager = HeartbeatManager(time_source=fake_time)

        fake_time.advance(50.0)
        await manager.send_if_needed("stage", 50)


class TestSendIfNeededIntervalNotElapsed:
    """Tests for send_if_needed when interval has not elapsed."""

    @pytest.mark.asyncio
    async def test_send_if_needed_interval_not_elapsed(self):
        """Test that callback is not invoked when interval has not elapsed."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=30.0, progress_callback=fake_callback, time_source=fake_time)

        fake_time.advance(15.0)
        await manager.send_if_needed("crawling", 50)

        assert fake_callback.call_count() == 0
        assert manager.last_heartbeat == 0.0

    @pytest.mark.asyncio
    async def test_send_if_needed_just_before_interval(self):
        """Test that callback is not invoked just before interval threshold."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=30.0, progress_callback=fake_callback, time_source=fake_time)

        fake_time.advance(29.9)
        await manager.send_if_needed("crawling", 75)

        assert fake_callback.call_count() == 0


class TestSendIfNeededIntervalElapsed:
    """Tests for send_if_needed when interval has elapsed."""

    @pytest.mark.asyncio
    async def test_send_if_needed_exact_interval(self):
        """Test that callback is invoked at exact interval boundary."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=30.0, progress_callback=fake_callback, time_source=fake_time)

        fake_time.advance(30.0)
        await manager.send_if_needed("crawling", 50)

        assert fake_callback.call_count() == 1
        assert manager.last_heartbeat == 30.0

    @pytest.mark.asyncio
    async def test_send_if_needed_interval_exceeded(self):
        """Test that callback is invoked when interval is exceeded."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=30.0, progress_callback=fake_callback, time_source=fake_time)

        fake_time.advance(45.0)
        await manager.send_if_needed("processing", 75)

        assert fake_callback.call_count() == 1
        assert manager.last_heartbeat == 45.0

    @pytest.mark.asyncio
    async def test_send_if_needed_very_long_interval(self):
        """Test callback invocation after very long interval."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=30.0, progress_callback=fake_callback, time_source=fake_time)

        fake_time.advance(300.0)
        await manager.send_if_needed("finalization", 100)

        assert fake_callback.call_count() == 1
        assert manager.last_heartbeat == 300.0


class TestSendIfNeededCallbackParameters:
    """Tests for callback parameters in send_if_needed."""

    @pytest.mark.asyncio
    async def test_send_if_needed_callback_receives_correct_stage(self):
        """Test that callback receives the correct stage parameter."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=30.0, progress_callback=fake_callback, time_source=fake_time)

        fake_time.advance(30.0)
        await manager.send_if_needed("analyzing", 25)

        stage, _ = fake_callback.last_call()
        assert stage == "analyzing"

    @pytest.mark.asyncio
    async def test_send_if_needed_callback_receives_progress(self):
        """Test that callback data contains correct progress value."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=30.0, progress_callback=fake_callback, time_source=fake_time)

        fake_time.advance(30.0)
        await manager.send_if_needed("crawling", 50)

        _, data = fake_callback.last_call()
        assert data["progress"] == 50

    @pytest.mark.asyncio
    async def test_send_if_needed_callback_receives_heartbeat_flag(self):
        """Test that callback data contains heartbeat flag."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=30.0, progress_callback=fake_callback, time_source=fake_time)

        fake_time.advance(30.0)
        await manager.send_if_needed("crawling", 50)

        _, data = fake_callback.last_call()
        assert data["heartbeat"] is True

    @pytest.mark.asyncio
    async def test_send_if_needed_callback_receives_log_message(self):
        """Test that callback data contains log message."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=30.0, progress_callback=fake_callback, time_source=fake_time)

        fake_time.advance(30.0)
        await manager.send_if_needed("crawling", 50)

        _, data = fake_callback.last_call()
        assert data["log"] == "Background task still running..."

    @pytest.mark.asyncio
    async def test_send_if_needed_callback_receives_message(self):
        """Test that callback data contains message field."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=30.0, progress_callback=fake_callback, time_source=fake_time)

        fake_time.advance(30.0)
        await manager.send_if_needed("crawling", 50)

        _, data = fake_callback.last_call()
        assert data["message"] == "Processing..."


class TestSendIfNeededMultipleCalls:
    """Tests for multiple calls to send_if_needed."""

    @pytest.mark.asyncio
    async def test_send_if_needed_multiple_calls_within_interval(self):
        """Test that multiple calls within interval do not trigger callbacks."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=30.0, progress_callback=fake_callback, time_source=fake_time)

        fake_time.set_time(10.0)
        await manager.send_if_needed("stage1", 25)

        fake_time.set_time(20.0)
        await manager.send_if_needed("stage2", 50)

        fake_time.set_time(25.0)
        await manager.send_if_needed("stage3", 75)

        assert fake_callback.call_count() == 0

    @pytest.mark.asyncio
    async def test_send_if_needed_multiple_calls_crossing_intervals(self):
        """Test multiple calls that cross interval boundaries."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=30.0, progress_callback=fake_callback, time_source=fake_time)

        fake_time.set_time(35.0)
        await manager.send_if_needed("stage1", 25)
        assert fake_callback.call_count() == 1
        assert manager.last_heartbeat == 35.0

        fake_time.set_time(40.0)
        await manager.send_if_needed("stage2", 50)
        assert fake_callback.call_count() == 1

        fake_time.set_time(70.0)
        await manager.send_if_needed("stage3", 75)
        assert fake_callback.call_count() == 2
        assert manager.last_heartbeat == 70.0

    @pytest.mark.asyncio
    async def test_send_if_needed_alternating_stages(self):
        """Test alternating stages with proper intervals."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=10.0, progress_callback=fake_callback, time_source=fake_time)

        fake_time.set_time(11.0)
        await manager.send_if_needed("crawling", 25)

        fake_time.set_time(22.0)
        await manager.send_if_needed("processing", 50)

        fake_time.set_time(33.0)
        await manager.send_if_needed("storing", 75)

        assert fake_callback.call_count() == 3
        calls = fake_callback.get_calls()
        assert calls[0][0] == "crawling"
        assert calls[1][0] == "processing"
        assert calls[2][0] == "storing"


class TestReset:
    """Tests for reset functionality."""

    def test_reset_updates_timestamp(self):
        """Test that reset updates the last heartbeat timestamp."""
        fake_time = FakeTimeSource(0.0)
        manager = HeartbeatManager(time_source=fake_time)

        fake_time.advance(50.0)
        manager.reset()

        assert manager.last_heartbeat == 50.0

    @pytest.mark.asyncio
    async def test_reset_prevents_immediate_heartbeat(self):
        """Test that reset prevents immediate heartbeat on next call."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=30.0, progress_callback=fake_callback, time_source=fake_time)

        fake_time.set_time(50.0)
        manager.reset()

        fake_time.set_time(60.0)
        await manager.send_if_needed("stage", 50)

        assert fake_callback.call_count() == 0

    @pytest.mark.asyncio
    async def test_reset_after_heartbeat_sent(self):
        """Test reset behavior after a heartbeat has been sent."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=30.0, progress_callback=fake_callback, time_source=fake_time)

        fake_time.set_time(35.0)
        await manager.send_if_needed("stage1", 50)
        assert fake_callback.call_count() == 1

        fake_time.set_time(40.0)
        manager.reset()

        fake_time.set_time(50.0)
        await manager.send_if_needed("stage2", 75)

        assert fake_callback.call_count() == 1


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_send_if_needed_with_zero_interval(self):
        """Test behavior with zero interval."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=0.0, progress_callback=fake_callback, time_source=fake_time)

        await manager.send_if_needed("stage", 50)

        assert fake_callback.call_count() == 1

    @pytest.mark.asyncio
    async def test_send_if_needed_with_negative_interval(self):
        """Test behavior with negative interval."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=-10.0, progress_callback=fake_callback, time_source=fake_time)

        await manager.send_if_needed("stage", 50)

        assert fake_callback.call_count() == 1

    @pytest.mark.asyncio
    async def test_send_if_needed_with_very_large_interval(self):
        """Test behavior with very large interval."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=86400.0, progress_callback=fake_callback, time_source=fake_time)

        fake_time.advance(3600.0)
        await manager.send_if_needed("stage", 50)

        assert fake_callback.call_count() == 0

    @pytest.mark.asyncio
    async def test_send_if_needed_with_progress_zero(self):
        """Test callback with progress value of zero."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=30.0, progress_callback=fake_callback, time_source=fake_time)

        fake_time.advance(30.0)
        await manager.send_if_needed("starting", 0)

        _, data = fake_callback.last_call()
        assert data["progress"] == 0

    @pytest.mark.asyncio
    async def test_send_if_needed_with_progress_hundred(self):
        """Test callback with progress value of 100."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=30.0, progress_callback=fake_callback, time_source=fake_time)

        fake_time.advance(30.0)
        await manager.send_if_needed("completed", 100)

        _, data = fake_callback.last_call()
        assert data["progress"] == 100

    @pytest.mark.asyncio
    async def test_send_if_needed_with_empty_stage(self):
        """Test callback with empty stage string."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=30.0, progress_callback=fake_callback, time_source=fake_time)

        fake_time.advance(30.0)
        await manager.send_if_needed("", 50)

        stage, _ = fake_callback.last_call()
        assert stage == ""


class TestIntegrationScenarios:
    """Tests for realistic integration scenarios."""

    @pytest.mark.asyncio
    async def test_typical_crawl_heartbeat_sequence(self):
        """Test typical crawl sequence with realistic heartbeat timing."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=30.0, progress_callback=fake_callback, time_source=fake_time)

        fake_time.set_time(5.0)
        await manager.send_if_needed("analyzing", 5)
        assert fake_callback.call_count() == 0

        fake_time.set_time(20.0)
        await manager.send_if_needed("crawling", 25)
        assert fake_callback.call_count() == 0

        fake_time.set_time(35.0)
        await manager.send_if_needed("crawling", 50)
        assert fake_callback.call_count() == 1

        fake_time.set_time(50.0)
        await manager.send_if_needed("processing", 70)
        assert fake_callback.call_count() == 1

        fake_time.set_time(68.0)
        await manager.send_if_needed("storing", 90)
        assert fake_callback.call_count() == 2

    @pytest.mark.asyncio
    async def test_rapid_progress_updates_limited_heartbeats(self):
        """Test that rapid progress updates only send limited heartbeats."""
        fake_time = FakeTimeSource(0.0)
        fake_callback = FakeProgressCallback()
        manager = HeartbeatManager(interval=30.0, progress_callback=fake_callback, time_source=fake_time)

        for i in range(20):
            fake_time.set_time(i * 5.0)
            await manager.send_if_needed("crawling", i * 5)

        assert fake_callback.call_count() == 3
        calls = fake_callback.get_calls()
        assert calls[0][1]["progress"] == 30
        assert calls[1][1]["progress"] == 60
        assert calls[2][1]["progress"] == 90
