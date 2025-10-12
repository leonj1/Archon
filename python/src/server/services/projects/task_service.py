"""
Task Service Module for Archon

This module provides core business logic for task operations that can be
shared between MCP tools and FastAPI endpoints.
"""

# Removed direct logging import - using unified config
from datetime import datetime
from typing import Any, Optional

from src.server.utils import get_supabase_client
from ...repositories.database_repository import DatabaseRepository
from ...repositories.repository_factory import get_repository

from ...config.logfire_config import get_logger

logger = get_logger(__name__)

# Task updates are handled via polling - no broadcasting needed

class TaskService:
    """Service class for task operations"""

    VALID_STATUSES = ["todo", "doing", "review", "done"]

    def __init__(self, repository: Optional[DatabaseRepository] = None, supabase_client=None):
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
            self.repository = get_repository()

    def validate_status(self, status: str) -> tuple[bool, str]:
        """Validate task status"""
        if status not in self.VALID_STATUSES:
            return (
                False,
                f"Invalid status '{status}'. Must be one of: {', '.join(self.VALID_STATUSES)}",
            )
        return True, ""

    def validate_assignee(self, assignee: str) -> tuple[bool, str]:
        """Validate task assignee"""
        if not assignee or not isinstance(assignee, str) or len(assignee.strip()) == 0:
            return False, "Assignee must be a non-empty string"
        return True, ""

    def validate_priority(self, priority: str) -> tuple[bool, str]:
        """Validate task priority against allowed enum values"""
        VALID_PRIORITIES = ["low", "medium", "high", "critical"]
        if priority not in VALID_PRIORITIES:
            return (
                False,
                f"Invalid priority '{priority}'. Must be one of: {', '.join(VALID_PRIORITIES)}",
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
        sources: list[dict[str, Any]] = None,
        code_examples: list[dict[str, Any]] = None,
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

            # Validate assignee
            is_valid, error_msg = self.validate_assignee(assignee)
            if not is_valid:
                return False, {"error": error_msg}

            # Validate priority
            is_valid, error_msg = self.validate_priority(priority)
            if not is_valid:
                return False, {"error": error_msg}

            task_status = "todo"

            # REORDERING LOGIC: If inserting at a specific position, increment existing tasks
            if task_order > 0:
                # Get all tasks in the same project and status with task_order >= new task's order
                existing_tasks = await self.repository.get_tasks_by_project_and_status(
                    project_id=project_id,
                    status=task_status,
                    task_order_gte=task_order
                )

                if existing_tasks:
                    logger.info(f"Reordering {len(existing_tasks)} existing tasks")

                    # Increment task_order for all affected tasks
                    for existing_task in existing_tasks:
                        new_order = existing_task["task_order"] + 1
                        await self.repository.update_task(
                            task_id=existing_task["id"],
                            update_data={
                                "task_order": new_order,
                                "updated_at": datetime.now().isoformat(),
                            }
                        )

            task_data = {
                "project_id": project_id,
                "title": title,
                "description": description,
                "status": task_status,
                "assignee": assignee,
                "task_order": task_order,
                "priority": priority,
                "sources": sources or [],
                "code_examples": code_examples or [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            if feature:
                task_data["feature"] = feature

            task = await self.repository.create_task(task_data)

            if task:

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
        exclude_large_fields: bool = False,
        include_archived: bool = False,
        search_query: str = None
    ) -> tuple[bool, dict[str, Any]]:
        """
        List tasks with various filters.

        Args:
            project_id: Filter by project
            status: Filter by status
            include_closed: Include done tasks
            exclude_large_fields: If True, excludes sources and code_examples fields
            include_archived: If True, includes archived tasks
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
                assignee=None,  # Not filtering by assignee here
                include_archived=include_archived,
                exclude_large_fields=exclude_large_fields,
                search_query=search_query,
                order_by="task_order"
            )

            # Filter by "done" status if include_closed is False and no specific status
            if not status and not include_closed:
                # We'll filter out done tasks in the post-processing
                pass
            
            # Track filters for debugging
            filters_applied = []
            if project_id:
                filters_applied.append(f"project_id={project_id}")
            if status:
                filters_applied.append(f"status={status}")
            if search_query:
                filters_applied.append(f"search={search_query}")
            if not include_archived:
                filters_applied.append("exclude archived")
            if not include_closed:
                filters_applied.append("exclude done tasks")

            logger.debug(f"Listing tasks with filters: {', '.join(filters_applied)}")

            # Filter out done tasks if needed
            if not include_closed and not status:
                tasks = [t for t in tasks if t.get("status") != "done"]

            # Process tasks to match expected format
            processed_tasks = []
            for task in tasks:
                task_data = {
                    "id": task["id"],
                    "project_id": task["project_id"],
                    "title": task["title"],
                    "description": task["description"],
                    "status": task["status"],
                    "assignee": task.get("assignee", "User"),
                    "task_order": task.get("task_order", 0),
                    "priority": task.get("priority", "medium"),
                    "feature": task.get("feature"),
                    "created_at": task["created_at"],
                    "updated_at": task["updated_at"],
                    "archived": task.get("archived", False),
                }

                if not exclude_large_fields:
                    # Include full JSONB fields
                    task_data["sources"] = task.get("sources", [])
                    task_data["code_examples"] = task.get("code_examples", [])
                else:
                    # Add counts instead of full content
                    task_data["stats"] = {
                        "sources_count": len(task.get("sources", [])),
                        "code_examples_count": len(task.get("code_examples", []))
                    }

                processed_tasks.append(task_data)

            filter_info = []
            if project_id:
                filter_info.append(f"project_id={project_id}")
            if status:
                filter_info.append(f"status={status}")
            if not include_closed:
                filter_info.append("excluding closed tasks")

            return True, {
                "tasks": processed_tasks,
                "total_count": len(processed_tasks),
                "filters_applied": ", ".join(filter_info) if filter_info else "none",
                "include_closed": include_closed,
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
        self, task_id: str, update_fields: dict[str, Any]
    ) -> tuple[bool, dict[str, Any]]:
        """
        Update task with specified fields.

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Build update data
            update_data = {"updated_at": datetime.now().isoformat()}

            # Validate and add fields
            if "title" in update_fields:
                update_data["title"] = update_fields["title"]

            if "description" in update_fields:
                update_data["description"] = update_fields["description"]

            if "status" in update_fields:
                is_valid, error_msg = self.validate_status(update_fields["status"])
                if not is_valid:
                    return False, {"error": error_msg}
                update_data["status"] = update_fields["status"]

            if "assignee" in update_fields:
                is_valid, error_msg = self.validate_assignee(update_fields["assignee"])
                if not is_valid:
                    return False, {"error": error_msg}
                update_data["assignee"] = update_fields["assignee"]

            if "priority" in update_fields:
                is_valid, error_msg = self.validate_priority(update_fields["priority"])
                if not is_valid:
                    return False, {"error": error_msg}
                update_data["priority"] = update_fields["priority"]

            if "task_order" in update_fields:
                update_data["task_order"] = update_fields["task_order"]

            if "feature" in update_fields:
                update_data["feature"] = update_fields["feature"]

            # Update task
            task = await self.repository.update_task(
                task_id=task_id,
                update_data=update_data
            )

            if task:
                return True, {"task": task, "message": "Task updated successfully"}
            else:
                return False, {"error": f"Task with ID {task_id} not found"}

        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return False, {"error": f"Error updating task: {str(e)}"}

    async def archive_task(
        self, task_id: str, archived_by: str = "mcp"
    ) -> tuple[bool, dict[str, Any]]:
        """
        Archive a task and all its subtasks (soft delete).

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # First, check if task exists and is not already archived
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

            if not counts:
                logger.debug("No tasks found")
                return True, {}

            logger.debug(f"Task counts fetched for {len(counts)} projects")

            return True, counts

        except Exception as e:
            logger.error(f"Error fetching task counts: {e}")
            return False, {"error": f"Error fetching task counts: {str(e)}"}
