"""
PostgreSQL Adapter for Database Abstraction Layer

Implements IDatabase interface for PostgreSQL databases with pgvector support.
Provides native vector search capabilities and full compatibility with Archon's data model.
"""

import json
import struct
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import asyncpg
import numpy as np

from ...config.logfire_config import search_logger
from ..interfaces import (
    IDatabase,
    ITransaction,
    IVectorStore,
    QueryResult,
    TransactionState,
    VectorSearchResult,
)


class PostgreSQLTransaction(ITransaction):
    """PostgreSQL transaction implementation"""
    
    def __init__(self, connection: asyncpg.Connection, database: IDatabase):
        super().__init__(database)
        self.connection = connection
        self.transaction = None
    
    async def __aenter__(self):
        """Start transaction"""
        self.transaction = self.connection.transaction()
        await self.transaction.start()
        return self
    
    async def commit(self):
        """Commit transaction"""
        if self.transaction and self.state == TransactionState.PENDING:
            await self.transaction.commit()
            self.state = TransactionState.COMMITTED
            self.transaction = None
    
    async def rollback(self):
        """Rollback transaction"""
        if self.transaction and self.state == TransactionState.PENDING:
            await self.transaction.rollback()
            self.state = TransactionState.ROLLED_BACK
            self.transaction = None
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit transaction context"""
        if exc_type is not None:
            await self.rollback()
        elif self.state == TransactionState.PENDING:
            await self.commit()


class PostgreSQLAdapter(IDatabase, IVectorStore):
    """
    PostgreSQL adapter implementation with pgvector support.
    Provides full IDatabase and IVectorStore interface compatibility.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "archon_db",
        user: str = "archon",
        password: str = "archon_secure_password",
        connection_string: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize PostgreSQL adapter.
        
        Args:
            host: PostgreSQL server host
            port: PostgreSQL server port
            database: Database name
            user: Username
            password: Password
            connection_string: Optional full connection string (overrides other params)
            **kwargs: Additional connection parameters
        """
        if connection_string:
            self.connection_string = connection_string
        else:
            # Build connection string from parameters
            self.connection_string = (
                f"postgresql://{user}:{password}@{host}:{port}/{database}"
            )
        
        self.pool: Optional[asyncpg.Pool] = None
        self.table_prefix = kwargs.get("table_prefix", "archon_")
    
    async def connect(self) -> None:
        """Establish database connection pool"""
        if not self.pool:
            try:
                self.pool = await asyncpg.create_pool(
                    self.connection_string,
                    min_size=5,
                    max_size=20,
                    command_timeout=60,
                    server_settings={
                        'application_name': 'archon_app',
                    }
                )
                
                # Enable pgvector extension
                async with self.pool.acquire() as conn:
                    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
                    await conn.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
                
                search_logger.info("PostgreSQL connection pool established with pgvector support")
            except Exception as e:
                search_logger.error(f"Failed to connect to PostgreSQL: {e}")
                raise
    
    async def disconnect(self) -> None:
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            search_logger.info("PostgreSQL connection pool closed")
    
    async def health_check(self) -> bool:
        """Check database health"""
        if not self.pool:
            return False
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                return result == 1
        except Exception as e:
            search_logger.error(f"PostgreSQL health check failed: {e}")
            return False
    
    async def execute(self, query: str, params: Optional[Union[list, dict]] = None) -> QueryResult:
        """Execute raw SQL query"""
        if not self.pool:
            await self.connect()
        
        try:
            async with self.pool.acquire() as conn:
                if params:
                    if isinstance(params, dict):
                        # Convert dict params to positional for asyncpg
                        result = await conn.fetch(query, *params.values())
                    else:
                        result = await conn.fetch(query, *params)
                else:
                    result = await conn.fetch(query)
                
                return QueryResult(
                    data=[dict(row) for row in result] if result else [],
                    count=len(result) if result else 0
                )
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
        offset: Optional[int] = None
    ) -> QueryResult:
        """Select records from table"""
        if not self.pool:
            await self.connect()
        
        try:
            # Build query
            columns_str = ", ".join(columns) if columns else "*"
            query_parts = [f"SELECT {columns_str} FROM {self.table_prefix}{table}"]
            
            params = []
            param_count = 0
            
            # Add WHERE clause
            if filters:
                where_clauses = []
                for key, value in filters.items():
                    param_count += 1
                    if value is None:
                        where_clauses.append(f"{key} IS NULL")
                    else:
                        where_clauses.append(f"{key} = ${param_count}")
                        params.append(value)
                
                if where_clauses:
                    query_parts.append(f"WHERE {' AND '.join(where_clauses)}")
            
            # Add ORDER BY
            if order_by:
                query_parts.append(f"ORDER BY {order_by}")
            
            # Add LIMIT
            if limit:
                param_count += 1
                query_parts.append(f"LIMIT ${param_count}")
                params.append(limit)
            
            # Add OFFSET
            if offset:
                param_count += 1
                query_parts.append(f"OFFSET ${param_count}")
                params.append(offset)
            
            query = " ".join(query_parts)
            
            async with self.pool.acquire() as conn:
                result = await conn.fetch(query, *params)
                
                return QueryResult(
                    data=[dict(row) for row in result],
                    count=len(result)
                )
        except Exception as e:
            search_logger.error(f"Select query failed: {e}")
            return QueryResult(data=[], error=str(e))
    
    async def insert(
        self,
        table: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> QueryResult:
        """Insert records into table"""
        if not self.pool:
            await self.connect()
        
        if isinstance(data, dict):
            data = [data]
        
        if not data:
            return QueryResult(data=[], error="No data to insert")
        
        try:
            async with self.pool.acquire() as conn:
                inserted_ids = []
                
                for record in data:
                    # Generate UUID if id not provided
                    if 'id' not in record:
                        record['id'] = str(uuid4())
                    
                    # Handle JSON fields
                    for key, value in record.items():
                        if isinstance(value, (dict, list)):
                            record[key] = json.dumps(value)
                    
                    columns = list(record.keys())
                    values = list(record.values())
                    
                    # Build query with parameterized values
                    placeholders = ", ".join([f"${i+1}" for i in range(len(values))])
                    query = f"""
                        INSERT INTO {self.table_prefix}{table} ({', '.join(columns)})
                        VALUES ({placeholders})
                        RETURNING id
                    """
                    
                    result = await conn.fetchval(query, *values)
                    inserted_ids.append(result)
                
                return QueryResult(
                    data=[{"id": id} for id in inserted_ids],
                    count=len(inserted_ids)
                )
        except Exception as e:
            search_logger.error(f"Insert query failed: {e}")
            return QueryResult(data=[], error=str(e))
    
    async def update(
        self,
        table: str,
        data: Dict[str, Any],
        filters: Dict[str, Any]
    ) -> QueryResult:
        """Update records in table"""
        if not self.pool:
            await self.connect()
        
        if not data or not filters:
            return QueryResult(data=[], error="Data and filters are required for update")
        
        try:
            async with self.pool.acquire() as conn:
                # Handle JSON fields
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        data[key] = json.dumps(value)
                
                # Build SET clause
                set_clauses = []
                params = []
                param_count = 0
                
                for key, value in data.items():
                    param_count += 1
                    set_clauses.append(f"{key} = ${param_count}")
                    params.append(value)
                
                # Build WHERE clause
                where_clauses = []
                for key, value in filters.items():
                    param_count += 1
                    if value is None:
                        where_clauses.append(f"{key} IS NULL")
                    else:
                        where_clauses.append(f"{key} = ${param_count}")
                        params.append(value)
                
                query = f"""
                    UPDATE {self.table_prefix}{table}
                    SET {', '.join(set_clauses)}
                    WHERE {' AND '.join(where_clauses)}
                    RETURNING id
                """
                
                result = await conn.fetch(query, *params)
                
                return QueryResult(
                    data=[{"id": row["id"]} for row in result],
                    count=len(result)
                )
        except Exception as e:
            search_logger.error(f"Update query failed: {e}")
            return QueryResult(data=[], error=str(e))
    
    async def delete(
        self,
        table: str,
        filters: Dict[str, Any]
    ) -> QueryResult:
        """Delete records from table"""
        if not self.pool:
            await self.connect()
        
        if not filters:
            return QueryResult(data=[], error="Filters are required for delete")
        
        try:
            async with self.pool.acquire() as conn:
                # Build WHERE clause
                where_clauses = []
                params = []
                param_count = 0
                
                for key, value in filters.items():
                    param_count += 1
                    if value is None:
                        where_clauses.append(f"{key} IS NULL")
                    else:
                        where_clauses.append(f"{key} = ${param_count}")
                        params.append(value)
                
                query = f"""
                    DELETE FROM {self.table_prefix}{table}
                    WHERE {' AND '.join(where_clauses)}
                    RETURNING id
                """
                
                result = await conn.fetch(query, *params)
                
                return QueryResult(
                    data=[{"id": row["id"]} for row in result],
                    count=len(result)
                )
        except Exception as e:
            search_logger.error(f"Delete query failed: {e}")
            return QueryResult(data=[], error=str(e))
    
    async def upsert(
        self,
        table: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        conflict_columns: List[str]
    ) -> QueryResult:
        """Insert or update records"""
        if not self.pool:
            await self.connect()
        
        if isinstance(data, dict):
            data = [data]
        
        if not data or not conflict_columns:
            return QueryResult(
                data=[],
                error="Data and conflict columns are required for upsert"
            )
        
        try:
            async with self.pool.acquire() as conn:
                upserted_ids = []
                
                for record in data:
                    # Generate UUID if id not provided
                    if 'id' not in record:
                        record['id'] = str(uuid4())
                    
                    # Handle JSON fields
                    for key, value in record.items():
                        if isinstance(value, (dict, list)):
                            record[key] = json.dumps(value)
                    
                    columns = list(record.keys())
                    values = list(record.values())
                    
                    # Build INSERT query
                    placeholders = ", ".join([f"${i+1}" for i in range(len(values))])
                    
                    # Build UPDATE clause for conflict
                    update_clauses = []
                    for col in columns:
                        if col not in conflict_columns:
                            update_clauses.append(f"{col} = EXCLUDED.{col}")
                    
                    query = f"""
                        INSERT INTO {self.table_prefix}{table} ({', '.join(columns)})
                        VALUES ({placeholders})
                        ON CONFLICT ({', '.join(conflict_columns)})
                        DO UPDATE SET {', '.join(update_clauses)}
                        RETURNING id
                    """
                    
                    result = await conn.fetchval(query, *values)
                    upserted_ids.append(result)
                
                return QueryResult(
                    data=[{"id": id} for id in upserted_ids],
                    count=len(upserted_ids)
                )
        except Exception as e:
            search_logger.error(f"Upsert query failed: {e}")
            return QueryResult(data=[], error=str(e))
    
    async def transaction(self) -> PostgreSQLTransaction:
        """Start a database transaction"""
        if not self.pool:
            await self.connect()
        
        conn = await self.pool.acquire()
        return PostgreSQLTransaction(conn, self)
    
    async def begin_transaction(self) -> PostgreSQLTransaction:
        """Begin a database transaction (alias for transaction)"""
        return await self.transaction()
    
    # Vector Store Implementation
    
    async def create_collection(
        self,
        name: str,
        dimension: int = 1536,
        metric: str = "cosine"
    ) -> bool:
        """Create a vector collection (table with vector column)"""
        if not self.pool:
            await self.connect()
        
        try:
            async with self.pool.acquire() as conn:
                # Create table with vector column
                query = f"""
                    CREATE TABLE IF NOT EXISTS {self.table_prefix}{name} (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        content TEXT,
                        metadata JSONB DEFAULT '{{}}',
                        embedding vector({dimension}),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                await conn.execute(query)
                
                # Create index based on metric
                if metric == "cosine":
                    index_op = "vector_cosine_ops"
                elif metric == "euclidean":
                    index_op = "vector_l2_ops"
                else:
                    index_op = "vector_ip_ops"  # inner product
                
                index_query = f"""
                    CREATE INDEX IF NOT EXISTS idx_{name}_embedding
                    ON {self.table_prefix}{name}
                    USING ivfflat (embedding {index_op})
                    WITH (lists = 100)
                """
                await conn.execute(index_query)
                
                search_logger.info(f"Created vector collection: {name}")
                return True
        except Exception as e:
            search_logger.error(f"Failed to create vector collection: {e}")
            return False
    
    async def insert_vectors(
        self,
        collection: str,
        vectors: List[np.ndarray],
        metadata: List[Dict[str, Any]]
    ) -> bool:
        """Insert vectors with metadata"""
        if not self.pool:
            await self.connect()
        
        try:
            async with self.pool.acquire() as conn:
                for vector, meta in zip(vectors, metadata):
                    # Convert numpy array to list for PostgreSQL
                    vector_list = vector.tolist()
                    
                    query = f"""
                        INSERT INTO {self.table_prefix}{collection}
                        (content, metadata, embedding)
                        VALUES ($1, $2, $3::vector)
                    """
                    
                    await conn.execute(
                        query,
                        meta.get("content", ""),
                        json.dumps(meta),
                        vector_list
                    )
                
                search_logger.info(f"Inserted {len(vectors)} vectors into {collection}")
                return True
        except Exception as e:
            search_logger.error(f"Failed to insert vectors: {e}")
            return False
    
    async def search(
        self,
        collection: str,
        query_vector: np.ndarray,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """Search for similar vectors"""
        if not self.pool:
            await self.connect()
        
        try:
            async with self.pool.acquire() as conn:
                # Build query with vector similarity
                vector_list = query_vector.tolist()
                
                where_clause = ""
                params = [vector_list, top_k]
                param_count = 2
                
                if filters:
                    where_conditions = []
                    for key, value in filters.items():
                        param_count += 1
                        where_conditions.append(f"metadata->>${param_count-1} = ${param_count}")
                        params.extend([key, str(value)])
                    
                    if where_conditions:
                        where_clause = f"WHERE {' AND '.join(where_conditions)}"
                
                query = f"""
                    SELECT id, content, metadata,
                           1 - (embedding <=> $1::vector) as similarity
                    FROM {self.table_prefix}{collection}
                    {where_clause}
                    ORDER BY embedding <=> $1::vector
                    LIMIT $2
                """
                
                result = await conn.fetch(query, *params)
                
                return [
                    VectorSearchResult(
                        id=str(row["id"]),
                        score=float(row["similarity"]),
                        metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                        content=row.get("content")
                    )
                    for row in result
                ]
        except Exception as e:
            search_logger.error(f"Vector search failed: {e}")
            return []
    
    async def delete_vectors(
        self,
        collection: str,
        ids: List[str]
    ) -> bool:
        """Delete vectors by ID"""
        if not self.pool:
            await self.connect()
        
        try:
            async with self.pool.acquire() as conn:
                query = f"""
                    DELETE FROM {self.table_prefix}{collection}
                    WHERE id = ANY($1::uuid[])
                """
                
                await conn.execute(query, ids)
                search_logger.info(f"Deleted {len(ids)} vectors from {collection}")
                return True
        except Exception as e:
            search_logger.error(f"Failed to delete vectors: {e}")
            return False
    
    async def update_metadata(
        self,
        collection: str,
        id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Update vector metadata"""
        if not self.pool:
            await self.connect()
        
        try:
            async with self.pool.acquire() as conn:
                query = f"""
                    UPDATE {self.table_prefix}{collection}
                    SET metadata = $1
                    WHERE id = $2::uuid
                """
                
                await conn.execute(query, json.dumps(metadata), id)
                search_logger.info(f"Updated metadata for vector {id} in {collection}")
                return True
        except Exception as e:
            search_logger.error(f"Failed to update vector metadata: {e}")
            return False
    
    async def delete_collection(self, name: str) -> bool:
        """Delete a vector collection (drop table)"""
        if not self.pool:
            await self.connect()
        
        try:
            async with self.pool.acquire() as conn:
                # Drop the table
                query = f"DROP TABLE IF EXISTS {self.table_prefix}{name} CASCADE"
                await conn.execute(query)
                search_logger.info(f"Deleted vector collection: {name}")
                return True
        except Exception as e:
            search_logger.error(f"Failed to delete vector collection: {e}")
            return False
    
    async def list_collections(self) -> List[Dict[str, Any]]:
        """List all vector collections"""
        if not self.pool:
            await self.connect()
        
        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT table_name, 
                           pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                           n_live_tup as count
                    FROM information_schema.tables
                    LEFT JOIN pg_stat_user_tables ON table_name = tablename
                    WHERE table_schema = 'public' 
                    AND table_name LIKE $1
                    AND column_name = 'embedding'
                    AND table_name IN (
                        SELECT table_name 
                        FROM information_schema.columns 
                        WHERE column_name = 'embedding'
                    )
                """
                
                result = await conn.fetch(query, f"{self.table_prefix}%")
                
                return [
                    {
                        "name": row["table_name"].replace(self.table_prefix, ""),
                        "size": row["size"],
                        "count": row["count"] or 0
                    }
                    for row in result
                ]
        except Exception as e:
            search_logger.error(f"Failed to list vector collections: {e}")
            return []
    
    async def update_vectors(
        self,
        collection: str,
        ids: List[str],
        vectors: List[np.ndarray],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Update existing vectors"""
        if not self.pool:
            await self.connect()
        
        try:
            async with self.pool.acquire() as conn:
                for i, (id, vector) in enumerate(zip(ids, vectors)):
                    vector_list = vector.tolist()
                    
                    if metadata and i < len(metadata):
                        query = f"""
                            UPDATE {self.table_prefix}{collection}
                            SET embedding = $1::vector, metadata = $2
                            WHERE id = $3::uuid
                        """
                        await conn.execute(
                            query,
                            vector_list,
                            json.dumps(metadata[i]),
                            id
                        )
                    else:
                        query = f"""
                            UPDATE {self.table_prefix}{collection}
                            SET embedding = $1::vector
                            WHERE id = $2::uuid
                        """
                        await conn.execute(query, vector_list, id)
                
                search_logger.info(f"Updated {len(ids)} vectors in {collection}")
                return True
        except Exception as e:
            search_logger.error(f"Failed to update vectors: {e}")
            return False
    
    async def batch_search(
        self,
        collection: str,
        query_vectors: List[np.ndarray],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[List[VectorSearchResult]]:
        """Batch search for similar vectors"""
        if not self.pool:
            await self.connect()
        
        results = []
        for query_vector in query_vectors:
            result = await self.search(collection, query_vector, top_k, filters)
            results.append(result)
        
        return results
    
    async def get_vector(
        self,
        collection: str,
        id: str
    ) -> Optional[VectorSearchResult]:
        """Get a specific vector by ID"""
        if not self.pool:
            await self.connect()
        
        try:
            async with self.pool.acquire() as conn:
                query = f"""
                    SELECT id, content, metadata, embedding
                    FROM {self.table_prefix}{collection}
                    WHERE id = $1::uuid
                """
                
                row = await conn.fetchrow(query, id)
                
                if row:
                    return VectorSearchResult(
                        id=str(row["id"]),
                        score=1.0,  # Perfect match for direct ID lookup
                        metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                        content=row.get("content")
                    )
                return None
        except Exception as e:
            search_logger.error(f"Failed to get vector: {e}")
            return None