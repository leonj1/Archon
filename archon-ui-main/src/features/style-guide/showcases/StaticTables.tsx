export const StaticTables = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Tables</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Table styles with glassmorphism and hover states
        </p>
      </div>

      {/* Basic Table */}
      <div>
        <h3 className="text-sm font-semibold mb-3 text-gray-800 dark:text-gray-200">Standard Table</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Name
                </th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Status
                </th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Count
                </th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Date
                </th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-white/5 hover:bg-white/5 dark:hover:bg-white/5 transition-colors">
                <td className="py-3 px-4 text-sm text-gray-900 dark:text-white">React Documentation</td>
                <td className="py-3 px-4">
                  <span className="px-2 py-1 text-xs rounded-md bg-green-500/10 text-green-600 dark:text-green-400">
                    Active
                  </span>
                </td>
                <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">145</td>
                <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">2024-01-15</td>
              </tr>
              <tr className="border-b border-white/5 hover:bg-white/5 dark:hover:bg-white/5 transition-colors">
                <td className="py-3 px-4 text-sm text-gray-900 dark:text-white">API Integration</td>
                <td className="py-3 px-4">
                  <span className="px-2 py-1 text-xs rounded-md bg-yellow-500/10 text-yellow-600 dark:text-yellow-400">
                    Processing
                  </span>
                </td>
                <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">89</td>
                <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">2024-01-18</td>
              </tr>
              <tr className="border-b border-white/5 hover:bg-white/5 dark:hover:bg-white/5 transition-colors">
                <td className="py-3 px-4 text-sm text-gray-900 dark:text-white">TypeScript Guide</td>
                <td className="py-3 px-4">
                  <span className="px-2 py-1 text-xs rounded-md bg-cyan-500/10 text-cyan-600 dark:text-cyan-400">
                    Complete
                  </span>
                </td>
                <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">203</td>
                <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">2024-01-20</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-3">
          Features: Hover row highlight, status badges, responsive overflow
        </p>
      </div>
    </div>
  );
};
