"""
Task Models

Pydantic models for task management including tasks, task status, and related entities.
Maps to the archon_tasks table and task workflow functionality.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .base_models import BaseEntity, MetadataMixin, validate_non_empty_string


class TaskStatus(str, Enum):
    """Task status enumeration matching database enum."""
    
    TODO = "todo"
    DOING = "doing" 
    REVIEW = "review"
    DONE = "done"
    
    @classmethod
    def get_valid_statuses(cls) -> List[str]:
        """Get list of valid status values."""
        return [status.value for status in cls]
    
    @classmethod
    def get_open_statuses(cls) -> List[str]:
        """Get list of open (not completed) status values."""
        return [cls.TODO.value, cls.DOING.value, cls.REVIEW.value]
    
    @classmethod
    def get_closed_statuses(cls) -> List[str]:
        """Get list of closed (completed) status values."""
        return [cls.DONE.value]
    
    def is_open(self) -> bool:
        """Check if status represents an open task."""
        return self.value in self.get_open_statuses()
    
    def is_closed(self) -> bool:
        """Check if status represents a closed task."""
        return self.value in self.get_closed_statuses()


class TaskSource(BaseModel):
    """Task source reference model."""
    
    model_config = ConfigDict(from_attributes=True)
    
    source_id: str = Field(description="Source ID from knowledge base")
    title: Optional[str] = Field(default=None, description="Source title")
    url: Optional[str] = Field(default=None, description="Source URL")
    relevance: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Relevance score")
    notes: Optional[str] = Field(default=None, description="Notes about this source")


class TaskCodeExample(BaseModel):
    """Task code example reference model."""
    
    model_config = ConfigDict(from_attributes=True)
    
    code_example_id: str = Field(description="Code example ID")
    title: Optional[str] = Field(default=None, description="Example title")
    language: Optional[str] = Field(default=None, description="Programming language")
    function_name: Optional[str] = Field(default=None, description="Function name")
    relevance: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Relevance score")
    notes: Optional[str] = Field(default=None, description="Notes about this example")


class Task(BaseEntity, MetadataMixin):
    """
    Main task model.
    
    Maps to the archon_tasks table with comprehensive task management features.
    """
    
    project_id: str = Field(
        description="ID of the project this task belongs to",
        examples=["01HQ2VPZ62KSF185Y54MQ93VD2"]
    )
    
    parent_task_id: Optional[str] = Field(
        default=None,
        description="ID of parent task for subtasks",
        examples=["01HQ2VPZ62KSF185Y54MQ93VD3"]
    )
    
    title: str = Field(
        description="Task title",
        min_length=1,
        max_length=300,
        examples=["Implement user authentication", "Design database schema"]
    )
    
    description: str = Field(
        default="",
        description="Detailed task description",
        max_length=5000,
        examples=["Create JWT-based authentication system with login/logout functionality"]
    )
    
    status: TaskStatus = Field(
        default=TaskStatus.TODO,
        description="Current task status"
    )
    
    assignee: str = Field(
        default="User",
        description="Person or agent assigned to this task",
        min_length=1,
        max_length=100,
        examples=["User", "Claude", "Agent-1", "john.doe"]
    )
    
    task_order: int = Field(
        default=0,
        description="Task priority order (higher = higher priority)",
        examples=[1, 5, 10]
    )
    
    feature: Optional[str] = Field(
        default=None,
        description="Feature this task belongs to",
        max_length=100,
        examples=["Authentication", "User Management", "API"]
    )
    
    # JSONB fields from database
    sources: List[TaskSource] = Field(
        default_factory=list,
        description="Knowledge sources related to this task"
    )
    
    code_examples: List[TaskCodeExample] = Field(
        default_factory=list,
        description="Code examples related to this task"
    )
    
    # Soft delete fields
    archived: bool = Field(
        default=False,
        description="Whether the task is archived (soft deleted)"
    )
    
    archived_at: Optional[datetime] = Field(
        default=None,
        description="When the task was archived"
    )
    
    archived_by: Optional[str] = Field(
        default=None,
        description="Who archived the task"
    )
    
    # Additional fields not in database but useful for the domain
    estimated_hours: Optional[float] = Field(
        default=None,
        ge=0,
        description="Estimated hours to complete",
        examples=[2.5, 8.0, 16.0]
    )
    
    actual_hours: Optional[float] = Field(
        default=None,
        ge=0,
        description="Actual hours spent"
    )
    
    due_date: Optional[datetime] = Field(
        default=None,
        description="Task due date"
    )
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate task title."""
        return validate_non_empty_string(v, "Task title")
    
    @field_validator('assignee')
    @classmethod
    def validate_assignee(cls, v: str) -> str:
        """Validate assignee."""
        return validate_non_empty_string(v, "Assignee")
    
    @field_validator('project_id', 'parent_task_id')
    @classmethod
    def validate_ids(cls, v: Optional[str]) -> Optional[str]:
        """Validate ID fields."""
        if v is not None:
            return validate_non_empty_string(v, "ID")
        return v
    
    @model_validator(mode='after')
    def validate_task_consistency(self) -> 'Task':
        """Validate task data consistency."""
        # Check due date is in the future
        if self.due_date and self.due_date < datetime.utcnow():
            # Allow past due dates but could add warning logic here
            pass
        
        # Validate actual hours vs estimated
        if (self.estimated_hours and self.actual_hours and 
            self.actual_hours > self.estimated_hours * 3):
            # Allow but could add warning for significantly over-estimated tasks
            pass
        
        # Ensure archived tasks have archived_at timestamp
        if self.archived and not self.archived_at:
            self.archived_at = datetime.utcnow()
        
        # Ensure non-archived tasks don't have archived fields set
        if not self.archived:
            self.archived_at = None
            self.archived_by = None
        
        return self
    
    # Status management methods
    def move_to_doing(self, assignee: Optional[str] = None) -> None:
        """Move task to doing status."""
        self.status = TaskStatus.DOING
        if assignee:
            self.assignee = assignee
        self.updated_at = datetime.utcnow()
    
    def move_to_review(self) -> None:
        """Move task to review status."""
        self.status = TaskStatus.REVIEW
        self.updated_at = datetime.utcnow()
    
    def complete(self) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.DONE
        self.updated_at = datetime.utcnow()
    
    def reopen(self) -> None:
        """Reopen a completed task."""
        self.status = TaskStatus.TODO
        self.updated_at = datetime.utcnow()
    
    def archive(self, archived_by: str = "system") -> None:
        """Archive the task (soft delete)."""
        self.archived = True
        self.archived_at = datetime.utcnow()
        self.archived_by = archived_by
        self.updated_at = datetime.utcnow()
    
    def unarchive(self) -> None:
        """Unarchive the task."""
        self.archived = False
        self.archived_at = None
        self.archived_by = None
        self.updated_at = datetime.utcnow()
    
    # Source management methods
    def add_source(self, source_id: str, title: Optional[str] = None, 
                  url: Optional[str] = None, relevance: Optional[float] = None,
                  notes: Optional[str] = None) -> TaskSource:
        """Add a source reference to the task."""
        # Check if source already exists
        if any(s.source_id == source_id for s in self.sources):
            raise ValueError(f"Source '{source_id}' already exists in task")
        
        source = TaskSource(
            source_id=source_id,
            title=title,
            url=url,
            relevance=relevance,
            notes=notes
        )
        self.sources.append(source)
        self.updated_at = datetime.utcnow()
        return source
    
    def remove_source(self, source_id: str) -> bool:
        """Remove a source reference from the task."""
        original_count = len(self.sources)
        self.sources = [s for s in self.sources if s.source_id != source_id]
        
        if len(self.sources) < original_count:
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def get_source(self, source_id: str) -> Optional[TaskSource]:
        """Get a source by ID."""
        return next((s for s in self.sources if s.source_id == source_id), None)
    
    # Code example management methods
    def add_code_example(self, code_example_id: str, title: Optional[str] = None,
                        language: Optional[str] = None, function_name: Optional[str] = None,
                        relevance: Optional[float] = None, notes: Optional[str] = None) -> TaskCodeExample:
        """Add a code example reference to the task."""
        # Check if code example already exists
        if any(c.code_example_id == code_example_id for c in self.code_examples):
            raise ValueError(f"Code example '{code_example_id}' already exists in task")
        
        code_example = TaskCodeExample(
            code_example_id=code_example_id,
            title=title,
            language=language,
            function_name=function_name,
            relevance=relevance,
            notes=notes
        )
        self.code_examples.append(code_example)
        self.updated_at = datetime.utcnow()
        return code_example
    
    def remove_code_example(self, code_example_id: str) -> bool:
        """Remove a code example reference from the task."""
        original_count = len(self.code_examples)
        self.code_examples = [c for c in self.code_examples if c.code_example_id != code_example_id]
        
        if len(self.code_examples) < original_count:
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    # Utility properties
    @property
    def is_open(self) -> bool:
        """Check if task is open (not completed)."""
        return self.status.is_open()
    
    @property
    def is_closed(self) -> bool:
        """Check if task is closed (completed)."""
        return self.status.is_closed()
    
    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        return (self.due_date is not None and 
                self.due_date < datetime.utcnow() and 
                self.is_open)
    
    @property
    def has_subtasks(self) -> bool:
        """Check if task has subtasks (would need to be determined by repository)."""
        # This would need to be populated by the repository layer
        return False
    
    @property
    def is_subtask(self) -> bool:
        """Check if task is a subtask."""
        return self.parent_task_id is not None
    
    @property
    def source_count(self) -> int:
        """Get number of sources."""
        return len(self.sources)
    
    @property
    def code_example_count(self) -> int:
        """Get number of code examples."""
        return len(self.code_examples)
    
    @property
    def progress_info(self) -> Dict[str, Any]:
        """Get task progress information."""
        return {
            "status": self.status.value,
            "is_open": self.is_open,
            "is_closed": self.is_closed,
            "is_overdue": self.is_overdue,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "due_date": self.due_date,
            "sources": self.source_count,
            "code_examples": self.code_example_count
        }
    
    def to_summary(self) -> Dict[str, Any]:
        """Get task summary for listings."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description[:100] + "..." if len(self.description) > 100 else self.description,
            "status": self.status.value,
            "assignee": self.assignee,
            "task_order": self.task_order,
            "feature": self.feature,
            "is_overdue": self.is_overdue,
            "source_count": self.source_count,
            "code_example_count": self.code_example_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class TaskCreate(BaseModel):
    """Model for creating new tasks."""
    
    model_config = ConfigDict(from_attributes=True)
    
    project_id: str = Field(description="Project ID")
    parent_task_id: Optional[str] = Field(default=None, description="Parent task ID for subtasks")
    title: str = Field(description="Task title", min_length=1, max_length=300)
    description: str = Field(default="", description="Task description", max_length=5000)
    assignee: str = Field(default="User", description="Task assignee")
    task_order: int = Field(default=0, description="Task priority order")
    feature: Optional[str] = Field(default=None, description="Feature name")
    estimated_hours: Optional[float] = Field(default=None, ge=0, description="Estimated hours")
    due_date: Optional[datetime] = Field(default=None, description="Due date")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        return validate_non_empty_string(v, "Task title")
    
    @field_validator('project_id')
    @classmethod
    def validate_project_id(cls, v: str) -> str:
        return validate_non_empty_string(v, "Project ID")


class TaskUpdate(BaseModel):
    """Model for updating existing tasks."""
    
    model_config = ConfigDict(from_attributes=True)
    
    title: Optional[str] = Field(default=None, min_length=1, max_length=300)
    description: Optional[str] = Field(default=None, max_length=5000)
    status: Optional[TaskStatus] = Field(default=None)
    assignee: Optional[str] = Field(default=None, min_length=1)
    task_order: Optional[int] = Field(default=None)
    feature: Optional[str] = Field(default=None)
    estimated_hours: Optional[float] = Field(default=None, ge=0)
    actual_hours: Optional[float] = Field(default=None, ge=0)
    due_date: Optional[datetime] = Field(default=None)
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_non_empty_string(v, "Task title")
        return v


class TaskFilter(BaseModel):
    """Model for filtering tasks."""
    
    model_config = ConfigDict(from_attributes=True)
    
    project_id: Optional[str] = Field(default=None, description="Project ID filter")
    status: Optional[Union[TaskStatus, List[TaskStatus]]] = Field(default=None, description="Status filter")
    assignee: Optional[str] = Field(default=None, description="Assignee filter")
    feature: Optional[str] = Field(default=None, description="Feature filter")
    is_archived: Optional[bool] = Field(default=False, description="Include archived tasks")
    is_overdue: Optional[bool] = Field(default=None, description="Overdue tasks filter")
    has_due_date: Optional[bool] = Field(default=None, description="Tasks with due dates")
    search_term: Optional[str] = Field(default=None, description="Search in title/description")
    created_after: Optional[datetime] = Field(default=None, description="Created after date")
    created_before: Optional[datetime] = Field(default=None, description="Created before date")
    
    @model_validator(mode='after')
    def validate_date_range(self) -> 'TaskFilter':
        """Validate date range."""
        if (self.created_after and self.created_before and 
            self.created_after > self.created_before):
            raise ValueError("created_after must be before created_before")
        return self


class TaskStatistics(BaseModel):
    """Task statistics model."""
    
    model_config = ConfigDict(from_attributes=True)
    
    total_tasks: int = Field(description="Total number of tasks")
    open_tasks: int = Field(description="Number of open tasks")
    closed_tasks: int = Field(description="Number of closed tasks")
    archived_tasks: int = Field(description="Number of archived tasks")
    overdue_tasks: int = Field(description="Number of overdue tasks")
    
    status_breakdown: Dict[str, int] = Field(
        default_factory=dict,
        description="Task count by status"
    )
    
    assignee_breakdown: Dict[str, int] = Field(
        default_factory=dict,
        description="Task count by assignee"
    )
    
    feature_breakdown: Dict[str, int] = Field(
        default_factory=dict,
        description="Task count by feature"
    )
    
    @property
    def completion_rate(self) -> float:
        """Calculate task completion rate."""
        if self.total_tasks == 0:
            return 0.0
        return self.closed_tasks / self.total_tasks
    
    @property
    def open_rate(self) -> float:
        """Calculate open task rate."""
        if self.total_tasks == 0:
            return 0.0
        return self.open_tasks / self.total_tasks