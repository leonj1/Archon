"""
Fix sources with crawl_status='pending' but have documents.

This script updates sources that were successfully crawled but weren't
properly marked as 'completed' due to earlier code versions.
"""

import asyncio
import json

from src.server.repositories.repository_factory import get_repository


async def fix_pending_sources():
    """Update sources with documents but pending status to completed."""
    repository = get_repository()

    # Initialize repository if needed
    if hasattr(repository, 'initialize'):
        await repository.initialize()

    print("🔍 Finding sources with pending status but have documents...")

    # Get all sources
    sources = await repository.list_sources()

    fixed_count = 0
    already_correct = 0
    no_documents = 0

    for source in sources:
        source_id = source["source_id"]
        metadata = source.get("metadata", {})

        # Parse metadata if it's a string
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata) if metadata else {}
            except (json.JSONDecodeError, TypeError):
                metadata = {}

        crawl_status = metadata.get("crawl_status", "pending")

        # Get document count for this source
        doc_count = await repository.get_page_count_by_source(source_id)

        if crawl_status == "pending" and doc_count > 0:
            # This source should be marked as completed!
            print(f"📝 Fixing {source['title']}: {doc_count} documents, status={crawl_status}")

            # Update metadata with completed status
            metadata["crawl_status"] = "completed"

            # Update the source
            await repository.upsert_source({
                "source_id": source_id,
                "title": source.get("title"),
                "summary": source.get("summary"),
                "total_word_count": source.get("total_word_count", 0),
                "metadata": metadata,
                "source_url": source.get("source_url"),
                "source_display_name": source.get("source_display_name"),
            })

            fixed_count += 1

        elif crawl_status == "completed":
            already_correct += 1

        elif doc_count == 0:
            no_documents += 1
            print(f"⏳ {source['title']}: No documents yet (status={crawl_status})")

    print(f"\n✅ Fixed {fixed_count} sources")
    print(f"✓  {already_correct} sources already had correct status")
    print(f"⏳ {no_documents} sources have no documents yet")

    return fixed_count


async def main():
    """Main entry point."""
    print("=" * 60)
    print("Fix Pending Sources Script")
    print("=" * 60)
    print()

    fixed = await fix_pending_sources()

    print()
    print("=" * 60)
    print(f"Complete! Fixed {fixed} sources with incorrect status.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
