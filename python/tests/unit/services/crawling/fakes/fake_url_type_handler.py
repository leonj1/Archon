"""Fake URL type handler for testing."""

from typing import Any, Callable, Awaitable


class FakeUrlTypeHandler:
    """
    Fake URL type handler for testing.

    Allows configurable crawl results and type detection.
    """

    def __init__(self):
        """Initialize fake URL type handler."""
        self.crawl_calls: list[dict[str, Any]] = []
        self._crawl_results: list[dict[str, Any]] = [
            {"url": "https://example.com", "markdown": "# Test Content"}
        ]
        self._crawl_type = "single_page"
        self._should_fail = False
        self._failure_error: Exception | None = None

    async def crawl_by_type(
        self,
        url: str,
        request: dict[str, Any],
        progress_callback: Callable[[str, int, str], Awaitable[None]] | None = None,
    ) -> tuple[list[dict[str, Any]], str]:
        """
        Record crawl call and return configured results.

        Args:
            url: URL to crawl
            request: Crawl request
            progress_callback: Progress callback

        Returns:
            Tuple of (crawl_results, crawl_type)
        """
        self.crawl_calls.append({
            "url": url,
            "request": request,
            "has_callback": progress_callback is not None,
        })

        if self._should_fail:
            raise self._failure_error or ValueError("Configured to fail")

        return self._crawl_results.copy(), self._crawl_type

    def set_results(
        self,
        crawl_results: list[dict[str, Any]],
        crawl_type: str = "single_page",
    ) -> None:
        """Configure the results to return."""
        self._crawl_results = crawl_results
        self._crawl_type = crawl_type

    def configure_failure(self, error: Exception) -> None:
        """Configure the handler to fail with given error."""
        self._should_fail = True
        self._failure_error = error

    def reset(self) -> None:
        """Clear all recorded calls and reset configuration."""
        self.crawl_calls.clear()
        self._should_fail = False
        self._failure_error = None
        self._crawl_results = [
            {"url": "https://example.com", "markdown": "# Test Content"}
        ]
        self._crawl_type = "single_page"
