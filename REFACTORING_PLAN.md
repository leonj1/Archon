# Recursive Refactoring Agents Plan

## Core Principle: Recursive Decomposition

**The decomposition agent works RECURSIVELY until all functions are < 30 lines.**

When you extract a class:
1. Create new service file
2. **Immediately analyze the NEW service** for further decomposition
3. Extract any private/nested classes or functions > 30 lines
4. Repeat steps 2-3 on each newly created service
5. Stop when all functions < 30 lines

## Example Recursive Flow

```
CrawlingService.py (has _DocumentProcessor with 150 line method)
  ↓ Extract _DocumentProcessor
DocumentProcessorService.py (created, has 80 line chunk_content method)
  ↓ Recursively analyze (not done yet - has 80 line method!)
  ↓ Extract chunk logic
ChunkingService.py (created, has 45 line validate_chunks method)
  ↓ Recursively analyze (not done yet - has 45 line method!)
  ↓ Extract validation logic
ChunkValidatorService.py (created, all methods < 30 lines) ✓ DONE
  ↓ Back to ChunkingService
ChunkingService.py (now all methods < 30 lines) ✓ DONE
  ↓ Back to DocumentProcessorService
DocumentProcessorService.py (now all methods < 30 lines) ✓ DONE
  ↓ Back to CrawlingService
CrawlingService.py (now all methods < 30 lines) ✓ DONE

RESULT: 1 original file → 4 well-decomposed services
```

## What's Missing from Original Plan

### 1. **Orchestration & Coordination** ⚠️ CRITICAL
**Problem**: No clear workflow for how agents work together
**Solution**: Added CoordinatorAgent to:
- Sequence the refactoring steps
- Delegate to specialized agents
- Track progress across workflow
- Handle failures and rollbacks

### 2. **Testing & Validation** ⚠️ CRITICAL
**Problem**: No mechanism to verify refactored code still works
**Solution**: Added TestRunnerAgent to:
- Run pytest after each change
- Identify breaking changes immediately
- Prevent cascading failures
- Validate linting and type checking

### 3. **Scope Definition** 🔍 IMPORTANT
**Problem**: Unclear what code to refactor
**Solution**:
- `--target-dir` flag to specify scope
- Exclusion rules for tests, generated code, models
- Detection rules for private classes vs legitimate private implementation

### 4. **Safety Mechanisms** 🛡️ IMPORTANT
**Problem**: No protection against breaking changes
**Solution**:
- Test after EVERY single refactor
- Git commit after each successful change
- Rollback capability with git reset
- Dry-run mode for analysis only

### 5. **Context Sharing** 🔗 IMPORTANT
**Problem**: Agents don't know what others changed
**Solution**:
- Coordinator maintains todo list
- TodoWrite tracks progress
- Git commits provide change history
- Each agent reads current file state

### 6. **Detection Logic** 🎯 USEFUL
**Problem**: Vague criteria for what to refactor
**Added**:
- Private class detection: Classes starting with `_`, nested classes, >50 line helpers
- ENV var detection: `os.getenv`, `os.environ[]` patterns
- Client instantiation: `Client()` calls inside methods
- Exclusions: dataclasses, Pydantic models, test fixtures

### 7. **Dependency Analysis** 📦 USEFUL
**Problem**: How to determine what to inject?
**Guidance**:
- ClassCreatorAgent analyzes class for external dependencies
- Type hints required for all injected parameters
- Optional dependencies use `Type | None = None` pattern
- Constructor parameter order: required first, optional last

### 8. **Documentation** 📝 USEFUL
**Added**:
- Progress reports from coordinator
- Git commit messages document each change
- Final summary report showing:
  - Classes extracted
  - Dependencies injected
  - ENV vars eliminated
  - Test results

### 9. **Incremental Execution** ⚡ USEFUL
**Problem**: All-or-nothing is risky
**Solution**: Workflow phases:
- Analysis (no changes)
- Decomposition only
- Injection only
- Full workflow

### 10. **Error Recovery** 🚨 USEFUL
**Problem**: What if something breaks mid-refactor?
**Solution**:
- Stop on first test failure
- Don't proceed until fixed
- Maintain rollback points
- Clear error reporting

## Termination Conditions

The recursive decomposition stops when:
- ✅ All functions in a service class are < 30 lines
- ✅ No private/nested classes remain
- ✅ No single-responsibility violations
- ✅ Maximum recursion depth of 5 reached (safety limit)

## Recursion Safety Mechanisms

1. **Depth Tracking**: Each decomposition tracks its depth (e.g., "depth: 3")
2. **Maximum Depth**: Hard limit of 5 levels to prevent infinite loops
3. **Todo List**: TodoWrite tracks "Decompose ServiceX (depth: N)"
4. **Testing**: Tests run after EACH extraction to catch issues early
5. **Commits**: Each extraction committed separately for easy rollback

## Decomposition Tree Tracking

The coordinator maintains a tree structure:
```
CrawlingService
├── DocumentProcessorService (depth 1) ✓ all < 30 lines
│   ├── ChunkingService (depth 2) ✓ all < 30 lines
│   │   └── ChunkValidatorService (depth 3) ✓ all < 30 lines
│   └── MetadataExtractorService (depth 2) ✓ all < 30 lines
└── URLHandlerService (depth 1) ✓ all < 30 lines
    └── ProtocolValidatorService (depth 2) ✓ all < 30 lines
```

Metrics collected:
- Total services created: 7
- Maximum depth: 3
- Average functions per service: 3-5
- Functions < 30 lines: 100%

## Recommended Workflow

### Phase 1: Analysis (Safe, Read-Only)
```bash
python refactoring_agents.py --workflow analysis --dry-run
```
**Output**: Report of refactoring candidates, no changes

### Phase 2: Recursive Decomposition
```bash
python refactoring_agents.py --workflow decomposition
```
**Process** (RECURSIVE):
1. Start with initial class/file
2. Extract private/nested class to new service
3. **Immediately analyze NEW service** - does it have functions > 30 lines?
4. If YES, recurse to step 2 on the new service
5. If NO, mark as "fully decomposed" ✓
6. Run tests after EACH extraction
7. Commit each successful extraction
8. Track decomposition depth and tree structure
9. Continue until ALL services have functions < 30 lines

**Example**:
```
Start: CrawlingService → Extract _DocProcessor →
  Analyze DocProcessorService → Extract _ChunkHandler →
    Analyze ChunkHandlerService → All < 30 lines ✓ →
  Back to DocProcessorService → All < 30 lines ✓ →
Back to CrawlingService → All < 30 lines ✓ DONE
```

### Phase 3: Dependency Injection (Incremental)
```bash
python refactoring_agents.py --workflow injection
```
**Process**:
1. Refactor one class at a time
2. Update all callers
3. Run tests after each class
4. Commit if tests pass
5. Stop if tests fail

### Phase 4: Full Workflow (Complete)
```bash
python refactoring_agents.py --workflow full --target-dir ./python/src/server
```
**Process**: All phases in sequence with validation

## The 30-Line Rule

**Why 30 lines?**
- Functions < 30 lines are easier to understand, test, and maintain
- Single Responsibility Principle: one function, one job
- Reduces cognitive load when reading code
- Easier to refactor and reuse
- Better testability with focused unit tests

**What counts as a line?**
- Actual code lines (excluding blank lines and comments)
- Function body only (not including signature/decorators)

**When to stop decomposing?**
```python
# ✓ GOOD - All functions < 30 lines
class ChunkValidatorService:
    def __init__(self, config: Config):  # 2 lines
        self.config = config

    def validate_size(self, chunk: str) -> bool:  # 5 lines
        min_size = self.config.min_chunk_size
        max_size = self.config.max_chunk_size
        size = len(chunk)
        return min_size <= size <= max_size

    def validate_content(self, chunk: str) -> bool:  # 4 lines
        if not chunk.strip():
            return False
        return True
```

**When to keep decomposing?**
```python
# ❌ BAD - Function > 30 lines, needs decomposition
class DocumentProcessor:
    def process_document(self, doc: str) -> List[Chunk]:  # 45 lines
        # Validation logic (10 lines)
        if not doc:
            raise ValueError("Empty document")
        # ... more validation

        # Chunking logic (20 lines)
        chunks = []
        current_chunk = ""
        # ... chunking algorithm

        # Metadata extraction (15 lines)
        for chunk in chunks:
            chunk.metadata = self._extract_metadata(chunk)
        # ... more metadata logic

        return chunks
```
Should be decomposed into:
- `DocumentValidator` (validation logic)
- `DocumentChunker` (chunking logic)
- `MetadataExtractor` (metadata logic)

## Agent Responsibilities (Clear Separation)

| Agent | What It Does | What It Doesn't Do |
|-------|--------------|-------------------|
| **CoordinatorAgent** | Plans, delegates, tracks recursion depth & tree | No code changes |
| **DecompositionAgent** | **RECURSIVELY** extracts classes until all functions < 30 lines | No DI changes, no testing |
| **ClassCreatorAgent** | Implements constructor injection on all services (including newly created) | No class extraction, no testing |
| **TestRunnerAgent** | Runs tests, reports results | No code changes, no fixes |

**Key**: DecompositionAgent doesn't just extract once - it keeps going recursively on each new service until termination conditions met.

## Safety Rules (Non-Negotiable)

1. ✅ **One Extraction at a Time**: Extract one class/function, test, commit, then recurse
2. ✅ **Test After Every Extraction**: No exceptions - even during recursion
3. ✅ **Track Recursion Depth**: Maximum depth of 5 levels to prevent infinite loops
4. ✅ **Commit Each Successful Extraction**: Provides rollback points at every depth level
5. ✅ **Stop on Failure**: Don't continue recursing if tests fail
6. ✅ **Verify Termination**: Ensure all functions < 30 lines before marking "done"
7. ✅ **Don't Interrupt Recursion**: Let agent complete full recursive tree before moving to next phase

## Example Usage

### Analysis Only
```bash
# What needs refactoring?
python refactoring_agents.py --workflow analysis --dry-run --target-dir ./python/src/server/services
```

### Extract Private Classes
```bash
# Safe, incremental extraction
python refactoring_agents.py --workflow decomposition --target-dir ./python/src/server/services
```

### Implement Dependency Injection
```bash
# Refactor constructors
python refactoring_agents.py --workflow injection --target-dir ./python/src/server/services
```

### Complete Refactor
```bash
# Full workflow with all safety checks
python refactoring_agents.py --workflow full --target-dir ./python/src/server --model sonnet
```

## Configuration

The script respects `.env` for API keys and uses:
- **uv** for Python dependency management (per project standards)
- **pytest** for testing
- **ruff** for linting
- **mypy** for type checking
- **git** for version control

## Metrics to Track

After refactoring, you'll have:

**Recursive Decomposition Metrics:**
- Total services created (including all recursive levels)
- Maximum recursion depth reached
- Average recursion depth
- Decomposition tree structure (visual diagram)
- Functions > 30 lines BEFORE: X
- Functions < 30 lines AFTER: 100% ✓
- Average function length: Y lines

**Dependency Injection Metrics:**
- Number of ENV var reads eliminated
- Number of classes using constructor injection
- Number of direct client instantiations removed

**Quality Metrics:**
- Test coverage maintained/improved
- Linting/type checking status
- Number of commits created (shows granularity)

**Example Report:**
```
Decomposition Complete!
━━━━━━━━━━━━━━━━━━━━━━━━
Original Files: 3
Services Created: 12
Max Depth: 4
Avg Depth: 2.3

Tree Structure:
CrawlingService
├── DocumentProcessorService (depth 1)
│   ├── ChunkingService (depth 2)
│   │   └── ChunkValidatorService (depth 3)
│   └── MetadataExtractorService (depth 2)
└── URLHandlerService (depth 1)
    └── ProtocolValidatorService (depth 2)
        └── SchemeValidatorService (depth 3)

Functions Analysis:
Before: 45% < 30 lines (18/40 functions)
After: 100% < 30 lines (68/68 functions) ✓

All tests passing ✓
```

## Potential Issues & Mitigations

| Issue | Mitigation |
|-------|-----------|
| **Infinite recursion** | Max depth of 5, track visited services, termination conditions |
| **Tests break during recursion** | Stop immediately, rollback to last working depth, fix manually |
| **Circular dependencies between services** | Decomposition agent identifies, coordinator resolves before proceeding |
| **Over-decomposition** | 30-line rule prevents excessive splitting, focus on single responsibility |
| **Missing dependencies** | ClassCreatorAgent analyzes thoroughly before changes |
| **Complex nested classes** | Mark for manual review, skip if too complex (flag at depth > 5) |
| **Recursion takes too long** | Limit initial scope, process one file/class at a time |
| **Performance impact** | Measure before/after, optimize if needed, accept some service overhead |
| **Lost in recursion tree** | TodoWrite tracks current depth and path, visual tree diagram |

## Next Steps

1. Review this plan and the generated `refactoring_agents.py`
2. Run analysis workflow first: `--workflow analysis --dry-run`
3. Review analysis output
4. Execute decomposition phase if needed
5. Execute injection phase
6. Validate with full test suite

## Questions to Consider

1. **Scope**: Start with one service or entire `python/src/server`?
2. **Priority**: Decomposition first or DI first?
3. **Testing**: Do you have comprehensive test coverage?
4. **Rollback**: Is the repo in a clean state for easy rollback?
5. **Review**: Do you want human review between phases?
