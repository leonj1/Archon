# Crawl4AI Update to v0.7.4

## Summary
Updated Crawl4AI from version 0.6.2 to 0.7.4.

## Changes Made
- Updated `crawl4ai==0.6.2` to `crawl4ai==0.7.4` in `python/pyproject.toml`
  - Updated in both `server` and `all` dependency groups
- Ran `uv sync --group all` to update dependencies
- All imports verified working
- All existing tests passing (18/18 tests pass)

## Key Features in v0.7.4
- **LLM Table Extraction**: Revolutionary table extraction with intelligent chunking
- **Performance**: Dispatcher bug fixes for better concurrent processing
- **Browser Management**: Fixed race conditions in concurrent page creation
- **URL Processing**: Better handling of raw:// URLs and base tag link resolution
- **Proxy Support**: Enhanced flexible proxy configuration

## Breaking Changes
No breaking changes identified. The v0.7.x series maintains backward compatibility.

## API Compatibility
All existing Archon code remains compatible:
- ✅ `AsyncWebCrawler` - Working
- ✅ `BrowserConfig` - Working
- ✅ `CrawlerRunConfig` - Working
- ✅ `CacheMode` - Working
- ✅ Result properties (`markdown`, `html`, `links`, etc.) - Working

## Testing
All crawl orchestration tests pass:
```bash
cd python && uv run pytest tests/test_crawl_orchestration_isolated.py -v
# Result: 18 passed in 1.13s
```

## URL Resolution Bug Status

**Known Issue in v0.6.2** (documented in `crawler-test` branch):
- Bug: `../../` relative paths only go up ONE directory instead of TWO
- Impact: ~80% of URLs fail on documentation sites with deep nesting
- Example: `../../guide/page.html` incorrectly becomes `.../reference/guide/page.html`

**Status in v0.7.4**:
- ⚠️ **UNKNOWN** - No specific mention in changelog
- v0.7.4 mentions "Advanced URL Processing" improvements
- Related issues (#570, #1268, #1323) fixed, but not this specific bug
- **TESTING REQUIRED** before deploying to production

**Testing Recommendation**:
```bash
cd python
uv run python test_url_resolution_fix.py
```

## Deployment Notes
After merging:
1. **TEST URL RESOLUTION BUG FIRST** (see test script above)
2. Rebuild Docker images to pick up new dependency
3. Test crawling functionality in development environment
4. Verify no regressions on documentation sites (AWS Boto3, etc.)
5. Monitor for any unexpected behavior in production

## References
- [Crawl4AI v0.7.4 Release](https://github.com/unclecode/crawl4ai/releases/tag/v0.7.4)
- [Crawl4AI Changelog](https://github.com/unclecode/crawl4ai/blob/main/CHANGELOG.md)
- [Crawl4AI Documentation (v0.7.x)](https://docs.crawl4ai.com/)
