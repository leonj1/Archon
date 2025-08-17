"""
Fake repository implementations for testing.

This module provides complete in-memory implementations of all repository interfaces
that can be used for testing without requiring a database connection.

All fake repositories:
- Implement the same interfaces as their real counterparts
- Use thread-safe in-memory storage
- Generate realistic IDs and timestamps
- Support all the same operations with proper error handling
- Include realistic behavior like cosine similarity for vector search
- Maintain data consistency and relationships
"""

from .fake_project_repository import FakeProjectRepository
from .fake_task_repository import FakeTaskRepository
from .fake_knowledge_repository import FakeKnowledgeRepository
from .fake_settings_repository import FakeSettingsRepository
from .fake_search_repository import FakeSearchRepository

__all__ = [
    "FakeProjectRepository",
    "FakeTaskRepository", 
    "FakeKnowledgeRepository",
    "FakeSettingsRepository",
    "FakeSearchRepository"
]


def create_fake_repositories():
    """
    Create a complete set of fake repositories for testing.
    
    Returns:
        dict: Dictionary containing all fake repository instances
    """
    return {
        "project": FakeProjectRepository(),
        "task": FakeTaskRepository(),
        "knowledge": FakeKnowledgeRepository(),
        "settings": FakeSettingsRepository(),
        "search": FakeSearchRepository()
    }


def clear_all_fake_repositories(repositories: dict):
    """
    Clear all data from fake repositories.
    
    Args:
        repositories: Dictionary of repository instances from create_fake_repositories()
    """
    for repo in repositories.values():
        if hasattr(repo, 'clear_all'):
            repo.clear_all()