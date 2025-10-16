"""
Fake implementations of crawl strategy protocols for testing.
"""

from collections.abc import Awaitable, Callable
from typing import Any


class FakeBatchCrawlStrategy:
    """Fake batch crawl strategy for testing."""

    def __init__(self):
        """Initialize fake batch crawl strategy."""
        self._results: list[dict[str, Any]] = []
        self.crawl_batch_with_progress_calls: list[dict[str, Any]] = []

    def configure_results(self, results: list[dict[str, Any]]):
        """Configure crawl results to return."""
        self._results = results

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
        """Crawl batch with progress."""
        self.crawl_batch_with_progress_calls.append({
            "urls": urls,
            "max_concurrent": max_concurrent,
            "has_progress_callback": progress_callback is not None,
            "has_cancellation_check": cancellation_check is not None,
            "link_text_fallbacks": link_text_fallbacks,
        })

        # Call progress callback if provided
        if progress_callback:
            await progress_callback("crawling", 50, f"Processing {len(urls)} URLs")

        # Check cancellation if provided
        if cancellation_check:
            cancellation_check()

        return self._results

    def reset_tracking(self):
        """Reset call tracking."""
        self.crawl_batch_with_progress_calls = []


class FakeRecursiveCrawlStrategy:
    """Fake recursive crawl strategy for testing."""

    def __init__(self):
        """Initialize fake recursive crawl strategy."""
        self._results: list[dict[str, Any]] = []
        self.crawl_recursive_with_progress_calls: list[dict[str, Any]] = []

    def configure_results(self, results: list[dict[str, Any]]):
        """Configure crawl results to return."""
        self._results = results

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
        """Crawl recursively with progress."""
        self.crawl_recursive_with_progress_calls.append({
            "start_urls": start_urls,
            "max_depth": max_depth,
            "max_concurrent": max_concurrent,
            "has_progress_callback": progress_callback is not None,
            "has_cancellation_check": cancellation_check is not None,
        })

        # Call progress callback if provided
        if progress_callback:
            await progress_callback("crawling", 50, f"Recursively crawling from {len(start_urls)} URLs")

        # Check cancellation if provided
        if cancellation_check:
            cancellation_check()

        return self._results

    def reset_tracking(self):
        """Reset call tracking."""
        self.crawl_recursive_with_progress_calls = []


class FakeSinglePageCrawlStrategy:
    """Fake single page crawl strategy for testing."""

    def __init__(self):
        """Initialize fake single page crawl strategy."""
        self._single_page_result: dict[str, Any] = {}
        self._markdown_file_results: list[dict[str, Any]] = []
        self.crawl_single_page_calls: list[dict[str, Any]] = []
        self.crawl_markdown_file_calls: list[dict[str, Any]] = []

    def configure_single_page_result(self, result: dict[str, Any]):
        """Configure single page crawl result."""
        self._single_page_result = result

    def configure_markdown_file_results(self, results: list[dict[str, Any]]):
        """Configure markdown file crawl results."""
        self._markdown_file_results = results

    async def crawl_single_page(
        self,
        url: str,
        transform_url_func: Callable[[str], str],
        is_documentation_site_func: Callable[[str], bool],
        retry_count: int = 3,
    ) -> dict[str, Any]:
        """Crawl a single page."""
        self.crawl_single_page_calls.append({
            "url": url,
            "retry_count": retry_count,
        })
        return self._single_page_result

    async def crawl_markdown_file(
        self,
        url: str,
        transform_url_func: Callable[[str], str],
        progress_callback: Callable[[str, int, str], Awaitable[None]] | None = None,
    ) -> list[dict[str, Any]]:
        """Crawl a markdown file."""
        self.crawl_markdown_file_calls.append({
            "url": url,
            "has_progress_callback": progress_callback is not None,
        })

        # Call progress callback if provided
        if progress_callback:
            await progress_callback("processing", 50, "Processing markdown file")

        return self._markdown_file_results

    def reset_tracking(self):
        """Reset call tracking."""
        self.crawl_single_page_calls = []
        self.crawl_markdown_file_calls = []


class FakeSitemapCrawlStrategy:
    """Fake sitemap crawl strategy for testing."""

    def __init__(self):
        """Initialize fake sitemap crawl strategy."""
        self._urls: list[str] = []
        self.parse_sitemap_calls: list[dict[str, Any]] = []

    def configure_urls(self, urls: list[str]):
        """Configure URLs to return from sitemap."""
        self._urls = urls

    def parse_sitemap(
        self,
        sitemap_url: str,
        cancellation_check: Callable[[], None] | None = None,
    ) -> list[str]:
        """Parse sitemap."""
        self.parse_sitemap_calls.append({
            "sitemap_url": sitemap_url,
            "has_cancellation_check": cancellation_check is not None,
        })

        # Check cancellation if provided
        if cancellation_check:
            cancellation_check()

        return self._urls

    def reset_tracking(self):
        """Reset call tracking."""
        self.parse_sitemap_calls = []
