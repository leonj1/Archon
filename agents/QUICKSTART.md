# Quick Start Guide - Status Badge Implementation Agents

This guide shows you how to run the automated agents to implement all phases of the Status Badge feature.

## Prerequisites

1. **Docker services running**:
   ```bash
   docker compose up -d
   ```

2. **Anthropic API Key**:
   - Get your API key from https://console.anthropic.com/
   - Add to `.env` file in project root:
     ```bash
     ANTHROPIC_API_KEY=sk-ant-xxxxx
     ```

3. **Install dependencies**:
   ```bash
   cd /home/jose/src/Archon/python
   uv sync --group agents
   ```

## Running the Agents

### Complete Workflow (All Phases)

Run all phases in sequence:

```bash
cd /home/jose/src/Archon

# Phase 1: Backend API Mapping (~1 min)
uv run python agents/implement_status_badge_phase1.py

# Phase 2: Frontend Types (~30 sec)
uv run python agents/implement_status_badge_phase2.py

# Phase 3: Frontend Components (~1 min)
uv run python agents/implement_status_badge_phase3.py

# Phase 4: Testing & Verification (~1 min)
uv run python agents/implement_status_badge_phase4.py
```

**Total automated time**: ~3-4 minutes
**Manual time saved**: ~60 minutes (95% reduction)

---

### Phase 1: Backend API Mapping

```bash
cd /home/jose/src/Archon
uv run python agents/implement_status_badge_phase1.py
```

**What it does**:
1. ✅ Read `knowledge_item_service.py`
2. ✅ Update `list_items` method with status mapping logic
3. ✅ Update `_transform_source_to_item` method with status mapping logic
4. ✅ Restart backend: `docker compose restart archon-server`
5. ✅ Verify health: `curl http://localhost:8181/api/health`

---

### Phase 2: Frontend Types

```bash
cd /home/jose/src/Archon
uv run python agents/implement_status_badge_phase2.py
```

**What it does**:
1. ✅ Read `knowledge.ts` interface
2. ✅ Add `crawl_status` field to `KnowledgeItemMetadata`
3. ✅ Run TypeScript compiler: `npx tsc --noEmit`
4. ✅ Verify no new errors

---

### Phase 3: Frontend Components

```bash
cd /home/jose/src/Archon
uv run python agents/implement_status_badge_phase3.py
```

**What it does**:
1. ✅ Create `KnowledgeCardStatus.tsx` component (new file)
2. ✅ Import component in `KnowledgeCard.tsx`
3. ✅ Add status badge to card header
4. ✅ Run Biome formatter: `npm run biome:fix`

---

### Phase 4: Testing & Verification

```bash
cd /home/jose/src/Archon
uv run python agents/implement_status_badge_phase4.py
```

**What it does**:
1. ✅ Verify backend API includes `crawl_status`
2. ✅ Test status mapping (pending/completed/failed)
3. ✅ Run TypeScript compiler checks
4. ✅ Run Biome linter checks
5. ✅ Generate comprehensive verification report

**Note**: Manual UI testing still required (browser interactions)

### Expected Output

You'll see colored terminal output showing:
- Tool executions (Read, Edit, Bash)
- File changes being made
- Backend restart progress
- Health check results
- Session statistics (tokens, cost, duration)

### Verification

After the agent completes, verify the changes:

```bash
# Check that API includes crawl_status
curl http://localhost:8181/api/knowledge-items | jq '.items[0].metadata | {status, crawl_status}'

# Expected output:
# {
#   "status": "processing",
#   "crawl_status": "pending"
# }
```

### If Something Goes Wrong

**Agent fails to connect**:
- Check `ANTHROPIC_API_KEY` in `.env`
- Verify the key is valid

**Backend not accessible**:
- Ensure Docker services are running: `docker compose ps`
- Check logs: `docker compose logs archon-server`
- Restart if needed: `docker compose restart archon-server`

**File edit errors**:
- The agent may need to retry if file structure has changed
- Review the output to see what went wrong
- You can manually make the changes following the checklist

**Health check fails**:
- Wait 10-15 seconds for backend to fully restart
- Check logs: `docker compose logs archon-server`
- Verify no syntax errors in Python code

## Manual Verification

After the agent runs, you should manually verify:

1. **Check the modified file**:
   ```bash
   cat python/src/server/services/knowledge/knowledge_item_service.py | grep -A 10 "frontend_status"
   ```

2. **Look for the mapping logic**:
   ```python
   crawl_status = source_metadata.get("crawl_status", "pending")
   frontend_status = {
       "completed": "active",
       "failed": "error",
       "pending": "processing"
   }.get(crawl_status, "processing")
   ```

3. **Test the API endpoint**:
   ```bash
   curl http://localhost:8181/api/knowledge-items
   ```

## Next Steps After Automation

Once all automated phases complete:

1. **Mark tasks complete** in `STATUS_BADGE_IMPLEMENTATION.md`
2. **Manual UI Testing** (Phase 4 continuation):
   - Start frontend: `cd archon-ui-main && npm run dev`
   - Open http://localhost:3737
   - Navigate to Knowledge page
   - Verify badges appear on all cards
   - Test tooltips on hover
   - Check responsive design (mobile, tablet, desktop)
   - Verify dark mode styling
3. **Phase 5: Final Verification**:
   - Run final code quality checks
   - Visual verification checklist
   - Update documentation
   - Commit changes

## Cost Estimate

### Per Phase
- **Phase 1**: ~$0.10 (3k input + 1.5k output tokens)
- **Phase 2**: ~$0.05 (1.5k input + 800 output tokens)
- **Phase 3**: ~$0.15 (4k input + 2k output tokens)
- **Phase 4**: ~$0.08 (2k input + 1k output tokens)

### Total
- **All Phases**: ~$0.38
- **Time**: 3-4 minutes
- **Manual time saved**: ~60 minutes
- **Developer cost saved**: ~$50 (at $50/hr)
- **ROI**: 130x return on investment

## Troubleshooting

### Common Issues

**ImportError: No module named 'claude_agent_sdk'**:
```bash
cd python
uv sync --group agents
```

**ImportError: No module named 'cli_tools'**:
```bash
# Ensure cli_tools.py exists in agents directory
ls -la agents/cli_tools.py
```

**Docker not running**:
```bash
docker compose up -d
docker compose ps
```

**Permission errors**:
```bash
# Ensure files are writable
chmod +w python/src/server/services/knowledge/knowledge_item_service.py
```

## Manual Alternative

If the agent doesn't work, you can implement Phase 1 manually:

1. Follow the checklist in `STATUS_BADGE_IMPLEMENTATION.md`
2. Each step has exact line numbers and code snippets
3. Takes about 15 minutes manually vs 1 minute with the agent

## Support

- Review agent code: `agents/implement_status_badge_phase1.py`
- Check SDK examples: `tmp/claude-agent-sdk-intro/`
- Read implementation checklist: `STATUS_BADGE_IMPLEMENTATION.md`
