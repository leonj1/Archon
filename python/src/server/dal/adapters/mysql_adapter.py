"""
MySQL Adapter for Database Abstraction Layer

Implements IDatabase interface for MySQL 8.0+ databases.
Handles JSON fields and provides compatibility with Archon's data model.
"""

import json
import struct
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import aiomysql
import numpy as np

from ...config.logfire_config import search_logger
from ..interfaces import (
    IDatabase,
    ITransaction,
    IVectorStore,
    IDatabaseWithVectors,
    QueryResult,
    TransactionState,
    VectorSearchResult,
)


class MySQLTransaction(ITransaction):
    """MySQL transaction implementation"""
    
    def __init__(self, connection: aiomysql.Connection, database: IDatabase):
        super().__init__(database)
        self.connection = connection
        self._started = False
    
    async def __aenter__(self):
        """Start transaction"""
        await self.connection.begin()
        self._started = True
        return self
    
    async def commit(self):
        """Commit transaction"""
        if self._started and self.state == TransactionState.PENDING:
            await self.connection.commit()
            self.state = TransactionState.COMMITTED
            self._started = False
    
    async def rollback(self):
        """Rollback transaction"""
        if self._started and self.state == TransactionState.PENDING:
            await self.connection.rollback()
            self.state = TransactionState.ROLLED_BACK
            self._started = False
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit transaction context"""
        if exc_type is not None:
            await self.rollback()
        elif self.state == TransactionState.PENDING:
            await self.commit()


class MySQLAdapter(IDatabaseWithVectors):
    """
    MySQL adapter implementation.
    Provides full IDatabase interface compatibility for MySQL 8.0+ databases.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        database: str = "archon_db",
        user: str = "archon",
        password: str = "archon_secure_password",
        charset: str = "utf8mb4",
        **kwargs
    ):
        """
        Initialize MySQL adapter.
        
        Args:
            host: MySQL server host
            port: MySQL server port
            database: Database name
            user: Username
            password: Password
            charset: Character set (default: utf8mb4)
            **kwargs: Additional connection parameters
        """
        self.connection_params = {
            "host": host,
            "port": port,
            "db": database,
            "user": user,
            "password": password,
            "charset": charset,
            "autocommit": False,
            **kwargs
        }
        self.pool: Optional[aiomysql.Pool] = None
    
    async def connect(self) -> None:
        """Create connection pool"""
        if not self.pool:
            try:
                self.pool = await aiomysql.create_pool(
                    **self.connection_params,
                    minsize=5,
                    maxsize=20,
                    pool_recycle=3600,  # Recycle connections after 1 hour
                    echo=False,  # Set to True for SQL debugging
                )
                search_logger.info(
                    f"MySQL adapter connected to {self.connection_params['host']}:"
                    f"{self.connection_params['port']}/{self.connection_params['db']}"
                )
            except Exception as e:
                search_logger.error(f"Failed to connect to MySQL: {e}")
                raise
    
    async def disconnect(self) -> None:
        """Close connection pool"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None
            search_logger.info("MySQL adapter disconnected")
    
    async def health_check(self) -> bool:
        """Check if MySQL connection is healthy"""
        if not self.pool:
            return False
        
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    result = await cursor.fetchone()
                    return result == (1,)
        except Exception as e:
            search_logger.error(f"MySQL health check failed: {e}")
            return False
    
    async def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> QueryResult:
        """Execute raw SQL query"""
        if not self.pool:
            return QueryResult(data=[], error="Not connected to database")
        
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    # MySQL uses %s for parameter substitution
                    if params:
                        # Handle parameter conversion for MySQL
                        if isinstance(params, dict):
                            # Convert dict params to list for MySQL
                            param_list = list(params.values())
                        elif isinstance(params, (list, tuple)):
                            # Use list/tuple directly
                            param_list = params
                        else:
                            # Single parameter
                            param_list = [params]
                        await cursor.execute(query, param_list)
                    else:
                        await cursor.execute(query)
                    
                    # Commit if it's not a SELECT query
                    if not query.strip().upper().startswith("SELECT"):
                        await conn.commit()
                    
                    # Fetch results if available
                    if cursor.description:
                        rows = await cursor.fetchall()
                        return QueryResult(
                            data=rows,
                            count=len(rows),
                            affected_rows=cursor.rowcount
                        )
                    else:
                        return QueryResult(
                            data=[],
                            affected_rows=cursor.rowcount
                        )
        except Exception as e:
            search_logger.error(f"MySQL query execution failed: {e}")
            return QueryResult(data=[], error=str(e))
    
    def _build_where_clause(self, filters: Dict[str, Any]) -> tuple[str, List[Any]]:
        """
        Build WHERE clause from complex filter dictionary.
        
        Supports:
        - Simple equality: {"column": "value"}
        - NULL checks: {"column": None}
        - NOT equal: {"column": {"neq": "value"}}
        - OR conditions: {"column": {"or": [{"eq": "val1"}, {"is": None}]}}
        - IS NULL/NOT NULL: {"column": {"is": None}}, {"column": {"is_not": None}}
        """
        where_clauses = []
        params = []
        
        for key, value in filters.items():
            if value is None:
                where_clauses.append(f"`{key}` IS NULL")
            elif isinstance(value, dict):
                # Handle complex filter operations
                if "neq" in value:
                    where_clauses.append(f"`{key}` != %s")
                    params.append(value["neq"])
                elif "eq" in value:
                    where_clauses.append(f"`{key}` = %s")
                    params.append(value["eq"])
                elif "is" in value:
                    if value["is"] is None:
                        where_clauses.append(f"`{key}` IS NULL")
                    else:
                        where_clauses.append(f"`{key}` = %s")
                        params.append(value["is"])
                elif "is_not" in value:
                    if value["is_not"] is None:
                        where_clauses.append(f"`{key}` IS NOT NULL")
                    else:
                        where_clauses.append(f"`{key}` != %s")
                        params.append(value["is_not"])
                elif "or" in value:
                    # Handle OR conditions
                    or_clauses = []
                    for or_condition in value["or"]:
                        if isinstance(or_condition, dict):
                            if "eq" in or_condition:
                                or_clauses.append(f"`{key}` = %s")
                                params.append(or_condition["eq"])
                            elif "is" in or_condition:
                                if or_condition["is"] is None:
                                    or_clauses.append(f"`{key}` IS NULL")
                                else:
                                    or_clauses.append(f"`{key}` = %s")
                                    params.append(or_condition["is"])
                            elif "neq" in or_condition:
                                or_clauses.append(f"`{key}` != %s")
                                params.append(or_condition["neq"])
                        else:
                            # Direct value in OR
                            if or_condition is None:
                                or_clauses.append(f"`{key}` IS NULL")
                            else:
                                or_clauses.append(f"`{key}` = %s")
                                params.append(or_condition)
                    
                    if or_clauses:
                        where_clauses.append(f"({' OR '.join(or_clauses)})")
                else:
                    # Unknown operation, try to serialize it
                    search_logger.warning(f"Unknown filter operation for {key}: {value}")
                    if isinstance(value, (list, dict)):
                        # Skip complex types we don't understand
                        search_logger.error(f"Skipping unsupported filter: {key} = {value}")
                        continue
                    else:
                        where_clauses.append(f"`{key}` = %s")
                        params.append(value)
            else:
                # Simple equality
                where_clauses.append(f"`{key}` = %s")
                params.append(value)
        
        where_clause = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        return where_clause, params

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
            # Build SELECT query
            if columns and columns != ["*"]:
                columns_str = ", ".join(f"`{col}`" for col in columns)
            else:
                columns_str = "*"
            
            query = f"SELECT {columns_str} FROM `{table}`"
            params = []
            
            # Add WHERE clause using complex filter support
            if filters:
                where_clause, where_params = self._build_where_clause(filters)
                query += where_clause
                params.extend(where_params)
            
            # Add ORDER BY clause
            if order_by:
                # Parse order_by string (e.g., "created_at DESC")
                query += f" ORDER BY {order_by}"
            
            # Add LIMIT and OFFSET
            if limit:
                query += f" LIMIT {limit}"
            if offset:
                query += f" OFFSET {offset}"
            
            # Execute query
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, params)
                    rows = await cursor.fetchall()
                    
                    # Convert JSON strings to dicts
                    for row in rows:
                        for key, value in row.items():
                            if isinstance(value, str) and value.startswith('{'):
                                try:
                                    row[key] = json.loads(value)
                                except json.JSONDecodeError:
                                    pass
                    
                    return QueryResult(data=rows, count=len(rows))
        
        except Exception as e:
            search_logger.error(f"MySQL select query failed: {e}")
            return QueryResult(data=[], error=str(e))
    
    async def insert(
        self,
        table: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        returning: Optional[List[str]] = None,
    ) -> QueryResult:
        """Insert records into table"""
        try:
            # Ensure data is a list
            records = data if isinstance(data, list) else [data]
            
            if not records:
                return QueryResult(data=[], error="No data to insert")
            
            # Get column names from first record
            columns = list(records[0].keys())
            columns_str = ", ".join(f"`{col}`" for col in columns)
            
            # Build VALUES clause
            placeholders = ", ".join(["%s"] * len(columns))
            values_clause = f"({placeholders})"
            
            # Prepare values, converting JSON objects to strings
            all_values = []
            for record in records:
                values = []
                for col in columns:
                    value = record.get(col)
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value)
                    values.append(value)
                all_values.extend(values)
            
            # Build query
            if len(records) == 1:
                query = f"INSERT INTO `{table}` ({columns_str}) VALUES {values_clause}"
            else:
                values_clauses = [values_clause] * len(records)
                query = f"INSERT INTO `{table}` ({columns_str}) VALUES {', '.join(values_clauses)}"
            
            # Execute query
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, all_values)
                    await conn.commit()
                    
                    # Get inserted IDs if possible
                    last_id = cursor.lastrowid
                    
                    # If returning columns requested, fetch the inserted records
                    if returning and last_id:
                        # For single insert, we can get the record by ID
                        if len(records) == 1:
                            select_query = f"SELECT {', '.join(returning)} FROM `{table}` WHERE id = %s"
                            await cursor.execute(select_query, (last_id,))
                            result_data = await cursor.fetchall()
                        else:
                            # For batch insert, return the original data with IDs
                            result_data = records
                    else:
                        result_data = records
                    
                    return QueryResult(
                        data=result_data,
                        affected_rows=cursor.rowcount
                    )
        
        except Exception as e:
            search_logger.error(f"MySQL insert query failed: {e}")
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
            if not data:
                return QueryResult(data=[], error="No data to update")
            
            # Build SET clause
            set_clauses = []
            params = []
            
            for key, value in data.items():
                set_clauses.append(f"`{key}` = %s")
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                params.append(value)
            
            query = f"UPDATE `{table}` SET {', '.join(set_clauses)}"
            
            # Add WHERE clause using complex filter support
            if filters:
                where_clause, where_params = self._build_where_clause(filters)
                query += where_clause
                params.extend(where_params)
            else:
                search_logger.warning("UPDATE query without WHERE clause - this will update all records!")
            
            # Execute query
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, params)
                    await conn.commit()
                    
                    # If returning columns requested, fetch the updated records
                    if returning and filters:
                        select_query = f"SELECT {', '.join(returning)} FROM `{table}`"
                        where_clauses = []
                        select_params = []
                        
                        for key, value in filters.items():
                            if value is None:
                                where_clauses.append(f"`{key}` IS NULL")
                            else:
                                where_clauses.append(f"`{key}` = %s")
                                select_params.append(value)
                        
                        if where_clauses:
                            select_query += f" WHERE {' AND '.join(where_clauses)}"
                        
                        await cursor.execute(select_query, select_params)
                        result_data = await cursor.fetchall()
                    else:
                        result_data = []
                    
                    return QueryResult(
                        data=result_data,
                        affected_rows=cursor.rowcount
                    )
        
        except Exception as e:
            search_logger.error(f"MySQL update query failed: {e}")
            return QueryResult(data=[], error=str(e))
    
    async def delete(
        self,
        table: str,
        filters: Dict[str, Any],
        returning: Optional[List[str]] = None,
    ) -> QueryResult:
        """Delete records from table"""
        try:
            # If returning columns requested, fetch records before deletion
            result_data = []
            if returning:
                select_result = await self.select(table, returning, filters)
                result_data = select_result.data
            
            # Build DELETE query
            query = f"DELETE FROM `{table}`"
            params = []
            
            # Add WHERE clause using complex filter support
            if filters:
                where_clause, where_params = self._build_where_clause(filters)
                query += where_clause
                params.extend(where_params)
            else:
                search_logger.warning("DELETE query without WHERE clause - this will delete all records!")
            
            # Execute query
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    await conn.commit()
                    
                    return QueryResult(
                        data=result_data,
                        affected_rows=cursor.rowcount
                    )
        
        except Exception as e:
            search_logger.error(f"MySQL delete query failed: {e}")
            return QueryResult(data=[], error=str(e))
    
    async def upsert(
        self,
        table: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        conflict_columns: List[str],
        update_columns: Optional[List[str]] = None,
        returning: Optional[List[str]] = None,
    ) -> QueryResult:
        """Insert or update records (UPSERT operation)"""
        try:
            # Ensure data is a list
            records = data if isinstance(data, list) else [data]
            
            if not records:
                return QueryResult(data=[], error="No data to upsert")
            
            # Get column names from first record
            columns = list(records[0].keys())
            columns_str = ", ".join(f"`{col}`" for col in columns)
            
            # Build VALUES clause
            placeholders = ", ".join(["%s"] * len(columns))
            values_clause = f"({placeholders})"
            
            # Prepare values
            all_values = []
            for record in records:
                values = []
                for col in columns:
                    value = record.get(col)
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value)
                    values.append(value)
                all_values.extend(values)
            
            # Build query
            if len(records) == 1:
                query = f"INSERT INTO `{table}` ({columns_str}) VALUES {values_clause}"
            else:
                values_clauses = [values_clause] * len(records)
                query = f"INSERT INTO `{table}` ({columns_str}) VALUES {', '.join(values_clauses)}"
            
            # Add ON DUPLICATE KEY UPDATE clause
            if update_columns is None:
                # Update all columns except conflict columns
                update_columns = [col for col in columns if col not in conflict_columns]
            
            if update_columns:
                update_clauses = []
                for col in update_columns:
                    update_clauses.append(f"`{col}` = VALUES(`{col}`)")
                
                query += f" ON DUPLICATE KEY UPDATE {', '.join(update_clauses)}"
            
            # Execute query
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, all_values)
                    await conn.commit()
                    
                    return QueryResult(
                        data=records,
                        affected_rows=cursor.rowcount
                    )
        
        except Exception as e:
            search_logger.error(f"MySQL upsert query failed: {e}")
            return QueryResult(data=[], error=str(e))
    
    async def begin_transaction(self) -> ITransaction:
        """Begin a database transaction"""
        if not self.pool:
            raise RuntimeError("Not connected to database")
        
        conn = await self.pool.acquire()
        return MySQLTransaction(conn, self)
    
    # Helper methods for vector operations (stored as BLOB)
    
    def _encode_vector(self, vector: np.ndarray) -> bytes:
        """Encode numpy array to bytes for storage"""
        return struct.pack(f'{len(vector)}f', *vector.tolist())
    
    def _decode_vector(self, blob: bytes) -> np.ndarray:
        """Decode bytes to numpy array"""
        if not blob:
            return None
        float_count = len(blob) // 4
        return np.array(struct.unpack(f'{float_count}f', blob))
    
    # IVectorStore implementation (fallback using BLOB storage)
    
    async def create_collection(
        self,
        name: str,
        dimension: int,
        distance_metric: str = "cosine",
        metadata_schema: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Create a vector collection (table) for storing embeddings.
        
        Args:
            name: Collection name
            dimension: Vector dimension
            distance_metric: Distance metric (cosine, euclidean, etc.)
            metadata_schema: Optional metadata schema
        
        Returns:
            True if collection created successfully
        """
        try:
            # Create table for vector storage with fallback implementation
            create_sql = f"""
            CREATE TABLE IF NOT EXISTS `{name}` (
                `id` VARCHAR(255) PRIMARY KEY,
                `embedding` BLOB NOT NULL,
                `content` TEXT,
                `metadata` JSON,
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_{name}_created_at` (`created_at`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            result = await self.execute(create_sql)
            if result.success:
                search_logger.info(f"Created vector collection '{name}' with fallback storage")
                return True
            else:
                search_logger.error(f"Failed to create vector collection '{name}': {result.error}")
                return False
                
        except Exception as e:
            search_logger.error(f"Error creating vector collection '{name}': {e}")
            return False
    
    async def delete_collection(self, name: str) -> bool:
        """
        Delete a vector collection.
        
        Args:
            name: Collection name
        
        Returns:
            True if collection deleted successfully
        """
        try:
            result = await self.execute(f"DROP TABLE IF EXISTS `{name}`")
            return result.success
        except Exception as e:
            search_logger.error(f"Error deleting vector collection '{name}': {e}")
            return False
    
    async def list_collections(self) -> List[Dict[str, Any]]:
        """
        List all vector collections with metadata.
        
        Returns:
            List of collection metadata (implements IVectorStore interface)
        """
        try:
            result = await self.execute("SHOW TABLES")
            if result.success:
                # Filter tables that have the expected vector storage structure
                collections = []
                for row in result.data:
                    table_name = list(row.values())[0]  # Get table name from result
                    
                    # Check if table has vector storage columns
                    check_sql = f"""
                    SELECT COUNT(*) as has_vector_cols
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = '{table_name}'
                    AND COLUMN_NAME IN ('id', 'embedding', 'metadata')
                    """
                    
                    check_result = await self.execute(check_sql)
                    if check_result.success and check_result.first.get('has_vector_cols', 0) >= 3:
                        # Get additional metadata for this collection
                        info_sql = """
                        SELECT 
                            TABLE_NAME as name,
                            TABLE_COMMENT as comment,
                            CREATE_TIME as created_at
                        FROM INFORMATION_SCHEMA.TABLES 
                        WHERE TABLE_SCHEMA = DATABASE()
                        AND TABLE_NAME = %s
                        """
                        
                        info_result = await self.execute(info_sql, [table_name])
                        
                        if info_result.success and info_result.data:
                            table_info = info_result.data[0]
                            collection_meta = {
                                'name': table_info.get('name', table_name),
                                'comment': table_info.get('comment', ''),
                                'created_at': table_info.get('created_at'),
                                'type': 'mysql_vector_fallback'
                            }
                        else:
                            # Fallback metadata
                            collection_meta = {
                                'name': table_name,
                                'type': 'mysql_vector_fallback'
                            }
                        
                        collections.append(collection_meta)
                
                return collections
            return []
        except Exception as e:
            search_logger.error(f"Error listing vector collections: {e}")
            return []
    
    async def list_collection_names(self) -> List[str]:
        """
        Helper method to get just collection names (for backward compatibility).
        
        Returns:
            List of collection names
        """
        try:
            collections = await self.list_collections()
            return [coll['name'] for coll in collections]
        except Exception as e:
            search_logger.error(f"Error getting collection names: {e}")
            return []
    
    async def upsert_vectors(
        self,
        collection: str,
        vectors: List[Dict[str, Any]],
    ) -> bool:
        """
        Insert or update vectors in a collection.
        
        Args:
            collection: Collection name
            vectors: List of vector data with id, embedding, content, metadata
        
        Returns:
            True if operation successful
        """
        try:
            if not vectors:
                return True
            
            # Prepare data for upsert
            upsert_data = []
            for vector_data in vectors:
                if 'id' not in vector_data or 'embedding' not in vector_data:
                    search_logger.warning("Skipping vector without id or embedding")
                    continue
                
                # Encode vector to bytes
                embedding_bytes = self._encode_vector(np.array(vector_data['embedding']))
                
                record = {
                    'id': vector_data['id'],
                    'embedding': embedding_bytes,
                    'content': vector_data.get('content'),
                    'metadata': vector_data.get('metadata', {})
                }
                upsert_data.append(record)
            
            if not upsert_data:
                return True
            
            # Use upsert operation
            result = await self.upsert(
                table=collection,
                data=upsert_data,
                conflict_columns=['id'],
                update_columns=['embedding', 'content', 'metadata'],
            )
            
            return result.success
            
        except Exception as e:
            search_logger.error(f"Error upserting vectors to collection '{collection}': {e}")
            return False
    
    async def search_vectors(
        self,
        collection: str,
        query_vector: np.ndarray,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True,
        include_content: bool = True,
    ) -> List[VectorSearchResult]:
        """
        Search for similar vectors using fallback implementation.
        
        Args:
            collection: Collection name
            query_vector: Query vector
            top_k: Number of results to return
            filters: Optional metadata filters
            include_metadata: Include metadata in results
            include_content: Include content in results
        
        Returns:
            List of search results
        """
        try:
            # Build filters for database query
            db_filters = {}
            if filters:
                # Convert vector search filters to database filters
                # This is a simplified implementation - real implementation would need
                # more sophisticated metadata filtering
                for key, value in filters.items():
                    if key.startswith('metadata.'):
                        # MySQL JSON path filtering would go here
                        # For now, we'll fetch all records and filter in memory
                        pass
                    else:
                        db_filters[key] = value
            
            # Fetch records from collection
            columns = ['id', 'embedding']
            if include_metadata:
                columns.append('metadata')
            if include_content:
                columns.append('content')
            
            result = await self.select(collection, columns=columns, filters=db_filters)
            
            if not result.success or not result.data:
                return []
            
            # Calculate similarities in memory (fallback approach)
            similarities = []
            for record in result.data:
                if 'embedding' in record and record['embedding']:
                    stored_vector = self._decode_vector(record['embedding'])
                    if stored_vector is not None:
                        # Ensure vectors have same dimension
                        if len(stored_vector) != len(query_vector):
                            search_logger.warning(
                                f"Vector dimension mismatch: expected {len(query_vector)}, "
                                f"got {len(stored_vector)} for record {record.get('id')}"
                            )
                            continue
                        
                        # Calculate cosine similarity
                        try:
                            similarity = np.dot(query_vector, stored_vector) / (
                                np.linalg.norm(query_vector) * np.linalg.norm(stored_vector)
                            )
                            
                            # Apply metadata filters in memory if needed
                            if filters:
                                metadata = record.get('metadata', {})
                                if not self._apply_metadata_filters(metadata, filters):
                                    continue
                            
                            similarities.append({
                                'record': record,
                                'similarity': float(similarity)
                            })
                        except (ValueError, ZeroDivisionError) as e:
                            search_logger.warning(f"Error calculating similarity for record {record.get('id')}: {e}")
                            continue
            
            # Sort by similarity and take top_k
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            top_results = similarities[:top_k]
            
            # Convert to VectorSearchResult format
            search_results = []
            for item in top_results:
                record = item['record']
                result_obj = VectorSearchResult(
                    id=record['id'],
                    score=item['similarity'],
                    metadata=record.get('metadata', {}) if include_metadata else {},
                    content=record.get('content') if include_content else None,
                    embedding=None  # Don't include embedding in results by default
                )
                search_results.append(result_obj)
            
            return search_results
            
        except Exception as e:
            search_logger.error(f"Vector search failed for collection '{collection}': {e}")
            return []
    
    async def search_vectors_batch(
        self,
        collection: str,
        query_vectors: List[np.ndarray],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[List[VectorSearchResult]]:
        """
        Batch vector search using fallback implementation.
        
        Args:
            collection: Collection name
            query_vectors: List of query vectors
            top_k: Number of results per query
            filters: Optional metadata filters
        
        Returns:
            List of search results for each query
        """
        try:
            results = []
            for query_vector in query_vectors:
                query_results = await self.search_vectors(
                    collection=collection,
                    query_vector=query_vector,
                    top_k=top_k,
                    filters=filters
                )
                results.append(query_results)
            return results
        except Exception as e:
            search_logger.error(f"Batch vector search failed for collection '{collection}': {e}")
            return [[] for _ in query_vectors]
    
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
        try:
            columns = ['id']
            if include_metadata:
                columns.append('metadata')
            if include_vector:
                columns.append('embedding')
            
            result = await self.select(collection, columns=columns, filters={'id': id})
            
            if not result.success or not result.data:
                return None
            
            record = result.data[0]
            embedding = None
            
            if include_vector and 'embedding' in record:
                embedding = self._decode_vector(record['embedding'])
            
            return VectorSearchResult(
                id=record['id'],
                score=1.0,  # No similarity score for direct fetch
                metadata=record.get('metadata', {}) if include_metadata else {},
                content=record.get('content'),
                embedding=embedding
            )
            
        except Exception as e:
            search_logger.error(f"Error getting vector {id} from collection '{collection}': {e}")
            return None
    
    def _apply_metadata_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """
        Apply metadata filters in memory (fallback approach).
        
        Args:
            metadata: Record metadata
            filters: Filters to apply
        
        Returns:
            True if record matches filters
        """
        try:
            for key, value in filters.items():
                if key.startswith('metadata.'):
                    # Extract metadata key
                    meta_key = key[9:]  # Remove 'metadata.' prefix
                    
                    # Simple equality check - could be extended for complex operators
                    if meta_key not in metadata or metadata[meta_key] != value:
                        return False
            return True
        except Exception as e:
            search_logger.warning(f"Error applying metadata filters: {e}")
            return True  # Default to include if filtering fails
    
    # Required abstract methods from IVectorStore interface
    
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
        try:
            if not vectors:
                return []
            
            # Generate IDs if not provided
            if ids is None:
                ids = [str(uuid4()) for _ in vectors]
            
            # Ensure metadata list matches vectors length
            if metadata is None:
                metadata = [{} for _ in vectors]
            
            # Build vector data for upsert
            vector_data = []
            for i, (vector, vector_id) in enumerate(zip(vectors, ids)):
                vector_meta = metadata[i] if i < len(metadata) else {}
                vector_data.append({
                    'id': vector_id,
                    'embedding': vector,
                    'metadata': vector_meta
                })
            
            # Use existing upsert_vectors method
            success = await self.upsert_vectors(collection, vector_data)
            
            if success:
                return ids
            else:
                return []
                
        except Exception as e:
            search_logger.error(f"Error inserting vectors to collection '{collection}': {e}")
            return []
    
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
        try:
            if not ids:
                return True
            
            # Build update data
            for i, vector_id in enumerate(ids):
                update_data = {}
                
                # Add vector if provided
                if vectors and i < len(vectors):
                    update_data['embedding'] = self._encode_vector(vectors[i])
                
                # Add metadata if provided
                if metadata and i < len(metadata):
                    update_data['metadata'] = metadata[i]
                
                if update_data:
                    result = await self.update(
                        table=collection,
                        data=update_data,
                        filters={'id': vector_id}
                    )
                    
                    if not result.success:
                        search_logger.error(f"Failed to update vector {vector_id}: {result.error}")
                        return False
            
            return True
            
        except Exception as e:
            search_logger.error(f"Error updating vectors in collection '{collection}': {e}")
            return False
    
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
        try:
            delete_filters = {}
            
            # Build filters for deletion
            if ids:
                if len(ids) == 1:
                    delete_filters['id'] = ids[0]
                else:
                    # Use OR condition for multiple IDs
                    delete_filters['id'] = {'or': [{'eq': id_val} for id_val in ids]}
            
            # Add metadata filters if provided
            if filters:
                delete_filters.update(filters)
            
            if not delete_filters:
                search_logger.warning("No filters provided for vector deletion")
                return 0
            
            # Execute deletion
            result = await self.delete(table=collection, filters=delete_filters)
            
            if result.success:
                return result.affected_rows or 0
            else:
                search_logger.error(f"Failed to delete vectors: {result.error}")
                return 0
                
        except Exception as e:
            search_logger.error(f"Error deleting vectors from collection '{collection}': {e}")
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
        # Use existing search_vectors method with proper parameter mapping
        return await self.search_vectors(
            collection=collection,
            query_vector=query_vector,
            top_k=top_k,
            filters=filters,
            include_metadata=include_metadata,
            include_content=True  # Always include content for compatibility
        )
    
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
        # Use existing search_vectors_batch method
        return await self.search_vectors_batch(
            collection=collection,
            query_vectors=query_vectors,
            top_k=top_k,
            filters=filters
        )
    
    
    # Legacy method for backward compatibility
    async def search_vectors_fallback(
        self,
        table: str,
        query_vector: np.ndarray,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Legacy fallback vector search method.
        Use search_vectors() instead for new code.
        """
        search_logger.warning("Using legacy search_vectors_fallback method. Consider using search_vectors() instead.")
        
        results = await self.search_vectors(
            collection=table,
            query_vector=query_vector,
            top_k=top_k,
            filters=filters
        )
        
        # Convert VectorSearchResult back to dict format for compatibility
        legacy_results = []
        for result in results:
            legacy_result = {
                'id': result.id,
                'similarity': result.score,
                'metadata': result.metadata
            }
            if result.content:
                legacy_result['content'] = result.content
            legacy_results.append(legacy_result)
        
        return legacy_results