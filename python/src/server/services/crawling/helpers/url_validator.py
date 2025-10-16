"""
URL Validator

Validates URLs for specific characteristics like self-referential links.
"""

from ....config.logfire_config import get_logger

logger = get_logger(__name__)


class UrlValidator:
    """Validates URLs for various characteristics."""

    @staticmethod
    def is_self_link(link: str, base_url: str) -> bool:
        """
        Check if a link is a self-referential link to the base URL.
        Handles query parameters, fragments, trailing slashes, and normalizes
        scheme/host/ports for accurate comparison.

        Args:
            link: The link to check
            base_url: The base URL to compare against

        Returns:
            True if the link is self-referential, False otherwise
        """
        try:
            return UrlValidator._compare_normalized_urls(link, base_url)
        except Exception as e:
            logger.warning(f"Error checking if link is self-referential: {e}", exc_info=True)
            return UrlValidator._fallback_comparison(link, base_url)

    @staticmethod
    def _compare_normalized_urls(link: str, base_url: str) -> bool:
        """Compare URLs after normalization."""
        from urllib.parse import urlparse

        core_link = UrlValidator._normalize_url(urlparse(link))
        core_base = UrlValidator._normalize_url(urlparse(base_url))
        return core_link == core_base

    @staticmethod
    def _normalize_url(parsed_url) -> str:
        """
        Normalize a parsed URL for comparison.

        Args:
            parsed_url: A parsed URL object from urlparse

        Returns:
            Normalized URL string
        """
        scheme = (parsed_url.scheme or "http").lower()
        host = (parsed_url.hostname or "").lower()
        port = parsed_url.port

        port_part = UrlValidator._get_port_part(scheme, port)
        path = parsed_url.path.rstrip("/")

        return f"{scheme}://{host}{port_part}{path}"

    @staticmethod
    def _get_port_part(scheme: str, port: int | None) -> str:
        """Get the port part of the URL, omitting default ports."""
        if (scheme == "http" and port in (None, 80)) or (scheme == "https" and port in (None, 443)):
            return ""
        return f":{port}" if port else ""

    @staticmethod
    def _fallback_comparison(link: str, base_url: str) -> bool:
        """Fallback to simple string comparison if normalization fails."""
        return link.rstrip('/') == base_url.rstrip('/')
