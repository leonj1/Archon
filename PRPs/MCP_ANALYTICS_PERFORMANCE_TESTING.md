# MCP Analytics Performance Testing & Optimization Guide

**Version**: 1.0
**Status**: Ready for Use
**Created**: 2025-01-13
**Target Feature**: MCP Usage Analytics
**Related Documents**: MCP_USAGE_ANALYTICS_IMPLEMENTATION_PLAN.md, MCP_USAGE_ANALYTICS_SPEC.md

---

## Table of Contents

1. [Performance Targets](#performance-targets)
2. [Backend Performance Testing](#backend-performance-testing)
3. [Frontend Performance Testing](#frontend-performance-testing)
4. [Database Optimization](#database-optimization)
5. [Profiling Instructions](#profiling-instructions)
6. [Performance Monitoring Setup](#performance-monitoring-setup)
7. [Optimization Recommendations](#optimization-recommendations)
8. [Benchmark Templates](#benchmark-templates)

---

## Performance Targets

### API Response Times
- **Target**: < 500ms (95th percentile)
- **Critical**: < 1000ms (99th percentile)
- **Optimal**: < 200ms (median)

### Tracking Overhead
- **Target**: < 10ms per tool call
- **Critical**: < 50ms per tool call
- **Optimal**: < 5ms per tool call

### Frontend Performance
- **Page Load**: < 2 seconds (initial render)
- **Chart Render**: < 200ms (data to pixels)
- **Filter Response**: < 100ms (interactive feedback)
- **Bundle Impact**: < 100KB gzipped (incremental)

### Database Performance
- **Hourly Query**: < 100ms for 168 hours (7 days)
- **Daily Query**: < 200ms for 180 days
- **Summary Query**: < 150ms
- **Materialized View Refresh**: < 5 seconds

### Lighthouse Scores
- **Performance**: > 90
- **Accessibility**: > 90
- **Best Practices**: > 90
- **SEO**: > 90

---

## Backend Performance Testing

### 1. Load Testing with Apache Bench

#### Test Hourly Endpoint (24 hours)
```bash
# Basic load test: 1000 requests, 10 concurrent
ab -n 1000 -c 10 \
   -H "Accept: application/json" \
   http://localhost:8181/api/mcp/analytics/hourly?hours=24

# Heavy load test: 5000 requests, 50 concurrent
ab -n 5000 -c 50 \
   -H "Accept: application/json" \
   http://localhost:8181/api/mcp/analytics/hourly?hours=24

# Sustained load: 10000 requests, 20 concurrent
ab -n 10000 -c 20 \
   -H "Accept: application/json" \
   http://localhost:8181/api/mcp/analytics/hourly?hours=24
```

#### Test Daily Endpoint (30 days)
```bash
# Standard load
ab -n 1000 -c 10 \
   -H "Accept: application/json" \
   http://localhost:8181/api/mcp/analytics/daily?days=30

# With category filter
ab -n 1000 -c 10 \
   -H "Accept: application/json" \
   http://localhost:8181/api/mcp/analytics/daily?days=30&tool_category=rag
```

#### Test Summary Endpoint
```bash
# High frequency test (simulating dashboard refreshes)
ab -n 2000 -c 20 \
   -H "Accept: application/json" \
   http://localhost:8181/api/mcp/analytics/summary
```

#### Expected Results
```
Concurrency Level:      10
Time taken for tests:   X.XXX seconds
Complete requests:      1000
Failed requests:        0
Requests per second:    > 50.00 [#/sec] (mean)
Time per request:       < 200.000 [ms] (mean)
Time per request:       < 20.000 [ms] (mean, across all concurrent requests)

Percentage of the requests served within a certain time (ms)
  50%    < 150
  66%    < 200
  75%    < 250
  80%    < 300
  90%    < 400
  95%    < 500  ← Target
  98%    < 700
  99%    < 900
 100%    < 1000
```

### 2. Load Testing with wrk (Alternative)

```bash
# Install wrk if not available
# Ubuntu: sudo apt-get install wrk
# macOS: brew install wrk

# 30-second test, 10 connections, 4 threads
wrk -t4 -c10 -d30s \
    -H "Accept: application/json" \
    http://localhost:8181/api/mcp/analytics/hourly?hours=24

# With Lua script for more complex scenarios
cat > analytics_load_test.lua << 'EOF'
request = function()
    local hours = math.random(1, 168)
    local categories = {"rag", "project", "task", "document"}
    local category = categories[math.random(1, #categories)]
    local path = string.format("/api/mcp/analytics/hourly?hours=%d&tool_category=%s", hours, category)
    return wrk.format("GET", path)
end
EOF

wrk -t4 -c20 -d60s -s analytics_load_test.lua http://localhost:8181
```

### 3. Load Testing with Locust (Python-based)

```python
# File: tests/performance/locustfile_analytics.py
from locust import HttpUser, task, between
import random

class AnalyticsUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests

    @task(3)  # Weight: 3x more likely
    def get_hourly_usage(self):
        hours = random.choice([24, 48, 168])
        self.client.get(f"/api/mcp/analytics/hourly?hours={hours}")

    @task(2)
    def get_daily_usage(self):
        days = random.choice([7, 30, 90])
        self.client.get(f"/api/mcp/analytics/daily?days={days}")

    @task(5)  # Most frequent (dashboard refreshes)
    def get_summary(self):
        self.client.get("/api/mcp/analytics/summary")

    @task(1)
    def get_filtered_hourly(self):
        category = random.choice(["rag", "project", "task", "document"])
        self.client.get(f"/api/mcp/analytics/hourly?hours=24&tool_category={category}")

# Run with: locust -f tests/performance/locustfile_analytics.py --host=http://localhost:8181
# Open browser to http://localhost:8089 for web UI
```

### 4. Tracking Overhead Measurement

```python
# File: tests/performance/test_tracking_overhead.py
import time
import pytest
from src.mcp_server.middleware.usage_tracker import usage_tracker

async def test_tracking_overhead():
    """Measure overhead of usage tracking."""

    # Simulate tool call data
    request_data = {
        "query": "test query",
        "source_id": "test_source",
        "match_count": 5
    }

    iterations = 1000
    overhead_times = []

    for _ in range(iterations):
        start = time.perf_counter()

        await usage_tracker.track_tool_usage(
            tool_name="test_tool",
            tool_category="rag",
            request_data=request_data,
            response_data=None,
            response_time_ms=50,
            success=True
        )

        overhead = (time.perf_counter() - start) * 1000  # Convert to ms
        overhead_times.append(overhead)

    # Calculate statistics
    avg_overhead = sum(overhead_times) / len(overhead_times)
    p95_overhead = sorted(overhead_times)[int(0.95 * len(overhead_times))]
    p99_overhead = sorted(overhead_times)[int(0.99 * len(overhead_times))]
    max_overhead = max(overhead_times)

    print(f"\nTracking Overhead Statistics:")
    print(f"  Average: {avg_overhead:.2f}ms")
    print(f"  95th percentile: {p95_overhead:.2f}ms")
    print(f"  99th percentile: {p99_overhead:.2f}ms")
    print(f"  Maximum: {max_overhead:.2f}ms")

    # Assertions
    assert avg_overhead < 10, f"Average overhead {avg_overhead:.2f}ms exceeds 10ms target"
    assert p95_overhead < 20, f"P95 overhead {p95_overhead:.2f}ms exceeds 20ms threshold"

# Run with: pytest tests/performance/test_tracking_overhead.py -v -s
```

### 5. API Profiling with cProfile

```python
# File: tests/performance/profile_analytics_api.py
import cProfile
import pstats
import io
from fastapi.testclient import TestClient
from src.server.main import app

def profile_hourly_endpoint():
    """Profile the hourly analytics endpoint."""
    client = TestClient(app)

    profiler = cProfile.Profile()
    profiler.enable()

    # Make multiple requests
    for _ in range(100):
        response = client.get("/api/mcp/analytics/hourly?hours=24")
        assert response.status_code == 200

    profiler.disable()

    # Print stats
    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
    print(s.getvalue())

if __name__ == "__main__":
    print("Profiling hourly endpoint...")
    profile_hourly_endpoint()

# Run with: python tests/performance/profile_analytics_api.py
```

### 6. Memory Profiling with memory_profiler

```python
# File: tests/performance/memory_profile_analytics.py
from memory_profiler import profile
from fastapi.testclient import TestClient
from src.server.main import app

@profile
def test_hourly_endpoint_memory():
    """Profile memory usage of hourly endpoint."""
    client = TestClient(app)

    for _ in range(50):
        response = client.get("/api/mcp/analytics/hourly?hours=168")
        data = response.json()
        # Ensure we're processing the data
        _ = len(data.get('data', []))

if __name__ == "__main__":
    test_hourly_endpoint_memory()

# Run with: python -m memory_profiler tests/performance/memory_profile_analytics.py
```

---

## Frontend Performance Testing

### 1. React DevTools Profiler

#### Setup
1. Install React DevTools browser extension
2. Open DevTools → Profiler tab
3. Click "Record" before performing actions

#### Test Scenarios

**Scenario 1: Initial Page Load**
```
1. Navigate to Settings page
2. Expand MCP Analytics section
3. Record time to interactive (TTI)
4. Check for unnecessary re-renders
```

**Scenario 2: Filter Changes**
```
1. Start profiling
2. Change time range filter (24h → 48h → 7d)
3. Stop profiling
4. Analyze component render times
5. Identify slow components
```

**Scenario 3: Data Refresh**
```
1. Start profiling
2. Wait for automatic data refresh (staleTime expiry)
3. Stop profiling
4. Check query execution time
5. Verify no cascading re-renders
```

#### Expected Results
- Initial render: < 500ms
- Filter change response: < 100ms
- Chart re-render: < 200ms
- No unnecessary component updates

### 2. Chrome DevTools Performance

#### Recording a Performance Profile

```bash
# Steps:
1. Open Chrome DevTools (F12)
2. Go to Performance tab
3. Click "Record" (Ctrl+E)
4. Perform actions (load page, change filters, etc.)
5. Click "Stop" (Ctrl+E)
6. Analyze the flame chart
```

#### Key Metrics to Check

**Loading Performance**
- First Contentful Paint (FCP): < 1.5s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3.5s
- Total Blocking Time (TBT): < 300ms

**Runtime Performance**
- Long tasks: None > 50ms
- Layout shifts (CLS): < 0.1
- JavaScript execution time: < 500ms
- Render time: < 200ms

#### Analyzing Results

```javascript
// Look for:
// 1. Long tasks (yellow bars > 50ms)
// 2. Layout thrashing (purple spikes)
// 3. JavaScript execution bottlenecks
// 4. Network waterfall delays
// 5. Forced reflows/repaints

// Common issues:
// - Expensive chart calculations in render
// - Missing useMemo for data transformations
// - Unnecessary useEffect dependencies
// - Large bundle sizes blocking main thread
```

### 3. Lighthouse Performance Audit

#### Running Lighthouse

```bash
# CLI method (recommended for CI/CD)
npm install -g lighthouse

# Run audit on analytics page
lighthouse http://localhost:3737/settings \
    --output=html \
    --output=json \
    --output-path=./lighthouse-analytics-report \
    --only-categories=performance,accessibility \
    --chrome-flags="--headless"

# Open report
open lighthouse-analytics-report.report.html
```

#### DevTools Method
```
1. Open Chrome DevTools
2. Go to Lighthouse tab
3. Select categories: Performance, Accessibility, Best Practices
4. Click "Analyze page load"
5. Review report
```

#### Expected Scores
```
Performance:         > 90  (Target: 95+)
Accessibility:       > 90  (Target: 100)
Best Practices:      > 90  (Target: 100)
SEO:                 > 90  (Target: 95+)
```

### 4. Bundle Size Analysis

```bash
# Analyze bundle size impact
cd archon-ui-main

# Build with analysis
npm run build -- --mode=production

# Use webpack-bundle-analyzer
npx vite-bundle-visualizer

# Check for:
# 1. Recharts size impact (should be < 100KB gzipped)
# 2. Code splitting effectiveness
# 3. Duplicate dependencies
# 4. Unused exports

# Expected bundle sizes:
# - Main bundle: < 500KB gzipped
# - Analytics chunk: < 100KB gzipped
# - Total increase: < 150KB gzipped
```

### 5. Chart Render Performance Testing

```typescript
// File: archon-ui-main/src/features/mcp/tests/performance/ChartPerformance.test.tsx
import { render, waitFor } from '@testing-library/react';
import { MCPUsageAnalytics } from '../components/MCPUsageAnalytics';
import { QueryClientProvider } from '@tanstack/react-query';
import { createQueryClient } from '@/features/shared/config/queryClient';

describe('Chart Render Performance', () => {
  it('should render large datasets within 200ms', async () => {
    // Generate large dataset (168 hours, multiple tools)
    const largeDataset = generateMockData(168, 10); // 168 hours, 10 tools

    const startTime = performance.now();

    const { container } = render(
      <QueryClientProvider client={createQueryClient()}>
        <MCPUsageAnalytics />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(container.querySelector('svg')).toBeInTheDocument();
    });

    const renderTime = performance.now() - startTime;

    console.log(`Chart render time: ${renderTime.toFixed(2)}ms`);
    expect(renderTime).toBeLessThan(200);
  });

  it('should handle filter changes quickly', async () => {
    const { container, rerender } = render(
      <QueryClientProvider client={createQueryClient()}>
        <MCPUsageAnalytics />
      </QueryClientProvider>
    );

    // Change filter and measure re-render
    const startTime = performance.now();

    rerender(
      <QueryClientProvider client={createQueryClient()}>
        <MCPUsageAnalytics />
      </QueryClientProvider>
    );

    const rerenderTime = performance.now() - startTime;

    console.log(`Filter change re-render time: ${rerenderTime.toFixed(2)}ms`);
    expect(rerenderTime).toBeLessThan(100);
  });
});

function generateMockData(hours: number, toolsPerHour: number) {
  // Generate realistic mock data
  const data = [];
  for (let h = 0; h < hours; h++) {
    for (let t = 0; t < toolsPerHour; t++) {
      data.push({
        hour_bucket: new Date(Date.now() - h * 3600000).toISOString(),
        tool_name: `tool_${t}`,
        tool_category: 'rag',
        call_count: Math.floor(Math.random() * 100),
        error_count: Math.floor(Math.random() * 10),
        avg_response_time_ms: Math.random() * 500,
        unique_sessions: Math.floor(Math.random() * 50),
      });
    }
  }
  return data;
}
```

### 6. React Query Performance

```typescript
// File: archon-ui-main/src/features/mcp/tests/performance/QueryPerformance.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClientProvider } from '@tanstack/react-query';
import { createQueryClient } from '@/features/shared/config/queryClient';
import { useMcpHourlyUsage } from '../hooks/useMcpAnalytics';

describe('React Query Performance', () => {
  it('should deduplicate concurrent requests', async () => {
    let fetchCount = 0;

    // Mock service to count fetches
    jest.mock('../services/mcpAnalyticsService', () => ({
      mcpAnalyticsService: {
        getHourlyUsage: async () => {
          fetchCount++;
          return mockData;
        }
      }
    }));

    const queryClient = createQueryClient();

    // Render hook multiple times concurrently
    const { result: result1 } = renderHook(
      () => useMcpHourlyUsage(24),
      { wrapper: ({ children }) => <QueryClientProvider client={queryClient}>{children}</QueryClientProvider> }
    );

    const { result: result2 } = renderHook(
      () => useMcpHourlyUsage(24),
      { wrapper: ({ children }) => <QueryClientProvider client={queryClient}>{children}</QueryClientProvider> }
    );

    await waitFor(() => {
      expect(result1.current.isSuccess).toBe(true);
      expect(result2.current.isSuccess).toBe(true);
    });

    // Should only fetch once due to deduplication
    expect(fetchCount).toBe(1);
  });

  it('should respect staleTime configuration', async () => {
    // Test that queries don't refetch unnecessarily
    const { result, rerender } = renderHook(
      () => useMcpHourlyUsage(24),
      { wrapper: QueryWrapper }
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    const firstFetchTime = Date.now();

    // Trigger re-render within staleTime
    rerender();

    // Should use cached data
    expect(result.current.isFetching).toBe(false);

    // Wait for staleTime to expire (5 seconds for frequent)
    await new Promise(resolve => setTimeout(resolve, 5100));

    rerender();

    // Should refetch after staleTime
    expect(result.current.isFetching).toBe(true);
  });
});
```

---

## Database Optimization

### 1. Query Performance Analysis

#### Test Hourly Query
```sql
EXPLAIN ANALYZE
SELECT *
FROM archon_mcp_usage_hourly
WHERE hour_bucket >= NOW() - INTERVAL '24 hours'
ORDER BY hour_bucket DESC;

-- Expected output:
-- Seq Scan on archon_mcp_usage_hourly (cost=0.00..X rows=Y width=Z)
--   Filter: (hour_bucket >= ...)
--   Planning Time: < 1 ms
--   Execution Time: < 50 ms
```

#### Test Hourly Query with Filters
```sql
EXPLAIN ANALYZE
SELECT *
FROM archon_mcp_usage_hourly
WHERE hour_bucket >= NOW() - INTERVAL '168 hours'
  AND tool_category = 'rag'
ORDER BY hour_bucket DESC;

-- Check for:
-- 1. Index usage (Index Scan vs Seq Scan)
-- 2. Filter pushdown
-- 3. Low cost estimate
-- 4. Fast execution time
```

#### Test Daily Query
```sql
EXPLAIN ANALYZE
SELECT *
FROM archon_mcp_usage_daily
WHERE date_bucket >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY date_bucket DESC;

-- Expected execution time: < 100 ms
```

#### Test Summary Query (Raw Events)
```sql
EXPLAIN ANALYZE
SELECT
    tool_name,
    tool_category,
    COUNT(*) as call_count,
    COUNT(*) FILTER (WHERE success = false) as error_count
FROM archon_mcp_usage_events
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY tool_name, tool_category
ORDER BY call_count DESC
LIMIT 10;

-- Expected execution time: < 200 ms
-- Should use index on timestamp
```

### 2. Index Usage Verification

```sql
-- Check if indexes are being used
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename IN (
    'archon_mcp_usage_events',
    'archon_mcp_usage_hourly',
    'archon_mcp_usage_daily'
)
ORDER BY idx_scan DESC;

-- Expected:
-- idx_mcp_usage_timestamp: High idx_scan count
-- idx_mcp_usage_hour_bucket: Moderate idx_scan count
-- idx_mcp_usage_category: Moderate idx_scan count
```

### 3. Table Statistics

```sql
-- Check table sizes and row counts
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    n_live_tup as row_count,
    n_dead_tup as dead_rows,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE tablename LIKE 'archon_mcp%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Expected after 180 days at 1000 calls/day:
-- archon_mcp_usage_events: ~50-100 MB
-- archon_mcp_usage_hourly: < 5 MB
-- archon_mcp_usage_daily: < 1 MB
```

### 4. Materialized View Performance

```sql
-- Test materialized view refresh time
\timing on

-- Refresh hourly view
REFRESH MATERIALIZED VIEW CONCURRENTLY archon_mcp_usage_hourly;
-- Expected: < 3 seconds

-- Refresh daily view
REFRESH MATERIALIZED VIEW CONCURRENTLY archon_mcp_usage_daily;
-- Expected: < 2 seconds

\timing off

-- Check view sizes
SELECT
    schemaname,
    matviewname,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||matviewname)) AS size
FROM pg_matviews
WHERE matviewname LIKE 'archon_mcp%';
```

### 5. Slow Query Detection

```sql
-- Enable slow query logging (requires superuser)
-- Add to postgresql.conf or set via Supabase dashboard:
-- log_min_duration_statement = 100  -- Log queries > 100ms

-- Check pg_stat_statements for slow queries
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
WHERE query LIKE '%archon_mcp%'
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Expected:
-- All mean_exec_time < 500ms
-- No queries with max_exec_time > 1000ms
```

### 6. Database Connection Pooling

```sql
-- Check active connections
SELECT
    count(*) as connection_count,
    state,
    wait_event_type
FROM pg_stat_activity
WHERE datname = current_database()
GROUP BY state, wait_event_type;

-- Expected:
-- Active connections: < 10 under normal load
-- Idle connections: Depends on pool configuration
-- No long-running queries (> 5 seconds)
```

### 7. Vacuum and Analyze

```sql
-- Manually trigger vacuum/analyze if needed
VACUUM ANALYZE archon_mcp_usage_events;
VACUUM ANALYZE archon_mcp_usage_hourly;
VACUUM ANALYZE archon_mcp_usage_daily;

-- Check if autovacuum is keeping up
SELECT
    schemaname,
    tablename,
    n_dead_tup,
    n_live_tup,
    n_dead_tup::float / NULLIF(n_live_tup, 0) as dead_ratio,
    last_autovacuum
FROM pg_stat_user_tables
WHERE tablename LIKE 'archon_mcp%'
ORDER BY n_dead_tup DESC;

-- Expected dead_ratio: < 0.1 (< 10% dead tuples)
```

---

## Profiling Instructions

### Backend Profiling with py-spy

```bash
# Install py-spy
pip install py-spy

# Profile running MCP server
py-spy record -o profile.svg --pid <MCP_SERVER_PID>

# Or profile from start
py-spy record -o profile.svg -- python -m src.mcp_server.main

# Generate flamegraph (opens in browser)
py-spy record -o profile.svg -F --duration 60 --pid <PID>

# Top function report
py-spy top --pid <PID>
```

### Backend Profiling with Pydantic Logfire

```python
# Archon already uses Logfire - leverage it for profiling

# File: python/src/server/api_routes/mcp_analytics_api.py
from src.server.config.logfire_config import safe_span, get_logger

@router.get("/hourly")
async def get_hourly_usage(...):
    with safe_span("mcp_analytics.get_hourly", hours=hours, category=tool_category):
        # Existing implementation
        pass

# View traces in Logfire dashboard
# Look for slow spans and high call counts
```

### Frontend Profiling with Chrome DevTools

```javascript
// Add performance marks in code
// File: archon-ui-main/src/features/mcp/components/MCPUsageAnalytics.tsx

useEffect(() => {
  performance.mark('analytics-component-mount');

  return () => {
    performance.mark('analytics-component-unmount');
    performance.measure(
      'analytics-component-lifetime',
      'analytics-component-mount',
      'analytics-component-unmount'
    );

    const measures = performance.getEntriesByType('measure');
    console.log('Component performance:', measures);
  };
}, []);

// Chart render timing
const chartData = useMemo(() => {
  performance.mark('chart-data-start');

  // Data transformation logic
  const result = transformData(hourlyData);

  performance.mark('chart-data-end');
  performance.measure('chart-data-transform', 'chart-data-start', 'chart-data-end');

  return result;
}, [hourlyData]);
```

### React Query DevTools

```typescript
// File: archon-ui-main/src/main.tsx (add for development)
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  );
}

// Use DevTools to:
// 1. Monitor query states
// 2. Check cache hit rates
// 3. Identify slow queries
// 4. Debug stale/refetch behavior
```

---

## Performance Monitoring Setup

### 1. Backend Monitoring with Logfire

```python
# File: python/src/mcp_server/middleware/usage_tracker.py
from src.server.config.logfire_config import safe_span

async def track_tool_usage(...):
    with safe_span("mcp.track_usage", tool_name=tool_name, category=tool_category):
        # Track timing of database insert
        insert_start = time.perf_counter()

        try:
            self.supabase.table('archon_mcp_usage_events').insert(event_data).execute()

            insert_time = (time.perf_counter() - insert_start) * 1000
            logfire.metric('mcp.tracking.insert_time', insert_time, unit='ms')

            # Alert if tracking is slow
            if insert_time > 50:
                logfire.warn(
                    'Slow tracking insert',
                    insert_time=insert_time,
                    tool_name=tool_name
                )

        except Exception as e:
            logfire.error('Tracking failed', error=str(e), exc_info=True)
```

### 2. Frontend Monitoring with Performance Observer

```typescript
// File: archon-ui-main/src/features/mcp/hooks/useAnalyticsPerformance.ts
import { useEffect } from 'react';

export function useAnalyticsPerformance() {
  useEffect(() => {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        // Log long tasks (> 50ms)
        if (entry.duration > 50) {
          console.warn('Long task detected:', {
            name: entry.name,
            duration: entry.duration,
            startTime: entry.startTime,
          });
        }

        // Track specific metrics
        if (entry.entryType === 'measure') {
          console.log('Performance measure:', {
            name: entry.name,
            duration: entry.duration,
          });
        }
      }
    });

    observer.observe({ entryTypes: ['longtask', 'measure'] });

    return () => observer.disconnect();
  }, []);
}

// Use in MCPUsageAnalytics component
export const MCPUsageAnalytics = () => {
  useAnalyticsPerformance();
  // ... rest of component
};
```

### 3. Custom Metrics Collection

```typescript
// File: archon-ui-main/src/features/mcp/utils/performanceMetrics.ts
class AnalyticsPerformanceMetrics {
  private metrics: Map<string, number[]> = new Map();

  recordMetric(name: string, value: number) {
    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }
    this.metrics.get(name)!.push(value);
  }

  getStats(name: string) {
    const values = this.metrics.get(name) || [];
    if (values.length === 0) return null;

    const sorted = [...values].sort((a, b) => a - b);
    return {
      count: values.length,
      mean: values.reduce((a, b) => a + b) / values.length,
      median: sorted[Math.floor(values.length / 2)],
      p95: sorted[Math.floor(values.length * 0.95)],
      p99: sorted[Math.floor(values.length * 0.99)],
      min: sorted[0],
      max: sorted[sorted.length - 1],
    };
  }

  reportAll() {
    console.group('Analytics Performance Metrics');
    for (const [name, _] of this.metrics) {
      console.log(`${name}:`, this.getStats(name));
    }
    console.groupEnd();
  }
}

export const performanceMetrics = new AnalyticsPerformanceMetrics();

// Usage in component
const startTime = performance.now();
// ... some operation
performanceMetrics.recordMetric('chart-render', performance.now() - startTime);
```

### 4. Database Monitoring Queries

```sql
-- Create monitoring view
CREATE OR REPLACE VIEW mcp_analytics_performance AS
SELECT
    'hourly_view_size' as metric,
    pg_size_pretty(pg_total_relation_size('archon_mcp_usage_hourly')) as value
UNION ALL
SELECT
    'daily_view_size',
    pg_size_pretty(pg_total_relation_size('archon_mcp_usage_daily'))
UNION ALL
SELECT
    'events_table_size',
    pg_size_pretty(pg_total_relation_size('archon_mcp_usage_events'))
UNION ALL
SELECT
    'total_events',
    COUNT(*)::text
FROM archon_mcp_usage_events
UNION ALL
SELECT
    'events_last_24h',
    COUNT(*)::text
FROM archon_mcp_usage_events
WHERE timestamp >= NOW() - INTERVAL '24 hours';

-- Query periodically
SELECT * FROM mcp_analytics_performance;
```

---

## Optimization Recommendations

### Backend Optimizations

#### 1. Database Query Optimization

```sql
-- Add composite index for common filter combinations
CREATE INDEX CONCURRENTLY idx_mcp_usage_hourly_category_hour
ON archon_mcp_usage_hourly(tool_category, hour_bucket DESC);

-- Add index for tool name filtering
CREATE INDEX CONCURRENTLY idx_mcp_usage_hourly_tool_hour
ON archon_mcp_usage_hourly(tool_name, hour_bucket DESC);

-- Partial index for recent data (most queried)
CREATE INDEX CONCURRENTLY idx_mcp_usage_events_recent
ON archon_mcp_usage_events(timestamp DESC)
WHERE timestamp >= NOW() - INTERVAL '7 days';
```

#### 2. Materialized View Optimization

```sql
-- Use CONCURRENTLY to avoid locking
REFRESH MATERIALIZED VIEW CONCURRENTLY archon_mcp_usage_hourly;

-- Create function for automatic refresh
CREATE OR REPLACE FUNCTION refresh_mcp_usage_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY archon_mcp_usage_hourly;
    REFRESH MATERIALIZED VIEW CONCURRENTLY archon_mcp_usage_daily;
END;
$$ LANGUAGE plpgsql;

-- Schedule with pg_cron (if available)
SELECT cron.schedule(
    'refresh-mcp-views',
    '*/15 * * * *',  -- Every 15 minutes
    'SELECT refresh_mcp_usage_views();'
);
```

#### 3. API Response Optimization

```python
# File: python/src/server/api_routes/mcp_analytics_api.py
from fastapi import Request, Response
from src.server.utils.etag_utils import generate_etag, check_etag

@router.get("/hourly")
async def get_hourly_usage(request: Request, response: Response, ...):
    """Get hourly usage with ETag caching."""

    # Build query (existing code)
    result = query.execute()

    # Generate ETag
    etag = generate_etag(result.data)

    # Check if client has cached version
    if check_etag(request.headers.get("if-none-match"), etag):
        return Response(status_code=304)  # Not Modified

    # Set ETag header
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "no-cache, must-revalidate"

    return {
        "success": True,
        "data": result.data,
        "time_range": {...}
    }
```

#### 4. Connection Pool Tuning

```python
# File: python/src/server/config/database.py
from supabase import create_client

# Configure connection pooling
supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_KEY,
    options={
        "postgrest": {
            "pool_size": 20,  # Adjust based on load
            "pool_max_overflow": 10,
            "pool_timeout": 30,
            "pool_recycle": 3600,
        }
    }
)
```

### Frontend Optimizations

#### 1. Data Transformation Memoization

```typescript
// File: archon-ui-main/src/features/mcp/components/MCPUsageAnalytics.tsx
import { useMemo } from 'react';

const chartData = useMemo(() => {
  if (!hourlyData) return [];

  // Expensive aggregation - memoize it
  const aggregated = hourlyData.reduce((acc, item) => {
    const hour = new Date(item.hour_bucket).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
    });

    if (!acc[hour]) {
      acc[hour] = { hour, total: 0, errors: 0 };
    }

    acc[hour].total += item.call_count;
    acc[hour].errors += item.error_count;

    return acc;
  }, {} as Record<string, { hour: string; total: number; errors: number }>);

  return Object.values(aggregated);
}, [hourlyData]);  // Only recompute when data changes
```

#### 2. Chart Component Optimization

```typescript
// Use React.memo for expensive sub-components
const AnalyticsChart = React.memo(({ data }: { data: ChartData[] }) => {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={data}>
        {/* Chart configuration */}
      </BarChart>
    </ResponsiveContainer>
  );
}, (prevProps, nextProps) => {
  // Custom comparison - only re-render if data actually changed
  return JSON.stringify(prevProps.data) === JSON.stringify(nextProps.data);
});
```

#### 3. Query Configuration Optimization

```typescript
// File: archon-ui-main/src/features/mcp/hooks/useMcpAnalytics.ts
export function useMcpHourlyUsage(hours: number = 24, category?: string) {
  return useQuery({
    queryKey: mcpAnalyticsKeys.hourly(hours, category),
    queryFn: () => mcpAnalyticsService.getHourlyUsage(hours, category),
    staleTime: STALE_TIMES.frequent,  // 5 seconds
    gcTime: 1000 * 60 * 10,            // Keep in cache for 10 minutes
    refetchOnWindowFocus: false,        // Don't refetch on focus
    refetchOnReconnect: false,          // Don't refetch on reconnect
    retry: 1,                           // Only retry once on failure
  });
}
```

#### 4. Lazy Loading and Code Splitting

```typescript
// File: archon-ui-main/src/pages/SettingsPage.tsx
import { lazy, Suspense } from 'react';

// Lazy load analytics component
const MCPUsageAnalytics = lazy(() =>
  import('@/features/mcp/components/MCPUsageAnalytics').then(module => ({
    default: module.MCPUsageAnalytics
  }))
);

// Use with Suspense
<Suspense fallback={<AnalyticsLoadingSkeleton />}>
  <MCPUsageAnalytics />
</Suspense>
```

#### 5. Virtualization for Large Tables

```typescript
// If top tools table becomes large, use virtualization
import { useVirtualizer } from '@tanstack/react-virtual';

function TopToolsTable({ tools }: { tools: ToolData[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: tools.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 40,  // Row height
    overscan: 5,
  });

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
        {virtualizer.getVirtualItems().map(virtualRow => (
          <div
            key={virtualRow.index}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualRow.size}px`,
              transform: `translateY(${virtualRow.start}px)`,
            }}
          >
            {tools[virtualRow.index].tool_name} - {tools[virtualRow.index].calls}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## Benchmark Templates

### Backend Benchmark Template

```python
# File: tests/performance/benchmark_analytics_api.py
import time
import statistics
from typing import List
from fastapi.testclient import TestClient
from src.server.main import app

def benchmark_endpoint(
    endpoint: str,
    iterations: int = 100,
    warmup: int = 10
) -> dict:
    """Benchmark an API endpoint."""
    client = TestClient(app)

    # Warmup requests
    for _ in range(warmup):
        client.get(endpoint)

    # Benchmark requests
    times: List[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        response = client.get(endpoint)
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms

        assert response.status_code == 200
        times.append(elapsed)

    # Calculate statistics
    sorted_times = sorted(times)
    return {
        'endpoint': endpoint,
        'iterations': iterations,
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'stdev': statistics.stdev(times),
        'min': min(times),
        'max': max(times),
        'p50': sorted_times[int(0.50 * len(sorted_times))],
        'p75': sorted_times[int(0.75 * len(sorted_times))],
        'p90': sorted_times[int(0.90 * len(sorted_times))],
        'p95': sorted_times[int(0.95 * len(sorted_times))],
        'p99': sorted_times[int(0.99 * len(sorted_times))],
    }

def print_benchmark_results(results: dict):
    """Pretty print benchmark results."""
    print(f"\n{'='*60}")
    print(f"Benchmark: {results['endpoint']}")
    print(f"Iterations: {results['iterations']}")
    print(f"{'='*60}")
    print(f"Mean:     {results['mean']:>8.2f} ms")
    print(f"Median:   {results['median']:>8.2f} ms")
    print(f"Std Dev:  {results['stdev']:>8.2f} ms")
    print(f"Min:      {results['min']:>8.2f} ms")
    print(f"Max:      {results['max']:>8.2f} ms")
    print(f"{'-'*60}")
    print(f"P50:      {results['p50']:>8.2f} ms")
    print(f"P75:      {results['p75']:>8.2f} ms")
    print(f"P90:      {results['p90']:>8.2f} ms")
    print(f"P95:      {results['p95']:>8.2f} ms  ← Target")
    print(f"P99:      {results['p99']:>8.2f} ms")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    endpoints = [
        "/api/mcp/analytics/hourly?hours=24",
        "/api/mcp/analytics/hourly?hours=168",
        "/api/mcp/analytics/daily?days=30",
        "/api/mcp/analytics/summary",
    ]

    print("\n🔥 MCP Analytics API Benchmark")
    print(f"Target: P95 < 500ms\n")

    for endpoint in endpoints:
        results = benchmark_endpoint(endpoint, iterations=100)
        print_benchmark_results(results)

        # Check if target is met
        if results['p95'] > 500:
            print(f"⚠️  WARNING: P95 ({results['p95']:.2f}ms) exceeds 500ms target!\n")
        else:
            print(f"✅ P95 ({results['p95']:.2f}ms) meets target (<500ms)\n")
```

### Frontend Benchmark Template

```typescript
// File: archon-ui-main/src/features/mcp/tests/benchmark/ChartBenchmark.ts
interface BenchmarkResult {
  name: string;
  mean: number;
  median: number;
  p95: number;
  p99: number;
  samples: number;
}

function benchmarkFunction(
  name: string,
  fn: () => void,
  iterations: number = 100
): BenchmarkResult {
  const times: number[] = [];

  // Warmup
  for (let i = 0; i < 10; i++) {
    fn();
  }

  // Benchmark
  for (let i = 0; i < iterations; i++) {
    const start = performance.now();
    fn();
    const elapsed = performance.now() - start;
    times.push(elapsed);
  }

  const sorted = [...times].sort((a, b) => a - b);
  const mean = times.reduce((a, b) => a + b) / times.length;
  const median = sorted[Math.floor(sorted.length / 2)];
  const p95 = sorted[Math.floor(sorted.length * 0.95)];
  const p99 = sorted[Math.floor(sorted.length * 0.99)];

  return { name, mean, median, p95, p99, samples: iterations };
}

function printBenchmarkResult(result: BenchmarkResult) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`Benchmark: ${result.name}`);
  console.log(`Samples: ${result.samples}`);
  console.log(`${'='.repeat(60)}`);
  console.log(`Mean:     ${result.mean.toFixed(2)} ms`);
  console.log(`Median:   ${result.median.toFixed(2)} ms`);
  console.log(`${'-'.repeat(60)}`);
  console.log(`P95:      ${result.p95.toFixed(2)} ms  ← Target`);
  console.log(`P99:      ${result.p99.toFixed(2)} ms`);
  console.log(`${'='.repeat(60)}\n`);

  if (result.p95 > 200) {
    console.warn(`⚠️  WARNING: P95 exceeds 200ms target!`);
  } else {
    console.log(`✅ P95 meets target (<200ms)`);
  }
}

// Example usage
const chartData = generateMockData(168, 10);

const dataTransformResult = benchmarkFunction(
  'Chart Data Transformation',
  () => {
    const aggregated = chartData.reduce((acc, item) => {
      // Transformation logic
      return acc;
    }, {});
  },
  100
);

printBenchmarkResult(dataTransformResult);
```

### Database Query Benchmark Template

```sql
-- File: tests/performance/benchmark_queries.sql

-- Create benchmark function
CREATE OR REPLACE FUNCTION benchmark_query(
    query_name TEXT,
    query_sql TEXT,
    iterations INT DEFAULT 100
)
RETURNS TABLE (
    query_name TEXT,
    mean_time NUMERIC,
    median_time NUMERIC,
    p95_time NUMERIC,
    min_time NUMERIC,
    max_time NUMERIC
) AS $$
DECLARE
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    elapsed_ms NUMERIC;
    times NUMERIC[];
    sorted_times NUMERIC[];
BEGIN
    times := ARRAY[]::NUMERIC[];

    -- Run query multiple times
    FOR i IN 1..iterations LOOP
        start_time := clock_timestamp();

        -- Execute query
        EXECUTE query_sql;

        end_time := clock_timestamp();
        elapsed_ms := EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
        times := array_append(times, elapsed_ms);
    END LOOP;

    -- Sort times for percentiles
    sorted_times := (SELECT ARRAY_AGG(t ORDER BY t) FROM unnest(times) t);

    -- Calculate statistics
    RETURN QUERY SELECT
        benchmark_query.query_name,
        (SELECT AVG(t) FROM unnest(times) t),
        sorted_times[iterations / 2],
        sorted_times[(iterations * 95) / 100],
        sorted_times[1],
        sorted_times[iterations];
END;
$$ LANGUAGE plpgsql;

-- Benchmark hourly query
SELECT * FROM benchmark_query(
    'Hourly Query (24h)',
    $$SELECT * FROM archon_mcp_usage_hourly WHERE hour_bucket >= NOW() - INTERVAL '24 hours'$$,
    100
);

-- Benchmark daily query
SELECT * FROM benchmark_query(
    'Daily Query (30d)',
    $$SELECT * FROM archon_mcp_usage_daily WHERE date_bucket >= CURRENT_DATE - INTERVAL '30 days'$$,
    100
);

-- Benchmark summary query
SELECT * FROM benchmark_query(
    'Summary Query',
    $$SELECT tool_name, COUNT(*) FROM archon_mcp_usage_events
      WHERE timestamp >= NOW() - INTERVAL '24 hours'
      GROUP BY tool_name$$,
    100
);
```

---

## Performance Testing Checklist

### Pre-Testing
- [ ] Database has representative data (at least 7 days of usage)
- [ ] Materialized views are up to date
- [ ] Backend and frontend servers are running in production mode
- [ ] No other heavy processes running on test machine
- [ ] Browser cache cleared for frontend tests

### Backend Testing
- [ ] Run Apache Bench tests for all endpoints
- [ ] Verify P95 response times < 500ms
- [ ] Check tracking overhead < 10ms
- [ ] Test with concurrent users (10-50)
- [ ] Monitor database connection pool usage
- [ ] Profile slow queries with EXPLAIN ANALYZE
- [ ] Check memory usage under load

### Frontend Testing
- [ ] Run Lighthouse audit (score > 90)
- [ ] Measure initial page load time < 2s
- [ ] Test chart render performance < 200ms
- [ ] Profile with React DevTools
- [ ] Check bundle size impact < 100KB gzipped
- [ ] Test on mobile devices
- [ ] Verify smooth filter transitions

### Database Testing
- [ ] Run EXPLAIN ANALYZE on all queries
- [ ] Verify index usage with pg_stat_user_indexes
- [ ] Check materialized view refresh time < 5s
- [ ] Monitor table sizes and growth rate
- [ ] Test query performance with 180 days of data

### Optimization
- [ ] Add missing indexes if needed
- [ ] Implement query result caching
- [ ] Optimize data transformations with useMemo
- [ ] Enable ETag caching for API endpoints
- [ ] Consider lazy loading for analytics component

### Monitoring
- [ ] Set up Logfire spans for backend
- [ ] Add performance marks for frontend
- [ ] Create dashboard for key metrics
- [ ] Configure alerts for slow queries
- [ ] Document baseline performance metrics

---

## Troubleshooting Performance Issues

### Slow API Responses

**Symptoms**: API responses > 500ms
**Diagnosis**:
```sql
-- Check for missing indexes
SELECT * FROM pg_stat_user_tables
WHERE tablename LIKE 'archon_mcp%'
AND seq_scan > idx_scan;

-- Check for slow queries
EXPLAIN ANALYZE [your slow query];
```

**Solutions**:
- Add missing indexes
- Refresh materialized views
- Optimize query filters
- Enable connection pooling

### High Tracking Overhead

**Symptoms**: Tool calls taking longer than expected
**Diagnosis**:
```python
# Add timing to tracking middleware
import time
start = time.perf_counter()
# ... tracking code ...
overhead = (time.perf_counter() - start) * 1000
print(f"Tracking overhead: {overhead:.2f}ms")
```

**Solutions**:
- Use fire-and-forget pattern
- Batch inserts if needed
- Reduce request_metadata size
- Check database connection latency

### Slow Chart Rendering

**Symptoms**: Chart takes > 200ms to render
**Diagnosis**:
```typescript
performance.mark('chart-start');
// ... chart render ...
performance.mark('chart-end');
performance.measure('chart-render', 'chart-start', 'chart-end');
console.log(performance.getEntriesByName('chart-render'));
```

**Solutions**:
- Memoize data transformations with useMemo
- Reduce data points (aggregate before sending)
- Use React.memo for chart component
- Consider virtualization for large datasets

### Large Bundle Size

**Symptoms**: Bundle size increase > 100KB
**Diagnosis**:
```bash
npx vite-bundle-visualizer
```

**Solutions**:
- Lazy load analytics component
- Tree-shake unused Recharts components
- Check for duplicate dependencies
- Consider lighter chart library

---

## Continuous Performance Monitoring

### Daily Checks
- API response times (Logfire dashboard)
- Database query performance
- Error rates

### Weekly Checks
- Lighthouse audit scores
- Bundle size analysis
- User-reported performance issues

### Monthly Checks
- Load testing regression tests
- Database growth and cleanup
- Query optimization review

---

**End of Performance Testing Guide**

For implementation details, see:
- MCP_USAGE_ANALYTICS_IMPLEMENTATION_PLAN.md (Task 6.2)
- MCP_USAGE_ANALYTICS_SPEC.md (Section 6.1)

Questions or issues? Create a benchmark report and share with the team.
