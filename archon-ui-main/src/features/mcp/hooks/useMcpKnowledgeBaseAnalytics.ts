import { useQuery } from "@tanstack/react-query";
import { STALE_TIMES } from "@/features/shared/config/queryPatterns";
import { mcpAnalyticsService } from "../services/mcpAnalyticsService";

/**
 * Query keys factory for MCP Knowledge Base Analytics
 *
 * Follows the standard pattern:
 * - all: Base key for the domain
 * - lists: For list queries
 * - list: For specific list query with parameters
 */
export const mcpKnowledgeBaseKeys = {
  all: ["mcp", "knowledge-bases"] as const,
  lists: () => [...mcpKnowledgeBaseKeys.all, "list"] as const,
  list: (hours: number) => [...mcpKnowledgeBaseKeys.lists(), { hours }] as const,
};

/**
 * Hook to fetch knowledge base analytics data
 *
 * Provides breakdown of knowledge base usage including:
 * - Query counts per source
 * - Unique queries
 * - Average response times
 * - Success rates
 * - Percentage of total usage
 *
 * @param hours - Number of hours to query (default: 24)
 * @param options - Query options (enabled, etc.)
 * @returns Query result with knowledge base analytics data
 */
export function useMcpKnowledgeBaseAnalytics(hours: number = 24, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: mcpKnowledgeBaseKeys.list(hours),
    queryFn: () => mcpAnalyticsService.getKnowledgeBaseAnalytics(hours),
    staleTime: STALE_TIMES.normal,
    enabled: options?.enabled !== false,
  });
}
