"""Fake URL handler for testing."""


class FakeURLHandler:
    """
    Fake URL handler for testing.

    Provides predictable transformations and ID generation.
    """

    def __init__(self):
        """Initialize fake URL handler."""
        self.generate_id_calls: list[str] = []
        self.extract_name_calls: list[str] = []
        self.transform_github_calls: list[str] = []

    def generate_unique_source_id(self, url: str) -> str:
        """
        Generate predictable source ID.

        Args:
            url: Source URL

        Returns:
            Predictable source ID based on URL
        """
        self.generate_id_calls.append(url)
        # Return predictable ID for testing
        return f"src_{hash(url) % 10000}"

    def extract_display_name(self, url: str) -> str:
        """
        Extract simple display name.

        Args:
            url: Source URL

        Returns:
            Simple display name
        """
        self.extract_name_calls.append(url)
        # Simple extraction for testing
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc or "unknown"

    def transform_github_url(self, url: str) -> str:
        """
        No-op GitHub URL transformation for testing.

        Args:
            url: GitHub URL

        Returns:
            Unchanged URL
        """
        self.transform_github_calls.append(url)
        return url

    def reset(self) -> None:
        """Clear all recorded calls."""
        self.generate_id_calls.clear()
        self.extract_name_calls.clear()
        self.transform_github_calls.clear()
