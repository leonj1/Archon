# Database Abstraction Layer Migration Specification

## Executive Summary

This specification outlines the complete migration of Archon from direct Supabase dependency to a fully abstracted database layer supporting MySQL, PostgreSQL, and Supabase backends. Currently, while the DAL infrastructure exists, all service operations bypass it and directly call Supabase, making the multi-database support non-functional.

## Current State Analysis

### What's Already Implemented
- ✅ Database Abstraction Layer (DAL) with interfaces (`IDatabase`, `IVectorStore`)
- ✅ Adapter implementations for MySQL, PostgreSQL, and Supabase
- ✅ Connection manager with pooling and failover support
- ✅ Environment-based database selection (`DATABASE_TYPE`)
- ✅ UI database configuration display
- ✅ Database schema migrations for MySQL and PostgreSQL

### What's Missing
- ❌ Service layer migration from `get_supabase_client()` to `get_connection_manager()`
- ❌ Query translation from Supabase REST API to DAL methods
- ❌ Vector search abstraction for non-pgvector databases
- ❌ Real-time event handling abstraction
- ❌ Transaction management across services
- ❌ Comprehensive testing suite for multi-database scenarios

## Technical Architecture

### Service Migration Pattern

Each service needs to transition from:
```python
# Current (Supabase-specific)
from ..utils import get_supabase_client

client = get_supabase_client()
result = client.table("archon_sources").select("*").execute()
```

To:
```python
# Target (Database-agnostic)
from ..services.client_manager import get_connection_manager

manager = get_connection_manager()
async with manager.get_primary() as db:
    result = await db.select("sources", columns=["*"])
```

### Affected Services (18 files)

#### Core Services
1. **knowledge_api.py** - Knowledge base operations
2. **projects_api.py** - Project management
3. **settings_api.py** - Configuration management
4. **mcp_api.py** - Model Context Protocol operations

#### Storage Services
5. **base_storage_service.py** - Document storage abstraction
6. **crawling_service.py** - Web crawling and indexing
7. **source_management_service.py** - Source CRUD operations

#### Search Services
8. **rag_service.py** - RAG query processing
9. **prompt_service.py** - Prompt template management

#### Project Services
10. **document_service.py** - Document processing
11. **project_creation_service.py** - Project initialization
12. **project_service.py** - Project CRUD
13. **source_linking_service.py** - Source-project associations
14. **task_service.py** - Task management
15. **versioning_service.py** - Version control

#### Utility Services
16. **credential_service.py** - Credential storage
17. **client_manager.py** - Client initialization
18. **utils/__init__.py** - Shared utilities

## Implementation Phases

### Phase 1: Core Infrastructure Enhancement
**Duration: 1 week**
**Priority: Critical**

#### Tasks:
1. **Enhance DAL Query Builder**
   - Add support for complex JOIN operations
   - Implement aggregation functions (COUNT, SUM, etc.)
   - Add support for JSON field operations
   - Implement full-text search abstraction

2. **Create Service Base Class**
   ```python
   class DALService:
       def __init__(self):
           self.manager = get_connection_manager()
       
       async def with_transaction(self, operations):
           async with self.manager.get_primary() as db:
               async with db.transaction() as tx:
                   return await operations(tx)
   ```

3. **Implement Vector Search Abstraction**
   - Create fallback vector search for MySQL using external service
   - Implement hybrid search combining text and vector search
   - Add caching layer for vector operations

### Phase 2: Service Migration - Read Operations
**Duration: 1 week**
**Priority: High**

#### Migration Order (by dependency):
1. **credential_service.py** - No dependencies
2. **prompt_service.py** - Depends on credentials
3. **source_management_service.py** - Core data model
4. **document_service.py** - Depends on sources
5. **knowledge_api.py** - Depends on documents

#### Pattern for Each Service:
```python
class MigratedService(DALService):
    async def get_items(self, filters=None):
        async with self.manager.get_primary() as db:
            result = await db.select(
                table="sources",
                filters=filters,
                order_by="created_at DESC"
            )
            return result.data if result.success else []
```

### Phase 3: Service Migration - Write Operations
**Duration: 1 week**
**Priority: High**

#### Critical Write Operations:
1. **Document Upload & Processing**
   - Migrate file upload to use DAL transactions
   - Implement chunking strategy for large documents
   - Add rollback on processing failure

2. **Crawling Operations**
   - Convert batch inserts to use DAL
   - Implement progress tracking without Supabase realtime
   - Add error recovery mechanisms

3. **Project & Task Management**
   - Migrate CRUD operations
   - Implement cascading deletes
   - Add optimistic locking for concurrent updates

### Phase 4: Vector Operations & Search
**Duration: 2 weeks**
**Priority: High**

#### Components:
1. **Vector Storage Strategy**
   ```python
   class VectorManager:
       async def store_embeddings(self, docs, embeddings):
           if self.has_native_vectors():
               # PostgreSQL/Supabase with pgvector
               return await self.native_store(docs, embeddings)
           else:
               # MySQL - store in BLOB + external index
               return await self.fallback_store(docs, embeddings)
   ```

2. **Search Implementation**
   - Unified search interface across databases
   - Fallback to keyword search when vectors unavailable
   - Result ranking and reranking abstraction

3. **Performance Optimization**
   - Implement connection pooling per database type
   - Add query result caching
   - Optimize batch operations

### Phase 5: Real-time & Advanced Features
**Duration: 1 week**
**Priority: Medium**

#### Features to Abstract:
1. **Real-time Updates**
   - WebSocket-based polling for MySQL/PostgreSQL
   - Native Supabase realtime when available
   - Event queue for consistency

2. **Row-Level Security**
   - Application-level RLS for MySQL/PostgreSQL
   - Native RLS for Supabase
   - Unified permission model

3. **Backup & Migration Tools**
   - Cross-database data migration utilities
   - Backup/restore functionality
   - Schema version management

### Phase 6: Testing & Validation
**Duration: 1 week**
**Priority: Critical**

#### Test Suite Components:
1. **Unit Tests**
   - Test each DAL adapter independently
   - Mock database operations
   - Verify query translation

2. **Integration Tests**
   ```python
   @pytest.mark.parametrize("db_type", ["mysql", "postgresql", "supabase"])
   async def test_knowledge_operations(db_type):
       os.environ["DATABASE_TYPE"] = db_type
       # Test full CRUD cycle
   ```

3. **Performance Tests**
   - Benchmark operations across databases
   - Load testing with concurrent operations
   - Memory leak detection

4. **Migration Tests**
   - Test data migration between database types
   - Verify data integrity
   - Test rollback scenarios

## Technical Specifications

### Query Translation Layer

```python
class QueryTranslator:
    def translate_supabase_to_dal(self, supabase_query):
        """
        Convert Supabase query to DAL format
        Example:
            Input: client.table("sources").select("*").eq("status", "active")
            Output: db.select("sources", filters={"status": "active"})
        """
        pass
```

### Connection Management

```python
class EnhancedConnectionManager(ConnectionManager):
    async def execute_with_retry(self, operation, max_retries=3):
        """Execute operation with automatic retry and failover"""
        for attempt in range(max_retries):
            try:
                return await operation()
            except ConnectionError:
                if attempt == max_retries - 1:
                    raise
                await self.failover_to_replica()
```

### Migration Utilities

```python
class DatabaseMigrator:
    async def migrate_data(self, source_type: str, target_type: str):
        """Migrate data between database types"""
        source_manager = self.get_manager(source_type)
        target_manager = self.get_manager(target_type)
        
        # Stream data to avoid memory issues
        async for batch in self.stream_data(source_manager):
            await self.write_batch(target_manager, batch)
```

## Migration Checklist

### Per-Service Migration Steps:
- [ ] Identify all Supabase client calls
- [ ] Map Supabase operations to DAL methods
- [ ] Update imports and initialization
- [ ] Convert queries to DAL format
- [ ] Add error handling for database-specific issues
- [ ] Update transaction boundaries
- [ ] Add integration tests
- [ ] Update documentation

### Database-Specific Considerations:

#### MySQL
- [ ] Implement vector search workaround
- [ ] Handle JSON field limitations
- [ ] Optimize for InnoDB engine
- [ ] Configure connection pooling

#### PostgreSQL
- [ ] Leverage pgvector for embeddings
- [ ] Use native JSON operations
- [ ] Implement listen/notify for events
- [ ] Optimize for concurrent access

#### Supabase
- [ ] Maintain realtime subscriptions
- [ ] Preserve RLS policies
- [ ] Use edge functions where applicable
- [ ] Maintain PostgREST compatibility

## Risk Mitigation

### Identified Risks:
1. **Data Loss During Migration**
   - Mitigation: Implement comprehensive backup before migration
   - Add rollback capability for each service

2. **Performance Degradation**
   - Mitigation: Benchmark before/after migration
   - Implement caching layer
   - Optimize query patterns per database

3. **Feature Parity Issues**
   - Mitigation: Create feature compatibility matrix
   - Implement polyfills for missing features
   - Document limitations per database

4. **Breaking Changes**
   - Mitigation: Version the API
   - Maintain backward compatibility layer
   - Gradual rollout with feature flags

## Success Criteria

### Functional Requirements:
- [ ] All 18 services fully migrated to DAL
- [ ] Zero direct Supabase dependencies in service layer
- [ ] Full CRUD operations working on all databases
- [ ] Search functionality operational across backends
- [ ] No data loss during migration

### Performance Requirements:
- [ ] Query performance within 10% of direct Supabase calls
- [ ] Connection pool utilization > 80%
- [ ] Response time < 200ms for simple queries
- [ ] Batch operations handle 1000+ records

### Quality Requirements:
- [ ] 90% test coverage for migrated services
- [ ] Zero critical bugs in production
- [ ] Documentation complete for all services
- [ ] Migration guide for developers

## Timeline Summary

| Phase | Duration | Dependencies | Status |
|-------|----------|--------------|--------|
| Phase 1: Infrastructure | 1 week | None | Not Started |
| Phase 2: Read Operations | 1 week | Phase 1 | Not Started |
| Phase 3: Write Operations | 1 week | Phase 2 | Not Started |
| Phase 4: Vector & Search | 2 weeks | Phase 3 | Not Started |
| Phase 5: Advanced Features | 1 week | Phase 4 | Not Started |
| Phase 6: Testing | 1 week | Phase 5 | Not Started |

**Total Duration: 7 weeks**

## Conclusion

This migration represents a significant architectural improvement that will:
1. Enable true multi-database support
2. Reduce vendor lock-in
3. Improve testability and maintainability
4. Allow for deployment flexibility

The phased approach ensures minimal disruption while maintaining system stability throughout the migration process.