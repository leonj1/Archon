# Repository Factory - Quick Start

## TL;DR

```python
# Get repository (uses configured backend)
from repositories import get_repository
repo = get_repository()

# Use with services
service = MyService(repository=repo)
```

## Common Patterns

### Pattern 1: API Route

```python
from repositories import get_repository
from services.projects import ProjectService

@router.get("/api/projects")
async def list_projects():
    repo = get_repository()
    service = ProjectService(repository=repo)
    success, result = service.list_projects()
    return result
```

### Pattern 2: Service Class

```python
from repositories import DatabaseRepository, get_repository

class MyService:
    def __init__(self, repository: DatabaseRepository = None):
        self.repository = repository or get_repository()
```

### Pattern 3: Testing

```python
from repositories import get_repository, reset_factory

def test_something():
    reset_factory()
    repo = get_repository(backend="fake")
    service = MyService(repository=repo)
    # Test with in-memory data
```

## Configuration

```bash
# .env file
ARCHON_DB_BACKEND=supabase  # production (default)
# or
ARCHON_DB_BACKEND=fake      # testing
```

## Available Backends

- `supabase` - Production database (default)
- `fake` - In-memory for testing
- `sqlite` - Coming soon

## Full Documentation

See `REPOSITORY_FACTORY.md` for complete guide.
