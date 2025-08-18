"""
Simple document management tools for Archon MCP Server.

Provides separate, focused tools for each document operation.
Supports various document types including specs, designs, notes, and PRPs.
"""

import json
import logging
from typing import Any, Optional, Dict, List
from urllib.parse import urljoin

import httpx
from mcp.server.fastmcp import Context, FastMCP

from src.server.config.service_discovery import get_api_url

logger = logging.getLogger(__name__)


def register_document_tools(mcp: FastMCP):
    """Register individual document management tools with the MCP server."""

    @mcp.tool()
    async def create_document(
        ctx: Context,
        project_id: str,
        title: str,
        document_type: str,
        content: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        author: Optional[str] = None,
    ) -> str:
        """
        Create a new document with automatic versioning.

        Args:
            project_id: Project UUID (required)
            title: Document title (required)
            document_type: Type of document. Common types:
                - "spec": Technical specifications
                - "design": Design documents
                - "note": General notes
                - "prp": Product requirement prompts
                - "api": API documentation
                - "guide": User guides
            content: Document content as structured JSON (optional).
                     Can be any JSON structure that fits your needs.
            tags: List of tags for categorization (e.g., ["backend", "auth"])
            author: Document author name (optional)

        Returns:
            JSON with document details:
            {
                "success": true,
                "document": {...},
                "document_id": "doc-123",
                "message": "Document created successfully"
            }

        Examples:
            # Create API specification
            create_document(
                project_id="550e8400-e29b-41d4-a716-446655440000",
                title="REST API Specification",
                document_type="spec",
                content={
                    "endpoints": [
                        {"path": "/users", "method": "GET", "description": "List users"},
                        {"path": "/users/{id}", "method": "GET", "description": "Get user"}
                    ],
                    "authentication": "Bearer token",
                    "version": "1.0.0"
                },
                tags=["api", "backend"],
                author="API Team"
            )

            # Create design document
            create_document(
                project_id="550e8400-e29b-41d4-a716-446655440000",
                title="Authentication Flow Design",
                document_type="design",
                content={
                    "overview": "OAuth2 implementation design",
                    "components": ["AuthProvider", "TokenManager", "UserSession"],
                    "flow": {"step1": "Redirect to provider", "step2": "Exchange code"}
                }
            )
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    urljoin(api_url, f"/api/projects/{project_id}/docs"),
                    json={
                        "document_type": document_type,
                        "title": title,
                        "content": content or {},
                        "tags": tags,
                        "author": author,
                    },
                )

                if response.status_code == 200:
                    result = response.json()
                    return json.dumps({
                        "success": True,
                        "document": result.get("document"),
                        "document_id": result.get("document", {}).get("id"),
                        "message": result.get("message", "Document created successfully"),
                    })
                else:
                    error_detail = response.text
                    return json.dumps({"success": False, "error": error_detail})

        except Exception as e:
            logger.error(f"Error creating document: {e}")
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool()
    async def list_documents(ctx: Context, project_id: str) -> str:
        """
        List all documents for a project.

        Args:
            project_id: Project UUID (required)

        Returns:
            JSON array of documents

        Example:
            list_documents(project_id="uuid")
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(urljoin(api_url, f"/api/projects/{project_id}/docs"))

                if response.status_code == 200:
                    result = response.json()
                    return json.dumps({
                        "success": True,
                        "documents": result.get("documents", []),
                        "count": len(result.get("documents", [])),
                    })
                else:
                    return json.dumps({
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text}",
                    })

        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool()
    async def get_document(ctx: Context, project_id: str, doc_id: str) -> str:
        """
        Get detailed information about a specific document.

        Args:
            project_id: Project UUID (required)
            doc_id: Document UUID (required)

        Returns:
            JSON with complete document details

        Example:
            get_document(project_id="uuid", doc_id="doc-uuid")
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(
                    urljoin(api_url, f"/api/projects/{project_id}/docs/{doc_id}")
                )

                if response.status_code == 200:
                    document = response.json()
                    return json.dumps({"success": True, "document": document})
                elif response.status_code == 404:
                    return json.dumps({"success": False, "error": f"Document {doc_id} not found"})
                else:
                    return json.dumps({"success": False, "error": "Failed to get document"})

        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool()
    async def update_document(
        ctx: Context,
        project_id: str,
        doc_id: str,
        title: Optional[str] = None,
        content: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        author: Optional[str] = None,
    ) -> str:
        """
        Update a document's properties.

        Args:
            project_id: Project UUID (required)
            doc_id: Document UUID (required)
            title: New document title (optional)
            content: New document content (optional)
            tags: New tags list (optional)
            author: New author (optional)

        Returns:
            JSON with updated document details

        Example:
            update_document(project_id="uuid", doc_id="doc-uuid", title="New Title",
                          content={"updated": "content"})
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            # Build update fields
            update_fields: Dict[str, Any] = {}
            if title is not None:
                update_fields["title"] = title
            if content is not None:
                update_fields["content"] = content
            if tags is not None:
                update_fields["tags"] = tags
            if author is not None:
                update_fields["author"] = author

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
                        "message": result.get("message", "Document updated successfully"),
                    })
                else:
                    error_detail = response.text
                    return json.dumps({"success": False, "error": error_detail})

        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool()
    async def delete_document(ctx: Context, project_id: str, doc_id: str) -> str:
        """
        Delete a document.

        Args:
            project_id: Project UUID (required)
            doc_id: Document UUID (required)

        Returns:
            JSON confirmation of deletion

        Example:
            delete_document(project_id="uuid", doc_id="doc-uuid")
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.delete(
                    urljoin(api_url, f"/api/projects/{project_id}/docs/{doc_id}")
                )

                if response.status_code == 200:
                    result = response.json()
                    return json.dumps({
                        "success": True,
                        "message": result.get("message", f"Document {doc_id} deleted successfully"),
                    })
                elif response.status_code == 404:
                    return json.dumps({"success": False, "error": f"Document {doc_id} not found"})
                else:
                    return json.dumps({"success": False, "error": "Failed to delete document"})

        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return json.dumps({"success": False, "error": str(e)})
