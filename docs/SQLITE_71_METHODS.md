# SQLite Implementation - All 71 Methods Documentation

This document lists all 71 abstract methods from the DatabaseRepository interface that need SQLite query implementations.

## Current Status
- ✅ All methods have stub implementations that return appropriate empty/default values
- ❌ No actual SQLite queries implemented yet
- 📋 Methods are organized by functional category

## Implementation Checklist

### 1. Page Metadata Operations (3 methods)

- [ ] `get_page_metadata_by_id()` - Retrieve page metadata by page ID.
- [ ] `get_page_metadata_by_url()` - Retrieve page metadata by URL.
- [ ] `upsert_page_metadata_batch()` - Insert or update multiple page metadata records in a batch.

### 10. Crawled Page Operations (5 methods)

- [ ] `delete_crawled_pages_by_urls()` - Delete crawled pages by a list of URLs.
- [ ] `get_crawled_page_by_url()` - Get a crawled page by URL.
- [ ] `insert_crawled_page()` - Insert a new crawled page.
- [ ] `insert_crawled_pages_batch()` - Insert multiple crawled pages in a batch.
- [ ] `upsert_crawled_page()` - Insert or update a crawled page.

### 11. Migration Operations (3 methods)

- [ ] `get_applied_migrations()` - Retrieve all applied migrations from archon_migrations table.
- [ ] `migration_exists()` - Check if a migration has been applied.
- [ ] `record_migration()` - Record a migration as applied.

### 12. RPC Operations (1 methods)

- [ ] `execute_rpc()` - Execute a database RPC (Remote Procedure Call) function.

### 13. Prompt Operations (1 methods)

- [ ] `get_all_prompts()` - Retrieve all prompts from the archon_prompts table.

### 14. Utility Operations (1 methods)

- [ ] `get_table_count()` - Get the count of records in a specified table.

### 15. Other Operations (1 methods)

- [ ] `update_page_chunk_count()` - Update the chunk_count field for a page after chunking is complete.

### 2. Document Search Operations (2 methods)

- [ ] `search_documents_hybrid()` - Perform hybrid search combining vector and full-text search.
- [ ] `search_documents_vector()` - Perform vector similarity search on documents.

### 3. Document Operations (5 methods)

- [ ] `delete_documents_by_source()` - Delete all documents for a source.
- [ ] `get_document_by_id()` - Get a specific document by ID.
- [ ] `get_documents_by_source()` - Get all document chunks for a source.
- [ ] `insert_document()` - Insert a new document chunk.
- [ ] `insert_documents_batch()` - Insert multiple document chunks in a batch.

### 4. Code Example Operations (7 methods)

- [ ] `delete_code_examples_by_source()` - Delete all code examples for a source.
- [ ] `delete_code_examples_by_url()` - Delete all code examples for a specific URL.
- [ ] `get_code_example_count_by_source()` - Get the count of code examples for a source.
- [ ] `get_code_examples_by_source()` - Get all code examples for a source.
- [ ] `insert_code_example()` - Insert a new code example.
- [ ] `insert_code_examples_batch()` - Insert multiple code examples in a batch.
- [ ] `search_code_examples()` - Search for code examples using vector similarity.

### 5. Settings Operations (7 methods)

- [ ] `delete_setting()` - Delete a setting by key.
- [ ] `get_all_setting_records()` - Retrieve all setting records with full details.
- [ ] `get_all_settings()` - Retrieve all settings as a dictionary.
- [ ] `get_setting_records_by_category()` - Retrieve setting records filtered by category.
- [ ] `get_settings_by_key()` - Retrieve a setting value by its key.
- [ ] `upsert_setting()` - Insert or update a setting.
- [ ] `upsert_setting_record()` - Insert or update a full setting record.

### 6. Project Operations (14 methods)

- [ ] `create_project()` - Create a new project.
- [ ] `delete_project()` - Delete a project.
- [ ] `get_all_project_task_counts()` - Get task counts for all projects in a single query.
- [ ] `get_project_by_id()` - Get a specific project by ID.
- [ ] `get_project_features()` - Get features from a project's features JSONB field.
- [ ] `get_sources_for_project()` - Get full source objects for a list of source IDs.
- [ ] `get_task_counts_by_project()` - Get task counts grouped by status for a project.
- [ ] `get_tasks_by_project_and_status()` - Get tasks filtered by project, status, and optionally task_order.
- [ ] `link_project_source()` - Link a source to a project.
- [ ] `list_project_sources()` - List sources linked to a project.
- [ ] `list_projects()` - List all projects.
- [ ] `unlink_project_source()` - Unlink a source from a project.
- [ ] `unpin_all_projects_except()` - Unpin all projects except the specified one.
- [ ] `update_project()` - Update a project with specified fields.

### 7. Task Operations (6 methods)

- [ ] `archive_task()` - Archive a task (soft delete).
- [ ] `create_task()` - Create a new task.
- [ ] `delete_task()` - Delete a task (hard delete).
- [ ] `get_task_by_id()` - Get a specific task by ID.
- [ ] `list_tasks()` - List tasks with various filters.
- [ ] `update_task()` - Update a task with specified fields.

### 8. Source Operations (11 methods)

- [ ] `delete_crawled_pages_by_source()` - Delete all crawled pages for a source.
- [ ] `delete_source()` - Delete a source (CASCADE deletes related records).
- [ ] `get_first_url_by_sources()` - Get the first (oldest) URL for each source.
- [ ] `get_page_count_by_source()` - Get the count of pages for a source.
- [ ] `get_source_by_id()` - Get a specific source by ID.
- [ ] `list_crawled_pages_by_source()` - List crawled pages for a source.
- [ ] `list_pages_by_source()` - List all pages for a given source.
- [ ] `list_sources()` - List all sources, optionally filtered by knowledge type.
- [ ] `list_sources_with_pagination()` - List sources with search, filtering, and pagination.
- [ ] `update_source_metadata()` - Update source metadata.
- [ ] `upsert_source()` - Insert or update a source.

### 9. Document Version Operations (4 methods)

- [ ] `create_document_version()` - Create a new document version.
- [ ] `delete_document_version()` - Delete a document version.
- [ ] `get_document_version_by_id()` - Get a specific document version by ID.
- [ ] `list_document_versions()` - List document versions for a project.

## Detailed Method Specifications

## 1. Page Metadata Operations

### `get_page_metadata_by_id()`

```python
async def get_page_metadata_by_id(page_id: str) -> dict[str, Any] | None
```

**Purpose:** Retrieve page metadata by page ID.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_page_metadata_by_url()`

```python
async def get_page_metadata_by_url(url: str) -> dict[str, Any] | None
```

**Purpose:** Retrieve page metadata by URL.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `upsert_page_metadata_batch()`

```python
async def upsert_page_metadata_batch(pages: list[dict[str, Any]]) -> list[dict[str, Any]]
```

**Purpose:** Insert or update multiple page metadata records in a batch.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

## 10. Crawled Page Operations

### `delete_crawled_pages_by_urls()`

```python
async def delete_crawled_pages_by_urls(urls: list[str]) -> int
```

**Purpose:** Delete crawled pages by a list of URLs.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_crawled_page_by_url()`

```python
async def get_crawled_page_by_url(url: str, source_id: str | None = None) -> dict[str, Any] | None
```

**Purpose:** Get a crawled page by URL.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `insert_crawled_page()`

```python
async def insert_crawled_page(page_data: dict[str, Any]) -> dict[str, Any]
```

**Purpose:** Insert a new crawled page.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `insert_crawled_pages_batch()`

```python
async def insert_crawled_pages_batch(pages: list[dict[str, Any]]) -> list[dict[str, Any]]
```

**Purpose:** Insert multiple crawled pages in a batch.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `upsert_crawled_page()`

```python
async def upsert_crawled_page(page_data: dict[str, Any]) -> dict[str, Any]
```

**Purpose:** Insert or update a crawled page.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

## 11. Migration Operations

### `get_applied_migrations()`

```python
async def get_applied_migrations() -> list[dict[str, Any]]
```

**Purpose:** Retrieve all applied migrations from archon_migrations table.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `migration_exists()`

```python
async def migration_exists(migration_name: str) -> bool
```

**Purpose:** Check if a migration has been applied.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `record_migration()`

```python
async def record_migration(migration_data: dict[str, Any]) -> dict[str, Any]
```

**Purpose:** Record a migration as applied.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

## 12. RPC Operations

### `execute_rpc()`

```python
async def execute_rpc(function_name: str, params: dict[str, Any]) -> list[dict[str, Any]]
```

**Purpose:** Execute a database RPC (Remote Procedure Call) function.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

## 13. Prompt Operations

### `get_all_prompts()`

```python
async def get_all_prompts() -> list[dict[str, Any]]
```

**Purpose:** Retrieve all prompts from the archon_prompts table.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

## 14. Utility Operations

### `get_table_count()`

```python
async def get_table_count(table_name: str) -> int
```

**Purpose:** Get the count of records in a specified table.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

## 15. Other Operations

### `update_page_chunk_count()`

```python
async def update_page_chunk_count(page_id: str, chunk_count: int) -> dict[str, Any] | None
```

**Purpose:** Update the chunk_count field for a page after chunking is complete.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

## 2. Document Search Operations

### `search_documents_hybrid()`

```python
async def search_documents_hybrid(
    query: str,
    query_embedding: list[float],
    match_count: int = 5,
    filter_metadata: dict[str, Any] | None = None
) -> list[dict[str, Any]]
```

**Purpose:** Perform hybrid search combining vector and full-text search.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `search_documents_vector()`

```python
async def search_documents_vector(
    query_embedding: list[float],
    match_count: int = 5,
    filter_metadata: dict[str, Any] | None = None
) -> list[dict[str, Any]]
```

**Purpose:** Perform vector similarity search on documents.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

## 3. Document Operations

### `delete_documents_by_source()`

```python
async def delete_documents_by_source(source_id: str) -> int
```

**Purpose:** Delete all documents for a source.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_document_by_id()`

```python
async def get_document_by_id(document_id: str) -> dict[str, Any] | None
```

**Purpose:** Get a specific document by ID.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_documents_by_source()`

```python
async def get_documents_by_source(source_id: str, limit: int | None = None) -> list[dict[str, Any]]
```

**Purpose:** Get all document chunks for a source.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `insert_document()`

```python
async def insert_document(document_data: dict[str, Any]) -> dict[str, Any]
```

**Purpose:** Insert a new document chunk.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `insert_documents_batch()`

```python
async def insert_documents_batch(documents: list[dict[str, Any]]) -> list[dict[str, Any]]
```

**Purpose:** Insert multiple document chunks in a batch.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

## 4. Code Example Operations

### `delete_code_examples_by_source()`

```python
async def delete_code_examples_by_source(source_id: str) -> int
```

**Purpose:** Delete all code examples for a source.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `delete_code_examples_by_url()`

```python
async def delete_code_examples_by_url(url: str) -> int
```

**Purpose:** Delete all code examples for a specific URL.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_code_example_count_by_source()`

```python
async def get_code_example_count_by_source(source_id: str) -> int
```

**Purpose:** Get the count of code examples for a source.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_code_examples_by_source()`

```python
async def get_code_examples_by_source(source_id: str, limit: int | None = None) -> list[dict[str, Any]]
```

**Purpose:** Get all code examples for a source.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `insert_code_example()`

```python
async def insert_code_example(code_example_data: dict[str, Any]) -> dict[str, Any]
```

**Purpose:** Insert a new code example.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `insert_code_examples_batch()`

```python
async def insert_code_examples_batch(code_examples: list[dict[str, Any]]) -> list[dict[str, Any]]
```

**Purpose:** Insert multiple code examples in a batch.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `search_code_examples()`

```python
async def search_code_examples(
    query_embedding: list[float],
    match_count: int = 10,
    filter_metadata: dict[str, Any] | None = None,
    source_id: str | None = None
) -> list[dict[str, Any]]
```

**Purpose:** Search for code examples using vector similarity.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

## 5. Settings Operations

### `delete_setting()`

```python
async def delete_setting(key: str) -> bool
```

**Purpose:** Delete a setting by key.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_all_setting_records()`

```python
async def get_all_setting_records() -> list[dict[str, Any]]
```

**Purpose:** Retrieve all setting records with full details.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_all_settings()`

```python
async def get_all_settings() -> dict[str, Any]
```

**Purpose:** Retrieve all settings as a dictionary.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_setting_records_by_category()`

```python
async def get_setting_records_by_category(category: str) -> list[dict[str, Any]]
```

**Purpose:** Retrieve setting records filtered by category.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_settings_by_key()`

```python
async def get_settings_by_key(key: str) -> Any | None
```

**Purpose:** Retrieve a setting value by its key.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `upsert_setting()`

```python
async def upsert_setting(key: str, value: Any) -> dict[str, Any]
```

**Purpose:** Insert or update a setting.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `upsert_setting_record()`

```python
async def upsert_setting_record(setting_data: dict[str, Any]) -> dict[str, Any]
```

**Purpose:** Insert or update a full setting record.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

## 6. Project Operations

### `create_project()`

```python
async def create_project(project_data: dict[str, Any]) -> dict[str, Any]
```

**Purpose:** Create a new project.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `delete_project()`

```python
async def delete_project(project_id: str) -> bool
```

**Purpose:** Delete a project.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_all_project_task_counts()`

```python
async def get_all_project_task_counts() -> dict[str, dict[str, int]]
```

**Purpose:** Get task counts for all projects in a single query.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_project_by_id()`

```python
async def get_project_by_id(project_id: str) -> dict[str, Any] | None
```

**Purpose:** Get a specific project by ID.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_project_features()`

```python
async def get_project_features(project_id: str) -> list[dict[str, Any]]
```

**Purpose:** Get features from a project's features JSONB field.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_sources_for_project()`

```python
async def get_sources_for_project(project_id: str, source_ids: list[str]) -> list[dict[str, Any]]
```

**Purpose:** Get full source objects for a list of source IDs.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_task_counts_by_project()`

```python
async def get_task_counts_by_project(project_id: str) -> dict[str, int]
```

**Purpose:** Get task counts grouped by status for a project.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_tasks_by_project_and_status()`

```python
async def get_tasks_by_project_and_status(project_id: str, status: str, task_order_gte: int | None = None) -> list[dict[str, Any]]
```

**Purpose:** Get tasks filtered by project, status, and optionally task_order.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `link_project_source()`

```python
async def link_project_source(project_id: str, source_id: str, notes: str | None = None) -> dict[str, Any]
```

**Purpose:** Link a source to a project.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `list_project_sources()`

```python
async def list_project_sources(project_id: str, notes_filter: str | None = None) -> list[dict[str, Any]]
```

**Purpose:** List sources linked to a project.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `list_projects()`

```python
async def list_projects(
    include_content: bool = True,
    order_by: str = 'created_at',
    desc: bool = True
) -> list[dict[str, Any]]
```

**Purpose:** List all projects.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `unlink_project_source()`

```python
async def unlink_project_source(project_id: str, source_id: str) -> bool
```

**Purpose:** Unlink a source from a project.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `unpin_all_projects_except()`

```python
async def unpin_all_projects_except(project_id: str) -> int
```

**Purpose:** Unpin all projects except the specified one.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `update_project()`

```python
async def update_project(project_id: str, update_data: dict[str, Any]) -> dict[str, Any] | None
```

**Purpose:** Update a project with specified fields.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

## 7. Task Operations

### `archive_task()`

```python
async def archive_task(task_id: str, archived_by: str = 'system') -> dict[str, Any] | None
```

**Purpose:** Archive a task (soft delete).

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `create_task()`

```python
async def create_task(task_data: dict[str, Any]) -> dict[str, Any]
```

**Purpose:** Create a new task.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `delete_task()`

```python
async def delete_task(task_id: str) -> bool
```

**Purpose:** Delete a task (hard delete).

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_task_by_id()`

```python
async def get_task_by_id(task_id: str) -> dict[str, Any] | None
```

**Purpose:** Get a specific task by ID.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `list_tasks()`

```python
async def list_tasks(
    project_id: str | None = None,
    status: str | None = None,
    assignee: str | None = None,
    include_archived: bool = False,
    exclude_large_fields: bool = False,
    search_query: str | None = None,
    order_by: str = 'task_order'
) -> list[dict[str, Any]]
```

**Purpose:** List tasks with various filters.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `update_task()`

```python
async def update_task(task_id: str, update_data: dict[str, Any]) -> dict[str, Any] | None
```

**Purpose:** Update a task with specified fields.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

## 8. Source Operations

### `delete_crawled_pages_by_source()`

```python
async def delete_crawled_pages_by_source(source_id: str) -> int
```

**Purpose:** Delete all crawled pages for a source.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `delete_source()`

```python
async def delete_source(source_id: str) -> bool
```

**Purpose:** Delete a source (CASCADE deletes related records).

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_first_url_by_sources()`

```python
async def get_first_url_by_sources(source_ids: list[str]) -> dict[str, str]
```

**Purpose:** Get the first (oldest) URL for each source.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_page_count_by_source()`

```python
async def get_page_count_by_source(source_id: str) -> int
```

**Purpose:** Get the count of pages for a source.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_source_by_id()`

```python
async def get_source_by_id(source_id: str) -> dict[str, Any] | None
```

**Purpose:** Get a specific source by ID.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `list_crawled_pages_by_source()`

```python
async def list_crawled_pages_by_source(source_id: str, limit: int | None = None, offset: int | None = None) -> list[dict[str, Any]]
```

**Purpose:** List crawled pages for a source.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `list_pages_by_source()`

```python
async def list_pages_by_source(source_id: str, limit: int | None = None, offset: int | None = None) -> list[dict[str, Any]]
```

**Purpose:** List all pages for a given source.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `list_sources()`

```python
async def list_sources(knowledge_type: str | None = None) -> list[dict[str, Any]]
```

**Purpose:** List all sources, optionally filtered by knowledge type.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `list_sources_with_pagination()`

```python
async def list_sources_with_pagination(
    knowledge_type: str | None = None,
    search_query: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    order_by: str = 'updated_at',
    desc: bool = True,
    select_fields: str | None = None
) -> tuple[list[dict[str, Any]], int]
```

**Purpose:** List sources with search, filtering, and pagination.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `update_source_metadata()`

```python
async def update_source_metadata(source_id: str, metadata: dict[str, Any]) -> dict[str, Any] | None
```

**Purpose:** Update source metadata.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `upsert_source()`

```python
async def upsert_source(source_data: dict[str, Any]) -> dict[str, Any]
```

**Purpose:** Insert or update a source.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

## 9. Document Version Operations

### `create_document_version()`

```python
async def create_document_version(version_data: dict[str, Any]) -> dict[str, Any]
```

**Purpose:** Create a new document version.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `delete_document_version()`

```python
async def delete_document_version(version_id: str) -> bool
```

**Purpose:** Delete a document version.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `get_document_version_by_id()`

```python
async def get_document_version_by_id(version_id: str) -> dict[str, Any] | None
```

**Purpose:** Get a specific document version by ID.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

### `list_document_versions()`

```python
async def list_document_versions(project_id: str, limit: int | None = None) -> list[dict[str, Any]]
```

**Purpose:** List document versions for a project.

**SQLite Implementation Needed:**
- [ ] Write SQL query
- [ ] Handle transactions if needed
- [ ] Add proper error handling
- [ ] Test with sample data

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total Methods | 71 |
| Categories | 15 |
| Implemented | 0 |
| Remaining | 71 |

## Implementation Priority

### 🔴 High Priority (Core Functionality)
1. **Settings Operations** - Required for configuration persistence
2. **Source Operations** - Required for knowledge base management
3. **Document Operations** - Required for content storage and retrieval
4. **Document Search Operations** - Required for RAG functionality

### 🟡 Medium Priority (Features)
5. **Project Operations** - For project management features
6. **Task Operations** - For task tracking functionality
7. **Page Metadata Operations** - For documentation storage
8. **Code Example Operations** - For code snippet management

### 🟢 Low Priority (Advanced/Optional)
9. **Document Version Operations** - For version control features
10. **Crawled Page Operations** - For web crawling functionality
11. **Migration Operations** - Already handled by Flyway
12. **RPC Operations** - For stored procedures (may not be needed)
13. **Prompt Operations** - For prompt management
14. **Utility Operations** - Helper functions

## Next Steps

1. Start with high-priority methods
2. Implement actual SQLite queries using aiosqlite
3. Add proper error handling and logging
4. Write unit tests for each implemented method
5. Update this document as methods are completed
