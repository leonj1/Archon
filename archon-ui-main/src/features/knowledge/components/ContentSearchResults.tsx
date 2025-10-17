/**
 * Content Search Results Component
 * Displays search results from full-text content search across all knowledge bases
 */

import { motion } from "framer-motion";
import { AlertCircle, ExternalLink, FileText, Loader2 } from "lucide-react";
import { Button } from "../../ui/primitives";
import type { DocumentChunk, KnowledgeItem } from "../types";

interface ContentSearchResultsProps {
  query: string;
  results: DocumentChunk[];
  isLoading: boolean;
  error: Error | null;
  knowledgeItems: KnowledgeItem[];
  onClearSearch: () => void;
  onViewDocument: (sourceId: string) => void;
}

const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3, ease: [0.23, 1, 0.32, 1] },
  },
};

export const ContentSearchResults: React.FC<ContentSearchResultsProps> = ({
  query,
  results,
  isLoading,
  error,
  knowledgeItems,
  onClearSearch,
  onViewDocument,
}) => {
  // Helper to get knowledge item title from source_id
  const getKnowledgeItemTitle = (sourceId: string): string => {
    const item = knowledgeItems.find((k) => k.source_id === sourceId);
    return item?.title || "Unknown Source";
  };

  // Highlight search terms in text
  const highlightText = (text: string, searchQuery: string) => {
    if (!searchQuery.trim()) return text;

    const terms = searchQuery.toLowerCase().split(/\s+/);
    const regex = new RegExp(`(${terms.join("|")})`, "gi");
    const parts = text.split(regex);

    return parts.map((part, i) => {
      const isMatch = terms.some((term) => part.toLowerCase() === term);
      // Use part content + offset for unique key to avoid index-based keys
      const offset = text.indexOf(part, i > 0 ? text.indexOf(parts[i - 1]) + parts[i - 1].length : 0);
      return isMatch ? (
        <mark key={`mark-${offset}-${part}`} className="bg-yellow-500/30 text-yellow-200 px-0.5">
          {part}
        </mark>
      ) : (
        <span key={`text-${offset}-${part.substring(0, 10)}`}>{part}</span>
      );
    });
  };

  // Loading state
  if (isLoading) {
    return (
      <motion.div initial="hidden" animate="visible" variants={itemVariants} className="py-12">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-purple-400 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Searching across all knowledge bases...</p>
          <p className="text-sm text-gray-500 mt-2">Query: "{query}"</p>
        </div>
      </motion.div>
    );
  }

  // Error state
  if (error) {
    return (
      <motion.div initial="hidden" animate="visible" variants={itemVariants} className="py-12">
        <div className="text-center max-w-md mx-auto">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-red-500/10 dark:bg-red-500/10 mb-4">
            <AlertCircle className="w-6 h-6 text-red-400" />
          </div>
          <h3 className="text-lg font-semibold mb-2">Search Failed</h3>
          <p className="text-gray-400 mb-4">{error.message}</p>
          <Button onClick={onClearSearch} variant="outline">
            Clear Search
          </Button>
        </div>
      </motion.div>
    );
  }

  // Empty results
  if (results.length === 0) {
    return (
      <motion.div initial="hidden" animate="visible" variants={itemVariants} className="py-12">
        <div className="text-center max-w-md mx-auto">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-purple-500/10 dark:bg-purple-500/10 mb-4">
            <FileText className="w-6 h-6 text-purple-400" />
          </div>
          <h3 className="text-lg font-semibold mb-2">No Content Found</h3>
          <p className="text-gray-400 mb-2">
            No results found for "<span className="text-white">{query}</span>"
          </p>
          <p className="text-sm text-gray-500 mb-4">Try different keywords or check your knowledge base content.</p>
          <Button onClick={onClearSearch} variant="outline">
            Clear Search
          </Button>
        </div>
      </motion.div>
    );
  }

  // Results list
  return (
    <div className="space-y-4">
      {/* Search header */}
      <div className="flex items-center justify-between pb-4 border-b border-white/10">
        <div>
          <h3 className="text-lg font-semibold text-white mb-1">Content Search Results ({results.length})</h3>
          <p className="text-sm text-gray-400">
            Found in {new Set(results.map((r) => r.source_id)).size} knowledge base(s)
          </p>
        </div>
        <Button onClick={onClearSearch} variant="outline" size="sm">
          Clear Search
        </Button>
      </div>

      {/* Results */}
      <div className="space-y-3">
        {results.map((result, index) => {
          const sourceTitle = getKnowledgeItemTitle(result.source_id);

          return (
            <motion.div
              key={`${result.source_id}-${index}`}
              initial="hidden"
              animate="visible"
              variants={itemVariants}
              className="bg-black/30 border border-white/10 rounded-lg p-4 hover:border-purple-500/30 transition-colors"
            >
              {/* Source info */}
              <div className="flex items-start justify-between gap-3 mb-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium text-white truncate">{result.title || "Untitled"}</h4>
                    {result.section && (
                      <span className="text-xs text-gray-400 bg-white/5 px-2 py-0.5 rounded">{result.section}</span>
                    )}
                  </div>
                  <button
                    type="button"
                    onClick={() => onViewDocument(result.source_id)}
                    className="text-sm text-purple-400 hover:text-purple-300 flex items-center gap-1 group"
                  >
                    <span className="truncate">{sourceTitle}</span>
                    <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                  </button>
                </div>
              </div>

              {/* Content preview with highlighting */}
              <p className="text-sm text-gray-300 leading-relaxed line-clamp-3">
                {highlightText(result.content, query)}
              </p>

              {/* URL if available */}
              {result.url && (
                <a
                  href={result.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-cyan-400 hover:text-cyan-300 mt-2 inline-flex items-center gap-1"
                >
                  View Source
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};
