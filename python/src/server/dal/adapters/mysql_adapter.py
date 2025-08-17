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
    QueryResult,
    TransactionState,
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


class MySQLAdapter(IDatabase):
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
                        # Convert dict params to list for MySQL
                        param_list = list(params.values()) if isinstance(params, dict) else params
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
            
            # Add WHERE clause
            if filters:
                where_clauses = []
                for key, value in filters.items():
                    if value is None:
                        where_clauses.append(f"`{key}` IS NULL")
                    else:
                        where_clauses.append(f"`{key}` = %s")
                        params.append(value)
                
                if where_clauses:
                    query += f" WHERE {' AND '.join(where_clauses)}"
            
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
            
            # Add WHERE clause
            if filters:
                where_clauses = []
                for key, value in filters.items():
                    if value is None:
                        where_clauses.append(f"`{key}` IS NULL")
                    else:
                        where_clauses.append(f"`{key}` = %s")
                        params.append(value)
                
                if where_clauses:
                    query += f" WHERE {' AND '.join(where_clauses)}"
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
            
            # Add WHERE clause
            if filters:
                where_clauses = []
                for key, value in filters.items():
                    if value is None:
                        where_clauses.append(f"`{key}` IS NULL")
                    else:
                        where_clauses.append(f"`{key}` = %s")
                        params.append(value)
                
                if where_clauses:
                    query += f" WHERE {' AND '.join(where_clauses)}"
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
    
    async def search_vectors_fallback(
        self,
        table: str,
        query_vector: np.ndarray,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fallback vector search using in-memory computation.
        This is not efficient for large datasets and should be replaced
        with an external vector service in production.
        """
        try:
            # Fetch all records (with filters if provided)
            result = await self.select(table, filters=filters)
            
            if not result.success or not result.data:
                return []
            
            # Calculate similarities
            similarities = []
            for record in result.data:
                if 'embedding' in record and record['embedding']:
                    stored_vector = self._decode_vector(record['embedding'])
                    if stored_vector is not None:
                        # Cosine similarity
                        similarity = np.dot(query_vector, stored_vector) / (
                            np.linalg.norm(query_vector) * np.linalg.norm(stored_vector)
                        )
                        record['similarity'] = float(similarity)
                        similarities.append(record)
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:top_k]
        
        except Exception as e:
            search_logger.error(f"Vector search fallback failed: {e}")
            return []