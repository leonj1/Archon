"""
Simple project management tools for Archon MCP Server.

Provides separate, focused tools for each project operation.
No complex PRP examples - just straightforward project management.
"""

import asyncio
import json
import logging
from typing import Any, Optional
from urllib.parse import urljoin

import httpx
from mcp.server.fastmcp import Context, FastMCP

from src.server.config.service_discovery import get_api_url

logger = logging.getLogger(__name__)


def register_project_tools(mcp: FastMCP):
    """Register individual project management tools with the MCP server."""

    @mcp.tool()
    async def create_project(
        ctx: Context,
        title: str,
        description: str = "",
        github_repo: Optional[str] = None,
    ) -> str:
        """
        Create a new project.

        Args:
            title: Project title (required)
            description: Project description (optional)
            github_repo: GitHub repository URL (optional)

        Returns:
            JSON with project details including project_id

        Example:
            create_project(title="My New Project", description="A test project")
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    urljoin(api_url, "/api/projects"),
                    json={"title": title, "description": description, "github_repo": github_repo},
                )

                if response.status_code == 200:
                    result = response.json()
                    
                    # Handle async project creation
                    if "progress_id" in result:
                        # Poll for completion (max 30 seconds)
                        for attempt in range(30):
                            await asyncio.sleep(1)
                            
                            # List projects to find the newly created one
                            list_response = await client.get(urljoin(api_url, "/api/projects"))
                            if list_response.status_code == 200:
                                projects = list_response.json()
                                # Find project with matching title created recently
                                for proj in projects:
                                    if proj.get("title") == title:
                                        return json.dumps({
                                            "success": True,
                                            "project": proj,
                                            "project_id": proj["id"],
                                            "message": f"Project created successfully with ID: {proj['id']}"
                                        })
                        
                        # If we couldn't find it after polling
                        return json.dumps({
                            "success": True,
                            "progress_id": result["progress_id"],
                            "message": "Project creation started. Use list_projects to find it once complete."
                        })
                    else:
                        # Direct response (shouldn't happen with current API)
                        return json.dumps({"success": True, "project": result})
                else:
                    error_detail = response.json().get("detail", {}).get("error", "Unknown error")
                    return json.dumps({"success": False, "error": error_detail})

        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool()
    async def list_projects(ctx: Context) -> str:
        """
        List all projects.

        Returns:
            JSON array of all projects with their basic information

        Example:
            list_projects()
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(urljoin(api_url, "/api/projects"))

                if response.status_code == 200:
                    projects = response.json()
                    return json.dumps({
                        "success": True,
                        "projects": projects,
                        "count": len(projects)
                    })
                else:
                    return json.dumps({
                        "success": False,
                        "error": "Failed to list projects"
                    })

        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool()
    async def get_project(ctx: Context, project_id: str) -> str:
        """
        Get detailed information about a specific project.

        Args:
            project_id: UUID of the project

        Returns:
            JSON with complete project details

        Example:
            get_project(project_id="550e8400-e29b-41d4-a716-446655440000")
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(urljoin(api_url, f"/api/projects/{project_id}"))

                if response.status_code == 200:
                    project = response.json()
                    return json.dumps({"success": True, "project": project})
                elif response.status_code == 404:
                    return json.dumps({
                        "success": False,
                        "error": f"Project {project_id} not found"
                    })
                else:
                    return json.dumps({
                        "success": False,
                        "error": "Failed to get project"
                    })

        except Exception as e:
            logger.error(f"Error getting project: {e}")
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool()
    async def delete_project(ctx: Context, project_id: str) -> str:
        """
        Delete a project.

        Args:
            project_id: UUID of the project to delete

        Returns:
            JSON confirmation of deletion

        Example:
            delete_project(project_id="550e8400-e29b-41d4-a716-446655440000")
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.delete(
                    urljoin(api_url, f"/api/projects/{project_id}")
                )

                if response.status_code == 200:
                    return json.dumps({
                        "success": True,
                        "message": f"Project {project_id} deleted successfully"
                    })
                elif response.status_code == 404:
                    return json.dumps({
                        "success": False,
                        "error": f"Project {project_id} not found"
                    })
                else:
                    return json.dumps({
                        "success": False,
                        "error": "Failed to delete project"
                    })

        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool()
    async def update_project(
        ctx: Context,
        project_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        github_repo: Optional[str] = None,
    ) -> str:
        """
        Update a project's basic information.

        Args:
            project_id: UUID of the project to update
            title: New title (optional)
            description: New description (optional)
            github_repo: New GitHub repository URL (optional)

        Returns:
            JSON with updated project details

        Example:
            update_project(project_id="550e8400-e29b-41d4-a716-446655440000",
                         title="Updated Project Title")
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            # Build update payload with only provided fields
            update_data = {}
            if title is not None:
                update_data["title"] = title
            if description is not None:
                update_data["description"] = description
            if github_repo is not None:
                update_data["github_repo"] = github_repo

            if not update_data:
                return json.dumps({
                    "success": False,
                    "error": "No fields to update"
                })

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.put(
                    urljoin(api_url, f"/api/projects/{project_id}"),
                    json=update_data
                )

                if response.status_code == 200:
                    project = response.json()
                    return json.dumps({
                        "success": True,
                        "project": project,
                        "message": "Project updated successfully"
                    })
                elif response.status_code == 404:
                    return json.dumps({
                        "success": False,
                        "error": f"Project {project_id} not found"
                    })
                else:
                    return json.dumps({
                        "success": False,
                        "error": "Failed to update project"
                    })

        except Exception as e:
            logger.error(f"Error updating project: {e}")
            return json.dumps({"success": False, "error": str(e)})