# Generated SQLite Repository Stub Methods

# Add these to SQLiteRepositoryStubsMixin class in sqlite_repository_stubs.py

from typing import Any, Dict, List, Optional


    # Task operations
    async def archive_task(self,
        task_id: str,
        archived_by: str = 'system'
    ) -> dict[str, Any] | None:
        """Stub implementation of archive_task."""
        return None

    async def create_task(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Stub implementation of create_task."""
        return {}

    async def delete_task(self, task_id: str) -> bool:
        """Stub implementation of delete_task."""
        return True

    async def get_task_by_id(self, task_id: str) -> dict[str, Any] | None:
        """Stub implementation of get_task_by_id."""
        return None

    async def list_tasks(self,
        project_id: str | None = None,
        status: str | None = None,
        assignee: str | None = None,
        include_archived: bool = False,
        exclude_large_fields: bool = False,
        search_query: str | None = None,
        order_by: str = 'task_order'
    ) -> list[dict[str, Any]]:
        """Stub implementation of list_tasks."""
        return []

    async def update_task(self,
        task_id: str,
        update_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Stub implementation of update_task."""
        return None


    # Document operations
    async def create_document_version(self, version_data: dict[str, Any]) -> dict[str, Any]:
        """Stub implementation of create_document_version."""
        return {}

    async def delete_document_version(self, version_id: str) -> bool:
        """Stub implementation of delete_document_version."""
        return True

    async def delete_documents_by_source(self, source_id: str) -> int:
        """Stub implementation of delete_documents_by_source."""
        return 0

    async def get_document_by_id(self, document_id: str) -> dict[str, Any] | None:
        """Stub implementation of get_document_by_id."""
        return None

    async def get_document_version_by_id(self, version_id: str) -> dict[str, Any] | None:
        """Stub implementation of get_document_version_by_id."""
        return None

    async def get_documents_by_source(self,
        source_id: str,
        limit: int | None = None
    ) -> list[dict[str, Any]]:
        """Stub implementation of get_documents_by_source."""
        return []

    async def insert_document(self, document_data: dict[str, Any]) -> dict[str, Any]:
        """Stub implementation of insert_document."""
        return {}

    async def insert_documents_batch(self, documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Stub implementation of insert_documents_batch."""
        return []

    async def list_document_versions(self,
        project_id: str,
        limit: int | None = None
    ) -> list[dict[str, Any]]:
        """Stub implementation of list_document_versions."""
        return []

    async def search_documents_hybrid(self,
        query: str,
        query_embedding: list[float],
        match_count: int = 5,
        filter_metadata: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Stub implementation of search_documents_hybrid."""
        return []

    async def search_documents_vector(self,
        query_embedding: list[float],
        match_count: int = 5,
        filter_metadata: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Stub implementation of search_documents_vector."""
        return []


    # Project operations
    async def create_project(self, project_data: dict[str, Any]) -> dict[str, Any]:
        """Stub implementation of create_project."""
        return {}

    async def delete_project(self, project_id: str) -> bool:
        """Stub implementation of delete_project."""
        return True

    async def get_all_project_task_counts(self) -> dict[str, dict[str, int]]:
        """Stub implementation of get_all_project_task_counts."""
        return {}

    async def get_project_by_id(self, project_id: str) -> dict[str, Any] | None:
        """Stub implementation of get_project_by_id."""
        return None

    async def get_project_features(self, project_id: str) -> list[dict[str, Any]]:
        """Stub implementation of get_project_features."""
        return []

    async def get_sources_for_project(self,
        project_id: str,
        source_ids: list[str]
    ) -> list[dict[str, Any]]:
        """Stub implementation of get_sources_for_project."""
        return []

    async def get_task_counts_by_project(self, project_id: str) -> dict[str, int]:
        """Stub implementation of get_task_counts_by_project."""
        return {}

    async def get_tasks_by_project_and_status(self,
        project_id: str,
        status: str,
        task_order_gte: int | None = None
    ) -> list[dict[str, Any]]:
        """Stub implementation of get_tasks_by_project_and_status."""
        return []

    async def link_project_source(self,
        project_id: str,
        source_id: str,
        notes: str | None = None
    ) -> dict[str, Any]:
        """Stub implementation of link_project_source."""
        return {}

    async def list_project_sources(self,
        project_id: str,
        notes_filter: str | None = None
    ) -> list[dict[str, Any]]:
        """Stub implementation of list_project_sources."""
        return []

    async def list_projects(self,
        include_content: bool = True,
        order_by: str = 'created_at',
        desc: bool = True
    ) -> list[dict[str, Any]]:
        """Stub implementation of list_projects."""
        return []

    async def unlink_project_source(self,
        project_id: str,
        source_id: str
    ) -> bool:
        """Stub implementation of unlink_project_source."""
        return True

    async def unpin_all_projects_except(self, project_id: str) -> int:
        """Stub implementation of unpin_all_projects_except."""
        return 0

    async def update_project(self,
        project_id: str,
        update_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Stub implementation of update_project."""
        return None


    # Code example operations
    async def delete_code_examples_by_source(self, source_id: str) -> int:
        """Stub implementation of delete_code_examples_by_source."""
        return 0

    async def delete_code_examples_by_url(self, url: str) -> int:
        """Stub implementation of delete_code_examples_by_url."""
        return 0

    async def get_code_example_count_by_source(self, source_id: str) -> int:
        """Stub implementation of get_code_example_count_by_source."""
        return 0

    async def get_code_examples_by_source(self,
        source_id: str,
        limit: int | None = None
    ) -> list[dict[str, Any]]:
        """Stub implementation of get_code_examples_by_source."""
        return []

    async def insert_code_example(self, code_example_data: dict[str, Any]) -> dict[str, Any]:
        """Stub implementation of insert_code_example."""
        return {}

    async def insert_code_examples_batch(self, code_examples: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Stub implementation of insert_code_examples_batch."""
        return []

    async def search_code_examples(self,
        query_embedding: list[float],
        match_count: int = 10,
        filter_metadata: dict[str, Any] | None = None,
        source_id: str | None = None
    ) -> list[dict[str, Any]]:
        """Stub implementation of search_code_examples."""
        return []


    # Source operations
    async def delete_crawled_pages_by_source(self, source_id: str) -> int:
        """Stub implementation of delete_crawled_pages_by_source."""
        return 0

    async def delete_source(self, source_id: str) -> bool:
        """Stub implementation of delete_source."""
        return True

    async def get_first_url_by_sources(self, source_ids: list[str]) -> dict[str, str]:
        """Stub implementation of get_first_url_by_sources."""
        return {}

    async def get_source_by_id(self, source_id: str) -> dict[str, Any] | None:
        """Stub implementation of get_source_by_id."""
        return None

    async def list_crawled_pages_by_source(self,
        source_id: str,
        limit: int | None = None,
        offset: int | None = None
    ) -> list[dict[str, Any]]:
        """Stub implementation of list_crawled_pages_by_source."""
        return []

    async def list_pages_by_source(self,
        source_id: str,
        limit: int | None = None,
        offset: int | None = None
    ) -> list[dict[str, Any]]:
        """Stub implementation of list_pages_by_source."""
        return []

    async def list_sources(self, knowledge_type: str | None = None) -> list[dict[str, Any]]:
        """Stub implementation of list_sources."""
        return []

    async def list_sources_with_pagination(self,
        knowledge_type: str | None = None,
        search_query: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str = 'updated_at',
        desc: bool = True,
        select_fields: str | None = None
    ) -> tuple[list[dict[str, Any]], int]:
        """Stub implementation of list_sources_with_pagination."""
        return []

    async def update_source_metadata(self,
        source_id: str,
        metadata: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Stub implementation of update_source_metadata."""
        return None

    async def upsert_source(self, source_data: dict[str, Any]) -> dict[str, Any]:
        """Stub implementation of upsert_source."""
        return {}


    # Crawled page operations
    async def delete_crawled_pages_by_urls(self, urls: list[str]) -> int:
        """Stub implementation of delete_crawled_pages_by_urls."""
        return 0

    async def insert_crawled_page(self, page_data: dict[str, Any]) -> dict[str, Any]:
        """Stub implementation of insert_crawled_page."""
        return {}

    async def insert_crawled_pages_batch(self, pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Stub implementation of insert_crawled_pages_batch."""
        return []

    async def upsert_crawled_page(self, page_data: dict[str, Any]) -> dict[str, Any]:
        """Stub implementation of upsert_crawled_page."""
        return {}


    # Settings operations
    async def delete_setting(self, key: str) -> bool:
        """Stub implementation of delete_setting."""
        return True

    async def get_all_setting_records(self) -> list[dict[str, Any]]:
        """Stub implementation of get_all_setting_records."""
        return []

    async def get_all_settings(self) -> dict[str, Any]:
        """Stub implementation of get_all_settings."""
        return {}

    async def get_setting_records_by_category(self, category: str) -> list[dict[str, Any]]:
        """Stub implementation of get_setting_records_by_category."""
        return []

    async def get_settings_by_key(self, key: str) -> Any | None:
        """Stub implementation of get_settings_by_key."""
        return None

    async def upsert_setting(self,
        key: str,
        value: Any
    ) -> dict[str, Any]:
        """Stub implementation of upsert_setting."""
        return {}

    async def upsert_setting_record(self, setting_data: dict[str, Any]) -> dict[str, Any]:
        """Stub implementation of upsert_setting_record."""
        return {}


    # RPC operations
    async def execute_rpc(self,
        function_name: str,
        params: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Stub implementation of execute_rpc."""
        return []


    # Prompt operations
    async def get_all_prompts(self) -> list[dict[str, Any]]:
        """Stub implementation of get_all_prompts."""
        return []


    # Migration operations
    async def get_applied_migrations(self) -> list[dict[str, Any]]:
        """Stub implementation of get_applied_migrations."""
        return []

    async def migration_exists(self, migration_name: str) -> bool:
        """Stub implementation of migration_exists."""
        return True

    async def record_migration(self, migration_data: dict[str, Any]) -> dict[str, Any]:
        """Stub implementation of record_migration."""
        return {}


    # Page operations
    async def get_crawled_page_by_url(self,
        url: str,
        source_id: str | None = None
    ) -> dict[str, Any] | None:
        """Stub implementation of get_crawled_page_by_url."""
        return None

    async def get_page_count_by_source(self, source_id: str) -> int:
        """Stub implementation of get_page_count_by_source."""
        return 0

    async def get_page_metadata_by_id(self, page_id: str) -> dict[str, Any] | None:
        """Stub implementation of get_page_metadata_by_id."""
        return None

    async def get_page_metadata_by_url(self, url: str) -> dict[str, Any] | None:
        """Stub implementation of get_page_metadata_by_url."""
        return None

    async def update_page_chunk_count(self,
        page_id: str,
        chunk_count: int
    ) -> dict[str, Any] | None:
        """Stub implementation of update_page_chunk_count."""
        return None

    async def upsert_page_metadata_batch(self, pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Stub implementation of upsert_page_metadata_batch."""
        return []


    # Utility operations
    async def get_table_count(self, table_name: str) -> int:
        """Stub implementation of get_table_count."""
        return 0

