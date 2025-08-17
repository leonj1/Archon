"""
Source Linking Service Module for Archon

This module provides centralized logic for managing project-source relationships,
handling both technical and business source associations.
"""

# Removed direct logging import - using unified config
from typing import Any

from ...config.logfire_config import get_logger
from ..client_manager import get_connection_manager

logger = get_logger(__name__)


class SourceLinkingService:
    """Service class for managing project-source relationships"""

    def __init__(self, connection_manager=None):
        """Initialize with optional connection manager"""
        self.connection_manager = connection_manager or get_connection_manager()

    async def get_project_sources(self, project_id: str) -> tuple[bool, dict[str, list[str]]]:
        """
        Get all linked sources for a project, separated by type.

        Returns:
            Tuple of (success, {"technical_sources": [...], "business_sources": [...]})
        """
        try:
            async with self.connection_manager.get_reader() as db:
                response = await db.select(
                    table="project_sources",
                    columns=["source_id", "notes"],
                    filters={"project_id": project_id}
                )

                if not response.success:
                    logger.error(f"Database error getting project sources: {response.error}")
                    return False, {
                        "error": f"Failed to retrieve linked sources: {response.error}",
                        "technical_sources": [],
                        "business_sources": [],
                    }

                technical_sources = []
                business_sources = []

                for source_link in response.data:
                    if source_link.get("notes") == "technical":
                        technical_sources.append(source_link["source_id"])
                    elif source_link.get("notes") == "business":
                        business_sources.append(source_link["source_id"])

                return True, {
                    "technical_sources": technical_sources,
                    "business_sources": business_sources,
                }
        except Exception as e:
            logger.error(f"Error getting project sources: {e}")
            return False, {
                "error": f"Failed to retrieve linked sources: {str(e)}",
                "technical_sources": [],
                "business_sources": [],
            }

    async def update_project_sources(
        self,
        project_id: str,
        technical_sources: list[str] | None = None,
        business_sources: list[str] | None = None,
    ) -> tuple[bool, dict[str, Any]]:
        """
        Update project sources, replacing existing ones if provided.

        Returns:
            Tuple of (success, result_dict with counts)
        """
        result = {
            "technical_success": 0,
            "technical_failed": 0,
            "business_success": 0,
            "business_failed": 0,
        }

        try:
            async with self.connection_manager.get_primary() as db:
                # Update technical sources if provided
                if technical_sources is not None:
                    # Remove existing technical sources
                    await db.delete(
                        table="project_sources",
                        filters={"project_id": project_id, "notes": "technical"}
                    )

                    # Add new technical sources
                    for source_id in technical_sources:
                        try:
                            response = await db.insert(
                                table="project_sources",
                                data={
                                    "project_id": project_id,
                                    "source_id": source_id,
                                    "notes": "technical",
                                }
                            )
                            if response.success:
                                result["technical_success"] += 1
                            else:
                                result["technical_failed"] += 1
                                logger.warning(f"Failed to link technical source {source_id}: {response.error}")
                        except Exception as e:
                            result["technical_failed"] += 1
                            logger.warning(f"Failed to link technical source {source_id}: {e}")

                # Update business sources if provided
                if business_sources is not None:
                    # Remove existing business sources
                    await db.delete(
                        table="project_sources",
                        filters={"project_id": project_id, "notes": "business"}
                    )

                    # Add new business sources
                    for source_id in business_sources:
                        try:
                            response = await db.insert(
                                table="project_sources",
                                data={
                                    "project_id": project_id,
                                    "source_id": source_id,
                                    "notes": "business",
                                }
                            )
                            if response.success:
                                result["business_success"] += 1
                            else:
                                result["business_failed"] += 1
                                logger.warning(f"Failed to link business source {source_id}: {response.error}")
                        except Exception as e:
                            result["business_failed"] += 1
                            logger.warning(f"Failed to link business source {source_id}: {e}")

                # Overall success if no critical failures
                total_failed = result["technical_failed"] + result["business_failed"]

                return True, result

        except Exception as e:
            logger.error(f"Error updating project sources: {e}")
            return False, {"error": str(e), **result}

    async def format_project_with_sources(self, project: dict[str, Any]) -> dict[str, Any]:
        """
        Format a project dict with its linked sources included.
        Also handles datetime conversion for Socket.IO compatibility.

        Returns:
            Formatted project dict with technical_sources and business_sources
        """
        # Get linked sources
        success, sources = await self.get_project_sources(project["id"])
        if not success:
            logger.warning(f"Failed to get sources for project {project['id']}")
            sources = {"technical_sources": [], "business_sources": []}

        # Ensure datetime objects are converted to strings
        created_at = project.get("created_at", "")
        updated_at = project.get("updated_at", "")
        if hasattr(created_at, "isoformat"):
            created_at = created_at.isoformat()
        if hasattr(updated_at, "isoformat"):
            updated_at = updated_at.isoformat()

        return {
            "id": project["id"],
            "title": project["title"],
            "description": project.get("description", ""),
            "github_repo": project.get("github_repo"),
            "created_at": created_at,
            "updated_at": updated_at,
            "docs": project.get("docs", []),
            "features": project.get("features", []),
            "data": project.get("data", []),
            "technical_sources": sources["technical_sources"],
            "business_sources": sources["business_sources"],
            "pinned": project.get("pinned", False),
        }

    async def format_projects_with_sources(self, projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Format a list of projects with their linked sources.

        Returns:
            List of formatted project dicts
        """
        formatted_projects = []
        for project in projects:
            formatted_project = await self.format_project_with_sources(project)
            formatted_projects.append(formatted_project)
        return formatted_projects