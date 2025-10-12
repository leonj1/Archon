# Repository Pattern Migration Guide

This guide provides step-by-step instructions for migrating services and API routes to use the repository pattern.

## Table of Contents

- [Before You Start](#before-you-start)
- [Migrating a Service](#migrating-a-service)
- [Migrating an API Route](#migrating-an-api-route)
- [Migrating Tests](#migrating-tests)
- [Common Pitfalls](#common-pitfalls)
- [Verification Steps](#verification-steps)

## Before You Start

### Prerequisites

1. **Understand the Pattern**: Read `python/REPOSITORY_PATTERN.md` first
2. **Review Examples**: Check `python/EXAMPLES.md` for complete examples
3. **Check Existing Work**: See `TaskService` and `ProjectService` for reference implementations

### Required Files

- Repository Interface: `python/src/server/repositories/database_repository.py`
- Supabase Implementation: `python/src/server/repositories/supabase_repository.py`
- Fake Implementation: `python/src/server/repositories/fake_repository.py`

## Migrating a Service

### Step 1: Update Imports

**BEFORE:**
```python
from src.server.utils import get_supabase_client
```

**AFTER:**
```python
from typing import Optional
from src.server.utils import get_supabase_client
from ...repositories.database_repository import DatabaseRepository
from ...repositories.supabase_repository import SupabaseDatabaseRepository
```

### Step 2: Update Constructor

**BEFORE:**
```python
class MyService:
    def __init__(self, supabase_client=None):
        self.supabase_client = supabase_client or get_supabase_client()
```

**AFTER:**
```python
class MyService:
    def __init__(
        self,
        repository: Optional[DatabaseRepository] = None,
        supabase_client=None
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
```

**Why keep `supabase_client`?**
- Maintains backward compatibility during migration
- Allows gradual rollout
- Prevents breaking existing code

### Step 3: Convert Methods to Async

**BEFORE:**
```python
def get_item(self, item_id: str):
    response = self.supabase_client.table("items").select("*").eq("id", item_id).execute()
    return response.data[0] if response.data else None
```

**AFTER:**
```python
async def get_item(self, item_id: str):
    item = await self.repository.get_item_by_id(item_id)
    return item
```

**Key Changes:**
- Add `async` keyword to method definition
- Use `await` for repository calls
- Repository methods handle the query logic

### Step 4: Replace Supabase Calls with Repository Methods

**BEFORE:**
```python
def list_items(self, status: str = None):
    query = self.supabase_client.table("items").select("*")
    if status:
        query = query.eq("status", status)
    response = query.execute()
    return response.data
```

**AFTER:**
```python
async def list_items(self, status: str = None):
    items = await self.repository.list_items(status=status)
    return items
```

**Repository Method Mapping:**

| Supabase Pattern | Repository Method |
|-----------------|-------------------|
| `.table("tasks").select("*").eq("id", x)` | `get_task_by_id(x)` |
| `.table("tasks").select("*")` | `list_tasks()` |
| `.table("tasks").insert(data)` | `create_task(data)` |
| `.table("tasks").update(data).eq("id", x)` | `update_task(x, data)` |
| `.table("tasks").delete().eq("id", x)` | `delete_task(x)` |

### Step 5: Update Error Handling

**BEFORE:**
```python
def create_item(self, data: dict):
    try:
        response = self.supabase_client.table("items").insert(data).execute()
        return response.data[0]
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
```

**AFTER:**
```python
async def create_item(self, data: dict) -> tuple[bool, dict]:
    try:
        item = await self.repository.create_item(data)
        if item:
            return True, {"item": item}
        else:
            return False, {"error": "Failed to create item"}
    except Exception as e:
        logger.error(f"Error creating item: {e}")
        return False, {"error": f"Error creating item: {str(e)}"}
```

**Best Practices:**
- Return tuple of `(success: bool, result: dict)`
- Log errors with context
- Don't let exceptions bubble up uncaught
- Provide meaningful error messages

### Complete Example: Before & After

**BEFORE:**
```python
from src.server.utils import get_supabase_client
from src.server.config.logfire_config import get_logger

logger = get_logger(__name__)

class TaskService:
    def __init__(self, supabase_client=None):
        self.supabase_client = supabase_client or get_supabase_client()

    def get_task(self, task_id: str):
        try:
            response = (
                self.supabase_client
                .table("archon_tasks")
                .select("*")
                .eq("id", task_id)
                .execute()
            )

            if response.data:
                return response.data[0]
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting task: {e}")
            return None

    def list_tasks(self, project_id: str = None, status: str = None):
        try:
            query = self.supabase_client.table("archon_tasks").select("*")

            if project_id:
                query = query.eq("project_id", project_id)
            if status:
                query = query.eq("status", status)

            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return []
```

**AFTER:**
```python
from typing import Any, Optional
from src.server.utils import get_supabase_client
from src.server.config.logfire_config import get_logger
from ...repositories.database_repository import DatabaseRepository
from ...repositories.supabase_repository import SupabaseDatabaseRepository

logger = get_logger(__name__)

class TaskService:
    def __init__(
        self,
        repository: Optional[DatabaseRepository] = None,
        supabase_client=None
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

    async def get_task(self, task_id: str) -> tuple[bool, dict[str, Any]]:
        """Get a specific task by ID."""
        try:
            task = await self.repository.get_task_by_id(task_id)

            if task:
                return True, {"task": task}
            else:
                return False, {"error": f"Task with ID {task_id} not found"}
        except Exception as e:
            logger.error(f"Error getting task: {e}")
            return False, {"error": f"Error getting task: {str(e)}"}

    async def list_tasks(
        self,
        project_id: str = None,
        status: str = None,
        include_archived: bool = False
    ) -> tuple[bool, dict[str, Any]]:
        """List tasks with optional filters."""
        try:
            tasks = await self.repository.list_tasks(
                project_id=project_id,
                status=status,
                include_archived=include_archived
            )

            return True, {
                "tasks": tasks,
                "total_count": len(tasks)
            }
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return False, {"error": f"Error listing tasks: {str(e)}"}
```

## Migrating an API Route

### Step 1: Import Repository

**BEFORE:**
```python
from src.server.utils import get_supabase_client
from src.server.services import MyService
```

**AFTER:**
```python
from src.server.utils import get_supabase_client
from src.server.services import MyService
from src.server.repositories import get_repository  # Factory pattern
# OR
from src.server.repositories.supabase_repository import SupabaseDatabaseRepository  # Direct
```

### Step 2: Update Route Handler

**BEFORE:**
```python
@router.get("/api/items")
async def list_items():
    service = MyService(get_supabase_client())
    items = service.list_items()  # Sync call
    return {"items": items}
```

**AFTER (using factory):**
```python
@router.get("/api/items")
async def list_items():
    try:
        # Get repository from factory
        repository = get_repository()

        # Create service with repository
        service = MyService(repository=repository)

        # Call async service method
        success, result = await service.list_items()

        if not success:
            raise HTTPException(status_code=500, detail=result)

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
```

**AFTER (direct instantiation):**
```python
@router.get("/api/items")
async def list_items():
    try:
        # Create repository directly
        repository = SupabaseDatabaseRepository(get_supabase_client())

        # Create service with repository
        service = MyService(repository=repository)

        # Call async service method
        success, result = await service.list_items()

        if not success:
            raise HTTPException(status_code=500, detail=result)

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
```

### Step 3: Add Await to Service Calls

**BEFORE:**
```python
success, result = service.update_item(item_id, data)
```

**AFTER:**
```python
success, result = await service.update_item(item_id, data)
```

**Important**: All service methods that use repository must be awaited!

### Complete Example: Before & After

**BEFORE:**
```python
@router.post("/api/tasks")
async def create_task(request: CreateTaskRequest):
    try:
        service = TaskService(get_supabase_client())
        task = service.create_task(
            project_id=request.project_id,
            title=request.title,
            description=request.description
        )

        if task:
            return {"message": "Task created", "task": task}
        else:
            raise HTTPException(status_code=400, detail="Failed to create task")
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
```

**AFTER:**
```python
@router.post("/api/tasks")
async def create_task(request: CreateTaskRequest):
    try:
        # Create repository
        repository = SupabaseDatabaseRepository(get_supabase_client())

        # Create service with repository
        service = TaskService(repository=repository)

        # Await async service method
        success, result = await service.create_task(
            project_id=request.project_id,
            title=request.title,
            description=request.description
        )

        if not success:
            raise HTTPException(status_code=400, detail=result)

        return {"message": "Task created successfully", "task": result["task"]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
```

## Migrating Tests

### Step 1: Update Test Imports

**BEFORE:**
```python
from unittest.mock import Mock
from src.server.services import MyService

@pytest.fixture
def mock_supabase():
    return Mock()
```

**AFTER:**
```python
import pytest
from src.server.repositories.fake_repository import FakeDatabaseRepository
from src.server.services import MyService

@pytest.fixture
def repository():
    return FakeDatabaseRepository()
```

### Step 2: Update Test Fixtures

**BEFORE:**
```python
@pytest.fixture
def service(mock_supabase):
    return MyService(supabase_client=mock_supabase)
```

**AFTER:**
```python
@pytest.fixture
def service(repository):
    return MyService(repository=repository)
```

### Step 3: Convert Tests to Async

**BEFORE:**
```python
def test_get_item(service, mock_supabase):
    # Mock Supabase response
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {"id": "123", "name": "Test"}
    ]

    # Call service
    item = service.get_item("123")

    # Assert
    assert item["name"] == "Test"
```

**AFTER:**
```python
@pytest.mark.asyncio
async def test_get_item(service, repository):
    # Create test data in repository
    test_item = {"id": "123", "name": "Test"}
    await repository.create_item(test_item)

    # Call service
    success, result = await service.get_item("123")

    # Assert
    assert success is True
    assert result["item"]["name"] == "Test"
```

### Step 4: Remove Supabase Mocks

**BEFORE:**
```python
@pytest.fixture
def mock_supabase():
    mock = Mock()
    mock.table = Mock()
    mock.table.return_value.select = Mock()
    # ... complex mock setup
    return mock
```

**AFTER:**
```python
# No mocking needed! FakeDatabaseRepository is real implementation
@pytest.fixture
def repository():
    return FakeDatabaseRepository()
```

### Complete Example: Before & After

**BEFORE:**
```python
from unittest.mock import Mock
import pytest
from src.server.services.projects.task_service import TaskService

@pytest.fixture
def mock_supabase():
    mock = Mock()
    return mock

@pytest.fixture
def service(mock_supabase):
    return TaskService(supabase_client=mock_supabase)

def test_create_task(service, mock_supabase):
    # Setup mock
    mock_response = Mock()
    mock_response.data = [{"id": "task-123", "title": "Test Task", "status": "todo"}]
    mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

    # Call service
    task = service.create_task(
        project_id="project-123",
        title="Test Task",
        description="Test"
    )

    # Assert
    assert task["id"] == "task-123"
    assert task["status"] == "todo"
```

**AFTER:**
```python
import pytest
from src.server.repositories.fake_repository import FakeDatabaseRepository
from src.server.services.projects.task_service import TaskService

@pytest.fixture
def repository():
    return FakeDatabaseRepository()

@pytest.fixture
def service(repository):
    return TaskService(repository=repository)

@pytest.mark.asyncio
async def test_create_task(service, repository):
    # Create test project first
    project_data = {"title": "Test Project", "description": "Test"}
    project = await repository.create_project(project_data)

    # Call service
    success, result = await service.create_task(
        project_id=project["id"],
        title="Test Task",
        description="Test"
    )

    # Assert
    assert success is True
    assert result["task"]["title"] == "Test Task"
    assert result["task"]["status"] == "todo"

    # Verify in repository
    task = await repository.get_task_by_id(result["task"]["id"])
    assert task is not None
    assert task["project_id"] == project["id"]
```

## Common Pitfalls

### 1. Forgetting to Make Methods Async

**❌ Wrong:**
```python
def get_item(self, item_id: str):
    return await self.repository.get_item_by_id(item_id)  # Can't await in sync method
```

**✅ Correct:**
```python
async def get_item(self, item_id: str):
    return await self.repository.get_item_by_id(item_id)
```

### 2. Forgetting to Await Service Calls

**❌ Wrong:**
```python
@router.get("/api/items/{item_id}")
async def get_item(item_id: str):
    service = MyService(repository=repository)
    result = service.get_item(item_id)  # Missing await
    return result
```

**✅ Correct:**
```python
@router.get("/api/items/{item_id}")
async def get_item(item_id: str):
    service = MyService(repository=repository)
    success, result = await service.get_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail=result)
    return result
```

### 3. Not Handling None Returns

**❌ Wrong:**
```python
async def get_item(self, item_id: str):
    item = await self.repository.get_item_by_id(item_id)
    return item["name"]  # Crashes if item is None
```

**✅ Correct:**
```python
async def get_item(self, item_id: str):
    item = await self.repository.get_item_by_id(item_id)
    if item:
        return True, {"item": item}
    else:
        return False, {"error": "Item not found"}
```

### 4. Creating Repository in Every Method

**❌ Wrong:**
```python
async def get_item(self, item_id: str):
    repository = SupabaseDatabaseRepository(get_supabase_client())
    return await repository.get_item_by_id(item_id)
```

**✅ Correct:**
```python
def __init__(self, repository: Optional[DatabaseRepository] = None):
    self.repository = repository or SupabaseDatabaseRepository(get_supabase_client())

async def get_item(self, item_id: str):
    return await self.repository.get_item_by_id(item_id)
```

### 5. Not Adding @pytest.mark.asyncio to Tests

**❌ Wrong:**
```python
def test_async_method(service):
    result = await service.get_item("123")  # Can't await in sync test
```

**✅ Correct:**
```python
@pytest.mark.asyncio
async def test_async_method(service):
    success, result = await service.get_item("123")
```

## Verification Steps

After migrating a service, verify the following:

### 1. Service Level

- [ ] All methods are async
- [ ] All repository calls use await
- [ ] Constructor accepts repository parameter
- [ ] Constructor has backward compatibility with supabase_client
- [ ] All Supabase calls replaced with repository calls
- [ ] Error handling is proper (try/except)
- [ ] Return values are consistent (tuple of success, result)
- [ ] Type hints are correct

### 2. API Route Level

- [ ] Repository is created at route level
- [ ] Service is instantiated with repository
- [ ] Service calls use await
- [ ] Error handling includes HTTPException
- [ ] Response format is correct

### 3. Test Level

- [ ] Tests use FakeDatabaseRepository
- [ ] All test methods are async
- [ ] Tests are marked with @pytest.mark.asyncio
- [ ] Supabase mocks are removed
- [ ] Tests verify both success and failure cases
- [ ] Tests check repository state after operations

### 4. Runtime Verification

Run these checks:

```bash
# 1. Run tests
cd python
uv run pytest tests/test_my_service.py -v

# 2. Run linter
uv run ruff check src/server/services/my_service.py

# 3. Run type checker
uv run mypy src/server/services/my_service.py

# 4. Test API endpoint manually
curl http://localhost:8181/api/my-endpoint

# 5. Check logs for errors
docker compose logs archon-server | grep ERROR
```

## Migration Checklist

Use this checklist for each service:

### Service Migration

- [ ] Update imports
  - [ ] Add DatabaseRepository import
  - [ ] Add SupabaseDatabaseRepository import
  - [ ] Add Optional from typing
- [ ] Update constructor
  - [ ] Add repository parameter
  - [ ] Keep supabase_client for backward compatibility
  - [ ] Add proper fallback logic
- [ ] Convert all methods to async
- [ ] Replace all Supabase calls
  - [ ] Find all self.supabase_client references
  - [ ] Map to appropriate repository methods
  - [ ] Add await to all calls
- [ ] Update error handling
  - [ ] Add try/except blocks
  - [ ] Return (success, result) tuples
  - [ ] Add logging
- [ ] Update docstrings
- [ ] Add type hints

### API Route Migration

- [ ] Import repository or factory
- [ ] Create repository instance
- [ ] Pass repository to service
- [ ] Add await to service calls
- [ ] Update error handling
- [ ] Test endpoint manually

### Test Migration

- [ ] Import FakeDatabaseRepository
- [ ] Update fixtures
- [ ] Add @pytest.mark.asyncio
- [ ] Convert tests to async
- [ ] Remove Supabase mocks
- [ ] Run tests and verify pass

### Final Verification

- [ ] All tests pass
- [ ] No linter errors
- [ ] No type checker errors
- [ ] Manual API testing works
- [ ] No errors in logs
- [ ] Performance is acceptable

## Next Steps

After completing migration:

1. **Remove Old Code**: Once verified, remove backward compatibility with supabase_client
2. **Update Documentation**: Update service docstrings and comments
3. **Share Learnings**: Document any issues encountered for other developers
4. **Continue Migration**: Move to next service in priority order

## Getting Help

If you encounter issues:

1. Check `python/REPOSITORY_PATTERN.md` for patterns
2. Review `python/EXAMPLES.md` for complete examples
3. Look at migrated services (TaskService, ProjectService)
4. Check the troubleshooting section in REPOSITORY_PATTERN.md
5. Ask team members who have completed migrations
