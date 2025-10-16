import { callAPIWithETag } from "@/features/shared/api/apiClient";
import type { KnowledgeBaseAnalyticsResponse } from "../types/analytics";

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
   * Fetch hourly usage data with optional filters
   */
  async getHourlyUsage(hours: number = 24, toolCategory?: string, toolName?: string): Promise<HourlyUsageData[]> {
    try {
      const params = new URLSearchParams({ hours: hours.toString() });
      if (toolCategory) params.append("tool_category", toolCategory);
      if (toolName) params.append("tool_name", toolName);

      const response = await callAPIWithETag<{ data: HourlyUsageData[] }>(
        `/api/mcp/analytics/hourly?${params.toString()}`,
      );
      return response.data;
    } catch (error) {
      console.error("Failed to get hourly usage:", error);
      throw error;
    }
  }

  /**
   * Fetch daily usage data with optional category filter
   */
  async getDailyUsage(days: number = 7, toolCategory?: string): Promise<DailyUsageData[]> {
    try {
      const params = new URLSearchParams({ days: days.toString() });
      if (toolCategory) params.append("tool_category", toolCategory);

      const response = await callAPIWithETag<{ data: DailyUsageData[] }>(
        `/api/mcp/analytics/daily?${params.toString()}`,
      );
      return response.data;
    } catch (error) {
      console.error("Failed to get daily usage:", error);
      throw error;
    }
  }

  /**
   * Fetch summary statistics for the last 24 hours
   */
  async getSummary(): Promise<UsageSummary> {
    try {
      const response = await callAPIWithETag<UsageSummary>("/api/mcp/analytics/summary");
      return response;
    } catch (error) {
      console.error("Failed to get usage summary:", error);
      throw error;
    }
  }

  /**
   * Fetch knowledge base analytics with source breakdown
   */
  async getKnowledgeBaseAnalytics(hours: number = 24): Promise<KnowledgeBaseAnalyticsResponse> {
    try {
      const params = new URLSearchParams({ hours: hours.toString() });
      const response = await callAPIWithETag<KnowledgeBaseAnalyticsResponse>(
        `/api/mcp/analytics/knowledge-bases?${params.toString()}`,
      );
      return response;
    } catch (error) {
      console.error("Failed to get knowledge base analytics:", error);
      throw error;
    }
  }
}

export const mcpAnalyticsService = new MCPAnalyticsService();
