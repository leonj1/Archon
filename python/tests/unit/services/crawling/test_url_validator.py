"""
Unit tests for UrlValidator

Tests URL validation functionality including self-link detection,
normalization, and edge case handling.
"""

import pytest
from src.server.services.crawling.helpers.url_validator import UrlValidator


class TestUrlValidatorSelfLinkDetection:
    """Test self-link detection functionality."""

    def test_is_self_link_identical_urls(self):
        """Test that identical URLs are detected as self-links."""
        url = "https://example.com/path"
        assert UrlValidator.is_self_link(url, url) is True

    def test_is_self_link_with_trailing_slash(self):
        """Test that trailing slash differences are normalized."""
        link = "https://example.com/path/"
        base = "https://example.com/path"
        assert UrlValidator.is_self_link(link, base) is True

    def test_is_self_link_with_fragment(self):
        """Test that fragment differences result in different URLs."""
        link = "https://example.com/path#section"
        base = "https://example.com/path"
        # Fragments are removed by netloc parsing, so these should match
        assert UrlValidator.is_self_link(link, base) is True

    def test_is_self_link_with_query_params(self):
        """Test that query parameter differences are ignored during comparison."""
        link = "https://example.com/path?key=value"
        base = "https://example.com/path"
        # Query params are ignored by urlparse.path normalization, so these should match
        assert UrlValidator.is_self_link(link, base) is True

    def test_is_self_link_different_domains(self):
        """Test that different domains are not self-links."""
        link = "https://example.com/path"
        base = "https://other.com/path"
        assert UrlValidator.is_self_link(link, base) is False

    def test_is_self_link_different_paths(self):
        """Test that different paths are not self-links."""
        link = "https://example.com/path1"
        base = "https://example.com/path2"
        assert UrlValidator.is_self_link(link, base) is False


class TestUrlValidatorNormalization:
    """Test URL normalization functionality."""

    def test_normalize_url_lowercase_scheme(self):
        """Test that scheme is normalized to lowercase."""
        url1 = "HTTPS://example.com/path"
        url2 = "https://example.com/path"
        assert UrlValidator.is_self_link(url1, url2) is True

    def test_normalize_url_lowercase_host(self):
        """Test that host is normalized to lowercase."""
        url1 = "https://EXAMPLE.COM/path"
        url2 = "https://example.com/path"
        assert UrlValidator.is_self_link(url1, url2) is True

    def test_normalize_url_removes_trailing_slash(self):
        """Test that trailing slashes are removed during normalization."""
        url1 = "https://example.com/path/"
        url2 = "https://example.com/path"
        assert UrlValidator.is_self_link(url1, url2) is True

    def test_normalize_url_default_http_port(self):
        """Test that default HTTP port 80 is omitted."""
        url1 = "http://example.com:80/path"
        url2 = "http://example.com/path"
        assert UrlValidator.is_self_link(url1, url2) is True

    def test_normalize_url_default_https_port(self):
        """Test that default HTTPS port 443 is omitted."""
        url1 = "https://example.com:443/path"
        url2 = "https://example.com/path"
        assert UrlValidator.is_self_link(url1, url2) is True

    def test_normalize_url_custom_port(self):
        """Test that custom ports are preserved."""
        url1 = "https://example.com:8080/path"
        url2 = "https://example.com/path"
        assert UrlValidator.is_self_link(url1, url2) is False

    def test_normalize_url_no_scheme(self):
        """Test handling of URLs without scheme."""
        # When scheme is missing, urlparse returns empty scheme
        # _normalize_url defaults to "http"
        url1 = "example.com/path"
        url2 = "http://example.com/path"
        assert UrlValidator.is_self_link(url1, url2) is True


class TestUrlValidatorPortHandling:
    """Test port handling during normalization."""

    def test_get_port_part_http_default(self):
        """Test that HTTP default port 80 returns empty string."""
        from urllib.parse import urlparse

        parsed = urlparse("http://example.com:80/path")
        port_part = UrlValidator._get_port_part(parsed.scheme, parsed.port)
        assert port_part == ""

    def test_get_port_part_https_default(self):
        """Test that HTTPS default port 443 returns empty string."""
        from urllib.parse import urlparse

        parsed = urlparse("https://example.com:443/path")
        port_part = UrlValidator._get_port_part(parsed.scheme, parsed.port)
        assert port_part == ""

    def test_get_port_part_custom_port(self):
        """Test that custom ports are included."""
        from urllib.parse import urlparse

        parsed = urlparse("https://example.com:8080/path")
        port_part = UrlValidator._get_port_part(parsed.scheme, parsed.port)
        assert port_part == ":8080"

    def test_get_port_part_none_port(self):
        """Test that None port returns empty string."""
        port_part = UrlValidator._get_port_part("http", None)
        assert port_part == ""


class TestUrlValidatorFallback:
    """Test fallback comparison when normalization fails."""

    def test_fallback_comparison_identical(self):
        """Test fallback with identical URLs."""
        url = "https://example.com/path"
        assert UrlValidator._fallback_comparison(url, url) is True

    def test_fallback_comparison_trailing_slash(self):
        """Test fallback handles trailing slashes."""
        url1 = "https://example.com/path/"
        url2 = "https://example.com/path"
        assert UrlValidator._fallback_comparison(url1, url2) is True

    def test_fallback_comparison_different_urls(self):
        """Test fallback with different URLs."""
        url1 = "https://example.com/path1"
        url2 = "https://example.com/path2"
        assert UrlValidator._fallback_comparison(url1, url2) is False


class TestUrlValidatorErrorHandling:
    """Test error handling and edge cases."""

    def test_is_self_link_invalid_link(self):
        """Test handling of invalid link URL."""
        # This should trigger exception and use fallback
        link = "not a valid url"
        base = "https://example.com"
        result = UrlValidator.is_self_link(link, base)
        # Fallback comparison will be used
        assert isinstance(result, bool)

    def test_is_self_link_invalid_base(self):
        """Test handling of invalid base URL."""
        link = "https://example.com"
        base = "not a valid url"
        result = UrlValidator.is_self_link(link, base)
        assert isinstance(result, bool)

    def test_is_self_link_both_invalid(self):
        """Test handling when both URLs are invalid."""
        link = "invalid1"
        base = "invalid2"
        result = UrlValidator.is_self_link(link, base)
        assert isinstance(result, bool)

    def test_is_self_link_exception_uses_fallback(self):
        """Test that exceptions trigger fallback comparison."""
        # Identical strings should match in fallback
        url = "some://strange:url"
        result = UrlValidator.is_self_link(url, url)
        # Even if normalization fails, fallback should work
        assert isinstance(result, bool)


class TestUrlValidatorEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_is_self_link_empty_strings(self):
        """Test handling of empty strings."""
        result = UrlValidator.is_self_link("", "")
        assert result is True  # Fallback: "" == ""

    def test_is_self_link_whitespace(self):
        """Test handling of whitespace."""
        result = UrlValidator.is_self_link("   ", "   ")
        assert isinstance(result, bool)

    def test_is_self_link_unicode_urls(self):
        """Test handling of Unicode characters in URLs."""
        link = "https://example.com/path/ü"
        base = "https://example.com/path/ü"
        assert UrlValidator.is_self_link(link, base) is True

    def test_is_self_link_case_sensitivity(self):
        """Test case sensitivity in path component."""
        # Scheme and host are case-insensitive, path is case-sensitive
        link = "https://example.com/PATH"
        base = "https://example.com/path"
        assert UrlValidator.is_self_link(link, base) is False


class TestUrlValidatorRealWorldScenarios:
    """Test real-world URL scenarios."""

    def test_is_self_link_github_urls(self):
        """Test GitHub URL variations."""
        link = "https://github.com/user/repo"
        base = "https://github.com/user/repo/"
        assert UrlValidator.is_self_link(link, base) is True

    def test_is_self_link_documentation_sites(self):
        """Test documentation site URL patterns."""
        link = "https://docs.python.org/3/"
        base = "https://docs.python.org/3"
        assert UrlValidator.is_self_link(link, base) is True

    def test_is_self_link_api_endpoints(self):
        """Test API endpoint variations."""
        link = "https://api.example.com/v1/users"
        base = "https://api.example.com/v1/users/"
        assert UrlValidator.is_self_link(link, base) is True

    def test_is_self_link_localhost(self):
        """Test localhost variations."""
        link = "http://localhost:8080/path"
        base = "http://127.0.0.1:8080/path"
        # Different hosts, even though they resolve to same address
        assert UrlValidator.is_self_link(link, base) is False

    def test_is_self_link_with_subdomain(self):
        """Test subdomain differences."""
        link = "https://api.example.com/path"
        base = "https://www.example.com/path"
        assert UrlValidator.is_self_link(link, base) is False

    def test_is_self_link_http_vs_https(self):
        """Test HTTP vs HTTPS."""
        link = "http://example.com/path"
        base = "https://example.com/path"
        assert UrlValidator.is_self_link(link, base) is False

    def test_is_self_link_with_port_variations(self):
        """Test various port scenarios."""
        # Same port explicitly vs implicitly
        link = "https://example.com:443/path"
        base = "https://example.com/path"
        assert UrlValidator.is_self_link(link, base) is True

        # Different ports
        link = "https://example.com:8443/path"
        base = "https://example.com:443/path"
        assert UrlValidator.is_self_link(link, base) is False

    def test_is_self_link_nested_paths(self):
        """Test deeply nested paths."""
        link = "https://example.com/a/b/c/d/e"
        base = "https://example.com/a/b/c/d/e/"
        assert UrlValidator.is_self_link(link, base) is True

    def test_is_self_link_special_characters_in_path(self):
        """Test special characters in URL paths."""
        link = "https://example.com/path-with-dashes_and_underscores"
        base = "https://example.com/path-with-dashes_and_underscores/"
        assert UrlValidator.is_self_link(link, base) is True
