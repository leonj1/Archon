"""
Fake implementation of ISiteConfig for testing.
"""

from typing import Any


class FakeSiteConfig:
    """Fake site configuration for testing."""

    def __init__(self):
        """Initialize fake site config."""
        self._doc_site_patterns: list[str] = []
        self._markdown_generator: Any = "FakeMarkdownGenerator"
        self._link_pruning_generator: Any = "FakeLinkPruningMarkdownGenerator"
        self.is_documentation_site_calls: list[str] = []
        self.get_markdown_generator_calls: int = 0
        self.get_link_pruning_markdown_generator_calls: int = 0

    def configure_documentation_patterns(self, patterns: list[str]):
        """Configure patterns for documentation site detection."""
        self._doc_site_patterns = patterns

    def configure_markdown_generator(self, generator: Any):
        """Configure the markdown generator to return."""
        self._markdown_generator = generator

    def configure_link_pruning_generator(self, generator: Any):
        """Configure the link pruning markdown generator to return."""
        self._link_pruning_generator = generator

    def is_documentation_site(self, url: str) -> bool:
        """Check if URL is a documentation site."""
        self.is_documentation_site_calls.append(url)
        if not self._doc_site_patterns:
            # Default behavior: check common patterns
            return any(
                pattern in url.lower()
                for pattern in ['docs.', 'documentation.', '/docs/', 'readthedocs']
            )
        return any(pattern in url.lower() for pattern in self._doc_site_patterns)

    def get_markdown_generator(self) -> Any:
        """Get markdown generator."""
        self.get_markdown_generator_calls += 1
        return self._markdown_generator

    def get_link_pruning_markdown_generator(self) -> Any:
        """Get link pruning markdown generator."""
        self.get_link_pruning_markdown_generator_calls += 1
        return self._link_pruning_generator

    def reset_tracking(self):
        """Reset call tracking."""
        self.is_documentation_site_calls = []
        self.get_markdown_generator_calls = 0
        self.get_link_pruning_markdown_generator_calls = 0
