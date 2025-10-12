"""
Knowledge Item Service

Handles all knowledge item CRUD operations and data transformations.
"""

from typing import Any

from ...config.logfire_config import safe_logfire_error, safe_logfire_info
from ...repositories.database_repository import DatabaseRepository
from ...repositories.supabase_repository import SupabaseDatabaseRepository
from ...utils import get_supabase_client


class KnowledgeItemService:
    """
    Service for managing knowledge items including listing, filtering, updating, and deletion.
    """

    def __init__(self, repository: DatabaseRepository | None = None):
        """
        Initialize the knowledge item service.

        Args:
            repository: DatabaseRepository instance
        """
        if repository is not None:
            self.repository = repository
        else:
            self.repository = SupabaseDatabaseRepository(get_supabase_client())

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
            # Get all sources from repository
            all_sources = await self.repository.list_sources(knowledge_type=knowledge_type)

            # Apply search filter if provided
            if search:
                search_lower = search.lower()
                filtered_sources = [
                    s for s in all_sources
                    if search_lower in s.get("title", "").lower()
                    or search_lower in s.get("summary", "").lower()
                    or search_lower in s.get("source_id", "").lower()
                ]
            else:
                filtered_sources = all_sources

            # Get total count before pagination
            total = len(filtered_sources)

            # Apply pagination
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            sources = filtered_sources[start_idx:end_idx]

            # Get source IDs for batch queries
            source_ids = [source["source_id"] for source in sources]

            # Debug log source IDs
            safe_logfire_info(f"Source IDs for batch query: {source_ids}")

            # Batch fetch related data to avoid N+1 queries
            first_urls = {}
            code_example_counts = {}
            chunk_counts = {}

            if source_ids:
                # Batch fetch first URLs using repository
                for source_id in source_ids:
                    pages = await self.repository.list_pages_by_source(source_id, limit=1)
                    if pages:
                        first_urls[source_id] = pages[0].get("url", f"source://{source_id}")

                # Get code example counts per source
                for source_id in source_ids:
                    count = await self.repository.get_code_example_count_by_source(source_id)
                    code_example_counts[source_id] = count

                # Get page counts per source (chunks)
                for source_id in source_ids:
                    count = await self.repository.get_page_count_by_source(source_id)
                    chunk_counts[source_id] = count

                safe_logfire_info(f"Code example counts: {code_example_counts}")

            # Transform sources to items with batched data
            items = []
            for source in sources:
                source_id = source["source_id"]
                source_metadata = source.get("metadata", {})

                # Use the original source_url from the source record (the URL the user entered)
                # Fall back to first crawled page URL, then to source:// format as last resort
                source_url = source.get("source_url")
                if source_url:
                    display_url = source_url
                else:
                    display_url = first_urls.get(source_id, f"source://{source_id}")

                code_examples_count = code_example_counts.get(source_id, 0)
                chunks_count = chunk_counts.get(source_id, 0)

                # Determine source type - use display_url for type detection
                source_type = self._determine_source_type(source_metadata, display_url)

                item = {
                    "id": source_id,
                    "title": source.get("title", source.get("summary", "Untitled")),
                    "url": display_url,
                    "source_id": source_id,
                    "source_type": source_type,  # Add top-level source_type field
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

            # Get the source record using repository
            source = await self.repository.get_source_by_id(source_id)

            if not source:
                return None

            # Transform the source to item format
            item = await self._transform_source_to_item(source)
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

            # Get current source
            current_source = await self.repository.get_source_by_id(source_id)
            if not current_source:
                safe_logfire_error(f"Knowledge item not found | source_id={source_id}")
                return False, {"error": f"Knowledge item {source_id} not found"}

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
                # Get current metadata and merge
                current_metadata = current_source.get("metadata", {})
                current_metadata.update(metadata_updates)
                update_data["metadata"] = current_metadata

            # Build the upsert data
            upsert_data = {
                "source_id": source_id,
                **current_source,
                **update_data,
            }

            # Perform the update using upsert_source
            result = await self.repository.upsert_source(upsert_data)

            if result:
                safe_logfire_info(f"Knowledge item updated successfully | source_id={source_id}")
                return True, {
                    "success": True,
                    "message": f"Successfully updated knowledge item {source_id}",
                    "source_id": source_id,
                }
            else:
                safe_logfire_error(f"Failed to update knowledge item | source_id={source_id}")
                return False, {"error": f"Failed to update knowledge item {source_id}"}

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
            # Get all sources using repository
            all_sources = await self.repository.list_sources()

            # Format the sources
            sources = []
            for source in all_sources:
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
                # Spread source_metadata first, then override with computed values
                **source_metadata,
                "knowledge_type": source_metadata.get("knowledge_type", "technical"),
                "tags": source_metadata.get("tags", []),
                "source_type": source_type,  # This should be the correctly determined source_type
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
            },
            "created_at": source.get("created_at"),
            "updated_at": source.get("updated_at"),
        }

    async def _get_first_page_url(self, source_id: str) -> str:
        """Get the first page URL for a source."""
        try:
            pages = await self.repository.list_pages_by_source(source_id, limit=1)

            if pages:
                return pages[0].get("url", f"source://{source_id}")

        except Exception:
            pass

        return f"source://{source_id}"

    async def _get_code_examples(self, source_id: str) -> list[dict[str, Any]]:
        """Get code examples for a source."""
        try:
            code_examples = await self.repository.get_code_examples_by_source(source_id)
            return code_examples if code_examples else []

        except Exception:
            return []

    def _determine_source_type(self, metadata: dict[str, Any], url: str) -> str:
        """Determine the source type from metadata or URL pattern."""
        stored_source_type = metadata.get("source_type")
        if stored_source_type:
            return stored_source_type

        # Legacy fallback - check URL pattern
        return "file" if url.startswith("file://") else "url"

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
            # Count the actual rows in crawled_pages for this source
            count = await self.repository.get_page_count_by_source(source_id)
            return count

        except Exception as e:
            # If we can't get chunk count, return 0
            safe_logfire_info(f"Failed to get chunk count for {source_id}: {e}")
            return 0

    async def get_chunks_for_source(
        self,
        source_id: str,
        domain_filter: str | None = None,
        limit: int = 20,
        offset: int = 0
    ) -> dict[str, Any]:
        """
        Get paginated document chunks for a specific source.

        Args:
            source_id: The source ID to get chunks for
            domain_filter: Optional domain filter for URLs (not yet implemented)
            limit: Maximum number of chunks to return
            offset: Number of chunks to skip for pagination

        Returns:
            Dict with chunks, total count, and pagination info
        """
        try:
            # Get total count for this source
            total = await self.repository.get_page_count_by_source(source_id)

            # Get paginated chunks using repository method
            # Note: list_crawled_pages_by_source returns archon_crawled_pages data
            chunks = await self.repository.list_crawled_pages_by_source(
                source_id=source_id,
                limit=limit,
                offset=offset
            )

            # Apply domain filtering if provided (manual filter since repository doesn't support it yet)
            if domain_filter:
                chunks = [
                    chunk for chunk in chunks
                    if domain_filter.lower() in chunk.get("url", "").lower()
                ]
                # Recalculate total for filtered results (approximation)
                total = len(chunks)

            safe_logfire_info(
                f"Retrieved {len(chunks)} chunks for source {source_id} | total={total}"
            )

            return {
                "chunks": chunks,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total,
            }

        except Exception as e:
            safe_logfire_error(
                f"Failed to get chunks for source | error={str(e)} | source_id={source_id}"
            )
            raise

    async def get_code_examples_for_source(
        self,
        source_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> dict[str, Any]:
        """
        Get paginated code examples for a specific source.

        Args:
            source_id: The source ID to get code examples for
            limit: Maximum number of examples to return
            offset: Number of examples to skip for pagination

        Returns:
            Dict with code examples, total count, and pagination info
        """
        try:
            # Get total count using repository
            total = await self.repository.get_code_example_count_by_source(source_id)

            # Get paginated code examples
            # Note: repository method doesn't support offset, so we'll fetch and slice
            # This is a limitation we should address in the repository later
            all_examples = await self.repository.get_code_examples_by_source(
                source_id=source_id,
                limit=limit + offset  # Fetch enough to support offset
            )

            # Manual offset handling (not ideal, but works for now)
            code_examples = all_examples[offset:offset + limit] if all_examples else []

            safe_logfire_info(
                f"Retrieved {len(code_examples)} code examples for source {source_id} | total={total}"
            )

            return {
                "code_examples": code_examples,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total,
            }

        except Exception as e:
            safe_logfire_error(
                f"Failed to get code examples for source | error={str(e)} | source_id={source_id}"
            )
            raise
