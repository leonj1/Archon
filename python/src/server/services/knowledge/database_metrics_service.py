"""
Database Metrics Service

Handles retrieval of database statistics and metrics.
"""

from datetime import datetime
from typing import Any, Optional

from ...repositories.database_repository import DatabaseRepository
from ...repositories.repository_factory import get_repository
from ...config.logfire_config import safe_logfire_error, safe_logfire_info

class DatabaseMetricsService:
    """
    Service for retrieving database metrics and statistics.
    """

    def __init__(self, repository: Optional[DatabaseRepository] = None, supabase_client=None):
        """
        Initialize with optional repository or supabase client.

        Args:
            repository: DatabaseRepository instance (preferred)
            supabase_client: Legacy supabase client (for backward compatibility)
        """
        if repository is not None:
            self.repository = repository
        elif supabase_client is not None:
            self.repository = SupabaseDatabaseRepository(supabase_client)
        else:
            self.repository = get_repository()

    async def get_metrics(self) -> dict[str, Any]:
        """
        Get database metrics and statistics.

        Returns:
            Dictionary containing database metrics
        """
        try:
            safe_logfire_info("Getting database metrics")

            metrics = {}

            # Sources count - get all sources and count them
            sources = await self.repository.list_sources()
            metrics["sources_count"] = len(sources)

            # Crawled pages count - sum up pages across all sources
            pages_count = 0
            for source in sources:
                source_id = source.get("source_id")
                if source_id:
                    source_page_count = await self.repository.get_page_count_by_source(source_id)
                    pages_count += source_page_count
            metrics["pages_count"] = pages_count

            # Code examples count - sum up code examples across all sources
            code_examples_count = 0
            try:
                for source in sources:
                    source_id = source.get("source_id")
                    if source_id:
                        source_code_count = await self.repository.get_code_example_count_by_source(source_id)
                        code_examples_count += source_code_count
            except Exception:
                # If code examples table doesn't exist or errors, set to 0
                code_examples_count = 0
            metrics["code_examples_count"] = code_examples_count

            # Add timestamp
            metrics["timestamp"] = datetime.now().isoformat()

            # Calculate additional metrics
            metrics["average_pages_per_source"] = (
                round(metrics["pages_count"] / metrics["sources_count"], 2)
                if metrics["sources_count"] > 0
                else 0
            )

            safe_logfire_info(
                f"Database metrics retrieved | sources={metrics['sources_count']} | pages={metrics['pages_count']} | code_examples={metrics['code_examples_count']}"
            )

            return metrics

        except Exception as e:
            safe_logfire_error(f"Failed to get database metrics | error={str(e)}")
            raise

    async def get_storage_statistics(self) -> dict[str, Any]:
        """
        Get storage statistics including sizes and counts by type.

        Returns:
            Dictionary containing storage statistics
        """
        try:
            stats = {}

            # Get all sources to extract knowledge type distribution
            sources = await self.repository.list_sources()

            if sources:
                type_counts = {}
                for source in sources:
                    metadata = source.get("metadata", {})
                    ktype = metadata.get("knowledge_type", "unknown")
                    type_counts[ktype] = type_counts.get(ktype, 0) + 1
                stats["knowledge_type_distribution"] = type_counts

                # Get recent activity - sort by created_at and take first 5
                sorted_sources = sorted(
                    sources,
                    key=lambda s: s.get("created_at", ""),
                    reverse=True
                )
                stats["recent_sources"] = [
                    {"source_id": s["source_id"], "created_at": s["created_at"]}
                    for s in sorted_sources[:5]
                ]
            else:
                stats["knowledge_type_distribution"] = {}
                stats["recent_sources"] = []

            return stats

        except Exception as e:
            safe_logfire_error(f"Failed to get storage statistics | error={str(e)}")
            return {}
