"""
Knowledge Summary Service

Provides lightweight summary data for knowledge items to minimize data transfer.
Optimized for frequent polling and card displays.
"""

from typing import Any, Optional

from ...config.logfire_config import safe_logfire_info, safe_logfire_error
from ...repositories.database_repository import DatabaseRepository
from ...repositories.supabase_repository import SupabaseDatabaseRepository
from ...utils import get_supabase_client


class KnowledgeSummaryService:
    """
    Service for providing lightweight knowledge item summaries.
    Designed for efficient polling with minimal data transfer.
    """

    def __init__(self, repository: Optional[DatabaseRepository] = None):
        """
        Initialize with optional repository.

        Args:
            repository: DatabaseRepository instance
        """
        if repository is not None:
            self.repository = repository
        else:
            self.repository = SupabaseDatabaseRepository(get_supabase_client())

    async def get_summaries(
        self,
        page: int = 1,
        per_page: int = 20,
        knowledge_type: Optional[str] = None,
        search: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Get lightweight summaries of knowledge items.

        Returns only essential data needed for card displays:
        - Basic metadata (title, url, type, tags)
        - Counts only (no actual content)
        - Minimal processing overhead

        Args:
            page: Page number (1-based)
            per_page: Items per page
            knowledge_type: Optional filter by knowledge type
            search: Optional search term

        Returns:
            Dict with minimal item summaries and pagination info
        """
        try:
            safe_logfire_info(f"Fetching knowledge summaries | page={page} | per_page={per_page}")

            # Calculate pagination offsets
            start_idx = (page - 1) * per_page

            # Use repository method for filtering, searching, and pagination
            sources, total = await self.repository.list_sources_with_pagination(
                knowledge_type=knowledge_type,
                search_query=search,
                limit=per_page,
                offset=start_idx,
                order_by="updated_at",
                desc=True,
                select_fields="source_id, title, summary, metadata, source_url, created_at, updated_at"
            )
            
            # Get source IDs for batch operations
            source_ids = [s["source_id"] for s in sources]
            
            # Batch fetch counts only (no content!)
            summaries = []
            
            if source_ids:
                # Get document counts in a single query
                doc_counts = await self._get_document_counts_batch(source_ids)
                
                # Get code example counts in a single query
                code_counts = await self._get_code_example_counts_batch(source_ids)
                
                # Get first URLs in a single query
                first_urls = await self._get_first_urls_batch(source_ids)
                
                # Build summaries
                for source in sources:
                    source_id = source["source_id"]
                    metadata = source.get("metadata", {})
                    
                    # Use the original source_url from the source record (the URL the user entered)
                    # Fall back to first crawled page URL, then to source:// format as last resort
                    source_url = source.get("source_url")
                    if source_url:
                        first_url = source_url
                    else:
                        first_url = first_urls.get(source_id, f"source://{source_id}")
                    
                    source_type = metadata.get("source_type", "file" if first_url.startswith("file://") else "url")
                    
                    # Extract knowledge_type - check metadata first, otherwise default based on source content
                    # The metadata should always have it if it was crawled properly
                    knowledge_type = metadata.get("knowledge_type")
                    if not knowledge_type:
                        # Fallback: If not in metadata, default to "technical" for now
                        # This handles legacy data that might not have knowledge_type set
                        safe_logfire_info(f"Knowledge type not found in metadata for {source_id}, defaulting to technical")
                        knowledge_type = "technical"
                    
                    summary = {
                        "source_id": source_id,
                        "title": source.get("title", source.get("summary", "Untitled")),
                        "url": first_url,
                        "status": "active",  # Always active for now
                        "document_count": doc_counts.get(source_id, 0),
                        "code_examples_count": code_counts.get(source_id, 0),
                        "knowledge_type": knowledge_type,
                        "source_type": source_type,
                        "created_at": source.get("created_at"),
                        "updated_at": source.get("updated_at"),
                        "metadata": metadata,  # Include full metadata (contains tags)
                    }
                    summaries.append(summary)
            
            safe_logfire_info(
                f"Knowledge summaries fetched | count={len(summaries)} | total={total}"
            )
            
            return {
                "items": summaries,
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page if per_page > 0 else 0,
            }
            
        except Exception as e:
            safe_logfire_error(f"Failed to get knowledge summaries | error={str(e)}")
            raise
    
    async def _get_document_counts_batch(self, source_ids: list[str]) -> dict[str, int]:
        """
        Get document counts for multiple sources in a single query.

        Args:
            source_ids: List of source IDs

        Returns:
            Dict mapping source_id to document count
        """
        try:
            counts = {}

            # Use repository method for each source
            for source_id in source_ids:
                count = await self.repository.get_page_count_by_source(source_id)
                counts[source_id] = count

            return counts

        except Exception as e:
            safe_logfire_error(f"Failed to get document counts | error={str(e)}")
            return {sid: 0 for sid in source_ids}
    
    async def _get_code_example_counts_batch(self, source_ids: list[str]) -> dict[str, int]:
        """
        Get code example counts for multiple sources efficiently.

        Args:
            source_ids: List of source IDs

        Returns:
            Dict mapping source_id to code example count
        """
        try:
            counts = {}

            # Use repository method for each source
            for source_id in source_ids:
                count = await self.repository.get_code_example_count_by_source(source_id)
                counts[source_id] = count

            return counts

        except Exception as e:
            safe_logfire_error(f"Failed to get code example counts | error={str(e)}")
            return {sid: 0 for sid in source_ids}
    
    async def _get_first_urls_batch(self, source_ids: list[str]) -> dict[str, str]:
        """
        Get first URL for each source in a batch.

        Args:
            source_ids: List of source IDs

        Returns:
            Dict mapping source_id to first URL
        """
        try:
            # Use repository method to get first URLs
            urls = await self.repository.get_first_url_by_sources(source_ids)

            # Provide defaults for any missing
            for source_id in source_ids:
                if source_id not in urls:
                    urls[source_id] = f"source://{source_id}"

            return urls

        except Exception as e:
            safe_logfire_error(f"Failed to get first URLs | error={str(e)}")
            return {sid: f"source://{sid}" for sid in source_ids}