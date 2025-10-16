import { AlertCircle, Clock, Database, Loader2, TrendingUp } from "lucide-react";
import React from "react";
import { Card } from "@/features/ui/primitives/card";
import { cn } from "@/features/ui/primitives/styles";
import { useMcpKnowledgeBaseAnalytics } from "../hooks/useMcpKnowledgeBaseAnalytics";

interface KnowledgeBaseUsageCardProps {
  hours?: number;
}

interface TooltipData {
  name: string;
  queryCount: number;
  avgResponseTimeMs: number;
  successRate: number;
}

const KnowledgeBaseTooltip: React.FC<TooltipData> = ({ name, queryCount, avgResponseTimeMs, successRate }) => {
  return (
    <div className="bg-black/90 dark:bg-black/95 text-white p-3 rounded-lg shadow-lg border border-white/10 backdrop-blur-sm min-w-[250px]">
      <p className="font-semibold mb-2 text-purple-400">{name}</p>
      <div className="space-y-1 text-sm">
        <p className="flex items-center justify-between gap-4">
          <span className="flex items-center gap-2">
            <Database className="w-3 h-3 text-purple-400" />
            Queries:
          </span>
          <span className="font-medium">{queryCount.toLocaleString()}</span>
        </p>
        <p className="flex items-center justify-between gap-4">
          <span className="flex items-center gap-2">
            <Clock className="w-3 h-3 text-blue-400" />
            Avg Time:
          </span>
          <span className="font-medium">{avgResponseTimeMs.toFixed(0)}ms</span>
        </p>
        <p className="flex items-center justify-between gap-4">
          <span className="flex items-center gap-2">
            <TrendingUp className="w-3 h-3 text-green-400" />
            Success:
          </span>
          <span className="font-medium text-green-400">{successRate.toFixed(1)}%</span>
        </p>
      </div>
    </div>
  );
};

export const KnowledgeBaseUsageCard: React.FC<KnowledgeBaseUsageCardProps> = ({ hours = 24 }) => {
  const { data, isLoading, error } = useMcpKnowledgeBaseAnalytics(hours);
  const [hoveredIndex, setHoveredIndex] = React.useState<number | null>(null);

  // Loading state
  if (isLoading) {
    return (
      <Card blur="md" transparency="light" size="lg" className="relative">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 rounded-lg bg-purple-500/10 dark:bg-purple-400/10">
            <Database className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Knowledge Base Usage</h3>
        </div>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
        </div>
      </Card>
    );
  }

  // Error state
  if (error) {
    return (
      <Card blur="md" transparency="light" size="lg" className="relative">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 rounded-lg bg-purple-500/10 dark:bg-purple-400/10">
            <Database className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Knowledge Base Usage</h3>
        </div>
        <div className="text-center py-8">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-sm text-gray-600 dark:text-gray-400">Failed to load knowledge base analytics</p>
          <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">{(error as Error)?.message}</p>
        </div>
      </Card>
    );
  }

  // Empty state
  if (!data || !data.data || data.data.length === 0) {
    return (
      <Card blur="md" transparency="light" size="lg" className="relative">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 rounded-lg bg-purple-500/10 dark:bg-purple-400/10">
            <Database className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Knowledge Base Usage</h3>
        </div>
        <div className="text-center py-8">
          <Database className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">No knowledge bases queried yet</p>
          <p className="text-xs text-gray-500 dark:text-gray-500">Start using RAG tools to search your knowledge</p>
        </div>
      </Card>
    );
  }

  // Get the knowledge base data array
  const knowledgeBases = data.data;

  // Calculate max query count for percentage calculations
  const maxQueries = Math.max(...knowledgeBases.map((kb) => kb.query_count));

  // Take top 5 knowledge bases (or all if less than 5)
  const topKnowledgeBases = knowledgeBases.slice(0, 5);

  return (
    <Card
      blur="md"
      transparency="light"
      glowColor="purple"
      glowType="outer"
      glowSize="sm"
      size="lg"
      className="relative transition-all duration-300 hover:scale-[1.01]"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 rounded-lg bg-purple-500/10 dark:bg-purple-400/10">
          <Database className="w-5 h-5 text-purple-600 dark:text-purple-400" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Knowledge Base Usage</h3>
          <p className="text-xs text-gray-600 dark:text-gray-400">
            Top {topKnowledgeBases.length} most queried {topKnowledgeBases.length === 1 ? "source" : "sources"}
          </p>
        </div>
      </div>

      {/* Knowledge base list with horizontal bars */}
      <div className="space-y-4">
        {topKnowledgeBases.map((kb, index) => {
          const percentage = maxQueries > 0 ? (kb.query_count / maxQueries) * 100 : 0;
          const isHovered = hoveredIndex === index;

          return (
            <div
              key={kb.source_name}
              className="relative"
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              {/* Tooltip on hover */}
              {isHovered && (
                <div className="absolute left-0 bottom-full mb-2 z-50 animate-in fade-in slide-in-from-bottom-2 duration-200">
                  <KnowledgeBaseTooltip
                    name={kb.source_name}
                    queryCount={kb.query_count}
                    avgResponseTimeMs={kb.avg_response_time_ms}
                    successRate={kb.success_rate}
                  />
                </div>
              )}

              {/* Knowledge base item */}
              <div className="space-y-2">
                {/* Name and metrics */}
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="text-xs font-medium text-gray-500 dark:text-gray-400 w-4 shrink-0">
                      {index + 1}.
                    </span>
                    <span className="text-sm font-medium text-gray-900 dark:text-white truncate" title={kb.source_name}>
                      {kb.source_name}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <span className="text-xs text-gray-600 dark:text-gray-400">
                      {kb.query_count} {kb.query_count === 1 ? "query" : "queries"}
                    </span>
                    <span className="text-xs font-semibold text-purple-600 dark:text-purple-400 w-12 text-right">
                      {percentage.toFixed(0)}%
                    </span>
                  </div>
                </div>

                {/* Horizontal bar */}
                <div className="relative h-2 bg-gray-200/50 dark:bg-gray-700/50 rounded-full overflow-hidden">
                  {/* Background glow */}
                  <div
                    className={cn(
                      "absolute inset-y-0 left-0 bg-purple-500/20 dark:bg-purple-400/20 blur-sm transition-all duration-300",
                      isHovered && "bg-purple-500/30 dark:bg-purple-400/30",
                    )}
                    style={{ width: `${percentage}%` }}
                  />
                  {/* Solid bar */}
                  <div
                    className={cn(
                      "absolute inset-y-0 left-0 bg-gradient-to-r from-purple-500 to-purple-600 dark:from-purple-400 dark:to-purple-500 rounded-full transition-all duration-500 ease-out",
                      isHovered && "from-purple-600 to-purple-700 dark:from-purple-300 dark:to-purple-400",
                    )}
                    style={{ width: `${percentage}%` }}
                  />
                </div>

                {/* Quick stats row */}
                <div className="flex items-center gap-4 text-xs text-gray-600 dark:text-gray-400 pl-6">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {kb.avg_response_time_ms.toFixed(0)}ms
                  </span>
                  <span className="flex items-center gap-1">
                    <TrendingUp className="w-3 h-3 text-green-600 dark:text-green-400" />
                    {kb.success_rate.toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer info if there are more than 5 knowledge bases */}
      {knowledgeBases.length > 5 && (
        <div className="mt-6 pt-4 border-t border-gray-200/30 dark:border-gray-700/30">
          <p className="text-xs text-gray-500 dark:text-gray-500 text-center">
            Showing top 5 of {knowledgeBases.length} knowledge bases
          </p>
        </div>
      )}
    </Card>
  );
};
