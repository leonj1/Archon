import { useState } from "react";
import {
  Type,
  Sparkles,
  CreditCard,
  MousePointer,
  Navigation as NavIcon,
  Square,
  FormInput,
  Table as TableIcon,
  ToggleLeft,
  Power,
  CheckSquare,
} from "lucide-react";
import { SideNavigation, type SideNavigationSection } from "../shared/SideNavigation";
import { TypographyFoundation } from "../foundations/TypographyFoundation";
import { EffectsFoundation } from "../foundations/EffectsFoundation";
import { GlassCardConfigurator } from "../configurators/GlassCardConfigurator";
import { ButtonConfigurator } from "../configurators/ButtonConfigurator";
import { NavigationPattern } from "../configurators/NavigationConfigurator";
import { ModalConfigurator } from "../configurators/ModalConfigurator";
import { FormConfigurator } from "../configurators/FormConfigurator";
import { TableConfigurator } from "../configurators/TableConfigurator";
import { ToggleConfigurator } from "../configurators/ToggleConfigurator";
import { SwitchConfigurator } from "../configurators/SwitchConfigurator";
import { CheckboxConfigurator } from "../configurators/CheckboxConfigurator";

export const ConfiguratorsTab = () => {
  const [activeSection, setActiveSection] = useState("typography");

  const sections: SideNavigationSection[] = [
    { id: "typography", label: "Typography", icon: <Type className="w-3 h-3" /> },
    { id: "effects", label: "Effects", icon: <Sparkles className="w-3 h-3" /> },
    { id: "glass-card", label: "Glass Card", icon: <CreditCard className="w-3 h-3" /> },
    { id: "button", label: "Button", icon: <MousePointer className="w-3 h-3" /> },
    { id: "navigation", label: "Navigation", icon: <NavIcon className="w-3 h-3" /> },
    { id: "modal", label: "Modal", icon: <Square className="w-3 h-3" /> },
    { id: "form", label: "Form", icon: <FormInput className="w-3 h-3" /> },
    { id: "table", label: "Table", icon: <TableIcon className="w-3 h-3" /> },
    { id: "toggle", label: "Toggle", icon: <ToggleLeft className="w-3 h-3" /> },
    { id: "switch", label: "Switch", icon: <Power className="w-3 h-3" /> },
    { id: "checkbox", label: "Checkbox", icon: <CheckSquare className="w-3 h-3" /> },
  ];

  // Render content based on active section
  const renderContent = () => {
    switch (activeSection) {
      case "typography":
        return (
          <div>
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
              Typography Configurator
            </h2>
            <TypographyFoundation />
          </div>
        );
      case "effects":
        return (
          <div>
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
              Effects Configurator
            </h2>
            <EffectsFoundation />
          </div>
        );
      case "glass-card":
        return (
          <div>
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
              Glass Card Configurator
            </h2>
            <GlassCardConfigurator />
          </div>
        );
      case "button":
        return (
          <div>
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
              Button Configurator
            </h2>
            <ButtonConfigurator />
          </div>
        );
      case "navigation":
        return (
          <div>
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
              Navigation Configurator
            </h2>
            <NavigationPattern />
          </div>
        );
      case "modal":
        return (
          <div>
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
              Modal Configurator
            </h2>
            <ModalConfigurator />
          </div>
        );
      case "form":
        return (
          <div>
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
              Form Configurator
            </h2>
            <FormConfigurator />
          </div>
        );
      case "table":
        return (
          <div>
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
              Table Configurator
            </h2>
            <TableConfigurator />
          </div>
        );
      case "toggle":
        return (
          <div>
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
              Toggle Configurator
            </h2>
            <ToggleConfigurator />
          </div>
        );
      case "switch":
        return (
          <div>
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
              Switch Configurator
            </h2>
            <SwitchConfigurator />
          </div>
        );
      case "checkbox":
        return (
          <div>
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
              Checkbox Configurator
            </h2>
            <CheckboxConfigurator />
          </div>
        );
      default:
        return (
          <div>
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
              Glass Card Configurator
            </h2>
            <GlassCardConfigurator />
          </div>
        );
    }
  };

  return (
    <div className="flex gap-6">
      {/* Side Navigation */}
      <SideNavigation
        sections={sections}
        activeSection={activeSection}
        onSectionClick={setActiveSection}
      />

      {/* Main Content */}
      <div className="flex-1 max-w-5xl">{renderContent()}</div>
    </div>
  );
};
