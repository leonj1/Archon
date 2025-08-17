"""
Repository Interface Definitions

Abstract base classes defining the contracts for domain-specific repository operations.
All repository implementations must implement these interfaces.
"""

from .base_repository import BaseRepository, T
from .knowledge_repository_interface import IKnowledgeRepository
from .project_repository_interface import IProjectRepository
from .search_repository_interface import ISearchRepository
from .settings_repository_interface import ISettingsRepository
from .task_repository_interface import ITaskRepository

__all__ = [
    "BaseRepository",
    "T",
    "IKnowledgeRepository", 
    "IProjectRepository",
    "ISearchRepository",
    "ISettingsRepository",
    "ITaskRepository",
]