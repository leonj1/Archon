# Automated Test Fixer using Claude Agent SDK

## Overview

This script uses Claude Code SDK agents to automatically fix failing unit tests. It identifies failing tests by running `make test`, then spawns specialized agents to fix each failing test individually.

## Architecture

### Components

1. **Test Runner** (Python subprocess)
   - Runs `make test` directly
   - Captures output for parsing
   - No agent needed for this step

2. **Parser** (Python logic)
   - Parses test output to extract:
     - File paths
     - Test names
     - Error messages
   - Identifies both failed tests and failed suites (import errors)

3. **Fix Agent** (Claude SDK Agent)
   - Spawned for each failing test
   - Has access to:
     - Read, Write, Edit, Grep, Glob, Bash tools
   - Constrained to:
     - Never use Supabase directly
     - Only use database repository interface for DB operations
   - Makes minimal, targeted fixes

### Workflow

```
┌─────────────────────────────────────────────┐
│  Iteration Loop (max 10 iterations)         │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │ 1. Run make test (subprocess)         │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │ 2. Parse failures (Python)            │  │
│  │    - Extract file paths               │  │
│  │    - Extract test names               │  │
│  │    - Extract error messages           │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │ 3. Display failures table             │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │ 4. For each failing test:             │  │
│  │    ┌───────────────────────────────┐  │  │
│  │    │ Spawn Fix Agent                │  │  │
│  │    │ - Read test file               │  │  │
│  │    │ - Read implementation          │  │  │
│  │    │ - Identify mismatch            │  │  │
│  │    │ - Apply fix                    │  │  │
│  │    │ - Run specific test to verify │  │  │
│  │    └───────────────────────────────┘  │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │ 5. Check if all tests pass            │  │
│  │    - Yes: Exit with success           │  │
│  │    - No: Continue to next iteration   │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

## Usage

### Prerequisites

1. **Dependencies** (already installed if you have the project set up):
   ```bash
   uv sync  # Installs claude-agent-sdk, rich, python-dotenv
   ```

2. **Environment**:
   - Either set `ANTHROPIC_API_KEY` in `.env`
   - Or authenticate with Claude Code (no API key needed)

### Running the Script

```bash
# Make executable
chmod +x fix_tests_agent.py

# Run with uv
uv run python fix_tests_agent.py

# Or run directly with Python
python fix_tests_agent.py
```

### Expected Output

```
╭─────────────────────────────────────────────────╮
│ Automated Test Fixer                            │
│ Uses Claude agents to systematically fix        │
│ failing tests                                   │
│ Iterates until all tests pass or max            │
│ iterations reached                              │
╰─────────────────────────────────────────────────╯

======================================================================
Iteration 1/10
======================================================================

╭─────────────────────────────────────────────────╮
│ Step 1: Test Identification                     │
│ Running 'make test' to identify failing tests...│
╰─────────────────────────────────────────────────╯

Found 7 failing test(s)

           Failing Tests
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ #  ┃ File                  ┃ Test                ┃ Error          ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ 1  │ src/features/...      │ should apply...     │ expected...    │
│ 2  │ src/features/...      │ should apply...     │ expected...    │
...
```

## Configuration

### Max Iterations

Edit `fix_tests_agent.py`:
```python
class TestFixerOrchestrator:
    def __init__(self):
        self.max_iterations = 10  # Change this value
```

### Model Selection

Change the model in the agent options:
```python
options = ClaudeAgentOptions(
    model="sonnet",  # Options: "haiku", "sonnet", "opus"
    ...
)
```

### Tool Permissions

Modify the allowed_tools list:
```python
options = ClaudeAgentOptions(
    allowed_tools=[
        'Read',
        'Write',
        'Edit',
        'Grep',
        'Glob',
        'Bash',
        # Add or remove tools as needed
    ],
)
```

## How It Works

### Test Identification

The script runs `make test` via subprocess and captures the full output. It then parses the output looking for:

1. **Failed Tests**: Lines containing `FAIL` followed by file paths and test names
2. **Failed Suites**: Import errors or module resolution failures

Example parsing:
```
FAIL  src/features/projects/components/tests/ProjectCard.test.tsx > ProjectCard > should apply selected styles
```

Parsed as:
- File: `src/features/projects/components/tests/ProjectCard.test.tsx`
- Test: `should apply selected styles`

### Fix Agent Prompt

Each agent receives a detailed prompt including:

1. **Test Information**: File path, test name, error message
2. **Critical Constraints**: No Supabase, use repository pattern
3. **Workflow Steps**: Read → Understand → Identify → Fix → Validate
4. **Important Notes**: Specific guidance for common test types

The agent:
1. Reads the test file to understand expectations
2. Reads the implementation to understand current behavior
3. Identifies the mismatch
4. Applies a minimal fix
5. Runs the specific test to validate
6. Reports success or failure

### Success Detection

The script looks for these phrases in the agent's output:
- "test passed"
- "tests passed"
- "1 passed"
- "all tests passed"
- "test fixed successfully"

## Constraints & Best Practices

### What the Agent MUST Follow

1. **Never use Supabase directly**
   - Use database repository interface instead
   - Example: `repository.get_item()` not `supabase.from_('table').select()`

2. **Make minimal changes**
   - Fix only what's needed for the specific test
   - Don't refactor or add features

3. **Validate fixes**
   - Always run the specific test after making changes
   - Frontend: `cd archon-ui-main && npm run test -- <file>`
   - Backend: `cd python && uv run pytest <file> -v`

### Common Test Fix Patterns

1. **ClassName/Styling Tests**
   - Issue: Test expects specific CSS classes that don't match actual render
   - Solution: Update test expectations to match actual classes

2. **API/Header Tests**
   - Issue: Test expects headers that apiClient doesn't send
   - Solution: Update test expectations to match apiClient behavior

3. **Integration Tests**
   - Issue: Import errors or missing files
   - Solution: Fix imports or create missing files

4. **Pagination Tests**
   - Issue: Backend returns wrong page number
   - Solution: Fix backend pagination logic or test expectations

## Troubleshooting

### Agent Gets Stuck

If an agent can't fix a test after multiple attempts:
1. Check the error message - is it clear?
2. Review the agent's last output for clues
3. Manually investigate the test
4. Fix it manually and move on

### Tests Pass Locally but Fail in Script

This usually means:
1. Environment differences (check `.env`)
2. Database state (might need to reset test DB)
3. Timing issues (tests might be flaky)

### "Maximum iterations reached"

This means the script tried 10 times and couldn't fix all tests:
1. Review which tests are still failing
2. Increase max_iterations if making progress
3. Fix the hardest ones manually
4. Re-run the script

## Example Run

```bash
$ uv run python fix_tests_agent.py

╭─────────────────────────────────────────╮
│ Automated Test Fixer                    │
╰─────────────────────────────────────────╯

======================================================================
Iteration 1/10
======================================================================

Found 7 failing test(s)

╭───────────────────────────────────────────────────────────╮
│ Agent: Test Fixer (Iteration 1)                           │
│ Fixing: src/features/projects/components/tests/...        │
│ Test: should apply selected styles when isSelected is true│
╰───────────────────────────────────────────────────────────╯

Agent output: The test was expecting 'border-purple' but the actual...

✓ Successfully fixed: src/features/...::should apply selected styles

[... continues for each test ...]

Iteration 1 Summary:
Tests attempted: 7
Fixes successful: 5
Remaining failures: 2

======================================================================
Iteration 2/10
======================================================================

[... continues until all tests pass or max iterations ...]

╭───────────────────────────────────╮
│ 🎉 SUCCESS! All tests are now    │
│ passing!                          │
╰───────────────────────────────────╯
```

## Limitations

1. **No parallel execution**: Agents run sequentially
2. **Basic success detection**: Looks for keywords in output
3. **No learning**: Each agent starts fresh
4. **Depends on clear error messages**: Vague errors are hard to fix

## Future Enhancements

1. Add parallel agent execution for independent tests
2. Implement learning from previous fixes
3. Add test categorization (unit vs integration)
4. Improve success detection with actual test result parsing
5. Add support for backend tests (currently frontend-focused)
6. Track fix strategies that work and reuse them

## References

- [Claude Agent SDK Documentation](https://docs.claude.com/en/api/agent-sdk/python)
- [Example agents in ./tmp/claude-agent-sdk-intro/](./tmp/claude-agent-sdk-intro/)
- [Agent SDK Subagents Guide](https://docs.claude.com/en/api/agent-sdk/subagents)
