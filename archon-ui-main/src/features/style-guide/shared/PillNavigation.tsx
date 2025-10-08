import React, { useState } from 'react';
import { cn, glassmorphism, glassCard } from '@/features/ui/primitives/styles';
import { Palette, Component, Layout, Code, ChevronRight } from 'lucide-react';

interface NavigationItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  items?: string[];
}

interface PillNavigationProps {
  selectedSection: string;
  selectedItem: string | null;
  onSectionChange: (section: string) => void;
  onItemChange: (item: string | null) => void;
}

const NAVIGATION_ITEMS: NavigationItem[] = [
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
    items: ['Cards', 'Buttons', 'Forms', 'Tables', 'Modals', 'Toggles']
  },
  {
    id: 'patterns',
    label: 'Patterns',
    icon: <Layout className="w-4 h-4" />,
    items: ['Layouts', 'Feedback', 'Navigation', 'Data Display']
  },
  {
    id: 'examples',
    label: 'Examples',
    icon: <Code className="w-4 h-4" />,
    items: ['Compositions', 'Pages', 'Workflows']
  }
];

export const PillNavigation: React.FC<PillNavigationProps> = ({
  selectedSection,
  selectedItem,
  onSectionChange,
  onItemChange
}) => {
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);

  const handleSectionClick = (sectionId: string) => {
    if (selectedSection === sectionId && openDropdown === sectionId) {
      // Close dropdown if same section clicked
      setOpenDropdown(null);
    } else {
      // Open new section
      onSectionChange(sectionId);
      setOpenDropdown(sectionId);
    }
  };

  const handleItemClick = (item: string) => {
    onItemChange(item);
    // Keep dropdown open after selection to show the selected state
  };

  const selectedSectionData = NAVIGATION_ITEMS.find(item => item.id === selectedSection);
  const isExpanded = openDropdown === selectedSection && selectedSectionData?.items;

  return (
    <div className="flex items-center justify-center">
      <div className={cn(
        "backdrop-blur-sm bg-white/40 dark:bg-white/5 border border-white/30 dark:border-white/15 rounded-full p-1 shadow-lg transition-all duration-300 ease-in-out"
      )}>
        <div className="flex gap-1 items-center">
          {/* Main navigation items */}
          {NAVIGATION_ITEMS.map((item) => {
            const isSelected = selectedSection === item.id;
            const hasDropdown = item.items && item.items.length > 0;
            const isThisExpanded = openDropdown === item.id && hasDropdown;

            return (
              <div key={item.id} className="relative">
                {/* Extended pill for selected item with dropdown */}
                {isSelected && hasDropdown ? (
                  <div className={cn(
                    "flex items-center gap-2 px-6 py-3 rounded-full transition-all duration-200",
                    "text-sm font-medium whitespace-nowrap",
                    "bg-cyan-500/20 dark:bg-cyan-400/20 text-cyan-700 dark:text-cyan-300 border border-cyan-400/50 shadow-[0_0_10px_rgba(34,211,238,0.5)]"
                  )}>
                    {item.icon}
                    {item.label}

                    {/* Dropdown selector inside the pill */}
                    <div className="flex items-center ml-4 pl-4 border-l border-cyan-400/30">
                      <select
                        value={selectedItem || ''}
                        onChange={(e) => handleItemClick(e.target.value)}
                        className={cn(
                          "bg-transparent text-cyan-700 dark:text-cyan-300 border-none outline-none",
                          "text-sm font-medium cursor-pointer"
                        )}
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
                        "w-4 h-4 transition-transform duration-300 ml-2",
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
                      "flex items-center gap-2 px-6 py-3 rounded-full transition-all duration-200",
                      "text-sm font-medium whitespace-nowrap",
                      isSelected
                        ? "bg-cyan-500/20 dark:bg-cyan-400/20 text-cyan-700 dark:text-cyan-300 border border-cyan-400/50 shadow-[0_0_10px_rgba(34,211,238,0.5)]"
                        : "text-gray-700 dark:text-gray-300 hover:bg-white/10 dark:hover:bg-white/5"
                    )}
                  >
                    {item.icon}
                    {item.label}
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
    </div>
  );
};