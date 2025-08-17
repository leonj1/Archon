"""
Fake in-memory implementation of TaskRepository for testing.
"""
import threading
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from enum import Enum

from ..interfaces.task_repository import TaskRepository
from ...models.task import Task, TaskStatus


class FakeTaskRepository(TaskRepository):
    """In-memory implementation of TaskRepository for testing."""
    
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._lock = threading.RLock()
        self._next_id = 1

    def _generate_id(self) -> str:
        """Generate a realistic task ID."""
        with self._lock:
            task_id = f"task_{self._next_id:06d}"
            self._next_id += 1
            return task_id

    async def create_task(
        self,
        title: str,
        project_id: Optional[str] = None,
        description: Optional[str] = None,
        status: TaskStatus = TaskStatus.TODO,
        feature: Optional[str] = None,
        task_order: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Task:
        """Create a new task."""
        with self._lock:
            now = datetime.now(timezone.utc)
            task = Task(
                id=self._generate_id(),
                title=title,
                project_id=project_id,
                description=description,
                status=status,
                feature=feature,
                task_order=task_order,
                metadata=metadata or {},
                created_at=now,
                updated_at=now
            )
            self._tasks[task.id] = task
            return task

    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        with self._lock:
            return self._tasks.get(task_id)

    async def list_tasks(
        self,
        project_id: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        feature: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        search_query: Optional[str] = None,
        include_closed: bool = True
    ) -> List[Task]:
        """List tasks with filtering and pagination."""
        with self._lock:
            tasks = list(self._tasks.values())
            
            # Apply filters
            if project_id:
                tasks = [t for t in tasks if t.project_id == project_id]
            
            if status:
                tasks = [t for t in tasks if t.status == status]
            
            if feature:
                tasks = [t for t in tasks if t.feature == feature]
            
            if not include_closed:
                tasks = [t for t in tasks if t.status not in [TaskStatus.DONE, TaskStatus.ARCHIVED]]
            
            if search_query:
                search_lower = search_query.lower()
                tasks = [
                    t for t in tasks
                    if search_lower in t.title.lower() or
                    (t.description and search_lower in t.description.lower()) or
                    (t.feature and search_lower in t.feature.lower())
                ]
            
            # Sort by task_order (descending), then by created_at (descending)
            tasks.sort(key=lambda t: (-t.task_order, t.created_at), reverse=True)
            
            # Apply pagination
            return tasks[offset:offset + limit]

    async def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        feature: Optional[str] = None,
        task_order: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Task]:
        """Update a task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None
            
            # Update fields
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if status is not None:
                task.status = status
            if feature is not None:
                task.feature = feature
            if task_order is not None:
                task.task_order = task_order
            if metadata is not None:
                task.metadata = metadata
            
            task.updated_at = datetime.now(timezone.utc)
            return task

    async def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                return True
            return False

    async def archive_task(self, task_id: str) -> bool:
        """Archive a task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            
            task.status = TaskStatus.ARCHIVED
            task.updated_at = datetime.now(timezone.utc)
            return True

    async def get_tasks_by_project(
        self,
        project_id: str,
        include_closed: bool = True
    ) -> List[Task]:
        """Get all tasks for a project."""
        return await self.list_tasks(
            project_id=project_id,
            include_closed=include_closed,
            limit=1000  # Large limit to get all tasks
        )

    async def get_tasks_by_status(
        self,
        status: TaskStatus,
        project_id: Optional[str] = None
    ) -> List[Task]:
        """Get tasks by status."""
        return await self.list_tasks(
            project_id=project_id,
            status=status,
            limit=1000  # Large limit to get all tasks
        )

    async def get_tasks_by_feature(
        self,
        feature: str,
        project_id: Optional[str] = None
    ) -> List[Task]:
        """Get tasks by feature."""
        return await self.list_tasks(
            project_id=project_id,
            feature=feature,
            limit=1000  # Large limit to get all tasks
        )

    async def count_tasks(
        self,
        project_id: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        feature: Optional[str] = None,
        search_query: Optional[str] = None,
        include_closed: bool = True
    ) -> int:
        """Count tasks with filtering."""
        with self._lock:
            tasks = list(self._tasks.values())
            
            # Apply same filters as list_tasks
            if project_id:
                tasks = [t for t in tasks if t.project_id == project_id]
            
            if status:
                tasks = [t for t in tasks if t.status == status]
            
            if feature:
                tasks = [t for t in tasks if t.feature == feature]
            
            if not include_closed:
                tasks = [t for t in tasks if t.status not in [TaskStatus.DONE, TaskStatus.ARCHIVED]]
            
            if search_query:
                search_lower = search_query.lower()
                tasks = [
                    t for t in tasks
                    if search_lower in t.title.lower() or
                    (t.description and search_lower in t.description.lower()) or
                    (t.feature and search_lower in t.feature.lower())
                ]
            
            return len(tasks)

    async def get_next_task_order(self, project_id: Optional[str] = None) -> int:
        """Get the next task order number."""
        with self._lock:
            tasks = list(self._tasks.values())
            if project_id:
                tasks = [t for t in tasks if t.project_id == project_id]
            
            if not tasks:
                return 1
            
            max_order = max(t.task_order for t in tasks)
            return max_order + 1

    async def reorder_tasks(
        self,
        task_orders: List[tuple[str, int]]
    ) -> bool:
        """Reorder multiple tasks."""
        with self._lock:
            try:
                for task_id, new_order in task_orders:
                    task = self._tasks.get(task_id)
                    if task:
                        task.task_order = new_order
                        task.updated_at = datetime.now(timezone.utc)
                return True
            except Exception:
                return False

    # Test utility methods
    def clear_all(self) -> None:
        """Clear all tasks (for testing)."""
        with self._lock:
            self._tasks.clear()
            self._next_id = 1

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks (for testing)."""
        with self._lock:
            return list(self._tasks.values())

    def get_task_count_by_status(self) -> Dict[TaskStatus, int]:
        """Get count of tasks by status (for testing)."""
        with self._lock:
            counts = {status: 0 for status in TaskStatus}
            for task in self._tasks.values():
                counts[task.status] += 1
            return counts