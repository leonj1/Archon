import { useState } from 'react';
import { Card } from '@/features/ui/primitives/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/features/ui/primitives/select';
import { CodeDisplay } from '../shared/CodeDisplay';
import { cn } from '@/features/ui/primitives/styles';

// Simplified spacing scale
const SPACING_VALUES = [
  { name: '1', pixels: '4px', value: '0.25rem' },
  { name: '2', pixels: '8px', value: '0.5rem' },
  { name: '3', pixels: '12px', value: '0.75rem' },
  { name: '4', pixels: '16px', value: '1rem' },
  { name: '6', pixels: '24px', value: '1.5rem' },
  { name: '8', pixels: '32px', value: '2rem' },
  { name: '12', pixels: '48px', value: '3rem' },
  { name: '16', pixels: '64px', value: '4rem' },
  { name: '20', pixels: '80px', value: '5rem' },
  { name: '24', pixels: '96px', value: '6rem' }
];

const SPACING_TYPES = [
  { name: 'Padding', prefix: 'p' },
  { name: 'Margin', prefix: 'm' },
  { name: 'Gap', prefix: 'gap' },
  { name: 'Space Y', prefix: 'space-y' },
  { name: 'Space X', prefix: 'space-x' }
];

export const SpacingFoundation = () => {
  const [selectedValue, setSelectedValue] = useState('4');
  const [selectedType, setSelectedType] = useState('Padding');

  const currentSpacing = SPACING_VALUES.find(s => s.name === selectedValue);
  const currentType = SPACING_TYPES.find(t => t.name === selectedType);

  const generateCode = () => {
    if (!currentSpacing || !currentType) return '';

    const className = `${currentType.prefix}-${selectedValue}`;
    const pixelValue = currentSpacing.pixels;
    const remValue = currentSpacing.value;

    return `// ${selectedType} with ${pixelValue} spacing
<div className="${className}">
  Content with ${selectedType.toLowerCase()} of ${pixelValue}
</div>

// Values:
// ${className} = ${remValue} (${pixelValue})`;
  };

  const renderDemo = () => {
    if (!currentSpacing || !currentType) return null;

    const className = `${currentType.prefix}-${selectedValue}`;

    switch (selectedType) {
      case 'Padding':
        return (
          <div className="border-2 border-dashed border-gray-300 dark:border-gray-600">
            <div className={cn(className, 'bg-cyan-100 dark:bg-cyan-900/30')}>
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded text-center py-4">
                Content with {currentSpacing.pixels} padding
              </div>
            </div>
          </div>
        );

      case 'Margin':
        return (
          <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 p-4">
            <div className={cn(className, 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded text-center py-4 bg-cyan-100 dark:bg-cyan-900/30')}>
              Content with {currentSpacing.pixels} margin
            </div>
          </div>
        );

      case 'Gap':
        return (
          <div className={cn('flex', className)}>
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="w-20 h-16 bg-cyan-100 dark:bg-cyan-900/30 border border-gray-200 dark:border-gray-700 rounded flex items-center justify-center text-sm"
              >
                Item {i}
              </div>
            ))}
          </div>
        );

      case 'Space Y':
        return (
          <div className={cn('space-y-' + selectedValue)}>
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="w-full h-12 bg-cyan-100 dark:bg-cyan-900/30 border border-gray-200 dark:border-gray-700 rounded flex items-center justify-center text-sm"
              >
                Item {i}
              </div>
            ))}
          </div>
        );

      case 'Space X':
        return (
          <div className={cn('flex space-x-' + selectedValue)}>
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="w-20 h-16 bg-cyan-100 dark:bg-cyan-900/30 border border-gray-200 dark:border-gray-700 rounded flex items-center justify-center text-sm"
              >
                Item {i}
              </div>
            ))}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Spacing System</h2>
        <p className="text-gray-600 dark:text-gray-400 text-lg">
          Interactive spacing scale explorer
        </p>
      </div>

      {/* Spacing Explorer - Above the Fold */}
      <Card className="p-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: Controls */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Spacing Type</label>
              <Select value={selectedType} onValueChange={setSelectedType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {SPACING_TYPES.map((type) => (
                    <SelectItem key={type.name} value={type.name}>
                      {type.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Spacing Value</label>
              <Select value={selectedValue} onValueChange={setSelectedValue}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {SPACING_VALUES.map((spacing) => (
                    <SelectItem key={spacing.name} value={spacing.name}>
                      {spacing.name} ({spacing.pixels})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Current Selection Info */}
            <div className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg text-sm">
              <div className="font-medium text-gray-900 dark:text-white">
                {currentType?.prefix}-{selectedValue}
              </div>
              <div className="text-gray-600 dark:text-gray-400">
                {currentSpacing?.pixels} • {currentSpacing?.value}
              </div>
            </div>
          </div>

          {/* Center: Live Demo */}
          <div className="flex items-center justify-center">
            <div className="w-full max-w-xs">
              {renderDemo()}
            </div>
          </div>

          {/* Right: Spacing Scale */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-900 dark:text-white">Spacing Scale</h4>
            <div className="space-y-2">
              {SPACING_VALUES.map((spacing) => (
                <div
                  key={spacing.name}
                  className={cn(
                    "flex items-center justify-between p-2 rounded cursor-pointer transition-colors",
                    selectedValue === spacing.name
                      ? "bg-cyan-500/20 border border-cyan-500"
                      : "hover:bg-gray-100 dark:hover:bg-gray-800"
                  )}
                  onClick={() => setSelectedValue(spacing.name)}
                >
                  <div className="flex items-center gap-2">
                    <div
                      className="bg-cyan-500 rounded"
                      style={{
                        width: Math.min(parseInt(spacing.pixels), 24) + 'px',
                        height: '12px'
                      }}
                    />
                    <span className="text-sm font-mono">{spacing.name}</span>
                  </div>
                  <span className="text-xs text-gray-500">{spacing.pixels}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Generated Code */}
        <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Generated Code</h4>
          <CodeDisplay
            code={generateCode()}
            showLineNumbers={false}
          />
        </div>
      </Card>
    </div>
  );
};