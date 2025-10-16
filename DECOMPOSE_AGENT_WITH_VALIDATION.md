# DecomposeAgent with Validation Hooks - Complete System

## TL;DR

**What it does**: Automatically refactors code with real-time validation enforcing architectural constraints.

**How it works**:
1. DecomposeAgent extracts classes, breaks down long functions
2. Three validation hooks check every change in parallel
3. Agent auto-retries if validation fails
4. Circuit breakers prevent infinite loops

**Run it**:
```bash
# Test hooks first
python test_validation_hooks.py

# Run refactoring with automatic validation
python refactoring_agents.py --workflow full --target ./python/src/server/services/
```

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    DecomposeAgent                        │
│  Recursively extracts classes until functions < 30 lines │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │  Write/Edit Tool     │
          │  (creates new file)  │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────────────────┐
          │    PostToolUse Hooks (PARALLEL)  │
          └──────────┬───────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌─────────────┐
   │Function │  │Constructor│ │  Pydantic   │
   │ Length  │  │   Deps   │  │   Types     │
   │ < 30    │  │    DI    │  │Strong Typing│
   └────┬────┘  └────┬────┘  └──────┬──────┘
        │            │               │
        └────────────┼───────────────┘
                     │
              All Pass? ────No──→ Block + Feedback ─→ Agent Retries
                     │                                      │
                    Yes                    ┌────────────────┘
                     │                     │
                     ▼                     ▼
              Continue              Circuit Breaker
                                   (after 3 attempts)
                                         │
                                         ▼
                                  Allow + Warning
                                   (manual review)
```

## Three Validation Constraints

### 1. Function Length < 30 Lines

**Enforces**: Single Responsibility Principle

**Example Violation**:
```python
def process_document(self, doc):
    # 50 lines of code mixing validation, transformation, storage
    # ... 50 lines ...
```

**Feedback**:
```
❌ process_document() - 50 lines (lines 23-72)

HOW TO FIX:
1. Extract into DocumentProcessorService
2. Break down: validate() -> transform() -> store()
3. Each method < 30 lines
```

### 2. Constructor Dependencies (Dependency Injection)

**Enforces**:
- Fundamental dependencies (clients, repos) in `__init__`
- Only changing values (IDs, data) in method params

**Example Violation**:
```python
class DocumentService:
    # ❌ Missing dependencies in __init__

    def process(self, doc_id: str, database_repo: IDatabaseRepository):
        # ❌ database_repo should be in __init__, not here
        return database_repo.get(doc_id)
```

**Correct Pattern**:
```python
class DocumentService:
    def __init__(self, database_repo: IDatabaseRepository):
        self.db = database_repo  # ✅ Injected

    def process(self, doc_id: str):
        return self.db.get(doc_id)  # ✅ Uses self.db
```

### 3. Pydantic Strong Typing

**Enforces**: Type-safe APIs with runtime validation

**Example Violation**:
```python
def process(self, data: dict) -> dict:
    # ❌ Weak typing - no validation, no IDE support
    return {'result': data['field']}
```

**Correct Pattern**:
```python
class ProcessRequest(BaseModel):
    field: str
    metadata: dict[str, str]

class ProcessResponse(BaseModel):
    result: str
    status: str

def process(self, request: ProcessRequest) -> ProcessResponse:
    # ✅ Strong typing, runtime validation, IDE autocomplete
    return ProcessResponse(result=request.field, status="done")
```

## Quick Start

### 1. Install Dependencies

```bash
# Already included in your environment
# Hooks use standard library (ast, json, subprocess)
```

### 2. Test Hooks

```bash
# Run test suite
python test_validation_hooks.py

# Expected output:
# ✅ PASS: Function Length - Valid (short function)
# ✅ PASS: Function Length - Invalid (50-line function)
# ✅ PASS: Constructor Dependencies - Valid
# ...
# 🎉 All tests passed!
```

### 3. Run Refactoring with Validation

```bash
# Full workflow with automatic validation
python refactoring_agents.py --workflow full --target ./python/src/server/services/crawling_service.py

# What happens:
# 1. DecomposeAgent extracts DocumentProcessorService from CrawlingService
# 2. Hooks validate:
#    ✓ All functions < 30 lines?
#    ✓ Dependencies in __init__?
#    ✓ Pydantic types used?
# 3. If any fail: Agent gets feedback and retries
# 4. After 3 attempts: Circuit breaker allows (with warning)
```

### 4. Bypass Validation (Development Only)

```bash
# Temporarily skip validation
SKIP_VALIDATION=1 python refactoring_agents.py --workflow decomposition --target ./services/
```

## Configuration

### Hook Configuration

**File**: `.claude/settings.json`

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/validate_function_length.py",
            "timeout": 30
          },
          {
            "type": "command",
            "command": "python .claude/hooks/validate_constructor_dependencies.py",
            "timeout": 30
          },
          {
            "type": "command",
            "command": "python .claude/hooks/validate_pydantic_types.py",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### Circuit Breaker Settings

**Edit any hook file** to adjust:

```python
# Configuration (at top of each hook file)
MAX_RETRIES = 3  # Number of attempts before bypass
LOOP_DETECTION_WINDOW = timedelta(minutes=5)  # Reset window
```

## Example Workflow

### Before Refactoring

```python
# crawling_service.py - 800 lines
class CrawlingService:
    def crawl_and_process(self, url, options):
        # 150 lines of code
        # - Fetch URL
        # - Parse HTML
        # - Extract text
        # - Chunk documents
        # - Store in database
        # - Update metadata
        # ... many more lines ...
```

### After Refactoring (with validation enforced)

```python
# crawling_service.py - Clean, < 30 lines per method
class CrawlingService:
    def __init__(self,
                 http_client: IHttpClient,          # ✅ DI
                 document_processor: DocumentProcessor):
        self.http = http_client
        self.processor = document_processor

    def crawl(self, request: CrawlRequest) -> CrawlResponse:  # ✅ Pydantic
        content = self.http.get(request.url)  # ✅ < 30 lines
        result = self.processor.process(content)
        return CrawlResponse(status="done", doc_id=result.id)

# document_processor.py - Extracted, validated
class DocumentProcessor:
    def __init__(self,
                 chunker: IChunker,                 # ✅ DI
                 database_repo: IDatabaseRepository):
        self.chunker = chunker
        self.db = database_repo

    def process(self, content: ProcessRequest) -> ProcessResponse:  # ✅ Pydantic
        chunks = self.chunker.chunk(content.text)  # ✅ < 30 lines
        doc_id = self.db.store(chunks)
        return ProcessResponse(id=doc_id)

# chunker_service.py - Extracted, validated
class ChunkerService:
    def chunk(self, request: ChunkRequest) -> ChunkResponse:  # ✅ Pydantic
        # ✅ All functions < 30 lines
        validated = self._validate(request)  # 8 lines
        chunked = self._split(validated)     # 12 lines
        return self._format(chunked)         # 7 lines
```

**Result**:
- 1 monolithic 800-line class → 3 clean services
- All functions < 30 lines ✅
- Dependency injection everywhere ✅
- Strong typing with Pydantic ✅
- Automatically validated during refactoring ✅

## Monitoring & Debugging

### Check Circuit Breaker State

```bash
# View all circuit breaker states
ls -la ~/.claude/hook_state/

# Example output:
# function_length/
#   crawling_service.py.state.json  (retry_count: 2)
# constructor_deps/
#   document_service.py.state.json  (retry_count: 1)
```

### View Circuit Breaker State

```bash
# Check specific file state
cat ~/.claude/hook_state/function_length/crawling_service.py.state.json

# Output:
{
  "attempts": ["2025-01-15T10:23:45", "2025-01-15T10:24:12"],
  "retry_count": 2
}
```

### Reset Circuit Breaker

```bash
# Reset for specific file
rm ~/.claude/hook_state/function_length/crawling_service.py.state.json

# Reset all states
rm -rf ~/.claude/hook_state/
```

### Debug Hook Execution

```bash
# Test hook manually with sample payload
echo '{
  "tool_name": "Write",
  "tool_input": {
    "file_path": "services/test.py",
    "content": "def test(): pass"
  }
}' | python .claude/hooks/validate_function_length.py

# Output (valid):
{"decision": "allow"}

# Output (invalid):
{"decision": "block", "reason": "..."}
```

## Troubleshooting

### Problem: Hook Validation Fails Repeatedly

**Symptom**: Same validation fails 3 times, circuit breaker triggers

**Diagnosis**:
```bash
# Check what's failing
cat ~/.claude/hook_state/*/service_name.py.state.json
```

**Solutions**:
1. Review agent feedback - is it clear and actionable?
2. Check if code can actually be fixed
3. Temporarily bypass: `SKIP_VALIDATION=1`
4. Manually fix the issue
5. Reset circuit breaker

### Problem: Validation Too Strict

**Symptom**: Legitimate code patterns get blocked

**Solutions**:
1. Edit hook file `.claude/hooks/validate_*.py`
2. Add exceptions for specific patterns
3. Adjust validation logic
4. Lower `MAX_RETRIES` for faster bypass

### Problem: Hook Performance Issues

**Symptom**: Validation takes >30 seconds

**Solutions**:
1. Increase timeout in `.claude/settings.json`
2. Optimize AST parsing in hook
3. Skip validation for large generated files

## Advanced Customization

### Add Custom Validation

Create `.claude/hooks/validate_no_env_reads.py`:

```python
#!/usr/bin/env python3
"""Ensure no os.getenv() calls in service classes"""
import json
import sys
import re

def main():
    payload = json.load(sys.stdin)
    content = payload.get('tool_input', {}).get('content', '')

    # Check for os.getenv() calls
    if re.search(r'os\.getenv\(', content):
        output = {
            "decision": "block",
            "reason": "Found os.getenv() call - use dependency injection instead"
        }
        print(json.dumps(output))
        sys.exit(2)

    print(json.dumps({"decision": "allow"}))
    sys.exit(0)

if __name__ == "__main__":
    main()
```

Add to `.claude/settings.json`:
```json
{
  "hooks": [
    /* ... existing hooks ... */,
    {
      "type": "command",
      "command": "python .claude/hooks/validate_no_env_reads.py",
      "timeout": 10
    }
  ]
}
```

## Best Practices

1. **Test hooks before refactoring** - Run `python test_validation_hooks.py`
2. **Start with one file** - Test on small scope first
3. **Monitor circuit breaker** - Watch for repeated failures
4. **Review bypassed code** - Circuit breaker = manual review needed
5. **Provide actionable feedback** - Make error messages helpful
6. **Keep hooks fast** - Target < 5 seconds per validation
7. **Version control state** - Don't commit `~/.claude/hook_state/`

## Performance Characteristics

| Metric | Value |
|--------|-------|
| **Hook execution time** | < 5 seconds per hook |
| **Parallel execution** | All 3 hooks run simultaneously |
| **Total validation overhead** | ~5-10 seconds per Write/Edit |
| **Circuit breaker trigger** | After 3 failed attempts |
| **State reset window** | 5 minutes of inactivity |

## Files Reference

```
.claude/
├── settings.json                                    # Hook configuration
└── hooks/                                          # Validation hooks
    ├── validate_function_length.py                 # Functions < 30 lines
    ├── validate_constructor_dependencies.py        # Dependency injection
    └── validate_pydantic_types.py                  # Strong typing

refactoring_agents.py                               # Main refactoring script
test_validation_hooks.py                            # Hook test suite

~/.claude/hook_state/                               # Circuit breaker state (not in git)
├── function_length/
├── constructor_deps/
└── pydantic_types/
```

## Documentation

- **System Overview**: `VALIDATION_HOOKS_SYSTEM.md`
- **Refactoring System**: `COMPLETE_REFACTORING_SYSTEM.md`
- **This Document**: `DECOMPOSE_AGENT_WITH_VALIDATION.md`
- **Claude Hooks Reference**: https://docs.claude.com/en/docs/claude-code/hooks

## Next Steps

1. ✅ Test hooks: `python test_validation_hooks.py`
2. ✅ Run on single file: `python refactoring_agents.py --workflow full --target services/crawling_service.py`
3. ✅ Review validation feedback
4. ✅ Check circuit breaker triggers
5. ✅ Expand to directory: `python refactoring_agents.py --workflow full --target services/`
6. ✅ Add custom validations as needed

🎉 **Result**: Automatically refactored, architecturally sound code with zero manual validation!
