# Repository Pattern Documentation

## Overview

The repository pattern provides a clean abstraction layer between business logic (services) and database operations (Supabase). This enables better testability, maintainability, and flexibility for future database changes.

## Architecture

```
┌─────────────────────────────────────────────┐
│         API Routes (FastAPI)                │
│  - projects_api.py                          │
│  - knowledge_api.py                         │
│  - etc.                                     │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│         Service Layer                       │
│  - ProjectService                           │
│  - TaskService                              │
│  - KnowledgeItemService                     │
│  - etc.                                     │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│    DatabaseRepository (Interface)           │
│  - Defines 58 abstract methods             │
│  - 13 operation domains                     │
└──────────────┬──────────────────────────────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
┌──────────────┐  ┌──────────────┐
│  Supabase    │  │     Fake     │
│  Repository  │  │  Repository  │
│ (Production) │  │   (Testing)  │
└──────────────┘  └──────────────┘
```

## Why Use the Repository Pattern?

### 1. **Testability**
- Services can be tested with in-memory `FakeDatabaseRepository`
- No need to mock Supabase client directly
- Fast, isolated unit tests

### 2. **Separation of Concerns**
- Services focus on business logic only
- Repository handles database operations only
- Clear boundaries and responsibilities

### 3. **Future Flexibility**
- Easy to add new database implementations (PostgreSQL, MongoDB, etc.)
- Can swap databases without changing service code
- Configuration-based database selection

### 4. **Centralized Database Logic**
- All queries in one place
- Consistent error handling
- Easy to optimize and monitor
- Single point for caching

### 5. **Dependency Injection**
- Services depend on interface, not concrete implementation
- Constructor injection for clean architecture
- Easy to configure for different environments

## Core Components

### DatabaseRepository Interface

**Location**: `python/src/server/repositories/database_repository.py`

The abstract interface defines 58 methods organized into 13 domains:

1. **Page Metadata Operations** (5 methods)
   - `get_page_metadata_by_id()`
   - `get_page_metadata_by_url()`
   - `list_pages_by_source()`
   - `get_page_count_by_source()`
   - `upsert_page_metadata_batch()`
   - `update_page_chunk_count()`

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

12. **Prompt Operations** (1 method)
    - `get_all_prompts()`

13. **Table Count Operations** (1 method)
    - `get_table_count()`

### SupabaseDatabaseRepository

**Location**: `python/src/server/repositories/supabase_repository.py`

Production implementation using Supabase client:
- 1,333 lines of production-ready code
- Full async/await support
- Comprehensive error handling
- Detailed logging for debugging
- Proper null handling with Optional returns

### FakeDatabaseRepository

**Location**: `python/src/server/repositories/fake_repository.py`

In-memory implementation for testing:
- 824 lines of test-ready code
- Thread-safe with `threading.RLock()`
- Stores data in Python dictionaries
- Generates UUIDs for IDs
- No external dependencies

## How to Use in Services

### Basic Pattern

```python
from typing import Optional
from src.server.repositories.database_repository import DatabaseRepository
from src.server.repositories.supabase_repository import SupabaseDatabaseRepository
from src.server.utils import get_supabase_client

class YourService:
    def __init__(
        self,
        repository: Optional[DatabaseRepository] = None,
        supabase_client = None
    ):
        """
        Initialize with optional repository or supabase client.

        Args:
            repository: DatabaseRepository instance (preferred)
            supabase_client: Legacy supabase client (for backward compatibility)
        """
        if repository is not None:
            self.repository = repository
        elif supabase_client is not None:
            self.repository = SupabaseDatabaseRepository(supabase_client)
        else:
            self.repository = SupabaseDatabaseRepository(get_supabase_client())

    async def some_method(self, param: str):
        """All service methods should be async when using repository."""
        # Use repository methods instead of direct Supabase calls
        result = await self.repository.some_repository_method(param)
        return result
```

### Real Example: TaskService

**Location**: `python/src/server/services/projects/task_service.py`

```python
class TaskService:
    def __init__(
        self,
        repository: Optional[DatabaseRepository] = None,
        supabase_client = None
    ):
        if repository is not None:
            self.repository = repository
        elif supabase_client is not None:
            self.repository = SupabaseDatabaseRepository(supabase_client)
        else:
            self.repository = SupabaseDatabaseRepository(get_supabase_client())

    async def create_task(
        self,
        project_id: str,
        title: str,
        description: str = "",
        assignee: str = "User",
        task_order: int = 0,
        priority: str = "medium",
        feature: str | None = None,
    ) -> tuple[bool, dict[str, Any]]:
        """Create a new task."""
        try:
            # Build task data
            task_data = {
                "project_id": project_id,
                "title": title,
                "description": description,
                "status": "todo",
                "assignee": assignee,
                "task_order": task_order,
                "priority": priority,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            # Use repository method
            task = await self.repository.create_task(task_data)

            if task:
                return True, {"task": task}
            else:
                return False, {"error": "Failed to create task"}

        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return False, {"error": f"Error creating task: {str(e)}"}
```

## How to Use in API Routes

### Using Factory Pattern (Recommended)

```python
from src.server.repositories import get_repository

@router.get("/api/resource")
async def list_resources():
    """List resources using repository factory."""
    try:
        # Get repository from factory (uses configured backend)
        repository = get_repository()

        # Create service with repository
        service = YourService(repository=repository)

        # Call service method
        success, result = await service.list_items()

        if not success:
            raise HTTPException(status_code=500, detail=result)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
```

### Direct Instantiation

```python
from src.server.repositories.supabase_repository import SupabaseDatabaseRepository
from src.server.utils import get_supabase_client

@router.post("/api/resource")
async def create_resource(request: CreateRequest):
    """Create resource with direct repository instantiation."""
    try:
        # Create repository explicitly
        repository = SupabaseDatabaseRepository(get_supabase_client())

        # Create service with repository
        service = YourService(repository=repository)

        # Call service method
        success, result = await service.create_item(request.data)

        if not success:
            raise HTTPException(status_code=400, detail=result)

        return {"message": "Created successfully", "item": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
```

### Real Example: Projects API

**Location**: `python/src/server/api_routes/projects_api.py`

```python
@router.get("/api/projects/task-counts")
async def get_all_task_counts(request: Request, response: Response):
    """Get task counts for all projects using repository factory."""
    try:
        # Get repository from factory
        repository = get_repository()

        # Create service with repository
        task_service = TaskService(repository=repository)
        success, result = await task_service.get_all_project_task_counts()

        if not success:
            raise HTTPException(status_code=500, detail=result)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
```

## How to Test with FakeDatabaseRepository

### Basic Test Pattern

```python
import pytest
from src.server.repositories.fake_repository import FakeDatabaseRepository

@pytest.fixture
def repository():
    """Provide in-memory repository for testing."""
    return FakeDatabaseRepository()

@pytest.mark.asyncio
async def test_service_method(repository):
    """Test service with fake repository."""
    # Create service with fake repository
    service = YourService(repository=repository)

    # Call service method
    success, result = await service.create_item("test")

    # Assert results
    assert success is True
    assert "item" in result
    assert result["item"]["name"] == "test"
```

### Real Example: Task Service Test

```python
import pytest
from src.server.repositories.fake_repository import FakeDatabaseRepository
from src.server.services.projects.task_service import TaskService

@pytest.fixture
def repository():
    return FakeDatabaseRepository()

@pytest.fixture
def task_service(repository):
    return TaskService(repository=repository)

@pytest.mark.asyncio
async def test_create_task(task_service, repository):
    """Test task creation with fake repository."""
    # Create a project first
    project_data = {
        "title": "Test Project",
        "description": "Test description"
    }
    project = await repository.create_project(project_data)

    # Create task
    success, result = await task_service.create_task(
        project_id=project["id"],
        title="Test Task",
        description="Test description",
        assignee="User"
    )

    # Verify success
    assert success is True
    assert "task" in result
    assert result["task"]["title"] == "Test Task"
    assert result["task"]["status"] == "todo"

    # Verify task exists in repository
    task = await repository.get_task_by_id(result["task"]["id"])
    assert task is not None
    assert task["project_id"] == project["id"]
```

## Common Patterns

### ✅ DO: Use Repository Methods

```python
# Good - Use repository
async def get_items(self):
    items = await self.repository.list_items()
    return items
```

### ❌ DON'T: Use Direct Supabase Calls

```python
# Bad - Direct Supabase call
async def get_items(self):
    response = self.supabase_client.table("items").select("*").execute()
    return response.data
```

### ✅ DO: Make Methods Async

```python
# Good - Async method
async def create_item(self, data: dict):
    item = await self.repository.create_item(data)
    return item
```

### ❌ DON'T: Use Sync Methods

```python
# Bad - Sync method with async repository
def create_item(self, data: dict):
    item = await self.repository.create_item(data)  # Can't await in sync method
    return item
```

### ✅ DO: Use Constructor Injection

```python
# Good - Constructor injection
def __init__(self, repository: Optional[DatabaseRepository] = None):
    if repository is None:
        repository = SupabaseDatabaseRepository(get_supabase_client())
    self.repository = repository
```

### ❌ DON'T: Create Repository in Methods

```python
# Bad - Creating repository in methods
async def get_items(self):
    repository = SupabaseDatabaseRepository(get_supabase_client())
    return await repository.list_items()
```

### ✅ DO: Handle Errors Gracefully

```python
# Good - Proper error handling
async def update_item(self, item_id: str, data: dict):
    try:
        item = await self.repository.update_item(item_id, data)
        if item:
            return True, {"item": item}
        else:
            return False, {"error": "Item not found"}
    except Exception as e:
        logger.error(f"Failed to update item: {e}")
        return False, {"error": str(e)}
```

### ❌ DON'T: Let Exceptions Bubble Up

```python
# Bad - No error handling
async def update_item(self, item_id: str, data: dict):
    item = await self.repository.update_item(item_id, data)
    return True, {"item": item}  # What if repository throws?
```

## Anti-Patterns to Avoid

### 1. Mixing Direct Supabase and Repository Calls

```python
# ❌ BAD
class MixedService:
    def __init__(self, repository, supabase_client):
        self.repository = repository
        self.supabase = supabase_client

    async def get_item(self, item_id):
        # Using repository
        item = await self.repository.get_item_by_id(item_id)

        # Then using direct Supabase call - DON'T DO THIS
        response = self.supabase.table("related").select("*").execute()
        return item, response.data

# ✅ GOOD
class ConsistentService:
    def __init__(self, repository):
        self.repository = repository

    async def get_item(self, item_id):
        # Only use repository
        item = await self.repository.get_item_by_id(item_id)
        related = await self.repository.get_related_items(item_id)
        return item, related
```

### 2. Not Using Optional for Repository Parameter

```python
# ❌ BAD - No Optional, no default
class BadService:
    def __init__(self, repository: DatabaseRepository):
        self.repository = repository

# ✅ GOOD - Optional with default
class GoodService:
    def __init__(self, repository: Optional[DatabaseRepository] = None):
        if repository is None:
            repository = SupabaseDatabaseRepository(get_supabase_client())
        self.repository = repository
```

### 3. Creating Multiple Repository Instances

```python
# ❌ BAD - Creating new instance each call
async def get_items(self):
    repository = SupabaseDatabaseRepository(get_supabase_client())
    return await repository.list_items()

# ✅ GOOD - Use instance from constructor
def __init__(self, repository: Optional[DatabaseRepository] = None):
    self.repository = repository or SupabaseDatabaseRepository(get_supabase_client())

async def get_items(self):
    return await self.repository.list_items()
```

### 4. Not Handling None Returns

```python
# ❌ BAD - No None check
async def get_item(self, item_id: str):
    item = await self.repository.get_item_by_id(item_id)
    return item["name"]  # Will crash if item is None

# ✅ GOOD - Handle None
async def get_item(self, item_id: str):
    item = await self.repository.get_item_by_id(item_id)
    if item:
        return True, {"item": item}
    else:
        return False, {"error": "Item not found"}
```

## Troubleshooting

### Issue: "RuntimeError: await wasn't used with future"

**Cause**: Calling async repository method without await

```python
# ❌ Wrong
item = self.repository.get_item_by_id(item_id)

# ✅ Correct
item = await self.repository.get_item_by_id(item_id)
```

### Issue: "TypeError: object dict can't be used in 'await' expression"

**Cause**: Trying to await non-async method

```python
# ❌ Wrong - Service method not async
def get_item(self, item_id: str):
    return await self.repository.get_item_by_id(item_id)

# ✅ Correct - Make method async
async def get_item(self, item_id: str):
    return await self.repository.get_item_by_id(item_id)
```

### Issue: Tests fail with "FakeDatabaseRepository has no attribute..."

**Cause**: Repository method not implemented in FakeDatabaseRepository

**Solution**: Add the missing method to `fake_repository.py`

### Issue: "AttributeError: 'NoneType' object has no attribute..."

**Cause**: Repository method returned None, not handled

**Solution**: Always check for None before accessing attributes

```python
# ✅ Correct
item = await self.repository.get_item_by_id(item_id)
if item:
    name = item["name"]
else:
    return False, {"error": "Item not found"}
```

## Migration Checklist

When migrating a service to use the repository pattern:

- [ ] Add `repository` parameter to `__init__`
- [ ] Add backward compatibility for `supabase_client` parameter
- [ ] Convert all methods to `async`
- [ ] Replace all `self.supabase_client` calls with `self.repository` calls
- [ ] Add proper error handling with try/except
- [ ] Update service docstrings
- [ ] Update tests to use `FakeDatabaseRepository`
- [ ] Update API routes to pass repository
- [ ] Verify all methods work correctly
- [ ] Remove old Supabase client code

## Next Steps

1. Continue migrating remaining services (see `repository-pattern-migration-checklist.md`)
2. Update all API routes to use repository pattern
3. Convert all tests to use `FakeDatabaseRepository`
4. Add repository factory for centralized configuration
5. Consider adding caching layer in repository

## References

- Repository Interface: `python/src/server/repositories/database_repository.py`
- Supabase Implementation: `python/src/server/repositories/supabase_repository.py`
- Fake Implementation: `python/src/server/repositories/fake_repository.py`
- Migration Checklist: `repository-pattern-migration-checklist.md`
- Migration Guide: `python/MIGRATION_GUIDE.md`
- API Patterns: `python/API_PATTERNS.md`
- Examples: `python/EXAMPLES.md`
