import React, { useState } from 'react';
import { cn, glassmorphism, glassCard } from '@/features/ui/primitives/styles';
import { Palette, Component, Layout, Code, ChevronDown } from 'lucide-react';

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
    setOpenDropdown(null); // Close dropdown after selection
  };

  const selectedSectionData = NAVIGATION_ITEMS.find(item => item.id === selectedSection);

  return (
    <div className="relative">
      {/* Top-level Glass Pill Navigation - Using proper glass styles */}
      <div className="flex items-center justify-center">
        <div className={cn(
          glassCard.blur.xl,  // Standard glass blur
          glassCard.transparency.light,  // Light transparency for true glass
          glassmorphism.border.default,  // Proper glass border
          "rounded-full p-1 shadow-lg"
        )}>
          <div className="flex gap-1">
            {NAVIGATION_ITEMS.map((item) => {
              const isSelected = selectedSection === item.id;
              const hasDropdown = item.items && item.items.length > 0;

              return (
                <button
                  key={item.id}
                  onClick={() => handleSectionClick(item.id)}
                  className={cn(
                    "flex items-center gap-2 px-6 py-3 rounded-full transition-all duration-200",
                    "text-sm font-medium",
                    isSelected
                      ? "bg-cyan-500/20 dark:bg-cyan-400/20 text-cyan-700 dark:text-cyan-300 border border-cyan-400/50 shadow-[0_0_10px_rgba(34,211,238,0.5)]"
                      : "text-gray-700 dark:text-gray-300 hover:bg-white/10 dark:hover:bg-white/5"
                  )}
                >
                  {item.icon}
                  {item.label}
                  {hasDropdown && (
                    <ChevronDown
                      className={cn(
                        "w-4 h-4 transition-transform duration-200",
                        openDropdown === item.id && "rotate-180"
                      )}
                    />
                  )}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Sub-menu Drawer - Using proper glass styles */}
      {openDropdown && selectedSectionData?.items && (
        <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 z-50">
          <div className={cn(
            glassCard.blur["2xl"],  // Slightly stronger blur for dropdown
            "shadow-2xl"
          )}>
            {/* Square top edge connecting to pill */}
            <div className={cn(
              glassCard.transparency.medium,
              glassmorphism.border.default,
              "h-4 border-t border-l border-r"
            )} />

            {/* Dropdown content */}
            <div className={cn(
              glassCard.transparency.medium,
              glassmorphism.border.default,
              "rounded-b-lg border border-t-0 p-2"
            )}>
              <div className="grid grid-cols-3 gap-1 min-w-[400px]">
                {selectedSectionData.items.map((subItem) => {
                  const isSelected = selectedItem === subItem;

                  return (
                    <button
                      key={subItem}
                      onClick={() => handleItemClick(subItem)}
                      className={cn(
                        "px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200",
                        isSelected
                          ? "bg-cyan-500/30 dark:bg-cyan-400/30 text-cyan-700 dark:text-cyan-300 border border-cyan-400/50 shadow-[0_0_10px_rgba(34,211,238,0.5)]"
                          : "text-gray-700 dark:text-gray-300 hover:bg-white/20 dark:hover:bg-white/10"
                      )}
                    >
                      {subItem}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};