import { useState } from 'react';
import { Button } from '@/features/ui/primitives/button';
import { Switch } from '@/features/ui/primitives/switch';
import { Label } from '@/features/ui/primitives/label';
import { LivePreview } from '../shared/LivePreview';
import { CodeDisplay } from '../shared/CodeDisplay';
import { ConfigPanel } from '../shared/ConfigPanel';
import { Edit, Trash2, Eye, Code } from 'lucide-react';

interface TableConfig {
  glassMorphism: boolean;
  actions: boolean;
  headers: boolean;
  striped: boolean;
}

const sampleData = [
  { id: 1, name: 'John Doe', email: 'john@example.com', status: 'Active' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', status: 'Inactive' },
  { id: 3, name: 'Bob Johnson', email: 'bob@example.com', status: 'Active' },
];

export const TableConfigurator = () => {
  const [config, setConfig] = useState<TableConfig>({
    glassMorphism: true,
    actions: true,
    headers: true,
    striped: true
  });
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');

  const generateCode = (_config: TableConfig) => {
    const imports = `import { Button } from '@/features/ui/primitives/button';
import { Edit, Trash2, Eye } from 'lucide-react';`;

    const aiContext = `/**
 * 🤖 AI CONTEXT: Glass Morphism Table
 *
 * PURPOSE: Data display with glass morphism styling and interactive elements
 * WHEN TO USE: Data grids, lists with actions, dashboard tables
 * WHEN NOT TO USE: Simple lists (use basic ul/li), massive datasets (use virtualization)
 */`;

    return `${imports}\n\n${aiContext}\n\n// Table component code here...`;
  };

  return (
    <div className="grid grid-cols-4 gap-6 h-full">
      {/* LEFT: Configuration Panel (1/4 width) */}
      <div className="col-span-1">
        <ConfigPanel title="Table Configuration">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label htmlFor="glass-morphism" className="text-sm">Glass Morphism</Label>
              <Switch
                id="glass-morphism"
                checked={config.glassMorphism}
                onCheckedChange={(glassMorphism) => setConfig({...config, glassMorphism})}
              />
            </div>

            <div className="flex items-center justify-between">
              <Label htmlFor="show-actions" className="text-sm">Show Actions</Label>
              <Switch
                id="show-actions"
                checked={config.actions}
                onCheckedChange={(actions) => setConfig({...config, actions})}
              />
            </div>

            <div className="flex items-center justify-between">
              <Label htmlFor="show-headers" className="text-sm">Show Headers</Label>
              <Switch
                id="show-headers"
                checked={config.headers}
                onCheckedChange={(headers) => setConfig({...config, headers})}
              />
            </div>

            <div className="flex items-center justify-between">
              <Label htmlFor="striped-rows" className="text-sm">Striped Rows</Label>
              <Switch
                id="striped-rows"
                checked={config.striped}
                onCheckedChange={(striped) => setConfig({...config, striped})}
              />
            </div>
          </div>

          {/* Preview/Code Tabs INSIDE configurator */}
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex gap-2">
              <Button
                size="sm"
                variant={activeTab === 'preview' ? 'default' : 'outline'}
                onClick={() => setActiveTab('preview')}
                className="flex items-center gap-2"
              >
                <Eye className="w-4 h-4" />
                Preview
              </Button>
              <Button
                size="sm"
                variant={activeTab === 'code' ? 'default' : 'outline'}
                onClick={() => setActiveTab('code')}
                className="flex items-center gap-2"
              >
                <Code className="w-4 h-4" />
                Code
              </Button>
            </div>
          </div>
        </ConfigPanel>
      </div>

      {/* RIGHT: Preview or Code Content (3/4 width) */}
      <div className="col-span-3">
        {activeTab === 'preview' ? (
          <LivePreview>
            <div className={`w-full ${config.glassMorphism
              ? 'backdrop-blur-md bg-white/80 dark:bg-black/30 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden shadow-lg'
              : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden'
            }`}>
              <table className="w-full">
                {config.headers && (
                  <thead className="bg-gray-50/80 dark:bg-gray-800/80 border-b border-gray-200 dark:border-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Email
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Status
                      </th>
                      {config.actions && (
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          Actions
                        </th>
                      )}
                    </tr>
                  </thead>
                )}
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {sampleData.map((item, index) => (
                    <tr
                      key={item.id}
                      className={`${config.striped && index % 2 === 1 ? 'bg-gray-50/50 dark:bg-gray-800/50' : ''} hover:bg-gray-50/70 dark:hover:bg-gray-800/70 transition-colors`}
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                        {item.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {item.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          item.status === 'Active'
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                            : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                        }`}>
                          {item.status}
                        </span>
                      </td>
                      {config.actions && (
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex justify-end gap-2">
                            <Button size="icon" variant="ghost">
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button size="icon" variant="ghost">
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button size="icon" variant="ghost">
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </LivePreview>
        ) : (
          <CodeDisplay
            code={generateCode(config)}
            showLineNumbers
          />
        )}
      </div>
    </div>
  );
};