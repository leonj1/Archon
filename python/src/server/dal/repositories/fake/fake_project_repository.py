"""
Fake in-memory implementation of ProjectRepository for testing.
"""
import asyncio
import threading
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from uuid import uuid4

from ..interfaces.project_repository import ProjectRepository
from ...models.project import Project


class FakeProjectRepository(ProjectRepository):
    """In-memory implementation of ProjectRepository for testing."""
    
    def __init__(self):
        self._projects: Dict[str, Project] = {}
        self._lock = threading.RLock()
        self._next_id = 1

    def _generate_id(self) -> str:
        """Generate a realistic project ID."""
        with self._lock:
            project_id = f"proj_{self._next_id:06d}"
            self._next_id += 1
            return project_id

    async def create_project(
        self,
        title: str,
        description: Optional[str] = None,
        github_repo: Optional[str] = None,
        features: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Project:
        """Create a new project."""
        with self._lock:
            now = datetime.now(timezone.utc)
            project = Project(
                id=self._generate_id(),
                title=title,
                description=description,
                github_repo=github_repo,
                features=features or [],
                metadata=metadata or {},
                created_at=now,
                updated_at=now
            )
            self._projects[project.id] = project
            return project

    async def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID."""
        with self._lock:
            return self._projects.get(project_id)

    async def list_projects(
        self,
        limit: int = 50,
        offset: int = 0,
        search_query: Optional[str] = None
    ) -> List[Project]:
        """List projects with optional search and pagination."""
        with self._lock:
            projects = list(self._projects.values())
            
            # Apply search filter
            if search_query:
                search_lower = search_query.lower()
                projects = [
                    p for p in projects
                    if search_lower in p.title.lower() or
                    (p.description and search_lower in p.description.lower()) or
                    (p.github_repo and search_lower in p.github_repo.lower())
                ]
            
            # Sort by updated_at descending
            projects.sort(key=lambda p: p.updated_at, reverse=True)
            
            # Apply pagination
            return projects[offset:offset + limit]

    async def update_project(
        self,
        project_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        github_repo: Optional[str] = None,
        features: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Project]:
        """Update a project."""
        with self._lock:
            project = self._projects.get(project_id)
            if not project:
                return None
            
            # Update fields
            if title is not None:
                project.title = title
            if description is not None:
                project.description = description
            if github_repo is not None:
                project.github_repo = github_repo
            if features is not None:
                project.features = features
            if metadata is not None:
                project.metadata = metadata
            
            project.updated_at = datetime.now(timezone.utc)
            return project

    async def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        with self._lock:
            if project_id in self._projects:
                del self._projects[project_id]
                return True
            return False

    async def get_project_features(self, project_id: str) -> List[str]:
        """Get features for a project."""
        with self._lock:
            project = self._projects.get(project_id)
            return project.features if project else []

    async def add_project_feature(self, project_id: str, feature: str) -> bool:
        """Add a feature to a project."""
        with self._lock:
            project = self._projects.get(project_id)
            if not project:
                return False
            
            if feature not in project.features:
                project.features.append(feature)
                project.updated_at = datetime.now(timezone.utc)
            return True

    async def remove_project_feature(self, project_id: str, feature: str) -> bool:
        """Remove a feature from a project."""
        with self._lock:
            project = self._projects.get(project_id)
            if not project:
                return False
            
            if feature in project.features:
                project.features.remove(feature)
                project.updated_at = datetime.now(timezone.utc)
            return True

    async def count_projects(self, search_query: Optional[str] = None) -> int:
        """Count projects with optional search filter."""
        with self._lock:
            if not search_query:
                return len(self._projects)
            
            search_lower = search_query.lower()
            count = 0
            for project in self._projects.values():
                if (search_lower in project.title.lower() or
                    (project.description and search_lower in project.description.lower()) or
                    (project.github_repo and search_lower in project.github_repo.lower())):
                    count += 1
            return count

    # Test utility methods
    def clear_all(self) -> None:
        """Clear all projects (for testing)."""
        with self._lock:
            self._projects.clear()
            self._next_id = 1

    def get_all_projects(self) -> List[Project]:
        """Get all projects (for testing)."""
        with self._lock:
            return list(self._projects.values())