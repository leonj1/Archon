"""
Fake Database Repository Implementation

In-memory implementation of the DatabaseRepository interface for testing.
Uses dictionaries to store data and generates UUIDs for IDs.
Thread-safe and maintains referential integrity.
"""

import threading
import uuid
from datetime import datetime
from typing import Any

from .database_repository import DatabaseRepository

class FakeDatabaseRepository(DatabaseRepository):
    """
    In-memory implementation of DatabaseRepository for testing.

    All data is stored in dictionaries. Perfect for unit testing services
    without needing a real database connection.
    """

    def __init__(self):
        """Initialize with empty in-memory storage."""
        self.lock = threading.RLock()

        # Storage dictionaries
        self.page_metadata: dict[str, dict[str, Any]] = {}
        self.documents: dict[str, dict[str, Any]] = {}
        self.code_examples: dict[str, dict[str, Any]] = {}
        self.settings: dict[str, Any] = {}
        self.projects: dict[str, dict[str, Any]] = {}
        self.tasks: dict[str, dict[str, Any]] = {}
        self.sources: dict[str, dict[str, Any]] = {}
        self.crawled_pages: dict[str, dict[str, Any]] = {}
        self.document_versions: dict[str, dict[str, Any]] = {}
        self.project_sources: list[dict[str, Any]] = []

    def _generate_id(self) -> str:
        """Generate a UUID for new records."""
        return str(uuid.uuid4())

    # ========================================================================
    # 1. PAGE METADATA OPERATIONS
    # ========================================================================

    async def get_page_metadata_by_id(self, page_id: str) -> dict[str, Any] | None:
        """Retrieve page metadata by page ID."""
        with self.lock:
            return self.page_metadata.get(page_id)

    async def get_page_metadata_by_url(self, url: str) -> dict[str, Any] | None:
        """Retrieve page metadata by URL."""
        with self.lock:
            for page in self.page_metadata.values():
                if page.get("url") == url:
                    return page
            return None

    async def list_pages_by_source(
        self,
        source_id: str,
        limit: int | None = None,
        offset: int | None = None
    ) -> list[dict[str, Any]]:
        """List all pages for a given source."""
        with self.lock:
            pages = [
                page for page in self.crawled_pages.values()
                if page.get("source_id") == source_id
            ]
            pages.sort(key=lambda x: x.get("created_at", ""), reverse=True)

            if offset:
                pages = pages[offset:]
            if limit:
                pages = pages[:limit]

            return pages

    async def get_page_count_by_source(self, source_id: str) -> int:
        """Get the count of pages for a source."""
        with self.lock:
            return sum(
                1 for page in self.crawled_pages.values()
                if page.get("source_id") == source_id
            )

    async def upsert_page_metadata_batch(
        self,
        pages: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Insert or update multiple page metadata records in a batch."""
        with self.lock:
            result = []
            for page_data in pages:
                url = page_data.get("url")
                # Find existing by URL
                existing_page_id = None
                for page_id, page in self.page_metadata.items():
                    if page.get("url") == url:
                        existing_page_id = page_id
                        break

                if existing_page_id:
                    # Update existing
                    self.page_metadata[existing_page_id].update(page_data)
                    result.append(self.page_metadata[existing_page_id])
                else:
                    # Insert new
                    page_id = page_data.get("id") or self._generate_id()
                    page_data["id"] = page_id
                    self.page_metadata[page_id] = page_data.copy()
                    result.append(self.page_metadata[page_id])

            return result

    async def update_page_chunk_count(self, page_id: str, chunk_count: int) -> dict[str, Any] | None:
        """Update the chunk_count field for a page after chunking is complete."""
        with self.lock:
            if page_id not in self.page_metadata:
                return None

            self.page_metadata[page_id]["chunk_count"] = chunk_count
            return self.page_metadata[page_id]

    # ========================================================================
    # 2. DOCUMENT SEARCH OPERATIONS
    # ========================================================================

    async def search_documents_vector(
        self,
        query_embedding: list[float],
        match_count: int = 5,
        filter_metadata: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Perform vector similarity search (simplified for testing)."""
        with self.lock:
            docs = list(self.documents.values())
            if filter_metadata:
                docs = [
                    doc for doc in docs
                    if all(doc.get(k) == v for k, v in filter_metadata.items())
                ]
            return docs[:match_count]

    async def search_documents_hybrid(
        self,
        query: str,
        query_embedding: list[float],
        match_count: int = 5,
        filter_metadata: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Perform hybrid search (simplified for testing)."""
        with self.lock:
            docs = list(self.documents.values())
            if filter_metadata:
                docs = [
                    doc for doc in docs
                    if all(doc.get(k) == v for k, v in filter_metadata.items())
                ]
            # Simple text matching
            query_lower = query.lower()
            matching_docs = [
                doc for doc in docs
                if query_lower in doc.get("content", "").lower()
            ]
            return matching_docs[:match_count]

    async def get_documents_by_source(
        self,
        source_id: str,
        limit: int | None = None
    ) -> list[dict[str, Any]]:
        """Get all document chunks for a source."""
        with self.lock:
            docs = [
                doc for doc in self.documents.values()
                if doc.get("source_id") == source_id
            ]
            if limit:
                docs = docs[:limit]
            return docs

    async def get_document_by_id(self, document_id: str) -> dict[str, Any] | None:
        """Get a specific document by ID."""
        with self.lock:
            return self.documents.get(document_id)

    async def insert_document(self, document_data: dict[str, Any]) -> dict[str, Any]:
        """Insert a new document chunk."""
        with self.lock:
            doc_id = document_data.get("id") or self._generate_id()
            document_data["id"] = doc_id
            self.documents[doc_id] = document_data.copy()
            return self.documents[doc_id]

    async def insert_documents_batch(
        self,
        documents: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Insert multiple document chunks in a batch."""
        with self.lock:
            inserted = []
            for doc_data in documents:
                doc = await self.insert_document(doc_data)
                inserted.append(doc)
            return inserted

    async def delete_documents_by_source(self, source_id: str) -> int:
        """Delete all documents for a source."""
        with self.lock:
            to_delete = [
                doc_id for doc_id, doc in self.documents.items()
                if doc.get("source_id") == source_id
            ]
            for doc_id in to_delete:
                del self.documents[doc_id]
            return len(to_delete)

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
        with self.lock:
            examples = list(self.code_examples.values())
            if source_id:
                examples = [ex for ex in examples if ex.get("source_id") == source_id]
            if filter_metadata:
                examples = [
                    ex for ex in examples
                    if all(ex.get(k) == v for k, v in filter_metadata.items())
                ]
            return examples[:match_count]

    async def get_code_examples_by_source(
        self,
        source_id: str,
        limit: int | None = None
    ) -> list[dict[str, Any]]:
        """Get all code examples for a source."""
        with self.lock:
            examples = [
                ex for ex in self.code_examples.values()
                if ex.get("source_id") == source_id
            ]
            if limit:
                examples = examples[:limit]
            return examples

    async def get_code_example_count_by_source(self, source_id: str) -> int:
        """Get the count of code examples for a source."""
        with self.lock:
            return sum(
                1 for ex in self.code_examples.values()
                if ex.get("source_id") == source_id
            )

    async def insert_code_example(
        self,
        code_example_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Insert a new code example."""
        with self.lock:
            ex_id = code_example_data.get("id") or self._generate_id()
            code_example_data["id"] = ex_id
            self.code_examples[ex_id] = code_example_data.copy()
            return self.code_examples[ex_id]

    async def insert_code_examples_batch(
        self,
        code_examples: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Insert multiple code examples in a batch."""
        with self.lock:
            inserted = []
            for ex_data in code_examples:
                ex = await self.insert_code_example(ex_data)
                inserted.append(ex)
            return inserted

    async def delete_code_examples_by_source(self, source_id: str) -> int:
        """Delete all code examples for a source."""
        with self.lock:
            to_delete = [
                ex_id for ex_id, ex in self.code_examples.items()
                if ex.get("source_id") == source_id
            ]
            for ex_id in to_delete:
                del self.code_examples[ex_id]
            return len(to_delete)

    async def delete_code_examples_by_url(self, url: str) -> int:
        """Delete all code examples for a specific URL."""
        with self.lock:
            to_delete = [
                ex_id for ex_id, ex in self.code_examples.items()
                if ex.get("url") == url
            ]
            for ex_id in to_delete:
                del self.code_examples[ex_id]
            return len(to_delete)

    # ========================================================================
    # 4. SETTINGS OPERATIONS
    # ========================================================================

    async def get_settings_by_key(self, key: str) -> Any | None:
        """Retrieve a setting value by its key."""
        with self.lock:
            return self.settings.get(key)

    async def get_all_settings(self) -> dict[str, Any]:
        """Retrieve all settings as a dictionary."""
        with self.lock:
            return self.settings.copy()

    async def upsert_setting(self, key: str, value: Any) -> dict[str, Any]:
        """Insert or update a setting."""
        with self.lock:
            self.settings[key] = value
            return {"key": key, "value": value}

    async def delete_setting(self, key: str) -> bool:
        """Delete a setting by key."""
        with self.lock:
            if key in self.settings:
                del self.settings[key]
                return True
            return False

    async def get_all_setting_records(self) -> list[dict[str, Any]]:
        """Retrieve all setting records with full details."""
        with self.lock:
            # For testing, settings are stored as dict, convert to records
            return [
                {"key": key, "value": value}
                for key, value in self.settings.items()
            ]

    async def get_setting_records_by_category(self, category: str) -> list[dict[str, Any]]:
        """Retrieve setting records filtered by category."""
        with self.lock:
            # For testing, simplified - return empty list or filter if metadata exists
            return []

    async def upsert_setting_record(self, setting_data: dict[str, Any]) -> dict[str, Any]:
        """Insert or update a full setting record."""
        with self.lock:
            key = setting_data.get("key")
            value = setting_data.get("value")
            if key:
                self.settings[key] = value
            return setting_data

    # ========================================================================
    # 5. PROJECT OPERATIONS
    # ========================================================================

    async def create_project(self, project_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new project."""
        with self.lock:
            project_id = project_data.get("id") or self._generate_id()
            project_data["id"] = project_id

            if "created_at" not in project_data:
                project_data["created_at"] = datetime.now().isoformat()
            if "updated_at" not in project_data:
                project_data["updated_at"] = datetime.now().isoformat()

            self.projects[project_id] = project_data.copy()
            return self.projects[project_id]

    async def list_projects(
        self,
        include_content: bool = True,
        order_by: str = "created_at",
        desc: bool = True
    ) -> list[dict[str, Any]]:
        """List all projects."""
        with self.lock:
            projects = list(self.projects.values())
            projects.sort(key=lambda x: x.get(order_by, ""), reverse=desc)
            return projects

    async def get_project_by_id(self, project_id: str) -> dict[str, Any] | None:
        """Get a specific project by ID."""
        with self.lock:
            return self.projects.get(project_id)

    async def update_project(
        self,
        project_id: str,
        update_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update a project with specified fields."""
        with self.lock:
            if project_id not in self.projects:
                return None

            update_data["updated_at"] = datetime.now().isoformat()
            self.projects[project_id].update(update_data)
            return self.projects[project_id]

    async def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        with self.lock:
            if project_id in self.projects:
                del self.projects[project_id]
                # CASCADE delete tasks
                to_delete = [
                    task_id for task_id, task in self.tasks.items()
                    if task.get("project_id") == project_id
                ]
                for task_id in to_delete:
                    del self.tasks[task_id]
                return True
            return False

    async def unpin_all_projects_except(self, project_id: str) -> int:
        """Unpin all projects except the specified one."""
        with self.lock:
            count = 0
            for pid, project in self.projects.items():
                if pid != project_id and project.get("pinned"):
                    project["pinned"] = False
                    count += 1
            return count

    async def get_project_features(self, project_id: str) -> list[dict[str, Any]] | None:
        """Get features from a project's features JSONB field.

        Returns:
            List of features if project exists, None if project doesn't exist.
        """
        with self.lock:
            project = self.projects.get(project_id)
            if not project:
                return None
            return project.get("features", [])

    # ========================================================================
    # 6. TASK OPERATIONS
    # ========================================================================

    async def create_task(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new task."""
        with self.lock:
            task_id = task_data.get("id") or self._generate_id()
            task_data["id"] = task_id

            # Set default values for required fields
            if "created_at" not in task_data:
                task_data["created_at"] = datetime.now().isoformat()
            if "updated_at" not in task_data:
                task_data["updated_at"] = datetime.now().isoformat()
            if "description" not in task_data:
                task_data["description"] = ""
            if "assignee" not in task_data:
                task_data["assignee"] = "User"
            if "task_order" not in task_data:
                task_data["task_order"] = 0
            if "priority" not in task_data:
                task_data["priority"] = "medium"
            if "archived" not in task_data:
                task_data["archived"] = False

            self.tasks[task_id] = task_data.copy()
            return self.tasks[task_id]

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
        with self.lock:
            tasks = list(self.tasks.values())

            # Apply filters
            if project_id:
                tasks = [t for t in tasks if t.get("project_id") == project_id]
            if status:
                tasks = [t for t in tasks if t.get("status") == status]
            if assignee:
                tasks = [t for t in tasks if t.get("assignee") == assignee]
            if not include_archived:
                tasks = [t for t in tasks if not t.get("archived")]
            if search_query:
                query_lower = search_query.lower()
                tasks = [
                    t for t in tasks
                    if query_lower in t.get("title", "").lower()
                    or query_lower in t.get("description", "").lower()
                    or query_lower in t.get("feature", "").lower()
                ]

            # Sort
            tasks.sort(key=lambda x: (x.get(order_by, 0), x.get("created_at", "")))

            return tasks

    async def get_task_by_id(self, task_id: str) -> dict[str, Any] | None:
        """Get a specific task by ID."""
        with self.lock:
            return self.tasks.get(task_id)

    async def update_task(
        self,
        task_id: str,
        update_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update a task with specified fields."""
        with self.lock:
            if task_id not in self.tasks:
                return None

            update_data["updated_at"] = datetime.now().isoformat()
            self.tasks[task_id].update(update_data)
            return self.tasks[task_id]

    async def delete_task(self, task_id: str) -> bool:
        """Delete a task (hard delete)."""
        with self.lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                return True
            return False

    async def archive_task(
        self,
        task_id: str,
        archived_by: str = "system"
    ) -> dict[str, Any] | None:
        """Archive a task (soft delete)."""
        with self.lock:
            if task_id not in self.tasks:
                return None

            self.tasks[task_id].update({
                "archived": True,
                "archived_at": datetime.now().isoformat(),
                "archived_by": archived_by,
                "updated_at": datetime.now().isoformat(),
            })
            return self.tasks[task_id]

    async def get_tasks_by_project_and_status(
        self,
        project_id: str,
        status: str,
        task_order_gte: int | None = None
    ) -> list[dict[str, Any]]:
        """Get tasks filtered by project, status, and optionally task_order."""
        with self.lock:
            tasks = [
                t for t in self.tasks.values()
                if t.get("project_id") == project_id and t.get("status") == status
            ]
            if task_order_gte is not None:
                tasks = [t for t in tasks if t.get("task_order", 0) >= task_order_gte]
            return tasks

    async def get_task_counts_by_project(self, project_id: str) -> dict[str, int]:
        """Get task counts grouped by status for a project."""
        with self.lock:
            counts = {"todo": 0, "doing": 0, "review": 0, "done": 0}
            for task in self.tasks.values():
                if task.get("project_id") == project_id and not task.get("archived"):
                    status = task.get("status")
                    if status in counts:
                        counts[status] += 1
            return counts

    async def get_all_project_task_counts(self) -> dict[str, dict[str, int]]:
        """Get task counts for all projects in a single query."""
        with self.lock:
            counts_by_project: dict[str, dict[str, int]] = {}
            for task in self.tasks.values():
                if task.get("archived"):
                    continue

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

    # ========================================================================
    # 7. SOURCE OPERATIONS
    # ========================================================================

    async def list_sources(
        self,
        knowledge_type: str | None = None
    ) -> list[dict[str, Any]]:
        """List all sources, optionally filtered by knowledge type."""
        with self.lock:
            sources = list(self.sources.values())
            if knowledge_type:
                sources = [
                    s for s in sources
                    if s.get("metadata", {}).get("knowledge_type") == knowledge_type
                ]
            return sources

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
        with self.lock:
            sources = list(self.sources.values())

            # Apply knowledge type filter
            if knowledge_type:
                sources = [
                    s for s in sources
                    if s.get("metadata", {}).get("knowledge_type") == knowledge_type
                ]

            # Apply search filter
            if search_query:
                query_lower = search_query.lower()
                sources = [
                    s for s in sources
                    if query_lower in s.get("title", "").lower()
                    or query_lower in s.get("summary", "").lower()
                ]

            # Get total count before pagination
            total = len(sources)

            # Apply ordering
            sources.sort(key=lambda x: x.get(order_by, ""), reverse=desc)

            # Apply pagination
            if offset is not None:
                sources = sources[offset:]
            if limit is not None:
                sources = sources[:limit]

            return sources, total

    async def get_source_by_id(self, source_id: str) -> dict[str, Any] | None:
        """Get a specific source by ID."""
        with self.lock:
            return self.sources.get(source_id)

    async def upsert_source(self, source_data: dict[str, Any]) -> dict[str, Any]:
        """Insert or update a source."""
        with self.lock:
            source_id = source_data.get("source_id")
            if not source_id:
                raise ValueError("source_id is required")

            # Check if source exists
            if source_id in self.sources:
                # MERGE update: preserve existing fields not in source_data
                existing = self.sources[source_id]

                # Merge top-level fields
                merged = existing.copy()
                merged.update(source_data)

                # Special handling for metadata: deep merge
                if "metadata" in source_data and "metadata" in existing:
                    # Merge metadata dicts (new values override old)
                    merged_metadata = existing.get("metadata", {}).copy()
                    merged_metadata.update(source_data["metadata"])
                    merged["metadata"] = merged_metadata

                self.sources[source_id] = merged
            else:
                # INSERT: new source
                self.sources[source_id] = source_data.copy()

            return self.sources[source_id]

    async def update_source_metadata(
        self,
        source_id: str,
        metadata: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update source metadata."""
        with self.lock:
            if source_id not in self.sources:
                return None

            current_metadata = self.sources[source_id].get("metadata", {})
            merged_metadata = {**current_metadata, **metadata}
            self.sources[source_id]["metadata"] = merged_metadata
            return self.sources[source_id]

    async def delete_source(self, source_id: str) -> bool:
        """Delete a source (CASCADE deletes related records)."""
        with self.lock:
            if source_id not in self.sources:
                return False

            del self.sources[source_id]

            # CASCADE delete related records
            # Documents
            doc_ids = [
                doc_id for doc_id, doc in self.documents.items()
                if doc.get("source_id") == source_id
            ]
            for doc_id in doc_ids:
                del self.documents[doc_id]

            # Code examples
            ex_ids = [
                ex_id for ex_id, ex in self.code_examples.items()
                if ex.get("source_id") == source_id
            ]
            for ex_id in ex_ids:
                del self.code_examples[ex_id]

            # Crawled pages
            page_ids = [
                page_id for page_id, page in self.crawled_pages.items()
                if page.get("source_id") == source_id
            ]
            for page_id in page_ids:
                del self.crawled_pages[page_id]

            return True

    # ========================================================================
    # 8. CRAWLED PAGES OPERATIONS
    # ========================================================================

    async def get_crawled_page_by_url(
        self,
        url: str,
        source_id: str | None = None
    ) -> dict[str, Any] | None:
        """Get a crawled page by URL."""
        with self.lock:
            for page in self.crawled_pages.values():
                if page.get("url") == url:
                    if source_id is None or page.get("source_id") == source_id:
                        return page
            return None

    async def insert_crawled_page(
        self,
        page_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Insert a new crawled page."""
        with self.lock:
            page_id = page_data.get("id") or self._generate_id()
            page_data["id"] = page_id
            self.crawled_pages[page_id] = page_data.copy()
            return self.crawled_pages[page_id]

    async def upsert_crawled_page(
        self,
        page_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Insert or update a crawled page."""
        with self.lock:
            # Find existing by URL and source_id
            url = page_data.get("url")
            source_id = page_data.get("source_id")

            existing_page = None
            for page in self.crawled_pages.values():
                if page.get("url") == url and page.get("source_id") == source_id:
                    existing_page = page
                    break

            if existing_page:
                # Update existing
                page_id = existing_page["id"]
                self.crawled_pages[page_id].update(page_data)
                return self.crawled_pages[page_id]
            else:
                # Insert new
                return await self.insert_crawled_page(page_data)

    async def delete_crawled_pages_by_source(self, source_id: str) -> int:
        """Delete all crawled pages for a source."""
        with self.lock:
            to_delete = [
                page_id for page_id, page in self.crawled_pages.items()
                if page.get("source_id") == source_id
            ]
            for page_id in to_delete:
                del self.crawled_pages[page_id]
            return len(to_delete)

    async def list_crawled_pages_by_source(
        self,
        source_id: str,
        limit: int | None = None,
        offset: int | None = None
    ) -> list[dict[str, Any]]:
        """List crawled pages for a source."""
        with self.lock:
            pages = [
                page for page in self.crawled_pages.values()
                if page.get("source_id") == source_id
            ]
            pages.sort(key=lambda x: x.get("created_at", ""), reverse=True)

            if offset:
                pages = pages[offset:]
            if limit:
                pages = pages[:limit]

            return pages

    async def delete_crawled_pages_by_urls(self, urls: list[str]) -> int:
        """Delete crawled pages by a list of URLs."""
        with self.lock:
            if not urls:
                return 0

            urls_set = set(urls)
            to_delete = [
                page_id for page_id, page in self.crawled_pages.items()
                if page.get("url") in urls_set
            ]
            for page_id in to_delete:
                del self.crawled_pages[page_id]
            return len(to_delete)

    async def insert_crawled_pages_batch(
        self,
        pages: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Insert multiple crawled pages in a batch."""
        with self.lock:
            if not pages:
                return []

            inserted = []
            for page_data in pages:
                page = await self.insert_crawled_page(page_data)
                inserted.append(page)
            return inserted

    async def get_first_url_by_sources(
        self,
        source_ids: list[str]
    ) -> dict[str, str]:
        """Get the first (oldest) URL for each source."""
        with self.lock:
            if not source_ids:
                return {}

            urls = {}

            # Get all pages for these sources
            pages = [
                page for page in self.crawled_pages.values()
                if page.get("source_id") in source_ids
            ]

            # Sort by created_at ascending
            pages.sort(key=lambda x: x.get("created_at", ""))

            # Group by source_id, keeping first URL for each
            for page in pages:
                source_id = page["source_id"]
                if source_id not in urls:
                    urls[source_id] = page["url"]

            return urls

    # ========================================================================
    # 9. DOCUMENT VERSION OPERATIONS
    # ========================================================================

    async def create_document_version(
        self,
        version_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a new document version."""
        with self.lock:
            version_id = version_data.get("id") or self._generate_id()
            version_data["id"] = version_id

            if "created_at" not in version_data:
                version_data["created_at"] = datetime.now().isoformat()

            self.document_versions[version_id] = version_data.copy()
            return self.document_versions[version_id]

    async def list_document_versions(
        self,
        project_id: str,
        limit: int | None = None
    ) -> list[dict[str, Any]]:
        """List document versions for a project."""
        with self.lock:
            versions = [
                v for v in self.document_versions.values()
                if v.get("project_id") == project_id
            ]
            versions.sort(key=lambda x: x.get("created_at", ""), reverse=True)

            if limit:
                versions = versions[:limit]

            return versions

    async def get_document_version_by_id(
        self,
        version_id: str
    ) -> dict[str, Any] | None:
        """Get a specific document version by ID."""
        with self.lock:
            return self.document_versions.get(version_id)

    async def delete_document_version(self, version_id: str) -> bool:
        """Delete a document version."""
        with self.lock:
            if version_id in self.document_versions:
                del self.document_versions[version_id]
                return True
            return False

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
        with self.lock:
            link = {
                "project_id": project_id,
                "source_id": source_id,
                "notes": notes,
            }
            self.project_sources.append(link)
            return link

    async def unlink_project_source(
        self,
        project_id: str,
        source_id: str
    ) -> bool:
        """Unlink a source from a project."""
        with self.lock:
            initial_len = len(self.project_sources)
            self.project_sources = [
                link for link in self.project_sources
                if not (link["project_id"] == project_id and link["source_id"] == source_id)
            ]
            return len(self.project_sources) < initial_len

    async def list_project_sources(
        self,
        project_id: str,
        notes_filter: str | None = None
    ) -> list[dict[str, Any]]:
        """List sources linked to a project."""
        with self.lock:
            links = [
                link for link in self.project_sources
                if link["project_id"] == project_id
            ]
            if notes_filter:
                links = [link for link in links if link.get("notes") == notes_filter]
            return links

    async def get_sources_for_project(
        self,
        project_id: str,
        source_ids: list[str]
    ) -> list[dict[str, Any]]:
        """Get full source objects for a list of source IDs."""
        with self.lock:
            return [
                self.sources[source_id]
                for source_id in source_ids
                if source_id in self.sources
            ]

    # ========================================================================
    # 11. RPC OPERATIONS
    # ========================================================================

    async def execute_rpc(
        self,
        function_name: str,
        params: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Execute a database RPC (simplified for testing)."""
        # For testing, just return empty list
        # Real implementations would handle specific RPC functions
        return []

    # ========================================================================
    # 12. PROMPT OPERATIONS
    # ========================================================================

    async def get_all_prompts(self) -> list[dict[str, Any]]:
        """Retrieve all prompts (simplified for testing)."""
        # For testing, return empty list or mock data if needed
        return []

    # ========================================================================
    # 13. TABLE COUNT OPERATIONS
    # ========================================================================

    async def get_table_count(self, table_name: str) -> int:
        """Get the count of records in a specified table."""
        with self.lock:
            # Map table names to storage dictionaries
            table_map = {
                "archon_page_metadata": self.page_metadata,
                "archon_documents": self.documents,
                "archon_code_examples": self.code_examples,
                "archon_settings": self.settings,
                "archon_projects": self.projects,
                "archon_tasks": self.tasks,
                "archon_sources": self.sources,
                "archon_crawled_pages": self.crawled_pages,
                "archon_document_versions": self.document_versions,
            }
            storage = table_map.get(table_name)
            if storage is None:
                return 0
            return len(storage)

    # ========================================================================
    # 14. MIGRATION OPERATIONS
    # ========================================================================

    async def get_applied_migrations(self) -> list[dict[str, Any]]:
        """Retrieve all applied migrations (simplified for testing)."""
        with self.lock:
            # For testing, return empty list
            # In real tests, you could populate this with mock migration data
            return []

    async def migration_exists(self, migration_name: str) -> bool:
        """Check if a migration has been applied (simplified for testing)."""
        with self.lock:
            # For testing, always return False (no migrations applied)
            # In real tests, you could check against a mock migrations dictionary
            return False

    async def record_migration(self, migration_data: dict[str, Any]) -> dict[str, Any]:
        """Record a migration as applied (simplified for testing)."""
        with self.lock:
            # For testing, just return the migration data with an ID
            migration_id = self._generate_id()
            migration_data["id"] = migration_id
            # In a real test, you might store this in a migrations dictionary
            return migration_data
