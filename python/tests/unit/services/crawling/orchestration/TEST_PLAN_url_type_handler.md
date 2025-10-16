# Test Plan: UrlTypeHandler

## Executive Summary

**Service**: `UrlTypeHandler` (orchestration/url_type_handler.py)
**Testability Rating**: HIGH
**Lines of Code**: ~216
**External Dependencies**: 6 (URLHandler, crawl functions, is_self_link_checker)
**Recommended Test Coverage**: 100% line, 100% branch

## 1. Function Purity Analysis

### Pure Functions

NONE - All functions involve external calls or I/O operations

### Impure Functions

#### `__init__(url_handler, crawl_markdown_file, parse_sitemap, crawl_batch_with_progress, crawl_recursive_with_progress, is_self_link_checker)` (Lines 18-43)
- **Purity**: IMPURE (constructor with state initialization)
- **Side Effects**: Stores function references
- **External Dependencies**: Multiple crawling functions and URL handler
- **Testability**: HIGH - Clean dependency injection

#### `async crawl_by_type(url, request, progress_callback)` (Lines 45-69)
- **Purity**: IMPURE (routing with external calls)
- **Side Effects**: Calls various crawling strategies based on URL type
- **External Dependencies**: URLHandler, multiple crawling functions
- **Testability**: HIGH - Clear routing logic, easy to test with mocks

#### `async _handle_text_file(url, request, progress_callback)` (Lines 71-91)
- **Purity**: IMPURE (external crawling + conditional processing)
- **Side Effects**:
  - Calls crawl_markdown_file
  - Checks if file is link collection
  - May process links
- **External Dependencies**: crawl_markdown_file, URLHandler
- **Testability**: HIGH - Well-structured with clear branches

#### `async _process_link_collection(url, content, original_results, request, progress_callback)` (Lines 93-139)
- **Purity**: IMPURE (link extraction + crawling)
- **Side Effects**:
  - Extracts links from content
  - Filters links (self-links, binary files)
  - Crawls extracted links
  - Combines results
- **External Dependencies**: URLHandler, crawl_batch_with_progress
- **Testability**: MEDIUM - Complex logic with multiple filtering steps

#### `async _handle_sitemap(url, progress_callback)` (Lines 141-154)
- **Purity**: IMPURE (sitemap parsing + batch crawling)
- **Side Effects**: Parses sitemap, crawls URLs
- **External Dependencies**: parse_sitemap, crawl_batch_with_progress
- **Testability**: HIGH - Simple delegation

#### `async _handle_regular_webpage(url, request, progress_callback)` (Lines 156-169)
- **Purity**: IMPURE (recursive crawling)
- **Side Effects**: Performs recursive crawl
- **External Dependencies**: crawl_recursive_with_progress
- **Testability**: HIGH - Simple delegation with max_depth extraction

#### `_filter_self_links(links_with_text, base_url)` (Lines 171-192)
- **Purity**: IMPURE (filtering with logging)
- **Side Effects**: Logs filtered count
- **External Dependencies**: is_self_link_checker, logger
- **Testability**: HIGH - Simple list filtering

#### `_filter_binary_files(links_with_text)` (Lines 194-215)
- **Purity**: IMPURE (filtering with logging)
- **Side Effects**: Logs filtered count
- **External Dependencies**: URLHandler, logger
- **Testability**: HIGH - Simple list filtering

## 2. External Dependencies Analysis

### URL Handling Dependencies

#### `URLHandler`
- **Usage**: URL type detection and link extraction
- **Methods Used**:
  - `is_txt(url: str) -> bool`
  - `is_markdown(url: str) -> bool`
  - `is_sitemap(url: str) -> bool`
  - `is_link_collection_file(url: str, content: str) -> bool`
  - `extract_markdown_links_with_text(content: str, url: str) -> list[tuple[str, str]]`
  - `is_binary_file(url: str) -> bool`
- **Interface Needed**: YES - `IURLHandler` Protocol

### Crawling Function Dependencies

#### `crawl_markdown_file: Callable`
- **Usage**: Crawl text/markdown files
- **Signature**: `async def (url: str, progress_callback) -> list[dict]`
- **Interface Needed**: YES - Mock function

#### `parse_sitemap: Callable`
- **Usage**: Parse sitemap XML
- **Signature**: `def (sitemap_url: str) -> list[str]`
- **Interface Needed**: YES - Mock function

#### `crawl_batch_with_progress: Callable`
- **Usage**: Crawl multiple URLs in batch
- **Signature**: `async def (urls, max_concurrent, progress_callback, link_text_fallbacks) -> list[dict]`
- **Interface Needed**: YES - Mock function

#### `crawl_recursive_with_progress: Callable`
- **Usage**: Recursively crawl URLs
- **Signature**: `async def (start_urls, max_depth, max_concurrent, progress_callback) -> list[dict]`
- **Interface Needed**: YES - Mock function

#### `is_self_link_checker: Callable`
- **Usage**: Check if link is self-referential
- **Signature**: `def (link: str, base_url: str) -> bool`
- **Interface Needed**: YES - Mock function

### Logging Dependencies

#### `logger`
- **Usage**: Info logging
- **Methods Used**: `logger.info()`
- **Interface Needed**: NO - Not critical for logic

## 3. Testability Assessment

### Overall Testability: HIGH

**Strengths**:
1. Excellent dependency injection for all crawling functions
2. Clear separation of URL type handling logic
3. Private methods are well-encapsulated
4. Filtering methods are simple and focused
5. Easy to test with mock functions

**Weaknesses**:
1. `_process_link_collection` has multiple responsibilities (extract, filter, crawl)
2. Some conditional logic complexity in link collection processing

**Testing Challenges**:
1. **Multiple Async Calls**: Need proper async test harness
2. **Link Filtering Logic**: Need to test multiple filtering steps
3. **Progress Callbacks**: Need to verify they're passed through correctly

### Recommended Refactoring for Testability

NONE critical - Code is already well-structured. Optional: Extract link filtering to separate service.

## 4. Interface Extraction Plan

### Core Protocols (Priority: HIGH)

#### `IURLHandler`
```python
from typing import Protocol

class IURLHandler(Protocol):
    """Interface for URL operations."""

    def is_txt(self, url: str) -> bool:
        ...

    def is_markdown(self, url: str) -> bool:
        ...

    def is_sitemap(self, url: str) -> bool:
        ...

    def is_link_collection_file(self, url: str, content: str) -> bool:
        ...

    def extract_markdown_links_with_text(
        self, content: str, base_url: str
    ) -> list[tuple[str, str]]:
        ...

    def is_binary_file(self, url: str) -> bool:
        ...
```

#### `ICrawlFunction` (Generic)
```python
from typing import Protocol, Callable, Awaitable, Any, Optional

# For specific crawl functions, we can use simple callables
# since they're already injectable
```

### Fake Implementations

#### `FakeURLHandler`
```python
class FakeURLHandler:
    """Fake URL handler for testing."""

    def __init__(self):
        self.txt_urls: set[str] = set()
        self.markdown_urls: set[str] = set()
        self.sitemap_urls: set[str] = set()
        self.link_collection_files: dict[str, bool] = {}
        self.binary_files: set[str] = set()
        self.extracted_links: dict[str, list[tuple[str, str]]] = {}

    def is_txt(self, url: str) -> bool:
        return url in self.txt_urls or url.endswith('.txt')

    def is_markdown(self, url: str) -> bool:
        return url in self.markdown_urls or url.endswith(('.md', '.mdx'))

    def is_sitemap(self, url: str) -> bool:
        return url in self.sitemap_urls or 'sitemap' in url.lower()

    def is_link_collection_file(self, url: str, content: str) -> bool:
        if url in self.link_collection_files:
            return self.link_collection_files[url]
        return 'llms.txt' in url or 'links.txt' in url

    def extract_markdown_links_with_text(
        self, content: str, base_url: str
    ) -> list[tuple[str, str]]:
        return self.extracted_links.get(content, [])

    def is_binary_file(self, url: str) -> bool:
        return url in self.binary_files

    # Test helpers
    def set_link_collection(self, url: str, is_collection: bool):
        self.link_collection_files[url] = is_collection

    def set_extracted_links(self, content: str, links: list[tuple[str, str]]):
        self.extracted_links[content] = links
```

#### `FakeCrawlMarkdownFile`
```python
class FakeCrawlMarkdownFile:
    """Fake markdown file crawler."""

    def __init__(self):
        self.calls: list[dict] = []
        self.results: dict[str, list[dict]] = {}

    async def __call__(
        self, url: str, progress_callback=None
    ) -> list[dict]:
        self.calls.append({"url": url, "progress_callback": progress_callback})
        return self.results.get(url, [{
            "url": url,
            "markdown": f"Content from {url}",
            "success": True
        }])

    def set_result(self, url: str, result: list[dict]):
        """Set the result for a specific URL."""
        self.results[url] = result
```

#### `FakeParseSitemap`
```python
class FakeParseSitemap:
    """Fake sitemap parser."""

    def __init__(self):
        self.calls: list[str] = []
        self.results: dict[str, list[str]] = {}

    def __call__(self, sitemap_url: str) -> list[str]:
        self.calls.append(sitemap_url)
        return self.results.get(sitemap_url, [
            f"{sitemap_url}/page1",
            f"{sitemap_url}/page2"
        ])

    def set_result(self, sitemap_url: str, urls: list[str]):
        """Set the URLs for a specific sitemap."""
        self.results[sitemap_url] = urls
```

#### `FakeCrawlBatchWithProgress`
```python
class FakeCrawlBatchWithProgress:
    """Fake batch crawler."""

    def __init__(self):
        self.calls: list[dict] = []
        self.results: list[dict] = []

    async def __call__(
        self, urls, max_concurrent, progress_callback, link_text_fallbacks
    ) -> list[dict]:
        self.calls.append({
            "urls": urls,
            "max_concurrent": max_concurrent,
            "progress_callback": progress_callback,
            "link_text_fallbacks": link_text_fallbacks,
        })

        # Return mock results for each URL
        return [
            {"url": url, "markdown": f"Content from {url}", "success": True}
            for url in urls
        ]

    def set_results(self, results: list[dict]):
        """Set custom results."""
        self.results = results
```

#### `FakeCrawlRecursiveWithProgress`
```python
class FakeCrawlRecursiveWithProgress:
    """Fake recursive crawler."""

    def __init__(self):
        self.calls: list[dict] = []

    async def __call__(
        self, start_urls, max_depth, max_concurrent, progress_callback
    ) -> list[dict]:
        self.calls.append({
            "start_urls": start_urls,
            "max_depth": max_depth,
            "max_concurrent": max_concurrent,
            "progress_callback": progress_callback,
        })

        return [
            {"url": url, "markdown": f"Content from {url}", "success": True}
            for url in start_urls
        ]
```

#### `FakeIsSelfLinkChecker`
```python
class FakeIsSelfLinkChecker:
    """Fake self-link checker."""

    def __init__(self):
        self.calls: list[tuple[str, str]] = []
        self.self_links: set[tuple[str, str]] = set()

    def __call__(self, link: str, base_url: str) -> bool:
        self.calls.append((link, base_url))
        return (link, base_url) in self.self_links

    def mark_as_self_link(self, link: str, base_url: str):
        """Mark a link as self-referential."""
        self.self_links.add((link, base_url))
```

## 5. Test Plan

### Test File Structure

```
tests/unit/services/crawling/orchestration/
├── test_url_type_handler.py
└── fakes/
    ├── fake_url_handler.py
    ├── fake_crawl_functions.py  # All crawl function fakes
    └── fake_is_self_link_checker.py
```

### Test Scenarios

#### Constructor Tests

**Test: `test_init_with_all_dependencies`**
- Setup: Create all fake functions
- Action: Initialize UrlTypeHandler
- Expected: All dependencies assigned
- Type: Unit test with Fakes

#### Crawl By Type Tests - Text Files

**Test: `test_crawl_by_type_txt_file`**
- Setup:
  - FakeURLHandler (is_txt returns True)
  - FakeCrawlMarkdownFile
  - UrlTypeHandler
- Action: Call crawl_by_type("https://example.com/file.txt", request)
- Expected:
  - _handle_text_file called
  - crawl_type = "text_file"
  - Returns crawl results
- Type: Unit test with Fakes

**Test: `test_crawl_by_type_markdown_file`**
- Setup:
  - FakeURLHandler (is_markdown returns True)
  - FakeCrawlMarkdownFile
- Action: Call crawl_by_type("https://example.com/doc.md", request)
- Expected:
  - _handle_text_file called
  - crawl_type = "text_file" (or specific markdown type)
  - Returns crawl results
- Type: Unit test with Fakes

**Test: `test_crawl_by_type_llms_txt`**
- Setup:
  - FakeURLHandler (is_txt returns True)
  - URL contains "llms"
  - FakeCrawlMarkdownFile
- Action: Call crawl_by_type("https://example.com/llms.txt", request)
- Expected:
  - crawl_type = "llms-txt"
  - Returns crawl results
- Type: Unit test with Fakes

#### Crawl By Type Tests - Sitemap

**Test: `test_crawl_by_type_sitemap`**
- Setup:
  - FakeURLHandler (is_sitemap returns True)
  - FakeParseSitemap
  - FakeCrawlBatchWithProgress
- Action: Call crawl_by_type("https://example.com/sitemap.xml", request)
- Expected:
  - _handle_sitemap called
  - parse_sitemap called
  - crawl_batch_with_progress called
  - crawl_type = "sitemap"
- Type: Unit test with Fakes

**Test: `test_crawl_by_type_empty_sitemap`**
- Setup:
  - FakeParseSitemap returning empty list
- Action: Call crawl_by_type("https://example.com/sitemap.xml", request)
- Expected:
  - Returns empty list
  - crawl_type = "sitemap"
- Type: Unit test with Fakes

#### Crawl By Type Tests - Regular Webpage

**Test: `test_crawl_by_type_regular_webpage`**
- Setup:
  - FakeURLHandler (all type checks return False)
  - FakeCrawlRecursiveWithProgress
- Action: Call crawl_by_type("https://example.com", request)
- Expected:
  - _handle_regular_webpage called
  - crawl_recursive_with_progress called
  - crawl_type = "normal"
- Type: Unit test with Fakes

**Test: `test_crawl_by_type_with_custom_max_depth`**
- Setup:
  - FakeCrawlRecursiveWithProgress
  - request = {"max_depth": 5}
- Action: Call crawl_by_type("https://example.com", request)
- Expected:
  - crawl_recursive_with_progress called with max_depth=5
- Type: Unit test with Fakes

**Test: `test_crawl_by_type_default_max_depth`**
- Setup:
  - FakeCrawlRecursiveWithProgress
  - request = {}
- Action: Call crawl_by_type("https://example.com", request)
- Expected:
  - crawl_recursive_with_progress called with max_depth=1
- Type: Unit test with Fakes

#### Handle Text File Tests - Simple Text File

**Test: `test_handle_text_file_simple`**
- Setup:
  - FakeURLHandler (is_link_collection_file returns False)
  - FakeCrawlMarkdownFile
- Action: Call _handle_text_file("https://example.com/file.txt", request, callback)
- Expected:
  - crawl_markdown_file called
  - No link extraction
  - Returns original results
  - crawl_type = "text_file"
- Type: Unit test with Fakes

**Test: `test_handle_text_file_empty_results`**
- Setup:
  - FakeCrawlMarkdownFile returning []
- Action: Call _handle_text_file("https://example.com/file.txt", request, callback)
- Expected:
  - Returns []
  - crawl_type = "text_file"
- Type: Unit test with Fakes

#### Handle Text File Tests - Link Collection

**Test: `test_handle_text_file_link_collection`**
- Setup:
  - FakeURLHandler (is_link_collection_file returns True)
  - extracted_links = [("https://link1.com", "Link 1"), ("https://link2.com", "Link 2")]
  - FakeCrawlMarkdownFile
  - FakeCrawlBatchWithProgress
- Action: Call _handle_text_file("https://example.com/llms.txt", request, callback)
- Expected:
  - is_link_collection_file called
  - extract_markdown_links_with_text called
  - crawl_batch_with_progress called with extracted links
  - Returns combined results (original + batch)
  - crawl_type = "link_collection_with_crawled_links"
- Type: Unit test with Fakes

**Test: `test_handle_text_file_link_collection_no_valid_links`**
- Setup:
  - FakeURLHandler (is_link_collection_file returns True)
  - extracted_links = [] (empty after filtering)
- Action: Call _handle_text_file("https://example.com/llms.txt", request, callback)
- Expected:
  - Returns original results
  - crawl_type = "text_file" (falls back)
- Type: Unit test with Fakes

#### Process Link Collection Tests

**Test: `test_process_link_collection_success`**
- Setup:
  - FakeURLHandler with extracted links
  - FakeCrawlBatchWithProgress
  - FakeIsSelfLinkChecker (no self-links)
- Action: Call _process_link_collection(url, content, original_results, request, callback)
- Expected:
  - extract_markdown_links_with_text called
  - Self-links filtered
  - Binary files filtered
  - crawl_batch_with_progress called
  - Returns combined results
- Type: Unit test with Fakes

**Test: `test_process_link_collection_filters_self_links`**
- Setup:
  - extracted_links = [("https://example.com", "Self"), ("https://other.com", "Other")]
  - FakeIsSelfLinkChecker marking first as self-link
- Action: Call _process_link_collection("https://example.com/llms.txt", content, ...)
- Expected:
  - Only "https://other.com" crawled
  - Self-link filtered out
- Type: Unit test with Fakes

**Test: `test_process_link_collection_filters_binary_files`**
- Setup:
  - extracted_links = [("https://example.com/doc.pdf", "PDF"), ("https://example.com/page", "Page")]
  - FakeURLHandler marking PDF as binary
- Action: Call _process_link_collection(url, content, ...)
- Expected:
  - Only "https://example.com/page" crawled
  - PDF filtered out
- Type: Unit test with Fakes

**Test: `test_process_link_collection_includes_link_text`**
- Setup:
  - extracted_links = [("https://link1.com", "Text 1"), ("https://link2.com", "Text 2")]
  - FakeCrawlBatchWithProgress
- Action: Call _process_link_collection(url, content, ...)
- Expected:
  - crawl_batch_with_progress called with link_text_fallbacks
  - link_text_fallbacks = {"https://link1.com": "Text 1", "https://link2.com": "Text 2"}
- Type: Unit test with Fakes

#### Handle Sitemap Tests

**Test: `test_handle_sitemap_success`**
- Setup:
  - FakeParseSitemap returning ["url1", "url2", "url3"]
  - FakeCrawlBatchWithProgress
- Action: Call _handle_sitemap("https://example.com/sitemap.xml", callback)
- Expected:
  - parse_sitemap called
  - crawl_batch_with_progress called with sitemap URLs
  - Returns batch results
  - crawl_type = "sitemap"
- Type: Unit test with Fakes

**Test: `test_handle_sitemap_empty`**
- Setup: FakeParseSitemap returning []
- Action: Call _handle_sitemap("https://example.com/sitemap.xml", callback)
- Expected:
  - Returns empty list
  - crawl_batch_with_progress NOT called
- Type: Unit test with Fakes

#### Handle Regular Webpage Tests

**Test: `test_handle_regular_webpage_default_depth`**
- Setup:
  - request = {}
  - FakeCrawlRecursiveWithProgress
- Action: Call _handle_regular_webpage("https://example.com", request, callback)
- Expected:
  - crawl_recursive_with_progress called with max_depth=1
- Type: Unit test with Fakes

**Test: `test_handle_regular_webpage_custom_depth`**
- Setup:
  - request = {"max_depth": 3}
  - FakeCrawlRecursiveWithProgress
- Action: Call _handle_regular_webpage("https://example.com", request, callback)
- Expected:
  - crawl_recursive_with_progress called with max_depth=3
- Type: Unit test with Fakes

#### Filter Self Links Tests

**Test: `test_filter_self_links_removes_self_links`**
- Setup:
  - links = [("https://example.com", "Self"), ("https://other.com", "Other")]
  - FakeIsSelfLinkChecker marking first as self
- Action: Call _filter_self_links(links, "https://example.com")
- Expected:
  - Returns [("https://other.com", "Other")]
  - Logs filtered count
- Type: Unit test with Fake

**Test: `test_filter_self_links_no_self_links`**
- Setup:
  - links = [("https://link1.com", "Link 1"), ("https://link2.com", "Link 2")]
  - FakeIsSelfLinkChecker returning False for all
- Action: Call _filter_self_links(links, "https://example.com")
- Expected: Returns all links unchanged
- Type: Unit test with Fake

**Test: `test_filter_self_links_all_self_links`**
- Setup:
  - links = [("https://example.com", "Self 1"), ("https://example.com/", "Self 2")]
  - FakeIsSelfLinkChecker returning True for all
- Action: Call _filter_self_links(links, "https://example.com")
- Expected:
  - Returns []
  - Logs filtered count
- Type: Unit test with Fake

**Test: `test_filter_self_links_empty_list`**
- Setup: links = []
- Action: Call _filter_self_links([], "https://example.com")
- Expected: Returns []
- Type: Unit test

#### Filter Binary Files Tests

**Test: `test_filter_binary_files_removes_pdfs`**
- Setup:
  - links = [("https://example.com/doc.pdf", "PDF"), ("https://example.com/page", "Page")]
  - FakeURLHandler marking PDF as binary
- Action: Call _filter_binary_files(links)
- Expected:
  - Returns [("https://example.com/page", "Page")]
  - Logs filtered count
- Type: Unit test with Fake

**Test: `test_filter_binary_files_multiple_types`**
- Setup:
  - links with PDF, PNG, ZIP, HTML
  - FakeURLHandler marking binary types
- Action: Call _filter_binary_files(links)
- Expected: Only HTML link remains
- Type: Unit test with Fake

**Test: `test_filter_binary_files_no_binary_files`**
- Setup: links with only HTML pages
- Action: Call _filter_binary_files(links)
- Expected: Returns all links unchanged
- Type: Unit test with Fake

**Test: `test_filter_binary_files_empty_list`**
- Setup: links = []
- Action: Call _filter_binary_files([])
- Expected: Returns []
- Type: Unit test

#### Integration Scenarios

**Test: `test_full_workflow_link_collection_with_filtering`**
- Setup:
  - URL: "https://example.com/llms.txt"
  - Content with mixed links: self-links, binary files, valid links
  - All fakes configured
- Action: Call crawl_by_type(url, request)
- Expected:
  1. Identified as text file
  2. Identified as link collection
  3. Links extracted
  4. Self-links filtered
  5. Binary files filtered
  6. Remaining links crawled
  7. Results combined
  8. Returns with crawl_type = "link_collection_with_crawled_links"
- Type: Unit test with comprehensive Fakes

**Test: `test_full_workflow_sitemap`**
- Setup:
  - URL: "https://example.com/sitemap.xml"
  - Sitemap with 10 URLs
- Action: Call crawl_by_type(url, request)
- Expected:
  1. Identified as sitemap
  2. Sitemap parsed
  3. Batch crawl of URLs
  4. Returns results with crawl_type = "sitemap"
- Type: Unit test with Fakes

**Test: `test_full_workflow_recursive_crawl`**
- Setup:
  - URL: "https://example.com"
  - max_depth: 3
- Action: Call crawl_by_type(url, request)
- Expected:
  1. Identified as regular webpage
  2. Recursive crawl initiated with depth=3
  3. Returns results with crawl_type = "normal"
- Type: Unit test with Fakes

#### Edge Cases

**Test: `test_crawl_by_type_with_none_progress_callback`**
- Setup: All fakes, progress_callback=None
- Action: Call crawl_by_type(url, request, progress_callback=None)
- Expected: Works correctly (callbacks handle None)
- Type: Unit test with Fakes

**Test: `test_filter_self_links_with_unicode_urls`**
- Setup: links with Unicode URLs
- Action: Call _filter_self_links(links, "https://example.com/文档")
- Expected: Works correctly
- Type: Unit test with Fake

**Test: `test_process_link_collection_with_no_link_text`**
- Setup: extracted_links with empty link text
- Action: Call _process_link_collection(...)
- Expected: link_text_fallbacks includes URLs with empty text
- Type: Unit test with Fakes

**Test: `test_handle_sitemap_with_large_url_list`**
- Setup: FakeParseSitemap returning 1000 URLs
- Action: Call _handle_sitemap(url, callback)
- Expected: All 1000 URLs passed to batch crawler
- Type: Unit test with Fakes

### Fake Implementations Needed (Summary)

1. `FakeURLHandler` - Handles URL type detection and link extraction
2. `FakeCrawlMarkdownFile` - Simulates markdown file crawling
3. `FakeParseSitemap` - Simulates sitemap parsing
4. `FakeCrawlBatchWithProgress` - Simulates batch crawling
5. `FakeCrawlRecursiveWithProgress` - Simulates recursive crawling
6. `FakeIsSelfLinkChecker` - Checks for self-referential links

### Coverage Goals

- **Line Coverage**: 100%
- **Branch Coverage**: 100%
- **Function Coverage**: 100%

### Priority Test Implementation Order

1. **Phase 1**: Constructor tests
2. **Phase 2**: crawl_by_type routing tests
3. **Phase 3**: _handle_text_file (simple and link collection)
4. **Phase 4**: _handle_sitemap
5. **Phase 5**: _handle_regular_webpage
6. **Phase 6**: Filtering methods (_filter_self_links, _filter_binary_files)
7. **Phase 7**: _process_link_collection (complex logic)
8. **Phase 8**: Integration workflows and edge cases

## 6. Test Data Requirements

### URLs
- Text file: "https://example.com/file.txt", "https://example.com/llms.txt"
- Markdown: "https://example.com/doc.md", "https://example.com/guide.mdx"
- Sitemap: "https://example.com/sitemap.xml"
- Regular: "https://example.com", "https://docs.python.org"

### Extracted Links (with text)
```python
[
    ("https://example.com/page1", "Page 1"),
    ("https://example.com/doc.pdf", "PDF Document"),
    ("https://example.com", "Home"),  # Self-link
    ("https://other.com/resource", "External Resource"),
]
```

### Crawl Results
```python
[
    {"url": "https://example.com/page1", "markdown": "Content 1", "success": True},
    {"url": "https://example.com/page2", "markdown": "Content 2", "success": True},
]
```

### Request
```python
{
    "max_depth": 3,
    "max_concurrent": 5,
}
```

## 7. Notes and Recommendations

### Critical Issues to Address Before Testing

NONE - Code is well-structured and ready for testing

### Testing Best Practices

1. **Async Tests**: Use pytest-asyncio
2. **Fake Completeness**: Ensure all fakes accurately simulate real behavior
3. **Filtering Tests**: Test filtering logic thoroughly (edge cases matter)
4. **Progress Callbacks**: Verify they're passed through correctly

### Testing Patterns

#### Testing URL Type Routing
```python
@pytest.mark.asyncio
async def test_routing_pattern():
    # Setup fakes
    url_handler = FakeURLHandler()
    # Configure URL type
    url_handler.txt_urls.add("https://example.com/file.txt")

    # Create handler
    handler = UrlTypeHandler(url_handler, ...)

    # Test routing
    results, crawl_type = await handler.crawl_by_type(
        "https://example.com/file.txt", {}
    )

    # Verify correct path taken
    assert crawl_type == "text_file"
```

### Future Improvements

1. **Configurable Filtering**: Allow disabling certain filters
2. **Link Validation**: Add URL validation before crawling
3. **Duplicate Detection**: Filter duplicate links before crawling
4. **Error Handling**: Add retry logic for failed crawls
5. **Metrics**: Track filtering statistics (how many links filtered)

### Additional Test Utilities

#### Link Builder
```python
def build_links_with_text(urls: list[str], texts: Optional[list[str]] = None) -> list[tuple[str, str]]:
    """Build list of (url, text) tuples."""
    if texts is None:
        texts = [f"Link {i}" for i in range(len(urls))]
    return list(zip(urls, texts))
```

#### Crawl Result Builder
```python
def build_crawl_result(url: str, content: str = "Content", success: bool = True) -> dict:
    """Build a crawl result dictionary."""
    return {
        "url": url,
        "markdown": content,
        "success": success,
    }
```
