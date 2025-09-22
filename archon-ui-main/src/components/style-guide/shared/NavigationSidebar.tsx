import { useState } from 'react';
import { ChevronRight, ChevronDown } from 'lucide-react';
import { cn } from '@/features/ui/primitives/styles';

interface NavigationSection {
  label: string;
  items: string[];
}

interface NavigationSidebarProps {
  sections: NavigationSection[];
  selectedItem: string;
  onItemSelect: (item: string) => void;
}

// Default navigation structure for style guide
// This can be used when creating a NavigationSidebar instanc

export const NavigationSidebar: React.FC<NavigationSidebarProps> = ({
  sections,
  selectedItem,
  onItemSelect
}) => {
  const [expandedSections, setExpandedSections] = useState<string[]>(
    sections.map(s => s.label)
  );

  const toggleSection = (label: string) => {
    setExpandedSections(prev =>
      prev.includes(label)
        ? prev.filter(l => l !== label)
        : [...prev, label]
    );
  };

  return (
    <aside className="w-64 p-4">
      <div className="space-y-2">
        {sections.map((section) => {
          const isExpanded = expandedSections.includes(section.label);

          return (
            <div key={section.label}>
              <button
                onClick={() => toggleSection(section.label)}
                className={cn(
                  "flex items-center justify-between w-full px-3 py-2 text-left",
                  "rounded-md hover:bg-white/10 dark:hover:bg-white/5",
                  "text-sm font-medium text-gray-700 dark:text-gray-300",
                  "transition-colors"
                )}
              >
                {section.label}
                {isExpanded ? (
                  <ChevronDown className="w-4 h-4" />
                ) : (
                  <ChevronRight className="w-4 h-4" />
                )}
              </button>

              {isExpanded && (
                <div className="ml-2 mt-1 space-y-1">
                  {section.items.map((item) => {
                    const isSelected = selectedItem === item;

                    return (
                      <button
                        key={item}
                        onClick={() => onItemSelect(item)}
                        className={cn(
                          "block w-full px-3 py-1.5 text-left rounded-md",
                          "text-sm text-gray-600 dark:text-gray-400",
                          "transition-colors",
                          isSelected
                            ? "bg-cyan-500/20 text-cyan-700 dark:text-cyan-300"
                            : "hover:bg-white/10 dark:hover:bg-white/5"
                        )}
                      >
                        {item}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </aside>
  );
};