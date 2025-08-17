"""
Domain Models Package

Comprehensive Pydantic models for all Archon entities including projects, tasks,
knowledge base items, settings, and search operations.

This package provides:
- Base models with common functionality
- Project and task management models
- Knowledge base models (sources, documents, code examples)
- Settings and configuration models
- Search and analytics models

All models support:
- Pydantic v2 validation
- JSON serialization/deserialization
- Database record mapping
- Field validation and constraints
- Type safety and IDE support
"""

# Base models and utilities
from .base_models import (
    BaseEntity,
    MetadataMixin,
    StatusMixin,
    TimestampMixin,
    VectorMixin,
    SearchResult as BaseSearchResult,
    ValidationError,
    PaginationParams,
    FilterParams,
    validate_url,
    validate_language_code,
    validate_non_empty_string,
    sanitize_json_metadata,
)

# Project models
from .project_models import (
    Project,
    ProjectDocument,
    ProjectFeature,
    ProjectData,
    ProjectWithTasks,
    ProjectCreate,
    ProjectUpdate,
    ProjectFilter,
)

# Task models
from .task_models import (
    Task,
    TaskStatus,
    TaskSource,
    TaskCodeExample,
    TaskCreate,
    TaskUpdate,
    TaskFilter,
    TaskStatistics,
)

# Knowledge models
from .knowledge_models import (
    Source,
    Document,
    CodeExample,
    KnowledgeItem,
    SourceCreate,
    DocumentCreate,
    CodeExampleCreate,
    KnowledgeFilter,
)

# Settings models
from .settings_models import (
    Setting,
    SettingEntity,
    SettingCategory,
    SettingType,
    SettingCreate,
    SettingUpdate,
    SettingFilter,
    SettingsSummary,
    SettingsExport,
    DefaultSettings,
)

# Search models
from .search_models import (
    SearchResult,
    CodeSearchResult,
    VectorSearchResult,
    SearchQuery,
    SearchResponse,
    SearchAnalytics,
    SearchType,
)

# Entity type mapping for repository pattern
ENTITY_MODELS = {
    "project": Project,
    "task": Task,
    "source": Source,
    "document": Document,
    "code_example": CodeExample,
    "setting": Setting,
}

# Create models (for API input)
CREATE_MODELS = {
    "project": ProjectCreate,
    "task": TaskCreate,
    "source": SourceCreate,
    "document": DocumentCreate,
    "code_example": CodeExampleCreate,
    "setting": SettingCreate,
}

# Update models (for API input)
UPDATE_MODELS = {
    "project": ProjectUpdate,
    "task": TaskUpdate,
    "setting": SettingUpdate,
}

# Filter models (for API queries)
FILTER_MODELS = {
    "project": ProjectFilter,
    "task": TaskFilter,
    "knowledge": KnowledgeFilter,
    "setting": SettingFilter,
}

__all__ = [
    # Base models
    "BaseEntity",
    "MetadataMixin",
    "StatusMixin", 
    "TimestampMixin",
    "VectorMixin",
    "BaseSearchResult",
    "ValidationError",
    "PaginationParams",
    "FilterParams",
    "validate_url",
    "validate_language_code",
    "validate_non_empty_string",
    "sanitize_json_metadata",
    
    # Project models
    "Project",
    "ProjectDocument",
    "ProjectFeature",
    "ProjectData",
    "ProjectWithTasks",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectFilter",
    
    # Task models
    "Task",
    "TaskStatus",
    "TaskSource",
    "TaskCodeExample",
    "TaskCreate",
    "TaskUpdate",
    "TaskFilter",
    "TaskStatistics",
    
    # Knowledge models
    "Source",
    "Document",
    "CodeExample",
    "KnowledgeItem",
    "SourceCreate",
    "DocumentCreate",
    "CodeExampleCreate",
    "KnowledgeFilter",
    
    # Settings models
    "Setting",
    "SettingEntity",
    "SettingCategory",
    "SettingType",
    "SettingCreate",
    "SettingUpdate",
    "SettingFilter",
    "SettingsSummary",
    "SettingsExport",
    "DefaultSettings",
    
    # Search models
    "SearchResult",
    "CodeSearchResult",
    "VectorSearchResult", 
    "SearchQuery",
    "SearchResponse",
    "SearchAnalytics",
    "SearchType",
    
    # Model mappings
    "ENTITY_MODELS",
    "CREATE_MODELS",
    "UPDATE_MODELS",
    "FILTER_MODELS",
]