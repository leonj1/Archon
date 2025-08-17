"""
PostgreSQL Repository Implementations

Concrete repository implementations for PostgreSQL database backend.
TODO: Implement PostgreSQL-specific optimizations.
"""

# For now, we can inherit from Supabase implementations since Supabase is PostgreSQL-based
# In the future, these would be optimized for direct PostgreSQL connections

from ..supabase.project_repository import SupabaseProjectRepository as PostgreSQLProjectRepository
from ..supabase.task_repository import SupabaseTaskRepository as PostgreSQLTaskRepository
from ..supabase.knowledge_repository import SupabaseKnowledgeRepository as PostgreSQLKnowledgeRepository
from ..supabase.settings_repository import SupabaseSettingsRepository as PostgreSQLSettingsRepository
from ..supabase.search_repository import SupabaseSearchRepository as PostgreSQLSearchRepository

__all__ = [
    "PostgreSQLProjectRepository",
    "PostgreSQLTaskRepository",
    "PostgreSQLKnowledgeRepository", 
    "PostgreSQLSettingsRepository",
    "PostgreSQLSearchRepository",
]