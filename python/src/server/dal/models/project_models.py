"""
Project Models

Pydantic models for project management including projects, features, and related entities.
Maps to the archon_projects table and related functionality.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .base_models import BaseEntity, MetadataMixin, StatusMixin, validate_non_empty_string


class ProjectFeature(BaseModel):
    """Individual project feature model."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(description="Feature ID")
    name: str = Field(description="Feature name", min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, description="Feature description")
    priority: str = Field(default="medium", description="Feature priority")
    status: str = Field(default="planned", description="Feature status")
    estimated_hours: Optional[float] = Field(default=None, ge=0, description="Estimated hours")
    assigned_to: Optional[str] = Field(default=None, description="Assignee")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate priority levels."""
        valid_priorities = ["low", "medium", "high", "critical"]
        if v.lower() not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")
        return v.lower()
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate feature status."""
        valid_statuses = ["planned", "in_progress", "completed", "on_hold", "cancelled"]
        if v.lower() not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v.lower()
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate feature name."""
        return validate_non_empty_string(v, "Feature name")


class ProjectDocument(BaseModel):
    """Project document reference model."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(description="Document ID")
    doc_type: str = Field(description="Document type")
    title: str = Field(description="Document title", min_length=1)
    author: str = Field(description="Document author")
    body: Dict[str, Any] = Field(default_factory=dict, description="Document content")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Update timestamp")
    
    @field_validator('doc_type')
    @classmethod
    def validate_doc_type(cls, v: str) -> str:
        """Validate document type."""
        valid_types = ["PRD", "FEATURE_SPEC", "REFACTOR_PLAN", "TECH_SPEC", "MEETING_NOTES"]
        if v.upper() not in valid_types:
            raise ValueError(f"Document type must be one of: {', '.join(valid_types)}")
        return v.upper()
    
    @field_validator('title', 'author')
    @classmethod
    def validate_required_strings(cls, v: str) -> str:
        """Validate required string fields."""
        return validate_non_empty_string(v)


class ProjectData(BaseModel):
    """Project data/ERD model."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(description="Data model ID")
    data_type: str = Field(description="Data model type")
    name: str = Field(description="Data model name", min_length=1)
    title: str = Field(description="Data model title")
    content: Dict[str, Any] = Field(default_factory=dict, description="Data model content")
    created_by: str = Field(description="Creator name")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    @field_validator('data_type')
    @classmethod
    def validate_data_type(cls, v: str) -> str:
        """Validate data model type."""
        valid_types = ["erd", "schema", "migration", "seed_data"]
        if v.lower() not in valid_types:
            raise ValueError(f"Data type must be one of: {', '.join(valid_types)}")
        return v.lower()


class Project(BaseEntity, StatusMixin):
    """
    Main project model.
    
    Maps to the archon_projects table with comprehensive project management features.
    """
    
    title: str = Field(
        description="Project title",
        min_length=1,
        max_length=200,
        examples=["E-commerce Platform", "Mobile App Redesign"]
    )
    
    description: str = Field(
        default="",
        description="Project description",
        max_length=2000,
        examples=["A modern e-commerce platform with React frontend and FastAPI backend"]
    )
    
    github_repo: Optional[str] = Field(
        default=None,
        description="GitHub repository URL",
        examples=["https://github.com/user/project"]
    )
    
    pinned: bool = Field(
        default=False,
        description="Whether the project is pinned for quick access"
    )
    
    # JSONB fields from database
    docs: List[ProjectDocument] = Field(
        default_factory=list,
        description="Project documentation"
    )
    
    features: List[ProjectFeature] = Field(
        default_factory=list,
        description="Project features list"
    )
    
    data: List[ProjectData] = Field(
        default_factory=list,
        description="Project data models and ERDs"
    )
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate project title."""
        return validate_non_empty_string(v, "Project title")
    
    @field_validator('github_repo')
    @classmethod
    def validate_github_repo(cls, v: Optional[str]) -> Optional[str]:
        """Validate GitHub repository URL."""
        if v is None:
            return None
        
        v = v.strip()
        if not v:
            return None
        
        # Basic GitHub URL validation
        if not (v.startswith('https://github.com/') or v.startswith('http://github.com/')):
            raise ValueError("GitHub repository must be a valid GitHub URL")
        
        return v
    
    @model_validator(mode='after')
    def validate_project_consistency(self) -> 'Project':
        """Validate project data consistency."""
        # Ensure feature names are unique
        feature_names = [f.name for f in self.features]
        if len(feature_names) != len(set(feature_names)):
            raise ValueError("Feature names must be unique within a project")
        
        # Ensure document titles are unique per type
        doc_keys = [(d.doc_type, d.title) for d in self.docs]
        if len(doc_keys) != len(set(doc_keys)):
            raise ValueError("Document titles must be unique per document type")
        
        return self
    
    # Feature management methods
    def add_feature(self, name: str, description: Optional[str] = None, **kwargs) -> ProjectFeature:
        """Add a new feature to the project."""
        # Check if feature already exists
        if any(f.name == name for f in self.features):
            raise ValueError(f"Feature '{name}' already exists")
        
        feature = ProjectFeature(
            id=f"feat_{len(self.features) + 1:03d}",
            name=name,
            description=description,
            **kwargs
        )
        self.features.append(feature)
        self.updated_at = datetime.utcnow()
        return feature
    
    def remove_feature(self, name: str) -> bool:
        """Remove a feature from the project."""
        original_count = len(self.features)
        self.features = [f for f in self.features if f.name != name]
        
        if len(self.features) < original_count:
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def get_feature(self, name: str) -> Optional[ProjectFeature]:
        """Get a feature by name."""
        return next((f for f in self.features if f.name == name), None)
    
    def update_feature(self, name: str, **updates) -> Optional[ProjectFeature]:
        """Update a feature."""
        feature = self.get_feature(name)
        if not feature:
            return None
        
        # Update feature fields
        for field, value in updates.items():
            if hasattr(feature, field):
                setattr(feature, field, value)
        
        self.updated_at = datetime.utcnow()
        return feature
    
    # Document management methods
    def add_document(self, doc_type: str, title: str, author: str, body: Dict[str, Any]) -> ProjectDocument:
        """Add a new document to the project."""
        # Check for duplicate titles in same type
        if any(d.doc_type == doc_type.upper() and d.title == title for d in self.docs):
            raise ValueError(f"Document '{title}' of type '{doc_type}' already exists")
        
        document = ProjectDocument(
            id=f"doc_{len(self.docs) + 1:03d}",
            doc_type=doc_type,
            title=title,
            author=author,
            body=body
        )
        self.docs.append(document)
        self.updated_at = datetime.utcnow()
        return document
    
    def remove_document(self, doc_id: str) -> bool:
        """Remove a document from the project."""
        original_count = len(self.docs)
        self.docs = [d for d in self.docs if d.id != doc_id]
        
        if len(self.docs) < original_count:
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def get_document(self, doc_id: str) -> Optional[ProjectDocument]:
        """Get a document by ID."""
        return next((d for d in self.docs if d.id == doc_id), None)
    
    def get_documents_by_type(self, doc_type: str) -> List[ProjectDocument]:
        """Get all documents of a specific type."""
        return [d for d in self.docs if d.doc_type == doc_type.upper()]
    
    # Data model management methods
    def add_data_model(self, data_type: str, name: str, title: str, 
                      content: Dict[str, Any], created_by: str) -> ProjectData:
        """Add a new data model to the project."""
        data_model = ProjectData(
            id=f"data_{len(self.data) + 1:03d}",
            data_type=data_type,
            name=name,
            title=title,
            content=content,
            created_by=created_by
        )
        self.data.append(data_model)
        self.updated_at = datetime.utcnow()
        return data_model
    
    # Utility methods
    @property
    def feature_count(self) -> int:
        """Get total number of features."""
        return len(self.features)
    
    @property
    def document_count(self) -> int:
        """Get total number of documents."""
        return len(self.docs)
    
    @property
    def data_model_count(self) -> int:
        """Get total number of data models."""
        return len(self.data)
    
    @property
    def completion_stats(self) -> Dict[str, Any]:
        """Get project completion statistics."""
        if not self.features:
            return {"total": 0, "completed": 0, "in_progress": 0, "planned": 0, "completion_rate": 0.0}
        
        total = len(self.features)
        completed = len([f for f in self.features if f.status == "completed"])
        in_progress = len([f for f in self.features if f.status == "in_progress"])
        planned = len([f for f in self.features if f.status == "planned"])
        
        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "planned": planned,
            "completion_rate": completed / total if total > 0 else 0.0
        }
    
    @property
    def priority_breakdown(self) -> Dict[str, int]:
        """Get feature priority breakdown."""
        breakdown = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for feature in self.features:
            breakdown[feature.priority] += 1
        return breakdown
    
    def to_summary(self) -> Dict[str, Any]:
        """Get project summary for listings."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description[:100] + "..." if len(self.description) > 100 else self.description,
            "status": self.status,
            "github_repo": self.github_repo,
            "pinned": self.pinned,
            "feature_count": self.feature_count,
            "document_count": self.document_count,
            "completion_rate": self.completion_stats["completion_rate"],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class ProjectWithTasks(Project):
    """Project model extended with related tasks information."""
    
    task_count: int = Field(default=0, description="Total number of tasks")
    open_task_count: int = Field(default=0, description="Number of open tasks")
    completed_task_count: int = Field(default=0, description="Number of completed tasks")
    task_completion_rate: float = Field(default=0.0, description="Task completion rate")
    
    @property
    def has_tasks(self) -> bool:
        """Check if project has any tasks."""
        return self.task_count > 0
    
    @property
    def task_progress(self) -> Dict[str, Any]:
        """Get detailed task progress information."""
        return {
            "total": self.task_count,
            "open": self.open_task_count,
            "completed": self.completed_task_count,
            "completion_rate": self.task_completion_rate,
            "remaining": self.task_count - self.completed_task_count
        }


class ProjectCreate(BaseModel):
    """Model for creating new projects."""
    
    model_config = ConfigDict(from_attributes=True)
    
    title: str = Field(description="Project title", min_length=1, max_length=200)
    description: str = Field(default="", description="Project description", max_length=2000)
    github_repo: Optional[str] = Field(default=None, description="GitHub repository URL")
    status: str = Field(default="active", description="Initial project status")
    features: List[str] = Field(default_factory=list, description="Initial feature names")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        return validate_non_empty_string(v, "Project title")


class ProjectUpdate(BaseModel):
    """Model for updating existing projects."""
    
    model_config = ConfigDict(from_attributes=True)
    
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    github_repo: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    pinned: Optional[bool] = Field(default=None)
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_non_empty_string(v, "Project title")
        return v


class ProjectFilter(BaseModel):
    """Model for filtering projects."""
    
    model_config = ConfigDict(from_attributes=True)
    
    status: Optional[Union[str, List[str]]] = Field(default=None, description="Status filter")
    pinned: Optional[bool] = Field(default=None, description="Pinned filter")
    github_repo: Optional[str] = Field(default=None, description="GitHub repo filter")
    feature: Optional[str] = Field(default=None, description="Feature filter")
    search_term: Optional[str] = Field(default=None, description="Search in title/description")
    created_after: Optional[datetime] = Field(default=None, description="Created after date")
    created_before: Optional[datetime] = Field(default=None, description="Created before date")
    
    @model_validator(mode='after')
    def validate_date_range(self) -> 'ProjectFilter':
        """Validate date range."""
        if (self.created_after and self.created_before and 
            self.created_after > self.created_before):
            raise ValueError("created_after must be before created_before")
        return self