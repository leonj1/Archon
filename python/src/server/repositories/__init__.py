"""
Repository pattern implementation for Archon Server.

This package implements the Repository Pattern to abstract database operations
and provide a clean separation between business logic and data access layers.
It includes both abstract interfaces and concrete implementations.

Package Structure:
- interfaces/: Abstract repository interfaces and contracts
- implementations/: Concrete database-specific implementations (to be added)

The repository pattern provides:
- Database abstraction and technology independence
- Improved testability through interface-based design
- Centralized data access logic
- Transaction management capabilities
- Type safety through Python generics

Example Usage:
    ```python
    from src.server.repositories.interfaces import IBaseRepository
    from src.server.repositories.implementations import SupabaseDatabase
    
    # Dependency injection
    database = SupabaseDatabase()
    user_repository = database.users
    
    # Repository operations
    user = await user_repository.create(user_data)
    users = await user_repository.list(filters={"active": True})
    ```
"""

# Import interfaces for easy access
from .interfaces import (
    IBaseRepository,
    IUnitOfWork,
    ITransactionContext,
    TransactionError,
    SavepointError,
    NestedTransactionError,
    T
)

__all__ = [
    # Interfaces
    "IBaseRepository",
    "IUnitOfWork",
    "ITransactionContext",
    
    # Type variables
    "T",
    
    # Exceptions
    "TransactionError",
    "SavepointError",
    "NestedTransactionError"
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Archon Development Team"
__description__ = "Repository pattern implementation for database abstraction"