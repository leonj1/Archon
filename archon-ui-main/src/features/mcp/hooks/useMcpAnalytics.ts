import { useQuery } from "@tanstack/react-query";
import { STALE_TIMES } from "@/features/shared/config/queryPatterns";
import { mcpAnalyticsService } from "../services/mcpAnalyticsService";

/**
 * Query keys factory for MCP Analytics
 *
 * Follows the standard pattern:
 * - all: Base key for the domain
 * - hourly: For hourly usage data with parameters
 * - daily: For daily usage data with parameters
 * - summary: For summary statistics
 */
export const mcpAnalyticsKeys = {
  all: ["mcp-analytics"] as const,
  hourly: (hours: number, category?: string, tool?: string) =>
    [...mcpAnalyticsKeys.all, "hourly", hours, category, tool] as const,
  daily: (days: number, category?: string) =>
    [...mcpAnalyticsKeys.all, "daily", days, category] as const,
  summary: () => [...mcpAnalyticsKeys.all, "summary"] as const,
};

/**
 * Hook to fetch hourly MCP usage data
 *
 * @param hours - Number of hours to query (1-168)
 * @param toolCategory - Optional category filter (e.g., "rag", "project", "task")
 * @param toolName - Optional tool name filter (e.g., "rag_search_knowledge_base")
 * @param options - Query options (enabled, etc.)
 * @returns Query result with hourly usage data
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
    staleTime: STALE_TIMES.frequent, // 5 seconds - frequently changing data
    enabled: options?.enabled !== false,
  });
}

/**
 * Hook to fetch daily MCP usage data
 *
 * @param days - Number of days to query (1-180)
 * @param toolCategory - Optional category filter (e.g., "rag", "project", "task")
 * @param options - Query options (enabled, etc.)
 * @returns Query result with daily usage data
 */
export function useMcpDailyUsage(
  days: number = 7,
  toolCategory?: string,
  options?: { enabled?: boolean }
) {
  return useQuery({
    queryKey: mcpAnalyticsKeys.daily(days, toolCategory),
    queryFn: () => mcpAnalyticsService.getDailyUsage(days, toolCategory),
    staleTime: STALE_TIMES.normal, // 30 seconds - standard cache time
    enabled: options?.enabled !== false,
  });
}

/**
 * Hook to fetch MCP usage summary statistics
 *
 * Returns summary for the last 24 hours including:
 * - Total calls
 * - Success rate
 * - Top tools
 * - By-category counts
 *
 * @param options - Query options (enabled, etc.)
 * @returns Query result with summary statistics
 */
export function useMcpUsageSummary(options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: mcpAnalyticsKeys.summary(),
    queryFn: () => mcpAnalyticsService.getSummary(),
    staleTime: STALE_TIMES.frequent, // 5 seconds - real-time summary
    enabled: options?.enabled !== false,
  });
}
