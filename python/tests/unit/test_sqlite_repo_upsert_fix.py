"""
Test SQLite repository upsert_source() merge logic fix.

This test verifies that the production SQLite repository properly merges
metadata instead of replacing it, ensuring crawl_status persists.
"""

import os
import tempfile
import unittest

from src.server.repositories.sqlite_repository import SQLiteDatabaseRepository


class TestSQLiteRepoUpsertFix(unittest.IsolatedAsyncioTestCase):
    """Test SQLite repository upsert behavior."""

    async def asyncSetUp(self):
        """Set up test database."""
        # Create a temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name

        # Initialize repository
        self.repo = SQLiteDatabaseRepository(db_path=self.db_path)
        await self.repo.initialize()

    async def asyncTearDown(self):
        """Clean up test database."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    async def test_sqlite_upsert_merges_metadata(self):
        """Test that upsert merges metadata instead of replacing it."""
        # Create initial source with metadata
        initial_data = {
            "source_id": "test_source_sqlite",
            "source_url": "https://example.com",
            "source_display_name": "Example Docs",
            "metadata": {
                "crawl_status": "pending",
                "custom_field": "should_be_preserved",
                "knowledge_type": "documentation"
            }
        }
        await self.repo.upsert_source(initial_data)

        # Update with partial metadata (only crawl_status)
        update_data = {
            "source_id": "test_source_sqlite",
            "crawl_status": "completed",  # This goes into metadata
            "summary": "New summary"  # Top-level field
        }
        await self.repo.upsert_source(update_data)

        # Verify metadata was merged, not replaced
        source = await self.repo.get_source_by_id("test_source_sqlite")

        self.assertIsNotNone(source)
        self.assertEqual(source["metadata"]["crawl_status"], "completed")
        self.assertEqual(source["metadata"]["custom_field"], "should_be_preserved")
        self.assertEqual(source["metadata"]["knowledge_type"], "documentation")
        self.assertEqual(source["summary"], "New summary")

    async def test_sqlite_crawl_status_lifecycle(self):
        """Test real-world scenario: crawl_status transitions."""
        # Step 1: Create source (pending)
        await self.repo.upsert_source({
            "source_id": "test_crawl",
            "source_url": "https://docs.example.com",
            "source_display_name": "Example API Docs",
            "crawl_status": "pending",
            "metadata": {
                "api_version": "v2",
                "tags": ["backend", "api"]
            }
        })

        source = await self.repo.get_source_by_id("test_crawl")
        self.assertEqual(source["metadata"]["crawl_status"], "pending")
        self.assertEqual(source["metadata"]["api_version"], "v2")

        # Step 2: Update to completed after crawl
        await self.repo.upsert_source({
            "source_id": "test_crawl",
            "crawl_status": "completed",
            "last_crawled_at": "2025-10-17T12:00:00",
            "summary": "Complete API documentation"
        })

        source = await self.repo.get_source_by_id("test_crawl")
        self.assertEqual(source["metadata"]["crawl_status"], "completed")
        self.assertEqual(source["metadata"]["last_crawled_at"], "2025-10-17T12:00:00")
        # Verify original metadata preserved
        self.assertEqual(source["metadata"]["api_version"], "v2")
        self.assertIn("backend", source["metadata"]["tags"])
        # Verify top-level field updated
        self.assertEqual(source["summary"], "Complete API documentation")

    async def test_sqlite_insert_vs_update(self):
        """Test that INSERT happens for new sources and UPDATE for existing."""
        # First call should INSERT
        result1 = await self.repo.upsert_source({
            "source_id": "insert_update_test",
            "source_url": "https://example.com",
            "title": "Original Title"
        })
        self.assertEqual(result1["source_id"], "insert_update_test")

        # Verify it was inserted
        source = await self.repo.get_source_by_id("insert_update_test")
        self.assertEqual(source["title"], "Original Title")

        # Second call should UPDATE
        result2 = await self.repo.upsert_source({
            "source_id": "insert_update_test",
            "title": "Updated Title"
        })
        self.assertEqual(result2["source_id"], "insert_update_test")

        # Verify it was updated and source_url was preserved
        source = await self.repo.get_source_by_id("insert_update_test")
        self.assertEqual(source["title"], "Updated Title")
        self.assertEqual(source["source_url"], "https://example.com")
