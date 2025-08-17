"""
SQLite Repository Implementations

Concrete repository implementations for SQLite database backend.
TODO: Implement SQLite-specific SQL syntax and local file optimizations.
"""

# For now, these are stubs that would need SQLite-specific implementations
# They inherit from Supabase implementations but would need SQL syntax adjustments

from ..supabase.project_repository import SupabaseProjectRepository as SQLiteProjectRepository
from ..supabase.task_repository import SupabaseTaskRepository as SQLiteTaskRepository
from ..supabase.knowledge_repository import SupabaseKnowledgeRepository as SQLiteKnowledgeRepository  
from ..supabase.settings_repository import SupabaseSettingsRepository as SQLiteSettingsRepository
from ..supabase.search_repository import SupabaseSearchRepository as SQLiteSearchRepository

__all__ = [
    "SQLiteProjectRepository",
    "SQLiteTaskRepository",
    "SQLiteKnowledgeRepository",
    "SQLiteSettingsRepository", 
    "SQLiteSearchRepository",
]