"""
URL Type Handler

Detects URL types and performs appropriate crawling strategy.
"""

from typing import Any, Callable, Awaitable, Optional

from ....config.logfire_config import get_logger
from ..helpers.url_handler import URLHandler

logger = get_logger(__name__)


class UrlTypeHandler:
    """Handles URL type detection and appropriate crawling."""

    def __init__(
        self,
        url_handler: URLHandler,
        crawl_markdown_file: Callable,
        parse_sitemap: Callable,
        crawl_batch_with_progress: Callable,
        crawl_recursive_with_progress: Callable,
        is_self_link_checker: Callable[[str, str], bool],
    ):
        """
        Initialize the URL type handler.

        Args:
            url_handler: URL handler instance
            crawl_markdown_file: Function to crawl markdown files
            parse_sitemap: Function to parse sitemaps
            crawl_batch_with_progress: Function for batch crawling
            crawl_recursive_with_progress: Function for recursive crawling
            is_self_link_checker: Function to check if link is self-referential
        """
        self.url_handler = url_handler
        self.crawl_markdown_file = crawl_markdown_file
        self.parse_sitemap = parse_sitemap
        self.crawl_batch_with_progress = crawl_batch_with_progress
        self.crawl_recursive_with_progress = crawl_recursive_with_progress
        self.is_self_link_checker = is_self_link_checker

    async def crawl_by_type(
        self,
        url: str,
        request: dict[str, Any],
        progress_callback: Optional[Callable] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        """
        Detect URL type and perform appropriate crawling.

        Args:
            url: URL to crawl
            request: Crawl request parameters
            progress_callback: Optional progress callback

        Returns:
            Tuple of (crawl_results, crawl_type)
        """
        if self.url_handler.is_txt(url) or self.url_handler.is_markdown(url):
            return await self._handle_text_file(url, request, progress_callback)

        elif self.url_handler.is_sitemap(url):
            return await self._handle_sitemap(url, progress_callback)

        else:
            return await self._handle_regular_webpage(url, request, progress_callback)

    async def _handle_text_file(
        self,
        url: str,
        request: dict[str, Any],
        progress_callback: Optional[Callable],
    ) -> tuple[list[dict[str, Any]], str]:
        """Handle text file crawling."""
        crawl_type = "llms-txt" if "llms" in url.lower() else "text_file"

        crawl_results = await self.crawl_markdown_file(url, progress_callback)

        # Check if this is a link collection file
        if crawl_results and len(crawl_results) > 0:
            content = crawl_results[0].get("markdown", "")
            if self.url_handler.is_link_collection_file(url, content):
                return await self._process_link_collection(
                    url, content, crawl_results, request, progress_callback
                )

        logger.info(f"Text file crawling completed: {len(crawl_results)} results")
        return crawl_results, crawl_type

    async def _process_link_collection(
        self,
        url: str,
        content: str,
        original_results: list[dict[str, Any]],
        request: dict[str, Any],
        progress_callback: Optional[Callable],
    ) -> tuple[list[dict[str, Any]], str]:
        """Process a link collection file by extracting and crawling links."""
        # Extract links with text
        extracted_links_with_text = self.url_handler.extract_markdown_links_with_text(
            content, url
        )

        # Filter self-referential links
        extracted_links_with_text = self._filter_self_links(
            extracted_links_with_text, url
        )

        # Filter binary files
        extracted_links_with_text = self._filter_binary_files(extracted_links_with_text)

        if not extracted_links_with_text:
            logger.info(f"No valid links found in link collection file: {url}")
            return original_results, "text_file"

        # Build URL to link text mapping
        url_to_link_text = {link: text for link, text in extracted_links_with_text}
        extracted_links = [link for link, _ in extracted_links_with_text]

        # Crawl extracted links
        logger.info(f"Crawling {len(extracted_links)} extracted links from {url}")
        batch_results = await self.crawl_batch_with_progress(
            extracted_links,
            request.get("max_concurrent"),
            progress_callback,
            url_to_link_text,
        )

        # Combine results
        combined_results = original_results + batch_results
        logger.info(
            f"Link collection crawling completed: {len(combined_results)} total results "
            f"(1 text file + {len(batch_results)} extracted links)"
        )

        return combined_results, "link_collection_with_crawled_links"

    async def _handle_sitemap(
        self, url: str, progress_callback: Optional[Callable]
    ) -> tuple[list[dict[str, Any]], str]:
        """Handle sitemap crawling."""
        sitemap_urls = self.parse_sitemap(url)

        if not sitemap_urls:
            return [], "sitemap"

        crawl_results = await self.crawl_batch_with_progress(
            sitemap_urls, None, progress_callback, None
        )

        return crawl_results, "sitemap"

    async def _handle_regular_webpage(
        self,
        url: str,
        request: dict[str, Any],
        progress_callback: Optional[Callable],
    ) -> tuple[list[dict[str, Any]], str]:
        """Handle regular webpage with recursive crawling."""
        max_depth = request.get("max_depth", 1)

        crawl_results = await self.crawl_recursive_with_progress(
            [url], max_depth, None, progress_callback
        )

        return crawl_results, "normal"

    def _filter_self_links(
        self, links_with_text: list[tuple[str, str]], base_url: str
    ) -> list[tuple[str, str]]:
        """Filter out self-referential links."""
        if not links_with_text:
            return links_with_text

        original_count = len(links_with_text)
        filtered = [
            (link, text)
            for link, text in links_with_text
            if not self.is_self_link_checker(link, base_url)
        ]

        filtered_count = original_count - len(filtered)
        if filtered_count > 0:
            logger.info(
                f"Filtered out {filtered_count} self-referential links "
                f"from {original_count} extracted links"
            )

        return filtered

    def _filter_binary_files(
        self, links_with_text: list[tuple[str, str]]
    ) -> list[tuple[str, str]]:
        """Filter out binary files (PDFs, images, archives)."""
        if not links_with_text:
            return links_with_text

        original_count = len(links_with_text)
        filtered = [
            (link, text)
            for link, text in links_with_text
            if not self.url_handler.is_binary_file(link)
        ]

        filtered_count = original_count - len(filtered)
        if filtered_count > 0:
            logger.info(
                f"Filtered out {filtered_count} binary files "
                f"from {original_count} extracted links"
            )

        return filtered
