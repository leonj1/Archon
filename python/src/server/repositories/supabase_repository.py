"""
Supabase Database Repository Implementation

Concrete implementation of the DatabaseRepository interface using Supabase.
All methods are production-ready with proper error handling and logging.
"""

from datetime import datetime
from typing import Any

from supabase import Client

from ..config.logfire_config import get_logger
from .database_repository import DatabaseRepository

logger = get_logger(__name__)

class SupabaseDatabaseRepository(DatabaseRepository):
    """
    Concrete implementation of DatabaseRepository using Supabase client.

    This class encapsulates all Supabase-specific database operations,
    providing a clean interface for service classes.
    """

    def __init__(self, supabase_client: Client):
        """
        Initialize the repository with a Supabase client.

        Args:
            supabase_client: Configured Supabase client instance
        """
        self.supabase_client = supabase_client

    # ========================================================================
    # 1. PAGE METADATA OPERATIONS
    # ========================================================================

    async def get_page_metadata_by_id(self, page_id: str) -> dict[str, Any] | None:
        """Retrieve page metadata by page ID from archon_page_metadata table."""
        try:
            result = (
                self.supabase_client.table("archon_page_metadata")
                .select("id, url, section_title, word_count")
                .eq("id", page_id)
                .maybe_single()
                .execute()
            )

            if result and result.data is not None:
                return result.data
            return None

        except Exception as e:
            logger.error(f"Failed to get page metadata by ID {page_id}: {e}")
            raise

    async def get_page_metadata_by_url(self, url: str) -> dict[str, Any] | None:
        """Retrieve page metadata by URL from archon_page_metadata table."""
        try:
            result = (
                self.supabase_client.table("archon_page_metadata")
                .select("id, url, section_title, word_count")
                .eq("url", url)
                .maybe_single()
                .execute()
            )

            if result and result.data is not None:
                return result.data
            return None

        except Exception as e:
            logger.error(f"Failed to get page metadata by URL {url}: {e}")
            raise

    async def list_pages_by_source(
        self,
        source_id: str,
        limit: int | None = None,
        offset: int | None = None
    ) -> list[dict[str, Any]]:
        """List all pages for a given source."""
        try:
            query = (
                self.supabase_client.table("archon_crawled_pages")
                .select("*")
                .eq("source_id", source_id)
                .order("created_at", desc=True)
            )

            if limit is not None:
                query = query.limit(limit)
            if offset is not None:
                query = query.offset(offset)

            result = query.execute()
            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to list pages by source {source_id}: {e}")
            raise

    async def get_page_count_by_source(self, source_id: str) -> int:
        """Get the count of pages for a source."""
        try:
            result = (
                self.supabase_client.table("archon_crawled_pages")
                .select("id", count="exact")
                .eq("source_id", source_id)
                .execute()
            )
            return result.count if result.count is not None else 0

        except Exception as e:
            logger.error(f"Failed to get page count for source {source_id}: {e}")
            raise

    async def upsert_page_metadata_batch(
        self,
        pages: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Insert or update multiple page metadata records in a batch."""
        try:
            if not pages:
                return []

            result = (
                self.supabase_client.table("archon_page_metadata")
                .upsert(pages, on_conflict="url")
                .execute()
            )

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to batch upsert {len(pages)} page metadata records: {e}")
            raise

    async def update_page_chunk_count(self, page_id: str, chunk_count: int) -> dict[str, Any] | None:
        """Update the chunk_count field for a page after chunking is complete."""
        try:
            result = (
                self.supabase_client.table("archon_page_metadata")
                .update({"chunk_count": chunk_count})
                .eq("id", page_id)
                .execute()
            )

            if result.data and len(result.data) > 0:
                return result.data[0]

            return None

        except Exception as e:
            logger.error(f"Failed to update chunk_count for page {page_id}: {e}")
            raise

    async def list_page_metadata_by_source(
        self,
        source_id: str,
        section_title: str | None = None
    ) -> list[dict[str, Any]]:
        """
        List page metadata for a given source with optional section filtering.
        Returns summary fields only (no full_content).
        """
        try:
            query = (
                self.supabase_client.table("archon_page_metadata")
                .select("id, url, section_title, section_order, word_count, char_count, chunk_count")
                .eq("source_id", source_id)
            )

            if section_title:
                query = query.eq("section_title", section_title)

            query = query.order("section_order").order("created_at")

            result = query.execute()
            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to list page metadata for source {source_id}: {e}")
            raise

    async def get_full_page_metadata_by_url(self, url: str) -> dict[str, Any] | None:
        """
        Retrieve complete page metadata by URL including full_content.
        """
        try:
            result = (
                self.supabase_client.table("archon_page_metadata")
                .select("*")
                .eq("url", url)
                .maybe_single()
                .execute()
            )

            return result.data if result and result.data else None

        except Exception as e:
            logger.error(f"Failed to get full page metadata by URL {url}: {e}")
            raise

    async def get_full_page_metadata_by_id(self, page_id: str) -> dict[str, Any] | None:
        """
        Retrieve complete page metadata by ID including full_content.
        """
        try:
            result = (
                self.supabase_client.table("archon_page_metadata")
                .select("*")
                .eq("id", page_id)
                .maybe_single()
                .execute()
            )

            return result.data if result and result.data else None

        except Exception as e:
            logger.error(f"Failed to get full page metadata by ID {page_id}: {e}")
            raise

    # ========================================================================
    # 2. DOCUMENT SEARCH OPERATIONS
    # ========================================================================

    async def search_documents_vector(
        self,
        query_embedding: list[float],
        match_count: int = 5,
        filter_metadata: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Perform vector similarity search on documents using Supabase RPC."""
        try:
            params = {
                "query_embedding": query_embedding,
                "match_count": match_count,
            }
            if filter_metadata:
                params["filter_metadata"] = filter_metadata

            result = self.supabase_client.rpc(
                "match_documents",
                params
            ).execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to perform vector search: {e}")
            raise

    async def search_documents_hybrid(
        self,
        query: str,
        query_embedding: list[float],
        match_count: int = 5,
        filter_metadata: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Perform hybrid search combining vector and full-text search."""
        try:
            params = {
                "query_text": query,
                "query_embedding": query_embedding,
                "match_count": match_count,
            }
            if filter_metadata:
                params["filter_metadata"] = filter_metadata

            result = self.supabase_client.rpc(
                "hybrid_search",
                params
            ).execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to perform hybrid search: {e}")
            raise

    async def get_documents_by_source(
        self,
        source_id: str,
        limit: int | None = None
    ) -> list[dict[str, Any]]:
        """Get all document chunks for a source."""
        try:
            query = (
                self.supabase_client.table("archon_documents")
                .select("*")
                .eq("source_id", source_id)
            )

            if limit is not None:
                query = query.limit(limit)

            result = query.execute()
            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to get documents by source {source_id}: {e}")
            raise

    async def get_document_by_id(self, document_id: str) -> dict[str, Any] | None:
        """Get a specific document by ID."""
        try:
            result = (
                self.supabase_client.table("archon_documents")
                .select("*")
                .eq("id", document_id)
                .maybe_single()
                .execute()
            )

            return result.data if result and result.data else None

        except Exception as e:
            logger.error(f"Failed to get document by ID {document_id}: {e}")
            raise

    async def insert_document(self, document_data: dict[str, Any]) -> dict[str, Any]:
        """Insert a new document chunk."""
        try:
            result = (
                self.supabase_client.table("archon_documents")
                .insert(document_data)
                .execute()
            )

            if not result.data:
                raise ValueError("Insert returned no data")

            return result.data[0]

        except Exception as e:
            logger.error(f"Failed to insert document: {e}")
            raise

    async def insert_documents_batch(
        self,
        documents: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Insert multiple document chunks in a batch."""
        try:
            if not documents:
                return []

            result = (
                self.supabase_client.table("archon_documents")
                .insert(documents)
                .execute()
            )

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to batch insert {len(documents)} documents: {e}")
            raise

    async def delete_documents_by_source(self, source_id: str) -> int:
        """Delete all documents for a source."""
        try:
            result = (
                self.supabase_client.table("archon_documents")
                .delete()
                .eq("source_id", source_id)
                .execute()
            )

            deleted_count = len(result.data) if result.data else 0
            logger.info(f"Deleted {deleted_count} documents for source {source_id}")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to delete documents by source {source_id}: {e}")
            raise

    # ========================================================================
    # 3. CODE EXAMPLES OPERATIONS
    # ========================================================================

    async def search_code_examples(
        self,
        query_embedding: list[float],
        match_count: int = 10,
        filter_metadata: dict[str, Any] | None = None,
        source_id: str | None = None
    ) -> list[dict[str, Any]]:
        """Search for code examples using vector similarity."""
        try:
            params = {
                "query_embedding": query_embedding,
                "match_count": match_count,
            }
            if filter_metadata:
                params["filter_metadata"] = filter_metadata
            if source_id:
                params["source_id"] = source_id

            result = self.supabase_client.rpc(
                "match_code_examples",
                params
            ).execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to search code examples: {e}")
            raise

    async def get_code_examples_by_source(
        self,
        source_id: str,
        limit: int | None = None
    ) -> list[dict[str, Any]]:
        """Get all code examples for a source."""
        try:
            query = (
                self.supabase_client.table("archon_code_examples")
                .select("*")
                .eq("source_id", source_id)
            )

            if limit is not None:
                query = query.limit(limit)

            result = query.execute()
            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to get code examples by source {source_id}: {e}")
            raise

    async def get_code_example_count_by_source(self, source_id: str) -> int:
        """Get the count of code examples for a source."""
        try:
            result = (
                self.supabase_client.table("archon_code_examples")
                .select("id", count="exact")
                .eq("source_id", source_id)
                .execute()
            )
            return result.count if result.count is not None else 0

        except Exception as e:
            logger.error(f"Failed to get code example count for source {source_id}: {e}")
            raise

    async def insert_code_example(
        self,
        code_example_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Insert a new code example."""
        try:
            result = (
                self.supabase_client.table("archon_code_examples")
                .insert(code_example_data)
                .execute()
            )

            if not result.data:
                raise ValueError("Insert returned no data")

            return result.data[0]

        except Exception as e:
            logger.error(f"Failed to insert code example: {e}")
            raise

    async def insert_code_examples_batch(
        self,
        code_examples: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Insert multiple code examples in a batch."""
        try:
            if not code_examples:
                return []

            result = (
                self.supabase_client.table("archon_code_examples")
                .insert(code_examples)
                .execute()
            )

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to batch insert {len(code_examples)} code examples: {e}")
            raise

    async def delete_code_examples_by_source(self, source_id: str) -> int:
        """Delete all code examples for a source."""
        try:
            result = (
                self.supabase_client.table("archon_code_examples")
                .delete()
                .eq("source_id", source_id)
                .execute()
            )

            deleted_count = len(result.data) if result.data else 0
            logger.info(f"Deleted {deleted_count} code examples for source {source_id}")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to delete code examples by source {source_id}: {e}")
            raise

    async def delete_code_examples_by_url(self, url: str) -> int:
        """Delete all code examples for a specific URL."""
        try:
            result = (
                self.supabase_client.table("archon_code_examples")
                .delete()
                .eq("url", url)
                .execute()
            )

            deleted_count = len(result.data) if result.data else 0
            logger.info(f"Deleted {deleted_count} code examples for URL {url}")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to delete code examples by URL {url}: {e}")
            raise

    # ========================================================================
    # 4. SETTINGS OPERATIONS
    # ========================================================================

    async def get_settings_by_key(self, key: str) -> Any | None:
        """Retrieve a setting value by its key from archon_settings table."""
        try:
            result = (
                self.supabase_client.table("archon_settings")
                .select("*")
                .eq("key", key)
                .maybe_single()
                .execute()
            )

            if result and result.data is not None:
                return result.data.get("value")
            return None

        except Exception as e:
            logger.error(f"Failed to get setting {key}: {e}")
            raise

    async def get_all_settings(self) -> dict[str, Any]:
        """Retrieve all settings as a dictionary from archon_settings table."""
        try:
            result = (
                self.supabase_client.table("archon_settings")
                .select("*")
                .execute()
            )

            if result and result.data:
                return {item["key"]: item["value"] for item in result.data}
            return {}

        except Exception as e:
            logger.error(f"Failed to get all settings: {e}")
            raise

    async def upsert_setting(self, key: str, value: Any) -> dict[str, Any]:
        """Insert or update a setting."""
        try:
            result = (
                self.supabase_client.table("archon_settings")
                .upsert({"key": key, "value": value})
                .execute()
            )

            if not result.data:
                raise ValueError("Upsert returned no data")

            return result.data[0]

        except Exception as e:
            logger.error(f"Failed to upsert setting {key}: {e}")
            raise

    async def delete_setting(self, key: str) -> bool:
        """Delete a setting by key."""
        try:
            result = (
                self.supabase_client.table("archon_settings")
                .delete()
                .eq("key", key)
                .execute()
            )

            return len(result.data) > 0 if result.data else False

        except Exception as e:
            logger.error(f"Failed to delete setting {key}: {e}")
            raise

    async def get_all_setting_records(self) -> list[dict[str, Any]]:
        """Retrieve all setting records with full details."""
        try:
            result = (
                self.supabase_client.table("archon_settings")
                .select("*")
                .execute()
            )

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to get all setting records: {e}")
            raise

    async def get_setting_records_by_category(self, category: str) -> list[dict[str, Any]]:
        """Retrieve setting records filtered by category."""
        try:
            result = (
                self.supabase_client.table("archon_settings")
                .select("*")
                .eq("category", category)
                .execute()
            )

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to get setting records by category {category}: {e}")
            raise

    async def upsert_setting_record(self, setting_data: dict[str, Any]) -> dict[str, Any]:
        """Insert or update a full setting record."""
        try:
            result = (
                self.supabase_client.table("archon_settings")
                .upsert(setting_data, on_conflict="key")
                .execute()
            )

            if not result.data:
                raise ValueError("Upsert returned no data")

            return result.data[0]

        except Exception as e:
            logger.error(f"Failed to upsert setting record: {e}")
            raise

    # ========================================================================
    # 5. PROJECT OPERATIONS
    # ========================================================================

    async def create_project(self, project_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new project."""
        try:
            if "created_at" not in project_data:
                project_data["created_at"] = datetime.now().isoformat()
            if "updated_at" not in project_data:
                project_data["updated_at"] = datetime.now().isoformat()

            result = (
                self.supabase_client.table("archon_projects")
                .insert(project_data)
                .execute()
            )

            if not result.data:
                raise ValueError("Insert returned no data")

            logger.info(f"Created project {result.data[0]['id']}")
            return result.data[0]

        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            raise

    async def list_projects(
        self,
        include_content: bool = True,
        order_by: str = "created_at",
        desc: bool = True
    ) -> list[dict[str, Any]]:
        """List all projects."""
        try:
            query = self.supabase_client.table("archon_projects").select("*")
            query = query.order(order_by, desc=desc)

            result = query.execute()
            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            raise

    async def get_project_by_id(self, project_id: str) -> dict[str, Any] | None:
        """Get a specific project by ID."""
        try:
            result = (
                self.supabase_client.table("archon_projects")
                .select("*")
                .eq("id", project_id)
                .maybe_single()
                .execute()
            )

            return result.data if result and result.data else None

        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {e}")
            raise

    async def update_project(
        self,
        project_id: str,
        update_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update a project with specified fields."""
        try:
            update_data["updated_at"] = datetime.now().isoformat()

            result = (
                self.supabase_client.table("archon_projects")
                .update(update_data)
                .eq("id", project_id)
                .execute()
            )

            if result.data and len(result.data) > 0:
                return result.data[0]

            # If update returned no data, verify project exists
            project = await self.get_project_by_id(project_id)
            return project

        except Exception as e:
            logger.error(f"Failed to update project {project_id}: {e}")
            raise

    async def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        try:
            result = (
                self.supabase_client.table("archon_projects")
                .delete()
                .eq("id", project_id)
                .execute()
            )

            deleted = len(result.data) > 0 if result.data else False
            if deleted:
                logger.info(f"Deleted project {project_id}")
            return deleted

        except Exception as e:
            logger.error(f"Failed to delete project {project_id}: {e}")
            raise

    async def unpin_all_projects_except(self, project_id: str) -> int:
        """Unpin all projects except the specified one."""
        try:
            result = (
                self.supabase_client.table("archon_projects")
                .update({"pinned": False})
                .neq("id", project_id)
                .eq("pinned", True)
                .execute()
            )

            count = len(result.data) if result.data else 0
            if count > 0:
                logger.debug(f"Unpinned {count} projects")
            return count

        except Exception as e:
            logger.error(f"Failed to unpin projects: {e}")
            raise

    async def get_project_features(self, project_id: str) -> list[dict[str, Any]]:
        """Get features from a project's features JSONB field."""
        try:
            result = (
                self.supabase_client.table("archon_projects")
                .select("features")
                .eq("id", project_id)
                .maybe_single()
                .execute()
            )

            if not result or not result.data:
                return []

            return result.data.get("features", [])

        except Exception as e:
            logger.error(f"Failed to get project features for {project_id}: {e}")
            raise

    # ========================================================================
    # 6. TASK OPERATIONS
    # ========================================================================

    async def create_task(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new task."""
        try:
            if "created_at" not in task_data:
                task_data["created_at"] = datetime.now().isoformat()
            if "updated_at" not in task_data:
                task_data["updated_at"] = datetime.now().isoformat()

            result = (
                self.supabase_client.table("archon_tasks")
                .insert(task_data)
                .execute()
            )

            if not result.data:
                raise ValueError("Insert returned no data")

            logger.info(f"Created task {result.data[0]['id']}")
            return result.data[0]

        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise

    async def list_tasks(
        self,
        project_id: str | None = None,
        status: str | None = None,
        assignee: str | None = None,
        include_archived: bool = False,
        exclude_large_fields: bool = False,
        search_query: str | None = None,
        order_by: str = "task_order"
    ) -> list[dict[str, Any]]:
        """List tasks with various filters."""
        try:
            if exclude_large_fields:
                query = self.supabase_client.table("archon_tasks").select(
                    "id, project_id, parent_task_id, title, description, "
                    "status, assignee, task_order, priority, feature, archived, "
                    "archived_at, archived_by, created_at, updated_at, "
                    "sources, code_examples"
                )
            else:
                query = self.supabase_client.table("archon_tasks").select("*")

            if project_id:
                query = query.eq("project_id", project_id)
            if status:
                query = query.eq("status", status)
            if assignee:
                query = query.eq("assignee", assignee)

            if not include_archived:
                query = query.or_("archived.is.null,archived.is.false")

            if search_query:
                search_terms = search_query.lower().split()
                if len(search_terms) == 1:
                    term = search_terms[0]
                    query = query.or_(
                        f"title.ilike.%{term}%,"
                        f"description.ilike.%{term}%,"
                        f"feature.ilike.%{term}%"
                    )
                else:
                    full_query = search_query.lower()
                    query = query.or_(
                        f"title.ilike.%{full_query}%,"
                        f"description.ilike.%{full_query}%,"
                        f"feature.ilike.%{full_query}%"
                    )

            query = query.order(order_by, desc=False).order("created_at", desc=False)

            result = query.execute()
            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            raise

    async def get_task_by_id(self, task_id: str) -> dict[str, Any] | None:
        """Get a specific task by ID."""
        try:
            result = (
                self.supabase_client.table("archon_tasks")
                .select("*")
                .eq("id", task_id)
                .maybe_single()
                .execute()
            )

            return result.data if result and result.data else None

        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            raise

    async def update_task(
        self,
        task_id: str,
        update_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update a task with specified fields."""
        try:
            update_data["updated_at"] = datetime.now().isoformat()

            result = (
                self.supabase_client.table("archon_tasks")
                .update(update_data)
                .eq("id", task_id)
                .execute()
            )

            if result.data and len(result.data) > 0:
                return result.data[0]

            return None

        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            raise

    async def delete_task(self, task_id: str) -> bool:
        """Delete a task (hard delete)."""
        try:
            result = (
                self.supabase_client.table("archon_tasks")
                .delete()
                .eq("id", task_id)
                .execute()
            )

            deleted = len(result.data) > 0 if result.data else False
            if deleted:
                logger.info(f"Deleted task {task_id}")
            return deleted

        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            raise

    async def archive_task(
        self,
        task_id: str,
        archived_by: str = "system"
    ) -> dict[str, Any] | None:
        """Archive a task (soft delete)."""
        try:
            archive_data = {
                "archived": True,
                "archived_at": datetime.now().isoformat(),
                "archived_by": archived_by,
                "updated_at": datetime.now().isoformat(),
            }

            result = (
                self.supabase_client.table("archon_tasks")
                .update(archive_data)
                .eq("id", task_id)
                .execute()
            )

            if result.data and len(result.data) > 0:
                logger.info(f"Archived task {task_id}")
                return result.data[0]

            return None

        except Exception as e:
            logger.error(f"Failed to archive task {task_id}: {e}")
            raise

    async def get_tasks_by_project_and_status(
        self,
        project_id: str,
        status: str,
        task_order_gte: int | None = None
    ) -> list[dict[str, Any]]:
        """Get tasks filtered by project, status, and optionally task_order."""
        try:
            query = (
                self.supabase_client.table("archon_tasks")
                .select("id, task_order")
                .eq("project_id", project_id)
                .eq("status", status)
            )

            if task_order_gte is not None:
                query = query.gte("task_order", task_order_gte)

            result = query.execute()
            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to get tasks by project and status: {e}")
            raise

    async def get_task_counts_by_project(self, project_id: str) -> dict[str, int]:
        """Get task counts grouped by status for a project."""
        try:
            result = (
                self.supabase_client.table("archon_tasks")
                .select("status")
                .eq("project_id", project_id)
                .or_("archived.is.null,archived.is.false")
                .execute()
            )

            counts = {"todo": 0, "doing": 0, "review": 0, "done": 0}
            if result.data:
                for task in result.data:
                    status = task.get("status")
                    if status in counts:
                        counts[status] += 1

            return counts

        except Exception as e:
            logger.error(f"Failed to get task counts for project {project_id}: {e}")
            raise

    async def get_all_project_task_counts(self) -> dict[str, dict[str, int]]:
        """Get task counts for all projects in a single query."""
        try:
            result = (
                self.supabase_client.table("archon_tasks")
                .select("project_id, status")
                .or_("archived.is.null,archived.is.false")
                .execute()
            )

            if not result.data:
                return {}

            counts_by_project: dict[str, dict[str, int]] = {}

            for task in result.data:
                project_id = task.get("project_id")
                status = task.get("status")

                if not project_id or not status:
                    continue

                if project_id not in counts_by_project:
                    counts_by_project[project_id] = {
                        "todo": 0,
                        "doing": 0,
                        "review": 0,
                        "done": 0
                    }

                if status in ["todo", "doing", "review", "done"]:
                    counts_by_project[project_id][status] += 1

            return counts_by_project

        except Exception as e:
            logger.error(f"Failed to get all project task counts: {e}")
            raise

    # ========================================================================
    # 7. SOURCE OPERATIONS
    # ========================================================================

    async def list_sources(
        self,
        knowledge_type: str | None = None
    ) -> list[dict[str, Any]]:
        """List all sources, optionally filtered by knowledge type."""
        try:
            query = self.supabase_client.table("archon_sources").select("*")

            if knowledge_type:
                query = query.contains("metadata", {"knowledge_type": knowledge_type})

            result = query.execute()
            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to list sources: {e}")
            raise

    async def list_sources_with_pagination(
        self,
        knowledge_type: str | None = None,
        search_query: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str = "updated_at",
        desc: bool = True,
        select_fields: str | None = None
    ) -> tuple[list[dict[str, Any]], int]:
        """List sources with search, filtering, and pagination."""
        try:
            # Build select fields
            fields = select_fields if select_fields else "*"

            # Build main query
            query = self.supabase_client.table("archon_sources").select(fields)

            # Apply knowledge type filter
            if knowledge_type:
                query = query.contains("metadata", {"knowledge_type": knowledge_type})

            # Apply search filter
            if search_query:
                search_pattern = f"%{search_query}%"
                query = query.or_(
                    f"title.ilike.{search_pattern},summary.ilike.{search_pattern}"
                )

            # Build count query with same filters
            count_query = self.supabase_client.table("archon_sources").select("*", count="exact", head=True)

            if knowledge_type:
                count_query = count_query.contains("metadata", {"knowledge_type": knowledge_type})

            if search_query:
                search_pattern = f"%{search_query}%"
                count_query = count_query.or_(
                    f"title.ilike.{search_pattern},summary.ilike.{search_pattern}"
                )

            # Get total count
            count_result = count_query.execute()
            total = count_result.count if hasattr(count_result, "count") else 0

            # Apply pagination
            if limit is not None and offset is not None:
                end_idx = offset + limit - 1
                query = query.range(offset, end_idx)

            # Apply ordering
            query = query.order(order_by, desc=desc)

            # Execute main query
            result = query.execute()
            sources = result.data if result.data else []

            return sources, total

        except Exception as e:
            logger.error(f"Failed to list sources with pagination: {e}")
            raise

    async def get_source_by_id(self, source_id: str) -> dict[str, Any] | None:
        """Get a specific source by ID."""
        try:
            result = (
                self.supabase_client.table("archon_sources")
                .select("*")
                .eq("source_id", source_id)
                .maybe_single()
                .execute()
            )

            return result.data if result and result.data else None

        except Exception as e:
            logger.error(f"Failed to get source {source_id}: {e}")
            raise

    async def upsert_source(self, source_data: dict[str, Any]) -> dict[str, Any]:
        """Insert or update a source."""
        try:
            result = (
                self.supabase_client.table("archon_sources")
                .upsert(source_data)
                .execute()
            )

            if not result.data:
                raise ValueError("Upsert returned no data")

            return result.data[0]

        except Exception as e:
            logger.error(f"Failed to upsert source: {e}")
            raise

    async def update_source_metadata(
        self,
        source_id: str,
        metadata: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update source metadata."""
        try:
            # Get existing metadata
            existing = await self.get_source_by_id(source_id)
            if not existing:
                return None

            current_metadata = existing.get("metadata", {})
            merged_metadata = {**current_metadata, **metadata}

            result = (
                self.supabase_client.table("archon_sources")
                .update({"metadata": merged_metadata})
                .eq("source_id", source_id)
                .execute()
            )

            if result.data and len(result.data) > 0:
                return result.data[0]

            return None

        except Exception as e:
            logger.error(f"Failed to update source metadata for {source_id}: {e}")
            raise

    async def delete_source(self, source_id: str) -> bool:
        """
        Delete a source and explicitly delete all related records.

        This method explicitly deletes related records before deleting the source
        to ensure cleanup happens even if CASCADE DELETE constraints are not
        properly configured in the database.
        """
        try:
            # Step 1: Explicitly delete related crawled_pages
            # This prevents orphaned records if CASCADE DELETE is not working
            crawled_pages_deleted = await self.delete_crawled_pages_by_source(source_id)
            logger.info(f"Explicitly deleted {crawled_pages_deleted} crawled pages for source {source_id}")

            # Step 2: Explicitly delete related code_examples
            code_examples_deleted = await self.delete_code_examples_by_source(source_id)
            logger.info(f"Explicitly deleted {code_examples_deleted} code examples for source {source_id}")

            # Step 3: Delete the source itself
            result = (
                self.supabase_client.table("archon_sources")
                .delete()
                .eq("source_id", source_id)
                .execute()
            )

            deleted = len(result.data) > 0 if result.data else False
            if deleted:
                logger.info(
                    f"Deleted source {source_id} and all related records "
                    f"({crawled_pages_deleted} pages, {code_examples_deleted} code examples)"
                )
            return deleted

        except Exception as e:
            logger.error(f"Failed to delete source {source_id}: {e}")
            raise

    # ========================================================================
    # 8. CRAWLED PAGES OPERATIONS
    # ========================================================================

    async def get_crawled_page_by_url(
        self,
        url: str,
        source_id: str | None = None
    ) -> dict[str, Any] | None:
        """Get a crawled page by URL."""
        try:
            query = (
                self.supabase_client.table("archon_crawled_pages")
                .select("*")
                .eq("url", url)
            )

            if source_id:
                query = query.eq("source_id", source_id)

            result = query.maybe_single().execute()
            return result.data if result and result.data else None

        except Exception as e:
            logger.error(f"Failed to get crawled page by URL {url}: {e}")
            raise

    async def insert_crawled_page(
        self,
        page_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Insert a new crawled page."""
        try:
            result = (
                self.supabase_client.table("archon_crawled_pages")
                .insert(page_data)
                .execute()
            )

            if not result.data:
                raise ValueError("Insert returned no data")

            return result.data[0]

        except Exception as e:
            logger.error(f"Failed to insert crawled page: {e}")
            raise

    async def upsert_crawled_page(
        self,
        page_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Insert or update a crawled page."""
        try:
            result = (
                self.supabase_client.table("archon_crawled_pages")
                .upsert(page_data)
                .execute()
            )

            if not result.data:
                raise ValueError("Upsert returned no data")

            return result.data[0]

        except Exception as e:
            logger.error(f"Failed to upsert crawled page: {e}")
            raise

    async def delete_crawled_pages_by_source(self, source_id: str) -> int:
        """Delete all crawled pages for a source."""
        try:
            result = (
                self.supabase_client.table("archon_crawled_pages")
                .delete()
                .eq("source_id", source_id)
                .execute()
            )

            deleted_count = len(result.data) if result.data else 0
            logger.info(f"Deleted {deleted_count} crawled pages for source {source_id}")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to delete crawled pages by source {source_id}: {e}")
            raise

    async def list_crawled_pages_by_source(
        self,
        source_id: str,
        limit: int | None = None,
        offset: int | None = None
    ) -> list[dict[str, Any]]:
        """List crawled pages for a source."""
        try:
            query = (
                self.supabase_client.table("archon_crawled_pages")
                .select("*")
                .eq("source_id", source_id)
                .order("created_at", desc=True)
            )

            if limit is not None:
                query = query.limit(limit)
            if offset is not None:
                query = query.offset(offset)

            result = query.execute()
            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to list crawled pages for source {source_id}: {e}")
            raise

    async def delete_crawled_pages_by_urls(self, urls: list[str]) -> int:
        """Delete crawled pages by a list of URLs."""
        try:
            if not urls:
                return 0

            result = (
                self.supabase_client.table("archon_crawled_pages")
                .delete()
                .in_("url", urls)
                .execute()
            )

            deleted_count = len(result.data) if result.data else 0
            logger.info(f"Deleted {deleted_count} crawled pages by URL list")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to delete crawled pages by URLs: {e}")
            raise

    async def insert_crawled_pages_batch(
        self,
        pages: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Insert multiple crawled pages in a batch."""
        try:
            if not pages:
                return []

            result = (
                self.supabase_client.table("archon_crawled_pages")
                .insert(pages)
                .execute()
            )

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to batch insert {len(pages)} crawled pages: {e}")
            raise

    async def get_first_url_by_sources(
        self,
        source_ids: list[str]
    ) -> dict[str, str]:
        """Get the first (oldest) URL for each source."""
        try:
            if not source_ids:
                return {}

            # Get all pages for these sources ordered by created_at ascending
            result = (
                self.supabase_client.table("archon_crawled_pages")
                .select("source_id, url")
                .in_("source_id", source_ids)
                .order("created_at", desc=False)
                .execute()
            )

            urls = {}

            # Group by source_id, keeping first URL for each
            for item in result.data or []:
                source_id = item["source_id"]
                if source_id not in urls:
                    urls[source_id] = item["url"]

            return urls

        except Exception as e:
            logger.error(f"Failed to get first URLs for sources: {e}")
            raise

    # ========================================================================
    # 9. DOCUMENT VERSION OPERATIONS
    # ========================================================================

    async def create_document_version(
        self,
        version_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a new document version."""
        try:
            if "created_at" not in version_data:
                version_data["created_at"] = datetime.now().isoformat()

            result = (
                self.supabase_client.table("archon_document_versions")
                .insert(version_data)
                .execute()
            )

            if not result.data:
                raise ValueError("Insert returned no data")

            logger.info(f"Created document version {result.data[0]['id']}")
            return result.data[0]

        except Exception as e:
            logger.error(f"Failed to create document version: {e}")
            raise

    async def list_document_versions(
        self,
        project_id: str,
        limit: int | None = None
    ) -> list[dict[str, Any]]:
        """List document versions for a project."""
        try:
            query = (
                self.supabase_client.table("archon_document_versions")
                .select("*")
                .eq("project_id", project_id)
                .order("created_at", desc=True)
            )

            if limit is not None:
                query = query.limit(limit)

            result = query.execute()
            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to list document versions for project {project_id}: {e}")
            raise

    async def get_document_version_by_id(
        self,
        version_id: str
    ) -> dict[str, Any] | None:
        """Get a specific document version by ID."""
        try:
            result = (
                self.supabase_client.table("archon_document_versions")
                .select("*")
                .eq("id", version_id)
                .maybe_single()
                .execute()
            )

            return result.data if result and result.data else None

        except Exception as e:
            logger.error(f"Failed to get document version {version_id}: {e}")
            raise

    async def delete_document_version(self, version_id: str) -> bool:
        """Delete a document version."""
        try:
            result = (
                self.supabase_client.table("archon_document_versions")
                .delete()
                .eq("id", version_id)
                .execute()
            )

            deleted = len(result.data) > 0 if result.data else False
            if deleted:
                logger.info(f"Deleted document version {version_id}")
            return deleted

        except Exception as e:
            logger.error(f"Failed to delete document version {version_id}: {e}")
            raise

    # ========================================================================
    # 10. PROJECT SOURCE LINKING OPERATIONS
    # ========================================================================

    async def link_project_source(
        self,
        project_id: str,
        source_id: str,
        notes: str | None = None
    ) -> dict[str, Any]:
        """Link a source to a project."""
        try:
            link_data = {
                "project_id": project_id,
                "source_id": source_id,
            }
            if notes:
                link_data["notes"] = notes

            result = (
                self.supabase_client.table("archon_project_sources")
                .insert(link_data)
                .execute()
            )

            if not result.data:
                raise ValueError("Insert returned no data")

            logger.info(f"Linked source {source_id} to project {project_id}")
            return result.data[0]

        except Exception as e:
            logger.error(f"Failed to link source {source_id} to project {project_id}: {e}")
            raise

    async def unlink_project_source(
        self,
        project_id: str,
        source_id: str
    ) -> bool:
        """Unlink a source from a project."""
        try:
            result = (
                self.supabase_client.table("archon_project_sources")
                .delete()
                .eq("project_id", project_id)
                .eq("source_id", source_id)
                .execute()
            )

            unlinked = len(result.data) > 0 if result.data else False
            if unlinked:
                logger.info(f"Unlinked source {source_id} from project {project_id}")
            return unlinked

        except Exception as e:
            logger.error(f"Failed to unlink source {source_id} from project {project_id}: {e}")
            raise

    async def list_project_sources(
        self,
        project_id: str,
        notes_filter: str | None = None
    ) -> list[dict[str, Any]]:
        """List sources linked to a project."""
        try:
            query = (
                self.supabase_client.table("archon_project_sources")
                .select("source_id, notes")
                .eq("project_id", project_id)
            )

            if notes_filter:
                query = query.eq("notes", notes_filter)

            result = query.execute()
            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to list project sources for {project_id}: {e}")
            raise

    async def get_sources_for_project(
        self,
        project_id: str,
        source_ids: list[str]
    ) -> list[dict[str, Any]]:
        """Get full source objects for a list of source IDs."""
        try:
            if not source_ids:
                return []

            result = (
                self.supabase_client.table("archon_sources")
                .select("*")
                .in_("source_id", source_ids)
                .execute()
            )

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to get sources for project {project_id}: {e}")
            raise

    # ========================================================================
    # 11. RPC OPERATIONS
    # ========================================================================

    async def execute_rpc(
        self,
        function_name: str,
        params: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Execute a database RPC (Remote Procedure Call) function."""
        try:
            result = self.supabase_client.rpc(function_name, params).execute()

            if result and result.data:
                return result.data
            return []

        except Exception as e:
            logger.error(f"Failed to execute RPC {function_name}: {e}")
            raise

    # ========================================================================
    # 12. PROMPT OPERATIONS
    # ========================================================================

    async def get_all_prompts(self) -> list[dict[str, Any]]:
        """Retrieve all prompts from the archon_prompts table."""
        try:
            result = (
                self.supabase_client.table("archon_prompts")
                .select("*")
                .execute()
            )

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to get all prompts: {e}")
            raise

    # ========================================================================
    # 13. TABLE COUNT OPERATIONS
    # ========================================================================

    async def get_table_count(self, table_name: str) -> int:
        """Get the count of records in a specified table."""
        try:
            result = (
                self.supabase_client.table(table_name)
                .select("id", count="exact")
                .execute()
            )

            return result.count if result.count is not None else 0

        except Exception as e:
            logger.error(f"Failed to get count for table {table_name}: {e}")
            raise

    # ========================================================================
    # 14. MIGRATION OPERATIONS
    # ========================================================================

    async def get_applied_migrations(self) -> list[dict[str, Any]]:
        """Retrieve all applied migrations from archon_migrations table."""
        try:
            result = (
                self.supabase_client.table("archon_migrations")
                .select("*")
                .order("applied_at", desc=True)
                .execute()
            )

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            raise

    async def migration_exists(self, migration_name: str) -> bool:
        """Check if a migration has been applied."""
        try:
            result = (
                self.supabase_client.table("archon_migrations")
                .select("id")
                .eq("migration_name", migration_name)
                .maybe_single()
                .execute()
            )

            return result.data is not None

        except Exception as e:
            logger.error(f"Failed to check migration existence for {migration_name}: {e}")
            raise

    async def record_migration(self, migration_data: dict[str, Any]) -> dict[str, Any]:
        """Record a migration as applied."""
        try:
            result = (
                self.supabase_client.table("archon_migrations")
                .insert(migration_data)
                .execute()
            )

            if not result.data:
                raise ValueError("Insert returned no data")

            logger.info(f"Recorded migration {migration_data.get('migration_name')}")
            return result.data[0]

        except Exception as e:
            logger.error(f"Failed to record migration: {e}")
            raise
