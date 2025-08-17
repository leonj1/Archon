"""Simple test configuration for Archon - Essential tests only."""

import os
from unittest.mock import MagicMock, patch, AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.server.dal.interfaces import QueryResult

# Set test environment
os.environ["TEST_MODE"] = "true"
os.environ["TESTING"] = "true"
# Set fake database credentials to prevent connection attempts
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_SERVICE_KEY"] = "test-key"
# Set required port environment variables for ServiceDiscovery
os.environ.setdefault("ARCHON_SERVER_PORT", "8181")
os.environ.setdefault("ARCHON_MCP_PORT", "8051")
os.environ.setdefault("ARCHON_AGENTS_PORT", "8052")


@pytest.fixture(autouse=True)
def prevent_real_db_calls():
    """Automatically prevent any real database calls in all tests."""
    with patch("supabase.create_client") as mock_create:
        # Make create_client raise an error if called without our mock
        mock_create.side_effect = Exception("Real database calls are not allowed in tests!")
        yield


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    mock_client = MagicMock()

    # Mock table operations with chaining support
    mock_table = MagicMock()
    mock_select = MagicMock()
    mock_insert = MagicMock()
    mock_update = MagicMock()
    mock_delete = MagicMock()

    # Setup method chaining for select
    mock_select.execute.return_value.data = []
    mock_select.eq.return_value = mock_select
    mock_select.neq.return_value = mock_select
    mock_select.order.return_value = mock_select
    mock_select.limit.return_value = mock_select
    mock_table.select.return_value = mock_select

    # Setup method chaining for insert
    mock_insert.execute.return_value.data = [{"id": "test-id"}]
    mock_table.insert.return_value = mock_insert

    # Setup method chaining for update
    mock_update.execute.return_value.data = [{"id": "test-id"}]
    mock_update.eq.return_value = mock_update
    mock_table.update.return_value = mock_update

    # Setup method chaining for delete
    mock_delete.execute.return_value.data = []
    mock_delete.eq.return_value = mock_delete
    mock_table.delete.return_value = mock_delete

    # Make table() return the mock table
    mock_client.table.return_value = mock_table

    # Mock auth operations
    mock_client.auth = MagicMock()
    mock_client.auth.get_user.return_value = None

    # Mock storage operations
    mock_client.storage = MagicMock()

    return mock_client


@pytest.fixture
def mock_database_connection():
    """Mock database connection that returns QueryResult objects."""
    mock_db = AsyncMock()
    
    # Configure default responses to return successful QueryResult objects
    mock_db.select.return_value = QueryResult(data=[])
    mock_db.insert.return_value = QueryResult(data=[{"id": "test-id"}])
    mock_db.update.return_value = QueryResult(data=[{"id": "test-id"}])
    mock_db.delete.return_value = QueryResult(data=[])
    mock_db.upsert.return_value = QueryResult(data=[{"id": "test-id"}])
    
    return mock_db


@pytest.fixture
def client(mock_supabase_client, mock_database_connection):
    """FastAPI test client with mocked database."""
    # Patch all the ways Supabase client can be created
    with patch(
        "src.server.services.client_manager.create_client", return_value=mock_supabase_client
    ):
        with patch(
            "src.server.services.client_manager.get_supabase_client",
            return_value=mock_supabase_client,
        ):
            with patch("supabase.create_client", return_value=mock_supabase_client):
                # Mock the connection manager for the new repository pattern
                with patch("src.server.services.client_manager.get_connection_manager") as mock_manager:
                    # Setup mock connection manager with proper async context manager behavior
                    mock_conn_mgr = mock_manager.return_value
                    
                    # Create async context managers that return the mock database connection
                    mock_conn_mgr.get_reader.return_value.__aenter__ = AsyncMock(return_value=mock_database_connection)
                    mock_conn_mgr.get_reader.return_value.__aexit__ = AsyncMock(return_value=None)
                    mock_conn_mgr.get_primary.return_value.__aenter__ = AsyncMock(return_value=mock_database_connection)
                    mock_conn_mgr.get_primary.return_value.__aexit__ = AsyncMock(return_value=None)
                    
                    # Import app after patching to ensure mocks are used
                    from src.server.main import app

                    return TestClient(app)


@pytest.fixture
def test_project():
    """Simple test project data."""
    return {"title": "Test Project", "description": "A test project for essential tests"}


@pytest.fixture
def test_task():
    """Simple test task data."""
    return {
        "title": "Test Task",
        "description": "A test task for essential tests",
        "status": "todo",
        "assignee": "User",
    }


@pytest.fixture
def test_knowledge_item():
    """Simple test knowledge item data."""
    return {
        "url": "https://example.com/test",
        "title": "Test Knowledge Item",
        "content": "This is test content for knowledge base",
        "source_id": "test-source",
    }
