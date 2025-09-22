import React, { useState } from 'react';
import { Card } from '@/features/ui/primitives/card';
import type { GlowColor } from '../types';
import { Button } from '@/features/ui/primitives/button';
import { CodeDisplay } from '../shared/CodeDisplay';
import { LivePreview } from '../shared/LivePreview';
import { cn, glassmorphism } from '@/features/ui/primitives/styles';
import {
  Home,
  Settings,
  User,
  FileText,
  BarChart,
  Plus,
  Search,
  Bell,
  MoreVertical,
  Calendar,
} from 'lucide-react';

interface ExampleComposition {
  id: string;
  name: string;
  description: string;
  usage: string;
  component: React.ComponentType;
}

// Complete Dashboard Composition
const DashboardComposition = () => {
  return (
    <div className="h-96 bg-gray-50 dark:bg-gray-900 overflow-hidden rounded-lg">
      {/* Top Navigation */}
      <Card className="p-4 rounded-none border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-purple-500 rounded-lg" />
            <span className="font-bold text-lg">Archon</span>
          </div>
          <nav className="hidden md:flex items-center gap-1">
            {['Dashboard', 'Projects', 'Team', 'Analytics'].map((item, index) => (
              <button
                key={item}
                className={cn(
                  "px-3 py-1 rounded-lg text-sm font-medium transition-all duration-200",
                  index === 0
                    ? cn(glassmorphism.background.cyan, "text-cyan-700 dark:text-cyan-300")
                    : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
                )}
              >
                {item}
              </button>
            ))}
          </nav>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm"><Search className="w-4 h-4" /></Button>
            <Button variant="ghost" size="sm"><Bell className="w-4 h-4" /></Button>
            <Button variant="ghost" size="sm"><User className="w-4 h-4" /></Button>
          </div>
        </div>
      </Card>

      <div className="flex h-full">
        {/* Sidebar */}
        <Card className="w-48 h-full rounded-none border-r">
          <div className="p-3">
            <nav className="space-y-1">
              {[
                { icon: <Home className="w-4 h-4" />, label: 'Dashboard', active: true },
                { icon: <FileText className="w-4 h-4" />, label: 'Projects' },
                { icon: <BarChart className="w-4 h-4" />, label: 'Analytics' },
                { icon: <Settings className="w-4 h-4" />, label: 'Settings' }
              ].map((item) => (
                <button
                  key={item.label}
                  className={cn(
                    "w-full flex items-center gap-2 px-2 py-1.5 rounded text-sm transition-all",
                    item.active
                      ? cn(glassmorphism.background.cyan, "text-cyan-700 dark:text-cyan-300")
                      : "hover:bg-gray-100 dark:hover:bg-gray-800"
                  )}
                >
                  {item.icon}
                  {item.label}
                </button>
              ))}
            </nav>
          </div>
        </Card>

        {/* Main Content */}
        <div className="flex-1 p-4 space-y-4">
          {/* Stats Grid */}
          <div className="grid grid-cols-3 gap-3">
            {[
              { label: 'Projects', value: '24', color: 'purple' },
              { label: 'Tasks', value: '156', color: 'blue' },
              { label: 'Team', value: '8', color: 'green' }
            ].map((stat) => (
              <Card key={stat.label} glowColor={stat.color as GlowColor} className="p-3 text-center">
                <p className="text-lg font-bold">{stat.value}</p>
                <p className="text-xs text-gray-600 dark:text-gray-400">{stat.label}</p>
              </Card>
            ))}
          </div>

          {/* Content Grid */}
          <div className="grid grid-cols-3 gap-3 flex-1">
            <Card className="col-span-2 p-3">
              <h3 className="font-medium text-sm mb-2">Recent Activity</h3>
              <div className="space-y-1">
                {['Project updated', 'Task completed', 'New member'].map((activity, i) => (
                  <div key={i} className="text-xs py-1 border-b border-gray-200 dark:border-gray-700 last:border-b-0">
                    {activity}
                  </div>
                ))}
              </div>
            </Card>
            <Card className="p-3">
              <h3 className="font-medium text-sm mb-2">Quick Actions</h3>
              <div className="space-y-1">
                <Button variant="outline" size="sm" className="w-full text-xs">Create</Button>
                <Button variant="outline" size="sm" className="w-full text-xs">Invite</Button>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

// Project Card Collection
const ProjectCardsComposition = () => {
  const projects = [
    { title: 'Alpha', status: 'Active', progress: 75, color: 'purple' },
    { title: 'Beta', status: 'Review', progress: 90, color: 'blue' },
    { title: 'Gamma', status: 'Planning', progress: 25, color: 'orange' }
  ];

  return (
    <div className="p-6 bg-gray-50 dark:bg-gray-900 rounded-lg">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold">Projects</h2>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-2" />
          New Project
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {projects.map((project) => (
          <Card
            key={project.title}
            glowColor={project.color as GlowColor}
            className="p-4 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start justify-between mb-3">
              <h3 className="font-semibold">Project {project.title}</h3>
              <Button variant="ghost" size="sm">
                <MoreVertical className="w-4 h-4" />
              </Button>
            </div>

            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
              Development project with team collaboration features.
            </p>

            <div className="mb-3">
              <div className="flex justify-between text-sm mb-1">
                <span>Progress</span>
                <span>{project.progress}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-cyan-500 h-2 rounded-full"
                  style={{ width: `${project.progress}%` }}
                />
              </div>
            </div>

            <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
              <span className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                Due: 2 weeks
              </span>
              <span className="flex items-center gap-1">
                <User className="w-3 h-3" />
                5 members
              </span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

// Modal with Form
const ModalFormComposition = () => {
  const [showModal, setShowModal] = useState(false);

  return (
    <div className="relative">
      <div className="p-6 text-center">
        <Button onClick={() => setShowModal(true)}>
          Show Modal Example
        </Button>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <Card size="lg" glowColor="purple" className="w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Create New Task</h2>
              <Button variant="ghost" size="sm" onClick={() => setShowModal(false)}>
                ×
              </Button>
            </div>

            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Task Title</label>
                <input
                  type="text"
                  className={cn(
                    "w-full px-3 py-2 rounded-md text-sm",
                    glassmorphism.background.subtle,
                    glassmorphism.border.default,
                    glassmorphism.border.focus
                  )}
                  placeholder="Enter task title"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Priority</label>
                <select
                  className={cn(
                    "w-full px-3 py-2 rounded-md text-sm",
                    glassmorphism.background.subtle,
                    glassmorphism.border.default,
                    glassmorphism.border.focus
                  )}
                >
                  <option>High</option>
                  <option>Medium</option>
                  <option>Low</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Description</label>
                <textarea
                  className={cn(
                    "w-full px-3 py-2 rounded-md text-sm h-20 resize-none",
                    glassmorphism.background.subtle,
                    glassmorphism.border.default,
                    glassmorphism.border.focus
                  )}
                  placeholder="Describe the task"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setShowModal(false)}
                >
                  Cancel
                </Button>
                <Button
                  className="flex-1"
                  onClick={() => setShowModal(false)}
                >
                  Create Task
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
};

const EXAMPLE_COMPOSITIONS: ExampleComposition[] = [
  {
    id: 'dashboard',
    name: 'Complete Dashboard',
    description: 'Full dashboard layout with navigation, sidebar, stats, and content areas',
    usage: 'Admin panels, application dashboards, overview pages',
    component: DashboardComposition
  },
  {
    id: 'cards',
    name: 'Project Cards Grid',
    description: 'Collection of project cards with consistent styling and interactions',
    usage: 'Project portfolios, product grids, content galleries',
    component: ProjectCardsComposition
  },
  {
    id: 'modal',
    name: 'Modal with Form',
    description: 'Interactive modal dialog with form inputs and glassmorphism styling',
    usage: 'Create/edit dialogs, settings panels, confirmation prompts',
    component: ModalFormComposition
  }
];

const generateCode = (compositionId: string) => {
  const codeExamples = {
    dashboard: `/**
 * 🤖 AI CONTEXT: Complete Dashboard Composition
 *
 * PURPOSE: Full-featured dashboard with navigation and content
 * WHEN TO USE: Admin interfaces, application dashboards, data overview
 * WHEN NOT TO USE: Simple pages, mobile-first designs, content-focused sites
 *
 * COMPOSITION ELEMENTS:
 * - Top navigation with branding and user actions
 * - Collapsible sidebar with navigation items
 * - Stats cards grid for key metrics
 * - Content areas with recent activity and quick actions
 *
 * RESPONSIVE STRATEGY:
 * - Desktop: Full layout with sidebar
 * - Tablet: Collapsible sidebar
 * - Mobile: Overlay navigation drawer
 */

import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';
import { glassmorphism } from '@/features/ui/primitives/styles';

export const DashboardLayout = () => {
  return (
    <div className="h-screen bg-gray-50 dark:bg-gray-900">
      {/* Top Navigation */}
      <Card className="p-4 rounded-none border-b">
        <div className="flex items-center justify-between">
          {/* Brand */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-purple-500 rounded-lg" />
            <span className="font-bold text-lg">Your App</span>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {/* Navigation items */}
          </nav>

          {/* User Actions */}
          <div className="flex items-center gap-2">
            {/* User action buttons */}
          </div>
        </div>
      </Card>

      <div className="flex h-full">
        {/* Sidebar */}
        <Card className="w-64 h-full rounded-none border-r">
          <nav className="p-4 space-y-1">
            {/* Navigation items */}
          </nav>
        </Card>

        {/* Main Content */}
        <div className="flex-1 p-6 space-y-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Stat cards */}
          </div>

          {/* Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Content sections */}
          </div>
        </div>
      </div>
    </div>
  );
};`,

    cards: `/**
 * 🤖 AI CONTEXT: Project Cards Grid Composition
 *
 * PURPOSE: Consistent card layout for project/product display
 * WHEN TO USE: Portfolios, galleries, collection views
 * WHEN NOT TO USE: List data, text-heavy content, simple navigation
 *
 * CARD ELEMENTS:
 * - Header with title and actions
 * - Progress indicators for status
 * - Metadata with icons and labels
 * - Consistent hover states and interactions
 *
 * GRID BEHAVIOR:
 * - Responsive: 1->2->3 columns
 * - Equal heights maintained
 * - Proper spacing and alignment
 */

import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';

export const ProjectCardsGrid = ({ projects }: { projects: any[] }) => {
  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Projects</h2>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          New Project
        </Button>
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((project) => (
          <Card
            key={project.id}
            glowColor={project.status}
            className="p-6 hover:shadow-lg transition-all duration-300"
          >
            {/* Card header */}
            <div className="flex items-start justify-between mb-4">
              <h3 className="font-semibold text-lg">{project.title}</h3>
              <Button variant="ghost" size="sm">
                <MoreVertical className="w-4 h-4" />
              </Button>
            </div>

            {/* Card content */}
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              {project.description}
            </p>

            {/* Progress */}
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-2">
                <span>Progress</span>
                <span>{project.progress}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-cyan-500 h-2 rounded-full transition-all"
                  style={{ width: \`\${project.progress}%\` }}
                />
              </div>
            </div>

            {/* Metadata */}
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>Due: {project.dueDate}</span>
              <span>{project.teamSize} members</span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};`,

    modal: `/**
 * 🤖 AI CONTEXT: Modal with Form Composition
 *
 * PURPOSE: Interactive dialog for data input and actions
 * WHEN TO USE: Create/edit workflows, settings, confirmations
 * WHEN NOT TO USE: Large forms, multi-step processes, navigation
 *
 * MODAL STRUCTURE:
 * - Backdrop with blur effect
 * - Card container with glassmorphism
 * - Form with consistent input styling
 * - Action buttons with clear hierarchy
 *
 * ACCESSIBILITY:
 * - Focus trap within modal
 * - Escape key to close
 * - Proper ARIA labels
 * - Keyboard navigation
 */

import { useState } from 'react';
import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';
import { glassmorphism, cn } from '@/features/ui/primitives/styles';

export const ModalForm = ({ isOpen, onClose, onSubmit }: {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <Card size="lg" glowColor="purple" className="w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold">Create New Item</h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            ×
          </Button>
        </div>

        {/* Form */}
        <form className="space-y-4" onSubmit={onSubmit}>
          <div>
            <label className="block text-sm font-medium mb-2">
              Title
            </label>
            <input
              type="text"
              className={cn(
                "w-full px-3 py-2 rounded-md text-sm",
                glassmorphism.background.subtle,
                glassmorphism.border.default,
                glassmorphism.border.focus,
                "transition-all duration-200"
              )}
              placeholder="Enter title"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Description
            </label>
            <textarea
              className={cn(
                "w-full px-3 py-2 rounded-md text-sm h-20 resize-none",
                glassmorphism.background.subtle,
                glassmorphism.border.default,
                glassmorphism.border.focus,
                "transition-all duration-200"
              )}
              placeholder="Enter description"
            />
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              className="flex-1"
              onClick={onClose}
            >
              Cancel
            </Button>
            <Button type="submit" className="flex-1">
              Create
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};`
  };

  return codeExamples[compositionId as keyof typeof codeExamples] || '';
};

export const CompositionsExample = () => {
  const [selectedComposition, setSelectedComposition] = useState<string>('dashboard');

  const currentComposition = EXAMPLE_COMPOSITIONS.find(c => c.id === selectedComposition);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-4">Complete Compositions</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Real-world examples combining multiple components into complete UI compositions.
        </p>
      </div>

      {/* Composition Selector */}
      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Select Composition</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {EXAMPLE_COMPOSITIONS.map((composition) => (
            <Card
              key={composition.id}
              className={cn(
                "p-4 cursor-pointer transition-all duration-200",
                selectedComposition === composition.id
                  ? "border-cyan-500 shadow-[0_0_10px_rgba(34,211,238,0.3)]"
                  : "hover:shadow-lg"
              )}
              onClick={() => setSelectedComposition(composition.id)}
            >
              <h4 className="font-medium mb-2">{composition.name}</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                {composition.description}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                <strong>Use for:</strong> {composition.usage}
              </p>
            </Card>
          ))}
        </div>
      </Card>

      {/* Live Preview */}
      {currentComposition && (
        <Card className="p-6 max-w-none">
          <h3 className="text-lg font-semibold mb-4">
            {currentComposition.name} - Live Preview
          </h3>
          <LivePreview minHeight="400px">
            <div className="w-full max-w-6xl">
              <currentComposition.component />
            </div>
          </LivePreview>
        </Card>
      )}

      {/* Generated Code */}
      {currentComposition && (
        <Card className="p-6 max-w-none">
          <h3 className="text-lg font-semibold mb-4">Implementation Code</h3>
          <CodeDisplay
            code={generateCode(selectedComposition)}
            
            showLineNumbers
          />
        </Card>
      )}
    </div>
  );
};