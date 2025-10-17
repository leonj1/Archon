"""URL type handler protocol for crawling different URL types."""

from collections.abc import Awaitable, Callable
from typing import Any, Protocol


class IUrlTypeHandler(Protocol):
    """Interface for handling different URL types during crawling."""

    async def crawl_by_type(
        self,
        url: str,
        request: dict[str, Any],
        progress_callback: Callable[..., Any] | None = None,
    ) -> tuple[list[dict[str, Any]], str | None]:
        """
        Crawl URL based on its detected type.

        Args:
            url: The URL to crawl
            request: Crawl request containing configuration
            progress_callback: Optional progress callback

        Returns:
            Tuple of (crawl_results, crawl_type) where:
            - crawl_results: List of crawled page dictionaries
            - crawl_type: Type of crawl performed (e.g., 'single_page', 'recursive'), or None
        """
        ...
