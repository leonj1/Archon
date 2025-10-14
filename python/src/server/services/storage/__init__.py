"""
Storage Services

Handles document and code storage operations.
"""

from .base_storage_service import BaseStorageService
from .code_storage_service import (
    add_code_examples_to_database,
    add_code_examples_to_supabase,  # Deprecated alias
    extract_code_blocks,
    generate_code_example_summary,
)
from .document_storage_service import (
    add_documents_to_database,
    add_documents_to_supabase,  # Deprecated alias
)
from .storage_services import DocumentStorageService

__all__ = [
    # Base service
    "BaseStorageService",
    # Service classes
    "DocumentStorageService",
    # Document storage utilities
    "add_documents_to_database",
    "add_documents_to_supabase",  # Deprecated - use add_documents_to_database
    # Code storage utilities
    "extract_code_blocks",
    "generate_code_example_summary",
    "add_code_examples_to_database",
    "add_code_examples_to_supabase",  # Deprecated - use add_code_examples_to_database
]
