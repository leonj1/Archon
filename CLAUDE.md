# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Beta Development Guidelines

**Local-only deployment** - each user runs their own instance.

### Core Principles

- **No backwards compatibility; we follow a fix‑forward approach** — remove deprecated code immediately
- **Detailed errors over graceful failures** - we want to identify and fix issues fast
- **Break things to improve them** - beta is for rapid iteration
- **Continuous improvement** - embrace change and learn from mistakes
- **KISS** - keep it simple
- **DRY** when appropriate
- **YAGNI** — don't implement features that are not needed

### Error Handling

**Core Principle**: In beta, we need to intelligently decide when to fail hard and fast to quickly address issues, and when to allow processes to complete in critical services despite failures. Read below carefully and make intelligent decisions on a case-by-case basis.

#### When to Fail Fast and Loud (Let it Crash!)

These errors should stop execution and bubble up immediately: (except for crawling flows)

- **Service startup failures** - If credentials, database, or any service can't initialize, the system should crash with a clear error
- **Missing configuration** - Missing environment variables or invalid settings should stop the system
- **Database connection failures** - Don't hide connection issues, expose them
- **Authentication/authorization failures** - Security errors must be visible and halt the operation
- **Data corruption or validation errors** - Never silently accept bad data, Pydantic should raise
- **Critical dependencies unavailable** - If a required service is down, fail immediately
- **Invalid data that would corrupt state** - Never store zero embeddings, null foreign keys, or malformed JSON

#### When to Complete but Log Detailed Errors

These operations should continue but track and report failures clearly:

- **Batch processing** - When crawling websites or processing documents, complete what you can and report detailed failures for each item
- **Background tasks** - Embedding generation, async jobs should finish the queue but log failures
- **WebSocket events** - Don't crash on a single event failure, log it and continue serving other clients
- **Optional features** - If projects/tasks are disabled, log and skip rather than crash
- **External API calls** - Retry with exponential backoff, then fail with a clear message about what service failed and why

#### Critical Nuance: Never Accept Corrupted Data

When a process should continue despite failures, it must **skip the failed item entirely** rather than storing corrupted data

#### Error Message Guidelines

- Include context about what was being attempted when the error occurred
- Preserve full stack traces with `exc_info=True` in Python logging
- Use specific exception types, not generic Exception catching
- Include relevant IDs, URLs, or data that helps debug the issue
- Never return None/null to indicate failure - raise an exception with details
- For batch operations, always report both success count and detailed failure list

### Code Quality

- Remove dead code immediately rather than maintaining it - no backward compatibility or legacy functions
- Avoid backward compatibility mappings or legacy function wrappers
- Fix forward
- Focus on user experience and feature completeness
- When updating code, don't reference what is changing (avoid keywords like SIMPLIFIED, ENHANCED, LEGACY, CHANGED, REMOVED), instead focus on comments that document just the functionality of the code
- When commenting on code in the codebase, only comment on the functionality and reasoning behind the code. Refrain from speaking to Archon being in "beta" or referencing anything else that comes from these global rules.

## Development Commands

### Frontend (archon-ui-main/)

```bash
npm run dev              # Start development server on port 3737
npm run build            # Build for production
npm run lint             # Run ESLint on legacy code (excludes /features)
npm run lint:files path/to/file.tsx  # Lint specific files

# Biome for /src/features directory only
npm run biome            # Check features directory
npm run biome:fix        # Auto-fix issues
npm run biome:format     # Format code (120 char lines)
npm run biome:ai         # Machine-readable JSON output for AI
npm run biome:ai-fix     # Auto-fix with JSON output

# Testing
npm run test             # Run all tests in watch mode
npm run test:ui          # Run with Vitest UI interface
npm run test:coverage:stream  # Run once with streaming output
vitest run src/features/projects  # Test specific directory

# TypeScript
npx tsc --noEmit         # Check all TypeScript errors
npx tsc --noEmit 2>&1 | grep "src/features"  # Check features only
```

### Backend (python/)

```bash
# Using uv package manager (preferred)
uv sync --group all      # Install all dependencies
uv run python -m src.server.main  # Run server locally on 8181
uv run pytest            # Run all tests
uv run pytest tests/test_api_essentials.py -v  # Run specific test
uv run ruff check        # Run linter
uv run ruff check --fix  # Auto-fix linting issues
uv run mypy src/         # Type check

# Docker operations
docker compose up --build -d       # Start all services
docker compose --profile backend up -d  # Backend only (for hybrid dev)
docker compose logs -f archon-server   # View server logs
docker compose logs -f archon-mcp      # View MCP server logs
docker compose restart archon-server   # Restart after code changes
docker compose down      # Stop all services
docker compose down -v   # Stop and remove volumes
```

### Quick Workflows

```bash
# Hybrid development (recommended) - backend in Docker, frontend local
make dev                 # Or manually: docker compose --profile backend up -d && cd archon-ui-main && npm run dev

# Full Docker mode
make dev-docker          # Or: docker compose up --build -d

# Run linters before committing
make lint                # Runs both frontend and backend linters
make lint-fe             # Frontend only (ESLint + Biome)
make lint-be             # Backend only (Ruff + MyPy)

# Testing
make test                # Run all tests
make test-fe             # Frontend tests only
make test-be             # Backend tests only
```

## Architecture Overview

@PRPs/ai_docs/ARCHITECTURE.md

#### TanStack Query Implementation

For architecture and file references:
@PRPs/ai_docs/DATA_FETCHING_ARCHITECTURE.md

For code patterns and examples:
@PRPs/ai_docs/QUERY_PATTERNS.md

#### Service Layer Pattern

See implementation examples:
- API routes: `python/src/server/api_routes/projects_api.py`
- Service layer: `python/src/server/services/project_service.py`
- Pattern: API Route → Service → Database

#### Error Handling Patterns

See implementation examples:
- Custom exceptions: `python/src/server/exceptions.py`
- Exception handlers: `python/src/server/main.py` (search for @app.exception_handler)
- Service error handling: `python/src/server/services/` (various services)

## ETag Implementation

@PRPs/ai_docs/ETAG_IMPLEMENTATION.md

## Database Schema

Key tables in Supabase:

- `sources` - Crawled websites and uploaded documents
  - Stores metadata, crawl status, and configuration
- `documents` - Processed document chunks with embeddings
  - Text chunks with vector embeddings for semantic search
- `projects` - Project management (optional feature)
  - Contains features array, documents, and metadata
- `tasks` - Task tracking linked to projects
  - Status: todo, doing, review, done
  - Assignee: User, Archon, AI IDE Agent
- `code_examples` - Extracted code snippets
  - Language, summary, and relevance metadata

## API Naming Conventions

@PRPs/ai_docs/API_NAMING_CONVENTIONS.md

Use database values directly (no FE mapping; type‑safe end‑to‑end from BE upward):

## Environment Variables

Required in `.env`:

```bash
SUPABASE_URL=https://your-project.supabase.co  # Or http://host.docker.internal:8000 for local
SUPABASE_SERVICE_KEY=your-service-key-here      # Use legacy key format for cloud Supabase
```

Optional variables and full configuration:
See `python/.env.example` for complete list

## Common Development Tasks

### Add a new API endpoint

1. Create route handler in `python/src/server/api_routes/`
2. Add service logic in `python/src/server/services/`
3. Include router in `python/src/server/main.py`
4. Update frontend service in `archon-ui-main/src/features/[feature]/services/`

### Add a new UI component in features directory

**IMPORTANT**: Review UI design standards in `@PRPs/ai_docs/UI_STANDARDS.md` before creating UI components.

1. Use Radix UI primitives from `src/features/ui/primitives/`
2. Create component in relevant feature folder under `src/features/[feature]/components/`
3. Define types in `src/features/[feature]/types/`
4. Use TanStack Query hook from `src/features/[feature]/hooks/`
5. Apply Tron-inspired glassmorphism styling with Tailwind
6. Follow responsive design patterns (mobile-first with breakpoints)
7. Ensure no dynamic Tailwind class construction (see UI_STANDARDS.md Section 2)

### Add or modify MCP tools

1. MCP tools are in `python/src/mcp_server/features/[feature]/[feature]_tools.py`
2. Follow the pattern:
   - `find_[resource]` - Handles list, search, and get single item operations
   - `manage_[resource]` - Handles create, update, delete with an "action" parameter
3. Register tools in the feature's `__init__.py` file

### Debug MCP connection issues

1. Check MCP health: `curl http://localhost:8051/health`
2. View MCP logs: `docker compose logs archon-mcp`
3. Test tool execution via UI MCP page
4. Verify Supabase connection and credentials

### Fix TypeScript/Linting Issues

```bash
# TypeScript errors in features
npx tsc --noEmit 2>&1 | grep "src/features"

# Biome auto-fix for features
npm run biome:fix

# ESLint for legacy code
npm run lint:files src/components/SomeComponent.tsx
```

## Code Quality Standards

### Frontend

- **TypeScript**: Strict mode enabled, no implicit any
- **Biome** for `/src/features/`: 120 char lines, double quotes, trailing commas
- **ESLint** for legacy code: Standard React rules
- **Testing**: Vitest with React Testing Library

### Backend

- **Python 3.12** with 120 character line length
- **Ruff** for linting - checks for errors, warnings, unused imports
- **Mypy** for type checking - ensures type safety
- **Pytest** for testing with async support

## MCP Tools Available

When connected to Claude/Cursor/Windsurf, the following tools are available:

### Knowledge Base Tools

- `archon:rag_search_knowledge_base` - Search knowledge base for relevant content
- `archon:rag_search_code_examples` - Find code snippets in the knowledge base
- `archon:rag_get_available_sources` - List available knowledge sources
- `archon:rag_list_pages_for_source` - List all pages for a given source (browse documentation structure)
- `archon:rag_read_full_page` - Retrieve full page content by page_id or URL

### Project Management

- `archon:find_projects` - Find all projects, search, or get specific project (by project_id)
- `archon:manage_project` - Manage projects with actions: "create", "update", "delete"

### Task Management

- `archon:find_tasks` - Find tasks with search, filters, or get specific task (by task_id)
- `archon:manage_task` - Manage tasks with actions: "create", "update", "delete"

### Document Management

- `archon:find_documents` - Find documents, search, or get specific document (by document_id)
- `archon:manage_document` - Manage documents with actions: "create", "update", "delete"

### Version Control

- `archon:find_versions` - Find version history or get specific version
- `archon:manage_version` - Manage versions with actions: "create", "restore"

## MCP Usage Analytics

### Overview

The MCP Usage Analytics feature provides comprehensive insights into MCP server usage patterns, helping you understand how AI IDEs interact with Archon's knowledge base and project management tools. Track usage metrics, monitor performance, and identify the most valuable tools with an interactive dashboard featuring time-series visualizations and real-time statistics.

### Key Features

- **Time-Series Data Storage**: 180-day retention of usage events with automatic cleanup
- **Hourly and Daily Aggregations**: Pre-computed materialized views for fast query performance
- **Interactive Bar Charts**: Visual representation of usage patterns with hover tooltips
- **Real-Time Metrics**: Summary statistics for the last 24 hours including call counts and success rates
- **Category Filtering**: Filter analytics by tool category (RAG, Project, Task, Document, Version, Feature)
- **Tool Breakdown**: Identify most-used MCP tools with sortable statistics
- **Performance Monitoring**: Track average response times and error rates

### API Endpoints

All analytics endpoints are available under `/api/mcp/analytics`:

**GET /api/mcp/analytics/hourly**
- Query hourly usage data with time range filtering
- Query parameters:
  - `hours` (1-168): Number of hours to query (default: 24)
  - `tool_category` (optional): Filter by category (rag, project, task, document, version, feature)
  - `tool_name` (optional): Filter by specific tool name
- Response: Array of hourly aggregations with call counts, error counts, response times, unique sessions
- ETag support for efficient caching

**GET /api/mcp/analytics/daily**
- Query daily usage aggregations for longer time periods
- Query parameters:
  - `days` (1-180): Number of days to query (default: 7)
  - `tool_category` (optional): Filter by category
- Response: Array of daily aggregations with summarized metrics
- ETag support for efficient caching

**GET /api/mcp/analytics/summary**
- Get summary statistics for the last 24 hours
- Response includes:
  - `total_calls`: Total number of MCP tool invocations
  - `success_rate`: Percentage of successful calls
  - `top_tools`: Array of most-used tools with call counts
  - `by_category`: Call count breakdown by category

**POST /api/mcp/analytics/refresh-views**
- Manually trigger refresh of materialized views
- Returns status of view refresh operations
- Useful for ensuring up-to-date data when automatic refresh is delayed

### Usage

1. Navigate to **Settings** in the Archon UI
2. Scroll to the **MCP Usage Analytics** section
3. Expand the collapsible card to view the dashboard
4. Use the time range selector to choose between 24h, 48h, or 7 days
5. Filter by tool category to focus on specific functionality
6. Hover over chart bars for detailed information
7. Review the Top Tools table to identify most-used capabilities

### Privacy

All usage data is stored **locally in your Supabase instance**. No analytics data is transmitted to external services or third parties. The tracking system records:
- Tool invocations (tool name, category, timestamp)
- Response times and success/failure status
- Session identifiers (for unique user counting)
- No sensitive data or query parameters are logged

### Technical Details

#### Database Tables

**archon_mcp_usage_events**
- Primary storage table for raw usage events
- Columns: event_id, tool_name, tool_category, status, response_time_ms, session_id, created_at
- Automatic cleanup policy: Events older than 180 days are automatically removed
- Indexed on: tool_name, tool_category, status, created_at for fast queries

**Materialized Views**
- `archon_mcp_usage_hourly`: Hourly aggregations for recent data (last 7 days)
- `archon_mcp_usage_daily`: Daily aggregations for historical data (last 180 days)
- Auto-refresh every 15 minutes via scheduled function
- Manual refresh available via API endpoint

#### Tracking Middleware

**Location**: `python/src/mcp_server/middleware/usage_tracking.py`

Usage tracking is implemented as a decorator pattern applied to all MCP tools:
- Automatically tracks tool invocations, success/failure, and response times
- Minimal overhead (< 10ms per call)
- Non-blocking: tracking failures do not affect tool execution
- Integrated into all 14 MCP tools across RAG, Project, Task, Document, Version, and Feature categories

#### Frontend Implementation

**Service**: `archon-ui-main/src/features/mcp/services/mcpAnalyticsService.ts`
- TypeScript service wrapping analytics API endpoints
- Type-safe request/response handling

**Hooks**: `archon-ui-main/src/features/mcp/hooks/useMcpAnalytics.ts`
- React Query hooks for data fetching: `useMcpHourlyUsage`, `useMcpDailyUsage`, `useMcpUsageSummary`
- Smart caching with 5-second stale time for frequently changing data
- Automatic refetching and cache invalidation

**Component**: `archon-ui-main/src/features/mcp/components/MCPUsageAnalytics.tsx`
- Interactive dashboard with Recharts visualization
- Summary cards, filters, bar chart, and top tools table
- Responsive design with mobile support

### Performance Characteristics

- **API Response Times**: < 500ms for typical queries (95th percentile)
- **Tracking Overhead**: < 10ms per MCP tool invocation
- **Chart Render Time**: < 200ms for up to 168 data points
- **Cache Hit Rate**: ~70% bandwidth reduction via ETag caching
- **Materialized View Refresh**: Completes in < 1 second for typical datasets

### Configuration Options

**Environment Variables**
- No additional configuration required
- Uses existing `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`

**Database Settings**
- Event retention: 180 days (configurable in migration SQL)
- Materialized view refresh interval: 15 minutes (configurable in refresh function)
- Automatic cleanup enabled by default

**Frontend Settings**
- Time range options: 24h, 48h, 7 days (configurable in component)
- Stale time: 5 seconds for real-time data (configurable in hooks)
- Chart data aggregation: Automatic grouping by hour/day

### Troubleshooting

**Analytics not showing data**
1. Verify database migration has been run: Check for `archon_mcp_usage_events` table in Supabase
2. Ensure MCP tools are being invoked: Check MCP server logs
3. Manually refresh materialized views: POST to `/api/mcp/analytics/refresh-views`
4. Check browser console for API errors

**Slow query performance**
1. Verify database indexes exist: Run migration SQL to recreate indexes
2. Check materialized view freshness: Review `last_refresh` timestamp
3. Reduce time range: Query smaller date ranges (24h instead of 7d)

**Missing recent data**
1. Wait for materialized view refresh (occurs every 15 minutes)
2. Manually trigger refresh via API endpoint
3. Check raw events table for recent entries

## Important Notes

- Projects feature is optional - toggle in Settings UI
- TanStack Query handles all data fetching; smart HTTP polling is used where appropriate (no WebSockets)
- Frontend uses Vite proxy for API calls in development
- Python backend uses `uv` for dependency management
- Docker Compose handles service orchestration
- TanStack Query for all data fetching - NO PROP DRILLING
- Vertical slice architecture in `/features` - features own their sub-features
