import { Card } from '@/features/ui/primitives/card';
import { CodeDisplay } from '../shared/CodeDisplay';
import { cn, glassmorphism } from '@/features/ui/primitives/styles';

interface Effect {
  name: string;
  className: string;
  description: string;
  usage: string;
}

const BLUR_EFFECTS: Effect[] = [
  {
    name: 'Backdrop Blur Small',
    className: 'backdrop-blur-sm',
    description: 'Subtle blur for lightweight overlays',
    usage: 'Light modals, hover effects, subtle overlays'
  },
  {
    name: 'Backdrop Blur Medium',
    className: 'backdrop-blur-md',
    description: 'Standard blur for glassmorphism',
    usage: 'Cards, panels, primary glassmorphism effects'
  },
  {
    name: 'Backdrop Blur Large',
    className: 'backdrop-blur-lg',
    description: 'Strong blur for prominent overlays',
    usage: 'Modals, sidebars, major overlay elements'
  },
  {
    name: 'Backdrop Blur Extra Large',
    className: 'backdrop-blur-xl',
    description: 'Maximum blur for full overlays',
    usage: 'Background overlays, page transitions'
  }
];

const SHADOW_EFFECTS: Effect[] = [
  {
    name: 'Small Shadow',
    className: glassmorphism.shadow.sm,
    description: 'Subtle elevation for small elements',
    usage: 'Buttons, small cards, minor elevation'
  },
  {
    name: 'Medium Shadow',
    className: glassmorphism.shadow.md,
    description: 'Standard elevation for cards',
    usage: 'Cards, panels, standard components'
  },
  {
    name: 'Large Shadow',
    className: glassmorphism.shadow.lg,
    description: 'Strong elevation for prominent elements',
    usage: 'Modals, floating panels, major elements'
  },
  {
    name: 'Elevated Shadow',
    className: glassmorphism.shadow.elevated,
    description: 'Maximum elevation with custom shadow',
    usage: 'Tooltips, dropdowns, floating elements'
  }
];

const GLOW_EFFECTS: Effect[] = [
  {
    name: 'Purple Glow',
    className: glassmorphism.shadow.glow.purple,
    description: 'Primary accent glow effect',
    usage: 'Primary actions, featured content'
  },
  {
    name: 'Blue Glow',
    className: glassmorphism.shadow.glow.blue,
    description: 'Information accent glow',
    usage: 'Information states, secondary actions'
  },
  {
    name: 'Green Glow',
    className: glassmorphism.shadow.glow.green,
    description: 'Success accent glow',
    usage: 'Success states, positive feedback'
  },
  {
    name: 'Red Glow',
    className: glassmorphism.shadow.glow.red,
    description: 'Danger accent glow',
    usage: 'Error states, destructive actions'
  },
  {
    name: 'Orange Glow',
    className: glassmorphism.shadow.glow.orange,
    description: 'Warning accent glow',
    usage: 'Warning states, caution indicators'
  },
  {
    name: 'Cyan Glow',
    className: glassmorphism.shadow.glow.cyan,
    description: 'Active accent glow',
    usage: 'Active states, focus indicators'
  }
];

const EDGE_EFFECTS: Effect[] = [
  {
    name: 'Top Edge Glow',
    className: glassmorphism.edgePositions.top,
    description: 'Glowing border at top edge',
    usage: 'Header cards, top navigation elements'
  },
  {
    name: 'Left Edge Glow',
    className: glassmorphism.edgePositions.left,
    description: 'Glowing border at left edge',
    usage: 'Sidebar items, left navigation'
  },
  {
    name: 'Right Edge Glow',
    className: glassmorphism.edgePositions.right,
    description: 'Glowing border at right edge',
    usage: 'Action panels, right sidebars'
  },
  {
    name: 'Bottom Edge Glow',
    className: glassmorphism.edgePositions.bottom,
    description: 'Glowing border at bottom edge',
    usage: 'Footer elements, bottom panels'
  }
];

const INTERACTIVE_EFFECTS: Effect[] = [
  {
    name: 'Hover Effect',
    className: glassmorphism.interactive.hover,
    description: 'Subtle background change on hover',
    usage: 'Interactive elements, buttons, clickable items'
  },
  {
    name: 'Active Effect',
    className: glassmorphism.interactive.active,
    description: 'Background change when pressed',
    usage: 'Button active states, pressed elements'
  },
  {
    name: 'Selected Effect',
    className: glassmorphism.interactive.selected,
    description: 'Background and text change when selected',
    usage: 'Selected items, active navigation'
  },
  {
    name: 'Focus Effect',
    className: glassmorphism.border.focus,
    description: 'Border and shadow change on focus',
    usage: 'Form inputs, keyboard navigation'
  }
];

const generateCode = () => {
  return `import { glassmorphism } from '@/features/ui/primitives/styles';

/**
 * 🤖 AI CONTEXT: Glassmorphism Effects System
 *
 * PURPOSE: Consistent visual effects for the Tron-inspired design
 * WHEN TO USE: Layer effects to create depth and visual hierarchy
 * WHEN NOT TO USE: Don't over-layer effects (max 3 layers)
 *
 * EFFECT HIERARCHY:
 * 1. Backdrop Blur: Creates the "glass" foundation
 * 2. Background: Adds subtle color and opacity
 * 3. Border: Defines edges and focus states
 * 4. Shadow/Glow: Adds depth and accent colors
 * 5. Interactive: Responds to user actions
 *
 * LAYERING GUIDELINES:
 * - Always start with backdrop-blur for glassmorphism
 * - Add background for subtle color tinting
 * - Use borders for definition and focus
 * - Apply shadows for elevation
 * - Add glow effects for accent and attention
 * - Include interactive states for usability
 *
 * PERFORMANCE CONSIDERATIONS:
 * - Backdrop blur is expensive, use sparingly
 * - Limit glow effects to 2-3 per view
 * - Use transform3d for smooth animations
 * - Prefer opacity changes over color changes
 */

// Basic Glassmorphism Card
<div className={cn(
  "backdrop-blur-md",                    // Glass effect
  glassmorphism.background.card,         // Subtle background
  glassmorphism.border.default,          // Border definition
  glassmorphism.shadow.md,               // Standard elevation
  "rounded-lg transition-all duration-300" // Shape and animation
)}>
  Standard glassmorphism card
</div>

// Accented Card with Glow
<div className={cn(
  "backdrop-blur-md",
  glassmorphism.background.card,
  glassmorphism.border.cyan,
  glassmorphism.shadow.glow.purple,      // Accent glow
  glassmorphism.edgePositions.top,       // Edge accent
  "rounded-lg"
)}>
  Accented card with purple glow
</div>

// Interactive Button
<button className={cn(
  "backdrop-blur-sm",
  glassmorphism.background.subtle,
  glassmorphism.border.default,
  glassmorphism.interactive.hover,       // Hover state
  glassmorphism.interactive.active,      // Active state
  glassmorphism.border.focus,            // Focus state
  "px-4 py-2 rounded-md transition-all"
)}>
  Interactive glassmorphism button
</button>

// Floating Panel
<div className={cn(
  "backdrop-blur-lg",                    // Strong blur
  glassmorphism.background.strong,       // High opacity
  glassmorphism.border.default,
  glassmorphism.shadow.elevated,         // Maximum elevation
  "rounded-xl p-6"
)}>
  Floating panel with strong effects
</div>`;
};

const EffectDemo = ({ effect, showBackground = false }: { effect: Effect; showBackground?: boolean }) => (
  <div className="space-y-2">
    <div className="relative h-24 rounded-lg overflow-hidden">
      {showBackground && (
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500 via-cyan-500 to-blue-500 opacity-30" />
      )}
      <div
        className={cn(
          'absolute inset-4 rounded-lg flex items-center justify-center text-sm font-medium',
          glassmorphism.background.card,
          glassmorphism.border.default,
          effect.className
        )}
      >
        {effect.name}
      </div>
    </div>
    <div className="text-xs">
      <p className="font-medium text-gray-900 dark:text-gray-100">{effect.description}</p>
      <p className="text-gray-600 dark:text-gray-400 mt-1">{effect.usage}</p>
    </div>
  </div>
);

export const EffectsFoundation = () => {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-4">Effects System</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Glassmorphism effects including blur, shadows, glows, and interactive states for the Tron-inspired design.
        </p>
      </div>

      {/* Blur Effects */}
      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Backdrop Blur Effects</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {BLUR_EFFECTS.map((effect) => (
            <EffectDemo key={effect.name} effect={effect} showBackground />
          ))}
        </div>
      </Card>

      {/* Shadow Effects */}
      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Shadow Effects</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {SHADOW_EFFECTS.map((effect) => (
            <EffectDemo key={effect.name} effect={effect} />
          ))}
        </div>
      </Card>

      {/* Glow Effects */}
      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Glow Effects</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {GLOW_EFFECTS.map((effect) => (
            <EffectDemo key={effect.name} effect={effect} />
          ))}
        </div>
      </Card>

      {/* Edge Effects */}
      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Edge Glow Effects</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {EDGE_EFFECTS.map((effect) => (
            <EffectDemo key={effect.name} effect={effect} />
          ))}
        </div>
      </Card>

      {/* Interactive Effects */}
      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Interactive Effects</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {INTERACTIVE_EFFECTS.map((effect) => (
            <div key={effect.name} className="space-y-2">
              <div
                className={cn(
                  'h-24 rounded-lg flex items-center justify-center text-sm font-medium cursor-pointer',
                  glassmorphism.background.card,
                  glassmorphism.border.default,
                  glassmorphism.shadow.md,
                  effect.className,
                  'transition-all duration-200'
                )}
              >
                {effect.name}
              </div>
              <div className="text-xs">
                <p className="font-medium text-gray-900 dark:text-gray-100">{effect.description}</p>
                <p className="text-gray-600 dark:text-gray-400 mt-1">{effect.usage}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Layered Example */}
      <Card className="p-6 max-w-none">
        <h3 className="text-lg font-semibold mb-4">Layered Effects Example</h3>
        <div className="relative h-48 rounded-lg overflow-hidden">
          {/* Background gradient */}
          <div className="absolute inset-0 bg-gradient-to-br from-purple-500 via-cyan-500 to-blue-500 opacity-30" />

          {/* Multiple layered elements */}
          <div className={cn(
            'absolute top-8 left-8 right-8 h-32 rounded-lg',
            'backdrop-blur-md',
            glassmorphism.background.card,
            glassmorphism.border.cyan,
            glassmorphism.shadow.glow.purple,
            glassmorphism.edgePositions.top,
            'flex items-center justify-center font-medium'
          )}>
            Complete Glassmorphism Effect
            <div className="absolute top-2 right-2 text-xs text-gray-500 dark:text-gray-400">
              Blur + Background + Border + Glow + Edge
            </div>
          </div>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-4">
          This example combines multiple effects: backdrop blur, glassmorphism background,
          colored border, purple glow shadow, and top edge glow for a complete Tron-inspired effect.
        </p>
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