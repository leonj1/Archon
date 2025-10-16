# Recursive Refactoring Agents - Quick Start

## TL;DR

Agents that **recursively** decompose code until all functions are < 30 lines, then apply dependency injection and create comprehensive tests.

**NEW**: Supports both **single file** and **directory** modes!

```bash
# Single file mode - refactor just one file
python refactoring_agents.py --workflow full --target ./python/src/server/services/crawling_service.py

# Directory mode - recursively refactor all .py files
python refactoring_agents.py --workflow full --target ./python/src/server

# Quick workflows
python refactoring_agents.py --workflow analysis --target <file-or-dir> --dry-run  # Analyze
python refactoring_agents.py --workflow decomposition --target <file-or-dir>       # Decompose
python refactoring_agents.py --workflow testing --target <file-or-dir>             # Test
```

## How Recursion Works

**Not just one-level extraction - it goes DEEP until all functions < 30 lines:**

```
CrawlingService.py (has 200-line method)
  ↓ Extract private class
DocumentProcessor.py (created, has 80-line method)
  ↓ Still > 30 lines! Extract again (RECURSIVE)
ChunkHandler.py (created, has 45-line method)
  ↓ Still > 30 lines! Extract again (RECURSIVE)
ChunkValidator.py (created, all methods < 30 lines) ✓ DONE
  ↓ Back up the tree
ChunkHandler.py (now all methods < 30 lines) ✓ DONE
  ↓ Back up the tree
DocumentProcessor.py (now all methods < 30 lines) ✓ DONE
  ↓ Back up the tree
CrawlingService.py (now all methods < 30 lines) ✓ DONE
```

**Result**: 1 file with 200-line method → 4 clean services with all functions < 30 lines

## Termination Conditions

Agent stops recursing when:
- ✅ All functions < 30 lines
- ✅ No private/nested classes remain
- ✅ Max depth of 5 reached (safety)

## Safety Mechanisms

1. **Tests after EVERY extraction** - catches issues immediately
2. **Git commit after each success** - easy rollback
3. **Depth tracking** - prevents infinite loops
4. **Todo list** - tracks "Decompose ServiceX (depth: 3)"
5. **Maximum depth of 5** - hard stop for safety

## The 4 Agents

| Agent | Job |
|-------|-----|
| **DecompositionAgent** | Recursively extracts classes until all functions < 30 lines |
| **ClassCreatorAgent** | Adds dependency injection to all services (including new ones) |
| **TestRunnerAgent** | Validates changes with pytest |
| **CoordinatorAgent** | Orchestrates the workflow, tracks recursion tree |

## Single File vs Directory Mode

The system automatically detects whether you're targeting a file or directory:

**Single File Mode** (path ends with .py):
- ✅ Process only that specific file
- ✅ Extract classes from it
- ✅ Create tests for it
- ❌ Won't touch other files
- 💡 Good for testing and iteration

**Directory Mode** (path is a directory):
- ✅ Recursively process all .py files
- ✅ Update imports automatically
- ✅ Comprehensive refactoring
- 💡 Good for production refactoring

See `SINGLE_FILE_VS_DIRECTORY.md` for detailed comparison.

## Common Workflows

### Start Small - Single File
```bash
# Analyze just one file
python refactoring_agents.py --workflow analysis --dry-run --target ./python/src/server/services/crawling_service.py
```

### Decompose One Service (Directory)
```bash
# Recursively decompose all files in crawling directory
python refactoring_agents.py --workflow decomposition --target ./python/src/server/services/crawling
```

### Full Refactor with DI and Testing
```bash
# Complete workflow: recursive decomposition + testing + dependency injection
python refactoring_agents.py --workflow full --target ./python/src/server
```

## What You'll Get

**Before:**
- 3 files
- 40 functions
- 18 functions < 30 lines (45%)
- Private classes mixed in
- ENV vars read directly
- Direct client instantiation

**After:**
- 12 service files (recursive extraction)
- 68 functions (more, but smaller)
- 68 functions < 30 lines (100%) ✓
- All classes independent
- All dependencies injected via constructor
- No ENV var reads in classes
- Clean decomposition tree

## Decomposition Tree Example

```
CrawlingService
├── DocumentProcessorService (depth 1) ✓
│   ├── ChunkingService (depth 2) ✓
│   │   └── ChunkValidatorService (depth 3) ✓
│   └── MetadataExtractorService (depth 2) ✓
└── URLHandlerService (depth 1) ✓
    └── ProtocolValidatorService (depth 2) ✓
        └── SchemeValidatorService (depth 3) ✓
```

All ✓ means all functions < 30 lines

## Flags

```bash
--workflow        # analysis | decomposition | testing | injection | full
--target          # File or directory to refactor (detects mode automatically)
--target-dir      # (Deprecated: use --target) Directory to refactor
--model           # haiku | sonnet | opus (default: sonnet)
--dry-run         # Analysis only, no changes
```

## Troubleshooting

**"Agent stuck in recursion"**
- Check TodoWrite list for current depth
- Max depth is 5, will auto-stop
- Look for "fully decomposed" message

**"Tests failing mid-recursion"**
- Agent stops automatically
- Rollback: `git reset --hard HEAD~N` (N = failed depth level)
- Fix manually, then resume

**"Too many services created"**
- Check 30-line rule is being applied
- Some complex logic legitimately needs many services
- Better than giant monolithic classes

**"Can't track what changed"**
- Check git log for commit messages: "extract [Service] from [Parent] (depth: X)"
- Use `git log --graph --oneline` for visual tree
- TodoWrite maintains decomposition todo list

## Advanced Usage

### Resume After Failure
```bash
# Check what was being worked on
git log --oneline -10

# See current state
python refactoring_agents.py --workflow analysis --dry-run

# Resume with same target
python refactoring_agents.py --workflow decomposition --target-dir <same-dir>
```

### Process Multiple Files
```bash
# Process services directory (agent will recurse on each)
python refactoring_agents.py --workflow full --target-dir ./python/src/server/services
```

### Custom Depth Limit
Edit `refactoring_agents.py` and change max depth in DecompositionAgent prompt (currently 5)

## Expected Timeline

**Analysis**: 5-10 minutes per 1000 lines
**Decomposition**: 30-60 minutes per service (depends on depth)
**Injection**: 10-20 minutes per service
**Testing**: 2-5 minutes per extraction

**Full workflow on `CrawlingService.py` (~800 lines)**: ~2 hours

## Next Steps

1. ✅ Review the plan: `REFACTORING_PLAN.md`
2. ✅ Run analysis: `--workflow analysis --dry-run`
3. ✅ Review analysis output
4. ✅ Start with one service: `--workflow decomposition --target-dir <specific-service>`
5. ✅ Verify tests pass
6. ✅ Expand to more services
7. ✅ Apply DI: `--workflow injection`
8. ✅ Final validation

## Files

- `refactoring_agents.py` - Main script with all 4 agents
- `REFACTORING_PLAN.md` - Detailed plan and gap analysis
- `RECURSIVE_REFACTORING_README.md` - This file (quick start)

## Help

See detailed documentation in `REFACTORING_PLAN.md` for:
- Gap analysis from original plan
- Termination conditions details
- Safety mechanisms
- Error handling strategies
- Metrics and reporting
