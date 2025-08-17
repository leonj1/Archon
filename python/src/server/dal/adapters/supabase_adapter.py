"""
Supabase Adapter for Database Abstraction Layer

Maintains backward compatibility with existing Supabase implementation.
"""

import json
from typing import Any, Dict, List, Optional, Union

import numpy as np
from supabase import Client, create_client

from ...config.logfire_config import search_logger
from ..interfaces import (
    IDatabase,
    IDatabaseWithVectors,
    ITransaction,
    IVectorStore,
    QueryResult,
    TransactionState,
    VectorSearchResult,
)


class SupabaseTransaction(ITransaction):
    """Supabase doesn't support traditional transactions, this is a placeholder"""
    
    async def commit(self) -> None:
        """Commit transaction (no-op for Supabase)"""
        self.state = TransactionState.COMMITTED
    
    async def rollback(self) -> None:
        """Rollback transaction (no-op for Supabase)"""
        self.state = TransactionState.ROLLED_BACK


class SupabaseAdapter(IDatabaseWithVectors):
    """
    Adapter for Supabase (PostgreSQL + pgvector).
    Implements both IDatabase and IVectorStore interfaces.
    """
    
    def __init__(self, url: str, key: str):
        """
        Initialize Supabase adapter.
        
        Args:
            url: Supabase project URL
            key: Supabase service key
        """
        self.url = url
        self.key = key
        self.client: Optional[Client] = None
    
    async def connect(self) -> None:
        """Establish connection to Supabase"""
        if not self.client:
            self.client = create_client(self.url, self.key)
            search_logger.info("Supabase adapter connected")
    
    async def disconnect(self) -> None:
        """Disconnect from Supabase"""
        # Supabase client doesn't have explicit disconnect
        self.client = None
        search_logger.info("Supabase adapter disconnected")
    
    async def health_check(self) -> bool:
        """Check if Supabase connection is healthy"""
        if not self.client:
            return False
        
        try:
            # Try a simple query to check connection
            # Use archon_sources table which exists in the current schema
            response = self.client.table("archon_sources").select("*").limit(1).execute()
            return True
        except Exception as e:
            search_logger.error(f"Supabase health check failed: {e}")
            return False
    
    async def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> QueryResult:
        """Execute raw SQL query via Supabase RPC"""
        try:
            # Supabase doesn't directly support raw SQL in the client
            # This would need to be implemented via RPC function
            search_logger.warning("Raw SQL execution not directly supported in Supabase client")
            return QueryResult(data=[], error="Raw SQL not supported via Supabase client")
        except Exception as e:
            search_logger.error(f"Query execution failed: {e}")
            return QueryResult(data=[], error=str(e))
    
    async def select(
        self,
        table: str,
        columns: List[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> QueryResult:
        """Select records from table"""
        try:
            query = self.client.table(table)
            
            # Select columns
            if columns:
                query = query.select(",".join(columns))
            else:
                query = query.select("*")
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    if value is None:
                        query = query.is_(key, "null")
                    else:
                        query = query.eq(key, value)
            
            # Apply ordering
            if order_by:
                # Parse order_by string (e.g., "created_at DESC")
                parts = order_by.split()
                if len(parts) == 2 and parts[1].upper() == "DESC":
                    query = query.order(parts[0], desc=True)
                else:
                    query = query.order(parts[0])
            
            # Apply limit and offset
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            # Execute query
            response = query.execute()
            
            return QueryResult(
                data=response.data,
                count=response.count if hasattr(response, 'count') else len(response.data)
            )
        except Exception as e:
            search_logger.error(f"Select query failed: {e}")
            return QueryResult(data=[], error=str(e))
    
    async def insert(
        self,
        table: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        returning: Optional[List[str]] = None,
    ) -> QueryResult:
        """Insert records into table"""
        try:
            query = self.client.table(table).insert(data)
            
            # Supabase always returns inserted data by default
            response = query.execute()
            
            return QueryResult(
                data=response.data,
                affected_rows=len(response.data) if response.data else 0
            )
        except Exception as e:
            search_logger.error(f"Insert query failed: {e}")
            return QueryResult(data=[], error=str(e))
    
    async def update(
        self,
        table: str,
        data: Dict[str, Any],
        filters: Dict[str, Any],
        returning: Optional[List[str]] = None,
    ) -> QueryResult:
        """Update records in table"""
        try:
            query = self.client.table(table).update(data)
            
            # Apply filters
            for key, value in filters.items():
                if value is None:
                    query = query.is_(key, "null")
                else:
                    query = query.eq(key, value)
            
            response = query.execute()
            
            return QueryResult(
                data=response.data,
                affected_rows=len(response.data) if response.data else 0
            )
        except Exception as e:
            search_logger.error(f"Update query failed: {e}")
            return QueryResult(data=[], error=str(e))
    
    async def delete(
        self,
        table: str,
        filters: Dict[str, Any],
        returning: Optional[List[str]] = None,
    ) -> QueryResult:
        """Delete records from table"""
        try:
            query = self.client.table(table).delete()
            
            # Apply filters
            for key, value in filters.items():
                if value is None:
                    query = query.is_(key, "null")
                else:
                    query = query.eq(key, value)
            
            response = query.execute()
            
            return QueryResult(
                data=response.data,
                affected_rows=len(response.data) if response.data else 0
            )
        except Exception as e:
            search_logger.error(f"Delete query failed: {e}")
            return QueryResult(data=[], error=str(e))
    
    async def upsert(
        self,
        table: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        conflict_columns: List[str],
        update_columns: Optional[List[str]] = None,
        returning: Optional[List[str]] = None,
    ) -> QueryResult:
        """Insert or update records"""
        try:
            # Supabase upsert uses on_conflict parameter
            response = self.client.table(table).upsert(
                data,
                on_conflict=",".join(conflict_columns)
            ).execute()
            
            return QueryResult(
                data=response.data,
                affected_rows=len(response.data) if response.data else 0
            )
        except Exception as e:
            search_logger.error(f"Upsert query failed: {e}")
            return QueryResult(data=[], error=str(e))
    
    async def begin_transaction(self) -> ITransaction:
        """Begin transaction (no-op for Supabase)"""
        return SupabaseTransaction(self)
    
    # Vector store operations
    
    async def create_collection(
        self,
        name: str,
        dimension: int,
        metric: str = "cosine",
        metadata_schema: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Create vector collection (table with vector column)"""
        # This would need to be implemented via SQL/migrations
        search_logger.warning("Collection creation should be handled via migrations")
        return False
    
    async def delete_collection(self, name: str) -> bool:
        """Delete vector collection"""
        search_logger.warning("Collection deletion should be handled via migrations")
        return False
    
    async def list_collections(self) -> List[Dict[str, Any]]:
        """List vector collections"""
        # Return known collections
        return [
            {"name": "archon_crawled_pages", "dimension": 1536},
            {"name": "archon_code_examples", "dimension": 1536},
        ]
    
    async def insert_vectors(
        self,
        collection: str,
        vectors: List[np.ndarray],
        ids: Optional[List[str]] = None,
        metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """Insert vectors into collection"""
        try:
            # Prepare data for insertion
            data = []
            for i, vector in enumerate(vectors):
                record = {
                    "embedding": vector.tolist(),
                }
                
                if ids and i < len(ids):
                    record["id"] = ids[i]
                
                if metadata and i < len(metadata):
                    record["metadata"] = json.dumps(metadata[i])
                
                data.append(record)
            
            # Insert into table
            response = self.client.table(collection).insert(data).execute()
            
            # Extract and return IDs
            return [item["id"] for item in response.data]
        except Exception as e:
            search_logger.error(f"Vector insertion failed: {e}")
            return []
    
    async def update_vectors(
        self,
        collection: str,
        ids: List[str],
        vectors: Optional[List[np.ndarray]] = None,
        metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """Update vectors or metadata"""
        try:
            for i, id in enumerate(ids):
                update_data = {}
                
                if vectors and i < len(vectors):
                    update_data["embedding"] = vectors[i].tolist()
                
                if metadata and i < len(metadata):
                    update_data["metadata"] = json.dumps(metadata[i])
                
                if update_data:
                    self.client.table(collection).update(update_data).eq("id", id).execute()
            
            return True
        except Exception as e:
            search_logger.error(f"Vector update failed: {e}")
            return False
    
    async def delete_vectors(
        self,
        collection: str,
        ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Delete vectors from collection"""
        try:
            query = self.client.table(collection).delete()
            
            if ids:
                query = query.in_("id", ids)
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.execute()
            return len(response.data)
        except Exception as e:
            search_logger.error(f"Vector deletion failed: {e}")
            return 0
    
    async def search(
        self,
        collection: str,
        query_vector: np.ndarray,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True,
        include_vectors: bool = False,
    ) -> List[VectorSearchResult]:
        """Search for similar vectors using RPC function"""
        try:
            # Call the PostgreSQL function for similarity search
            function_name = f"match_{collection}"
            
            params = {
                "query_embedding": query_vector.tolist(),
                "match_count": top_k,
            }
            
            if filters:
                params["filter"] = filters
            
            response = self.client.rpc(function_name, params).execute()
            
            # Convert results to VectorSearchResult
            results = []
            for item in response.data:
                result = VectorSearchResult(
                    id=item.get("id"),
                    score=item.get("similarity", 0.0),
                    metadata=json.loads(item.get("metadata", "{}")) if item.get("metadata") else {},
                    content=item.get("content"),
                )
                
                if include_vectors and "embedding" in item:
                    result.embedding = np.array(item["embedding"])
                
                results.append(result)
            
            return results
        except Exception as e:
            search_logger.error(f"Vector search failed: {e}")
            return []
    
    async def batch_search(
        self,
        collection: str,
        query_vectors: List[np.ndarray],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[List[VectorSearchResult]]:
        """Batch search for multiple vectors"""
        results = []
        for vector in query_vectors:
            result = await self.search(collection, vector, top_k, filters)
            results.append(result)
        return results
    
    async def get_vector(
        self,
        collection: str,
        id: str,
        include_metadata: bool = True,
        include_vector: bool = False,
    ) -> Optional[VectorSearchResult]:
        """Get specific vector by ID"""
        try:
            query = self.client.table(collection).select("*").eq("id", id)
            response = query.execute()
            
            if not response.data:
                return None
            
            item = response.data[0]
            result = VectorSearchResult(
                id=item.get("id"),
                score=1.0,  # Perfect match for direct lookup
                metadata=json.loads(item.get("metadata", "{}")) if item.get("metadata") else {},
                content=item.get("content"),
            )
            
            if include_vector and "embedding" in item:
                result.embedding = np.array(item["embedding"])
            
            return result
        except Exception as e:
            search_logger.error(f"Vector retrieval failed: {e}")
            return None