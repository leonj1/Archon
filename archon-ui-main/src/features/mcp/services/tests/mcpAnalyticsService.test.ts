import { beforeEach, describe, expect, it, vi } from "vitest";
import { callAPIWithETag } from "../../../shared/api/apiClient";
import type { DailyUsageData, HourlyUsageData, UsageSummary } from "../mcpAnalyticsService";
import { mcpAnalyticsService } from "../mcpAnalyticsService";

// Mock the API call
vi.mock("../../../shared/api/apiClient", () => ({
  callAPIWithETag: vi.fn(),
}));

describe("mcpAnalyticsService", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("getHourlyUsage", () => {
    const mockHourlyData: HourlyUsageData[] = [
      {
        hour_bucket: "2024-01-01T00:00:00Z",
        tool_category: "rag",
        tool_name: "rag_search_knowledge_base",
        call_count: 42,
        avg_response_time_ms: 150,
        error_count: 2,
        unique_sessions: 5,
      },
      {
        hour_bucket: "2024-01-01T01:00:00Z",
        tool_category: "project",
        tool_name: "find_projects",
        call_count: 15,
        avg_response_time_ms: 75,
        error_count: 0,
        unique_sessions: 3,
      },
    ];

    it("should fetch hourly usage with default parameters (24 hours)", async () => {
      const mockResponse = { data: mockHourlyData };
      (callAPIWithETag as any).mockResolvedValueOnce(mockResponse);

      const result = await mcpAnalyticsService.getHourlyUsage();

      expect(callAPIWithETag).toHaveBeenCalledWith("/api/mcp/analytics/hourly?hours=24");
      expect(result).toEqual(mockHourlyData);
    });

    it("should fetch hourly usage with custom hours parameter", async () => {
      const mockResponse = { data: mockHourlyData };
      (callAPIWithETag as any).mockResolvedValueOnce(mockResponse);

      const result = await mcpAnalyticsService.getHourlyUsage(48);

      expect(callAPIWithETag).toHaveBeenCalledWith("/api/mcp/analytics/hourly?hours=48");
      expect(result).toEqual(mockHourlyData);
    });

    it("should fetch hourly usage with tool category filter", async () => {
      const mockResponse = { data: mockHourlyData };
      (callAPIWithETag as any).mockResolvedValueOnce(mockResponse);

      const result = await mcpAnalyticsService.getHourlyUsage(24, "rag");

      expect(callAPIWithETag).toHaveBeenCalledWith("/api/mcp/analytics/hourly?hours=24&tool_category=rag");
      expect(result).toEqual(mockHourlyData);
    });

    it("should fetch hourly usage with tool name filter", async () => {
      const mockResponse = { data: mockHourlyData };
      (callAPIWithETag as any).mockResolvedValueOnce(mockResponse);

      const result = await mcpAnalyticsService.getHourlyUsage(24, undefined, "rag_search_knowledge_base");

      expect(callAPIWithETag).toHaveBeenCalledWith(
        "/api/mcp/analytics/hourly?hours=24&tool_name=rag_search_knowledge_base",
      );
      expect(result).toEqual(mockHourlyData);
    });

    it("should fetch hourly usage with both category and tool name filters", async () => {
      const mockResponse = { data: mockHourlyData };
      (callAPIWithETag as any).mockResolvedValueOnce(mockResponse);

      const result = await mcpAnalyticsService.getHourlyUsage(168, "rag", "rag_search_code_examples");

      expect(callAPIWithETag).toHaveBeenCalledWith(
        "/api/mcp/analytics/hourly?hours=168&tool_category=rag&tool_name=rag_search_code_examples",
      );
      expect(result).toEqual(mockHourlyData);
    });

    it("should handle empty hourly data array", async () => {
      const mockResponse = { data: [] };
      (callAPIWithETag as any).mockResolvedValueOnce(mockResponse);

      const result = await mcpAnalyticsService.getHourlyUsage();

      expect(result).toEqual([]);
      expect(result).toHaveLength(0);
    });

    it("should handle API errors properly", async () => {
      const errorMessage = "Failed to fetch hourly usage";
      (callAPIWithETag as any).mockRejectedValueOnce(new Error(errorMessage));

      await expect(mcpAnalyticsService.getHourlyUsage()).rejects.toThrow(errorMessage);
    });

    it("should log errors to console", async () => {
      const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
      const error = new Error("API failure");
      (callAPIWithETag as any).mockRejectedValueOnce(error);

      await expect(mcpAnalyticsService.getHourlyUsage()).rejects.toThrow();

      expect(consoleErrorSpy).toHaveBeenCalledWith("Failed to get hourly usage:", error);
      consoleErrorSpy.mockRestore();
    });
  });

  describe("getDailyUsage", () => {
    const mockDailyData: DailyUsageData[] = [
      {
        date_bucket: "2024-01-01",
        tool_category: "rag",
        tool_name: "rag_search_knowledge_base",
        call_count: 340,
        avg_response_time_ms: 145,
        error_count: 12,
        unique_sessions: 45,
      },
      {
        date_bucket: "2024-01-02",
        tool_category: "task",
        tool_name: "manage_task",
        call_count: 120,
        avg_response_time_ms: 90,
        error_count: 3,
        unique_sessions: 28,
      },
    ];

    it("should fetch daily usage with default parameters (7 days)", async () => {
      const mockResponse = { data: mockDailyData };
      (callAPIWithETag as any).mockResolvedValueOnce(mockResponse);

      const result = await mcpAnalyticsService.getDailyUsage();

      expect(callAPIWithETag).toHaveBeenCalledWith("/api/mcp/analytics/daily?days=7");
      expect(result).toEqual(mockDailyData);
    });

    it("should fetch daily usage with custom days parameter", async () => {
      const mockResponse = { data: mockDailyData };
      (callAPIWithETag as any).mockResolvedValueOnce(mockResponse);

      const result = await mcpAnalyticsService.getDailyUsage(30);

      expect(callAPIWithETag).toHaveBeenCalledWith("/api/mcp/analytics/daily?days=30");
      expect(result).toEqual(mockDailyData);
    });

    it("should fetch daily usage with tool category filter", async () => {
      const mockResponse = { data: mockDailyData };
      (callAPIWithETag as any).mockResolvedValueOnce(mockResponse);

      const result = await mcpAnalyticsService.getDailyUsage(7, "project");

      expect(callAPIWithETag).toHaveBeenCalledWith("/api/mcp/analytics/daily?days=7&tool_category=project");
      expect(result).toEqual(mockDailyData);
    });

    it("should fetch daily usage with maximum range (180 days)", async () => {
      const mockResponse = { data: mockDailyData };
      (callAPIWithETag as any).mockResolvedValueOnce(mockResponse);

      const result = await mcpAnalyticsService.getDailyUsage(180, "rag");

      expect(callAPIWithETag).toHaveBeenCalledWith("/api/mcp/analytics/daily?days=180&tool_category=rag");
      expect(result).toEqual(mockDailyData);
    });

    it("should handle empty daily data array", async () => {
      const mockResponse = { data: [] };
      (callAPIWithETag as any).mockResolvedValueOnce(mockResponse);

      const result = await mcpAnalyticsService.getDailyUsage();

      expect(result).toEqual([]);
      expect(result).toHaveLength(0);
    });

    it("should handle API errors properly", async () => {
      const errorMessage = "Failed to fetch daily usage";
      (callAPIWithETag as any).mockRejectedValueOnce(new Error(errorMessage));

      await expect(mcpAnalyticsService.getDailyUsage()).rejects.toThrow(errorMessage);
    });

    it("should log errors to console", async () => {
      const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
      const error = new Error("API failure");
      (callAPIWithETag as any).mockRejectedValueOnce(error);

      await expect(mcpAnalyticsService.getDailyUsage()).rejects.toThrow();

      expect(consoleErrorSpy).toHaveBeenCalledWith("Failed to get daily usage:", error);
      consoleErrorSpy.mockRestore();
    });
  });

  describe("getSummary", () => {
    const mockSummary: UsageSummary = {
      last_24_hours: {
        total_calls: 1250,
        successful_calls: 1198,
        failed_calls: 52,
        success_rate: 95.84,
      },
      by_category: {
        rag: 687,
        project: 234,
        task: 189,
        document: 98,
        version: 42,
      },
      top_tools: [
        { tool: "rag_search_knowledge_base", calls: 542 },
        { tool: "find_projects", calls: 187 },
        { tool: "manage_task", calls: 134 },
        { tool: "rag_search_code_examples", calls: 98 },
        { tool: "find_tasks", calls: 76 },
      ],
    };

    it("should fetch summary statistics", async () => {
      (callAPIWithETag as any).mockResolvedValueOnce(mockSummary);

      const result = await mcpAnalyticsService.getSummary();

      expect(callAPIWithETag).toHaveBeenCalledWith("/api/mcp/analytics/summary");
      expect(result).toEqual(mockSummary);
    });

    it("should return complete summary structure with all fields", async () => {
      (callAPIWithETag as any).mockResolvedValueOnce(mockSummary);

      const result = await mcpAnalyticsService.getSummary();

      expect(result).toHaveProperty("last_24_hours");
      expect(result.last_24_hours).toHaveProperty("total_calls");
      expect(result.last_24_hours).toHaveProperty("successful_calls");
      expect(result.last_24_hours).toHaveProperty("failed_calls");
      expect(result.last_24_hours).toHaveProperty("success_rate");

      expect(result).toHaveProperty("by_category");
      expect(typeof result.by_category).toBe("object");

      expect(result).toHaveProperty("top_tools");
      expect(Array.isArray(result.top_tools)).toBe(true);
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

      (callAPIWithETag as any).mockResolvedValueOnce(emptySummary);

      const result = await mcpAnalyticsService.getSummary();

      expect(result.last_24_hours.total_calls).toBe(0);
      expect(result.top_tools).toHaveLength(0);
      expect(Object.keys(result.by_category)).toHaveLength(0);
    });

    it("should handle API errors properly", async () => {
      const errorMessage = "Failed to fetch summary";
      (callAPIWithETag as any).mockRejectedValueOnce(new Error(errorMessage));

      await expect(mcpAnalyticsService.getSummary()).rejects.toThrow(errorMessage);
    });

    it("should log errors to console", async () => {
      const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
      const error = new Error("API failure");
      (callAPIWithETag as any).mockRejectedValueOnce(error);

      await expect(mcpAnalyticsService.getSummary()).rejects.toThrow();

      expect(consoleErrorSpy).toHaveBeenCalledWith("Failed to get usage summary:", error);
      consoleErrorSpy.mockRestore();
    });
  });

  describe("Query parameter construction", () => {
    it("should properly encode special characters in tool names", async () => {
      const mockResponse = { data: [] };
      (callAPIWithETag as any).mockResolvedValueOnce(mockResponse);

      await mcpAnalyticsService.getHourlyUsage(24, undefined, "tool_with_special_chars:@#$");

      expect(callAPIWithETag).toHaveBeenCalledWith(
        "/api/mcp/analytics/hourly?hours=24&tool_name=tool_with_special_chars%3A%40%23%24",
      );
    });

    it("should properly encode special characters in category names", async () => {
      const mockResponse = { data: [] };
      (callAPIWithETag as any).mockResolvedValueOnce(mockResponse);

      await mcpAnalyticsService.getHourlyUsage(24, "category/with/slashes");

      expect(callAPIWithETag).toHaveBeenCalledWith(
        "/api/mcp/analytics/hourly?hours=24&tool_category=category%2Fwith%2Fslashes",
      );
    });

    it("should handle spaces in parameter values", async () => {
      const mockResponse = { data: [] };
      (callAPIWithETag as any).mockResolvedValueOnce(mockResponse);

      await mcpAnalyticsService.getDailyUsage(7, "tool category with spaces");

      expect(callAPIWithETag).toHaveBeenCalledWith(
        "/api/mcp/analytics/daily?days=7&tool_category=tool+category+with+spaces",
      );
    });

    it("should not add parameters when values are undefined", async () => {
      const mockResponse = { data: [] };
      (callAPIWithETag as any).mockResolvedValueOnce(mockResponse);

      await mcpAnalyticsService.getHourlyUsage(24, undefined, undefined);

      expect(callAPIWithETag).toHaveBeenCalledWith("/api/mcp/analytics/hourly?hours=24");
    });

    it("should handle zero as a valid parameter value", async () => {
      const mockResponse = { data: [] };
      (callAPIWithETag as any).mockResolvedValueOnce(mockResponse);

      await mcpAnalyticsService.getHourlyUsage(0);

      expect(callAPIWithETag).toHaveBeenCalledWith("/api/mcp/analytics/hourly?hours=0");
    });
  });

  describe("Response data validation", () => {
    it("should preserve all hourly data fields", async () => {
      const complexHourlyData: HourlyUsageData[] = [
        {
          hour_bucket: "2024-01-01T12:00:00Z",
          tool_category: "rag",
          tool_name: "rag_read_full_page",
          call_count: 9999,
          avg_response_time_ms: 9999.99,
          error_count: 999,
          unique_sessions: 99,
        },
      ];

      const mockResponse = { data: complexHourlyData };
      (callAPIWithETag as any).mockResolvedValueOnce(mockResponse);

      const result = await mcpAnalyticsService.getHourlyUsage();

      expect(result[0]).toEqual(complexHourlyData[0]);
      expect(result[0].hour_bucket).toBe("2024-01-01T12:00:00Z");
      expect(result[0].tool_category).toBe("rag");
      expect(result[0].tool_name).toBe("rag_read_full_page");
      expect(result[0].call_count).toBe(9999);
      expect(result[0].avg_response_time_ms).toBe(9999.99);
      expect(result[0].error_count).toBe(999);
      expect(result[0].unique_sessions).toBe(99);
    });

    it("should preserve all daily data fields", async () => {
      const complexDailyData: DailyUsageData[] = [
        {
          date_bucket: "2024-12-31",
          tool_category: "version",
          tool_name: "manage_version",
          call_count: 8888,
          avg_response_time_ms: 8888.88,
          error_count: 888,
          unique_sessions: 88,
        },
      ];

      const mockResponse = { data: complexDailyData };
      (callAPIWithETag as any).mockResolvedValueOnce(mockResponse);

      const result = await mcpAnalyticsService.getDailyUsage();

      expect(result[0]).toEqual(complexDailyData[0]);
      expect(result[0].date_bucket).toBe("2024-12-31");
      expect(result[0].tool_category).toBe("version");
      expect(result[0].tool_name).toBe("manage_version");
      expect(result[0].call_count).toBe(8888);
      expect(result[0].avg_response_time_ms).toBe(8888.88);
      expect(result[0].error_count).toBe(888);
      expect(result[0].unique_sessions).toBe(88);
    });

    it("should preserve all summary fields with nested structure", async () => {
      const complexSummary: UsageSummary = {
        last_24_hours: {
          total_calls: 100000,
          successful_calls: 99900,
          failed_calls: 100,
          success_rate: 99.9,
        },
        by_category: {
          rag: 50000,
          project: 20000,
          task: 15000,
          document: 10000,
          version: 5000,
        },
        top_tools: [
          { tool: "tool1", calls: 10000 },
          { tool: "tool2", calls: 9000 },
          { tool: "tool3", calls: 8000 },
          { tool: "tool4", calls: 7000 },
          { tool: "tool5", calls: 6000 },
        ],
      };

      (callAPIWithETag as any).mockResolvedValueOnce(complexSummary);

      const result = await mcpAnalyticsService.getSummary();

      expect(result).toEqual(complexSummary);
      expect(result.last_24_hours.total_calls).toBe(100000);
      expect(result.last_24_hours.success_rate).toBe(99.9);
      expect(result.by_category.rag).toBe(50000);
      expect(result.top_tools).toHaveLength(5);
      expect(result.top_tools[0].tool).toBe("tool1");
      expect(result.top_tools[0].calls).toBe(10000);
    });
  });
});
