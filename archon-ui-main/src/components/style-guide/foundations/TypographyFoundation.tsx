import { Card } from '@/features/ui/primitives/card';
import { CodeDisplay } from '../shared/CodeDisplay';
import { cn } from '@/features/ui/primitives/styles';

interface TypographyStyle {
  name: string;
  className: string;
  size: string;
  weight: string;
  usage: string;
  example: string;
}

const HEADING_STYLES: TypographyStyle[] = [
  {
    name: 'Display Large',
    className: 'text-4xl md:text-5xl lg:text-6xl font-bold',
    size: '3.75rem / 4rem / 4.5rem',
    weight: '700',
    usage: 'Hero headings, landing page titles',
    example: 'Hero Title'
  },
  {
    name: 'Display Medium',
    className: 'text-3xl md:text-4xl font-bold',
    size: '1.875rem / 2.25rem',
    weight: '700',
    usage: 'Page titles, section headers',
    example: 'Page Title'
  },
  {
    name: 'Heading 1',
    className: 'text-2xl font-bold',
    size: '1.5rem',
    weight: '700',
    usage: 'Main section titles',
    example: 'Section Title'
  },
  {
    name: 'Heading 2',
    className: 'text-xl font-semibold',
    size: '1.25rem',
    weight: '600',
    usage: 'Subsection titles',
    example: 'Subsection Title'
  },
  {
    name: 'Heading 3',
    className: 'text-lg font-semibold',
    size: '1.125rem',
    weight: '600',
    usage: 'Card titles, component headers',
    example: 'Component Header'
  },
  {
    name: 'Heading 4',
    className: 'text-base font-medium',
    size: '1rem',
    weight: '500',
    usage: 'Small headings, labels',
    example: 'Label Text'
  }
];

const BODY_STYLES: TypographyStyle[] = [
  {
    name: 'Body Large',
    className: 'text-lg font-normal',
    size: '1.125rem',
    weight: '400',
    usage: 'Large body text, introductions',
    example: 'This is large body text used for introductions and important content that needs to stand out.'
  },
  {
    name: 'Body Medium',
    className: 'text-base font-normal',
    size: '1rem',
    weight: '400',
    usage: 'Standard body text, paragraphs',
    example: 'This is standard body text used for regular content, paragraphs, and general information.'
  },
  {
    name: 'Body Small',
    className: 'text-sm font-normal',
    size: '0.875rem',
    weight: '400',
    usage: 'Secondary text, descriptions',
    example: 'This is small body text used for secondary information and descriptions.'
  },
  {
    name: 'Caption',
    className: 'text-xs font-normal',
    size: '0.75rem',
    weight: '400',
    usage: 'Captions, metadata, helper text',
    example: 'This is caption text used for metadata and helper information.'
  }
];

const UTILITY_STYLES: TypographyStyle[] = [
  {
    name: 'Button Text',
    className: 'text-sm font-medium',
    size: '0.875rem',
    weight: '500',
    usage: 'Button labels, action text',
    example: 'Button Label'
  },
  {
    name: 'Code',
    className: 'text-sm font-mono bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded',
    size: '0.875rem',
    weight: '400',
    usage: 'Inline code, technical text',
    example: 'const variable = value;'
  },
  {
    name: 'Link',
    className: 'text-cyan-600 dark:text-cyan-400 hover:text-cyan-500 dark:hover:text-cyan-300 underline',
    size: 'inherit',
    weight: 'inherit',
    usage: 'Links, interactive text',
    example: 'This is a link'
  },
  {
    name: 'Muted',
    className: 'text-gray-500 dark:text-gray-400',
    size: 'inherit',
    weight: 'inherit',
    usage: 'Secondary text, disabled states',
    example: 'This is muted text'
  }
];

const COLOR_VARIATIONS = [
  {
    name: 'Primary Text',
    className: 'text-gray-900 dark:text-gray-100',
    usage: 'Main content, headings'
  },
  {
    name: 'Secondary Text',
    className: 'text-gray-700 dark:text-gray-300',
    usage: 'Body text, secondary content'
  },
  {
    name: 'Muted Text',
    className: 'text-gray-500 dark:text-gray-400',
    usage: 'Helper text, captions, disabled'
  },
  {
    name: 'Accent Text',
    className: 'text-cyan-600 dark:text-cyan-400',
    usage: 'Links, highlights, active states'
  },
  {
    name: 'Success Text',
    className: 'text-green-600 dark:text-green-400',
    usage: 'Success messages, positive states'
  },
  {
    name: 'Warning Text',
    className: 'text-orange-600 dark:text-orange-400',
    usage: 'Warning messages, caution states'
  },
  {
    name: 'Error Text',
    className: 'text-red-600 dark:text-red-400',
    usage: 'Error messages, destructive actions'
  }
];

const generateCode = () => {
  return `/**
 * 🤖 AI CONTEXT: Typography System
 *
 * PURPOSE: Consistent text styles across the application
 * WHEN TO USE: All text content should use these utility classes
 * WHEN NOT TO USE: Never hardcode font sizes, always use system classes
 *
 * HIERARCHY GUIDELINES:
 * - Display Large: Hero sections, landing pages
 * - Display Medium: Page titles, main headers
 * - Heading 1-4: Section titles, descending importance
 * - Body Large: Important content, introductions
 * - Body Medium: Standard content, paragraphs
 * - Body Small: Secondary content, descriptions
 * - Caption: Metadata, helper text, timestamps
 *
 * COLOR SEMANTIC MEANINGS:
 * - Primary: Main content, most important text
 * - Secondary: Body content, readable but less prominent
 * - Muted: Helper text, less important information
 * - Accent: Interactive elements, links, highlights
 * - Success/Warning/Error: Status-based messaging
 *
 * RESPONSIVE BEHAVIOR:
 * - Display styles scale down on smaller screens
 * - Body text maintains consistent size across devices
 * - Use responsive classes (md:, lg:) for display text
 */

// Heading Examples
<h1 className="text-2xl font-bold">Main Section Title</h1>
<h2 className="text-xl font-semibold">Subsection Title</h2>
<h3 className="text-lg font-semibold">Component Header</h3>

// Body Text Examples
<p className="text-lg font-normal">Large body text for introductions</p>
<p className="text-base font-normal">Standard body text for content</p>
<p className="text-sm font-normal">Small text for descriptions</p>

// Utility Examples
<button className="text-sm font-medium">Button Label</button>
<code className="text-sm font-mono bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded">
  code snippet
</code>
<a className="text-cyan-600 dark:text-cyan-400 hover:text-cyan-500 underline">
  Link text
</a>

// Color Variations
<span className="text-gray-900 dark:text-gray-100">Primary text</span>
<span className="text-gray-500 dark:text-gray-400">Muted text</span>
<span className="text-cyan-600 dark:text-cyan-400">Accent text</span>`;
};

export const TypographyFoundation = () => {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Typography System</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Consistent typography scale and styles for clear content hierarchy and optimal readability.
        </p>
      </div>

      {/* Heading Styles */}
      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Headings</h3>
        <div className="space-y-6">
          {HEADING_STYLES.map((style) => (
            <div key={style.name} className="border-b border-gray-200 dark:border-gray-700 pb-4 last:border-b-0">
              <div className={cn(style.className, 'mb-2')}>
                {style.example}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-gray-600 dark:text-gray-400">
                <div>
                  <span className="font-medium">Style:</span> {style.name}
                </div>
                <div>
                  <span className="font-medium">Size:</span> {style.size}
                </div>
                <div>
                  <span className="font-medium">Usage:</span> {style.usage}
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Body Styles */}
      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Body Text</h3>
        <div className="space-y-6">
          {BODY_STYLES.map((style) => (
            <div key={style.name} className="border-b border-gray-200 dark:border-gray-700 pb-4 last:border-b-0">
              <div className={cn(style.className, 'mb-2')}>
                {style.example}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-gray-600 dark:text-gray-400">
                <div>
                  <span className="font-medium">Style:</span> {style.name}
                </div>
                <div>
                  <span className="font-medium">Size:</span> {style.size}
                </div>
                <div>
                  <span className="font-medium">Usage:</span> {style.usage}
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Utility Styles */}
      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Utility Styles</h3>
        <div className="space-y-6">
          {UTILITY_STYLES.map((style) => (
            <div key={style.name} className="border-b border-gray-200 dark:border-gray-700 pb-4 last:border-b-0">
              <div className={cn(style.className, 'mb-2')}>
                {style.example}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-gray-600 dark:text-gray-400">
                <div>
                  <span className="font-medium">Style:</span> {style.name}
                </div>
                <div>
                  <span className="font-medium">Weight:</span> {style.weight}
                </div>
                <div>
                  <span className="font-medium">Usage:</span> {style.usage}
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Color Variations */}
      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Text Colors</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {COLOR_VARIATIONS.map((color) => (
            <div key={color.name} className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
              <div>
                <div className={cn(color.className, 'text-base font-medium mb-1')}>
                  {color.name}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {color.usage}
                </div>
              </div>
              <div className="text-xs font-mono text-gray-400 dark:text-gray-500">
                {color.className.split(' ')[0]}
              </div>
            </div>
          ))}
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