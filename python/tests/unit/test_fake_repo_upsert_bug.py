"""
Test to reproduce the upsert_source bug in FakeDatabaseRepository.

This test shows that upsert_source REPLACES the entire record
instead of MERGING metadata like the real database does.
"""

import pytest

from src.server.repositories.fake_repository import FakeDatabaseRepository


class TestFakeRepoUpsertBug:
    """Tests to demonstrate the upsert bug."""

    @pytest.mark.asyncio
    async def test_upsert_source_replaces_instead_of_merges(self):
        """
        BUG: upsert_source replaces the entire record instead of merging.
        This causes metadata fields like crawl_status to be lost.
        """
        fake_repo = FakeDatabaseRepository()

        # Step 1: Create source with initial metadata
        initial_data = {
            "source_id": "test_source",
            "title": "Test Source",
            "summary": "Initial summary",
            "total_word_count": 1000,
            "metadata": {
                "knowledge_type": "documentation",
                "crawl_status": "pending",
                "tags": ["test"],
                "custom_field": "should_be_preserved",
            }
        }
        await fake_repo.upsert_source(initial_data)

        # Verify initial state
        source = await fake_repo.get_source_by_id("test_source")
        assert source["metadata"]["crawl_status"] == "pending"
        assert source["metadata"]["custom_field"] == "should_be_preserved"

        # Step 2: Update with partial data (like update_source_info does)
        update_data = {
            "source_id": "test_source",
            "title": "Test Source",  # Same title
            "summary": "Updated summary",
            "total_word_count": 2000,
            "metadata": {
                "knowledge_type": "documentation",
                "crawl_status": "completed",  # Only updating this field
                # NOTE: custom_field is NOT included in update!
            }
        }
        await fake_repo.upsert_source(update_data)

        # Step 3: Verify the update
        source = await fake_repo.get_source_by_id("test_source")

        # This SHOULD work but DOESN'T due to the bug:
        assert source["metadata"]["crawl_status"] == "completed", \
            f"Expected 'completed', got '{source['metadata'].get('crawl_status')}'"

        # This field gets LOST because upsert replaces instead of merges:
        try:
            assert source["metadata"]["custom_field"] == "should_be_preserved", \
                "custom_field should be preserved during upsert"
        except (KeyError, AssertionError) as e:
            print(f"\n❌ BUG CONFIRMED: custom_field was lost during upsert!")
            print(f"   Expected: 'should_be_preserved'")
            print(f"   Actual: {source['metadata'].get('custom_field', 'MISSING')}")
            # This demonstrates the bug
            pytest.fail("custom_field was lost - upsert replaces instead of merging!")

    @pytest.mark.asyncio
    async def test_real_world_scenario_crawl_status_lost(self):
        """
        Simulates the real production bug where crawl_status doesn't update.
        """
        fake_repo = FakeDatabaseRepository()

        # Create source (like document_storage_operations.py does)
        await fake_repo.upsert_source({
            "source_id": "docs.example.com",
            "title": "Example Docs",
            "summary": "Documentation site",
            "total_word_count": 0,
            "metadata": {
                "knowledge_type": "documentation",
                "crawl_status": "pending",
                "tags": ["docs"],
                "original_url": "https://docs.example.com",
            }
        })

        # Later, update_source_info tries to set crawl_status to completed
        # (like SourceStatusManager.update_to_completed does)
        existing_source = await fake_repo.get_source_by_id("docs.example.com")

        # This is what update_source_info does:
        upsert_data = {
            "source_id": "docs.example.com",
            "title": existing_source["title"],
            "summary": existing_source["summary"],
            "total_word_count": existing_source["total_word_count"],
            "metadata": {
                "knowledge_type": existing_source["metadata"]["knowledge_type"],
                "crawl_status": "completed",  # UPDATE THIS
                "update_frequency": 7,
                # NOTE: tags and original_url are NOT explicitly included!
            }
        }
        await fake_repo.upsert_source(upsert_data)

        # Verify
        updated_source = await fake_repo.get_source_by_id("docs.example.com")

        # ✅ FIX VERIFIED: crawl_status updated
        assert updated_source["metadata"]["crawl_status"] == "completed"

        # ✅ FIX VERIFIED: Other fields are preserved (merged, not replaced)
        assert "tags" in updated_source["metadata"], \
            "tags should be preserved after merge"
        assert updated_source["metadata"]["tags"] == ["docs"], \
            f"Expected ['docs'], got {updated_source['metadata']['tags']}"

        assert "original_url" in updated_source["metadata"], \
            "original_url should be preserved after merge"
        assert updated_source["metadata"]["original_url"] == "https://docs.example.com"

        print("\n✅ BUG FIXED: Metadata fields are now preserved during upsert!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
