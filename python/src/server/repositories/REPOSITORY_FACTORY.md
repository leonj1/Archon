# Repository Factory Pattern

## Overview

The repository factory provides centralized management of repository instances across the Archon application. It supports multiple database backends and simplifies dependency injection for testing.

## Key Benefits

1. **Single Source of Truth**: One place to configure which database backend to use
2. **Easy Testing**: Switch to fake repository for unit tests without changing service code
3. **Future-Proof**: Add new backends (SQLite, PostgreSQL direct) without changing existing code
4. **Consistent Initialization**: All services use repositories the same way

## Quick Start

### Basic Usage in Services

```python
from repositories import get_repository

class MyService:
    def __init__(self, repository: DatabaseRepository = None):
        # Use injected repository or get default from factory
        self.repository = repository or get_repository()

    async def do_something(self):
        # Use repository methods
        projects = await self.repository.list_projects()
        return projects
```

### Usage in API Routes

```python
from repositories import get_repository

@router.get("/api/projects")
async def list_projects():
    # Get repository from factory
    repository = get_repository()

    # Use with services
    service = ProjectService(repository=repository)
    success, result = service.list_projects()

    return result
```

### Testing with Fake Repository

```python
from repositories import get_repository, reset_factory

def test_my_service():
    # Reset factory state for clean test
    reset_factory()

    # Use fake repository for testing
    repo = get_repository(backend="fake")
    service = MyService(repository=repo)

    # Test your service
    result = await service.do_something()
    assert result is not None
```

## Configuration

### Environment Variable

Set `ARCHON_DB_BACKEND` to choose the database backend:

```bash
# Production (default)
ARCHON_DB_BACKEND=supabase

# Testing
ARCHON_DB_BACKEND=fake

# Future backends
ARCHON_DB_BACKEND=sqlite  # Not yet implemented
```

If not set, defaults to `supabase`.

### Programmatic Configuration

```python
from repositories import get_repository

# Get default backend (from env or supabase)
repo = get_repository()

# Force specific backend
repo = get_repository(backend="supabase")
repo = get_repository(backend="fake")
```

## Available Backends

### Supabase (Production)

Default backend using Supabase PostgreSQL with pgvector.

**Requirements**:
- `SUPABASE_URL` environment variable
- `SUPABASE_SERVICE_KEY` environment variable

**Usage**:
```python
repo = get_repository(backend="supabase")
# or just
repo = get_repository()  # defaults to supabase
```

### Fake (Testing)

In-memory repository for unit testing. No database connection required.

**Usage**:
```python
repo = get_repository(backend="fake")
```

**Note**: Data is lost when the process exits. Perfect for tests!

### SQLite (Future)

Planned for local development and embedded deployments.

**Status**: Not yet implemented

## Architecture

### Components

1. **`RepositoryFactory`**: Singleton class managing repository instances
2. **`get_repository()`**: Main function to obtain repository instances
3. **`reset_factory()`**: Utility to reset factory state (useful for testing)

### Singleton Pattern

The factory uses a singleton pattern to ensure:
- Only one repository instance per backend
- Efficient resource usage (database connections)
- Consistent state across the application

```python
# These all return the same instance
repo1 = get_repository()
repo2 = get_repository()
assert repo1 is repo2  # True
```

## Migration Guide

### Before (Direct Instantiation)

```python
from repositories.supabase_repository import SupabaseDatabaseRepository
from utils import get_supabase_client

# Every route/service creates its own instance
repository = SupabaseDatabaseRepository(get_supabase_client())
service = MyService(repository=repository)
```

### After (Factory Pattern)

```python
from repositories import get_repository

# Use factory to get configured instance
repository = get_repository()
service = MyService(repository=repository)
```

### Service Layer Pattern (Recommended)

Services should accept repository as optional parameter:

```python
class MyService:
    def __init__(self, repository: DatabaseRepository = None):
        # Accept injection or use factory
        self.repository = repository or get_repository()
```

This pattern:
- Allows dependency injection for testing
- Falls back to factory for production use
- Keeps services decoupled from database implementation

## Examples

### Example 1: API Route

```python
# File: api_routes/projects_api.py
from repositories import get_repository
from services.projects import ProjectService

@router.get("/api/projects")
async def list_projects():
    """List all projects using repository factory."""
    repository = get_repository()
    service = ProjectService(repository=repository)
    success, result = service.list_projects()

    if not success:
        raise HTTPException(status_code=500, detail=result)

    return result
```

### Example 2: Service Class

```python
# File: services/my_service.py
from repositories import DatabaseRepository, get_repository

class MyService:
    """Service demonstrating repository factory usage."""

    def __init__(self, repository: DatabaseRepository = None):
        self.repository = repository or get_repository()

    async def get_projects(self) -> list[dict]:
        """Get all projects using repository."""
        return await self.repository.list_projects()
```

### Example 3: Unit Test

```python
# File: tests/test_my_service.py
import pytest
from repositories import get_repository, reset_factory
from services import MyService

@pytest.fixture
def fake_repo():
    """Fixture providing fake repository."""
    reset_factory()
    return get_repository(backend="fake")

async def test_my_service(fake_repo):
    """Test service with fake repository."""
    service = MyService(repository=fake_repo)

    # Test with in-memory data
    projects = await service.get_projects()
    assert isinstance(projects, list)
```

### Example 4: Integration Test

```python
# File: tests/integration/test_projects_api.py
from repositories import get_repository, reset_factory

async def test_projects_api():
    """Test API with real database."""
    # Use default (supabase) backend
    repository = get_repository()

    # Test against real database
    projects = await repository.list_projects()
    assert projects is not None
```

## Best Practices

### DO ✅

1. **Use `get_repository()` in API routes**: Simple and consistent
2. **Accept repository parameter in services**: Enables dependency injection
3. **Reset factory in tests**: Ensures clean state between tests
4. **Use type hints**: `repository: DatabaseRepository`

### DON'T ❌

1. **Don't create multiple factory instances**: Use the global `get_repository()`
2. **Don't bypass the factory**: Let it manage instances
3. **Don't hardcode backends**: Use environment variables
4. **Don't forget to reset in tests**: Can cause test pollution

## Error Handling

### Common Errors

#### 1. Missing Environment Variables

```
RuntimeError: Failed to initialize Supabase repository: Missing SUPABASE_URL
```

**Solution**: Set required environment variables in `.env`:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
```

#### 2. Invalid Backend

```
ValueError: Unknown backend: invalid. Supported backends: supabase, fake, sqlite
```

**Solution**: Use a valid backend name or check `ARCHON_DB_BACKEND` environment variable.

#### 3. SQLite Not Implemented

```
NotImplementedError: SQLite backend is not yet implemented
```

**Solution**: Use `supabase` or `fake` backend. SQLite support is coming in a future release.

## Logging

The factory logs important events:

```
INFO: Initializing repository with backend: supabase
INFO: Repository initialized successfully with backend: supabase
DEBUG: Repository factory reset
WARNING: Invalid ARCHON_DB_BACKEND value: invalid. Defaulting to 'supabase'
```

Monitor logs to verify correct backend initialization.

## Future Enhancements

### Planned Features

1. **SQLite Backend**: Local development and embedded deployments
2. **Connection Pooling**: Efficient database connection management
3. **Multiple Databases**: Support for different databases per tenant
4. **Health Checks**: Built-in repository health monitoring

### Contributing

To add a new backend:

1. Implement `DatabaseRepository` interface
2. Add backend type to `BackendType` literal
3. Add creation method in `RepositoryFactory`
4. Update documentation

Example:
```python
@staticmethod
def _create_sqlite_repository() -> SQLiteDatabaseRepository:
    """Create a SQLite repository instance."""
    return SQLiteDatabaseRepository(db_path="archon.db")
```

## Related Documentation

- **Repository Interface**: `database_repository.py` - Full interface definition
- **Supabase Implementation**: `supabase_repository.py` - Production backend
- **Fake Implementation**: `fake_repository.py` - Testing backend
- **Service Pattern**: See service files in `services/` directory

## Support

For questions or issues:
1. Check logs for initialization errors
2. Verify environment variables are set
3. Review examples in this document
4. Check service implementations for patterns
