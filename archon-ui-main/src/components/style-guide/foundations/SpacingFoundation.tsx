import { Card } from '@/features/ui/primitives/card';
import { CodeDisplay } from '../shared/CodeDisplay';
import { cn } from '@/features/ui/primitives/styles';

interface SpacingScale {
  name: string;
  value: string;
  pixels: string;
  usage: string;
  tailwindClass: string;
}

const SPACING_SCALE: SpacingScale[] = [
  {
    name: 'xs',
    value: '0.125rem',
    pixels: '2px',
    usage: 'Minimal spacing, fine adjustments',
    tailwindClass: '0.5'
  },
  {
    name: 'sm',
    value: '0.25rem',
    pixels: '4px',
    usage: 'Small gaps, tight layouts',
    tailwindClass: '1'
  },
  {
    name: 'md',
    value: '0.5rem',
    pixels: '8px',
    usage: 'Default small spacing',
    tailwindClass: '2'
  },
  {
    name: 'lg',
    value: '0.75rem',
    pixels: '12px',
    usage: 'Medium spacing between elements',
    tailwindClass: '3'
  },
  {
    name: 'xl',
    value: '1rem',
    pixels: '16px',
    usage: 'Standard spacing unit',
    tailwindClass: '4'
  },
  {
    name: '2xl',
    value: '1.25rem',
    pixels: '20px',
    usage: 'Comfortable spacing',
    tailwindClass: '5'
  },
  {
    name: '3xl',
    value: '1.5rem',
    pixels: '24px',
    usage: 'Large spacing between sections',
    tailwindClass: '6'
  },
  {
    name: '4xl',
    value: '2rem',
    pixels: '32px',
    usage: 'Extra large spacing',
    tailwindClass: '8'
  },
  {
    name: '5xl',
    value: '2.5rem',
    pixels: '40px',
    usage: 'Section dividers',
    tailwindClass: '10'
  },
  {
    name: '6xl',
    value: '3rem',
    pixels: '48px',
    usage: 'Major section spacing',
    tailwindClass: '12'
  }
];

const LAYOUT_SPACING = [
  {
    name: 'Component Padding',
    small: 'p-4 (1rem)',
    medium: 'p-6 (1.5rem)',
    large: 'p-8 (2rem)',
    usage: 'Internal spacing within cards and containers'
  },
  {
    name: 'Element Gaps',
    small: 'gap-2 (0.5rem)',
    medium: 'gap-4 (1rem)',
    large: 'gap-6 (1.5rem)',
    usage: 'Spacing between elements in flex/grid layouts'
  },
  {
    name: 'Section Margins',
    small: 'mb-4 (1rem)',
    medium: 'mb-6 (1.5rem)',
    large: 'mb-8 (2rem)',
    usage: 'Vertical spacing between page sections'
  },
  {
    name: 'Content Margins',
    small: 'mx-4 (1rem)',
    medium: 'mx-6 (1.5rem)',
    large: 'mx-8 (2rem)',
    usage: 'Horizontal margins for content containers'
  }
];

const generateCode = () => {
  return `/**
 * 🤖 AI CONTEXT: Spacing System
 *
 * PURPOSE: Consistent spacing throughout the application
 * WHEN TO USE: All layouts should use the standardized spacing scale
 * WHEN NOT TO USE: Never hardcode spacing values, always use Tailwind classes
 *
 * SPACING SCALE:
 * - 0.5 (2px): Minimal adjustments, fine-tuning
 * - 1 (4px): Small gaps in tight layouts
 * - 2 (8px): Default small spacing
 * - 3 (12px): Medium element spacing
 * - 4 (16px): Standard spacing unit (base)
 * - 5 (20px): Comfortable spacing
 * - 6 (24px): Large spacing between sections
 * - 8 (32px): Extra large spacing
 * - 10 (40px): Section dividers
 * - 12 (48px): Major section spacing
 *
 * LAYOUT PATTERNS:
 * - Card padding: p-4 (small), p-6 (medium), p-8 (large)
 * - Element gaps: gap-2 (tight), gap-4 (standard), gap-6 (loose)
 * - Section margins: mb-4 (small), mb-6 (medium), mb-8 (large)
 * - Page margins: mx-4 (mobile), mx-6 (tablet), mx-8 (desktop)
 *
 * RESPONSIVE SPACING:
 * - Use responsive variants: p-4 md:p-6 lg:p-8
 * - Scale up spacing on larger screens for better proportions
 * - Maintain readability and visual hierarchy across devices
 */

// Padding Examples
<div className="p-4">Small padding (16px)</div>
<div className="p-6">Medium padding (24px)</div>
<div className="p-8">Large padding (32px)</div>

// Margin Examples
<div className="mb-4">Small bottom margin (16px)</div>
<div className="mb-6">Medium bottom margin (24px)</div>
<div className="mb-8">Large bottom margin (32px)</div>

// Gap Examples (Flexbox/Grid)
<div className="flex gap-2">Tight gap (8px)</div>
<div className="flex gap-4">Standard gap (16px)</div>
<div className="flex gap-6">Loose gap (24px)</div>

// Responsive Spacing
<div className="p-4 md:p-6 lg:p-8">Responsive padding</div>
<div className="space-y-4 md:space-y-6">Responsive vertical spacing</div>`;
};

export const SpacingFoundation = () => {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-4">Spacing System</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Consistent spacing scale for layouts, components, and content organization.
        </p>
      </div>

      {/* Spacing Scale */}
      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Spacing Scale</h3>
        <div className="space-y-4">
          {SPACING_SCALE.map((spacing) => (
            <div key={spacing.name} className="flex items-center justify-between border-b border-gray-200 dark:border-gray-700 pb-4 last:border-b-0">
              <div className="flex items-center space-x-6">
                <div className="w-20 text-sm font-medium">
                  {spacing.name}
                </div>
                <div className="flex items-center space-x-2">
                  <div
                    className="bg-cyan-500"
                    style={{
                      width: spacing.pixels,
                      height: '20px'
                    }}
                  />
                  <span className="text-xs text-gray-500 dark:text-gray-400 w-12">
                    {spacing.pixels}
                  </span>
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 min-w-[100px]">
                  {spacing.value}
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-xs font-mono bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                  {spacing.tailwindClass}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400 max-w-[200px]">
                  {spacing.usage}
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Layout Spacing Patterns */}
      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Layout Patterns</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {LAYOUT_SPACING.map((pattern) => (
            <div key={pattern.name} className="space-y-3">
              <h4 className="font-medium text-gray-900 dark:text-gray-100">
                {pattern.name}
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Small:</span>
                  <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-xs">
                    {pattern.small}
                  </code>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Medium:</span>
                  <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-xs">
                    {pattern.medium}
                  </code>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Large:</span>
                  <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-xs">
                    {pattern.large}
                  </code>
                </div>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {pattern.usage}
              </p>
            </div>
          ))}
        </div>
      </Card>

      {/* Visual Examples */}
      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Visual Examples</h3>

        {/* Padding Examples */}
        <div className="space-y-6">
          <div>
            <h4 className="text-sm font-medium mb-3 text-gray-700 dark:text-gray-300">Padding Examples</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {['p-4', 'p-6', 'p-8'].map((padding) => (
                <div key={padding} className="space-y-2">
                  <div className="text-xs font-mono bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded inline-block">
                    {padding}
                  </div>
                  <div className="border-2 border-dashed border-gray-300 dark:border-gray-600">
                    <div className={cn(padding, 'bg-cyan-100 dark:bg-cyan-900/30')}>
                      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded text-center text-xs py-2">
                        Content
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Gap Examples */}
          <div>
            <h4 className="text-sm font-medium mb-3 text-gray-700 dark:text-gray-300">Gap Examples</h4>
            <div className="space-y-4">
              {[
                { gap: 'gap-2', label: 'gap-2 (8px)' },
                { gap: 'gap-4', label: 'gap-4 (16px)' },
                { gap: 'gap-6', label: 'gap-6 (24px)' }
              ].map((example) => (
                <div key={example.gap} className="space-y-2">
                  <div className="text-xs font-mono bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded inline-block">
                    {example.label}
                  </div>
                  <div className={cn('flex', example.gap)}>
                    {[1, 2, 3].map((i) => (
                      <div
                        key={i}
                        className="w-16 h-12 bg-cyan-100 dark:bg-cyan-900/30 border border-gray-200 dark:border-gray-700 rounded flex items-center justify-center text-xs"
                      >
                        {i}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {/* Usage Code */}
      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Usage Code</h3>
        <CodeDisplay
          code={generateCode()}
          
          showLineNumbers
        />
      </Card>
    </div>
  );
};