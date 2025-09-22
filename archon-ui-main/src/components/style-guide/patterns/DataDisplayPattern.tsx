import { useState } from 'react';
import { Card } from '@/features/ui/primitives/card';
import type { GlowColor } from '../types';
import { Button } from '@/features/ui/primitives/button';
import { CodeDisplay } from '../shared/CodeDisplay';
import { cn } from '@/features/ui/primitives/styles';
import {
  MoreVertical,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Edit,
  Calendar,
  Clock,
  User,
  Tag,
  Star,
  TrendingUp,
  Activity
} from 'lucide-react';

interface DataDisplayPattern {
  id: string;
  name: string;
  description: string;
  usage: string;
  component: React.ComponentType;
}

// Table Data Display Demo
const TableDisplayDemo = () => {
  const [sortField, setSortField] = useState<string>('name');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const data = [
    {
      id: 1,
      name: 'Project Alpha',
      status: 'Active',
      priority: 'High',
      progress: 75,
      assignee: 'John Doe',
      dueDate: '2024-02-15',
      tasks: 24
    },
    {
      id: 2,
      name: 'Project Beta',
      status: 'Pending',
      priority: 'Medium',
      progress: 25,
      assignee: 'Jane Smith',
      dueDate: '2024-03-01',
      tasks: 18
    },
    {
      id: 3,
      name: 'Project Gamma',
      status: 'Completed',
      priority: 'Low',
      progress: 100,
      assignee: 'Bob Wilson',
      dueDate: '2024-01-30',
      tasks: 32
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': return 'text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/30';
      case 'pending': return 'text-orange-600 dark:text-orange-400 bg-orange-100 dark:bg-orange-900/30';
      case 'completed': return 'text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/30';
      default: return 'text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-900/30';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'text-red-600 dark:text-red-400';
      case 'medium': return 'text-yellow-600 dark:text-yellow-400';
      case 'low': return 'text-green-600 dark:text-green-400';
      default: return 'text-gray-600 dark:text-gray-400';
    }
  };

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  return (
    <Card className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 dark:bg-gray-800/50">
            <tr>
              <th className="px-4 py-3 text-left">
                <button
                  onClick={() => handleSort('name')}
                  className="flex items-center gap-2 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase hover:text-gray-700 dark:hover:text-gray-300"
                >
                  Project Name
                  {sortField === 'name' && (
                    sortDirection === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />
                  )}
                </button>
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
                Assignee
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                Due Date
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {data.map((row) => (
              <tr key={row.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <td className="px-4 py-3">
                  <div className="font-medium text-sm">{row.name}</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">{row.tasks} tasks</div>
                </td>
                <td className="px-4 py-3">
                  <span className={cn(
                    'inline-flex px-2 py-1 text-xs font-medium rounded-full',
                    getStatusColor(row.status)
                  )}>
                    {row.status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={cn('text-sm font-medium', getPriorityColor(row.priority))}>
                    {row.priority}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2 max-w-[80px]">
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
                <td className="px-4 py-3 text-sm">{row.assignee}</td>
                <td className="px-4 py-3 text-sm">{row.dueDate}</td>
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
  );
};

// Card Grid Display Demo
const CardGridDemo = () => {
  const projects = [
    {
      id: 1,
      title: 'Project Alpha',
      description: 'Advanced analytics platform with real-time data processing capabilities.',
      status: 'Active',
      progress: 75,
      team: ['John Doe', 'Jane Smith', 'Bob Wilson'],
      tags: ['Analytics', 'React', 'Node.js'],
      lastUpdate: '2 hours ago',
      priority: 'High'
    },
    {
      id: 2,
      title: 'Project Beta',
      description: 'Mobile application for task management and team collaboration.',
      status: 'Pending',
      progress: 25,
      team: ['Alice Brown', 'Charlie Davis'],
      tags: ['Mobile', 'React Native', 'TypeScript'],
      lastUpdate: '1 day ago',
      priority: 'Medium'
    },
    {
      id: 3,
      title: 'Project Gamma',
      description: 'E-commerce platform with integrated payment processing.',
      status: 'Completed',
      progress: 100,
      team: ['Eva Martinez', 'Frank Wilson', 'Grace Lee', 'Henry Kim'],
      tags: ['E-commerce', 'Payment', 'Security'],
      lastUpdate: '3 days ago',
      priority: 'Low'
    }
  ];

  const getStatusGlow = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': return 'green';
      case 'pending': return 'orange';
      case 'completed': return 'blue';
      default: return 'purple';
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {projects.map((project) => (
        <Card
          key={project.id}
          glowColor={getStatusGlow(project.status) as GlowColor}
          className="p-6 hover:shadow-lg transition-all duration-300"
        >
          <div className="flex items-start justify-between mb-4">
            <h3 className="font-semibold text-lg">{project.title}</h3>
            <Button variant="ghost" size="sm">
              <MoreVertical className="w-4 h-4" />
            </Button>
          </div>

          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
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
                style={{ width: `${project.progress}%` }}
              />
            </div>
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-1 mb-4">
            {project.tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center px-2 py-1 text-xs font-medium bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-full"
              >
                <Tag className="w-3 h-3 mr-1" />
                {tag}
              </span>
            ))}
          </div>

          {/* Team & Meta */}
          <div className="space-y-2 text-xs text-gray-500 dark:text-gray-400">
            <div className="flex items-center gap-2">
              <User className="w-3 h-3" />
              <span>{project.team.length} team members</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-3 h-3" />
              <span>Updated {project.lastUpdate}</span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <Button variant="outline" size="sm" className="flex-1">
              <Edit className="w-4 h-4 mr-2" />
              Edit
            </Button>
            <Button variant="outline" size="sm" className="flex-1">
              <ExternalLink className="w-4 h-4 mr-2" />
              View
            </Button>
          </div>
        </Card>
      ))}
    </div>
  );
};

// List Display Demo
const ListDisplayDemo = () => {
  const [selectedItems, setSelectedItems] = useState<number[]>([]);

  const items = [
    {
      id: 1,
      title: 'Implement user authentication system',
      subtitle: 'Backend development required',
      meta: 'Due in 3 days',
      status: 'High Priority',
      avatar: '/api/placeholder/32/32',
      actions: ['edit', 'delete', 'assign']
    },
    {
      id: 2,
      title: 'Design new dashboard layout',
      subtitle: 'UI/UX improvements',
      meta: 'Due next week',
      status: 'Medium Priority',
      avatar: '/api/placeholder/32/32',
      actions: ['edit', 'delete', 'assign']
    },
    {
      id: 3,
      title: 'Optimize database queries',
      subtitle: 'Performance enhancement',
      meta: 'Due in 2 weeks',
      status: 'Low Priority',
      avatar: '/api/placeholder/32/32',
      actions: ['edit', 'delete', 'assign']
    },
    {
      id: 4,
      title: 'Write API documentation',
      subtitle: 'Documentation update',
      meta: 'Due in 1 week',
      status: 'Medium Priority',
      avatar: '/api/placeholder/32/32',
      actions: ['edit', 'delete', 'assign']
    }
  ];

  const toggleSelection = (id: number) => {
    setSelectedItems(prev =>
      prev.includes(id)
        ? prev.filter(item => item !== id)
        : [...prev, id]
    );
  };

  const getStatusColor = (status: string) => {
    if (status.includes('High')) return 'text-red-600 dark:text-red-400';
    if (status.includes('Medium')) return 'text-yellow-600 dark:text-yellow-400';
    if (status.includes('Low')) return 'text-green-600 dark:text-green-400';
    return 'text-gray-600 dark:text-gray-400';
  };

  return (
    <Card className="divide-y divide-gray-200 dark:divide-gray-700">
      {items.map((item) => (
        <div
          key={item.id}
          className={cn(
            "p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors",
            selectedItems.includes(item.id) && "bg-cyan-50 dark:bg-cyan-900/20"
          )}
        >
          <div className="flex items-center gap-4">
            {/* Selection Checkbox */}
            <input
              type="checkbox"
              checked={selectedItems.includes(item.id)}
              onChange={() => toggleSelection(item.id)}
              className="rounded border-gray-300 dark:border-gray-600"
            />

            {/* Avatar */}
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center text-white text-sm font-medium">
              {item.title[0]}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <h4 className="font-medium text-sm">{item.title}</h4>
                <span className={cn('text-xs font-medium', getStatusColor(item.status))}>
                  {item.status}
                </span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {item.subtitle}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {item.meta}
              </p>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-1">
              <Button variant="ghost" size="sm">
                <Edit className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm">
                <Star className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm">
                <MoreVertical className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      ))}

      {/* Bulk Actions */}
      {selectedItems.length > 0 && (
        <div className="p-4 bg-cyan-50 dark:bg-cyan-900/20 border-t border-cyan-200 dark:border-cyan-800">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">
              {selectedItems.length} item{selectedItems.length > 1 ? 's' : ''} selected
            </span>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                Bulk Edit
              </Button>
              <Button variant="outline" size="sm">
                Export
              </Button>
              <Button variant="destructive" size="sm">
                Delete
              </Button>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
};

// Stats Dashboard Demo
const StatsDisplayDemo = () => {
  const stats = [
    {
      label: 'Total Revenue',
      value: '$124,000',
      change: '+12.5%',
      trend: 'up',
      icon: <TrendingUp className="w-5 h-5" />,
      color: 'green'
    },
    {
      label: 'Active Users',
      value: '2,847',
      change: '+5.2%',
      trend: 'up',
      icon: <User className="w-5 h-5" />,
      color: 'blue'
    },
    {
      label: 'Conversion Rate',
      value: '3.24%',
      change: '-0.8%',
      trend: 'down',
      icon: <Activity className="w-5 h-5" />,
      color: 'orange'
    },
    {
      label: 'Support Tickets',
      value: '89',
      change: '-15.3%',
      trend: 'down',
      icon: <Calendar className="w-5 h-5" />,
      color: 'purple'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <Card
          key={stat.label}
          glowColor={stat.color as GlowColor}
          className="p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-center justify-between mb-4">
            <div className={cn(
              'p-2 rounded-lg',
              stat.color === 'green' && 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
              stat.color === 'blue' && 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
              stat.color === 'orange' && 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400',
              stat.color === 'purple' && 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400'
            )}>
              {stat.icon}
            </div>
            <span className={cn(
              'text-sm font-medium',
              stat.trend === 'up' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
            )}>
              {stat.change}
            </span>
          </div>

          <div>
            <p className="text-2xl font-bold mb-1">{stat.value}</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</p>
          </div>
        </Card>
      ))}
    </div>
  );
};

const DATA_DISPLAY_PATTERNS: DataDisplayPattern[] = [
  {
    id: 'table',
    name: 'Data Tables',
    description: 'Sortable and interactive data tables with actions',
    usage: 'Large datasets, admin interfaces, data management',
    component: TableDisplayDemo
  },
  {
    id: 'cards',
    name: 'Card Grids',
    description: 'Information displayed in card layout with actions',
    usage: 'Project portfolios, product catalogs, content galleries',
    component: CardGridDemo
  },
  {
    id: 'lists',
    name: 'List Views',
    description: 'Vertical list layout with selection and bulk actions',
    usage: 'Task lists, notifications, simple data display',
    component: ListDisplayDemo
  },
  {
    id: 'stats',
    name: 'Stats Display',
    description: 'Key metrics and KPI visualization cards',
    usage: 'Dashboards, analytics, performance monitoring',
    component: StatsDisplayDemo
  }
];

const generateCode = (patternId: string) => {
  const codeExamples = {
    table: `import { useState } from 'react';
import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';
import { ChevronUp, ChevronDown, MoreVertical } from 'lucide-react';

/**
 * 🤖 AI CONTEXT: Data Table Pattern
 *
 * PURPOSE: Display and interact with structured data in rows and columns
 * WHEN TO USE: Large datasets, admin interfaces, data management
 * WHEN NOT TO USE: Small datasets (use lists), visual content (use cards)
 *
 * FEATURES:
 * - Sortable columns with visual indicators
 * - Row hover states for interactivity
 * - Action buttons for row operations
 * - Progress bars for numeric data
 * - Status badges with semantic colors
 *
 * RESPONSIVE BEHAVIOR:
 * - Horizontal scroll on mobile
 * - Consider card view for narrow screens
 * - Sticky headers for long tables
 */

interface TableColumn {
  key: string;
  label: string;
  sortable?: boolean;
  render?: (value: any, row: any) => React.ReactNode;
}

interface DataTableProps {
  data: any[];
  columns: TableColumn[];
  onSort?: (field: string, direction: 'asc' | 'desc') => void;
  onRowAction?: (action: string, row: any) => void;
}

export const DataTable = ({ data, columns, onSort, onRowAction }: DataTableProps) => {
  const [sortField, setSortField] = useState<string>('');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const handleSort = (field: string) => {
    const newDirection = sortField === field && sortDirection === 'asc' ? 'desc' : 'asc';
    setSortField(field);
    setSortDirection(newDirection);
    onSort?.(field, newDirection);
  };

  return (
    <Card className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 dark:bg-gray-800/50">
            <tr>
              {columns.map((column) => (
                <th key={column.key} className="px-4 py-3 text-left">
                  {column.sortable ? (
                    <button
                      onClick={() => handleSort(column.key)}
                      className="flex items-center gap-2 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase hover:text-gray-700 dark:hover:text-gray-300"
                    >
                      {column.label}
                      {sortField === column.key && (
                        sortDirection === 'asc'
                          ? <ChevronUp className="w-3 h-3" />
                          : <ChevronDown className="w-3 h-3" />
                      )}
                    </button>
                  ) : (
                    <span className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                      {column.label}
                    </span>
                  )}
                </th>
              ))}
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {data.map((row) => (
              <tr key={row.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                {columns.map((column) => (
                  <td key={column.key} className="px-4 py-3 text-sm">
                    {column.render ? column.render(row[column.key], row) : row[column.key]}
                  </td>
                ))}
                <td className="px-4 py-3">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onRowAction?.('menu', row)}
                  >
                    <MoreVertical className="w-4 h-4" />
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};`,

    cards: `import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';
import { MoreVertical, Edit, ExternalLink, Tag, User, Clock } from 'lucide-react';

/**
 * 🤖 AI CONTEXT: Card Grid Pattern
 *
 * PURPOSE: Visual display of information in card format
 * WHEN TO USE: Projects, products, content with rich metadata
 * WHEN NOT TO USE: Simple lists, tabular data, text-heavy content
 *
 * CARD STRUCTURE:
 * - Header: Title and actions
 * - Body: Description and key information
 * - Metadata: Tags, stats, timestamps
 * - Footer: Actions and navigation
 *
 * RESPONSIVE BEHAVIOR:
 * - 1 column on mobile
 * - 2 columns on tablet
 * - 3+ columns on desktop
 * - Consistent card heights
 */

interface CardData {
  id: string;
  title: string;
  description: string;
  status: string;
  progress?: number;
  tags?: string[];
  meta?: Record<string, any>;
}

interface CardGridProps {
  items: CardData[];
  onCardAction?: (action: string, item: CardData) => void;
  getStatusGlow?: (status: string) => string;
}

export const CardGrid = ({ items, onCardAction, getStatusGlow }: CardGridProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {items.map((item) => (
        <Card
          key={item.id}
          glowColor={getStatusGlow?.(item.status) as GlowColor}
          className="p-6 hover:shadow-lg transition-all duration-300"
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <h3 className="font-semibold text-lg line-clamp-1">{item.title}</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onCardAction?.('menu', item)}
            >
              <MoreVertical className="w-4 h-4" />
            </Button>
          </div>

          {/* Description */}
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
            {item.description}
          </p>

          {/* Progress (if applicable) */}
          {item.progress !== undefined && (
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-2">
                <span>Progress</span>
                <span>{item.progress}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-cyan-500 h-2 rounded-full transition-all"
                  style={{ width: \`\${item.progress}%\` }}
                />
              </div>
            </div>
          )}

          {/* Tags */}
          {item.tags && (
            <div className="flex flex-wrap gap-1 mb-4">
              {item.tags.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center px-2 py-1 text-xs font-medium bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-full"
                >
                  <Tag className="w-3 h-3 mr-1" />
                  {tag}
                </span>
              ))}
            </div>
          )}

          {/* Metadata */}
          {item.meta && (
            <div className="space-y-2 text-xs text-gray-500 dark:text-gray-400 mb-4">
              {Object.entries(item.meta).map(([key, value]) => (
                <div key={key} className="flex items-center gap-2">
                  {key === 'team' && <User className="w-3 h-3" />}
                  {key === 'updated' && <Clock className="w-3 h-3" />}
                  <span>{value}</span>
                </div>
              ))}
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
            <Button
              variant="outline"
              size="sm"
              className="flex-1"
              onClick={() => onCardAction?.('edit', item)}
            >
              <Edit className="w-4 h-4 mr-2" />
              Edit
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="flex-1"
              onClick={() => onCardAction?.('view', item)}
            >
              <ExternalLink className="w-4 h-4 mr-2" />
              View
            </Button>
          </div>
        </Card>
      ))}
    </div>
  );
};`,

    lists: `import { useState } from 'react';
import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';
import { Edit, Star, MoreVertical } from 'lucide-react';
import { cn } from '@/features/ui/primitives/styles';

/**
 * 🤖 AI CONTEXT: List View Pattern
 *
 * PURPOSE: Linear display of items with actions and selection
 * WHEN TO USE: Tasks, notifications, simple data with actions
 * WHEN NOT TO USE: Complex data (use tables), visual content (use cards)
 *
 * FEATURES:
 * - Multi-selection with checkboxes
 * - Bulk actions for selected items
 * - Individual item actions
 * - Hover states and visual feedback
 *
 * ACCESSIBILITY:
 * - Keyboard navigation support
 * - Screen reader friendly
 * - Clear selection states
 * - Accessible action buttons
 */

interface ListItem {
  id: string;
  title: string;
  subtitle?: string;
  meta?: string;
  status?: string;
  avatar?: string;
}

interface ListViewProps {
  items: ListItem[];
  selectable?: boolean;
  onItemAction?: (action: string, item: ListItem) => void;
  onBulkAction?: (action: string, items: ListItem[]) => void;
  getStatusColor?: (status: string) => string;
}

export const ListView = ({
  items,
  selectable = true,
  onItemAction,
  onBulkAction,
  getStatusColor
}: ListViewProps) => {
  const [selectedItems, setSelectedItems] = useState<string[]>([]);

  const toggleSelection = (id: string) => {
    setSelectedItems(prev =>
      prev.includes(id)
        ? prev.filter(item => item !== id)
        : [...prev, id]
    );
  };

  const toggleAllSelection = () => {
    setSelectedItems(prev =>
      prev.length === items.length ? [] : items.map(item => item.id)
    );
  };

  const handleBulkAction = (action: string) => {
    const selectedObjects = items.filter(item => selectedItems.includes(item.id));
    onBulkAction?.(action, selectedObjects);
  };

  return (
    <Card className="divide-y divide-gray-200 dark:divide-gray-700">
      {/* Header with bulk selection */}
      {selectable && selectedItems.length > 0 && (
        <div className="p-4 bg-cyan-50 dark:bg-cyan-900/20 border-b border-cyan-200 dark:border-cyan-800">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">
              {selectedItems.length} item{selectedItems.length > 1 ? 's' : ''} selected
            </span>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleBulkAction('edit')}
              >
                Bulk Edit
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleBulkAction('export')}
              >
                Export
              </Button>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => handleBulkAction('delete')}
              >
                Delete
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* List Items */}
      {items.map((item) => (
        <div
          key={item.id}
          className={cn(
            "p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors",
            selectedItems.includes(item.id) && "bg-cyan-50 dark:bg-cyan-900/20"
          )}
        >
          <div className="flex items-center gap-4">
            {/* Selection Checkbox */}
            {selectable && (
              <input
                type="checkbox"
                checked={selectedItems.includes(item.id)}
                onChange={() => toggleSelection(item.id)}
                className="rounded border-gray-300 dark:border-gray-600"
              />
            )}

            {/* Avatar */}
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center text-white text-sm font-medium">
              {item.title[0]}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <h4 className="font-medium text-sm truncate">{item.title}</h4>
                {item.status && (
                  <span className={cn('text-xs font-medium', getStatusColor?.(item.status))}>
                    {item.status}
                  </span>
                )}
              </div>
              {item.subtitle && (
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 truncate">
                  {item.subtitle}
                </p>
              )}
              {item.meta && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {item.meta}
                </p>
              )}
            </div>

            {/* Actions */}
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onItemAction?.('edit', item)}
              >
                <Edit className="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onItemAction?.('star', item)}
              >
                <Star className="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onItemAction?.('menu', item)}
              >
                <MoreVertical className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      ))}
    </Card>
  );
};`,

    stats: `import { Card } from '@/features/ui/primitives/card';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/features/ui/primitives/styles';

/**
 * 🤖 AI CONTEXT: Stats Display Pattern
 *
 * PURPOSE: Visual display of key metrics and KPIs
 * WHEN TO USE: Dashboards, analytics, performance monitoring
 * WHEN NOT TO USE: Detailed data (use tables), content (use cards)
 *
 * STAT COMPONENTS:
 * - Icon: Visual identifier for the metric
 * - Value: Primary number with appropriate formatting
 * - Label: Clear description of what's measured
 * - Change: Trend indicator with direction and percentage
 *
 * RESPONSIVE BEHAVIOR:
 * - 1 column on mobile
 * - 2 columns on tablet
 * - 4 columns on desktop
 * - Consistent card heights
 */

interface StatData {
  label: string;
  value: string | number;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon?: React.ReactNode;
  color?: string;
  description?: string;
}

interface StatsDisplayProps {
  stats: StatData[];
  variant?: 'default' | 'compact' | 'detailed';
}

export const StatsDisplay = ({ stats, variant = 'default' }: StatsDisplayProps) => {
  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4" />;
      case 'down':
        return <TrendingDown className="w-4 h-4" />;
      default:
        return <Minus className="w-4 h-4" />;
    }
  };

  const getTrendColor = (trend?: string) => {
    switch (trend) {
      case 'up':
        return 'text-green-600 dark:text-green-400';
      case 'down':
        return 'text-red-600 dark:text-red-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  const getColorClasses = (color: string) => {
    const colorMap = {
      green: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
      blue: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
      orange: 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400',
      purple: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400',
      red: 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400',
      cyan: 'bg-cyan-100 dark:bg-cyan-900/30 text-cyan-600 dark:text-cyan-400'
    };
    return colorMap[color as keyof typeof colorMap] || colorMap.blue;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <Card
          key={stat.label}
          glowColor={stat.color as GlowColor}
          className={cn(
            "hover:shadow-lg transition-shadow",
            variant === 'compact' ? "p-4" : "p-6"
          )}
        >
          <div className={cn(
            "flex items-center justify-between",
            variant === 'compact' ? "mb-2" : "mb-4"
          )}>
            {/* Icon */}
            {stat.icon && (
              <div className={cn(
                'p-2 rounded-lg',
                getColorClasses(stat.color || 'blue')
              )}>
                {stat.icon}
              </div>
            )}

            {/* Trend */}
            {stat.change && (
              <div className={cn(
                'flex items-center gap-1 text-sm font-medium',
                getTrendColor(stat.trend)
              )}>
                {getTrendIcon(stat.trend)}
                <span>{stat.change}</span>
              </div>
            )}
          </div>

          {/* Value and Label */}
          <div>
            <p className={cn(
              'font-bold mb-1',
              variant === 'compact' ? 'text-xl' : 'text-2xl'
            )}>
              {stat.value}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {stat.label}
            </p>
            {variant === 'detailed' && stat.description && (
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                {stat.description}
              </p>
            )}
          </div>
        </Card>
      ))}
    </div>
  );
};`
  };

  return codeExamples[patternId as keyof typeof codeExamples] || '';
};

export const DataDisplayPattern = () => {
  const [selectedPattern, setSelectedPattern] = useState<string>('table');

  const currentPattern = DATA_DISPLAY_PATTERNS.find(p => p.id === selectedPattern);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-4">Data Display Patterns</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Patterns for displaying and interacting with data including tables, cards, lists, and statistics.
        </p>
      </div>

      {/* Pattern Selector */}
      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Select Data Display Pattern</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {DATA_DISPLAY_PATTERNS.map((pattern) => (
            <Card
              key={pattern.id}
              className={cn(
                "p-4 cursor-pointer transition-all duration-200",
                selectedPattern === pattern.id
                  ? "border-cyan-500 shadow-[0_0_10px_rgba(34,211,238,0.3)]"
                  : "hover:shadow-lg"
              )}
              onClick={() => setSelectedPattern(pattern.id)}
            >
              <h4 className="font-medium mb-2">{pattern.name}</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                {pattern.description}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                <strong>Use for:</strong> {pattern.usage}
              </p>
            </Card>
          ))}
        </div>
      </Card>

      {/* Live Preview */}
      {currentPattern && (
        <Card className="p-6 max-w-none">
          <h3 className="text-lg font-semibold mb-4">
            {currentPattern.name} - Examples
          </h3>
          <currentPattern.component />
        </Card>
      )}

      {/* Generated Code */}
      {currentPattern && (
        <Card className="p-6 max-w-none">
          <h3 className="text-lg font-semibold mb-4">Generated Code</h3>
          <CodeDisplay
            code={generateCode(selectedPattern)}
            
            showLineNumbers
          />
        </Card>
      )}
    </div>
  );
};