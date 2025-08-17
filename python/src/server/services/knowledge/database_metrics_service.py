"""
Database Metrics Service

Handles retrieval of database statistics and metrics.
"""

from datetime import datetime
from typing import Any

from ...config.logfire_config import safe_logfire_error, safe_logfire_info
from ..client_manager import get_connection_manager


class DatabaseMetricsService:
    """
    Service for retrieving database metrics and statistics.
    """

    def __init__(self):
        """
        Initialize the database metrics service.
        """
        pass

    async def get_metrics(self) -> dict[str, Any]:
        """
        Get database metrics and statistics.

        Returns:
            Dictionary containing database metrics
        """
        try:
            safe_logfire_info("Getting database metrics")
            manager = get_connection_manager()

            # Get counts from various tables
            metrics = {}

            async with manager.get_reader() as db:
                # Sources count
                sources_count = await db.count("sources")
                metrics["sources_count"] = sources_count

                # Crawled pages count
                pages_count = await db.count("crawled_pages")
                metrics["pages_count"] = pages_count

                # Code examples count
                try:
                    code_examples_count = await db.count("code_examples")
                    metrics["code_examples_count"] = code_examples_count
                except Exception:
                    metrics["code_examples_count"] = 0

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
            manager = get_connection_manager()

            async with manager.get_reader() as db:
                # Get knowledge type distribution
                knowledge_types_result = await db.select(
                    "sources",
                    columns=["metadata"]
                )

                if knowledge_types_result.success and knowledge_types_result.data:
                    type_counts = {}
                    for row in knowledge_types_result.data:
                        metadata = row.get("metadata", {})
                        ktype = metadata.get("knowledge_type", "unknown")
                        type_counts[ktype] = type_counts.get(ktype, 0) + 1
                    stats["knowledge_type_distribution"] = type_counts

                # Get recent activity
                recent_sources_result = await db.select(
                    "sources",
                    columns=["source_id", "created_at"],
                    order_by="created_at DESC",
                    limit=5
                )

                if recent_sources_result.success:
                    stats["recent_sources"] = [
                        {"source_id": s["source_id"], "created_at": s["created_at"]}
                        for s in (recent_sources_result.data or [])
                    ]
                else:
                    stats["recent_sources"] = []

            return stats

        except Exception as e:
            safe_logfire_error(f"Failed to get storage statistics | error={str(e)}")
            return {}
