"""
Base Search Strategy

Implements the foundational vector similarity search that all other strategies build upon.
This is the core semantic search functionality.
"""

from typing import Any

from ...dal import ConnectionManager

from ...config.logfire_config import get_logger, safe_span

logger = get_logger(__name__)

# Fixed similarity threshold for vector results
SIMILARITY_THRESHOLD = 0.15


class BaseSearchStrategy:
    """Base strategy implementing fundamental vector similarity search"""

    def __init__(self, connection_manager: ConnectionManager):
        """Initialize with connection manager"""
        self.connection_manager = connection_manager

    async def vector_search(
        self,
        query_embedding: list[float],
        match_count: int,
        filter_metadata: dict | None = None,
        table_name: str = "documents",
    ) -> list[dict[str, Any]]:
        """
        Perform basic vector similarity search.

        This is the foundational semantic search that all strategies use.

        Args:
            query_embedding: The embedding vector for the query
            match_count: Number of results to return
            filter_metadata: Optional metadata filters
            table_name: The table to search (documents or code_examples)

        Returns:
            List of matching documents with similarity scores
        """
        with safe_span("base_vector_search", table=table_name, match_count=match_count) as span:
            try:
                import numpy as np
                
                # Convert embedding to numpy array
                query_vector = np.array(query_embedding)
                
                # Build filters
                filters = {}
                if filter_metadata:
                    # Handle source filter specifically
                    if "source" in filter_metadata:
                        # Extract domain from source URL if it looks like a URL
                        source = filter_metadata["source"]
                        if source.startswith("http"):
                            from urllib.parse import urlparse
                            parsed = urlparse(source)
                            domain = parsed.netloc
                            filters["source"] = domain
                        else:
                            filters["source"] = source
                    else:
                        filters.update(filter_metadata)

                # Perform vector search
                async with self.connection_manager.get_vector_store() as db:
                    results = await db.search(
                        collection=table_name,
                        query_vector=query_vector,
                        top_k=match_count,
                        filters=filters,
                        include_metadata=True,
                        include_vectors=False,
                    )

                # Filter by similarity threshold and convert format
                filtered_results = []
                for result in results:
                    if result.score >= SIMILARITY_THRESHOLD:
                        # Convert to the expected format
                        formatted_result = {
                            "id": result.id,
                            "content": result.content,
                            "metadata": result.metadata,
                            "similarity": result.score,
                        }
                        filtered_results.append(formatted_result)

                span.set_attribute("results_found", len(filtered_results))
                span.set_attribute(
                    "results_filtered",
                    len(results) - len(filtered_results),
                )

                return filtered_results

            except Exception as e:
                logger.error(f"Vector search failed: {e}")
                span.set_attribute("error", str(e))
                return []
