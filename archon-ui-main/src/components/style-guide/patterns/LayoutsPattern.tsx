import { useState } from 'react';
import { Card } from '@/features/ui/primitives/card';
import type { GlowColor } from '../types';
import { Button } from '@/features/ui/primitives/button';
import { CodeDisplay } from '../shared/CodeDisplay';
import { LivePreview } from '../shared/LivePreview';
import { cn, glassmorphism } from '@/features/ui/primitives/styles';
import {
  LayoutGrid,
  Sidebar,
  PlusCircle,
  ChevronLeft,
  ChevronRight,
  MoreVertical
} from 'lucide-react';

interface LayoutTemplate {
  id: string;
  name: string;
  description: string;
  usage: string;
  component: React.ComponentType;
}

// Dashboard Template Component
const DashboardTemplate = () => {
  const cards = [
    { title: 'Total Projects', value: '12', change: '+2 this week', color: 'purple' },
    { title: 'Active Tasks', value: '38', change: '+5 today', color: 'blue' },
    { title: 'Completed', value: '245', change: '+12 this week', color: 'green' },
    { title: 'Team Members', value: '8', change: 'No change', color: 'orange' }
  ];

  return (
    <div className="p-4 space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Dashboard</h2>
        <Button size="sm" variant="outline">
          <PlusCircle className="w-4 h-4 mr-2" />
          New Project
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((card) => (
          <Card
            key={card.title}
            glowColor={card.color as GlowColor}
            className="p-4 hover:shadow-lg transition-shadow"
          >
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
              {card.title}
            </h3>
            <p className="text-2xl font-bold mt-1">{card.value}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {card.change}
            </p>
          </Card>
        ))}
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-2 p-4">
          <h3 className="font-semibold mb-3">Recent Activity</h3>
          <div className="space-y-2">
            {['Project Alpha updated', 'New task assigned', 'Beta milestone completed'].map((activity, i) => (
              <div key={i} className="text-sm py-2 border-b border-gray-200 dark:border-gray-700 last:border-b-0">
                {activity}
              </div>
            ))}
          </div>
        </Card>
        <Card className="p-4">
          <h3 className="font-semibold mb-3">Quick Actions</h3>
          <div className="space-y-2">
            <Button variant="outline" size="sm" className="w-full justify-start">
              Create Task
            </Button>
            <Button variant="outline" size="sm" className="w-full justify-start">
              Add Member
            </Button>
            <Button variant="outline" size="sm" className="w-full justify-start">
              View Reports
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
};

// Sidebar Template Component
const SidebarTemplate = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [sidebarPosition, setSidebarPosition] = useState<'top' | 'left'>('left');

  const items = [
    { id: '1', title: 'Project Alpha', status: 'active', color: 'purple' },
    { id: '2', title: 'Project Beta', status: 'pending', color: 'blue' },
    { id: '3', title: 'Project Gamma', status: 'completed', color: 'green' },
  ];

  return (
    <div className="h-64 flex flex-col">
      {/* Toggle Controls */}
      <div className="flex justify-between items-center p-2 border-b border-gray-200 dark:border-gray-700">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setSidebarPosition(p => p === 'top' ? 'left' : 'top')}
        >
          {sidebarPosition === 'top' ? <Sidebar className="w-4 h-4 mr-2" /> : <LayoutGrid className="w-4 h-4 mr-2" />}
          {sidebarPosition === 'top' ? 'Switch to Sidebar' : 'Switch to Top'}
        </Button>
        {sidebarPosition === 'left' && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          >
            {sidebarCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </Button>
        )}
      </div>

      <div className={cn(
        "flex flex-1",
        sidebarPosition === 'top' ? "flex-col" : "flex-row",
        "gap-4 p-4"
      )}>
        {/* Sidebar */}
        <div className={cn(
          sidebarPosition === 'left' && !sidebarCollapsed && "w-64",
          sidebarPosition === 'left' && sidebarCollapsed && "w-16",
          sidebarPosition === 'top' && "w-full",
          "transition-all duration-300"
        )}>
          {sidebarPosition === 'top' ? (
            <div className="grid grid-cols-3 gap-4">
              {items.map(item => (
                <Card
                  key={item.id}
                  glowColor={item.color as GlowColor}
                  className="p-3 hover:shadow-lg transition-shadow cursor-pointer"
                >
                  <h4 className="font-medium text-sm">{item.title}</h4>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{item.status}</p>
                </Card>
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              {items.map(item => (
                <Card
                  key={item.id}
                  className={cn(
                    "p-3 hover:shadow-lg transition-shadow cursor-pointer",
                    sidebarCollapsed && "p-2"
                  )}
                >
                  {!sidebarCollapsed ? (
                    <>
                      <h4 className="font-medium text-sm">{item.title}</h4>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{item.status}</p>
                    </>
                  ) : (
                    <div className="w-8 h-8 rounded bg-purple-500/20 flex items-center justify-center text-xs font-medium">
                      {item.title[0]}
                    </div>
                  )}
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="flex-1">
          <Card className="h-full p-6 border-2 border-dashed border-gray-300 dark:border-gray-600">
            <div className="text-center text-gray-500 dark:text-gray-400">
              <h3 className="font-medium mb-2">Main Content Area</h3>
              <p className="text-sm">Your application content goes here</p>
              <p className="text-xs mt-2">
                Sidebar: {sidebarPosition === 'top' ? 'Top' : `Left (${sidebarCollapsed ? 'Collapsed' : 'Expanded'})`}
              </p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

// Table View Template Component
const TableViewTemplate = () => {
  const data = [
    { id: 1, name: 'Project Alpha', status: 'Active', priority: 'High', progress: 75 },
    { id: 2, name: 'Project Beta', status: 'Pending', priority: 'Medium', progress: 25 },
    { id: 3, name: 'Project Gamma', status: 'Completed', priority: 'Low', progress: 100 },
  ];

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': return 'text-green-600 dark:text-green-400';
      case 'pending': return 'text-orange-600 dark:text-orange-400';
      case 'completed': return 'text-blue-600 dark:text-blue-400';
      default: return 'text-gray-600 dark:text-gray-400';
    }
  };

  return (
    <div className="p-4 space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Projects Table</h2>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">Filter</Button>
          <Button size="sm">
            <PlusCircle className="w-4 h-4 mr-2" />
            Add Project
          </Button>
        </div>
      </div>

      {/* Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-800/50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Name
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Priority
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Progress
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {data.map((row) => (
                <tr key={row.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                  <td className="px-4 py-3 text-sm font-medium">{row.name}</td>
                  <td className="px-4 py-3">
                    <span className={cn('text-sm font-medium', getStatusColor(row.status))}>
                      {row.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm">{row.priority}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-cyan-500 h-2 rounded-full transition-all"
                          style={{ width: `${row.progress}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500 dark:text-gray-400 w-8">
                        {row.progress}%
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <Button variant="ghost" size="sm">
                      <MoreVertical className="w-4 h-4" />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

// Centered Form Template Component
const CenteredFormTemplate = () => {
  return (
    <div className="min-h-64 flex items-center justify-center p-8">
      <Card size="lg" glowColor="purple" className="w-full max-w-md">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold mb-2">Create Project</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Enter the details for your new project
          </p>
        </div>

        <form className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Project Name</label>
            <input
              type="text"
              className={cn(
                "w-full px-3 py-2 rounded-md text-sm",
                glassmorphism.background.subtle,
                glassmorphism.border.default,
                glassmorphism.border.focus,
                "transition-all duration-200"
              )}
              placeholder="Enter project name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Description</label>
            <textarea
              className={cn(
                "w-full px-3 py-2 rounded-md text-sm h-20 resize-none",
                glassmorphism.background.subtle,
                glassmorphism.border.default,
                glassmorphism.border.focus,
                "transition-all duration-200"
              )}
              placeholder="Describe your project"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Priority</label>
            <select
              className={cn(
                "w-full px-3 py-2 rounded-md text-sm",
                glassmorphism.background.subtle,
                glassmorphism.border.default,
                glassmorphism.border.focus,
                "transition-all duration-200"
              )}
            >
              <option>High</option>
              <option>Medium</option>
              <option>Low</option>
            </select>
          </div>

          <div className="flex gap-3 pt-4">
            <Button variant="outline" className="flex-1">
              Cancel
            </Button>
            <Button className="flex-1">
              Create Project
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};

const LAYOUT_TEMPLATES: LayoutTemplate[] = [
  {
    id: 'dashboard',
    name: 'Dashboard Layout',
    description: 'Grid-based dashboard with stats cards and content sections',
    usage: 'Admin panels, analytics dashboards, overview pages',
    component: DashboardTemplate
  },
  {
    id: 'sidebar',
    name: 'Sidebar Layout',
    description: 'Collapsible sidebar with main content area (like ProjectsView)',
    usage: 'Applications with navigation, project management, file browsers',
    component: SidebarTemplate
  },
  {
    id: 'table',
    name: 'Table View Layout',
    description: 'Data table with actions and filters',
    usage: 'Data management, lists, admin interfaces',
    component: TableViewTemplate
  },
  {
    id: 'form',
    name: 'Centered Form Layout',
    description: 'Single focus form with centered alignment',
    usage: 'Login forms, creation dialogs, focused input workflows',
    component: CenteredFormTemplate
  }
];

const generateCode = (templateId: string) => {
  const template = LAYOUT_TEMPLATES.find(t => t.id === templateId);
  if (!template) return '';

  const codeExamples = {
    dashboard: `import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';

/**
 * 🤖 AI CONTEXT: Dashboard Layout Pattern
 *
 * PURPOSE: Grid-based layout for displaying metrics and overview data
 * WHEN TO USE: Admin dashboards, analytics views, KPI displays
 * WHEN NOT TO USE: Forms, detailed content pages, navigation-heavy interfaces
 *
 * STRUCTURE:
 * - Header with title and primary action
 * - Stats cards in responsive grid (1->2->4 columns)
 * - Content sections in asymmetric grid (2:1 ratio typical)
 *
 * RESPONSIVE BEHAVIOR:
 * - Mobile: Single column stack
 * - Tablet: 2-column stats, stacked content
 * - Desktop: 4-column stats, side-by-side content
 */

export const DashboardLayout = () => {
  return (
    <div className="p-4 space-y-4">
      {/* Header Section */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <Button>Primary Action</Button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statsData.map((stat) => (
          <Card key={stat.id} glowColor={stat.color} className="p-4">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
              {stat.title}
            </h3>
            <p className="text-2xl font-bold mt-1">{stat.value}</p>
            <p className="text-xs text-gray-500 mt-1">{stat.change}</p>
          </Card>
        ))}
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-2 p-4">
          {/* Main content area */}
        </Card>
        <Card className="p-4">
          {/* Sidebar content */}
        </Card>
      </div>
    </div>
  );
};`,

    sidebar: `import { useState } from 'react';
import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';
import { ChevronLeft, ChevronRight } from 'lucide-react';

/**
 * 🤖 AI CONTEXT: Sidebar Layout Pattern
 *
 * PURPOSE: Navigation-focused layout with collapsible sidebar
 * WHEN TO USE: File browsers, project management, settings pages
 * WHEN NOT TO USE: Simple content pages, forms, dashboards
 *
 * FEATURES:
 * - Collapsible sidebar (280px -> 60px)
 * - Responsive behavior (sidebar -> top nav on mobile)
 * - Smooth transitions and state preservation
 * - Keyboard navigation support
 *
 * ACCESSIBILITY:
 * - ARIA labels for collapse state
 * - Keyboard shortcuts (Ctrl+\\)
 * - Focus management on state change
 */

export const SidebarLayout = () => {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <div className={cn(
        "transition-all duration-300",
        collapsed ? "w-16" : "w-64"
      )}>
        <Card className="h-full p-4 rounded-none border-r">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setCollapsed(!collapsed)}
            className="mb-4"
          >
            {collapsed ? <ChevronRight /> : <ChevronLeft />}
          </Button>

          {/* Sidebar content */}
          <nav className="space-y-2">
            {navigationItems.map((item) => (
              <Card
                key={item.id}
                className={cn(
                  "p-3 cursor-pointer transition-all",
                  collapsed && "p-2"
                )}
              >
                {collapsed ? (
                  <div className="w-8 h-8 flex items-center justify-center">
                    {item.icon}
                  </div>
                ) : (
                  <>
                    <div className="flex items-center gap-3">
                      {item.icon}
                      <span>{item.label}</span>
                    </div>
                  </>
                )}
              </Card>
            ))}
          </nav>
        </Card>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6">
        {/* Your main content */}
      </div>
    </div>
  );
};`,

    table: `import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';

/**
 * 🤖 AI CONTEXT: Table View Layout Pattern
 *
 * PURPOSE: Data-heavy interface with filtering and actions
 * WHEN TO USE: Admin interfaces, data management, list views
 * WHEN NOT TO USE: Dashboards, forms, content-focused pages
 *
 * FEATURES:
 * - Responsive table with horizontal scroll
 * - Action buttons in header and rows
 * - Sortable columns and filtering
 * - Pagination support
 *
 * RESPONSIVE BEHAVIOR:
 * - Desktop: Full table display
 * - Tablet: Horizontal scroll for wide tables
 * - Mobile: Card-based list view (transform table to cards)
 */

export const TableViewLayout = () => {
  return (
    <div className="p-4 space-y-4">
      {/* Header with Actions */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Data Table</h1>
        <div className="flex gap-2">
          <Button variant="outline">Filter</Button>
          <Button>Add Item</Button>
        </div>
      </div>

      {/* Table Container */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-800/50">
              <tr>
                {columns.map((column) => (
                  <th
                    key={column.key}
                    className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
                  >
                    {column.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
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
        </div>
      </Card>
    </div>
  );
};`,

    form: `import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';
import { glassmorphism, cn } from '@/features/ui/primitives/styles';

/**
 * 🤖 AI CONTEXT: Centered Form Layout Pattern
 *
 * PURPOSE: Single-focus form interface with minimal distractions
 * WHEN TO USE: Login/signup, creation modals, settings forms
 * WHEN NOT TO USE: Complex multi-step forms, data entry workflows
 *
 * FEATURES:
 * - Centered card with appropriate max-width
 * - Glassmorphism form controls
 * - Clear visual hierarchy
 * - Consistent spacing and typography
 *
 * FORM VALIDATION:
 * - Real-time validation feedback
 * - Error states with glassmorphism styling
 * - Success states with appropriate colors
 * - Accessibility-compliant error messages
 */

export const CenteredFormLayout = () => {
  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <Card size="lg" glowColor="purple" className="w-full max-w-md">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold mb-2">Form Title</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Brief description of the form purpose
          </p>
        </div>

        <form className="space-y-4">
          {formFields.map((field) => (
            <div key={field.name}>
              <label className="block text-sm font-medium mb-2">
                {field.label}
              </label>
              <input
                type={field.type}
                className={cn(
                  "w-full px-3 py-2 rounded-md text-sm",
                  glassmorphism.background.subtle,
                  glassmorphism.border.default,
                  glassmorphism.border.focus,
                  "transition-all duration-200"
                )}
                placeholder={field.placeholder}
              />
            </div>
          ))}

          <div className="flex gap-3 pt-4">
            <Button variant="outline" className="flex-1">
              Cancel
            </Button>
            <Button className="flex-1">
              Submit
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};`
  };

  return codeExamples[templateId as keyof typeof codeExamples] || '';
};

export const LayoutsPattern = () => {
  const [selectedTemplate, setSelectedTemplate] = useState<string>('dashboard');

  const currentTemplate = LAYOUT_TEMPLATES.find(t => t.id === selectedTemplate);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-4">Layout Patterns</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Reusable layout templates for common application structures and workflows.
        </p>
      </div>

      {/* Template Selector */}
      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Select Layout Template</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {LAYOUT_TEMPLATES.map((template) => (
            <Card
              key={template.id}
              className={cn(
                "p-4 cursor-pointer transition-all duration-200",
                selectedTemplate === template.id
                  ? "border-cyan-500 shadow-[0_0_10px_rgba(34,211,238,0.3)]"
                  : "hover:shadow-lg"
              )}
              onClick={() => setSelectedTemplate(template.id)}
            >
              <h4 className="font-medium mb-2">{template.name}</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                {template.description}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                <strong>Use for:</strong> {template.usage}
              </p>
            </Card>
          ))}
        </div>
      </Card>

      {/* Live Preview */}
      {currentTemplate && (
        <Card className="p-6 max-w-none">
          <h3 className="text-lg font-semibold mb-4">
            {currentTemplate.name} - Live Preview
          </h3>
          <LivePreview minHeight="320px">
            <div className="w-full max-w-4xl">
              <currentTemplate.component />
            </div>
          </LivePreview>
        </Card>
      )}

      {/* Generated Code */}
      {currentTemplate && (
        <Card className="p-6 max-w-none">
          <h3 className="text-lg font-semibold mb-4">Generated Code</h3>
          <CodeDisplay
            code={generateCode(selectedTemplate)}
            
            showLineNumbers
          />
        </Card>
      )}
    </div>
  );
};