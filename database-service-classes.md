# Database Service Classes in Archon

This document tracks all service classes that directly interact with the Supabase database and their refactoring status to use the DatabaseRepository pattern.

## Service Classes Refactoring Checklist (23 total)

### Search Services
1. - [x] **RAGService** - Coordinates search strategies and performs RAG queries ✅ (Refactored to use DatabaseRepository)
2. - [x] **BaseSearchStrategy** - Implements fundamental vector similarity search ✅ (Refactored to use DatabaseRepository)
3. - [ ] **HybridSearchStrategy** - Combines vector and full-text search

### Storage Services
4. - [ ] **BaseStorageService** - Abstract base class for storage operations
5. - [ ] **DocumentStorageService** - Handles document uploads and storage
6. - [ ] **PageStorageOperations** - Manages web page storage operations
7. - [ ] **DocumentStorageOperations** - Handles document chunk storage operations

### Project Management Services
8. - [ ] **ProjectService** - Core business logic for project operations
9. - [ ] **TaskService** - Manages project tasks and task hierarchies
10. - [ ] **VersioningService** - Handles document versioning within projects
11. - [ ] **ProjectCreationService** - Advanced project creation with AI assistance
12. - [ ] **DocumentService** - Manages documents within projects
13. - [ ] **SourceLinkingService** - Manages project-source relationships

### Crawling Services
14. - [ ] **CrawlingService** - Orchestrates web crawling operations
15. - [ ] **CodeExtractionService** - Extracts and stores code examples from documents

### Knowledge Base Services
16. - [ ] **KnowledgeItemService** - Manages knowledge base items
17. - [ ] **KnowledgeSummaryService** - Provides lightweight summaries for polling
18. - [ ] **DatabaseMetricsService** - Retrieves database usage metrics

### Core System Services
19. - [ ] **MigrationService** - Manages database migrations
20. - [ ] **CredentialService** - Manages application credentials and configuration
21. - [ ] **PromptService** - Manages AI agent prompts
22. - [ ] **SourceManagementService** - Manages data sources (crawled/uploaded)

### Ollama Integration Services
23. - [ ] **ModelDiscoveryService** - Discovers and validates Ollama models

## Architecture Pattern

These services follow a **Service Layer Pattern** where:
- Each service contains business logic
- Services directly use the Supabase client
- Database operations are performed via `self.supabase_client` calls
- No repository abstraction layer exists

## Common Database Operations

Services typically use these Supabase methods:
- `.table()` - Select a table
- `.select()` - Query data
- `.insert()` - Add new records
- `.update()` - Modify existing records
- `.delete()` - Remove records
- `.rpc()` - Call stored procedures

## Client Initialization

All services obtain the Supabase client through:
```python
from src.server.utils import get_supabase_client
self.supabase_client = supabase_client or get_supabase_client()
```
