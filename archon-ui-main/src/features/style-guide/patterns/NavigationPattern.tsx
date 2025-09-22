import React, { useState } from 'react';
import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';
import { CodeDisplay } from '../shared/CodeDisplay';
import { cn, glassmorphism } from '@/features/ui/primitives/styles';
import {
  Home,
  Settings,
  User,
  FileText,
  BarChart,
  Menu,
  ChevronDown,
  ChevronRight,
  Search,
  Bell
} from 'lucide-react';

interface NavigationPattern {
  id: string;
  name: string;
  description: string;
  usage: string;
  component: React.ComponentType;
}

// Pill Navigation Demo
const PillNavigationDemo = () => {
  const [activeTab, setActiveTab] = useState('dashboard');

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: <Home className="w-4 h-4" /> },
    { id: 'projects', label: 'Projects', icon: <FileText className="w-4 h-4" /> },
    { id: 'analytics', label: 'Analytics', icon: <BarChart className="w-4 h-4" /> },
    { id: 'settings', label: 'Settings', icon: <Settings className="w-4 h-4" /> }
  ];

  return (
    <div className="space-y-6">
      {/* Standard Pill Navigation */}
      <div>
        <h4 className="font-medium mb-3">Standard Pills</h4>
        <div className="backdrop-blur-sm bg-white/40 dark:bg-white/5 border border-white/30 dark:border-white/15 rounded-full p-1 shadow-lg inline-flex">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-full transition-all duration-200 text-sm font-medium",
                activeTab === tab.id
                  ? "text-white border border-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.3)] dark:shadow-[0_0_10px_rgba(34,211,238,0.5)]"
                  : "text-gray-700 dark:text-gray-300 hover:bg-white/20 dark:hover:bg-white/5"
              )}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Icon-only Pills */}
      <div>
        <h4 className="font-medium mb-3">Icon Pills</h4>
        <div className="backdrop-blur-sm bg-white/40 dark:bg-white/5 border border-white/30 dark:border-white/15 rounded-full p-1 shadow-lg inline-flex">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "p-3 rounded-full transition-all duration-200",
                activeTab === tab.id
                  ? "text-white border border-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.3)]"
                  : "text-gray-700 dark:text-gray-300 hover:bg-white/20 dark:hover:bg-white/5"
              )}
              title={tab.label}
            >
              {tab.icon}
            </button>
          ))}
        </div>
      </div>

      {/* Vertical Pills */}
      <div>
        <h4 className="font-medium mb-3">Vertical Pills</h4>
        <div className="backdrop-blur-sm bg-white/40 dark:bg-white/5 border border-white/30 dark:border-white/15 rounded-2xl p-1 shadow-lg inline-flex flex-col">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-200 text-sm font-medium min-w-[120px]",
                activeTab === tab.id
                  ? "text-white border border-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.3)]"
                  : "text-gray-700 dark:text-gray-300 hover:bg-white/20 dark:hover:bg-white/5"
              )}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

// Sidebar Navigation Demo
const SidebarNavigationDemo = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [activeItem, setActiveItem] = useState('dashboard');

  const navItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: <Home className="w-5 h-5" />,
      hasSubmenu: false
    },
    {
      id: 'projects',
      label: 'Projects',
      icon: <FileText className="w-5 h-5" />,
      hasSubmenu: true,
      submenu: ['All Projects', 'Active', 'Archived']
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: <BarChart className="w-5 h-5" />,
      hasSubmenu: false
    },
    {
      id: 'team',
      label: 'Team',
      icon: <User className="w-5 h-5" />,
      hasSubmenu: true,
      submenu: ['Members', 'Roles', 'Permissions']
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: <Settings className="w-5 h-5" />,
      hasSubmenu: false
    }
  ];

  const [expandedItems, setExpandedItems] = useState<string[]>([]);

  const toggleExpanded = (itemId: string) => {
    setExpandedItems(prev =>
      prev.includes(itemId)
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  return (
    <div className="h-96 flex">
      {/* Sidebar */}
      <Card className={cn(
        "h-full transition-all duration-300 rounded-r-none border-r-0",
        collapsed ? "w-16" : "w-64"
      )}>
        <div className="p-4">
          {/* Toggle Button */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setCollapsed(!collapsed)}
            className="mb-4 w-full justify-start"
          >
            <Menu className="w-4 h-4" />
            {!collapsed && <span className="ml-2">Menu</span>}
          </Button>

          {/* Navigation Items */}
          <nav className="space-y-1">
            {navItems.map((item) => (
              <div key={item.id}>
                <button
                  onClick={() => {
                    setActiveItem(item.id);
                    if (item.hasSubmenu && !collapsed) {
                      toggleExpanded(item.id);
                    }
                  }}
                  className={cn(
                    "w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200 text-left",
                    activeItem === item.id
                      ? cn(glassmorphism.background.cyan, "text-cyan-700 dark:text-cyan-300")
                      : "hover:bg-gray-100 dark:hover:bg-gray-800"
                  )}
                >
                  {item.icon}
                  {!collapsed && (
                    <>
                      <span className="flex-1 text-sm font-medium">
                        {item.label}
                      </span>
                      {item.hasSubmenu && (
                        <ChevronDown
                          className={cn(
                            "w-4 h-4 transition-transform",
                            expandedItems.includes(item.id) && "rotate-180"
                          )}
                        />
                      )}
                    </>
                  )}
                </button>

                {/* Submenu */}
                {item.hasSubmenu && !collapsed && expandedItems.includes(item.id) && (
                  <div className="ml-8 mt-1 space-y-1">
                    {item.submenu?.map((subItem) => (
                      <button
                        key={subItem}
                        className="w-full text-left px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 rounded"
                      >
                        {subItem}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </nav>
        </div>
      </Card>

      {/* Main Content */}
      <Card className="flex-1 rounded-l-none border-l-0 p-6">
        <div className="text-center text-gray-500 dark:text-gray-400">
          <h3 className="font-medium mb-2">Main Content</h3>
          <p className="text-sm">Active page: {activeItem}</p>
          <p className="text-xs mt-2">Sidebar: {collapsed ? 'Collapsed' : 'Expanded'}</p>
        </div>
      </Card>
    </div>
  );
};

// Top Navigation Demo
const TopNavigationDemo = () => {
  const [activeNav, setActiveNav] = useState('dashboard');

  const navItems = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'projects', label: 'Projects' },
    { id: 'team', label: 'Team' },
    { id: 'analytics', label: 'Analytics' }
  ];

  return (
    <div className="space-y-4">
      {/* Top Navigation Bar */}
      <Card className="p-4">
        <div className="flex items-center justify-between">
          {/* Logo/Brand */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-purple-500 rounded-lg" />
            <span className="font-bold text-lg">Archon</span>
          </div>

          {/* Navigation Links */}
          <nav className="flex items-center gap-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveNav(item.id)}
                className={cn(
                  "px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                  activeNav === item.id
                    ? cn(glassmorphism.background.cyan, "text-cyan-700 dark:text-cyan-300")
                    : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-800"
                )}
              >
                {item.label}
              </button>
            ))}
          </nav>

          {/* User Actions */}
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm">
              <Search className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm">
              <Bell className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm">
              <User className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </Card>

      {/* Content Area */}
      <Card className="h-48 p-6">
        <div className="text-center text-gray-500 dark:text-gray-400">
          <h3 className="font-medium mb-2">Page Content</h3>
          <p className="text-sm">Currently viewing: {activeNav}</p>
        </div>
      </Card>
    </div>
  );
};

// Breadcrumb Navigation Demo
const BreadcrumbDemo = () => {
  const breadcrumbs = [
    { label: 'Home', href: '/' },
    { label: 'Projects', href: '/projects' },
    { label: 'Project Alpha', href: '/projects/alpha' },
    { label: 'Settings', href: '/projects/alpha/settings' }
  ];

  return (
    <div className="space-y-6">
      {/* Standard Breadcrumbs */}
      <div>
        <h4 className="font-medium mb-3">Standard Breadcrumbs</h4>
        <nav className="flex items-center space-x-2 text-sm">
          {breadcrumbs.map((crumb, index) => (
            <React.Fragment key={crumb.href}>
              <button
                className={cn(
                  "hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors",
                  index === breadcrumbs.length - 1
                    ? "text-gray-900 dark:text-gray-100 font-medium"
                    : "text-gray-500 dark:text-gray-400"
                )}
              >
                {crumb.label}
              </button>
              {index < breadcrumbs.length - 1 && (
                <ChevronRight className="w-4 h-4 text-gray-400" />
              )}
            </React.Fragment>
          ))}
        </nav>
      </div>

      {/* Pill Breadcrumbs */}
      <div>
        <h4 className="font-medium mb-3">Pill Breadcrumbs</h4>
        <nav className="flex items-center space-x-1">
          {breadcrumbs.map((crumb, index) => (
            <React.Fragment key={crumb.href}>
              <button
                className={cn(
                  "px-3 py-1 rounded-full text-sm transition-all duration-200",
                  index === breadcrumbs.length - 1
                    ? cn(glassmorphism.background.cyan, "text-cyan-700 dark:text-cyan-300 font-medium")
                    : "text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
                )}
              >
                {crumb.label}
              </button>
              {index < breadcrumbs.length - 1 && (
                <ChevronRight className="w-4 h-4 text-gray-400 mx-1" />
              )}
            </React.Fragment>
          ))}
        </nav>
      </div>

      {/* Compact Breadcrumbs */}
      <div>
        <h4 className="font-medium mb-3">Compact (Mobile)</h4>
        <nav className="flex items-center space-x-2 text-sm">
          <button className="text-gray-500 dark:text-gray-400 hover:text-cyan-600 dark:hover:text-cyan-400">
            ...
          </button>
          <ChevronRight className="w-4 h-4 text-gray-400" />
          <button className="text-gray-500 dark:text-gray-400 hover:text-cyan-600 dark:hover:text-cyan-400">
            {breadcrumbs[breadcrumbs.length - 2]?.label}
          </button>
          <ChevronRight className="w-4 h-4 text-gray-400" />
          <span className="text-gray-900 dark:text-gray-100 font-medium">
            {breadcrumbs[breadcrumbs.length - 1]?.label}
          </span>
        </nav>
      </div>
    </div>
  );
};

const NAVIGATION_PATTERNS: NavigationPattern[] = [
  {
    id: 'pills',
    name: 'Pill Navigation',
    description: 'Modern glassmorphism pill-style navigation tabs',
    usage: 'Primary navigation, tab switching, section selection',
    component: PillNavigationDemo
  },
  {
    id: 'sidebar',
    name: 'Sidebar Navigation',
    description: 'Collapsible sidebar with hierarchical navigation',
    usage: 'Application navigation, admin panels, file browsers',
    component: SidebarNavigationDemo
  },
  {
    id: 'topnav',
    name: 'Top Navigation',
    description: 'Horizontal navigation bar with branding and actions',
    usage: 'Website headers, application top bars, main navigation',
    component: TopNavigationDemo
  },
  {
    id: 'breadcrumbs',
    name: 'Breadcrumb Navigation',
    description: 'Hierarchical path navigation showing current location',
    usage: 'Deep navigation, file paths, multi-level applications',
    component: BreadcrumbDemo
  }
];

const generateCode = (patternId: string) => {
  const codeExamples = {
    pills: `import { useState } from 'react';
import { cn } from '@/features/ui/primitives/styles';

/**
 * 🤖 AI CONTEXT: Pill Navigation Pattern
 *
 * PURPOSE: Modern tab-style navigation with glassmorphism design
 * WHEN TO USE: Primary navigation, tab switching, section selection
 * WHEN NOT TO USE: Deep hierarchies, complex menus, long lists
 *
 * VARIANTS:
 * - Standard: Icon + text for desktop
 * - Icon-only: Compact for mobile/narrow spaces
 * - Vertical: Sidebar-style pill navigation
 *
 * ACCESSIBILITY:
 * - Use semantic nav element
 * - Include ARIA states (aria-current)
 * - Support keyboard navigation
 * - Provide tooltips for icon-only variants
 */

interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
}

export const PillNavigation = ({
  tabs,
  activeTab,
  onTabChange,
  variant = 'standard'
}: {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
  variant?: 'standard' | 'icon-only' | 'vertical';
}) => {
  return (
    <nav
      className={cn(
        "backdrop-blur-sm bg-white/40 dark:bg-white/5",
        "border border-white/30 dark:border-white/15 shadow-lg",
        variant === 'vertical' ? "rounded-2xl p-1 inline-flex flex-col" : "rounded-full p-1 inline-flex"
      )}
    >
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={cn(
            "transition-all duration-200 text-sm font-medium",
            variant === 'vertical' ? "rounded-xl min-w-[120px]" : "rounded-full",
            variant === 'icon-only' ? "p-3" : "px-4 py-2",
            "flex items-center gap-2",
            activeTab === tab.id
              ? "text-white border border-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.3)] dark:shadow-[0_0_10px_rgba(34,211,238,0.5)]"
              : "text-gray-700 dark:text-gray-300 hover:bg-white/20 dark:hover:bg-white/5"
          )}
          aria-current={activeTab === tab.id ? 'page' : undefined}
          title={variant === 'icon-only' ? tab.label : undefined}
        >
          {tab.icon}
          {variant !== 'icon-only' && tab.label}
        </button>
      ))}
    </nav>
  );
};`,

    sidebar: `import { useState } from 'react';
import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';
import { ChevronDown, ChevronLeft, ChevronRight } from 'lucide-react';
import { cn, glassmorphism } from '@/features/ui/primitives/styles';

/**
 * 🤖 AI CONTEXT: Sidebar Navigation Pattern
 *
 * PURPOSE: Hierarchical navigation with collapsible sidebar
 * WHEN TO USE: Complex applications, admin panels, file systems
 * WHEN NOT TO USE: Simple sites, mobile-first designs, shallow navigation
 *
 * FEATURES:
 * - Collapsible width (280px -> 60px)
 * - Submenu support with expansion
 * - Active state highlighting
 * - Smooth transitions
 *
 * RESPONSIVE BEHAVIOR:
 * - Desktop: Side-by-side layout
 * - Tablet: Overlay sidebar
 * - Mobile: Full-screen drawer
 */

interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  hasSubmenu?: boolean;
  submenu?: string[];
}

export const SidebarNavigation = ({
  items,
  activeItem,
  onItemClick,
  collapsed = false,
  onToggleCollapse
}: {
  items: NavItem[];
  activeItem: string;
  onItemClick: (itemId: string) => void;
  collapsed?: boolean;
  onToggleCollapse: () => void;
}) => {
  const [expandedItems, setExpandedItems] = useState<string[]>([]);

  const toggleExpanded = (itemId: string) => {
    setExpandedItems(prev =>
      prev.includes(itemId)
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  return (
    <Card className={cn(
      "h-full transition-all duration-300",
      collapsed ? "w-16" : "w-64"
    )}>
      <div className="p-4">
        {/* Toggle Button */}
        <Button
          variant="ghost"
          size="sm"
          onClick={onToggleCollapse}
          className="mb-4 w-full justify-start"
        >
          {collapsed ? <ChevronRight /> : <ChevronLeft />}
          {!collapsed && <span className="ml-2">Collapse</span>}
        </Button>

        {/* Navigation Items */}
        <nav className="space-y-1">
          {items.map((item) => (
            <div key={item.id}>
              <button
                onClick={() => {
                  onItemClick(item.id);
                  if (item.hasSubmenu && !collapsed) {
                    toggleExpanded(item.id);
                  }
                }}
                className={cn(
                  "w-full flex items-center gap-3 px-3 py-2 rounded-lg",
                  "transition-all duration-200 text-left",
                  activeItem === item.id
                    ? cn(glassmorphism.background.cyan, "text-cyan-700 dark:text-cyan-300")
                    : "hover:bg-gray-100 dark:hover:bg-gray-800"
                )}
              >
                {item.icon}
                {!collapsed && (
                  <>
                    <span className="flex-1 text-sm font-medium">
                      {item.label}
                    </span>
                    {item.hasSubmenu && (
                      <ChevronDown
                        className={cn(
                          "w-4 h-4 transition-transform",
                          expandedItems.includes(item.id) && "rotate-180"
                        )}
                      />
                    )}
                  </>
                )}
              </button>

              {/* Submenu */}
              {item.hasSubmenu && !collapsed && expandedItems.includes(item.id) && (
                <div className="ml-8 mt-1 space-y-1">
                  {item.submenu?.map((subItem) => (
                    <button
                      key={subItem}
                      className="w-full text-left px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 rounded"
                    >
                      {subItem}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </nav>
      </div>
    </Card>
  );
};`,

    topnav: `import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';
import { Search, Bell, User } from 'lucide-react';
import { cn, glassmorphism } from '@/features/ui/primitives/styles';

/**
 * 🤖 AI CONTEXT: Top Navigation Pattern
 *
 * PURPOSE: Primary horizontal navigation with branding and actions
 * WHEN TO USE: Website headers, app top bars, main navigation
 * WHEN NOT TO USE: Deep navigation, complex hierarchies, space-constrained designs
 *
 * STRUCTURE:
 * - Left: Brand/logo
 * - Center: Primary navigation links
 * - Right: User actions and utilities
 *
 * RESPONSIVE BEHAVIOR:
 * - Desktop: Full horizontal layout
 * - Tablet: Collapsed navigation menu
 * - Mobile: Hamburger menu with drawer
 */

interface NavItem {
  id: string;
  label: string;
  href?: string;
}

export const TopNavigation = ({
  brand,
  navItems,
  activeItem,
  onNavClick,
  userActions
}: {
  brand: React.ReactNode;
  navItems: NavItem[];
  activeItem: string;
  onNavClick: (itemId: string) => void;
  userActions?: React.ReactNode;
}) => {
  return (
    <Card className="p-4">
      <div className="flex items-center justify-between">
        {/* Brand/Logo */}
        <div className="flex items-center gap-3">
          {brand}
        </div>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onNavClick(item.id)}
              className={cn(
                "px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                activeItem === item.id
                  ? cn(glassmorphism.background.cyan, "text-cyan-700 dark:text-cyan-300")
                  : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-800"
              )}
            >
              {item.label}
            </button>
          ))}
        </nav>

        {/* User Actions */}
        <div className="flex items-center gap-2">
          {userActions || (
            <>
              <Button variant="ghost" size="sm">
                <Search className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm">
                <Bell className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm">
                <User className="w-4 h-4" />
              </Button>
            </>
          )}
        </div>
      </div>
    </Card>
  );
};`,

    breadcrumbs: `import { ChevronRight } from 'lucide-react';
import { cn, glassmorphism } from '@/features/ui/primitives/styles';

/**
 * 🤖 AI CONTEXT: Breadcrumb Navigation Pattern
 *
 * PURPOSE: Hierarchical path navigation showing current location
 * WHEN TO USE: Deep navigation, file systems, multi-level apps
 * WHEN NOT TO USE: Shallow navigation, single-page apps, unclear hierarchies
 *
 * VARIANTS:
 * - Standard: Text links with separators
 * - Pill: Rounded pill-style breadcrumbs
 * - Compact: Ellipsis for mobile/narrow spaces
 *
 * ACCESSIBILITY:
 * - Use semantic nav element
 * - Include aria-label for navigation
 * - Mark current page with aria-current
 * - Ensure sufficient color contrast
 */

interface Breadcrumb {
  label: string;
  href: string;
}

export const BreadcrumbNavigation = ({
  breadcrumbs,
  variant = 'standard',
  maxItems = 4
}: {
  breadcrumbs: Breadcrumb[];
  variant?: 'standard' | 'pill' | 'compact';
  maxItems?: number;
}) => {
  const displayCrumbs = variant === 'compact' && breadcrumbs.length > maxItems
    ? [
        ...breadcrumbs.slice(0, 1),
        { label: '...', href: '#' },
        ...breadcrumbs.slice(-2)
      ]
    : breadcrumbs;

  return (
    <nav aria-label="Breadcrumb" className="flex items-center space-x-1">
      {displayCrumbs.map((crumb, index) => (
        <React.Fragment key={crumb.href}>
          {variant === 'pill' ? (
            <button
              className={cn(
                "px-3 py-1 rounded-full text-sm transition-all duration-200",
                index === displayCrumbs.length - 1
                  ? cn(glassmorphism.background.cyan, "text-cyan-700 dark:text-cyan-300 font-medium")
                  : "text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
              )}
              aria-current={index === displayCrumbs.length - 1 ? 'page' : undefined}
            >
              {crumb.label}
            </button>
          ) : (
            <button
              className={cn(
                "hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors text-sm",
                index === displayCrumbs.length - 1
                  ? "text-gray-900 dark:text-gray-100 font-medium"
                  : "text-gray-500 dark:text-gray-400"
              )}
              aria-current={index === displayCrumbs.length - 1 ? 'page' : undefined}
            >
              {crumb.label}
            </button>
          )}

          {index < displayCrumbs.length - 1 && (
            <ChevronRight className="w-4 h-4 text-gray-400 mx-1" />
          )}
        </React.Fragment>
      ))}
    </nav>
  );
};`
  };

  return codeExamples[patternId as keyof typeof codeExamples] || '';
};

export const NavigationPattern = () => {
  const [selectedPattern, setSelectedPattern] = useState<string>('pills');

  const currentPattern = NAVIGATION_PATTERNS.find(p => p.id === selectedPattern);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-4">Navigation Patterns</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Navigation components including pills, sidebars, top navigation, and breadcrumbs.
        </p>
      </div>

      {/* Pattern Selector */}
      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Select Navigation Pattern</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {NAVIGATION_PATTERNS.map((pattern) => (
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