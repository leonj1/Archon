# Multi-Database Support Specification
## Archon V2 Alpha Database Abstraction Layer

### Document Version: 1.0.0
### Date: 2025-08-16
### Status: Draft
### Authors: System Architecture Team

---

## 1. Executive Summary

### Current State
Archon V2 Alpha is tightly coupled to Supabase (PostgreSQL + pgvector), with direct client usage throughout the codebase. This specification outlines the architectural changes required to support multiple database backends including MySQL, PostgreSQL (standalone), and vector databases.

### Proposed Solution
Implement a comprehensive Database Abstraction Layer (DAL) that provides a unified interface for all database operations while maintaining backward compatibility with existing Supabase deployments.

### Key Benefits
- **Database Flexibility**: Support for MySQL, PostgreSQL, SQLite, and vector databases
- **Deployment Options**: From SQLite for local development to enterprise PostgreSQL
- **Cost Optimization**: Choose database based on scale and budget requirements
- **Development Velocity**: Faster local development with lightweight databases
- **Testing Improvements**: In-memory databases for unit testing

---

## 2. Requirements

### 2.1 Functional Requirements

#### Core Database Support
- **FR-1**: Support Supabase (existing, must maintain compatibility)
- **FR-2**: Support standalone PostgreSQL (with pgvector extension)
- **FR-3**: Support MySQL 8.0+ (with vector capabilities via plugins)
- **FR-4**: Support SQLite for local development
- **FR-5**: Support external vector databases (Pinecone, Weaviate, Chroma)

#### Feature Parity
- **FR-6**: CRUD operations for all entities across all databases
- **FR-7**: Vector similarity search with configurable algorithms
- **FR-8**: JSONB/JSON field support with querying capabilities
- **FR-9**: Transaction support with rollback capabilities
- **FR-10**: Migration system for schema management

#### Configuration Management
- **FR-11**: Runtime database selection via environment variables
- **FR-12**: Connection pooling and retry mechanisms
- **FR-13**: Multi-database support (read/write splitting)
- **FR-14**: Feature detection and graceful degradation

### 2.2 Non-Functional Requirements

#### Performance
- **NFR-1**: < 10% performance overhead for abstraction layer
- **NFR-2**: Lazy loading of database adapters
- **NFR-3**: Connection pooling with configurable limits
- **NFR-4**: Query optimization per database engine

#### Reliability
- **NFR-5**: 99.9% uptime for database operations
- **NFR-6**: Automatic failover for multi-database setups
- **NFR-7**: Transaction integrity across all databases
- **NFR-8**: Data consistency validation

#### Security
- **NFR-9**: Encrypted credential storage
- **NFR-10**: SQL injection prevention
- **NFR-11**: Row-level security abstraction
- **NFR-12**: Audit logging for all operations

#### Maintainability
- **NFR-13**: 90%+ test coverage for DAL
- **NFR-14**: Database-specific integration tests
- **NFR-15**: Clear adapter implementation patterns
- **NFR-16**: Comprehensive documentation

---

## 3. Architecture Design

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│                  (FastAPI, MCP, Agents)                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Database Abstraction Layer                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    DAL Interface                     │  │
│  │  • IDatabase  • IVectorStore  • IMigrationManager    │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   Query Builder                      │  │
│  │  • SELECT  • INSERT  • UPDATE  • DELETE  • VECTOR    │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                 Connection Manager                   │  │
│  │  • Pooling  • Retry  • Failover  • Load Balancing   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Supabase   │    │  PostgreSQL  │    │    MySQL     │
│   Adapter    │    │   Adapter    │    │   Adapter    │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Supabase   │    │  PostgreSQL  │    │  MySQL 8.0+  │
│   (Cloud)    │    │  + pgvector  │    │  + Plugins   │
└──────────────┘    └──────────────┘    └──────────────┘
```

### 3.2 Component Design

#### 3.2.1 Database Interface (IDatabase)

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

@dataclass
class QueryResult:
    data: List[Dict[str, Any]]
    count: Optional[int] = None
    error: Optional[str] = None

class IDatabase(ABC):
    """Abstract base class for database operations"""
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish database connection"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection"""
        pass
    
    @abstractmethod
    async def execute(self, query: str, params: Optional[Dict] = None) -> QueryResult:
        """Execute raw SQL query"""
        pass
    
    @abstractmethod
    async def select(self, table: str, columns: List[str] = ["*"], 
                    filters: Optional[Dict] = None, 
                    order_by: Optional[str] = None,
                    limit: Optional[int] = None) -> QueryResult:
        """Select records from table"""
        pass
    
    @abstractmethod
    async def insert(self, table: str, data: Union[Dict, List[Dict]]) -> QueryResult:
        """Insert records into table"""
        pass
    
    @abstractmethod
    async def update(self, table: str, data: Dict, 
                    filters: Dict) -> QueryResult:
        """Update records in table"""
        pass
    
    @abstractmethod
    async def delete(self, table: str, filters: Dict) -> QueryResult:
        """Delete records from table"""
        pass
    
    @abstractmethod
    async def upsert(self, table: str, data: Union[Dict, List[Dict]], 
                    conflict_columns: List[str]) -> QueryResult:
        """Insert or update records"""
        pass
    
    @abstractmethod
    async def transaction(self) -> 'TransactionContext':
        """Start a database transaction"""
        pass
```

#### 3.2.2 Vector Store Interface (IVectorStore)

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np

@dataclass
class VectorSearchResult:
    id: str
    score: float
    metadata: Dict[str, Any]
    content: Optional[str] = None

class IVectorStore(ABC):
    """Abstract base class for vector operations"""
    
    @abstractmethod
    async def create_collection(self, name: str, dimension: int, 
                              metric: str = "cosine") -> bool:
        """Create a vector collection/index"""
        pass
    
    @abstractmethod
    async def insert_vectors(self, collection: str, 
                           vectors: List[np.ndarray],
                           metadata: List[Dict[str, Any]]) -> bool:
        """Insert vectors with metadata"""
        pass
    
    @abstractmethod
    async def search(self, collection: str, 
                    query_vector: np.ndarray,
                    top_k: int = 10,
                    filters: Optional[Dict] = None) -> List[VectorSearchResult]:
        """Search for similar vectors"""
        pass
    
    @abstractmethod
    async def delete_vectors(self, collection: str, 
                           ids: List[str]) -> bool:
        """Delete vectors by ID"""
        pass
    
    @abstractmethod
    async def update_metadata(self, collection: str, 
                            id: str, 
                            metadata: Dict[str, Any]) -> bool:
        """Update vector metadata"""
        pass
```

#### 3.2.3 Database Adapters

##### Supabase Adapter
```python
from supabase import create_client, Client
from typing import Optional
import os

class SupabaseAdapter(IDatabase, IVectorStore):
    """Adapter for Supabase (PostgreSQL + pgvector)"""
    
    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self.client: Optional[Client] = None
    
    async def connect(self) -> None:
        self.client = create_client(self.url, self.key)
    
    async def select(self, table: str, **kwargs) -> QueryResult:
        query = self.client.table(table)
        
        if kwargs.get('columns'):
            query = query.select(','.join(kwargs['columns']))
        else:
            query = query.select('*')
        
        if kwargs.get('filters'):
            for key, value in kwargs['filters'].items():
                query = query.eq(key, value)
        
        if kwargs.get('order_by'):
            query = query.order(kwargs['order_by'])
        
        if kwargs.get('limit'):
            query = query.limit(kwargs['limit'])
        
        response = query.execute()
        return QueryResult(data=response.data)
    
    async def search(self, collection: str, query_vector: np.ndarray, 
                    top_k: int = 10, **kwargs) -> List[VectorSearchResult]:
        # Call PostgreSQL function for vector similarity
        response = self.client.rpc(
            f'match_{collection}',
            {
                'query_embedding': query_vector.tolist(),
                'match_count': top_k,
                'filter': kwargs.get('filters', {})
            }
        ).execute()
        
        return [
            VectorSearchResult(
                id=item['id'],
                score=item['similarity'],
                metadata=item['metadata'],
                content=item.get('content')
            )
            for item in response.data
        ]
```

##### PostgreSQL Adapter
```python
import asyncpg
from typing import Optional
import json

class PostgreSQLAdapter(IDatabase, IVectorStore):
    """Adapter for standalone PostgreSQL with pgvector"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> None:
        self.pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        # Enable pgvector extension
        async with self.pool.acquire() as conn:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    
    async def select(self, table: str, **kwargs) -> QueryResult:
        query_parts = [f"SELECT {','.join(kwargs.get('columns', ['*']))}"]
        query_parts.append(f"FROM {table}")
        
        params = []
        if filters := kwargs.get('filters'):
            where_clauses = []
            for i, (key, value) in enumerate(filters.items(), 1):
                where_clauses.append(f"{key} = ${i}")
                params.append(value)
            query_parts.append(f"WHERE {' AND '.join(where_clauses)}")
        
        if order_by := kwargs.get('order_by'):
            query_parts.append(f"ORDER BY {order_by}")
        
        if limit := kwargs.get('limit'):
            query_parts.append(f"LIMIT {limit}")
        
        query = ' '.join(query_parts)
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return QueryResult(data=[dict(row) for row in rows])
    
    async def search(self, collection: str, query_vector: np.ndarray,
                    top_k: int = 10, **kwargs) -> List[VectorSearchResult]:
        query = f"""
            SELECT id, content, metadata,
                   1 - (embedding <=> $1::vector) as similarity
            FROM {collection}
            WHERE ($2::jsonb IS NULL OR metadata @> $2::jsonb)
            ORDER BY embedding <=> $1::vector
            LIMIT $3
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                query,
                query_vector.tolist(),
                json.dumps(kwargs.get('filters')) if kwargs.get('filters') else None,
                top_k
            )
            
            return [
                VectorSearchResult(
                    id=row['id'],
                    score=row['similarity'],
                    metadata=json.loads(row['metadata']),
                    content=row.get('content')
                )
                for row in rows
            ]
```

##### MySQL Adapter
```python
import aiomysql
from typing import Optional
import json

class MySQLAdapter(IDatabase):
    """Adapter for MySQL 8.0+"""
    
    def __init__(self, **connection_params):
        self.connection_params = connection_params
        self.pool: Optional[aiomysql.Pool] = None
    
    async def connect(self) -> None:
        self.pool = await aiomysql.create_pool(
            **self.connection_params,
            minsize=5,
            maxsize=20,
            autocommit=False
        )
    
    async def select(self, table: str, **kwargs) -> QueryResult:
        query_parts = [f"SELECT {','.join(kwargs.get('columns', ['*']))}"]
        query_parts.append(f"FROM {table}")
        
        params = []
        if filters := kwargs.get('filters'):
            where_clauses = []
            for key, value in filters.items():
                # Handle JSON field queries
                if '->>' in key:
                    where_clauses.append(f"{key} = %s")
                else:
                    where_clauses.append(f"`{key}` = %s")
                params.append(value)
            query_parts.append(f"WHERE {' AND '.join(where_clauses)}")
        
        if order_by := kwargs.get('order_by'):
            query_parts.append(f"ORDER BY {order_by}")
        
        if limit := kwargs.get('limit'):
            query_parts.append(f"LIMIT {limit}")
        
        query = ' '.join(query_parts)
        
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                rows = await cursor.fetchall()
                return QueryResult(data=rows)
    
    async def insert(self, table: str, data: Union[Dict, List[Dict]]) -> QueryResult:
        if isinstance(data, dict):
            data = [data]
        
        if not data:
            return QueryResult(data=[], error="No data to insert")
        
        columns = list(data[0].keys())
        placeholders = ', '.join(['%s'] * len(columns))
        
        query = f"""
            INSERT INTO `{table}` ({', '.join(f'`{col}`' for col in columns)})
            VALUES ({placeholders})
        """
        
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                if len(data) == 1:
                    await cursor.execute(query, list(data[0].values()))
                else:
                    await cursor.executemany(
                        query, 
                        [list(row.values()) for row in data]
                    )
                await conn.commit()
                
                # Return inserted data with IDs if available
                if cursor.lastrowid:
                    for i, row in enumerate(data):
                        row['id'] = cursor.lastrowid + i
                
                return QueryResult(data=data)
```

### 3.3 Query Builder Design

```python
from typing import Any, Dict, List, Optional, Union
from enum import Enum

class QueryType(Enum):
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    
class QueryBuilder:
    """Database-agnostic query builder"""
    
    def __init__(self, adapter: IDatabase):
        self.adapter = adapter
        self.reset()
    
    def reset(self):
        self.query_type = None
        self.table_name = None
        self.columns = []
        self.values = []
        self.conditions = []
        self.joins = []
        self.order = []
        self.limit_value = None
        self.offset_value = None
        return self
    
    def table(self, name: str) -> 'QueryBuilder':
        self.table_name = name
        return self
    
    def select(self, *columns: str) -> 'QueryBuilder':
        self.query_type = QueryType.SELECT
        self.columns = list(columns) if columns else ['*']
        return self
    
    def insert(self, data: Union[Dict, List[Dict]]) -> 'QueryBuilder':
        self.query_type = QueryType.INSERT
        self.values = data if isinstance(data, list) else [data]
        return self
    
    def update(self, data: Dict) -> 'QueryBuilder':
        self.query_type = QueryType.UPDATE
        self.values = data
        return self
    
    def delete(self) -> 'QueryBuilder':
        self.query_type = QueryType.DELETE
        return self
    
    def where(self, column: str, operator: str, value: Any) -> 'QueryBuilder':
        self.conditions.append((column, operator, value))
        return self
    
    def where_in(self, column: str, values: List[Any]) -> 'QueryBuilder':
        self.conditions.append((column, 'IN', values))
        return self
    
    def where_json(self, column: str, path: str, value: Any) -> 'QueryBuilder':
        # JSON field query support
        self.conditions.append((f"{column}->>{path}", '=', value))
        return self
    
    def join(self, table: str, on: str) -> 'QueryBuilder':
        self.joins.append(('INNER', table, on))
        return self
    
    def left_join(self, table: str, on: str) -> 'QueryBuilder':
        self.joins.append(('LEFT', table, on))
        return self
    
    def order_by(self, column: str, direction: str = 'ASC') -> 'QueryBuilder':
        self.order.append((column, direction))
        return self
    
    def limit(self, value: int) -> 'QueryBuilder':
        self.limit_value = value
        return self
    
    def offset(self, value: int) -> 'QueryBuilder':
        self.offset_value = value
        return self
    
    async def execute(self) -> QueryResult:
        """Execute the built query using the adapter"""
        if self.query_type == QueryType.SELECT:
            filters = {cond[0]: cond[2] for cond in self.conditions if cond[1] == '='}
            order_str = ', '.join(f"{col} {dir}" for col, dir in self.order) if self.order else None
            
            return await self.adapter.select(
                table=self.table_name,
                columns=self.columns,
                filters=filters if filters else None,
                order_by=order_str,
                limit=self.limit_value
            )
        
        elif self.query_type == QueryType.INSERT:
            return await self.adapter.insert(self.table_name, self.values)
        
        elif self.query_type == QueryType.UPDATE:
            filters = {cond[0]: cond[2] for cond in self.conditions if cond[1] == '='}
            return await self.adapter.update(self.table_name, self.values, filters)
        
        elif self.query_type == QueryType.DELETE:
            filters = {cond[0]: cond[2] for cond in self.conditions if cond[1] == '='}
            return await self.adapter.delete(self.table_name, filters)
        
        raise ValueError(f"Unsupported query type: {self.query_type}")
```

### 3.4 Connection Manager

```python
from typing import Dict, Optional, Type
import os
from enum import Enum

class DatabaseType(Enum):
    SUPABASE = "supabase"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"

class ConnectionManager:
    """Manages database connections and adapter selection"""
    
    # Adapter registry
    ADAPTERS: Dict[DatabaseType, Type[IDatabase]] = {
        DatabaseType.SUPABASE: SupabaseAdapter,
        DatabaseType.POSTGRESQL: PostgreSQLAdapter,
        DatabaseType.MYSQL: MySQLAdapter,
    }
    
    def __init__(self):
        self.primary_adapter: Optional[IDatabase] = None
        self.vector_adapter: Optional[IVectorStore] = None
        self.read_replicas: List[IDatabase] = []
    
    @classmethod
    def from_env(cls) -> 'ConnectionManager':
        """Create connection manager from environment variables"""
        manager = cls()
        
        # Detect database type from environment
        db_type = DatabaseType(os.getenv("DATABASE_TYPE", "supabase").lower())
        
        # Create primary adapter based on type
        if db_type == DatabaseType.SUPABASE:
            adapter = SupabaseAdapter(
                url=os.getenv("SUPABASE_URL"),
                key=os.getenv("SUPABASE_SERVICE_KEY")
            )
        elif db_type == DatabaseType.POSTGRESQL:
            adapter = PostgreSQLAdapter(
                connection_string=os.getenv("DATABASE_URL")
            )
        elif db_type == DatabaseType.MYSQL:
            adapter = MySQLAdapter(
                host=os.getenv("MYSQL_HOST", "localhost"),
                port=int(os.getenv("MYSQL_PORT", 3306)),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                db=os.getenv("MYSQL_DATABASE")
            )
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        manager.primary_adapter = adapter
        
        # Set vector adapter (same as primary if it supports vectors)
        if isinstance(adapter, IVectorStore):
            manager.vector_adapter = adapter
        else:
            # Use external vector database if configured
            if vector_db := os.getenv("VECTOR_DATABASE"):
                manager.vector_adapter = cls._create_vector_adapter(vector_db)
        
        return manager
    
    @staticmethod
    def _create_vector_adapter(vector_type: str) -> IVectorStore:
        """Create external vector database adapter"""
        if vector_type == "pinecone":
            from .adapters.pinecone_adapter import PineconeAdapter
            return PineconeAdapter(
                api_key=os.getenv("PINECONE_API_KEY"),
                environment=os.getenv("PINECONE_ENVIRONMENT")
            )
        elif vector_type == "weaviate":
            from .adapters.weaviate_adapter import WeaviateAdapter
            return WeaviateAdapter(
                url=os.getenv("WEAVIATE_URL"),
                api_key=os.getenv("WEAVIATE_API_KEY")
            )
        else:
            raise ValueError(f"Unsupported vector database: {vector_type}")
    
    async def connect_all(self):
        """Connect all configured adapters"""
        if self.primary_adapter:
            await self.primary_adapter.connect()
        
        if self.vector_adapter and self.vector_adapter != self.primary_adapter:
            await self.vector_adapter.connect()
        
        for replica in self.read_replicas:
            await replica.connect()
    
    async def disconnect_all(self):
        """Disconnect all adapters"""
        if self.primary_adapter:
            await self.primary_adapter.disconnect()
        
        if self.vector_adapter and self.vector_adapter != self.primary_adapter:
            await self.vector_adapter.disconnect()
        
        for replica in self.read_replicas:
            await replica.disconnect()
    
    def get_primary(self) -> IDatabase:
        """Get primary database adapter for writes"""
        if not self.primary_adapter:
            raise RuntimeError("No primary database configured")
        return self.primary_adapter
    
    def get_reader(self) -> IDatabase:
        """Get database adapter for reads (load balancing)"""
        if self.read_replicas:
            # Simple round-robin load balancing
            import random
            return random.choice(self.read_replicas)
        return self.get_primary()
    
    def get_vector_store(self) -> IVectorStore:
        """Get vector store adapter"""
        if not self.vector_adapter:
            raise RuntimeError("No vector store configured")
        return self.vector_adapter
```

---

## 4. Migration Strategy

### 4.1 Schema Migration System

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import hashlib
from datetime import datetime

class Migration(ABC):
    """Base class for database migrations"""
    
    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description
        self.checksum = self._calculate_checksum()
    
    @abstractmethod
    def up(self, db: IDatabase) -> None:
        """Apply migration"""
        pass
    
    @abstractmethod
    def down(self, db: IDatabase) -> None:
        """Rollback migration"""
        pass
    
    def _calculate_checksum(self) -> str:
        """Calculate migration checksum for validation"""
        content = f"{self.version}:{self.description}:{self.up.__code__.co_code}"
        return hashlib.sha256(content.encode()).hexdigest()

class MigrationManager:
    """Manages database migrations across different database types"""
    
    def __init__(self, db: IDatabase):
        self.db = db
        self.migrations_table = "archon_migrations"
    
    async def initialize(self):
        """Create migrations tracking table"""
        await self.db.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.migrations_table} (
                version VARCHAR(50) PRIMARY KEY,
                description TEXT,
                checksum VARCHAR(64),
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    async def apply_migrations(self, migrations: List[Migration]):
        """Apply pending migrations"""
        applied = await self._get_applied_migrations()
        
        for migration in migrations:
            if migration.version not in applied:
                print(f"Applying migration {migration.version}: {migration.description}")
                
                async with self.db.transaction() as tx:
                    try:
                        await migration.up(self.db)
                        await self._record_migration(migration)
                        await tx.commit()
                    except Exception as e:
                        await tx.rollback()
                        raise Exception(f"Migration {migration.version} failed: {e}")
    
    async def _get_applied_migrations(self) -> Set[str]:
        """Get list of applied migration versions"""
        result = await self.db.select(
            self.migrations_table,
            columns=["version"]
        )
        return {row["version"] for row in result.data}
    
    async def _record_migration(self, migration: Migration):
        """Record successful migration"""
        await self.db.insert(
            self.migrations_table,
            {
                "version": migration.version,
                "description": migration.description,
                "checksum": migration.checksum
            }
        )
```

### 4.2 Database-Specific Migrations

```python
# migrations/001_initial_schema.py
class InitialSchemaMigration(Migration):
    """Initial schema setup for all databases"""
    
    def __init__(self):
        super().__init__("001", "Initial schema setup")
    
    async def up(self, db: IDatabase):
        # Detect database type and apply appropriate schema
        if isinstance(db, SupabaseAdapter):
            await self._up_supabase(db)
        elif isinstance(db, PostgreSQLAdapter):
            await self._up_postgresql(db)
        elif isinstance(db, MySQLAdapter):
            await self._up_mysql(db)
    
    async def _up_postgresql(self, db: PostgreSQLAdapter):
        """PostgreSQL-specific schema"""
        await db.execute("""
            CREATE EXTENSION IF NOT EXISTS vector;
            CREATE EXTENSION IF NOT EXISTS pgcrypto;
            
            CREATE TABLE archon_sources (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                url TEXT,
                title TEXT,
                source_type VARCHAR(50),
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE archon_crawled_pages (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                source_id UUID REFERENCES archon_sources(id) ON DELETE CASCADE,
                url TEXT,
                content TEXT,
                chunk_index INTEGER,
                metadata JSONB DEFAULT '{}',
                embedding vector(1536),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX idx_crawled_pages_embedding 
            ON archon_crawled_pages 
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
        """)
    
    async def _up_mysql(self, db: MySQLAdapter):
        """MySQL-specific schema"""
        await db.execute("""
            CREATE TABLE archon_sources (
                id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
                url TEXT,
                title TEXT,
                source_type VARCHAR(50),
                metadata JSON DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
            
            CREATE TABLE archon_crawled_pages (
                id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
                source_id CHAR(36),
                url TEXT,
                content TEXT,
                chunk_index INTEGER,
                metadata JSON DEFAULT '{}',
                embedding_data BLOB,  -- Store vectors as binary
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES archon_sources(id) ON DELETE CASCADE,
                INDEX idx_source_id (source_id)
            );
            
            -- Create a separate table for vector indexing if using external service
            CREATE TABLE archon_vector_index (
                page_id CHAR(36) PRIMARY KEY,
                external_vector_id VARCHAR(100),
                vector_service VARCHAR(50),
                FOREIGN KEY (page_id) REFERENCES archon_crawled_pages(id) ON DELETE CASCADE
            );
        """)
```

---

## 5. Implementation Plan

### 5.1 Phase 1: Foundation (Weeks 1-2)

#### Tasks
1. **Create Database Abstraction Layer**
   - Define IDatabase interface
   - Define IVectorStore interface
   - Create base adapter class
   - Implement error handling

2. **Implement Query Builder**
   - Basic CRUD operations
   - JSON field support
   - Join operations
   - Transaction support

3. **Setup Connection Manager**
   - Environment detection
   - Connection pooling
   - Retry mechanisms
   - Load balancing logic

### 5.2 Phase 2: Adapter Implementation (Weeks 3-5)

#### Tasks
1. **Supabase Adapter (Maintain Compatibility)**
   - Implement IDatabase interface
   - Implement IVectorStore interface
   - Maintain existing functionality
   - Add comprehensive tests

2. **PostgreSQL Adapter**
   - Implement core database operations
   - pgvector integration
   - Connection pooling with asyncpg
   - Custom function support

3. **MySQL Adapter**
   - Implement core database operations
   - JSON field support
   - Binary vector storage
   - External vector service integration

### 5.3 Phase 3: Migration System (Week 6)

#### Tasks
1. **Migration Framework**
   - Migration tracking table
   - Version management
   - Rollback support
   - Checksum validation

2. **Schema Migrations**
   - Convert existing schema to migrations
   - Database-specific variations
   - Data migration scripts
   - Migration testing

### 5.4 Phase 4: Service Layer Refactoring (Weeks 7-8)

#### Tasks
1. **Refactor Storage Services**
   - Replace Supabase client with DAL
   - Update chunking logic
   - Maintain service interfaces
   - Add adapter selection

2. **Refactor Search Services**
   - Use IVectorStore interface
   - Support multiple vector backends
   - Implement fallback strategies
   - Performance optimization

3. **Refactor Project Services**
   - Database-agnostic queries
   - Transaction management
   - Batch operations
   - Error handling

### 5.5 Phase 5: Testing & Documentation (Week 9)

#### Tasks
1. **Unit Testing**
   - Adapter unit tests
   - Query builder tests
   - Migration tests
   - Mock database tests

2. **Integration Testing**
   - Multi-database test suite
   - Performance benchmarks
   - Load testing
   - Failover testing

3. **Documentation**
   - API documentation
   - Migration guide
   - Configuration examples
   - Troubleshooting guide

### 5.6 Phase 6: Deployment & Monitoring (Week 10)

#### Tasks
1. **Deployment Configuration**
   - Docker compose updates
   - Environment templates
   - CI/CD pipeline updates
   - Rollback procedures

2. **Monitoring Setup**
   - Database metrics
   - Query performance tracking
   - Error rate monitoring
   - Connection pool metrics

---

## 6. Task Breakdown

### 6.1 Development Tasks

```yaml
epic: Multi-Database Support
stories:
  - story: Database Abstraction Layer
    points: 8
    tasks:
      - task: Define IDatabase interface
        hours: 4
        assignee: backend-lead
      - task: Define IVectorStore interface
        hours: 4
        assignee: backend-lead
      - task: Create base adapter class
        hours: 6
        assignee: backend-dev
      - task: Implement connection manager
        hours: 8
        assignee: backend-dev
      - task: Add error handling and retry logic
        hours: 6
        assignee: backend-dev

  - story: Query Builder Implementation
    points: 5
    tasks:
      - task: Implement basic CRUD operations
        hours: 6
        assignee: backend-dev
      - task: Add JSON field support
        hours: 4
        assignee: backend-dev
      - task: Implement join operations
        hours: 4
        assignee: backend-dev
      - task: Add transaction support
        hours: 6
        assignee: backend-dev

  - story: Supabase Adapter
    points: 5
    tasks:
      - task: Implement IDatabase methods
        hours: 6
        assignee: backend-dev
      - task: Implement IVectorStore methods
        hours: 6
        assignee: backend-dev
      - task: Add backward compatibility layer
        hours: 4
        assignee: backend-dev
      - task: Write adapter tests
        hours: 4
        assignee: qa-engineer

  - story: PostgreSQL Adapter
    points: 8
    tasks:
      - task: Setup asyncpg connection pool
        hours: 4
        assignee: backend-dev
      - task: Implement database operations
        hours: 8
        assignee: backend-dev
      - task: Add pgvector support
        hours: 6
        assignee: backend-dev
      - task: Implement custom functions
        hours: 6
        assignee: backend-dev
      - task: Write adapter tests
        hours: 4
        assignee: qa-engineer

  - story: MySQL Adapter
    points: 8
    tasks:
      - task: Setup aiomysql connection pool
        hours: 4
        assignee: backend-dev
      - task: Implement database operations
        hours: 8
        assignee: backend-dev
      - task: Add JSON field support
        hours: 4
        assignee: backend-dev
      - task: Implement vector storage strategy
        hours: 8
        assignee: backend-dev
      - task: Write adapter tests
        hours: 4
        assignee: qa-engineer

  - story: Migration System
    points: 5
    tasks:
      - task: Create migration framework
        hours: 6
        assignee: backend-lead
      - task: Convert existing schema to migrations
        hours: 8
        assignee: backend-dev
      - task: Add database-specific migrations
        hours: 6
        assignee: backend-dev
      - task: Implement rollback functionality
        hours: 4
        assignee: backend-dev

  - story: Service Layer Refactoring
    points: 13
    tasks:
      - task: Refactor storage services
        hours: 8
        assignee: backend-dev
      - task: Refactor search services
        hours: 8
        assignee: backend-dev
      - task: Refactor project services
        hours: 8
        assignee: backend-dev
      - task: Update API routes
        hours: 6
        assignee: backend-dev
      - task: Update MCP server
        hours: 6
        assignee: backend-dev
      - task: Update agents service
        hours: 6
        assignee: backend-dev

  - story: Testing Suite
    points: 8
    tasks:
      - task: Write unit tests for DAL
        hours: 8
        assignee: qa-engineer
      - task: Create integration test suite
        hours: 8
        assignee: qa-engineer
      - task: Add performance benchmarks
        hours: 6
        assignee: qa-engineer
      - task: Setup CI/CD test matrix
        hours: 4
        assignee: devops

  - story: Documentation
    points: 3
    tasks:
      - task: Write API documentation
        hours: 4
        assignee: tech-writer
      - task: Create migration guide
        hours: 3
        assignee: tech-writer
      - task: Write configuration examples
        hours: 3
        assignee: tech-writer
      - task: Create troubleshooting guide
        hours: 2
        assignee: tech-writer

  - story: Deployment & Monitoring
    points: 5
    tasks:
      - task: Update Docker configurations
        hours: 4
        assignee: devops
      - task: Create environment templates
        hours: 2
        assignee: devops
      - task: Setup database monitoring
        hours: 6
        assignee: devops
      - task: Configure alerting rules
        hours: 4
        assignee: devops
      - task: Create rollback procedures
        hours: 4
        assignee: devops
```

### 6.2 Testing Requirements

#### Unit Tests
- 90% code coverage for DAL
- All adapters fully tested
- Query builder edge cases
- Migration rollback scenarios

#### Integration Tests
- Multi-database test matrix
- Connection failure handling
- Transaction rollback testing
- Vector search accuracy

#### Performance Tests
- Query execution benchmarks
- Connection pool stress testing
- Vector search performance
- Bulk operation throughput

### 6.3 Documentation Deliverables

1. **Developer Guide**
   - Architecture overview
   - Adapter implementation guide
   - Migration creation guide
   - Testing strategies

2. **Operations Guide**
   - Installation procedures
   - Configuration management
   - Monitoring setup
   - Troubleshooting

3. **API Reference**
   - Interface documentation
   - Adapter methods
   - Query builder API
   - Migration API

---

## 7. Risk Analysis

### 7.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Performance degradation | High | Medium | Comprehensive benchmarking, caching layer |
| Vector search incompatibility | High | Medium | External vector database fallback |
| Migration failures | High | Low | Rollback support, thorough testing |
| Connection pool exhaustion | Medium | Medium | Dynamic pool sizing, monitoring |
| Data consistency issues | High | Low | Transaction management, validation |

### 7.2 Operational Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Complex configuration | Medium | High | Configuration templates, validation |
| Increased monitoring overhead | Low | High | Automated monitoring setup |
| Deployment complexity | Medium | Medium | Docker compose templates |
| Team knowledge gaps | Medium | Medium | Training sessions, documentation |

---

## 8. Success Metrics

### 8.1 Performance Metrics
- Query execution time < 110% of direct Supabase
- Connection establishment < 500ms
- Vector search latency < 200ms
- Transaction throughput > 1000 TPS

### 8.2 Quality Metrics
- Code coverage > 90%
- Zero data corruption incidents
- < 1% query failure rate
- All migrations reversible

### 8.3 Adoption Metrics
- 3 production deployments in first month
- 50% of developers using local SQLite
- Zero rollbacks due to DAL issues
- 100% backward compatibility maintained

---

## 9. Configuration Examples

### 9.1 Environment Variables

```bash
# Database Type Selection
DATABASE_TYPE=postgresql  # supabase, postgresql, mysql, sqlite

# PostgreSQL Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/archon
DATABASE_POOL_SIZE=20
DATABASE_POOL_TIMEOUT=30

# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=archon
MYSQL_PASSWORD=secure_password
MYSQL_DATABASE=archon_db

# Vector Database (Optional)
VECTOR_DATABASE=pinecone  # pinecone, weaviate, chroma
PINECONE_API_KEY=your_api_key
PINECONE_ENVIRONMENT=us-west1-gcp

# Feature Flags
ENABLE_VECTOR_SEARCH=true
ENABLE_PROJECTS=true
ENABLE_READ_REPLICAS=false

# Monitoring
ENABLE_QUERY_LOGGING=true
SLOW_QUERY_THRESHOLD_MS=1000
```

### 9.2 Docker Compose Configuration

```yaml
version: '3.8'

services:
  archon-api:
    build: ./python
    environment:
      DATABASE_TYPE: ${DATABASE_TYPE:-postgresql}
      DATABASE_URL: ${DATABASE_URL}
      VECTOR_DATABASE: ${VECTOR_DATABASE:-}
    depends_on:
      - postgres
      - mysql

  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: archon
      POSTGRES_PASSWORD: archon_password
      POSTGRES_DB: archon_db
    volumes:
      - postgres_data:/var/lib/postgresql/data

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: archon_db
      MYSQL_USER: archon
      MYSQL_PASSWORD: archon_password
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  postgres_data:
  mysql_data:
```

---

## 10. Conclusion

This specification provides a comprehensive approach to adding multi-database support to Archon V2 Alpha. The proposed Database Abstraction Layer maintains backward compatibility while enabling support for PostgreSQL, MySQL, and various vector databases.

Key benefits include:
- **Flexibility**: Choose the right database for your deployment
- **Cost Optimization**: Use SQLite for development, scale to PostgreSQL for production
- **Performance**: Optimized adapters for each database type
- **Maintainability**: Clean separation of concerns with clear interfaces

The implementation plan spans 10 weeks with clear milestones and deliverables. Success will be measured through performance benchmarks, quality metrics, and adoption rates.

### Next Steps
1. Review and approve specification
2. Assign development team
3. Setup development environment
4. Begin Phase 1 implementation
5. Schedule weekly progress reviews

---

## Appendix A: Database Feature Matrix

| Feature | Supabase | PostgreSQL | MySQL 8.0+ | SQLite |
|---------|----------|------------|------------|--------|
| Vector Search | ✅ Native | ✅ pgvector | ⚠️ External | ❌ External |
| JSON Support | ✅ JSONB | ✅ JSONB | ✅ JSON | ⚠️ JSON1 |
| Full-Text Search | ✅ | ✅ | ✅ | ⚠️ FTS5 |
| Transactions | ✅ | ✅ | ✅ | ✅ |
| Row-Level Security | ✅ | ✅ | ❌ | ❌ |
| Replication | ✅ | ✅ | ✅ | ❌ |
| Connection Pooling | ✅ | ✅ | ✅ | N/A |
| Cloud Native | ✅ | ⚠️ | ⚠️ | ❌ |

## Appendix B: Migration Path Examples

### From Supabase to PostgreSQL
1. Export data using pg_dump
2. Update environment variables
3. Run migration system
4. Verify data integrity
5. Update monitoring

### From Supabase to MySQL
1. Export data to JSON
2. Transform data types
3. Import to MySQL
4. Setup vector service
5. Update configuration

### New Installation
1. Choose database type
2. Set environment variables
3. Run migrations
4. Verify installation
5. Begin development