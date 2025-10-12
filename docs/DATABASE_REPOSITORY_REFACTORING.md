# Database Repository Pattern Refactoring

## 1. Executive Summary

### Project Overview

This documentation describes the ongoing refactoring of Archon's data access layer from direct Supabase client calls to a repository pattern. The repository pattern provides a clean abstraction over database operations, enabling dependency injection, improved testability, and better separation of concerns.

### Refactoring Goals

- **Testability**: Enable unit testing of services without requiring a live database connection
- **Maintainability**: Centralize database operations in a single, well-defined interface
- **Flexibility**: Allow different implementations (production Supabase, in-memory fake, future database migrations)
- **Separation of Concerns**: Decouple business logic from data access implementation details
- **Type Safety**: Provide clear contracts for database operations with explicit typing

### Current Status

**Phase**: Initial Implementation Complete
**Files Refactored**: 2 service files (BaseSearchStrategy, RAGService)
**Remaining Work**: 21 service classes with ~145 database calls
**Interface**: Complete - 87 methods across 11 domains
**Implementations**: 3 (DatabaseRepository interface, SupabaseDatabaseRepository, FakeDatabaseRepository)

### Success Metrics

- **Zero Direct Database Calls**: Services use repository interface exclusively
- **Test Coverage**: All refactored services can be tested with FakeDatabaseRepository
- **No Breaking Changes**: Existing API contracts remain unchanged
- **Performance**: No degradation in query performance
- **Code Quality**: Reduced coupling between business logic and data access

---

## 2. Architecture Changes

### Before: Direct Database Access

```
┌─────────────────────────────────────────────────┐
│                 Service Layer                    │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐            │
│  │ProjectService│  │  RAGService  │  ...        │
│  └──────┬───────┘  └──────┬───────┘            │
│         │                  │                     │
│         │ Direct Calls     │ Direct Calls        │
│         ▼                  ▼                     │
│  ┌──────────────────────────────────────┐       │
│  │       Supabase Client                │       │
│  │  .table().select().execute()         │       │
│  │  .rpc().execute()                    │       │
│  └──────────────────────────────────────┘       │
└─────────────────────────────────────────────────┘
                    │
                    ▼
            ┌──────────────┐
            │   Database   │
            │  (Supabase)  │
            └──────────────┘
```

**Problems**:
- Services tightly coupled to Supabase implementation
- Difficult to unit test without database
- Database logic scattered across service files
- Hard to mock or stub database operations
- No clear contract for database operations

### After: Repository Pattern

```
┌────────────────────────────────────────────────────────┐
│                    Service Layer                        │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐                   │
│  │ProjectService│  │  RAGService  │  ...               │
│  └──────┬───────┘  └──────┬───────┘                   │
│         │ Inject           │ Inject                    │
│         ▼                  ▼                           │
│  ┌─────────────────────────────────────────────┐      │
│  │   DatabaseRepository (Interface)            │      │
│  │   - 87 abstract methods                     │      │
│  │   - 11 domain areas                         │      │
│  └─────────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ Supabase Impl    │    │   Fake Impl      │
│ (Production)     │    │   (Testing)      │
│                  │    │                  │
│ Uses Supabase    │    │ In-Memory Dict   │
│ Client           │    │ Storage          │
└────────┬─────────┘    └──────────────────┘
         │
         ▼
   ┌──────────────┐
   │   Database   │
   │  (Supabase)  │
   └──────────────┘
```

**Benefits**:
- Services depend on abstraction, not concrete implementation
- Easy to unit test with FakeDatabaseRepository
- Database operations centralized and documented
- Clear contract via interface definition
- Can swap implementations without changing services

### Repository Pattern Explanation

The repository pattern acts as a collection-like interface for accessing domain objects. Key principles:

1. **Single Responsibility**: Each repository method does one thing well
2. **Abstraction**: Services work with the interface, not implementation
3. **Dependency Injection**: Repository is injected into services
4. **Testability**: Fake implementations enable fast unit tests
5. **Flexibility**: Easy to change database technology

---

## 3. Repository Interface Documentation

### Interface Organization

The `DatabaseRepository` interface is organized into 11 domain areas:

1. **Page Metadata Operations** (4 methods) - Query page metadata and counts
2. **Document Search Operations** (8 methods) - Vector search and document management
3. **Code Examples Operations** (6 methods) - Code snippet search and storage
4. **Settings Operations** (4 methods) - Application settings management
5. **Project Operations** (7 methods) - Project CRUD and features
6. **Task Operations** (10 methods) - Task management and queries
7. **Source Operations** (5 methods) - Knowledge source management
8. **Crawled Pages Operations** (5 methods) - Web crawling data storage
9. **Document Version Operations** (4 methods) - Version history tracking
10. **Project Source Linking Operations** (4 methods) - Many-to-many relationships
11. **RPC Operations** (1 method) - Stored procedure execution

### Method Signatures by Domain

#### 1. Page Metadata Operations

```python
async def get_page_metadata_by_id(self, page_id: str) -> Optional[dict[str, Any]]
async def get_page_metadata_by_url(self, url: str) -> Optional[dict[str, Any]]
async def list_pages_by_source(self, source_id: str, limit: Optional[int] = None,
                                offset: Optional[int] = None) -> list[dict[str, Any]]
async def get_page_count_by_source(self, source_id: str) -> int
```

**Purpose**: Query page-level metadata for crawled documentation pages.

**Usage Example**:
```python
# Get metadata for a specific page
page = await repository.get_page_metadata_by_id("page-123")
if page:
    print(f"Page: {page['section_title']} - {page['word_count']} words")

# Count pages for a source
count = await repository.get_page_count_by_source("source-456")
print(f"Source has {count} pages")
```

#### 2. Document Search Operations

```python
async def search_documents_vector(self, query_embedding: list[float],
                                   match_count: int = 5,
                                   filter_metadata: Optional[dict[str, Any]] = None
                                   ) -> list[dict[str, Any]]

async def search_documents_hybrid(self, query: str, query_embedding: list[float],
                                   match_count: int = 5,
                                   filter_metadata: Optional[dict[str, Any]] = None
                                   ) -> list[dict[str, Any]]

async def get_documents_by_source(self, source_id: str,
                                   limit: Optional[int] = None) -> list[dict[str, Any]]

async def get_document_by_id(self, document_id: str) -> Optional[dict[str, Any]]

async def insert_document(self, document_data: dict[str, Any]) -> dict[str, Any]

async def insert_documents_batch(self, documents: list[dict[str, Any]]
                                 ) -> list[dict[str, Any]]

async def delete_documents_by_source(self, source_id: str) -> int
```

**Purpose**: Core RAG functionality - vector search, document retrieval, and batch operations.

**Usage Example**:
```python
# Vector search
embedding = await create_embedding("search query")
results = await repository.search_documents_vector(
    query_embedding=embedding,
    match_count=10,
    filter_metadata={"source": "docs.python.org"}
)

# Batch insert documents
documents = [{"content": "text", "source_id": "src-1", ...}]
inserted = await repository.insert_documents_batch(documents)
print(f"Inserted {len(inserted)} documents")
```

#### 3. Code Examples Operations

```python
async def search_code_examples(self, query_embedding: list[float],
                                match_count: int = 10,
                                filter_metadata: Optional[dict[str, Any]] = None,
                                source_id: Optional[str] = None
                                ) -> list[dict[str, Any]]

async def get_code_examples_by_source(self, source_id: str,
                                       limit: Optional[int] = None
                                       ) -> list[dict[str, Any]]

async def get_code_example_count_by_source(self, source_id: str) -> int

async def insert_code_example(self, code_example_data: dict[str, Any]
                               ) -> dict[str, Any]

async def insert_code_examples_batch(self, code_examples: list[dict[str, Any]]
                                      ) -> list[dict[str, Any]]

async def delete_code_examples_by_source(self, source_id: str) -> int
```

**Purpose**: Store and retrieve code snippets with vector embeddings.

**Usage Example**:
```python
# Search for code examples
code_embedding = await create_embedding("how to use asyncio")
examples = await repository.search_code_examples(
    query_embedding=code_embedding,
    match_count=5,
    source_id="python-docs"
)

for ex in examples:
    print(f"Language: {ex['metadata']['language']}")
    print(f"Code: {ex['content'][:100]}...")
```

#### 4. Settings Operations

```python
async def get_settings_by_key(self, key: str) -> Optional[Any]

async def get_all_settings(self) -> dict[str, Any]

async def upsert_setting(self, key: str, value: Any) -> dict[str, Any]

async def delete_setting(self, key: str) -> bool
```

**Purpose**: Persistent application configuration storage.

**Usage Example**:
```python
# Get a setting
model = await repository.get_settings_by_key("default_llm_model")

# Update or create setting
await repository.upsert_setting("max_results", 20)

# Get all settings
all_settings = await repository.get_all_settings()
```

#### 5. Project Operations

```python
async def create_project(self, project_data: dict[str, Any]) -> dict[str, Any]

async def list_projects(self, include_content: bool = True,
                        order_by: str = "created_at",
                        desc: bool = True) -> list[dict[str, Any]]

async def get_project_by_id(self, project_id: str) -> Optional[dict[str, Any]]

async def update_project(self, project_id: str,
                         update_data: dict[str, Any]) -> Optional[dict[str, Any]]

async def delete_project(self, project_id: str) -> bool

async def unpin_all_projects_except(self, project_id: str) -> int

async def get_project_features(self, project_id: str) -> list[dict[str, Any]]
```

**Purpose**: Manage projects - the core organizational unit.

**Usage Example**:
```python
# Create a new project
project = await repository.create_project({
    "name": "My API",
    "description": "REST API project",
    "features": []
})

# Update project
await repository.update_project(project["id"], {
    "status": "in_progress",
    "features": [{"name": "auth", "status": "done"}]
})

# Unpin other projects when pinning one
await repository.unpin_all_projects_except(project["id"])
```

#### 6. Task Operations

```python
async def create_task(self, task_data: dict[str, Any]) -> dict[str, Any]

async def list_tasks(self, project_id: Optional[str] = None,
                     status: Optional[str] = None,
                     assignee: Optional[str] = None,
                     include_archived: bool = False,
                     exclude_large_fields: bool = False,
                     search_query: Optional[str] = None,
                     order_by: str = "task_order") -> list[dict[str, Any]]

async def get_task_by_id(self, task_id: str) -> Optional[dict[str, Any]]

async def update_task(self, task_id: str,
                      update_data: dict[str, Any]) -> Optional[dict[str, Any]]

async def delete_task(self, task_id: str) -> bool

async def archive_task(self, task_id: str, archived_by: str = "system"
                       ) -> Optional[dict[str, Any]]

async def get_tasks_by_project_and_status(self, project_id: str, status: str,
                                           task_order_gte: Optional[int] = None
                                           ) -> list[dict[str, Any]]

async def get_task_counts_by_project(self, project_id: str) -> dict[str, int]

async def get_all_project_task_counts(self) -> dict[str, dict[str, int]]
```

**Purpose**: Comprehensive task management with flexible querying.

**Usage Example**:
```python
# List tasks with filters
tasks = await repository.list_tasks(
    project_id="proj-123",
    status="todo",
    search_query="authentication"
)

# Get task counts for dashboard
counts = await repository.get_task_counts_by_project("proj-123")
# Returns: {"todo": 5, "doing": 2, "review": 1, "done": 12}

# Archive a task (soft delete)
await repository.archive_task("task-456", archived_by="user-789")
```

#### 7. Source Operations

```python
async def list_sources(self, knowledge_type: Optional[str] = None
                       ) -> list[dict[str, Any]]

async def get_source_by_id(self, source_id: str) -> Optional[dict[str, Any]]

async def upsert_source(self, source_data: dict[str, Any]) -> dict[str, Any]

async def update_source_metadata(self, source_id: str,
                                 metadata: dict[str, Any]
                                 ) -> Optional[dict[str, Any]]

async def delete_source(self, source_id: str) -> bool
```

**Purpose**: Manage knowledge sources (crawled websites, uploaded documents).

**Usage Example**:
```python
# Create or update a source
source = await repository.upsert_source({
    "source_id": "python-docs",
    "url": "https://docs.python.org",
    "metadata": {"knowledge_type": "documentation"}
})

# Update metadata (merges with existing)
await repository.update_source_metadata("python-docs", {
    "last_crawled": "2024-01-15",
    "page_count": 450
})

# Delete source (CASCADE deletes documents, pages, code examples)
await repository.delete_source("python-docs")
```

#### 8. Crawled Pages Operations

```python
async def get_crawled_page_by_url(self, url: str,
                                   source_id: Optional[str] = None
                                   ) -> Optional[dict[str, Any]]

async def insert_crawled_page(self, page_data: dict[str, Any]) -> dict[str, Any]

async def upsert_crawled_page(self, page_data: dict[str, Any]) -> dict[str, Any]

async def delete_crawled_pages_by_source(self, source_id: str) -> int

async def list_crawled_pages_by_source(self, source_id: str,
                                        limit: Optional[int] = None,
                                        offset: Optional[int] = None
                                        ) -> list[dict[str, Any]]
```

**Purpose**: Track individual pages during web crawling operations.

**Usage Example**:
```python
# Check if page already crawled
existing = await repository.get_crawled_page_by_url(
    "https://docs.python.org/3/library/asyncio.html",
    source_id="python-docs"
)

# Upsert page (insert or update)
page = await repository.upsert_crawled_page({
    "url": "https://docs.python.org/3/library/asyncio.html",
    "source_id": "python-docs",
    "title": "asyncio — Asynchronous I/O",
    "content": "...",
    "crawled_at": datetime.now().isoformat()
})
```

#### 9. Document Version Operations

```python
async def create_document_version(self, version_data: dict[str, Any]
                                   ) -> dict[str, Any]

async def list_document_versions(self, project_id: str,
                                  limit: Optional[int] = None
                                  ) -> list[dict[str, Any]]

async def get_document_version_by_id(self, version_id: str
                                      ) -> Optional[dict[str, Any]]

async def delete_document_version(self, version_id: str) -> bool
```

**Purpose**: Track document version history for projects.

**Usage Example**:
```python
# Create a version snapshot
version = await repository.create_document_version({
    "project_id": "proj-123",
    "document_name": "api_spec.md",
    "content": "# API Specification\n...",
    "version_number": "1.2.0",
    "notes": "Added authentication endpoints"
})

# List version history
versions = await repository.list_document_versions("proj-123", limit=10)
for v in versions:
    print(f"v{v['version_number']} - {v['created_at']}")
```

#### 10. Project Source Linking Operations

```python
async def link_project_source(self, project_id: str, source_id: str,
                               notes: Optional[str] = None
                               ) -> dict[str, Any]

async def unlink_project_source(self, project_id: str, source_id: str) -> bool

async def list_project_sources(self, project_id: str,
                                notes_filter: Optional[str] = None
                                ) -> list[dict[str, Any]]

async def get_sources_for_project(self, project_id: str, source_ids: list[str]
                                   ) -> list[dict[str, Any]]
```

**Purpose**: Manage many-to-many relationships between projects and knowledge sources.

**Usage Example**:
```python
# Link a source to a project
await repository.link_project_source(
    project_id="proj-123",
    source_id="python-docs",
    notes="technical"
)

# Get all linked sources
links = await repository.list_project_sources("proj-123")
source_ids = [link["source_id"] for link in links]

# Get full source objects
sources = await repository.get_sources_for_project("proj-123", source_ids)
```

#### 11. RPC Operations

```python
async def execute_rpc(self, function_name: str, params: dict[str, Any]
                      ) -> list[dict[str, Any]]
```

**Purpose**: Execute database stored procedures/functions for complex queries.

**Usage Example**:
```python
# Execute custom RPC function
results = await repository.execute_rpc(
    "match_documents",
    {
        "query_embedding": embedding,
        "match_count": 10,
        "filter": {"source": "python-docs"}
    }
)
```

### Error Handling Guidelines

All repository methods follow these error handling patterns:

1. **Return None**: Methods that fetch single items return `None` when not found
2. **Return Empty List**: Query methods return `[]` when no results match
3. **Raise Exceptions**: Database errors, connection failures, and validation errors are raised
4. **Log Errors**: All exceptions are logged before raising

**Example Error Handling**:
```python
try:
    project = await repository.get_project_by_id("proj-123")
    if project is None:
        # Not found - handle gracefully
        return {"error": "Project not found"}

    # Process project...

except Exception as e:
    # Database error - log and re-raise or handle
    logger.error(f"Failed to fetch project: {e}")
    raise
```

### Transaction Management

The repository interface does not currently provide explicit transaction support. Each method call is atomic at the database level.

**Future Enhancement**: Consider adding transaction context managers:
```python
async with repository.transaction():
    project = await repository.create_project({...})
    await repository.create_task({...})
    # Commit or rollback together
```

### Best Practices

1. **Always use type hints**: Helps with IDE autocomplete and type checking
2. **Check for None**: Always check if single-item queries return None
3. **Use batch operations**: Prefer `insert_documents_batch` over loops
4. **Filter at database level**: Use repository filters instead of Python filtering
5. **Handle errors gracefully**: Catch specific exceptions, not generic `Exception`

---

## 4. Implementations

### SupabaseDatabaseRepository (Production)

**Location**: `/home/jose/src/Archon/python/src/server/repositories/supabase_repository.py`

**Purpose**: Production implementation using Supabase as the database backend.

**Key Features**:
- Full implementation of all 87 interface methods
- Comprehensive error handling and logging
- Automatic timestamp management (created_at, updated_at)
- Optimized queries with proper indexing
- Support for complex filters and pagination

**Initialization**:
```python
from supabase import Client
from repositories import SupabaseDatabaseRepository

supabase_client = get_supabase_client()
repository = SupabaseDatabaseRepository(supabase_client)
```

**Database Tables Used**:
- `archon_page_metadata` - Page-level metadata
- `archon_documents` - Document chunks with embeddings
- `archon_code_examples` - Code snippets
- `archon_settings` - Application settings
- `archon_projects` - Projects
- `archon_tasks` - Tasks
- `archon_sources` - Knowledge sources
- `archon_crawled_pages` - Crawled web pages
- `archon_document_versions` - Version history
- `archon_project_sources` - Project-source links

**Performance Characteristics**:
- Vector search: ~50-200ms depending on corpus size
- Simple queries: ~10-50ms
- Batch inserts: Linear with batch size
- RPC functions: Varies by function complexity

### FakeDatabaseRepository (Testing)

**Location**: `/home/jose/src/Archon/python/src/server/repositories/fake_repository.py`

**Purpose**: In-memory implementation for fast unit testing without database dependency.

**Key Features**:
- Thread-safe operations using RLock
- In-memory dictionary storage
- UUID generation for IDs
- Simulates database behavior
- CASCADE deletes for referential integrity
- No external dependencies

**Initialization**:
```python
from repositories import FakeDatabaseRepository

# No client needed - pure in-memory
repository = FakeDatabaseRepository()
```

**Storage Structure**:
```python
{
    "page_metadata": {},      # dict[str, dict]
    "documents": {},          # dict[str, dict]
    "code_examples": {},      # dict[str, dict]
    "settings": {},           # dict[str, Any]
    "projects": {},           # dict[str, dict]
    "tasks": {},              # dict[str, dict]
    "sources": {},            # dict[str, dict]
    "crawled_pages": {},      # dict[str, dict]
    "document_versions": {}, # dict[str, dict]
    "project_sources": []     # list[dict]
}
```

**Test Example**:
```python
import pytest
from repositories import FakeDatabaseRepository

@pytest.fixture
def repository():
    return FakeDatabaseRepository()

async def test_project_creation(repository):
    # Create project
    project = await repository.create_project({
        "name": "Test Project",
        "description": "Testing"
    })

    assert project["id"] is not None
    assert project["name"] == "Test Project"

    # Verify retrieval
    fetched = await repository.get_project_by_id(project["id"])
    assert fetched["name"] == project["name"]
```

**Limitations**:
- Vector search returns simple mocks (no real similarity calculation)
- RPC functions return empty lists
- No persistence between test runs
- Simplified filtering logic

### When to Use Each Implementation

**Use SupabaseDatabaseRepository when**:
- Running production server
- Integration testing against real database
- Performance testing
- Developing new features that need real data

**Use FakeDatabaseRepository when**:
- Writing unit tests for services
- Testing business logic without database overhead
- Continuous integration pipelines
- Local development without Supabase connection

### Configuration and Setup

**Production Setup**:
```python
# In service initialization
from repositories import SupabaseDatabaseRepository
from utils import get_supabase_client

supabase_client = get_supabase_client()
db_repository = SupabaseDatabaseRepository(supabase_client)

# Inject into service
service = ProjectService(database_repository=db_repository)
```

**Test Setup**:
```python
# In test file
from repositories import FakeDatabaseRepository

@pytest.fixture
def db_repository():
    return FakeDatabaseRepository()

@pytest.fixture
def service(db_repository):
    return ProjectService(database_repository=db_repository)

async def test_feature(service):
    # Test using fake repository
    result = await service.some_method()
    assert result is not None
```

---

## 5. Migration Guide

### Step-by-Step Refactoring Process

Follow this process to refactor a service to use the repository pattern:

#### Step 1: Add Repository Parameter

Add an optional `database_repository` parameter to the service's `__init__` method:

```python
# Before
class ProjectService:
    def __init__(self, supabase_client=None):
        self.supabase_client = supabase_client or get_supabase_client()

# After
from repositories import DatabaseRepository, SupabaseDatabaseRepository

class ProjectService:
    def __init__(self, database_repository: Optional[DatabaseRepository] = None):
        if database_repository is None:
            supabase_client = get_supabase_client()
            self.db_repository = SupabaseDatabaseRepository(supabase_client)
        else:
            self.db_repository = database_repository
```

#### Step 2: Identify Database Calls

Find all direct Supabase client calls in the service:

```python
# Search patterns to find:
self.supabase_client.table(...)
self.supabase_client.rpc(...)
supabase_client.table(...)
```

Create a checklist of all methods that need refactoring.

#### Step 3: Replace Database Calls

Replace each Supabase call with the corresponding repository method:

**Before**:
```python
async def get_project(self, project_id: str):
    result = (
        self.supabase_client.table("archon_projects")
        .select("*")
        .eq("id", project_id)
        .maybe_single()
        .execute()
    )

    if result and result.data:
        return result.data
    return None
```

**After**:
```python
async def get_project(self, project_id: str):
    return await self.db_repository.get_project_by_id(project_id)
```

#### Step 4: Update Error Handling

Repository methods raise exceptions - ensure proper error handling:

```python
# Before - manual error checking
result = self.supabase_client.table(...).execute()
if not result or not result.data:
    raise ValueError("Query failed")

# After - exception handling
try:
    result = await self.db_repository.some_method(...)
except Exception as e:
    logger.error(f"Database operation failed: {e}")
    raise
```

#### Step 5: Validate Refactoring

After refactoring, verify:

1. **No Direct Calls**: Search for `self.supabase_client.table` - should find none
2. **All Async**: Ensure all repository calls use `await`
3. **Type Hints**: Verify method signatures have proper types
4. **Error Handling**: Check exception handling is appropriate

#### Step 6: Write Tests

Create or update tests using FakeDatabaseRepository:

```python
@pytest.fixture
def repository():
    return FakeDatabaseRepository()

@pytest.fixture
def service(repository):
    return YourService(database_repository=repository)

async def test_service_method(service, repository):
    # Setup test data directly in repository
    project = await repository.create_project({"name": "Test"})

    # Test service method
    result = await service.some_method(project["id"])

    # Assert results
    assert result is not None
```

### Code Examples (Before/After)

#### Example 1: Simple Query

**Before**:
```python
async def get_source(self, source_id: str):
    result = (
        self.supabase_client.table("archon_sources")
        .select("*")
        .eq("source_id", source_id)
        .maybe_single()
        .execute()
    )
    return result.data if result and result.data else None
```

**After**:
```python
async def get_source(self, source_id: str):
    return await self.db_repository.get_source_by_id(source_id)
```

#### Example 2: Insert with Error Handling

**Before**:
```python
async def create_task(self, task_data: dict):
    try:
        task_data["created_at"] = datetime.now().isoformat()
        task_data["updated_at"] = datetime.now().isoformat()

        result = (
            self.supabase_client.table("archon_tasks")
            .insert(task_data)
            .execute()
        )

        if not result.data:
            raise ValueError("Insert failed")

        logger.info(f"Created task {result.data[0]['id']}")
        return result.data[0]

    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        raise
```

**After**:
```python
async def create_task(self, task_data: dict):
    try:
        # Repository handles timestamps automatically
        task = await self.db_repository.create_task(task_data)
        logger.info(f"Created task {task['id']}")
        return task
    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        raise
```

#### Example 3: Complex Query with Filters

**Before**:
```python
async def list_tasks(self, project_id: str, status: str = None):
    query = (
        self.supabase_client.table("archon_tasks")
        .select("*")
        .eq("project_id", project_id)
    )

    if status:
        query = query.eq("status", status)

    query = query.order("task_order", desc=False)

    result = query.execute()
    return result.data if result.data else []
```

**After**:
```python
async def list_tasks(self, project_id: str, status: str = None):
    return await self.db_repository.list_tasks(
        project_id=project_id,
        status=status,
        order_by="task_order"
    )
```

#### Example 4: RPC Function Call

**Before**:
```python
async def search_documents(self, query_embedding: list[float], count: int):
    result = self.supabase_client.rpc(
        "match_documents",
        {
            "query_embedding": query_embedding,
            "match_count": count
        }
    ).execute()

    return result.data if result.data else []
```

**After**:
```python
async def search_documents(self, query_embedding: list[float], count: int):
    return await self.db_repository.search_documents_vector(
        query_embedding=query_embedding,
        match_count=count
    )
```

### Common Pitfalls to Avoid

1. **Forgetting await**: Repository methods are async - always use `await`
   ```python
   # WRONG
   project = self.db_repository.get_project_by_id(id)

   # CORRECT
   project = await self.db_repository.get_project_by_id(id)
   ```

2. **Not checking None returns**: Single-item queries can return None
   ```python
   # WRONG
   project = await self.db_repository.get_project_by_id(id)
   name = project["name"]  # May crash if None

   # CORRECT
   project = await self.db_repository.get_project_by_id(id)
   if project is None:
       raise ValueError("Project not found")
   name = project["name"]
   ```

3. **Using wrong repository method**: Match the operation to the right method
   ```python
   # WRONG - Using generic list for specific filter
   all_tasks = await self.db_repository.list_tasks()
   todo_tasks = [t for t in all_tasks if t["status"] == "todo"]

   # CORRECT - Use repository filter
   todo_tasks = await self.db_repository.list_tasks(status="todo")
   ```

4. **Assuming exceptions are caught**: Repository raises exceptions - handle them
   ```python
   # WRONG - No error handling
   project = await self.db_repository.create_project(data)

   # CORRECT - Handle errors
   try:
       project = await self.db_repository.create_project(data)
   except Exception as e:
       logger.error(f"Project creation failed: {e}")
       raise ServiceError("Could not create project")
   ```

5. **Manual timestamp management**: Repository handles this automatically
   ```python
   # WRONG - Manual timestamps
   data = {
       "name": "Project",
       "created_at": datetime.now().isoformat(),
       "updated_at": datetime.now().isoformat()
   }

   # CORRECT - Let repository handle it
   data = {"name": "Project"}
   project = await self.db_repository.create_project(data)
   ```

---

## 6. Refactoring Progress

### Files Completed

#### 1. BaseSearchStrategy
**Location**: `python/src/server/services/search/base_search_strategy.py`
**Status**: ✅ Complete
**Database Calls Eliminated**: 1 (RPC call)
**Changes**:
- Added `database_repository` parameter to `__init__`
- Replaced `self.supabase_client.rpc()` with `self.db_repository.execute_rpc()`
- Updated all tests to use FakeDatabaseRepository

#### 2. RAGService
**Location**: `python/src/server/services/search/rag_service.py`
**Status**: ✅ Complete
**Database Calls Eliminated**: 2 (page metadata queries)
**Changes**:
- Added `database_repository` parameter to `__init__`
- Replaced page metadata queries with `db_repository.get_page_metadata_by_id()` and `get_page_metadata_by_url()`
- Maintained backward compatibility with existing strategies

### Files Remaining (21 services, ~145 database calls)

Listed in priority order based on coupling and usage frequency:

#### High Priority (Core Services)

1. **ProjectService** - `python/src/server/services/project_service.py`
   - Estimated calls: ~20
   - Complexity: High
   - Dependencies: TaskService, VersioningService
   - Impact: High - core project management

2. **TaskService** - `python/src/server/services/task_service.py`
   - Estimated calls: ~15
   - Complexity: Medium
   - Dependencies: ProjectService
   - Impact: High - task management

3. **SourceManagementService** - `python/src/server/services/source_management_service.py`
   - Estimated calls: ~12
   - Complexity: Medium
   - Dependencies: CrawlingService
   - Impact: High - knowledge source management

4. **CrawlingService** - `python/src/server/services/crawling/crawling_service.py`
   - Estimated calls: ~10
   - Complexity: High
   - Dependencies: CodeExtractionService, DocumentStorageService
   - Impact: High - web crawling pipeline

#### Medium Priority (Supporting Services)

5. **HybridSearchStrategy** - `python/src/server/services/search/hybrid_search_strategy.py`
   - Estimated calls: ~5
   - Complexity: Medium
   - Dependencies: BaseSearchStrategy
   - Impact: Medium - enhanced search

6. **DocumentStorageService** - `python/src/server/services/storage/document_storage_service.py`
   - Estimated calls: ~8
   - Complexity: Medium
   - Dependencies: None
   - Impact: Medium - document upload handling

7. **VersioningService** - `python/src/server/services/version_service.py`
   - Estimated calls: ~6
   - Complexity: Low
   - Dependencies: None
   - Impact: Medium - version history

8. **DocumentService** - `python/src/server/services/document_service.py`
   - Estimated calls: ~7
   - Complexity: Medium
   - Dependencies: ProjectService
   - Impact: Medium - project documents

9. **CodeExtractionService** - `python/src/server/services/crawling/code_extraction_service.py`
   - Estimated calls: ~6
   - Complexity: Medium
   - Dependencies: None
   - Impact: Medium - code snippet extraction

10. **PageStorageOperations** - `python/src/server/services/storage/page_storage_operations.py`
    - Estimated calls: ~5
    - Complexity: Low
    - Dependencies: None
    - Impact: Medium - crawled page storage

#### Lower Priority (Specialized Services)

11. **ProjectCreationService** - `python/src/server/services/project_creation_service.py`
    - Estimated calls: ~8
    - Complexity: High
    - Dependencies: ProjectService, AgentService
    - Impact: Low - AI-assisted project creation

12. **SourceLinkingService** - `python/src/server/services/source_linking_service.py`
    - Estimated calls: ~6
    - Complexity: Low
    - Dependencies: None
    - Impact: Low - project-source relationships

13. **KnowledgeItemService** - `python/src/server/services/knowledge_item_service.py`
    - Estimated calls: ~5
    - Complexity: Low
    - Dependencies: None
    - Impact: Low - knowledge base items

14. **KnowledgeSummaryService** - `python/src/server/services/knowledge_summary_service.py`
    - Estimated calls: ~4
    - Complexity: Low
    - Dependencies: None
    - Impact: Low - lightweight summaries

15. **DatabaseMetricsService** - `python/src/server/services/database_metrics_service.py`
    - Estimated calls: ~6
    - Complexity: Medium
    - Dependencies: None
    - Impact: Low - metrics/analytics

16. **CredentialService** - `python/src/server/services/credential_service.py`
    - Estimated calls: ~4
    - Complexity: Low
    - Dependencies: None
    - Impact: Low - settings storage

17. **PromptService** - `python/src/server/services/prompt_service.py`
    - Estimated calls: ~3
    - Complexity: Low
    - Dependencies: None
    - Impact: Low - AI prompt management

18. **MigrationService** - `python/src/server/services/migration_service.py`
    - Estimated calls: ~10
    - Complexity: High
    - Dependencies: Multiple
    - Impact: Low - one-time migrations

19. **ModelDiscoveryService** - `python/src/server/services/ollama/model_discovery_service.py`
    - Estimated calls: ~3
    - Complexity: Low
    - Dependencies: None
    - Impact: Low - Ollama integration

20. **BaseStorageService** - `python/src/server/services/storage/base_storage_service.py`
    - Estimated calls: ~2
    - Complexity: Low
    - Dependencies: None
    - Impact: Low - abstract base class

21. **DocumentStorageOperations** - `python/src/server/services/storage/document_storage_operations.py`
    - Estimated calls: ~4
    - Complexity: Low
    - Dependencies: None
    - Impact: Low - document chunk storage

### Estimated Effort

**Total Remaining Work**: ~145 database calls across 21 files

**Per-Service Estimates**:
- **Simple Service** (< 5 calls): 1-2 hours
- **Medium Service** (5-15 calls): 2-4 hours
- **Complex Service** (> 15 calls): 4-8 hours

**Total Estimated Time**: 50-80 developer hours

**Breakdown by Priority**:
- High Priority (4 services): 20-30 hours
- Medium Priority (7 services): 20-30 hours
- Lower Priority (10 services): 10-20 hours

---

## 7. Testing Strategy

### Using FakeDatabaseRepository for Tests

The `FakeDatabaseRepository` enables fast, reliable unit testing without database dependencies.

#### Basic Test Setup

```python
import pytest
from repositories import FakeDatabaseRepository
from services import YourService

@pytest.fixture
def db_repository():
    """Provide a fresh fake repository for each test."""
    return FakeDatabaseRepository()

@pytest.fixture
def service(db_repository):
    """Provide a service instance with fake repository."""
    return YourService(database_repository=db_repository)
```

#### Test Patterns

**Pattern 1: Test Create Operations**
```python
async def test_create_project(service, db_repository):
    # Test service create method
    project = await service.create_project({
        "name": "Test Project",
        "description": "Testing"
    })

    assert project["id"] is not None
    assert project["name"] == "Test Project"

    # Verify it's in the repository
    fetched = await db_repository.get_project_by_id(project["id"])
    assert fetched is not None
    assert fetched["name"] == project["name"]
```

**Pattern 2: Test Read Operations**
```python
async def test_get_project(service, db_repository):
    # Setup test data directly in repository
    project = await db_repository.create_project({
        "name": "Existing Project",
        "description": "Pre-existing"
    })

    # Test service read method
    result = await service.get_project(project["id"])

    assert result is not None
    assert result["id"] == project["id"]
    assert result["name"] == "Existing Project"
```

**Pattern 3: Test Update Operations**
```python
async def test_update_project(service, db_repository):
    # Create initial project
    project = await db_repository.create_project({
        "name": "Original",
        "status": "draft"
    })

    # Test service update
    updated = await service.update_project(project["id"], {
        "name": "Updated",
        "status": "active"
    })

    assert updated["name"] == "Updated"
    assert updated["status"] == "active"

    # Verify in repository
    fetched = await db_repository.get_project_by_id(project["id"])
    assert fetched["name"] == "Updated"
```

**Pattern 4: Test Delete Operations**
```python
async def test_delete_project(service, db_repository):
    # Create project
    project = await db_repository.create_project({"name": "To Delete"})

    # Verify exists
    assert await db_repository.get_project_by_id(project["id"]) is not None

    # Test service delete
    success = await service.delete_project(project["id"])
    assert success is True

    # Verify deleted
    assert await db_repository.get_project_by_id(project["id"]) is None
```

**Pattern 5: Test Complex Queries**
```python
async def test_list_tasks_with_filters(service, db_repository):
    # Setup test data
    project = await db_repository.create_project({"name": "Test"})

    # Create multiple tasks with different statuses
    await db_repository.create_task({
        "project_id": project["id"],
        "title": "Task 1",
        "status": "todo"
    })
    await db_repository.create_task({
        "project_id": project["id"],
        "title": "Task 2",
        "status": "doing"
    })
    await db_repository.create_task({
        "project_id": project["id"],
        "title": "Task 3",
        "status": "todo"
    })

    # Test filtered query
    todo_tasks = await service.list_tasks(
        project_id=project["id"],
        status="todo"
    )

    assert len(todo_tasks) == 2
    assert all(t["status"] == "todo" for t in todo_tasks)
```

**Pattern 6: Test Error Handling**
```python
async def test_get_nonexistent_project(service):
    # Test with non-existent ID
    result = await service.get_project("nonexistent-id")

    # Should return None or raise appropriate error
    assert result is None

async def test_create_invalid_project(service):
    # Test with invalid data
    with pytest.raises(ValueError):
        await service.create_project({})  # Missing required fields
```

### Test Data Setup

**Minimal Data Setup**:
```python
@pytest.fixture
async def test_project(db_repository):
    """Provide a test project."""
    return await db_repository.create_project({
        "name": "Test Project",
        "description": "For testing"
    })

@pytest.fixture
async def test_tasks(db_repository, test_project):
    """Provide test tasks."""
    tasks = []
    for i in range(3):
        task = await db_repository.create_task({
            "project_id": test_project["id"],
            "title": f"Task {i+1}",
            "status": "todo",
            "task_order": i
        })
        tasks.append(task)
    return tasks
```

**Complex Data Setup**:
```python
@pytest.fixture
async def populated_database(db_repository):
    """Setup a fully populated test database."""
    # Create sources
    source1 = await db_repository.upsert_source({
        "source_id": "test-source-1",
        "url": "https://example.com",
        "metadata": {"type": "documentation"}
    })

    # Create projects
    project1 = await db_repository.create_project({
        "name": "Project Alpha",
        "features": []
    })
    project2 = await db_repository.create_project({
        "name": "Project Beta",
        "features": []
    })

    # Create tasks
    for i in range(5):
        await db_repository.create_task({
            "project_id": project1["id"],
            "title": f"Task {i+1}",
            "status": ["todo", "doing", "review", "done"][i % 4]
        })

    # Link projects to sources
    await db_repository.link_project_source(
        project_id=project1["id"],
        source_id=source1["source_id"]
    )

    return {
        "sources": [source1],
        "projects": [project1, project2],
    }
```

### Integration Testing Approach

While FakeDatabaseRepository is great for unit tests, integration tests should use SupabaseDatabaseRepository:

```python
@pytest.mark.integration
async def test_full_workflow():
    """Integration test with real database."""
    # Use real Supabase client
    supabase_client = get_supabase_client()
    db_repository = SupabaseDatabaseRepository(supabase_client)
    service = YourService(database_repository=db_repository)

    try:
        # Test with real database
        project = await service.create_project({...})

        # Cleanup
        await db_repository.delete_project(project["id"])

    finally:
        # Ensure cleanup happens
        pass
```

### Common Test Patterns

**Testing CASCADE Deletes**:
```python
async def test_cascade_delete(db_repository):
    # Create project with tasks
    project = await db_repository.create_project({"name": "Test"})
    task = await db_repository.create_task({
        "project_id": project["id"],
        "title": "Task"
    })

    # Delete project
    await db_repository.delete_project(project["id"])

    # Verify task is also deleted (CASCADE)
    assert await db_repository.get_task_by_id(task["id"]) is None
```

**Testing Pagination**:
```python
async def test_pagination(db_repository):
    # Create many items
    source = await db_repository.upsert_source({
        "source_id": "test",
        "url": "http://example.com"
    })

    for i in range(25):
        await db_repository.insert_crawled_page({
            "source_id": "test",
            "url": f"http://example.com/page{i}"
        })

    # Test pagination
    page1 = await db_repository.list_pages_by_source("test", limit=10, offset=0)
    page2 = await db_repository.list_pages_by_source("test", limit=10, offset=10)
    page3 = await db_repository.list_pages_by_source("test", limit=10, offset=20)

    assert len(page1) == 10
    assert len(page2) == 10
    assert len(page3) == 5

    # Verify no overlap
    page1_urls = {p["url"] for p in page1}
    page2_urls = {p["url"] for p in page2}
    assert len(page1_urls & page2_urls) == 0
```

---

## 8. Future Work

### Next Files to Refactor (Priority Order)

#### Sprint 1: Core Services (Weeks 1-2)

1. **ProjectService** (Week 1, Days 1-2)
   - High complexity, central to system
   - Dependencies: None initially
   - Estimated: 8 hours

2. **TaskService** (Week 1, Days 3-4)
   - Medium complexity, high usage
   - Dependencies: ProjectService completed
   - Estimated: 6 hours

3. **SourceManagementService** (Week 1, Day 5)
   - Medium complexity, knowledge base core
   - Dependencies: None
   - Estimated: 5 hours

4. **CrawlingService** (Week 2, Days 1-3)
   - High complexity, multiple dependencies
   - Dependencies: SourceManagementService
   - Estimated: 10 hours

#### Sprint 2: Search & Storage (Weeks 3-4)

5. **HybridSearchStrategy** (Week 3, Day 1)
   - Medium complexity, search enhancement
   - Dependencies: BaseSearchStrategy (done)
   - Estimated: 4 hours

6. **DocumentStorageService** (Week 3, Days 2-3)
   - Medium complexity, file uploads
   - Dependencies: None
   - Estimated: 6 hours

7. **VersioningService** (Week 3, Day 4)
   - Low complexity, straightforward
   - Dependencies: None
   - Estimated: 3 hours

8. **DocumentService** (Week 3, Day 5)
   - Medium complexity, project documents
   - Dependencies: ProjectService
   - Estimated: 4 hours

9. **CodeExtractionService** (Week 4, Days 1-2)
   - Medium complexity, code analysis
   - Dependencies: None
   - Estimated: 5 hours

10. **PageStorageOperations** (Week 4, Day 2)
    - Low complexity, simple storage
    - Dependencies: None
    - Estimated: 3 hours

#### Sprint 3: Supporting Services (Weeks 5-6)

11-21. **Remaining Services** (Mixed priority)
    - Each service: 2-4 hours
    - Total estimated: 30-40 hours
    - Can be parallelized if multiple developers

### Timeline Estimates

**Aggressive Schedule** (Single Developer, Full-Time):
- Sprint 1: 2 weeks (29-39 hours)
- Sprint 2: 2 weeks (22-32 hours)
- Sprint 3: 2 weeks (30-40 hours)
- **Total**: 6 weeks (81-111 hours)

**Conservative Schedule** (Single Developer, Part-Time 50%):
- Sprint 1: 4 weeks
- Sprint 2: 4 weeks
- Sprint 3: 4 weeks
- **Total**: 12 weeks

**Team Schedule** (2 Developers, Full-Time):
- Sprint 1: 1 week (parallel on independent services)
- Sprint 2: 1 week (parallel on independent services)
- Sprint 3: 1 week (parallel on remaining services)
- **Total**: 3 weeks

### Risk Assessment

#### Technical Risks

**Risk 1: Breaking Changes**
- **Probability**: Medium
- **Impact**: High
- **Mitigation**:
  - Comprehensive test coverage before refactoring
  - Maintain backward compatibility during transition
  - Phased rollout per service

**Risk 2: Performance Regression**
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**:
  - Performance benchmarks before/after
  - Monitor query execution times
  - Repository caching if needed

**Risk 3: Hidden Dependencies**
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**:
  - Careful code analysis before refactoring
  - Search for all database calls including imports
  - Test thoroughly with integration tests

**Risk 4: Test Gaps**
- **Probability**: Medium
- **Impact**: High
- **Mitigation**:
  - Write tests before refactoring
  - Aim for >80% coverage per service
  - Both unit tests (Fake) and integration tests (Real)

#### Process Risks

**Risk 5: Scope Creep**
- **Probability**: High
- **Impact**: Medium
- **Mitigation**:
  - Stick to refactoring only (no new features)
  - Don't optimize unless necessary
  - Complete one service at a time

**Risk 6: Merge Conflicts**
- **Probability**: High (if multiple devs)
- **Impact**: Medium
- **Mitigation**:
  - Coordinate on service ownership
  - Frequent commits and syncs
  - Small, focused pull requests

**Risk 7: Documentation Drift**
- **Probability**: Medium
- **Impact**: Low
- **Mitigation**:
  - Update this doc as changes occur
  - Document any new patterns discovered
  - Keep examples current

### Success Criteria

The refactoring effort will be considered complete when:

1. **Zero Direct Database Calls**: No service directly uses `supabase_client.table()` or `.rpc()`
2. **Test Coverage**: All refactored services have >80% unit test coverage using FakeDatabaseRepository
3. **Documentation**: This document is kept current with all changes
4. **Performance**: No significant performance degradation (< 5% slower)
5. **Stability**: No production incidents related to refactoring
6. **Code Review**: All changes reviewed and approved by at least one other developer

### Recommended Next Steps

1. **Immediate** (This Week):
   - Review and approve this documentation
   - Set up tracking system (GitHub project board or similar)
   - Assign ownership for Sprint 1 services

2. **Short Term** (Weeks 1-2):
   - Complete Sprint 1 (ProjectService, TaskService, SourceManagementService, CrawlingService)
   - Write comprehensive tests for each
   - Monitor for issues in production

3. **Medium Term** (Weeks 3-6):
   - Complete Sprint 2 and Sprint 3
   - Continuous monitoring and bug fixes
   - Update documentation as patterns evolve

4. **Long Term** (Post-Completion):
   - Consider additional repository interfaces (e.g., for external APIs)
   - Evaluate caching strategies at repository level
   - Explore transaction support for complex operations
   - Consider separate repositories per bounded context

### Future Enhancements

Beyond the current refactoring scope, consider:

1. **Transaction Support**: Add transaction context managers for atomic multi-operation workflows
2. **Caching Layer**: Add optional caching at repository level for frequently accessed data
3. **Query Builder**: Type-safe query builder for complex filters
4. **Event Sourcing**: Repository methods emit domain events for audit logging
5. **Multiple Databases**: Abstract to support multiple database backends (PostgreSQL, MongoDB, etc.)
6. **Read/Write Separation**: Separate read and write repositories for CQRS pattern
7. **Repository Decorators**: Add decorators for logging, metrics, caching
8. **Batch Operations**: More sophisticated batch operations with transaction support

---

## Conclusion

The database repository pattern refactoring represents a significant architectural improvement for Archon. By decoupling services from direct database access, we gain:

- **Better testability** through FakeDatabaseRepository
- **Cleaner architecture** with clear separation of concerns
- **Flexibility** to change database implementations
- **Maintainability** with centralized database operations

The initial implementation (BaseSearchStrategy, RAGService) demonstrates the pattern's effectiveness. With a systematic approach to refactoring the remaining 21 services, Archon will have a robust, testable, and maintainable data access layer.

**Key Takeaway**: This is not just a technical refactoring - it's an investment in code quality that will pay dividends in development velocity, bug reduction, and system reliability for years to come.

---

**Document Version**: 1.0
**Last Updated**: 2025-10-12
**Author**: Database Refactoring Team
**Status**: Active Development
