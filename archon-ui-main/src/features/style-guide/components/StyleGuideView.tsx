import { useState } from 'react';
import { Palette, Component, Layout, Code } from 'lucide-react';
import { PillNavigation } from '../shared/PillNavigation';
import { ThemeToggle } from '../../../components/ui/ThemeToggle';
import { GlassCardConfigurator } from '../configurators/GlassCardConfigurator';
import { ButtonConfigurator } from '../configurators/ButtonConfigurator';
import { ModalConfigurator } from '../configurators/ModalConfigurator';
import { FormConfigurator } from '../configurators/FormConfigurator';
import { TableConfigurator } from '../configurators/TableConfigurator';
import { ToggleConfigurator } from '../configurators/ToggleConfigurator';
import { SwitchConfigurator } from '../configurators/SwitchConfigurator';
import { CheckboxConfigurator } from '../configurators/CheckboxConfigurator';
import { ColorsFoundation } from '../foundations/ColorsFoundation';
import { TypographyFoundation } from '../foundations/TypographyFoundation';
import { SpacingFoundation } from '../foundations/SpacingFoundation';
import { EffectsFoundation } from '../foundations/EffectsFoundation';
import { LayoutsPattern } from '../patterns/LayoutsPattern';
import { FeedbackPattern } from '../patterns/FeedbackPattern';
import { NavigationPattern } from '../patterns/NavigationPattern';
import { DataDisplayPattern } from '../patterns/DataDisplayPattern';
import { CompositionsExample } from '../examples/CompositionsExample';
import { PagesExample } from '../examples/PagesExample';
import { WorkflowsExample } from '../examples/WorkflowsExample';
import { RAGSettingsExample } from '../examples/RAGSettingsExample';

const FOUNDATION_TABS = [
  { id: 'Colors', label: 'Colors', component: ColorsFoundation },
  { id: 'Typography', label: 'Typography', component: TypographyFoundation },
  { id: 'Spacing', label: 'Spacing', component: SpacingFoundation },
  { id: 'Effects', label: 'Effects', component: EffectsFoundation },
];

const COMPONENT_TABS = [
  { id: 'Cards', label: 'Cards', component: GlassCardConfigurator },
  { id: 'Buttons', label: 'Buttons', component: ButtonConfigurator },
  { id: 'Forms', label: 'Forms', component: FormConfigurator },
  { id: 'Tables', label: 'Tables', component: TableConfigurator },
  { id: 'Modals', label: 'Modals', component: ModalConfigurator },
  { id: 'Toggles', label: 'Toggles', component: ToggleConfigurator },
  { id: 'Switches', label: 'Switches', component: SwitchConfigurator },
  { id: 'Checkboxes', label: 'Checkboxes', component: CheckboxConfigurator },
];

const PATTERN_TABS = [
  { id: 'Layouts', label: 'Layouts', component: LayoutsPattern },
  { id: 'Feedback', label: 'Feedback', component: FeedbackPattern },
  { id: 'Navigation', label: 'Navigation', component: NavigationPattern },
  { id: 'Data Display', label: 'Data Display', component: DataDisplayPattern },
];

const EXAMPLE_TABS = [
  { id: 'Compositions', label: 'Compositions', component: CompositionsExample },
  { id: 'Pages', label: 'Pages', component: PagesExample },
  { id: 'Workflows', label: 'Workflows', component: WorkflowsExample },
  { id: 'RAG Settings', label: 'RAG Settings', component: RAGSettingsExample },
];

export const StyleGuideView = () => {
  const [selectedSection, setSelectedSection] = useState('foundations');
  const [selectedComponent, setSelectedComponent] = useState<string | null>('Colors');

  const handleSectionChange = (section: string) => {
    setSelectedSection(section);
    // Reset to first item of new section
    if (section === 'foundations') setSelectedComponent('Colors');
    else if (section === 'components') setSelectedComponent('Cards');
    else if (section === 'patterns') setSelectedComponent('Layouts');
    else if (section === 'examples') setSelectedComponent('Compositions');
    else setSelectedComponent(null);
  };

  const renderContent = () => {
    if (selectedSection === 'foundations' && selectedComponent) {
      const tab = FOUNDATION_TABS.find(t => t.id === selectedComponent);
      if (tab) {
        const FoundationComponent = tab.component;
        return <FoundationComponent />;
      }
    }

    if (selectedSection === 'components' && selectedComponent) {
      const tab = COMPONENT_TABS.find(t => t.id === selectedComponent);
      if (tab) {
        const ComponentConfigurator = tab.component;
        return <ComponentConfigurator />;
      }
    }

    if (selectedSection === 'patterns' && selectedComponent) {
      const tab = PATTERN_TABS.find(t => t.id === selectedComponent);
      if (tab) {
        const PatternComponent = tab.component;
        return <PatternComponent />;
      }
    }

    if (selectedSection === 'examples' && selectedComponent) {
      const tab = EXAMPLE_TABS.find(t => t.id === selectedComponent);
      if (tab) {
        const ExampleComponent = tab.component;
        return <ExampleComponent />;
      }
    }

    // Default content for other sections or no selection
    const sectionContent = {
      foundations: { icon: <Palette className="w-16 h-16 mx-auto mb-4 opacity-50" />, text: "Select a foundation element from the dropdown above" },
      components: { icon: <Component className="w-16 h-16 mx-auto mb-4 opacity-50" />, text: "Select a component from the dropdown above" },
      patterns: { icon: <Layout className="w-16 h-16 mx-auto mb-4 opacity-50" />, text: "Select a pattern from the dropdown above" },
      examples: { icon: <Code className="w-16 h-16 mx-auto mb-4 opacity-50" />, text: "Select an example from the dropdown above" }
    };

    const content = sectionContent[selectedSection as keyof typeof sectionContent];

    return (
      <div className="text-center py-16 text-gray-500 dark:text-gray-400">
        {content.icon}
        <p>{content.text}</p>
      </div>
    );
  };

  return (
    <div className="space-y-12">
      {/* Header */}
      <div className="relative">
        {/* Theme Toggle in top right */}
        <div className="absolute top-0 right-0">
          <ThemeToggle accentColor="blue" />
        </div>

        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">Interactive Style Guide</h1>
          <p className="text-gray-600 dark:text-gray-400 text-lg max-w-2xl mx-auto">
            Configure and preview Archon's glassmorphism components with live code generation.
          </p>
        </div>
      </div>

      {/* Pill Navigation */}
      <div className="flex justify-center">
        <PillNavigation
          selectedSection={selectedSection}
          selectedItem={selectedComponent}
          onSectionChange={handleSectionChange}
          onItemChange={setSelectedComponent}
        />
      </div>

      {/* Content */}
      <div>
        {renderContent()}
      </div>
    </div>
  );
};