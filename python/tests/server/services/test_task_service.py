"""
Unit tests for TaskService using FakeDatabaseRepository

This test suite demonstrates the new testing pattern with FakeDatabaseRepository
instead of mocking Supabase directly. Benefits:
- Faster tests (in-memory operations)
- Simpler setup (no complex mocking)
- Better isolation (each test gets fresh repository)
- Type-safe (real repository interface)
"""

import pytest
from datetime import datetime

from src.server.repositories import FakeDatabaseRepository
from src.server.services.projects.task_service import TaskService


@pytest.fixture
def repository():
    """Create a fresh in-memory repository for each test."""
    return FakeDatabaseRepository()


@pytest.fixture
def task_service(repository):
    """Create a TaskService with the fake repository."""
    return TaskService(repository=repository)


@pytest.fixture
async def test_project(repository):
    """Create a test project for use in tests."""
    project = await repository.create_project({
        "id": "test-project-1",
        "name": "Test Project",
        "description": "A project for testing",
    })
    return project


# ========================================================================
# CREATE TASK TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_create_task_success(task_service, test_project):
    """Test successful task creation."""
    success, result = await task_service.create_task(
        project_id=test_project["id"],
        title="Implement authentication",
        description="Add JWT-based authentication",
        assignee="User",
        priority="high"
    )

    assert success
    assert "task" in result
    assert result["task"]["title"] == "Implement authentication"
    assert result["task"]["description"] == "Add JWT-based authentication"
    assert result["task"]["status"] == "todo"
    assert result["task"]["assignee"] == "User"
    assert result["task"]["priority"] == "high"
    assert result["task"]["project_id"] == test_project["id"]


@pytest.mark.asyncio
async def test_create_task_with_defaults(task_service, test_project):
    """Test task creation with default values."""
    success, result = await task_service.create_task(
        project_id=test_project["id"],
        title="Simple task"
    )

    assert success
    task = result["task"]
    assert task["title"] == "Simple task"
    assert task["description"] == ""
    assert task["assignee"] == "User"
    assert task["priority"] == "medium"
    assert task["task_order"] == 0


@pytest.mark.asyncio
async def test_create_task_empty_title_fails(task_service, test_project):
    """Test that creating a task with empty title fails validation."""
    success, result = await task_service.create_task(
        project_id=test_project["id"],
        title="",
        description="This should fail"
    )

    assert not success
    assert "error" in result
    assert "title" in result["error"].lower()


@pytest.mark.asyncio
async def test_create_task_invalid_priority_fails(task_service, test_project):
    """Test that invalid priority is rejected."""
    success, result = await task_service.create_task(
        project_id=test_project["id"],
        title="Test Task",
        priority="super-urgent"  # Invalid
    )

    assert not success
    assert "error" in result
    assert "priority" in result["error"].lower()


@pytest.mark.asyncio
async def test_create_task_with_feature(task_service, test_project):
    """Test creating a task with a feature label."""
    success, result = await task_service.create_task(
        project_id=test_project["id"],
        title="Add dark mode",
        feature="UI Theme"
    )

    assert success
    assert result["task"]["title"] == "Add dark mode"


@pytest.mark.asyncio
async def test_create_task_with_ordering(task_service, repository, test_project):
    """Test that task ordering works correctly."""
    # Create 3 tasks at positions 0, 1, 2
    for i in range(3):
        success, result = await task_service.create_task(
            project_id=test_project["id"],
            title=f"Task {i}",
            task_order=i
        )
        assert success

    # Insert a new task at position 1 - should shift others
    success, result = await task_service.create_task(
        project_id=test_project["id"],
        title="New Task at Position 1",
        task_order=1
    )

    assert success
    assert result["task"]["task_order"] == 1

    # Verify all tasks are correctly ordered
    tasks = await repository.list_tasks(project_id=test_project["id"], status="todo")
    tasks_sorted = sorted(tasks, key=lambda t: t["task_order"])

    assert len(tasks_sorted) == 4
    assert tasks_sorted[0]["title"] == "Task 0"
    assert tasks_sorted[0]["task_order"] == 0
    assert tasks_sorted[1]["title"] == "New Task at Position 1"
    assert tasks_sorted[1]["task_order"] == 1
    assert tasks_sorted[2]["title"] == "Task 1"
    assert tasks_sorted[2]["task_order"] == 2
    assert tasks_sorted[3]["title"] == "Task 2"
    assert tasks_sorted[3]["task_order"] == 3


# ========================================================================
# LIST TASKS TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_list_tasks_empty(task_service, test_project):
    """Test listing tasks when there are none."""
    success, result = await task_service.list_tasks(project_id=test_project["id"])

    assert success
    assert result["tasks"] == []
    assert result["total_count"] == 0


@pytest.mark.asyncio
async def test_list_tasks_for_project(task_service, repository, test_project):
    """Test listing tasks filtered by project."""
    # Create tasks in test project
    for i in range(3):
        await repository.create_task({
            "project_id": test_project["id"],
            "title": f"Task {i}",
            "status": "todo",
            "task_order": i
        })

    # Create task in different project
    await repository.create_project({"id": "other-project", "name": "Other"})
    await repository.create_task({
        "project_id": "other-project",
        "title": "Other Task",
        "status": "todo",
        "task_order": 0
    })

    # List tasks for test project only
    success, result = await task_service.list_tasks(project_id=test_project["id"])

    assert success
    assert len(result["tasks"]) == 3
    assert all(t["project_id"] == test_project["id"] for t in result["tasks"])


@pytest.mark.asyncio
async def test_list_tasks_by_status(task_service, repository, test_project):
    """Test filtering tasks by status."""
    # Create tasks with different statuses
    statuses = ["todo", "doing", "review", "done"]
    for status in statuses:
        await repository.create_task({
            "project_id": test_project["id"],
            "title": f"Task {status}",
            "status": status,
            "task_order": 0
        })

    # List only "doing" tasks
    success, result = await task_service.list_tasks(
        project_id=test_project["id"],
        status="doing"
    )

    assert success
    assert len(result["tasks"]) == 1
    assert result["tasks"][0]["status"] == "doing"


@pytest.mark.asyncio
async def test_list_tasks_excludes_done_by_default(task_service, repository, test_project):
    """Test that done tasks are excluded by default."""
    # Create tasks with different statuses
    await repository.create_task({
        "project_id": test_project["id"],
        "title": "Todo Task",
        "status": "todo"
    })
    await repository.create_task({
        "project_id": test_project["id"],
        "title": "Done Task",
        "status": "done"
    })

    # List without include_closed
    success, result = await task_service.list_tasks(
        project_id=test_project["id"],
        include_closed=False
    )

    assert success
    assert len(result["tasks"]) == 1
    assert result["tasks"][0]["status"] == "todo"


@pytest.mark.asyncio
async def test_list_tasks_includes_done_when_requested(task_service, repository, test_project):
    """Test that done tasks are included when requested."""
    # Create tasks with different statuses
    await repository.create_task({
        "project_id": test_project["id"],
        "title": "Todo Task",
        "status": "todo"
    })
    await repository.create_task({
        "project_id": test_project["id"],
        "title": "Done Task",
        "status": "done"
    })

    # List with include_closed=True
    success, result = await task_service.list_tasks(
        project_id=test_project["id"],
        include_closed=True
    )

    assert success
    assert len(result["tasks"]) == 2


@pytest.mark.asyncio
async def test_list_tasks_excludes_archived(task_service, repository, test_project):
    """Test that archived tasks are excluded by default."""
    # Create normal task
    await repository.create_task({
        "project_id": test_project["id"],
        "title": "Active Task",
        "status": "todo"
    })

    # Create archived task
    task = await repository.create_task({
        "project_id": test_project["id"],
        "title": "Archived Task",
        "status": "done"
    })
    await repository.archive_task(task["id"])

    # List tasks
    success, result = await task_service.list_tasks(
        project_id=test_project["id"],
        include_archived=False
    )

    assert success
    assert len(result["tasks"]) == 1
    assert result["tasks"][0]["title"] == "Active Task"


@pytest.mark.asyncio
async def test_list_tasks_with_search(task_service, repository, test_project):
    """Test searching tasks by keyword."""
    # Create tasks with different titles
    await repository.create_task({
        "project_id": test_project["id"],
        "title": "Implement authentication",
        "description": "Add JWT support",
        "status": "todo"
    })
    await repository.create_task({
        "project_id": test_project["id"],
        "title": "Add dark mode",
        "description": "UI theme switching",
        "status": "todo"
    })

    # Search for "auth"
    success, result = await task_service.list_tasks(
        project_id=test_project["id"],
        search_query="auth"
    )

    assert success
    assert len(result["tasks"]) == 1
    assert "authentication" in result["tasks"][0]["title"].lower()


# ========================================================================
# UPDATE TASK TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_update_task_title(task_service, repository, test_project):
    """Test updating a task's title."""
    # Create task
    task = await repository.create_task({
        "project_id": test_project["id"],
        "title": "Old Title",
        "status": "todo"
    })

    # Update title
    success, result = await task_service.update_task(
        task_id=task["id"],
        update_fields={"title": "New Title"}
    )

    assert success
    assert result["task"]["title"] == "New Title"


@pytest.mark.asyncio
async def test_update_task_status(task_service, repository, test_project):
    """Test updating a task's status."""
    # Create task
    task = await repository.create_task({
        "project_id": test_project["id"],
        "title": "Test Task",
        "status": "todo"
    })

    # Update to doing
    success, result = await task_service.update_task(
        task_id=task["id"],
        update_fields={"status": "doing"}
    )

    assert success
    assert result["task"]["status"] == "doing"

    # Update to review
    success, result = await task_service.update_task(
        task_id=task["id"],
        update_fields={"status": "review"}
    )

    assert success
    assert result["task"]["status"] == "review"


@pytest.mark.asyncio
async def test_update_task_invalid_status(task_service, repository, test_project):
    """Test that updating to invalid status fails."""
    # Create task
    task = await repository.create_task({
        "project_id": test_project["id"],
        "title": "Test Task",
        "status": "todo"
    })

    # Try to update to invalid status
    success, result = await task_service.update_task(
        task_id=task["id"],
        update_fields={"status": "invalid"}
    )

    assert not success
    assert "error" in result
    assert "Invalid status" in result["error"]


@pytest.mark.asyncio
async def test_update_task_priority(task_service, repository, test_project):
    """Test updating a task's priority."""
    # Create task
    task = await repository.create_task({
        "project_id": test_project["id"],
        "title": "Test Task",
        "status": "todo",
        "priority": "medium"
    })

    # Update priority
    success, result = await task_service.update_task(
        task_id=task["id"],
        update_fields={"priority": "critical"}
    )

    assert success
    assert result["task"]["priority"] == "critical"


@pytest.mark.asyncio
async def test_update_task_multiple_fields(task_service, repository, test_project):
    """Test updating multiple fields at once."""
    # Create task
    task = await repository.create_task({
        "project_id": test_project["id"],
        "title": "Old Title",
        "status": "todo",
        "priority": "low"
    })

    # Update multiple fields
    success, result = await task_service.update_task(
        task_id=task["id"],
        update_fields={
            "title": "New Title",
            "status": "doing",
            "priority": "high",
            "description": "Updated description"
        }
    )

    assert success
    assert result["task"]["title"] == "New Title"
    assert result["task"]["status"] == "doing"
    assert result["task"]["priority"] == "high"
    assert result["task"]["description"] == "Updated description"


@pytest.mark.asyncio
async def test_update_nonexistent_task(task_service):
    """Test updating a task that doesn't exist."""
    success, result = await task_service.update_task(
        task_id="nonexistent-id",
        update_fields={"title": "New Title"}
    )

    assert not success
    assert "error" in result


# ========================================================================
# GET TASK TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_get_task_success(task_service, repository, test_project):
    """Test retrieving a specific task."""
    # Create task
    task = await repository.create_task({
        "project_id": test_project["id"],
        "title": "Test Task",
        "status": "todo"
    })

    # Get task
    success, result = await task_service.get_task(task_id=task["id"])

    assert success
    assert result["task"]["id"] == task["id"]
    assert result["task"]["title"] == "Test Task"


@pytest.mark.asyncio
async def test_get_nonexistent_task(task_service):
    """Test getting a task that doesn't exist."""
    success, result = await task_service.get_task(task_id="nonexistent-id")

    assert not success
    assert "error" in result


# ========================================================================
# ARCHIVE TASK TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_archive_task_success(task_service, repository, test_project):
    """Test archiving a task."""
    # Create task
    task = await repository.create_task({
        "project_id": test_project["id"],
        "title": "Task to Archive",
        "status": "done"
    })

    # Archive it
    success, result = await task_service.archive_task(
        task_id=task["id"],
        archived_by="test-user"
    )

    assert success
    assert result["task_id"] == task["id"]

    # Verify archived flag is set
    archived_task = await repository.get_task_by_id(task["id"])
    assert archived_task["archived"] is True
    assert archived_task["archived_by"] == "test-user"


@pytest.mark.asyncio
async def test_archive_nonexistent_task(task_service):
    """Test archiving a task that doesn't exist."""
    success, result = await task_service.archive_task(
        task_id="nonexistent-id"
    )

    assert not success
    assert "error" in result


@pytest.mark.asyncio
async def test_archive_already_archived_task(task_service, repository, test_project):
    """Test that archiving an already archived task fails."""
    # Create and archive task
    task = await repository.create_task({
        "project_id": test_project["id"],
        "title": "Task",
        "status": "done"
    })
    await repository.archive_task(task["id"])

    # Try to archive again
    success, result = await task_service.archive_task(task_id=task["id"])

    assert not success
    assert "already archived" in result["error"].lower()


# ========================================================================
# TASK COUNTS TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_get_task_counts_single_project(task_service, repository, test_project):
    """Test getting task counts for a single project."""
    # Create tasks with different statuses
    statuses = ["todo", "todo", "doing", "review", "done", "done", "done"]
    for status in statuses:
        await repository.create_task({
            "project_id": test_project["id"],
            "title": f"Task {status}",
            "status": status
        })

    # Get counts
    success, counts = await task_service.get_all_project_task_counts()

    assert success
    assert test_project["id"] in counts
    assert counts[test_project["id"]]["todo"] == 2
    assert counts[test_project["id"]]["doing"] == 1
    assert counts[test_project["id"]]["review"] == 1
    assert counts[test_project["id"]]["done"] == 3


@pytest.mark.asyncio
async def test_get_task_counts_multiple_projects(task_service, repository):
    """Test getting task counts for multiple projects."""
    # Create two projects
    project1 = await repository.create_project({
        "id": "proj-1",
        "name": "Project 1"
    })
    project2 = await repository.create_project({
        "id": "proj-2",
        "name": "Project 2"
    })

    # Create tasks in project 1
    for _ in range(3):
        await repository.create_task({
            "project_id": project1["id"],
            "title": "Task",
            "status": "todo"
        })

    # Create tasks in project 2
    for _ in range(2):
        await repository.create_task({
            "project_id": project2["id"],
            "title": "Task",
            "status": "doing"
        })

    # Get counts
    success, counts = await task_service.get_all_project_task_counts()

    assert success
    assert len(counts) == 2
    assert counts[project1["id"]]["todo"] == 3
    assert counts[project2["id"]]["doing"] == 2


@pytest.mark.asyncio
async def test_get_task_counts_excludes_archived(task_service, repository, test_project):
    """Test that archived tasks are not counted."""
    # Create active task
    await repository.create_task({
        "project_id": test_project["id"],
        "title": "Active Task",
        "status": "todo"
    })

    # Create and archive task
    task = await repository.create_task({
        "project_id": test_project["id"],
        "title": "Archived Task",
        "status": "todo"
    })
    await repository.archive_task(task["id"])

    # Get counts
    success, counts = await task_service.get_all_project_task_counts()

    assert success
    # Only 1 todo task (archived one is excluded)
    assert counts[test_project["id"]]["todo"] == 1


# ========================================================================
# VALIDATION TESTS
# ========================================================================


@pytest.mark.parametrize("status,expected", [
    ("todo", True),
    ("doing", True),
    ("review", True),
    ("done", True),
    ("invalid", False),
    ("", False),
    ("TODO", False),  # Case sensitive
])
def test_validate_status(task_service, status, expected):
    """Test status validation."""
    is_valid, error = task_service.validate_status(status)
    assert is_valid == expected


@pytest.mark.parametrize("priority,expected", [
    ("low", True),
    ("medium", True),
    ("high", True),
    ("critical", True),
    ("invalid", False),
    ("", False),
    ("LOW", False),  # Case sensitive
])
def test_validate_priority(task_service, priority, expected):
    """Test priority validation."""
    is_valid, error = task_service.validate_priority(priority)
    assert is_valid == expected


@pytest.mark.parametrize("assignee,expected", [
    ("User", True),
    ("Archon", True),
    ("AI IDE Agent", True),
    ("", False),
    ("   ", False),
])
def test_validate_assignee(task_service, assignee, expected):
    """Test assignee validation."""
    is_valid, error = task_service.validate_assignee(assignee)
    assert is_valid == expected
