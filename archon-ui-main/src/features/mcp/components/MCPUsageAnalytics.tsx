import { Activity, AlertCircle, RefreshCw, TrendingUp } from "lucide-react";
import type React from "react";
import { useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card } from "@/features/ui/primitives/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/features/ui/primitives/select";
import { useMcpHourlyUsage, useMcpUsageSummary } from "../hooks/useMcpAnalytics";
import { KnowledgeBaseUsageCard } from "./KnowledgeBaseUsageCard";

interface ChartDataPoint {
  hour: string;
  total: number;
  errors: number;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    value: number;
    payload: ChartDataPoint;
  }>;
}

const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload }) => {
  if (!active || !payload || payload.length === 0) return null;

  const data = payload[0].payload;
  const total = data.total;
  const errors = data.errors;
  const successful = total - errors;
  const successRate = total > 0 ? ((successful / total) * 100).toFixed(1) : "0.0";

  return (
    <div className="bg-black/90 dark:bg-black/95 text-white p-3 rounded-lg shadow-lg border border-white/10 backdrop-blur-sm">
      <p className="font-semibold mb-2">{data.hour}</p>
      <div className="space-y-1 text-sm">
        <p className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-blue-500" />
          Total Calls: <span className="font-medium">{total}</span>
        </p>
        <p className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-red-500" />
          Errors: <span className="font-medium">{errors}</span>
        </p>
        <p className="text-green-400 font-medium mt-1">Success Rate: {successRate}%</p>
      </div>
    </div>
  );
};

export const MCPUsageAnalytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState<24 | 48 | 168>(24);
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>(undefined);

  const {
    data: hourlyData,
    isLoading: hourlyLoading,
    error: hourlyError,
    refetch: refetchHourly,
  } = useMcpHourlyUsage(timeRange, selectedCategory);

  const {
    data: summary,
    isLoading: summaryLoading,
    error: summaryError,
    refetch: refetchSummary,
  } = useMcpUsageSummary();

  // Aggregate data by hour for chart display
  const chartData = useMemo(() => {
    if (!hourlyData) return [];

    const aggregated = hourlyData.reduce(
      (acc, item) => {
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
      },
      {} as Record<string, ChartDataPoint>,
    );

    return Object.values(aggregated);
  }, [hourlyData]);

  // Calculate top tools from hourly data
  const topTools = useMemo(() => {
    if (!hourlyData) return [];

    const toolCounts = hourlyData.reduce(
      (acc, item) => {
        const tool = item.tool_name || "Unknown";
        acc[tool] = (acc[tool] || 0) + item.call_count;
        return acc;
      },
      {} as Record<string, number>,
    );

    return Object.entries(toolCounts)
      .map(([tool, calls]) => ({ tool, calls }))
      .sort((a, b) => b.calls - a.calls)
      .slice(0, 10);
  }, [hourlyData]);

  const handleRefresh = () => {
    refetchHourly();
    refetchSummary();
  };

  // Loading state
  if (hourlyLoading || summaryLoading) {
    return (
      <div className="space-y-6">
        {/* Summary cards skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} blur="md" transparency="light" size="md">
              <div className="h-20 bg-gray-200/50 dark:bg-gray-700/50 rounded animate-pulse" />
            </Card>
          ))}
        </div>

        {/* Filters skeleton */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="w-full sm:w-48 h-10 bg-gray-200/50 dark:bg-gray-700/50 rounded animate-pulse" />
          <div className="w-full sm:w-48 h-10 bg-gray-200/50 dark:bg-gray-700/50 rounded animate-pulse" />
        </div>

        {/* Chart skeleton */}
        <Card blur="md" transparency="light" size="lg">
          <div className="h-[400px] bg-gray-200/50 dark:bg-gray-700/50 rounded animate-pulse" />
        </Card>

        {/* Table skeleton */}
        <Card blur="md" transparency="light" size="lg">
          <div className="h-64 bg-gray-200/50 dark:bg-gray-700/50 rounded animate-pulse" />
        </Card>
      </div>
    );
  }

  // Error state
  if (hourlyError || summaryError) {
    return (
      <Card blur="md" transparency="light" size="lg">
        <div className="text-center py-8">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Failed to load analytics</p>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            {(hourlyError as Error)?.message || (summaryError as Error)?.message}
          </p>
          <button
            onClick={handleRefresh}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Retry
          </button>
        </div>
      </Card>
    );
  }

  // Empty state
  if (chartData.length === 0) {
    return (
      <Card blur="md" transparency="light" size="lg">
        <div className="text-center py-8">
          <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No usage data yet</p>
          <p className="text-sm text-gray-600 dark:text-gray-400">Start using MCP tools to see analytics here</p>
        </div>
      </Card>
    );
  }

  const totalCalls = summary?.last_24_hours?.total_calls || 0;
  const successRate = summary?.last_24_hours?.success_rate || 0;
  const failedCalls = summary?.last_24_hours?.failed_calls || 0;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Total Calls */}
        <Card
          blur="md"
          transparency="light"
          glowColor="blue"
          glowType="outer"
          glowSize="sm"
          size="md"
          className="transition-all duration-300 hover:scale-[1.02]"
        >
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-blue-500/10 dark:bg-blue-400/10">
              <Activity className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Calls (24h)</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{totalCalls.toLocaleString()}</p>
            </div>
          </div>
        </Card>

        {/* Success Rate */}
        <Card
          blur="md"
          transparency="light"
          glowColor="green"
          glowType="outer"
          glowSize="sm"
          size="md"
          className="transition-all duration-300 hover:scale-[1.02]"
        >
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-green-500/10 dark:bg-green-400/10">
              <TrendingUp className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Success Rate</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{successRate.toFixed(1)}%</p>
            </div>
          </div>
        </Card>

        {/* Failed Calls */}
        <Card
          blur="md"
          transparency="light"
          glowColor="red"
          glowType="outer"
          glowSize="sm"
          size="md"
          className="transition-all duration-300 hover:scale-[1.02]"
        >
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-red-500/10 dark:bg-red-400/10">
              <AlertCircle className="w-6 h-6 text-red-600 dark:text-red-400" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Failed Calls</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{failedCalls.toLocaleString()}</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Knowledge Base Usage Card */}
      <KnowledgeBaseUsageCard hours={timeRange} />

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Time Range Filter */}
        <div className="w-full sm:w-auto">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Time Range</label>
          <Select value={timeRange.toString()} onValueChange={(value) => setTimeRange(Number(value) as 24 | 48 | 168)}>
            <SelectTrigger color="blue" className="w-full sm:w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent color="blue">
              <SelectItem value="24" color="blue">
                Last 24 hours
              </SelectItem>
              <SelectItem value="48" color="blue">
                Last 48 hours
              </SelectItem>
              <SelectItem value="168" color="blue">
                Last 7 days
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Category Filter */}
        <div className="w-full sm:w-auto">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Category</label>
          <Select
            value={selectedCategory || "all"}
            onValueChange={(value) => setSelectedCategory(value === "all" ? undefined : value)}
          >
            <SelectTrigger color="cyan" className="w-full sm:w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent color="cyan">
              <SelectItem value="all" color="cyan">
                All Categories
              </SelectItem>
              <SelectItem value="rag" color="cyan">
                RAG
              </SelectItem>
              <SelectItem value="project" color="cyan">
                Project
              </SelectItem>
              <SelectItem value="task" color="cyan">
                Task
              </SelectItem>
              <SelectItem value="document" color="cyan">
                Document
              </SelectItem>
              <SelectItem value="version" color="cyan">
                Version
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Refresh Button */}
        <div className="flex items-end">
          <button
            onClick={handleRefresh}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 hover:bg-blue-500/20 text-blue-600 dark:text-blue-400 rounded-lg transition-colors border border-blue-500/30"
            aria-label="Refresh analytics data"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* Bar Chart */}
      <Card blur="md" transparency="light" size="lg">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Usage Over Time</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(156, 163, 175, 0.2)" />
            <XAxis
              dataKey="hour"
              stroke="rgba(156, 163, 175, 0.5)"
              tick={{ fill: "currentColor", fontSize: 12 }}
              className="text-gray-600 dark:text-gray-400"
            />
            <YAxis
              stroke="rgba(156, 163, 175, 0.5)"
              tick={{ fill: "currentColor", fontSize: 12 }}
              className="text-gray-600 dark:text-gray-400"
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(59, 130, 246, 0.1)" }} />
            <Legend
              wrapperStyle={{ paddingTop: "20px" }}
              iconType="circle"
              formatter={(value) => <span className="text-gray-700 dark:text-gray-300">{value}</span>}
            />
            <Bar
              dataKey="total"
              name="Total Calls"
              fill="rgb(59, 130, 246)"
              radius={[4, 4, 0, 0]}
              aria-label="Total calls bar chart"
            />
            <Bar
              dataKey="errors"
              name="Errors"
              fill="rgb(239, 68, 68)"
              radius={[4, 4, 0, 0]}
              aria-label="Errors bar chart"
            />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      {/* Top Tools Table */}
      <Card blur="md" transparency="light" size="lg">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Top 10 Most Used Tools</h3>
        <div className="overflow-x-auto">
          <table className="w-full" role="table">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700">
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">
                  Tool Name
                </th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">
                  Call Count
                </th>
              </tr>
            </thead>
            <tbody>
              {topTools.length > 0 ? (
                topTools.map((item, index) => (
                  <tr
                    key={item.tool}
                    className="border-b border-gray-200 dark:border-gray-700 last:border-0 hover:bg-blue-500/5 dark:hover:bg-blue-400/5 transition-colors"
                  >
                    <td className="py-3 px-4 text-sm text-gray-900 dark:text-white font-medium">
                      <span className="flex items-center gap-2">
                        <span className="text-xs text-gray-500 dark:text-gray-400 w-6">{index + 1}.</span>
                        {item.tool}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-700 dark:text-gray-300 text-right font-mono">
                      {item.calls.toLocaleString()}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={2} className="py-8 text-center text-gray-500 dark:text-gray-400">
                    No tool usage data available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
