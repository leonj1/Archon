"""
Knowledge Item Service

Handles all knowledge item CRUD operations and data transformations.
"""

from typing import Any

from ...config.logfire_config import safe_logfire_error, safe_logfire_info
from ..client_manager import get_connection_manager


class KnowledgeItemService:
    """
    Service for managing knowledge items including listing, filtering, updating, and deletion.
    """

    def __init__(self):
        """
        Initialize the knowledge item service.
        """
        pass

    async def list_items(
        self,
        page: int = 1,
        per_page: int = 20,
        knowledge_type: str | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        """
        List knowledge items with pagination and filtering.

        Args:
            page: Page number (1-based)
            per_page: Items per page
            knowledge_type: Filter by knowledge type
            search: Search term for filtering

        Returns:
            Dict containing items, pagination info, and total count
        """
        try:
            manager = get_connection_manager()

            async with manager.get_reader() as db:
                # Apply knowledge type filter at database level if provided
                # Note: JSON field filtering is handled by adapter implementation
                if knowledge_type:
                    # This is simplified - actual JSON querying depends on database adapter
                    pass

                # For search, we'll need to get all records and filter in memory
                # as complex text search across multiple fields varies by database

                # Get total count before pagination
                if not knowledge_type and not search:
                    # Simple count when no filters
                    total = await db.count("sources")
                else:
                    # Need to count filtered results
                    count_result = await db.select("sources", columns=["source_id"])
                    if count_result and count_result.success and count_result.data:
                        all_sources = count_result.data
                        # Apply filters in memory for count
                        filtered_sources = await self._apply_filters_in_memory(
                            all_sources, knowledge_type, search, db
                        )
                        total = len(filtered_sources)
                    else:
                        total = 0

                # Get sources with pagination
                start_idx = (page - 1) * per_page

                if not knowledge_type and not search:
                    # Simple query when no filters
                    sources_result = await db.select(
                        "sources",
                        order_by="source_id",
                        limit=per_page,
                        offset=start_idx
                    )
                    sources = sources_result.data if sources_result and sources_result.success and sources_result.data else []
                else:
                    # Get all and filter in memory
                    all_result = await db.select("sources", order_by="source_id")
                    if all_result and all_result.success and all_result.data:
                        all_sources = all_result.data
                        filtered_sources = await self._apply_filters_in_memory(
                            all_sources, knowledge_type, search, db
                        )
                        # Apply pagination to filtered results
                        sources = filtered_sources[start_idx:start_idx + per_page]
                    else:
                        sources = []

                # Get source IDs for batch queries
                source_ids = [source["source_id"] for source in sources]

                # Debug log source IDs
                safe_logfire_info(f"Source IDs for batch query: {source_ids}")

                # Batch fetch related data to avoid N+1 queries
                first_urls = {}
                code_example_counts = {}
                chunk_counts = {}

                if source_ids:
                    # Batch fetch first URLs
                    for source_id in source_ids:
                        urls_result = await db.select(
                            "crawled_pages",
                            columns=["url"],
                            filters={"source_id": source_id},
                            limit=1
                        )

                        if urls_result.success and urls_result.data:
                            first_urls[source_id] = urls_result.data[0]["url"]

                    # Get code example counts per source
                    for source_id in source_ids:
                        count = await db.count("code_examples", filters={"source_id": source_id})
                        code_example_counts[source_id] = count

                    # Ensure all sources have counts (default to 0)
                    for source_id in source_ids:
                        if source_id not in code_example_counts:
                            code_example_counts[source_id] = 0
                        chunk_counts[source_id] = 0  # Default to 0 to avoid timeout

                    safe_logfire_info(f"Code example counts: {code_example_counts}")

                # Transform sources to items with batched data
                items = []
                for source in sources:
                    source_id = source["source_id"]
                    source_metadata = source.get("metadata", {}) or {}

                    # Use batched data instead of individual queries
                    first_page_url = first_urls.get(source_id, f"source://{source_id}")
                    code_examples_count = code_example_counts.get(source_id, 0)
                    chunks_count = chunk_counts.get(source_id, 0)

                    # Determine source type
                    source_type = self._determine_source_type(source_metadata, first_page_url)

                    item = {
                        "id": source_id,
                        "title": source.get("title", source.get("summary", "Untitled")),
                        "url": first_page_url,
                        "source_id": source_id,
                        "code_examples": [{"count": code_examples_count}]
                        if code_examples_count > 0
                        else [],  # Minimal array just for count display
                        "metadata": {
                            "knowledge_type": source_metadata.get("knowledge_type", "technical"),
                            "tags": source_metadata.get("tags", []),
                            "source_type": source_type,
                            "status": "active",
                            "description": source_metadata.get(
                                "description", source.get("summary", "")
                            ),
                            "chunks_count": chunks_count,
                            "word_count": source.get("total_word_count", 0),
                            "estimated_pages": round(source.get("total_word_count", 0) / 250, 1),
                            "pages_tooltip": f"{round(source.get('total_word_count', 0) / 250, 1)} pages (≈ {source.get('total_word_count', 0):,} words)",
                            "last_scraped": source.get("updated_at"),
                            "file_name": source_metadata.get("file_name"),
                            "file_type": source_metadata.get("file_type"),
                            "update_frequency": source_metadata.get("update_frequency", 7),
                            "code_examples_count": code_examples_count,
                            **source_metadata,
                        },
                        "created_at": source.get("created_at"),
                        "updated_at": source.get("updated_at"),
                    }
                    items.append(item)

                safe_logfire_info(
                    f"Knowledge items retrieved | total={total} | page={page} | filtered_count={len(items)}"
                )

                return {
                    "items": items,
                    "total": total,
                    "page": page,
                    "per_page": per_page,
                    "pages": (total + per_page - 1) // per_page,
                }

        except Exception as e:
            safe_logfire_error(f"Failed to list knowledge items | error={str(e)}")
            raise

    async def get_item(self, source_id: str) -> dict[str, Any] | None:
        """
        Get a single knowledge item by source ID.

        Args:
            source_id: The source ID to retrieve

        Returns:
            Knowledge item dict or None if not found
        """
        try:
            safe_logfire_info(f"Getting knowledge item | source_id={source_id}")
            manager = get_connection_manager()

            async with manager.get_reader() as db:
                # Get the source record
                result = await db.select(
                    "sources",
                    filters={"source_id": source_id}
                )

                if not result.success or not result.data:
                    return None

                # Transform the source to item format
                item = await self._transform_source_to_item(result.data[0])
                return item

        except Exception as e:
            safe_logfire_error(
                f"Failed to get knowledge item | error={str(e)} | source_id={source_id}"
            )
            return None

    async def update_item(
        self, source_id: str, updates: dict[str, Any]
    ) -> tuple[bool, dict[str, Any]]:
        """
        Update a knowledge item's metadata.

        Args:
            source_id: The source ID to update
            updates: Dictionary of fields to update

        Returns:
            Tuple of (success, result)
        """
        try:
            safe_logfire_info(
                f"Updating knowledge item | source_id={source_id} | updates={updates}"
            )
            manager = get_connection_manager()

            async with manager.get_primary() as db:
                # Prepare update data
                update_data = {}

                # Handle title updates
                if "title" in updates:
                    update_data["title"] = updates["title"]

                # Handle metadata updates
                metadata_fields = [
                    "description",
                    "knowledge_type",
                    "tags",
                    "status",
                    "update_frequency",
                    "group_name",
                ]
                metadata_updates = {k: v for k, v in updates.items() if k in metadata_fields}

                if metadata_updates:
                    # Get current metadata
                    current_result = await db.select(
                        "sources",
                        columns=["metadata"],
                        filters={"source_id": source_id}
                    )

                    if current_result.success and current_result.data:
                        current_metadata = current_result.data[0].get("metadata", {})
                        current_metadata.update(metadata_updates)
                        update_data["metadata"] = current_metadata
                    else:
                        update_data["metadata"] = metadata_updates

                # Perform the update
                result = await db.update(
                    "sources",
                    update_data,
                    filters={"source_id": source_id},
                    returning=["source_id"]
                )

                if result.success and result.data:
                    safe_logfire_info(f"Knowledge item updated successfully | source_id={source_id}")
                    return True, {
                        "success": True,
                        "message": f"Successfully updated knowledge item {source_id}",
                        "source_id": source_id,
                    }
                else:
                    safe_logfire_error(f"Knowledge item not found | source_id={source_id}")
                    return False, {"error": f"Knowledge item {source_id} not found"}

        except Exception as e:
            safe_logfire_error(
                f"Failed to update knowledge item | error={str(e)} | source_id={source_id}"
            )
            return False, {"error": str(e)}

    async def get_available_sources(self) -> dict[str, Any]:
        """
        Get all available sources with their details.

        Returns:
            Dict containing sources list and count
        """
        try:
            manager = get_connection_manager()

            async with manager.get_reader() as db:
                # Query the sources table
                result = await db.select("sources", order_by="source_id")

                # Format the sources
                sources = []
                if result.success and result.data:
                    for source in result.data:
                        sources.append({
                            "source_id": source.get("source_id"),
                            "title": source.get("title", source.get("summary", "Untitled")),
                            "summary": source.get("summary"),
                            "metadata": source.get("metadata", {}),
                            "total_words": source.get("total_words", source.get("total_word_count", 0)),
                            "update_frequency": source.get("update_frequency", 7),
                            "created_at": source.get("created_at"),
                            "updated_at": source.get("updated_at", source.get("created_at")),
                        })

                return {"success": True, "sources": sources, "count": len(sources)}

        except Exception as e:
            safe_logfire_error(f"Failed to get available sources | error={str(e)}")
            return {"success": False, "error": str(e), "sources": [], "count": 0}

    async def _get_all_sources(self) -> list[dict[str, Any]]:
        """Get all sources from the database."""
        result = await self.get_available_sources()
        return result.get("sources", [])

    async def _transform_source_to_item(self, source: dict[str, Any]) -> dict[str, Any]:
        """
        Transform a source record into a knowledge item with enriched data.

        Args:
            source: The source record from database

        Returns:
            Transformed knowledge item
        """
        source_metadata = source.get("metadata", {})
        source_id = source["source_id"]

        # Get first page URL
        first_page_url = await self._get_first_page_url(source_id)

        # Determine source type
        source_type = self._determine_source_type(source_metadata, first_page_url)

        # Get code examples
        code_examples = await self._get_code_examples(source_id)

        return {
            "id": source_id,
            "title": source.get("title", source.get("summary", "Untitled")),
            "url": first_page_url,
            "source_id": source_id,
            "code_examples": code_examples,
            "metadata": {
                "knowledge_type": source_metadata.get("knowledge_type", "technical"),
                "tags": source_metadata.get("tags", []),
                "source_type": source_type,
                "status": "active",
                "description": source_metadata.get("description", source.get("summary", "")),
                "chunks_count": await self._get_chunks_count(source_id),  # Get actual chunk count
                "word_count": source.get("total_words", 0),
                "estimated_pages": round(
                    source.get("total_words", 0) / 250, 1
                ),  # Average book page = 250 words
                "pages_tooltip": f"{round(source.get('total_words', 0) / 250, 1)} pages (≈ {source.get('total_words', 0):,} words)",
                "last_scraped": source.get("updated_at"),
                "file_name": source_metadata.get("file_name"),
                "file_type": source_metadata.get("file_type"),
                "update_frequency": source.get("update_frequency", 7),
                "code_examples_count": len(code_examples),
                **source_metadata,
            },
            "created_at": source.get("created_at"),
            "updated_at": source.get("updated_at"),
        }

    async def _get_first_page_url(self, source_id: str) -> str:
        """Get the first page URL for a source."""
        try:
            manager = get_connection_manager()

            async with manager.get_reader() as db:
                pages_result = await db.select(
                    "crawled_pages",
                    columns=["url"],
                    filters={"source_id": source_id},
                    limit=1
                )

                if pages_result.success and pages_result.data:
                    return pages_result.data[0].get("url", f"source://{source_id}")

        except Exception:
            pass

        return f"source://{source_id}"

    async def _get_code_examples(self, source_id: str) -> list[dict[str, Any]]:
        """Get code examples for a source."""
        try:
            manager = get_connection_manager()

            async with manager.get_reader() as db:
                code_examples_result = await db.select(
                    "code_examples",
                    columns=["id", "content", "summary", "metadata"],
                    filters={"source_id": source_id}
                )

                return code_examples_result.data if code_examples_result.success else []

        except Exception:
            return []

    def _determine_source_type(self, metadata: dict[str, Any] | None, url: str) -> str:
        """Determine the source type from metadata or URL pattern."""
        if metadata is None:
            metadata = {}
            
        stored_source_type = metadata.get("source_type")
        if stored_source_type:
            return stored_source_type

        # Legacy fallback - check URL pattern
        return "file" if url.startswith("file://") else "url"

    async def _apply_filters_in_memory(
        self,
        sources: list[dict[str, Any]],
        knowledge_type: str | None,
        search: str | None,
        db
    ) -> list[dict[str, Any]]:
        """Apply filters to sources in memory when database-level filtering isn't available."""
        filtered_sources = sources

        # Filter by knowledge type
        if knowledge_type:
            filtered_sources = [
                source for source in filtered_sources
                if source.get("metadata", {}).get("knowledge_type") == knowledge_type
            ]

        # Filter by search term
        if search:
            search_lower = search.lower()
            filtered_sources = [
                source for source in filtered_sources
                if (
                    search_lower in source.get("title", "").lower() or
                    search_lower in source.get("summary", "").lower() or
                    search_lower in source.get("source_id", "").lower()
                )
            ]

        return filtered_sources

    def _filter_by_search(self, items: list[dict[str, Any]], search: str) -> list[dict[str, Any]]:
        """Filter items by search term."""
        search_lower = search.lower()
        return [
            item
            for item in items
            if search_lower in item["title"].lower()
            or search_lower in item["metadata"].get("description", "").lower()
            or any(search_lower in tag.lower() for tag in item["metadata"].get("tags", []))
        ]

    def _filter_by_knowledge_type(
        self, items: list[dict[str, Any]], knowledge_type: str
    ) -> list[dict[str, Any]]:
        """Filter items by knowledge type."""
        return [item for item in items if item["metadata"].get("knowledge_type") == knowledge_type]

    async def _get_chunks_count(self, source_id: str) -> int:
        """Get the actual number of chunks for a source."""
        try:
            manager = get_connection_manager()

            async with manager.get_reader() as db:
                # Count the actual rows in crawled_pages for this source
                count = await db.count("crawled_pages", filters={"source_id": source_id})
                return count

        except Exception as e:
            # If we can't get chunk count, return 0
            safe_logfire_info(f"Failed to get chunk count for {source_id}: {e}")
            return 0
