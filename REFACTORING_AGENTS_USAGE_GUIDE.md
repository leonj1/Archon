# How to Use refactoring_agents.py

## Overview

`refactoring_agents.py` is a **multi-agent system** that uses Claude Agent SDK to systematically refactor Python code through specialized agents working together. It now integrates with **validation hooks** that automatically enforce architectural constraints.

## Quick Start

```bash
# 1. Test validation hooks first
python test_validation_hooks.py

# 2. Run on a single file (recommended for first use)
python refactoring_agents.py --workflow full --target ./python/src/server/services/crawling_service.py

# 3. Watch the agents work together
# - DecompositionAgent extracts classes recursively
# - Validation hooks check every change
# - TestCreatorAgent creates comprehensive tests
# - All automated!
```

## Command-Line Interface

### Basic Syntax

```bash
python refactoring_agents.py --workflow <workflow> --target <path> [options]
```

### Required Arguments

**`--workflow <type>`** - Which refactoring workflow to execute:
- `analysis` - Analyze code, report issues (no changes)
- `decomposition` - Recursively extract classes until functions < 30 lines
- `testing` - Create interfaces, Fakes, and unit tests
- `injection` - Implement dependency injection patterns
- `full` - Complete workflow (analysis → decomposition → testing → validation)

**`--target <path>`** - File or directory to refactor:
- **File mode**: `./services/crawling_service.py` (single file)
- **Directory mode**: `./services/` (all .py files recursively)

### Optional Arguments

**`--model <model>`** - Claude model to use (default: `sonnet`):
- `haiku` - Fast, economical (good for testing)
- `sonnet` - Balanced performance (recommended)
- `opus` - Maximum capability (for complex refactoring)

**`--dry-run`** - Analysis only, no modifications:
- Sets permission mode to "ask"
- Useful for understanding what would change

**`--target-dir <path>`** - (Deprecated, use `--target`)

## The Six Agents

### 1. DecompositionAgent
**Purpose**: Recursively extracts classes until all functions < 30 lines

**What it does**:
- Finds private/nested classes
- Extracts them into independent service files
- **Recursively** analyzes each new service
- Continues until termination conditions met

**When to use**: `--workflow decomposition` or `--workflow full`

### 2. ClassCreatorAgent
**Purpose**: Implements dependency injection via constructors

**What it does**:
- Moves clients, repos, config to `__init__` parameters
- Removes `os.getenv()` calls from classes
- Updates all callers with injected dependencies

**When to use**: `--workflow injection` or `--workflow full`

### 3. ClassQualityAgent
**Purpose**: Analyzes testability and plans unit tests

**What it does**:
- Distinguishes pure vs impure functions
- Identifies external dependencies needing interfaces
- Creates test plan documents

**When to use**: `--workflow testing` or `--workflow full`

### 4. TestCreatorAgent
**Purpose**: Implements test plans with interfaces and Fakes

**What it does**:
- Creates Python Protocol interfaces
- Implements Fake classes for testing
- Writes comprehensive pytest unit tests
- Verifies 100% coverage

**When to use**: `--workflow testing` or `--workflow full`

### 5. TestRunnerAgent
**Purpose**: Validates refactored code with test execution

**What it does**:
- Runs pytest with coverage
- Analyzes failures
- Reports detailed findings

**When to use**: `--workflow full` (automatic)

### 6. CoordinatorAgent
**Purpose**: Orchestrates all other agents

**What it does**:
- Plans workflow phases
- Delegates to specialized agents via Task tool
- Tracks progress and metrics
- Ensures safety (tests after every change)

**When to use**: Always (automatically used)

## Workflows Explained

### Workflow: `analysis` (Safe - No Changes)

**Purpose**: Understand what needs refactoring

**Command**:
```bash
python refactoring_agents.py --workflow analysis --target ./services/ --dry-run
```

**What happens**:
1. Scans target for refactoring candidates
2. Reports:
   - Private/nested classes to extract
   - Functions > 30 lines
   - `os.getenv()` usage
   - Direct client instantiation
   - Estimated effort

**Output**: Analysis report (no code changes)

**Use when**:
- First time using the system
- Planning refactoring effort
- Understanding codebase issues

### Workflow: `decomposition` (Code Changes)

**Purpose**: Recursively extract classes until all functions < 30 lines

**Command**:
```bash
python refactoring_agents.py --workflow decomposition --target ./services/crawling_service.py
```

**What happens**:
1. DecompositionAgent analyzes target
2. Extracts private/nested classes → new service files
3. **Recursively** analyzes each new service
4. Validation hooks check each Write/Edit:
   - ✓ Functions < 30 lines?
   - ✓ Dependencies in constructor?
   - ✓ Pydantic types used?
5. Continues until all functions < 30 lines
6. Commits after each successful extraction

**Output**: Multiple service files, all with functions < 30 lines

**Use when**:
- Code has long functions (>30 lines)
- Private classes mixed with public classes
- Want better separation of concerns

**Example Result**:
```
Before: crawling_service.py (800 lines, 150-line function)
After:
  crawling_service.py (clean, < 30 lines per method)
  document_processor.py (extracted, < 30 lines per method)
  chunk_handler.py (extracted from processor, < 30 lines)
  chunk_validator.py (extracted from handler, < 30 lines)
```

### Workflow: `testing` (Code Changes)

**Purpose**: Create comprehensive test suite with interfaces and Fakes

**Command**:
```bash
python refactoring_agents.py --workflow testing --target ./services/
```

**What happens**:
1. For each service in target:
   - ClassQualityAgent analyzes purity
   - Identifies external dependencies
   - Creates test plan
2. TestCreatorAgent implements plan:
   - Creates Protocol interfaces
   - Creates Fake implementations
   - Refactors service to use interfaces
   - Writes unit tests with Fakes
3. Validation hooks verify:
   - ✓ Constructor has dependencies
   - ✓ Pydantic types used
4. Verifies 100% test coverage
5. Commits successful tests

**Output**: Interfaces, Fakes, comprehensive unit tests

**Use when**:
- After decomposition is complete
- Want testable code with dependency injection
- Need 100% test coverage

**Example Result**:
```
Created:
  protocols/database_protocol.py (IDatabaseClient interface)
  tests/fakes/fake_database_client.py (in-memory implementation)
  tests/unit/test_document_service.py (15 tests, 100% coverage)
```

### Workflow: `injection` (Code Changes)

**Purpose**: Implement dependency injection via constructors

**Command**:
```bash
python refactoring_agents.py --workflow injection --target ./services/
```

**What happens**:
1. ClassCreatorAgent processes each service
2. Moves dependencies to `__init__`
3. Removes `os.getenv()` calls
4. Updates all callers
5. Validation hooks verify DI pattern
6. Runs tests after each change

**Output**: Clean dependency injection throughout

**Use when**:
- Code has `os.getenv()` calls
- Services directly instantiate clients
- Want testable code with mocked dependencies

### Workflow: `full` (Complete Refactoring)

**Purpose**: Complete end-to-end refactoring with validation

**Command**:
```bash
python refactoring_agents.py --workflow full --target ./services/crawling_service.py --model sonnet
```

**What happens** (4 Phases):

**Phase 1 - Analysis**:
- Scan for refactoring candidates
- Estimate effort and decomposition depth

**Phase 2 - Recursive Decomposition**:
- Extract classes until all functions < 30 lines
- Validation hooks enforce constraints on every change
- Commit after each successful extraction

**Phase 3 - Interface Extraction & Testing**:
- Create interfaces for external dependencies
- Create Fake implementations
- Write comprehensive unit tests
- Verify 100% coverage

**Phase 4 - Final Validation**:
- Run complete test suite
- Check linting and type checking
- Generate final report with metrics

**Output**: Fully refactored, tested, validated code

**Use when**:
- Ready for complete refactoring
- Want automated, validated transformation
- Have time for full workflow (1-3 hours depending on size)

## Single File vs Directory Mode

### Single File Mode

**When**: Target is a `.py` file

**Example**:
```bash
python refactoring_agents.py --workflow full --target ./services/crawling_service.py
```

**Behavior**:
- ✅ Only processes that specific file
- ✅ New services created in same directory
- ❌ Won't touch other existing files
- ❌ Import updates in other files are manual

**Use when**:
- Testing the system
- Focused refactoring on one problematic file
- Quick iteration

**Timeline**: ~30-60 minutes for 800-line file

### Directory Mode

**When**: Target is a directory

**Example**:
```bash
python refactoring_agents.py --workflow full --target ./services/
```

**Behavior**:
- ✅ Recursively processes all `.py` files
- ✅ Creates new services maintaining structure
- ✅ Updates imports across directory
- ✅ Comprehensive refactoring

**Use when**:
- Production refactoring
- Want to refactor entire module
- Confident in the system

**Timeline**: ~2-4 hours for 10 files

## Integration with Validation Hooks

**Automatic Validation**: Every `Write` or `Edit` triggers 3 validation hooks:

### 1. Function Length Hook
Blocks if any function > 30 lines:
```
❌ process_document() - 45 lines

HOW TO FIX:
Extract into smaller methods
```

### 2. Constructor Dependencies Hook
Blocks if dependencies in wrong place:
```
❌ database_repo found in method parameter

Should be in __init__
```

### 3. Pydantic Types Hook
Blocks if using dicts instead of Pydantic:
```
❌ Parameter 'data: dict'

Use Pydantic BaseModel instead
```

**Circuit Breaker**: After 3 failed attempts, allows with warning

**Bypass**: `SKIP_VALIDATION=1 python refactoring_agents.py ...`

## Example Usage Scenarios

### Scenario 1: First-Time User

```bash
# Step 1: Analyze to understand scope
python refactoring_agents.py --workflow analysis --target ./services/crawling_service.py --dry-run

# Step 2: Test on single file
python refactoring_agents.py --workflow decomposition --target ./services/crawling_service.py --model haiku

# Step 3: Review results
git diff
pytest tests/unit/

# Step 4: If good, proceed with full workflow
python refactoring_agents.py --workflow full --target ./services/crawling_service.py
```

### Scenario 2: Production Refactoring

```bash
# Step 1: Create backup tag
git tag refactor-backup-$(date +%Y%m%d)

# Step 2: Run full workflow on directory
python refactoring_agents.py --workflow full --target ./python/src/server/services/ --model sonnet

# Step 3: Validate results
pytest python/tests/
uv run ruff check python/src/
uv run mypy python/src/

# Step 4: Commit if successful
git add -A
git commit -m "refactor: complete refactoring of services directory"
```

### Scenario 3: Just Testing

```bash
# Create interfaces and tests for already-decomposed code
python refactoring_agents.py --workflow testing --target ./services/document_processor.py
```

### Scenario 4: Just Dependency Injection

```bash
# Fix os.getenv() calls and direct instantiation
python refactoring_agents.py --workflow injection --target ./services/
```

## What to Expect During Execution

### Real-Time Output

```
🤖 Refactoring Automation
Target: ./services/crawling_service.py
Type: FILE
Model: sonnet
Workflow: full

Starting workflow: full

Agent: Analyzing crawling_service.py...
Tool: Read
Agent: Found 2 functions > 30 lines
Agent: Planning decomposition...
Tool: TodoWrite
Agent: Extracting DocumentProcessor class...
Tool: Write

❌ VALIDATION FAILED (1/3)
Function Length Validation: process_document() - 45 lines
Agent: Fixing function length...
Tool: Edit

✅ Validation passed
Agent: Committing extraction...
Tool: Bash
✓ Task completed
```

### Validation Feedback Loop

```
Agent creates file
    ↓
Hooks validate
    ↓
Any fail? → Agent receives feedback → Retries
    ↓
All pass → Continue
```

### Circuit Breaker Activation

```
Attempt 1: ❌ Function too long
Attempt 2: ❌ Still too long
Attempt 3: ❌ Still too long
⚠️ CIRCUIT BREAKER: Allowed after 3 attempts
Manual review required
```

## Expected Timeline

| Workflow | Single File (800 lines) | Directory (10 files) |
|----------|------------------------|----------------------|
| `analysis` | 5-10 minutes | 10-20 minutes |
| `decomposition` | 30-60 minutes | 2-3 hours |
| `testing` | 20-40 minutes | 1-2 hours |
| `injection` | 10-20 minutes | 30-60 minutes |
| `full` | 1-2 hours | 3-5 hours |

## Output Artifacts

After running `--workflow full`, you'll have:

### Code Files
```
services/
├── crawling_service.py          # Refactored, < 30 lines per method
├── document_processor.py        # Extracted
├── chunk_handler.py             # Extracted recursively
└── chunk_validator.py           # Extracted recursively
```

### Interface Files
```
protocols/
├── database_protocol.py         # IDatabaseClient
├── http_protocol.py             # IHttpClient
└── file_storage_protocol.py    # IFileStorage
```

### Test Files
```
tests/
├── unit/
│   ├── test_crawling_service.py    # 15 tests, 100% coverage
│   ├── test_document_processor.py  # 10 tests, 100% coverage
│   └── test_chunk_handler.py       # 8 tests, 100% coverage
├── fakes/
│   ├── fake_database_client.py
│   ├── fake_http_client.py
│   └── fake_file_storage.py
└── plans/
    ├── crawling_service_test_plan.md
    └── document_processor_test_plan.md
```

### Git Commits
```
refactor: extract DocumentProcessor from CrawlingService (depth: 1)
refactor: extract ChunkHandler from DocumentProcessor (depth: 2)
refactor: extract ChunkValidator from ChunkHandler (depth: 3)
test: add interfaces and tests for CrawlingService
test: add interfaces and tests for DocumentProcessor
test: add interfaces and tests for ChunkHandler
```

## Error Handling

### Validation Failure

**What happens**: Hook blocks, agent gets feedback, automatically retries

**When circuit breaker triggers**: After 3 attempts, allows with warning

**What to do**: Review the bypassed code manually

### Test Failure

**What happens**: Agent stops, reports failure

**What to do**:
```bash
# Review the failure
cat test_output.txt

# Rollback if needed
git reset --hard HEAD~N

# Fix manually or adjust validation
```

### Agent Stuck

**What happens**: Agent keeps retrying same operation

**What to do**:
```bash
# Check circuit breaker state
ls -la ~/.claude/hook_state/

# Force allow with escape hatch
SKIP_VALIDATION=1 python refactoring_agents.py --workflow decomposition --target ./services/

# Or manually fix the issue
```

## Best Practices

### 1. Start Small
✅ Test on single file first
✅ Use `--dry-run` for analysis
✅ Understand scope before running

### 2. Safety First
✅ Create git tag before refactoring
✅ Have comprehensive test suite
✅ Review changes before pushing

### 3. Progressive Refactoring
```bash
# Step 1: One file
python refactoring_agents.py --workflow full --target file1.py

# Step 2: Review and validate
git diff
pytest

# Step 3: Another file
python refactoring_agents.py --workflow full --target file2.py

# Step 4: Entire directory
python refactoring_agents.py --workflow full --target ./services/
```

### 4. Monitor Progress
✅ Watch validation feedback
✅ Check circuit breaker triggers
✅ Review git commits
✅ Run tests frequently

### 5. Recovery Strategy
✅ Git tags for rollback points
✅ Understand circuit breaker state
✅ Know when to bypass validation
✅ Keep test suite green

## Troubleshooting

### Problem: "Target path does not exist"
**Solution**: Verify path is correct, use absolute or relative path

### Problem: "Target file must be a Python file"
**Solution**: Only `.py` files supported in single file mode

### Problem: Validation keeps failing
**Solution**:
1. Check feedback message
2. Review circuit breaker state
3. Manually fix or bypass with `SKIP_VALIDATION=1`

### Problem: Agent creates too many files
**Solution**: This is expected - recursive decomposition creates multiple services. Review the decomposition tree.

### Problem: Tests failing after refactoring
**Solution**: Check if failures are in new code or existing code. Agent stops on test failures.

## Advanced Usage

### Custom Model Selection
```bash
# Fast iteration with Haiku
python refactoring_agents.py --workflow decomposition --target ./services/ --model haiku

# Production refactoring with Opus
python refactoring_agents.py --workflow full --target ./services/ --model opus
```

### Combining with Git Workflow
```bash
# Create feature branch
git checkout -b refactor/services

# Run refactoring
python refactoring_agents.py --workflow full --target ./services/

# Review changes
git diff main

# Run full test suite
pytest python/tests/

# Create PR if successful
git push origin refactor/services
```

### Selective Workflows
```bash
# Only decomposition (no tests)
python refactoring_agents.py --workflow decomposition --target ./services/

# Only testing (after manual decomposition)
python refactoring_agents.py --workflow testing --target ./services/

# Only DI (without decomposition)
python refactoring_agents.py --workflow injection --target ./services/
```

## Summary

**`refactoring_agents.py` is designed to be**:
- **Automated**: Agents work together without manual intervention
- **Validated**: Hooks enforce architectural constraints automatically
- **Safe**: Tests after every change, circuit breakers prevent loops
- **Flexible**: Single file or directory mode, multiple workflows
- **Comprehensive**: Complete refactoring from analysis to testing

**Recommended first run**:
```bash
python test_validation_hooks.py  # Verify hooks work
python refactoring_agents.py --workflow full --target ./path/to/single_file.py --model sonnet
```

**Production usage**:
```bash
git tag refactor-backup-$(date +%Y%m%d)
python refactoring_agents.py --workflow full --target ./directory/ --model sonnet
pytest && git commit -m "refactor: automated refactoring with validation"
```
