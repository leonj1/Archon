"""
Project Module for Archon MCP Server - PRP-Driven Development Platform

🛡️ AUTOMATIC VERSION CONTROL & DATA PROTECTION:
This module provides comprehensive project management with BUILT-IN VERSION CONTROL
that prevents documentation erasure and enables complete audit trails.

🔄 Version Control Features:
- AUTOMATIC SNAPSHOTS: Every document update creates immutable version backup
- COMPLETE ROLLBACK: Any version can be restored without data loss
- AUDIT COMPLIANCE: Full change history with timestamps and creator attribution
- DISASTER RECOVERY: All operations preserve historical data permanently

📋 PRP (Product Requirement Prompt) Integration:
- Structured JSON format for proper PRPViewer compatibility
- Complete PRP templates with all required sections
- Validation gates and implementation blueprints
- Task generation from PRP implementation plans

🏗️ Consolidated MCP Tools:
- manage_project: Project lifecycle with automatic version control
- manage_task: PRP-driven task management with status workflows
- manage_document: Document management with version snapshots
- manage_versions: Complete version history and rollback capabilities
- get_project_features: Feature query operations

⚠️ CRITICAL SAFETY: All operations preserve data through automatic versioning.
No content can be permanently lost - use manage_versions for recovery.
"""

import json
import logging
from typing import Any
from urllib.parse import urljoin

# Import HTTP client and service discovery
import httpx

from mcp.server.fastmcp import Context, FastMCP

# Import service discovery for HTTP calls
from src.server.config.service_discovery import get_api_url

logger = logging.getLogger(__name__)


def register_project_tools(mcp: FastMCP):
    """Register consolidated project and task management tools with the MCP server."""

    @mcp.tool()
    async def manage_project(
        ctx: Context,
        action: str,
        project_id: str = None,
        title: str = None,
        prd: dict[str, Any] = None,
        github_repo: str = None,
    ) -> str:
        """
        Manage Archon projects with automatic version control.

        Projects use PRP (Product Requirement Prompt) methodology for task-driven development.
        All data is auto-versioned - deletions preserve history for recovery via manage_versions.

        Args:
            action: "create" | "list" | "get" | "delete"
            project_id: Project UUID (required for get/delete)
            title: Project title (required for create)
            prd: Product requirements dict with vision, features, metrics (optional)
            github_repo: GitHub URL (optional)

        Returns:
            JSON string with structure:
            - success: bool - Operation success status
            - project: dict - Project object (for create/get actions)
            - projects: list[dict] - Array of projects (for list action)
            - message: str - "Project deleted successfully" (for delete action)
            - error: str - Error description if success=false

        Examples:
            Create: manage_project(action="create", title="OAuth System", prd={...})
            List: manage_project(action="list")
            Get: manage_project(action="get", project_id="uuid")
            Delete: manage_project(action="delete", project_id="uuid")
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            if action == "create":
                if not title:
                    return json.dumps({
                        "success": False,
                        "error": "Title is required for create action",
                    })

                # Call Server API to create project
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        urljoin(api_url, "/api/projects"),
                        json={"title": title, "prd": prd, "github_repo": github_repo},
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({"success": True, "project": result})
                    else:
                        error_detail = (
                            response.json().get("detail", {}).get("error", "Unknown error")
                        )
                        return json.dumps({"success": False, "error": error_detail})

            elif action == "list":
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(urljoin(api_url, "/api/projects"))

                    if response.status_code == 200:
                        projects = response.json()
                        return json.dumps({"success": True, "projects": projects})
                    else:
                        return json.dumps({"success": False, "error": "Failed to list projects"})

            elif action == "get":
                if not project_id:
                    return json.dumps({
                        "success": False,
                        "error": "project_id is required for get action",
                    })

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(urljoin(api_url, f"/api/projects/{project_id}"))

                    if response.status_code == 200:
                        project = response.json()
                        return json.dumps({"success": True, "project": project})
                    elif response.status_code == 404:
                        return json.dumps({
                            "success": False,
                            "error": f"Project {project_id} not found",
                        })
                    else:
                        return json.dumps({"success": False, "error": "Failed to get project"})

            elif action == "delete":
                if not project_id:
                    return json.dumps({
                        "success": False,
                        "error": "project_id is required for delete action",
                    })

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.delete(urljoin(api_url, f"/api/projects/{project_id}"))

                    if response.status_code == 200:
                        return json.dumps({
                            "success": True,
                            "message": "Project deleted successfully",
                        })
                    else:
                        return json.dumps({"success": False, "error": "Failed to delete project"})

            else:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid action '{action}'. Must be one of: create, list, get, delete",
                })

        except Exception as e:
            logger.error(f"Error in manage_project: {e}")
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool()
    async def manage_task(
        ctx: Context,
        action: str,
        task_id: str = None,
        project_id: str = None,
        filter_by: str = None,
        filter_value: str = None,
        title: str = None,
        description: str = "",
        assignee: str = "User",
        task_order: int = 0,
        feature: str = None,
        sources: list[dict[str, Any]] = None,
        code_examples: list[dict[str, Any]] = None,
        update_fields: dict[str, Any] = None,
        include_closed: bool = False,
        page: int = 1,
        per_page: int = 50,
    ) -> str:
        """
        Manage tasks within PRP-driven projects.

        Status flow: todo → doing → review → done
        Only one task in 'doing' per agent. Tasks auto-versioned for recovery.

        Args:
            action: "create" | "list" | "get" | "update" | "delete" | "archive"
            task_id: Task UUID (required for get/update/delete/archive)
            project_id: Project UUID (required for create, optional for list)
            filter_by: "status" | "project" | "assignee" (for list)
            filter_value: Filter value (e.g., "todo", "doing", "review", "done")
            title: Task title (required for create)
            description: Task description with acceptance criteria
            assignee: "User" | "Archon" | "AI IDE Agent" | "prp-executor" | "prp-validator"
            task_order: Priority (0-100, higher = more priority)
            feature: Feature label for grouping
            sources: List of source metadata dicts [{"url": str, "type": str, "relevance": str}]
            code_examples: List of code example dicts [{"file": str, "function": str, "purpose": str}]
            update_fields: Dict of fields to update (for update action)
            include_closed: Include done tasks in list (default: False)
            page/per_page: Pagination controls

        Returns:
            JSON string with structure:
            - success: bool - Operation success status
            - task: dict - Task object (for create/get/update/delete/archive actions)
            - tasks: list[dict] - Array of tasks (for list action)
            - pagination: dict|null - Page info if available (for list action)
            - total_count: int - Total tasks count (for list action)
            - message: str - Operation message (for create/update/delete/archive actions)
            - error: str - Error description if success=false

        Examples:
            Create: manage_task(action="create", project_id="uuid", title="Implement OAuth")
            Update status: manage_task(action="update", task_id="uuid", update_fields={"status": "doing"})
            List todos: manage_task(action="list", filter_by="status", filter_value="todo")
            Get details: manage_task(action="get", task_id="uuid")
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            if action == "create":
                if not project_id:
                    return json.dumps({
                        "success": False,
                        "error": "project_id is required for create action",
                    })
                if not title:
                    return json.dumps({
                        "success": False,
                        "error": "title is required for create action",
                    })

                # Call Server API to create task
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        urljoin(api_url, "/api/tasks"),
                        json={
                            "project_id": project_id,
                            "title": title,
                            "description": description,
                            "assignee": assignee,
                            "task_order": task_order,
                            "feature": feature,
                            "sources": sources,
                            "code_examples": code_examples,
                        },
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "task": result.get("task"),
                            "message": result.get("message"),
                        })
                    else:
                        error_detail = response.text
                        return json.dumps({"success": False, "error": error_detail})

            elif action == "list":
                # Build URL with query parameters based on filter type
                params = {
                    "page": page,
                    "per_page": per_page,
                    "exclude_large_fields": True,  # Always exclude large fields in MCP responses
                }

                # Use different endpoints based on filter type for proper parameter handling
                if filter_by == "project" and filter_value:
                    # Use project-specific endpoint for project filtering
                    url = urljoin(api_url, f"/api/projects/{filter_value}/tasks")
                    params["include_archived"] = False  # For backward compatibility

                    # Only add include_closed logic for project filtering
                    if not include_closed:
                        # This endpoint handles done task filtering differently
                        pass  # Let the endpoint handle it
                elif filter_by == "status" and filter_value:
                    # Use generic tasks endpoint for status filtering
                    url = urljoin(api_url, "/api/tasks")
                    params["status"] = filter_value
                    params["include_closed"] = include_closed
                    # Add project_id if provided
                    if project_id:
                        params["project_id"] = project_id
                else:
                    # Default to generic tasks endpoint
                    url = urljoin(api_url, "/api/tasks")
                    params["include_closed"] = include_closed

                # Make the API call
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()

                    result = response.json()

                    # Handle both direct array and paginated response formats
                    if isinstance(result, list):
                        # Direct array response
                        tasks = result
                        pagination_info = None
                    else:
                        # Paginated response or object with tasks property
                        if "tasks" in result:
                            tasks = result.get("tasks", [])
                            pagination_info = result.get("pagination", {})
                        else:
                            # Direct array in object form
                            tasks = result if isinstance(result, list) else []
                            pagination_info = None

                    return json.dumps({
                        "success": True,
                        "tasks": tasks,
                        "pagination": pagination_info,
                        "total_count": len(tasks)
                        if pagination_info is None
                        else pagination_info.get("total", len(tasks)),
                    })

            elif action == "get":
                if not task_id:
                    return json.dumps({
                        "success": False,
                        "error": "task_id is required for get action",
                    })

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(urljoin(api_url, f"/api/tasks/{task_id}"))

                    if response.status_code == 200:
                        task = response.json()
                        return json.dumps({"success": True, "task": task})
                    elif response.status_code == 404:
                        return json.dumps({"success": False, "error": f"Task {task_id} not found"})
                    else:
                        return json.dumps({"success": False, "error": "Failed to get task"})

            elif action == "update":
                if not task_id:
                    return json.dumps({
                        "success": False,
                        "error": "task_id is required for update action",
                    })
                if not update_fields:
                    return json.dumps({
                        "success": False,
                        "error": "update_fields is required for update action",
                    })

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.put(
                        urljoin(api_url, f"/api/tasks/{task_id}"), json=update_fields
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "task": result.get("task"),
                            "message": result.get("message"),
                        })
                    else:
                        error_detail = response.text
                        return json.dumps({"success": False, "error": error_detail})

            elif action in ["delete", "archive"]:
                if not task_id:
                    return json.dumps({
                        "success": False,
                        "error": "task_id is required for delete/archive action",
                    })

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.delete(urljoin(api_url, f"/api/tasks/{task_id}"))

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "message": result.get("message"),
                            "subtasks_archived": result.get("subtasks_archived", 0),
                        })
                    else:
                        return json.dumps({"success": False, "error": "Failed to archive task"})

            else:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid action '{action}'. Must be one of: create, list, get, update, delete, archive",
                })

        except Exception as e:
            logger.error(f"Error in manage_task: {e}")
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool()
    async def manage_document(
        ctx: Context,
        action: str,
        project_id: str,
        doc_id: str = None,
        document_type: str = None,
        title: str = None,
        content: dict[str, Any] = None,
        metadata: dict[str, Any] = None,
    ) -> str:
        """
        Manage project documents with automatic version control.

        Every update creates immutable version backup. Use manage_versions to restore.
        PRP documents require structured JSON format, not markdown.

        Args:
            action: "add" | "list" | "get" | "update" | "delete"
            project_id: Project UUID (always required)
            doc_id: Document UUID (required for get/update/delete)
            document_type: Document type (required for add, "prp" for PRPs)
            title: Document title (required for add)
            content: Structured JSON content (for add/update)
            metadata: Optional metadata dict with tags, author fields

        Returns:
            JSON string with structure:
            - success: bool - Operation success status
            - document: dict - Document object (for add/get/update actions)
            - documents: list[dict] - Array of documents (for list action, via spread operator)
            - message: str - Operation message (for add/update/delete actions)
            - error: str - Error description if success=false

        Examples:
            Add PRP: manage_document(action="add", project_id="uuid", document_type="prp", title="OAuth", content={...})
            List: manage_document(action="list", project_id="uuid")
            Get: manage_document(action="get", project_id="uuid", doc_id="doc-uuid")
            Update: manage_document(action="update", project_id="uuid", doc_id="doc-uuid", content={...})
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            if action == "add":
                if not document_type:
                    return json.dumps({
                        "success": False,
                        "error": "document_type is required for add action",
                    })
                if not title:
                    return json.dumps({
                        "success": False,
                        "error": "title is required for add action",
                    })

                # CRITICAL VALIDATION: PRP documents must use structured JSON format
                if document_type == "prp":
                    if not isinstance(content, dict):
                        return json.dumps({
                            "success": False,
                            "error": "PRP documents (document_type='prp') require structured JSON content, not markdown strings. Content must be a dictionary with sections like 'goal', 'why', 'what', 'context', 'implementation_blueprint', 'validation'. See MCP documentation for required PRP structure.",
                        })

                    # Validate required PRP structure fields
                    required_fields = [
                        "goal",
                        "why",
                        "what",
                        "context",
                        "implementation_blueprint",
                        "validation",
                    ]
                    missing_fields = [field for field in required_fields if field not in content]
                    if missing_fields:
                        return json.dumps({
                            "success": False,
                            "error": f"PRP content missing required fields: {missing_fields}. PRP documents must include: goal, why, what, context, implementation_blueprint, validation. See MCP documentation for complete PRP structure template.",
                        })

                    # Ensure document_type is set in content for PRPViewer compatibility
                    if "document_type" not in content:
                        content["document_type"] = "prp"

                # Call Server API to create document
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        urljoin(api_url, f"/api/projects/{project_id}/docs"),
                        json={
                            "document_type": document_type,
                            "title": title,
                            "content": content,
                            "tags": metadata.get("tags") if metadata else None,
                            "author": metadata.get("author") if metadata else None,
                        },
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "document": result.get("document"),
                            "message": result.get("message"),
                        })
                    else:
                        error_detail = response.text
                        return json.dumps({"success": False, "error": error_detail})

            elif action == "list":
                async with httpx.AsyncClient(timeout=timeout) as client:
                    url = urljoin(api_url, f"/api/projects/{project_id}/docs")
                    logger.info(f"Calling document list API: {url}")
                    response = await client.get(url)

                    logger.info(f"Document list API response: {response.status_code}")
                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({"success": True, **result})
                    else:
                        error_text = response.text
                        logger.error(
                            f"Document list API error: {response.status_code} - {error_text}"
                        )
                        return json.dumps({
                            "success": False,
                            "error": f"HTTP {response.status_code}: {error_text}",
                        })

            elif action == "get":
                if not doc_id:
                    return json.dumps({
                        "success": False,
                        "error": "doc_id is required for get action",
                    })

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        urljoin(api_url, f"/api/projects/{project_id}/docs/{doc_id}")
                    )

                    if response.status_code == 200:
                        document = response.json()
                        return json.dumps({"success": True, "document": document})
                    elif response.status_code == 404:
                        return json.dumps({
                            "success": False,
                            "error": f"Document {doc_id} not found",
                        })
                    else:
                        return json.dumps({"success": False, "error": "Failed to get document"})

            elif action == "update":
                if not doc_id:
                    return json.dumps({
                        "success": False,
                        "error": "doc_id is required for update action",
                    })

                # CRITICAL VALIDATION: PRP documents must use structured JSON format
                if content is not None:
                    # First get the existing document to check its type
                    async with httpx.AsyncClient(timeout=timeout) as client:
                        get_response = await client.get(
                            urljoin(api_url, f"/api/projects/{project_id}/docs/{doc_id}")
                        )
                        if get_response.status_code == 200:
                            existing_doc = get_response.json().get("document", {})
                            existing_type = existing_doc.get(
                                "document_type", existing_doc.get("type")
                            )

                            if existing_type == "prp":
                                if not isinstance(content, dict):
                                    return json.dumps({
                                        "success": False,
                                        "error": "PRP documents (document_type='prp') require structured JSON content, not markdown strings. "
                                        "Content must be a dictionary with required fields: goal, why, what, context, implementation_blueprint, validation. "
                                        "See project_module.py lines 570-756 for the complete PRP structure specification.",
                                    })

                                # Validate required PRP fields
                                required_fields = [
                                    "goal",
                                    "why",
                                    "what",
                                    "context",
                                    "implementation_blueprint",
                                    "validation",
                                ]
                                missing_fields = [
                                    field for field in required_fields if field not in content
                                ]

                                if missing_fields:
                                    return json.dumps({
                                        "success": False,
                                        "error": f"PRP content missing required fields: {', '.join(missing_fields)}. "
                                        f"Required fields: {', '.join(required_fields)}",
                                    })

                                # Ensure document_type is set for PRPViewer compatibility
                                if "document_type" not in content:
                                    content["document_type"] = "prp"

                # Build update fields
                update_fields = {}
                if title is not None:
                    update_fields["title"] = title
                if content is not None:
                    update_fields["content"] = content
                if metadata:
                    if "tags" in metadata:
                        update_fields["tags"] = metadata["tags"]
                    if "author" in metadata:
                        update_fields["author"] = metadata["author"]

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.put(
                        urljoin(api_url, f"/api/projects/{project_id}/docs/{doc_id}"),
                        json=update_fields,
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "document": result.get("document"),
                            "message": result.get("message"),
                        })
                    else:
                        error_detail = response.text
                        return json.dumps({"success": False, "error": error_detail})

            elif action == "delete":
                if not doc_id:
                    return json.dumps({
                        "success": False,
                        "error": "doc_id is required for delete action",
                    })

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.delete(
                        urljoin(api_url, f"/api/projects/{project_id}/docs/{doc_id}")
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({"success": True, "message": result.get("message")})
                    else:
                        return json.dumps({"success": False, "error": "Failed to delete document"})

            else:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid action '{action}'. Must be one of: add, list, get, update, delete",
                })

        except Exception as e:
            logger.error(f"Error in manage_document: {e}")
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool()
    async def manage_versions(
        ctx: Context,
        action: str,
        project_id: str,
        field_name: str,
        version_number: int = None,
        content: dict[str, Any] = None,
        change_summary: str = None,
        document_id: str = None,
        created_by: str = "system",
    ) -> str:
        """
        Manage immutable version history for project data.

        Auto-versions created on every document update. Versions are permanent and restorable.

        Args:
            action: "create" | "list" | "get" | "restore"
            project_id: Project UUID (always required)
            field_name: "docs" | "features" | "data" | "prd"
            version_number: Version number (for get/restore)
            content: Complete content to snapshot (for create)
            change_summary: Description of changes (for create)
            document_id: Document UUID (optional, for docs field)
            created_by: Creator identifier (default: "system")

        Returns:
            JSON string with structure:
            - success: bool - Operation success status
            - version: dict - Version object with metadata (for create action)
            - versions: list[dict] - Array of versions (for list action, via spread operator)
            - content: Any - Full versioned content (for get action, via spread operator)
            - message: str - Operation message (for create/restore actions)
            - error: str - Error description if success=false

        Examples:
            List history: manage_versions(action="list", project_id="uuid", field_name="docs")
            Get version: manage_versions(action="get", project_id="uuid", field_name="docs", version_number=3)
            Restore: manage_versions(action="restore", project_id="uuid", field_name="docs", version_number=2)
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            if action == "create":
                if not content:
                    return json.dumps({
                        "success": False,
                        "error": "content is required for create action",
                    })

                # Call Server API to create version
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        urljoin(api_url, f"/api/projects/{project_id}/versions"),
                        json={
                            "field_name": field_name,
                            "content": content,
                            "change_summary": change_summary,
                            "change_type": "manual",
                            "document_id": document_id,
                            "created_by": created_by,
                        },
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "version": result.get("version"),
                            "message": result.get("message"),
                        })
                    else:
                        error_detail = response.text
                        return json.dumps({"success": False, "error": error_detail})

            elif action == "list":
                # Build URL with optional field_name parameter
                params = {}
                if field_name:
                    params["field_name"] = field_name

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        urljoin(api_url, f"/api/projects/{project_id}/versions"), params=params
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({"success": True, **result})
                    else:
                        return json.dumps({"success": False, "error": "Failed to list versions"})

            elif action == "get":
                if not version_number:
                    return json.dumps({
                        "success": False,
                        "error": "version_number is required for get action",
                    })

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        urljoin(
                            api_url,
                            f"/api/projects/{project_id}/versions/{field_name}/{version_number}",
                        )
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({"success": True, **result})
                    elif response.status_code == 404:
                        return json.dumps({
                            "success": False,
                            "error": f"Version {version_number} not found",
                        })
                    else:
                        return json.dumps({"success": False, "error": "Failed to get version"})

            elif action == "restore":
                if not version_number:
                    return json.dumps({
                        "success": False,
                        "error": "version_number is required for restore action",
                    })

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        urljoin(
                            api_url,
                            f"/api/projects/{project_id}/versions/{field_name}/{version_number}/restore",
                        ),
                        json={"restored_by": created_by},
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({"success": True, "message": result.get("message")})
                    else:
                        error_detail = response.text
                        return json.dumps({"success": False, "error": error_detail})

            else:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid action '{action}'. Must be one of: create, list, get, restore",
                })

        except Exception as e:
            logger.error(f"Error in manage_versions: {e}")
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool()
    async def get_project_features(ctx: Context, project_id: str) -> str:
        """
        Get features from a project's features JSONB field.

        Args:
            project_id: UUID of the project

        Returns:
            JSON string with structure:
            - success: bool - Operation success status
            - features: list[dict] - Array of project features (via spread operator)
            - error: str - Error description if success=false
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(
                    urljoin(api_url, f"/api/projects/{project_id}/features")
                )

                if response.status_code == 200:
                    result = response.json()
                    return json.dumps({"success": True, **result})
                elif response.status_code == 404:
                    return json.dumps({"success": False, "error": "Project not found"})
                else:
                    return json.dumps({"success": False, "error": "Failed to get project features"})

        except Exception as e:
            logger.error(f"Error getting project features: {e}")
            return json.dumps({"success": False, "error": str(e)})

    logger.info("✓ Project Module registered with 5 consolidated tools")
