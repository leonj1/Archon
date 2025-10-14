"""
Test race condition handling in source creation.

This test ensures that concurrent source creation attempts
don't fail with PRIMARY KEY violations.
"""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch
import pytest

from src.server.services.source_management_service import update_source_info


class TestSourceRaceCondition:
    """Test that concurrent source creation handles race conditions properly."""

    def test_concurrent_source_creation_no_race(self):
        """Test that concurrent attempts to create the same source don't fail."""
        # Track successful operations
        successful_creates = []
        failed_creates = []

        async def mock_get_source_by_id(source_id):
            """Mock get_source_by_id - always returns None (source doesn't exist)."""
            return None

        async def mock_upsert_source(data):
            """Mock upsert_source that tracks calls."""
            successful_creates.append(data["source_id"])
            return data

        # Mock database repository
        mock_repository = Mock()
        mock_repository.get_source_by_id = mock_get_source_by_id
        mock_repository.upsert_source = mock_upsert_source

        def create_source(thread_id):
            """Simulate creating a source from a thread."""
            try:
                # Run async function in new event loop for each thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(update_source_info(
                    repository=mock_repository,
                    source_id="test_source_123",
                    summary=f"Summary from thread {thread_id}",
                    word_count=100,
                    content=f"Content from thread {thread_id}",
                    knowledge_type="documentation",
                    tags=["test"],
                    update_frequency=0,
                    source_url="https://example.com",
                    source_display_name=f"Example Site {thread_id}"  # Will be used as title
                ))
                loop.close()
            except Exception as e:
                failed_creates.append((thread_id, str(e)))

        # Run 5 threads concurrently trying to create the same source
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for i in range(5):
                futures.append(executor.submit(create_source, i))

            # Wait for all to complete
            for future in futures:
                future.result()

        # All should succeed (no failures due to PRIMARY KEY violation)
        assert len(failed_creates) == 0, f"Some creates failed: {failed_creates}"
        assert len(successful_creates) == 5, "All 5 attempts should succeed"
        assert all(sid == "test_source_123" for sid in successful_creates)

    def test_upsert_vs_insert_behavior(self):
        """Test that upsert is used instead of insert for new sources."""
        # Track which method is called
        methods_called = []

        async def mock_get_source_by_id(source_id):
            """Source doesn't exist."""
            return None

        async def mock_upsert_source(data):
            """Track upsert calls."""
            methods_called.append("upsert")
            return data

        # Mock database repository
        mock_repository = Mock()
        mock_repository.get_source_by_id = mock_get_source_by_id
        mock_repository.upsert_source = mock_upsert_source

        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(update_source_info(
            repository=mock_repository,
            source_id="new_source",
            summary="Test summary",
            word_count=100,
            content="Test content",
            knowledge_type="documentation",
            source_display_name="Test Display Name"  # Will be used as title
        ))
        loop.close()

        # Should use upsert, not insert
        assert "upsert" in methods_called, "Should use upsert for new sources"
        assert "insert" not in methods_called, "Should not use insert to avoid race conditions"

    def test_existing_source_uses_upsert(self):
        """Test that existing sources use UPSERT to handle race conditions."""
        methods_called = []

        async def mock_get_source_by_id(source_id):
            """Source exists."""
            return {
                "source_id": "existing_source",
                "title": "Existing Title",
                "metadata": {"knowledge_type": "api"}
            }

        async def mock_upsert_source(data):
            """Track upsert calls."""
            methods_called.append("upsert")
            return data

        # Mock database repository
        mock_repository = Mock()
        mock_repository.get_source_by_id = mock_get_source_by_id
        mock_repository.upsert_source = mock_upsert_source

        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(update_source_info(
            repository=mock_repository,
            source_id="existing_source",
            summary="Updated summary",
            word_count=200,
            content="Updated content",
            knowledge_type="documentation"
        ))
        loop.close()

        # Should use upsert for existing sources to handle race conditions
        assert "upsert" in methods_called, "Should use upsert for existing sources"
        assert "update" not in methods_called, "Should not use update (upsert handles race conditions)"

    @pytest.mark.asyncio
    async def test_async_concurrent_creation(self):
        """Test concurrent source creation in async context."""
        # Track operations
        operations = []

        async def mock_get_source_by_id(source_id):
            """No existing sources."""
            return None

        async def mock_upsert_source(data):
            """Track upsert calls."""
            operations.append(("upsert", data["source_id"]))
            return data

        # Mock database repository
        mock_repository = Mock()
        mock_repository.get_source_by_id = mock_get_source_by_id
        mock_repository.upsert_source = mock_upsert_source

        async def create_source_async(task_id):
            """Async wrapper for source creation."""
            await update_source_info(
                repository=mock_repository,
                source_id=f"async_source_{task_id % 2}",  # Only 2 unique sources
                summary=f"Summary {task_id}",
                word_count=100,
                content=f"Content {task_id}",
                knowledge_type="documentation"
            )

        # Create 10 tasks, but only 2 unique source_ids
        tasks = [create_source_async(i) for i in range(10)]
        await asyncio.gather(*tasks)

        # All operations should succeed
        assert len(operations) == 10, "All 10 operations should complete"

        # Check that we tried to upsert the two sources multiple times
        source_0_count = sum(1 for op, sid in operations if sid == "async_source_0")
        source_1_count = sum(1 for op, sid in operations if sid == "async_source_1")

        assert source_0_count == 5, "async_source_0 should be upserted 5 times"
        assert source_1_count == 5, "async_source_1 should be upserted 5 times"

    def test_race_condition_with_delay(self):
        """Test race condition with simulated delay between check and create."""
        import time

        # Track timing of operations
        check_times = []
        create_times = []
        source_created = threading.Event()

        async def delayed_get_source_by_id(source_id):
            """Simulate get_source_by_id with delay."""
            check_times.append(time.time())
            # First thread doesn't see the source
            if not source_created.is_set():
                time.sleep(0.01)  # Small delay to let both threads check
                return None
            else:
                # Subsequent checks would see it (but we use upsert so this doesn't matter)
                return {"source_id": "race_source", "title": "Existing", "metadata": {}}

        async def track_upsert(data):
            """Track upsert and set event."""
            create_times.append(time.time())
            source_created.set()
            return data

        # Mock database repository
        mock_repository = Mock()
        mock_repository.get_source_by_id = delayed_get_source_by_id
        mock_repository.upsert_source = track_upsert

        errors = []

        def create_with_error_tracking(thread_id):
            try:
                # Run async function in new event loop for each thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(update_source_info(
                    repository=mock_repository,
                    source_id="race_source",
                    summary="Race summary",
                    word_count=100,
                    content="Race content",
                    knowledge_type="documentation",
                    source_display_name="Race Display Name"  # Will be used as title
                ))
                loop.close()
            except Exception as e:
                errors.append((thread_id, str(e)))

        # Run 2 threads that will both check before either creates
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(create_with_error_tracking, 1),
                executor.submit(create_with_error_tracking, 2)
            ]
            for future in futures:
                future.result()

        # Both should succeed with upsert (no errors)
        assert len(errors) == 0, f"No errors should occur with upsert: {errors}"
        assert len(check_times) == 2, "Both threads should check"
        assert len(create_times) == 2, "Both threads should attempt create/upsert"