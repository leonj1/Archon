export interface KnowledgeBaseUsageItem {
  source_id: string;
  source_name: string;
  query_count: number;
  unique_queries: number;
  avg_response_time_ms: number;
  success_rate: number;
  percentage_of_total: number;
}

export interface KnowledgeBaseAnalyticsResponse {
  success: boolean;
  data: KnowledgeBaseUsageItem[];
  total_queries: number;
  period: {
    hours: number;
    start_time: string;
    end_time: string;
  };
}
