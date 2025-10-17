/**
 * Search Mode Toggle Component
 * Allows users to switch between title and content search modes
 */

import { FileText, Search } from "lucide-react";
import { Button } from "../../ui/primitives";
import { cn } from "../../ui/primitives/styles";

export type SearchMode = "title" | "content";

interface SearchModeToggleProps {
  mode: SearchMode;
  onModeChange: (mode: SearchMode) => void;
}

export const SearchModeToggle: React.FC<SearchModeToggleProps> = ({ mode, onModeChange }) => {
  return (
    <div className="flex gap-1 p-1 bg-black/30 rounded-lg border border-white/10">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => onModeChange("title")}
        aria-label="Search titles"
        aria-pressed={mode === "title"}
        title="Search by title"
        className={cn(
          "px-3 flex items-center gap-2 text-xs",
          mode === "title" ? "bg-cyan-500/20 dark:bg-cyan-500/20 text-cyan-400" : "text-gray-400 hover:text-white",
        )}
      >
        <Search className="w-3.5 h-3.5" aria-hidden="true" />
        <span className="hidden sm:inline">Title</span>
      </Button>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => onModeChange("content")}
        aria-label="Search content"
        aria-pressed={mode === "content"}
        title="Search within content"
        className={cn(
          "px-3 flex items-center gap-2 text-xs",
          mode === "content"
            ? "bg-purple-500/20 dark:bg-purple-500/20 text-purple-400"
            : "text-gray-400 hover:text-white",
        )}
      >
        <FileText className="w-3.5 h-3.5" aria-hidden="true" />
        <span className="hidden sm:inline">Content</span>
      </Button>
    </div>
  );
};
