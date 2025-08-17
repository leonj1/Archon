"""
Task Service Module for Archon

This module provides core business logic for task operations that can be
shared between MCP tools and FastAPI endpoints.
"""

# Removed direct logging import - using unified config
from datetime import datetime
from typing import Any

from ...config.logfire_config import get_logger
from ..client_manager import get_connection_manager

logger = get_logger(__name__)

# Import Socket.IO instance directly to avoid circular imports
try:
    from ...socketio_app import get_socketio_instance
    
    _sio = get_socketio_instance()
    _broadcast_available = True
    logger.info("✅ Socket.IO broadcasting is AVAILABLE - real-time updates enabled")
    
    async def broadcast_task_update(project_id: str, event_type: str, task_data: dict):
        """Broadcast task updates to project room."""
        await _sio.emit(event_type, task_data, room=project_id)
        logger.info(
            f"✅ Broadcasted {event_type} for task {task_data.get('id', 'unknown')} to project {project_id}"
        )
        
except ImportError as e:
    logger.warning(f"❌ Socket.IO broadcasting not available - ImportError: {e}")
    _broadcast_available = False
    _sio = None

    # Dummy function when broadcasting is not available
    async def broadcast_task_update(*args, **kwargs):
        logger.debug(f"Socket.IO broadcast skipped - not available")
        pass

except Exception as e:
    logger.warning(f"❌ Socket.IO broadcasting not available - Exception: {type(e).__name__}: {e}")
    import traceback

    logger.warning(f"❌ Full traceback: {traceback.format_exc()}")
    _broadcast_available = False
    _sio = None

    # Dummy function when broadcasting is not available
    async def broadcast_task_update(*args, **kwargs):
        logger.debug(f"Socket.IO broadcast skipped - not available")
        pass


class TaskService:
    """Service class for task operations"""

    VALID_STATUSES = ["todo", "doing", "review", "done"]

    def __init__(self, connection_manager=None):
        """Initialize with optional connection manager"""
        self.connection_manager = connection_manager or get_connection_manager()

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

    async def create_task(
        self,
        project_id: str,
        title: str,
        description: str = "",
        assignee: str = "User",
        task_order: int = 0,
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

            task_status = "todo"

            async with self.connection_manager.get_primary() as db:
                # REORDERING LOGIC: If inserting at a specific position, increment existing tasks
                if task_order > 0:
                    # Get all tasks in the same project and status with task_order >= new task's order
                    existing_tasks_response = await db.select(
                        table="tasks",
                        columns=["id", "task_order"],
                        filters={
                            "project_id": project_id,
                            "status": task_status,
                            "task_order": {"gte": task_order}
                        }
                    )

                    if existing_tasks_response.success and existing_tasks_response.data:
                        logger.info(f"Reordering {len(existing_tasks_response.data)} existing tasks")

                        # Increment task_order for all affected tasks
                        for existing_task in existing_tasks_response.data:
                            new_order = existing_task["task_order"] + 1
                            await db.update(
                                table="tasks",
                                data={
                                    "task_order": new_order,
                                    "updated_at": datetime.now().isoformat(),
                                },
                                filters={"id": existing_task["id"]}
                            )

                task_data = {
                    "project_id": project_id,
                    "title": title,
                    "description": description,
                    "status": task_status,
                    "assignee": assignee,
                    "task_order": task_order,
                    "sources": sources or [],
                    "code_examples": code_examples or [],
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                }

                if feature:
                    task_data["feature"] = feature

                response = await db.insert(
                    table="tasks",
                    data=task_data,
                    returning=["*"]
                )

                if response.success and response.data:
                    task = response.data[0]

                    # Broadcast Socket.IO update for new task
                    if _broadcast_available:
                        try:
                            await broadcast_task_update(
                                project_id=task["project_id"], event_type="task_created", task_data=task
                            )
                            logger.info(f"Socket.IO broadcast sent for new task {task['id']}")
                        except Exception as ws_error:
                            logger.warning(
                                f"Failed to broadcast Socket.IO update for new task {task['id']}: {ws_error}"
                            )

                    return True, {
                        "task": {
                            "id": task["id"],
                            "project_id": task["project_id"],
                            "title": task["title"],
                            "description": task["description"],
                            "status": task["status"],
                            "assignee": task["assignee"],
                            "task_order": task["task_order"],
                            "created_at": task["created_at"],
                        }
                    }
                else:
                    error_msg = response.error or "Failed to create task"
                    return False, {"error": error_msg}

        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return False, {"error": f"Error creating task: {str(e)}"}

    async def list_tasks(
        self, project_id: str = None, status: str = None, include_closed: bool = False
    ) -> tuple[bool, dict[str, Any]]:
        """
        List tasks with various filters.

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Build filters dictionary
            filters = {}
            filters_applied = []

            # Apply filters
            if project_id:
                filters["project_id"] = project_id
                filters_applied.append(f"project_id={project_id}")

            if status:
                # Validate status
                is_valid, error_msg = self.validate_status(status)
                if not is_valid:
                    return False, {"error": error_msg}
                filters["status"] = status
                filters_applied.append(f"status={status}")
                # When filtering by specific status, don't apply include_closed filter
                # as it would be redundant or potentially conflicting
            elif not include_closed:
                # Only exclude done tasks if no specific status filter is applied
                filters["status"] = {"neq": "done"}
                filters_applied.append("exclude done tasks")

            # Filter out archived tasks (null or false)
            filters["archived"] = {"or": [{"is": None}, {"eq": False}]}
            filters_applied.append("exclude archived tasks (null or false)")

            logger.info(f"Listing tasks with filters: {', '.join(filters_applied)}")

            async with self.connection_manager.get_reader() as db:
                # Execute query
                response = await db.select(
                    table="tasks",
                    columns=["*"],
                    filters=filters,
                    order_by="task_order ASC, created_at ASC"
                )

                if not response.success:
                    logger.error(f"Database error listing tasks: {response.error}")
                    return False, {"error": f"Database error: {response.error}"}

            # Debug: Log task status distribution and filter effectiveness
            if response.data:
                status_counts = {}
                archived_counts = {"null": 0, "true": 0, "false": 0}

                for task in response.data:
                    task_status = task.get("status", "unknown")
                    status_counts[task_status] = status_counts.get(task_status, 0) + 1

                    # Check archived field
                    archived_value = task.get("archived")
                    if archived_value is None:
                        archived_counts["null"] += 1
                    elif archived_value is True:
                        archived_counts["true"] += 1
                    else:
                        archived_counts["false"] += 1

                logger.info(
                    f"Retrieved {len(response.data)} tasks. Status distribution: {status_counts}"
                )
                logger.info(f"Archived field distribution: {archived_counts}")

                # If we're filtering by status and getting wrong results, log sample
                if status and len(response.data) > 0:
                    first_task = response.data[0]
                    logger.warning(
                        f"Status filter: {status}, First task status: {first_task.get('status')}, archived: {first_task.get('archived')}"
                    )
            else:
                logger.info("No tasks found with applied filters")

            return True, {
                "tasks": response.data,
                "total_count": len(response.data),
                "filters_applied": filters_applied,
            }

        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return False, {"error": f"Error listing tasks: {str(e)}"}

    async def get_task(self, task_id: str) -> tuple[bool, dict[str, Any]]:
        """
        Get a single task by ID.

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            async with self.connection_manager.get_reader() as db:
                response = await db.select(
                    table="tasks",
                    columns=["*"],
                    filters={"id": task_id}
                )

                if not response.success:
                    logger.error(f"Database error getting task: {response.error}")
                    return False, {"error": f"Database error: {response.error}"}

                if not response.data:
                    return False, {"error": f"Task with ID {task_id} not found"}

                return True, {"task": response.data[0]}

        except Exception as e:
            logger.error(f"Error getting task: {e}")
            return False, {"error": f"Error getting task: {str(e)}"}

    async def update_task(
        self, task_id: str, update_fields: dict[str, Any]
    ) -> tuple[bool, dict[str, Any]]:
        """
        Update a task.

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Validate status if provided
            if "status" in update_fields:
                is_valid, error_msg = self.validate_status(update_fields["status"])
                if not is_valid:
                    return False, {"error": error_msg}

            # Validate assignee if provided
            if "assignee" in update_fields:
                is_valid, error_msg = self.validate_assignee(update_fields["assignee"])
                if not is_valid:
                    return False, {"error": error_msg}

            # Add updated_at timestamp
            update_fields["updated_at"] = datetime.now().isoformat()

            async with self.connection_manager.get_primary() as db:
                response = await db.update(
                    table="tasks",
                    data=update_fields,
                    filters={"id": task_id},
                    returning=["*"]
                )

                if not response.success:
                    logger.error(f"Database error updating task: {response.error}")
                    return False, {"error": f"Database error: {response.error}"}

                if not response.data:
                    return False, {"error": f"Task with ID {task_id} not found"}

                task = response.data[0]

                # Broadcast Socket.IO update for task change
                if _broadcast_available:
                    try:
                        await broadcast_task_update(
                            project_id=task["project_id"], event_type="task_updated", task_data=task
                        )
                        logger.info(f"Socket.IO broadcast sent for updated task {task['id']}")
                    except Exception as ws_error:
                        logger.warning(
                            f"Failed to broadcast Socket.IO update for updated task {task['id']}: {ws_error}"
                        )

                return True, {"task": task}

        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return False, {"error": f"Error updating task: {str(e)}"}

    async def archive_task(self, task_id: str) -> tuple[bool, dict[str, Any]]:
        """
        Archive a task (soft delete).

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            async with self.connection_manager.get_primary() as db:
                response = await db.update(
                    table="tasks",
                    data={"archived": True, "updated_at": datetime.now().isoformat()},
                    filters={"id": task_id},
                    returning=["*"]
                )

                if not response.success:
                    logger.error(f"Database error archiving task: {response.error}")
                    return False, {"error": f"Database error: {response.error}"}

                if not response.data:
                    return False, {"error": f"Task with ID {task_id} not found"}

                task = response.data[0]

                # Broadcast Socket.IO update for task archival
                if _broadcast_available:
                    try:
                        await broadcast_task_update(
                            project_id=task["project_id"], event_type="task_archived", task_data=task
                        )
                        logger.info(f"Socket.IO broadcast sent for archived task {task['id']}")
                    except Exception as ws_error:
                        logger.warning(
                            f"Failed to broadcast Socket.IO update for archived task {task['id']}: {ws_error}"
                        )

                return True, {"task": task}

        except Exception as e:
            logger.error(f"Error archiving task: {e}")
            return False, {"error": f"Error archiving task: {str(e)}"}

    async def delete_task(self, task_id: str) -> tuple[bool, dict[str, Any]]:
        """
        Permanently delete a task.

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            async with self.connection_manager.get_primary() as db:
                # First get the task for broadcast
                get_response = await db.select(
                    table="tasks",
                    columns=["*"],
                    filters={"id": task_id}
                )

                if not get_response.success or not get_response.data:
                    return False, {"error": f"Task with ID {task_id} not found"}

                task = get_response.data[0]

                # Delete the task
                response = await db.delete(
                    table="tasks",
                    filters={"id": task_id}
                )

                if not response.success:
                    logger.error(f"Database error deleting task: {response.error}")
                    return False, {"error": f"Database error: {response.error}"}

                # Broadcast Socket.IO update for task deletion
                if _broadcast_available:
                    try:
                        await broadcast_task_update(
                            project_id=task["project_id"], event_type="task_deleted", task_data=task
                        )
                        logger.info(f"Socket.IO broadcast sent for deleted task {task['id']}")
                    except Exception as ws_error:
                        logger.warning(
                            f"Failed to broadcast Socket.IO update for deleted task {task['id']}: {ws_error}"
                        )

                return True, {"task_id": task_id}

        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return False, {"error": f"Error deleting task: {str(e)}"}