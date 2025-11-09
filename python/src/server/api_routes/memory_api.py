"""
Memory API endpoints for Archon

Handles:
- Memory storage (create/update)
- Memory retrieval (by key, search, list)
- Memory deletion
"""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Response
from fastapi import status as http_status
from pydantic import BaseModel, Field

from ..config.logfire_config import get_logger, logfire
from ..services.memory_service import get_memory_service

logger = get_logger(__name__)

router = APIRouter(prefix="/api/memory", tags=["memory"])


class StoreMemoryRequest(BaseModel):
    """Request model for storing a memory"""
    memory_key: str = Field(..., description="Unique identifier for the memory")
    memory_content: str = Field(..., description="The actual knowledge/pattern to store")
    memory_type: str = Field(
        default="learning",
        description="Category: pattern, solution, api, architecture, learning"
    )
    session_id: Optional[str] = Field(None, description="Optional session scoping")
    tags: Optional[list[str]] = Field(None, description="List of tags for filtering")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional context")


class SearchMemoriesRequest(BaseModel):
    """Request model for searching memories"""
    query: Optional[str] = Field(None, description="Text query for search")
    memory_type: Optional[str] = Field(None, description="Filter by type")
    tags: Optional[list[str]] = Field(None, description="Filter by tags")
    session_id: Optional[str] = Field(None, description="Filter by session")
    match_count: int = Field(default=5, ge=1, le=50, description="Maximum results")


@router.post("/store")
async def store_memory(request: StoreMemoryRequest, response: Response):
    """
    Store a new memory or update existing one.

    If a memory with the same key exists, it will be updated.
    Otherwise, a new memory will be created.

    Returns:
        JSON with memory_id, memory_key, action (created/updated), and message
    """
    try:
        logfire.info(
            f"Storing memory | key={request.memory_key} | type={request.memory_type}"
        )

        memory_service = get_memory_service()
        success, result = await memory_service.store_memory(
            memory_key=request.memory_key,
            memory_content=request.memory_content,
            memory_type=request.memory_type,
            session_id=request.session_id,
            tags=request.tags,
            metadata=request.metadata,
        )

        if not success:
            error_msg = result.get("error", "Unknown error")
            logfire.error(f"Failed to store memory | error={error_msg}")
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        logfire.info(
            f"Memory stored successfully | key={request.memory_key} | "
            f"action={result.get('action')} | id={result.get('memory_id')}"
        )

        return {
            "success": True,
            "memory_id": result.get("memory_id"),
            "memory_key": result.get("memory_key"),
            "action": result.get("action"),
            "message": result.get("message"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error storing memory: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store memory: {str(e)}"
        )


@router.get("/retrieve/{memory_key}")
async def retrieve_memory_by_key(memory_key: str):
    """
    Retrieve a memory by exact key match.

    Args:
        memory_key: The unique identifier for the memory

    Returns:
        JSON with memory object containing all fields
    """
    try:
        logfire.info(f"Retrieving memory by key | key={memory_key}")

        memory_service = get_memory_service()
        success, result = await memory_service.retrieve_memory_by_key(memory_key)

        if not success:
            error_msg = result.get("error", "Unknown error")
            logfire.warning(f"Memory not found | key={memory_key}")
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )

        logfire.info(f"Memory retrieved successfully | key={memory_key}")

        return {
            "success": True,
            "memory": result.get("memory"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving memory: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve memory: {str(e)}"
        )


@router.post("/search")
async def search_memories(request: SearchMemoriesRequest):
    """
    Search memories by query, type, tags, or session.

    Performs text-based search when query is provided.
    Filters by type, tags, or session when specified.
    Results are ordered by access count and recency.

    Returns:
        JSON with list of matching memories
    """
    try:
        logfire.info(
            f"Searching memories | query={request.query} | "
            f"type={request.memory_type} | tags={request.tags}"
        )

        memory_service = get_memory_service()
        success, result = await memory_service.search_memories(
            query=request.query,
            memory_type=request.memory_type,
            tags=request.tags,
            session_id=request.session_id,
            match_count=request.match_count,
        )

        if not success:
            error_msg = result.get("error", "Unknown error")
            logfire.error(f"Failed to search memories | error={error_msg}")
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        memory_count = result.get("count", 0)
        logfire.info(f"Memory search completed | results={memory_count}")

        return {
            "success": True,
            "memories": result.get("memories", []),
            "count": memory_count,
            "query": result.get("query"),
            "filters": result.get("filters", {}),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching memories: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search memories: {str(e)}"
        )


@router.get("/list")
async def list_memories(
    memory_type: Optional[str] = None,
    session_id: Optional[str] = None,
    limit: int = 50,
):
    """
    List all memories with optional filtering.

    Query parameters:
        memory_type: Filter by type (pattern, solution, api, architecture, learning)
        session_id: Filter by session ID
        limit: Maximum number of results (default 50, max 200)

    Returns:
        JSON with list of memories (content truncated for list view)
    """
    try:
        # Enforce maximum limit
        limit = min(limit, 200)

        logfire.info(
            f"Listing memories | type={memory_type} | "
            f"session={session_id} | limit={limit}"
        )

        memory_service = get_memory_service()
        success, result = await memory_service.list_memories(
            memory_type=memory_type,
            session_id=session_id,
            limit=limit,
        )

        if not success:
            error_msg = result.get("error", "Unknown error")
            logfire.error(f"Failed to list memories | error={error_msg}")
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        total = result.get("total", 0)
        logfire.info(f"Memories listed successfully | total={total}")

        return {
            "success": True,
            "memories": result.get("memories", []),
            "total": total,
            "filters": {
                "memory_type": memory_type,
                "session_id": session_id,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing memories: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list memories: {str(e)}"
        )


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str):
    """
    Delete a memory by ID.

    Args:
        memory_id: UUID of the memory to delete

    Returns:
        JSON with success message
    """
    try:
        logfire.info(f"Deleting memory | id={memory_id}")

        memory_service = get_memory_service()
        success, result = await memory_service.delete_memory(memory_id)

        if not success:
            error_msg = result.get("error", "Unknown error")
            logfire.warning(f"Memory not found for deletion | id={memory_id}")
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )

        logfire.info(
            f"Memory deleted successfully | id={memory_id} | "
            f"key={result.get('memory_key')}"
        )

        return {
            "success": True,
            "message": result.get("message"),
            "memory_key": result.get("memory_key"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting memory: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete memory: {str(e)}"
        )
