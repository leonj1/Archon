"""Document processing orchestrator protocol."""

from collections.abc import Callable
from typing import Any, Protocol


class IDocumentProcessingOrchestrator(Protocol):
    """Interface for document processing operations."""

    async def process_and_store(
        self,
        crawl_results: list[dict[str, Any]],
        request: dict[str, Any],
        crawl_type: str,
        original_source_id: str,
        cancellation_check: Callable[[], None],
        url: str,
        source_display_name: str,
    ) -> dict[str, Any]:
        """
        Process crawled documents and store them.

        Args:
            crawl_results: List of crawled page results
            request: Original crawl request
            crawl_type: Type of crawl performed
            original_source_id: Generated source identifier
            cancellation_check: Function to check for cancellation
            url: Source URL
            source_display_name: Display name for source

        Returns:
            Dictionary containing storage results with keys:
            - source_id: Final source ID
            - chunks_stored: Number of chunks stored
            - url_to_full_document: Mapping of URLs to full documents
        """
        ...
