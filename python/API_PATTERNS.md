# API Patterns with Repository

This document describes standard patterns for implementing FastAPI routes using the repository pattern.

## Table of Contents

- [Standard Route Structure](#standard-route-structure)
- [Error Handling](#error-handling)
- [Response Formatting](#response-formatting)
- [ETag Support](#etag-support)
- [Complete Examples](#complete-examples)

## Standard Route Structure

### Basic GET Endpoint

```python
from fastapi import APIRouter, HTTPException
from src.server.repositories import get_repository
from src.server.services import YourService

router = APIRouter(prefix="/api", tags=["your-feature"])

@router.get("/items")
async def list_items():
    """List all items."""
    try:
        # 1. Get repository from factory
        repository = get_repository()

        # 2. Create service with repository
        service = YourService(repository=repository)

        # 3. Call async service method
        success, result = await service.list_items()

        # 4. Handle failure
        if not success:
            raise HTTPException(status_code=500, detail=result)

        # 5. Return success result
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
```

### Basic POST Endpoint

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.server.repositories import get_repository
from src.server.services import YourService

class CreateItemRequest(BaseModel):
    name: str
    description: str | None = None

@router.post("/items")
async def create_item(request: CreateItemRequest):
    """Create a new item."""
    try:
        # Validate request
        if not request.name or not request.name.strip():
            raise HTTPException(status_code=422, detail="Name is required")

        # Get repository and create service
        repository = get_repository()
        service = YourService(repository=repository)

        # Call service method
        success, result = await service.create_item(
            name=request.name,
            description=request.description
        )

        # Handle failure
        if not success:
            raise HTTPException(status_code=400, detail=result)

        # Return success
        return {
            "message": "Item created successfully",
            "item": result["item"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
```

### Basic PUT Endpoint

```python
class UpdateItemRequest(BaseModel):
    name: str | None = None
    description: str | None = None

@router.put("/items/{item_id}")
async def update_item(item_id: str, request: UpdateItemRequest):
    """Update an existing item."""
    try:
        # Build update fields
        update_fields = {}
        if request.name is not None:
            update_fields["name"] = request.name
        if request.description is not None:
            update_fields["description"] = request.description

        # Get repository and create service
        repository = get_repository()
        service = YourService(repository=repository)

        # Call service method
        success, result = await service.update_item(item_id, update_fields)

        # Handle failure
        if not success:
            if "not found" in result.get("error", "").lower():
                raise HTTPException(status_code=404, detail=result)
            else:
                raise HTTPException(status_code=500, detail=result)

        # Return success
        return {
            "message": "Item updated successfully",
            "item": result["item"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
```

### Basic DELETE Endpoint

```python
@router.delete("/items/{item_id}")
async def delete_item(item_id: str):
    """Delete an item (or archive for soft delete)."""
    try:
        # Get repository and create service
        repository = get_repository()
        service = YourService(repository=repository)

        # Call service method
        success, result = await service.delete_item(item_id)

        # Handle failure
        if not success:
            if "not found" in result.get("error", "").lower():
                raise HTTPException(status_code=404, detail=result)
            else:
                raise HTTPException(status_code=500, detail=result)

        # Return success
        return {"message": "Item deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
```

## Error Handling

### Standard Error Handling Pattern

```python
@router.get("/items/{item_id}")
async def get_item(item_id: str):
    """Get a specific item."""
    try:
        repository = get_repository()
        service = YourService(repository=repository)
        success, result = await service.get_item(item_id)

        if not success:
            # Check for specific error types
            error = result.get("error", "")

            if "not found" in error.lower():
                raise HTTPException(status_code=404, detail=result)
            elif "permission" in error.lower():
                raise HTTPException(status_code=403, detail=result)
            elif "validation" in error.lower():
                raise HTTPException(status_code=422, detail=result)
            else:
                raise HTTPException(status_code=500, detail=result)

        return result["item"]

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={"error": str(e)})
```

### HTTP Status Code Guidelines

| Status Code | When to Use | Example |
|------------|-------------|---------|
| 200 OK | Successful GET/PUT | Item retrieved/updated |
| 201 Created | Successful POST | Item created |
| 204 No Content | Successful DELETE | Item deleted (no body) |
| 400 Bad Request | Invalid input | Validation failed |
| 404 Not Found | Resource doesn't exist | Item not found |
| 409 Conflict | Resource conflict | Item already exists |
| 422 Unprocessable Entity | Validation error | Missing required field |
| 500 Internal Server Error | Server error | Database error |

## Response Formatting

### Success Response Patterns

**Single Item:**
```python
return {
    "item": {
        "id": "123",
        "name": "Example",
        "created_at": "2024-01-01T00:00:00"
    }
}
```

**List of Items:**
```python
return {
    "items": [
        {"id": "1", "name": "Item 1"},
        {"id": "2", "name": "Item 2"}
    ],
    "total_count": 2,
    "timestamp": datetime.utcnow().isoformat()
}
```

**Creation Success:**
```python
return {
    "message": "Item created successfully",
    "item": {
        "id": "123",
        "name": "New Item"
    }
}
```

**Update Success:**
```python
return {
    "message": "Item updated successfully",
    "item": {
        "id": "123",
        "name": "Updated Item"
    }
}
```

**Delete Success:**
```python
return {
    "message": "Item deleted successfully"
}
# OR return nothing with 204 status
```

### Error Response Format

**Consistent Error Structure:**
```python
{
    "error": "Descriptive error message",
    "details": {
        "field": "name",
        "issue": "Required field missing"
    }
}
```

## ETag Support

ETags enable efficient HTTP caching by returning 304 Not Modified when data hasn't changed.

### Basic ETag Pattern

```python
from datetime import datetime
from fastapi import Request, Response
from fastapi import status as http_status
from src.server.utils.etag_utils import generate_etag, check_etag

@router.get("/items")
async def list_items(
    request: Request,
    response: Response
):
    """List items with ETag support."""
    try:
        # Get If-None-Match header from client
        if_none_match = request.headers.get("If-None-Match")

        # Get data from service
        repository = get_repository()
        service = YourService(repository=repository)
        success, result = await service.list_items()

        if not success:
            raise HTTPException(status_code=500, detail=result)

        items = result["items"]

        # Generate ETag from stable data (excluding timestamp)
        etag_data = {
            "items": items,
            "count": len(items)
        }
        current_etag = generate_etag(etag_data)

        # Check if client's ETag matches
        if check_etag(if_none_match, current_etag):
            response.status_code = http_status.HTTP_304_NOT_MODIFIED
            response.headers["ETag"] = current_etag
            response.headers["Cache-Control"] = "no-cache, must-revalidate"
            return None

        # Set ETag headers for new data
        response.headers["ETag"] = current_etag
        response.headers["Cache-Control"] = "no-cache, must-revalidate"
        response.headers["Last-Modified"] = datetime.utcnow().isoformat()

        # Return response with timestamp
        return {
            "items": items,
            "timestamp": datetime.utcnow().isoformat(),
            "count": len(items)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
```

### ETag Best Practices

1. **Exclude Timestamps from ETag**: Only use stable data that changes when content changes
2. **Include Count**: Include item count to detect additions/deletions
3. **Use Cache-Control**: Set `no-cache, must-revalidate` to force validation
4. **Return None on 304**: Return None when ETags match (FastAPI handles empty body)
5. **Set Last-Modified**: Provide Last-Modified header for additional caching hints

## Complete Examples

### Example 1: Task API with Repository

**Location**: `python/src/server/api_routes/projects_api.py`

```python
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi import status as http_status
from pydantic import BaseModel
from src.server.repositories import get_repository
from src.server.services.projects.task_service import TaskService
from src.server.utils.etag_utils import generate_etag, check_etag
from src.server.config.logfire_config import logfire

router = APIRouter(prefix="/api", tags=["tasks"])

class CreateTaskRequest(BaseModel):
    project_id: str
    title: str
    description: str | None = None
    assignee: str | None = "User"
    priority: str | None = "medium"

@router.post("/tasks")
async def create_task(request: CreateTaskRequest):
    """Create a new task."""
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
            priority=request.priority or "medium"
        )

        if not success:
            raise HTTPException(status_code=400, detail=result)

        created_task = result["task"]

        logfire.info(f"Task created | task_id={created_task['id']}")

        return {
            "message": "Task created successfully",
            "task": created_task
        }

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
    """List tasks for a project with ETag support."""
    try:
        # Get ETag from client
        if_none_match = request.headers.get("If-None-Match")

        logfire.debug(f"Listing tasks | project_id={project_id}")

        # Get repository and create service
        repository = get_repository()
        task_service = TaskService(repository=repository)

        # Get tasks
        success, result = await task_service.list_tasks(
            project_id=project_id,
            include_closed=True,
            include_archived=include_archived
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

        # Check for 304 Not Modified
        if check_etag(if_none_match, current_etag):
            response.status_code = http_status.HTTP_304_NOT_MODIFIED
            response.headers["ETag"] = current_etag
            response.headers["Cache-Control"] = "no-cache, must-revalidate"
            logfire.debug(f"Tasks unchanged | project_id={project_id}")
            return None

        # Set ETag headers
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


@router.get"/tasks/{task_id}")
async def get_task(task_id: str):
    """Get a specific task."""
    try:
        logfire.info(f"Getting task | task_id={task_id}")

        # Get repository and create service
        repository = get_repository()
        task_service = TaskService(repository=repository)

        # Get task
        success, result = await task_service.get_task(task_id)

        if not success:
            if "not found" in result.get("error", "").lower():
                raise HTTPException(status_code=404, detail=result)
            else:
                raise HTTPException(status_code=500, detail=result)

        logfire.info(f"Task retrieved | task_id={task_id}")

        return result["task"]

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Failed to get task | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


class UpdateTaskRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    assignee: str | None = None
    priority: str | None = None

@router.put("/tasks/{task_id}")
async def update_task(task_id: str, request: UpdateTaskRequest):
    """Update a task."""
    try:
        logfire.info(f"Updating task | task_id={task_id}")

        # Build update fields
        update_fields = {}
        if request.title is not None:
            update_fields["title"] = request.title
        if request.description is not None:
            update_fields["description"] = request.description
        if request.status is not None:
            update_fields["status"] = request.status
        if request.assignee is not None:
            update_fields["assignee"] = request.assignee
        if request.priority is not None:
            update_fields["priority"] = request.priority

        # Get repository and create service
        repository = get_repository()
        task_service = TaskService(repository=repository)

        # Update task
        success, result = await task_service.update_task(task_id, update_fields)

        if not success:
            if "not found" in result.get("error", "").lower():
                raise HTTPException(status_code=404, detail=result)
            else:
                raise HTTPException(status_code=500, detail=result)

        logfire.info(f"Task updated | task_id={task_id}")

        return {
            "message": "Task updated successfully",
            "task": result["task"]
        }

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

        # Get repository and create service
        repository = get_repository()
        task_service = TaskService(repository=repository)

        # Archive task
        success, result = await task_service.archive_task(task_id, archived_by="api")

        if not success:
            if "not found" in result.get("error", "").lower():
                raise HTTPException(status_code=404, detail=result)
            elif "already archived" in result.get("error", "").lower():
                raise HTTPException(status_code=409, detail=result)
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

### Example 2: Health Check Endpoint

```python
@router.get("/health")
async def health_check():
    """
    Health check using repository pattern.

    This endpoint demonstrates factory pattern usage.
    """
    try:
        logfire.info("Health check requested")

        # Get repository from factory
        repository = get_repository()

        # Test database connectivity
        try:
            service = YourService(repository=repository)
            success, _ = await service.list_items()
            database_ok = success
        except Exception as e:
            database_ok = False
            logfire.warning(f"Database check failed: {e}")

        result = {
            "status": "healthy" if database_ok else "degraded",
            "service": "your-service",
            "database": database_ok
        }

        logfire.info(f"Health check completed | status={result['status']}")

        return result

    except Exception as e:
        logfire.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "your-service",
            "error": str(e)
        }
```

## Common Patterns Summary

### ✅ DO: Use Factory Pattern

```python
repository = get_repository()
service = YourService(repository=repository)
```

### ✅ DO: Await Service Calls

```python
success, result = await service.method()
```

### ✅ DO: Handle HTTPException Separately

```python
except HTTPException:
    raise
except Exception as e:
    raise HTTPException(status_code=500, detail={"error": str(e)})
```

### ✅ DO: Use Structured Error Messages

```python
{"error": "Descriptive message", "details": {...}}
```

### ✅ DO: Add Logging

```python
logfire.info(f"Operation started | param={value}")
logfire.error(f"Operation failed | error={str(e)}")
```

### ❌ DON'T: Create Repository in Every Route

```python
# Bad
repository = SupabaseDatabaseRepository(get_supabase_client())
```

### ❌ DON'T: Forget to Await

```python
# Bad
result = service.method()  # Missing await
```

### ❌ DON'T: Return Plain Strings for Errors

```python
# Bad
return "Error occurred"

# Good
raise HTTPException(status_code=500, detail={"error": "Error occurred"})
```

## Next Steps

1. Review existing implementations in `python/src/server/api_routes/`
2. Follow patterns in `projects_api.py` for complex examples
3. Use `health` endpoints as templates for simple cases
4. Refer to `MIGRATION_GUIDE.md` for step-by-step conversion
5. Check `EXAMPLES.md` for complete working examples
