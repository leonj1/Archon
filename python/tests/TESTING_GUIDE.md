# Testing Guide: Using FakeDatabaseRepository

This guide explains how to write tests for Archon services using the Repository Pattern with `FakeDatabaseRepository`.

## Table of Contents

1. [Why FakeDatabaseRepository?](#why-fakedatabaserepository)
2. [Basic Patterns](#basic-patterns)
3. [Common Scenarios](#common-scenarios)
4. [Migration from Mocking](#migration-from-mocking)
5. [Integration Tests](#integration-tests)
6. [Best Practices](#best-practices)

## Why FakeDatabaseRepository?

### Benefits

- **Fast**: In-memory operations, no database roundtrips
- **Isolated**: Each test gets a fresh repository instance
- **Simple**: No complex mocking setup or assertions
- **Reliable**: Real repository interface implementation
- **Type-safe**: Full type checking with Python type hints

### Old Pattern (Mocking Supabase)

```python
from unittest.mock import MagicMock, patch

@patch('src.server.utils.get_supabase_client')
def test_create_task_old(mock_get_client):
    # Complex mock setup
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [{"id": "123", "title": "Test Task"}]
    mock_client.table.return_value.insert.return_value.execute.return_value = mock_response
    mock_get_client.return_value = mock_client

    # Test code...
```

### New Pattern (FakeDatabaseRepository)

```python
from src.server.repositories import FakeDatabaseRepository
from src.server.services.projects.task_service import TaskService

async def test_create_task_new():
    # Simple setup - no mocking
    repo = FakeDatabaseRepository()
    service = TaskService(repository=repo)

    # Pre-populate test data if needed
    await repo.create_project({"id": "proj-1", "name": "Test Project"})

    # Test code...
```

## Basic Patterns

### 1. Service Initialization

```python
import pytest
from src.server.repositories import FakeDatabaseRepository
from src.server.services.projects.task_service import TaskService

@pytest.fixture
def repository():
    """Create a fresh repository for each test."""
    return FakeDatabaseRepository()

@pytest.fixture
def task_service(repository):
    """Create a task service with the fake repository."""
    return TaskService(repository=repository)

@pytest.mark.asyncio
async def test_something(task_service, repository):
    # Your test here
    pass
```

### 2. Pre-populating Test Data

```python
@pytest.mark.asyncio
async def test_list_tasks_for_project(task_service, repository):
    # Create test project
    project = await repository.create_project({
        "id": "proj-1",
        "name": "Test Project",
        "description": "A test project"
    })

    # Create test tasks
    task1 = await repository.create_task({
        "project_id": "proj-1",
        "title": "Task 1",
        "status": "todo",
        "task_order": 0
    })

    task2 = await repository.create_task({
        "project_id": "proj-1",
        "title": "Task 2",
        "status": "doing",
        "task_order": 1
    })

    # Test the service
    success, result = await task_service.list_tasks(project_id="proj-1")

    assert success
    assert len(result["tasks"]) == 2
```

### 3. Direct Repository Access

You can directly inspect repository state for assertions:

```python
@pytest.mark.asyncio
async def test_task_created_in_database(task_service, repository):
    # Create task through service
    success, result = await task_service.create_task(
        project_id="proj-1",
        title="New Task",
        description="Test"
    )

    # Verify it's in the repository
    assert success
    task_id = result["task"]["id"]

    # Direct repository check
    task = await repository.get_task_by_id(task_id)
    assert task is not None
    assert task["title"] == "New Task"
```

## Common Scenarios

### Testing Task Operations

```python
@pytest.mark.asyncio
async def test_create_task_with_validation(task_service, repository):
    """Test task creation with input validation."""
    # Setup: Create a project
    await repository.create_project({
        "id": "proj-1",
        "name": "Test Project"
    })

    # Test: Create task
    success, result = await task_service.create_task(
        project_id="proj-1",
        title="Implement feature",
        description="Add user authentication",
        assignee="User",
        priority="high"
    )

    # Assert: Check success and data
    assert success
    assert result["task"]["title"] == "Implement feature"
    assert result["task"]["priority"] == "high"

    # Verify in repository
    task = await repository.get_task_by_id(result["task"]["id"])
    assert task["assignee"] == "User"
```

### Testing Task Status Transitions

```python
@pytest.mark.asyncio
async def test_update_task_status(task_service, repository):
    """Test updating a task's status."""
    # Setup
    await repository.create_project({"id": "proj-1", "name": "Test"})
    task = await repository.create_task({
        "project_id": "proj-1",
        "title": "Test Task",
        "status": "todo"
    })

    # Test: Update status
    success, result = await task_service.update_task(
        task_id=task["id"],
        update_fields={"status": "doing"}
    )

    # Assert
    assert success
    assert result["task"]["status"] == "doing"
```

### Testing Task Ordering

```python
@pytest.mark.asyncio
async def test_task_reordering(task_service, repository):
    """Test that creating a task at a specific order shifts others."""
    # Setup: Create project and tasks
    await repository.create_project({"id": "proj-1", "name": "Test"})

    # Create tasks at orders 0, 1, 2
    for i in range(3):
        await repository.create_task({
            "project_id": "proj-1",
            "title": f"Task {i}",
            "status": "todo",
            "task_order": i
        })

    # Test: Insert a new task at position 1
    success, result = await task_service.create_task(
        project_id="proj-1",
        title="New Task",
        task_order=1
    )

    # Assert: New task is at position 1
    assert success
    assert result["task"]["task_order"] == 1

    # Verify: Old tasks at 1 and 2 were shifted
    tasks = await repository.list_tasks(project_id="proj-1", status="todo")
    tasks_sorted = sorted(tasks, key=lambda t: t["task_order"])

    assert len(tasks_sorted) == 4
    assert tasks_sorted[0]["title"] == "Task 0"
    assert tasks_sorted[1]["title"] == "New Task"  # Inserted here
    assert tasks_sorted[2]["title"] == "Task 1"    # Shifted
    assert tasks_sorted[3]["title"] == "Task 2"    # Shifted
```

### Testing Task Counts

```python
@pytest.mark.asyncio
async def test_get_task_counts_by_project(task_service, repository):
    """Test getting task counts grouped by status."""
    # Setup: Create project with tasks in different statuses
    await repository.create_project({"id": "proj-1", "name": "Test"})

    # 2 todo, 1 doing, 3 done
    statuses = ["todo", "todo", "doing", "done", "done", "done"]
    for i, status in enumerate(statuses):
        await repository.create_task({
            "project_id": "proj-1",
            "title": f"Task {i}",
            "status": status
        })

    # Test: Get counts
    success, counts = await task_service.get_all_project_task_counts()

    # Assert
    assert success
    assert counts["proj-1"]["todo"] == 2
    assert counts["proj-1"]["doing"] == 1
    assert counts["proj-1"]["done"] == 3
```

### Testing Validation Errors

```python
@pytest.mark.asyncio
async def test_create_task_invalid_status(task_service, repository):
    """Test that invalid status is rejected."""
    await repository.create_project({"id": "proj-1", "name": "Test"})

    # Attempt to update with invalid status
    task = await repository.create_task({
        "project_id": "proj-1",
        "title": "Test Task",
        "status": "todo"
    })

    success, result = await task_service.update_task(
        task_id=task["id"],
        update_fields={"status": "invalid-status"}
    )

    # Should fail
    assert not success
    assert "error" in result
    assert "Invalid status" in result["error"]
```

### Testing Archive Operations

```python
@pytest.mark.asyncio
async def test_archive_task(task_service, repository):
    """Test archiving a task."""
    # Setup
    await repository.create_project({"id": "proj-1", "name": "Test"})
    task = await repository.create_task({
        "project_id": "proj-1",
        "title": "Task to Archive",
        "status": "done"
    })

    # Test: Archive task
    success, result = await task_service.archive_task(
        task_id=task["id"],
        archived_by="test-user"
    )

    # Assert: Success
    assert success

    # Verify: Task is marked as archived
    archived_task = await repository.get_task_by_id(task["id"])
    assert archived_task["archived"] is True
    assert archived_task["archived_by"] == "test-user"

    # Verify: Archived tasks don't appear in normal queries
    tasks = await repository.list_tasks(
        project_id="proj-1",
        include_archived=False
    )
    assert len(tasks) == 0
```

## Migration from Mocking

### Step 1: Identify Mocked Supabase Calls

Old test with mocking:

```python
from unittest.mock import MagicMock, patch

@patch('src.server.utils.get_supabase_client')
def test_old_way(mock_get_client):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [{"id": "1", "title": "Task"}]
    mock_client.table.return_value.select.return_value.execute.return_value = mock_response
    mock_get_client.return_value = mock_client

    service = TaskService()  # Uses mocked client
    # ... rest of test
```

### Step 2: Convert to Repository Pattern

New test with FakeDatabaseRepository:

```python
from src.server.repositories import FakeDatabaseRepository

@pytest.mark.asyncio
async def test_new_way():
    # Create fake repository
    repo = FakeDatabaseRepository()

    # Pre-populate test data
    await repo.create_task({
        "id": "1",
        "title": "Task",
        "project_id": "proj-1",
        "status": "todo"
    })

    # Create service with repository
    service = TaskService(repository=repo)

    # ... rest of test (same assertions)
```

### Step 3: Remove Mock Imports

Remove these imports:

```python
from unittest.mock import MagicMock, patch  # Not needed anymore
```

Add these imports:

```python
import pytest
from src.server.repositories import FakeDatabaseRepository
```

### Step 4: Update Test Function Signatures

Old:

```python
def test_something(mock_client):
    pass
```

New:

```python
@pytest.mark.asyncio  # Add this decorator
async def test_something(repository, task_service):  # Use fixtures
    pass
```

## Integration Tests

For tests that need to verify behavior against a real database:

```python
import pytest
from src.server.repositories import SupabaseDatabaseRepository
from src.server.utils import get_supabase_client

@pytest.fixture
def real_repository():
    """Use real Supabase connection for integration tests."""
    client = get_supabase_client()
    return SupabaseDatabaseRepository(client)

@pytest.mark.integration  # Mark as integration test
@pytest.mark.asyncio
async def test_with_real_database(real_repository):
    """Integration test with actual Supabase."""
    # This will interact with real database
    # Use carefully and clean up after!

    task = await real_repository.create_task({
        "project_id": "test-proj",
        "title": "Integration Test Task",
        "status": "todo"
    })

    try:
        # Your test assertions
        assert task is not None
        assert task["title"] == "Integration Test Task"
    finally:
        # Clean up
        await real_repository.delete_task(task["id"])
```

Run integration tests separately:

```bash
# Run only unit tests (fake repository)
pytest tests/ -m "not integration"

# Run only integration tests (real database)
pytest tests/ -m integration
```

## Best Practices

### 1. Use Fixtures for Common Setup

```python
@pytest.fixture
def project_with_tasks(repository):
    """Create a project with sample tasks."""
    async def _create():
        project = await repository.create_project({
            "id": "test-proj",
            "name": "Test Project"
        })

        tasks = []
        for i in range(3):
            task = await repository.create_task({
                "project_id": "test-proj",
                "title": f"Task {i}",
                "status": "todo",
                "task_order": i
            })
            tasks.append(task)

        return project, tasks

    return _create

@pytest.mark.asyncio
async def test_with_fixture(project_with_tasks, task_service):
    # Use the fixture
    project, tasks = await project_with_tasks()

    # Test with pre-populated data
    success, result = await task_service.list_tasks(project_id=project["id"])
    assert len(result["tasks"]) == 3
```

### 2. Test One Thing at a Time

```python
# Good: Tests one specific behavior
@pytest.mark.asyncio
async def test_create_task_validates_title():
    repo = FakeDatabaseRepository()
    service = TaskService(repository=repo)

    success, result = await service.create_task(
        project_id="proj-1",
        title="",  # Empty title
        description="Test"
    )

    assert not success
    assert "title" in result["error"].lower()

# Avoid: Testing multiple unrelated things
@pytest.mark.asyncio
async def test_everything():
    # Tests creation, update, delete, validation all at once
    # Hard to debug when it fails
    pass
```

### 3. Use Descriptive Test Names

```python
# Good
@pytest.mark.asyncio
async def test_archive_task_sets_archived_flag_and_timestamp():
    pass

# Bad
@pytest.mark.asyncio
async def test_archive():
    pass
```

### 4. Assert on Specific Values

```python
# Good: Specific assertions
assert task["title"] == "Expected Title"
assert task["status"] == "doing"
assert task["archived"] is False

# Avoid: Generic assertions
assert task is not None
assert len(tasks) > 0
```

### 5. Clean Test Data

```python
@pytest.mark.asyncio
async def test_something(repository):
    # Each test gets a fresh repository
    # No need to clean up - repository is discarded after test

    # But if you modify global state or files:
    try:
        # Your test
        pass
    finally:
        # Clean up global state
        pass
```

### 6. Use Parametrized Tests for Similar Cases

```python
@pytest.mark.parametrize("status,expected", [
    ("todo", True),
    ("doing", True),
    ("review", True),
    ("done", True),
    ("invalid", False),
])
@pytest.mark.asyncio
async def test_validate_status(status, expected, task_service):
    is_valid, error = task_service.validate_status(status)
    assert is_valid == expected
```

## Summary

The `FakeDatabaseRepository` provides:

- **Faster tests**: No database I/O
- **Simpler code**: No mock configuration
- **Better isolation**: Each test is independent
- **Type safety**: Real interface implementation
- **Easier debugging**: Real code paths, not mocks

When writing new tests:

1. Import `FakeDatabaseRepository`
2. Create repository and service instances
3. Pre-populate test data using repository methods
4. Test service methods
5. Assert on results

No mocking required!
