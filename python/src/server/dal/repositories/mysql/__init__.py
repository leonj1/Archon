"""
MySQL Repository Implementations

Concrete repository implementations for MySQL database backend.
TODO: Implement MySQL-specific SQL syntax and optimizations.
"""

# For now, these are stubs that would need MySQL-specific implementations
# They inherit from Supabase implementations but would need SQL syntax adjustments

from ..supabase.project_repository import SupabaseProjectRepository as MySQLProjectRepository
from ..supabase.task_repository import SupabaseTaskRepository as MySQLTaskRepository  
from ..supabase.knowledge_repository import SupabaseKnowledgeRepository as MySQLKnowledgeRepository
from ..supabase.settings_repository import SupabaseSettingsRepository as MySQLSettingsRepository
from ..supabase.search_repository import SupabaseSearchRepository as MySQLSearchRepository

__all__ = [
    "MySQLProjectRepository",
    "MySQLTaskRepository", 
    "MySQLKnowledgeRepository",
    "MySQLSettingsRepository",
    "MySQLSearchRepository",
]