"""
Code Examples Orchestrator

Coordinates code example extraction with progress tracking and error handling.
"""

from collections.abc import Awaitable, Callable
from typing import Any

from ....config.logfire_config import get_logger, safe_logfire_error
from ...credential_service import credential_service
from ..document_storage_operations import DocumentStorageOperations

logger = get_logger(__name__)


class CodeExamplesOrchestrator:
    """Orchestrates code example extraction with progress tracking."""

    def __init__(
        self,
        doc_storage_ops: DocumentStorageOperations,
        progress_mapper,
        cancellation_check: Callable[[], None],
    ):
        """
        Initialize the code examples orchestrator.

        Args:
            doc_storage_ops: Document storage operations instance
            progress_mapper: Progress mapper for tracking
            cancellation_check: Function to check if operation is cancelled
        """
        self.doc_storage_ops = doc_storage_ops
        self.progress_mapper = progress_mapper
        self.cancellation_check = cancellation_check

    async def extract_code_examples(
        self,
        request: dict[str, Any],
        crawl_results: list[dict[str, Any]],
        url_to_full_document: dict[str, str],
        source_id: str,
        progress_callback: Callable[..., Awaitable[None]] | None,
        total_pages: int,
    ) -> int:
        """
        Extract and store code examples with progress tracking.

        Args:
            request: Original crawl request
            crawl_results: Crawled pages data
            url_to_full_document: Mapping of URLs to full document text
            source_id: Source ID for storage
            progress_callback: Callback for progress updates
            total_pages: Total number of pages for context

        Returns:
            Number of code examples extracted
        """
        if not request.get("extract_code_examples", True):
            return 0

        # Check for cancellation before starting
        self.cancellation_check()

        # Get provider configuration
        provider = await self._get_llm_provider(request)
        embedding_provider = await self._get_embedding_provider()

        try:
            # Create wrapped progress callback
            wrapped_callback = self._create_progress_callback(
                progress_callback, total_pages
            )

            code_examples_count = await self.doc_storage_ops.extract_and_store_code_examples(
                crawl_results,
                url_to_full_document,
                source_id,
                wrapped_callback,
                self.cancellation_check,
                provider,
                embedding_provider,
            )

            return code_examples_count

        except RuntimeError as e:
            logger.error(
                "Code extraction failed, continuing crawl without code examples",
                exc_info=True,
            )
            safe_logfire_error(f"Code extraction failed | error={e}")

            # Report failure to progress tracker
            if progress_callback:
                await progress_callback(
                    "code_extraction",
                    self.progress_mapper.map_progress("code_extraction", 100),
                    f"Code extraction failed: {str(e)}. Continuing crawl without code examples.",
                    total_pages=total_pages,
                )

            return 0

    async def _get_llm_provider(self, request: dict[str, Any]) -> str:
        """Get LLM provider from request or credential service."""
        provider = request.get("provider")

        if not provider:
            try:
                provider_config = await credential_service.get_active_provider("llm")
                provider = provider_config.get("provider", "openai")
            except Exception as e:
                logger.warning(
                    f"Failed to get provider from credential service: {e}, defaulting to openai"
                )
                provider = "openai"

        return provider

    async def _get_embedding_provider(self) -> str | None:
        """Get embedding provider from credential service."""
        try:
            embedding_config = await credential_service.get_active_provider("embedding")
            return embedding_config.get("provider")
        except Exception as e:
            logger.warning(
                f"Failed to get embedding provider from credential service: {e}. "
                f"Using configured default."
            )
            return None

    def _create_progress_callback(
        self,
        progress_callback: Callable[..., Awaitable[None]] | None,
        total_pages: int,
    ) -> Callable[[dict[str, Any]], Awaitable[None]]:
        """
        Create a wrapped progress callback with mapping.

        Args:
            progress_callback: Original progress callback
            total_pages: Total pages for context

        Returns:
            Wrapped progress callback
        """
        async def wrapped_callback(data: dict):
            if progress_callback:
                raw_progress = data.get("progress", data.get("percentage", 0))
                mapped_progress = self.progress_mapper.map_progress(
                    "code_extraction", raw_progress
                )

                # Call with positional arguments matching IProgressTracker.update signature
                await progress_callback(
                    data.get("status", "code_extraction"),  # status
                    mapped_progress,  # progress
                    data.get("log", "Extracting code examples..."),  # log
                    total_pages=total_pages,  # kwargs
                    **{k: v for k, v in data.items() if k not in ["status", "progress", "percentage", "log"]}
                )

        return wrapped_callback
