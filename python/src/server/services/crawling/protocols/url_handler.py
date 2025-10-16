"""URL handler protocol for URL transformations and ID generation."""

from typing import Protocol


class IURLHandler(Protocol):
    """Interface for URL handling operations."""

    def generate_unique_source_id(self, url: str) -> str:
        """
        Generate a unique source ID from URL.

        Args:
            url: The source URL

        Returns:
            Unique source identifier
        """
        ...

    def extract_display_name(self, url: str) -> str:
        """
        Extract a display name from URL.

        Args:
            url: The source URL

        Returns:
            Human-readable display name
        """
        ...

    def transform_github_url(self, url: str) -> str:
        """
        Transform GitHub URLs to raw content URLs.

        Args:
            url: GitHub URL

        Returns:
            Transformed URL for raw content access
        """
        ...
