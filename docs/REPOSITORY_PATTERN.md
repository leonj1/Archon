# Repository Pattern Implementation

This document describes the repository pattern implementation used to abstract database operations in Archon.

## Architecture Overview

```
Service Layer (Business Logic)
       ↓
DatabaseRepository (Interface)
       ↓
Concrete Implementations:
  - SupabaseDatabaseRepository (Production)
  - FakeDatabaseRepository (Testing)
```

## Components

### 1. DatabaseRepository (Interface)
**Location**: `python/src/server/repositories/database_repository.py`

The abstract interface that defines the contract for all database operations. It organizes operations into 11 domains:

1. **Page Metadata Operations** (4 methods)
   - `get_page_metadata_by_id()`
   - `get_page_metadata_by_url()`
   - `list_pages_by_source()`
   - `get_page_count_by_source()`

2. **Document Search Operations** (7 methods)
   - `search_documents_vector()`
   - `search_documents_hybrid()`
   - `get_documents_by_source()`
   - `get_document_by_id()`
   - `insert_document()`
   - `insert_documents_batch()`
   - `delete_documents_by_source()`

3. **Code Examples Operations** (6 methods)
   - `search_code_examples()`
   - `get_code_examples_by_source()`
   - `get_code_example_count_by_source()`
   - `insert_code_example()`
   - `insert_code_examples_batch()`
   - `delete_code_examples_by_source()`

4. **Settings Operations** (4 methods)
   - `get_settings_by_key()`
   - `get_all_settings()`
   - `upsert_setting()`
   - `delete_setting()`

5. **Project Operations** (7 methods)
   - `create_project()`
   - `list_projects()`
   - `get_project_by_id()`
   - `update_project()`
   - `delete_project()`
   - `unpin_all_projects_except()`
   - `get_project_features()`

6. **Task Operations** (9 methods)
   - `create_task()`
   - `list_tasks()`
   - `get_task_by_id()`
   - `update_task()`
   - `delete_task()`
   - `archive_task()`
   - `get_tasks_by_project_and_status()`
   - `get_task_counts_by_project()`
   - `get_all_project_task_counts()`

7. **Source Operations** (5 methods)
   - `list_sources()`
   - `get_source_by_id()`
   - `upsert_source()`
   - `update_source_metadata()`
   - `delete_source()`

8. **Crawled Pages Operations** (5 methods)
   - `get_crawled_page_by_url()`
   - `insert_crawled_page()`
   - `upsert_crawled_page()`
   - `delete_crawled_pages_by_source()`
   - `list_crawled_pages_by_source()`

9. **Document Version Operations** (4 methods)
   - `create_document_version()`
   - `list_document_versions()`
   - `get_document_version_by_id()`
   - `delete_document_version()`

10. **Project Source Linking Operations** (4 methods)
    - `link_project_source()`
    - `unlink_project_source()`
    - `list_project_sources()`
    - `get_sources_for_project()`

11. **RPC Operations** (1 method)
    - `execute_rpc()`

**Total**: 56 abstract methods defining the complete database interface.

### 2. SupabaseDatabaseRepository (Production Implementation)
**Location**: `python/src/server/repositories/supabase_repository.py`

The concrete production implementation that:
- Uses Supabase client for all database operations
- Implements all 56 abstract methods from the interface
- Provides proper error handling and logging
- Contains 1,333 lines of production-ready code

**Key Features**:
- Full async/await support
- Comprehensive error handling with try/catch blocks
- Detailed logging for debugging
- Type hints for all methods
- Proper null handling with Optional returns

**Example Usage**:
```python
from src.server.repositories import SupabaseDatabaseRepository
from src.server.utils import get_supabase_client

# Create repository
client = get_supabase_client()
repository = SupabaseDatabaseRepository(client)

# Use in service
service = ProjectService(repository=repository)
```

### 3. FakeDatabaseRepository (Test Implementation)
**Location**: `python/src/server/repositories/fake_repository.py`

An in-memory implementation for testing that:
- Stores all data in Python dictionaries
- Thread-safe with `threading.RLock()`
- Generates UUIDs for new records
- Maintains referential integrity
- Perfect for unit testing without database

**Key Features**:
- No external dependencies
- Fast execution for tests
- Isolated test environments
- Easy to reset between tests
- 824 lines of test-ready code

**Example Usage**:
```python
from src.server.repositories import FakeDatabaseRepository

# Create in-memory repository for testing
repository = FakeDatabaseRepository()

# Use in tests
service = ProjectService(repository=repository)
# All operations work in memory
```

## Benefits of This Pattern

### 1. Dependency Injection
Services depend on the abstract interface, not concrete implementations:
```python
class ProjectService:
    def __init__(self, repository: Optional[DatabaseRepository] = None):
        if repository is None:
            # Default to production
            repository = SupabaseDatabaseRepository(get_supabase_client())
        self.repository = repository
```

### 2. Testability
Easy to swap implementations for testing:
```python
# Production
service = ProjectService(SupabaseDatabaseRepository(client))

# Testing
service = ProjectService(FakeDatabaseRepository())
```

### 3. Separation of Concerns
- **Services**: Business logic only
- **Repository**: Database operations only
- **No mixing**: Clean architecture

### 4. Future Flexibility
Easy to add new implementations:
- PostgreSQL repository
- MongoDB repository
- Redis repository
- GraphQL repository

### 5. Centralized Database Logic
All database operations in one place:
- Easier to optimize queries
- Consistent error handling
- Single point for caching
- Easy to add metrics/monitoring

## Migration Status

Currently, 3 service classes have been migrated to use the repository pattern:

1. ✅ **RAGService** - Search and retrieval operations
2. ✅ **BaseSearchStrategy** - Vector similarity search
3. ✅ **ProjectService** - Project management operations

20 more service classes remain to be migrated (see `database-service-classes.md`).

## Testing Strategy

### Unit Tests
Use `FakeDatabaseRepository` for fast, isolated tests:
```python
@pytest.fixture
def repository():
    return FakeDatabaseRepository()

def test_project_creation(repository):
    service = ProjectService(repository=repository)
    success, result = await service.create_project("Test")
    assert success
```

### Integration Tests
Use `SupabaseDatabaseRepository` with test database:
```python
@pytest.fixture
def repository():
    test_client = create_test_supabase_client()
    return SupabaseDatabaseRepository(test_client)
```

## Next Steps

1. Continue migrating remaining 20 service classes
2. Add caching layer in repository implementations
3. Add metrics/monitoring in repository methods
4. Consider adding transaction support
5. Add connection pooling optimizations

## Conclusion

The repository pattern provides a clean abstraction layer between business logic and database operations, enabling better testability, maintainability, and flexibility for future changes.
