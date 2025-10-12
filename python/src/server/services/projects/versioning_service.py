"""
Versioning Service Module for Archon

This module provides core business logic for document versioning operations
that can be shared between MCP tools and FastAPI endpoints.
"""

from datetime import datetime
from typing import Any, Optional

from src.server.utils import get_supabase_client
from ...repositories.database_repository import DatabaseRepository
from ...repositories.repository_factory import get_repository

from ...config.logfire_config import get_logger

logger = get_logger(__name__)

class VersioningService:
    """Service class for document versioning operations"""

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
            self.repository = get_repository()

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
            # Note: Repository doesn't have a direct method for this, need to fetch and filter
            all_versions = await self.repository.list_document_versions(project_id=project_id)

            # Filter by field_name and get max version_number
            field_versions = [v for v in all_versions if v.get("field_name") == field_name]
            next_version = 1
            if field_versions:
                max_version = max(v.get("version_number", 0) for v in field_versions)
                next_version = max_version + 1

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

            version = await self.repository.create_document_version(version_data)

            if version:
                return True, {
                    "version": version,
                    "project_id": project_id,
                    "field_name": field_name,
                    "version_number": next_version,
                }
            else:
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
            # Get all versions for the project
            versions = await self.repository.list_document_versions(project_id=project_id)

            # Filter by field_name if specified
            if field_name:
                versions = [v for v in versions if v.get("field_name") == field_name]

            # Sort by version_number descending (repository returns by created_at desc)
            versions.sort(key=lambda v: v.get("version_number", 0), reverse=True)

            return True, {
                "project_id": project_id,
                "field_name": field_name,
                "versions": versions,
                "total_count": len(versions),
            }

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
            # Get all versions for the project and filter
            all_versions = await self.repository.list_document_versions(project_id=project_id)

            # Find the specific version by field_name and version_number
            matching_versions = [
                v for v in all_versions
                if v.get("field_name") == field_name and v.get("version_number") == version_number
            ]

            if matching_versions:
                version = matching_versions[0]
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
            all_versions = await self.repository.list_document_versions(project_id=project_id)
            matching_versions = [
                v for v in all_versions
                if v.get("field_name") == field_name and v.get("version_number") == version_number
            ]

            if not matching_versions:
                return False, {
                    "error": f"Version {version_number} not found for {field_name} in project {project_id}"
                }

            version_to_restore = matching_versions[0]
            content_to_restore = version_to_restore["content"]

            # Get current content to create backup
            current_project = await self.repository.get_project_by_id(project_id)
            if current_project:
                current_content = current_project.get(field_name, {})

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
            update_data = {field_name: content_to_restore}

            updated_project = await self.repository.update_project(
                project_id=project_id,
                update_data=update_data
            )

            if updated_project:
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
                return False, {"error": "Failed to restore version"}

        except Exception as e:
            logger.error(f"Error restoring version: {e}")
            return False, {"error": f"Error restoring version: {str(e)}"}
