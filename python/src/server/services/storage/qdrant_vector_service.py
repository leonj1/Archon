"""
Qdrant Vector Storage Service

This service handles vector storage operations with Qdrant,
providing an alternative to pgvector for semantic search capabilities.
"""

import uuid
from typing import Any

try:
    from qdrant_client import AsyncQdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    AsyncQdrantClient = None  # Type: ignore
    Distance = None  # Type: ignore
    PointStruct = None  # Type: ignore
    VectorParams = None  # Type: ignore

from ...config.logfire_config import get_logger

logger = get_logger(__name__)


class QdrantVectorService:
    """Service for managing vector storage in Qdrant."""

    def __init__(self, url: str = "http://localhost:6333", collection_name: str = "archon_documents"):
        """
        Initialize Qdrant vector service.

        Args:
            url: Qdrant server URL (default: localhost:6333)
            collection_name: Name of the collection to use

        Raises:
            ImportError: If qdrant-client is not installed
        """
        if not QDRANT_AVAILABLE:
            raise ImportError(
                "qdrant-client is not installed. "
                "Install with: pip install qdrant-client>=1.7.0"
            )
        self.client = AsyncQdrantClient(url=url)
        self.collection_name = collection_name
        self.embedding_dimension = 1536  # OpenAI text-embedding-3-small default

    async def ensure_collection(self, dimension: int | None = None):
        """
        Ensure the collection exists with proper configuration.

        Args:
            dimension: Vector dimension (default: 1536 for OpenAI)
        """
        if dimension:
            self.embedding_dimension = dimension

        collections = await self.client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if self.collection_name not in collection_names:
            logger.info(f"Creating Qdrant collection: {self.collection_name}")
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dimension,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Collection {self.collection_name} created successfully")

    async def store_embeddings(
        self,
        documents: list[dict[str, Any]],
        embeddings: list[list[float]]
    ) -> list[str]:
        """
        Store document embeddings in Qdrant.

        Args:
            documents: List of document metadata dictionaries
            embeddings: List of embedding vectors

        Returns:
            List of point IDs that were stored
        """
        if len(documents) != len(embeddings):
            raise ValueError(f"Mismatch: {len(documents)} documents but {len(embeddings)} embeddings")

        # Ensure collection exists
        await self.ensure_collection()

        points = []
        point_ids = []

        for doc, embedding in zip(documents, embeddings):
            # Generate unique ID or use existing document ID
            point_id = doc.get("id") or str(uuid.uuid4())
            point_ids.append(point_id)

            # Create point with embedding and metadata
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "document_id": doc.get("id", ""),
                    "url": doc.get("url", ""),
                    "source_id": doc.get("source_id", ""),
                    "chunk_number": doc.get("chunk_number", 0),
                    "content": doc.get("content", ""),
                    "metadata": doc.get("metadata", {}),
                }
            )
            points.append(point)

        # Batch upsert to Qdrant
        await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        logger.info(f"Stored {len(points)} embeddings in Qdrant collection {self.collection_name}")
        return point_ids

    async def search_similar(
        self,
        query_embedding: list[float],
        limit: int = 5,
        source_filter: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Search for similar documents using vector similarity.

        Args:
            query_embedding: Query vector
            limit: Maximum number of results
            source_filter: Optional source ID to filter results

        Returns:
            List of similar documents with scores
        """
        # Build query filter if needed
        query_filter = None
        if source_filter:
            from qdrant_client.models import FieldCondition, Filter, MatchValue
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="source_id",
                        match=MatchValue(value=source_filter)
                    )
                ]
            )

        # Perform vector search
        results = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            query_filter=query_filter
        )

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.id,
                "score": result.score,
                "document_id": result.payload.get("document_id"),
                "url": result.payload.get("url"),
                "source_id": result.payload.get("source_id"),
                "chunk_number": result.payload.get("chunk_number"),
                "content": result.payload.get("content"),
                "metadata": result.payload.get("metadata", {}),
            })

        logger.info(f"Found {len(formatted_results)} similar documents in Qdrant")
        return formatted_results

    async def delete_by_source(self, source_id: str) -> int:
        """
        Delete all vectors for a given source.

        Args:
            source_id: Source ID to delete

        Returns:
            Number of points deleted
        """
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        # Get count before deletion
        count_result = await self.client.count(
            collection_name=self.collection_name,
            count_filter=Filter(
                must=[
                    FieldCondition(
                        key="source_id",
                        match=MatchValue(value=source_id)
                    )
                ]
            )
        )
        count_before = count_result.count

        # Delete points
        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="source_id",
                        match=MatchValue(value=source_id)
                    )
                ]
            )
        )

        logger.info(f"Deleted {count_before} vectors for source {source_id}")
        return count_before

    async def get_collection_info(self) -> dict[str, Any]:
        """
        Get information about the collection.

        Returns:
            Dictionary with collection statistics
        """
        try:
            info = await self.client.get_collection(collection_name=self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status.value if info.status else "unknown",
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {
                "name": self.collection_name,
                "vectors_count": 0,
                "points_count": 0,
                "status": "error",
                "error": str(e)
            }

    async def close(self):
        """Close the Qdrant client connection."""
        await self.client.close()
