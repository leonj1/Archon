# Database Abstraction Layer Migration - Remaining Services Specification

## Executive Summary

This specification details the migration plan for the remaining 14 services in Archon's codebase, building upon the successful migration patterns established with `credential_service.py`, `prompt_service.py`, and `source_management_service.py`. The document provides concrete migration patterns, code templates, and specific instructions for each service category.

## Current Migration Status

### ✅ Completed (4/18 services)
- `client_manager.py` - Foundation established
- `credential_service.py` - Settings/credentials with encryption
- `prompt_service.py` - Read-only with caching
- `source_management_service.py` - Complex multi-table with transactions

### 🔄 Remaining (14/18 services)
Organized by complexity and dependencies for optimal migration order.

## Established Migration Patterns

### Pattern 1: Simple Read-Only Service
```python
# Before (Supabase)
from ..utils import get_supabase_client

def get_data():
    client = get_supabase_client()
    response = client.table("archon_table").select("*").execute()
    return response.data

# After (DAL)
from .client_manager import get_connection_manager

async def get_data():
    manager = get_connection_manager()
    async with manager.get_reader() as db:
        result = await db.select("table")
        if not result.success:
            raise RuntimeError(f"Failed to fetch data: {result.error}")
        return result.data
```

### Pattern 2: CRUD Service with Transactions
```python
# After (DAL)
async def complex_operation(data):
    manager = get_connection_manager()
    async with manager.get_primary() as db:
        async with db.transaction() as tx:
            # Multiple operations in transaction
            result1 = await tx.insert("table1", data1)
            if not result1.success:
                raise RuntimeError(f"Insert failed: {result1.error}")
            
            result2 = await tx.update("table2", data2, {"id": id})
            if not result2.success:
                raise RuntimeError(f"Update failed: {result2.error}")
            
            return result1.data
```

### Pattern 3: Service with JSON Operations
```python
# Handle JSON fields
async def update_json_field(id: str, json_data: dict):
    manager = get_connection_manager()
    async with manager.get_primary() as db:
        # JSON is automatically serialized by DAL
        result = await db.update(
            "table",
            {"metadata": json_data},  # Will be JSON.stringify'd
            {"id": id}
        )
        return result.success
```

## Phase 3: Business Logic Services (4 services)

### 3.1 projects/versioning_service.py
**Complexity**: Low
**Tables**: `archon_project_versions` → `project_versions`
**Special Features**: JSON version data storage

#### Migration Requirements:
```python
# Key conversions:
# 1. List versions
client.table("archon_project_versions").select("*").eq("project_id", pid).order("created_at", desc=True)
→ 
await db.select("project_versions", 
    filters={"project_id": pid},
    order_by="created_at DESC"
)

# 2. Create version (with JSON)
client.table("archon_project_versions").insert({
    "project_id": pid,
    "version_data": json_data,  # JSONB field
    "version_number": num
})
→
await db.insert("project_versions", {
    "project_id": pid,
    "version_data": json_data,  # DAL handles JSON serialization
    "version_number": num
})

# 3. Get latest version
client.table("archon_project_versions").select("*").eq("project_id", pid).order("created_at", desc=True).limit(1)
→
await db.select("project_versions",
    filters={"project_id": pid},
    order_by="created_at DESC",
    limit=1
)
```

### 3.2 projects/document_service.py
**Complexity**: Medium
**Tables**: `archon_project_documents` → `project_documents`
**Special Features**: Document metadata, batch operations

#### Migration Requirements:
```python
# Key conversions:
# 1. Batch insert documents
docs = [{"project_id": pid, "content": c, "metadata": m} for c, m in items]
client.table("archon_project_documents").insert(docs)
→
await db.insert("project_documents", docs)  # DAL handles batch

# 2. Update document metadata
client.table("archon_project_documents").update({"metadata": meta}).eq("id", doc_id)
→
await db.update("project_documents", 
    {"metadata": meta},
    {"id": doc_id}
)

# 3. Delete project documents (cascading)
client.table("archon_project_documents").delete().eq("project_id", pid)
→
async with db.transaction() as tx:
    await tx.delete("project_documents", {"project_id": pid})
```

### 3.3 projects/project_service.py
**Complexity**: Medium
**Tables**: `archon_projects` → `projects`
**Special Features**: Complex JSON fields (docs, features, data, prd)

#### Migration Requirements:
```python
# Key conversions:
# 1. Create project with JSON fields
client.table("archon_projects").insert({
    "title": title,
    "description": desc,
    "docs": docs_json,      # JSONB
    "features": features_json,  # JSONB
    "data": data_json,      # JSONB
    "prd": prd_json         # JSONB
})
→
await db.insert("projects", {
    "title": title,
    "description": desc,
    "docs": docs_json,      # DAL handles all JSON
    "features": features_json,
    "data": data_json,
    "prd": prd_json
})

# 2. Update specific JSON field
client.table("archon_projects").update({"features": new_features}).eq("id", pid)
→
await db.update("projects",
    {"features": new_features},
    {"id": pid}
)

# 3. List projects with filtering
client.table("archon_projects").select("*").eq("status", "active").order("created_at", desc=True)
→
await db.select("projects",
    filters={"status": "active"},
    order_by="created_at DESC"
)
```

### 3.4 projects/task_service.py
**Complexity**: Medium
**Tables**: `archon_tasks` → `tasks`
**Special Features**: Status management, parent-child relationships, archiving

#### Migration Requirements:
```python
# Key conversions:
# 1. Get tasks with complex filters
client.table("archon_tasks").select("*")
    .eq("project_id", pid)
    .eq("status", "todo")
    .eq("archived", False)
    .order("task_order")
→
await db.select("tasks",
    filters={
        "project_id": pid,
        "status": "todo",
        "archived": False
    },
    order_by="task_order ASC"
)

# 2. Update task status
client.table("archon_tasks").update({
    "status": new_status,
    "updated_at": datetime.now()
}).eq("id", task_id)
→
await db.update("tasks",
    {
        "status": new_status,
        "updated_at": datetime.now()
    },
    {"id": task_id}
)

# 3. Archive tasks (soft delete)
client.table("archon_tasks").update({
    "archived": True,
    "archived_at": datetime.now(),
    "archived_by": user
}).eq("id", task_id)
→
await db.update("tasks",
    {
        "archived": True,
        "archived_at": datetime.now(),
        "archived_by": user
    },
    {"id": task_id}
)
```

## Phase 4: Complex Services (7 services)

### 4.1 projects/source_linking_service.py
**Complexity**: Low
**Tables**: `archon_project_sources` → `project_sources`
**Special Features**: Many-to-many relationships

#### Migration Requirements:
```python
# Link sources to project
links = [{"project_id": pid, "source_id": sid} for sid in source_ids]
await db.insert("project_sources", links)

# Get project sources (with JOIN logic in application)
await db.select("project_sources", filters={"project_id": pid})
```

### 4.2 storage/base_storage_service.py
**Complexity**: Low (mostly abstract)
**Tables**: None directly (base class)
**Special Features**: Threading, chunking algorithms

#### Migration Requirements:
- Update any database client initialization
- Ensure child classes can use DAL
- Maintain chunking/threading logic

### 4.3 crawling/crawling_service.py
**Complexity**: High
**Tables**: `archon_sources`, `archon_crawled_pages`, `archon_code_examples`
**Special Features**: Batch operations, progress tracking, concurrent processing

#### Migration Requirements:
```python
# 1. Batch insert crawled pages
async with manager.get_primary() as db:
    async with db.transaction() as tx:
        # Insert source
        source_result = await tx.insert("sources", source_data)
        source_id = source_result.data[0]["id"]
        
        # Batch insert pages
        pages = [{"source_id": source_id, ...} for page in crawled_pages]
        await tx.insert("crawled_pages", pages)
        
        # Batch insert code examples
        examples = [{"source_id": source_id, ...} for ex in code_examples]
        await tx.insert("code_examples", examples)

# 2. Update crawl progress
await db.update("sources",
    {"status": "crawling", "metadata": {"progress": percent}},
    {"id": source_id}
)

# 3. Handle concurrent crawls with locking
# Use application-level locking or database advisory locks
```

### 4.4 projects/project_creation_service.py
**Complexity**: High
**Tables**: Multiple (via other services)
**Special Features**: Orchestrates multiple services, AI integration

#### Migration Requirements:
- This service primarily calls other services
- Ensure all called services are migrated first
- Wrap multi-service operations in transactions where possible
- Maintain AI integration (OpenAI calls remain unchanged)

### 4.5 search/rag_service.py
**Complexity**: Very High
**Tables**: `archon_crawled_pages`, `archon_code_examples`
**Special Features**: Vector search, RPC functions, hybrid search

#### Critical Vector Search Migration:
```python
# Supabase RPC for vector search
client.rpc("search_documents", {
    "query_embedding": embedding,
    "match_count": 10,
    "filter": {"source_id": sid}
})

# DAL abstraction (needs special handling)
async with manager.get_primary() as db:
    if hasattr(db, 'search'):  # PostgreSQL/Supabase with pgvector
        results = await db.search(
            "crawled_pages",
            query_vector=embedding,
            top_k=10,
            filters={"source_id": sid}
        )
    else:  # MySQL fallback
        # Implement alternative search strategy
        # Option 1: External vector service
        # Option 2: Keyword search fallback
        # Option 3: Load embeddings and compute in-memory
        results = await fallback_search(db, embedding, filters)
```

#### Hybrid Search Pattern:
```python
async def hybrid_search(query: str, embedding: list):
    manager = get_connection_manager()
    async with manager.get_reader() as db:
        # Keyword search
        keyword_results = await db.select(
            "crawled_pages",
            filters={"content": f"%{query}%"},  # LIKE query
            limit=50
        )
        
        # Vector search (if supported)
        if hasattr(db, 'search'):
            vector_results = await db.search(
                "crawled_pages",
                query_vector=embedding,
                top_k=50
            )
            
            # Merge and rerank results
            return merge_results(keyword_results, vector_results)
        
        return keyword_results
```

## Phase 5: API Routes (5 services)

### 5.1 api_routes/settings_api.py
**Complexity**: Low
**Current State**: Partially uses DAL via credential_service
**Migration Requirements**:
```python
# Remove direct Supabase usage for metrics
# Before:
supabase_client = get_supabase_client()
projects_response = supabase_client.table("archon_projects").select("id", count="exact")

# After:
manager = get_connection_manager()
async with manager.get_reader() as db:
    result = await db.select("projects", columns=["id"])
    count = len(result.data) if result.success else 0
```

### 5.2 api_routes/mcp_api.py
**Complexity**: Medium
**Tables**: Accesses multiple via services
**Migration Requirements**:
- Ensure all underlying services are migrated
- Update any direct Supabase calls
- Maintain MCP protocol compatibility

### 5.3 api_routes/knowledge_api.py
**Complexity**: High
**Tables**: Multiple via services
**Special Features**: Socket.IO, real-time updates, file uploads

#### Migration Requirements:
```python
# 1. Update progress tracking
async def emit_progress(source_id: str, progress: int):
    manager = get_connection_manager()
    async with manager.get_primary() as db:
        await db.update("sources",
            {"metadata": {"progress": progress}},
            {"id": source_id}
        )
    # Emit via Socket.IO (unchanged)
    await sio.emit("crawl_progress", {"progress": progress})

# 2. Handle file uploads with transactions
async def upload_document(file, metadata):
    manager = get_connection_manager()
    async with manager.get_primary() as db:
        async with db.transaction() as tx:
            # Insert source
            source = await tx.insert("sources", source_data)
            # Process and insert chunks
            for chunk in chunks:
                await tx.insert("crawled_pages", chunk)
```

### 5.4 api_routes/projects_api.py
**Complexity**: Medium
**Tables**: Multiple via services
**Special Features**: Socket.IO, complex workflows

#### Migration Requirements:
- Ensure all project services are migrated
- Wrap complex operations in transactions
- Maintain Socket.IO events

### 5.5 utils/__init__.py
**Complexity**: Low
**Purpose**: Backward compatibility layer
**Migration Requirements**:
```python
# Provide compatibility wrapper
async def get_supabase_client():
    """
    Deprecated: Use get_connection_manager() instead.
    This function now returns a compatibility wrapper.
    """
    warnings.warn(
        "get_supabase_client() is deprecated. Use get_connection_manager() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    manager = get_connection_manager()
    return SupabaseCompatibilityWrapper(manager)

class SupabaseCompatibilityWrapper:
    """Wraps DAL to provide Supabase-like interface for gradual migration"""
    def __init__(self, manager):
        self.manager = manager
    
    def table(self, name):
        # Return a query builder that mimics Supabase
        return QueryBuilder(self.manager, name)
```

## Testing Strategy

### Unit Test Template
```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_service_with_dal():
    # Mock the connection manager
    mock_manager = Mock()
    mock_db = AsyncMock()
    mock_manager.get_primary.return_value.__aenter__.return_value = mock_db
    mock_manager.get_reader.return_value.__aenter__.return_value = mock_db
    
    # Mock DAL responses
    mock_db.select.return_value = QueryResult(
        data=[{"id": "1", "title": "Test"}],
        count=1
    )
    
    # Test service methods
    service = ServiceClass()
    service.manager = mock_manager
    
    result = await service.get_items()
    assert len(result) == 1
    mock_db.select.assert_called_once_with("table_name")
```

### Integration Test Template
```python
@pytest.mark.integration
@pytest.mark.parametrize("db_type", ["mysql", "postgresql", "supabase"])
async def test_cross_database(db_type, setup_test_db):
    os.environ["DATABASE_TYPE"] = db_type
    
    # Initialize service with real database
    service = ServiceClass()
    
    # Test CRUD operations
    created = await service.create(test_data)
    assert created["id"]
    
    fetched = await service.get(created["id"])
    assert fetched["title"] == test_data["title"]
    
    updated = await service.update(created["id"], new_data)
    assert updated
    
    deleted = await service.delete(created["id"])
    assert deleted
```

## Migration Validation Checklist

### Per-Service Validation
- [ ] All `get_supabase_client()` calls removed
- [ ] All `client.table()` calls converted to DAL
- [ ] All operations made async
- [ ] Error handling uses `result.success` checks
- [ ] Transactions used for multi-table operations
- [ ] Table names use non-prefixed versions
- [ ] JSON fields handled correctly
- [ ] Unit tests updated
- [ ] Integration tests pass on all databases

### System-Wide Validation
- [ ] No direct Supabase imports in service layer
- [ ] All services use connection manager
- [ ] Connection pooling working
- [ ] Read replica routing working
- [ ] Transaction rollback working
- [ ] Vector search has fallback for MySQL
- [ ] Real-time updates have polling fallback
- [ ] Performance within 10% of baseline

## Risk Mitigation

### High-Risk Areas
1. **Vector Search in RAG Service**
   - Risk: MySQL doesn't support native vectors
   - Mitigation: Implement fallback search strategies
   - Testing: Extensive testing with all databases

2. **Real-time Updates**
   - Risk: Only Supabase has native real-time
   - Mitigation: Implement WebSocket polling for others
   - Testing: Load test WebSocket connections

3. **Complex Transactions**
   - Risk: Different transaction semantics across databases
   - Mitigation: Use standard ACID properties only
   - Testing: Test rollback scenarios

4. **JSON Operations**
   - Risk: Different JSON syntax across databases
   - Mitigation: Use DAL abstraction for JSON ops
   - Testing: Test complex JSON queries

## Performance Optimization

### Connection Pool Tuning
```python
# Environment variables for tuning
POOL_SIZE=20           # Number of connections
POOL_TIMEOUT=30        # Seconds to wait for connection
POOL_RECYCLE=3600     # Recycle connections after 1 hour
POOL_PRE_PING=true    # Test connections before use
```

### Query Optimization
```python
# Use prepared statements for repeated queries
async def get_by_id_optimized(ids: List[str]):
    manager = get_connection_manager()
    async with manager.get_reader() as db:
        # DAL can cache prepared statements
        return await db.select(
            "table",
            filters={"id": {"$in": ids}},  # IN query
            columns=["id", "title"]  # Only needed columns
        )
```

### Caching Strategy
```python
from functools import lru_cache
from aiocache import cached

class OptimizedService:
    @cached(ttl=300)  # Cache for 5 minutes
    async def get_frequently_accessed(self, key: str):
        manager = get_connection_manager()
        async with manager.get_reader() as db:
            result = await db.select("table", filters={"key": key})
            return result.data[0] if result.data else None
```

## Timeline & Prioritization

### Week 1: Complete Foundation & Business Logic
- Complete remaining Phase 3 services (4 services)
- Focus on services with fewer dependencies
- Establish patterns for JSON and transaction handling

### Week 2: Complex Services
- Migrate crawling and search services
- Implement vector search fallbacks
- Test batch operations thoroughly

### Week 3: API Layer & Testing
- Migrate all API routes
- Create compatibility layer in utils
- Comprehensive integration testing

### Week 4: Optimization & Documentation
- Performance tuning
- Load testing
- Documentation updates
- Training materials

## Success Metrics

### Functional Metrics
- ✅ All 18 services migrated
- ✅ Zero direct Supabase dependencies
- ✅ All tests passing on MySQL, PostgreSQL, and Supabase
- ✅ Vector search working with fallbacks
- ✅ Real-time updates working with polling

### Performance Metrics
- ✅ Response time < 200ms for simple queries
- ✅ Batch operations handle 1000+ records
- ✅ Connection pool utilization > 80%
- ✅ Memory usage stable under load
- ✅ No connection leaks after 24h operation

### Quality Metrics
- ✅ 90% test coverage
- ✅ Zero critical bugs
- ✅ All APIs backward compatible
- ✅ Migration guide complete
- ✅ Rollback procedures tested

## Conclusion

The remaining 14 services can be successfully migrated following the established patterns from the initial 4 services. The key to success is maintaining the migration order based on dependencies, ensuring comprehensive testing at each phase, and providing appropriate fallbacks for database-specific features. The migration will enable Archon to truly support multiple database backends while maintaining full functionality and performance.