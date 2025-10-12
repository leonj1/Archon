# Repository Pattern Examples

This document provides complete, working examples of services, API routes, and tests using the repository pattern.

## Table of Contents

- [Complete Service Example](#complete-service-example)
- [Complete API Route Example](#complete-api-route-example)
- [Complete Test Example](#complete-test-example)
- [Integration Test Example](#integration-test-example)
- [Factory Usage Examples](#factory-usage-examples)
- [Common Query Patterns](#common-query-patterns)

## Complete Service Example

**File**: `python/src/server/services/projects/task_service.py`

```python
"""
Task Service Module for Archon

This module provides core business logic for task operations that can be
shared between MCP tools and FastAPI endpoints.
"""

from datetime import datetime
from typing import Any, Optional

from src.server.utils import get_supabase_client
from ...repositories.database_repository import DatabaseRepository
from ...repositories.supabase_repository import SupabaseDatabaseRepository
from ...config.logfire_config import get_logger

logger = get_logger(__name__)


class TaskService:
    """Service class for task operations"""

    VALID_STATUSES = ["todo", "doing", "review", "done"]
    VALID_PRIORITIES = ["low", "medium", "high", "critical"]

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

    def validate_status(self, status: str) -> tuple[bool, str]:
        """Validate task status"""
        if status not in self.VALID_STATUSES:
            return (
                False,
                f"Invalid status '{status}'. Must be one of: {', '.join(self.VALID_STATUSES)}",
            )
        return True, ""

    def validate_priority(self, priority: str) -> tuple[bool, str]:
        """Validate task priority"""
        if priority not in self.VALID_PRIORITIES:
            return (
                False,
                f"Invalid priority '{priority}'. Must be one of: {', '.join(self.VALID_PRIORITIES)}",
            )
        return True, ""

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
        """
        Create a new task under a project with automatic reordering.

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Validate inputs
            if not title or not isinstance(title, str) or len(title.strip()) == 0:
                return False, {"error": "Task title is required and must be a non-empty string"}

            if not project_id or not isinstance(project_id, str):
                return False, {"error": "Project ID is required and must be a string"}

            # Validate priority
            is_valid, error_msg = self.validate_priority(priority)
            if not is_valid:
                return False, {"error": error_msg}

            task_status = "todo"

            # Build task data
            task_data = {
                "project_id": project_id,
                "title": title,
                "description": description,
                "status": task_status,
                "assignee": assignee,
                "task_order": task_order,
                "priority": priority,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            if feature:
                task_data["feature"] = feature

            # Create task via repository
            task = await self.repository.create_task(task_data)

            if task:
                logger.info(f"Task created | task_id={task['id']}")
                return True, {
                    "task": {
                        "id": task["id"],
                        "project_id": task["project_id"],
                        "title": task["title"],
                        "description": task["description"],
                        "status": task["status"],
                        "assignee": task["assignee"],
                        "task_order": task["task_order"],
                        "priority": task["priority"],
                        "created_at": task["created_at"],
                    }
                }
            else:
                return False, {"error": "Failed to create task"}

        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return False, {"error": f"Error creating task: {str(e)}"}

    async def list_tasks(
        self,
        project_id: str = None,
        status: str = None,
        include_closed: bool = False,
        include_archived: bool = False,
        search_query: str = None
    ) -> tuple[bool, dict[str, Any]]:
        """
        List tasks with various filters.

        Args:
            project_id: Filter by project
            status: Filter by status
            include_closed: Include done tasks
            include_archived: Include archived tasks
            search_query: Keyword search in title, description, and feature fields

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Validate status if provided
            if status:
                is_valid, error_msg = self.validate_status(status)
                if not is_valid:
                    return False, {"error": error_msg}

            # Use repository to list tasks
            tasks = await self.repository.list_tasks(
                project_id=project_id,
                status=status,
                assignee=None,
                include_archived=include_archived,
                search_query=search_query,
                order_by="task_order"
            )

            # Filter out done tasks if needed
            if not include_closed and not status:
                tasks = [t for t in tasks if t.get("status") != "done"]

            logger.debug(f"Listed {len(tasks)} tasks | project_id={project_id}")

            return True, {
                "tasks": tasks,
                "total_count": len(tasks)
            }

        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return False, {"error": f"Error listing tasks: {str(e)}"}

    async def get_task(self, task_id: str) -> tuple[bool, dict[str, Any]]:
        """
        Get a specific task by ID.

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            task = await self.repository.get_task_by_id(task_id)

            if task:
                return True, {"task": task}
            else:
                return False, {"error": f"Task with ID {task_id} not found"}

        except Exception as e:
            logger.error(f"Error getting task: {e}")
            return False, {"error": f"Error getting task: {str(e)}"}

    async def update_task(
        self,
        task_id: str,
        update_fields: dict[str, Any]
    ) -> tuple[bool, dict[str, Any]]:
        """
        Update task with specified fields.

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Build update data with validation
            update_data = {"updated_at": datetime.now().isoformat()}

            if "status" in update_fields:
                is_valid, error_msg = self.validate_status(update_fields["status"])
                if not is_valid:
                    return False, {"error": error_msg}
                update_data["status"] = update_fields["status"]

            if "priority" in update_fields:
                is_valid, error_msg = self.validate_priority(update_fields["priority"])
                if not is_valid:
                    return False, {"error": error_msg}
                update_data["priority"] = update_fields["priority"]

            # Add other fields
            for field in ["title", "description", "assignee", "task_order", "feature"]:
                if field in update_fields:
                    update_data[field] = update_fields[field]

            # Update task via repository
            task = await self.repository.update_task(
                task_id=task_id,
                update_data=update_data
            )

            if task:
                logger.info(f"Task updated | task_id={task_id}")
                return True, {"task": task, "message": "Task updated successfully"}
            else:
                return False, {"error": f"Task with ID {task_id} not found"}

        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return False, {"error": f"Error updating task: {str(e)}"}

    async def archive_task(
        self,
        task_id: str,
        archived_by: str = "system"
    ) -> tuple[bool, dict[str, Any]]:
        """
        Archive a task (soft delete).

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # First check if task exists
            task = await self.repository.get_task_by_id(task_id)

            if not task:
                return False, {"error": f"Task with ID {task_id} not found"}

            if task.get("archived") is True:
                return False, {"error": f"Task with ID {task_id} is already archived"}

            # Archive the task using repository method
            archived_task = await self.repository.archive_task(
                task_id=task_id,
                archived_by=archived_by
            )

            if archived_task:
                logger.info(f"Task archived | task_id={task_id}")
                return True, {"task_id": task_id, "message": "Task archived successfully"}
            else:
                return False, {"error": f"Failed to archive task {task_id}"}

        except Exception as e:
            logger.error(f"Error archiving task: {e}")
            return False, {"error": f"Error archiving task: {str(e)}"}

    async def get_all_project_task_counts(self) -> tuple[bool, dict[str, dict[str, int]]]:
        """
        Get task counts for all projects in a single optimized query.

        Returns task counts grouped by project_id and status.

        Returns:
            Tuple of (success, counts_dict) where counts_dict is:
            {"project-id": {"todo": 5, "doing": 2, "review": 3, "done": 10}}
        """
        try:
            logger.debug("Fetching task counts for all projects in batch")

            # Use repository method to get task counts
            counts = await self.repository.get_all_project_task_counts()

            logger.debug(f"Task counts fetched for {len(counts)} projects")

            return True, counts

        except Exception as e:
            logger.error(f"Error fetching task counts: {e}")
            return False, {"error": f"Error fetching task counts: {str(e)}"}
```

## Complete API Route Example

**File**: `python/src/server/api_routes/tasks_api.py`

```python
"""
Task API endpoints using repository pattern
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi import status as http_status
from pydantic import BaseModel

from src.server.repositories import get_repository
from src.server.services.projects.task_service import TaskService
from src.server.utils.etag_utils import generate_etag, check_etag
from src.server.config.logfire_config import get_logger, logfire

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["tasks"])


class CreateTaskRequest(BaseModel):
    project_id: str
    title: str
    description: str | None = None
    assignee: str | None = "User"
    task_order: int | None = 0
    priority: str | None = "medium"
    feature: str | None = None


class UpdateTaskRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    assignee: str | None = None
    task_order: int | None = None
    priority: str | None = None
    feature: str | None = None


@router.post("/tasks")
async def create_task(request: CreateTaskRequest):
    """Create a new task with automatic reordering."""
    try:
        logfire.info(f"Creating task | title={request.title}")

        # Get repository and create service
        repository = get_repository()
        task_service = TaskService(repository=repository)

        # Create task
        success, result = await task_service.create_task(
            project_id=request.project_id,
            title=request.title,
            description=request.description or "",
            assignee=request.assignee or "User",
            task_order=request.task_order or 0,
            priority=request.priority or "medium",
            feature=request.feature,
        )

        if not success:
            raise HTTPException(status_code=400, detail=result)

        created_task = result["task"]

        logfire.info(f"Task created | task_id={created_task['id']}")

        return {"message": "Task created successfully", "task": created_task}

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Failed to create task | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/projects/{project_id}/tasks")
async def list_project_tasks(
    project_id: str,
    request: Request,
    response: Response,
    include_archived: bool = False
):
    """List all tasks for a specific project with ETag support."""
    try:
        # Get If-None-Match header for ETag comparison
        if_none_match = request.headers.get("If-None-Match")

        logfire.debug(f"Listing tasks | project_id={project_id}")

        # Use repository and service
        repository = get_repository()
        task_service = TaskService(repository=repository)

        # Get tasks
        success, result = await task_service.list_tasks(
            project_id=project_id,
            include_closed=True,
            include_archived=include_archived,
        )

        if not success:
            raise HTTPException(status_code=500, detail=result)

        tasks = result.get("tasks", [])

        # Generate ETag from task data
        etag_data = {
            "tasks": [
                {
                    "id": t.get("id"),
                    "title": t.get("title"),
                    "status": t.get("status"),
                    "updated_at": t.get("updated_at")
                }
                for t in tasks
            ],
            "project_id": project_id,
            "count": len(tasks)
        }
        current_etag = generate_etag(etag_data)

        # Check if client's ETag matches (304 Not Modified)
        if check_etag(if_none_match, current_etag):
            response.status_code = http_status.HTTP_304_NOT_MODIFIED
            response.headers["ETag"] = current_etag
            response.headers["Cache-Control"] = "no-cache, must-revalidate"
            logfire.debug(f"Tasks unchanged | etag={current_etag}")
            return None

        # Set ETag headers for successful response
        response.headers["ETag"] = current_etag
        response.headers["Cache-Control"] = "no-cache, must-revalidate"
        response.headers["Last-Modified"] = datetime.utcnow().isoformat()

        logfire.debug(f"Tasks retrieved | count={len(tasks)}")

        return tasks

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Failed to list tasks | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get a specific task by ID."""
    try:
        logfire.info(f"Getting task | task_id={task_id}")

        # Use repository and service
        repository = get_repository()
        task_service = TaskService(repository=repository)

        # Get task
        success, result = await task_service.get_task(task_id)

        if not success:
            if "not found" in result.get("error", "").lower():
                raise HTTPException(status_code=404, detail=result.get("error"))
            else:
                raise HTTPException(status_code=500, detail=result)

        logfire.info(f"Task retrieved | task_id={task_id}")

        return result["task"]

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Failed to get task | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.put("/tasks/{task_id}")
async def update_task(task_id: str, request: UpdateTaskRequest):
    """Update a task."""
    try:
        logfire.info(f"Updating task | task_id={task_id}")

        # Build update fields dictionary
        update_fields = {}
        if request.title is not None:
            update_fields["title"] = request.title
        if request.description is not None:
            update_fields["description"] = request.description
        if request.status is not None:
            update_fields["status"] = request.status
        if request.assignee is not None:
            update_fields["assignee"] = request.assignee
        if request.task_order is not None:
            update_fields["task_order"] = request.task_order
        if request.priority is not None:
            update_fields["priority"] = request.priority
        if request.feature is not None:
            update_fields["feature"] = request.feature

        # Use repository and service
        repository = get_repository()
        task_service = TaskService(repository=repository)

        # Update task
        success, result = await task_service.update_task(task_id, update_fields)

        if not success:
            if "not found" in result.get("error", "").lower():
                raise HTTPException(status_code=404, detail=result.get("error"))
            else:
                raise HTTPException(status_code=500, detail=result)

        logfire.info(f"Task updated | task_id={task_id}")

        return {"message": "Task updated successfully", "task": result["task"]}

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Failed to update task | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Archive a task (soft delete)."""
    try:
        logfire.info(f"Archiving task | task_id={task_id}")

        # Use repository and service
        repository = get_repository()
        task_service = TaskService(repository=repository)

        # Archive task
        success, result = await task_service.archive_task(task_id, archived_by="api")

        if not success:
            if "not found" in result.get("error", "").lower():
                raise HTTPException(status_code=404, detail=result.get("error"))
            elif "already archived" in result.get("error", "").lower():
                raise HTTPException(status_code=409, detail=result.get("error"))
            else:
                raise HTTPException(status_code=500, detail=result)

        logfire.info(f"Task archived | task_id={task_id}")

        return {"message": "Task archived successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Failed to archive task | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})
```

## Complete Test Example

**File**: `python/tests/services/test_task_service.py`

```python
"""Unit tests for TaskService using FakeDatabaseRepository"""

import pytest
from src.server.repositories.fake_repository import FakeDatabaseRepository
from src.server.services.projects.task_service import TaskService


@pytest.fixture
def repository():
    """Provide in-memory repository for testing."""
    return FakeDatabaseRepository()


@pytest.fixture
def task_service(repository):
    """Provide TaskService with fake repository."""
    return TaskService(repository=repository)


@pytest.fixture
async def test_project(repository):
    """Create a test project."""
    project_data = {
        "title": "Test Project",
        "description": "Test project for task tests"
    }
    project = await repository.create_project(project_data)
    return project


@pytest.mark.asyncio
async def test_create_task_success(task_service, test_project):
    """Test successful task creation."""
    # Create task
    success, result = await task_service.create_task(
        project_id=test_project["id"],
        title="Test Task",
        description="Test description",
        assignee="User",
        priority="high"
    )

    # Verify success
    assert success is True
    assert "task" in result
    assert result["task"]["title"] == "Test Task"
    assert result["task"]["description"] == "Test description"
    assert result["task"]["status"] == "todo"
    assert result["task"]["assignee"] == "User"
    assert result["task"]["priority"] == "high"
    assert result["task"]["project_id"] == test_project["id"]


@pytest.mark.asyncio
async def test_create_task_missing_title(task_service, test_project):
    """Test task creation with missing title."""
    # Try to create task without title
    success, result = await task_service.create_task(
        project_id=test_project["id"],
        title="",
        description="Test"
    )

    # Verify failure
    assert success is False
    assert "error" in result
    assert "title" in result["error"].lower()


@pytest.mark.asyncio
async def test_create_task_invalid_priority(task_service, test_project):
    """Test task creation with invalid priority."""
    # Try to create task with invalid priority
    success, result = await task_service.create_task(
        project_id=test_project["id"],
        title="Test Task",
        priority="invalid"
    )

    # Verify failure
    assert success is False
    assert "error" in result
    assert "priority" in result["error"].lower()


@pytest.mark.asyncio
async def test_list_tasks_by_project(task_service, repository, test_project):
    """Test listing tasks filtered by project."""
    # Create multiple tasks
    await task_service.create_task(
        project_id=test_project["id"],
        title="Task 1",
        description="First task"
    )
    await task_service.create_task(
        project_id=test_project["id"],
        title="Task 2",
        description="Second task"
    )

    # List tasks
    success, result = await task_service.list_tasks(project_id=test_project["id"])

    # Verify results
    assert success is True
    assert "tasks" in result
    assert len(result["tasks"]) == 2
    assert result["total_count"] == 2


@pytest.mark.asyncio
async def test_list_tasks_by_status(task_service, repository, test_project):
    """Test listing tasks filtered by status."""
    # Create tasks with different statuses
    success1, result1 = await task_service.create_task(
        project_id=test_project["id"],
        title="Todo Task",
        description="Todo"
    )

    # Update one to doing
    task_id = result1["task"]["id"]
    await task_service.update_task(task_id, {"status": "doing"})

    # List only doing tasks
    success, result = await task_service.list_tasks(
        project_id=test_project["id"],
        status="doing"
    )

    # Verify results
    assert success is True
    assert len(result["tasks"]) == 1
    assert result["tasks"][0]["status"] == "doing"


@pytest.mark.asyncio
async def test_get_task_success(task_service, test_project):
    """Test getting a specific task."""
    # Create task
    create_success, create_result = await task_service.create_task(
        project_id=test_project["id"],
        title="Get Test Task",
        description="Test"
    )
    task_id = create_result["task"]["id"]

    # Get task
    success, result = await task_service.get_task(task_id)

    # Verify results
    assert success is True
    assert "task" in result
    assert result["task"]["id"] == task_id
    assert result["task"]["title"] == "Get Test Task"


@pytest.mark.asyncio
async def test_get_task_not_found(task_service):
    """Test getting a non-existent task."""
    # Try to get non-existent task
    success, result = await task_service.get_task("nonexistent-id")

    # Verify failure
    assert success is False
    assert "error" in result
    assert "not found" in result["error"].lower()


@pytest.mark.asyncio
async def test_update_task_success(task_service, test_project):
    """Test successful task update."""
    # Create task
    create_success, create_result = await task_service.create_task(
        project_id=test_project["id"],
        title="Original Title",
        description="Original description"
    )
    task_id = create_result["task"]["id"]

    # Update task
    success, result = await task_service.update_task(
        task_id,
        {
            "title": "Updated Title",
            "description": "Updated description",
            "status": "doing"
        }
    )

    # Verify results
    assert success is True
    assert result["task"]["title"] == "Updated Title"
    assert result["task"]["description"] == "Updated description"
    assert result["task"]["status"] == "doing"


@pytest.mark.asyncio
async def test_update_task_invalid_status(task_service, test_project):
    """Test updating task with invalid status."""
    # Create task
    create_success, create_result = await task_service.create_task(
        project_id=test_project["id"],
        title="Test Task",
        description="Test"
    )
    task_id = create_result["task"]["id"]

    # Try to update with invalid status
    success, result = await task_service.update_task(
        task_id,
        {"status": "invalid"}
    )

    # Verify failure
    assert success is False
    assert "error" in result
    assert "status" in result["error"].lower()


@pytest.mark.asyncio
async def test_archive_task_success(task_service, repository, test_project):
    """Test successful task archiving."""
    # Create task
    create_success, create_result = await task_service.create_task(
        project_id=test_project["id"],
        title="Archive Test",
        description="Test"
    )
    task_id = create_result["task"]["id"]

    # Archive task
    success, result = await task_service.archive_task(task_id, archived_by="test")

    # Verify success
    assert success is True
    assert "message" in result

    # Verify task is archived in repository
    task = await repository.get_task_by_id(task_id)
    assert task["archived"] is True


@pytest.mark.asyncio
async def test_archive_task_already_archived(task_service, repository, test_project):
    """Test archiving an already archived task."""
    # Create and archive task
    create_success, create_result = await task_service.create_task(
        project_id=test_project["id"],
        title="Archive Test",
        description="Test"
    )
    task_id = create_result["task"]["id"]
    await task_service.archive_task(task_id)

    # Try to archive again
    success, result = await task_service.archive_task(task_id)

    # Verify failure
    assert success is False
    assert "error" in result
    assert "already archived" in result["error"].lower()


@pytest.mark.asyncio
async def test_get_all_project_task_counts(task_service, repository):
    """Test getting task counts for all projects."""
    # Create multiple projects and tasks
    project1 = await repository.create_project({"title": "Project 1"})
    project2 = await repository.create_project({"title": "Project 2"})

    # Create tasks for project 1
    await task_service.create_task(project1["id"], "Task 1", status="todo")
    await task_service.create_task(project1["id"], "Task 2", status="doing")
    await task_service.create_task(project1["id"], "Task 3", status="done")

    # Create tasks for project 2
    await task_service.create_task(project2["id"], "Task 4", status="todo")

    # Get counts
    success, counts = await task_service.get_all_project_task_counts()

    # Verify results
    assert success is True
    assert project1["id"] in counts
    assert project2["id"] in counts
    assert counts[project1["id"]]["todo"] >= 1
    assert counts[project1["id"]]["doing"] >= 1
    assert counts[project1["id"]]["done"] >= 1
    assert counts[project2["id"]]["todo"] >= 1
```

## Integration Test Example

**File**: `python/tests/integration/test_task_api_integration.py`

```python
"""Integration tests for Task API with real Supabase"""

import pytest
from httpx import AsyncClient
from src.server.main import app


@pytest.mark.integration
@pytest.mark.asyncio
async def test_task_lifecycle():
    """Test complete task lifecycle: create -> update -> archive."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Create a project first
        project_response = await client.post(
            "/api/projects",
            json={
                "title": "Integration Test Project",
                "description": "Test project for integration tests"
            }
        )
        assert project_response.status_code == 200
        project_id = project_response.json()["project_id"]

        # 2. Create a task
        create_response = await client.post(
            "/api/tasks",
            json={
                "project_id": project_id,
                "title": "Integration Test Task",
                "description": "Test task",
                "assignee": "User",
                "priority": "high"
            }
        )
        assert create_response.status_code == 200
        task_data = create_response.json()
        task_id = task_data["task"]["id"]
        assert task_data["task"]["title"] == "Integration Test Task"
        assert task_data["task"]["status"] == "todo"

        # 3. Get the task
        get_response = await client.get(f"/api/tasks/{task_id}")
        assert get_response.status_code == 200
        retrieved_task = get_response.json()
        assert retrieved_task["id"] == task_id

        # 4. Update the task
        update_response = await client.put(
            f"/api/tasks/{task_id}",
            json={
                "title": "Updated Task Title",
                "status": "doing"
            }
        )
        assert update_response.status_code == 200
        updated_task = update_response.json()["task"]
        assert updated_task["title"] == "Updated Task Title"
        assert updated_task["status"] == "doing"

        # 5. List tasks for the project
        list_response = await client.get(f"/api/projects/{project_id}/tasks")
        assert list_response.status_code == 200
        tasks = list_response.json()
        assert len(tasks) >= 1
        assert any(t["id"] == task_id for t in tasks)

        # 6. Archive the task
        delete_response = await client.delete(f"/api/tasks/{task_id}")
        assert delete_response.status_code == 200

        # 7. Verify task is archived (not in normal list)
        list_after_delete = await client.get(
            f"/api/projects/{project_id}/tasks",
            params={"include_archived": False}
        )
        assert list_after_delete.status_code == 200
        tasks_after = list_after_delete.json()
        assert not any(t["id"] == task_id for t in tasks_after)

        # 8. Cleanup: Delete the project
        await client.delete(f"/api/projects/{project_id}")
```

## Factory Usage Examples

### Basic Factory Usage

```python
from src.server.repositories import get_repository

# Get configured repository (uses environment settings)
repository = get_repository()

# Use repository with service
service = YourService(repository=repository)
```

### Factory with Configuration

```python
# In configuration/settings
REPOSITORY_TYPE = "supabase"  # or "fake" for testing

# Factory handles configuration
def get_repository() -> DatabaseRepository:
    if REPOSITORY_TYPE == "fake":
        return FakeDatabaseRepository()
    else:
        return SupabaseDatabaseRepository(get_supabase_client())
```

## Common Query Patterns

### Pattern 1: List with Filters

```python
async def list_items(
    self,
    category: str = None,
    status: str = None,
    search: str = None
) -> tuple[bool, dict]:
    """List items with optional filters."""
    try:
        items = await self.repository.list_items(
            category=category,
            status=status,
            search_query=search
        )
        return True, {"items": items, "total_count": len(items)}
    except Exception as e:
        logger.error(f"Error listing items: {e}")
        return False, {"error": str(e)}
```

### Pattern 2: Get by ID with Not Found Handling

```python
async def get_item(self, item_id: str) -> tuple[bool, dict]:
    """Get item by ID."""
    try:
        item = await self.repository.get_item_by_id(item_id)
        if item:
            return True, {"item": item}
        else:
            return False, {"error": f"Item {item_id} not found"}
    except Exception as e:
        logger.error(f"Error getting item: {e}")
        return False, {"error": str(e)}
```

### Pattern 3: Create with Validation

```python
async def create_item(
    self,
    name: str,
    category: str,
    data: dict = None
) -> tuple[bool, dict]:
    """Create item with validation."""
    try:
        # Validate inputs
        if not name or len(name.strip()) == 0:
            return False, {"error": "Name is required"}

        if category not in ["type1", "type2", "type3"]:
            return False, {"error": f"Invalid category: {category}"}

        # Build item data
        item_data = {
            "name": name,
            "category": category,
            "data": data or {},
            "created_at": datetime.now().isoformat()
        }

        # Create via repository
        item = await self.repository.create_item(item_data)

        if item:
            return True, {"item": item}
        else:
            return False, {"error": "Failed to create item"}

    except Exception as e:
        logger.error(f"Error creating item: {e}")
        return False, {"error": str(e)}
```

### Pattern 4: Update with Partial Fields

```python
async def update_item(
    self,
    item_id: str,
    update_fields: dict
) -> tuple[bool, dict]:
    """Update item with partial fields."""
    try:
        # Build update data
        update_data = {"updated_at": datetime.now().isoformat()}

        # Validate and add fields
        if "name" in update_fields:
            if not update_fields["name"].strip():
                return False, {"error": "Name cannot be empty"}
            update_data["name"] = update_fields["name"]

        if "category" in update_fields:
            if update_fields["category"] not in ["type1", "type2"]:
                return False, {"error": "Invalid category"}
            update_data["category"] = update_fields["category"]

        # Update via repository
        item = await self.repository.update_item(item_id, update_data)

        if item:
            return True, {"item": item}
        else:
            return False, {"error": f"Item {item_id} not found"}

    except Exception as e:
        logger.error(f"Error updating item: {e}")
        return False, {"error": str(e)}
```

### Pattern 5: Delete with Soft Delete (Archive)

```python
async def delete_item(
    self,
    item_id: str,
    deleted_by: str = "system"
) -> tuple[bool, dict]:
    """Soft delete (archive) an item."""
    try:
        # Check if exists
        item = await self.repository.get_item_by_id(item_id)
        if not item:
            return False, {"error": f"Item {item_id} not found"}

        # Check if already deleted
        if item.get("archived"):
            return False, {"error": f"Item {item_id} already deleted"}

        # Archive item
        archived = await self.repository.archive_item(
            item_id=item_id,
            archived_by=deleted_by
        )

        if archived:
            return True, {"message": "Item deleted successfully"}
        else:
            return False, {"error": "Failed to delete item"}

    except Exception as e:
        logger.error(f"Error deleting item: {e}")
        return False, {"error": str(e)}
```

### Pattern 6: Batch Operations

```python
async def create_items_batch(
    self,
    items_data: list[dict]
) -> tuple[bool, dict]:
    """Create multiple items in a batch."""
    try:
        # Validate all items first
        for item_data in items_data:
            if not item_data.get("name"):
                return False, {"error": "All items must have names"}

        # Add timestamps
        for item_data in items_data:
            item_data["created_at"] = datetime.now().isoformat()

        # Create batch via repository
        items = await self.repository.create_items_batch(items_data)

        return True, {
            "items": items,
            "total_count": len(items)
        }

    except Exception as e:
        logger.error(f"Error creating batch: {e}")
        return False, {"error": str(e)}
```

## Summary

These examples demonstrate:

1. **Complete Service** - Full TaskService implementation with all CRUD operations
2. **Complete API Routes** - FastAPI endpoints using repository pattern
3. **Complete Tests** - Unit tests with FakeDatabaseRepository
4. **Integration Tests** - End-to-end API testing
5. **Factory Pattern** - Using get_repository() for configuration
6. **Common Patterns** - Reusable query patterns for various scenarios

All examples follow the established patterns and best practices documented in `REPOSITORY_PATTERN.md` and `MIGRATION_GUIDE.md`.
