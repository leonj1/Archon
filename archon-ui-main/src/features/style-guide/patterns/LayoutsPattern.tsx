import { useState } from 'react';
import { Card } from '@/features/ui/primitives/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/features/ui/primitives/select';
import { CodeDisplay } from '../shared/CodeDisplay';
import { cn } from '@/features/ui/primitives/styles';
import { BarChart, FileText, Users, Calendar, Grid, Table, Kanban } from 'lucide-react';

// Layout types that float over the grid
const LAYOUT_TYPES = [
  {
    name: 'Dashboard',
    description: 'Cards arranged in responsive grid layout',
    component: 'DashboardLayout'
  },
  {
    name: 'Kanban Board',
    description: 'Draggable columns with task cards',
    component: 'KanbanLayout'
  },
  {
    name: 'Data Table',
    description: 'Structured data with sorting and actions',
    component: 'TableLayout'
  },
  {
    name: 'Card Grid',
    description: 'Uniform cards in responsive grid',
    component: 'CardGridLayout'
  }
];

export const LayoutsPattern = () => {
  const [selectedLayout, setSelectedLayout] = useState('Dashboard');

  const generateCode = () => {
    switch (selectedLayout) {
      case 'Dashboard':
        return `// Dashboard Layout - Cards over grid
<div className="p-6 space-y-6">
  {/* Stats Row */}
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    {statsCards.map((card) => (
      <Card key={card.id} className="p-4">
        <h3 className="text-sm text-gray-600">{card.title}</h3>
        <p className="text-2xl font-bold">{card.value}</p>
      </Card>
    ))}
  </div>

  {/* Content Grid */}
  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <Card className="lg:col-span-2 p-6">
      {/* Main content */}
    </Card>
    <Card className="p-6">
      {/* Sidebar content */}
    </Card>
  </div>
</div>`;

      case 'Kanban Board':
        return `// Kanban Layout - Columns over grid
<div className="p-6 overflow-x-auto">
  <div className="flex gap-4 min-w-max">
    {columns.map((column) => (
      <Card key={column.id} className="w-72 p-4">
        <h3 className="font-semibold mb-4">{column.title}</h3>
        <div className="space-y-3">
          {column.tasks.map((task) => (
            <Card key={task.id} className="p-3 cursor-pointer hover:shadow-lg">
              <h4 className="font-medium text-sm">{task.title}</h4>
              <p className="text-xs text-gray-500 mt-1">{task.description}</p>
            </Card>
          ))}
        </div>
      </Card>
    ))}
  </div>
</div>`;

      case 'Data Table':
        return `// Table Layout - Structured data over grid
<div className="p-6 space-y-4">
  <div className="flex justify-between items-center">
    <h1 className="text-2xl font-bold">Data Table</h1>
    <Button>Add Item</Button>
  </div>

  <Card className="overflow-hidden">
    <table className="w-full">
      <thead className="bg-gray-50 dark:bg-gray-800/50">
        <tr>
          {columns.map((column) => (
            <th key={column.key} className="px-4 py-3 text-left text-xs font-medium">
              {column.label}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row) => (
          <tr key={row.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
            {columns.map((column) => (
              <td key={column.key} className="px-4 py-3 text-sm">
                {row[column.key]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </Card>
</div>`;

      case 'Card Grid':
        return `// Card Grid Layout - Uniform cards over grid
<div className="p-6 space-y-6">
  <div className="flex justify-between items-center">
    <h1 className="text-2xl font-bold">Card Grid</h1>
    <Button>Add Card</Button>
  </div>

  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
    {cards.map((card) => (
      <Card key={card.id} className="p-4 hover:shadow-lg transition-shadow">
        <h3 className="font-semibold mb-2">{card.title}</h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
          {card.description}
        </p>
        <div className="flex justify-between items-center">
          <span className="text-xs text-gray-500">{card.meta}</span>
          <Button size="sm" variant="outline">Action</Button>
        </div>
      </Card>
    ))}
  </div>
</div>`;

      default:
        return '';
    }
  };

  const renderLayoutDemo = () => {
    switch (selectedLayout) {
      case 'Dashboard':
        return (
          <div className="space-y-4">
            {/* Stats Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
              {[
                { title: 'Projects', value: '12', icon: <FileText className="w-4 h-4" /> },
                { title: 'Tasks', value: '38', icon: <BarChart className="w-4 h-4" /> },
                { title: 'Team', value: '8', icon: <Users className="w-4 h-4" /> },
                { title: 'Events', value: '24', icon: <Calendar className="w-4 h-4" /> }
              ].map((stat, i) => (
                <Card key={i} className="p-3 text-center">
                  <div className="flex items-center justify-center mb-2 text-cyan-500">
                    {stat.icon}
                  </div>
                  <p className="text-lg font-bold">{stat.value}</p>
                  <p className="text-xs text-gray-500">{stat.title}</p>
                </Card>
              ))}
            </div>
            {/* Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <Card className="lg:col-span-2 p-4">
                <h3 className="font-semibold mb-3">Main Content</h3>
                <div className="space-y-2">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="h-8 bg-gray-100 dark:bg-gray-800 rounded"></div>
                  ))}
                </div>
              </Card>
              <Card className="p-4">
                <h3 className="font-semibold mb-3">Sidebar</h3>
                <div className="space-y-2">
                  {[1, 2].map(i => (
                    <div key={i} className="h-6 bg-gray-100 dark:bg-gray-800 rounded"></div>
                  ))}
                </div>
              </Card>
            </div>
          </div>
        );

      case 'Kanban Board':
        return (
          <div className="flex gap-4 overflow-x-auto pb-4">
            {['To Do', 'In Progress', 'Done'].map((column, i) => (
              <Card key={column} className="w-48 p-4 flex-shrink-0">
                <h3 className="font-semibold mb-3 text-sm">{column}</h3>
                <div className="space-y-2">
                  {[1, 2].map(j => (
                    <Card key={j} className="p-2 cursor-pointer hover:shadow-md">
                      <p className="text-xs font-medium">Task {i + 1}.{j}</p>
                      <p className="text-xs text-gray-500 mt-1">Description</p>
                    </Card>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        );

      case 'Data Table':
        return (
          <Card className="overflow-hidden">
            <table className="w-full text-xs">
              <thead className="bg-gray-50 dark:bg-gray-800/50">
                <tr>
                  {['Name', 'Status', 'Priority', 'Progress'].map(header => (
                    <th key={header} className="px-3 py-2 text-left font-medium">
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {[
                  { name: 'Project A', status: 'Active', priority: 'High', progress: '75%' },
                  { name: 'Project B', status: 'Pending', priority: 'Medium', progress: '25%' },
                  { name: 'Project C', status: 'Done', priority: 'Low', progress: '100%' }
                ].map((row, i) => (
                  <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td className="px-3 py-2 font-medium">{row.name}</td>
                    <td className="px-3 py-2">{row.status}</td>
                    <td className="px-3 py-2">{row.priority}</td>
                    <td className="px-3 py-2">{row.progress}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        );

      case 'Card Grid':
        return (
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <Card key={i} className="p-3 hover:shadow-lg transition-shadow">
                <h3 className="font-semibold text-sm mb-2">Card {i}</h3>
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                  Description text for card item {i}
                </p>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-500">Meta info</span>
                  <button className="text-xs text-cyan-500 hover:text-cyan-600">Action</button>
                </div>
              </Card>
            ))}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Layout System</h2>
        <p className="text-gray-600 dark:text-gray-400 text-lg">
          Floating layout patterns over grid backgrounds
        </p>
      </div>

      {/* Layout Explorer - Above the Fold */}
      <Card className="p-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: Layout Selector */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Layout Type</label>
              <Select value={selectedLayout} onValueChange={setSelectedLayout}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {LAYOUT_TYPES.map((layout) => (
                    <SelectItem key={layout.name} value={layout.name}>
                      {layout.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Current Layout Info */}
            <div className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
              <h4 className="font-medium text-gray-900 dark:text-white text-sm">
                {selectedLayout}
              </h4>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                {LAYOUT_TYPES.find(l => l.name === selectedLayout)?.description}
              </p>
            </div>

            {/* Layout Options */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white">Available Layouts</h4>
              {LAYOUT_TYPES.map((layout) => (
                <div
                  key={layout.name}
                  className={cn(
                    "p-2 rounded cursor-pointer transition-colors flex items-center gap-2",
                    selectedLayout === layout.name
                      ? "bg-cyan-500/20 border border-cyan-500"
                      : "hover:bg-gray-100 dark:hover:bg-gray-800"
                  )}
                  onClick={() => setSelectedLayout(layout.name)}
                >
                  {layout.name === 'Dashboard' && <Grid className="w-4 h-4" />}
                  {layout.name === 'Kanban Board' && <Kanban className="w-4 h-4" />}
                  {layout.name === 'Data Table' && <Table className="w-4 h-4" />}
                  {layout.name === 'Card Grid' && <BarChart className="w-4 h-4" />}
                  <span className="text-sm">{layout.name}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Center & Right: Grid Background with Floating Layout */}
          <div className="lg:col-span-2">
            {/* Grid Background with Floating Elements */}
            <div
              className="relative min-h-80 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
              style={{
                backgroundImage: `
                  linear-gradient(rgba(156, 163, 175, 0.1) 1px, transparent 1px),
                  linear-gradient(90deg, rgba(156, 163, 175, 0.1) 1px, transparent 1px)
                `,
                backgroundSize: '20px 20px'
              }}
            >
              {/* Layout Content Floating Over Grid */}
              <div className="absolute inset-4">
                {renderLayoutDemo()}
              </div>
            </div>
          </div>
        </div>

        {/* Generated Code */}
        <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Generated Code</h4>
          <CodeDisplay
            code={generateCode()}
            showLineNumbers={false}
          />
        </div>
      </Card>
    </div>
  );
};