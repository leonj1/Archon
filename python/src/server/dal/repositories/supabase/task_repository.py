"""
Supabase Task Repository Implementation

Concrete implementation of task repository for Supabase database backend.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import json

from ...interfaces import IDatabase, QueryResult
from ..interfaces.task_repository_interface import ITaskRepository, TaskEntity


class SupabaseTaskRepository(ITaskRepository):
    """
    Supabase implementation of task repository.
    Handles task CRUD operations for Supabase database backend.
    """
    
    def __init__(self, database: IDatabase, table_name: str = "tasks"):
        """
        Initialize Supabase task repository.
        
        Args:
            database: Supabase database interface
            table_name: Tasks table name
        """
        super().__init__(database, table_name)
    
    async def create(self, entity_data: Dict[str, Any]) -> Optional[TaskEntity]:
        """Create a new task."""
        try:
            # Ensure required fields are present
            if "id" not in entity_data:
                entity_data["id"] = f"task-{datetime.utcnow().strftime('%Y%m%d-%H%M%S-%f')[:20]}"
            
            # Set timestamps
            now = datetime.utcnow()
            entity_data.setdefault("created_at", now.isoformat())
            entity_data.setdefault("updated_at", now.isoformat())
            
            # Set defaults
            entity_data.setdefault("status", "todo")
            entity_data.setdefault("assignee", "User")
            entity_data.setdefault("task_order", 0)
            entity_data.setdefault("metadata", {})
            entity_data.setdefault("sources", [])
            entity_data.setdefault("code_examples", [])
            
            # Use adapter's insert method
            result = await self._database.insert(self._table_name, entity_data)
            
            if result.success and result.data:
                return TaskEntity.from_dict(result.data[0])
            return None
            
        except Exception as e:
            # Log error but don't crash - let caller handle
            return None
    
    async def get_by_id(self, entity_id: str) -> Optional[TaskEntity]:
        """Get task by ID."""
        try:
            result = await self._database.select(
                self._table_name,
                filters={"id": entity_id}
            )
            
            if result.success and result.data:
                return TaskEntity.from_dict(result.data[0])
            return None
            
        except Exception:
            return None
    
    async def update(self, entity_id: str, update_data: Dict[str, Any]) -> Optional[TaskEntity]:
        """Update an existing task."""
        try:
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self._database.update(
                self._table_name,
                update_data,
                filters={"id": entity_id}
            )
            
            if result.success and result.data:
                return TaskEntity.from_dict(result.data[0])
            return None
            
        except Exception:
            return None
    
    async def delete(self, entity_id: str) -> bool:
        """Delete a task by ID."""
        try:
            result = await self._database.delete(
                self._table_name,
                filters={"id": entity_id}
            )
            return result.success and result.affected_rows > 0
        except Exception:
            return False
    
    async def list_all(
        self, 
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[TaskEntity]:
        """List all tasks with optional pagination and ordering."""
        try:
            result = await self._database.select(
                self._table_name,
                order_by=order_by or "updated_at DESC",
                limit=limit,
                offset=offset
            )
            
            if result.success:
                return [TaskEntity.from_dict(row) for row in result.data]
            return []
            
        except Exception:
            return []
    
    async def find_by_criteria(
        self, 
        criteria: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[TaskEntity]:
        """Find tasks matching given criteria."""
        try:
            result = await self._database.select(
                self._table_name,
                filters=criteria,
                order_by=order_by or "updated_at DESC",
                limit=limit,
                offset=offset
            )
            
            if result.success:
                return [TaskEntity.from_dict(row) for row in result.data]
            return []
            
        except Exception:
            return []
    
    async def count(self, criteria: Optional[Dict[str, Any]] = None) -> int:
        """Count tasks matching optional criteria."""
        try:
            return await self._database.count(self._table_name, criteria)
        except Exception:
            return 0
    
    async def exists(self, entity_id: str) -> bool:
        """Check if task exists by ID."""
        try:
            return await self._database.exists(self._table_name, {"id": entity_id})
        except Exception:
            return False
    
    # Task-specific methods
    
    async def get_by_project(
        self, 
        project_id: str,
        include_closed: bool = True
    ) -> List[TaskEntity]:
        """Get all tasks for a specific project."""
        try:
            filters = {"project_id": project_id}
            if not include_closed:
                # For now, use a simple status filter; could be expanded
                filters["status"] = "todo"  # You might want to use NOT IN for multiple closed statuses
            
            return await self.find_by_criteria(
                filters, 
                order_by="task_order DESC, updated_at DESC"
            )
        except Exception:
            return []
    
    async def get_by_status(
        self, 
        status: str,
        project_id: Optional[str] = None
    ) -> List[TaskEntity]:
        """Get all tasks with a specific status."""
        try:
            filters = {"status": status}
            if project_id:
                filters["project_id"] = project_id
            
            return await self.find_by_criteria(
                filters,
                order_by="task_order DESC, updated_at DESC"
            )
        except Exception:
            return []
    
    async def get_by_assignee(
        self, 
        assignee: str,
        project_id: Optional[str] = None
    ) -> List[TaskEntity]:
        """Get all tasks assigned to a specific person."""
        try:
            filters = {"assignee": assignee}
            if project_id:
                filters["project_id"] = project_id
            
            return await self.find_by_criteria(
                filters,
                order_by="task_order DESC, updated_at DESC"
            )
        except Exception:
            return []
    
    async def get_by_feature(
        self, 
        feature: str,
        project_id: Optional[str] = None
    ) -> List[TaskEntity]:
        """Get all tasks related to a specific feature."""
        try:
            filters = {"feature": feature}
            if project_id:
                filters["project_id"] = project_id
            
            return await self.find_by_criteria(
                filters,
                order_by="task_order DESC, updated_at DESC"
            )
        except Exception:
            return []
    
    async def get_ordered_tasks(
        self, 
        project_id: str,
        status_filter: Optional[str] = None
    ) -> List[TaskEntity]:
        """Get tasks ordered by task_order (priority)."""
        try:
            filters = {"project_id": project_id}
            if status_filter:
                filters["status"] = status_filter
            
            return await self.find_by_criteria(
                filters,
                order_by="task_order DESC, created_at ASC"
            )
        except Exception:
            return []
    
    async def update_status(self, task_id: str, status: str) -> Optional[TaskEntity]:
        """Update task status."""
        return await self.update(task_id, {"status": status})
    
    async def update_assignee(self, task_id: str, assignee: str) -> Optional[TaskEntity]:
        """Update task assignee."""
        return await self.update(task_id, {"assignee": assignee})
    
    async def update_order(self, task_id: str, task_order: int) -> Optional[TaskEntity]:
        """Update task order/priority."""
        return await self.update(task_id, {"task_order": task_order})
    
    async def add_source(self, task_id: str, source: str) -> bool:
        """Add a source reference to a task."""
        try:
            task = await self.get_by_id(task_id)
            if not task:
                return False
            
            sources = list(task.sources) if task.sources else []
            if source not in sources:
                sources.append(source)
                result = await self.update(task_id, {"sources": sources})
                return result is not None
            
            return True  # Source already exists
            
        except Exception:
            return False
    
    async def remove_source(self, task_id: str, source: str) -> bool:
        """Remove a source reference from a task."""
        try:
            task = await self.get_by_id(task_id)
            if not task:
                return False
            
            sources = list(task.sources) if task.sources else []
            if source in sources:
                sources.remove(source)
                result = await self.update(task_id, {"sources": sources})
                return result is not None
            
            return True  # Source already removed
            
        except Exception:
            return False
    
    async def add_code_example(
        self, 
        task_id: str, 
        code_example: Dict[str, Any]
    ) -> bool:
        """Add a code example to a task."""
        try:
            task = await self.get_by_id(task_id)
            if not task:
                return False
            
            code_examples = list(task.code_examples) if task.code_examples else []
            code_examples.append(code_example)
            
            result = await self.update(task_id, {"code_examples": code_examples})
            return result is not None
            
        except Exception:
            return False
    
    async def update_metadata(
        self, 
        task_id: str, 
        metadata: Dict[str, Any]
    ) -> Optional[TaskEntity]:
        """Update task metadata."""
        try:
            # Get current metadata and merge
            task = await self.get_by_id(task_id)
            if not task:
                return None
            
            current_metadata = task.metadata or {}
            current_metadata.update(metadata)
            
            return await self.update(task_id, {"metadata": current_metadata})
        except Exception:
            return None
    
    async def update_estimated_hours(
        self, 
        task_id: str, 
        hours: float
    ) -> Optional[TaskEntity]:
        """Update estimated hours for a task."""
        return await self.update(task_id, {"estimated_hours": hours})
    
    async def get_task_statistics(
        self, 
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get task statistics (counts by status, assignee, etc.)."""
        try:
            # Base filters
            filters = {}
            if project_id:
                filters["project_id"] = project_id
            
            # Get all tasks matching filters
            tasks = await self.find_by_criteria(filters)
            
            # Calculate statistics
            stats = {
                "total_tasks": len(tasks),
                "by_status": {},
                "by_assignee": {},
                "by_feature": {},
            }
            
            for task in tasks:
                # Count by status
                status = task.status
                stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
                
                # Count by assignee
                assignee = task.assignee
                stats["by_assignee"][assignee] = stats["by_assignee"].get(assignee, 0) + 1
                
                # Count by feature
                if task.feature:
                    feature = task.feature
                    stats["by_feature"][feature] = stats["by_feature"].get(feature, 0) + 1
            
            return stats
            
        except Exception:
            return {
                "total_tasks": 0,
                "by_status": {},
                "by_assignee": {},
                "by_feature": {},
            }
    
    async def search_tasks(
        self, 
        keyword: str,
        project_id: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> List[TaskEntity]:
        """Search tasks by keyword in title or description."""
        try:
            # Get base filters
            filters = {}
            if project_id:
                filters["project_id"] = project_id
            if status_filter:
                filters["status"] = status_filter
            
            # Get all matching tasks and filter in memory
            # (Supabase adapter doesn't support LIKE queries directly)
            tasks = await self.find_by_criteria(filters)
            
            # Filter by keyword
            keyword_lower = keyword.lower()
            matching_tasks = []
            
            for task in tasks:
                if (keyword_lower in task.title.lower() or 
                    (task.description and keyword_lower in task.description.lower())):
                    matching_tasks.append(task)
            
            return matching_tasks
            
        except Exception:
            return []
    
    async def get_next_priority_task(
        self, 
        project_id: str,
        assignee: Optional[str] = None
    ) -> Optional[TaskEntity]:
        """Get the next highest priority task that's ready to work on."""
        try:
            filters = {
                "project_id": project_id,
                "status": "todo"  # Only ready tasks
            }
            if assignee:
                filters["assignee"] = assignee
            
            tasks = await self.find_by_criteria(
                filters,
                order_by="task_order DESC, created_at ASC",
                limit=1
            )
            
            return tasks[0] if tasks else None
            
        except Exception:
            return None
    
    async def bulk_update_status(
        self, 
        task_ids: List[str], 
        status: str
    ) -> int:
        """Update status for multiple tasks."""
        try:
            updated_count = 0
            for task_id in task_ids:
                result = await self.update_status(task_id, status)
                if result:
                    updated_count += 1
            
            return updated_count
            
        except Exception:
            return 0
    
    async def reorder_tasks(
        self, 
        project_id: str,
        task_order_mapping: Dict[str, int]
    ) -> bool:
        """Reorder multiple tasks by updating their task_order values."""
        try:
            updated_count = 0
            total_tasks = len(task_order_mapping)
            
            for task_id, new_order in task_order_mapping.items():
                result = await self.update_order(task_id, new_order)
                if result:
                    updated_count += 1
            
            # Return True if all tasks were successfully reordered
            return updated_count == total_tasks
            
        except Exception:
            return False