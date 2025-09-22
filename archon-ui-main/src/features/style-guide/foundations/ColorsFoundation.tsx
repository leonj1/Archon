import { Card } from '@/features/ui/primitives/card';
import { CodeDisplay } from '../shared/CodeDisplay';

// Colored glass cards (tinted glass, no glow)
const GLASS_TINT_COLORS = [
  {
    name: 'Clear Glass',
    glassTint: 'none' as const,
    transparency: 'light' as const,
    description: 'Pure transparent glass',
    usage: 'Default containers, neutral elements'
  },
  {
    name: 'Purple Glass',
    glassTint: 'purple' as const,
    transparency: 'medium' as const,
    description: 'Purple-tinted transparent glass',
    usage: 'Primary content areas'
  },
  {
    name: 'Blue Glass',
    glassTint: 'blue' as const,
    transparency: 'medium' as const,
    description: 'Blue-tinted transparent glass',
    usage: 'Informational panels'
  },
  {
    name: 'Cyan Glass',
    glassTint: 'cyan' as const,
    transparency: 'medium' as const,
    description: 'Cyan-tinted transparent glass',
    usage: 'Active/selected states'
  },
  {
    name: 'Green Glass',
    glassTint: 'green' as const,
    transparency: 'medium' as const,
    description: 'Green-tinted transparent glass',
    usage: 'Success messages'
  },
  {
    name: 'Orange Glass',
    glassTint: 'orange' as const,
    transparency: 'medium' as const,
    description: 'Orange-tinted transparent glass',
    usage: 'Warning notifications'
  }
];

// Neon glow cards (backlight effect)
const NEON_GLOW_COLORS = [
  {
    name: 'Purple Glow',
    glowColor: 'purple' as const,
    transparency: 'light' as const,
    description: 'Glass with purple neon backlight',
    usage: 'Featured content, primary CTAs'
  },
  {
    name: 'Blue Glow',
    glowColor: 'blue' as const,
    transparency: 'light' as const,
    description: 'Glass with blue neon backlight',
    usage: 'Information highlights'
  },
  {
    name: 'Cyan Glow',
    glowColor: 'cyan' as const,
    transparency: 'light' as const,
    description: 'Glass with cyan neon backlight',
    usage: 'Tron-style emphasis'
  },
  {
    name: 'Green Glow',
    glowColor: 'green' as const,
    transparency: 'light' as const,
    description: 'Glass with green neon backlight',
    usage: 'Success states'
  },
  {
    name: 'Red Glow',
    glowColor: 'red' as const,
    transparency: 'light' as const,
    description: 'Glass with red neon backlight',
    usage: 'Errors and critical alerts'
  },
  {
    name: 'Pink Glow',
    glowColor: 'pink' as const,
    transparency: 'light' as const,
    description: 'Glass with pink neon backlight',
    usage: 'Special features'
  }
];

// Transparency levels
const TRANSPARENCY_LEVELS = [
  { level: 'clear' as const, name: 'Clear', description: 'Almost invisible' },
  { level: 'light' as const, name: 'Light', description: 'Subtle frosting' },
  { level: 'medium' as const, name: 'Medium', description: 'Standard glass' },
  { level: 'frosted' as const, name: 'Frosted', description: 'Heavy frosting' },
  { level: 'solid' as const, name: 'Solid', description: 'Nearly opaque' }
];

const generateCode = () => {
  return `import { Card } from '@/features/ui/primitives/card';

/**
 * 🤖 AI CONTEXT: Glass Card System
 *
 * Three independent properties for maximum flexibility:
 *
 * 1. TRANSPARENCY - How much you can see through the glass
 *    - clear: Almost invisible (0.01 opacity)
 *    - light: Subtle frosting (0.05 opacity)
 *    - medium: Standard glass (0.08 opacity)
 *    - frosted: Heavy frosting (0.12 opacity)
 *    - solid: Nearly opaque (0.20 opacity)
 *
 * 2. GLASS TINT - Adds color to the glass itself
 *    - none: Pure transparent
 *    - purple/blue/cyan/green/orange/pink/red: Colored glass
 *
 * 3. GLOW COLOR - Neon backlight effect
 *    - none: No glow
 *    - purple/blue/cyan/green/orange/pink/red: Neon glow
 *
 * USAGE PATTERNS:
 * - Default containers: transparency="light" glassTint="none"
 * - Colored sections: transparency="medium" glassTint="blue"
 * - Featured content: transparency="light" glowColor="purple"
 * - Layered UI: Use different transparency levels for depth
 */

// Basic transparent glass
<Card transparency="light">
  Pure glass effect
</Card>

// Colored glass (tinted)
<Card transparency="medium" glassTint="blue">
  Blue-tinted glass
</Card>

// Glass with neon glow
<Card transparency="light" glowColor="purple">
  Glass with purple backlight
</Card>

// Combined: Colored glass with glow
<Card transparency="medium" glassTint="cyan" glowColor="cyan">
  Cyan glass with matching glow
</Card>

// Heavy frosted glass
<Card transparency="frosted" glassTint="none">
  Heavily frosted glass
</Card>`;
};

export const ColorsFoundation = () => {
  return (
    <div className="space-y-12">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Glass Card System</h2>
        <p className="text-gray-600 dark:text-gray-400 text-lg max-w-3xl mx-auto">
          True glassmorphism with independent control over transparency, tint, and neon glow effects.
        </p>
      </div>

      {/* Transparency Levels */}
      <div className="space-y-6">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white text-center">Glass Transparency Levels</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {TRANSPARENCY_LEVELS.map((item) => (
            <Card
              key={item.level}
              transparency={item.level}
              className="hover:scale-105 transition-transform duration-300"
            >
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">{item.name}</h4>
              <p className="text-gray-600 dark:text-gray-400 text-xs">{item.description}</p>
            </Card>
          ))}
        </div>
      </div>

      {/* Colored Glass (Tints) */}
      <div className="space-y-6">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white text-center">Colored Glass Tints</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {GLASS_TINT_COLORS.map((color) => (
            <Card
              key={color.name}
              glassTint={color.glassTint}
              transparency={color.transparency}
              className="hover:scale-105 transition-transform duration-300"
            >
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{color.name}</h4>
              <p className="text-gray-700 dark:text-gray-300 text-sm mb-2">{color.description}</p>
              <p className="text-gray-600 dark:text-gray-400 text-xs">{color.usage}</p>
            </Card>
          ))}
        </div>
      </div>

      {/* Neon Glow Effects */}
      <div className="space-y-6">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white text-center">Neon Backlight Glow</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {NEON_GLOW_COLORS.map((color) => (
            <Card
              key={color.name}
              glowColor={color.glowColor}
              transparency={color.transparency}
              className="hover:scale-105 transition-transform duration-300"
            >
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{color.name}</h4>
              <p className="text-gray-700 dark:text-gray-300 text-sm mb-2">{color.description}</p>
              <p className="text-gray-600 dark:text-gray-400 text-xs">{color.usage}</p>
            </Card>
          ))}
        </div>
      </div>

      {/* Combined Examples */}
      <div className="space-y-6">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white text-center">Combined Effects</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card transparency="frosted" glassTint="purple" glowColor="purple">
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Frosted Purple</h4>
            <p className="text-gray-700 dark:text-gray-300 text-sm">Heavy frosting with purple tint and glow</p>
          </Card>
          <Card transparency="clear" glassTint="none" glowColor="cyan">
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Clear with Cyan Edge</h4>
            <p className="text-gray-700 dark:text-gray-300 text-sm">Nearly invisible with cyan neon edge</p>
          </Card>
          <Card transparency="medium" glassTint="blue" glowColor="none">
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Blue Tinted Glass</h4>
            <p className="text-gray-700 dark:text-gray-300 text-sm">Medium opacity blue glass, no glow</p>
          </Card>
        </div>
      </div>

      {/* Usage Code */}
      <div className="max-w-4xl mx-auto">
        <Card className="p-6" transparency="light">
          <h3 className="text-xl font-semibold text-white mb-6 text-center">Usage Code</h3>
          <CodeDisplay
            code={generateCode()}
            showLineNumbers
          />
        </Card>
      </div>
    </div>
  );
};