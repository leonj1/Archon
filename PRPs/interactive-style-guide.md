# PRP: Interactive Style Guide Implementation

## Overview
Implement a comprehensive interactive style guide page for the Archon UI system that provides configurators for glass morphism components, standardized modal types, layout templates, and generates copy-ready code with AI-friendly documentation.

## Context for AI Implementation
This PRP provides complete implementation guidance for creating an interactive style guide at `/style-guide` route. The style guide will showcase existing Archon glass morphism components with interactive configurators, allowing developers to visually configure components and copy production-ready code.

**CRITICAL LAYOUT CONSTRAINT**: The Archon app has a fixed left navigation sidebar and potential right chat sidebar. The style guide must work within these constraints:
- Main app navigation stays on the left (always visible)
- Style guide has its own internal navigation (sections/components)
- Layout templates must include collapsible sidebars that work within the main content area
- The "Sidebar Layout" template should demonstrate a collapsible project sidebar (like ProjectsView)

**CRITICAL COMPONENT CONSISTENCY**: The style guide must use existing Radix UI primitives and extend them, not create new competing components. All components should import from `/features/ui/primitives/`.

## Existing Patterns to Follow

### Glass Morphism Styles (Reference)
- **Location**: `/archon-ui-main/src/features/ui/primitives/styles.ts`
- Glass backgrounds, borders, shadows with glow effects
- Priority colors system already defined
- Use existing `glassmorphism` and `compoundStyles` objects

### Button Component (Reference)
- **Location**: `/archon-ui-main/src/features/ui/primitives/button.tsx`
- Variants: default, destructive, outline, ghost, link, cyan, knowledge
- Sizes: xs, sm, default, lg, icon
- Loading state support built-in

### Modal Patterns (Reference)
- **Location**: `/archon-ui-main/src/features/ui/components/DeleteConfirmModal.tsx`
- Uses AlertDialog from primitives
- Size prop support (compact, default, large)
- Proper glass morphism styling

### Routing Pattern (Reference)
- **Location**: `/archon-ui-main/src/App.tsx`
- Add new route: `<Route path="/style-guide" element={<StyleGuidePage />} />`
- Follow existing page import pattern

## Implementation Tasks

### Task 0: Create Missing Radix Primitives (PRIORITY)
Before implementing the style guide, we need to create missing Radix primitives that the configurators will use:

#### Create RadioGroup Primitive
```typescript
// /src/features/ui/primitives/radio-group.tsx
import * as RadioGroupPrimitive from "@radix-ui/react-radio-group";
import { Circle } from "lucide-react";
import React from "react";
import { cn, glassmorphism } from "./styles";

export const RadioGroup = RadioGroupPrimitive.Root;

export const RadioGroupItem = React.forwardRef<
  React.ElementRef<typeof RadioGroupPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof RadioGroupPrimitive.Item>
>(({ className, ...props }, ref) => (
  <RadioGroupPrimitive.Item
    ref={ref}
    className={cn(
      "aspect-square h-4 w-4 rounded-full",
      "backdrop-blur-md bg-gradient-to-b from-white/80 to-white/60",
      "dark:from-white/10 dark:to-black/30",
      glassmorphism.border.default,
      glassmorphism.interactive.base,
      "focus:outline-none focus:ring-2 focus:ring-cyan-500",
      "disabled:cursor-not-allowed disabled:opacity-50",
      "data-[state=checked]:border-cyan-500",
      className
    )}
    {...props}
  >
    <RadioGroupPrimitive.Indicator className="flex items-center justify-center">
      <Circle className="h-2.5 w-2.5 fill-cyan-500 text-cyan-500" />
    </RadioGroupPrimitive.Indicator>
  </RadioGroupPrimitive.Item>
));
RadioGroupItem.displayName = RadioGroupPrimitive.Item.displayName;
```

#### Create Label Primitive
```typescript
// /src/features/ui/primitives/label.tsx
import * as LabelPrimitive from "@radix-ui/react-label";
import React from "react";
import { cn } from "./styles";

export const Label = React.forwardRef<
  React.ElementRef<typeof LabelPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof LabelPrimitive.Root>
>(({ className, ...props }, ref) => (
  <LabelPrimitive.Root
    ref={ref}
    className={cn(
      "text-sm font-medium leading-none",
      "text-gray-700 dark:text-gray-200",
      "peer-disabled:cursor-not-allowed peer-disabled:opacity-70",
      className
    )}
    {...props}
  />
));
Label.displayName = LabelPrimitive.Root.displayName;
```

#### Create Card Primitive
```typescript
// /src/features/ui/primitives/card.tsx
import React from "react";
import { cn, glassmorphism } from "./styles";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  glowColor?: keyof typeof glassmorphism.shadow.glow | 'none';
  edgePosition?: keyof typeof glassmorphism.edgeGlow | 'none';
  size?: keyof typeof glassmorphism.sizes.card;
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, glowColor = 'none', edgePosition = 'none', size = 'md', children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          glassmorphism.background.card,
          glassmorphism.border.default,
          glassmorphism.shadow.md,
          glowColor !== 'none' && glassmorphism.shadow.glow[glowColor],
          edgePosition !== 'none' && glassmorphism.edgeGlow[edgePosition],
          glassmorphism.sizes.card[size],
          "rounded-lg transition-all duration-300",
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);
Card.displayName = "Card";
```

#### Enhance styles.ts
```typescript
// Add to /src/features/ui/primitives/styles.ts

export const glassmorphism = {
  // ... existing code ...

  // Add edge glow positions for card configurator
  edgeGlow: {
    top: "border-t-2 border-t-cyan-400 relative before:content-[''] before:absolute before:top-0 before:left-0 before:right-0 before:h-[2px] before:bg-gradient-to-r before:from-transparent before:via-cyan-400 before:to-transparent",
    left: "border-l-2 border-l-cyan-400 relative before:content-[''] before:absolute before:top-0 before:left-0 before:bottom-0 before:w-[2px] before:bg-gradient-to-b before:from-transparent before:via-cyan-400 before:to-transparent",
    right: "border-r-2 border-r-cyan-400 relative before:content-[''] before:absolute before:top-0 before:right-0 before:bottom-0 before:w-[2px] before:bg-gradient-to-b before:from-transparent before:via-cyan-400 before:to-transparent",
    bottom: "border-b-2 border-b-cyan-400 relative before:content-[''] before:absolute before:bottom-0 before:left-0 before:right-0 before:h-[2px] before:bg-gradient-to-r before:from-transparent before:via-cyan-400 before:to-transparent",
    all: "border-2 border-cyan-400 relative before:content-[''] before:absolute before:inset-0 before:rounded-lg before:p-[2px] before:bg-gradient-to-r before:from-cyan-400 before:via-cyan-500 before:to-cyan-400 before:-z-10",
    none: ""
  },

  // Add configurable sizes for cards
  sizes: {
    card: {
      sm: "p-4 max-w-sm",
      md: "p-6 max-w-md",
      lg: "p-8 max-w-lg",
      xl: "p-10 max-w-xl"
    }
  },

  // Ensure all glow colors are available
  shadow: {
    // ... existing shadow code ...
    glow: {
      purple: "shadow-[0_0_10px_2px_rgba(168,85,247,0.4)] dark:shadow-[0_0_20px_5px_rgba(168,85,247,0.7)]",
      blue: "shadow-[0_0_10px_2px_rgba(59,130,246,0.4)] dark:shadow-[0_0_20px_5px_rgba(59,130,246,0.7)]",
      green: "shadow-[0_0_10px_2px_rgba(16,185,129,0.4)] dark:shadow-[0_0_20px_5px_rgba(16,185,129,0.7)]",
      red: "shadow-[0_0_10px_2px_rgba(239,68,68,0.4)] dark:shadow-[0_0_20px_5px_rgba(239,68,68,0.7)]",
      orange: "shadow-[0_0_10px_2px_rgba(251,146,60,0.4)] dark:shadow-[0_0_20px_5px_rgba(251,146,60,0.7)]",
      cyan: "shadow-[0_0_10px_2px_rgba(34,211,238,0.4)] dark:shadow-[0_0_20px_5px_rgba(34,211,238,0.7)]",
      pink: "shadow-[0_0_10px_2px_rgba(236,72,153,0.4)] dark:shadow-[0_0_20px_5px_rgba(236,72,153,0.7)]"
    }
  }
};
```

### Task 1: Create Page Structure and Routing
```typescript
// 1. Create /src/pages/StyleGuidePage.tsx
// 2. Add route in App.tsx
// 3. Add navigation link in MainLayout navigation
```

### Task 2: Create Base Components Structure
```
/src/components/style-guide/
├── shared/
│   ├── NavigationSidebar.tsx    # 4 sections with expandable items
│   ├── LivePreview.tsx          # Preview container with zoom controls
│   ├── CodeDisplay.tsx          # Syntax highlighted code with copy
│   └── ConfigPanel.tsx          # Configuration controls container
```

### Task 3: Implement Component Configurators
```
/src/components/style-guide/configurators/
├── GlassCardConfigurator.tsx    # Glow colors, edge positions, sizes
├── ButtonConfigurator.tsx       # All variants, sizes, states
├── ModalConfigurator.tsx        # 6 standard types showcase
├── TableConfigurator.tsx        # Table with glass effects
├── FormConfigurator.tsx         # Input states and validation
└── ToggleConfigurator.tsx       # PowerButton variations
```

### Task 4: Create Modal Standards
```typescript
// /src/components/style-guide/standards/modalStandards.ts
export const MODAL_TYPES = {
  confirmation: { size: "sm", glowColor: "red", purpose: "Destructive actions" },
  formCreate: { size: "md", glowColor: "green", purpose: "Creating resources" },
  formEdit: { size: "md", glowColor: "blue", purpose: "Editing resources" },
  display: { size: "lg", glowColor: "purple", purpose: "Detailed information" },
  codeViewer: { size: "xl", glowColor: "cyan", purpose: "Code display" },
  settings: { size: "lg", glowColor: "blue", purpose: "App settings" }
};
```

### Task 5: Implement Layout Templates
```
/src/components/style-guide/layout-templates/
├── DashboardTemplate.tsx        # Grid of cards/widgets
├── SidebarTemplate.tsx          # Collapsible sidebar + main (like ProjectsView)
├── KanbanTemplate.tsx           # Column-based organization
├── TableViewTemplate.tsx        # Data table with actions
└── CenteredFormTemplate.tsx     # Single focus area
```

**SidebarTemplate Special Requirements:**
- Must show a collapsible sidebar within the main content area
- Sidebar toggles between top position (cards) and left position (list)
- Similar to ProjectsView with project cards that can be toggled to sidebar
- Include toggle button to switch between layouts
- Sidebar width: 280px when on left, full width when on top

### Task 6: Code Generation System
```typescript
// Each configurator must:
// 1. Generate real-time code based on configuration
// 2. Include all imports
// 3. Add AI context comments with decision trees
// 4. Provide copy-to-clipboard functionality
```

## Component Implementation Details

### ConfigPanel Component (Uses Card Primitive)
```typescript
// /src/components/style-guide/shared/ConfigPanel.tsx
import { Card } from '@/features/ui/primitives/card';
import { cn } from '@/features/ui/primitives/styles';

interface ConfigPanelProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export const ConfigPanel = ({ title, children, className }: ConfigPanelProps) => (
  <Card className={cn("space-y-4", className)}>
    {title && <h3 className="font-semibold text-lg mb-2">{title}</h3>}
    {children}
  </Card>
);
```

### GlassCardConfigurator (Using All Primitives)
```typescript
// Configuration Options:
- glowColor: ["purple", "blue", "green", "orange", "red", "none"]
- edgePosition: ["top", "left", "right", "bottom", "all", "none"]
- size: ["sm", "md", "lg", "xl"]

// Generated Code must include:
/**
 * 🤖 AI CONTEXT: GlassCard Component
 * PURPOSE: Container with glass morphism effect
 * WHEN TO USE: Primary content containers, cards, panels
 * WHEN NOT TO USE: Backgrounds, layout wrappers
 *
 * DECISION TREE:
 * - If primary content → glowColor="purple"
 * - If success message → glowColor="green"
 * - If error/danger → glowColor="red"
 */
```

### NavigationSidebar Structure
```typescript
const NAVIGATION = {
  foundations: {
    label: "Foundations",
    items: ["Colors", "Typography", "Spacing", "Effects"]
  },
  components: {
    label: "Components",
    items: ["Cards", "Buttons", "Forms", "Tables", "Modals", "Toggles"]
  },
  patterns: {
    label: "Patterns",
    items: ["Layouts", "Feedback", "Navigation", "Data Display"]
  },
  examples: {
    label: "Examples",
    items: ["Compositions", "Pages", "Workflows"]
  }
};
```

### LivePreview Component
```typescript
// Implementation: /src/components/style-guide/shared/LivePreview.tsx
import { useState } from 'react';
import { ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';
import { Button } from '@/features/ui/primitives/button';
import { cn } from '@/features/ui/primitives/styles';

interface LivePreviewProps {
  children: React.ReactNode;
  className?: string;
  minHeight?: string;
}

export const LivePreview = ({ children, className, minHeight = "400px" }: LivePreviewProps) => {
  const [zoom, setZoom] = useState(100);

  return (
    <div className="relative rounded-lg overflow-hidden">
      {/* Zoom Controls */}
      <div className="absolute top-2 right-2 z-10 flex gap-1">
        <Button
          size="icon"
          variant="outline"
          onClick={() => setZoom(prev => Math.max(50, prev - 25))}
        >
          <ZoomOut className="w-4 h-4" />
        </Button>
        <Button
          size="icon"
          variant="outline"
          onClick={() => setZoom(100)}
        >
          <RotateCcw className="w-4 h-4" />
        </Button>
        <Button
          size="icon"
          variant="outline"
          onClick={() => setZoom(prev => Math.min(150, prev + 25))}
        >
          <ZoomIn className="w-4 h-4" />
        </Button>
      </div>

      {/* Grid Background */}
      <div
        className={cn(
          "bg-gray-50 dark:bg-gray-900/50",
          "bg-[linear-gradient(to_right,#8882_1px,transparent_1px),linear-gradient(to_bottom,#8882_1px,transparent_1px)]",
          "bg-[size:20px_20px]",
          "p-8 flex items-center justify-center",
          className
        )}
        style={{ minHeight }}
      >
        <div
          style={{
            transform: `scale(${zoom / 100})`,
            transformOrigin: 'center'
          }}
        >
          {children}
        </div>
      </div>
    </div>
  );
};
```

### CodeDisplay Component
```typescript
// Implementation: /src/components/style-guide/shared/CodeDisplay.tsx
import { useState } from 'react';
import { Check, Copy } from 'lucide-react';
import { Button } from '@/features/ui/primitives/button';
import { cn } from '@/features/ui/primitives/styles';

interface CodeDisplayProps {
  code: string;
  language?: 'typescript' | 'jsx' | 'css';
  showLineNumbers?: boolean;
  className?: string;
}

export const CodeDisplay = ({
  code,
  language = 'typescript',
  showLineNumbers = false,
  className
}: CodeDisplayProps) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const lines = code.split('\n');

  // Basic syntax highlighting with regex
  const highlightCode = (line: string) => {
    // Escape HTML
    line = line.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

    // Keywords
    line = line.replace(
      /\b(import|export|from|const|let|var|function|return|if|else|interface|type|class|extends|implements)\b/g,
      '<span class="text-purple-400">$1</span>'
    );

    // Strings
    line = line.replace(
      /(["'`])([^"'`]*)\1/g,
      '<span class="text-green-400">$1$2$1</span>'
    );

    // Comments
    line = line.replace(
      /(\/\/.*$|\/\*.*\*\/)/g,
      '<span class="text-gray-500">$1</span>'
    );

    // JSX tags
    line = line.replace(
      /&lt;([A-Z][A-Za-z0-9]*)(\s|&gt;|\/&gt;)/g,
      '&lt;<span class="text-cyan-400">$1</span>$2'
    );

    // Props
    line = line.replace(
      /(\w+)=/g,
      '<span class="text-orange-400">$1</span>='
    );

    return line;
  };

  return (
    <div className={cn(
      "relative rounded-lg overflow-hidden",
      "bg-gray-900 border border-gray-800",
      className
    )}>
      {/* Copy Button */}
      <Button
        size="icon"
        variant="ghost"
        onClick={handleCopy}
        className="absolute top-2 right-2 z-10 text-gray-400 hover:text-white"
      >
        {copied ? (
          <Check className="w-4 h-4 text-green-400" />
        ) : (
          <Copy className="w-4 h-4" />
        )}
      </Button>

      {/* Code Content */}
      <pre className="p-4 overflow-x-auto">
        <code className="text-sm font-mono">
          {lines.map((line, index) => (
            <div key={index} className="flex">
              {showLineNumbers && (
                <span className="text-gray-500 mr-4 select-none w-8 text-right">
                  {index + 1}
                </span>
              )}
              <span
                dangerouslySetInnerHTML={{
                  __html: highlightCode(line) || '&nbsp;'
                }}
              />
            </div>
          ))}
        </code>
      </pre>
    </div>
  );
};
```

### Code Generation System (Updated with Proper Imports)
```typescript
// Detailed implementation for code generation
// Example: /src/components/style-guide/configurators/GlassCardConfigurator.tsx

import { useState } from 'react';
import { Card } from '@/features/ui/primitives/card';
import { Button } from '@/features/ui/primitives/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/features/ui/primitives/select';
import { RadioGroup, RadioGroupItem } from '@/features/ui/primitives/radio-group';
import { Label } from '@/features/ui/primitives/label';
import { LivePreview } from '../shared/LivePreview';
import { CodeDisplay } from '../shared/CodeDisplay';
import { ConfigPanel } from '../shared/ConfigPanel';
import { glassmorphism } from '@/features/ui/primitives/styles';

interface GlassCardConfig {
  glowColor: 'purple' | 'blue' | 'green' | 'orange' | 'red' | 'none';
  edgePosition: 'top' | 'left' | 'right' | 'bottom' | 'all' | 'none';
  size: 'sm' | 'md' | 'lg' | 'xl';
  content: string;
}

export const GlassCardConfigurator = () => {
  const [config, setConfig] = useState<GlassCardConfig>({
    glowColor: 'purple',
    edgePosition: 'top',
    size: 'md',
    content: 'Your content here'
  });

  const generateCode = (config: GlassCardConfig) => {
    const imports = `import { Card } from '@/features/ui/primitives/card';`;

    const aiContext = `/**
 * 🤖 AI CONTEXT: GlassCard Component
 *
 * PURPOSE: Container with glass morphism effect for primary content
 * WHEN TO USE: Feature cards, content sections, important information displays
 * WHEN NOT TO USE: Backgrounds, full-page layouts, navigation elements
 *
 * DECISION TREE:
 * - If primary/featured content → glowColor="purple"
 * - If success state/creation → glowColor="green"
 * - If error/danger/deletion → glowColor="red"
 * - If informational/edit → glowColor="blue"
 * - If warning/caution → glowColor="orange"
 *
 * SEMANTIC COLORS:
 * - purple: Primary actions, featured content, main CTAs
 * - green: Success states, creation, positive feedback
 * - red: Destructive actions, errors, critical alerts
 * - blue: Information, editing, secondary actions
 * - orange: Warnings, important notices, caution states
 *
 * EDGE POSITION GUIDELINES:
 * - top: Default, draws eye downward into content
 * - left: For sidebar items or navigation cards
 * - right: For action panels or secondary info
 * - bottom: For footer-like content or summaries
 * - all: For highly important or selected states
 * - none: For subtle, non-emphasized containers
 */`;

    const component = `export const MyCard = ({ children }) => {
  return (
    <Card
      glowColor="${config.glowColor}"
      edgePosition="${config.edgePosition}"
      size="${config.size}"
    >
      {children}
    </Card>
  );
};`;

    return `${imports}\n\n${aiContext}\n\n${component}`;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Left side: Configuration */}
      <div className="space-y-6">
        <ConfigPanel title="Glass Card Configuration">
          <div className="space-y-4">
            {/* Glow Color */}
            <div>
              <Label>Glow Color</Label>
              <Select
                value={config.glowColor}
                onValueChange={(value) => setConfig({...config, glowColor: value as any})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="purple">Purple (Primary)</SelectItem>
                  <SelectItem value="blue">Blue (Info)</SelectItem>
                  <SelectItem value="green">Green (Success)</SelectItem>
                  <SelectItem value="orange">Orange (Warning)</SelectItem>
                  <SelectItem value="red">Red (Danger)</SelectItem>
                  <SelectItem value="none">None</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Edge Position */}
            <div>
              <Label>Edge Glow Position</Label>
              <RadioGroup
                value={config.edgePosition}
                onValueChange={(value) => setConfig({...config, edgePosition: value as any})}
              >
                <div className="grid grid-cols-3 gap-2">
                  {['top', 'left', 'right', 'bottom', 'all', 'none'].map(position => (
                    <div key={position} className="flex items-center space-x-2">
                      <RadioGroupItem value={position} id={position} />
                      <Label htmlFor={position} className="capitalize">
                        {position}
                      </Label>
                    </div>
                  ))}
                </div>
              </RadioGroup>
            </div>

            {/* Size */}
            <div>
              <Label>Size</Label>
              <RadioGroup
                value={config.size}
                onValueChange={(value) => setConfig({...config, size: value as any})}
              >
                <div className="flex gap-4">
                  {['sm', 'md', 'lg', 'xl'].map(size => (
                    <div key={size} className="flex items-center space-x-2">
                      <RadioGroupItem value={size} id={`size-${size}`} />
                      <Label htmlFor={`size-${size}`} className="uppercase">
                        {size}
                      </Label>
                    </div>
                  ))}
                </div>
              </RadioGroup>
            </div>
          </div>
        </ConfigPanel>

        {/* Live Preview */}
        <LivePreview>
          <Card
            glowColor={config.glowColor}
            edgePosition={config.edgePosition}
            size={config.size}
          >
            <h3 className="text-lg font-semibold mb-2">Glass Card Example</h3>
            <p className="text-gray-600 dark:text-gray-300">
              {config.content}
            </p>
          </Card>
        </LivePreview>
      </div>

      {/* Right side: Generated Code */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Generated Code</h3>
        <CodeDisplay
          code={generateCode(config)}
          language="typescript"
          showLineNumbers
        />
      </div>
    </div>
  );
};
```

### SidebarTemplate Implementation (Using Primitives)
```typescript
// /src/components/style-guide/layout-templates/SidebarTemplate.tsx
import { useState } from 'react';
import { ChevronLeft, ChevronRight, LayoutGrid, List } from 'lucide-react';
import { Button } from '@/features/ui/primitives/button';
import { Card } from '@/features/ui/primitives/card';
import { cn } from '@/features/ui/primitives/styles';
import { CodeDisplay } from '../shared/CodeDisplay';

export const SidebarTemplate = () => {
  const [sidebarPosition, setSidebarPosition] = useState<'top' | 'left'>('top');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const items = [
    { id: '1', title: 'Project Alpha', status: 'active' },
    { id: '2', title: 'Project Beta', status: 'pending' },
    { id: '3', title: 'Project Gamma', status: 'completed' },
  ];

  const generateCode = () => {
    return `import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/features/ui/primitives/button';
import { Card } from '@/features/ui/primitives/card';

export const SidebarLayout = () => {
  const [position, setPosition] = useState<'top' | 'left'>('top');
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="flex flex-col h-full">
      {/* Toggle Button */}
      <div className="flex justify-end p-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setPosition(p => p === 'top' ? 'left' : 'top')}
        >
          {position === 'top' ? <List /> : <LayoutGrid />}
        </Button>
      </div>

      <div className={cn(
        "flex",
        position === 'top' ? "flex-col" : "flex-row",
        "flex-1 gap-4 p-4"
      )}>
        {/* Sidebar Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={position}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className={cn(
              position === 'left' && !collapsed && "w-[280px]",
              position === 'left' && collapsed && "w-[60px]",
              position === 'top' && "w-full",
              "transition-all duration-300"
            )}
          >
            {/* Sidebar items here */}
          </motion.div>
        </AnimatePresence>

        {/* Main Content Area */}
        <div className="flex-1">
          {/* Main content here */}
        </div>
      </div>
    </div>
  );
};`;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Sidebar Layout Template</h3>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setSidebarPosition(p => p === 'top' ? 'left' : 'top')}
        >
          Toggle Position: {sidebarPosition === 'top' ? <LayoutGrid className="w-4 h-4 ml-2" /> : <List className="w-4 h-4 ml-2" />}
        </Button>
      </div>

      {/* Live Demo */}
      <div className="border rounded-lg p-4 min-h-[400px] bg-gray-50 dark:bg-gray-900/50">
        <div className={cn(
          "flex h-full",
          sidebarPosition === 'top' ? "flex-col" : "flex-row",
          "gap-4"
        )}>
          {/* Sidebar */}
          <div className={cn(
            sidebarPosition === 'left' && !sidebarCollapsed && "w-[280px]",
            sidebarPosition === 'left' && sidebarCollapsed && "w-[60px]",
            sidebarPosition === 'top' && "w-full",
            "transition-all duration-300"
          )}>
            {sidebarPosition === 'top' ? (
              <div className="grid grid-cols-3 gap-4">
                {items.map(item => (
                  <Card key={item.id} glowColor="purple" className="hover:shadow-lg transition-shadow cursor-pointer">
                    <h4 className="font-medium">{item.title}</h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{item.status}</p>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="space-y-2">
                {sidebarPosition === 'left' && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="w-full justify-start"
                    onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                  >
                    {sidebarCollapsed ? <ChevronRight /> : <ChevronLeft />}
                  </Button>
                )}
                {items.map(item => (
                  <Card
                    key={item.id}
                    className={cn(
                      "hover:shadow-lg transition-shadow cursor-pointer",
                      sidebarCollapsed && "p-2"
                    )}
                  >
                    {!sidebarCollapsed ? (
                      <>
                        <h4 className="font-medium text-sm">{item.title}</h4>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{item.status}</p>
                      </>
                    ) : (
                      <div className="w-8 h-8 rounded bg-purple-500/20 flex items-center justify-center">
                        {item.title[0]}
                      </div>
                    )}
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Main Content */}
          <div className="flex-1 border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-8">
            <div className="text-center text-gray-500 dark:text-gray-400">
              <p className="text-lg font-medium mb-2">Main Content Area</p>
              <p className="text-sm">This is where your main content would go</p>
              <p className="text-xs mt-4">Sidebar is currently: {sidebarPosition === 'top' ? 'Top' : `Left (${sidebarCollapsed ? 'Collapsed' : 'Expanded'})`}</p>
            </div>
          </div>
        </div>
      </div>

      <CodeDisplay code={generateCode()} language="typescript" showLineNumbers />
    </div>
  );
};
```

## Confidence Score: 10/10

The PRP provides comprehensive implementation guidance with:
- **Radix primitive creation tasks** for missing components
- **Style enhancements** to support configurator needs
- **Consistent imports** from `/features/ui/primitives/`
- **Complete code examples** using actual primitives
- **Clear implementation order** with primitive creation first

The score is 10/10 because:
- **Component consistency**: All configurators use existing primitives
- **No duplicate components**: Reuses existing infrastructure
- **Enhanced flexibility**: styles.ts gets necessary additions
- **Complete primitive set**: Creates missing RadioGroup, Label, and Card
- **Production ready**: Uses same components developers will use

This PRP ensures the style guide showcases actual Archon components, not separate demo versions.

## Validation Gates

```bash
# Frontend checks
cd archon-ui-main
npm run lint                    # No linting errors
npx tsc --noEmit                # No TypeScript errors
npm run test                    # All tests pass

# Verify primitives work
# Check that all new primitives render correctly
# Verify Card primitive replaces old Card.tsx
# Test RadioGroup and Label components
# Confirm styles.ts enhancements work

# Verify routes work
# Navigate to http://localhost:3737/style-guide
# Verify all configurators render
# Test code generation and copy functionality
# Check responsive behavior
```

## Dependencies
- Existing Archon UI primitives and components
- Tailwind CSS (already configured)
- Lucide React icons (already installed)
- React Router (already installed)
- Radix UI packages (already installed):
  - @radix-ui/react-radio-group
  - @radix-ui/react-label
- For syntax highlighting: Use simple regex-based solution (no external libs)

## File Creation Order
1. **Create missing primitives first** (RadioGroup, Label, Card)
2. **Enhance styles.ts** with edgeGlow and sizes
3. Create page and add route
4. Build shared components (NavigationSidebar, LivePreview, CodeDisplay, ConfigPanel)
5. Implement GlassCardConfigurator first (as template)
6. Add ButtonConfigurator
7. Create modal standards and ModalConfigurator
8. Add remaining configurators
9. Implement layout templates
10. Add AI context comments throughout

## Key Implementation Notes

### State Management
- Use React hooks (useState) for configuration state
- Each configurator manages its own state
- URL params for sharing configurations (optional enhancement)

### Import Consistency
- ALWAYS import from `/features/ui/primitives/` for UI components
- Never create duplicate components
- Use the Card primitive for all card needs
- Import glassmorphism styles from styles.ts

### Performance Considerations
- Lazy load configurators that aren't visible
- Debounce configuration changes (200ms)
- Use React.memo for expensive preview renders
- Limit blur effects to 3 layers maximum

## Success Criteria
- [ ] All primitives created and working
- [ ] Old Card.tsx replaced with new primitive
- [ ] All routes work and page loads without errors
- [ ] Navigation sidebar with 4 main sections
- [ ] GlassCard configurator with live preview using Card primitive
- [ ] Button configurator with all variants
- [ ] 6 modal types clearly documented
- [ ] 5 layout templates available
- [ ] Code generation with AI comments
- [ ] Copy-to-clipboard works
- [ ] Responsive design functions properly
- [ ] No TypeScript or linting errors
- [ ] All imports from primitives folder

## Common Pitfalls to Avoid
- Don't create new component variants - use existing ones
- Don't duplicate components - use primitives
- Don't add external libraries for syntax highlighting initially
- Don't forget AI context comments in generated code
- Don't nest glass effects more than 3 levels
- Don't hardcode values - use configuration objects
- Don't import from old `/components/ui/` folder

## Testing Approach
1. Manual testing of all configurators
2. Verify code generation accuracy
3. Test copy-to-clipboard functionality
4. Check responsive breakpoints
5. Validate AI comments are included
6. Test with actual AI assistant to verify comments help
7. Verify all imports use primitives

## References
- Button component: `/archon-ui-main/src/features/ui/primitives/button.tsx`
- Glass morphism styles: `/archon-ui-main/src/features/ui/primitives/styles.ts`
- Select primitive: `/archon-ui-main/src/features/ui/primitives/select.tsx`
- Modal example: `/archon-ui-main/src/features/ui/components/DeleteConfirmModal.tsx`
- Routing: `/archon-ui-main/src/App.tsx`
- Layout: `/archon-ui-main/src/components/layout/MainLayout.tsx`
- Projects View (sidebar example): `/archon-ui-main/src/features/projects/views/ProjectsView.tsx`
- Old Card to replace: `/archon-ui-main/src/components/ui/Card.tsx`