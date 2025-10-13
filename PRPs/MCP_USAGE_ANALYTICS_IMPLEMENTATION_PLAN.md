# MCP Usage Analytics - Implementation Plan (Phases 3-6)

**Version**: 1.0
**Status**: Ready for Implementation
**Created**: 2025-01-13
**Backend Complete**: Phases 1-2 ✅
**Remaining Work**: Phases 3-6

---

## Executive Summary

This implementation plan details the remaining work to complete the MCP Usage Analytics feature. The backend infrastructure (database schema and tracking middleware) is fully implemented and integrated across all 14 MCP tools. The remaining work focuses on exposing analytics via API, building frontend components, and comprehensive testing.

### Completed Work (Phases 1-2)
- ✅ Database migration file with tables, views, functions, and indexes
- ✅ Usage tracking middleware with decorator pattern
- ✅ Integration into all 14 MCP tools (5 RAG, 2 Project, 2 Task, 2 Document, 2 Version, 1 Feature)
- ✅ Migration tooling and documentation

### Remaining Work
- Phase 3: Analytics API (Backend REST endpoints)
- Phase 4: Frontend Service & Hooks (Data fetching layer)
- Phase 5: UI Components (Dashboard with charts)
- Phase 6: Testing & Optimization (E2E tests and performance)

### Total Estimated Time: 32.5 hours
- Phase 3: 9.5 hours
- Phase 4: 6 hours
- Phase 5: 8 hours
- Phase 6: 9 hours

---

## Phase 3: Analytics API (Backend REST Endpoints)

**Goal**: Create FastAPI endpoints to query usage data and expose aggregated metrics.

**Priority**: High
**Estimated Time**: 9.5 hours
**Dependencies**: Database migration must be run in Supabase

### Task 3.1: Create Analytics API Routes

**File**: `python/src/server/api_routes/mcp_analytics_api.py`
**Estimated Time**: 4 hours

**Description**:
Create a new FastAPI router with endpoints for querying hourly/daily usage data and summary statistics.

**Implementation Requirements**:

1. **Endpoint: GET /api/mcp/analytics/hourly**
   - Query parameters: `hours` (1-168), `tool_category` (optional), `tool_name` (optional)
   - Returns: Aggregated hourly usage data from materialized view
   - Response includes: call_count, avg_response_time_ms, error_count, unique_sessions per hour
   - Add ETag support for caching

2. **Endpoint: GET /api/mcp/analytics/daily**
   - Query parameters: `days` (1-180), `tool_category` (optional)
   - Returns: Aggregated daily usage data from materialized view
   - Similar structure to hourly endpoint
   - Add ETag support

3. **Endpoint: GET /api/mcp/analytics/summary**
   - Returns: Summary statistics for last 24 hours
   - Includes: total_calls, success_rate, top_tools, by_category counts
   - Query raw events table, not materialized views

4. **Endpoint: POST /api/mcp/analytics/refresh-views**
   - Manually trigger materialized view refresh
   - Calls the `refresh_mcp_usage_views()` PostgreSQL function
   - Returns: Status of both view refreshes

**Code Pattern**:
```python
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import Optional

from ..config.database import get_supabase_client
from ..config.logfire_config import get_logger
from ..utils.etag_utils import generate_etag, check_etag

router = APIRouter(prefix="/api/mcp/analytics", tags=["mcp-analytics"])

@router.get("/hourly")
async def get_hourly_usage(
    request: Request,
    hours: int = Query(24, ge=1, le=168),
    tool_category: Optional[str] = None,
    tool_name: Optional[str] = None
):
    # Implementation follows spec pattern
    pass
```

**Testing**:
- Test all query parameter combinations
- Verify filtering works correctly
- Test time range calculations
- Verify ETag generation and 304 responses

**Acceptance Criteria**:
- [ ] All 4 endpoints implemented
- [ ] Query parameters validated
- [ ] Error handling for database failures
- [ ] ETag support for GET endpoints
- [ ] Response times < 500ms for typical queries
- [ ] Proper HTTP status codes

---

### Task 3.2: Register Analytics Routes

**File**: `python/src/server/main.py`
**Estimated Time**: 30 minutes

**Description**:
Register the new analytics router in the main FastAPI application.

**Implementation Steps**:
1. Import the analytics router
2. Include it in the app with proper prefix
3. Ensure it appears in OpenAPI docs
4. Add to the router list after other MCP routes

**Code Pattern**:
```python
from .api_routes import mcp_analytics_api

# Add after existing routers
app.include_router(mcp_analytics_api.router)
```

**Testing**:
- Verify routes appear in OpenAPI docs at `/docs`
- Test endpoint accessibility
- Verify proper CORS configuration

**Acceptance Criteria**:
- [ ] Router registered and accessible
- [ ] All endpoints visible in `/docs`
- [ ] No route conflicts with existing endpoints

---

### Task 3.3: Create Materialized View Refresh Mechanism

**Estimated Time**: 2 hours

**Description**:
Implement automated refresh of materialized views using one of the available options.

**Options** (choose one based on environment):

**Option A: Supabase Edge Function** (Recommended if pg_cron unavailable)
- Create Supabase Edge Function to call the refresh endpoint
- Schedule using Supabase's built-in scheduling
- File: `supabase/functions/refresh-mcp-views/index.ts`

**Option B: pg_cron Extension** (If available in Supabase)
```sql
-- Run in Supabase SQL Editor
SELECT cron.schedule(
    'refresh-mcp-usage-views',
    '*/15 * * * *',  -- Every 15 minutes
    $$ SELECT refresh_mcp_usage_views(); $$
);
```

**Option C: Python APScheduler** (Backend-based)
- Add APScheduler to the FastAPI application
- Schedule periodic calls to refresh function
- File: `python/src/server/scheduler/mcp_refresh_job.py`

**Recommendation**: Start with Option A (Edge Function) or manual endpoint calls, migrate to pg_cron later.

**Testing**:
- Manually trigger refresh via endpoint
- Verify materialized views update
- Check view last_refresh timestamp
- Validate data consistency

**Acceptance Criteria**:
- [ ] Materialized views refresh every 15 minutes (or on-demand)
- [ ] Refresh job logs success/failure
- [ ] Views show updated data within refresh interval
- [ ] No performance impact on main application

---

### Task 3.4: Write API Tests

**File**: `python/tests/server/api_routes/test_mcp_analytics_api.py`
**Estimated Time**: 3 hours

**Description**:
Comprehensive test suite for all analytics endpoints using pytest and FastAPI TestClient.

**Test Coverage**:

1. **Test Hourly Endpoint**:
   - Valid time ranges (24h, 48h, 168h)
   - Category filtering
   - Tool name filtering
   - Empty results handling
   - ETag generation and validation

2. **Test Daily Endpoint**:
   - Valid day ranges (1-180)
   - Category filtering
   - Date range calculations
   - ETag support

3. **Test Summary Endpoint**:
   - Summary calculation accuracy
   - Top tools ordering
   - Category aggregation
   - Empty data handling

4. **Test Refresh Endpoint**:
   - Successful refresh
   - Error handling
   - Permission checks (if applicable)

5. **Test Edge Cases**:
   - Invalid query parameters
   - Out-of-range values
   - Database connection failures
   - Malformed requests

**Code Pattern**:
```python
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

def test_get_hourly_usage_default(client: TestClient):
    """Test hourly usage with default parameters."""
    response = client.get("/api/mcp/analytics/hourly")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "time_range" in data

def test_get_hourly_usage_with_filters(client: TestClient):
    """Test hourly usage with category filter."""
    response = client.get("/api/mcp/analytics/hourly?tool_category=rag")
    assert response.status_code == 200
    # Verify all results have category='rag'
```

**Testing Requirements**:
- Use test database or mock Supabase client
- Create test fixtures with sample usage data
- Test all query parameter combinations
- Verify response schemas
- Check HTTP status codes

**Acceptance Criteria**:
- [ ] 100% endpoint coverage
- [ ] All query parameter combinations tested
- [ ] Error cases handled
- [ ] ETag behavior validated
- [ ] Tests pass consistently
- [ ] < 5 seconds total test execution time

---

## Phase 4: Frontend Service & Hooks (Data Fetching Layer)

**Goal**: Create TypeScript services and React Query hooks for fetching analytics data.

**Priority**: Medium
**Estimated Time**: 6 hours
**Dependencies**: Phase 3 (Analytics API) must be completed

### Task 4.1: Create Analytics Service

**File**: `archon-ui-main/src/features/mcp/services/mcpAnalyticsService.ts`
**Estimated Time**: 2 hours

**Description**:
Create a TypeScript service class that wraps the analytics API endpoints using the shared apiClient.

**Implementation Requirements**:

1. **Type Definitions**:
```typescript
export interface HourlyUsageData {
  hour_bucket: string;
  tool_category: string;
  tool_name: string;
  call_count: number;
  avg_response_time_ms: number;
  error_count: number;
  unique_sessions: number;
}

export interface DailyUsageData {
  date_bucket: string;
  tool_category: string;
  tool_name: string;
  call_count: number;
  avg_response_time_ms: number;
  error_count: number;
  unique_sessions: number;
}

export interface UsageSummary {
  last_24_hours: {
    total_calls: number;
    successful_calls: number;
    failed_calls: number;
    success_rate: number;
  };
  by_category: Record<string, number>;
  top_tools: Array<{ tool: string; calls: number }>;
}
```

2. **Service Methods**:
   - `getHourlyUsage(hours, category?, toolName?)`: Fetch hourly data
   - `getDailyUsage(days, category?)`: Fetch daily data
   - `getSummary()`: Fetch summary statistics
   - Use URLSearchParams for query string construction
   - Leverage existing apiClient for HTTP calls and ETag support

3. **Error Handling**:
   - Let apiClient handle HTTP errors
   - Type-safe response parsing
   - Optional parameters with defaults

**Code Pattern**:
```typescript
import { apiClient } from "@/features/shared/api/apiClient";

class MCPAnalyticsService {
  async getHourlyUsage(
    hours: number = 24,
    toolCategory?: string,
    toolName?: string
  ): Promise<HourlyUsageData[]> {
    const params = new URLSearchParams({ hours: hours.toString() });
    if (toolCategory) params.append("tool_category", toolCategory);
    if (toolName) params.append("tool_name", toolName);

    const response = await apiClient.get<{ data: HourlyUsageData[] }>(
      `/api/mcp/analytics/hourly?${params.toString()}`
    );
    return response.data;
  }
}

export const mcpAnalyticsService = new MCPAnalyticsService();
```

**Testing**:
- Mock apiClient for unit tests
- Test all parameter combinations
- Verify query string construction
- Test error scenarios

**Acceptance Criteria**:
- [ ] All service methods implemented
- [ ] TypeScript types properly defined
- [ ] Uses shared apiClient
- [ ] Query parameters correctly encoded
- [ ] Default values work as expected
- [ ] Service exported as singleton

---

### Task 4.2: Create React Query Hooks

**File**: `archon-ui-main/src/features/mcp/hooks/useMcpAnalytics.ts`
**Estimated Time**: 2 hours

**Description**:
Create TanStack Query hooks that wrap the analytics service methods and provide proper cache management.

**Implementation Requirements**:

1. **Query Key Factory**:
```typescript
export const mcpAnalyticsKeys = {
  all: ["mcp-analytics"] as const,
  hourly: (hours: number, category?: string, tool?: string) =>
    [...mcpAnalyticsKeys.all, "hourly", hours, category, tool] as const,
  daily: (days: number, category?: string) =>
    [...mcpAnalyticsKeys.all, "daily", days, category] as const,
  summary: () => [...mcpAnalyticsKeys.all, "summary"] as const,
};
```

2. **Hooks to Implement**:
   - `useMcpHourlyUsage(hours, category?, tool?, options?)`
   - `useMcpDailyUsage(days, category?, options?)`
   - `useMcpUsageSummary(options?)`

3. **Configuration**:
   - Use `STALE_TIMES.frequent` (5s) for summary and hourly data
   - Use `STALE_TIMES.normal` (30s) for daily data
   - Enable/disable queries via options parameter
   - Proper error handling via useQuery's error state

4. **Smart Polling** (Optional):
   - Consider adding smart polling for real-time updates
   - Use `useSmartPolling` hook if needed
   - Default to no polling, rely on staleTime

**Code Pattern**:
```typescript
import { useQuery } from "@tanstack/react-query";
import { mcpAnalyticsService } from "../services/mcpAnalyticsService";
import { STALE_TIMES } from "@/features/shared/config/queryPatterns";

export function useMcpHourlyUsage(
  hours: number = 24,
  toolCategory?: string,
  toolName?: string,
  options?: { enabled?: boolean }
) {
  return useQuery({
    queryKey: mcpAnalyticsKeys.hourly(hours, toolCategory, toolName),
    queryFn: () => mcpAnalyticsService.getHourlyUsage(hours, toolCategory, toolName),
    staleTime: STALE_TIMES.frequent,
    enabled: options?.enabled !== false,
  });
}
```

**Testing**:
- Mock service methods
- Mock STALE_TIMES and query patterns
- Test query key generation
- Verify staleTime configuration
- Test enabled/disabled states

**Acceptance Criteria**:
- [ ] Query key factory follows patterns
- [ ] All hooks implemented
- [ ] Proper staleTime configuration
- [ ] Enable/disable functionality works
- [ ] Hooks return proper loading/error states
- [ ] Query keys are stable and predictable

---

### Task 4.3: Write Service and Hook Tests

**Files**:
- `archon-ui-main/src/features/mcp/services/tests/mcpAnalyticsService.test.ts`
- `archon-ui-main/src/features/mcp/hooks/tests/useMcpAnalytics.test.ts`

**Estimated Time**: 2 hours

**Description**:
Comprehensive unit tests for both service and hooks using Vitest and React Testing Library.

**Service Tests**:
1. Test all service methods
2. Verify query parameter construction
3. Test error handling
4. Mock apiClient responses

**Hook Tests**:
1. Test query key generation
2. Verify staleTime configuration
3. Test enabled/disabled states
4. Test data transformation (if any)
5. Mock service method responses

**Code Pattern**:
```typescript
import { describe, it, expect, vi } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useMcpHourlyUsage } from "../useMcpAnalytics";
import { mcpAnalyticsService } from "../../services/mcpAnalyticsService";

vi.mock("../../services/mcpAnalyticsService");
vi.mock("../../../shared/config/queryPatterns", () => ({
  STALE_TIMES: {
    instant: 0,
    frequent: 5_000,
    normal: 30_000,
  },
}));

describe("useMcpHourlyUsage", () => {
  it("should fetch hourly usage data", async () => {
    const mockData = [/* mock data */];
    vi.mocked(mcpAnalyticsService.getHourlyUsage).mockResolvedValue(mockData);

    const { result } = renderHook(() => useMcpHourlyUsage(24), {
      wrapper: createQueryWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockData);
  });
});
```

**Testing Requirements**:
- Mock all external dependencies
- Test success and error paths
- Verify query key consistency
- Test all parameter combinations

**Acceptance Criteria**:
- [ ] All service methods tested
- [ ] All hooks tested
- [ ] Error cases covered
- [ ] Mock patterns follow codebase conventions
- [ ] Tests pass consistently

---

## Phase 5: UI Components (Dashboard with Charts)

**Goal**: Build interactive React components with charts to display usage analytics.

**Priority**: Medium
**Estimated Time**: 8 hours
**Dependencies**: Phase 4 (Frontend hooks) must be completed

### Task 5.1: Install Recharts Dependency

**Estimated Time**: 15 minutes

**Description**:
Install the Recharts library for data visualization.

**Commands**:
```bash
cd archon-ui-main
npm install recharts
npm install --save-dev @types/recharts  # If types not included
```

**Verification**:
- Check `package.json` for recharts entry
- Verify no version conflicts
- Test import in a component

**Acceptance Criteria**:
- [ ] Recharts installed successfully
- [ ] No dependency conflicts
- [ ] Types available

---

### Task 5.2: Create MCPUsageAnalytics Component

**File**: `archon-ui-main/src/features/mcp/components/MCPUsageAnalytics.tsx`
**Estimated Time**: 4 hours

**Description**:
Main analytics dashboard component with bar charts, summary cards, and filters.

**Component Structure**:

1. **Summary Cards** (Top Row):
   - Total Calls (24h) with Activity icon
   - Success Rate (%) with TrendingUp icon
   - Failed Calls with AlertCircle icon
   - Use Card primitive from UI library

2. **Filters** (Second Row):
   - Time Range selector: 24h, 48h, 7 days
   - Category filter: All, RAG, Project, Task, Document
   - Use Select primitive from UI library

3. **Bar Chart** (Main Content):
   - Horizontal axis: Time (hours)
   - Vertical axis: Call count
   - Two bars per time bucket: Total calls (blue), Errors (red)
   - Responsive container (100% width, 400px height)
   - Interactive tooltips with detailed info

4. **Top Tools Table** (Bottom):
   - Two columns: Tool Name, Call Count
   - Sorted by usage (descending)
   - Limit to top 10 tools
   - Hover effect on rows

**Implementation Details**:
```typescript
import React, { useState, useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Activity, TrendingUp, AlertCircle } from "lucide-react";
import { useMcpHourlyUsage, useMcpUsageSummary } from "../hooks/useMcpAnalytics";
import { Card } from "@/features/ui/primitives/Card";

export const MCPUsageAnalytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState<24 | 48 | 168>(24);
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>();

  const { data: hourlyData, isLoading: hourlyLoading } = useMcpHourlyUsage(
    timeRange,
    selectedCategory
  );

  const { data: summary, isLoading: summaryLoading } = useMcpUsageSummary();

  // Aggregate data by hour for chart display
  const chartData = useMemo(() => {
    if (!hourlyData) return [];

    // Group by hour_bucket, sum call_count and error_count
    const aggregated = hourlyData.reduce((acc, item) => {
      const hour = new Date(item.hour_bucket).toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
      });

      if (!acc[hour]) {
        acc[hour] = { hour, total: 0, errors: 0 };
      }

      acc[hour].total += item.call_count;
      acc[hour].errors += item.error_count;

      return acc;
    }, {} as Record<string, { hour: string; total: number; errors: number }>);

    return Object.values(aggregated);
  }, [hourlyData]);

  // Loading and error states implementation
  // Component JSX with Cards, Select, BarChart, and Table
};
```

**Styling Requirements**:
- Follow Tron-inspired glassmorphism theme
- Use existing UI primitives (Card, Select)
- Responsive design (mobile-first)
- Dark mode support
- Match existing Settings page aesthetics

**Accessibility**:
- Proper ARIA labels for charts
- Keyboard navigation for filters
- Screen reader friendly tooltips

**Acceptance Criteria**:
- [ ] Summary cards display correct metrics
- [ ] Bar chart renders with proper data
- [ ] Filters update chart data
- [ ] Top tools table sorts correctly
- [ ] Loading states display properly
- [ ] Error states handled gracefully
- [ ] Mobile responsive (< 768px)
- [ ] Dark mode works correctly

---

### Task 5.3: Integrate into Settings Page

**File**: `archon-ui-main/src/pages/SettingsPage.tsx`
**Estimated Time**: 1 hour

**Description**:
Add the MCPUsageAnalytics component to the Settings page in a collapsible card.

**Implementation Steps**:

1. Import the component:
```typescript
import { MCPUsageAnalytics } from "@/features/mcp/components/MCPUsageAnalytics";
import { Activity } from "lucide-react";
```

2. Add to the page layout (after Database section):
```typescript
<motion.div variants={itemVariants}>
  <CollapsibleSettingsCard
    title="MCP Usage Analytics"
    icon={Activity}
    accentColor="blue"
    storageKey="settings-mcp-analytics"
    defaultExpanded={false}
  >
    <MCPUsageAnalytics />
  </CollapsibleSettingsCard>
</motion.div>
```

3. Update the settings page state to include the new section
4. Ensure proper animation and collapsible behavior

**Testing**:
- Verify component renders in Settings page
- Test collapsible expand/collapse
- Check localStorage persistence of expanded state
- Verify scroll behavior
- Test on mobile and desktop

**Acceptance Criteria**:
- [ ] Analytics section added to Settings page
- [ ] Collapsible card works properly
- [ ] Default collapsed state
- [ ] localStorage persistence works
- [ ] Icon and accent color correct
- [ ] No layout issues

---

### Task 5.4: Polish UI and Loading States

**Estimated Time**: 2 hours

**Description**:
Refine the UI, add proper loading skeletons, error messages, and empty states.

**Requirements**:

1. **Loading States**:
   - Skeleton loaders for cards (use Tailwind animate-pulse)
   - Chart loading placeholder
   - Table shimmer effect

2. **Error States**:
   - Error message with retry button
   - Friendly error text
   - Maintain layout structure

3. **Empty States**:
   - "No data available" message when no usage events
   - Helpful text explaining how to generate usage
   - Icon and clear call-to-action

4. **Responsive Design**:
   - Test breakpoints: 320px, 768px, 1024px, 1440px
   - Adjust chart height on mobile
   - Stack cards vertically on small screens
   - Horizontal scroll for table if needed

5. **Accessibility**:
   - ARIA labels for interactive elements
   - Focus indicators
   - Color contrast compliance (WCAG AA)

**Code Pattern**:
```typescript
// Loading state
if (hourlyLoading || summaryLoading) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="p-4 animate-pulse">
            <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded" />
          </Card>
        ))}
      </div>
      {/* More skeleton loaders */}
    </div>
  );
}

// Error state
if (hourlyError || summaryError) {
  return (
    <Card className="p-6">
      <div className="text-center">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <p className="text-lg font-semibold mb-2">Failed to load analytics</p>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          {hourlyError?.message || summaryError?.message}
        </p>
        <button onClick={() => refetch()}>Retry</button>
      </div>
    </Card>
  );
}

// Empty state
if (chartData.length === 0) {
  return (
    <Card className="p-6 text-center">
      <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <p className="text-lg font-semibold mb-2">No usage data yet</p>
      <p className="text-sm text-gray-600 dark:text-gray-400">
        Start using MCP tools to see analytics here
      </p>
    </Card>
  );
}
```

**Testing**:
- Test all states (loading, error, empty, success)
- Verify responsive behavior at all breakpoints
- Test dark mode appearance
- Run accessibility audit (Lighthouse)
- Test keyboard navigation

**Acceptance Criteria**:
- [ ] Loading skeletons match final UI
- [ ] Error states are user-friendly
- [ ] Empty states provide guidance
- [ ] Responsive at all breakpoints
- [ ] Mobile experience is smooth
- [ ] Accessibility score > 90
- [ ] Dark mode looks polished

---

### Task 5.5: Add Chart Interactivity

**Estimated Time**: 45 minutes

**Description**:
Enhance the bar chart with interactive features.

**Features to Add**:

1. **Custom Tooltips**:
   - Show detailed info on hover
   - Format timestamps nicely
   - Display exact call counts and percentages

2. **Click to Filter** (Optional):
   - Click on a bar to see tool breakdown for that hour
   - Modal or expandable detail view

3. **Legend Interactivity**:
   - Click legend to toggle data series
   - Hide/show error bars

**Code Pattern**:
```typescript
<Tooltip
  content={({ active, payload }) => {
    if (!active || !payload) return null;

    return (
      <div className="bg-black/90 text-white p-3 rounded-lg shadow-lg">
        <p className="font-semibold mb-1">{payload[0].payload.hour}</p>
        <p className="text-sm">Total Calls: {payload[0].value}</p>
        <p className="text-sm">Errors: {payload[1].value}</p>
        <p className="text-sm">
          Success Rate: {((payload[0].value - payload[1].value) / payload[0].value * 100).toFixed(1)}%
        </p>
      </div>
    );
  }}
/>
```

**Acceptance Criteria**:
- [ ] Tooltips show detailed information
- [ ] Hover effects are smooth
- [ ] Interactions feel responsive
- [ ] Legend controls work (if implemented)

---

## Phase 6: Testing & Optimization

**Goal**: Comprehensive testing, performance optimization, and documentation.

**Priority**: Low
**Estimated Time**: 9 hours
**Dependencies**: Phases 3-5 must be completed

### Task 6.1: End-to-End Testing

**Estimated Time**: 3 hours

**Description**:
Test the complete flow from MCP tool invocation to UI display.

**Test Scenarios**:

1. **Happy Path**:
   - Run MCP tool via MCP server
   - Verify event stored in database
   - Check API returns correct data
   - Verify UI displays updated metrics
   - Complete flow < 5 seconds

2. **Filter Scenarios**:
   - Change time range (24h → 48h → 7d)
   - Filter by category (RAG → Project → All)
   - Verify chart updates correctly
   - Check summary cards reflect filters

3. **Real-Time Updates**:
   - Generate usage events
   - Wait for staleTime to expire
   - Verify UI auto-refreshes
   - Check no data loss

4. **Error Scenarios**:
   - Simulate API failure
   - Verify error state displays
   - Test retry functionality
   - Ensure no UI crashes

5. **Mobile Testing**:
   - Test on actual mobile devices or emulators
   - Verify touch interactions
   - Check responsiveness
   - Test chart readability

**Testing Approach**:
- Manual testing with real data
- Playwright/Cypress for automated E2E
- Test on Chrome, Firefox, Safari
- Test on iOS and Android (mobile)

**Acceptance Criteria**:
- [ ] All happy path scenarios pass
- [ ] Filters work correctly
- [ ] Real-time updates function
- [ ] Error handling works
- [ ] Mobile experience is smooth
- [ ] Cross-browser compatibility verified

---

### Task 6.2: Performance Testing

**Estimated Time**: 2 hours

**Description**:
Measure and optimize performance across the stack.

**Metrics to Measure**:

1. **Backend Performance**:
   - API response times (target: < 500ms)
   - Database query times
   - Materialized view refresh time
   - Tracking overhead (target: < 10ms per tool call)

2. **Frontend Performance**:
   - Initial page load time
   - Chart render time
   - Re-render performance with filters
   - Bundle size impact

3. **Database Performance**:
   - Query execution plans
   - Index usage verification
   - Materialized view size

**Testing Approach**:

1. **Load Testing**:
```bash
# Use Apache Bench or similar
ab -n 1000 -c 10 http://localhost:8181/api/mcp/analytics/hourly?hours=24
```

2. **Database Profiling**:
```sql
EXPLAIN ANALYZE
SELECT * FROM archon_mcp_usage_hourly
WHERE hour_bucket >= NOW() - INTERVAL '24 hours';
```

3. **Frontend Profiling**:
   - Use React DevTools Profiler
   - Chrome DevTools Performance tab
   - Lighthouse audit

**Optimization Opportunities**:
- Add database indexes if needed
- Implement request memoization
- Optimize chart data transformation
- Consider pagination for large datasets

**Acceptance Criteria**:
- [ ] API responses < 500ms (95th percentile)
- [ ] Tracking overhead < 10ms per tool call
- [ ] Page load time < 2 seconds
- [ ] Chart renders in < 200ms
- [ ] No performance regressions
- [ ] Lighthouse score > 90

---

### Task 6.3: Query Result Caching

**Estimated Time**: 2 hours

**Description**:
Optimize repeated queries with aggressive caching strategies.

**Caching Strategies**:

1. **HTTP-Level Caching**:
   - ETags already implemented in Phase 3
   - Verify 304 responses working
   - Check cache headers

2. **TanStack Query Caching**:
   - Review staleTime settings
   - Consider longer cache for daily data
   - Implement background refetch for fresh data

3. **Backend Caching** (Optional):
   - Redis cache for expensive queries
   - Cache materialized view results
   - Time-based cache invalidation

4. **Materialized View Optimization**:
   - Review refresh frequency
   - Consider CONCURRENTLY refresh to avoid locks
   - Monitor view size and query performance

**Implementation**:
```typescript
// Aggressive caching for daily data
export function useMcpDailyUsage(days: number, category?: string) {
  return useQuery({
    queryKey: mcpAnalyticsKeys.daily(days, category),
    queryFn: () => mcpAnalyticsService.getDailyUsage(days, category),
    staleTime: STALE_TIMES.rare, // 5 minutes for daily data
    cacheTime: 1000 * 60 * 30, // Keep in cache for 30 minutes
    refetchOnWindowFocus: false, // Don't refetch on focus
  });
}
```

**Testing**:
- Monitor network requests (DevTools)
- Verify 304 responses
- Check cache hit rates
- Measure bandwidth savings

**Acceptance Criteria**:
- [ ] HTTP cache working (304 responses)
- [ ] TanStack Query cache optimized
- [ ] Repeated queries use cache
- [ ] Bandwidth savings measured
- [ ] No stale data issues

---

### Task 6.4: Documentation

**Estimated Time**: 2 hours

**Description**:
Update project documentation to include the new analytics feature.

**Documentation Updates**:

1. **CLAUDE.md** (`/home/jose/src/Archon/CLAUDE.md`):
   - Add MCP Analytics feature section
   - Document new API endpoints
   - Explain usage tracking
   - Add troubleshooting guide

2. **API Documentation**:
   - OpenAPI/Swagger docs already auto-generated
   - Add endpoint descriptions
   - Document query parameters
   - Provide example responses

3. **Frontend Documentation**:
   - Update component documentation
   - Document hooks usage
   - Add examples for developers

4. **User Guide** (Optional):
   - How to interpret analytics
   - What metrics mean
   - Privacy considerations

5. **README Updates**:
   - Add analytics to feature list
   - Update architecture diagram if exists
   - Add screenshots

**Documentation Structure**:
```markdown
## MCP Usage Analytics

### Overview
Track MCP server usage with comprehensive analytics dashboard showing hourly usage patterns, success rates, and most-used tools.

### Features
- Time-series data storage (180-day retention)
- Hourly and daily aggregations
- Interactive bar charts
- Real-time metrics

### API Endpoints
- `GET /api/mcp/analytics/hourly` - Hourly usage data
- `GET /api/mcp/analytics/daily` - Daily usage data
- `GET /api/mcp/analytics/summary` - Summary statistics
- `POST /api/mcp/analytics/refresh-views` - Refresh views

### Usage
Navigate to Settings → MCP Usage Analytics to view the dashboard.

### Privacy
All usage data is stored locally in your Supabase instance. No data is transmitted externally.
```

**Acceptance Criteria**:
- [ ] CLAUDE.md updated with analytics info
- [ ] API documentation complete
- [ ] Frontend hooks documented
- [ ] User-facing documentation clear
- [ ] Code examples provided
- [ ] Screenshots added (if applicable)

---

## Implementation Workflow

### Recommended Execution Order

1. **Phase 3: Analytics API** (Backend first approach)
   - Complete all API endpoints
   - Test thoroughly
   - Document API responses

2. **Phase 4: Frontend Services** (Data layer)
   - Build services to consume API
   - Create hooks with proper caching
   - Test data flow

3. **Phase 5: UI Components** (Visual layer)
   - Build components incrementally
   - Test each component in isolation
   - Integrate into Settings page

4. **Phase 6: Polish** (Final refinement)
   - End-to-end testing
   - Performance optimization
   - Documentation

### Daily Implementation Plan

**Day 1: Analytics API Foundation**
- Morning: Task 3.1 (API routes)
- Afternoon: Task 3.2 (Register routes) + Task 3.3 (Refresh mechanism)

**Day 2: API Testing & Frontend Services**
- Morning: Task 3.4 (API tests)
- Afternoon: Task 4.1 (Analytics service) + Task 4.2 (React hooks)

**Day 3: Frontend Testing & UI Foundation**
- Morning: Task 4.3 (Service/hook tests)
- Afternoon: Task 5.1 (Install Recharts) + Start Task 5.2 (Main component)

**Day 4: UI Components**
- Morning: Complete Task 5.2 (Main component)
- Afternoon: Task 5.3 (Settings integration) + Task 5.4 (Polish UI)

**Day 5: Testing & Optimization**
- Morning: Task 6.1 (E2E testing) + Task 6.2 (Performance)
- Afternoon: Task 6.3 (Caching) + Task 6.4 (Documentation)

---

## Prerequisites

### Before Starting Phase 3

1. **Database Migration**:
   - [ ] Run migration SQL in Supabase SQL Editor
   - [ ] Verify tables created: `archon_mcp_usage_events`
   - [ ] Verify materialized views: `archon_mcp_usage_hourly`, `archon_mcp_usage_daily`
   - [ ] Test schema: `docker compose exec archon-server python /app/migration/test_mcp_schema.py`

2. **Backend Running**:
   - [ ] MCP server running with tracking enabled
   - [ ] Generate some test usage events
   - [ ] Verify events stored in database

3. **Development Environment**:
   - [ ] Backend development server running
   - [ ] Frontend development server running
   - [ ] Database accessible

---

## Success Criteria (Overall)

### Functional Requirements
- ✅ Analytics API endpoints return correct data
- ✅ Frontend displays usage metrics accurately
- ✅ Filters work correctly (time range, category)
- ✅ Charts are interactive and informative
- ✅ Real-time updates within staleTime

### Performance Requirements
- ✅ API responses < 500ms (95th percentile)
- ✅ Tracking overhead < 10ms per tool call
- ✅ Page load < 2 seconds
- ✅ Chart renders < 200ms

### User Experience
- ✅ Clear, intuitive interface
- ✅ Responsive design (mobile + desktop)
- ✅ Proper loading/error/empty states
- ✅ Accessible (WCAG AA compliance)
- ✅ Dark mode support

### Code Quality
- ✅ Comprehensive test coverage
- ✅ Follows codebase patterns
- ✅ Proper TypeScript types
- ✅ Clean, maintainable code
- ✅ Documented

---

## Risk Mitigation

### Potential Issues and Solutions

1. **Materialized View Refresh**:
   - **Risk**: Views not updating
   - **Mitigation**: Manual refresh endpoint + monitoring
   - **Fallback**: Query raw events table directly

2. **Performance Degradation**:
   - **Risk**: Slow queries with large datasets
   - **Mitigation**: Proper indexing + materialized views
   - **Fallback**: Pagination and date range limits

3. **Chart Rendering**:
   - **Risk**: Recharts performance with many data points
   - **Mitigation**: Data aggregation in useMemo
   - **Fallback**: Limit chart data points to 168 max

4. **Browser Compatibility**:
   - **Risk**: Chart not rendering in older browsers
   - **Mitigation**: Polyfills + graceful degradation
   - **Fallback**: Table view of data

---

## Post-Implementation Tasks

After completing all phases:

1. **Deploy to Production**:
   - Run migration on production database
   - Deploy backend changes
   - Deploy frontend changes
   - Monitor for errors

2. **Set Up Monitoring**:
   - Track API error rates
   - Monitor query performance
   - Set up alerts for failures

3. **User Feedback**:
   - Gather user feedback on UI/UX
   - Identify improvement opportunities
   - Plan Phase 2 enhancements

4. **Maintenance Schedule**:
   - Weekly: Review analytics performance
   - Monthly: Check database size and cleanup
   - Quarterly: Review feature usage and optimize

---

## Future Enhancements (Phase 2)

Once MVP is complete and stable:

1. **Advanced Filtering**:
   - Filter by source ID (most queried docs)
   - Filter by success/failure
   - Session-based analysis

2. **Export Functionality**:
   - Export usage data as CSV/JSON
   - Generate PDF reports

3. **Alerting**:
   - Alert on high error rates
   - Alert on unusual patterns

4. **Comparative Analytics**:
   - Week-over-week comparisons
   - Trend analysis
   - Forecasting

5. **Usage Insights**:
   - Most queried knowledge sources
   - Peak usage hours
   - Tool adoption metrics

---

**End of Implementation Plan**

Ready to execute? Run the migration first, then start with Phase 3, Task 3.1!
