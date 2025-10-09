import { useState } from "react";
import { Grid, List, Asterisk, Terminal, FileCode, Globe, FileText, Calendar } from "lucide-react";
import { Button } from "@/features/ui/primitives/button";
import { DataCard, DataCardHeader, DataCardContent, DataCardFooter } from "@/features/ui/primitives/data-card";
import { StatPill } from "@/features/ui/primitives/pill";
import { Input } from "@/features/ui/primitives/input";
import { ToggleGroup, ToggleGroupItem } from "@/features/ui/primitives/toggle-group";
import { cn } from "@/features/ui/primitives/styles";

const MOCK_KNOWLEDGE_ITEMS = [
  {
    id: "1",
    title: "React Documentation",
    type: "technical",
    url: "https://react.dev",
    date: "2024-01-15",
    chunks: 145,
  },
  {
    id: "2",
    title: "Product Requirements",
    type: "business",
    url: null,
    date: "2024-01-20",
    chunks: 23,
  },
  {
    id: "3",
    title: "FastAPI Guide",
    type: "technical",
    url: "https://fastapi.tiangolo.com",
    date: "2024-01-18",
    chunks: 89,
  },
  {
    id: "4",
    title: "TailwindCSS Docs",
    type: "technical",
    url: "https://tailwindcss.com",
    date: "2024-01-22",
    chunks: 112,
  },
  {
    id: "5",
    title: "Marketing Strategy",
    type: "business",
    url: null,
    date: "2024-01-10",
    chunks: 15,
  },
  {
    id: "6",
    title: "TypeScript Handbook",
    type: "technical",
    url: "https://www.typescriptlang.org/docs",
    date: "2024-01-25",
    chunks: 203,
  },
];

export const KnowledgeLayoutExample = () => {
  const [viewMode, setViewMode] = useState<"grid" | "table">("grid");
  const [typeFilter, setTypeFilter] = useState("all");

  return (
    <div className="space-y-4">
      {/* Explanation Text */}
      <p className="text-sm text-gray-600 dark:text-gray-400">
        <strong>Use this layout for:</strong> Switchable views (grid/table/list), filterable data,
        search interfaces. Users can toggle between dense (table) and spacious (grid) layouts.
      </p>

      {/* Header with Controls */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <Input placeholder="Search knowledge base..." className="max-w-xs" />

        <div className="flex gap-2 items-center">
          {/* Type Filter */}
          <ToggleGroup
            type="single"
            size="sm"
            value={typeFilter}
            onValueChange={(v) => v && setTypeFilter(v)}
            aria-label="Filter type"
          >
            <ToggleGroupItem value="all" aria-label="All" title="All">
              <Asterisk className="w-4 h-4" />
            </ToggleGroupItem>
            <ToggleGroupItem value="technical" aria-label="Technical" title="Technical">
              <Terminal className="w-4 h-4" />
            </ToggleGroupItem>
            <ToggleGroupItem value="business" aria-label="Business" title="Business">
              <FileCode className="w-4 h-4" />
            </ToggleGroupItem>
          </ToggleGroup>

          {/* View Toggle */}
          <div className="flex gap-1 p-1 bg-black/30 rounded-lg border border-white/10">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setViewMode("grid")}
              className={cn("px-3", viewMode === "grid" && "bg-cyan-500/20 text-cyan-400")}
            >
              <Grid className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setViewMode("table")}
              className={cn("px-3", viewMode === "table" && "bg-cyan-500/20 text-cyan-400")}
            >
              <List className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Conditional View Rendering */}
      {viewMode === "grid" ? (
        // Grid View - Responsive columns
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {MOCK_KNOWLEDGE_ITEMS.map((item) => (
            <KnowledgeCard key={item.id} item={item} />
          ))}
        </div>
      ) : (
        // Table View - Overflow-x-auto wrapper
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Title
                </th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Type
                </th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Source
                </th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Chunks
                </th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Date
                </th>
              </tr>
            </thead>
            <tbody>
              {MOCK_KNOWLEDGE_ITEMS.map((item) => (
                <KnowledgeTableRow key={item.id} item={item} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

// Grid Card Component - using DataCard primitive
const KnowledgeCard = ({ item }: { item: typeof MOCK_KNOWLEDGE_ITEMS[0] }) => {
  const isUrl = !!item.url;
  const isTechnical = item.type === "technical";

  const getEdgeColor = (): "cyan" | "purple" | "blue" | "pink" => {
    if (isTechnical) return isUrl ? "cyan" : "purple";
    return isUrl ? "blue" : "pink";
  };

  return (
    <DataCard
      edgePosition="top"
      edgeColor={getEdgeColor()}
      className="cursor-pointer hover:shadow-[0_0_30px_rgba(6,182,212,0.2)] transition-shadow"
    >
      <DataCardHeader>
        <div className="flex items-center gap-2 mb-3">
          <div
            className={cn(
              "flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium",
              isUrl
                ? "bg-cyan-100 text-cyan-700 dark:bg-cyan-500/10 dark:text-cyan-400"
                : "bg-purple-100 text-purple-700 dark:bg-purple-500/10 dark:text-purple-400",
            )}
          >
            {isUrl ? <Globe className="w-3.5 h-3.5" /> : <FileText className="w-3.5 h-3.5" />}
            <span>{isUrl ? "Web Page" : "Document"}</span>
          </div>
          <span
            className={cn(
              "px-2 py-1 text-xs rounded-md font-medium",
              item.type === "technical"
                ? "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400"
                : "bg-purple-500/10 text-purple-600 dark:text-purple-400",
            )}
          >
            {item.type}
          </span>
        </div>

        <h4 className="font-medium text-gray-900 dark:text-white mb-2 line-clamp-2">{item.title}</h4>

        {item.url && <div className="text-xs text-gray-600 dark:text-gray-400 truncate">{item.url}</div>}
      </DataCardHeader>

      <DataCardContent />

      <DataCardFooter>
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-1 text-gray-600 dark:text-gray-400">
            <Calendar className="w-3 h-3" />
            <span>{item.date}</span>
          </div>
          <StatPill
            color="orange"
            value={item.chunks}
            icon={<FileText className="w-3.5 h-3.5" />}
            size="sm"
            onClick={() => console.log('View documents')}
            className="cursor-pointer hover:scale-105 transition-transform"
          />
        </div>
      </DataCardFooter>
    </DataCard>
  );
};

// Table Row Component
const KnowledgeTableRow = ({ item }: { item: typeof MOCK_KNOWLEDGE_ITEMS[0] }) => {
  return (
    <tr className="border-b border-white/5 hover:bg-white/5 dark:hover:bg-white/5 transition-colors cursor-pointer">
      <td className="py-3 px-4">
        <div className="flex items-center gap-2">
          {item.url ? (
            <Globe className="w-4 h-4 text-cyan-500 flex-shrink-0" />
          ) : (
            <FileText className="w-4 h-4 text-purple-500 flex-shrink-0" />
          )}
          <span className="text-sm text-gray-900 dark:text-white">{item.title}</span>
        </div>
      </td>
      <td className="py-3 px-4">
        <span
          className={cn(
            "px-2 py-0.5 text-xs rounded border",
            item.type === "technical"
              ? "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border-cyan-500/30"
              : "bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/30",
          )}
        >
          {item.type}
        </span>
      </td>
      <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400 max-w-xs truncate">
        {item.url || "Uploaded Document"}
      </td>
      <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">{item.chunks}</td>
      <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">{item.date}</td>
    </tr>
  );
};
