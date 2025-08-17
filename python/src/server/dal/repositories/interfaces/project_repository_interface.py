"""
Project Repository Interface

Interface for project management operations including project CRUD,
feature management, and project-specific queries.
"""

from abc import abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base_repository import BaseRepository


class ProjectEntity:
    """Project entity representation."""
    
    def __init__(
        self,
        id: str,
        title: str,
        description: Optional[str] = None,
        status: str = "active",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        github_repo: Optional[str] = None,
        features: Optional[List[str]] = None,
        docs: Optional[Dict[str, Any]] = None,
        version: int = 1,
    ):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.metadata = metadata or {}
        self.github_repo = github_repo
        self.features = features or []
        self.docs = docs or {}
        self.version = version
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "github_repo": self.github_repo,
            "features": self.features,
            "docs": self.docs,
            "version": self.version,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectEntity":
        """Create entity from dictionary."""
        return cls(**data)


class IProjectRepository(BaseRepository[ProjectEntity]):
    """
    Interface for project repository operations.
    Extends BaseRepository with project-specific functionality.
    """
    
    @abstractmethod
    async def get_by_title(self, title: str) -> Optional[ProjectEntity]:
        """
        Get project by title.
        
        Args:
            title: Project title
            
        Returns:
            Project entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_status(self, status: str) -> List[ProjectEntity]:
        """
        Get all projects with a specific status.
        
        Args:
            status: Project status (active, archived, etc.)
            
        Returns:
            List of projects with the specified status
        """
        pass
    
    @abstractmethod
    async def get_by_github_repo(self, github_repo: str) -> Optional[ProjectEntity]:
        """
        Get project by GitHub repository.
        
        Args:
            github_repo: GitHub repository URL or path
            
        Returns:
            Project entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def add_feature(self, project_id: str, feature: str) -> bool:
        """
        Add a feature to a project.
        
        Args:
            project_id: Project ID
            feature: Feature name to add
            
        Returns:
            True if feature was added successfully
        """
        pass
    
    @abstractmethod
    async def remove_feature(self, project_id: str, feature: str) -> bool:
        """
        Remove a feature from a project.
        
        Args:
            project_id: Project ID
            feature: Feature name to remove
            
        Returns:
            True if feature was removed successfully
        """
        pass
    
    @abstractmethod
    async def get_features(self, project_id: str) -> List[str]:
        """
        Get all features for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of feature names
        """
        pass
    
    @abstractmethod
    async def update_features(self, project_id: str, features: List[str]) -> bool:
        """
        Update the complete feature list for a project.
        
        Args:
            project_id: Project ID
            features: Complete list of features
            
        Returns:
            True if features were updated successfully
        """
        pass
    
    @abstractmethod
    async def update_metadata(
        self, 
        project_id: str, 
        metadata: Dict[str, Any]
    ) -> Optional[ProjectEntity]:
        """
        Update project metadata.
        
        Args:
            project_id: Project ID
            metadata: Metadata to update or merge
            
        Returns:
            Updated project entity or None if update failed
        """
        pass
    
    @abstractmethod
    async def update_docs(
        self, 
        project_id: str, 
        docs: Dict[str, Any]
    ) -> Optional[ProjectEntity]:
        """
        Update project documentation references.
        
        Args:
            project_id: Project ID
            docs: Documentation metadata to update
            
        Returns:
            Updated project entity or None if update failed
        """
        pass
    
    @abstractmethod
    async def archive_project(self, project_id: str) -> bool:
        """
        Archive a project (set status to archived).
        
        Args:
            project_id: Project ID
            
        Returns:
            True if project was archived successfully
        """
        pass
    
    @abstractmethod
    async def activate_project(self, project_id: str) -> bool:
        """
        Activate a project (set status to active).
        
        Args:
            project_id: Project ID
            
        Returns:
            True if project was activated successfully
        """
        pass
    
    @abstractmethod
    async def increment_version(self, project_id: str) -> Optional[ProjectEntity]:
        """
        Increment the project version number.
        
        Args:
            project_id: Project ID
            
        Returns:
            Updated project entity with incremented version
        """
        pass
    
    @abstractmethod
    async def search_by_keyword(
        self, 
        keyword: str,
        include_archived: bool = False
    ) -> List[ProjectEntity]:
        """
        Search projects by keyword in title or description.
        
        Args:
            keyword: Search keyword
            include_archived: Whether to include archived projects
            
        Returns:
            List of matching projects
        """
        pass
    
    @abstractmethod
    async def get_recent_projects(
        self, 
        limit: int = 10,
        include_archived: bool = False
    ) -> List[ProjectEntity]:
        """
        Get recently updated projects.
        
        Args:
            limit: Maximum number of projects to return
            include_archived: Whether to include archived projects
            
        Returns:
            List of recent projects ordered by updated_at desc
        """
        pass
    
    @abstractmethod
    async def get_projects_with_feature(self, feature: str) -> List[ProjectEntity]:
        """
        Get all projects that have a specific feature.
        
        Args:
            feature: Feature name to search for
            
        Returns:
            List of projects with the specified feature
        """
        pass