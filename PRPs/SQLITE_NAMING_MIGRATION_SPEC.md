# SQLite Naming Migration Specification

**Status**: Draft
**Created**: 2025-10-14
**Author**: AI Assistant
**Priority**: High
**Effort**: Medium (3-5 days)

## Overview

This specification outlines the complete migration from Supabase-specific naming and references to database-agnostic naming throughout the Archon codebase. While the repository abstraction layer already supports SQLite, the codebase still contains numerous Supabase-specific function names, comments, and configuration references that need to be updated for consistency.

## Problem Statement

The current codebase has completed the technical migration to support SQLite through a repository pattern, but:

1. **Function names** like `add_documents_to_supabase()` mislead developers about the actual database backend
2. **Default configuration** still points to Supabase instead of SQLite
3. **Environment variables** in Docker Compose reference Supabase even when using SQLite
4. **Comments and documentation** reference Supabase-specific operations
5. **42+ files** contain Supabase references that should be database-agnostic

This creates confusion about the actual database backend in use and makes the codebase harder to maintain.

## Goals

1. **Rename all database functions** to use generic naming (e.g., `add_documents_to_database()`)
2. **Update repository factory** to default to SQLite instead of Supabase
3. **Clean up Docker Compose** to remove unused Supabase environment variables
4. **Update all comments and docstrings** to use database-agnostic language
5. **Maintain backward compatibility** where possible for existing deployments

## Non-Goals

- Removing the Supabase repository implementation entirely (keep for backward compatibility)
- Changing the database schema or data structure
- Modifying the repository abstraction interface
- Adding new database backends beyond SQLite

## Technical Design

### 1. Function Renaming Strategy

#### Core Storage Functions

**File**: `python/src/server/services/storage/document_storage_service.py`

Current:
```python
async def add_documents_to_supabase(
    client=None,  # Deprecated
    urls: list[str],
    chunk_numbers: list[int],
    contents: list[str],
    metadatas: list[dict[str, Any]],
    url_to_full_document: dict[str, str],
    batch_size: int = 15,
    progress_callback=None,
    enable_parallel_batches: bool = True,
    provider: str | None = None,
    cancellation_check=None,
    repository: DatabaseRepository | None = None,
) -> None:
```

New:
```python
async def add_documents_to_database(
    urls: list[str],
    chunk_numbers: list[int],
    contents: list[str],
    metadatas: list[dict[str, Any]],
    url_to_full_document: dict[str, str],
    batch_size: int = 15,
    progress_callback=None,
    enable_parallel_batches: bool = True,
    provider: str | None = None,
    cancellation_check=None,
    repository: DatabaseRepository | None = None,
) -> None:
```

**Changes**:
- Rename function from `add_documents_to_supabase` to `add_documents_to_database`
- Remove deprecated `client` parameter entirely
- Update all docstrings to reference "database" instead of "Supabase"
- Update the `@safe_span` decorator name

**File**: `python/src/server/services/storage/code_storage_service.py`

Current:
```python
async def add_code_examples_to_supabase(
    repository: DatabaseRepository,
    urls: list[str],
    chunk_numbers: list[int],
    code_examples: list[str],
    summaries: list[str],
    metadatas: list[dict[str, Any]],
    batch_size: int = 20,
    url_to_full_document: dict[str, str] | None = None,
    progress_callback=None,
    provider: str | None = None,
    embedding_provider: str | None = None,
) -> None:
```

New:
```python
async def add_code_examples_to_database(
    repository: DatabaseRepository,
    urls: list[str],
    chunk_numbers: list[int],
    code_examples: list[str],
    summaries: list[str],
    metadatas: list[dict[str, Any]],
    batch_size: int = 20,
    url_to_full_document: dict[str, str] | None = None,
    progress_callback=None,
    provider: str | None = None,
    embedding_provider: str | None = None,
) -> None:
```

#### Backward Compatibility Aliases

To maintain compatibility with existing code, create deprecated aliases:

```python
# Deprecated aliases for backward compatibility
async def add_documents_to_supabase(*args, **kwargs):
    """
    Deprecated: Use add_documents_to_database() instead.
    This function is maintained for backward compatibility only.
    """
    import warnings
    warnings.warn(
        "add_documents_to_supabase() is deprecated. Use add_documents_to_database() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return await add_documents_to_database(*args, **kwargs)

async def add_code_examples_to_supabase(*args, **kwargs):
    """
    Deprecated: Use add_code_examples_to_database() instead.
    This function is maintained for backward compatibility only.
    """
    import warnings
    warnings.warn(
        "add_code_examples_to_supabase() is deprecated. Use add_code_examples_to_database() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return await add_code_examples_to_database(*args, **kwargs)
```

### 2. Repository Factory Updates

**File**: `python/src/server/repositories/repository_factory.py`

#### Changes:

1. **Update default backend** from `"supabase"` to `"sqlite"`:

```python
@staticmethod
def _get_backend_type_from_env() -> BackendType:
    """
    Get the database backend type from environment variable.

    Returns:
        Backend type from ARCHON_DB_BACKEND or "sqlite" as default
    """
    backend = os.getenv("ARCHON_DB_BACKEND", "sqlite").lower()  # Changed default

    valid_backends = ("supabase", "fake", "sqlite")
    if backend not in valid_backends:
        logger.warning(
            f"Invalid ARCHON_DB_BACKEND value: '{backend}'. "
            f"Defaulting to 'sqlite'. Valid options: {', '.join(valid_backends)}"
        )
        return "sqlite"  # Changed default

    return backend
```

2. **Update documentation** to reflect SQLite as the primary backend:

```python
"""
Repository Factory

Provides centralized creation and management of database repositories for
different database backends (SQLite, Supabase, Fake for testing).

This factory supports:
    - "sqlite" (default): Lightweight file-based SQLite backend
    - "supabase" (legacy): Production PostgreSQL backend via Supabase
    - "fake" (testing): In-memory mock repository for testing

Usage:
    # Get repository with default backend (SQLite)
    repo = get_repository()

    # Get repository with specific backend
    repo = get_repository(backend="sqlite")

    # Use repository factory directly
    factory = RepositoryFactory()
    repo = factory.get_repository(backend="sqlite")
"""
```

3. **Update error messages** to reference SQLite:

```python
raise ValueError(
    f"Unsupported database backend: {backend}. "
    f"Supported backends: sqlite (default), supabase, fake"
)
```

### 3. Docker Compose Cleanup

**File**: `docker-compose.yml`

#### Changes:

1. **Remove Supabase variables from archon-migrations service** (keep for backward compat if ARCHON_DB_BACKEND=supabase):

```yaml
archon-migrations:
  build:
    context: .
    dockerfile: Dockerfile.migrations
  container_name: archon-migrations
  environment:
    - ARCHON_DB_BACKEND=${ARCHON_DB_BACKEND:-sqlite}
    - ARCHON_SQLITE_PATH=/data/archon.db
    # Supabase variables (only used if ARCHON_DB_BACKEND=supabase)
    - SUPABASE_URL=${SUPABASE_URL:-}
    - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY:-}
    - SUPABASE_DB_URL=${SUPABASE_DB_URL:-}
    - SUPABASE_DB_PASSWORD=${SUPABASE_DB_PASSWORD:-}
    - SUPABASE_DB_HOST=${SUPABASE_DB_HOST:-}
    - SUPABASE_DB_PORT=${SUPABASE_DB_PORT:-5432}
    - SUPABASE_DB_NAME=${SUPABASE_DB_NAME:-postgres}
    - SUPABASE_DB_USER=${SUPABASE_DB_USER:-postgres}
  volumes:
    - ./data:/data # SQLite database location
    - ./migration:/migration # Migration files
  networks:
    - app-network
```

2. **Update service comments** to clarify SQLite is primary:

```yaml
services:
  # Database Migration Service (Flyway)
  # Runs first to ensure database schema is up-to-date
  # Supports both SQLite (default) and Supabase backends
  archon-migrations:
```

3. **Simplify server environment** (keep Supabase vars with empty defaults):

```yaml
archon-server:
  environment:
    - ARCHON_DB_BACKEND=${ARCHON_DB_BACKEND:-sqlite}
    - ARCHON_SQLITE_PATH=/data/archon.db
    - ARCHON_SKIP_DB_INIT=true
    # Legacy Supabase support (only used if ARCHON_DB_BACKEND=supabase)
    - SUPABASE_URL=${SUPABASE_URL:-}
    - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY:-}
```

4. **Update MCP service**:

```yaml
archon-mcp:
  environment:
    - ARCHON_DB_BACKEND=${ARCHON_DB_BACKEND:-sqlite}
    - ARCHON_SQLITE_PATH=/data/archon.db
    # Legacy Supabase support (only used if ARCHON_DB_BACKEND=supabase)
    - SUPABASE_URL=${SUPABASE_URL:-}
    - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY:-}
```

### 4. Comment and Documentation Updates

#### Pattern Replacements

Apply these systematic replacements across all files:

| Old Pattern | New Pattern |
|------------|-------------|
| "Add documents to Supabase" | "Add documents to database" |
| "Store in Supabase" | "Store in database" |
| "Supabase client" | "Database repository" |
| "supabase_client" | "repository" |
| "Insert into Supabase" | "Insert into database" |
| "Handles storage of documents in Supabase" | "Handles storage of documents in the database" |

#### Files Requiring Comment Updates

Based on grep results, these files need comment/docstring updates:

**Storage Services**:
- `python/src/server/services/storage/document_storage_service.py`
- `python/src/server/services/storage/code_storage_service.py`
- `python/src/server/services/storage/base_storage_service.py`

**Crawling Services**:
- `python/src/server/services/crawling/code_extraction_service.py`
- `python/src/server/services/crawling/document_storage_operations.py`
- `python/src/server/services/crawling/page_storage_operations.py`

**Repository Files**:
- `python/src/server/repositories/sqlite_repository.py` (lines 26, 99)
- `python/src/server/repositories/repository_factory.py`
- `python/src/server/repositories/QUICK_START.md`
- `python/src/server/repositories/REPOSITORY_FACTORY.md`

**Service Layer**:
- All files in `python/src/server/services/`

**API Routes**:
- `python/src/server/api_routes/knowledge_api.py`
- `python/src/server/api_routes/projects_api.py`
- `python/src/server/api_routes/settings_api.py`

### 5. Import Statement Updates

Update all imports that reference the old function names:

**Pattern to find**:
```python
from ..storage.document_storage_service import add_documents_to_supabase
from ..storage.code_storage_service import add_code_examples_to_supabase
```

**Replace with**:
```python
from ..storage.document_storage_service import add_documents_to_database
from ..storage.code_storage_service import add_code_examples_to_database
```

**Files with imports to update** (use grep to find all):
```bash
grep -r "from.*add_documents_to_supabase" python/src/
grep -r "from.*add_code_examples_to_supabase" python/src/
```

## Implementation Plan

### Phase 1: Function Renaming (Day 1-2)

1. **Rename core storage functions**
   - Update `document_storage_service.py`
   - Update `code_storage_service.py`
   - Add backward compatibility aliases
   - Update function docstrings

2. **Update all function calls**
   - Find all usages with grep
   - Update imports throughout codebase
   - Update function calls
   - Test each module after changes

3. **Update tests**
   - Update test imports
   - Update test function calls
   - Ensure all tests pass

### Phase 2: Repository Factory Updates (Day 2)

1. **Update default backend**
   - Change `_get_backend_type_from_env()` default
   - Update factory docstrings
   - Update error messages

2. **Update factory documentation**
   - Update module docstring
   - Update REPOSITORY_FACTORY.md
   - Update QUICK_START.md

3. **Test backend switching**
   - Test SQLite default
   - Test Supabase fallback
   - Test fake backend for tests

### Phase 3: Docker Compose Cleanup (Day 3)

1. **Update environment variables**
   - Add comments for Supabase vars
   - Set empty defaults for Supabase vars
   - Update service comments

2. **Test Docker deployments**
   - Test with SQLite only (no Supabase vars)
   - Test with Supabase vars (backward compat)
   - Verify all services start correctly

### Phase 4: Comment and Documentation Updates (Day 4-5)

1. **Systematic comment replacement**
   - Run grep to find all Supabase references
   - Update docstrings in storage services
   - Update docstrings in crawling services
   - Update docstrings in repository files

2. **Update documentation files**
   - Update README.md references
   - Update CLAUDE.md instructions
   - Update architecture docs
   - Update migration guides

3. **Update code comments**
   - Replace inline comments
   - Update TODO comments
   - Update error messages

### Phase 5: Testing and Validation (Day 5)

1. **Run test suite**
   - Run all unit tests
   - Run integration tests
   - Run API tests
   - Verify no regressions

2. **Manual testing**
   - Test document upload
   - Test code extraction
   - Test crawling operations
   - Test project management

3. **Documentation review**
   - Review all updated docs
   - Ensure consistency
   - Fix any missed references

## Testing Strategy

### Unit Tests

1. **Test function aliases**:
```python
async def test_deprecated_add_documents_to_supabase_still_works():
    """Verify backward compatibility alias works."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        await add_documents_to_supabase(
            urls=["test"],
            chunk_numbers=[0],
            contents=["content"],
            metadatas=[{}],
            url_to_full_document={"test": "full"},
            repository=mock_repo,
        )
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "deprecated" in str(w[-1].message).lower()
```

2. **Test default backend**:
```python
def test_repository_factory_defaults_to_sqlite():
    """Verify repository factory uses SQLite by default."""
    factory = RepositoryFactory()
    # Clear env to ensure default is used
    with patch.dict(os.environ, {}, clear=True):
        repo = factory.get_repository()
        assert isinstance(repo, SQLiteDatabaseRepository)
```

### Integration Tests

1. **Test document storage with new function names**
2. **Test code extraction with new function names**
3. **Test crawling operations end-to-end**
4. **Test Docker Compose with SQLite only**
5. **Test Docker Compose with Supabase (backward compat)**

### Regression Tests

1. **Verify existing functionality unchanged**
2. **Test all API endpoints**
3. **Test MCP tools**
4. **Test frontend integration**

## Migration Guide

### For Developers

If you have custom code calling the old functions:

**Before**:
```python
from src.server.services.storage.document_storage_service import add_documents_to_supabase

await add_documents_to_supabase(
    client=supabase_client,  # Deprecated
    urls=urls,
    chunk_numbers=chunk_numbers,
    contents=contents,
    metadatas=metadatas,
    url_to_full_document=url_map,
)
```

**After**:
```python
from src.server.services.storage.document_storage_service import add_documents_to_database

await add_documents_to_database(
    urls=urls,
    chunk_numbers=chunk_numbers,
    contents=contents,
    metadatas=metadatas,
    url_to_full_document=url_map,
    repository=repository,  # Now required
)
```

### For Deployment

**Environment Variables**:
- Add `ARCHON_DB_BACKEND=sqlite` to explicitly use SQLite (now default)
- Keep Supabase variables only if using `ARCHON_DB_BACKEND=supabase`
- SQLite requires `ARCHON_SQLITE_PATH=/data/archon.db`

## Risks and Mitigations

### Risk 1: Breaking Changes for External Code

**Mitigation**:
- Provide backward compatibility aliases with deprecation warnings
- Document migration path clearly
- Keep aliases for at least 2 major versions

### Risk 2: Docker Compose Deployment Issues

**Mitigation**:
- Keep Supabase env vars with empty defaults
- Test both SQLite-only and Supabase deployments
- Provide clear documentation on environment setup

### Risk 3: Missed Supabase References

**Mitigation**:
- Use comprehensive grep searches
- Review all 42+ affected files systematically
- Run full test suite after changes
- Manual testing of all features

### Risk 4: Documentation Inconsistencies

**Mitigation**:
- Update all docs in same PR
- Review docs for consistency
- Cross-reference between files

## Success Metrics

1. **Zero test failures** after migration
2. **All 42+ files updated** with database-agnostic naming
3. **Docker Compose works** with SQLite-only configuration
4. **Backward compatibility maintained** via deprecation aliases
5. **Documentation complete** and consistent

## Future Considerations

### Deprecation Timeline

- **Version 1.0** (this migration): Add aliases with deprecation warnings
- **Version 2.0** (6 months): Mark old functions as removed in docs
- **Version 3.0** (12 months): Remove backward compatibility aliases entirely

### Additional Database Backends

The naming changes make it easier to add new backends:
- PostgreSQL (direct, not via Supabase)
- MySQL
- MongoDB
- Cloud-hosted SQLite (Turso, etc.)

All backends would use the same generic function names like `add_documents_to_database()`.

## Appendix

### Complete File List

Files requiring updates (42+ total):

```
python/src/server/services/storage/storage_services.py
python/src/server/services/storage/document_storage_service.py
python/src/server/services/storage/code_storage_service.py
python/src/server/services/storage/base_storage_service.py
python/src/server/services/crawling/code_extraction_service.py
python/src/server/services/crawling/document_storage_operations.py
python/src/server/services/crawling/page_storage_operations.py
python/src/server/services/crawling/crawling_service.py
python/src/server/services/projects/*.py (all files)
python/src/server/services/search/*.py (all files)
python/src/server/services/knowledge/database_metrics_service.py
python/src/server/services/migration_service.py
python/src/server/services/source_management_service.py
python/src/server/services/credential_service.py
python/src/server/services/prompt_service.py
python/src/server/repositories/sqlite_repository.py
python/src/server/repositories/repository_factory.py
python/src/server/repositories/__init__.py
python/src/server/api_routes/knowledge_api.py
python/src/server/api_routes/projects_api.py
python/src/server/api_routes/settings_api.py
python/src/server/config/config.py
python/src/server/main.py
python/src/mcp_server/mcp_server.py
python/src/agents/document_agent.py
docker-compose.yml
```

### Grep Commands for Finding References

```bash
# Find all Supabase references
grep -r "supabase" python/src/ -i

# Find function calls
grep -r "add_documents_to_supabase" python/src/
grep -r "add_code_examples_to_supabase" python/src/

# Find imports
grep -r "from.*supabase" python/src/
grep -r "import.*supabase" python/src/

# Find comments
grep -r "# .*[Ss]upabase" python/src/
grep -r '""".*[Ss]upabase' python/src/
```

### References

- Repository Pattern Documentation: `python/src/server/repositories/REPOSITORY_PATTERN.md`
- Repository Factory Guide: `python/src/server/repositories/REPOSITORY_FACTORY.md`
- Quick Start: `python/src/server/repositories/QUICK_START.md`
- Database Migration: `docs/DATABASE_REPOSITORY_REFACTORING.md`
