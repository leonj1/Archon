import { useState } from "react";
import { Palette, Layout, Settings } from "lucide-react";
import { PillNavigation, type PillNavigationItem } from "../shared/PillNavigation";
import { StyleGuideTab } from "../tabs/StyleGuideTab";
import { LayoutsTab } from "../tabs/LayoutsTab";
import { ConfiguratorsTab } from "../tabs/ConfiguratorsTab";
import { ThemeToggle } from "../../../components/ui/ThemeToggle";

export const StyleGuideView = () => {
  const [activeTab, setActiveTab] = useState<"style-guide" | "layouts" | "configurators">(
    "style-guide",
  );

  const navigationItems: PillNavigationItem[] = [
    { id: "style-guide", label: "Style Guide", icon: <Palette className="w-4 h-4" /> },
    { id: "layouts", label: "Layouts", icon: <Layout className="w-4 h-4" /> },
    { id: "configurators", label: "Configurators", icon: <Settings className="w-4 h-4" /> },
  ];

  return (
    <div className="space-y-12">
      {/* Header */}
      <div className="relative">
        <div className="absolute top-0 right-0">
          <ThemeToggle accentColor="blue" />
        </div>
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Archon UI Style Guide
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-lg max-w-2xl mx-auto">
            Design system foundations, layout patterns, and interactive component configurators.
          </p>
        </div>
      </div>

      {/* Tab Navigation - Blue Pill Navigation */}
      <div className="flex justify-center">
        <PillNavigation
          items={navigationItems}
          activeSection={activeTab}
          onSectionClick={(id) => setActiveTab(id as typeof activeTab)}
          colorVariant="blue"
          showIcons={true}
          showText={true}
          hasSubmenus={false}
        />
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === "style-guide" && <StyleGuideTab />}
        {activeTab === "layouts" && <LayoutsTab />}
        {activeTab === "configurators" && <ConfiguratorsTab />}
      </div>
    </div>
  );
};
