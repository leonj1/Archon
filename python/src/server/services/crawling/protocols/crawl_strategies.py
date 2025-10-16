"""
Protocols for Crawling Strategy Operations

Defines interfaces for different crawling strategies.
"""

from collections.abc import Awaitable, Callable
from typing import Any, Protocol


class IBatchCrawlStrategy(Protocol):
    """Protocol for batch crawling strategy."""

    async def crawl_batch_with_progress(
        self,
        urls: list[str],
        transform_url_func: Callable[[str], str],
        is_documentation_site_func: Callable[[str], bool],
        max_concurrent: int | None = None,
        progress_callback: Callable[..., Awaitable[None]] | None = None,
        cancellation_check: Callable[[], None] | None = None,
        link_text_fallbacks: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Batch crawl multiple URLs in parallel with progress reporting.

        Args:
            urls: List of URLs to crawl
            transform_url_func: Function to transform URLs
            is_documentation_site_func: Function to check if URL is documentation site
            max_concurrent: Maximum concurrent crawls
            progress_callback: Optional callback for progress updates
            cancellation_check: Optional function to check for cancellation
            link_text_fallbacks: Optional dict mapping URLs to link text

        Returns:
            List of crawl results
        """
        ...


class IRecursiveCrawlStrategy(Protocol):
    """Protocol for recursive crawling strategy."""

    async def crawl_recursive_with_progress(
        self,
        start_urls: list[str],
        transform_url_func: Callable[[str], str],
        is_documentation_site_func: Callable[[str], bool],
        max_depth: int = 3,
        max_concurrent: int | None = None,
        progress_callback: Callable[..., Awaitable[None]] | None = None,
        cancellation_check: Callable[[], None] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Recursively crawl internal links from start URLs.

        Args:
            start_urls: List of starting URLs
            transform_url_func: Function to transform URLs
            is_documentation_site_func: Function to check if URL is documentation site
            max_depth: Maximum depth for recursive crawling
            max_concurrent: Maximum concurrent crawls
            progress_callback: Optional callback for progress updates
            cancellation_check: Optional function to check for cancellation

        Returns:
            List of crawl results
        """
        ...


class ISinglePageCrawlStrategy(Protocol):
    """Protocol for single page crawling strategy."""

    async def crawl_single_page(
        self,
        url: str,
        transform_url_func: Callable[[str], str],
        is_documentation_site_func: Callable[[str], bool],
        retry_count: int = 3,
    ) -> dict[str, Any]:
        """
        Crawl a single web page.

        Args:
            url: URL to crawl
            transform_url_func: Function to transform URLs
            is_documentation_site_func: Function to check if URL is documentation site
            retry_count: Number of retries on failure

        Returns:
            Crawl result dictionary
        """
        ...

    async def crawl_markdown_file(
        self,
        url: str,
        transform_url_func: Callable[[str], str],
        progress_callback: Callable[[str, int, str], Awaitable[None]] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Crawl a .txt or markdown file.

        Args:
            url: URL to crawl
            transform_url_func: Function to transform URLs
            progress_callback: Optional callback for progress updates

        Returns:
            List of crawl results
        """
        ...


class ISitemapCrawlStrategy(Protocol):
    """Protocol for sitemap crawling strategy."""

    def parse_sitemap(
        self,
        sitemap_url: str,
        cancellation_check: Callable[[], None] | None = None,
    ) -> list[str]:
        """
        Parse a sitemap and extract URLs.

        Args:
            sitemap_url: URL of the sitemap
            cancellation_check: Optional function to check for cancellation

        Returns:
            List of URLs from the sitemap
        """
        ...
