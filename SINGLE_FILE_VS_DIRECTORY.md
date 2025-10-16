# Single File vs Directory Mode

## Overview

The refactoring agents system supports two modes of operation:
1. **Single File Mode** - Process only one specific file
2. **Directory Mode** - Recursively process all Python files in a directory

## Automatic Detection

The system automatically detects the mode based on the provided path:

```bash
# Single file mode (path is a .py file)
python refactoring_agents.py --target ./python/src/server/services/crawling_service.py

# Directory mode (path is a directory)
python refactoring_agents.py --target ./python/src/server/services
```

## Single File Mode

### When to Use
- You want to refactor just one specific file
- Testing the refactoring process on a small scope
- The file is isolated and doesn't need changes to other files
- Quick iteration on a single problematic class

### Behavior
```
Target: ./python/src/server/services/crawling_service.py

✅ WILL:
- Analyze only crawling_service.py
- Extract private/nested classes from this file
- Create new service files in the same directory
- Recursively decompose each extracted class
- Create tests for the original file and all extracted services

❌ WON'T:
- Touch any other existing files
- Analyze other files in the directory
- Modify imports in other files (you'll need to update manually)
```

### Example Workflow

**Before**:
```
services/
└── crawling_service.py  (800 lines, has _DocumentProcessor class)
```

**Command**:
```bash
python refactoring_agents.py --workflow full --target ./services/crawling_service.py
```

**After**:
```
services/
├── crawling_service.py  (now clean, < 30 lines per method)
├── document_processor_service.py  (extracted)
├── chunk_handler_service.py  (extracted from document_processor)
└── chunk_validator_service.py  (extracted from chunk_handler)
```

**Note**: You'll need to manually update any other files that import `crawling_service.py`.

### Limitations
- Import updates in other files must be done manually
- If the file depends on other files that also need refactoring, do those separately
- Integration tests that span multiple files won't be updated

## Directory Mode

### When to Use
- Refactoring an entire service layer
- Want to process multiple related files
- Need comprehensive refactoring across a module
- Want imports updated automatically across the directory

### Behavior
```
Target: ./python/src/server/services

✅ WILL:
- Recursively find all .py files in directory and subdirectories
- Process each file independently
- Extract classes and create new services
- Update imports across all files in the directory
- Create comprehensive test suite for all services

❌ WON'T:
- Modify files outside the target directory
- Update imports in parent/sibling directories
```

### Example Workflow

**Before**:
```
services/
├── crawling/
│   ├── crawling_service.py  (800 lines)
│   └── helpers.py  (500 lines)
└── storage/
    └── document_storage.py  (600 lines)
```

**Command**:
```bash
python refactoring_agents.py --workflow full --target ./services
```

**After**:
```
services/
├── crawling/
│   ├── crawling_service.py  (clean)
│   ├── document_processor_service.py  (extracted)
│   ├── chunk_handler_service.py  (extracted)
│   ├── helpers.py  (clean)
│   └── url_validator_service.py  (extracted from helpers)
└── storage/
    ├── document_storage.py  (clean)
    ├── chunk_storage_service.py  (extracted)
    └── metadata_service.py  (extracted)
```

**Benefit**: All imports between these files are automatically updated.

## Command Examples

### Single File Examples

```bash
# Analyze one file only
python refactoring_agents.py --workflow analysis --target ./services/crawling_service.py --dry-run

# Decompose one file
python refactoring_agents.py --workflow decomposition --target ./services/crawling_service.py

# Create tests for one file
python refactoring_agents.py --workflow testing --target ./services/crawling_service.py

# Full workflow on one file
python refactoring_agents.py --workflow full --target ./services/crawling_service.py
```

### Directory Examples

```bash
# Analyze entire directory
python refactoring_agents.py --workflow analysis --target ./services --dry-run

# Decompose all files in directory
python refactoring_agents.py --workflow decomposition --target ./services

# Create tests for all services
python refactoring_agents.py --workflow testing --target ./services

# Full workflow on directory
python refactoring_agents.py --workflow full --target ./services
```

### Backward Compatibility

The old `--target-dir` flag still works:
```bash
# Old syntax (still works)
python refactoring_agents.py --workflow full --target-dir ./services

# New syntax (preferred)
python refactoring_agents.py --workflow full --target ./services
```

## When to Use Which Mode

### Use Single File Mode When:
✅ You want precise control over what gets refactored
✅ Testing the system on a small scope first
✅ The file is self-contained or has minimal dependencies
✅ You want to review changes before doing more files
✅ Quick iteration during development

### Use Directory Mode When:
✅ Refactoring an entire module or service layer
✅ Files have interdependencies that need updating
✅ Want comprehensive refactoring across related files
✅ Confident in the refactoring process
✅ Production-ready refactoring

## Progressive Refactoring Strategy

Start small and expand:

```bash
# Step 1: Test on one file
python refactoring_agents.py --workflow full --target ./services/crawling_service.py

# Step 2: Review results, verify tests pass
git diff
pytest tests/unit/test_crawling_service.py

# Step 3: If successful, do related files
python refactoring_agents.py --workflow full --target ./services/document_service.py

# Step 4: Once confident, do entire directory
python refactoring_agents.py --workflow full --target ./services
```

## File Organization After Refactoring

### Single File Mode
Extracted services go in the **same directory** as the original file:

```
services/
├── crawling_service.py          # Original
├── document_processor.py        # Extracted from crawling_service
└── chunk_handler.py             # Extracted from document_processor
```

### Directory Mode
Maintains existing directory structure:

```
services/
├── crawling/
│   ├── crawling_service.py      # Original
│   └── document_processor.py    # Extracted, stays in crawling/
└── storage/
    ├── storage_service.py       # Original
    └── chunk_storage.py         # Extracted, stays in storage/
```

## Import Updates

### Single File Mode
**Manual** - You must update imports yourself:

```python
# Before (in other_file.py)
from services.crawling_service import CrawlingService, _DocumentProcessor

# After (you must change this manually)
from services.crawling_service import CrawlingService
from services.document_processor import DocumentProcessor  # NEW
```

### Directory Mode
**Automatic** - Imports updated within the target directory:

```python
# Before
from .crawling_service import CrawlingService, _DocumentProcessor

# After (automatically updated)
from .crawling_service import CrawlingService
from .document_processor import DocumentProcessor  # AUTO
```

## Testing Considerations

### Single File Mode
- Tests created for the file and all extracted services
- Existing tests for other files remain unchanged
- May need to update test fixtures manually if they import the refactored file

### Directory Mode
- Comprehensive test suite for all files
- Test imports updated automatically
- Fixtures updated across the directory

## Git Workflow

Both modes create commits after each successful change:

### Single File Mode Commits
```
refactor: extract DocumentProcessor from CrawlingService (depth: 1)
refactor: extract ChunkHandler from DocumentProcessor (depth: 2)
test: add interfaces and tests for CrawlingService
test: add interfaces and tests for DocumentProcessor
```

### Directory Mode Commits
```
refactor: extract DocumentProcessor from CrawlingService (depth: 1)
refactor: extract ChunkHandler from DocumentProcessor (depth: 2)
refactor: extract StorageHandler from StorageService (depth: 1)
test: add interfaces and tests for services/crawling/
test: add interfaces and tests for services/storage/
```

## Error Recovery

### Single File Mode
- Easier to rollback: `git reset --hard HEAD~N`
- Clear scope of changes
- Faster recovery

### Directory Mode
- More commits to rollback
- Use git tags for phase boundaries: `git tag before-directory-refactor`
- Rollback to tag: `git reset --hard before-directory-refactor`

## Performance

### Single File Mode
- Fast: ~30-60 minutes for 800 line file
- Predictable duration
- Good for iteration

### Directory Mode
- Slower: ~2-4 hours for 10 files
- Duration varies with directory size
- Good for production refactoring

## Summary

| Aspect | Single File Mode | Directory Mode |
|--------|-----------------|----------------|
| **Target** | One .py file | Directory (recursive) |
| **Scope** | Just that file | All .py files in dir |
| **Import Updates** | Manual | Automatic (within dir) |
| **Use Case** | Testing, iteration | Production refactoring |
| **Speed** | Fast (~1 hour) | Slower (~2-4 hours) |
| **Rollback** | Easy | More commits to undo |
| **Control** | Precise | Comprehensive |

## Best Practice: Start with Single File

```bash
# 1. Start with one problematic file
python refactoring_agents.py --workflow full --target ./services/crawling_service.py

# 2. Verify results
git diff
pytest tests/unit/

# 3. If successful, do more files individually
python refactoring_agents.py --workflow full --target ./services/storage_service.py

# 4. Once confident, do entire directory
python refactoring_agents.py --workflow full --target ./services
```

This progressive approach:
- Builds confidence in the refactoring process
- Allows early error detection
- Provides clear rollback points
- Minimizes risk of large-scale issues
