/**
 * Sort Control Component
 * Provides dropdown to select sort field and toggle sort direction
 */

import { ArrowDown, ArrowUp, ArrowUpDown } from "lucide-react";
import { Button } from "../../ui/primitives";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "../../ui/primitives/dropdown-menu";
import type { KnowledgeSortConfig, KnowledgeSortField } from "../types";

interface SortControlProps {
  sortConfig: KnowledgeSortConfig;
  onSortChange: (config: KnowledgeSortConfig) => void;
}

const SORT_LABELS: Record<KnowledgeSortField, string> = {
  title: "Name",
  created_at: "Created Date",
  updated_at: "Updated Date",
  status: "Status",
  document_count: "Documents",
  code_examples_count: "Code Examples",
};

export const SortControl: React.FC<SortControlProps> = ({ sortConfig, onSortChange }) => {
  const toggleDirection = () => {
    onSortChange({
      ...sortConfig,
      direction: sortConfig.direction === "asc" ? "desc" : "asc",
    });
  };

  const handleFieldChange = (field: KnowledgeSortField) => {
    onSortChange({
      field,
      direction: sortConfig.direction,
    });
  };

  const DirectionIcon = sortConfig.direction === "asc" ? ArrowUp : ArrowDown;

  return (
    <div className="flex items-center gap-1 bg-black/30 rounded-lg border border-white/10 p-1">
      {/* Sort field dropdown */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="text-gray-400 hover:text-white flex items-center gap-2"
            aria-label="Select sort field"
          >
            <ArrowUpDown className="w-4 h-4" />
            <span className="hidden sm:inline">{SORT_LABELS[sortConfig.field]}</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48 bg-gray-900 border-white/10">
          {Object.entries(SORT_LABELS).map(([field, label]) => (
            <DropdownMenuItem
              key={field}
              onClick={() => handleFieldChange(field as KnowledgeSortField)}
              className={
                sortConfig.field === field
                  ? "bg-cyan-500/20 text-cyan-400 focus:bg-cyan-500/30 focus:text-cyan-400"
                  : "text-gray-300 focus:bg-white/10 focus:text-white"
              }
            >
              {label}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Direction toggle button */}
      <Button
        variant="ghost"
        size="sm"
        onClick={toggleDirection}
        className="px-3 text-gray-400 hover:text-white"
        aria-label={`Sort ${sortConfig.direction === "asc" ? "ascending" : "descending"}`}
        title={`Sort ${sortConfig.direction === "asc" ? "ascending" : "descending"}`}
      >
        <DirectionIcon className="w-4 h-4" />
      </Button>
    </div>
  );
};
