import React, { useState } from 'react';
import { Card } from '@/features/ui/primitives/card';
import { Checkbox } from '@/features/ui/primitives/checkbox';
import { CodeDisplay } from '../shared/CodeDisplay';
import { cn } from '@/features/ui/primitives/styles';
import {
  Home,
  FileText,
  BarChart,
  Settings,
  ChevronRight,
  Palette,
  Component,
  Layout,
  Code
} from 'lucide-react';

// Pill Navigation Configurator
const PillNavigationConfigurator = () => {
  const [activeSection, setActiveSection] = useState('foundations');
  const [activeItem, setActiveItem] = useState('Colors');
  const [openDropdown, setOpenDropdown] = useState<string | null>('foundations');

  // Configuration options
  const [colorVariant, setColorVariant] = useState('cyan');
  const [size, setSize] = useState('default');
  const [showIcons, setShowIcons] = useState(true);
  const [showText, setShowText] = useState(true);
  const [hasSubmenus, setHasSubmenus] = useState(true);

  // Editable navigation items
  const [navigationItems, setNavigationItems] = useState([
    {
      id: 'foundations',
      label: 'Foundations',
      icon: <Palette className="w-4 h-4" />,
      items: ['Colors', 'Typography', 'Spacing', 'Effects']
    },
    {
      id: 'components',
      label: 'Components',
      icon: <Component className="w-4 h-4" />,
      items: ['Cards', 'Buttons', 'Forms', 'Tables']
    },
    {
      id: 'patterns',
      label: 'Patterns',
      icon: <Layout className="w-4 h-4" />,
      items: ['Layouts', 'Navigation', 'Data Display']
    },
    {
      id: 'examples',
      label: 'Examples',
      icon: <Code className="w-4 h-4" />,
      items: ['Compositions', 'Pages', 'Workflows']
    }
  ]);

  const handleSectionClick = (sectionId: string) => {
    if (activeSection === sectionId && openDropdown === sectionId) {
      setOpenDropdown(null);
    } else {
      setActiveSection(sectionId);
      if (hasSubmenus) {
        setOpenDropdown(sectionId);
        // Set first item as default
        const section = navigationItems.find(item => item.id === sectionId);
        if (section?.items?.[0]) {
          setActiveItem(section.items[0]);
        }
      }
    }
  };

  const handleItemClick = (item: string) => {
    setActiveItem(item);
  };

  const updateItemLabel = (itemIndex: number, newLabel: string) => {
    setNavigationItems(prev =>
      prev.map((item, index) =>
        index === itemIndex ? { ...item, label: newLabel } : item
      )
    );
  };

  const getColorClasses = (variant: string, isSelected: boolean) => {
    const colors = {
      cyan: isSelected
        ? "bg-cyan-500/20 dark:bg-cyan-400/20 text-cyan-700 dark:text-cyan-300 border border-cyan-400/50 shadow-[0_0_10px_rgba(34,211,238,0.5)]"
        : "text-gray-700 dark:text-gray-300 hover:bg-white/10 dark:hover:bg-white/5",
      purple: isSelected
        ? "bg-purple-500/20 dark:bg-purple-400/20 text-purple-700 dark:text-purple-300 border border-purple-400/50 shadow-[0_0_10px_rgba(147,51,234,0.5)]"
        : "text-gray-700 dark:text-gray-300 hover:bg-white/10 dark:hover:bg-white/5",
      emerald: isSelected
        ? "bg-emerald-500/20 dark:bg-emerald-400/20 text-emerald-700 dark:text-emerald-300 border border-emerald-400/50 shadow-[0_0_10px_rgba(16,185,129,0.5)]"
        : "text-gray-700 dark:text-gray-300 hover:bg-white/10 dark:hover:bg-white/5",
      orange: isSelected
        ? "bg-orange-500/20 dark:bg-orange-400/20 text-orange-700 dark:text-orange-300 border border-orange-400/50 shadow-[0_0_10px_rgba(251,146,60,0.5)]"
        : "text-gray-700 dark:text-gray-300 hover:bg-white/10 dark:hover:bg-white/5"
    };
    return colors[variant as keyof typeof colors] || colors.cyan;
  };

  const getSizeClasses = (sizeVariant: string) => {
    const sizes = {
      small: "px-4 py-2 text-xs",
      default: "px-6 py-3 text-sm",
      large: "px-8 py-4 text-base"
    };
    return sizes[sizeVariant as keyof typeof sizes] || sizes.default;
  };

  const selectedSectionData = navigationItems.find(item => item.id === activeSection);

  const renderPillNavigation = () => (
    <div className="backdrop-blur-sm bg-white/40 dark:bg-white/5 border border-white/30 dark:border-white/15 rounded-full p-1 shadow-lg transition-all duration-300 ease-in-out">
      <div className="flex gap-1 items-center">
        {navigationItems.map((item) => {
          const isSelected = activeSection === item.id;
          const hasDropdown = hasSubmenus && item.items && item.items.length > 0;
          const isThisExpanded = openDropdown === item.id && hasDropdown;

          return (
            <div key={item.id} className="relative">
              {/* Extended pill for selected item with dropdown */}
              {isSelected && hasDropdown ? (
                <div className={cn(
                  "flex items-center gap-2 rounded-full transition-all duration-200",
                  "font-medium whitespace-nowrap",
                  getSizeClasses(size),
                  getColorClasses(colorVariant, true)
                )}>
                  {showIcons && item.icon}
                  {showText && item.label}

                  {/* Dropdown selector inside the pill */}
                  <div className="flex items-center ml-4 pl-4 border-l border-current/30">
                    <select
                      value={activeItem || ''}
                      onChange={(e) => handleItemClick(e.target.value)}
                      className="bg-transparent border-none outline-none font-medium cursor-pointer text-inherit"
                    >
                      <option value="" disabled>Select...</option>
                      {item.items?.map((subItem) => (
                        <option key={subItem} value={subItem} className="bg-gray-800 text-white">
                          {subItem}
                        </option>
                      ))}
                    </select>
                  </div>

                  <ChevronRight
                    className={cn(
                      "w-4 h-4 transition-transform duration-300 ml-2 cursor-pointer",
                      isThisExpanded ? "-rotate-90" : "rotate-0"
                    )}
                    onClick={() => handleSectionClick(item.id)}
                  />
                </div>
              ) : (
                /* Regular pill for non-selected items */
                <button
                  onClick={() => handleSectionClick(item.id)}
                  className={cn(
                    "flex items-center gap-2 rounded-full transition-all duration-200",
                    "font-medium whitespace-nowrap",
                    getSizeClasses(size),
                    getColorClasses(colorVariant, isSelected)
                  )}
                >
                  {showIcons && item.icon}
                  {showText && item.label}
                  {hasDropdown && (
                    <ChevronRight
                      className={cn(
                        "w-4 h-4 transition-transform duration-300",
                        isThisExpanded ? "-rotate-90" : "rotate-0"
                      )}
                    />
                  )}
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );

  return {
    renderPillNavigation,
    activeSection,
    activeItem,
    colorVariant,
    setColorVariant,
    size,
    setSize,
    showIcons,
    setShowIcons,
    showText,
    setShowText,
    hasSubmenus,
    setHasSubmenus,
    navigationItems,
    updateItemLabel
  };
};



const generateCode = (configurator: ReturnType<typeof PillNavigationConfigurator>) => {
  const hasSubmenus = configurator.hasSubmenus;
  const colorVariant = configurator.colorVariant;
  const size = configurator.size;
  const showIcons = configurator.showIcons;
  const showText = configurator.showText;
  const navigationItems = configurator.navigationItems;

  const itemsCode = navigationItems.map(item => {
    const iconName = item.icon?.type?.displayName || item.icon?.type?.name || 'Icon';
    return `    {
      id: '${item.id}',
      label: '${item.label}',${showIcons ? `
      icon: <${iconName} className="w-4 h-4" />,` : ''}${hasSubmenus ? `
      items: [${item.items?.map(subItem => `'${subItem}'`).join(', ')}]` : ''}
    }`;
  }).join(',\n');

  return `import { useState } from 'react';
import { cn } from '@/features/ui/primitives/styles';${hasSubmenus ? `
import { ChevronRight } from 'lucide-react';` : ''}${showIcons ? `
import { ${navigationItems.map(item => {
    const iconName = item.icon?.type?.displayName || item.icon?.type?.name || 'Icon';
    return iconName;
  }).filter((name, index, arr) => arr.indexOf(name) === index).join(', ')} } from 'lucide-react';` : ''}

export const PillNavigation = () => {
  const [activeSection, setActiveSection] = useState('${configurator.activeSection}');${hasSubmenus ? `
  const [activeItem, setActiveItem] = useState('${configurator.activeItem}');
  const [openDropdown, setOpenDropdown] = useState<string | null>('${configurator.activeSection}');` : ''}

  const navigationItems = [
${itemsCode}
  ];

  const handleSectionClick = (sectionId: string) => {${hasSubmenus ? `
    if (activeSection === sectionId && openDropdown === sectionId) {
      setOpenDropdown(null);
    } else {
      setActiveSection(sectionId);
      setOpenDropdown(sectionId);
      // Set first item as default
      const section = navigationItems.find(item => item.id === sectionId);
      if (section?.items?.[0]) {
        setActiveItem(section.items[0]);
      }
    }` : `
    setActiveSection(sectionId);`}
  };${hasSubmenus ? `

  const handleItemClick = (item: string) => {
    setActiveItem(item);
  };` : ''}

  const getColorClasses = (isSelected: boolean) => {
    return isSelected
      ? "bg-${colorVariant}-500/20 dark:bg-${colorVariant}-400/20 text-${colorVariant}-700 dark:text-${colorVariant}-300 border border-${colorVariant}-400/50 shadow-[0_0_10px_rgba(${colorVariant === 'cyan' ? '34,211,238' : colorVariant === 'purple' ? '147,51,234' : colorVariant === 'emerald' ? '16,185,129' : '251,146,60'},0.5)]"
      : "text-gray-700 dark:text-gray-300 hover:bg-white/10 dark:hover:bg-white/5";
  };${hasSubmenus ? `

  const selectedSectionData = navigationItems.find(item => item.id === activeSection);` : ''}

  return (
    <div className="backdrop-blur-sm bg-white/40 dark:bg-white/5 border border-white/30 dark:border-white/15 rounded-full p-1 shadow-lg transition-all duration-300 ease-in-out">
      <div className="flex gap-1 items-center">
        {navigationItems.map((item) => {
          const isSelected = activeSection === item.id;${hasSubmenus ? `
          const hasDropdown = item.items && item.items.length > 0;
          const isThisExpanded = openDropdown === item.id && hasDropdown;` : ''}

          return (
            <div key={item.id} className="relative">${hasSubmenus ? `
              {/* Extended pill for selected item with dropdown */}
              {isSelected && hasDropdown ? (
                <div className={cn(
                  "flex items-center gap-2 ${size === 'small' ? 'px-4 py-2 text-xs' : size === 'large' ? 'px-8 py-4 text-base' : 'px-6 py-3 text-sm'} rounded-full transition-all duration-200",
                  "font-medium whitespace-nowrap",
                  getColorClasses(true)
                )}>
                  ${showIcons ? '{item.icon}' : ''}${showText ? `${showIcons ? ' ' : ''}{item.label}` : ''}

                  {/* Dropdown selector inside the pill */}
                  <div className="flex items-center ml-4 pl-4 border-l border-current/30">
                    <select
                      value={activeItem || ''}
                      onChange={(e) => handleItemClick(e.target.value)}
                      className="bg-transparent border-none outline-none font-medium cursor-pointer text-inherit"
                    >
                      <option value="" disabled>Select...</option>
                      {item.items?.map((subItem) => (
                        <option key={subItem} value={subItem} className="bg-gray-800 text-white">
                          {subItem}
                        </option>
                      ))}
                    </select>
                  </div>

                  <ChevronRight
                    className={cn(
                      "w-4 h-4 transition-transform duration-300 ml-2 cursor-pointer",
                      isThisExpanded ? "-rotate-90" : "rotate-0"
                    )}
                    onClick={() => handleSectionClick(item.id)}
                  />
                </div>
              ) : (
                /* Regular pill for non-selected items */` : ''}
              <button
                onClick={() => handleSectionClick(item.id)}
                className={cn(
                  "flex items-center gap-2 ${size === 'small' ? 'px-4 py-2 text-xs' : size === 'large' ? 'px-8 py-4 text-base' : 'px-6 py-3 text-sm'} rounded-full transition-all duration-200",
                  "font-medium whitespace-nowrap",
                  getColorClasses(isSelected)
                )}
              >
                ${showIcons ? '{item.icon}' : ''}${showText ? `${showIcons ? ' ' : ''}{item.label}` : ''}${hasSubmenus ? `
                {hasDropdown && (
                  <ChevronRight
                    className={cn(
                      "w-4 h-4 transition-transform duration-300",
                      isThisExpanded ? "-rotate-90" : "rotate-0"
                    )}
                  />
                )}` : ''}
              </button>${hasSubmenus ? `
              )}` : ''}
            </div>
          );
        })}
      </div>
    </div>
  );
};`;
};

export const NavigationPattern = () => {
  const configurator = PillNavigationConfigurator();

  return (
    <div className="space-y-8">
      {/* Header Description */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Pill Navigation</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Modern glassmorphism pill-style navigation with optional sub-menu support. Perfect for primary navigation,
          tab switching, and section selection with hierarchical options. Features an extended pill design for selected
          items with internal dropdown selectors.
        </p>
      </div>

      {/* Full Width Live Preview */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Live Preview</h3>
        <div className="flex items-center justify-center py-8">
          {configurator.renderPillNavigation()}
        </div>

        {/* Current Selection Display */}
        {configurator.hasSubmenus && (
          <div className="mt-6 text-center p-4 bg-gray-50 dark:bg-gray-800/30 rounded-lg">
            <h4 className="font-medium text-gray-900 dark:text-gray-100">Current Selection</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Section: <span className="font-medium">{configurator.activeSection}</span>
              {configurator.activeItem && (
                <> | Item: <span className="font-medium">{configurator.activeItem}</span></>
              )}
            </p>
          </div>
        )}
      </Card>

      {/* Split Layout: Configurator + Code */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

        {/* Left Half: Configuration Controls */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Configuration Options</h3>
          <div className="space-y-4">

            {/* Color and Size */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Color Variant</label>
                <select
                  value={configurator.colorVariant}
                  onChange={(e) => configurator.setColorVariant(e.target.value)}
                  className="w-full p-2 text-sm border rounded-md bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600"
                >
                  <option value="cyan">Cyan</option>
                  <option value="purple">Purple</option>
                  <option value="emerald">Emerald</option>
                  <option value="orange">Orange</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Size</label>
                <select
                  value={configurator.size}
                  onChange={(e) => configurator.setSize(e.target.value)}
                  className="w-full p-2 text-sm border rounded-md bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600"
                >
                  <option value="small">Small</option>
                  <option value="default">Default</option>
                  <option value="large">Large</option>
                </select>
              </div>
            </div>

            {/* Checkboxes */}
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-3">
                <Checkbox
                  id="show-icons"
                  checked={configurator.showIcons}
                  onCheckedChange={configurator.setShowIcons}
                  color="cyan"
                />
                <label htmlFor="show-icons" className="text-sm font-medium">
                  Show Icons
                </label>
              </div>
              <div className="flex items-center gap-3">
                <Checkbox
                  id="show-text"
                  checked={configurator.showText}
                  onCheckedChange={configurator.setShowText}
                  color="cyan"
                />
                <label htmlFor="show-text" className="text-sm font-medium">
                  Show Text
                </label>
              </div>
            </div>

            {/* Submenu toggle */}
            <div className="flex items-center gap-3">
              <Checkbox
                id="has-submenus"
                checked={configurator.hasSubmenus}
                onCheckedChange={configurator.setHasSubmenus}
                color="cyan"
              />
              <label htmlFor="has-submenus" className="text-sm font-medium">
                Enable Sub-menus
              </label>
            </div>

            {/* Editable Navigation Items */}
            <div>
              <label className="block text-sm font-medium mb-2">Navigation Items</label>
              <div className="space-y-2">
                {configurator.navigationItems.map((item, index) => (
                  <input
                    key={item.id}
                    type="text"
                    value={item.label}
                    onChange={(e) => configurator.updateItemLabel(index, e.target.value)}
                    className="w-full p-2 text-sm border rounded-md bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600"
                    placeholder={`Item ${index + 1} label`}
                  />
                ))}
              </div>
            </div>
          </div>
        </Card>

        {/* Right Half: Generated Code */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Generated Code</h3>
          <CodeDisplay
            code={generateCode(configurator)}
            showLineNumbers
          />
        </Card>
      </div>
    </div>
  );
};