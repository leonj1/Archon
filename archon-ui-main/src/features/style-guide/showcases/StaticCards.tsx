import { Card } from "@/features/ui/primitives/card";
import { cn } from "@/features/ui/primitives/styles";

export const StaticCards = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Cards</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Glass card variants used in the application
        </p>
      </div>

      <div className="space-y-6">
        {/* Base Glass Card */}
        <div>
          <h4 className="text-sm font-semibold mb-3 text-gray-800 dark:text-gray-200">Base Glass Card</h4>
          <Card className="p-6 max-w-md">
            <h5 className="font-medium text-gray-900 dark:text-white mb-2">Card Title</h5>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Default glass card with backdrop blur and semi-transparent background. Used for general containers, settings panels, and content wrappers.
            </p>
          </Card>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 font-mono">
            {"<Card />"}
          </p>
        </div>

        {/* Outer Glow Card */}
        <div>
          <h4 className="text-sm font-semibold mb-3 text-gray-800 dark:text-gray-200">Outer Glow Card</h4>
          <div className="relative max-w-md">
            <div className="absolute inset-0 bg-cyan-500/20 blur-xl rounded-xl" />
            <Card className="p-6 relative border-cyan-500/30 hover:shadow-[0_0_30px_rgba(6,182,212,0.4)] transition-shadow">
              <h5 className="font-medium text-gray-900 dark:text-white mb-2">Active Card</h5>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Card with external glow. Used for selected or active states. Hover to see enhanced glow.
              </p>
            </Card>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 font-mono">
            shadow-[0_0_30px_rgba(6,182,212,0.3)] + hover effect
          </p>
        </div>

        {/* Inner Glow Card */}
        <div>
          <h4 className="text-sm font-semibold mb-3 text-gray-800 dark:text-gray-200">Inner Glow Card</h4>
          <Card className="p-6 max-w-md shadow-[inset_0_0_20px_rgba(59,130,246,0.2)] border-blue-500/30">
            <h5 className="font-medium text-gray-900 dark:text-white mb-2">Featured Card</h5>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Card with internal glow effect. Used for special containers, featured sections, and highlighted content areas.
            </p>
          </Card>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 font-mono">
            shadow-[inset_0_0_20px_rgba(59,130,246,0.2)]
          </p>
        </div>

        {/* Top Edge Glow Card */}
        <div>
          <h4 className="text-sm font-semibold mb-3 text-gray-800 dark:text-gray-200">Top Edge Glow Card</h4>
          <div className="relative overflow-hidden rounded-xl max-w-md">
            <div className="absolute inset-x-0 top-0 h-[2px] bg-cyan-500 mx-1 mt-0.5 rounded-full pointer-events-none" />
            <div className="absolute inset-x-0 top-0 h-8 bg-gradient-to-b from-cyan-500/25 to-transparent blur-md -mt-1 pointer-events-none" />
            <Card className="p-6 relative border-cyan-500/30 bg-gradient-to-b from-cyan-100/50 via-cyan-50/25 to-white/60 dark:from-cyan-900/20 dark:via-cyan-900/10 dark:to-black/30">
              <h5 className="font-medium text-gray-900 dark:text-white mb-2">Knowledge Item</h5>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Card with colored top edge glow. Used for knowledge cards - cyan for technical web pages, purple for uploaded docs, blue for business content.
              </p>
            </Card>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 font-mono">
            Top hairline (2px) + blur smear (8px)
          </p>
        </div>
      </div>
    </div>
  );
};
