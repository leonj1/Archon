# Services with Direct Supabase References

This document lists all services and API routes that still contain direct Supabase references and need to be updated to use the DatabaseRepository interface.

## Summary

- **Total Services with Direct References**: 8 services
- **Total API Routes with Direct References**: 1 route file
- **Total Direct Database Calls to Fix**: ~30 instances

---

## Services Requiring Updates

### 1. CredentialService (`services/credential_service.py`)

**Status**: ⚠️ Has repository but uses `self.repository.supabase_client` directly

**Direct Supabase Calls**:
- Line 117: `self.repository.supabase_client.table("archon_settings").select("*")`
- Line 219: `self.repository.supabase_client.table("archon_settings").upsert()`
- Line 268: `self.repository.supabase_client.table("archon_settings").delete()`
- Line 334: `self.repository.supabase_client.table("archon_settings").select("*").eq("category", category)`
- Line 368: `self.repository.supabase_client.table("archon_settings").select("*")`

**Fix Required**: 
- These operations should use repository methods for settings: `get_all_settings()`, `upsert_setting()`, `delete_setting()`, etc.

---

### 2. MigrationService (`services/migration_service.py`)

**Status**: ⚠️ Has repository but accesses `self.repository.supabase_client` for migration-specific table

**Direct Supabase Calls**:
- Line 99: `self.repository.supabase_client.table("archon_migrations").select("id")`
- Line 119: `self.repository.supabase_client.table("archon_migrations").select("*").order("applied_at", desc=True)`

**Fix Required**: 
- Add migration methods to DatabaseRepository interface
- Or create a separate MigrationRepository interface
- Note: This is a special case as migrations table isn't in the standard repository

---

### 3. DocumentStorageService (`services/storage/document_storage_service.py`)

**Status**: ❌ Still using direct Supabase client

**Direct Supabase Calls**:
- Line 104: `client.table("archon_crawled_pages").delete().in_("url", batch_urls)`
- Line 134: `client.table("archon_crawled_pages").delete().in_("url", batch_urls)`
- Line 442: `client.table("archon_crawled_pages").insert(batch_data)`
- Line 500: `client.table("archon_crawled_pages").insert(record)`

**Fix Required**:
- Convert to use repository methods: `delete_crawled_pages_by_source()`, `insert_crawled_page()`, `upsert_crawled_page()`
- May need to add batch operations to repository interface

---

### 4. CodeStorageService (`services/storage/code_storage_service.py`)

**Status**: ❌ Still using direct Supabase client

**Direct Supabase Calls**:
- Line 1167: `client.table("archon_code_examples").delete().eq("url", url)`
- Line 1348: `client.table("archon_code_examples").insert(batch_data)`
- Line 1367: `client.table("archon_code_examples").insert(record)`

**Fix Required**:
- Convert to use repository methods: `insert_code_example()`, `insert_code_examples_batch()`, `delete_code_examples_by_source()`
- May need to add delete by URL method to repository

---

### 5. KnowledgeItemService (`services/knowledge/knowledge_item_service.py`)

**Status**: ⚠️ Partially migrated, still has direct calls via `self.supabase`

**Direct Supabase Calls**:
- Line 73: `self.supabase.from_("archon_sources").select()`
- Line 112: `self.supabase.from_("archon_crawled_pages").select()`
- Line 127: `self.supabase.from_("archon_code_examples").select()`
- Line 228: `self.supabase.from_("archon_sources").select()`
- Line 287: `self.supabase.table("archon_sources").select("metadata")`
- Line 301: `self.supabase.table("archon_sources").update()`
- Line 333: `self.supabase.from_("archon_sources").select("*")`
- Line 417: `self.supabase.from_("archon_crawled_pages").select("url")`
- Line 436: `self.supabase.from_("archon_code_examples").select()`
- Line 478: `self.supabase.table("archon_crawled_pages").select("*", count="exact")`

**Fix Required**:
- Remove `self.supabase` property entirely
- Use `self.repository` methods exclusively
- Convert all queries to use repository methods

---

### 6. KnowledgeSummaryService (`services/knowledge/knowledge_summary_service.py`)

**Status**: ❌ Still using direct Supabase client parameter

**Direct Supabase Calls**:
- Line 69: `supabase_client.from_("archon_sources").select()`
- Line 84: `supabase_client.from_("archon_sources").select()`
- Line 245: `supabase_client.from_("archon_crawled_pages").select()`

**Fix Required**:
- Add repository parameter to methods or class
- Convert to use repository methods: `list_sources()`, `list_pages_by_source()`

---

### 7. SourceManagementService (`services/source_management_service.py`)

**Status**: ❌ Still has direct client usage

**Direct Supabase Calls**:
- Line 247: `client.table("archon_sources").select("title")`
- Line 293: `client.table("archon_sources").upsert(upsert_data)`
- Line 356: `client.table("archon_sources").upsert(upsert_data)`

**Fix Required**:
- Convert to use repository methods: `get_source_by_id()`, `upsert_source()`

---

### 8. BaseStorageService (`services/storage/base_storage_service.py`)

**Status**: ✅ Has repository but may need verification

**Note**: This is an abstract base class. Need to verify all concrete implementations properly use repository.

---

## API Routes Requiring Updates

### knowledge_api.py (`api_routes/knowledge_api.py`)

**Direct Supabase Calls**:
- Line 401: `supabase.from_("archon_crawled_pages").select()`
- Line 413: `supabase.from_("archon_crawled_pages").select()`
- Line 558: `supabase.from_("archon_code_examples")`
- Line 567: `supabase.from_("archon_code_examples")`

**Fix Required**:
- Move these operations to appropriate service methods
- Services should handle all database operations
- API routes should only orchestrate service calls

---

## Migration Priority

### High Priority (Core Functionality)
1. **KnowledgeItemService** - Core knowledge base operations
2. **DocumentStorageService** - Critical for document uploads
3. **knowledge_api.py** - API routes should not have direct DB calls

### Medium Priority (Supporting Services)
4. **SourceManagementService** - Source management
5. **KnowledgeSummaryService** - Summary operations
6. **CodeStorageService** - Code example storage

### Low Priority (System Services)
7. **CredentialService** - Settings management
8. **MigrationService** - Special case, may need custom handling

---

## Verification Steps

After fixing each service, verify with:

```bash
# Check for any remaining direct Supabase calls
grep -r "\.table(" src/server/services/[service_name].py
grep -r "\.from_(" src/server/services/[service_name].py
grep -r "supabase_client\." src/server/services/[service_name].py
grep -r "\.rpc(" src/server/services/[service_name].py

# Run tests for the service
uv run pytest tests/services/test_[service_name].py -v
```

---

## Common Patterns to Fix

### Pattern 1: Direct Table Access
```python
# ❌ Before
result = self.supabase_client.table("archon_sources").select("*").execute()

# ✅ After
sources = await self.repository.list_sources()
```

### Pattern 2: Direct Insert/Update
```python
# ❌ Before
client.table("archon_sources").upsert(data).execute()

# ✅ After
source = await self.repository.upsert_source(data)
```

### Pattern 3: Complex Queries
```python
# ❌ Before
query = supabase.from_("archon_sources").select("*").eq("id", id).execute()

# ✅ After
source = await self.repository.get_source_by_id(id)
```

### Pattern 4: Batch Operations
```python
# ❌ Before
client.table("archon_code_examples").insert(batch_data).execute()

# ✅ After
examples = await self.repository.insert_code_examples_batch(batch_data)
```

---

## Notes

1. **Repository Access Pattern**: Some services have `self.repository.supabase_client` which defeats the purpose of abstraction. This should be removed entirely.

2. **Missing Repository Methods**: Some operations may require new methods to be added to the DatabaseRepository interface (e.g., batch deletes by URL, migration-specific operations).

3. **Async Conversion**: All repository methods are async, so service methods using them must also be async.

4. **Error Handling**: Repository methods should handle database errors and return appropriate responses.

5. **Testing**: After migration, all tests should use `FakeDatabaseRepository` instead of mocking Supabase.

---

## Success Criteria

- [ ] No direct `.table()`, `.from_()`, or `.rpc()` calls in services
- [ ] No references to `supabase_client` except in repository creation
- [ ] No `self.repository.supabase_client` usage
- [ ] All database operations go through repository methods
- [ ] All tests use `FakeDatabaseRepository`
- [ ] API routes contain no direct database calls

---

## Estimated Effort

Based on the scope:
- **Simple services** (1-3 calls): ~30 minutes each
- **Complex services** (5+ calls): ~1 hour each
- **API route fixes**: ~20 minutes

**Total estimated time**: 5-7 hours for complete migration
