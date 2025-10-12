"""
Project Service Module for Archon

This module provides core business logic for project operations that can be
shared between MCP tools and FastAPI endpoints. It follows the pattern of
separating business logic from transport-specific code.
"""

# Removed direct logging import - using unified config
from datetime import datetime
from typing import Any, Optional

from src.server.utils import get_supabase_client
from ...repositories.database_repository import DatabaseRepository
from ...repositories.supabase_repository import SupabaseDatabaseRepository

from ...config.logfire_config import get_logger

logger = get_logger(__name__)


class ProjectService:
    """Service class for project operations"""

    def __init__(self, repository: Optional[DatabaseRepository] = None, supabase_client=None):
        """
        Initialize with optional repository or supabase client.

        Args:
            repository: DatabaseRepository instance (preferred)
            supabase_client: Legacy supabase client (for backward compatibility)
        """
        if repository is not None:
            self.repository = repository
        elif supabase_client is not None:
            self.repository = SupabaseDatabaseRepository(supabase_client)
        else:
            self.repository = SupabaseDatabaseRepository(get_supabase_client())

    async def create_project(self, title: str, github_repo: str = None) -> tuple[bool, dict[str, Any]]:
        """
        Create a new project with optional PRD and GitHub repo.

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Validate inputs
            if not title or not isinstance(title, str) or len(title.strip()) == 0:
                return False, {"error": "Project title is required and must be a non-empty string"}

            # Create project data
            project_data = {
                "title": title.strip(),
                "docs": [],
                "features": [],
                "data": [],
            }

            if github_repo and isinstance(github_repo, str) and len(github_repo.strip()) > 0:
                project_data["github_repo"] = github_repo.strip()

            # Create project via repository
            project = await self.repository.create_project(project_data)

            project_id = project["id"]
            logger.info(f"Project created successfully with ID: {project_id}")

            return True, {
                "project": {
                    "id": project_id,
                    "title": project["title"],
                    "github_repo": project.get("github_repo"),
                    "created_at": project["created_at"],
                }
            }

        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return False, {"error": f"Database error: {str(e)}"}

    async def list_projects(self, include_content: bool = True) -> tuple[bool, dict[str, Any]]:
        """
        List all projects.

        Args:
            include_content: If True (default), includes docs, features, data fields.
                           If False, returns lightweight metadata only with counts.

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Fetch all projects via repository
            raw_projects = await self.repository.list_projects(
                include_content=True,
                order_by="created_at",
                desc=True
            )

            projects = []
            if include_content:
                # Return full project data
                for project in raw_projects:
                    projects.append({
                        "id": project["id"],
                        "title": project["title"],
                        "github_repo": project.get("github_repo"),
                        "created_at": project["created_at"],
                        "updated_at": project["updated_at"],
                        "pinned": project.get("pinned", False),
                        "description": project.get("description", ""),
                        "docs": project.get("docs", []),
                        "features": project.get("features", []),
                        "data": project.get("data", []),
                    })
            else:
                # Lightweight response for MCP - calculate stats from fetched data
                for project in raw_projects:
                    docs_count = len(project.get("docs", []))
                    features_count = len(project.get("features", []))
                    has_data = bool(project.get("data", []))

                    projects.append({
                        "id": project["id"],
                        "title": project["title"],
                        "github_repo": project.get("github_repo"),
                        "created_at": project["created_at"],
                        "updated_at": project["updated_at"],
                        "pinned": project.get("pinned", False),
                        "description": project.get("description", ""),
                        "stats": {
                            "docs_count": docs_count,
                            "features_count": features_count,
                            "has_data": has_data
                        }
                    })

            return True, {"projects": projects, "total_count": len(projects)}

        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return False, {"error": f"Error listing projects: {str(e)}"}

    async def get_project(self, project_id: str) -> tuple[bool, dict[str, Any]]:
        """
        Get a specific project by ID.

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Get project via repository
            project = await self.repository.get_project_by_id(project_id)

            if not project:
                return False, {"error": f"Project with ID {project_id} not found"}

            # Get linked sources
            technical_sources = []
            business_sources = []

            try:
                # Get source links from project_sources table
                source_links = await self.repository.list_project_sources(project_id)

                # Collect source IDs by type
                technical_source_ids = []
                business_source_ids = []

                for source_link in source_links:
                    if source_link.get("notes") == "technical":
                        technical_source_ids.append(source_link["source_id"])
                    elif source_link.get("notes") == "business":
                        business_source_ids.append(source_link["source_id"])

                # Fetch full source objects
                if technical_source_ids:
                    technical_sources = await self.repository.get_sources_for_project(
                        project_id, technical_source_ids
                    )

                if business_source_ids:
                    business_sources = await self.repository.get_sources_for_project(
                        project_id, business_source_ids
                    )

            except Exception as e:
                logger.warning(
                    f"Failed to retrieve linked sources for project {project['id']}: {e}"
                )

            # Add sources to project data
            project["technical_sources"] = technical_sources
            project["business_sources"] = business_sources

            return True, {"project": project}

        except Exception as e:
            logger.error(f"Error getting project: {e}")
            return False, {"error": f"Error getting project: {str(e)}"}

    async def delete_project(self, project_id: str) -> tuple[bool, dict[str, Any]]:
        """
        Delete a project and all its associated tasks.

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Check if project exists
            project = await self.repository.get_project_by_id(project_id)
            if not project:
                return False, {"error": f"Project with ID {project_id} not found"}

            # Get task count for reporting (before deletion)
            tasks = await self.repository.list_tasks(project_id=project_id, include_archived=True)
            tasks_count = len(tasks)

            # Delete the project (tasks will be deleted by cascade)
            deleted = await self.repository.delete_project(project_id)

            if not deleted:
                return False, {"error": f"Failed to delete project {project_id}"}

            return True, {
                "project_id": project_id,
                "deleted_tasks": tasks_count,
                "message": "Project deleted successfully",
            }

        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            return False, {"error": f"Error deleting project: {str(e)}"}

    async def get_project_features(self, project_id: str) -> tuple[bool, dict[str, Any]]:
        """
        Get features from a project's features JSONB field.

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Get features via repository
            features = await self.repository.get_project_features(project_id)

            if features is None:
                return False, {"error": "Project not found"}

            # Extract feature labels for dropdown options
            feature_options = []
            for feature in features:
                if isinstance(feature, dict) and "data" in feature and "label" in feature["data"]:
                    feature_options.append({
                        "id": feature.get("id", ""),
                        "label": feature["data"]["label"],
                        "type": feature["data"].get("type", ""),
                        "feature_type": feature.get("type", "page"),
                    })

            return True, {"features": feature_options, "count": len(feature_options)}

        except Exception as e:
            # Check if it's a "no rows found" error from PostgREST
            error_message = str(e)
            if "The result contains 0 rows" in error_message or "PGRST116" in error_message:
                return False, {"error": "Project not found"}

            logger.error(f"Error getting project features: {e}")
            return False, {"error": f"Error getting project features: {str(e)}"}

    async def update_project(
        self, project_id: str, update_fields: dict[str, Any]
    ) -> tuple[bool, dict[str, Any]]:
        """
        Update a project with specified fields.

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Build update data with allowed fields
            allowed_fields = [
                "title",
                "description",
                "github_repo",
                "docs",
                "features",
                "data",
                "technical_sources",
                "business_sources",
                "pinned",
            ]

            update_data = {}
            for field in allowed_fields:
                if field in update_fields:
                    update_data[field] = update_fields[field]

            # Handle pinning logic - only one project can be pinned at a time
            if update_fields.get("pinned") is True:
                # Unpin any other pinned projects first
                unpinned_count = await self.repository.unpin_all_projects_except(project_id)
                logger.debug(f"Unpinned {unpinned_count} other projects before pinning {project_id}")

            # Update the target project via repository
            project = await self.repository.update_project(project_id, update_data)

            if project:
                return True, {"project": project, "message": "Project updated successfully"}
            else:
                return False, {"error": f"Project with ID {project_id} not found"}

        except Exception as e:
            logger.error(f"Error updating project: {e}")
            return False, {"error": f"Error updating project: {str(e)}"}
