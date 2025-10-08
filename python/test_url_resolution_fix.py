#!/usr/bin/env python3
"""
Test script to verify if Crawl4AI v0.7.4 fixes the URL resolution bug.

Bug in v0.6.2:
- ../../ only goes up ONE directory instead of TWO
- Base: .../reference/services/page.html
- Link: ../../guide/paginators.html
- Expected: .../guide/paginators.html
- Got: .../reference/guide/paginators.html (WRONG)
"""

import asyncio
from urllib.parse import urljoin

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig


async def test_url_resolution():
    """Test if Crawl4AI correctly resolves ../../ relative URLs."""

    # Test case from bug report
    base_url = "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock.html"
    relative_url = "../../guide/paginators.html"

    # Expected correct result (Python's urljoin)
    expected = urljoin(base_url, relative_url)
    print(f"✅ Python urljoin (correct): {expected}")
    print(f"   Expected: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/paginators.html")

    # Test Crawl4AI's URL resolution
    print(f"\n🔍 Testing Crawl4AI v0.7.4 URL resolution...")

    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        crawl_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            page_timeout=15000,
        )

        result = await crawler.arun(url=base_url, config=crawl_config)

        if not result.success:
            print(f"❌ Failed to crawl: {result.error_message}")
            return False

        # Look for the guide/paginators link in internal links
        found_correct = False
        found_incorrect = False

        if result.links and 'internal' in result.links:
            for link in result.links['internal']:
                if 'guide/paginators.html' in link:
                    # Check if it's the correct URL (without extra "reference")
                    if '/latest/guide/paginators.html' in link and '/reference/guide/' not in link:
                        found_correct = True
                        print(f"✅ CORRECT URL found: {link}")
                    elif '/reference/guide/paginators.html' in link:
                        found_incorrect = True
                        print(f"❌ INCORRECT URL found (bug still present): {link}")

        if found_correct and not found_incorrect:
            print(f"\n🎉 SUCCESS! Crawl4AI v0.7.4 correctly resolves ../../ URLs")
            return True
        elif found_incorrect:
            print(f"\n⚠️  BUG STILL PRESENT in v0.7.4: URL resolution issue not fixed")
            return False
        else:
            print(f"\n⚠️  Could not find the specific test URL in links")
            print(f"   Total internal links: {len(result.links.get('internal', []))}")
            return None


if __name__ == "__main__":
    result = asyncio.run(test_url_resolution())

    if result is True:
        print("\n✅ Test PASSED - Bug is fixed in v0.7.4")
        exit(0)
    elif result is False:
        print("\n❌ Test FAILED - Bug still present in v0.7.4")
        exit(1)
    else:
        print("\n⚠️  Test INCONCLUSIVE - Manual verification needed")
        exit(2)
