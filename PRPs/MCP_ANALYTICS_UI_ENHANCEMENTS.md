# MCP Analytics UI Enhancements - Knowledge Base Tracking

**Status**: Draft
**Created**: 2025-10-13
**Priority**: Medium
**Complexity**: Low-Medium

## Overview

Enhance the MCP Usage Analytics dashboard to display knowledge base usage patterns, popular queries, and performance metrics that are already being tracked but not yet visualized in the UI.

## Current State

### What's Already Tracked (Backend)
The `archon_mcp_usage_events` table captures:
- ✅ `source_id` - Which knowledge base was queried
- ✅ `query_text` - Search query (truncated to 500 chars)
- ✅ `match_count` - Number of results requested
- ✅ `response_time_ms` - Query performance
- ✅ `tool_name` - Which MCP tool was used
- ✅ `tool_category` - Tool category
- ✅ `session_id` - User session identifier
- ✅ `client_type` - AI IDE type (Claude Code, Cursor, etc.)

### What's Currently Displayed (Frontend)
**MCPUsageAnalytics.tsx** shows:
- Total calls (24h)
- Success rate
- Failed calls count
- Bar chart: Usage over time
- Table: Top 10 most-used tools
- Filters: Time range (24h/48h/7d), Category

### What's Missing
- ❌ Knowledge base usage breakdown
- ❌ Popular search queries
- ❌ Average response times per tool
- ❌ Client type distribution (Claude Code vs Cursor vs Windsurf)
- ❌ Performance trends
- ❌ Query patterns analysis

## Proposed Enhancements

### Phase 1: Knowledge Base Tracking (High Priority)

#### 1.1 Add Knowledge Base Usage Card
**Location**: After summary cards, before filters

**Design**:
```
┌─────────────────────────────────────────────┐
│ 📚 Knowledge Bases Queried (24h)            │
├─────────────────────────────────────────────┤
│ Supabase Docs          127 queries  ████░░ │
│ Anthropic AI           89 queries   ███░░░ │
│ Python Docs            45 queries   ██░░░░ │
│ React Documentation    23 queries   █░░░░░ │
│ Custom Knowledge       12 queries   ░░░░░░ │
└─────────────────────────────────────────────┘
```

**Implementation**:
- New component: `KnowledgeBaseUsageCard.tsx`
- Fetch data from existing `/summary` endpoint (already includes source breakdowns)
- Display top 5 sources with horizontal bar visualization
- Show query count and percentage of total

#### 1.2 Backend API Enhancement
**Endpoint**: `GET /api/mcp/analytics/knowledge-bases`

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "source_id": "src_abc123",
      "source_name": "Supabase Documentation",
      "query_count": 127,
      "unique_queries": 45,
      "avg_response_time_ms": 234,
      "success_rate": 98.4,
      "popular_queries": [
        "vector search",
        "authentication",
        "realtime subscriptions"
      ]
    }
  ],
  "period": {
    "hours": 24,
    "start_time": "2025-10-12T13:00:00Z",
    "end_time": "2025-10-13T13:00:00Z"
  }
}
```

**SQL Query** (for SQLite):
```sql
SELECT
  source_id,
  COUNT(*) as query_count,
  COUNT(DISTINCT query_text) as unique_queries,
  AVG(response_time_ms) as avg_response_time,
  ROUND(AVG(CASE WHEN success = 1 THEN 100.0 ELSE 0.0 END), 1) as success_rate
FROM archon_mcp_usage_events
WHERE
  timestamp >= datetime('now', '-24 hours')
  AND source_id IS NOT NULL
GROUP BY source_id
ORDER BY query_count DESC
LIMIT 10
```

### Phase 2: Popular Queries Display (Medium Priority)

#### 2.1 Add Popular Queries Card
**Location**: Below knowledge base usage card

**Design**:
```
┌─────────────────────────────────────────────┐
│ 🔍 Popular Search Queries (24h)             │
├─────────────────────────────────────────────┤
│ 1. "vector search pgvector"        23 times │
│ 2. "authentication JWT"            18 times │
│ 3. "React hooks useState"          15 times │
│ 4. "FastAPI middleware"            12 times │
│ 5. "database migrations"            9 times │
└─────────────────────────────────────────────┘
```

**Implementation**:
- Component: `PopularQueriesCard.tsx`
- Aggregates `query_text` column from events
- Shows top 5 queries with count
- Click to filter analytics by that query

#### 2.2 Backend API Enhancement
**Endpoint**: `GET /api/mcp/analytics/popular-queries?limit=10&hours=24`

**SQL Query**:
```sql
SELECT
  query_text,
  COUNT(*) as query_count,
  tool_name,
  AVG(response_time_ms) as avg_response_time
FROM archon_mcp_usage_events
WHERE
  timestamp >= datetime('now', '-24 hours')
  AND query_text IS NOT NULL
  AND query_text != ''
GROUP BY query_text
ORDER BY query_count DESC
LIMIT 10
```

### Phase 3: Performance Metrics (Medium Priority)

#### 3.1 Add Performance Overview Card
**Location**: In summary cards row (expand to 4 cards)

**Design**:
```
┌─────────────────────────────────┐
│ ⚡ Avg Response Time             │
│                                 │
│        234 ms                   │
│                                 │
│ 📊 95th percentile: 512 ms      │
└─────────────────────────────────┘
```

**Implementation**:
- Update summary cards grid to `grid-cols-1 md:grid-cols-4`
- Calculate average and P95 response times
- Color-code based on performance thresholds:
  - Green: < 300ms
  - Yellow: 300-1000ms
  - Red: > 1000ms

#### 3.2 Backend API Enhancement
Update `/summary` endpoint to include:
```json
"performance": {
  "avg_response_time_ms": 234,
  "p95_response_time_ms": 512,
  "p99_response_time_ms": 1024,
  "slowest_tool": {
    "name": "rag_search_knowledge_base",
    "avg_time_ms": 456
  }
}
```

### Phase 4: Client Type Distribution (Low Priority)

#### 4.1 Add Client Distribution Pie Chart
**Location**: New card below bar chart

**Design**:
```
┌─────────────────────────────────────────────┐
│ 💻 Client Distribution                      │
├─────────────────────────────────────────────┤
│                 [PIE CHART]                 │
│                                             │
│ • Claude Code    65% (234 calls)            │
│ • Cursor         28% (101 calls)            │
│ • Windsurf        7% (25 calls)             │
└─────────────────────────────────────────────┘
```

**Implementation**:
- Component: `ClientDistributionCard.tsx`
- Uses Recharts PieChart
- Shows client type breakdown
- Useful for understanding which AI IDEs are most popular

## File Structure

### New Files to Create
```
archon-ui-main/src/features/mcp/
├── components/
│   ├── MCPUsageAnalytics.tsx (existing - update)
│   ├── KnowledgeBaseUsageCard.tsx (new)
│   ├── PopularQueriesCard.tsx (new)
│   ├── PerformanceMetricsCard.tsx (new)
│   └── ClientDistributionCard.tsx (new)
├── hooks/
│   ├── useMcpAnalytics.ts (existing - update)
│   └── useMcpKnowledgeBaseAnalytics.ts (new)
├── services/
│   └── mcpAnalyticsService.ts (existing - update)
└── types/
    └── analytics.ts (new - shared types)

python/src/server/api_routes/
└── mcp_analytics_api.py (existing - update)
```

### Modified Files
```
archon-ui-main/src/features/mcp/components/MCPUsageAnalytics.tsx
archon-ui-main/src/features/mcp/hooks/useMcpAnalytics.ts
archon-ui-main/src/features/mcp/services/mcpAnalyticsService.ts
python/src/server/api_routes/mcp_analytics_api.py
```

## Implementation Steps

### Step 1: Backend API Extensions (2-3 hours)
1. Add `/api/mcp/analytics/knowledge-bases` endpoint
2. Add `/api/mcp/analytics/popular-queries` endpoint
3. Enhance `/api/mcp/analytics/summary` with performance metrics
4. Add query to join source_id with sources table for source names
5. Write tests for new endpoints

**Files to modify**:
- `python/src/server/api_routes/mcp_analytics_api.py`
- `python/tests/server/api_routes/test_mcp_analytics_api.py`

### Step 2: Frontend Types & Services (1 hour)
1. Create `analytics.ts` with shared TypeScript types
2. Update `mcpAnalyticsService.ts` with new API calls
3. Create React Query hooks for new endpoints

**Files to create/modify**:
- `archon-ui-main/src/features/mcp/types/analytics.ts` (new)
- `archon-ui-main/src/features/mcp/services/mcpAnalyticsService.ts`
- `archon-ui-main/src/features/mcp/hooks/useMcpKnowledgeBaseAnalytics.ts` (new)

### Step 3: Knowledge Base Usage Component (2 hours)
1. Create `KnowledgeBaseUsageCard.tsx`
2. Implement horizontal bar chart visualization
3. Add tooltip with detailed metrics
4. Handle empty state

**Files to create**:
- `archon-ui-main/src/features/mcp/components/KnowledgeBaseUsageCard.tsx`

### Step 4: Popular Queries Component (1-2 hours)
1. Create `PopularQueriesCard.tsx`
2. Display top queries with counts
3. Add click-to-filter functionality
4. Truncate long queries with tooltip

**Files to create**:
- `archon-ui-main/src/features/mcp/components/PopularQueriesCard.tsx`

### Step 5: Performance Metrics Component (1-2 hours)
1. Create `PerformanceMetricsCard.tsx`
2. Add to summary cards row
3. Implement color-coded performance indicators
4. Add trend arrows (faster/slower than previous period)

**Files to create**:
- `archon-ui-main/src/features/mcp/components/PerformanceMetricsCard.tsx`

### Step 6: Main Dashboard Integration (1 hour)
1. Update `MCPUsageAnalytics.tsx` to include new components
2. Adjust layout for new cards
3. Ensure responsive design
4. Test all interactions

**Files to modify**:
- `archon-ui-main/src/features/mcp/components/MCPUsageAnalytics.tsx`

### Step 7: Testing & Documentation (1-2 hours)
1. Write component tests
2. Test API endpoints with sample data
3. Update CLAUDE.md with new analytics features
4. Test responsive layout on mobile/tablet

**Files to create/modify**:
- Component test files in `tests/` subdirectories
- Update `CLAUDE.md`

## Database Queries

### Get Source Names
Currently, `source_id` is a foreign key but we need to join with the `sources` table to get human-readable names:

```sql
SELECT
  e.source_id,
  COALESCE(s.name, s.base_url, e.source_id) as source_name,
  COUNT(*) as query_count
FROM archon_mcp_usage_events e
LEFT JOIN sources s ON e.source_id = s.id
WHERE e.timestamp >= datetime('now', '-24 hours')
  AND e.source_id IS NOT NULL
GROUP BY e.source_id, source_name
ORDER BY query_count DESC
LIMIT 10
```

### Calculate Performance Percentiles
```sql
WITH ranked_times AS (
  SELECT
    response_time_ms,
    ROW_NUMBER() OVER (ORDER BY response_time_ms) as row_num,
    COUNT(*) OVER () as total_count
  FROM archon_mcp_usage_events
  WHERE timestamp >= datetime('now', '-24 hours')
    AND success = 1
)
SELECT
  AVG(CASE WHEN row_num <= total_count * 0.95 THEN response_time_ms END) as p95,
  AVG(CASE WHEN row_num <= total_count * 0.99 THEN response_time_ms END) as p99
FROM ranked_times
```

## UI/UX Considerations

### Visual Hierarchy
1. **Summary cards** (top) - Quick metrics at a glance
2. **Knowledge base usage** (prominent) - Answers "what am I searching?"
3. **Filters** - Control time range and category
4. **Time-series chart** - Historical trends
5. **Popular queries** - Query patterns
6. **Top tools table** - Tool usage breakdown
7. **Client distribution** (optional) - AI IDE breakdown

### Color Coding
- **Blue** - General metrics, total calls
- **Green** - Success rates, performance
- **Red** - Errors, slow queries
- **Purple** - Knowledge base related
- **Cyan** - Query related

### Responsive Design
- Summary cards: 1 column (mobile), 3-4 columns (desktop)
- Knowledge base bars: Stack on mobile, horizontal on desktop
- Charts: Full width, adjust height for mobile

### Empty States
- "No knowledge bases queried yet" - Before any RAG searches
- "No popular queries" - Before meaningful query data
- Link to Knowledge page with CTA: "Add a knowledge source"

## Testing Strategy

### Backend Tests
```python
# Test knowledge base analytics endpoint
def test_get_knowledge_base_analytics(client):
    response = client.get("/api/mcp/analytics/knowledge-bases?hours=24")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "data" in data
    assert isinstance(data["data"], list)

# Test popular queries endpoint
def test_get_popular_queries(client):
    response = client.get("/api/mcp/analytics/popular-queries?limit=10")
    assert response.status_code == 200
```

### Frontend Tests
```typescript
// Test knowledge base card rendering
describe("KnowledgeBaseUsageCard", () => {
  it("renders knowledge base list", () => {
    const mockData = [
      { source_name: "Test KB", query_count: 10 }
    ];
    render(<KnowledgeBaseUsageCard data={mockData} />);
    expect(screen.getByText("Test KB")).toBeInTheDocument();
  });

  it("shows empty state when no data", () => {
    render(<KnowledgeBaseUsageCard data={[]} />);
    expect(screen.getByText(/no knowledge bases/i)).toBeInTheDocument();
  });
});
```

## Migration Path

### Phase 1 (MVP) - 4-6 hours
- Backend: Knowledge base analytics endpoint
- Frontend: Knowledge Base Usage Card
- Integration: Add to main dashboard

**Deliverable**: Users can see which knowledge bases are queried most

### Phase 2 (Enhanced) - 3-4 hours
- Backend: Popular queries endpoint
- Frontend: Popular Queries Card
- Integration: Click-to-filter functionality

**Deliverable**: Users can see popular search queries

### Phase 3 (Complete) - 3-4 hours
- Backend: Performance metrics in summary
- Frontend: Performance card + Client distribution
- Polish: Responsive design, empty states

**Deliverable**: Complete analytics dashboard with all metrics

## Success Metrics

- ✅ Users can identify most-queried knowledge bases
- ✅ Users can see popular search patterns
- ✅ Users can monitor query performance
- ✅ Dashboard loads in < 500ms
- ✅ All charts responsive on mobile
- ✅ Empty states guide users to add knowledge

## Future Enhancements

### Advanced Features (Future)
- Export analytics to CSV
- Date range picker (custom dates)
- Query performance alerts
- Knowledge base comparison view
- Search query autocomplete suggestions
- Session replay (view user's search journey)
- A/B testing for different RAG configurations

### Machine Learning Insights
- Query intent classification
- Duplicate query detection
- Recommendation: "Users who searched X also searched Y"
- Anomaly detection (unusual query patterns)

## Appendix

### Sample Data for Testing

```python
# Insert sample MCP usage data
import sqlite3
import uuid
from datetime import datetime, timedelta

conn = sqlite3.connect('/data/archon.db')

sources = [
    ('src_supabase', 'Supabase Documentation'),
    ('src_anthropic', 'Anthropic AI'),
    ('src_python', 'Python Official Docs'),
]

queries = [
    'vector search pgvector',
    'authentication JWT tokens',
    'React hooks useState',
    'FastAPI middleware',
    'database migrations',
]

# Insert 100 sample events
for i in range(100):
    source = sources[i % len(sources)]
    query = queries[i % len(queries)]

    conn.execute('''
        INSERT INTO archon_mcp_usage_events
        (id, tool_name, tool_category, source_id, query_text,
         response_time_ms, success, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        str(uuid.uuid4()),
        'rag_search_knowledge_base',
        'rag',
        source[0],
        query,
        200 + (i * 10),
        1,
        (datetime.now() - timedelta(hours=i % 24)).isoformat()
    ))

conn.commit()
```

### API Response Examples

**Knowledge Base Analytics**:
```json
{
  "success": true,
  "data": [
    {
      "source_id": "src_abc123",
      "source_name": "Supabase Documentation",
      "query_count": 127,
      "unique_queries": 45,
      "avg_response_time_ms": 234,
      "success_rate": 98.4,
      "percentage_of_total": 42.5
    }
  ],
  "total_queries": 299
}
```

**Popular Queries**:
```json
{
  "success": true,
  "data": [
    {
      "query_text": "vector search pgvector",
      "query_count": 23,
      "avg_response_time_ms": 245,
      "success_rate": 100.0,
      "most_used_source": "Supabase Documentation"
    }
  ]
}
```

---

**Estimated Total Time**: 12-18 hours (MVP in 4-6 hours)
**Dependencies**: Existing MCP analytics infrastructure
**Risk Level**: Low (additive changes, no breaking modifications)
