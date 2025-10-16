# Archon AI Agents

This directory contains autonomous AI agents built with the Claude Agent SDK to automate development tasks.

## Status Badge Implementation Agents

These agents implement the Status Badge feature from `@STATUS_BADGE_IMPLEMENTATION.md`:

### Phase 1: Backend API Mapping
**Script**: `implement_status_badge_phase1.py`

Automates backend changes:
- Updates `knowledge_item_service.py` to map `crawl_status` to frontend `status`
- Modifies `list_items` method
- Modifies `_transform_source_to_item` method
- Restarts backend and verifies health

**Usage**:
```bash
cd /home/jose/src/Archon
uv run python agents/implement_status_badge_phase1.py
```

**Requirements**:
- `ANTHROPIC_API_KEY` environment variable
- Docker services running
- Backend accessible on localhost:8181

### Phase 2: Frontend Types
**Script**: `implement_status_badge_phase2.py`

Automates frontend type changes:
- Updates `KnowledgeItemMetadata` interface in `knowledge.ts`
- Adds `crawl_status` field with proper TypeScript types
- Runs TypeScript compiler to verify no errors

**Usage**:
```bash
cd /home/jose/src/Archon
uv run python agents/implement_status_badge_phase2.py
```

### Phase 3: Frontend Components
**Script**: `implement_status_badge_phase3.py`

Automates component creation and integration:
- Creates `KnowledgeCardStatus.tsx` component
- Imports component in `KnowledgeCard.tsx`
- Adds status badge to card header with proper props
- Runs Biome formatter for code quality

**Usage**:
```bash
cd /home/jose/src/Archon
uv run python agents/implement_status_badge_phase3.py
```

### Phase 4: Testing & Verification
**Script**: `implement_status_badge_phase4.py`

Automates testing and verification:
- Verifies backend API changes and status mapping
- Runs TypeScript compiler checks
- Runs Biome linter checks
- Generates comprehensive verification report
- Identifies issues and provides fixes

**Usage**:
```bash
cd /home/jose/src/Archon
uv run python agents/implement_status_badge_phase4.py
```

**Note**: Manual UI testing still required (browser interactions)

## Dependencies

Install the Claude Agent SDK:
```bash
uv add claude-agent-sdk rich python-dotenv nest-asyncio
```

Or using pip:
```bash
pip install claude-agent-sdk rich python-dotenv nest-asyncio
```

## Environment Variables

Create a `.env` file in the project root:
```bash
ANTHROPIC_API_KEY=your_api_key_here
```

## How It Works

1. Each agent uses the Claude Agent SDK to interact with Claude Code
2. Agents have access to file editing, bash commands, and code analysis tools
3. The SDK handles conversation state and tool execution
4. Rich library provides beautiful terminal output

## Best Practices

- Run agents from the project root: `/home/jose/src/Archon`
- Review changes before committing
- Check agent output for errors
- Verify health checks pass after backend changes
- Run TypeScript checks after frontend changes

## Extending Agents

To create a new agent:

1. Copy an existing agent script as a template
2. Define the task in the implementation prompt
3. Configure allowed/disallowed tools
4. Add error handling and verification steps
5. Document usage in this README

## Troubleshooting

**Import errors**:
- Ensure `cli_tools.py` is in the agents directory
- Check that all dependencies are installed

**API key errors**:
- Verify `.env` file exists in project root
- Check `ANTHROPIC_API_KEY` is set correctly

**Tool execution errors**:
- Ensure Docker services are running
- Check file paths are absolute
- Verify permissions for file operations

## References

- [Claude Agent SDK Documentation](https://docs.claude.com/en/api/agent-sdk/python)
- [SDK Examples](../tmp/claude-agent-sdk-intro/)
- [Status Badge Checklist](../STATUS_BADGE_IMPLEMENTATION.md)
