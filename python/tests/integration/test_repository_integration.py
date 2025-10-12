"""
Integration Tests with SupabaseDatabaseRepository

These tests demonstrate how to write integration tests that use the real
SupabaseDatabaseRepository against an actual database. These tests:

1. Verify that the repository pattern works with real Supabase
2. Test database schema and constraints
3. Validate that services work end-to-end

IMPORTANT: These tests should be run against a test database, not production!

Run with: pytest tests/integration/ -m integration
"""

import os
import pytest

from src.server.repositories import SupabaseDatabaseRepository
from src.server.services.projects.task_service import TaskService
from src.server.services.projects.project_service import ProjectService
from src.server.utils import get_supabase_client


# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def real_repository():
    """
    Create a repository using real Supabase connection.

    This fixture should only be used in integration tests and
    requires a valid Supabase connection.
    """
    # Skip if not in integration test environment
    if not os.getenv("RUN_INTEGRATION_TESTS"):
        pytest.skip("Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to run.")

    client = get_supabase_client()
    return SupabaseDatabaseRepository(client)


@pytest.fixture
def task_service_integration(real_repository):
    """Create TaskService with real repository."""
    return TaskService(repository=real_repository)


@pytest.fixture
def project_service_integration(real_repository):
    """Create ProjectService with real repository."""
    return ProjectService(repository=real_repository)


# ========================================================================
# PROJECT INTEGRATION TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_create_project_in_database(project_service_integration, real_repository):
    """
    Integration test: Create a project in real database.

    This verifies that:
    - Project creation works with real database
    - UUID generation works
    - Timestamps are set correctly
    - JSONB fields are handled properly
    """
    # Create project
    success, result = await project_service_integration.create_project(
        title="Integration Test Project",
        github_repo="https://github.com/test/integration"
    )

    assert success
    project_id = result["project"]["id"]

    try:
        # Verify in database
        project = await real_repository.get_project_by_id(project_id)

        assert project is not None
        assert project["title"] == "Integration Test Project"
        assert project["github_repo"] == "https://github.com/test/integration"
        assert "created_at" in project
        assert "updated_at" in project

        # Verify JSONB fields exist
        assert "docs" in project
        assert "features" in project
        assert "data" in project

    finally:
        # Cleanup: Delete test project
        await real_repository.delete_project(project_id)


@pytest.mark.asyncio
async def test_project_cascade_delete_in_database(
    project_service_integration,
    task_service_integration,
    real_repository
):
    """
    Integration test: Verify CASCADE delete works.

    This tests that deleting a project also deletes all associated tasks
    via database CASCADE constraint.
    """
    # Create project
    success, project_result = await project_service_integration.create_project(
        title="Cascade Test Project"
    )
    assert success
    project_id = project_result["project"]["id"]

    try:
        # Create tasks
        task_ids = []
        for i in range(3):
            success, task_result = await task_service_integration.create_task(
                project_id=project_id,
                title=f"Task {i}",
                description=f"Test task {i}"
            )
            assert success
            task_ids.append(task_result["task"]["id"])

        # Verify tasks exist
        for task_id in task_ids:
            task = await real_repository.get_task_by_id(task_id)
            assert task is not None

        # Delete project
        success, delete_result = await project_service_integration.delete_project(project_id)
        assert success

        # Verify project is deleted
        project = await real_repository.get_project_by_id(project_id)
        assert project is None

        # Verify tasks are also deleted (CASCADE)
        for task_id in task_ids:
            task = await real_repository.get_task_by_id(task_id)
            assert task is None, f"Task {task_id} should have been deleted by CASCADE"

    except Exception as e:
        # Cleanup on error
        try:
            await real_repository.delete_project(project_id)
        except:
            pass
        raise e


# ========================================================================
# TASK INTEGRATION TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_task_status_constraint_in_database(
    project_service_integration,
    real_repository
):
    """
    Integration test: Verify that task status enum constraint works.

    This tests that the database enforces valid status values.
    """
    # Create project
    success, project_result = await project_service_integration.create_project(
        title="Status Constraint Test"
    )
    assert success
    project_id = project_result["project"]["id"]

    try:
        # Try to create task with invalid status directly in repository
        # This should fail at the database level
        with pytest.raises(Exception) as exc_info:
            await real_repository.create_task({
                "project_id": project_id,
                "title": "Invalid Status Task",
                "status": "invalid-status",  # Not in enum
                "task_order": 0
            })

        # Verify it's a database constraint error
        error_msg = str(exc_info.value).lower()
        assert "invalid" in error_msg or "constraint" in error_msg or "enum" in error_msg

    finally:
        # Cleanup
        await real_repository.delete_project(project_id)


@pytest.mark.asyncio
async def test_task_ordering_in_database(
    project_service_integration,
    task_service_integration,
    real_repository
):
    """
    Integration test: Verify task ordering with real database.

    This tests that task order updates work correctly with real database
    transactions and constraints.
    """
    # Create project
    success, project_result = await project_service_integration.create_project(
        title="Task Ordering Test"
    )
    assert success
    project_id = project_result["project"]["id"]

    try:
        # Create tasks at specific orders
        task1_success, task1_result = await task_service_integration.create_task(
            project_id=project_id,
            title="Task at order 0",
            task_order=0
        )
        assert task1_success

        task2_success, task2_result = await task_service_integration.create_task(
            project_id=project_id,
            title="Task at order 1",
            task_order=1
        )
        assert task2_success

        # Insert task at position 1 (should shift task2 to order 2)
        task3_success, task3_result = await task_service_integration.create_task(
            project_id=project_id,
            title="Inserted at order 1",
            task_order=1
        )
        assert task3_success

        # Fetch all tasks from database
        tasks = await real_repository.list_tasks(
            project_id=project_id,
            status="todo"
        )

        # Sort by order
        tasks_sorted = sorted(tasks, key=lambda t: t["task_order"])

        # Verify ordering
        assert len(tasks_sorted) == 3
        assert tasks_sorted[0]["title"] == "Task at order 0"
        assert tasks_sorted[0]["task_order"] == 0
        assert tasks_sorted[1]["title"] == "Inserted at order 1"
        assert tasks_sorted[1]["task_order"] == 1
        assert tasks_sorted[2]["title"] == "Task at order 1"  # Original task2
        assert tasks_sorted[2]["task_order"] == 2  # Shifted

    finally:
        # Cleanup
        await real_repository.delete_project(project_id)


@pytest.mark.asyncio
async def test_task_counts_aggregation_in_database(
    project_service_integration,
    task_service_integration,
    real_repository
):
    """
    Integration test: Verify task count aggregation with real database.

    This tests that the repository's get_all_project_task_counts method
    works correctly with real database queries.
    """
    # Create two projects
    success1, project1_result = await project_service_integration.create_project(
        title="Project 1 for Counts"
    )
    assert success1
    project1_id = project1_result["project"]["id"]

    success2, project2_result = await project_service_integration.create_project(
        title="Project 2 for Counts"
    )
    assert success2
    project2_id = project2_result["project"]["id"]

    try:
        # Create tasks for project 1
        for status in ["todo", "todo", "doing", "done"]:
            await task_service_integration.create_task(
                project_id=project1_id,
                title=f"Task {status}",
                status=status if status != "todo" else "todo"
            )
            if status != "todo":
                # Update status after creation
                tasks = await real_repository.list_tasks(project_id=project1_id)
                latest_task = tasks[-1]
                await real_repository.update_task(
                    latest_task["id"],
                    {"status": status}
                )

        # Create tasks for project 2
        for status in ["todo", "doing", "doing"]:
            await task_service_integration.create_task(
                project_id=project2_id,
                title=f"Task {status}",
                status="todo"
            )
            if status != "todo":
                tasks = await real_repository.list_tasks(project_id=project2_id)
                latest_task = tasks[-1]
                await real_repository.update_task(
                    latest_task["id"],
                    {"status": status}
                )

        # Get aggregated counts
        counts = await real_repository.get_all_project_task_counts()

        # Verify counts for project 1
        assert project1_id in counts
        assert counts[project1_id]["todo"] == 2
        assert counts[project1_id]["doing"] == 1
        assert counts[project1_id]["done"] == 1

        # Verify counts for project 2
        assert project2_id in counts
        assert counts[project2_id]["todo"] == 1
        assert counts[project2_id]["doing"] == 2
        assert counts[project2_id]["done"] == 0

    finally:
        # Cleanup
        await real_repository.delete_project(project1_id)
        await real_repository.delete_project(project2_id)


# ========================================================================
# SOURCE INTEGRATION TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_source_cascade_delete_in_database(real_repository):
    """
    Integration test: Verify source CASCADE delete.

    This tests that deleting a source also deletes:
    - All associated documents
    - All associated code examples
    - All associated crawled pages
    """
    # Create source
    source = await real_repository.upsert_source({
        "source_id": "integration-test-source",
        "title": "Integration Test Source",
        "metadata": {"knowledge_type": "technical"}
    })

    try:
        # Create related records
        doc = await real_repository.insert_document({
            "source_id": source["source_id"],
            "content": "Test document",
            "embedding": [0.1] * 1536  # Example embedding
        })

        code = await real_repository.insert_code_example({
            "source_id": source["source_id"],
            "content": "def test(): pass",
            "summary": "Test function",
            "metadata": {}
        })

        page = await real_repository.insert_crawled_page({
            "source_id": source["source_id"],
            "url": "https://example.com/test",
            "content": "Test page"
        })

        # Verify all records exist
        assert await real_repository.get_source_by_id(source["source_id"]) is not None
        assert await real_repository.get_document_by_id(doc["id"]) is not None

        # Delete source
        deleted = await real_repository.delete_source(source["source_id"])
        assert deleted

        # Verify all related records are deleted
        assert await real_repository.get_source_by_id(source["source_id"]) is None
        assert await real_repository.get_document_by_id(doc["id"]) is None

        # Verify code examples are deleted
        code_examples = await real_repository.get_code_examples_by_source(source["source_id"])
        assert len(code_examples) == 0

        # Verify pages are deleted
        pages = await real_repository.list_crawled_pages_by_source(source["source_id"])
        assert len(pages) == 0

    except Exception as e:
        # Cleanup on error
        try:
            await real_repository.delete_source(source["source_id"])
        except:
            pass
        raise e


# ========================================================================
# NOTES FOR RUNNING INTEGRATION TESTS
# ========================================================================


"""
To run these integration tests:

1. Set up a test Supabase instance (NOT production!)
2. Set environment variables:
   - SUPABASE_URL=<your-test-supabase-url>
   - SUPABASE_SERVICE_KEY=<your-test-service-key>
   - RUN_INTEGRATION_TESTS=1

3. Run tests:
   pytest tests/integration/ -m integration -v

4. Or run specific test:
   pytest tests/integration/test_repository_integration.py::test_create_project_in_database -v

Best Practices:
- Always clean up test data in finally blocks
- Use unique identifiers for test data
- Don't run against production database
- Consider using database transactions that can be rolled back
"""
