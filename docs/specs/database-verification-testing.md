# Database Verification and Testing Specification
## MySQL and PostgreSQL Support Validation for Archon V2

### Document Version: 1.0.0
### Date: 2025-08-16
### Status: Draft
### Authors: System Architecture Team

---

## 1. Executive Summary

### Current State
Archon V2 has implemented a Database Abstraction Layer (DAL) with interfaces and a Supabase adapter. The system needs verification that MySQL and PostgreSQL databases can fully replace Supabase as the backend.

### Proposed Solution
Create a comprehensive testing framework with Docker-based database environments, automated migration scripts, and integration tests to verify full compatibility with MySQL 8.0+ and PostgreSQL 14+ databases.

### Key Deliverables
- Docker Compose configurations for MySQL and PostgreSQL environments
- Database migration scripts with schema adaptation
- Adapter implementations for MySQL and PostgreSQL
- Automated test suite for database compatibility
- Performance benchmarking framework
- Documentation for database-specific configurations

---

## 2. Requirements

### 2.1 Functional Requirements

#### Database Environment Setup
- **FR-1**: Docker Compose file supporting MySQL 8.0+ with proper configuration
- **FR-2**: Docker Compose file supporting PostgreSQL 14+ with pgvector extension
- **FR-3**: Automated database initialization on container startup
- **FR-4**: Support for both single-node and replicated configurations
- **FR-5**: Persistent volume management for data retention

#### Schema Migration
- **FR-6**: Convert Supabase schema to MySQL-compatible DDL
- **FR-7**: Convert Supabase schema to PostgreSQL-compatible DDL
- **FR-8**: Handle vector storage differences between databases
- **FR-9**: Migrate all indexes, constraints, and triggers
- **FR-10**: Support for JSONB to JSON field conversion (MySQL)

#### Adapter Implementation
- **FR-11**: Complete MySQL adapter implementing IDatabase interface
- **FR-12**: Complete PostgreSQL adapter implementing IDatabase and IVectorStore
- **FR-13**: Connection pooling for both adapters
- **FR-14**: Transaction support with proper isolation levels
- **FR-15**: Batch operation optimization

#### Testing Framework
- **FR-16**: Unit tests for each adapter method
- **FR-17**: Integration tests covering all CRUD operations
- **FR-18**: Vector search accuracy tests
- **FR-19**: Performance benchmarks against Supabase baseline
- **FR-20**: Data integrity validation tests

### 2.2 Non-Functional Requirements

#### Performance
- **NFR-1**: Query performance within 120% of Supabase baseline
- **NFR-2**: Support for 100+ concurrent connections
- **NFR-3**: Sub-second response time for standard queries
- **NFR-4**: Efficient handling of large BLOB/TEXT fields

#### Reliability
- **NFR-5**: Automatic reconnection on connection loss
- **NFR-6**: Graceful degradation for missing features
- **NFR-7**: Transaction rollback on errors
- **NFR-8**: Connection pool recovery after database restart

#### Compatibility
- **NFR-9**: Zero changes required in application code
- **NFR-10**: Backward compatible with existing API
- **NFR-11**: Support for all existing Archon features
- **NFR-12**: Database-agnostic test suite

---

## 3. Technical Architecture

### 3.1 Docker Environment Structure

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  # PostgreSQL with pgvector
  postgres:
    image: pgvector/pgvector:pg16
    container_name: archon-postgres
    environment:
      POSTGRES_USER: archon
      POSTGRES_PASSWORD: archon_secure_password
      POSTGRES_DB: archon_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./migrations/postgres/init.sql:/docker-entrypoint-initdb.d/01-init.sql
      - ./migrations/postgres/schema.sql:/docker-entrypoint-initdb.d/02-schema.sql
      - ./migrations/postgres/functions.sql:/docker-entrypoint-initdb.d/03-functions.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U archon"]
      interval: 10s
      timeout: 5s
      retries: 5

  # MySQL 8.0
  mysql:
    image: mysql:8.0
    container_name: archon-mysql
    environment:
      MYSQL_ROOT_PASSWORD: root_secure_password
      MYSQL_DATABASE: archon_db
      MYSQL_USER: archon
      MYSQL_PASSWORD: archon_secure_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./migrations/mysql/init.sql:/docker-entrypoint-initdb.d/01-init.sql
      - ./migrations/mysql/schema.sql:/docker-entrypoint-initdb.d/02-schema.sql
      - ./migrations/mysql/procedures.sql:/docker-entrypoint-initdb.d/03-procedures.sql
    command: --default-authentication-plugin=mysql_native_password --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis for caching (optional)
  redis:
    image: redis:7-alpine
    container_name: archon-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Adminer for database management
  adminer:
    image: adminer
    container_name: archon-adminer
    ports:
      - "8080:8080"
    environment:
      ADMINER_DEFAULT_SERVER: postgres
    depends_on:
      - postgres
      - mysql

volumes:
  postgres_data:
  mysql_data:
  redis_data:

networks:
  default:
    name: archon-network
```

### 3.2 PostgreSQL Schema Migration

```sql
-- migrations/postgres/init.sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- migrations/postgres/schema.sql
-- Core tables matching Supabase schema
CREATE TABLE archon_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url TEXT,
    title TEXT,
    source_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    metadata JSONB DEFAULT '{}',
    error_message TEXT,
    crawled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE archon_crawled_pages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES archon_sources(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    title TEXT,
    content TEXT,
    chunk_index INTEGER DEFAULT 0,
    total_chunks INTEGER DEFAULT 1,
    metadata JSONB DEFAULT '{}',
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE archon_code_examples (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES archon_sources(id) ON DELETE CASCADE,
    file_path TEXT,
    function_name TEXT,
    class_name TEXT,
    code_snippet TEXT,
    language VARCHAR(50),
    summary TEXT,
    metadata JSONB DEFAULT '{}',
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE archon_projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    github_repo TEXT,
    docs JSONB DEFAULT '[]',
    features JSONB DEFAULT '{}',
    data JSONB DEFAULT '{}',
    prd JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE archon_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES archon_projects(id) ON DELETE CASCADE,
    parent_task_id UUID REFERENCES archon_tasks(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'todo',
    assignee VARCHAR(100) DEFAULT 'User',
    task_order INTEGER DEFAULT 0,
    feature VARCHAR(100),
    sources JSONB DEFAULT '[]',
    code_examples JSONB DEFAULT '[]',
    archived BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMP WITH TIME ZONE,
    archived_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_sources_status ON archon_sources(status);
CREATE INDEX idx_sources_created ON archon_sources(created_at DESC);
CREATE INDEX idx_crawled_source ON archon_crawled_pages(source_id);
CREATE INDEX idx_crawled_embedding ON archon_crawled_pages USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_code_embedding ON archon_code_examples USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_tasks_project ON archon_tasks(project_id);
CREATE INDEX idx_tasks_status ON archon_tasks(status);
CREATE INDEX idx_projects_created ON archon_projects(created_at DESC);

-- migrations/postgres/functions.sql
-- Vector similarity search functions
CREATE OR REPLACE FUNCTION match_archon_crawled_pages(
    query_embedding vector(1536),
    match_count INT DEFAULT 10,
    filter JSONB DEFAULT '{}'::jsonb
)
RETURNS TABLE (
    id UUID,
    source_id UUID,
    url TEXT,
    title TEXT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cp.id,
        cp.source_id,
        cp.url,
        cp.title,
        cp.content,
        cp.metadata,
        1 - (cp.embedding <=> query_embedding) AS similarity
    FROM archon_crawled_pages cp
    WHERE (filter IS NULL OR cp.metadata @> filter)
    ORDER BY cp.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

CREATE OR REPLACE FUNCTION match_archon_code_examples(
    query_embedding vector(1536),
    match_count INT DEFAULT 10,
    filter JSONB DEFAULT '{}'::jsonb
)
RETURNS TABLE (
    id UUID,
    source_id UUID,
    file_path TEXT,
    function_name TEXT,
    code_snippet TEXT,
    summary TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ce.id,
        ce.source_id,
        ce.file_path,
        ce.function_name,
        ce.code_snippet,
        ce.summary,
        ce.metadata,
        1 - (ce.embedding <=> query_embedding) AS similarity
    FROM archon_code_examples ce
    WHERE (filter IS NULL OR ce.metadata @> filter)
    ORDER BY ce.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

### 3.3 MySQL Schema Migration

```sql
-- migrations/mysql/init.sql
-- Set proper character encoding
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- migrations/mysql/schema.sql
-- Core tables adapted for MySQL
CREATE TABLE archon_sources (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    url TEXT,
    title TEXT,
    source_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    metadata JSON DEFAULT (JSON_OBJECT()),
    error_message TEXT,
    crawled_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_created (created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE archon_crawled_pages (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    source_id CHAR(36),
    url TEXT NOT NULL,
    title TEXT,
    content LONGTEXT,
    chunk_index INT DEFAULT 0,
    total_chunks INT DEFAULT 1,
    metadata JSON DEFAULT (JSON_OBJECT()),
    embedding BLOB,  -- Store as binary, 1536 * 4 bytes for float32
    embedding_json JSON GENERATED ALWAYS AS (
        CASE 
            WHEN embedding IS NOT NULL 
            THEN JSON_ARRAY() -- Placeholder, actual parsing in application
            ELSE NULL 
        END
    ) VIRTUAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES archon_sources(id) ON DELETE CASCADE,
    INDEX idx_source (source_id),
    FULLTEXT INDEX idx_content (title, content)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE archon_code_examples (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    source_id CHAR(36),
    file_path TEXT,
    function_name TEXT,
    class_name TEXT,
    code_snippet TEXT,
    language VARCHAR(50),
    summary TEXT,
    metadata JSON DEFAULT (JSON_OBJECT()),
    embedding BLOB,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES archon_sources(id) ON DELETE CASCADE,
    INDEX idx_source (source_id),
    INDEX idx_language (language)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE archon_projects (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    title TEXT NOT NULL,
    description TEXT,
    github_repo TEXT,
    docs JSON DEFAULT (JSON_ARRAY()),
    features JSON DEFAULT (JSON_OBJECT()),
    data JSON DEFAULT (JSON_OBJECT()),
    prd JSON DEFAULT (JSON_OBJECT()),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_created (created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE archon_tasks (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    project_id CHAR(36),
    parent_task_id CHAR(36),
    title TEXT NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'todo',
    assignee VARCHAR(100) DEFAULT 'User',
    task_order INT DEFAULT 0,
    feature VARCHAR(100),
    sources JSON DEFAULT (JSON_ARRAY()),
    code_examples JSON DEFAULT (JSON_ARRAY()),
    archived BOOLEAN DEFAULT FALSE,
    archived_at DATETIME,
    archived_by VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES archon_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_task_id) REFERENCES archon_tasks(id) ON DELETE CASCADE,
    INDEX idx_project (project_id),
    INDEX idx_status (status),
    INDEX idx_order (task_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- External vector index table for MySQL
CREATE TABLE archon_vector_index (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    table_name VARCHAR(50) NOT NULL,
    record_id CHAR(36) NOT NULL,
    vector_service VARCHAR(50) DEFAULT 'local',
    external_id VARCHAR(255),
    metadata JSON DEFAULT (JSON_OBJECT()),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_table_record (table_name, record_id),
    INDEX idx_external (external_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- migrations/mysql/procedures.sql
-- Stored procedures for vector operations
DELIMITER //

CREATE PROCEDURE search_vectors(
    IN p_table_name VARCHAR(50),
    IN p_query_vector JSON,
    IN p_match_count INT
)
BEGIN
    -- This is a placeholder for vector search
    -- Actual implementation would use external service or custom logic
    -- For testing, return random results
    IF p_table_name = 'archon_crawled_pages' THEN
        SELECT 
            id,
            source_id,
            url,
            title,
            content,
            metadata,
            RAND() AS similarity
        FROM archon_crawled_pages
        ORDER BY RAND()
        LIMIT p_match_count;
    ELSEIF p_table_name = 'archon_code_examples' THEN
        SELECT 
            id,
            source_id,
            file_path,
            function_name,
            code_snippet,
            summary,
            metadata,
            RAND() AS similarity
        FROM archon_code_examples
        ORDER BY RAND()
        LIMIT p_match_count;
    END IF;
END//

CREATE FUNCTION calculate_cosine_similarity(
    vector1 JSON,
    vector2 JSON
)
RETURNS FLOAT
DETERMINISTIC
BEGIN
    -- Placeholder for cosine similarity calculation
    -- Real implementation would parse JSON arrays and compute similarity
    RETURN RAND();
END//

DELIMITER ;
```

### 3.4 Database Adapter Implementations

#### PostgreSQL Adapter

```python
# python/src/server/dal/adapters/postgresql_adapter.py
import asyncpg
import json
import numpy as np
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from ...config.logfire_config import search_logger
from ..interfaces import (
    IDatabase,
    IDatabaseWithVectors,
    ITransaction,
    QueryResult,
    TransactionState,
    VectorSearchResult,
)


class PostgreSQLTransaction(ITransaction):
    """PostgreSQL transaction implementation"""
    
    def __init__(self, connection: asyncpg.Connection):
        super().__init__(None)
        self.connection = connection
        self.transaction = None
    
    async def __aenter__(self):
        self.transaction = self.connection.transaction()
        await self.transaction.start()
        return self
    
    async def commit(self):
        if self.transaction and self.state == TransactionState.PENDING:
            await self.transaction.commit()
            self.state = TransactionState.COMMITTED
    
    async def rollback(self):
        if self.transaction and self.state == TransactionState.PENDING:
            await self.transaction.rollback()
            self.state = TransactionState.ROLLED_BACK


class PostgreSQLAdapter(IDatabaseWithVectors):
    """PostgreSQL adapter with pgvector support"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "archon_db",
        user: str = "archon",
        password: str = "archon_password",
        **kwargs
    ):
        self.connection_params = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
            **kwargs
        }
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create connection pool"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                **self.connection_params,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            
            # Ensure pgvector extension is enabled
            async with self.pool.acquire() as conn:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            search_logger.info("PostgreSQL adapter connected")
    
    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            search_logger.info("PostgreSQL adapter disconnected")
    
    async def health_check(self) -> bool:
        """Check connection health"""
        if not self.pool:
            return False
        
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
                return True
        except Exception as e:
            search_logger.error(f"PostgreSQL health check failed: {e}")
            return False
    
    # Implement all IDatabase methods...
    # (Full implementation would be similar to Supabase adapter)
```

#### MySQL Adapter

```python
# python/src/server/dal/adapters/mysql_adapter.py
import aiomysql
import json
import numpy as np
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from ...config.logfire_config import search_logger
from ..interfaces import IDatabase, ITransaction, QueryResult, TransactionState


class MySQLTransaction(ITransaction):
    """MySQL transaction implementation"""
    
    def __init__(self, connection: aiomysql.Connection):
        super().__init__(None)
        self.connection = connection
    
    async def __aenter__(self):
        await self.connection.begin()
        return self
    
    async def commit(self):
        if self.state == TransactionState.PENDING:
            await self.connection.commit()
            self.state = TransactionState.COMMITTED
    
    async def rollback(self):
        if self.state == TransactionState.PENDING:
            await self.connection.rollback()
            self.state = TransactionState.ROLLED_BACK


class MySQLAdapter(IDatabase):
    """MySQL adapter implementation"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        database: str = "archon_db",
        user: str = "archon",
        password: str = "archon_password",
        **kwargs
    ):
        self.connection_params = {
            "host": host,
            "port": port,
            "db": database,
            "user": user,
            "password": password,
            "charset": "utf8mb4",
            **kwargs
        }
        self.pool: Optional[aiomysql.Pool] = None
    
    async def connect(self):
        """Create connection pool"""
        if not self.pool:
            self.pool = await aiomysql.create_pool(
                **self.connection_params,
                minsize=5,
                maxsize=20,
                autocommit=False
            )
            search_logger.info("MySQL adapter connected")
    
    # Implement all IDatabase methods...
    # (Full implementation similar to PostgreSQL but without vector operations)
```

---

## 4. Testing Strategy

### 4.1 Unit Tests

```python
# tests/dal/test_postgresql_adapter.py
import pytest
import asyncio
from src.server.dal.adapters.postgresql_adapter import PostgreSQLAdapter

@pytest.mark.asyncio
async def test_postgresql_connection():
    """Test PostgreSQL adapter connection"""
    adapter = PostgreSQLAdapter(
        host="localhost",
        database="archon_test"
    )
    
    await adapter.connect()
    assert await adapter.health_check()
    
    await adapter.disconnect()
    assert not await adapter.health_check()

@pytest.mark.asyncio
async def test_postgresql_crud():
    """Test CRUD operations"""
    adapter = PostgreSQLAdapter()
    await adapter.connect()
    
    # Insert
    result = await adapter.insert(
        "archon_sources",
        {"url": "https://test.com", "title": "Test"}
    )
    assert result.success
    assert len(result.data) == 1
    
    # Select
    result = await adapter.select("archon_sources")
    assert result.success
    assert len(result.data) > 0
    
    # Update
    source_id = result.data[0]["id"]
    result = await adapter.update(
        "archon_sources",
        {"title": "Updated"},
        {"id": source_id}
    )
    assert result.success
    
    # Delete
    result = await adapter.delete(
        "archon_sources",
        {"id": source_id}
    )
    assert result.success
    
    await adapter.disconnect()
```

### 4.2 Integration Tests

```python
# tests/integration/test_database_compatibility.py
import pytest
from src.server.dal import ConnectionManager, DatabaseType

@pytest.mark.parametrize("db_type", [
    DatabaseType.SUPABASE,
    DatabaseType.POSTGRESQL,
    DatabaseType.MYSQL
])
@pytest.mark.asyncio
async def test_database_operations(db_type, monkeypatch):
    """Test operations across all database types"""
    monkeypatch.setenv("DATABASE_TYPE", db_type.value)
    
    manager = ConnectionManager.from_env()
    await manager.initialize()
    
    async with manager.get_primary() as db:
        # Test all operations
        result = await db.select("archon_projects", limit=10)
        assert result.success
    
    await manager.close()
```

### 4.3 Performance Benchmarks

```python
# tests/benchmarks/benchmark_databases.py
import time
import asyncio
from statistics import mean, stdev

async def benchmark_query(adapter, query_func, iterations=100):
    """Benchmark a query function"""
    times = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        await query_func(adapter)
        end = time.perf_counter()
        times.append(end - start)
    
    return {
        "mean": mean(times),
        "stdev": stdev(times),
        "min": min(times),
        "max": max(times)
    }

async def run_benchmarks():
    """Run benchmarks for all databases"""
    databases = {
        "Supabase": SupabaseAdapter(),
        "PostgreSQL": PostgreSQLAdapter(),
        "MySQL": MySQLAdapter()
    }
    
    results = {}
    
    for name, adapter in databases.items():
        await adapter.connect()
        
        # Benchmark SELECT
        select_results = await benchmark_query(
            adapter,
            lambda a: a.select("archon_sources", limit=100)
        )
        
        # Benchmark INSERT
        insert_results = await benchmark_query(
            adapter,
            lambda a: a.insert("archon_sources", {"url": "test", "title": "test"}),
            iterations=50
        )
        
        results[name] = {
            "select": select_results,
            "insert": insert_results
        }
        
        await adapter.disconnect()
    
    return results
```

---

## 5. Implementation Plan

### 5.1 Phase 1: Environment Setup (Week 1)

#### Tasks
1. **Create Docker Compose Configuration**
   - Setup PostgreSQL with pgvector
   - Setup MySQL 8.0
   - Configure networking and volumes
   - Add health checks

2. **Create Migration Scripts**
   - PostgreSQL schema with vector support
   - MySQL schema with JSON fields
   - Index creation scripts
   - Function/procedure definitions

3. **Setup Development Environment**
   - Environment variable templates
   - Docker helper scripts
   - Database initialization automation

### 5.2 Phase 2: Adapter Implementation (Week 2-3)

#### Tasks
1. **PostgreSQL Adapter**
   - Connection pool management
   - CRUD operations
   - Vector operations with pgvector
   - Transaction support

2. **MySQL Adapter**
   - Connection pool management
   - CRUD operations
   - JSON field handling
   - External vector service integration

3. **Adapter Registration**
   - Update ConnectionManager
   - Add adapter auto-discovery
   - Configuration validation

### 5.3 Phase 3: Testing Framework (Week 4)

#### Tasks
1. **Unit Tests**
   - Test each adapter method
   - Mock database connections
   - Error handling tests
   - Edge case coverage

2. **Integration Tests**
   - Cross-database compatibility
   - Data integrity validation
   - Transaction rollback tests
   - Connection failure recovery

3. **Performance Tests**
   - Query benchmarks
   - Load testing
   - Memory usage profiling
   - Connection pool stress tests

### 5.4 Phase 4: Verification & Documentation (Week 5)

#### Tasks
1. **End-to-End Testing**
   - Full application testing with each database
   - API endpoint validation
   - WebSocket functionality
   - MCP server compatibility

2. **Documentation**
   - Setup guides for each database
   - Migration instructions
   - Performance tuning guides
   - Troubleshooting documentation

---

## 6. Task Breakdown

### 6.1 Development Tasks

```yaml
epic: Database Verification and Testing
stories:
  - story: Docker Environment Setup
    points: 5
    tasks:
      - task: Create docker-compose.dev.yml
        hours: 3
        assignee: devops
        priority: high
      - task: Configure PostgreSQL container
        hours: 2
        assignee: devops
        priority: high
      - task: Configure MySQL container
        hours: 2
        assignee: devops
        priority: high
      - task: Setup persistent volumes
        hours: 1
        assignee: devops
        priority: medium
      - task: Add health checks
        hours: 1
        assignee: devops
        priority: medium

  - story: PostgreSQL Migration Scripts
    points: 8
    tasks:
      - task: Create schema migration
        hours: 4
        assignee: backend-dev
        priority: high
      - task: Add vector functions
        hours: 3
        assignee: backend-dev
        priority: high
      - task: Create indexes
        hours: 2
        assignee: backend-dev
        priority: medium
      - task: Add triggers and constraints
        hours: 2
        assignee: backend-dev
        priority: low

  - story: MySQL Migration Scripts
    points: 8
    tasks:
      - task: Create schema migration
        hours: 4
        assignee: backend-dev
        priority: high
      - task: Handle JSON fields
        hours: 3
        assignee: backend-dev
        priority: high
      - task: Create stored procedures
        hours: 3
        assignee: backend-dev
        priority: medium
      - task: Add indexes
        hours: 2
        assignee: backend-dev
        priority: medium

  - story: PostgreSQL Adapter Implementation
    points: 13
    tasks:
      - task: Implement connection management
        hours: 3
        assignee: backend-dev
        priority: high
      - task: Implement CRUD operations
        hours: 6
        assignee: backend-dev
        priority: high
      - task: Implement vector operations
        hours: 6
        assignee: backend-dev
        priority: high
      - task: Add transaction support
        hours: 4
        assignee: backend-dev
        priority: medium
      - task: Add error handling
        hours: 3
        assignee: backend-dev
        priority: medium

  - story: MySQL Adapter Implementation
    points: 13
    tasks:
      - task: Implement connection management
        hours: 3
        assignee: backend-dev
        priority: high
      - task: Implement CRUD operations
        hours: 6
        assignee: backend-dev
        priority: high
      - task: Handle JSON operations
        hours: 4
        assignee: backend-dev
        priority: high
      - task: Add transaction support
        hours: 4
        assignee: backend-dev
        priority: medium
      - task: Integrate vector service
        hours: 5
        assignee: backend-dev
        priority: low

  - story: Testing Framework
    points: 8
    tasks:
      - task: Create unit test suite
        hours: 6
        assignee: qa-engineer
        priority: high
      - task: Create integration tests
        hours: 6
        assignee: qa-engineer
        priority: high
      - task: Create performance benchmarks
        hours: 4
        assignee: qa-engineer
        priority: medium
      - task: Setup CI/CD pipeline
        hours: 3
        assignee: devops
        priority: medium

  - story: End-to-End Verification
    points: 5
    tasks:
      - task: Test with PostgreSQL
        hours: 4
        assignee: qa-engineer
        priority: high
      - task: Test with MySQL
        hours: 4
        assignee: qa-engineer
        priority: high
      - task: Performance comparison
        hours: 3
        assignee: qa-engineer
        priority: medium
      - task: Document results
        hours: 2
        assignee: tech-writer
        priority: low

  - story: Documentation
    points: 3
    tasks:
      - task: Write setup guides
        hours: 3
        assignee: tech-writer
        priority: medium
      - task: Create migration guides
        hours: 2
        assignee: tech-writer
        priority: medium
      - task: Document configuration
        hours: 2
        assignee: tech-writer
        priority: low
      - task: Create troubleshooting guide
        hours: 2
        assignee: tech-writer
        priority: low
```

### 6.2 Helper Scripts

#### Database Setup Script
```bash
#!/bin/bash
# scripts/setup-databases.sh

echo "Setting up Archon databases..."

# Start containers
docker-compose -f docker-compose.dev.yml up -d

# Wait for databases to be ready
echo "Waiting for databases to initialize..."
sleep 10

# Verify PostgreSQL
docker exec archon-postgres psql -U archon -d archon_db -c "SELECT version();"

# Verify MySQL
docker exec archon-mysql mysql -u archon -parchon_secure_password -e "SELECT VERSION();"

echo "Databases ready!"
```

#### Migration Runner
```bash
#!/bin/bash
# scripts/run-migrations.sh

DB_TYPE=${1:-all}

if [ "$DB_TYPE" = "postgres" ] || [ "$DB_TYPE" = "all" ]; then
    echo "Running PostgreSQL migrations..."
    docker exec archon-postgres psql -U archon -d archon_db -f /docker-entrypoint-initdb.d/02-schema.sql
    docker exec archon-postgres psql -U archon -d archon_db -f /docker-entrypoint-initdb.d/03-functions.sql
fi

if [ "$DB_TYPE" = "mysql" ] || [ "$DB_TYPE" = "all" ]; then
    echo "Running MySQL migrations..."
    docker exec archon-mysql mysql -u archon -parchon_secure_password archon_db < /docker-entrypoint-initdb.d/02-schema.sql
    docker exec archon-mysql mysql -u archon -parchon_secure_password archon_db < /docker-entrypoint-initdb.d/03-procedures.sql
fi

echo "Migrations complete!"
```

#### Test Runner
```bash
#!/bin/bash
# scripts/test-databases.sh

# Run unit tests
echo "Running unit tests..."
uv run pytest tests/dal/ -v

# Run integration tests
echo "Running integration tests..."
DATABASE_TYPE=postgresql uv run pytest tests/integration/ -v
DATABASE_TYPE=mysql uv run pytest tests/integration/ -v

# Run benchmarks
echo "Running performance benchmarks..."
uv run python tests/benchmarks/benchmark_databases.py

echo "All tests complete!"
```

---

## 7. Verification Criteria

### 7.1 Functional Verification

| Feature | PostgreSQL | MySQL | Test Method |
|---------|------------|-------|-------------|
| CRUD Operations | ✓ | ✓ | Unit tests |
| Transactions | ✓ | ✓ | Integration tests |
| JSON Fields | ✓ | ✓ | Unit tests |
| Vector Search | ✓ | External | Integration tests |
| Batch Operations | ✓ | ✓ | Load tests |
| Connection Pooling | ✓ | ✓ | Stress tests |
| Error Recovery | ✓ | ✓ | Failure injection |

### 7.2 Performance Verification

| Metric | Target | PostgreSQL | MySQL |
|--------|--------|------------|-------|
| Query Latency | < 100ms | TBD | TBD |
| Throughput | > 1000 QPS | TBD | TBD |
| Connection Time | < 500ms | TBD | TBD |
| Memory Usage | < 500MB | TBD | TBD |
| CPU Usage | < 50% | TBD | TBD |

### 7.3 Compatibility Verification

- [ ] All API endpoints functional
- [ ] WebSocket connections stable
- [ ] MCP server operations successful
- [ ] Data migration without loss
- [ ] Backward compatibility maintained

---

## 8. Risk Analysis

### 8.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Vector search incompatibility | High | Medium | External vector service fallback |
| Performance degradation | Medium | Medium | Query optimization, caching |
| Data type mismatches | Medium | High | Comprehensive type mapping |
| Transaction isolation differences | Low | Medium | Configurable isolation levels |
| Connection pool exhaustion | Medium | Low | Dynamic pool sizing |

### 8.2 Operational Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Complex setup process | Medium | High | Automated scripts, clear docs |
| Migration failures | High | Low | Rollback procedures, backups |
| Docker resource usage | Low | Medium | Resource limits, monitoring |
| Database configuration errors | Medium | Medium | Validation scripts |

---

## 9. Success Metrics

### 9.1 Technical Metrics
- All unit tests passing (100% coverage)
- All integration tests passing
- Performance within 120% of Supabase baseline
- Zero data loss during migration
- Connection pool stability over 24 hours

### 9.2 Operational Metrics
- Setup time < 15 minutes
- Migration time < 30 minutes for 1GB database
- Documentation coverage 100%
- Support for all existing features
- No breaking changes in API

### 9.3 Quality Metrics
- Code review approval
- Security scan passing
- Load test successful (1000 concurrent users)
- Memory leak test passing
- Error rate < 0.1%

---

## 10. Conclusion

This specification provides a comprehensive approach to verifying MySQL and PostgreSQL support for Archon V2. The implementation includes:

1. **Complete Docker environment** for local development and testing
2. **Migration scripts** adapting the schema for each database
3. **Full adapter implementations** maintaining API compatibility
4. **Comprehensive test suite** ensuring functionality and performance
5. **Helper scripts** for easy setup and management

The verification process will validate that Archon can successfully operate with MySQL and PostgreSQL as drop-in replacements for Supabase, providing users with flexibility in their database choice while maintaining full functionality.

### Next Steps
1. Review and approve specification
2. Set up Docker environments
3. Implement database adapters
4. Execute verification tests
5. Document results and recommendations

### Estimated Timeline
- Total Duration: 5 weeks
- Development: 3 weeks
- Testing: 1 week
- Documentation: 1 week

---

## Appendix A: Environment Variables

### PostgreSQL Configuration
```bash
# PostgreSQL Connection
DATABASE_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=archon_db
POSTGRES_USER=archon
POSTGRES_PASSWORD=archon_secure_password

# Connection Pool
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30

# SSL Configuration (optional)
DB_SSL_ENABLED=false
DB_SSL_CA_CERT=/path/to/ca.pem
```

### MySQL Configuration
```bash
# MySQL Connection
DATABASE_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=archon_db
MYSQL_USER=archon
MYSQL_PASSWORD=archon_secure_password

# Connection Pool
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30

# Character Encoding
MYSQL_CHARSET=utf8mb4
MYSQL_COLLATION=utf8mb4_unicode_ci
```

## Appendix B: Quick Start Commands

```bash
# Clone repository
git clone https://github.com/archon/archon-v2.git
cd archon-v2

# Start databases
docker-compose -f docker-compose.dev.yml up -d

# Run migrations
./scripts/run-migrations.sh all

# Run tests
./scripts/test-databases.sh

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop databases
docker-compose -f docker-compose.dev.yml down

# Clean up (including volumes)
docker-compose -f docker-compose.dev.yml down -v
```