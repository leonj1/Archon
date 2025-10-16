"""Fake code examples orchestrator for testing."""

from typing import Any, Callable, Awaitable


class FakeCodeExamplesOrchestrator:
    """
    Fake code examples orchestrator for testing.

    Allows configurable code count and tracks method calls.
    """

    def __init__(self):
        """Initialize fake code orchestrator."""
        self.extract_calls: list[dict[str, Any]] = []
        self._code_count = 5
        self._should_fail = False
        self._failure_error: Exception | None = None

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
        Record extraction call and return configured code count.

        Args:
            request: Crawl request
            crawl_results: Crawled pages
            url_to_full_document: URL to document mapping
            source_id: Source identifier
            progress_callback: Progress callback
            total_pages: Total pages

        Returns:
            Configured code examples count
        """
        self.extract_calls.append({
            "request": request,
            "crawl_results": crawl_results,
            "url_to_full_document": url_to_full_document,
            "source_id": source_id,
            "total_pages": total_pages,
        })

        if self._should_fail:
            raise self._failure_error or ValueError("Configured to fail")

        return self._code_count

    def set_code_count(self, count: int) -> None:
        """Configure the code count to return."""
        self._code_count = count

    def configure_failure(self, error: Exception) -> None:
        """Configure the orchestrator to fail with given error."""
        self._should_fail = True
        self._failure_error = error

    def reset(self) -> None:
        """Clear all recorded calls and reset configuration."""
        self.extract_calls.clear()
        self._should_fail = False
        self._failure_error = None
        self._code_count = 5
