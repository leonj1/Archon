"""
SimpleCrawlingService - Lightweight web crawling for vector database integration

This service provides a simplified async interface for web crawling without database storage.
It returns structured document data suitable for direct integration with vector databases.

Key Features:
- Async/await pattern for efficient I/O
- Single page, recursive, and sitemap crawling
- Structured document output (url, title, content, metadata)
- Comprehensive error handling with detailed logging
- Reuses existing crawling helpers and strategies
- No database dependencies - returns raw data

Usage Example:
    ```python
    from server.services.simple_crawling_service import SimpleCrawlingService

    # Initialize service
    service = SimpleCrawlingService()

    # Crawl a single page
    docs = await service.crawl("https://example.com")

    # Crawl with depth
    docs = await service.crawl("https://example.com", max_depth=2)

    # Process results
    for doc in docs:
        print(f"URL: {doc['url']}")
        print(f"Title: {doc['title']}")
        print(f"Content length: {len(doc['content'])}")
        print(f"Metadata: {doc['metadata']}")
    ```
"""

import asyncio
from typing import Any, Dict, List, Optional

from crawl4ai import AsyncWebCrawler

from ..config.logfire_config import get_logger, safe_logfire_error, safe_logfire_info
from .crawling.helpers.site_config import SiteConfig
from .crawling.helpers.url_handler import URLHandler
from .crawling.strategies.batch import BatchCrawlStrategy
from .crawling.strategies.recursive import RecursiveCrawlStrategy
from .crawling.strategies.single_page import SinglePageCrawlStrategy
from .crawling.strategies.sitemap import SitemapCrawlStrategy

logger = get_logger(__name__)


class SimpleCrawlingService:
    """
    Simplified async web crawling service for vector database integration.

    This service provides a clean interface for web crawling that returns structured
    document data without requiring database connectivity. It reuses battle-tested
    crawling strategies from the existing codebase.

    Attributes:
        crawler: AsyncWebCrawler instance for web crawling
        url_handler: Helper for URL transformations and validations
        site_config: Configuration for documentation site detection
        single_page_strategy: Strategy for crawling individual pages
        batch_strategy: Strategy for batch crawling multiple URLs
        recursive_strategy: Strategy for recursive link following
        sitemap_strategy: Strategy for sitemap parsing
    """

    def __init__(self, crawler: Optional[AsyncWebCrawler] = None):
        """
        Initialize the SimpleCrawlingService.

        Args:
            crawler: Optional AsyncWebCrawler instance. If not provided,
                    one will be created automatically when needed.

        Raises:
            ValueError: If crawler initialization fails (fail fast on config errors)
        """
        self.crawler = crawler
        self._crawler_initialized = False

        # Initialize helpers
        self.url_handler = URLHandler()
        self.site_config = SiteConfig()

        # Get markdown generators from site config
        self.markdown_generator = self.site_config.get_markdown_generator()
        self.link_pruning_markdown_generator = self.site_config.get_link_pruning_markdown_generator()

        # Initialize strategies (they'll use the crawler when needed)
        self.single_page_strategy: Optional[SinglePageCrawlStrategy] = None
        self.batch_strategy: Optional[BatchCrawlStrategy] = None
        self.recursive_strategy: Optional[RecursiveCrawlStrategy] = None
        self.sitemap_strategy = SitemapCrawlStrategy()

        safe_logfire_info("SimpleCrawlingService initialized")

    async def _ensure_crawler(self) -> None:
        """
        Ensure crawler is initialized and ready to use.

        Raises:
            RuntimeError: If crawler initialization fails (fail fast)
        """
        if self._crawler_initialized:
            return

        if self.crawler is None:
            try:
                # Initialize crawler following existing patterns
                self.crawler = AsyncWebCrawler(verbose=False)
                await self.crawler.__aenter__()
                safe_logfire_info("AsyncWebCrawler initialized successfully")
            except Exception as e:
                error_msg = f"Failed to initialize AsyncWebCrawler: {str(e)}"
                safe_logfire_error(error_msg)
                logger.error(error_msg, exc_info=True)
                raise RuntimeError(error_msg) from e

        # Initialize strategies with crawler
        self.single_page_strategy = SinglePageCrawlStrategy(
            self.crawler,
            self.markdown_generator
        )
        self.batch_strategy = BatchCrawlStrategy(
            self.crawler,
            self.link_pruning_markdown_generator
        )
        self.recursive_strategy = RecursiveCrawlStrategy(
            self.crawler,
            self.link_pruning_markdown_generator
        )

        self._crawler_initialized = True

    async def crawl(
        self,
        url: str,
        max_depth: int = 1,
        max_concurrent: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Crawl a URL and return structured document data.

        This method automatically detects the URL type (single page, sitemap, text file)
        and applies the appropriate crawling strategy. For regular web pages, it performs
        recursive crawling up to max_depth.

        Args:
            url: The URL to crawl (supports web pages, sitemaps, .txt, .md files)
            max_depth: Maximum depth for recursive crawling (default: 1)
                      - 1: Single page only
                      - 2+: Follow internal links to specified depth
            max_concurrent: Maximum concurrent requests (default: 10)
                           None uses default settings from strategies

        Returns:
            List of document dictionaries with structure:
            [
                {
                    "url": str,           # Original URL of the document
                    "title": str,         # Extracted page title
                    "content": str,       # Markdown-formatted content
                    "metadata": {
                        "content_length": int,  # Length of content in characters
                        "crawl_type": str,      # Type of crawl performed
                        "links": dict,          # Internal/external links found
                        "depth": int            # Crawl depth (0 for single page)
                    }
                }
            ]

        Raises:
            ValueError: If URL is invalid or empty
            RuntimeError: If crawler initialization fails

        Example:
            ```python
            service = SimpleCrawlingService()

            # Single page crawl
            docs = await service.crawl("https://example.com/docs")

            # Deep crawl with 3 levels
            docs = await service.crawl("https://example.com", max_depth=3)

            # Sitemap crawl (auto-detected)
            docs = await service.crawl("https://example.com/sitemap.xml")
            ```
        """
        if not url or not url.strip():
            raise ValueError("URL cannot be empty")

        url = url.strip()
        safe_logfire_info(f"Starting crawl | url={url} | max_depth={max_depth}")

        try:
            # Ensure crawler is initialized
            await self._ensure_crawler()

            # Detect URL type and crawl accordingly
            crawl_results, crawl_type = await self._crawl_by_url_type(
                url,
                max_depth,
                max_concurrent
            )

            # Transform results to simplified document format
            documents = self._transform_to_documents(crawl_results, crawl_type)

            safe_logfire_info(
                f"Crawl completed | url={url} | documents={len(documents)} | type={crawl_type}"
            )

            return documents

        except Exception as e:
            error_msg = f"Crawl failed for {url}: {str(e)}"
            safe_logfire_error(error_msg)
            logger.error(error_msg, exc_info=True)
            raise

    async def _crawl_by_url_type(
        self,
        url: str,
        max_depth: int,
        max_concurrent: Optional[int]
    ) -> tuple[List[Dict[str, Any]], str]:
        """
        Detect URL type and perform appropriate crawling strategy.

        Args:
            url: URL to crawl
            max_depth: Maximum depth for recursive crawling
            max_concurrent: Maximum concurrent requests

        Returns:
            Tuple of (crawl_results, crawl_type)

        Raises:
            ValueError: If no content could be crawled
        """
        crawl_results = []
        crawl_type = "unknown"

        # Check for text/markdown files
        if self.url_handler.is_txt(url) or self.url_handler.is_markdown(url):
            crawl_type = "text_file"
            safe_logfire_info(f"Detected text file | url={url}")

            result = await self.single_page_strategy.crawl_markdown_file(
                url,
                transform_url_func=self.url_handler.transform_github_url,
                progress_callback=None
            )
            crawl_results = result

            # Check if it's a link collection file
            if crawl_results and len(crawl_results) > 0:
                content = crawl_results[0].get('markdown', '')
                if self.url_handler.is_link_collection_file(url, content):
                    # Extract links and crawl them
                    extracted_links = self.url_handler.extract_markdown_links(content, url)

                    if extracted_links:
                        # Filter out self-referential and binary links
                        filtered_links = [
                            link for link in extracted_links
                            if not self._is_self_link(link, url)
                            and not self.url_handler.is_binary_file(link)
                        ]

                        if filtered_links:
                            safe_logfire_info(
                                f"Crawling {len(filtered_links)} links from collection | url={url}"
                            )
                            batch_results = await self.batch_strategy.crawl_batch_with_progress(
                                filtered_links,
                                transform_url_func=self.url_handler.transform_github_url,
                                is_documentation_site_func=self.site_config.is_documentation_site,
                                max_concurrent=max_concurrent,
                                progress_callback=None,
                                cancellation_check=None,
                                link_text_fallbacks=None
                            )
                            crawl_results.extend(batch_results)
                            crawl_type = "link_collection"

        # Check for sitemaps
        elif self.url_handler.is_sitemap(url):
            crawl_type = "sitemap"
            safe_logfire_info(f"Detected sitemap | url={url}")

            sitemap_urls = self.sitemap_strategy.parse_sitemap(url, cancellation_check=None)

            if sitemap_urls:
                safe_logfire_info(f"Crawling {len(sitemap_urls)} URLs from sitemap")
                crawl_results = await self.batch_strategy.crawl_batch_with_progress(
                    sitemap_urls,
                    transform_url_func=self.url_handler.transform_github_url,
                    is_documentation_site_func=self.site_config.is_documentation_site,
                    max_concurrent=max_concurrent,
                    progress_callback=None,
                    cancellation_check=None,
                    link_text_fallbacks=None
                )

        # Regular web page - use recursive crawling
        else:
            if max_depth == 1:
                crawl_type = "single_page"
                safe_logfire_info(f"Crawling single page | url={url}")

                result = await self.single_page_strategy.crawl_single_page(
                    url,
                    transform_url_func=self.url_handler.transform_github_url,
                    is_documentation_site_func=self.site_config.is_documentation_site,
                    retry_count=3
                )

                if result.get("success"):
                    crawl_results = [result]
                else:
                    error_msg = result.get("error", "Unknown error")
                    raise ValueError(f"Failed to crawl single page: {error_msg}")
            else:
                crawl_type = "recursive"
                safe_logfire_info(f"Starting recursive crawl | url={url} | max_depth={max_depth}")

                crawl_results = await self.recursive_strategy.crawl_recursive_with_progress(
                    start_urls=[url],
                    transform_url_func=self.url_handler.transform_github_url,
                    is_documentation_site_func=self.site_config.is_documentation_site,
                    max_depth=max_depth,
                    max_concurrent=max_concurrent,
                    progress_callback=None,
                    cancellation_check=None
                )

        if not crawl_results:
            raise ValueError(f"No content was crawled from {url}")

        return crawl_results, crawl_type

    def _is_self_link(self, link: str, base_url: str) -> bool:
        """
        Check if a link is a self-referential link to the base URL.

        Args:
            link: The link to check
            base_url: The base URL to compare against

        Returns:
            True if the link is self-referential, False otherwise
        """
        try:
            from urllib.parse import urlparse

            def _core(u: str) -> str:
                p = urlparse(u)
                scheme = (p.scheme or "http").lower()
                host = (p.hostname or "").lower()
                port = p.port
                if (scheme == "http" and port in (None, 80)) or (
                    scheme == "https" and port in (None, 443)
                ):
                    port_part = ""
                else:
                    port_part = f":{port}" if port else ""
                path = p.path.rstrip("/")
                return f"{scheme}://{host}{port_part}{path}"

            return _core(link) == _core(base_url)
        except Exception as e:
            logger.warning(f"Error checking if link is self-referential: {e}", exc_info=True)
            return link.rstrip('/') == base_url.rstrip('/')

    def _transform_to_documents(
        self,
        crawl_results: List[Dict[str, Any]],
        crawl_type: str
    ) -> List[Dict[str, Any]]:
        """
        Transform raw crawl results into structured document format.

        This method converts the internal crawl result format into a simplified
        document structure suitable for vector database ingestion.

        Args:
            crawl_results: Raw results from crawling strategies
            crawl_type: Type of crawl that was performed

        Returns:
            List of structured document dictionaries

        Note:
            This method skips failed crawls (success=False) and logs detailed
            error information following the "continue but log detailed failures"
            pattern for batch operations.
        """
        documents = []
        failed_count = 0

        for idx, result in enumerate(crawl_results):
            try:
                # Skip failed crawls but log them
                if not result.get("success", True):
                    failed_count += 1
                    error = result.get("error", "Unknown error")
                    url = result.get("url", "unknown")
                    logger.warning(f"Skipping failed crawl result | url={url} | error={error}")
                    continue

                # Extract required fields
                url = result.get("url", "")
                title = result.get("title", "Untitled")

                # Use markdown as primary content, fallback to html if needed
                content = result.get("markdown", "")
                if not content:
                    content = result.get("html", "")

                # Skip empty content
                if not content or len(content.strip()) < 50:
                    failed_count += 1
                    logger.warning(
                        f"Skipping result with insufficient content | url={url} | "
                        f"content_length={len(content) if content else 0}"
                    )
                    continue

                # Build metadata
                metadata = {
                    "content_length": len(content),
                    "crawl_type": crawl_type,
                    "depth": idx,  # Use index as depth indicator
                }

                # Add links if available
                if "links" in result:
                    metadata["links"] = result["links"]

                # Create document
                doc = {
                    "url": url,
                    "title": title,
                    "content": content,
                    "metadata": metadata
                }

                documents.append(doc)

            except Exception as e:
                failed_count += 1
                url = result.get("url", "unknown") if isinstance(result, dict) else "unknown"
                logger.error(
                    f"Error transforming crawl result to document | url={url} | error={e}",
                    exc_info=True
                )

        if failed_count > 0:
            safe_logfire_info(
                f"Transformed crawl results | successful={len(documents)} | failed={failed_count}"
            )

        return documents

    async def close(self) -> None:
        """
        Close the crawler and clean up resources.

        This should be called when the service is no longer needed to properly
        release browser resources and connections.

        Example:
            ```python
            service = SimpleCrawlingService()
            try:
                docs = await service.crawl("https://example.com")
            finally:
                await service.close()
            ```
        """
        if self.crawler and self._crawler_initialized:
            try:
                await self.crawler.__aexit__(None, None, None)
                safe_logfire_info("AsyncWebCrawler closed successfully")
            except Exception as e:
                logger.warning(f"Error closing crawler: {e}", exc_info=True)
            finally:
                self._crawler_initialized = False

    async def __aenter__(self):
        """Context manager entry - ensures crawler is initialized."""
        await self._ensure_crawler()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup."""
        await self.close()


# Convenience function for simple usage
async def crawl_url(
    url: str,
    max_depth: int = 1,
    max_concurrent: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function for simple crawling without managing service lifecycle.

    This function automatically handles crawler initialization and cleanup,
    making it ideal for one-off crawling tasks.

    Args:
        url: The URL to crawl
        max_depth: Maximum depth for recursive crawling (default: 1)
        max_concurrent: Maximum concurrent requests (default: 10)

    Returns:
        List of document dictionaries

    Example:
        ```python
        from server.services.simple_crawling_service import crawl_url

        # Single page crawl
        docs = await crawl_url("https://example.com/docs")

        # Deep crawl
        docs = await crawl_url("https://example.com", max_depth=3)
        ```
    """
    async with SimpleCrawlingService() as service:
        return await service.crawl(url, max_depth, max_concurrent)
