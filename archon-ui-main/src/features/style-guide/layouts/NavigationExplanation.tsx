import { ChevronRight } from "lucide-react";
import { Card } from "@/features/ui/primitives/card";

export const NavigationExplanation = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
          Navigation Patterns
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Archon uses a layered navigation approach with distinct patterns for different navigation levels.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Main Navigation */}
        <Card className="p-6">
          <div className="flex items-start gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-cyan-500/20 flex items-center justify-center">
              <span className="text-cyan-400 font-bold">1</span>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Main Navigation
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Fixed left sidebar (72px wide) with icon-based navigation. Always visible across all pages.
              </p>
            </div>
          </div>
          <div className="bg-black/20 rounded-lg p-4 border border-white/10">
            <code className="text-xs text-gray-300">
              <div>position: fixed</div>
              <div>left: 24px (left-6)</div>
              <div>width: 72px</div>
              <div>Icon-based with tooltips</div>
            </code>
          </div>
        </Card>

        {/* Content Area */}
        <Card className="p-6">
          <div className="flex items-start gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
              <span className="text-purple-400 font-bold">2</span>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Content Area
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                All page content lives in the content area with left padding to accommodate main nav.
              </p>
            </div>
          </div>
          <div className="bg-black/20 rounded-lg p-4 border border-white/10">
            <code className="text-xs text-gray-300">
              <div>padding-left: 100px (pl-[100px])</div>
              <div>Gives space for 72px nav + 28px gap</div>
              <div>All layouts exist INSIDE this area</div>
            </code>
          </div>
        </Card>

        {/* Page Navigation */}
        <Card className="p-6">
          <div className="flex items-start gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
              <span className="text-blue-400 font-bold">3</span>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Page Navigation
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Top-level tabs or pills for page sections. Uses Radix Tabs primitive with glassmorphism.
              </p>
            </div>
          </div>
          <div className="bg-black/20 rounded-lg p-4 border border-white/10">
            <code className="text-xs text-gray-300">
              <div>{'<Tabs>'} with TabsList</div>
              <div>Example: Docs/Tasks tabs</div>
              <div>Color variants: cyan, blue, purple, orange</div>
            </code>
          </div>
        </Card>

        {/* View Controls */}
        <Card className="p-6">
          <div className="flex items-start gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
              <span className="text-green-400 font-bold">4</span>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                View Controls
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Toggle buttons for switching between view modes (grid/table/list).
              </p>
            </div>
          </div>
          <div className="bg-black/20 rounded-lg p-4 border border-white/10">
            <code className="text-xs text-gray-300">
              <div>Icon buttons with active state</div>
              <div>Grid, List, Table icons</div>
              <div>Glassmorphism background</div>
            </code>
          </div>
        </Card>
      </div>

      {/* Visual Hierarchy */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Navigation Hierarchy
        </h3>
        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <span className="px-3 py-1 bg-cyan-500/20 text-cyan-400 rounded border border-cyan-400/30">
            Main Nav
          </span>
          <ChevronRight className="w-4 h-4" />
          <span className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded border border-purple-400/30">
            Content Area
          </span>
          <ChevronRight className="w-4 h-4" />
          <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded border border-blue-400/30">
            Page Tabs
          </span>
          <ChevronRight className="w-4 h-4" />
          <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded border border-green-400/30">
            View Controls
          </span>
        </div>
      </Card>

      {/* Key Point */}
      <div className="bg-orange-500/10 border border-orange-400/30 rounded-lg p-4">
        <p className="text-sm text-gray-700 dark:text-gray-300">
          <strong className="text-orange-600 dark:text-orange-400">Important:</strong>{" "}
          Main navigation is OUTSIDE the content area (fixed position). All page layouts
          (including sidebar variants) exist INSIDE the content area and use relative positioning
          to avoid overlapping with the main nav.
        </p>
      </div>
    </div>
  );
};
