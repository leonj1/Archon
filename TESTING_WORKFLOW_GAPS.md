# Testing Workflow - What Was Missing

## Your Original Addition

You wanted to add testing after decomposition with:
- **ClassQualityAgent**: Plans unit tests for fully decomposed classes
- Distinguish pure functions (easy to test) from impure functions (need interfaces)
- Use **Fake implementations** for external dependencies
- Create interfaces for anything with network/disk I/O

## Critical Gaps Identified & Addressed

### 1. ⚠️ **Interface Extraction - Who Creates Them?**

**Problem**: You mentioned needing interfaces but didn't specify who creates them.

**Solution**: Added **TestCreatorAgent** that:
- Creates `Protocol` interfaces (Python's structural typing)
- Refactors services to depend on interfaces instead of concrete implementations
- Updates constructor signatures to accept interfaces
- Updates all callers to provide interface implementations

**Example**:
```python
# BEFORE (concrete dependency)
class DocumentService:
    def __init__(self, supabase_client: SupabaseClient):
        self.db = supabase_client

# AFTER (interface dependency)
class DocumentService:
    def __init__(self, database_client: IDatabaseClient):  # Interface!
        self.db = database_client
```

### 2. ⚠️ **Workflow Integration - When Does Testing Happen?**

**Problem**: Unclear when testing occurs relative to decomposition and DI.

**Solution**: Defined clear workflow:
```
Analysis
  ↓
Recursive Decomposition (until all functions < 30 lines)
  ↓
For EACH fully decomposed service:
  ├── ClassQualityAgent: Analyze & plan tests
  ├── TestCreatorAgent: Create interfaces, Fakes, tests
  └── Verify 100% coverage
  ↓
Final Validation
```

**Key**: Testing happens AFTER decomposition but BEFORE moving to next service.

### 3. ⚠️ **Interface vs Concrete Implementation Tracking**

**Problem**: Need to know what concrete class is being abstracted.

**Solution**: ClassQualityAgent documents:
```
Service: DocumentStorageService
External Dependency: supabase_client
├── Interface: IDatabaseClient (to be created)
├── Methods: insert(), query(), delete()
├── Fake: FakeDatabaseClient (in-memory storage)
└── Concrete: SupabaseClient (current implementation)
```

### 4. 🔍 **Pure Function Detection Patterns**

**Problem**: How to identify pure vs impure functions?

**Solution**: Defined detection rules:

**Pure** (no interfaces needed):
- Only uses function parameters
- No external calls
- Deterministic (same input = same output)
- No I/O operations

**Impure** (needs interfaces):
- Network I/O: `requests`, `httpx`, `aiohttp`
- Database I/O: Supabase, PostgreSQL, Redis
- File I/O: `open()`, `Path.read_text()`
- LLM Calls: OpenAI, Anthropic clients
- System calls: `subprocess`, `os.system`

### 5. 🔍 **Test Plan Documentation**

**Problem**: How to communicate test requirements between agents?

**Solution**: Test plan markdown format:
```markdown
# Test Plan: ServiceName

## Purity Analysis
- calculate_size: ✓ Pure
- store_document: ✗ Uses IDatabaseClient

## Interface Extraction Required
1. IDatabaseClient
   - Methods: insert(), query()
   - Fake: FakeDatabaseClient

## Test Cases
- test_calculate_size_valid_input
- test_store_document_success (with Fake)
- test_store_document_empty_content (error case)

## Coverage Target
- Lines: 100%
- Branches: 100%
```

### 6. 🔍 **Fake Implementation Guidelines**

**Problem**: How detailed should Fakes be?

**Solution**: Defined Fake characteristics:
- **Simple but realistic**: In-memory storage using dicts/lists
- **Implements interface**: Matches Protocol/ABC signatures
- **Stateful**: Maintains state across calls (like real service)
- **No network/disk**: All operations in-memory
- **Predictable**: Deterministic behavior for testing

**Example**:
```python
class FakeDatabaseClient:
    def __init__(self):
        self._storage: dict[str, list[dict]] = {}

    def insert(self, table: str, data: dict) -> dict:
        if table not in self._storage:
            self._storage[table] = []
        data['id'] = f"fake_id_{len(self._storage[table])}"
        self._storage[table].append(data)
        return data
```

### 7. 📦 **Test File Organization**

**Problem**: Where do tests, Fakes, and interfaces live?

**Solution**: Clear structure:
```
python/
├── src/server/
│   ├── protocols/              # Interfaces (Protocols)
│   │   ├── database_protocol.py
│   │   └── http_protocol.py
│   └── services/
│       └── document_service.py
└── tests/
    ├── unit/                   # Unit tests with Fakes
    │   └── test_document_service.py
    ├── integration/            # Integration tests (real dependencies)
    │   └── test_document_storage_integration.py
    ├── fakes/                  # Fake implementations
    │   ├── fake_database_client.py
    │   └── fake_http_client.py
    ├── fixtures/               # Test data
    │   └── sample_documents.py
    └── plans/                  # Test plans from ClassQualityAgent
        └── document_service_test_plan.md
```

### 8. 📊 **Coverage Metrics**

**Problem**: How to verify tests are sufficient?

**Solution**: Defined coverage targets:
- **Line coverage**: 100% (every line executed)
- **Branch coverage**: 100% (every if/else path)
- **Missing lines**: 0

Verification command:
```bash
uv run pytest python/tests/unit/test_service.py \
    --cov=python/src/server/services/service.py \
    --cov-report=term-missing
```

### 9. 🛡️ **Interface vs DI Integration**

**Problem**: How do interfaces relate to dependency injection?

**Solution**: They work together:

**ClassCreatorAgent** (original):
- Moves dependencies to constructor
- Removes `os.getenv()` calls

**TestCreatorAgent** (new):
- Creates interfaces for external dependencies
- Refactors constructor to accept interfaces
- Updates type hints to use Protocols

**Combined result**:
```python
class DocumentService:
    def __init__(
        self,
        database_client: IDatabaseClient,  # Interface (TestCreator)
        config: Config,                     # Injected (ClassCreator)
        http_client: IHttpClient,          # Interface (TestCreator)
    ):
        self.db = database_client
        self.config = config
        self.http = http_client
```

### 10. 🔄 **Existing Tests Handling**

**Problem**: What about tests that already exist?

**Solution**: TestCreatorAgent:
- Checks for existing test files first
- Augments existing tests rather than overwriting
- Updates existing tests if they use concrete implementations
- Preserves integration tests (different directory)

### 11. ⚡ **Test Quality Assurance**

**Problem**: How to ensure tests are actually good?

**Solution**: ClassQualityAgent plans:
- **Happy path**: Normal successful operation
- **Edge cases**: Empty inputs, boundary values, special characters
- **Error cases**: Invalid inputs, network failures, permissions
- **Assertions**: Verify both return values AND side effects

**Example test cases**:
```python
# Happy path
test_store_document_success

# Edge cases
test_store_document_empty_content
test_store_document_special_characters
test_store_document_max_size

# Error cases
test_store_document_database_failure
test_store_document_invalid_schema
```

### 12. 📝 **Protocol vs ABC Choice**

**Problem**: Python has multiple ways to define interfaces.

**Solution**: Use `typing.Protocol` for:
- Structural subtyping (duck typing)
- No inheritance required
- Easier to create Fakes
- Better for testing

Use ABC when:
- Need enforcement via inheritance
- Want abstract base class behavior
- Need shared implementation code

**Default**: Use `Protocol` for test interfaces.

### 13. 🔗 **Dependency Order**

**Problem**: Which services to test first?

**Solution**: Test in dependency order:
```
1. Leaf services (no dependencies on other services)
   ↓
2. Mid-level services (depend on leaf services)
   ↓
3. Root services (depend on mid-level services)
```

**Example**:
```
Test ChunkValidator (leaf) first
  ↓ (provides IChunkValidator)
Then ChunkHandler (uses IChunkValidator)
  ↓ (provides IChunkHandler)
Finally DocumentProcessor (uses IChunkHandler)
```

### 14. 🎯 **Mock vs Fake Clarification**

**Problem**: Terminology confusion.

**Solution**: Clear definitions:

| Type | Purpose | Example |
|------|---------|---------|
| **Fake** | Working implementation (in-memory) | FakeDatabaseClient with dict storage |
| **Mock** | Behavior verification | Verify method called X times |
| **Stub** | Canned responses | Always return same value |

**Default**: Use **Fakes** for dependencies (as you specified).

Use **Mocks** (via `unittest.mock`) only when:
- Verifying specific method calls
- Testing error handling paths
- Checking call counts/arguments

## Complete Updated Workflow

```
1. Analysis
   - Find classes needing decomposition
   - Find functions > 30 lines
   - Find external dependencies
   ↓
2. Recursive Decomposition
   - Extract until all functions < 30 lines
   ↓
3. For EACH fully decomposed service:
   ├─ ClassQualityAgent
   │  ├─ Analyze function purity
   │  ├─ Identify external dependencies
   │  ├─ Plan interface extraction
   │  └─ Create test plan document
   │
   ├─ TestCreatorAgent
   │  ├─ Create Protocol interfaces
   │  ├─ Create Fake implementations
   │  ├─ Refactor service to use interfaces
   │  ├─ Write pytest unit tests
   │  └─ Verify 100% coverage
   │
   └─ Validate
      ├─ Run tests (must pass)
      ├─ Check coverage (must be 100%)
      └─ Commit if successful
   ↓
4. Final Validation
   - Run all tests
   - Check linting
   - Generate report
```

## Key Metrics Tracked

**Decomposition**:
- Services created: X
- Max depth: X
- Functions < 30 lines: 100%

**Testing**:
- Test plans created: X/X (100%)
- Interfaces created: X
- Fakes created: X
- Unit tests written: X
- Test coverage: 100% (line & branch)
- Pure functions: X (no Fakes needed)
- Impure functions: X (Fakes needed)

## Commands Reference

```bash
# Run with testing
python refactoring_agents.py --workflow full --target-dir ./python/src/server

# Workflows now include:
# - analysis: Just analyze
# - decomposition: Recursive decomposition only
# - testing: Test planning and creation only (for already decomposed code)
# - full: Everything (decomposition → testing → validation)
```

## Example Output

```
Refactoring Complete!
━━━━━━━━━━━━━━━━━━━━━

Decomposition:
├─ Services created: 12
├─ Max depth: 4
└─ Functions < 30 lines: 100% ✓

Testing:
├─ Test plans: 12/12 (100%)
├─ Interfaces: 8 (IDatabaseClient, IHttpClient, IFileStorage, ...)
├─ Fakes: 8 (all working)
├─ Unit tests: 156 (all passing)
├─ Line coverage: 100% ✓
├─ Branch coverage: 100% ✓
├─ Pure functions: 42 (no Fakes)
└─ Impure functions: 28 (with Fakes)

Quality:
├─ Linting: Pass ✓
├─ Type checking: Pass ✓
└─ All tests: 156/156 passing ✓
```

## What's Now Included

✅ ClassQualityAgent - Analyzes testability and plans tests
✅ TestCreatorAgent - Creates interfaces, Fakes, and unit tests
✅ Interface extraction with Python Protocols
✅ Fake implementation guidelines and examples
✅ Pure vs impure function detection
✅ Test plan documentation format
✅ Test file organization structure
✅ 100% coverage verification
✅ Integration with dependency injection
✅ Dependency order testing
✅ Complete workflow integration

## Still Recommended to Add

1. **Performance testing**: For services with performance requirements
2. **Integration tests**: End-to-end tests with real dependencies (optional)
3. **Property-based testing**: Using `hypothesis` for edge case generation
4. **Mutation testing**: Using `mutmut` to verify test quality
5. **Contract testing**: For services that interact via APIs

These are advanced and can be added later. The current plan covers comprehensive unit testing with Fakes.
