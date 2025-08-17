# Database Integration Guide for Archon

## Overview

Archon now supports multiple database backends through a Database Abstraction Layer (DAL):
- **Supabase** (default) - Cloud PostgreSQL with pgvector
- **PostgreSQL** - Standalone PostgreSQL 14+ with pgvector extension
- **MySQL** - MySQL 8.0+ with JSON support

## Quick Start

### Using the Makefile

The easiest way to test database integration is using the provided Makefile:

```bash
# Run complete integration test suite
make integration-test

# Test only MySQL
make test-mysql

# Test only PostgreSQL
make test-postgres

# Start databases without running tests
make start-databases

# View database status
make status

# Stop all databases
make stop-databases
```

### Manual Testing

#### 1. Start Database Containers

```bash
# Start all databases
docker-compose -f docker-compose.dev.yml up -d

# Or start specific database
docker-compose -f docker-compose.dev.yml up -d mysql
docker-compose -f docker-compose.dev.yml up -d postgres
```

#### 2. Run Integration Tests

```bash
# Test MySQL support
DATABASE_TYPE=mysql uv run python test_mysql_support.py

# Test PostgreSQL support
DATABASE_TYPE=postgresql uv run python test_postgres_support.py
```

#### 3. Access Database UI

Open http://localhost:8080 in your browser to access Adminer.

**MySQL credentials:**
- Server: `mysql`
- Username: `archon`
- Password: `archon_secure_password`
- Database: `archon_db`

**PostgreSQL credentials:**
- Server: `postgres`
- Username: `archon`
- Password: `archon_secure_password`
- Database: `archon_db`

## Configuration

### Environment Variables

Set these environment variables to configure database connection:

#### MySQL Configuration
```bash
export DATABASE_TYPE=mysql
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_DATABASE=archon_db
export MYSQL_USER=archon
export MYSQL_PASSWORD=archon_secure_password
```

#### PostgreSQL Configuration
```bash
export DATABASE_TYPE=postgresql
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=archon_db
export POSTGRES_USER=archon
export POSTGRES_PASSWORD=archon_secure_password
```

#### Supabase Configuration (default)
```bash
export DATABASE_TYPE=supabase
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_SERVICE_KEY=your-service-key
```

### Using in Code

```python
from src.server.dal import ConnectionManager, DatabaseType
from src.server.dal.adapters import MySQLAdapter, PostgreSQLAdapter, SupabaseAdapter

# Register adapters
ConnectionManager.register_adapter(DatabaseType.MYSQL, MySQLAdapter)
ConnectionManager.register_adapter(DatabaseType.POSTGRESQL, PostgreSQLAdapter)
ConnectionManager.register_adapter(DatabaseType.SUPABASE, SupabaseAdapter)

# Create connection manager (reads from environment)
manager = ConnectionManager.from_env()
await manager.initialize()

# Use database
async with manager.get_primary() as db:
    result = await db.select("archon_sources", limit=10)
    print(f"Found {len(result.data)} sources")

# Clean up
await manager.close()
```

## Features Supported

### Database Feature Matrix

| Feature | Supabase | PostgreSQL | MySQL |
|---------|----------|------------|-------|
| CRUD Operations | ✅ | ✅ | ✅ |
| Transactions | ✅ | ✅ | ✅ |
| JSON Fields | ✅ (JSONB) | ✅ (JSONB) | ✅ (JSON) |
| Vector Search | ✅ (native) | ✅ (pgvector) | ⚠️ (fallback) |
| Connection Pooling | ✅ | ✅ | ✅ |
| Async Operations | ✅ | ✅ | ✅ |
| Schema Migrations | ✅ | ✅ | ✅ |

### Query Builder

The DAL includes a powerful query builder for database-agnostic queries:

```python
from src.server.dal import query

# Build complex queries
q = (query()
    .table("archon_sources")
    .select("id", "title", "url")
    .where("status", "=", "completed")
    .where_json("metadata", "category", "=", "documentation")
    .order_by("created_at", "DESC")
    .limit(10))

# Execute with any database
async with manager.get_primary() as db:
    result = await q.database(db).execute()
```

## Architecture

### Database Abstraction Layer (DAL)

```
Application Code
       ↓
ConnectionManager
       ↓
Database Adapters (MySQL/PostgreSQL/Supabase)
       ↓
Database Servers
```

### Key Components

1. **ConnectionManager** (`src/server/dal/connection_manager.py`)
   - Manages database connections and pooling
   - Handles environment detection
   - Provides failover and load balancing

2. **Database Interfaces** (`src/server/dal/interfaces.py`)
   - `IDatabase` - Core database operations
   - `IVectorStore` - Vector search operations
   - `ITransaction` - Transaction management

3. **Database Adapters** (`src/server/dal/adapters/`)
   - `SupabaseAdapter` - Supabase client implementation
   - `MySQLAdapter` - MySQL with aiomysql
   - `PostgreSQLAdapter` - PostgreSQL with asyncpg

4. **Query Builder** (`src/server/dal/query_builder.py`)
   - Fluent interface for building queries
   - Database-agnostic query construction
   - SQL injection prevention

## Testing

### Running Integration Tests

```bash
# Run all tests
make integration-test

# Run with verbose output
make integration-test VERBOSE=1

# Run specific test
make test-mysql
make test-postgres

# Run performance benchmarks
make benchmark
```

### Test Coverage

The integration tests verify:
- ✅ Database connectivity
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Transaction support
- ✅ JSON field handling
- ✅ Connection pooling
- ✅ Concurrent query execution
- ✅ Error handling and recovery
- ✅ Schema compatibility

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
name: Database Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install uv
        uv sync
    
    - name: Run integration tests
      run: make ci
```

## Troubleshooting

### Common Issues

#### 1. Database container won't start
```bash
# Check container logs
docker-compose -f docker-compose.dev.yml logs mysql
docker-compose -f docker-compose.dev.yml logs postgres

# Clean up and restart
make clean-databases
make start-databases
```

#### 2. Connection refused errors
```bash
# Check if containers are running
docker ps

# Test connection
make test-connection

# Restart containers
make stop-databases
make start-databases
```

#### 3. Schema not found errors
```bash
# MySQL: Re-run migrations
docker exec archon-mysql mysql -u archon -parchon_secure_password archon_db < migrations/mysql/schema.sql

# PostgreSQL: Re-run migrations
docker exec archon-postgres psql -U archon -d archon_db -f /docker-entrypoint-initdb.d/02-schema.sql
```

#### 4. Import errors
```bash
# Install missing dependencies
uv sync

# Or manually install
uv pip install aiomysql asyncpg
```

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or set environment variable
export LOG_LEVEL=DEBUG
```

## Performance Considerations

### Connection Pooling

Default pool sizes:
- Min connections: 5
- Max connections: 20
- Timeout: 30 seconds

Adjust via environment variables:
```bash
export DB_POOL_SIZE=20
export DB_MAX_OVERFLOW=10
export DB_POOL_TIMEOUT=30
```

### Query Optimization

1. **Use indexes**: Ensure proper indexes on frequently queried columns
2. **Limit results**: Always use LIMIT for large tables
3. **Batch operations**: Use bulk insert/update when possible
4. **Connection reuse**: Use connection pooling effectively

### Vector Search Performance

- **PostgreSQL**: Uses pgvector with IVFFlat indexes
- **MySQL**: Falls back to in-memory search (not recommended for large datasets)
- **Supabase**: Native pgvector support with optimized functions

For production MySQL deployments, consider using an external vector service like Pinecone or Weaviate.

## Migration Guide

### From Supabase to MySQL/PostgreSQL

1. Export data from Supabase
2. Set up new database using provided schemas
3. Import data
4. Update environment variables
5. Test with integration suite

### Adding a New Database

1. Create adapter implementing `IDatabase` interface
2. Register adapter with `ConnectionManager`
3. Add schema migrations
4. Update docker-compose.yml
5. Add integration tests

## Contributing

When adding database support:

1. Implement the `IDatabase` interface
2. Add comprehensive tests
3. Update documentation
4. Ensure backward compatibility
5. Run full integration test suite

## License

This database integration is part of the Archon project and follows the same license terms.