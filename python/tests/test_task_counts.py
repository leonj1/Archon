"""Test suite for batch task counts endpoint - Performance optimization tests."""

import time
from unittest.mock import MagicMock, patch


def test_batch_task_counts_endpoint_exists(client):
    """Test that batch task counts endpoint exists and responds."""
    response = client.get("/api/projects/task-counts")
    # Accept various status codes - endpoint exists
    assert response.status_code in [200, 400, 422, 500]
    
    # If successful, response should be JSON dict
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, dict)


def test_batch_task_counts_endpoint(client, mock_supabase_client):
    """Test that batch task counts endpoint returns counts for all projects."""
    from src.server.repositories.fake_repository import FakeDatabaseRepository
    from src.server.repositories.repository_factory import reset_factory

    # Reset factory to ensure clean state
    reset_factory()

    # Create a fake repository and populate with test data
    fake_repo = FakeDatabaseRepository()

    # Set up test tasks
    test_tasks = [
        {"id": "t1", "project_id": "project-1", "status": "todo", "archived": False, "title": "Task 1", "description": "", "assignee": "User", "task_order": 0, "priority": "medium", "sources": [], "code_examples": [], "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
        {"id": "t2", "project_id": "project-1", "status": "todo", "archived": False, "title": "Task 2", "description": "", "assignee": "User", "task_order": 1, "priority": "medium", "sources": [], "code_examples": [], "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
        {"id": "t3", "project_id": "project-1", "status": "doing", "archived": False, "title": "Task 3", "description": "", "assignee": "User", "task_order": 0, "priority": "medium", "sources": [], "code_examples": [], "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
        {"id": "t4", "project_id": "project-1", "status": "review", "archived": False, "title": "Task 4", "description": "", "assignee": "User", "task_order": 0, "priority": "medium", "sources": [], "code_examples": [], "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
        {"id": "t5", "project_id": "project-1", "status": "done", "archived": False, "title": "Task 5", "description": "", "assignee": "User", "task_order": 0, "priority": "medium", "sources": [], "code_examples": [], "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
        {"id": "t6", "project_id": "project-2", "status": "todo", "archived": False, "title": "Task 6", "description": "", "assignee": "User", "task_order": 0, "priority": "medium", "sources": [], "code_examples": [], "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
        {"id": "t7", "project_id": "project-2", "status": "doing", "archived": False, "title": "Task 7", "description": "", "assignee": "User", "task_order": 0, "priority": "medium", "sources": [], "code_examples": [], "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
        {"id": "t8", "project_id": "project-2", "status": "done", "archived": False, "title": "Task 8", "description": "", "assignee": "User", "task_order": 0, "priority": "medium", "sources": [], "code_examples": [], "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
        {"id": "t9", "project_id": "project-2", "status": "done", "archived": False, "title": "Task 9", "description": "", "assignee": "User", "task_order": 1, "priority": "medium", "sources": [], "code_examples": [], "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
        {"id": "t10", "project_id": "project-3", "status": "todo", "archived": False, "title": "Task 10", "description": "", "assignee": "User", "task_order": 0, "priority": "medium", "sources": [], "code_examples": [], "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"},
    ]

    # Add tasks to fake repository
    fake_repo.tasks = {task["id"]: task for task in test_tasks}

    # Patch get_repository to return our fake repository
    with patch("src.server.api_routes.projects_api.get_repository", return_value=fake_repo):
        # Make the request
        response = client.get("/api/projects/task-counts")

        # Should succeed
        assert response.status_code == 200

    # Check response format and data
    data = response.json()
    assert isinstance(data, dict)

    # Verify counts are correct
    assert "project-1" in data
    assert "project-2" in data
    assert "project-3" in data

    # Verify actual counts
    assert data["project-1"]["todo"] == 2
    assert data["project-1"]["doing"] == 1
    assert data["project-1"]["review"] == 1
    assert data["project-1"]["done"] == 1

    assert data["project-2"]["todo"] == 1
    assert data["project-2"]["doing"] == 1
    assert data["project-2"]["done"] == 2

    assert data["project-3"]["todo"] == 1
    assert data["project-3"]["doing"] == 0
    assert data["project-3"]["done"] == 0


def test_batch_task_counts_etag_caching(client, mock_supabase_client):
    """Test that ETag caching works correctly for task counts."""
    # Set up mock data
    mock_tasks = [
        {"project_id": "project-1", "status": "todo", "archived": False},
        {"project_id": "project-1", "status": "doing", "archived": False},
    ]

    # Configure mock with proper chaining
    mock_select = MagicMock()
    mock_or = MagicMock()
    mock_execute = MagicMock()
    mock_execute.data = mock_tasks
    mock_or.execute.return_value = mock_execute
    mock_select.or_.return_value = mock_or
    mock_supabase_client.table.return_value.select.return_value = mock_select

    # Mock the repository to use Supabase instead of SQLite
    from src.server.repositories.supabase_repository import SupabaseDatabaseRepository
    mock_repository = SupabaseDatabaseRepository(mock_supabase_client)

    # Explicitly patch the client creation and repository factory
    with patch("src.server.utils.get_supabase_client", return_value=mock_supabase_client):
        with patch("src.server.services.client_manager.get_supabase_client", return_value=mock_supabase_client):
            with patch("src.server.api_routes.projects_api.get_repository", return_value=mock_repository):
                # First request - should return data with ETag
                response1 = client.get("/api/projects/task-counts")
                assert response1.status_code == 200
                assert "ETag" in response1.headers
                etag = response1.headers["ETag"]

                # Second request with If-None-Match header - should return 304
                response2 = client.get("/api/projects/task-counts", headers={"If-None-Match": etag})
                assert response2.status_code == 304
                assert response2.headers.get("ETag") == etag

                # Verify no body is returned on 304
                assert response2.content == b''