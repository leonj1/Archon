"""
CrawlAndStoreService - Unified high-level pipeline for crawl-to-vector-database ingestion

This service provides a complete, production-ready wrapper that combines SimpleCrawlingService
and SimpleVectorDBService into a single, easy-to-use interface for knowledge base ingestion.

Key Features:
- Single-method ingestion: crawl and store in one call
- Progress tracking with optional callbacks
- Comprehensive error handling with detailed logging
- Resource management via context manager
- Stats aggregation from both crawl and storage
- Search interface with source filtering
- Graceful degradation on partial failures

Architecture:
    CrawlAndStoreService
        ├── SimpleCrawlingService (web crawling)
        └── SimpleVectorDBService (vector storage + search)

Usage Example:
    ```python
    from server.services.storage.crawl_and_store_service import CrawlAndStoreService

    async with CrawlAndStoreService() as service:
        # Ingest a documentation site
        result = await service.ingest_url(
            url="https://docs.example.com",
            source_id="example_docs",
            max_depth=3
        )

        print(f"Ingested {result['crawl']['total_pages']} pages")
        print(f"Stored {result['storage']['chunks_stored']} chunks")

        # Search the knowledge base
        results = await service.search(
            query="How do I authenticate?",
            source_id="example_docs"
        )
    ```
"""

import asyncio
from typing import Any, Callable, Dict, List, Optional

from ...config.logfire_config import get_logger, safe_logfire_error, safe_logfire_info
from ..simple_crawling_service import SimpleCrawlingService
from .simple_vectordb_service import SimpleVectorDBService

logger = get_logger(__name__)


class CrawlAndStoreService:
    """
    Unified service for crawling websites and storing them in vector database.

    This service orchestrates the complete pipeline from URL to searchable vector database,
    providing a simple interface for knowledge base ingestion with progress tracking and
    comprehensive error handling.

    Attributes:
        crawler: SimpleCrawlingService instance for web crawling
        vectordb: SimpleVectorDBService instance for vector storage
        default_max_depth: Default crawl depth (default: 2)
        default_chunk_size: Default chunk size for text splitting (default: 800)
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "archon_knowledge_base",
        default_max_depth: int = 2,
        default_chunk_size: int = 800,
        chunk_overlap: int = 100
    ):
        """
        Initialize the CrawlAndStoreService.

        Args:
            qdrant_url: Qdrant server URL (default: localhost:6333)
            collection_name: Collection name for vector storage
            default_max_depth: Default crawl depth for recursive crawling
            default_chunk_size: Default chunk size in characters
            chunk_overlap: Overlap between chunks in characters

        Raises:
            RuntimeError: If service initialization fails (fail fast)
        """
        try:
            self.crawler = SimpleCrawlingService()
            self.vectordb = SimpleVectorDBService(
                qdrant_url=qdrant_url,
                collection_name=collection_name,
                chunk_size=default_chunk_size,
                chunk_overlap=chunk_overlap
            )
            self.default_max_depth = default_max_depth
            self.default_chunk_size = default_chunk_size

            safe_logfire_info(
                f"CrawlAndStoreService initialized | "
                f"collection={collection_name} | "
                f"max_depth={default_max_depth} | "
                f"chunk_size={default_chunk_size}"
            )
        except Exception as e:
            error_msg = f"Failed to initialize CrawlAndStoreService: {str(e)}"
            safe_logfire_error(error_msg)
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e

    async def ingest_url(
        self,
        url: str,
        source_id: str | None = None,
        max_depth: int | None = None,
        chunk_size: int | None = None,
        max_concurrent: int | None = None,
        progress_callback: Callable[[str, int, Dict[str, Any]], None] | None = None
    ) -> Dict[str, Any]:
        """
        Crawl a URL and store the results in the vector database.

        This is the primary method for knowledge base ingestion. It orchestrates:
        1. Web crawling with SimpleCrawlingService
        2. Document validation and format checking
        3. Vector storage with SimpleVectorDBService
        4. Progress tracking at each stage
        5. Comprehensive error handling

        Args:
            url: The URL to crawl (supports web pages, sitemaps, .txt/.md files)
            source_id: Unique identifier for this source (default: auto-generated from URL)
            max_depth: Maximum crawl depth (default: use instance default)
                      - 1: Single page only
                      - 2+: Follow internal links to specified depth
            chunk_size: Override chunk size for this ingestion
            max_concurrent: Maximum concurrent requests during crawling
            progress_callback: Optional callback(stage, percentage, metadata) for tracking
                             Stages: "crawling", "validating", "storing", "completed"

        Returns:
            Dictionary containing comprehensive results:
            {
                "success": bool,               # Overall success status
                "crawl": {
                    "documents": List[Dict],   # Crawled documents
                    "total_pages": int,        # Number of pages crawled
                    "crawl_type": str          # Type of crawl performed
                },
                "storage": {
                    "chunks_stored": int,      # Number of chunks successfully stored
                    "source_id": str,          # The source_id used
                    "documents_processed": int, # Documents sent to storage
                    "failed_chunks": int       # Chunks that failed to store
                },
                "error": str | None            # Error message if failed
            }

        Raises:
            ValueError: If URL is invalid or empty
            RuntimeError: If both crawling and storage fail (fail fast)

        Note:
            This method follows the "complete but log detailed failures" pattern.
            If crawling succeeds but storage fails, it returns success=False with
            detailed error information. If crawling fails, storage is skipped entirely.

        Example:
            ```python
            async with CrawlAndStoreService() as service:
                result = await service.ingest_url(
                    url="https://docs.python.org",
                    source_id="python_docs",
                    max_depth=3,
                    progress_callback=lambda stage, pct, meta: print(f"{stage}: {pct}%")
                )

                if result["success"]:
                    print(f"Success! Stored {result['storage']['chunks_stored']} chunks")
                else:
                    print(f"Failed: {result['error']}")
            ```
        """
        # Input validation
        if not url or not url.strip():
            raise ValueError("URL cannot be empty")

        url = url.strip()

        # Auto-generate source_id if not provided
        if not source_id:
            source_id = self._generate_source_id(url)

        # Use defaults if not overridden
        max_depth = max_depth if max_depth is not None else self.default_max_depth
        chunk_size = chunk_size if chunk_size is not None else self.default_chunk_size

        safe_logfire_info(
            f"Starting ingestion | url={url} | source_id={source_id} | "
            f"max_depth={max_depth} | chunk_size={chunk_size}"
        )

        # Initialize result structure
        result: Dict[str, Any] = {
            "success": False,
            "crawl": {
                "documents": [],
                "total_pages": 0,
                "crawl_type": "unknown"
            },
            "storage": {
                "chunks_stored": 0,
                "source_id": source_id,
                "documents_processed": 0,
                "failed_chunks": 0
            },
            "error": None
        }

        try:
            # Stage 1: Crawling
            if progress_callback:
                await self._safe_callback(
                    progress_callback,
                    "crawling",
                    0,
                    {"url": url, "max_depth": max_depth}
                )

            documents = await self.crawler.crawl(
                url=url,
                max_depth=max_depth,
                max_concurrent=max_concurrent
            )

            result["crawl"]["documents"] = documents
            result["crawl"]["total_pages"] = len(documents)

            # Extract crawl type from first document's metadata if available
            if documents and documents[0].get("metadata"):
                result["crawl"]["crawl_type"] = documents[0]["metadata"].get("crawl_type", "unknown")

            safe_logfire_info(
                f"Crawling completed | url={url} | pages={len(documents)} | "
                f"type={result['crawl']['crawl_type']}"
            )

            if progress_callback:
                await self._safe_callback(
                    progress_callback,
                    "crawling",
                    50,
                    {"pages_crawled": len(documents)}
                )

            # Check if we got any documents
            if not documents:
                error_msg = "No documents were crawled from the URL"
                safe_logfire_error(f"Ingestion failed | url={url} | error={error_msg}")
                result["error"] = error_msg
                return result

            # Stage 2: Validation
            if progress_callback:
                await self._safe_callback(
                    progress_callback,
                    "validating",
                    60,
                    {"documents": len(documents)}
                )

            # Validate document format (critical for compatibility)
            # This will raise ValueError if format is invalid
            self._validate_crawl_output(documents)

            safe_logfire_info(f"Document validation passed | documents={len(documents)}")

            # Stage 3: Storage
            if progress_callback:
                await self._safe_callback(
                    progress_callback,
                    "storing",
                    70,
                    {"documents": len(documents)}
                )

            storage_result = await self.vectordb.store_documents(
                documents=documents,
                source_id=source_id,
                chunk_size=chunk_size
            )

            result["storage"] = storage_result

            safe_logfire_info(
                f"Storage completed | url={url} | chunks_stored={storage_result['chunks_stored']} | "
                f"failed={storage_result['failed_chunks']}"
            )

            # Stage 4: Completion
            if progress_callback:
                await self._safe_callback(
                    progress_callback,
                    "completed",
                    100,
                    {
                        "total_pages": len(documents),
                        "chunks_stored": storage_result["chunks_stored"],
                        "failed_chunks": storage_result["failed_chunks"]
                    }
                )

            # Determine overall success
            result["success"] = storage_result["chunks_stored"] > 0

            if not result["success"]:
                result["error"] = "No chunks were successfully stored"

            safe_logfire_info(
                f"Ingestion completed | url={url} | success={result['success']} | "
                f"pages={len(documents)} | chunks={storage_result['chunks_stored']}"
            )

            return result

        except ValueError as e:
            # Validation errors - likely format mismatch
            error_msg = f"Validation error: {str(e)}"
            safe_logfire_error(f"Ingestion failed | url={url} | error={error_msg}")
            logger.error(error_msg, exc_info=True)
            result["error"] = error_msg
            return result

        except Exception as e:
            # Unexpected errors - fail with detailed information
            error_msg = f"Ingestion failed: {str(e)}"
            safe_logfire_error(f"Ingestion failed | url={url} | error={error_msg}")
            logger.error(error_msg, exc_info=True)
            result["error"] = error_msg

            # If this is a critical initialization error, re-raise
            if "initialization" in str(e).lower() or "connection" in str(e).lower():
                raise RuntimeError(error_msg) from e

            return result

    async def search(
        self,
        query: str,
        limit: int = 5,
        source_id: str | None = None
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant content.

        Args:
            query: Search query text
            limit: Maximum number of results to return (default: 5)
            source_id: Optional filter by source_id (search only in specific source)

        Returns:
            List of search results with scores and metadata:
            [
                {
                    "id": str,
                    "score": float,
                    "url": str,
                    "title": str,
                    "content": str,
                    "chunk_number": int,
                    "metadata": dict
                }
            ]

        Raises:
            ValueError: If query is empty
            RuntimeError: If search fails

        Example:
            ```python
            results = await service.search(
                query="authentication methods",
                limit=10,
                source_id="example_docs"
            )

            for result in results:
                print(f"Score: {result['score']:.2f}")
                print(f"Title: {result['title']}")
                print(f"URL: {result['url']}")
                print(f"Content: {result['content'][:200]}...")
            ```
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        safe_logfire_info(
            f"Searching knowledge base | query='{query[:50]}...' | limit={limit} | "
            f"source_id={source_id or 'all'}"
        )

        try:
            results = await self.vectordb.search(
                query=query,
                limit=limit,
                source_id=source_id
            )

            safe_logfire_info(f"Search completed | results={len(results)}")
            return results

        except Exception as e:
            error_msg = f"Search failed: {str(e)}"
            safe_logfire_error(error_msg)
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e

    async def delete_source(self, source_id: str) -> int:
        """
        Delete all documents for a given source.

        Args:
            source_id: Source ID to delete

        Returns:
            Number of vectors deleted

        Raises:
            RuntimeError: If deletion fails

        Example:
            ```python
            deleted_count = await service.delete_source("old_docs")
            print(f"Deleted {deleted_count} vectors")
            ```
        """
        safe_logfire_info(f"Deleting source | source_id={source_id}")

        try:
            deleted_count = await self.vectordb.delete_by_source(source_id)
            safe_logfire_info(f"Source deleted | source_id={source_id} | deleted={deleted_count}")
            return deleted_count

        except Exception as e:
            error_msg = f"Failed to delete source {source_id}: {str(e)}"
            safe_logfire_error(error_msg)
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base.

        Returns:
            Dictionary with collection statistics including vector count,
            collection name, and status.

        Example:
            ```python
            stats = await service.get_stats()
            print(f"Collection: {stats['name']}")
            print(f"Vectors: {stats.get('vectors_count', 0)}")
            print(f"Status: {stats['status']}")
            ```
        """
        try:
            stats = await self.vectordb.get_stats()
            safe_logfire_info(f"Retrieved collection stats | vectors={stats.get('vectors_count', 0)}")
            return stats

        except Exception as e:
            logger.error(f"Failed to get stats: {e}", exc_info=True)
            return {
                "error": str(e),
                "status": "error"
            }

    async def close(self) -> None:
        """
        Close all connections and clean up resources.

        This should be called when the service is no longer needed to properly
        release browser resources, database connections, and other resources.

        Example:
            ```python
            service = CrawlAndStoreService()
            try:
                await service.ingest_url("https://example.com", "example")
            finally:
                await service.close()
            ```
        """
        try:
            await self.crawler.close()
            await self.vectordb.close()
            safe_logfire_info("CrawlAndStoreService closed successfully")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}", exc_info=True)

    async def __aenter__(self):
        """Context manager entry - service is ready to use."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup."""
        await self.close()

    # Private helper methods

    def _generate_source_id(self, url: str) -> str:
        """
        Generate a source_id from a URL.

        Args:
            url: URL to generate source_id from

        Returns:
            Generated source_id (domain-based)

        Example:
            https://docs.python.org/3/library -> python_org
        """
        from urllib.parse import urlparse

        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path.split('/')[0]

            # Clean up domain name
            domain = domain.replace('www.', '')
            domain = domain.replace('.', '_')
            domain = domain.replace('-', '_')

            # Remove common TLDs for cleaner names
            for tld in ['.com', '.org', '.net', '.io', '.dev']:
                domain = domain.replace(tld.replace('.', '_'), '')

            source_id = domain.lower() or "unknown_source"
            safe_logfire_info(f"Generated source_id | url={url} | source_id={source_id}")
            return source_id

        except Exception as e:
            logger.warning(f"Failed to generate source_id from URL: {e}")
            return "unknown_source"

    def _validate_crawl_output(self, documents: List[Dict[str, Any]]) -> None:
        """
        Validate that crawled documents match expected format.

        This is a critical compatibility check to ensure SimpleCrawlingService
        output is compatible with SimpleVectorDBService input.

        Args:
            documents: List of documents from crawler

        Raises:
            ValueError: If document format is invalid or incompatible

        Note:
            This delegates to SimpleVectorDBService's validation logic
            to ensure consistency.
        """
        try:
            # Use SimpleVectorDBService's validation (ensures consistency)
            self.vectordb._validate_document_format(documents)

        except ValueError as e:
            error_msg = (
                f"Document format validation failed: {str(e)}. "
                f"SimpleCrawlingService output may be incompatible with SimpleVectorDBService. "
                f"Expected format: {{url: str, title: str, content: str, metadata: dict}}"
            )
            raise ValueError(error_msg) from e

    async def _safe_callback(
        self,
        callback: Callable[[str, int, Dict[str, Any]], None],
        stage: str,
        percentage: int,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Safely invoke progress callback with error handling.

        Args:
            callback: Progress callback function
            stage: Current stage name
            percentage: Progress percentage (0-100)
            metadata: Additional metadata about current stage

        Note:
            Callback errors are logged but don't stop the pipeline.
        """
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(stage, percentage, metadata)
            else:
                callback(stage, percentage, metadata)
        except Exception as e:
            logger.warning(
                f"Progress callback error | stage={stage} | error={e}",
                exc_info=True
            )


# Convenience function for simple usage
async def ingest_url(
    url: str,
    source_id: str | None = None,
    max_depth: int = 2,
    qdrant_url: str = "http://localhost:6333",
    collection_name: str = "archon_knowledge_base"
) -> Dict[str, Any]:
    """
    Convenience function for one-off URL ingestion without managing service lifecycle.

    This function automatically handles initialization and cleanup, making it ideal
    for simple ingestion tasks or scripts.

    Args:
        url: The URL to crawl and ingest
        source_id: Optional source identifier (auto-generated if not provided)
        max_depth: Maximum crawl depth (default: 2)
        qdrant_url: Qdrant server URL
        collection_name: Collection name for storage

    Returns:
        Ingestion result dictionary with success status and stats

    Example:
        ```python
        from server.services.storage.crawl_and_store_service import ingest_url

        # Simple one-liner ingestion
        result = await ingest_url(
            "https://docs.python.org",
            source_id="python_docs",
            max_depth=3
        )

        if result["success"]:
            print(f"Success! Stored {result['storage']['chunks_stored']} chunks")
        ```
    """
    async with CrawlAndStoreService(
        qdrant_url=qdrant_url,
        collection_name=collection_name
    ) as service:
        return await service.ingest_url(
            url=url,
            source_id=source_id,
            max_depth=max_depth
        )
