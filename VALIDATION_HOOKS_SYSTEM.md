# Validation Hooks System for DecomposeAgent

## Overview

This system provides **automated validation** for the DecomposeAgent refactoring workflow. When the agent modifies code, **three validation hooks run in parallel** to ensure adherence to architectural constraints:

1. **Function Length** - All functions < 30 lines
2. **Constructor Dependencies** - Fundamental deps in `__init__`, only changing values in method params
3. **Pydantic Types** - Strong typing with Pydantic models for parameters and return types

If any validation fails, the agent receives **detailed feedback** and automatically retries. Built-in **circuit breakers** prevent infinite loops.

## Architecture

```
DecomposeAgent extracts class
         ↓
    Write/Edit tool executes
         ↓
    PostToolUse hooks trigger (PARALLEL)
         ├─→ validate_function_length.py
         ├─→ validate_constructor_dependencies.py
         └─→ validate_pydantic_types.py
         ↓
    ALL pass? → Continue
    ANY fail? → Block + Provide feedback → Agent retries
         ↓
    Circuit breaker after 3 attempts
         ↓
    Manual review required
```

## Validation Hooks

### 1. Function Length Validator

**File**: `.claude/hooks/validate_function_length.py`

**Validates**: All functions < 30 lines (excluding empty lines/comments)

**Triggers When**: Write or Edit on `.py` files (excludes test files)

**Feedback Example**:
```
FUNCTION LENGTH VALIDATION FAILED (1/3)

File: services/document_service.py
Found 2 function(s) exceeding 30 lines:

  • process_document() - 45 lines (lines 23-67)
  • validate_metadata() - 35 lines (lines 89-123)

📋 HOW TO FIX:
1. Extract each long function into a new service class
2. Break down complex logic into smaller helper methods
3. Each method should do ONE thing
4. Target: All functions < 30 lines

💡 EXAMPLE:
# Before: 50-line function
def process_document(self, doc):
    # ... 50 lines of code ...

# After: Extract to service
class DocumentProcessorService:
    def process(self, doc):  # 15 lines
        validated = self._validate(doc)  # 8 lines
        return self._transform(validated)  # 8 lines
```

### 2. Constructor Dependencies Validator

**File**: `.claude/hooks/validate_constructor_dependencies.py`

**Validates**:
- Fundamental dependencies (HTTP clients, DB repos, config) in `__init__`
- Method parameters only contain changing values (IDs, data, options)
- Service/Client classes have at least one fundamental dependency

**Triggers When**: Write or Edit on `.py` service files

**Feedback Example**:
```
CONSTRUCTOR DEPENDENCY VALIDATION FAILED (1/3)

File: services/document_service.py

❌ Fundamental dependencies found in method parameters (should be in __init__):

  • DocumentService.process_document(database_repo: IDatabaseRepository) - line 45

❌ Service classes missing dependencies in __init__:

  • ProcessorService - line 12

📋 DEPENDENCY INJECTION PATTERN:

✅ CORRECT - Dependencies in constructor:
class DocumentService:
    def __init__(self,
                 database_repo: IDatabaseRepository,  # Fundamental
                 http_client: IHttpClient,           # Fundamental
                 config: ServiceConfig):             # Fundamental
        self.db = database_repo
        self.http = http_client
        self.config = config

    def process_document(self, doc_id: str, options: ProcessOptions):
        # Uses self.db, self.http - NOT in parameters
        # Only 'doc_id' and 'options' (changing values) in parameters
        return self.db.get(doc_id)

❌ WRONG - Dependency in method parameter:
class DocumentService:
    def process_document(self, doc_id: str, database_repo: IDatabase):
        # BAD: database_repo should be in __init__, not here
        return database_repo.get(doc_id)

💡 RULE: Fundamental dependencies (clients, repos, config) in __init__
        Only changing values (IDs, data, options) in method parameters
```

### 3. Pydantic Types Validator

**File**: `.claude/hooks/validate_pydantic_types.py`

**Validates**:
- Function parameters use Pydantic models (not dicts or primitives)
- Return types are Pydantic models
- All complex data structures have type annotations

**Triggers When**: Write or Edit on `.py` service files

**Feedback Example**:
```
PYDANTIC TYPE VALIDATION FAILED (1/3)

File: services/document_service.py

❌ Return types should be Pydantic models:

  • process_document() -> dict (line 45)
    Return type 'dict' should be a Pydantic model

❌ Parameters should use Pydantic models (not dict):

  • store_document(data: dict) (line 67)
    Parameter 'data: dict' should use Pydantic model instead of dict

📋 PYDANTIC STRONG TYPING PATTERN:

✅ CORRECT - Pydantic models:
from pydantic import BaseModel

class DocumentRequest(BaseModel):
    content: str
    metadata: dict[str, str]
    tags: list[str]

class DocumentResponse(BaseModel):
    doc_id: str
    status: str
    created_at: datetime

def process_document(self,
                     request: DocumentRequest) -> DocumentResponse:
    # Strongly typed input and output
    return DocumentResponse(
        doc_id=generate_id(),
        status='processed',
        created_at=datetime.now()
    )

❌ WRONG - Using dict:
def process_document(self, data: dict) -> dict:
    # BAD: No type safety, hard to validate
    return {'doc_id': '123', 'status': 'done'}

💡 BENEFITS:
  • Runtime validation
  • IDE autocomplete
  • Clear API contracts
  • Automatic JSON serialization
```

## Circuit Breaker System

Each hook includes a **circuit breaker** to prevent infinite loops:

### Configuration
- **Max Retries**: 3 attempts
- **Time Window**: 5 minutes (resets counter after inactivity)
- **State Storage**: `~/.claude/hook_state/{hook_name}/{file}.state.json`

### Behavior

**Attempt 1-3**: Validation fails → Block → Provide feedback → Agent retries

**After 3 Attempts**: Circuit breaker triggers
```
⚠️ CIRCUIT BREAKER: Function length validation bypassed
Reason: Max retries (3) exceeded
File: services/document_service.py

Validation bypassed - manual review recommended.
```

### Escape Hatch

Bypass all validations temporarily:
```bash
SKIP_VALIDATION=1 python refactoring_agents.py --workflow full --target ./services/
```

## Integration with refactoring_agents.py

### DecomposeAgent Workflow

The DecomposeAgent in `refactoring_agents.py` works with hooks:

1. **Agent extracts class** → Writes new service file
2. **PostToolUse hooks trigger** → Validate in parallel
3. **Any failure?** → Agent receives feedback → Retries
4. **All pass?** → Proceeds to next decomposition
5. **Circuit breaker** → After 3 failures, allows (with warning)

### Configuration

Hooks are configured in `.claude/settings.json`:

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

### Parallel Execution

All three hooks run **simultaneously**:
- ✅ **Fast**: No sequential waiting
- ✅ **Independent**: Each validates different concerns
- ✅ **Any blocks all**: If one fails, agent gets ALL feedback

## Usage

### Running Refactoring with Validation

```bash
# Full workflow with automatic validation
python refactoring_agents.py --workflow full --target ./python/src/server/services/

# What happens:
# 1. DecomposeAgent extracts classes
# 2. For each Write/Edit:
#    → validate_function_length.py checks functions < 30 lines
#    → validate_constructor_dependencies.py checks DI pattern
#    → validate_pydantic_types.py checks strong typing
# 3. Agent auto-retries on failures
# 4. Circuit breaker after 3 attempts
```

### Bypassing Validation

Temporarily skip validation (development only):
```bash
SKIP_VALIDATION=1 python refactoring_agents.py --workflow decomposition --target ./services/crawling_service.py
```

### Checking Hook State

View circuit breaker state:
```bash
ls -la ~/.claude/hook_state/
# Shows retry counts and timestamps for each file
```

Reset circuit breaker for a file:
```bash
rm ~/.claude/hook_state/function_length/crawling_service.py.state.json
```

## Benefits

### 1. Automated Quality Enforcement
- No manual code review needed for architectural patterns
- Consistent standards across entire codebase
- Agent learns from feedback

### 2. Fast Feedback Loop
- Immediate validation on every change
- Parallel hook execution (fast)
- Specific, actionable error messages

### 3. Prevents Common Mistakes
- ❌ Long functions (>30 lines)
- ❌ Dependencies in wrong place
- ❌ Weak typing with dicts
- ❌ Missing type annotations

### 4. Safety Mechanisms
- Circuit breakers prevent infinite loops
- Escape hatch for emergency bypasses
- Timeout protection (30s per hook)

## File Structure

```
.claude/
├── settings.json              # Hook configuration
└── hooks/                     # Validation hooks
    ├── validate_function_length.py
    ├── validate_constructor_dependencies.py
    └── validate_pydantic_types.py

~/.claude/hook_state/          # Circuit breaker state
├── function_length/
│   ├── crawling_service.py.state.json
│   └── document_service.py.state.json
├── constructor_deps/
└── pydantic_types/
```

## Troubleshooting

### Hook Stuck in Loop

**Symptom**: Same validation fails 3+ times

**Solution**:
1. Check the feedback message - is it actionable?
2. Review the code - can the agent actually fix it?
3. Temporarily bypass: `SKIP_VALIDATION=1`
4. Manually fix the issue
5. Reset circuit breaker

### Validation Too Strict

**Symptom**: Legitimate code gets blocked

**Solution**:
1. Adjust hook logic in `.claude/hooks/validate_*.py`
2. Add exceptions for specific patterns
3. Lower `MAX_RETRIES` for faster bypass
4. Use `SKIP_VALIDATION=1` for that file

### Hook Performance

**Symptom**: Slow validation on large files

**Solution**:
1. Increase timeout in `.claude/settings.json`
2. Optimize AST parsing in hook
3. Skip validation for generated/vendor files

## Advanced Customization

### Adding New Validation

Create new hook:
```python
#!/usr/bin/env python3
# .claude/hooks/validate_custom.py

import json
import sys

def main():
    payload = json.load(sys.stdin)

    # Your validation logic here
    is_valid = True

    if not is_valid:
        output = {
            "decision": "block",
            "reason": "Custom validation failed...",
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
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          /* ... existing hooks ... */,
          {
            "type": "command",
            "command": "python .claude/hooks/validate_custom.py",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### Adjusting Circuit Breaker

Edit hook file:
```python
# Configuration
MAX_RETRIES = 5  # Increase from 3
LOOP_DETECTION_WINDOW = timedelta(minutes=10)  # Increase from 2
```

### Custom Feedback Messages

Modify `format_violation_message()` in any hook to customize feedback.

## Best Practices

1. **Start with validation disabled** - Get refactoring working first
2. **Enable one hook at a time** - Easier debugging
3. **Monitor circuit breaker state** - Watch for patterns
4. **Provide actionable feedback** - Help agent fix issues
5. **Review bypassed files** - Circuit breaker = needs manual review
6. **Keep hooks fast** - Target < 5 seconds per validation
7. **Test hooks independently** - Run with sample files

## Testing Hooks

Test a hook directly:
```bash
echo '{
  "tool_name": "Write",
  "tool_input": {
    "file_path": "test_service.py",
    "content": "def long_function():\n    pass"
  }
}' | python .claude/hooks/validate_function_length.py
```

Expected output for valid code:
```json
{"decision": "allow"}
```

Expected output for invalid code:
```json
{"decision": "block", "reason": "..."}
```

## Next Steps

1. ✅ Review validation hook implementations
2. ✅ Test on sample refactoring
3. ✅ Adjust `MAX_RETRIES` if needed
4. ✅ Add custom validations for your needs
5. ✅ Monitor circuit breaker triggers
6. ✅ Integrate with CI/CD for pre-commit validation

## References

- **Claude Code Hooks Documentation**: https://docs.claude.com/en/docs/claude-code/hooks
- **Refactoring Agents System**: `COMPLETE_REFACTORING_SYSTEM.md`
- **Circuit Breaker Pattern**: Prevents infinite loops in validation
- **Pydantic Documentation**: https://docs.pydantic.dev/
