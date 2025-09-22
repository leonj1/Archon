import { Card } from '@/features/ui/primitives/card';
import { CodeDisplay } from '../shared/CodeDisplay';

export const WorkflowsExample = () => {
  const generateCode = () => {
    return `/**
 * 🤖 AI CONTEXT: User Workflow Examples
 *
 * PURPOSE: Multi-step user flows using Archon components
 * WHEN TO USE: Complex user journeys requiring multiple screens
 * WHEN NOT TO USE: Simple single-page interactions
 *
 * WORKFLOW TYPES:
 * - Onboarding flows with progressive disclosure
 * - Multi-step forms with validation
 * - Wizard-style configuration processes
 * - Data import/export workflows
 * - User authentication flows
 *
 * FLOW PRINCIPLES:
 * - Clear progress indication
 * - Consistent navigation patterns
 * - Proper error handling and recovery
 * - Accessible keyboard navigation
 * - Mobile-responsive design
 */

import { useState } from 'react';
import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';

// Example: Multi-step Onboarding
export const OnboardingWorkflow = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({});

  const steps = [
    { title: "Welcome", component: WelcomeStep },
    { title: "Profile", component: ProfileStep },
    { title: "Preferences", component: PreferencesStep },
    { title: "Complete", component: CompleteStep }
  ];

  const nextStep = () => setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
  const prevStep = () => setCurrentStep(prev => Math.max(prev - 1, 0));

  return (
    <div className="max-w-2xl mx-auto">
      {/* Progress Indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          {steps.map((step, index) => (
            <div
              key={step.title}
              className={cn(
                "flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium",
                index <= currentStep
                  ? "bg-cyan-500 text-white"
                  : "bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400"
              )}
            >
              {index + 1}
            </div>
          ))}
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div
            className="bg-cyan-500 h-2 rounded-full transition-all"
            style={{ width: \`\${((currentStep + 1) / steps.length) * 100}%\` }}
          />
        </div>
      </div>

      {/* Step Content */}
      <Card glowColor="purple" className="p-8 mb-6">
        <h2 className="text-2xl font-bold mb-6">{steps[currentStep].title}</h2>
        <steps[currentStep].component
          formData={formData}
          setFormData={setFormData}
        />
      </Card>

      {/* Navigation */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={prevStep}
          disabled={currentStep === 0}
        >
          Previous
        </Button>
        <Button
          onClick={nextStep}
          disabled={currentStep === steps.length - 1}
        >
          {currentStep === steps.length - 1 ? 'Complete' : 'Next'}
        </Button>
      </div>
    </div>
  );
};`;
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-4">Workflow Examples</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Multi-step user flows and complex interactions using Archon's design system.
        </p>
      </div>

      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Coming Soon</h3>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          This section will include interactive workflow examples such as:
        </p>
        <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1 mb-6">
          <li>Onboarding flows with step-by-step guidance</li>
          <li>Multi-step form wizards with validation</li>
          <li>Data import/export workflows with progress tracking</li>
          <li>User authentication flows with error handling</li>
          <li>Configuration wizards with branching logic</li>
        </ul>
      </Card>

      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Example Workflow Pattern</h3>
        <CodeDisplay
          code={generateCode()}
          
          showLineNumbers
        />
      </Card>
    </div>
  );
};