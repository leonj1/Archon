"""
Unit tests for ProjectService using FakeDatabaseRepository

This test suite demonstrates testing the ProjectService with FakeDatabaseRepository
instead of mocking Supabase directly.
"""

import pytest

from src.server.repositories import FakeDatabaseRepository
from src.server.services.projects.project_service import ProjectService


@pytest.fixture
def repository():
    """Create a fresh in-memory repository for each test."""
    return FakeDatabaseRepository()


@pytest.fixture
def project_service(repository):
    """Create a ProjectService with the fake repository."""
    return ProjectService(repository=repository)


# ========================================================================
# CREATE PROJECT TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_create_project_success(project_service):
    """Test successful project creation."""
    success, result = await project_service.create_project(
        title="E-commerce Platform",
        github_repo="https://github.com/user/ecommerce"
    )

    assert success
    assert "project" in result
    assert result["project"]["title"] == "E-commerce Platform"
    assert result["project"]["github_repo"] == "https://github.com/user/ecommerce"
    assert "id" in result["project"]
    assert "created_at" in result["project"]


@pytest.mark.asyncio
async def test_create_project_without_github_repo(project_service):
    """Test creating a project without GitHub repo."""
    success, result = await project_service.create_project(
        title="Simple Project"
    )

    assert success
    assert result["project"]["title"] == "Simple Project"
    assert result["project"]["github_repo"] is None


@pytest.mark.asyncio
async def test_create_project_empty_title_fails(project_service):
    """Test that creating a project with empty title fails."""
    success, result = await project_service.create_project(
        title=""
    )

    assert not success
    assert "error" in result
    assert "title" in result["error"].lower()


@pytest.mark.asyncio
async def test_create_project_whitespace_title_fails(project_service):
    """Test that creating a project with whitespace-only title fails."""
    success, result = await project_service.create_project(
        title="   "
    )

    assert not success
    assert "error" in result


@pytest.mark.asyncio
async def test_create_project_strips_whitespace(project_service):
    """Test that project title is trimmed."""
    success, result = await project_service.create_project(
        title="  Padded Title  "
    )

    assert success
    assert result["project"]["title"] == "Padded Title"


# ========================================================================
# LIST PROJECTS TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_list_projects_empty(project_service):
    """Test listing projects when there are none."""
    success, result = await project_service.list_projects()

    assert success
    assert result["projects"] == []
    assert result["total_count"] == 0


@pytest.mark.asyncio
async def test_list_projects_with_content(project_service, repository):
    """Test listing projects with full content."""
    # Create projects directly in repository
    project1 = await repository.create_project({
        "title": "Project 1",
        "docs": ["doc1.md", "doc2.md"],
        "features": [{"id": "f1", "data": {"label": "Auth"}}],
        "data": ["data1"]
    })

    project2 = await repository.create_project({
        "title": "Project 2",
        "docs": [],
        "features": [],
        "data": []
    })

    # List with full content
    success, result = await project_service.list_projects(include_content=True)

    assert success
    assert len(result["projects"]) == 2

    # Find projects by title
    proj1_result = next(p for p in result["projects"] if p["title"] == "Project 1")
    assert len(proj1_result["docs"]) == 2
    assert len(proj1_result["features"]) == 1
    assert len(proj1_result["data"]) == 1


@pytest.mark.asyncio
async def test_list_projects_lightweight(project_service, repository):
    """Test listing projects with lightweight stats."""
    # Create project with some data
    await repository.create_project({
        "title": "Project with Data",
        "docs": ["doc1.md", "doc2.md", "doc3.md"],
        "features": [{"id": "f1"}, {"id": "f2"}],
        "data": ["data1"]
    })

    # List without content (stats only)
    success, result = await project_service.list_projects(include_content=False)

    assert success
    assert len(result["projects"]) == 1

    project = result["projects"][0]
    assert "stats" in project
    assert project["stats"]["docs_count"] == 3
    assert project["stats"]["features_count"] == 2
    assert project["stats"]["has_data"] is True


@pytest.mark.asyncio
async def test_list_projects_ordered_by_created_at(project_service, repository):
    """Test that projects are ordered by creation date (newest first)."""
    # Create multiple projects (order matters due to timestamps)
    import asyncio
    await repository.create_project({"title": "First Project"})
    await asyncio.sleep(0.01)  # Small delay to ensure different timestamps
    await repository.create_project({"title": "Second Project"})
    await asyncio.sleep(0.01)
    await repository.create_project({"title": "Third Project"})

    # List projects
    success, result = await project_service.list_projects()

    assert success
    assert len(result["projects"]) == 3

    # Should be in reverse chronological order (newest first)
    titles = [p["title"] for p in result["projects"]]
    assert titles[0] == "Third Project"
    assert titles[2] == "First Project"


# ========================================================================
# GET PROJECT TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_get_project_success(project_service, repository):
    """Test retrieving a specific project."""
    # Create project
    project = await repository.create_project({
        "title": "Test Project",
        "description": "A test project",
        "docs": ["doc1.md"],
        "features": [{"id": "f1", "data": {"label": "Auth"}}]
    })

    # Get project
    success, result = await project_service.get_project(project["id"])

    assert success
    assert result["project"]["id"] == project["id"]
    assert result["project"]["title"] == "Test Project"
    assert result["project"]["description"] == "A test project"


@pytest.mark.asyncio
async def test_get_nonexistent_project(project_service):
    """Test getting a project that doesn't exist."""
    success, result = await project_service.get_project("nonexistent-id")

    assert not success
    assert "error" in result
    assert "not found" in result["error"].lower()


@pytest.mark.asyncio
async def test_get_project_with_linked_sources(project_service, repository):
    """Test getting a project with linked technical and business sources."""
    # Create project
    project = await repository.create_project({
        "title": "Project with Sources"
    })

    # Create sources
    tech_source = await repository.upsert_source({
        "source_id": "tech-source-1",
        "title": "Technical Documentation",
        "metadata": {}
    })

    business_source = await repository.upsert_source({
        "source_id": "business-source-1",
        "title": "Business Requirements",
        "metadata": {}
    })

    # Link sources to project
    await repository.link_project_source(
        project["id"],
        tech_source["source_id"],
        notes="technical"
    )

    await repository.link_project_source(
        project["id"],
        business_source["source_id"],
        notes="business"
    )

    # Get project
    success, result = await project_service.get_project(project["id"])

    assert success
    assert "technical_sources" in result["project"]
    assert "business_sources" in result["project"]
    assert len(result["project"]["technical_sources"]) == 1
    assert len(result["project"]["business_sources"]) == 1


# ========================================================================
# UPDATE PROJECT TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_update_project_title(project_service, repository):
    """Test updating a project's title."""
    # Create project
    project = await repository.create_project({
        "title": "Old Title"
    })

    # Update title
    success, result = await project_service.update_project(
        project_id=project["id"],
        update_fields={"title": "New Title"}
    )

    assert success
    assert result["project"]["title"] == "New Title"


@pytest.mark.asyncio
async def test_update_project_multiple_fields(project_service, repository):
    """Test updating multiple project fields at once."""
    # Create project
    project = await repository.create_project({
        "title": "Original Project",
        "description": "Original description"
    })

    # Update multiple fields
    success, result = await project_service.update_project(
        project_id=project["id"],
        update_fields={
            "title": "Updated Project",
            "description": "Updated description",
            "github_repo": "https://github.com/user/repo"
        }
    )

    assert success
    assert result["project"]["title"] == "Updated Project"
    assert result["project"]["description"] == "Updated description"
    assert result["project"]["github_repo"] == "https://github.com/user/repo"


@pytest.mark.asyncio
async def test_update_nonexistent_project(project_service):
    """Test updating a project that doesn't exist."""
    success, result = await project_service.update_project(
        project_id="nonexistent-id",
        update_fields={"title": "New Title"}
    )

    assert not success
    assert "error" in result


@pytest.mark.asyncio
async def test_update_project_pinned_unpins_others(project_service, repository):
    """Test that pinning a project unpins all others."""
    # Create three projects
    project1 = await repository.create_project({
        "title": "Project 1",
        "pinned": True
    })

    project2 = await repository.create_project({
        "title": "Project 2",
        "pinned": False
    })

    project3 = await repository.create_project({
        "title": "Project 3",
        "pinned": False
    })

    # Pin project2
    success, result = await project_service.update_project(
        project_id=project2["id"],
        update_fields={"pinned": True}
    )

    assert success

    # Verify project2 is pinned
    p2 = await repository.get_project_by_id(project2["id"])
    assert p2["pinned"] is True

    # Verify project1 is unpinned
    p1 = await repository.get_project_by_id(project1["id"])
    assert p1["pinned"] is False

    # Verify project3 is still unpinned
    p3 = await repository.get_project_by_id(project3["id"])
    assert p3["pinned"] is False


# ========================================================================
# DELETE PROJECT TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_delete_project_success(project_service, repository):
    """Test deleting a project."""
    # Create project
    project = await repository.create_project({
        "title": "Project to Delete"
    })

    # Delete it
    success, result = await project_service.delete_project(project["id"])

    assert success
    assert result["project_id"] == project["id"]
    assert "message" in result

    # Verify it's gone
    deleted_project = await repository.get_project_by_id(project["id"])
    assert deleted_project is None


@pytest.mark.asyncio
async def test_delete_project_cascades_to_tasks(project_service, repository):
    """Test that deleting a project also deletes its tasks."""
    # Create project
    project = await repository.create_project({
        "title": "Project with Tasks"
    })

    # Create tasks
    task1 = await repository.create_task({
        "project_id": project["id"],
        "title": "Task 1",
        "status": "todo"
    })

    task2 = await repository.create_task({
        "project_id": project["id"],
        "title": "Task 2",
        "status": "doing"
    })

    # Delete project
    success, result = await project_service.delete_project(project["id"])

    assert success
    assert result["deleted_tasks"] == 2

    # Verify tasks are gone
    task1_check = await repository.get_task_by_id(task1["id"])
    task2_check = await repository.get_task_by_id(task2["id"])
    assert task1_check is None
    assert task2_check is None


@pytest.mark.asyncio
async def test_delete_nonexistent_project(project_service):
    """Test deleting a project that doesn't exist."""
    success, result = await project_service.delete_project("nonexistent-id")

    assert not success
    assert "error" in result


# ========================================================================
# GET PROJECT FEATURES TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_get_project_features_success(project_service, repository):
    """Test getting features from a project."""
    # Create project with features
    project = await repository.create_project({
        "title": "Project with Features",
        "features": [
            {
                "id": "feat-1",
                "type": "page",
                "data": {
                    "label": "User Authentication",
                    "type": "technical"
                }
            },
            {
                "id": "feat-2",
                "type": "page",
                "data": {
                    "label": "Payment Processing",
                    "type": "business"
                }
            }
        ]
    })

    # Get features
    success, result = await project_service.get_project_features(project["id"])

    assert success
    assert len(result["features"]) == 2
    assert result["count"] == 2

    # Check feature structure
    labels = [f["label"] for f in result["features"]]
    assert "User Authentication" in labels
    assert "Payment Processing" in labels


@pytest.mark.asyncio
async def test_get_project_features_empty(project_service, repository):
    """Test getting features from a project with no features."""
    # Create project without features
    project = await repository.create_project({
        "title": "Empty Project",
        "features": []
    })

    # Get features
    success, result = await project_service.get_project_features(project["id"])

    assert success
    assert result["features"] == []
    assert result["count"] == 0


@pytest.mark.asyncio
async def test_get_features_nonexistent_project(project_service):
    """Test getting features from a project that doesn't exist."""
    success, result = await project_service.get_project_features("nonexistent-id")

    assert not success
    assert "error" in result


@pytest.mark.asyncio
async def test_get_project_features_filters_valid_features(project_service, repository):
    """Test that only valid features with proper structure are returned."""
    # Create project with mixed feature formats
    project = await repository.create_project({
        "title": "Project with Mixed Features",
        "features": [
            {
                "id": "feat-1",
                "type": "page",
                "data": {
                    "label": "Valid Feature",
                    "type": "technical"
                }
            },
            {
                "id": "feat-2",
                # Missing 'data' or 'data.label' - should be filtered out
                "type": "page"
            },
            "invalid-string-feature"  # Invalid format
        ]
    })

    # Get features
    success, result = await project_service.get_project_features(project["id"])

    assert success
    # Only 1 valid feature should be returned
    assert len(result["features"]) == 1
    assert result["features"][0]["label"] == "Valid Feature"


# ========================================================================
# INTEGRATION TESTS
# ========================================================================


@pytest.mark.asyncio
async def test_full_project_lifecycle(project_service, repository):
    """Test creating, updating, and deleting a project."""
    # 1. Create project
    success, create_result = await project_service.create_project(
        title="Lifecycle Test Project",
        github_repo="https://github.com/test/repo"
    )
    assert success
    project_id = create_result["project"]["id"]

    # 2. Verify it exists
    success, get_result = await project_service.get_project(project_id)
    assert success
    assert get_result["project"]["title"] == "Lifecycle Test Project"

    # 3. Update it
    success, update_result = await project_service.update_project(
        project_id=project_id,
        update_fields={
            "title": "Updated Project",
            "description": "New description"
        }
    )
    assert success
    assert update_result["project"]["title"] == "Updated Project"

    # 4. Delete it
    success, delete_result = await project_service.delete_project(project_id)
    assert success

    # 5. Verify it's gone
    success, final_result = await project_service.get_project(project_id)
    assert not success
