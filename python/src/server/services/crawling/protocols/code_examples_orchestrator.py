"""Code examples orchestrator protocol."""

from collections.abc import Awaitable, Callable
from typing import Any, Protocol


class ICodeExamplesOrchestrator(Protocol):
    """Interface for code examples extraction operations."""

    async def extract_code_examples(
        self,
        request: dict[str, Any],
        crawl_results: list[dict[str, Any]],
        url_to_full_document: dict[str, str],
        source_id: str,
        progress_callback: Callable[[str, int, str], Awaitable[None]] | None,
        total_pages: int,
    ) -> int:
        """
        Extract code examples from crawled content.

        Args:
            request: Original crawl request
            crawl_results: List of crawled page results
            url_to_full_document: Mapping of URLs to full documents
            source_id: Source identifier
            progress_callback: Optional progress callback
            total_pages: Total number of pages

        Returns:
            Number of code examples extracted
        """
        ...
