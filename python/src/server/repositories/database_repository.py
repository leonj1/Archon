"""
Database Repository Interface

Defines the contract for database operations to enable dependency injection
and decouple service classes from direct database access.

This interface organizes database operations into 14 domains:
1. Page Metadata Operations
2. Document Search Operations
3. Code Examples Operations
4. Settings Operations
5. Project Operations
6. Task Operations
7. Source Operations
8. Crawled Pages Operations
9. Document Version Operations
10. Project Source Linking Operations
11. RPC Operations
12. Prompt Operations
13. Table Count Operations
14. Migration Operations
"""

from abc import ABC, abstractmethod
from typing import Any


class DatabaseRepository(ABC):
    """
    Abstract interface for database operations.

    This interface defines all database operations needed by service classes,
    enabling dependency injection and testability.
    """

    # ========================================================================
    # 1. PAGE METADATA OPERATIONS
    # ========================================================================

    @abstractmethod
    async def get_page_metadata_by_id(self, page_id: str) -> dict[str, Any] | None:
        """
        Retrieve page metadata by page ID.

        Args:
            page_id: The unique identifier of the page

        Returns:
            Page metadata dict if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_page_metadata_by_url(self, url: str) -> dict[str, Any] | None:
        """
        Retrieve page metadata by URL.

        Args:
            url: The URL of the page

        Returns:
            Page metadata dict if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_pages_by_source(
        self,
        source_id: str,
        limit: int | None = None,
        offset: int | None = None
    ) -> list[dict[str, Any]]:
        """
        List all pages for a given source.

        Args:
            source_id: The source identifier
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of page metadata dictionaries
        """
        pass

    @abstractmethod
    async def get_page_count_by_source(self, source_id: str) -> int:
        """
        Get the count of pages for a source.

        Args:
            source_id: The source identifier

        Returns:
            Number of pages for the source
        """
        pass

    @abstractmethod
    async def upsert_page_metadata_batch(
        self,
        pages: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Insert or update multiple page metadata records in a batch.

        Args:
            pages: List of page metadata dictionaries

        Returns:
            List of upserted page metadata records with IDs
        """
        pass

    @abstractmethod
    async def update_page_chunk_count(self, page_id: str, chunk_count: int) -> dict[str, Any] | None:
        """
        Update the chunk_count field for a page after chunking is complete.

        Args:
            page_id: The UUID of the page to update
            chunk_count: Number of chunks created from this page

        Returns:
            Updated page metadata dict if successful, None otherwise
        """
        pass

    # ========================================================================
    # 2. DOCUMENT SEARCH OPERATIONS
    # ========================================================================

    @abstractmethod
    async def search_documents_vector(
        self,
        query_embedding: list[float],
        match_count: int = 5,
        filter_metadata: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Perform vector similarity search on documents.

        Args:
            query_embedding: The embedding vector for the query
            match_count: Maximum number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of matching documents with similarity scores
        """
        pass

    @abstractmethod
    async def search_documents_hybrid(
        self,
        query: str,
        query_embedding: list[float],
        match_count: int = 5,
        filter_metadata: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Perform hybrid search combining vector and full-text search.

        Args:
            query: The search query text
            query_embedding: The embedding vector for the query
            match_count: Maximum number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of matching documents with combined scores
        """
        pass

    @abstractmethod
    async def get_documents_by_source(
        self,
        source_id: str,
        limit: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Get all document chunks for a source.

        Args:
            source_id: The source identifier
            limit: Maximum number of documents to return

        Returns:
            List of document dictionaries
        """
        pass

    @abstractmethod
    async def get_document_by_id(self, document_id: str) -> dict[str, Any] | None:
        """
        Get a specific document by ID.

        Args:
            document_id: The document identifier

        Returns:
            Document dict if found, None otherwise
        """
        pass

    @abstractmethod
    async def insert_document(self, document_data: dict[str, Any]) -> dict[str, Any]:
        """
        Insert a new document chunk.

        Args:
            document_data: Dictionary containing document fields

        Returns:
            The inserted document with ID
        """
        pass

    @abstractmethod
    async def insert_documents_batch(
        self,
        documents: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Insert multiple document chunks in a batch.

        Args:
            documents: List of document data dictionaries

        Returns:
            List of inserted documents with IDs
        """
        pass

    @abstractmethod
    async def delete_documents_by_source(self, source_id: str) -> int:
        """
        Delete all documents for a source.

        Args:
            source_id: The source identifier

        Returns:
            Number of documents deleted
        """
        pass

    # ========================================================================
    # 3. CODE EXAMPLES OPERATIONS
    # ========================================================================

    @abstractmethod
    async def search_code_examples(
        self,
        query_embedding: list[float],
        match_count: int = 10,
        filter_metadata: dict[str, Any] | None = None,
        source_id: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Search for code examples using vector similarity.

        Args:
            query_embedding: The embedding vector for the query
            match_count: Maximum number of results to return
            filter_metadata: Optional metadata filters
            source_id: Optional source ID to filter results

        Returns:
            List of matching code examples
        """
        pass

    @abstractmethod
    async def get_code_examples_by_source(
        self,
        source_id: str,
        limit: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Get all code examples for a source.

        Args:
            source_id: The source identifier
            limit: Maximum number of examples to return

        Returns:
            List of code example dictionaries
        """
        pass

    @abstractmethod
    async def get_code_example_count_by_source(self, source_id: str) -> int:
        """
        Get the count of code examples for a source.

        Args:
            source_id: The source identifier

        Returns:
            Number of code examples for the source
        """
        pass

    @abstractmethod
    async def insert_code_example(
        self,
        code_example_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Insert a new code example.

        Args:
            code_example_data: Dictionary containing code example fields

        Returns:
            The inserted code example with ID
        """
        pass

    @abstractmethod
    async def insert_code_examples_batch(
        self,
        code_examples: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Insert multiple code examples in a batch.

        Args:
            code_examples: List of code example data dictionaries

        Returns:
            List of inserted code examples with IDs
        """
        pass

    @abstractmethod
    async def delete_code_examples_by_source(self, source_id: str) -> int:
        """
        Delete all code examples for a source.

        Args:
            source_id: The source identifier

        Returns:
            Number of code examples deleted
        """
        pass

    @abstractmethod
    async def delete_code_examples_by_url(self, url: str) -> int:
        """
        Delete all code examples for a specific URL.

        Args:
            url: The URL to delete code examples for

        Returns:
            Number of code examples deleted
        """
        pass

    # ========================================================================
    # 4. SETTINGS OPERATIONS
    # ========================================================================

    @abstractmethod
    async def get_settings_by_key(self, key: str) -> Any | None:
        """
        Retrieve a setting value by its key.

        Args:
            key: The setting key

        Returns:
            The setting value if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_all_settings(self) -> dict[str, Any]:
        """
        Retrieve all settings as a dictionary.

        Returns:
            Dictionary of all settings
        """
        pass

    @abstractmethod
    async def upsert_setting(self, key: str, value: Any) -> dict[str, Any]:
        """
        Insert or update a setting.

        Args:
            key: The setting key
            value: The setting value

        Returns:
            The upserted setting record
        """
        pass

    @abstractmethod
    async def delete_setting(self, key: str) -> bool:
        """
        Delete a setting by key.

        Args:
            key: The setting key

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def get_all_setting_records(self) -> list[dict[str, Any]]:
        """
        Retrieve all setting records with full details.

        Returns:
            List of setting dictionaries with all fields (key, value, encrypted_value,
            is_encrypted, category, description)
        """
        pass

    @abstractmethod
    async def get_setting_records_by_category(self, category: str) -> list[dict[str, Any]]:
        """
        Retrieve setting records filtered by category.

        Args:
            category: The category to filter by

        Returns:
            List of setting dictionaries with all fields
        """
        pass

    @abstractmethod
    async def upsert_setting_record(self, setting_data: dict[str, Any]) -> dict[str, Any]:
        """
        Insert or update a full setting record.

        Args:
            setting_data: Dictionary with setting fields (key, value, encrypted_value,
                         is_encrypted, category, description)

        Returns:
            The upserted setting record
        """
        pass

    # ========================================================================
    # 5. PROJECT OPERATIONS
    # ========================================================================

    @abstractmethod
    async def create_project(self, project_data: dict[str, Any]) -> dict[str, Any]:
        """
        Create a new project.

        Args:
            project_data: Dictionary containing project fields

        Returns:
            The created project with ID
        """
        pass

    @abstractmethod
    async def list_projects(
        self,
        include_content: bool = True,
        order_by: str = "created_at",
        desc: bool = True
    ) -> list[dict[str, Any]]:
        """
        List all projects.

        Args:
            include_content: If True, includes docs, features, data fields
            order_by: Field to order by
            desc: If True, descending order

        Returns:
            List of project dictionaries
        """
        pass

    @abstractmethod
    async def get_project_by_id(self, project_id: str) -> dict[str, Any] | None:
        """
        Get a specific project by ID.

        Args:
            project_id: The project identifier

        Returns:
            Project dict if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_project(
        self,
        project_id: str,
        update_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """
        Update a project with specified fields.

        Args:
            project_id: The project identifier
            update_data: Dictionary of fields to update

        Returns:
            Updated project dict if successful, None otherwise
        """
        pass

    @abstractmethod
    async def delete_project(self, project_id: str) -> bool:
        """
        Delete a project.

        Args:
            project_id: The project identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def unpin_all_projects_except(self, project_id: str) -> int:
        """
        Unpin all projects except the specified one.

        Args:
            project_id: The project to keep pinned

        Returns:
            Number of projects unpinned
        """
        pass

    @abstractmethod
    async def get_project_features(self, project_id: str) -> list[dict[str, Any]]:
        """
        Get features from a project's features JSONB field.

        Args:
            project_id: The project identifier

        Returns:
            List of feature dictionaries
        """
        pass

    # ========================================================================
    # 6. TASK OPERATIONS
    # ========================================================================

    @abstractmethod
    async def create_task(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Create a new task.

        Args:
            task_data: Dictionary containing task fields

        Returns:
            The created task with ID
        """
        pass

    @abstractmethod
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
        """
        List tasks with various filters.

        Args:
            project_id: Filter by project
            status: Filter by status
            assignee: Filter by assignee
            include_archived: Include archived tasks
            exclude_large_fields: Exclude sources and code_examples
            search_query: Keyword search in title/description/feature
            order_by: Field to order by

        Returns:
            List of task dictionaries
        """
        pass

    @abstractmethod
    async def get_task_by_id(self, task_id: str) -> dict[str, Any] | None:
        """
        Get a specific task by ID.

        Args:
            task_id: The task identifier

        Returns:
            Task dict if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_task(
        self,
        task_id: str,
        update_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """
        Update a task with specified fields.

        Args:
            task_id: The task identifier
            update_data: Dictionary of fields to update

        Returns:
            Updated task dict if successful, None otherwise
        """
        pass

    @abstractmethod
    async def delete_task(self, task_id: str) -> bool:
        """
        Delete a task (hard delete).

        Args:
            task_id: The task identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def archive_task(
        self,
        task_id: str,
        archived_by: str = "system"
    ) -> dict[str, Any] | None:
        """
        Archive a task (soft delete).

        Args:
            task_id: The task identifier
            archived_by: Who archived the task

        Returns:
            Updated task dict if successful, None otherwise
        """
        pass

    @abstractmethod
    async def get_tasks_by_project_and_status(
        self,
        project_id: str,
        status: str,
        task_order_gte: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Get tasks filtered by project, status, and optionally task_order.

        Args:
            project_id: The project identifier
            status: The task status
            task_order_gte: Minimum task_order value (greater than or equal)

        Returns:
            List of task dictionaries
        """
        pass

    @abstractmethod
    async def get_task_counts_by_project(self, project_id: str) -> dict[str, int]:
        """
        Get task counts grouped by status for a project.

        Args:
            project_id: The project identifier

        Returns:
            Dictionary mapping status to count
        """
        pass

    @abstractmethod
    async def get_all_project_task_counts(self) -> dict[str, dict[str, int]]:
        """
        Get task counts for all projects in a single query.

        Returns:
            Dictionary mapping project_id to status counts
        """
        pass

    # ========================================================================
    # 7. SOURCE OPERATIONS
    # ========================================================================

    @abstractmethod
    async def list_sources(
        self,
        knowledge_type: str | None = None
    ) -> list[dict[str, Any]]:
        """
        List all sources, optionally filtered by knowledge type.

        Args:
            knowledge_type: Optional knowledge type filter

        Returns:
            List of source dictionaries
        """
        pass

    @abstractmethod
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
        """
        List sources with search, filtering, and pagination.

        Args:
            knowledge_type: Optional knowledge type filter
            search_query: Optional text search in title and summary
            limit: Maximum number of results
            offset: Number of results to skip
            order_by: Field to order by
            desc: If True, descending order
            select_fields: Comma-separated fields to select (default: all fields)

        Returns:
            Tuple of (list of source dictionaries, total count)
        """
        pass

    @abstractmethod
    async def get_source_by_id(self, source_id: str) -> dict[str, Any] | None:
        """
        Get a specific source by ID.

        Args:
            source_id: The source identifier

        Returns:
            Source dict if found, None otherwise
        """
        pass

    @abstractmethod
    async def upsert_source(self, source_data: dict[str, Any]) -> dict[str, Any]:
        """
        Insert or update a source.

        Args:
            source_data: Dictionary containing source fields

        Returns:
            The upserted source record
        """
        pass

    @abstractmethod
    async def update_source_metadata(
        self,
        source_id: str,
        metadata: dict[str, Any]
    ) -> dict[str, Any] | None:
        """
        Update source metadata.

        Args:
            source_id: The source identifier
            metadata: Metadata dictionary to merge

        Returns:
            Updated source dict if successful, None otherwise
        """
        pass

    @abstractmethod
    async def delete_source(self, source_id: str) -> bool:
        """
        Delete a source (CASCADE deletes related records).

        Args:
            source_id: The source identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    # ========================================================================
    # 8. CRAWLED PAGES OPERATIONS
    # ========================================================================

    @abstractmethod
    async def get_crawled_page_by_url(
        self,
        url: str,
        source_id: str | None = None
    ) -> dict[str, Any] | None:
        """
        Get a crawled page by URL.

        Args:
            url: The page URL
            source_id: Optional source filter

        Returns:
            Crawled page dict if found, None otherwise
        """
        pass

    @abstractmethod
    async def insert_crawled_page(
        self,
        page_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Insert a new crawled page.

        Args:
            page_data: Dictionary containing page fields

        Returns:
            The inserted page with ID
        """
        pass

    @abstractmethod
    async def upsert_crawled_page(
        self,
        page_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Insert or update a crawled page.

        Args:
            page_data: Dictionary containing page fields

        Returns:
            The upserted page record
        """
        pass

    @abstractmethod
    async def delete_crawled_pages_by_source(self, source_id: str) -> int:
        """
        Delete all crawled pages for a source.

        Args:
            source_id: The source identifier

        Returns:
            Number of pages deleted
        """
        pass

    @abstractmethod
    async def list_crawled_pages_by_source(
        self,
        source_id: str,
        limit: int | None = None,
        offset: int | None = None
    ) -> list[dict[str, Any]]:
        """
        List crawled pages for a source.

        Args:
            source_id: The source identifier
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of crawled page dictionaries
        """
        pass

    @abstractmethod
    async def delete_crawled_pages_by_urls(self, urls: list[str]) -> int:
        """
        Delete crawled pages by a list of URLs.

        Args:
            urls: List of URLs to delete

        Returns:
            Number of pages deleted
        """
        pass

    @abstractmethod
    async def insert_crawled_pages_batch(
        self,
        pages: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Insert multiple crawled pages in a batch.

        Args:
            pages: List of page data dictionaries

        Returns:
            List of inserted pages with IDs
        """
        pass

    @abstractmethod
    async def get_first_url_by_sources(
        self,
        source_ids: list[str]
    ) -> dict[str, str]:
        """
        Get the first (oldest) URL for each source.

        Args:
            source_ids: List of source identifiers

        Returns:
            Dictionary mapping source_id to first URL
        """
        pass

    # ========================================================================
    # 9. DOCUMENT VERSION OPERATIONS
    # ========================================================================

    @abstractmethod
    async def create_document_version(
        self,
        version_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Create a new document version.

        Args:
            version_data: Dictionary containing version fields

        Returns:
            The created version with ID
        """
        pass

    @abstractmethod
    async def list_document_versions(
        self,
        project_id: str,
        limit: int | None = None
    ) -> list[dict[str, Any]]:
        """
        List document versions for a project.

        Args:
            project_id: The project identifier
            limit: Maximum number of versions to return

        Returns:
            List of version dictionaries ordered by created_at desc
        """
        pass

    @abstractmethod
    async def get_document_version_by_id(
        self,
        version_id: str
    ) -> dict[str, Any] | None:
        """
        Get a specific document version by ID.

        Args:
            version_id: The version identifier

        Returns:
            Version dict if found, None otherwise
        """
        pass

    @abstractmethod
    async def delete_document_version(self, version_id: str) -> bool:
        """
        Delete a document version.

        Args:
            version_id: The version identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    # ========================================================================
    # 10. PROJECT SOURCE LINKING OPERATIONS
    # ========================================================================

    @abstractmethod
    async def link_project_source(
        self,
        project_id: str,
        source_id: str,
        notes: str | None = None
    ) -> dict[str, Any]:
        """
        Link a source to a project.

        Args:
            project_id: The project identifier
            source_id: The source identifier
            notes: Optional notes about the link (e.g., "technical", "business")

        Returns:
            The created link record
        """
        pass

    @abstractmethod
    async def unlink_project_source(
        self,
        project_id: str,
        source_id: str
    ) -> bool:
        """
        Unlink a source from a project.

        Args:
            project_id: The project identifier
            source_id: The source identifier

        Returns:
            True if unlinked, False if link not found
        """
        pass

    @abstractmethod
    async def list_project_sources(
        self,
        project_id: str,
        notes_filter: str | None = None
    ) -> list[dict[str, Any]]:
        """
        List sources linked to a project.

        Args:
            project_id: The project identifier
            notes_filter: Optional filter by notes field

        Returns:
            List of source link dictionaries
        """
        pass

    @abstractmethod
    async def get_sources_for_project(
        self,
        project_id: str,
        source_ids: list[str]
    ) -> list[dict[str, Any]]:
        """
        Get full source objects for a list of source IDs.

        Args:
            project_id: The project identifier (for context)
            source_ids: List of source identifiers

        Returns:
            List of source dictionaries
        """
        pass

    # ========================================================================
    # 11. RPC OPERATIONS
    # ========================================================================

    @abstractmethod
    async def execute_rpc(
        self,
        function_name: str,
        params: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Execute a database RPC (Remote Procedure Call) function.

        Args:
            function_name: Name of the RPC function to execute
            params: Parameters to pass to the RPC function

        Returns:
            List of results from the RPC function
        """
        pass

    # ========================================================================
    # 12. PROMPT OPERATIONS
    # ========================================================================

    @abstractmethod
    async def get_all_prompts(self) -> list[dict[str, Any]]:
        """
        Retrieve all prompts from the archon_prompts table.

        Returns:
            List of prompt dictionaries with prompt_name and prompt fields
        """
        pass

    # ========================================================================
    # 13. TABLE COUNT OPERATIONS
    # ========================================================================

    @abstractmethod
    async def get_table_count(self, table_name: str) -> int:
        """
        Get the count of records in a specified table.

        Args:
            table_name: The name of the table to count records in

        Returns:
            Number of records in the table
        """
        pass

    # ========================================================================
    # 14. MIGRATION OPERATIONS
    # ========================================================================

    @abstractmethod
    async def get_applied_migrations(self) -> list[dict[str, Any]]:
        """
        Retrieve all applied migrations from archon_migrations table.

        Returns:
            List of migration records ordered by applied_at desc
        """
        pass

    @abstractmethod
    async def migration_exists(self, migration_name: str) -> bool:
        """
        Check if a migration has been applied.

        Args:
            migration_name: The name of the migration to check

        Returns:
            True if migration exists, False otherwise
        """
        pass

    @abstractmethod
    async def record_migration(self, migration_data: dict[str, Any]) -> dict[str, Any]:
        """
        Record a migration as applied.

        Args:
            migration_data: Dictionary containing migration fields
                (version, migration_name, checksum, applied_by)

        Returns:
            The created migration record
        """
        pass
