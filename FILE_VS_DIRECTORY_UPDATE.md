# Single File vs Directory Mode - Update Summary

## What Changed

Added intelligent file vs directory detection to the refactoring agents system. Now the system automatically adapts based on whether you provide a file path or directory path.

## Key Features Added

### 1. Automatic Mode Detection
```python
# Detects if target is file or directory
is_single_file = os.path.isfile(target_path)
target_type = "file" if is_single_file else "directory"
```

### 2. Path Validation
- Checks if path exists
- Validates .py extension for single files
- Clear error messages for invalid paths

### 3. Mode-Aware Agent Prompts
All agents now understand which mode they're operating in:

**DecompositionAgent**:
- Single file: Only decompose that file
- Directory: Process all .py files recursively

**CoordinatorAgent**:
- Tracks file vs directory workflow
- Adjusts delegation strategy
- Reports appropriate metrics

### 4. New `--target` Flag
- Replaces `--target-dir` (which still works for backward compatibility)
- Accepts both files and directories
- Automatically detects which mode to use

### 5. Visual Mode Indicator
Console now shows:
```
Target: ./services/crawling_service.py
Type: FILE
...
Single File Mode:
Will refactor only the specified file
```

## Usage Examples

### Before (only directory mode)
```bash
python refactoring_agents.py --workflow full --target-dir ./python/src/server
```

### After (both modes)
```bash
# Single file
python refactoring_agents.py --workflow full --target ./services/crawling_service.py

# Directory (same as before)
python refactoring_agents.py --workflow full --target ./python/src/server

# Old flag still works
python refactoring_agents.py --workflow full --target-dir ./python/src/server
```

## Files Modified

### 1. `refactoring_agents.py`
**Changes**:
- Added `--target` argument (replaces `--target-dir`)
- Added file/directory detection logic
- Added `.py` extension validation
- Updated agent prompts with file mode context
- Updated display to show mode and type
- Updated all workflow prompts to include mode context

**Key sections**:
```python
# Argument parsing
parser.add_argument("--target", help="File or directory to refactor")
parser.add_argument("--target-dir", help="(Deprecated)")

# Detection
is_single_file = os.path.isfile(target_path)
target_type = "file" if is_single_file else "directory"

# Mode context for all prompts
file_mode_context = f"""
TARGET MODE: {'SINGLE FILE' if is_single_file else 'DIRECTORY (RECURSIVE)'}
Target: {target_path}
...
"""
```

### 2. `CoordinatorAgent` Prompt
**Changes**:
- Added FILE vs DIRECTORY MODE section
- Explains behavior in each mode
- Single file: focus only on that file
- Directory: process all .py files recursively

### 3. `DecompositionAgent` Prompt
**Changes**:
- Added TARGET MODE awareness
- Explains where extracted services should go
- Single file: same directory
- Directory: maintain structure

## Documentation Created

### 1. `SINGLE_FILE_VS_DIRECTORY.md` (NEW)
Comprehensive 250+ line guide covering:
- When to use which mode
- Behavior differences
- Command examples
- Import update handling
- File organization
- Testing considerations
- Git workflow
- Error recovery
- Performance comparison
- Progressive refactoring strategy

**Key sections**:
- Automatic Detection
- Single File Mode (when/how/limitations)
- Directory Mode (when/how/benefits)
- Command Examples
- File Organization After Refactoring
- Import Updates (manual vs automatic)
- Git Workflow
- Summary comparison table

### 2. Updated: `RECURSIVE_REFACTORING_README.md`
**Changes**:
- Added TL;DR showing both modes
- Added "Single File vs Directory Mode" section
- Updated all command examples to use `--target`
- Added mode icons (✅/❌/💡)
- Updated flags section

### 3. Updated: `COMPLETE_REFACTORING_SYSTEM.md`
**Changes**:
- Split Commands Quick Reference into two sections:
  - Single File Mode commands
  - Directory Mode commands
- Added auto-detection note

## Backward Compatibility

✅ `--target-dir` still works (deprecated but functional)
✅ Existing scripts won't break
✅ Directory-only workflows unchanged

## Benefits

### For Users

**Single File Mode**:
- ✅ Test refactoring on small scope
- ✅ Quick iteration (30-60 min)
- ✅ Easy rollback
- ✅ Precise control
- ✅ Good for learning the system

**Directory Mode**:
- ✅ Comprehensive refactoring
- ✅ Automatic import updates
- ✅ Production-ready
- ✅ Batch processing
- ✅ Consistent across codebase

### For Workflow

**Progressive Refactoring**:
```bash
# Step 1: Test on one file (30-60 min)
python refactoring_agents.py --workflow full --target ./services/crawling_service.py

# Step 2: Review and validate
git diff
pytest tests/unit/test_crawling_service.py

# Step 3: If successful, do more files
python refactoring_agents.py --workflow full --target ./services/document_service.py

# Step 4: Finally, do entire directory (2-4 hours)
python refactoring_agents.py --workflow full --target ./services
```

## Implementation Details

### Path Resolution
```python
# Handle backward compatibility
target_path = args.target_dir if args.target_dir else args.target

# Validate existence
if not os.path.exists(target_path):
    console.print(f"[red]Error:[/red] Target path does not exist: {target_path}")
    return

# Detect type
is_single_file = os.path.isfile(target_path)

# Validate file extension
if is_single_file and not target_path.endswith('.py'):
    console.print(f"[red]Error:[/red] Target file must be a Python file (.py)")
    return
```

### Mode Context Injection
```python
file_mode_context = f"""
TARGET MODE: {'SINGLE FILE' if is_single_file else 'DIRECTORY (RECURSIVE)'}
Target: {target_path}

{'Focus ONLY on this file. Do not analyze or modify any other files.'
 if is_single_file else
 'Recursively process all Python files in this directory and subdirectories.'}
"""

# Prepended to all workflow prompts
workflow_prompts = {
    "analysis": f"""{file_mode_context}

    Analyze {'the file' if is_single_file else 'the codebase'} and report:
    ...
    """
}
```

### Agent Awareness
Agents now receive explicit instructions about mode:

**Example from CoordinatorAgent**:
```
CRITICAL - FILE vs DIRECTORY MODE:
You will receive a target path that is either:
- **SINGLE FILE**: Only process that specific file
- **DIRECTORY**: Recursively process all .py files

SINGLE FILE MODE:
- Focus exclusively on the provided file
- Create new service files in same directory
- Do not analyze or modify other existing files

DIRECTORY MODE:
- Process all Python files recursively
- Track which files have been processed
- Maintain directory structure
```

## Error Handling

### Path Validation
```bash
# Non-existent path
$ python refactoring_agents.py --target ./missing.py
Error: Target path does not exist: ./missing.py

# Non-Python file
$ python refactoring_agents.py --target ./README.md
Error: Target file must be a Python file (.py): ./README.md
```

### Clear Visual Feedback
```
Target: ./services/crawling_service.py
Type: FILE
...
Single File Mode:
Will refactor only the specified file
```

## Testing Strategy

### Single File Mode (Recommended First)
1. Pick a problematic file with long functions
2. Run analysis to see what will change
3. Run full workflow
4. Review git diff
5. Run tests
6. If good, proceed to more files

### Directory Mode (After Validation)
1. Ensure single file tests were successful
2. Have comprehensive test coverage
3. Create git tag for rollback point
4. Run on directory
5. Validate all tests pass
6. Review changes

## Performance Characteristics

| Mode | Time (800 line file) | Time (10 files) | Commits | Rollback |
|------|---------------------|-----------------|---------|----------|
| **Single File** | 30-60 min | N/A | ~10 | Easy |
| **Directory** | N/A | 2-4 hours | ~50 | More commits |

## Example Scenarios

### Scenario 1: New to the system
```bash
# Start with smallest scope
python refactoring_agents.py --workflow analysis --target ./services/crawling_service.py --dry-run

# If analysis looks good, refactor
python refactoring_agents.py --workflow full --target ./services/crawling_service.py
```

### Scenario 2: Confident, ready for production
```bash
# Go straight to directory mode
python refactoring_agents.py --workflow full --target ./services
```

### Scenario 3: Mixed approach
```bash
# File by file for critical services
python refactoring_agents.py --workflow full --target ./services/auth_service.py
python refactoring_agents.py --workflow full --target ./services/payment_service.py

# Directory mode for less critical services
python refactoring_agents.py --workflow full --target ./services/utils
```

## Summary

✅ **Added**: Single file mode for precise control
✅ **Added**: Automatic file/directory detection
✅ **Added**: Mode-aware agent prompts
✅ **Added**: Comprehensive documentation
✅ **Updated**: All command examples
✅ **Maintained**: Backward compatibility
✅ **Improved**: User experience with clear visual feedback

The system is now more flexible and user-friendly, supporting both small-scope testing and large-scale production refactoring.
