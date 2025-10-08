import { useState } from 'react';
import { Card } from '@/features/ui/primitives/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/features/ui/primitives/select';
import { CodeDisplay } from '../shared/CodeDisplay';
import { cn } from '@/features/ui/primitives/styles';

// Typography scale
const TYPOGRAPHY_SCALE = [
  { name: 'Display', className: 'text-4xl md:text-5xl font-bold', example: 'Hero Title' },
  { name: 'H1', className: 'text-3xl font-bold', example: 'Page Title' },
  { name: 'H2', className: 'text-2xl font-bold', example: 'Section Title' },
  { name: 'H3', className: 'text-xl font-semibold', example: 'Subsection Title' },
  { name: 'H4', className: 'text-lg font-semibold', example: 'Component Header' },
  { name: 'Body Large', className: 'text-lg font-normal', example: 'Large body text for important content' },
  { name: 'Body', className: 'text-base font-normal', example: 'Standard body text for regular content' },
  { name: 'Body Small', className: 'text-sm font-normal', example: 'Small text for descriptions' },
  { name: 'Caption', className: 'text-xs font-normal', example: 'Caption and metadata text' },
  { name: 'Button', className: 'text-sm font-medium', example: 'Button Label' },
  { name: 'Code', className: 'text-sm font-mono', example: 'const variable = value;' }
];

// Color variations
const TEXT_COLORS = [
  { name: 'Primary', className: 'text-gray-900 dark:text-gray-100' },
  { name: 'Secondary', className: 'text-gray-700 dark:text-gray-300' },
  { name: 'Muted', className: 'text-gray-500 dark:text-gray-400' },
  { name: 'Accent', className: 'text-cyan-500' },
  { name: 'Success', className: 'text-emerald-500' },
  { name: 'Warning', className: 'text-orange-500' },
  { name: 'Error', className: 'text-red-500' }
];

export const TypographyFoundation = () => {
  const [selectedColor, setSelectedColor] = useState('Primary');
  const [selectedType, setSelectedType] = useState('H1');

  const currentColorClass = TEXT_COLORS.find(color => color.name === selectedColor)?.className || 'text-gray-900 dark:text-gray-100';

  const generateCode = () => {
    const selectedTypeData = TYPOGRAPHY_SCALE.find(type => type.name === selectedType);
    const selectedColorData = TEXT_COLORS.find(color => color.name === selectedColor);

    if (!selectedTypeData || !selectedColorData) return '';

    const className = selectedColorData.name === 'Primary'
      ? selectedTypeData.className
      : `${selectedTypeData.className} ${selectedColorData.className}`;

    return `// ${selectedTypeData.name} with ${selectedColorData.name} color
<${selectedType.toLowerCase().startsWith('h') ? selectedType.toLowerCase() : 'p'} className="${className}">
  ${selectedTypeData.example}
</${selectedType.toLowerCase().startsWith('h') ? selectedType.toLowerCase() : 'p'}>`;
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Typography System</h2>
        <p className="text-gray-600 dark:text-gray-400 text-lg">
          Interactive typography configurator with live examples
        </p>
      </div>

      {/* Typography Configurator */}
      <Card className="p-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left: Controls */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Typography Configurator</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Typography Style</label>
                <Select value={selectedType} onValueChange={setSelectedType}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {TYPOGRAPHY_SCALE.map((type) => (
                      <SelectItem key={type.name} value={type.name}>
                        {type.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Text Color</label>
                <Select value={selectedColor} onValueChange={setSelectedColor}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {TEXT_COLORS.map((color) => (
                      <SelectItem key={color.name} value={color.name}>
                        {color.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Current Selection */}
              <div className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                <div className="font-medium text-sm">Current Selection</div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  {selectedType} • {selectedColor}
                </div>
                <div className="text-xs font-mono text-gray-500 mt-1">
                  {TYPOGRAPHY_SCALE.find(t => t.name === selectedType)?.className} {selectedColor !== 'Primary' ? TEXT_COLORS.find(c => c.name === selectedColor)?.className : ''}
                </div>
              </div>
            </div>
          </div>

          {/* Right: Live Examples */}
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Live Examples</h3>

            {/* Card Example */}
            <Card className="p-4">
              <div className={cn(TYPOGRAPHY_SCALE.find(t => t.name === selectedType)?.className, currentColorClass)}>
                Sample {selectedType} Text
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                This is how your typography appears in a card component
              </div>
            </Card>

            {/* Code Example */}
            <Card className="p-4 bg-gray-900 dark:bg-gray-950">
              <div className="text-green-400 text-xs font-mono mb-1">// Code example</div>
              <div className={cn(TYPOGRAPHY_SCALE.find(t => t.name === selectedType)?.className, currentColorClass, 'font-mono')}>
                function example() {'{'}
              </div>
              <div className="text-gray-400 text-sm font-mono ml-4">
                console.log('Typography in code context');
              </div>
              <div className={cn(TYPOGRAPHY_SCALE.find(t => t.name === selectedType)?.className, currentColorClass, 'font-mono')}>
                {'}'}
              </div>
            </Card>

            {/* Section Example */}
            <div className="space-y-2">
              <div className={cn(TYPOGRAPHY_SCALE.find(t => t.name === selectedType)?.className, currentColorClass)}>
                Section Header Example
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                This demonstrates how the typography works as section headers with descriptions below.
              </div>
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