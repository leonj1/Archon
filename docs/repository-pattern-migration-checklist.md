# Repository Pattern Migration Checklist

This document tracks all components that need to be updated to fully implement the database repository pattern across the Archon codebase.

## 📚 Documentation

**New to the repository pattern? Start here:**

1. **[Repository Pattern Overview](python/REPOSITORY_PATTERN.md)** - Understand the pattern, benefits, and architecture
2. **[Migration Guide](python/MIGRATION_GUIDE.md)** - Step-by-step instructions for migrating services and routes
3. **[API Patterns](python/API_PATTERNS.md)** - Standard patterns for API routes with repository
4. **[Complete Examples](python/EXAMPLES.md)** - Working examples of services, routes, and tests

## Overview
- **Total Services to Refactor**: 20
- **Total API Route Updates**: 29
- **Direct Database Calls to Abstract**: 8

---

## ✅ How to Use This Pattern

### For Services

1. Add repository parameter to `__init__` with backward compatibility
2. Convert all methods to `async`
3. Replace Supabase calls with repository methods
4. Return `(success: bool, result: dict)` tuples
5. See [Migration Guide](python/MIGRATION_GUIDE.md) for details

### For API Routes

1. Get repository: `repository = get_repository()`
2. Create service: `service = YourService(repository=repository)`
3. Await service calls: `success, result = await service.method()`
4. Handle errors with HTTPException
5. See [API Patterns](python/API_PATTERNS.md) for details

### For Tests

1. Use `FakeDatabaseRepository()` instead of mocking Supabase
2. Add `@pytest.mark.asyncio` to test methods
3. Make test methods `async`
4. Test both success and failure cases
5. See [Examples](python/EXAMPLES.md) for complete test examples

---

## Phase 1: Refactor Service Classes (20 services)

### Storage Services (4)
1. - [ ] **BaseStorageService** (`services/storage/base_storage_service.py`)
2. - [ ] **DocumentStorageService** (`services/storage/storage_services.py`)
3. - [ ] **PageStorageOperations** (Find location)
4. - [ ] **DocumentStorageOperations** (`services/crawling/document_storage_operations.py`)

### Project Management Services (6)
5. - [x] **TaskService** (`services/projects/task_service.py`) ✅ Refactored to use DatabaseRepository
6. - [ ] **VersioningService** (`services/projects/versioning_service.py`)
7. - [ ] **ProjectCreationService** (`services/projects/project_creation_service.py`)
8. - [ ] **DocumentService** (`services/projects/document_service.py`)
9. - [ ] **SourceLinkingService** (`services/projects/source_linking_service.py`)
10. - [ ] **HybridSearchStrategy** (`services/search/hybrid_search_strategy.py`)

### Crawling Services (2)
11. - [ ] **CrawlingService** (`services/crawling/crawling_service.py`)
12. - [ ] **CodeExtractionService** (`services/crawling/code_extraction_service.py`)

### Knowledge Base Services (3)
13. - [x] **KnowledgeItemService** (`services/knowledge/knowledge_item_service.py`) ⚠️ Partially refactored
14. - [ ] **KnowledgeSummaryService** (`services/knowledge/knowledge_summary_service.py`)
15. - [ ] **DatabaseMetricsService** (`services/knowledge/database_metrics_service.py`)

### Core System Services (4)
16. - [ ] **MigrationService** (`services/migration_service.py`)
17. - [ ] **CredentialService** (`services/credential_service.py`)
18. - [ ] **PromptService** (`services/prompt_service.py`)
19. - [ ] **SourceManagementService** (`services/source_management_service.py`)

### Ollama Integration Services (1)
20. - [ ] **ModelDiscoveryService** (`services/ollama/model_discovery_service.py`)

---

## Phase 2: Update API Routes to Use Repository Pattern (29 instances)

### knowledge_api.py (14 updates)
21. - [ ] Line 245: `KnowledgeItemService(get_supabase_client())` → Use repository
22. - [ ] Line 276: `KnowledgeSummaryService(get_supabase_client())` → Use repository
23. - [ ] Line 294: `KnowledgeItemService(get_supabase_client())` → Use repository
24. - [ ] Line 325: `SourceManagementService(get_supabase_client())` → Use repository
25. - [ ] Line 393: Direct Supabase call → Abstract to repository
26. - [ ] Line 549: Direct Supabase call → Abstract to repository
27. - [ ] Line 627: `KnowledgeItemService(get_supabase_client())` → Use repository
28. - [ ] Line 678: `CrawlingService(crawler, get_supabase_client())` → Use repository
29. - [ ] Line 832: `CrawlingService(crawler, supabase_client)` → Use repository
30. - [ ] Line 1031: `DocumentStorageService(get_supabase_client())` → Use repository
31. - [ ] Line 1121: `RAGService(get_supabase_client())` → Use repository *(Service already supports it!)*
32. - [ ] Line 1151: `RAGService(get_supabase_client())` → Use repository *(Service already supports it!)*
33. - [ ] Line 1194: `KnowledgeItemService(get_supabase_client())` → Use repository
34. - [ ] Line 1216: `SourceManagementService(get_supabase_client())` → Use repository
35. - [ ] Line 1247: `DatabaseMetricsService(get_supabase_client())` → Use repository

### projects_api.py (7 updates)
36. - [ ] Line 223: `ProjectService(supabase_client)` → Use repository *(Service already supports it!)*
37. - [ ] Line 237: `TaskService(supabase_client)` → Use repository
38. - [ ] Line 298: `TaskService(supabase_client)` → Use repository
39. - [ ] Line 406: `VersioningService(supabase_client)` → Use repository
40. - [ ] Line 409: `ProjectService(supabase_client)` → Use repository *(Service already supports it!)*
41. - [ ] Line 443: `ProjectService(supabase_client)` → Use repository *(Service already supports it!)*
42. - [ ] Line 457: `SourceLinkingService(supabase_client)` → Use repository

### pages_api.py (3 updates)
43. - [ ] Line 108: Direct `get_supabase_client()` → Abstract to repository
44. - [ ] Line 150: Direct `get_supabase_client()` → Abstract to repository
45. - [ ] Line 182: Direct `get_supabase_client()` → Abstract to repository

### settings_api.py (1 update)
46. - [ ] Line 286: Direct `get_supabase_client()` → Abstract to repository

### ollama_api.py (3 updates)
47. - [ ] Line 426: Direct `get_supabase_client()` → Abstract to repository
48. - [ ] Line 511: Direct `get_supabase_client()` → Abstract to repository
49. - [ ] Line 972: Direct `get_supabase_client()` → Abstract to repository

### main.py (1 update)
50. - [ ] Lines 279-284: Health check using direct Supabase → Use repository

---

## Phase 3: Create Repository Singleton/Factory

51. - [ ] Create a repository factory or singleton pattern to manage repository instances
52. - [ ] Update application initialization to use repository pattern
53. - [ ] Create configuration to select repository implementation (Supabase/Fake/Future SQLite)

---

## Phase 4: Testing Updates

54. - [ ] Update all service tests to use `FakeDatabaseRepository`
55. - [ ] Remove direct Supabase mocking from tests
56. - [ ] Create integration tests using `SupabaseDatabaseRepository`
57. - [ ] Ensure all test fixtures use repository pattern

---

## Phase 5: Documentation

58. - [ ] Document repository pattern usage in README
59. - [ ] Create migration guide for developers
60. - [ ] Update API documentation to reflect repository pattern
61. - [ ] Add examples of proper repository usage

---

## Completed Items ✅

### Services Already Refactored
- [x] **RAGService** - Supports `DatabaseRepository` via constructor injection
- [x] **BaseSearchStrategy** - Supports `DatabaseRepository` via constructor injection
- [x] **ProjectService** - Supports `DatabaseRepository` via constructor injection

### Repository Implementations
- [x] **DatabaseRepository** - Abstract interface with 56 methods
- [x] **SupabaseDatabaseRepository** - Production implementation (1,333 lines)
- [x] **FakeDatabaseRepository** - Test implementation (824 lines)

---

## Implementation Strategy

### For Service Refactoring:
1. Add `database_repository: Optional[DatabaseRepository]` parameter to `__init__`
2. Use repository if provided, otherwise create `SupabaseDatabaseRepository` with default client
3. Replace all `self.supabase_client` calls with appropriate repository methods
4. Update tests to use `FakeDatabaseRepository`

### For API Route Updates:
1. Create repository instance at the route level or use singleton
2. Pass repository to service constructors
3. Remove direct `get_supabase_client()` calls
4. Handle repository errors appropriately

### Example Pattern:
```python
# Service refactoring
class SomeService:
    def __init__(self, repository: Optional[DatabaseRepository] = None):
        if repository is None:
            repository = SupabaseDatabaseRepository(get_supabase_client())
        self.repository = repository

# API route update
repository = SupabaseDatabaseRepository(get_supabase_client())
service = SomeService(repository=repository)
```

---

## Priority Order

### High Priority (Core functionality)
1. TaskService (used heavily in projects)
2. KnowledgeItemService (core knowledge base)
3. DocumentStorageService (document uploads)
4. CrawlingService (web crawling)

### Medium Priority (Supporting features)
5. SourceManagementService
6. VersioningService
7. SourceLinkingService
8. DatabaseMetricsService

### Low Priority (System/Config)
9. MigrationService
10. CredentialService
11. PromptService
12. ModelDiscoveryService

---

## Notes

- Services marked with *(Service already supports it!)* only need API route updates
- Direct database calls in API routes should be moved to service methods
- Consider creating a `SQLiteDatabaseRepository` for local development without Supabase
- The repository pattern will enable easier testing and future database migrations

## Success Criteria

- [ ] All services use `DatabaseRepository` interface
- [ ] No direct `get_supabase_client()` calls in API routes (except in repository creation)
- [ ] All tests use `FakeDatabaseRepository` instead of mocking Supabase
- [ ] Application can switch between repository implementations via configuration
- [ ] Health checks and migrations work through repository pattern
- [ ] All documentation is complete and accurate

---

## Verification Steps

After completing a migration, verify with these checks:

### 1. Code Quality Checks

```bash
# Run linter
cd python
uv run ruff check src/server/services/your_service.py

# Run type checker
uv run mypy src/server/services/your_service.py

# Check for remaining direct Supabase calls
grep -r "\.table(" src/server/services/your_service.py
grep -r "supabase_client" src/server/services/your_service.py
```

### 2. Test Verification

```bash
# Run service tests
uv run pytest tests/services/test_your_service.py -v

# Run API route tests
uv run pytest tests/api_routes/test_your_api.py -v

# Check test coverage
uv run pytest tests/services/test_your_service.py --cov=src/server/services/your_service
```

### 3. Runtime Verification

```bash
# Start services
docker compose up -d

# Test API endpoint
curl http://localhost:8181/api/your-endpoint

# Check logs for errors
docker compose logs archon-server | grep ERROR

# Test health check
curl http://localhost:8181/api/health
```

### 4. Review Checklist

For each migrated service/route:

- [ ] All methods are async
- [ ] All repository calls use await
- [ ] Constructor has backward compatibility
- [ ] Error handling returns proper tuples
- [ ] Tests use FakeDatabaseRepository
- [ ] Tests are marked with @pytest.mark.asyncio
- [ ] No hardcoded Supabase client references
- [ ] Documentation is updated
- [ ] Code follows patterns in EXAMPLES.md

---

## Quick Reference

### Repository Methods by Domain

**See [Repository Pattern Overview](python/REPOSITORY_PATTERN.md#databaserepository-interface) for complete list.**

Common patterns:
- `get_[entity]_by_id(id)` - Get single entity
- `list_[entities]()` - List all entities
- `create_[entity](data)` - Create new entity
- `update_[entity](id, data)` - Update entity
- `delete_[entity](id)` - Delete entity
- `archive_[entity](id)` - Soft delete entity

### Common Migrations

**Supabase → Repository:**

```python
# Before
response = self.supabase_client.table("tasks").select("*").eq("id", task_id).execute()
task = response.data[0] if response.data else None

# After
task = await self.repository.get_task_by_id(task_id)
```

**See [Migration Guide](python/MIGRATION_GUIDE.md) for comprehensive examples.**

---

## Getting Help

If you encounter issues during migration:

1. **Check Documentation**: Review the four main docs (REPOSITORY_PATTERN.md, MIGRATION_GUIDE.md, API_PATTERNS.md, EXAMPLES.md)
2. **Review Examples**: Look at completed migrations (TaskService, ProjectService)
3. **Check Troubleshooting**: See troubleshooting section in REPOSITORY_PATTERN.md
4. **Ask Team**: Reach out to developers who have completed migrations
5. **Create Issue**: Document the problem and solution for future reference

---

## Progress Tracking

**Last Updated**: 2025-10-12

### Completed (5 items)
- ✅ DatabaseRepository interface (58 methods)
- ✅ SupabaseDatabaseRepository implementation (1,333 lines)
- ✅ FakeDatabaseRepository implementation (824 lines)
- ✅ TaskService migration
- ⚠️ KnowledgeItemService (partially complete)

### In Progress (0 items)

### Remaining (54 items)
- 15 services need full migration
- 29 API routes need updates
- Multiple test files need conversion

### Estimated Completion
At current pace (~30 min/service, ~5 min/route):
- Services: ~7.5 hours
- Routes: ~2.5 hours
- Tests: ~5 hours
- **Total: ~15 hours**
