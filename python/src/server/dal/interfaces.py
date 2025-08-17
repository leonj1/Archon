"""
Database Interface Definitions

Abstract base classes defining the contracts for database and vector store operations.
All database adapters must implement these interfaces.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import numpy as np


@dataclass
class QueryResult:
    """Result of a database query operation"""
    data: List[Dict[str, Any]]
    count: Optional[int] = None
    error: Optional[str] = None
    affected_rows: Optional[int] = None
    
    @property
    def success(self) -> bool:
        """Check if query was successful"""
        return self.error is None
    
    @property
    def first(self) -> Optional[Dict[str, Any]]:
        """Get first result or None"""
        return self.data[0] if self.data else None


@dataclass
class VectorSearchResult:
    """Result of a vector similarity search"""
    id: str
    score: float
    metadata: Dict[str, Any]
    content: Optional[str] = None
    embedding: Optional[np.ndarray] = None


class TransactionState(Enum):
    """Transaction states"""
    PENDING = "pending"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"


class IDatabase(ABC):
    """
    Abstract base class for database operations.
    All database adapters must implement this interface.
    """
    
    @abstractmethod
    async def connect(self) -> None:
        """
        Establish database connection.
        Should handle connection pooling and initialization.
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """
        Close database connection.
        Should clean up resources and close connection pool.
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if database connection is healthy.
        
        Returns:
            True if connection is healthy, False otherwise
        """
        pass
    
    @abstractmethod
    async def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> QueryResult:
        """
        Execute raw SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters for safe substitution
            
        Returns:
            QueryResult with execution results
        """
        pass
    
    @abstractmethod
    async def select(
        self,
        table: str,
        columns: List[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> QueryResult:
        """
        Select records from table.
        
        Args:
            table: Table name
            columns: List of columns to select (default: all)
            filters: Filter conditions as key-value pairs
            order_by: ORDER BY clause
            limit: Maximum number of records
            offset: Number of records to skip
            
        Returns:
            QueryResult with selected records
        """
        pass
    
    @abstractmethod
    async def insert(
        self,
        table: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        returning: Optional[List[str]] = None,
    ) -> QueryResult:
        """
        Insert records into table.
        
        Args:
            table: Table name
            data: Record(s) to insert
            returning: Columns to return after insert
            
        Returns:
            QueryResult with inserted records
        """
        pass
    
    @abstractmethod
    async def update(
        self,
        table: str,
        data: Dict[str, Any],
        filters: Dict[str, Any],
        returning: Optional[List[str]] = None,
    ) -> QueryResult:
        """
        Update records in table.
        
        Args:
            table: Table name
            data: Fields to update
            filters: Filter conditions for records to update
            returning: Columns to return after update
            
        Returns:
            QueryResult with updated records
        """
        pass
    
    @abstractmethod
    async def delete(
        self,
        table: str,
        filters: Dict[str, Any],
        returning: Optional[List[str]] = None,
    ) -> QueryResult:
        """
        Delete records from table.
        
        Args:
            table: Table name
            filters: Filter conditions for records to delete
            returning: Columns to return after delete
            
        Returns:
            QueryResult with deleted records
        """
        pass
    
    @abstractmethod
    async def upsert(
        self,
        table: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        conflict_columns: List[str],
        update_columns: Optional[List[str]] = None,
        returning: Optional[List[str]] = None,
    ) -> QueryResult:
        """
        Insert or update records (UPSERT operation).
        
        Args:
            table: Table name
            data: Record(s) to insert or update
            conflict_columns: Columns that determine conflict
            update_columns: Columns to update on conflict (default: all)
            returning: Columns to return after operation
            
        Returns:
            QueryResult with affected records
        """
        pass
    
    @abstractmethod
    async def begin_transaction(self) -> "ITransaction":
        """
        Begin a database transaction.
        
        Returns:
            Transaction context manager
        """
        pass
    
    async def count(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Count records in table.
        
        Args:
            table: Table name
            filters: Filter conditions
            
        Returns:
            Number of records
        """
        result = await self.execute(
            f"SELECT COUNT(*) as count FROM {table}",
            params=filters
        )
        return result.first.get("count", 0) if result.success else 0
    
    async def exists(
        self,
        table: str,
        filters: Dict[str, Any],
    ) -> bool:
        """
        Check if record exists.
        
        Args:
            table: Table name
            filters: Filter conditions
            
        Returns:
            True if record exists, False otherwise
        """
        count = await self.count(table, filters)
        return count > 0


class ITransaction(ABC):
    """
    Abstract base class for database transactions.
    Provides context manager interface for transaction handling.
    """
    
    def __init__(self, database: IDatabase):
        self.database = database
        self.state = TransactionState.PENDING
    
    @abstractmethod
    async def commit(self) -> None:
        """Commit the transaction"""
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the transaction"""
        pass
    
    async def __aenter__(self) -> "ITransaction":
        """Enter transaction context"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit transaction context with automatic rollback on error"""
        if exc_type is not None:
            await self.rollback()
        elif self.state == TransactionState.PENDING:
            await self.commit()


class IVectorStore(ABC):
    """
    Abstract base class for vector database operations.
    Handles embedding storage and similarity search.
    """
    
    @abstractmethod
    async def create_collection(
        self,
        name: str,
        dimension: int,
        metric: str = "cosine",
        metadata_schema: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Create a vector collection/index.
        
        Args:
            name: Collection name
            dimension: Vector dimension
            metric: Distance metric (cosine, euclidean, dot_product)
            metadata_schema: Schema for metadata fields
            
        Returns:
            True if created successfully
        """
        pass
    
    @abstractmethod
    async def delete_collection(self, name: str) -> bool:
        """
        Delete a vector collection.
        
        Args:
            name: Collection name
            
        Returns:
            True if deleted successfully
        """
        pass
    
    @abstractmethod
    async def list_collections(self) -> List[Dict[str, Any]]:
        """
        List all vector collections.
        
        Returns:
            List of collection metadata
        """
        pass
    
    @abstractmethod
    async def insert_vectors(
        self,
        collection: str,
        vectors: List[np.ndarray],
        ids: Optional[List[str]] = None,
        metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """
        Insert vectors with metadata.
        
        Args:
            collection: Collection name
            vectors: List of embedding vectors
            ids: Optional vector IDs (auto-generated if not provided)
            metadata: Optional metadata for each vector
            
        Returns:
            List of inserted vector IDs
        """
        pass
    
    @abstractmethod
    async def update_vectors(
        self,
        collection: str,
        ids: List[str],
        vectors: Optional[List[np.ndarray]] = None,
        metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Update vectors or their metadata.
        
        Args:
            collection: Collection name
            ids: Vector IDs to update
            vectors: Optional new vectors
            metadata: Optional new metadata
            
        Returns:
            True if updated successfully
        """
        pass
    
    @abstractmethod
    async def delete_vectors(
        self,
        collection: str,
        ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Delete vectors by ID or metadata filter.
        
        Args:
            collection: Collection name
            ids: Optional vector IDs to delete
            filters: Optional metadata filters
            
        Returns:
            Number of deleted vectors
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        collection: str,
        query_vector: np.ndarray,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True,
        include_vectors: bool = False,
    ) -> List[VectorSearchResult]:
        """
        Search for similar vectors.
        
        Args:
            collection: Collection name
            query_vector: Query embedding vector
            top_k: Number of results to return
            filters: Optional metadata filters
            include_metadata: Include metadata in results
            include_vectors: Include vectors in results
            
        Returns:
            List of search results ordered by similarity
        """
        pass
    
    @abstractmethod
    async def batch_search(
        self,
        collection: str,
        query_vectors: List[np.ndarray],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[List[VectorSearchResult]]:
        """
        Batch search for multiple query vectors.
        
        Args:
            collection: Collection name
            query_vectors: List of query vectors
            top_k: Number of results per query
            filters: Optional metadata filters
            
        Returns:
            List of search results for each query
        """
        pass
    
    @abstractmethod
    async def get_vector(
        self,
        collection: str,
        id: str,
        include_metadata: bool = True,
        include_vector: bool = False,
    ) -> Optional[VectorSearchResult]:
        """
        Get a specific vector by ID.
        
        Args:
            collection: Collection name
            id: Vector ID
            include_metadata: Include metadata
            include_vector: Include vector data
            
        Returns:
            Vector data or None if not found
        """
        pass
    
    async def health_check(self) -> bool:
        """
        Check if vector store connection is healthy.
        
        Returns:
            True if connection is healthy
        """
        try:
            # Default implementation: try to list collections
            await self.list_collections()
            return True
        except Exception:
            return False


class IDatabaseWithVectors(IDatabase, IVectorStore):
    """
    Combined interface for databases that support both relational and vector operations.
    Used for databases like PostgreSQL with pgvector or Supabase.
    """
    pass