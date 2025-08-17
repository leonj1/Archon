"""
Task Repository Interface

Interface for task management operations including task CRUD,
status management, and task-specific queries.
"""

from abc import abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base_repository import BaseRepository


class TaskEntity:
    """Task entity representation."""
    
    def __init__(
        self,
        id: str,
        project_id: str,
        title: str,
        description: Optional[str] = None,
        status: str = "todo",
        assignee: str = "User",
        task_order: int = 0,
        feature: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        sources: Optional[List[str]] = None,
        code_examples: Optional[List[Dict[str, Any]]] = None,
        estimated_hours: Optional[float] = None,
    ):
        self.id = id
        self.project_id = project_id
        self.title = title
        self.description = description
        self.status = status
        self.assignee = assignee
        self.task_order = task_order
        self.feature = feature
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.metadata = metadata or {}
        self.sources = sources or []
        self.code_examples = code_examples or []
        self.estimated_hours = estimated_hours
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "assignee": self.assignee,
            "task_order": self.task_order,
            "feature": self.feature,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "sources": self.sources,
            "code_examples": self.code_examples,
            "estimated_hours": self.estimated_hours,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskEntity":
        """Create entity from dictionary."""
        return cls(**data)


class ITaskRepository(BaseRepository[TaskEntity]):
    """
    Interface for task repository operations.
    Extends BaseRepository with task-specific functionality.
    """
    
    @abstractmethod
    async def get_by_project(
        self, 
        project_id: str,
        include_closed: bool = True
    ) -> List[TaskEntity]:
        """
        Get all tasks for a specific project.
        
        Args:
            project_id: Project ID
            include_closed: Whether to include closed/done tasks
            
        Returns:
            List of tasks for the project
        """
        pass
    
    @abstractmethod
    async def get_by_status(
        self, 
        status: str,
        project_id: Optional[str] = None
    ) -> List[TaskEntity]:
        """
        Get all tasks with a specific status.
        
        Args:
            status: Task status (todo, doing, review, done, etc.)
            project_id: Optional project ID to filter by
            
        Returns:
            List of tasks with the specified status
        """
        pass
    
    @abstractmethod
    async def get_by_assignee(
        self, 
        assignee: str,
        project_id: Optional[str] = None
    ) -> List[TaskEntity]:
        """
        Get all tasks assigned to a specific person.
        
        Args:
            assignee: Assignee name
            project_id: Optional project ID to filter by
            
        Returns:
            List of tasks assigned to the person
        """
        pass
    
    @abstractmethod
    async def get_by_feature(
        self, 
        feature: str,
        project_id: Optional[str] = None
    ) -> List[TaskEntity]:
        """
        Get all tasks related to a specific feature.
        
        Args:
            feature: Feature name
            project_id: Optional project ID to filter by
            
        Returns:
            List of tasks for the feature
        """
        pass
    
    @abstractmethod
    async def get_ordered_tasks(
        self, 
        project_id: str,
        status_filter: Optional[str] = None
    ) -> List[TaskEntity]:
        """
        Get tasks ordered by task_order (priority).
        
        Args:
            project_id: Project ID
            status_filter: Optional status to filter by
            
        Returns:
            List of tasks ordered by task_order desc (highest priority first)
        """
        pass
    
    @abstractmethod
    async def update_status(self, task_id: str, status: str) -> Optional[TaskEntity]:
        """
        Update task status.
        
        Args:
            task_id: Task ID
            status: New status
            
        Returns:
            Updated task entity or None if update failed
        """
        pass
    
    @abstractmethod
    async def update_assignee(self, task_id: str, assignee: str) -> Optional[TaskEntity]:
        """
        Update task assignee.
        
        Args:
            task_id: Task ID
            assignee: New assignee
            
        Returns:
            Updated task entity or None if update failed
        """
        pass
    
    @abstractmethod
    async def update_order(self, task_id: str, task_order: int) -> Optional[TaskEntity]:
        """
        Update task order/priority.
        
        Args:
            task_id: Task ID
            task_order: New task order (higher = higher priority)
            
        Returns:
            Updated task entity or None if update failed
        """
        pass
    
    @abstractmethod
    async def add_source(self, task_id: str, source: str) -> bool:
        """
        Add a source reference to a task.
        
        Args:
            task_id: Task ID
            source: Source reference to add
            
        Returns:
            True if source was added successfully
        """
        pass
    
    @abstractmethod
    async def remove_source(self, task_id: str, source: str) -> bool:
        """
        Remove a source reference from a task.
        
        Args:
            task_id: Task ID
            source: Source reference to remove
            
        Returns:
            True if source was removed successfully
        """
        pass
    
    @abstractmethod
    async def add_code_example(
        self, 
        task_id: str, 
        code_example: Dict[str, Any]
    ) -> bool:
        """
        Add a code example to a task.
        
        Args:
            task_id: Task ID
            code_example: Code example data
            
        Returns:
            True if code example was added successfully
        """
        pass
    
    @abstractmethod
    async def update_metadata(
        self, 
        task_id: str, 
        metadata: Dict[str, Any]
    ) -> Optional[TaskEntity]:
        """
        Update task metadata.
        
        Args:
            task_id: Task ID
            metadata: Metadata to update or merge
            
        Returns:
            Updated task entity or None if update failed
        """
        pass
    
    @abstractmethod
    async def update_estimated_hours(
        self, 
        task_id: str, 
        hours: float
    ) -> Optional[TaskEntity]:
        """
        Update estimated hours for a task.
        
        Args:
            task_id: Task ID
            hours: Estimated hours
            
        Returns:
            Updated task entity or None if update failed
        """
        pass
    
    @abstractmethod
    async def get_task_statistics(
        self, 
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get task statistics (counts by status, assignee, etc.).
        
        Args:
            project_id: Optional project ID to filter by
            
        Returns:
            Dictionary with task statistics
        """
        pass
    
    @abstractmethod
    async def search_tasks(
        self, 
        keyword: str,
        project_id: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> List[TaskEntity]:
        """
        Search tasks by keyword in title or description.
        
        Args:
            keyword: Search keyword
            project_id: Optional project ID to filter by
            status_filter: Optional status to filter by
            
        Returns:
            List of matching tasks
        """
        pass
    
    @abstractmethod
    async def get_next_priority_task(
        self, 
        project_id: str,
        assignee: Optional[str] = None
    ) -> Optional[TaskEntity]:
        """
        Get the next highest priority task that's ready to work on.
        
        Args:
            project_id: Project ID
            assignee: Optional assignee filter
            
        Returns:
            Next priority task or None if no tasks available
        """
        pass
    
    @abstractmethod
    async def bulk_update_status(
        self, 
        task_ids: List[str], 
        status: str
    ) -> int:
        """
        Update status for multiple tasks.
        
        Args:
            task_ids: List of task IDs
            status: New status
            
        Returns:
            Number of tasks successfully updated
        """
        pass
    
    @abstractmethod
    async def reorder_tasks(
        self, 
        project_id: str,
        task_order_mapping: Dict[str, int]
    ) -> bool:
        """
        Reorder multiple tasks by updating their task_order values.
        
        Args:
            project_id: Project ID
            task_order_mapping: Dictionary mapping task_id to new task_order
            
        Returns:
            True if reordering was successful
        """
        pass