"""
Protocols for Storage Operations

Defines interfaces for document and page storage operations.
"""

from collections.abc import Callable
from typing import Any, Protocol


class IDocumentStorageOperations(Protocol):
    """Protocol for document storage operations."""

    async def process_and_store_documents(
        self,
        crawl_results: list[dict],
        request: dict[str, Any],
        crawl_type: str,
        original_source_id: str,
        progress_callback: Callable | None = None,
        cancellation_check: Callable | None = None,
        source_url: str | None = None,
        source_display_name: str | None = None,
        url_to_page_id: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Process crawled documents and store them in the database.

        Args:
            crawl_results: List of crawled documents
            request: The original crawl request
            crawl_type: Type of crawl performed
            original_source_id: The source ID for all documents
            progress_callback: Optional callback for progress updates
            cancellation_check: Optional function to check for cancellation
            source_url: Optional original URL that was crawled
            source_display_name: Optional human-readable name for the source
            url_to_page_id: Optional mapping of URLs to page IDs

        Returns:
            Dict containing storage statistics and document mappings
        """
        ...

    async def extract_and_store_code_examples(
        self,
        crawl_results: list[dict],
        url_to_full_document: dict[str, str],
        source_id: str,
        progress_callback: Callable | None = None,
        cancellation_check: Callable[[], None] | None = None,
        provider: str | None = None,
        embedding_provider: str | None = None,
    ) -> int:
        """
        Extract code examples from crawled documents and store them.

        Args:
            crawl_results: List of crawled documents
            url_to_full_document: Mapping of URLs to full document content
            source_id: The unique source_id for all documents
            progress_callback: Optional callback for progress updates
            cancellation_check: Optional function to check for cancellation
            provider: Optional LLM provider to use for code summaries
            embedding_provider: Optional embedding provider override

        Returns:
            Number of code examples stored
        """
        ...


class IPageStorageOperations(Protocol):
    """Protocol for page storage operations."""

    async def store_pages(
        self,
        crawl_results: list[dict],
        source_id: str,
        request: dict[str, Any],
        crawl_type: str,
    ) -> dict[str, str]:
        """
        Store pages in the database.

        Args:
            crawl_results: List of crawled documents
            source_id: Source identifier
            request: Original crawl request
            crawl_type: Type of crawl performed

        Returns:
            Mapping of URLs to page IDs
        """
        ...

    async def store_llms_full_sections(
        self,
        base_url: str,
        content: str,
        source_id: str,
        request: dict[str, Any],
        crawl_type: str = "llms_full",
    ) -> dict[str, str]:
        """
        Store sections from llms-full.txt file as separate pages.

        Args:
            base_url: Base URL of the llms-full.txt file
            content: Full content of the file
            source_id: Source identifier
            request: Original crawl request
            crawl_type: Type of crawl (default: "llms_full")

        Returns:
            Mapping of section URLs to page IDs
        """
        ...
