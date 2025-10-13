"""
Base Search Strategy

Implements the foundational vector similarity search that all other strategies build upon.
This is the core semantic search functionality.
"""

from typing import Any

from ...config.logfire_config import get_logger, safe_span
from ...repositories import DatabaseRepository

logger = get_logger(__name__)

# Fixed similarity threshold for vector results
SIMILARITY_THRESHOLD = 0.05

class BaseSearchStrategy:
    """Base strategy implementing fundamental vector similarity search"""

    def __init__(self, database_repository: DatabaseRepository):
        """
        Initialize with dependency injection.

        Args:
            database_repository: DatabaseRepository implementation for database operations.
                                Required - must be provided by caller.
        """
        # Always require repository to be passed in
        if database_repository is None:
            raise ValueError("database_repository is required - BaseSearchStrategy must be initialized with a repository")

        self.db_repository = database_repository

    async def vector_search(
        self,
        query_embedding: list[float],
        match_count: int,
        filter_metadata: dict | None = None,
        table_rpc: str = "match_archon_crawled_pages",
    ) -> list[dict[str, Any]]:
        """
        Perform basic vector similarity search.

        This is the foundational semantic search that all strategies use.

        Args:
            query_embedding: The embedding vector for the query
            match_count: Number of results to return
            filter_metadata: Optional metadata filters
            table_rpc: The RPC function to call (match_archon_crawled_pages or match_archon_code_examples)

        Returns:
            List of matching documents with similarity scores
        """
        with safe_span("base_vector_search", table=table_rpc, match_count=match_count) as span:
            try:
                # Build RPC parameters
                rpc_params = {"query_embedding": query_embedding, "match_count": match_count}

                # Add filter parameters
                if filter_metadata:
                    if "source" in filter_metadata:
                        rpc_params["source_filter"] = filter_metadata["source"]
                        rpc_params["filter"] = {}
                    else:
                        rpc_params["filter"] = filter_metadata
                else:
                    rpc_params["filter"] = {}

                # Execute search using repository
                results = await self.db_repository.execute_rpc(table_rpc, rpc_params)

                # Filter by similarity threshold
                filtered_results = []
                if results:
                    for result in results:
                        similarity = float(result.get("similarity", 0.0))
                        if similarity >= SIMILARITY_THRESHOLD:
                            filtered_results.append(result)

                span.set_attribute("results_found", len(filtered_results))
                span.set_attribute(
                    "results_filtered",
                    len(results) - len(filtered_results) if results else 0,
                )

                return filtered_results

            except Exception as e:
                logger.error(f"Vector search failed: {e}")
                span.set_attribute("error", str(e))
                return []
