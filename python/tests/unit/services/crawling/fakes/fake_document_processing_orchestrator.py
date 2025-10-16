"""Fake document processing orchestrator for testing."""

from typing import Any, Callable


class FakeDocumentProcessingOrchestrator:
    """
    Fake document processing orchestrator for testing.

    Allows configurable results and tracks method calls.
    """

    def __init__(self):
        """Initialize fake document processor."""
        self.process_calls: list[dict[str, Any]] = []
        self._result: dict[str, Any] = {
            "source_id": "fake-source-id",
            "chunks_stored": 10,
            "url_to_full_document": {},
        }
        self._should_fail = False
        self._failure_error: Exception | None = None

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
        Record process call and return configured result.

        Args:
            crawl_results: List of crawled pages
            request: Crawl request
            crawl_type: Type of crawl
            original_source_id: Generated source ID
            cancellation_check: Cancellation check function
            url: Source URL
            source_display_name: Display name

        Returns:
            Configured storage results
        """
        self.process_calls.append({
            "crawl_results": crawl_results,
            "request": request,
            "crawl_type": crawl_type,
            "original_source_id": original_source_id,
            "url": url,
            "source_display_name": source_display_name,
        })

        if self._should_fail:
            raise self._failure_error or ValueError("Configured to fail")

        return self._result.copy()

    def set_result(
        self,
        source_id: str = "fake-source-id",
        chunks_stored: int = 10,
        url_to_full_document: dict[str, str] | None = None,
    ) -> None:
        """Configure the result to return."""
        self._result = {
            "source_id": source_id,
            "chunks_stored": chunks_stored,
            "url_to_full_document": url_to_full_document or {},
        }

    def configure_failure(self, error: Exception) -> None:
        """Configure the processor to fail with given error."""
        self._should_fail = True
        self._failure_error = error

    def reset(self) -> None:
        """Clear all recorded calls and reset configuration."""
        self.process_calls.clear()
        self._should_fail = False
        self._failure_error = None
        self._result = {
            "source_id": "fake-source-id",
            "chunks_stored": 10,
            "url_to_full_document": {},
        }
