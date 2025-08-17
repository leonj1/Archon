"""
Versioning Service Module for Archon

This module provides core business logic for document versioning operations
that can be shared between MCP tools and FastAPI endpoints.
"""

# Removed direct logging import - using unified config
from datetime import datetime
from typing import Any

from ...config.logfire_config import get_logger
from ..client_manager import get_connection_manager

logger = get_logger(__name__)


class VersioningService:
    """Service class for document versioning operations"""

    def __init__(self, connection_manager=None):
        """Initialize with optional connection manager"""
        self.connection_manager = connection_manager or get_connection_manager()

    async def create_version(
        self,
        project_id: str,
        field_name: str,
        content: dict[str, Any],
        change_summary: str = None,
        change_type: str = "update",
        document_id: str = None,
        created_by: str = "system",
    ) -> tuple[bool, dict[str, Any]]:
        """
        Create a version snapshot for a project JSONB field.

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Get current highest version number for this project/field
            async with self.connection_manager.get_reader() as db:
                existing_versions_response = await db.select(
                    table="document_versions",
                    columns=["version_number"],
                    filters={
                        "project_id": project_id,
                        "field_name": field_name
                    },
                    order_by="version_number DESC",
                    limit=1
                )

            next_version = 1
            if existing_versions_response.success and existing_versions_response.data:
                next_version = existing_versions_response.data[0]["version_number"] + 1

            # Create new version record
            version_data = {
                "project_id": project_id,
                "field_name": field_name,
                "version_number": next_version,
                "content": content,
                "change_summary": change_summary or f"{change_type.capitalize()} {field_name}",
                "change_type": change_type,
                "document_id": document_id,
                "created_by": created_by,
                "created_at": datetime.now().isoformat(),
            }

            async with self.connection_manager.get_primary() as db:
                result = await db.insert(
                    table="document_versions",
                    data=version_data,
                    returning=["*"]
                )

            if result.success and result.data:
                return True, {
                    "version": result.data[0],
                    "project_id": project_id,
                    "field_name": field_name,
                    "version_number": next_version,
                }
            else:
                logger.error(f"Database error creating version: {result.error}")
                return False, {"error": "Failed to create version snapshot"}

        except Exception as e:
            logger.error(f"Error creating version: {e}")
            return False, {"error": f"Error creating version: {str(e)}"}

    async def list_versions(self, project_id: str, field_name: str = None) -> tuple[bool, dict[str, Any]]:
        """
        Get version history for project JSONB fields.

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Build filters
            filters = {"project_id": project_id}
            if field_name:
                filters["field_name"] = field_name

            async with self.connection_manager.get_reader() as db:
                result = await db.select(
                    table="document_versions",
                    columns=["*"],
                    filters=filters,
                    order_by="version_number DESC"
                )

            if result.success:
                return True, {
                    "project_id": project_id,
                    "field_name": field_name,
                    "versions": result.data,
                    "total_count": len(result.data),
                }
            else:
                logger.error(f"Database error listing versions: {result.error}")
                return False, {"error": "Failed to retrieve version history"}

        except Exception as e:
            logger.error(f"Error getting version history: {e}")
            return False, {"error": f"Error getting version history: {str(e)}"}

    async def get_version_content(
        self, project_id: str, field_name: str, version_number: int
    ) -> tuple[bool, dict[str, Any]]:
        """
        Get the content of a specific version.

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            async with self.connection_manager.get_reader() as db:
                result = await db.select(
                    table="document_versions",
                    columns=["*"],
                    filters={
                        "project_id": project_id,
                        "field_name": field_name,
                        "version_number": version_number
                    }
                )

            if result.success and result.data:
                version = result.data[0]
                return True, {
                    "version": version,
                    "content": version["content"],
                    "field_name": field_name,
                    "version_number": version_number,
                }
            else:
                return False, {"error": f"Version {version_number} not found for {field_name}"}

        except Exception as e:
            logger.error(f"Error getting version content: {e}")
            return False, {"error": f"Error getting version content: {str(e)}"}

    async def restore_version(
        self, project_id: str, field_name: str, version_number: int, restored_by: str = "system"
    ) -> tuple[bool, dict[str, Any]]:
        """
        Restore a project JSONB field to a specific version.

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Get the version to restore
            async with self.connection_manager.get_reader() as db:
                version_response = await db.select(
                    table="document_versions",
                    columns=["*"],
                    filters={
                        "project_id": project_id,
                        "field_name": field_name,
                        "version_number": version_number
                    }
                )

            if not version_response.success or not version_response.data:
                return False, {
                    "error": f"Version {version_number} not found for {field_name} in project {project_id}"
                }

            version_to_restore = version_response.data[0]
            content_to_restore = version_to_restore["content"]

            # Get current content to create backup
            async with self.connection_manager.get_reader() as db:
                current_project_response = await db.select(
                    table="projects",
                    columns=[field_name],
                    filters={"id": project_id}
                )

            if current_project_response.success and current_project_response.data:
                current_content = current_project_response.data[0].get(field_name, {})

                # Create backup version before restore
                backup_result = await self.create_version(
                    project_id=project_id,
                    field_name=field_name,
                    content=current_content,
                    change_summary=f"Backup before restoring to version {version_number}",
                    change_type="backup",
                    created_by=restored_by,
                )

                if not backup_result[0]:
                    logger.warning(f"Failed to create backup version: {backup_result[1]}")

            # Restore the content to project
            update_data = {field_name: content_to_restore, "updated_at": datetime.now().isoformat()}

            async with self.connection_manager.get_primary() as db:
                restore_response = await db.update(
                    table="projects",
                    data=update_data,
                    filters={"id": project_id},
                    returning=["*"]
                )

            if restore_response.success and restore_response.data:
                # Create restore version record
                restore_version_result = await self.create_version(
                    project_id=project_id,
                    field_name=field_name,
                    content=content_to_restore,
                    change_summary=f"Restored to version {version_number}",
                    change_type="restore",
                    created_by=restored_by,
                )

                return True, {
                    "project_id": project_id,
                    "field_name": field_name,
                    "restored_version": version_number,
                    "restored_by": restored_by,
                }
            else:
                logger.error(f"Database error restoring version: {restore_response.error}")
                return False, {"error": "Failed to restore version"}

        except Exception as e:
            logger.error(f"Error restoring version: {e}")
            return False, {"error": f"Error restoring version: {str(e)}"}