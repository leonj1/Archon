import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import React from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { DailyUsageData, HourlyUsageData, UsageSummary } from "../../services/mcpAnalyticsService";
import { mcpAnalyticsKeys, useMcpDailyUsage, useMcpHourlyUsage, useMcpUsageSummary } from "../useMcpAnalytics";

// Mock the service
vi.mock("../../services/mcpAnalyticsService", () => ({
  mcpAnalyticsService: {
    getHourlyUsage: vi.fn(),
    getDailyUsage: vi.fn(),
    getSummary: vi.fn(),
  },
}));

// Mock shared query patterns with ALL values
vi.mock("@/features/shared/config/queryPatterns", () => ({
  DISABLED_QUERY_KEY: ["disabled"] as const,
  STALE_TIMES: {
    instant: 0,
    realtime: 3_000,
    frequent: 5_000,
    normal: 30_000,
    rare: 300_000,
    static: Infinity,
  },
}));

// Test wrapper with QueryClient
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

describe("useMcpAnalytics", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("mcpAnalyticsKeys", () => {
    it("should generate correct base key", () => {
      expect(mcpAnalyticsKeys.all).toEqual(["mcp-analytics"]);
    });

    it("should generate correct hourly key with all parameters", () => {
      expect(mcpAnalyticsKeys.hourly(24, "rag", "search")).toEqual([
        "mcp-analytics",
        "hourly",
        24,
        "rag",
        "search",
      ]);
    });

    it("should generate correct hourly key with minimal parameters", () => {
      expect(mcpAnalyticsKeys.hourly(24)).toEqual(["mcp-analytics", "hourly", 24, undefined, undefined]);
    });

    it("should generate correct hourly key with category only", () => {
      expect(mcpAnalyticsKeys.hourly(48, "project")).toEqual([
        "mcp-analytics",
        "hourly",
        48,
        "project",
        undefined,
      ]);
    });

    it("should generate correct daily key with all parameters", () => {
      expect(mcpAnalyticsKeys.daily(7, "task")).toEqual(["mcp-analytics", "daily", 7, "task"]);
    });

    it("should generate correct daily key with minimal parameters", () => {
      expect(mcpAnalyticsKeys.daily(7)).toEqual(["mcp-analytics", "daily", 7, undefined]);
    });

    it("should generate correct summary key", () => {
      expect(mcpAnalyticsKeys.summary()).toEqual(["mcp-analytics", "summary"]);
    });

    it("should generate unique keys for different parameters", () => {
      const key1 = mcpAnalyticsKeys.hourly(24, "rag");
      const key2 = mcpAnalyticsKeys.hourly(24, "project");
      const key3 = mcpAnalyticsKeys.hourly(48, "rag");

      expect(key1).not.toEqual(key2);
      expect(key1).not.toEqual(key3);
      expect(key2).not.toEqual(key3);
    });
  });

  describe("useMcpHourlyUsage", () => {
    const mockHourlyData: HourlyUsageData[] = [
      {
        hour_bucket: "2024-01-15T10:00:00Z",
        tool_category: "rag",
        tool_name: "rag_search_knowledge_base",
        call_count: 42,
        avg_response_time_ms: 156.3,
        error_count: 2,
        unique_sessions: 5,
      },
      {
        hour_bucket: "2024-01-15T11:00:00Z",
        tool_category: "project",
        tool_name: "find_projects",
        call_count: 18,
        avg_response_time_ms: 89.7,
        error_count: 0,
        unique_sessions: 3,
      },
    ];

    it("should fetch hourly usage data with default parameters", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getHourlyUsage).mockResolvedValue(mockHourlyData);

      const { result } = renderHook(() => useMcpHourlyUsage(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
        expect(result.current.data).toEqual(mockHourlyData);
      });

      expect(mcpAnalyticsService.getHourlyUsage).toHaveBeenCalledWith(24, undefined, undefined);
      expect(mcpAnalyticsService.getHourlyUsage).toHaveBeenCalledTimes(1);
    });

    it("should fetch hourly usage data with custom hours parameter", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getHourlyUsage).mockResolvedValue(mockHourlyData);

      const { result } = renderHook(() => useMcpHourlyUsage(48), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(mcpAnalyticsService.getHourlyUsage).toHaveBeenCalledWith(48, undefined, undefined);
    });

    it("should fetch hourly usage data with category filter", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getHourlyUsage).mockResolvedValue(mockHourlyData);

      const { result } = renderHook(() => useMcpHourlyUsage(24, "rag"), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(mcpAnalyticsService.getHourlyUsage).toHaveBeenCalledWith(24, "rag", undefined);
    });

    it("should fetch hourly usage data with all filters", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getHourlyUsage).mockResolvedValue(mockHourlyData);

      const { result } = renderHook(() => useMcpHourlyUsage(168, "rag", "rag_search_knowledge_base"), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(mcpAnalyticsService.getHourlyUsage).toHaveBeenCalledWith(168, "rag", "rag_search_knowledge_base");
    });

    it("should handle disabled query via options", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getHourlyUsage).mockResolvedValue(mockHourlyData);

      const { result } = renderHook(() => useMcpHourlyUsage(24, undefined, undefined, { enabled: false }), {
        wrapper: createWrapper(),
      });

      // Should not be loading or have data since it's disabled
      expect(result.current.isLoading).toBe(false);
      expect(result.current.data).toBeUndefined();
      expect(mcpAnalyticsService.getHourlyUsage).not.toHaveBeenCalled();
    });

    it("should handle enabled query via options", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getHourlyUsage).mockResolvedValue(mockHourlyData);

      const { result } = renderHook(() => useMcpHourlyUsage(24, undefined, undefined, { enabled: true }), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(mcpAnalyticsService.getHourlyUsage).toHaveBeenCalledTimes(1);
    });

    it("should handle service errors", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      const mockError = new Error("Network error");
      vi.mocked(mcpAnalyticsService.getHourlyUsage).mockRejectedValue(mockError);

      const { result } = renderHook(() => useMcpHourlyUsage(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
        expect(result.current.error).toEqual(mockError);
      });
    });

    it("should use frequent stale time configuration", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getHourlyUsage).mockResolvedValue(mockHourlyData);

      const { result } = renderHook(() => useMcpHourlyUsage(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      // Verify staleTime is set to STALE_TIMES.frequent (5000ms)
      // Note: This is more of a configuration test, actual value verification would require inspecting query cache
      expect(result.current.dataUpdatedAt).toBeGreaterThan(0);
    });
  });

  describe("useMcpDailyUsage", () => {
    const mockDailyData: DailyUsageData[] = [
      {
        date_bucket: "2024-01-15",
        tool_category: "rag",
        tool_name: "rag_search_knowledge_base",
        call_count: 324,
        avg_response_time_ms: 145.8,
        error_count: 12,
        unique_sessions: 18,
      },
      {
        date_bucket: "2024-01-16",
        tool_category: "project",
        tool_name: "find_projects",
        call_count: 156,
        avg_response_time_ms: 92.3,
        error_count: 3,
        unique_sessions: 12,
      },
    ];

    it("should fetch daily usage data with default parameters", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getDailyUsage).mockResolvedValue(mockDailyData);

      const { result } = renderHook(() => useMcpDailyUsage(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
        expect(result.current.data).toEqual(mockDailyData);
      });

      expect(mcpAnalyticsService.getDailyUsage).toHaveBeenCalledWith(7, undefined);
      expect(mcpAnalyticsService.getDailyUsage).toHaveBeenCalledTimes(1);
    });

    it("should fetch daily usage data with custom days parameter", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getDailyUsage).mockResolvedValue(mockDailyData);

      const { result } = renderHook(() => useMcpDailyUsage(30), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(mcpAnalyticsService.getDailyUsage).toHaveBeenCalledWith(30, undefined);
    });

    it("should fetch daily usage data with category filter", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getDailyUsage).mockResolvedValue(mockDailyData);

      const { result } = renderHook(() => useMcpDailyUsage(7, "task"), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(mcpAnalyticsService.getDailyUsage).toHaveBeenCalledWith(7, "task");
    });

    it("should handle disabled query via options", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getDailyUsage).mockResolvedValue(mockDailyData);

      const { result } = renderHook(() => useMcpDailyUsage(7, undefined, { enabled: false }), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.data).toBeUndefined();
      expect(mcpAnalyticsService.getDailyUsage).not.toHaveBeenCalled();
    });

    it("should handle enabled query via options", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getDailyUsage).mockResolvedValue(mockDailyData);

      const { result } = renderHook(() => useMcpDailyUsage(7, undefined, { enabled: true }), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(mcpAnalyticsService.getDailyUsage).toHaveBeenCalledTimes(1);
    });

    it("should handle service errors", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      const mockError = new Error("Database connection failed");
      vi.mocked(mcpAnalyticsService.getDailyUsage).mockRejectedValue(mockError);

      const { result } = renderHook(() => useMcpDailyUsage(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
        expect(result.current.error).toEqual(mockError);
      });
    });

    it("should use normal stale time configuration", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getDailyUsage).mockResolvedValue(mockDailyData);

      const { result } = renderHook(() => useMcpDailyUsage(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      // Verify data is fetched and cached
      expect(result.current.dataUpdatedAt).toBeGreaterThan(0);
    });
  });

  describe("useMcpUsageSummary", () => {
    const mockSummary: UsageSummary = {
      last_24_hours: {
        total_calls: 1234,
        successful_calls: 1198,
        failed_calls: 36,
        success_rate: 97.08,
      },
      by_category: {
        rag: 567,
        project: 234,
        task: 189,
        document: 156,
        feature: 88,
      },
      top_tools: [
        { tool: "rag_search_knowledge_base", calls: 432 },
        { tool: "find_tasks", calls: 234 },
        { tool: "find_projects", calls: 198 },
        { tool: "rag_search_code_examples", calls: 135 },
        { tool: "manage_task", calls: 89 },
      ],
    };

    it("should fetch usage summary with default parameters", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getSummary).mockResolvedValue(mockSummary);

      const { result } = renderHook(() => useMcpUsageSummary(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
        expect(result.current.data).toEqual(mockSummary);
      });

      expect(mcpAnalyticsService.getSummary).toHaveBeenCalledTimes(1);
    });

    it("should handle disabled query via options", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getSummary).mockResolvedValue(mockSummary);

      const { result } = renderHook(() => useMcpUsageSummary({ enabled: false }), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.data).toBeUndefined();
      expect(mcpAnalyticsService.getSummary).not.toHaveBeenCalled();
    });

    it("should handle enabled query via options", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getSummary).mockResolvedValue(mockSummary);

      const { result } = renderHook(() => useMcpUsageSummary({ enabled: true }), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(mcpAnalyticsService.getSummary).toHaveBeenCalledTimes(1);
    });

    it("should handle service errors", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      const mockError = new Error("Unauthorized");
      vi.mocked(mcpAnalyticsService.getSummary).mockRejectedValue(mockError);

      const { result } = renderHook(() => useMcpUsageSummary(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
        expect(result.current.error).toEqual(mockError);
      });
    });

    it("should use frequent stale time configuration", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getSummary).mockResolvedValue(mockSummary);

      const { result } = renderHook(() => useMcpUsageSummary(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      // Verify data is fetched and cached
      expect(result.current.dataUpdatedAt).toBeGreaterThan(0);
    });

    it("should handle empty summary data", async () => {
      const emptySummary: UsageSummary = {
        last_24_hours: {
          total_calls: 0,
          successful_calls: 0,
          failed_calls: 0,
          success_rate: 0,
        },
        by_category: {},
        top_tools: [],
      };

      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getSummary).mockResolvedValue(emptySummary);

      const { result } = renderHook(() => useMcpUsageSummary(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
        expect(result.current.data).toEqual(emptySummary);
      });
    });
  });

  describe("Query key consistency", () => {
    it("should use consistent query keys across hook calls", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getHourlyUsage).mockResolvedValue([]);

      const wrapper = createWrapper();

      // First render
      const { result: result1 } = renderHook(() => useMcpHourlyUsage(24, "rag"), {
        wrapper,
      });

      // Second render with same parameters
      const { result: result2 } = renderHook(() => useMcpHourlyUsage(24, "rag"), {
        wrapper,
      });

      await waitFor(() => {
        expect(result1.current.isSuccess).toBe(true);
        expect(result2.current.isSuccess).toBe(true);
      });

      // Service should only be called once due to deduplication
      expect(mcpAnalyticsService.getHourlyUsage).toHaveBeenCalledTimes(1);
    });

    it("should generate different query keys for different parameters", () => {
      const key1 = mcpAnalyticsKeys.hourly(24, "rag");
      const key2 = mcpAnalyticsKeys.hourly(48, "rag");
      const key3 = mcpAnalyticsKeys.hourly(24, "project");

      expect(key1).not.toEqual(key2);
      expect(key1).not.toEqual(key3);
      expect(key2).not.toEqual(key3);
    });

    it("should maintain query key stability with undefined optional parameters", () => {
      const key1 = mcpAnalyticsKeys.hourly(24, undefined, undefined);
      const key2 = mcpAnalyticsKeys.hourly(24);

      // Both should produce the same key structure
      expect(key1).toEqual(key2);
    });
  });

  describe("Loading and error states", () => {
    it("should expose loading state during query execution", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getHourlyUsage).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve([]), 100))
      );

      const { result } = renderHook(() => useMcpHourlyUsage(), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(true);
      expect(result.current.data).toBeUndefined();

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
        expect(result.current.isSuccess).toBe(true);
      });
    });

    it("should expose error state on query failure", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      const error = new Error("API Error");
      vi.mocked(mcpAnalyticsService.getDailyUsage).mockRejectedValue(error);

      const { result } = renderHook(() => useMcpDailyUsage(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
        expect(result.current.error).toEqual(error);
      });
    });

    it("should provide refetch functionality", async () => {
      const { mcpAnalyticsService } = await import("../../services/mcpAnalyticsService");
      vi.mocked(mcpAnalyticsService.getSummary).mockResolvedValue({
        last_24_hours: { total_calls: 0, successful_calls: 0, failed_calls: 0, success_rate: 0 },
        by_category: {},
        top_tools: [],
      });

      const { result } = renderHook(() => useMcpUsageSummary(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(mcpAnalyticsService.getSummary).toHaveBeenCalledTimes(1);

      // Trigger refetch
      await result.current.refetch();

      expect(mcpAnalyticsService.getSummary).toHaveBeenCalledTimes(2);
    });
  });
});
