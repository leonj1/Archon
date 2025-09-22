import { useState } from 'react';
import { Button } from '@/features/ui/primitives/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/features/ui/primitives/select';
import { CodeDisplay } from '../shared/CodeDisplay';
import { ConfigPanel } from '../shared/ConfigPanel';
import { ConfigRow } from '../shared/ConfigRow';
import { MODAL_TYPES } from '../standards/modalStandards';
import { Eye, Code, X } from 'lucide-react';
import type { ModalSize, GlowColor } from '../types';

export const ModalConfigurator = () => {
  const [selectedType, setSelectedType] = useState<keyof typeof MODAL_TYPES>('confirmation');
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');
  const [customSize, setCustomSize] = useState<ModalSize>('sm');
  const [customGlowColor, setCustomGlowColor] = useState<Exclude<GlowColor, 'none' | 'pink'>>('red');

  const generateCode = (type: keyof typeof MODAL_TYPES) => {

    const imports = `import { AlertDialog, AlertDialogContent, AlertDialogHeader, AlertDialogTitle, AlertDialogDescription, AlertDialogFooter, AlertDialogAction, AlertDialogCancel, AlertDialogTrigger } from '@/features/ui/primitives/alert-dialog';
import { Button } from '@/features/ui/primitives/button';`;

    const aiContext = `/**
 * 🤖 AI CONTEXT: ${type.charAt(0).toUpperCase() + type.slice(1)} Modal
 *
 * PURPOSE: ${MODAL_TYPES[type].purpose}
 * SIZE: ${customSize.toUpperCase()} - ${customSize === 'sm' ? 'Compact for simple confirmations' :
                                        customSize === 'md' ? 'Standard for forms and content' :
                                        customSize === 'lg' ? 'Large for detailed displays' :
                                        'Extra large for code/data views'}
 * GLOW: ${customGlowColor.toUpperCase()} - ${customGlowColor === 'red' ? 'Danger/destructive actions' :
                                             customGlowColor === 'green' ? 'Success/creation actions' :
                                             customGlowColor === 'blue' ? 'Information/editing' :
                                             customGlowColor === 'purple' ? 'Primary/featured content' :
                                             'Special emphasis/code display'}
 *
 * WHEN TO USE:
 * ${type === 'confirmation' ? '- Delete operations\n * - Irreversible actions\n * - Warning confirmations' :
   type === 'formCreate' ? '- Creating new resources\n * - Data entry forms\n * - Positive actions' :
   type === 'formEdit' ? '- Editing existing data\n * - Update operations\n * - Modification forms' :
   type === 'display' ? '- Showing detailed information\n * - Read-only content\n * - Feature showcases' :
   type === 'codeViewer' ? '- Code snippets display\n * - JSON/data viewing\n * - Technical content' :
   '- Application settings\n * - Configuration panels\n * - User preferences'}
 *
 * IMPLEMENTATION: Use AlertDialog for modal behavior, wrap trigger in AlertDialogTrigger
 */`;

    const component = `export const ${type.charAt(0).toUpperCase() + type.slice(1)}Modal = ({ trigger, onConfirm }) => {
  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        {trigger}
      </AlertDialogTrigger>
      <AlertDialogContent className="sm:max-w-${customSize === 'sm' ? 'sm' : customSize === 'md' ? 'md' : customSize === 'lg' ? 'lg' : 'xl'}">
        <AlertDialogHeader>
          <AlertDialogTitle>${type === 'confirmation' ? 'Confirm Action' :
                                type === 'formCreate' ? 'Create New Item' :
                                type === 'formEdit' ? 'Edit Item' :
                                type === 'display' ? 'Details' :
                                type === 'codeViewer' ? 'Code Viewer' :
                                'Settings'}</AlertDialogTitle>
          <AlertDialogDescription>
            ${MODAL_TYPES[type].purpose}
          </AlertDialogDescription>
        </AlertDialogHeader>

        {/* Modal content goes here */}

        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={onConfirm}>
            ${type === 'confirmation' ? 'Confirm' :
              type === 'formCreate' ? 'Create' :
              type === 'formEdit' ? 'Save Changes' :
              'Close'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};`;

    return `${imports}\n\n${aiContext}\n\n${component}`;
  };

  const currentConfig = MODAL_TYPES[selectedType];

  return (
    <div className="grid grid-cols-4 gap-6 h-full">
      {/* LEFT: Configuration Panel (1/4 width) */}
      <div className="col-span-1">
        <ConfigPanel title="Modal Standards">
          <div className="space-y-4">
            <ConfigRow label="Modal Type">
              <Select
                value={selectedType}
                onValueChange={(value) => setSelectedType(value as keyof typeof MODAL_TYPES)}
              >
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="confirmation">Confirmation</SelectItem>
                  <SelectItem value="formCreate">Form Create</SelectItem>
                  <SelectItem value="formEdit">Form Edit</SelectItem>
                  <SelectItem value="display">Display</SelectItem>
                  <SelectItem value="codeViewer">Code Viewer</SelectItem>
                  <SelectItem value="settings">Settings</SelectItem>
                </SelectContent>
              </Select>
            </ConfigRow>

            <ConfigRow label="Size">
              <Select
                value={customSize}
                onValueChange={(value) => setCustomSize(value as ModalSize)}
              >
                <SelectTrigger className="w-24 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sm">SM</SelectItem>
                  <SelectItem value="md">MD</SelectItem>
                  <SelectItem value="lg">LG</SelectItem>
                  <SelectItem value="xl">XL</SelectItem>
                </SelectContent>
              </Select>
            </ConfigRow>

            <ConfigRow label="Glow Color">
              <Select
                value={customGlowColor}
                onValueChange={(value) => setCustomGlowColor(value as Exclude<GlowColor, 'none' | 'pink'>)}
              >
                <SelectTrigger className="w-24 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="purple">Purple</SelectItem>
                  <SelectItem value="blue">Blue</SelectItem>
                  <SelectItem value="green">Green</SelectItem>
                  <SelectItem value="red">Red</SelectItem>
                  <SelectItem value="orange">Orange</SelectItem>
                  <SelectItem value="cyan">Cyan</SelectItem>
                </SelectContent>
              </Select>
            </ConfigRow>

            <ConfigRow label="Purpose">
              <div className="text-xs text-gray-600 dark:text-gray-400 w-32 text-right">
                {currentConfig.purpose}
              </div>
            </ConfigRow>
          </div>

          {/* Preview/Code Tabs INSIDE configurator */}
          <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex gap-2">
              <Button
                size="sm"
                variant={activeTab === 'preview' ? 'default' : 'outline'}
                onClick={() => setActiveTab('preview')}
                className="flex items-center gap-2"
              >
                <Eye className="w-4 h-4" />
                Preview
              </Button>
              <Button
                size="sm"
                variant={activeTab === 'code' ? 'default' : 'outline'}
                onClick={() => setActiveTab('code')}
                className="flex items-center gap-2"
              >
                <Code className="w-4 h-4" />
                Code
              </Button>
            </div>
          </div>
        </ConfigPanel>
      </div>

      {/* RIGHT: Preview or Code Content (3/4 width) */}
      <div className="col-span-3">
        {activeTab === 'preview' ? (
          <div className="flex items-center justify-center min-h-[400px]">
            {/* Inline Modal Preview - No Button Trigger */}
            <div className={`relative max-w-${customSize === 'sm' ? 'sm' : customSize === 'md' ? 'md' : customSize === 'lg' ? 'lg' : 'xl'} w-full mx-auto`}>
              <div className="backdrop-blur-md bg-white/95 dark:bg-gray-900/95 border border-gray-200 dark:border-gray-700 rounded-lg shadow-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">
                    {selectedType === 'confirmation' ? 'Confirm Action' :
                     selectedType === 'formCreate' ? 'Create New Item' :
                     selectedType === 'formEdit' ? 'Edit Item' :
                     selectedType === 'display' ? 'Details' :
                     selectedType === 'codeViewer' ? 'Code Viewer' :
                     'Settings'}
                  </h3>
                  <Button size="icon" variant="ghost">
                    <X className="h-4 w-4" />
                  </Button>
                </div>

                <div className="mb-4">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {currentConfig.purpose} - This is an inline preview of the {selectedType} modal type.
                  </p>
                </div>

                <div className="py-4 mb-6">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Modal content would go here. This {customSize} sized modal uses {customGlowColor} color theming.
                  </p>
                </div>

                <div className="flex justify-end gap-3">
                  <Button variant="outline">Cancel</Button>
                  <Button variant={selectedType === 'confirmation' ? 'destructive' : 'default'}>
                    {selectedType === 'confirmation' ? 'Confirm' :
                     selectedType === 'formCreate' ? 'Create' :
                     selectedType === 'formEdit' ? 'Save Changes' :
                     'Close'}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <CodeDisplay
            code={generateCode(selectedType)}
            showLineNumbers
          />
        )}
      </div>
    </div>
  );
};