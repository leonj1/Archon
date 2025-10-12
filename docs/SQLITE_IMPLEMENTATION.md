# SQLite Database Implementation

## Overview

This document describes the SQLite database backend implementation for Archon, which allows the project to run without external dependencies like Supabase.

## What Has Been Implemented

### ✅ Completed Components

1. **SQLite Repository Pattern Integration**
   - Created `SQLiteDatabaseRepository` class that implements the `DatabaseRepository` interface
   - Integrated with the repository factory pattern
   - Automatically selected when `ARCHON_DB_BACKEND=sqlite`

2. **Database Schema Migration System**
   - Created SQLite-specific migration scripts in `/migration/sqlite/`
   - Implemented `SQLiteMigrationService` that handles:
     - Database initialization
     - Migration tracking
     - Schema creation
     - Health checks

3. **Conditional Initialization**
   - Modified `main.py` to detect SQLite backend and run migrations only when needed
   - Migrations are tracked in `archon_migrations` table to prevent re-running

4. **Complete Schema Implementation**
   All required tables are created with proper structure:
   - `archon_settings` - Configuration and credentials
   - `archon_sources` - Knowledge base sources
   - `archon_crawled_pages` - Document chunks (without vector columns)
   - `archon_code_examples` - Code snippets
   - `archon_page_metadata` - Full documentation pages
   - `archon_projects` - Project management
   - `archon_tasks` - Task tracking
   - `archon_project_sources` - Project-source relationships
   - `archon_document_versions` - Version control
   - `archon_migrations` - Migration tracking

5. **Basic CRUD Operations**
   Implemented essential methods for:
   - Settings management
   - Projects and tasks
   - Sources and documents
   - Page metadata
   - Version control

## Configuration

### Environment Variables

```bash
# Select SQLite backend
ARCHON_DB_BACKEND=sqlite

# Optional: Specify database file path (default: archon.db)
ARCHON_SQLITE_PATH=/path/to/database.db
```

## Usage

### Starting with SQLite Backend

1. Set the environment variable:
   ```bash
   export ARCHON_DB_BACKEND=sqlite
   ```

2. Start the application normally:
   ```bash
   python -m src.server.main
   ```

   The database will be automatically initialized on first run.

### Checking Database Health

```python
from src.server.services.sqlite_migration_service import SQLiteMigrationService

service = SQLiteMigrationService("archon.db")
health = await service.check_database_health()
print(f"Database healthy: {health['is_healthy']}")
print(f"Tables present: {health['required_tables']}")
```

## Limitations

### Current Limitations

1. **Vector Search Not Supported**
   - SQLite doesn't have native vector support
   - Embedding columns are excluded from the schema
   - RAG search falls back to keyword-based search

2. **Stub Implementations**
   - Many repository methods have stub implementations
   - Full feature parity with Supabase backend requires completing all methods

3. **Performance Considerations**
   - No built-in connection pooling
   - File-based storage may be slower for large datasets
   - No native full-text search (using LIKE queries instead)

## Next Steps for Full Implementation

### Priority 1: Complete Core Methods

The following methods need full implementation for basic functionality:

```python
# Document operations
- search_documents_vector()
- search_documents_hybrid()
- insert_document()
- get_document_by_id()

# Settings operations  
- get_all_settings()
- upsert_setting_record()

# Project/Task operations
- list_projects()
- get_project_by_id()
- list_tasks()
- get_task_by_id()
```

### Priority 2: Search Capabilities

Options for implementing vector search in SQLite:
1. Use [SQLite-VSS extension](https://github.com/asg017/sqlite-vss) for vector similarity search
2. Implement in-memory vector search using NumPy
3. Use a hybrid approach with BM25 ranking for text search

### Priority 3: Performance Optimization

1. Implement connection pooling
2. Add database indexes for frequently queried columns
3. Consider using WAL mode for better concurrency
4. Add caching layer for frequently accessed data

## Testing

### Manual Testing

```bash
# Set SQLite backend
export ARCHON_DB_BACKEND=sqlite

# Run the test script
python test_sqlite_simple.py
```

### Integration Testing

The SQLite backend can be tested with the existing test suite by setting the environment variable:

```bash
ARCHON_DB_BACKEND=sqlite pytest tests/
```

## Migration from Supabase

To migrate existing data from Supabase to SQLite:

1. Export data from Supabase (JSON or CSV)
2. Transform data to match SQLite schema
3. Import using the repository methods
4. Verify data integrity

## Benefits of SQLite Backend

1. **No External Dependencies** - Runs completely locally
2. **Simplified Deployment** - Single file database
3. **Easier Development** - No need for Supabase setup
4. **Better Testing** - Fast in-memory testing possible
5. **Data Portability** - Easy backup and migration

## File Structure

```
/migration/sqlite/
  001_initial_schema.sql    # Complete database schema

/python/src/server/
  repositories/
    sqlite_repository.py    # SQLite implementation
    sqlite_repository_stubs.py  # Stub methods
  
  services/
    sqlite_migration_service.py  # Migration handler
```

## Troubleshooting

### Database Not Initializing

1. Check file permissions for database location
2. Ensure migration files exist in `/migration/sqlite/`
3. Check logs for specific error messages

### Foreign Key Constraints

SQLite foreign keys must be explicitly enabled:
```python
await conn.execute("PRAGMA foreign_keys = ON")
```

### Schema Changes

To apply schema changes:
1. Create new migration file in `/migration/sqlite/`
2. Increment version number
3. Restart application to apply migrations

## Contributing

To contribute to the SQLite backend:

1. Implement stub methods in `sqlite_repository.py`
2. Add tests for new functionality
3. Update this documentation
4. Ensure backward compatibility with existing code

## References

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [aiosqlite Library](https://github.com/omnilib/aiosqlite)
- [Repository Pattern Documentation](./REPOSITORY_PATTERN.md)
