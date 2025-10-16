"""
Fake implementations of storage operation protocols for testing.
"""

from collections.abc import Callable
from typing import Any


class FakeDocumentStorageOperations:
    """Fake document storage operations for testing."""

    def __init__(self):
        """Initialize fake document storage operations."""
        self._process_result: dict[str, Any] = {
            'chunk_count': 0,
            'chunks_stored': 0,
            'total_word_count': 0,
            'url_to_full_document': {},
            'source_id': 'test-source-id',
        }
        self._code_examples_count: int = 0
        self.process_and_store_documents_calls: list[dict[str, Any]] = []
        self.extract_and_store_code_examples_calls: list[dict[str, Any]] = []

    def configure_process_result(self, result: dict[str, Any]):
        """Configure result to return from process_and_store_documents."""
        self._process_result = result

    def configure_code_examples_count(self, count: int):
        """Configure code examples count to return."""
        self._code_examples_count = count

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
        """Process and store documents."""
        self.process_and_store_documents_calls.append({
            "crawl_results_count": len(crawl_results),
            "crawl_type": crawl_type,
            "original_source_id": original_source_id,
            "has_progress_callback": progress_callback is not None,
            "has_cancellation_check": cancellation_check is not None,
            "source_url": source_url,
            "source_display_name": source_display_name,
            "has_url_to_page_id": url_to_page_id is not None,
        })

        # Call progress callback if provided
        if progress_callback:
            await progress_callback("processing", 75, f"Storing {len(crawl_results)} documents")

        # Check cancellation if provided
        if cancellation_check:
            cancellation_check()

        return self._process_result

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
        """Extract and store code examples."""
        self.extract_and_store_code_examples_calls.append({
            "crawl_results_count": len(crawl_results),
            "url_to_full_document_count": len(url_to_full_document),
            "source_id": source_id,
            "has_progress_callback": progress_callback is not None,
            "has_cancellation_check": cancellation_check is not None,
            "provider": provider,
            "embedding_provider": embedding_provider,
        })

        # Call progress callback if provided
        if progress_callback:
            await progress_callback("extracting_code", 90, "Extracting code examples")

        # Check cancellation if provided
        if cancellation_check:
            cancellation_check()

        return self._code_examples_count

    def reset_tracking(self):
        """Reset call tracking."""
        self.process_and_store_documents_calls = []
        self.extract_and_store_code_examples_calls = []


class FakePageStorageOperations:
    """Fake page storage operations for testing."""

    def __init__(self):
        """Initialize fake page storage operations."""
        self._url_to_page_id: dict[str, str] = {}
        self.store_pages_calls: list[dict[str, Any]] = []
        self.store_llms_full_sections_calls: list[dict[str, Any]] = []

    def configure_url_to_page_id(self, url_to_page_id: dict[str, str]):
        """Configure URL to page ID mapping."""
        self._url_to_page_id = url_to_page_id

    async def store_pages(
        self,
        crawl_results: list[dict],
        source_id: str,
        request: dict[str, Any],
        crawl_type: str,
    ) -> dict[str, str]:
        """Store pages."""
        self.store_pages_calls.append({
            "crawl_results_count": len(crawl_results),
            "source_id": source_id,
            "crawl_type": crawl_type,
        })
        return self._url_to_page_id

    async def store_llms_full_sections(
        self,
        base_url: str,
        content: str,
        source_id: str,
        request: dict[str, Any],
        crawl_type: str = "llms_full",
    ) -> dict[str, str]:
        """Store LLMS full sections."""
        self.store_llms_full_sections_calls.append({
            "base_url": base_url,
            "content_length": len(content),
            "source_id": source_id,
            "crawl_type": crawl_type,
        })
        return self._url_to_page_id

    def reset_tracking(self):
        """Reset call tracking."""
        self.store_pages_calls = []
        self.store_llms_full_sections_calls = []
