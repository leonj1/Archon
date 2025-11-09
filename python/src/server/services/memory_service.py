"""
Memory Service Module for Archon

This module provides core business logic for storing and retrieving AI memories
across sessions. Memories are contextual knowledge, patterns, and learnings that
AI assistants can persist and recall.
"""

import json
import struct
import uuid
from datetime import datetime
from typing import Any, Optional

import aiosqlite

from src.server.config.logfire_config import get_logger
from src.server.services.embeddings import create_embedding

logger = get_logger(__name__)


class MemoryService:
    """Service class for memory storage and retrieval operations"""

    VALID_MEMORY_TYPES = {"pattern", "solution", "api", "architecture", "learning"}

    def __init__(self, db_path: str = "/data/archon.db"):
        """
        Initialize memory service with SQLite database path.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

    async def store_memory(
        self,
        memory_key: str,
        memory_content: str,
        memory_type: str = "learning",
        session_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> tuple[bool, dict[str, Any]]:
        """
        Store a new memory or update existing one.

        Args:
            memory_key: Unique identifier for the memory (e.g., "auth_pattern_jwt")
            memory_content: The actual knowledge/pattern to store
            memory_type: Category - "pattern", "solution", "api", "architecture", "learning"
            session_id: Optional session scoping
            tags: List of tags for filtering
            metadata: Additional context as key-value pairs

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Validate inputs
            if not memory_key or not isinstance(memory_key, str):
                return False, {"error": "memory_key is required and must be a string"}

            if not memory_content or not isinstance(memory_content, str):
                return False, {"error": "memory_content is required and must be a string"}

            if memory_type not in self.VALID_MEMORY_TYPES:
                return False, {"error": f"memory_type must be one of {self.VALID_MEMORY_TYPES}"}

            # Generate embedding for semantic search
            try:
                embedding_vector = await create_embedding(memory_content)
                if not embedding_vector or not isinstance(embedding_vector, list):
                    logger.warning(f"Failed to generate embedding for memory: {memory_key}")
                    embedding_blob = None
                else:
                    # Convert list to blob for SQLite storage
                    embedding_blob = struct.pack(f"{len(embedding_vector)}f", *embedding_vector)
            except Exception as e:
                logger.error(f"Error generating embedding: {e}", exc_info=True)
                embedding_blob = None

            # Serialize tags and metadata
            tags_json = json.dumps(tags) if tags else None
            metadata_json = json.dumps(metadata) if metadata else None

            # Check if memory_key already exists
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute(
                    "SELECT id FROM archon_mcp_memories WHERE memory_key = ?",
                    (memory_key,)
                )
                existing = await cursor.fetchone()

                if existing:
                    # Update existing memory
                    memory_id = existing[0]
                    await conn.execute(
                        """
                        UPDATE archon_mcp_memories
                        SET memory_content = ?,
                            memory_type = ?,
                            session_id = ?,
                            tags = ?,
                            metadata = ?,
                            embedding = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                        """,
                        (
                            memory_content,
                            memory_type,
                            session_id,
                            tags_json,
                            metadata_json,
                            embedding_blob,
                            memory_id,
                        ),
                    )
                    await conn.commit()
                    action = "updated"
                else:
                    # Create new memory
                    memory_id = str(uuid.uuid4())
                    await conn.execute(
                        """
                        INSERT INTO archon_mcp_memories (
                            id, memory_key, memory_content, memory_type,
                            session_id, tags, metadata, embedding
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            memory_id,
                            memory_key,
                            memory_content,
                            memory_type,
                            session_id,
                            tags_json,
                            metadata_json,
                            embedding_blob,
                        ),
                    )
                    await conn.commit()
                    action = "created"

                    # Initialize stats entry
                    await conn.execute(
                        """
                        INSERT OR IGNORE INTO archon_mcp_memory_stats (memory_id, access_count)
                        VALUES (?, 0)
                        """,
                        (memory_id,)
                    )
                    await conn.commit()

            logger.info(f"Memory {action}: {memory_key} (ID: {memory_id})")

            return True, {
                "memory_id": memory_id,
                "memory_key": memory_key,
                "action": action,
                "message": f"Memory {action} successfully",
            }

        except Exception as e:
            logger.error(f"Error storing memory: {e}", exc_info=True)
            return False, {"error": f"Failed to store memory: {str(e)}"}

    async def retrieve_memory_by_key(
        self, memory_key: str
    ) -> tuple[bool, dict[str, Any]]:
        """
        Retrieve a memory by exact key match.

        Args:
            memory_key: The unique identifier for the memory

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute(
                    """
                    SELECT id, memory_key, memory_content, memory_type,
                           session_id, tags, metadata, created_at, updated_at
                    FROM archon_mcp_memories
                    WHERE memory_key = ?
                    """,
                    (memory_key,)
                )
                row = await cursor.fetchone()

                if not row:
                    return False, {"error": f"Memory not found: {memory_key}"}

                # Update access statistics (atomic increment)
                await conn.execute(
                    """
                    INSERT INTO archon_mcp_memory_stats (memory_id, access_count, last_accessed)
                    VALUES (?, 1, CURRENT_TIMESTAMP)
                    ON CONFLICT(memory_id) DO UPDATE SET
                        access_count = archon_mcp_memory_stats.access_count + 1,
                        last_accessed = excluded.last_accessed
                    """,
                    (row[0],)
                )
                await conn.commit()

                memory = {
                    "id": row[0],
                    "memory_key": row[1],
                    "memory_content": row[2],
                    "memory_type": row[3],
                    "session_id": row[4],
                    "tags": json.loads(row[5]) if row[5] else [],
                    "metadata": json.loads(row[6]) if row[6] else {},
                    "created_at": row[7],
                    "updated_at": row[8],
                }

                return True, {"memory": memory}

        except Exception as e:
            logger.error(f"Error retrieving memory: {e}", exc_info=True)
            return False, {"error": f"Failed to retrieve memory: {str(e)}"}

    async def search_memories(
        self,
        query: Optional[str] = None,
        memory_type: Optional[str] = None,
        tags: Optional[list[str]] = None,
        session_id: Optional[str] = None,
        match_count: int = 5,
    ) -> tuple[bool, dict[str, Any]]:
        """
        Search memories by query, type, tags, or session.

        For semantic search, provide a query string.
        For filtering, provide type, tags, or session_id.

        Args:
            query: Optional text query for semantic search
            memory_type: Filter by type
            tags: Filter by tags (exact match, returns memories with any of the specified tags)
            session_id: Filter by session
            match_count: Maximum results to return

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Validate match_count
            if match_count <= 0:
                return False, {"error": "match_count must be greater than 0"}

            async with aiosqlite.connect(self.db_path) as conn:
                # Build query dynamically
                sql = """
                    SELECT m.id, m.memory_key, m.memory_content, m.memory_type,
                           m.session_id, m.tags, m.metadata, m.created_at, m.updated_at,
                           COALESCE(s.access_count, 0) as access_count
                    FROM archon_mcp_memories m
                    LEFT JOIN archon_mcp_memory_stats s ON m.id = s.memory_id
                    WHERE 1=1
                """
                params = []

                # Apply filters
                if memory_type:
                    sql += " AND m.memory_type = ?"
                    params.append(memory_type)

                if session_id:
                    sql += " AND m.session_id = ?"
                    params.append(session_id)

                if tags:
                    # Filter by exact tag match using JSON functions (any tag in the list)
                    tag_conditions = " OR ".join([
                        "EXISTS (SELECT 1 FROM json_each(m.tags) WHERE json_each.value = ?)"
                        for _ in tags
                    ])
                    sql += f" AND ({tag_conditions})"
                    params.extend(tags)

                # If query provided, do simple text search (semantic search would require vector similarity)
                if query:
                    sql += " AND (m.memory_key LIKE ? OR m.memory_content LIKE ?)"
                    params.extend([f"%{query}%", f"%{query}%"])

                # Order by access count and recency
                sql += " ORDER BY s.access_count DESC, m.updated_at DESC LIMIT ?"
                params.append(match_count)

                cursor = await conn.execute(sql, params)
                rows = await cursor.fetchall()

                memories = []
                for row in rows:
                    memories.append({
                        "id": row[0],
                        "memory_key": row[1],
                        "memory_content": row[2],
                        "memory_type": row[3],
                        "session_id": row[4],
                        "tags": json.loads(row[5]) if row[5] else [],
                        "metadata": json.loads(row[6]) if row[6] else {},
                        "created_at": row[7],
                        "updated_at": row[8],
                        "access_count": row[9],
                    })

                return True, {
                    "memories": memories,
                    "count": len(memories),
                    "query": query,
                    "filters": {
                        "memory_type": memory_type,
                        "tags": tags,
                        "session_id": session_id,
                    }
                }

        except Exception as e:
            logger.error(f"Error searching memories: {e}", exc_info=True)
            return False, {"error": f"Failed to search memories: {str(e)}"}

    async def list_memories(
        self,
        memory_type: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 50,
    ) -> tuple[bool, dict[str, Any]]:
        """
        List all memories with optional filtering.

        Args:
            memory_type: Filter by type
            session_id: Filter by session
            limit: Maximum results to return

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Validate limit
            if limit <= 0:
                return False, {"error": "limit must be greater than 0"}

            async with aiosqlite.connect(self.db_path) as conn:
                sql = """
                    SELECT m.id, m.memory_key, m.memory_content, m.memory_type,
                           m.session_id, m.tags, m.metadata, m.created_at, m.updated_at
                    FROM archon_mcp_memories m
                    WHERE 1=1
                """
                params = []

                if memory_type:
                    sql += " AND m.memory_type = ?"
                    params.append(memory_type)

                if session_id:
                    sql += " AND m.session_id = ?"
                    params.append(session_id)

                sql += " ORDER BY m.updated_at DESC LIMIT ?"
                params.append(limit)

                cursor = await conn.execute(sql, params)
                rows = await cursor.fetchall()

                memories = []
                for row in rows:
                    # Truncate content for list view
                    content = row[2][:200] + "..." if len(row[2]) > 200 else row[2]
                    memories.append({
                        "id": row[0],
                        "memory_key": row[1],
                        "memory_content": content,
                        "memory_type": row[3],
                        "session_id": row[4],
                        "tags": json.loads(row[5]) if row[5] else [],
                        "metadata": json.loads(row[6]) if row[6] else {},
                        "created_at": row[7],
                        "updated_at": row[8],
                    })

                return True, {"memories": memories, "total": len(memories)}

        except Exception as e:
            logger.error(f"Error listing memories: {e}", exc_info=True)
            return False, {"error": f"Failed to list memories: {str(e)}"}

    async def delete_memory(self, memory_id: str) -> tuple[bool, dict[str, Any]]:
        """
        Delete a memory by ID.

        Args:
            memory_id: UUID of the memory to delete

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                # Check if memory exists
                cursor = await conn.execute(
                    "SELECT memory_key FROM archon_mcp_memories WHERE id = ?",
                    (memory_id,)
                )
                row = await cursor.fetchone()

                if not row:
                    return False, {"error": f"Memory not found: {memory_id}"}

                memory_key = row[0]

                # Delete memory (stats will cascade via foreign key)
                await conn.execute(
                    "DELETE FROM archon_mcp_memories WHERE id = ?",
                    (memory_id,)
                )
                await conn.commit()

                logger.info(f"Memory deleted: {memory_key} (ID: {memory_id})")

                return True, {"message": "Memory deleted successfully", "memory_key": memory_key}

        except Exception as e:
            logger.error(f"Error deleting memory: {e}", exc_info=True)
            return False, {"error": f"Failed to delete memory: {str(e)}"}


# Global instance for convenience
_memory_service_instance = None


def get_memory_service(db_path: str = "/data/archon.db") -> MemoryService:
    """
    Get or create the global memory service instance.

    Args:
        db_path: Path to SQLite database

    Returns:
        MemoryService instance
    """
    global _memory_service_instance
    if _memory_service_instance is None:
        _memory_service_instance = MemoryService(db_path)
    return _memory_service_instance
