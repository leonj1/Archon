"""
Protocol for Site Configuration Operations

Defines interface for site-specific configurations and markdown generation.
"""

from typing import Any, Protocol


class ISiteConfig(Protocol):
    """Protocol for site configuration operations."""

    def is_documentation_site(self, url: str) -> bool:
        """
        Check if URL is likely a documentation site that needs special handling.

        Args:
            url: URL to check

        Returns:
            True if URL appears to be a documentation site
        """
        ...

    def get_markdown_generator(self) -> Any:
        """
        Get markdown generator that preserves code blocks.

        Returns:
            Configured markdown generator
        """
        ...

    def get_link_pruning_markdown_generator(self) -> Any:
        """
        Get markdown generator with link pruning for recursive crawling.

        Returns:
            Configured markdown generator with pruning enabled
        """
        ...
