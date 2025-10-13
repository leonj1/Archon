# MCP Analytics Dashboard - UI Mockup

**Current State vs Proposed Enhancement**

---

## Current Dashboard Layout (Existing)

```
┌─────────────────────────────────────────────────────────────────────┐
│ MCP Usage Analytics                                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│ │  Total      │  │  Success    │  │  Failed     │                 │
│ │  Calls      │  │  Rate       │  │  Calls      │                 │
│ │  (24h)      │  │             │  │             │                 │
│ │             │  │             │  │             │                 │
│ │    127      │  │   98.4%     │  │     2       │                 │
│ └─────────────┘  └─────────────┘  └─────────────┘                 │
│                                                                     │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│ │ Time Range  │  │ Category    │  │ Refresh     │                 │
│ │ [24 hours▼] │  │ [All     ▼] │  │   🔄        │                 │
│ └─────────────┘  └─────────────┘  └─────────────┘                 │
│                                                                     │
│ ┌──────────────────── Usage Over Time ─────────────────────────┐   │
│ │                                                               │   │
│ │    [BAR CHART: Hourly usage with total calls and errors]     │   │
│ │                                                               │   │
│ │    120│                                                       │   │
│ │     90│  ██                                                   │   │
│ │     60│  ██  ██                                               │   │
│ │     30│  ██  ██  ██                                           │   │
│ │      0│──────────────────────────────────────────────────────│   │
│ │       Jan 12  Jan 12  Jan 12  Jan 12                         │   │
│ │       10am    2pm     6pm     10pm                            │   │
│ └───────────────────────────────────────────────────────────────┘   │
│                                                                     │
│ ┌────────────── Top 10 Most Used Tools ──────────────┐             │
│ │ Tool Name                          Call Count      │             │
│ │ ─────────────────────────────────────────────────  │             │
│ │ 1. rag_search_knowledge_base            87         │             │
│ │ 2. find_projects                        23         │             │
│ │ 3. find_tasks                           12         │             │
│ │ 4. manage_project                        5         │             │
│ └─────────────────────────────────────────────────────┘             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Enhanced Dashboard Layout (Proposed)

```
┌─────────────────────────────────────────────────────────────────────┐
│ MCP Usage Analytics                                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐ ← NEW!         │
│ │  Total  │  │ Success │  │ Failed  │  │  Avg    │                 │
│ │  Calls  │  │  Rate   │  │  Calls  │  │Response │                 │
│ │  (24h)  │  │         │  │         │  │  Time   │                 │
│ │         │  │         │  │         │  │         │                 │
│ │   127   │  │  98.4%  │  │    2    │  │ 234 ms  │                 │
│ └─────────┘  └─────────┘  └─────────┘  └─────────┘                 │
│                                                                     │
│ ┌──────────────── 📚 Knowledge Bases Queried (24h) ──────────────┐ │
│ │                                                                 │ │
│ │ Supabase Documentation           45 queries  ████████░░  73%   │ │
│ │ Anthropic AI                     23 queries  ████░░░░░░  37%   │ │
│ │ Python Official Docs             18 queries  ███░░░░░░░  29%   │ │
│ │ React Documentation              12 queries  ██░░░░░░░░  19%   │ │
│ │ Custom Knowledge Base             9 queries  █░░░░░░░░░  15%   │ │
│ │                                                                 │ │
│ │ Total: 107 queries across 5 sources                            │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                      ↑ NEW!          │
│                                                                     │
│ ┌──────────────── 🔍 Popular Search Queries (24h) ───────────────┐ │
│ │                                                                 │ │
│ │ 1. "vector search pgvector"                         23 times   │ │
│ │ 2. "authentication JWT tokens"                      18 times   │ │
│ │ 3. "React hooks useState useEffect"                 15 times   │ │
│ │ 4. "FastAPI middleware authentication"              12 times   │ │
│ │ 5. "database migrations SQLite"                      9 times   │ │
│ │                                                                 │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                      ↑ NEW!          │
│                                                                     │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│ │ Time Range  │  │ Category    │  │ Refresh     │                 │
│ │ [24 hours▼] │  │ [All     ▼] │  │   🔄        │                 │
│ └─────────────┘  └─────────────┘  └─────────────┘                 │
│                                                                     │
│ ┌──────────────────── Usage Over Time ─────────────────────────┐   │
│ │                                                               │   │
│ │    [BAR CHART: Hourly usage with total calls and errors]     │   │
│ │                                                               │   │
│ │    120│                                                       │   │
│ │     90│  ██                                                   │   │
│ │     60│  ██  ██                                               │   │
│ │     30│  ██  ██  ██                                           │   │
│ │      0│──────────────────────────────────────────────────────│   │
│ │       Jan 12  Jan 12  Jan 12  Jan 12                         │   │
│ │       10am    2pm     6pm     10pm                            │   │
│ └───────────────────────────────────────────────────────────────┘   │
│                                                                     │
│ ┌────────────── Top 10 Most Used Tools ──────────────┐             │
│ │ Tool Name                          Call Count      │             │
│ │ ─────────────────────────────────────────────────  │             │
│ │ 1. rag_search_knowledge_base            87         │             │
│ │ 2. find_projects                        23         │             │
│ │ 3. find_tasks                           12         │             │
│ │ 4. manage_project                        5         │             │
│ └─────────────────────────────────────────────────────┘             │
│                                                                     │
│ ┌──────────────── 💻 Client Distribution ────────────────┐ OPTIONAL│
│ │                                                         │         │
│ │              ╭─────────╮                                │         │
│ │             ╱           ╲          • Claude Code  65%  │         │
│ │            │    [PIE]    │         • Cursor       28%  │         │
│ │             ╲           ╱          • Windsurf      7%  │         │
│ │              ╰─────────╯                                │         │
│ │                                                         │         │
│ └─────────────────────────────────────────────────────────┘         │
│                                                      ↑ OPTIONAL      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Component Mockups

### 1. Knowledge Base Usage Card (NEW)

```
┌──────────────────────────────────────────────────────────────────┐
│ 📚 Knowledge Bases Queried (Last 24 hours)          🔄 Refresh   │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Supabase Documentation                                           │
│ ████████████████████████░░░░░░  45 queries (42.1%)              │
│ Avg: 234ms | 98% success                                        │
│                                                                  │
│ Anthropic AI Documentation                                       │
│ ███████████████░░░░░░░░░░░░░░░  23 queries (21.5%)              │
│ Avg: 189ms | 100% success                                       │
│                                                                  │
│ Python Official Documentation                                    │
│ ████████████░░░░░░░░░░░░░░░░░░  18 queries (16.8%)              │
│ Avg: 312ms | 94% success                                        │
│                                                                  │
│ React Documentation                                              │
│ ████████░░░░░░░░░░░░░░░░░░░░░░  12 queries (11.2%)              │
│ Avg: 267ms | 100% success                                       │
│                                                                  │
│ Custom Knowledge Base                                            │
│ ██████░░░░░░░░░░░░░░░░░░░░░░░░   9 queries (8.4%)               │
│ Avg: 456ms | 89% success                                        │
│                                                                  │
│ ─────────────────────────────────────────────────────────────── │
│ Total: 107 queries across 5 knowledge sources                   │
│                                                                  │
│ [View All Sources →]                                             │
└──────────────────────────────────────────────────────────────────┘

Hover Interaction:
┌────────────────────────────────────┐
│ Supabase Documentation             │
│ ───────────────────────────────────│
│ Total Queries: 45                  │
│ Unique Queries: 23                 │
│ Avg Response: 234ms                │
│ Success Rate: 98%                  │
│ Most Queried: "vector search"      │
└────────────────────────────────────┘
```

### 2. Popular Queries Card (NEW)

```
┌──────────────────────────────────────────────────────────────────┐
│ 🔍 Popular Search Queries (Last 24 hours)                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 1. "vector search pgvector"                      [23 searches]  │
│    Most used in: Supabase Documentation                         │
│    Avg response: 245ms                                           │
│                                                                  │
│ 2. "authentication JWT tokens"                   [18 searches]  │
│    Most used in: Anthropic AI                                   │
│    Avg response: 189ms                                           │
│                                                                  │
│ 3. "React hooks useState useEffect"              [15 searches]  │
│    Most used in: React Documentation                            │
│    Avg response: 267ms                                           │
│                                                                  │
│ 4. "FastAPI middleware authentication"           [12 searches]  │
│    Most used in: Python Documentation                           │
│    Avg response: 312ms                                           │
│                                                                  │
│ 5. "database migrations SQLite PostgreSQL"        [9 searches]  │
│    Most used in: Multiple Sources                               │
│    Avg response: 198ms                                           │
│                                                                  │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│ 💡 Tip: Popular queries indicate common knowledge gaps          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

Click Interaction:
→ Clicking a query filters the main chart to show usage of that query
```

### 3. Performance Metrics Card (NEW - 4th Summary Card)

```
┌─────────────────────────────────┐
│ ⚡ Avg Response Time             │
│                                 │
│         234 ms    ✓             │ ← Green (< 300ms)
│                                 │
│ 95th percentile: 512 ms         │
│ Slowest: rag_search (456ms)     │
│                                 │
│ ▲ 12% faster than yesterday     │
└─────────────────────────────────┘

Color Coding:
  Green:  < 300ms  (Fast)
  Yellow: 300-1000ms (Acceptable)
  Red:    > 1000ms (Slow)
```

### 4. Client Distribution Card (OPTIONAL)

```
┌──────────────────────────────────────────────────────────────────┐
│ 💻 AI IDE Client Distribution                                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│                     ╭─────────────╮                              │
│                    ╱               ╲                             │
│                   │   Windsurf 7%   │                            │
│                   │       (9)       │                            │
│              ╱────┴─────────────────┴────╲                       │
│             │                             │                      │
│             │      Claude Code 65%        │                      │
│             │         (87 calls)          │                      │
│             │                             │                      │
│              ╲────┬─────────────────┬────╱                       │
│                   │   Cursor 28%    │                            │
│                   │     (36)        │                            │
│                    ╲               ╱                             │
│                     ╰─────────────╯                              │
│                                                                  │
│ Legend:                                                          │
│ ● Claude Code    87 calls (65.4%)                               │
│ ● Cursor         36 calls (27.1%)                               │
│ ● Windsurf        9 calls (6.8%)                                │
│ ● Unknown         1 call  (0.7%)                                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Empty States

### Knowledge Base Card - No Data

```
┌──────────────────────────────────────────────────────────────────┐
│ 📚 Knowledge Bases Queried                                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│                        📂                                        │
│                                                                  │
│                No knowledge bases queried yet                    │
│                                                                  │
│         MCP tools haven't been used to search knowledge          │
│              bases in the selected time period.                  │
│                                                                  │
│                                                                  │
│            [Go to Knowledge Page →]  [View MCP Tools →]          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Popular Queries - No Data

```
┌──────────────────────────────────────────────────────────────────┐
│ 🔍 Popular Search Queries                                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│                        🔍                                        │
│                                                                  │
│                   No search queries yet                          │
│                                                                  │
│            Start using RAG tools to search your                  │
│                   knowledge base.                                │
│                                                                  │
│                                                                  │
│                  [Learn about RAG Tools →]                       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Mobile Layout (< 768px)

```
┌─────────────────────────────────┐
│ MCP Usage Analytics             │
├─────────────────────────────────┤
│                                 │
│ ┌─────────────────────────────┐ │
│ │  Total Calls (24h)          │ │
│ │         127                 │ │
│ └─────────────────────────────┘ │
│                                 │
│ ┌─────────────────────────────┐ │
│ │  Success Rate               │ │
│ │        98.4%                │ │
│ └─────────────────────────────┘ │
│                                 │
│ ┌─────────────────────────────┐ │
│ │  Failed Calls               │ │
│ │          2                  │ │
│ └─────────────────────────────┘ │
│                                 │
│ ┌─────────────────────────────┐ │
│ │  Avg Response               │ │
│ │       234 ms                │ │
│ └─────────────────────────────┘ │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ 📚 Knowledge Bases          │ │
│ │ ───────────────────────────│ │
│ │ Supabase  45 ████████░░ 42%│ │
│ │ Anthropic 23 ████░░░░░  21%│ │
│ │ Python    18 ███░░░░░░  17%│ │
│ │ [+ 2 more]                 │ │
│ └─────────────────────────────┘ │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ 🔍 Popular Queries          │ │
│ │ ───────────────────────────│ │
│ │ 1. vector search      23x  │ │
│ │ 2. authentication     18x  │ │
│ │ 3. React hooks        15x  │ │
│ │ [+ 2 more]                 │ │
│ └─────────────────────────────┘ │
│                                 │
│ [Filters]                       │
│                                 │
│ [Chart - Stacked]               │
│                                 │
│ [Top Tools Table]               │
│                                 │
└─────────────────────────────────┘
```

---

## Color Palette

### Card Accent Colors
- **Knowledge Bases**: Purple (#8B5CF6)
- **Popular Queries**: Cyan (#06B6D4)
- **Performance**: Green (#10B981) / Yellow (#F59E0B) / Red (#EF4444)
- **Client Distribution**: Blue (#3B82F6)

### Chart Colors
- **Total Calls**: Blue (#3B82F6)
- **Errors**: Red (#EF4444)
- **Success**: Green (#10B981)

### Status Indicators
- ✓ Success: Green (#10B981)
- ⚠ Warning: Yellow (#F59E0B)
- ✗ Error: Red (#EF4444)

---

## Interaction Patterns

### 1. Knowledge Base Bar - Hover
```
User hovers over "Supabase Documentation" bar
↓
Tooltip appears with:
- Total queries
- Unique queries
- Avg response time
- Success rate
- Most common query
```

### 2. Popular Query - Click
```
User clicks "vector search pgvector"
↓
Main chart filters to show only queries containing that term
↓
Filter chip appears: "Filtered: vector search ✕"
↓
User can clear filter by clicking ✕
```

### 3. Time Range - Change
```
User changes from "24h" to "7 days"
↓
All cards re-fetch with new time range
↓
Bar chart x-axis changes from hours to days
↓
Data aggregated differently for longer period
```

### 4. Refresh Button
```
User clicks refresh button
↓
Button shows spinner
↓
All data refetches
↓
Optimistic UI update
↓
Success toast: "Analytics updated"
```

---

## Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  User Opens Settings > MCP Usage Analytics                   │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  1. Initial Load                                       │ │
│  │     - Fetch summary (total, success, errors, perf)     │ │
│  │     - Fetch hourly usage (24h default)                 │ │
│  │     - Fetch knowledge base analytics                   │ │
│  │     - Fetch popular queries                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  2. Display Dashboard                                  │ │
│  │     - Render 4 summary cards                           │ │
│  │     - Render knowledge base card                       │ │
│  │     - Render popular queries card                      │ │
│  │     - Render filters                                   │ │
│  │     - Render bar chart                                 │ │
│  │     - Render top tools table                           │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  3. User Interactions                                  │ │
│  │     - Change time range → Refetch all data             │ │
│  │     - Change category → Filter client-side             │ │
│  │     - Click query → Filter chart                       │ │
│  │     - Click refresh → Manual refetch                   │ │
│  │     - Hover elements → Show tooltips                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  4. Automatic Updates (Smart Polling)                  │ │
│  │     - Refetch every 30s when tab active                │ │
│  │     - Pause when tab inactive                          │ │
│  │     - Use ETag caching to reduce bandwidth             │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Progressive Enhancement Strategy

### Phase 1 (MVP) - Week 1
```
✅ 4 Summary Cards (add performance)
✅ Knowledge Base Usage Card
✅ Basic filtering (time, category)
✅ Empty states
✅ Loading states
```

### Phase 2 (Enhanced) - Week 2
```
✅ Popular Queries Card
✅ Click-to-filter interaction
✅ Performance color coding
✅ Responsive mobile layout
```

### Phase 3 (Complete) - Week 3
```
✅ Client Distribution Card
✅ Advanced tooltips
✅ Export to CSV
✅ Performance optimizations
```

---

## Key Improvements Over Current State

1. **Knowledge Base Visibility** ✨
   - Shows which sources are most valuable
   - Identifies underutilized knowledge bases
   - Helps prioritize content updates

2. **Query Pattern Insights** 🔍
   - Reveals what users are searching for
   - Identifies knowledge gaps
   - Guides documentation improvements

3. **Performance Monitoring** ⚡
   - Instant view of query speed
   - Identifies slow tools/sources
   - Helps optimize infrastructure

4. **Better UX** 🎨
   - More visual feedback
   - Interactive filtering
   - Mobile-optimized

---

**Status**: Design Complete - Ready for Implementation
**Next Step**: Begin Phase 1 Backend Development
