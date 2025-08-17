"""
Base Repository Interface

Generic repository interface providing standard CRUD operations that all 
domain-specific repositories should inherit from.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from ...interfaces import IDatabase, QueryResult

# Generic type for repository entities
T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base class for all repository implementations.
    Provides standard CRUD operations that can be extended by domain-specific repositories.
    """
    
    def __init__(self, database: IDatabase, table_name: str):
        """
        Initialize repository with database connection and table name.
        
        Args:
            database: Database interface implementation
            table_name: Name of the database table this repository manages
        """
        self._database = database
        self._table_name = table_name
    
    @property
    def database(self) -> IDatabase:
        """Get the database interface."""
        return self._database
    
    @property
    def table_name(self) -> str:
        """Get the table name."""
        return self._table_name
    
    @abstractmethod
    async def create(self, entity_data: Dict[str, Any]) -> Optional[T]:
        """
        Create a new entity.
        
        Args:
            entity_data: Data for the new entity
            
        Returns:
            Created entity or None if creation failed
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            entity_id: Unique identifier for the entity
            
        Returns:
            Entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def update(self, entity_id: str, update_data: Dict[str, Any]) -> Optional[T]:
        """
        Update an existing entity.
        
        Args:
            entity_id: Unique identifier for the entity
            update_data: Fields to update
            
        Returns:
            Updated entity or None if update failed
        """
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """
        Delete an entity by ID.
        
        Args:
            entity_id: Unique identifier for the entity
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def list_all(
        self, 
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[T]:
        """
        List all entities with optional pagination and ordering.
        
        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip
            order_by: Field to order by
            
        Returns:
            List of entities
        """
        pass
    
    @abstractmethod
    async def find_by_criteria(
        self, 
        criteria: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[T]:
        """
        Find entities matching given criteria.
        
        Args:
            criteria: Search criteria as key-value pairs
            limit: Maximum number of entities to return
            offset: Number of entities to skip
            order_by: Field to order by
            
        Returns:
            List of matching entities
        """
        pass
    
    @abstractmethod
    async def count(self, criteria: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities matching optional criteria.
        
        Args:
            criteria: Optional search criteria
            
        Returns:
            Number of entities
        """
        pass
    
    @abstractmethod
    async def exists(self, entity_id: str) -> bool:
        """
        Check if entity exists by ID.
        
        Args:
            entity_id: Unique identifier for the entity
            
        Returns:
            True if entity exists, False otherwise
        """
        pass
    
    async def bulk_create(self, entities_data: List[Dict[str, Any]]) -> List[T]:
        """
        Create multiple entities in bulk.
        
        Args:
            entities_data: List of entity data dictionaries
            
        Returns:
            List of created entities
        """
        created_entities = []
        for entity_data in entities_data:
            entity = await self.create(entity_data)
            if entity:
                created_entities.append(entity)
        return created_entities
    
    async def bulk_update(
        self, 
        updates: List[Dict[str, Any]]
    ) -> List[Optional[T]]:
        """
        Update multiple entities in bulk.
        
        Args:
            updates: List of update dictionaries containing 'id' and update fields
            
        Returns:
            List of updated entities (None for failed updates)
        """
        updated_entities = []
        for update_data in updates:
            entity_id = update_data.pop('id', None)
            if entity_id:
                entity = await self.update(entity_id, update_data)
                updated_entities.append(entity)
            else:
                updated_entities.append(None)
        return updated_entities
    
    async def bulk_delete(self, entity_ids: List[str]) -> int:
        """
        Delete multiple entities in bulk.
        
        Args:
            entity_ids: List of entity IDs to delete
            
        Returns:
            Number of successfully deleted entities
        """
        deleted_count = 0
        for entity_id in entity_ids:
            if await self.delete(entity_id):
                deleted_count += 1
        return deleted_count
    
    async def health_check(self) -> bool:
        """
        Check if the repository and underlying database are healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            return await self._database.health_check()
        except Exception:
            return False
    
    async def _execute_query(
        self, 
        query: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> QueryResult:
        """
        Execute a raw SQL query through the database interface.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Query result
        """
        return await self._database.execute(query, params)
    
    def _build_where_clause(self, criteria: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """
        Build WHERE clause from criteria dictionary.
        
        Args:
            criteria: Search criteria
            
        Returns:
            Tuple of (where_clause, parameters)
        """
        if not criteria:
            return "", {}
        
        conditions = []
        params = {}
        
        for i, (key, value) in enumerate(criteria.items()):
            param_name = f"param_{i}"
            if value is None:
                conditions.append(f"{key} IS NULL")
            elif isinstance(value, list):
                placeholders = ", ".join(f":{param_name}_{j}" for j in range(len(value)))
                conditions.append(f"{key} IN ({placeholders})")
                for j, item in enumerate(value):
                    params[f"{param_name}_{j}"] = item
            else:
                conditions.append(f"{key} = :{param_name}")
                params[param_name] = value
        
        where_clause = " AND ".join(conditions)
        return f"WHERE {where_clause}" if where_clause else "", params