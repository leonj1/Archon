# MCP Server Usage Analytics - Feature Specification

**Version**: 1.0
**Status**: Draft
**Created**: 2025-01-13
**Author**: AI Assistant (via Claude Code)
**Project**: Archon V2 Beta

---

## 1. Executive Summary

Implement comprehensive usage analytics for the Archon MCP server to track tool invocations, API calls, and session metrics. Data will be stored in a time-series optimized structure with 180-day retention, enabling hourly aggregation visualizations via bar charts in the Settings UI.

### Goals
- Track all MCP tool calls with metadata (tool name, source ID, query details)
- Store time-series data efficiently with 180-day retention
- Aggregate usage metrics by hour for visualization
- Display interactive bar charts in Settings page
- Enable usage pattern analysis and optimization insights

### Success Metrics
- < 10ms overhead per MCP tool invocation
- 180 days of historical data retained
- < 500ms query time for hourly aggregations
- Real-time chart updates (< 3 second latency)

---

## 2. Architecture Overview

### 2.1 Data Storage Strategy

**Option A: PostgreSQL with TimescaleDB extension** (Recommended)
- Leverage existing Supabase PostgreSQL database
- TimescaleDB provides automatic chunking and compression
- Native SQL support, excellent for time-series aggregations
- Automatic data retention policies

**Option B: Embedded TimescaleDB (if Supabase doesn't support)**
- PostgreSQL table with partitioning by date
- Manual aggregation tables for performance
- Scheduled cleanup jobs for 180-day retention

**Decision**: Use PostgreSQL with manual time-series optimization (Supabase compatible)

### 2.2 Database Schema

```sql
-- Main usage events table (time-series data)
CREATE TABLE archon_mcp_usage_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- MCP tool metadata
    tool_name TEXT NOT NULL,
    tool_category TEXT NOT NULL, -- 'rag', 'project', 'task', 'document', 'health'

    -- Session context
    session_id TEXT,
    client_type TEXT, -- 'claude-code', 'cursor', 'windsurf', 'unknown'

    -- Request details
    request_metadata JSONB, -- Flexible JSON for tool-specific data
    source_id TEXT, -- For RAG queries
    query_text TEXT, -- For search operations (first 500 chars)
    match_count INT, -- For RAG queries

    -- Response metadata
    response_time_ms INT, -- Time taken to process
    success BOOLEAN NOT NULL DEFAULT true,
    error_type TEXT, -- If failed

    -- Aggregation helpers
    hour_bucket TIMESTAMPTZ GENERATED ALWAYS AS (date_trunc('hour', timestamp)) STORED,
    date_bucket DATE GENERATED ALWAYS AS (DATE(timestamp)) STORED
);

-- Indexes for fast time-series queries
CREATE INDEX idx_mcp_usage_timestamp ON archon_mcp_usage_events(timestamp DESC);
CREATE INDEX idx_mcp_usage_hour_bucket ON archon_mcp_usage_events(hour_bucket);
CREATE INDEX idx_mcp_usage_tool_name ON archon_mcp_usage_events(tool_name);
CREATE INDEX idx_mcp_usage_category ON archon_mcp_usage_events(tool_category);
CREATE INDEX idx_mcp_usage_source_id ON archon_mcp_usage_events(source_id) WHERE source_id IS NOT NULL;

-- Materialized view for hourly aggregations (refreshed periodically)
CREATE MATERIALIZED VIEW archon_mcp_usage_hourly AS
SELECT
    hour_bucket,
    tool_category,
    tool_name,
    COUNT(*) as call_count,
    AVG(response_time_ms) as avg_response_time_ms,
    COUNT(*) FILTER (WHERE success = false) as error_count,
    COUNT(DISTINCT session_id) as unique_sessions
FROM archon_mcp_usage_events
WHERE timestamp >= NOW() - INTERVAL '180 days'
GROUP BY hour_bucket, tool_category, tool_name;

CREATE UNIQUE INDEX idx_mcp_usage_hourly_unique
ON archon_mcp_usage_hourly(hour_bucket, tool_category, tool_name);

-- Daily aggregation for faster long-term queries
CREATE MATERIALIZED VIEW archon_mcp_usage_daily AS
SELECT
    date_bucket,
    tool_category,
    tool_name,
    COUNT(*) as call_count,
    AVG(response_time_ms) as avg_response_time_ms,
    COUNT(*) FILTER (WHERE success = false) as error_count,
    COUNT(DISTINCT session_id) as unique_sessions
FROM archon_mcp_usage_events
WHERE timestamp >= NOW() - INTERVAL '180 days'
GROUP BY date_bucket, tool_category, tool_name;

CREATE UNIQUE INDEX idx_mcp_usage_daily_unique
ON archon_mcp_usage_daily(date_bucket, tool_category, tool_name);
```

### 2.3 Data Retention Strategy

```sql
-- Function to delete events older than 180 days
CREATE OR REPLACE FUNCTION cleanup_mcp_usage_events()
RETURNS void AS $$
BEGIN
    DELETE FROM archon_mcp_usage_events
    WHERE timestamp < NOW() - INTERVAL '180 days';
END;
$$ LANGUAGE plpgsql;

-- Scheduled cleanup (run daily via cron or pg_cron)
-- Run this in Supabase SQL Editor or create a scheduled job
-- Example cron: SELECT cron.schedule('cleanup-mcp-usage', '0 2 * * *', 'SELECT cleanup_mcp_usage_events();');
```

---

## 3. Backend Implementation

### 3.1 Usage Tracking Middleware

**File**: `python/src/mcp_server/middleware/usage_tracker.py`

```python
"""
MCP Usage Tracking Middleware

Captures all MCP tool invocations and stores usage metrics in time-series database.
"""

import time
import logging
from typing import Any, Callable, Optional
from datetime import datetime
from functools import wraps
import json

from src.server.config.database import get_supabase_client
from src.server.config.logfire_config import safe_span, get_logger

logger = get_logger(__name__)


class MCPUsageTracker:
    """Tracks MCP tool usage and stores metrics in database."""

    def __init__(self):
        self.supabase = get_supabase_client()
        self._session_id: Optional[str] = None
        self._client_type: str = "unknown"

    def set_session_context(self, session_id: str, client_type: str = "unknown"):
        """Set session context for usage tracking."""
        self._session_id = session_id
        self._client_type = client_type

    async def track_tool_usage(
        self,
        tool_name: str,
        tool_category: str,
        request_data: dict[str, Any],
        response_data: Optional[dict[str, Any]],
        response_time_ms: int,
        success: bool = True,
        error_type: Optional[str] = None
    ):
        """
        Record a tool usage event in the database.

        Args:
            tool_name: Name of the MCP tool (e.g., 'rag_search_knowledge_base')
            tool_category: Category (rag, project, task, document, health)
            request_data: Request parameters
            response_data: Response data (if any)
            response_time_ms: Time taken in milliseconds
            success: Whether the operation succeeded
            error_type: Error type if failed
        """
        try:
            # Extract relevant metadata
            source_id = request_data.get('source_id') or request_data.get('source')
            query_text = request_data.get('query', '')[:500]  # First 500 chars
            match_count = request_data.get('match_count')

            # Build event record
            event_data = {
                'tool_name': tool_name,
                'tool_category': tool_category,
                'session_id': self._session_id,
                'client_type': self._client_type,
                'request_metadata': json.dumps(request_data),
                'source_id': source_id,
                'query_text': query_text if query_text else None,
                'match_count': match_count,
                'response_time_ms': response_time_ms,
                'success': success,
                'error_type': error_type,
            }

            # Insert into database (fire-and-forget, don't block tool execution)
            self.supabase.table('archon_mcp_usage_events').insert(event_data).execute()

        except Exception as e:
            # Never fail tool execution due to tracking errors
            logger.error(f"Failed to track MCP usage: {e}", exc_info=True)

    def track_tool(self, tool_name: str, tool_category: str):
        """
        Decorator to automatically track tool usage.

        Usage:
            @usage_tracker.track_tool('rag_search_knowledge_base', 'rag')
            async def rag_search_knowledge_base(ctx: Context, query: str, ...):
                ...
        """
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                error_type = None
                response_data = None

                try:
                    # Execute the tool
                    result = await func(*args, **kwargs)
                    response_data = result
                    return result

                except Exception as e:
                    success = False
                    error_type = type(e).__name__
                    raise

                finally:
                    # Calculate response time
                    response_time_ms = int((time.time() - start_time) * 1000)

                    # Extract request data from kwargs
                    request_data = {k: v for k, v in kwargs.items() if not k.startswith('_')}

                    # Track usage (async, non-blocking)
                    await self.track_tool_usage(
                        tool_name=tool_name,
                        tool_category=tool_category,
                        request_data=request_data,
                        response_data=response_data,
                        response_time_ms=response_time_ms,
                        success=success,
                        error_type=error_type
                    )

            return wrapper
        return decorator


# Global tracker instance
usage_tracker = MCPUsageTracker()
```

### 3.2 Integration with MCP Tools

**File**: `python/src/mcp_server/features/rag/rag_tools.py` (modifications)

```python
from src.mcp_server.middleware.usage_tracker import usage_tracker

def register_rag_tools(mcp: FastMCP):
    """Register all RAG tools with usage tracking."""

    @mcp.tool()
    @usage_tracker.track_tool('rag_search_knowledge_base', 'rag')
    async def rag_search_knowledge_base(
        ctx: Context,
        query: str,
        source_id: str | None = None,
        match_count: int = 5,
        return_mode: str = "pages"
    ) -> str:
        """Search knowledge base for relevant content using RAG."""
        # ... existing implementation ...

    @mcp.tool()
    @usage_tracker.track_tool('rag_search_code_examples', 'rag')
    async def rag_search_code_examples(
        ctx: Context,
        query: str,
        source_id: str | None = None,
        match_count: int = 5
    ) -> str:
        """Search for relevant code examples."""
        # ... existing implementation ...
```

### 3.3 Analytics API Endpoints

**File**: `python/src/server/api_routes/mcp_analytics_api.py`

```python
"""
MCP Analytics API Routes

Provides endpoints for retrieving MCP usage analytics and metrics.
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import Optional
import logging

from ..config.database import get_supabase_client
from ..config.logfire_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/mcp/analytics", tags=["mcp-analytics"])


@router.get("/hourly")
async def get_hourly_usage(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to retrieve (1-168)"),
    tool_category: Optional[str] = Query(None, description="Filter by tool category"),
    tool_name: Optional[str] = Query(None, description="Filter by specific tool")
):
    """
    Get hourly aggregated MCP usage data.

    Returns usage metrics aggregated by hour for the specified time range.
    """
    try:
        supabase = get_supabase_client()

        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        # Build query
        query = supabase.table('archon_mcp_usage_hourly').select('*')
        query = query.gte('hour_bucket', start_time.isoformat())
        query = query.lte('hour_bucket', end_time.isoformat())

        if tool_category:
            query = query.eq('tool_category', tool_category)
        if tool_name:
            query = query.eq('tool_name', tool_name)

        query = query.order('hour_bucket', desc=False)

        result = query.execute()

        return {
            "success": True,
            "data": result.data,
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours": hours
            }
        }

    except Exception as e:
        logger.error(f"Failed to get hourly usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily")
async def get_daily_usage(
    days: int = Query(30, ge=1, le=180, description="Number of days to retrieve (1-180)"),
    tool_category: Optional[str] = Query(None, description="Filter by tool category")
):
    """
    Get daily aggregated MCP usage data.

    Returns usage metrics aggregated by day for the specified time range.
    """
    try:
        supabase = get_supabase_client()

        # Calculate time range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        # Build query
        query = supabase.table('archon_mcp_usage_daily').select('*')
        query = query.gte('date_bucket', start_date.isoformat())
        query = query.lte('date_bucket', end_date.isoformat())

        if tool_category:
            query = query.eq('tool_category', tool_category)

        query = query.order('date_bucket', desc=False)

        result = query.execute()

        return {
            "success": True,
            "data": result.data,
            "time_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            }
        }

    except Exception as e:
        logger.error(f"Failed to get daily usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_usage_summary():
    """
    Get summary statistics for MCP usage.

    Returns overall metrics and top tools.
    """
    try:
        supabase = get_supabase_client()

        # Last 24 hours stats
        yesterday = (datetime.now() - timedelta(hours=24)).isoformat()

        result = supabase.table('archon_mcp_usage_events').select(
            'tool_name, tool_category, success'
        ).gte('timestamp', yesterday).execute()

        total_calls = len(result.data)
        successful_calls = sum(1 for r in result.data if r['success'])
        failed_calls = total_calls - successful_calls

        # Count by category
        category_counts = {}
        tool_counts = {}

        for row in result.data:
            category = row['tool_category']
            tool = row['tool_name']

            category_counts[category] = category_counts.get(category, 0) + 1
            tool_counts[tool] = tool_counts.get(tool, 0) + 1

        # Sort tools by usage
        top_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "success": True,
            "summary": {
                "last_24_hours": {
                    "total_calls": total_calls,
                    "successful_calls": successful_calls,
                    "failed_calls": failed_calls,
                    "success_rate": round(successful_calls / total_calls * 100, 2) if total_calls > 0 else 0
                },
                "by_category": category_counts,
                "top_tools": [{"tool": t, "calls": c} for t, c in top_tools]
            }
        }

    except Exception as e:
        logger.error(f"Failed to get usage summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh-materialized-views")
async def refresh_materialized_views():
    """
    Manually refresh materialized views for aggregated data.

    This is typically run on a schedule but can be triggered manually.
    """
    try:
        supabase = get_supabase_client()

        # Refresh hourly view
        supabase.rpc('refresh_materialized_view', {'view_name': 'archon_mcp_usage_hourly'}).execute()

        # Refresh daily view
        supabase.rpc('refresh_materialized_view', {'view_name': 'archon_mcp_usage_daily'}).execute()

        return {
            "success": True,
            "message": "Materialized views refreshed successfully"
        }

    except Exception as e:
        logger.error(f"Failed to refresh materialized views: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 4. Frontend Implementation

### 4.1 Service Layer

**File**: `archon-ui-main/src/features/mcp/services/mcpAnalyticsService.ts`

```typescript
/**
 * MCP Analytics Service
 *
 * Handles fetching and processing MCP usage analytics data.
 */

import { apiClient } from "@/features/shared/api/apiClient";

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

class MCPAnalyticsService {
  /**
   * Get hourly aggregated usage data
   */
  async getHourlyUsage(
    hours: number = 24,
    toolCategory?: string,
    toolName?: string
  ): Promise<HourlyUsageData[]> {
    const params = new URLSearchParams({
      hours: hours.toString(),
    });

    if (toolCategory) params.append('tool_category', toolCategory);
    if (toolName) params.append('tool_name', toolName);

    const response = await apiClient.get<{ data: HourlyUsageData[] }>(
      `/api/mcp/analytics/hourly?${params.toString()}`
    );

    return response.data;
  }

  /**
   * Get daily aggregated usage data
   */
  async getDailyUsage(
    days: number = 30,
    toolCategory?: string
  ): Promise<DailyUsageData[]> {
    const params = new URLSearchParams({
      days: days.toString(),
    });

    if (toolCategory) params.append('tool_category', toolCategory);

    const response = await apiClient.get<{ data: DailyUsageData[] }>(
      `/api/mcp/analytics/daily?${params.toString()}`
    );

    return response.data;
  }

  /**
   * Get usage summary statistics
   */
  async getSummary(): Promise<UsageSummary> {
    const response = await apiClient.get<{ summary: UsageSummary }>(
      '/api/mcp/analytics/summary'
    );

    return response.summary;
  }
}

export const mcpAnalyticsService = new MCPAnalyticsService();
```

### 4.2 React Query Hooks

**File**: `archon-ui-main/src/features/mcp/hooks/useMcpAnalytics.ts`

```typescript
/**
 * MCP Analytics Hooks
 *
 * TanStack Query hooks for MCP usage analytics.
 */

import { useQuery } from '@tanstack/react-query';
import { mcpAnalyticsService } from '../services/mcpAnalyticsService';
import { STALE_TIMES } from '@/features/shared/config/queryPatterns';

export const mcpAnalyticsKeys = {
  all: ['mcp-analytics'] as const,
  hourly: (hours: number, category?: string, tool?: string) =>
    [...mcpAnalyticsKeys.all, 'hourly', hours, category, tool] as const,
  daily: (days: number, category?: string) =>
    [...mcpAnalyticsKeys.all, 'daily', days, category] as const,
  summary: () => [...mcpAnalyticsKeys.all, 'summary'] as const,
};

/**
 * Hook to fetch hourly usage data
 */
export function useMcpHourlyUsage(
  hours: number = 24,
  toolCategory?: string,
  toolName?: string,
  options?: { enabled?: boolean }
) {
  return useQuery({
    queryKey: mcpAnalyticsKeys.hourly(hours, toolCategory, toolName),
    queryFn: () => mcpAnalyticsService.getHourlyUsage(hours, toolCategory, toolName),
    staleTime: STALE_TIMES.frequent, // 5 seconds
    enabled: options?.enabled !== false,
  });
}

/**
 * Hook to fetch daily usage data
 */
export function useMcpDailyUsage(
  days: number = 30,
  toolCategory?: string,
  options?: { enabled?: boolean }
) {
  return useQuery({
    queryKey: mcpAnalyticsKeys.daily(days, toolCategory),
    queryFn: () => mcpAnalyticsService.getDailyUsage(days, toolCategory),
    staleTime: STALE_TIMES.normal, // 30 seconds
    enabled: options?.enabled !== false,
  });
}

/**
 * Hook to fetch usage summary
 */
export function useMcpUsageSummary(options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: mcpAnalyticsKeys.summary(),
    queryFn: () => mcpAnalyticsService.getSummary(),
    staleTime: STALE_TIMES.frequent, // 5 seconds
    enabled: options?.enabled !== false,
  });
}
```

### 4.3 Usage Analytics Component

**File**: `archon-ui-main/src/features/mcp/components/MCPUsageAnalytics.tsx`

```typescript
/**
 * MCP Usage Analytics Component
 *
 * Displays bar charts and metrics for MCP server usage.
 */

import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Activity, TrendingUp, AlertCircle } from 'lucide-react';
import { useMcpHourlyUsage, useMcpUsageSummary } from '../hooks/useMcpAnalytics';
import { Card } from '@/features/ui/primitives/Card';
import { Select } from '@/features/ui/primitives/Select';

export const MCPUsageAnalytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState<24 | 48 | 168>(24); // 24h, 48h, 7 days
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>(undefined);

  const { data: hourlyData, isLoading: hourlyLoading } = useMcpHourlyUsage(
    timeRange,
    selectedCategory
  );

  const { data: summary, isLoading: summaryLoading } = useMcpUsageSummary();

  // Aggregate data by hour bucket for chart
  const chartData = React.useMemo(() => {
    if (!hourlyData) return [];

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
  }, [hourlyData]);

  if (hourlyLoading || summaryLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Calls (24h)</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {summary?.last_24_hours.total_calls || 0}
              </p>
            </div>
            <Activity className="w-8 h-8 text-blue-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Success Rate</p>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                {summary?.last_24_hours.success_rate || 0}%
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Failed Calls</p>
              <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                {summary?.last_24_hours.failed_calls || 0}
              </p>
            </div>
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex gap-4 items-center">
          <Select
            value={timeRange.toString()}
            onValueChange={(value) => setTimeRange(parseInt(value) as 24 | 48 | 168)}
          >
            <option value="24">Last 24 Hours</option>
            <option value="48">Last 48 Hours</option>
            <option value="168">Last 7 Days</option>
          </Select>

          <Select
            value={selectedCategory || "all"}
            onValueChange={(value) => setSelectedCategory(value === "all" ? undefined : value)}
          >
            <option value="all">All Categories</option>
            <option value="rag">RAG Tools</option>
            <option value="project">Project Tools</option>
            <option value="task">Task Tools</option>
            <option value="document">Document Tools</option>
          </Select>
        </div>
      </Card>

      {/* Bar Chart */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
          MCP Tool Usage Over Time
        </h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
            <XAxis
              dataKey="hour"
              angle={-45}
              textAnchor="end"
              height={100}
              className="text-xs"
            />
            <YAxis className="text-xs" />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                border: 'none',
                borderRadius: '8px',
              }}
            />
            <Legend />
            <Bar dataKey="total" fill="#3b82f6" name="Total Calls" />
            <Bar dataKey="errors" fill="#ef4444" name="Errors" />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      {/* Top Tools Table */}
      {summary?.top_tools && summary.top_tools.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            Most Used Tools (Last 24h)
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-2 px-4 text-sm font-medium text-gray-700 dark:text-gray-300">
                    Tool Name
                  </th>
                  <th className="text-right py-2 px-4 text-sm font-medium text-gray-700 dark:text-gray-300">
                    Calls
                  </th>
                </tr>
              </thead>
              <tbody>
                {summary.top_tools.map((tool, index) => (
                  <tr
                    key={tool.tool}
                    className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50"
                  >
                    <td className="py-2 px-4 text-sm text-gray-900 dark:text-gray-100">
                      {tool.tool}
                    </td>
                    <td className="py-2 px-4 text-sm text-right font-mono text-gray-700 dark:text-gray-300">
                      {tool.calls}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
};
```

### 4.4 Integration into Settings Page

**File**: `archon-ui-main/src/pages/SettingsPage.tsx` (addition)

```typescript
import { MCPUsageAnalytics } from '../features/mcp/components/MCPUsageAnalytics';
import { Activity } from 'lucide-react';

// Add to the settings page layout
<motion.div variants={itemVariants}>
  <CollapsibleSettingsCard
    title="MCP Usage Analytics"
    icon={Activity}
    accentColor="blue"
    storageKey="mcp-analytics"
    defaultExpanded={true}
  >
    <MCPUsageAnalytics />
  </CollapsibleSettingsCard>
</motion.div>
```

---

## 5. Implementation Tasks

### Phase 1: Database Setup (Priority: High)
- [ ] **Task 1.1**: Create migration file for usage events table
  - File: `migration/0.2.0/001_add_mcp_usage_tracking.sql`
  - Includes: Main table, indexes, materialized views
  - Estimated: 2 hours

- [ ] **Task 1.2**: Create cleanup function and schedule
  - File: Same migration file
  - Includes: Retention policy function
  - Estimated: 1 hour

- [ ] **Task 1.3**: Test migration on local Supabase
  - Verify table creation
  - Test data insertion and querying
  - Estimated: 1 hour

### Phase 2: Backend Tracking Implementation (Priority: High)
- [ ] **Task 2.1**: Implement usage tracking middleware
  - File: `python/src/mcp_server/middleware/usage_tracker.py`
  - Includes: MCPUsageTracker class and decorator
  - Estimated: 3 hours

- [ ] **Task 2.2**: Integrate tracking into RAG tools
  - File: `python/src/mcp_server/features/rag/rag_tools.py`
  - Apply `@track_tool` decorator to all tools
  - Estimated: 2 hours

- [ ] **Task 2.3**: Integrate tracking into Project/Task tools
  - Files: `python/src/mcp_server/features/projects/*.py`
  - Apply tracking to all MCP tools
  - Estimated: 2 hours

- [ ] **Task 2.4**: Add session context tracking
  - Update MCP server lifecycle to set session IDs
  - Estimated: 1 hour

### Phase 3: Analytics API (Priority: Medium)
- [ ] **Task 3.1**: Create analytics API routes
  - File: `python/src/server/api_routes/mcp_analytics_api.py`
  - Includes: Hourly, daily, and summary endpoints
  - Estimated: 4 hours

- [ ] **Task 3.2**: Register analytics routes in main app
  - File: `python/src/server/main.py`
  - Add router import and include
  - Estimated: 30 minutes

- [ ] **Task 3.3**: Create materialized view refresh job
  - Supabase function or scheduled task
  - Estimated: 2 hours

- [ ] **Task 3.4**: Write API tests
  - File: `python/tests/server/api_routes/test_mcp_analytics_api.py`
  - Test all endpoints
  - Estimated: 3 hours

### Phase 4: Frontend Service & Hooks (Priority: Medium)
- [ ] **Task 4.1**: Create analytics service
  - File: `archon-ui-main/src/features/mcp/services/mcpAnalyticsService.ts`
  - Includes: API client methods
  - Estimated: 2 hours

- [ ] **Task 4.2**: Create React Query hooks
  - File: `archon-ui-main/src/features/mcp/hooks/useMcpAnalytics.ts`
  - Includes: Query keys and hooks
  - Estimated: 2 hours

- [ ] **Task 4.3**: Write service and hook tests
  - Files: Test files in respective directories
  - Estimated: 2 hours

### Phase 5: UI Components (Priority: Medium)
- [ ] **Task 5.1**: Create MCPUsageAnalytics component
  - File: `archon-ui-main/src/features/mcp/components/MCPUsageAnalytics.tsx`
  - Includes: Bar chart and summary cards
  - Estimated: 4 hours

- [ ] **Task 5.2**: Integrate into Settings page
  - File: `archon-ui-main/src/pages/SettingsPage.tsx`
  - Add new collapsible section
  - Estimated: 1 hour

- [ ] **Task 5.3**: Style and responsiveness
  - Ensure mobile-friendly layout
  - Match Tron theme
  - Estimated: 2 hours

- [ ] **Task 5.4**: Add loading and error states
  - Proper UX for all states
  - Estimated: 1 hour

### Phase 6: Testing & Optimization (Priority: Low)
- [ ] **Task 6.1**: End-to-end testing
  - Test full flow from tool invocation to UI display
  - Estimated: 3 hours

- [ ] **Task 6.2**: Performance testing
  - Measure query performance
  - Test with large datasets
  - Estimated: 2 hours

- [ ] **Task 6.3**: Add query result caching
  - Optimize materialized view refresh
  - Estimated: 2 hours

- [ ] **Task 6.4**: Documentation
  - Update CLAUDE.md with new feature
  - API documentation
  - Estimated: 2 hours

---

## 6. Technical Considerations

### 6.1 Performance

**Tracking Overhead**:
- Async insertion (non-blocking)
- Target: < 10ms per tool invocation
- Fire-and-forget pattern to avoid blocking tool execution

**Query Performance**:
- Materialized views for fast aggregations
- Indexed by time buckets for efficient range queries
- Partitioning if needed for very large datasets

### 6.2 Data Retention

**Automated Cleanup**:
- Daily cron job to delete events older than 180 days
- Materialized views automatically filtered to 180-day window
- Estimated storage: ~50MB for 180 days (assumes 1000 calls/day)

### 6.3 Privacy Considerations

**Data Stored**:
- Tool names and categories (non-sensitive)
- Query text (first 500 chars only, anonymized)
- Source IDs (hashed, non-identifying)
- NO user-identifiable information
- NO API keys or credentials

**Compliance**:
- Local-only deployment (each user's own instance)
- No external data transmission
- User controls all data

### 6.4 Scalability

**Current Design Supports**:
- Up to 10,000 tool calls per day
- 180-day retention = ~1.8M records max
- Hourly aggregations = ~4,320 rows per category
- Daily aggregations = ~180 rows per category

**Future Scaling**:
- Table partitioning by month if needed
- TimescaleDB for automatic compression
- Archive old data to separate tables

---

## 7. Success Criteria

### Functional Requirements
- ✅ All MCP tool invocations tracked automatically
- ✅ 180 days of historical data retained
- ✅ Hourly aggregations display in bar charts
- ✅ Real-time updates (< 3 second latency)
- ✅ Filter by time range and tool category

### Performance Requirements
- ✅ < 10ms tracking overhead per tool call
- ✅ < 500ms query time for hourly aggregations
- ✅ < 2 seconds to load full analytics page

### User Experience
- ✅ Interactive bar charts with tooltips
- ✅ Summary cards with key metrics
- ✅ Top tools leaderboard
- ✅ Mobile-responsive design

---

## 8. Future Enhancements

### Phase 2 Features (Post-MVP)
1. **Advanced Filtering**
   - Filter by source ID (which docs are most queried)
   - Filter by success/failure
   - Session-based analysis

2. **Export Functionality**
   - Export usage data as CSV/JSON
   - Generate usage reports

3. **Alerting**
   - Alert on high error rates
   - Alert on unusual usage patterns

4. **Comparative Analytics**
   - Week-over-week comparisons
   - Trend analysis

5. **Usage Insights**
   - Most queried knowledge sources
   - Peak usage hours
   - Tool adoption metrics

---

## 9. Dependencies

### Backend
- `supabase-py` - Database client (already installed)
- No additional dependencies

### Frontend
- `recharts` - Chart library (need to install)
  ```bash
  cd archon-ui-main && npm install recharts
  ```
- All other dependencies already present

### Database
- PostgreSQL 14+ (via Supabase)
- pgvector extension (already installed)
- No additional extensions required

---

## 10. Rollout Plan

### Week 1: Backend Foundation
- Day 1-2: Database schema and migration
- Day 3-4: Tracking middleware implementation
- Day 5: Integration with MCP tools

### Week 2: API & Frontend Services
- Day 1-2: Analytics API endpoints
- Day 3-4: Frontend services and hooks
- Day 5: Testing and refinement

### Week 3: UI & Polish
- Day 1-3: UI components and charts
- Day 4: Integration and styling
- Day 5: Testing and bug fixes

### Week 4: Testing & Launch
- Day 1-2: End-to-end testing
- Day 3: Performance optimization
- Day 4: Documentation
- Day 5: Deployment and monitoring

---

## 11. Monitoring & Maintenance

### Ongoing Tasks
1. **Daily**: Monitor query performance
2. **Weekly**: Review error rates and failed calls
3. **Monthly**: Analyze usage patterns for optimization
4. **Quarterly**: Review data retention and storage usage

### Metrics to Track
- Query response times
- Database storage growth
- Most used tools
- Error rates by tool category
- Peak usage times

---

**End of Specification**
