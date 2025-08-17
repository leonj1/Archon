"""
Project Service Module for Archon

This module provides core business logic for project operations that can be
shared between MCP tools and FastAPI endpoints. It follows the pattern of
separating business logic from transport-specific code.
"""

# Removed direct logging import - using unified config
from datetime import datetime
from typing import Any

from ...config.logfire_config import get_logger
from ..client_manager import get_connection_manager

logger = get_logger(__name__)


class ProjectService:
    """Service class for project operations"""

    def __init__(self, connection_manager=None):
        """Initialize with optional connection manager"""
        self.connection_manager = connection_manager or get_connection_manager()

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
                "docs": [],  # Will add PRD document after creation
                "features": [],
                "data": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            if github_repo and isinstance(github_repo, str) and len(github_repo.strip()) > 0:
                project_data["github_repo"] = github_repo.strip()

            # Insert project
            async with self.connection_manager.get_primary() as db:
                response = await db.insert(
                    table="projects",
                    data=project_data,
                    returning=["*"]
                )

                if not response.success or not response.data:
                    logger.error(f"Database error creating project: {response.error}")
                    return False, {"error": "Failed to create project - database error"}

                project = response.data[0]
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

    async def list_projects(self) -> tuple[bool, dict[str, Any]]:
        """
        List all projects.

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            async with self.connection_manager.get_reader() as db:
                response = await db.select(
                    table="projects",
                    columns=["*"],
                    order_by="created_at DESC"
                )

                if not response.success:
                    logger.error(f"Database error listing projects: {response.error}")
                    return False, {"error": f"Database error: {response.error}"}

                projects = []
                for project in response.data:
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
            async with self.connection_manager.get_reader() as db:
                response = await db.select(
                    table="projects",
                    columns=["*"],
                    filters={"id": project_id}
                )

                if not response.success:
                    logger.error(f"Database error getting project: {response.error}")
                    return False, {"error": f"Database error: {response.error}"}

                if response.data:
                    project = response.data[0]

                    # Get linked sources
                    technical_sources = []
                    business_sources = []

                    try:
                        # Get source IDs from project_sources table
                        sources_response = await db.select(
                            table="project_sources",
                            columns=["source_id", "notes"],
                            filters={"project_id": project["id"]}
                        )

                        if sources_response.success:
                            # Collect source IDs by type
                            technical_source_ids = []
                            business_source_ids = []

                            for source_link in sources_response.data:
                                if source_link.get("notes") == "technical":
                                    technical_source_ids.append(source_link["source_id"])
                                elif source_link.get("notes") == "business":
                                    business_source_ids.append(source_link["source_id"])

                            # Fetch full source objects
                            if technical_source_ids:
                                tech_sources_response = await db.select(
                                    table="sources",
                                    columns=["*"],
                                    filters={"source_id": {"in": technical_source_ids}}
                                )
                                if tech_sources_response.success:
                                    technical_sources = tech_sources_response.data

                            if business_source_ids:
                                biz_sources_response = await db.select(
                                    table="sources",
                                    columns=["*"],
                                    filters={"source_id": {"in": business_source_ids}}
                                )
                                if biz_sources_response.success:
                                    business_sources = biz_sources_response.data

                    except Exception as e:
                        logger.warning(
                            f"Failed to retrieve linked sources for project {project['id']}: {e}"
                        )

                    # Add sources to project data
                    project["technical_sources"] = technical_sources
                    project["business_sources"] = business_sources

                    return True, {"project": project}
                else:
                    return False, {"error": f"Project with ID {project_id} not found"}

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
            async with self.connection_manager.get_primary() as db:
                # First, check if project exists
                check_response = await db.select(
                    table="projects",
                    columns=["id"],
                    filters={"id": project_id}
                )
                
                if not check_response.success or not check_response.data:
                    return False, {"error": f"Project with ID {project_id} not found"}

                # Get task count for reporting
                tasks_response = await db.select(
                    table="tasks",
                    columns=["id"],
                    filters={"project_id": project_id}
                )
                tasks_count = len(tasks_response.data) if tasks_response.success and tasks_response.data else 0

                # Delete the project (tasks will be deleted by cascade)
                response = await db.delete(
                    table="projects",
                    filters={"id": project_id}
                )

                if not response.success:
                    logger.error(f"Database error deleting project: {response.error}")
                    return False, {"error": f"Database error: {response.error}"}

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
            async with self.connection_manager.get_reader() as db:
                response = await db.select(
                    table="projects",
                    columns=["features"],
                    filters={"id": project_id},
                    limit=1
                )

                if not response.success or not response.data:
                    return False, {"error": "Project not found"}

                features = response.data[0].get("features", [])

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
            # Build update data
            update_data = {"updated_at": datetime.now().isoformat()}

            # Add allowed fields
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

            for field in allowed_fields:
                if field in update_fields:
                    update_data[field] = update_fields[field]

            async with self.connection_manager.get_primary() as db:
                # Handle pinning logic - only one project can be pinned at a time
                if update_fields.get("pinned") is True:
                    # Unpin any other pinned projects
                    await db.update(
                        table="projects",
                        data={"pinned": False},
                        filters={"pinned": True, "id": {"neq": project_id}}
                    )

                # Update the project
                response = await db.update(
                    table="projects",
                    data=update_data,
                    filters={"id": project_id},
                    returning=["*"]
                )

                if response.success and response.data:
                    project = response.data[0]
                    return True, {"project": project, "message": "Project updated successfully"}
                else:
                    error_msg = response.error or f"Project with ID {project_id} not found"
                    return False, {"error": error_msg}

        except Exception as e:
            logger.error(f"Error updating project: {e}")
            return False, {"error": f"Error updating project: {str(e)}"}
