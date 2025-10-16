# Complete Refactoring System - Final Specification

## Overview

A comprehensive AI-powered refactoring system that:
1. **Recursively decomposes** code until all functions < 30 lines
2. **Extracts interfaces** for external dependencies
3. **Creates Fake implementations** for unit testing
4. **Writes comprehensive unit tests** with 100% coverage
5. **Implements dependency injection** throughout

## The 6 Specialized Agents

### 1. DecompositionAgent
**Purpose**: Recursively extract classes until all functions < 30 lines

**Process**:
```
Extract class → Analyze new class → Still has >30 line methods?
  ├─ YES → Extract again (recurse)
  └─ NO → Mark "fully decomposed" ✓
```

**Termination**: Max depth 5, all functions < 30 lines

### 2. ClassQualityAgent
**Purpose**: Analyze testability and plan comprehensive unit tests

**Process**:
1. Read fully decomposed service
2. Identify pure functions (no external calls)
3. Identify impure functions (need interfaces)
4. Specify interfaces to create
5. Plan Fake implementations
6. Write test plan document

**Output**: Test plan markdown file

### 3. TestCreatorAgent
**Purpose**: Implement test plan with interfaces, Fakes, and tests

**Process**:
1. Create Protocol interfaces
2. Create Fake implementations
3. Refactor service to use interfaces
4. Write pytest unit tests
5. Verify 100% coverage

**Output**: Interfaces, Fakes, unit tests (all passing)

### 4. ClassCreatorAgent
**Purpose**: Implement dependency injection via constructors

**Process**:
1. Move all dependencies to `__init__`
2. Remove `os.getenv()` calls
3. Remove direct client instantiation
4. Update all callers

**Output**: Clean DI constructors

### 5. TestRunnerAgent
**Purpose**: Run tests and validate refactored code

**Process**:
1. Execute pytest suite
2. Analyze failures
3. Report coverage
4. Check linting/type checking

**Output**: Test results and coverage report

### 6. CoordinatorAgent
**Purpose**: Orchestrate the entire workflow

**Process**:
1. Plan workflow phases
2. Delegate to specialized agents
3. Track progress (decomposition tree, test coverage)
4. Validate each step
5. Generate final report

**Output**: Orchestrated refactoring with metrics

## Complete Workflow

### Phase 1: Analysis
```bash
python refactoring_agents.py --workflow analysis --dry-run
```

**Actions**:
- Find private/nested classes
- Find functions > 30 lines
- Find external dependencies
- Find `os.getenv()` calls
- Create prioritized todo list

**Output**: Analysis report (no changes)

### Phase 2: Recursive Decomposition
```bash
python refactoring_agents.py --workflow decomposition
```

**Actions**:
- Extract private/nested classes
- **Recursively** analyze each new service
- Continue until all functions < 30 lines
- Test after each extraction
- Commit each successful extraction

**Output**: Tree of decomposed services

**Example**:
```
CrawlingService (200 line method)
  ↓ extract
DocumentProcessor (80 line method)
  ↓ recursively extract
ChunkHandler (45 line method)
  ↓ recursively extract
ChunkValidator (all < 30 lines) ✓ DONE
```

### Phase 3: Testing & Interface Extraction
```bash
python refactoring_agents.py --workflow testing
```

**For each fully decomposed service**:

**3a. Test Planning** (ClassQualityAgent):
```
Analyze function purity:
├─ calculate_size: ✓ Pure (no Fakes)
└─ store_document: ✗ Uses database (needs IDatabaseClient)

Plan interfaces:
└─ IDatabaseClient
   ├─ Methods: insert(), query()
   └─ Fake: FakeDatabaseClient (in-memory dict)

Write test plan → tests/plans/service_test_plan.md
```

**3b. Test Implementation** (TestCreatorAgent):
```
Create Protocol:
└─ python/src/server/protocols/database_protocol.py

Create Fake:
└─ python/tests/fakes/fake_database_client.py

Refactor service to use interface:
class Service:
    def __init__(self, db: IDatabaseClient):  # Interface!
        self.db = db

Write unit tests:
└─ python/tests/unit/test_service.py
   ├─ test_calculate_size (pure, no Fake)
   ├─ test_store_document_success (with Fake)
   └─ test_store_document_errors (edge cases)

Verify 100% coverage ✓
```

**3c. Validation**:
```
Run tests → All passing ✓
Check coverage → 100% ✓
Commit → "test: add interfaces and tests for ServiceX"
```

### Phase 4: Final Validation
```
Run all tests → X/X passing ✓
Check linting → Pass ✓
Check type checking → Pass ✓
Generate report → metrics.md
```

### Full Workflow (All Phases)
```bash
python refactoring_agents.py --workflow full --target-dir ./python/src/server
```

Runs all phases sequentially with full validation.

## File Structure

### Before Refactoring
```
python/src/server/services/
└── crawling_service.py (monolithic, 800 lines)
```

### After Refactoring
```
python/
├── src/server/
│   ├── protocols/                      # Interfaces
│   │   ├── database_protocol.py        # IDatabaseClient
│   │   ├── http_protocol.py            # IHttpClient
│   │   └── file_storage_protocol.py    # IFileStorage
│   └── services/                       # Decomposed services
│       ├── crawling_service.py         # Clean, < 30 lines per method
│       ├── document_processor_service.py
│       ├── chunk_handler_service.py
│       ├── chunk_validator_service.py
│       └── metadata_extractor_service.py
└── tests/
    ├── unit/                           # Unit tests with Fakes
    │   ├── test_crawling_service.py
    │   ├── test_document_processor.py
    │   ├── test_chunk_handler.py
    │   └── test_chunk_validator.py
    ├── fakes/                          # Fake implementations
    │   ├── fake_database_client.py
    │   ├── fake_http_client.py
    │   └── fake_file_storage.py
    ├── fixtures/                       # Test data
    │   └── sample_documents.py
    └── plans/                          # Test plans
        ├── crawling_service_test_plan.md
        └── document_processor_test_plan.md
```

## Key Concepts

### Pure vs Impure Functions

**Pure** (easy to test, no interfaces):
```python
def calculate_chunk_size(text: str, max_size: int) -> int:
    # Only uses inputs, no external calls
    return min(len(text), max_size)

# Test: Simple unit test
def test_calculate_chunk_size():
    assert calculate_chunk_size("hello", 10) == 5
```

**Impure** (needs interface):
```python
def store_document(self, doc: dict) -> str:
    # Makes external database call
    result = self.database.insert('docs', doc)
    return result['id']

# Test: Unit test with Fake
def test_store_document(fake_db):
    service = DocumentService(database_client=fake_db)
    result = service.store_document({"content": "test"})
    assert result is not None
```

### Interface Pattern

**Protocol Definition**:
```python
# python/src/server/protocols/database_protocol.py
from typing import Protocol, Any

class IDatabaseClient(Protocol):
    def insert(self, table: str, data: dict) -> dict: ...
    def query(self, table: str, filters: dict) -> list[dict]: ...
```

**Fake Implementation**:
```python
# python/tests/fakes/fake_database_client.py
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

**Service Usage**:
```python
# python/src/server/services/document_service.py
from ..protocols.database_protocol import IDatabaseClient

class DocumentService:
    def __init__(self, database_client: IDatabaseClient):
        self.db = database_client  # Interface, not concrete!
```

**Test Usage**:
```python
# python/tests/unit/test_document_service.py
from tests.fakes.fake_database_client import FakeDatabaseClient

@pytest.fixture
def fake_db():
    return FakeDatabaseClient()

@pytest.fixture
def service(fake_db):
    return DocumentService(database_client=fake_db)

def test_store_document(service, fake_db):
    result = service.store_document({"content": "test"})
    assert result['id'] is not None

    # Verify Fake state
    stored = fake_db.query('documents', {'id': result['id']})
    assert len(stored) == 1
```

## Metrics Tracked

### Decomposition Metrics
- Services created: X
- Max recursion depth: X
- Average depth: X.X
- Functions > 30 lines BEFORE: X
- Functions < 30 lines AFTER: 100% ✓

### Testing Metrics
- Test plans created: X/X (100%)
- Protocols created: X
- Fakes created: X
- Unit tests written: X
- Pure functions (no Fakes): X
- Impure functions (with Fakes): X
- Line coverage: 100% ✓
- Branch coverage: 100% ✓

### Quality Metrics
- All tests passing: X/X ✓
- Linting: Pass ✓
- Type checking: Pass ✓

## Example Final Report

```
Refactoring Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DECOMPOSITION
─────────────────────
Original files: 3
Services created: 12
Max recursion depth: 4
Average depth: 2.3

Decomposition Tree:
CrawlingService (depth 0) ✓ ✓ [100%]
├── DocumentProcessor (depth 1) ✓ ✓ [100%]
│   ├── ChunkHandler (depth 2) ✓ ✓ [100%]
│   │   └── ChunkValidator (depth 3) ✓ ✓ [100%]
│   └── MetadataExtractor (depth 2) ✓ ✓ [100%]
└── URLHandler (depth 1) ✓ ✓ [100%]
    └── ProtocolValidator (depth 2) ✓ ✓ [100%]

Functions Analysis:
Before: 45% < 30 lines (18/40)
After: 100% < 30 lines (68/68) ✓

TESTING
─────────────────────
Test plans: 12/12 (100%)
Protocols: 8
  ├─ IDatabaseClient
  ├─ IHttpClient
  ├─ IFileStorage
  └─ ... (5 more)

Fakes: 8
  ├─ FakeDatabaseClient
  ├─ FakeHttpClient
  └─ ... (6 more)

Unit tests: 156
  ├─ Pure function tests: 89
  └─ Tests with Fakes: 67

Coverage:
  ├─ Line: 100% ✓
  ├─ Branch: 100% ✓
  └─ Missing: 0 ✓

QUALITY
─────────────────────
Tests: 156/156 passing ✓
Linting: Pass ✓
Type checking: Pass ✓

Git commits: 24
  ├─ Decomposition: 12
  └─ Testing: 12

Time taken: 2h 15m
```

## Safety Mechanisms

1. **Max Recursion Depth**: 5 levels (prevents infinite loops)
2. **Test After Every Change**: No exceptions
3. **Git Commits**: Each extraction and test suite
4. **100% Coverage Requirement**: Must achieve before proceeding
5. **Rollback Points**: Every commit is a rollback point
6. **Dry Run Mode**: Analyze first before making changes

## Commands Quick Reference

### Single File Mode (refactor one file)
```bash
# Analysis only (safe, no changes)
python refactoring_agents.py --workflow analysis --target ./services/crawling_service.py --dry-run

# Recursive decomposition
python refactoring_agents.py --workflow decomposition --target ./services/crawling_service.py

# Test planning and creation
python refactoring_agents.py --workflow testing --target ./services/crawling_service.py

# Full workflow (everything)
python refactoring_agents.py --workflow full --target ./services/crawling_service.py
```

### Directory Mode (refactor all .py files recursively)
```bash
# Analysis only (safe, no changes)
python refactoring_agents.py --workflow analysis --target ./python/src/server --dry-run

# Recursive decomposition
python refactoring_agents.py --workflow decomposition --target ./python/src/server

# Test planning and creation
python refactoring_agents.py --workflow testing --target ./python/src/server

# Dependency injection
python refactoring_agents.py --workflow injection --target ./python/src/server

# Full workflow (everything)
python refactoring_agents.py --workflow full --target ./python/src/server --model sonnet
```

**Note**: The system automatically detects whether the target is a file or directory.

## Dependencies

- Python 3.12+
- `uv` for package management
- `pytest` for testing
- `pytest-cov` for coverage
- `ruff` for linting
- `mypy` for type checking
- Claude Agent SDK

## What Makes This Complete

✅ **Recursive Decomposition**: Not just one level - goes deep until termination
✅ **Testability Analysis**: Distinguishes pure from impure functions
✅ **Interface Extraction**: Creates Protocols for external dependencies
✅ **Fake Implementations**: Working in-memory implementations for tests
✅ **100% Coverage**: Line and branch coverage verified
✅ **Dependency Injection**: Clean constructor injection
✅ **Safety First**: Tests after every change, max depth limits
✅ **Comprehensive Metrics**: Track everything
✅ **Clear Workflow**: Analysis → Decomposition → Testing → Validation
✅ **Git Integration**: Commit after each successful change

## Documentation Files

1. `refactoring_agents.py` - Main script with all 6 agents
2. `REFACTORING_PLAN.md` - Detailed recursive decomposition plan
3. `TESTING_WORKFLOW_GAPS.md` - What was missing from testing workflow
4. `RECURSIVE_REFACTORING_README.md` - Quick start for decomposition
5. `COMPLETE_REFACTORING_SYSTEM.md` - This file (complete specification)
