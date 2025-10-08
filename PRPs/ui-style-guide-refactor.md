name: "UI Style Guide Refactor - 3-Tab Organization with Layout Examples"
description: |
  Refactor the Archon style guide into a focused, AI-friendly reference with three distinct tabs:
  1. Style Guide - Traditional design system (typography, colors, spacing)
  2. Layouts - Page layout examples (Projects, Settings, Knowledge) with navigation patterns
  3. Configurators - Interactive component configurators with live code generation

---

## Goal

**Feature Goal**: Transform the current cluttered style guide into a focused, well-organized reference that serves both human users and AI agents, with clear separation between design foundations, layout patterns, and interactive component configuration.

**Deliverable**:
- Refactored `/style-guide` page with 3-tab navigation (Style Guide, Layouts, Configurators)
- `components.json` mapping file documenting all reusable components with locations and purposes
- Hard-coded layout examples (Projects, Settings, Knowledge pages) with NO data/functionality
- Simplified style guide tab showing typography, colors, spacing, effects foundations
- Configurators tab with existing interactive component configurators

**Success Definition**:
- AI agents can quickly find component examples via `components.json`
- Users can see layout options and understand visual hierarchy patterns
- Design system foundations (typography, colors) are clearly documented
- Interactive configurators provide live code generation for components

## User Persona

**Target User**:
1. **AI Coding Assistants** (Primary) - Need clear component references and code patterns
2. **Developers** - Building new features, need layout examples and component patterns
3. **Designers** - Understanding and extending the Tron-inspired glassmorphism system

**Use Case**:
- AI agent needs to build a new page: consults `components.json` → finds layout examples → copies patterns
- Developer adding a feature: reviews Layout tab → picks appropriate page structure → implements with hard-coded examples as reference
- Designer adjusting colors/typography: uses Style Guide tab → interactive configurators for testing

**User Journey**:
1. Open Style Guide page
2. See 3 clear tabs (Style Guide, Layouts, Configurators)
3. For layouts: Click "Layouts" → See 3 example pages (Projects, Settings, Knowledge) with explanatory text
4. For foundations: Click "Style Guide" → Review typography, colors, spacing, effects
5. For interactive config: Click "Configurators" → Play with glass cards, buttons, forms with live code

**Pain Points Addressed**:
- **Current**: Style guide is cluttered and mixes foundations, components, patterns, and examples
- **Current**: No clear separation between what's for learning vs what's for interactive configuration
- **Current**: AI agents struggle to find the right component because there's no index/map
- **New**: Clean 3-tab separation makes navigation obvious
- **New**: `components.json` provides quick component discovery for AI
- **New**: Hard-coded layout examples show patterns without complexity of real data

## Why

- **For AI Agents**: Reduce context needed - `components.json` points directly to relevant components, layout examples show patterns without implementation details
- **For Developers**: Faster feature development - see complete page layouts (Projects card grid, Settings bento, Knowledge view switching) to copy structure
- **For Design System**: Clearer documentation - separate "what colors exist" from "how to configure a glass card interactively"
- **Integration**: Existing configurators (GlassCard, Button, Modal, etc.) are preserved and moved to Configurators tab
- **User Experience**: Users can quickly understand options (layouts), learn basics (style guide), or interactively configure (configurators)

## What

### Success Criteria

- [ ] 3-tab navigation works smoothly (Style Guide, Layouts, Configurators)
- [ ] `components.json` file maps all reusable components with file paths and usage descriptions
- [ ] Layouts tab shows 3 example pages:
  - Projects: Card grid layout with horizontal scroll and project selection
  - Settings: Bento grid with CollapsibleSettingsCard components
  - Knowledge: View switching example (grid/table) with filters
- [ ] Style Guide tab shows traditional foundations: Typography, Colors, Spacing, Effects
- [ ] Configurators tab contains all existing interactive configurators
- [ ] All layout examples use hard-coded data (no API calls, no real functionality)
- [ ] Navigation explanation describes main nav (left sidebar) vs page nav (top tabs/pills)
- [ ] Each layout example includes explanatory text about when to use it

## All Needed Context

### Context Completeness Check

_This PRP provides complete context for refactoring the style guide without prior Archon knowledge. It includes:_
- ✅ Existing file structure and patterns to follow
- ✅ Specific component examples to extract (ProjectCard, CollapsibleSettingsCard, view switching)
- ✅ Exact tab structure and organization (3 tabs)
- ✅ Clear separation of concerns (foundations vs layouts vs configurators)
- ✅ `components.json` schema and purpose
- ✅ Hard-coded data examples for each layout type

### Documentation & References

```yaml
# Core Style Guide Files - READ THESE FIRST
- file: archon-ui-main/src/features/style-guide/components/StyleGuideView.tsx
  why: Current implementation - understand existing structure and tab navigation pattern
  pattern: PillNavigation component with sections and items
  gotcha: Currently has 4 sections (foundations, components, patterns, examples) - we're consolidating to 3 tabs

- file: archon-ui-main/src/features/style-guide/shared/PillNavigation.tsx
  why: Tab navigation component - will be adapted for 3-tab structure
  pattern: Pill-based navigation with dropdown per section
  gotcha: Current implementation has dropdown per section - new design has direct tabs

# Typography & Colors (Keep for Style Guide Tab)
- file: archon-ui-main/src/features/style-guide/foundations/TypographyFoundation.tsx
  why: Typography scale and configurator - moves to Style Guide tab
  pattern: Interactive configurator with live examples

- file: archon-ui-main/src/features/style-guide/foundations/ColorsFoundation.tsx
  why: Color palette with interactive swatches - moves to Style Guide tab
  pattern: Color variants with slider, copy-to-clipboard

- file: archon-ui-main/src/features/style-guide/foundations/SpacingFoundation.tsx
  why: Spacing scale visualization - moves to Style Guide tab

- file: archon-ui-main/src/features/style-guide/foundations/EffectsFoundation.tsx
  why: Glassmorphism effects examples - moves to Style Guide tab

# Configurators (Move to Configurators Tab)
- file: archon-ui-main/src/features/style-guide/configurators/GlassCardConfigurator.tsx
  why: Interactive glass card builder with code generation
  pattern: Showcase/Configurator toggle, live preview, code display

- file: archon-ui-main/src/features/style-guide/configurators/ButtonConfigurator.tsx
  why: Button variants configurator - keep in Configurators tab

- file: archon-ui-main/src/features/style-guide/configurators/ModalConfigurator.tsx
  why: Modal preview and configuration - keep in Configurators tab

- file: archon-ui-main/src/features/style-guide/configurators/FormConfigurator.tsx
  why: Form elements configurator - keep in Configurators tab

- file: archon-ui-main/src/features/style-guide/configurators/TableConfigurator.tsx
  why: Table styling configurator - keep in Configurators tab

- file: archon-ui-main/src/features/style-guide/patterns/NavigationPattern.tsx
  why: Pill navigation configurator with dropdown sub-menus
  pattern: PillNavigationConfigurator component with live preview and code generation
  critical: MOVE this to configurators as NavigationConfigurator - it's an interactive configurator, not a pattern

# Layout Examples (Source Components for Layouts Tab)
- file: archon-ui-main/src/features/projects/components/ProjectCard.tsx
  why: Example card component with glassmorphism, task counts, selection states
  pattern: Card with gradient backgrounds, hover effects, neon glow borders
  gotcha: Uses real data and optimistic updates - strip to hard-coded example

- file: archon-ui-main/src/features/projects/components/ProjectList.tsx
  why: Horizontal scrolling card grid layout pattern
  pattern: Flex container with overflow-x-auto, gap-4 spacing

- file: archon-ui-main/src/components/ui/CollapsibleSettingsCard.tsx
  why: Collapsible card component for bento grid
  pattern: PowerButton toggle, AnimatePresence for expand/collapse
  gotcha: Uses localStorage - remove for hard-coded example

- file: archon-ui-main/src/pages/SettingsPage.tsx
  why: Bento grid layout example (2-column responsive)
  pattern: grid grid-cols-1 lg:grid-cols-2 gap-6

- file: archon-ui-main/src/features/knowledge/views/KnowledgeView.tsx
  why: View mode switching pattern (grid vs table)
  pattern: useState for viewMode, conditional rendering
  gotcha: Has real data fetching - create simplified hard-coded version

- file: archon-ui-main/src/features/knowledge/components/KnowledgeHeader.tsx
  why: View toggle buttons (grid/table icons)
  pattern: Button group with active state styling

- file: archon-ui-main/src/features/knowledge/components/DocumentBrowser.tsx
  why: Information display modal with tabs, search, and expandable content
  pattern: Dialog + Tabs + Search + Collapsible content items
  critical: KEY PATTERN for displaying structured information in modals (documents, code examples, logs, etc.)

# Navigation Patterns
- file: archon-ui-main/src/components/layout/Navigation.tsx
  why: Main sidebar navigation with glassmorphism
  pattern: Fixed left sidebar, tooltip on hover, active state with neon glow

- file: archon-ui-main/src/components/layout/MainLayout.tsx
  why: Overall page layout structure
  pattern: Fixed nav sidebar, content area with padding

- file: archon-ui-main/src/features/projects/views/ProjectsView.tsx
  why: Top tabs navigation example (Docs/Tasks tabs)
  pattern: Radix Tabs component with TabsList and TabsTrigger

# Glassmorphism System
- file: archon-ui-main/src/features/ui/primitives/styles.ts
  why: Complete glassmorphism design system with all utilities
  pattern: glassmorphism object with background, border, shadow, variants
  critical: This is the foundation for all glass styling - reference extensively

# Tailwind Configuration
- file: archon-ui-main/tailwind.config.js
  why: Theme configuration, custom colors, animations
  pattern: HSL-based color tokens, custom keyframes

# Radix UI Primitives - ALL COMPONENTS MUST USE THESE
- file: archon-ui-main/src/features/ui/primitives/tabs.tsx
  why: Radix Tabs primitive with glassmorphism styling
  pattern: Tabs, TabsList, TabsTrigger, TabsContent components
  critical: Use for all tab navigation (Style Guide, Layouts, Configurators main tabs AND within examples)

- file: archon-ui-main/src/features/ui/primitives/select.tsx
  why: Radix Select primitive with glassmorphism and color variants
  pattern: Select, SelectTrigger, SelectValue, SelectContent, SelectItem
  critical: Use for ALL dropdowns - never use native HTML select

- file: archon-ui-main/src/features/ui/primitives/dialog.tsx
  why: Radix Dialog primitive for modals
  pattern: Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription

- file: archon-ui-main/src/features/ui/primitives/button.tsx
  why: Button primitive with glassmorphism variants
  pattern: Supports variants (default, destructive, outline, ghost, cyan, purple, green) and sizes (sm, md, lg, icon)

- file: archon-ui-main/src/features/ui/primitives/card.tsx
  why: GlassCard primitive with configurable blur, transparency, tints, edges
  pattern: Card component with extensive glassmorphism options

- file: archon-ui-main/src/features/ui/primitives/checkbox.tsx
  why: Radix Checkbox with glassmorphism and color variants
  pattern: Checkbox component with color prop (cyan, purple, blue, green, etc.)

- file: archon-ui-main/src/features/ui/primitives/switch.tsx
  why: Radix Switch toggle with glassmorphism
  pattern: Switch component with smooth animations

- file: archon-ui-main/src/features/ui/primitives/tooltip.tsx
  why: Radix Tooltip for hover hints
  pattern: Tooltip, TooltipTrigger, TooltipContent, TooltipProvider

- file: archon-ui-main/src/features/ui/primitives/dropdown-menu.tsx
  why: Radix DropdownMenu for context menus
  pattern: DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem

- file: archon-ui-main/src/features/ui/primitives/toggle-group.tsx
  why: Radix ToggleGroup for mutually exclusive selections
  pattern: ToggleGroup, ToggleGroupItem with single/multiple type

- file: archon-ui-main/src/features/ui/primitives/input.tsx
  why: Styled input component (not Radix, but used with Radix forms)
  pattern: Input component for text fields

- file: archon-ui-main/src/features/ui/primitives/label.tsx
  why: Label component for form fields
  pattern: Label primitive for accessibility

- file: archon-ui-main/src/features/ui/primitives/radio-group.tsx
  why: Radix RadioGroup for mutually exclusive options
  pattern: RadioGroup, RadioGroupItem

- file: archon-ui-main/src/features/ui/primitives/alert-dialog.tsx
  why: Radix AlertDialog for confirmation dialogs
  pattern: AlertDialog, AlertDialogTrigger, AlertDialogContent, AlertDialogAction

- url: https://www.radix-ui.com/primitives/docs/overview/introduction
  why: Radix UI documentation - understand composition patterns
  critical: All primitives use compound component pattern (Root + Sub-components)
  source_id: 72f799530ca992a6
```

### Current Codebase Tree

```
archon-ui-main/src/features/style-guide/
├── components/
│   └── StyleGuideView.tsx        # Main view - refactor this
├── shared/
│   ├── PillNavigation.tsx        # Adapt for 3 tabs
│   ├── CodeDisplay.tsx           # Reuse for code examples
│   └── ConfiguratorCard.tsx      # Reuse for configurators
├── foundations/                   # KEEP - move to Style Guide tab
│   ├── TypographyFoundation.tsx
│   ├── ColorsFoundation.tsx
│   ├── SpacingFoundation.tsx
│   └── EffectsFoundation.tsx
├── configurators/                 # KEEP - move to Configurators tab
│   ├── GlassCardConfigurator.tsx
│   ├── ButtonConfigurator.tsx
│   ├── ModalConfigurator.tsx
│   ├── FormConfigurator.tsx
│   ├── TableConfigurator.tsx
│   ├── ToggleConfigurator.tsx
│   ├── SwitchConfigurator.tsx
│   ├── CheckboxConfigurator.tsx
│   └── NavigationConfigurator.tsx # MOVE from patterns/NavigationPattern.tsx
├── patterns/                      # DELETE - will be replaced by Layouts tab
│   ├── LayoutsPattern.tsx
│   ├── FeedbackPattern.tsx
│   ├── NavigationPattern.tsx      # MOVE to configurators/NavigationConfigurator.tsx
│   └── DataDisplayPattern.tsx
└── examples/                      # DELETE - replaced by hard-coded layout examples
    ├── CompositionsExample.tsx
    ├── PagesExample.tsx
    ├── WorkflowsExample.tsx
    └── RAGSettingsExample.tsx
```

### Desired Codebase Tree

```
archon-ui-main/src/features/style-guide/
├── components/
│   └── StyleGuideView.tsx                        # REFACTORED - 3-tab structure
├── shared/
│   ├── SimpleTabNavigation.tsx                   # NEW - simple 3-tab nav (no dropdowns)
│   ├── CodeDisplay.tsx                           # KEEP as-is
│   └── ConfiguratorCard.tsx                      # KEEP as-is
├── tabs/                                         # NEW DIRECTORY
│   ├── StyleGuideTab.tsx                         # NEW - contains foundations
│   ├── LayoutsTab.tsx                            # NEW - contains layout examples
│   └── ConfiguratorsTab.tsx                      # NEW - contains configurators
├── foundations/                                   # KEEP - used by StyleGuideTab
│   ├── TypographyFoundation.tsx                  # KEEP as-is
│   ├── ColorsFoundation.tsx                      # KEEP as-is
│   ├── SpacingFoundation.tsx                     # KEEP as-is
│   └── EffectsFoundation.tsx                     # KEEP as-is
├── configurators/                                 # KEEP - used by ConfiguratorsTab
│   ├── GlassCardConfigurator.tsx                 # KEEP as-is
│   ├── ButtonConfigurator.tsx                    # KEEP as-is
│   ├── ModalConfigurator.tsx                     # KEEP as-is
│   ├── FormConfigurator.tsx                      # KEEP as-is
│   ├── TableConfigurator.tsx                     # KEEP as-is
│   ├── ToggleConfigurator.tsx                    # KEEP as-is
│   ├── SwitchConfigurator.tsx                    # KEEP as-is
│   ├── CheckboxConfigurator.tsx                  # KEEP as-is
│   └── NavigationConfigurator.tsx                # MOVED from patterns/NavigationPattern.tsx
└── layouts/                                       # NEW DIRECTORY
    ├── ProjectsLayoutExample.tsx                  # NEW - hard-coded Projects page (horizontal + sidebar)
    ├── SettingsLayoutExample.tsx                  # NEW - hard-coded Settings bento grid
    ├── KnowledgeLayoutExample.tsx                 # NEW - hard-coded view switching
    ├── DocumentBrowserExample.tsx                 # NEW - information display modal example
    └── NavigationExplanation.tsx                  # NEW - nav patterns explanation

archon-ui-main/public/
└── components.json                                # NEW - component mapping for AI
```

### Known Gotchas & Library Quirks

```typescript
// CRITICAL: Framer Motion AnimatePresence
// When removing items from arrays, use layout prop and unique keys
<AnimatePresence mode="popLayout">
  {items.map((item) => (
    <motion.div key={item.id} layout exit="exit">
      {/* content */}
    </motion.div>
  ))}
</AnimatePresence>

// CRITICAL: Radix UI Tabs
// Always wrap TabsContent in conditional or it will still render in DOM
{activeTab === "docs" && (
  <TabsContent value="docs">{/* content */}</TabsContent>
)}

// CRITICAL: Glassmorphism Styles
// Import from primitives/styles.ts, NOT from local constants
import { glassmorphism, glassCard, cn } from '@/features/ui/primitives/styles';

// CRITICAL: Hard-coded Data for Layouts
// NO real data, NO API calls, NO useState for data
// ONLY useState for UI state (view mode, selected tab, etc.)
const MOCK_PROJECTS = [
  { id: '1', title: 'Project Alpha', pinned: true, taskCounts: { todo: 5, doing: 2, review: 1, done: 12 } },
  { id: '2', title: 'Project Beta', pinned: false, taskCounts: { todo: 3, doing: 1, review: 0, done: 8 } },
];

// CRITICAL: View Mode Pattern
// Always use type-safe union types for view modes
const [viewMode, setViewMode] = useState<"grid" | "table">("grid");

// CRITICAL: Lucide React Icons
// Standard sizes are w-4 h-4 (small), w-5 h-5 (medium), w-6 h-6 (large)
import { Grid, List, LayoutGrid, Table } from 'lucide-react';

// CRITICAL: Radix UI Compound Component Pattern
// All Radix components use composition pattern (Root + Sub-components)
// Example - Tabs:
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/features/ui/primitives/tabs';
<Tabs defaultValue="tasks" value={activeTab} onValueChange={setActiveTab}>
  <TabsList>
    <TabsTrigger value="tasks" color="orange">Tasks</TabsTrigger>
    <TabsTrigger value="docs" color="blue">Docs</TabsTrigger>
  </TabsList>
  <TabsContent value="tasks">{/* content */}</TabsContent>
</Tabs>

// Example - Select:
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/features/ui/primitives/select';
<Select value={value} onValueChange={setValue}>
  <SelectTrigger color="cyan">
    <SelectValue placeholder="Choose..." />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="option1">Option 1</SelectItem>
    <SelectItem value="option2">Option 2</SelectItem>
  </SelectContent>
</Select>

// CRITICAL: Never use native HTML elements for these interactions
// ❌ WRONG: <select><option></option></select>
// ✅ CORRECT: Use Radix Select primitive
// ❌ WRONG: <input type="checkbox" />
// ✅ CORRECT: Use Radix Checkbox primitive
// ❌ WRONG: <button> for tab switching
// ✅ CORRECT: Use Radix Tabs primitive

// CRITICAL: All Radix primitives in Archon have glassmorphism styling
// Import from features/ui/primitives/* - they're already styled
// Don't re-style primitives - configure via props (color, variant, size)
```

## Implementation Blueprint

### Component Mapping Schema (components.json)

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "version": "1.0.0",
  "description": "Archon UI Component Reference for AI Agents and Developers",
  "categories": {
    "navigation": {
      "description": "Navigation components for app and page-level navigation",
      "components": [
        {
          "name": "MainNavigation",
          "path": "archon-ui-main/src/components/layout/Navigation.tsx",
          "usage": "Fixed left sidebar navigation with glassmorphism, tooltips, and active state indicators",
          "props": ["className?"],
          "example": "Fixed position, icon-based, tooltip on hover, neon glow on active"
        },
        {
          "name": "PageTabs",
          "path": "archon-ui-main/src/features/ui/primitives/tabs.tsx (Radix Tabs)",
          "usage": "Top-level page navigation tabs (e.g., Docs/Tasks in Projects)",
          "props": ["defaultValue", "value", "onValueChange"],
          "example": "See Projects page (Docs/Tasks tabs) - archon-ui-main/src/features/projects/views/ProjectsView.tsx:188-210"
        },
        {
          "name": "ViewToggleButtons",
          "path": "archon-ui-main/src/features/knowledge/components/KnowledgeHeader.tsx:88-118",
          "usage": "Toggle between grid and table views",
          "props": ["viewMode", "onViewModeChange"],
          "example": "Grid/List icon buttons with active state styling"
        }
      ]
    },
    "layouts": {
      "description": "Page layout patterns",
      "components": [
        {
          "name": "CardGridLayout",
          "path": "archon-ui-main/src/features/projects/components/ProjectList.tsx:100-117",
          "usage": "Horizontal scrolling card grid for project cards or similar items",
          "pattern": "flex gap-4 overflow-x-auto with min-w-max",
          "example": "Projects page - horizontal scrollable cards",
          "variant": "horizontal (default)"
        },
        {
          "name": "SidebarListLayout",
          "path": "NEW - see ProjectsLayoutExample.tsx",
          "usage": "Sidebar navigation list with compact cards and search",
          "pattern": "Fixed left column (w-72) with vertical list, Input for search, main content on right (flex-1)",
          "example": "Projects page sidebar variant - vertical list with smaller cards",
          "variant": "sidebar (alternative to horizontal cards)"
        },
        {
          "name": "BentoGridLayout",
          "path": "archon-ui-main/src/pages/SettingsPage.tsx:125-223",
          "usage": "Two-column responsive grid for collapsible settings cards",
          "pattern": "grid grid-cols-1 lg:grid-cols-2 gap-6",
          "example": "Settings page - left/right column layout"
        },
        {
          "name": "ResponsiveGridLayout",
          "path": "archon-ui-main/src/features/knowledge/components/KnowledgeList.tsx:158-183",
          "usage": "Responsive grid for card items (1/2/3/4 columns)",
          "pattern": "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4",
          "example": "Knowledge page grid view"
        },
        {
          "name": "TableLayout",
          "path": "archon-ui-main/src/features/knowledge/components/KnowledgeTable.tsx:68-209",
          "usage": "Table with glassmorphism styling, hover states, and action buttons",
          "pattern": "overflow-x-auto wrapper with full-width table",
          "example": "Knowledge page table view"
        }
      ]
    },
    "cards": {
      "description": "Card components for various use cases",
      "components": [
        {
          "name": "ProjectCard",
          "path": "archon-ui-main/src/features/projects/components/ProjectCard.tsx",
          "usage": "Card with real-time data (task counts), selection states, pinned indicator",
          "features": ["glassmorphism", "hover effects", "neon glow borders", "task count pills", "pin badge"],
          "example": "w-72 min-h-[180px] with gradient backgrounds"
        },
        {
          "name": "CollapsibleSettingsCard",
          "path": "archon-ui-main/src/components/ui/CollapsibleSettingsCard.tsx",
          "usage": "Collapsible card with PowerButton toggle and flicker animation",
          "features": ["expand/collapse", "localStorage persistence", "accent colors"],
          "example": "Settings page cards"
        },
        {
          "name": "GlassCard (Primitive)",
          "path": "archon-ui-main/src/features/ui/primitives/card.tsx",
          "usage": "Base glassmorphism card with configurable blur, transparency, tints, edges",
          "props": ["blur?", "transparency?", "glassTint?", "edgePosition?", "edgeColor?", "size?"],
          "example": "See GlassCardConfigurator for all options"
        }
      ]
    },
    "information_display": {
      "description": "Patterns for displaying structured information",
      "components": [
        {
          "name": "DocumentBrowser",
          "path": "archon-ui-main/src/features/knowledge/components/DocumentBrowser.tsx",
          "usage": "Modal for displaying documents, code, logs, or structured information with tabs and search",
          "features": ["Dialog modal", "Tabs navigation", "Search filtering", "Expandable content", "Code syntax highlighting"],
          "radix_used": ["Dialog", "Tabs", "Input"],
          "pattern": "Dialog + Tabs + Search input + Collapsible items with expand/collapse",
          "example": "Knowledge inspector, document viewer, code browser, log viewer"
        }
      ]
    },
    "buttons": {
      "description": "Button components and variants",
      "components": [
        {
          "name": "Button (Primitive)",
          "path": "archon-ui-main/src/features/ui/primitives/button.tsx",
          "usage": "Base button with glassmorphism variants",
          "variants": ["default", "destructive", "outline", "ghost", "cyan", "purple", "green"],
          "sizes": ["sm", "md", "lg", "icon"],
          "example": "See ButtonConfigurator for all variants"
        }
      ]
    },
    "radix_primitives": {
      "description": "Radix UI primitives with Archon glassmorphism styling",
      "components": [
        {
          "name": "Tabs",
          "path": "archon-ui-main/src/features/ui/primitives/tabs.tsx",
          "usage": "Tab navigation with color variants and neon glow effects",
          "radix_package": "@radix-ui/react-tabs",
          "parts": ["Tabs", "TabsList", "TabsTrigger", "TabsContent"],
          "props": ["defaultValue", "value", "onValueChange", "color (cyan|blue|purple|orange|green|pink)"],
          "example": "Projects page Docs/Tasks tabs"
        },
        {
          "name": "Select",
          "path": "archon-ui-main/src/features/ui/primitives/select.tsx",
          "usage": "Dropdown select with glassmorphism and color variants",
          "radix_package": "@radix-ui/react-select",
          "parts": ["Select", "SelectTrigger", "SelectValue", "SelectContent", "SelectItem"],
          "props": ["value", "onValueChange", "color (purple|blue|green|pink|orange|cyan)"],
          "example": "Configurators use Select for all dropdowns"
        },
        {
          "name": "Dialog",
          "path": "archon-ui-main/src/features/ui/primitives/dialog.tsx",
          "usage": "Modal dialogs with glassmorphism backdrop",
          "radix_package": "@radix-ui/react-dialog",
          "parts": ["Dialog", "DialogTrigger", "DialogContent", "DialogHeader", "DialogTitle", "DialogDescription"],
          "props": ["open", "onOpenChange"],
          "example": "NewProjectModal, EditTaskModal"
        },
        {
          "name": "Checkbox",
          "path": "archon-ui-main/src/features/ui/primitives/checkbox.tsx",
          "usage": "Styled checkbox with color variants",
          "radix_package": "@radix-ui/react-checkbox",
          "parts": ["Checkbox"],
          "props": ["checked", "onCheckedChange", "color (cyan|purple|blue|green|etc)"],
          "example": "Settings toggles, NavigationConfigurator"
        },
        {
          "name": "Switch",
          "path": "archon-ui-main/src/features/ui/primitives/switch.tsx",
          "usage": "Toggle switch with smooth animations",
          "radix_package": "@radix-ui/react-switch",
          "parts": ["Switch"],
          "props": ["checked", "onCheckedChange"],
          "example": "Feature toggles in Settings"
        },
        {
          "name": "Tooltip",
          "path": "archon-ui-main/src/features/ui/primitives/tooltip.tsx",
          "usage": "Hover tooltips with glassmorphism",
          "radix_package": "@radix-ui/react-tooltip",
          "parts": ["TooltipProvider", "Tooltip", "TooltipTrigger", "TooltipContent"],
          "props": ["delayDuration", "side", "align"],
          "example": "Navigation sidebar icons"
        },
        {
          "name": "DropdownMenu",
          "path": "archon-ui-main/src/features/ui/primitives/dropdown-menu.tsx",
          "usage": "Context menus with glassmorphism",
          "radix_package": "@radix-ui/react-dropdown-menu",
          "parts": ["DropdownMenu", "DropdownMenuTrigger", "DropdownMenuContent", "DropdownMenuItem"],
          "example": "ProjectCardActions, context menus"
        },
        {
          "name": "ToggleGroup",
          "path": "archon-ui-main/src/features/ui/primitives/toggle-group.tsx",
          "usage": "Mutually exclusive button group",
          "radix_package": "@radix-ui/react-toggle-group",
          "parts": ["ToggleGroup", "ToggleGroupItem"],
          "props": ["type (single|multiple)", "value", "onValueChange"],
          "example": "KnowledgeHeader type filter"
        }
      ]
    }
  }
}
```

### Implementation Tasks (Ordered by Dependencies)

```yaml
Task 1: CREATE archon-ui-main/public/components.json
  - IMPLEMENT: Complete component mapping schema (see above)
  - CONTENT: All navigation, layout, card, button components with paths and examples
  - NAMING: components.json in public directory for easy AI access
  - PURPOSE: AI agent quick reference - no need to search codebase
  - PLACEMENT: public/ directory (accessible at /components.json)

Task 2: CREATE archon-ui-main/src/features/style-guide/shared/SimpleTabNavigation.tsx
  - IMPLEMENT: Simple 3-tab navigation component (Style Guide, Layouts, Configurators)
  - FOLLOW pattern: Similar to GlassCardConfigurator's showcase/configurator toggle (lines 123-153)
  - STYLING: Pill-based tabs with glassmorphism background, active state glow
  - PROPS: { activeTab: 'style-guide' | 'layouts' | 'configurators', onTabChange: (tab) => void }
  - CRITICAL: Use button elements (not Radix Tabs) for this navigation - it's a styled button group
  - PATTERN:
    ```tsx
    import { cn } from '@/features/ui/primitives/styles';

    interface SimpleTabNavigationProps {
      activeTab: 'style-guide' | 'layouts' | 'configurators';
      onTabChange: (tab: 'style-guide' | 'layouts' | 'configurators') => void;
    }

    export const SimpleTabNavigation = ({ activeTab, onTabChange }: SimpleTabNavigationProps) => {
      const tabs = [
        { id: 'style-guide' as const, label: 'Style Guide' },
        { id: 'layouts' as const, label: 'Layouts' },
        { id: 'configurators' as const, label: 'Configurators' },
      ];

      return (
        <div className="backdrop-blur-sm bg-white/40 dark:bg-white/5 border border-white/30 dark:border-white/15 rounded-full p-1 shadow-lg">
          <div className="flex gap-1 items-center">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={cn(
                  "flex items-center gap-2 px-6 py-2.5 rounded-full transition-all duration-200",
                  "text-sm font-medium whitespace-nowrap",
                  activeTab === tab.id
                    ? "bg-cyan-500/20 dark:bg-cyan-400/20 text-cyan-700 dark:text-cyan-300 border border-cyan-400/50 shadow-[0_0_10px_rgba(34,211,238,0.5)]"
                    : "text-gray-700 dark:text-gray-300 hover:bg-white/10 dark:hover:bg-white/5"
                )}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      );
    };
    ```

Task 3: CREATE archon-ui-main/src/features/style-guide/layouts/NavigationExplanation.tsx
  - IMPLEMENT: Visual explanation of navigation patterns
  - CONTENT:
    - Main Navigation: Left sidebar, fixed position (left-6), icon-based, 72px wide
    - Content Area: pl-[100px] to accommodate main nav, all page content lives here
    - Page Navigation: Top tabs/pills for page sections (e.g., Docs/Tasks)
    - View Controls: Toggle buttons for grid/table views
  - CRITICAL: Explain that main nav is OUTSIDE content area, page layouts are INSIDE content area
  - VISUAL: Show diagram/examples with code snippets
  - PLACEMENT: Top of Layouts tab as introduction

Task 4: CREATE archon-ui-main/src/features/style-guide/layouts/ProjectsLayoutExample.tsx
  - IMPLEMENT: Hard-coded Projects page layout example with dual layout modes
  - MOCK DATA: 3-4 mock projects with task counts, one pinned
  - FEATURES:
    - Layout toggle: Horizontal cards (default) OR Sidebar list view
    - Horizontal scrolling card grid with project selection highlighting
    - Sidebar variant: Smaller card list on left with search bar
  - RADIX: Use Tabs primitive for Docs/Tasks navigation example, Input for search
  - LAYOUT MODES:
    - "horizontal": Cards across top (current ProjectList pattern)
    - "sidebar": Vertical list on left WITHIN content area (not covering main nav)
  - CRITICAL POSITIONING:
    - This component renders INSIDE the main content area (pl-[100px])
    - Main navigation is OUTSIDE at fixed left-6 (72px wide)
    - Sidebar layout should use relative positioning, NOT fixed
    - Sidebar project list: w-72 (288px) on left, flex-1 for content on right
    - Total width respects parent container, doesn't overlap main nav
  - STRIP: All real data fetching, optimistic updates, mutations
  - KEEP: Visual styling, layout structure, selection state (local)
  - PATTERN:
    ```tsx
    import { Input } from '@/features/ui/primitives/input';
    import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/features/ui/primitives/tabs';

    const MOCK_PROJECTS = [
      { id: '1', title: 'Design System', pinned: true, taskCounts: { todo: 5, doing: 2, review: 1, done: 12 } },
      { id: '2', title: 'API Integration', pinned: false, taskCounts: { todo: 3, doing: 1, review: 0, done: 8 } },
      { id: '3', title: 'Mobile App', pinned: false, taskCounts: { todo: 8, doing: 0, review: 0, done: 0 } },
    ];
    const [selectedId, setSelectedId] = useState('1');
    const [layoutMode, setLayoutMode] = useState<'horizontal' | 'sidebar'>('horizontal');

    // Layout toggle buttons (LayoutGrid icon for horizontal, List icon for sidebar)
    // Horizontal layout: flex gap-4 overflow-x-auto (current pattern)
    // Sidebar layout: flex gap-6 (left sidebar w-72, right content flex-1) - RELATIVE positioning
    // Sidebar DOES NOT use fixed/absolute - it's a flex container within the content area
    ```
  - EXPLANATION TEXT: "Use this layout for: Horizontal scrolling items (default), OR sidebar navigation for projects. Toggle shows both layout options. Sidebar respects main navigation (doesn't overlap). Cards with real-time data displays."

Task 5: CREATE archon-ui-main/src/features/style-guide/layouts/SettingsLayoutExample.tsx
  - IMPLEMENT: Hard-coded Settings bento grid layout
  - MOCK SECTIONS: 4-6 collapsible card sections (Features, API Keys, RAG, Code Extraction, etc.)
  - FEATURES: 2-column responsive grid, collapsible cards with PowerButton
  - STRIP: All real settings data, localStorage, API calls
  - KEEP: Visual layout, expand/collapse animation, accent colors
  - PATTERN:
    ```tsx
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <CollapsibleSettingsCard title="Features" icon={Palette} accentColor="purple" defaultExpanded={true}>
        {/* Mock content */}
      </CollapsibleSettingsCard>
      {/* More cards */}
    </div>
    ```
  - EXPLANATION TEXT: "Use this layout for: Settings pages, dashboard widgets, grouped configuration sections"

Task 6: CREATE archon-ui-main/src/features/style-guide/layouts/KnowledgeLayoutExample.tsx
  - IMPLEMENT: Hard-coded Knowledge page with view switching
  - MOCK DATA: 6-8 mock knowledge items (docs, websites, etc.)
  - FEATURES: View mode toggle (grid/table), filters, search (UI only, no real filtering)
  - RADIX: Use ToggleGroup for type filter (All/Technical/Business)
  - VIEW MODES: Grid (responsive columns) and Table (overflow-x-auto)
  - STRIP: All real data fetching, delete actions, real search/filter logic
  - KEEP: View switching logic, layout patterns, visual styling
  - PATTERN:
    ```tsx
    const [viewMode, setViewMode] = useState<"grid" | "table">("grid");

    {viewMode === "table" ? (
      <div className="overflow-x-auto">
        <table className="w-full">{/* table content */}</table>
      </div>
    ) : (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {/* grid items */}
      </div>
    )}
    ```
  - EXPLANATION TEXT: "Use this layout for: Switchable views (grid/table/list), filterable data, search interfaces"

Task 7: CREATE archon-ui-main/src/features/style-guide/layouts/DocumentBrowserExample.tsx
  - IMPLEMENT: Hard-coded information display modal example
  - MOCK DATA: 5-6 mock document chunks, 3-4 mock code examples
  - FEATURES: Dialog modal with Tabs (Documents/Code), Search input, Expandable content
  - RADIX: Dialog, Tabs, Input primitives
  - STRIP: All real data fetching, real search logic
  - KEEP: Visual structure, tab switching, expand/collapse interaction, search UI
  - PATTERN:
    ```tsx
    import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/features/ui/primitives/dialog';
    import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/features/ui/primitives/tabs';
    import { Input } from '@/features/ui/primitives/input';
    import { Button } from '@/features/ui/primitives/button';

    const MOCK_DOCUMENTS = [
      { id: '1', title: 'Getting Started', content: 'Full document content...', tags: ['guide', 'intro'] },
      { id: '2', title: 'API Reference', content: 'API documentation...', tags: ['api', 'reference'] },
    ];

    const MOCK_CODE = [
      { id: '1', language: 'typescript', summary: 'React component example', code: 'const Example = () => {...}' },
      { id: '2', language: 'python', summary: 'FastAPI endpoint', code: '@app.get("/api/items")...' },
    ];

    const [open, setOpen] = useState(false);
    const [activeTab, setActiveTab] = useState<'documents' | 'code'>('documents');
    const [searchQuery, setSearchQuery] = useState('');
    const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

    // Dialog with max-w-4xl, h-[80vh], flex flex-col for full-height modal
    // Search input in DialogHeader with Search icon (absolute left-3)
    // Tabs with icon + label + counts: "Documents (5)", "Code Examples (3)"
    // TabsContent with flex-1 overflow-hidden for scrollable content
    // Expandable items: Set<string> for tracking expanded state
    // Toggle pattern: ChevronRight (collapsed) / ChevronDown (expanded)
    // Content preview: first 200 chars with "Show more" link
    // Code display: <pre><code> with syntax highlighting classes

    // Example Button to Open Modal:
    <Button onClick={() => setOpen(true)}>
      View Documents
    </Button>
    <DocumentBrowserExample open={open} onOpenChange={setOpen} />
    ```
  - EXPLANATION TEXT: "Use this pattern for: Displaying structured information in modals (documents, logs, code, API responses). Tabs organize different data types, search filters content, items expand/collapse for details."

Task 8: CREATE archon-ui-main/src/features/style-guide/tabs/StyleGuideTab.tsx
  - IMPLEMENT: Container component for foundations
  - RENDER: TypographyFoundation, ColorsFoundation, SpacingFoundation, EffectsFoundation
  - LAYOUT: Vertical stack with spacing
  - PATTERN:
    ```tsx
    <div className="space-y-16">
      <TypographyFoundation />
      <ColorsFoundation />
      <SpacingFoundation />
      <EffectsFoundation />
    </div>
    ```

Task 9: CREATE archon-ui-main/src/features/style-guide/tabs/LayoutsTab.tsx
  - IMPLEMENT: Container component for layout examples
  - RENDER: NavigationExplanation, ProjectsLayoutExample, SettingsLayoutExample, KnowledgeLayoutExample, DocumentBrowserExample
  - LAYOUT: Vertical stack with large spacing and section headers
  - PATTERN:
    ```tsx
    <div className="space-y-12">
      <NavigationExplanation />
      <section>
        <h2 className="text-2xl font-bold mb-4">Projects Layout</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Horizontal scrolling cards OR sidebar navigation with search. Toggle to see both modes.
        </p>
        <ProjectsLayoutExample />
      </section>
      <section>
        <h2 className="text-2xl font-bold mb-4">Settings Layout</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Bento grid (2-column responsive) with collapsible cards.
        </p>
        <SettingsLayoutExample />
      </section>
      <section>
        <h2 className="text-2xl font-bold mb-4">Knowledge Layout</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Switchable views (grid/table) with filters and search.
        </p>
        <KnowledgeLayoutExample />
      </section>
      <section>
        <h2 className="text-2xl font-bold mb-4">Information Display Modal</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Modal with tabs, search, and expandable content for documents, code, logs.
        </p>
        <DocumentBrowserExample />
      </section>
    </div>
    ```

Task 10: MOVE archon-ui-main/src/features/style-guide/patterns/NavigationPattern.tsx
  - RENAME: NavigationPattern.tsx → NavigationConfigurator.tsx
  - MOVE TO: archon-ui-main/src/features/style-guide/configurators/NavigationConfigurator.tsx
  - KEEP: All existing functionality (pill navigation with dropdowns, color variants, size options)
  - UPDATE EXPORT: Change export name if needed to match configurator pattern
  - VERIFY: Import in ConfiguratorsTab works correctly

Task 11: CREATE archon-ui-main/src/features/style-guide/tabs/ConfiguratorsTab.tsx
  - IMPLEMENT: Container component for all configurators
  - RENDER: All 9 configurators (GlassCard, Button, Modal, Form, Table, Toggle, Switch, Checkbox, Navigation)
  - LAYOUT: Vertical stack with spacing, section headers per configurator
  - PATTERN:
    ```tsx
    import { GlassCardConfigurator } from '../configurators/GlassCardConfigurator';
    import { ButtonConfigurator } from '../configurators/ButtonConfigurator';
    import { ModalConfigurator } from '../configurators/ModalConfigurator';
    import { FormConfigurator } from '../configurators/FormConfigurator';
    import { TableConfigurator } from '../configurators/TableConfigurator';
    import { ToggleConfigurator } from '../configurators/ToggleConfigurator';
    import { SwitchConfigurator } from '../configurators/SwitchConfigurator';
    import { CheckboxConfigurator } from '../configurators/CheckboxConfigurator';
    import { NavigationConfigurator } from '../configurators/NavigationConfigurator';

    export const ConfiguratorsTab = () => {
      return (
        <div className="space-y-12">
          <section>
            <h2 className="text-2xl font-bold mb-4">Glass Card Configurator</h2>
            <GlassCardConfigurator />
          </section>
          <section>
            <h2 className="text-2xl font-bold mb-4">Button Configurator</h2>
            <ButtonConfigurator />
          </section>
          <section>
            <h2 className="text-2xl font-bold mb-4">Navigation Configurator</h2>
            <NavigationConfigurator />
          </section>
          <section>
            <h2 className="text-2xl font-bold mb-4">Modal Configurator</h2>
            <ModalConfigurator />
          </section>
          <section>
            <h2 className="text-2xl font-bold mb-4">Form Configurator</h2>
            <FormConfigurator />
          </section>
          <section>
            <h2 className="text-2xl font-bold mb-4">Table Configurator</h2>
            <TableConfigurator />
          </section>
          <section>
            <h2 className="text-2xl font-bold mb-4">Toggle Configurator</h2>
            <ToggleConfigurator />
          </section>
          <section>
            <h2 className="text-2xl font-bold mb-4">Switch Configurator</h2>
            <SwitchConfigurator />
          </section>
          <section>
            <h2 className="text-2xl font-bold mb-4">Checkbox Configurator</h2>
            <CheckboxConfigurator />
          </section>
        </div>
      );
    };
    ```

Task 12: MODIFY archon-ui-main/src/features/style-guide/components/StyleGuideView.tsx
  - REFACTOR: Replace complex navigation with SimpleTabNavigation
  - STATE: const [activeTab, setActiveTab] = useState<'style-guide' | 'layouts' | 'configurators'>('style-guide')
  - RENDER: Conditional rendering based on activeTab
  - REMOVE: All old FOUNDATION_TABS, COMPONENT_TABS, PATTERN_TABS, EXAMPLE_TABS arrays
  - KEEP: Header with title and description
  - KEEP: ThemeToggle component in top right corner
  - PATTERN:
    ```tsx
    import { SimpleTabNavigation } from '../shared/SimpleTabNavigation';
    import { StyleGuideTab } from '../tabs/StyleGuideTab';
    import { LayoutsTab } from '../tabs/LayoutsTab';
    import { ConfiguratorsTab } from '../tabs/ConfiguratorsTab';
    import { ThemeToggle } from '@/components/ui/ThemeToggle';

    export const StyleGuideView = () => {
      const [activeTab, setActiveTab] = useState<'style-guide' | 'layouts' | 'configurators'>('style-guide');

      return (
        <div className="space-y-12">
          {/* Header */}
          <div className="relative">
            <div className="absolute top-0 right-0">
              <ThemeToggle accentColor="blue" />
            </div>
            <div className="text-center space-y-4">
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
                Archon UI Style Guide
              </h1>
              <p className="text-gray-600 dark:text-gray-400 text-lg max-w-2xl mx-auto">
                Design system foundations, layout patterns, and interactive component configurators.
              </p>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="flex justify-center">
            <SimpleTabNavigation activeTab={activeTab} onTabChange={setActiveTab} />
          </div>

          {/* Tab Content */}
          <div>
            {activeTab === 'style-guide' && <StyleGuideTab />}
            {activeTab === 'layouts' && <LayoutsTab />}
            {activeTab === 'configurators' && <ConfiguratorsTab />}
          </div>
        </div>
      );
    };
    ```

Task 13: DELETE old pattern and example files (AFTER Tasks 1-12 complete)
  - DELETE: archon-ui-main/src/features/style-guide/patterns/ (entire directory)
  - DELETE: archon-ui-main/src/features/style-guide/examples/ (entire directory)
  - DELETE: archon-ui-main/src/features/style-guide/shared/PillNavigation.tsx (if not used elsewhere)
  - VERIFY: No imports referencing deleted files

Task 14: UPDATE archon-ui-main/src/features/style-guide/index.ts
  - MODIFY: Export new tab components and SimpleTabNavigation
  - REMOVE: Exports for deleted patterns and examples
  - ADD:
    ```typescript
    export { StyleGuideView } from './components/StyleGuideView';
    export { SimpleTabNavigation } from './shared/SimpleTabNavigation';
    export { StyleGuideTab } from './tabs/StyleGuideTab';
    export { LayoutsTab } from './tabs/LayoutsTab';
    export { ConfiguratorsTab } from './tabs/ConfiguratorsTab';
    ```
```

### Implementation Patterns & Key Details

```typescript
// SimpleTabNavigation Component Pattern
// archon-ui-main/src/features/style-guide/shared/SimpleTabNavigation.tsx
import { cn } from '@/features/ui/primitives/styles';

interface SimpleTabNavigationProps {
  activeTab: 'style-guide' | 'layouts' | 'configurators';
  onTabChange: (tab: 'style-guide' | 'layouts' | 'configurators') => void;
}

export const SimpleTabNavigation = ({ activeTab, onTabChange }: SimpleTabNavigationProps) => {
  const tabs = [
    { id: 'style-guide' as const, label: 'Style Guide' },
    { id: 'layouts' as const, label: 'Layouts' },
    { id: 'configurators' as const, label: 'Configurators' },
  ];

  return (
    <div className="backdrop-blur-sm bg-white/40 dark:bg-white/5 border border-white/30 dark:border-white/15 rounded-full p-1 shadow-lg">
      <div className="flex gap-1 items-center">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={cn(
              "flex items-center gap-2 px-6 py-2.5 rounded-full transition-all duration-200",
              "text-sm font-medium whitespace-nowrap",
              activeTab === tab.id
                ? "bg-cyan-500/20 dark:bg-cyan-400/20 text-cyan-700 dark:text-cyan-300 border border-cyan-400/50 shadow-[0_0_10px_rgba(34,211,238,0.5)]"
                : "text-gray-700 dark:text-gray-300 hover:bg-white/10 dark:hover:bg-white/5"
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  );
};

// Hard-Coded Project Card Pattern (Simplified)
// archon-ui-main/src/features/style-guide/layouts/ProjectsLayoutExample.tsx
const MOCK_PROJECTS = [
  {
    id: '1',
    title: 'Design System',
    pinned: true,
    taskCounts: { todo: 5, doing: 2, review: 1, done: 12 }
  },
  {
    id: '2',
    title: 'API Integration',
    pinned: false,
    taskCounts: { todo: 3, doing: 1, review: 0, done: 8 }
  },
  {
    id: '3',
    title: 'Mobile App',
    pinned: false,
    taskCounts: { todo: 8, doing: 0, review: 0, done: 0 }
  },
];

// Projects Layout with Horizontal vs Sidebar Toggle
const ProjectsLayoutExample = () => {
  const [selectedId, setSelectedId] = useState('1');
  const [layoutMode, setLayoutMode] = useState<'horizontal' | 'sidebar'>('horizontal');

  return (
    <div>
      {/* Layout Mode Toggle */}
      <div className="flex justify-end mb-4">
        <div className="flex gap-1 p-1 bg-black/30 rounded-lg border border-white/10">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setLayoutMode('horizontal')}
            className={cn(
              "px-3",
              layoutMode === 'horizontal' ? "bg-cyan-500/20 text-cyan-400" : "text-gray-400"
            )}
          >
            <LayoutGrid className="w-4 h-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setLayoutMode('sidebar')}
            className={cn(
              "px-3",
              layoutMode === 'sidebar' ? "bg-cyan-500/20 text-cyan-400" : "text-gray-400"
            )}
          >
            <List className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Conditional Layout Rendering */}
      {layoutMode === 'horizontal' ? (
        // Horizontal scrolling card grid (current pattern)
        <div className="overflow-x-auto pb-4">
          <div className="flex gap-4 min-w-max">
            {MOCK_PROJECTS.map((project) => (
              <SimplifiedProjectCard
                key={project.id}
                project={project}
                isSelected={selectedId === project.id}
                onSelect={setSelectedId}
              />
            ))}
          </div>
        </div>
      ) : (
        // Sidebar layout (new pattern) - RELATIVE positioning within content area
        <div className="flex gap-6">
          {/* Left Sidebar: Project List - w-72 (288px) */}
          <div className="w-72 space-y-3">
            <Input placeholder="Search projects..." className="mb-4" />
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {MOCK_PROJECTS.map((project) => (
                <SimplifiedSidebarProjectCard
                  key={project.id}
                  project={project}
                  isSelected={selectedId === project.id}
                  onSelect={setSelectedId}
                />
              ))}
            </div>
          </div>
          {/* Right: Main Content - flex-1 takes remaining space */}
          <div className="flex-1">
            {/* Example: Tabs for Docs/Tasks */}
            <Tabs defaultValue="tasks" className="w-full">
              <TabsList>
                <TabsTrigger value="tasks" color="orange">Tasks</TabsTrigger>
                <TabsTrigger value="docs" color="blue">Docs</TabsTrigger>
              </TabsList>
              <TabsContent value="tasks" className="mt-4">
                <Card className="p-6">Task content area...</Card>
              </TabsContent>
              <TabsContent value="docs" className="mt-4">
                <Card className="p-6">Docs content area...</Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      )}
    </div>
  );
};

// CRITICAL: Sidebar Positioning
// - Main nav: fixed left-6 (72px wide, 24px from left edge)
// - Content area: pl-[100px] (gives space for 72px nav + 28px gap)
// - Sidebar layout: INSIDE content area (relative positioning)
// - Total layout: [Main Nav (72px)] [Gap (28px)] [Content: [Sidebar (288px)] [Gap (24px)] [Main Content (flex-1)]]
// - No overlap with main navigation

// Full ProjectCard for horizontal layout (w-72, min-h-[180px])
const SimplifiedProjectCard = ({ project, isSelected, onSelect }) => {
  return (
    <div
      onClick={() => onSelect(project.id)}
      className={cn(
        "relative rounded-xl backdrop-blur-md w-72 min-h-[180px] cursor-pointer",
        "transition-all duration-300",
        project.pinned
          ? "bg-gradient-to-b from-purple-100/80 to-purple-100/50"
          : isSelected
            ? "bg-gradient-to-b from-white/70 to-white/50"
            : "bg-gradient-to-b from-white/80 to-white/60",
        // ... rest of styling from ProjectCard.tsx but without real data logic
      )}
    >
      {/* Card content - copy structure from ProjectCard but with mock data */}
    </div>
  );
};

// Compact SidebarProjectCard for sidebar layout (full width, h-auto)
const SimplifiedSidebarProjectCard = ({ project, isSelected, onSelect }) => {
  return (
    <div
      onClick={() => onSelect(project.id)}
      className={cn(
        "relative rounded-lg backdrop-blur-md p-3 cursor-pointer",
        "transition-all duration-300",
        project.pinned
          ? "bg-gradient-to-r from-purple-100/80 to-purple-100/50 border-l-2 border-purple-500"
          : isSelected
            ? "bg-gradient-to-r from-white/70 to-white/50 border-l-2 border-cyan-500"
            : "bg-gradient-to-r from-white/80 to-white/60 border-l-2 border-transparent",
      )}
    >
      <h4 className="font-medium text-sm mb-2">{project.title}</h4>
      <div className="flex gap-2 text-xs">
        <span className="text-pink-600">{project.taskCounts.todo} todo</span>
        <span className="text-blue-600">{project.taskCounts.doing} doing</span>
        <span className="text-green-600">{project.taskCounts.done} done</span>
      </div>
    </div>
  );
};

// View Mode Toggle Pattern
// archon-ui-main/src/features/style-guide/layouts/KnowledgeLayoutExample.tsx
const ViewModeToggle = ({ viewMode, onViewModeChange }) => {
  return (
    <div className="flex gap-1 p-1 bg-black/30 rounded-lg border border-white/10">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => onViewModeChange("grid")}
        className={cn(
          "px-3",
          viewMode === "grid"
            ? "bg-cyan-500/20 text-cyan-400"
            : "text-gray-400 hover:text-white"
        )}
      >
        <Grid className="w-4 h-4" />
      </Button>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => onViewModeChange("table")}
        className={cn(
          "px-3",
          viewMode === "table"
            ? "bg-cyan-500/20 text-cyan-400"
            : "text-gray-400 hover:text-white"
        )}
      >
        <List className="w-4 h-4" />
      </Button>
    </div>
  );
};

// ===== RADIX UI PRIMITIVES - COMPREHENSIVE GUIDE =====

// TABS PRIMITIVE PATTERN (for page-level navigation)
// archon-ui-main/src/features/projects/views/ProjectsView.tsx:188-210
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/features/ui/primitives/tabs';

const PageWithTabs = () => {
  const [activeTab, setActiveTab] = useState("tasks");

  return (
    <Tabs defaultValue="tasks" value={activeTab} onValueChange={setActiveTab} className="w-full">
      <TabsList>
        <TabsTrigger value="tasks" color="orange">
          Tasks
        </TabsTrigger>
        <TabsTrigger value="docs" color="blue">
          Docs
        </TabsTrigger>
      </TabsList>

      {/* CRITICAL: Wrap TabsContent in conditional to prevent rendering when inactive */}
      {activeTab === "tasks" && (
        <TabsContent value="tasks" className="mt-0">
          {/* Task content */}
        </TabsContent>
      )}
      {activeTab === "docs" && (
        <TabsContent value="docs" className="mt-0">
          {/* Docs content */}
        </TabsContent>
      )}
    </Tabs>
  );
};

// SELECT PRIMITIVE PATTERN (for dropdowns, always use this over native select)
// archon-ui-main/src/features/style-guide/configurators/GlassCardConfigurator.tsx:245-262
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/features/ui/primitives/select';

const DropdownExample = () => {
  const [value, setValue] = useState("medium");

  return (
    <Select value={value} onValueChange={setValue}>
      <SelectTrigger color="cyan">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="small">Small</SelectItem>
        <SelectItem value="medium">Medium</SelectItem>
        <SelectItem value="large">Large</SelectItem>
      </SelectContent>
    </Select>
  );
};

// CHECKBOX PRIMITIVE PATTERN
// archon-ui-main/src/features/style-guide/patterns/NavigationPattern.tsx:423-432
import { Checkbox } from '@/features/ui/primitives/checkbox';

const CheckboxExample = () => {
  const [checked, setChecked] = useState(false);

  return (
    <div className="flex items-center gap-3">
      <Checkbox
        id="show-icons"
        checked={checked}
        onCheckedChange={setChecked}
        color="cyan"
      />
      <label htmlFor="show-icons" className="text-sm font-medium">
        Show Icons
      </label>
    </div>
  );
};

// TOGGLE GROUP PRIMITIVE PATTERN (for filters, view modes)
// archon-ui-main/src/features/knowledge/components/KnowledgeHeader.tsx:59-75
import { ToggleGroup, ToggleGroupItem } from '@/features/ui/primitives/toggle-group';
import { Asterisk, Terminal, FileCode } from 'lucide-react';

const FilterExample = () => {
  const [filter, setFilter] = useState("all");

  return (
    <ToggleGroup
      type="single"
      size="sm"
      value={filter}
      onValueChange={(v) => v && setFilter(v)}
      aria-label="Filter type"
    >
      <ToggleGroupItem value="all" aria-label="All" title="All">
        <Asterisk className="w-4 h-4" />
      </ToggleGroupItem>
      <ToggleGroupItem value="technical" aria-label="Technical" title="Technical">
        <Terminal className="w-4 h-4" />
      </ToggleGroupItem>
      <ToggleGroupItem value="business" aria-label="Business" title="Business">
        <FileCode className="w-4 h-4" />
      </ToggleGroupItem>
    </ToggleGroup>
  );
};

// TOOLTIP PRIMITIVE PATTERN
// archon-ui-main/src/components/layout/Navigation.tsx:89-130
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from '@/features/ui/primitives/tooltip';

// CRITICAL: TooltipProvider must wrap entire app (already in App.tsx)
const TooltipExample = () => {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <button>Hover me</button>
      </TooltipTrigger>
      <TooltipContent>
        <p>Tooltip content</p>
      </TooltipContent>
    </Tooltip>
  );
};

// DIALOG PRIMITIVE PATTERN (for modals)
// archon-ui-main/src/features/projects/components/NewProjectModal.tsx (reference)
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/features/ui/primitives/dialog';

const ModalExample = () => {
  const [open, setOpen] = useState(false);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Modal Title</DialogTitle>
        </DialogHeader>
        {/* Modal content */}
      </DialogContent>
    </Dialog>
  );
};

// ===== DOCUMENT BROWSER PATTERN - Information Display Modal =====
// archon-ui-main/src/features/knowledge/components/DocumentBrowser.tsx
// CRITICAL: This is the pattern for displaying structured information in modals

import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/features/ui/primitives/dialog';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/features/ui/primitives/tabs';
import { Input } from '@/features/ui/primitives/input';
import { ChevronDown, ChevronRight, Code, FileText, Search } from 'lucide-react';

const DocumentBrowserExample = ({ open, onOpenChange }: { open: boolean, onOpenChange: (open: boolean) => void }) => {
  const [activeTab, setActiveTab] = useState<'documents' | 'code'>('documents');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

  const MOCK_DOCUMENTS = [
    { id: '1', title: 'Getting Started', content: 'Long content here...', tags: ['guide', 'intro'] },
    { id: '2', title: 'API Reference', content: 'API documentation...', tags: ['api', 'reference'] },
  ];

  const MOCK_CODE = [
    { id: '1', language: 'typescript', summary: 'React component', code: 'const Example = () => {...}', file_path: 'src/components/Example.tsx' },
    { id: '2', language: 'python', summary: 'FastAPI endpoint', code: '@app.get("/api/items")...', file_path: 'src/api/routes.py' },
  ];

  const toggleExpanded = (id: string) => {
    setExpandedItems(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Document Browser</DialogTitle>
          <div className="flex items-center gap-2 mt-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                placeholder="Search documents and code..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-black/30 border-white/10"
              />
            </div>
          </div>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)} className="flex-1 flex flex-col">
          <TabsList>
            <TabsTrigger value="documents" color="cyan">
              <FileText className="w-4 h-4 mr-2" />
              Documents ({MOCK_DOCUMENTS.length})
            </TabsTrigger>
            <TabsTrigger value="code" color="purple">
              <Code className="w-4 h-4 mr-2" />
              Code ({MOCK_CODE.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="documents" className="flex-1 overflow-hidden">
            <div className="h-full overflow-y-auto p-4 space-y-3">
              {MOCK_DOCUMENTS.map((doc) => {
                const isExpanded = expandedItems.has(doc.id);
                const preview = doc.content.substring(0, 200);
                const needsExpansion = doc.content.length > 200;

                return (
                  <div key={doc.id} className="bg-black/30 rounded-lg border border-white/10 p-4">
                    <h4 className="font-medium text-white/90 mb-2 flex items-center gap-2">
                      {needsExpansion && (
                        <button onClick={() => toggleExpanded(doc.id)}>
                          {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                        </button>
                      )}
                      {doc.title}
                    </h4>
                    <div className="text-sm text-gray-300">
                      {isExpanded || !needsExpansion ? doc.content : `${preview}...`}
                    </div>
                    {doc.tags && (
                      <div className="flex gap-2 mt-3">
                        {doc.tags.map(tag => (
                          <span key={tag} className="px-2 py-1 text-xs border border-white/20 rounded bg-black/20">
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </TabsContent>

          <TabsContent value="code" className="flex-1 overflow-hidden">
            <div className="h-full overflow-y-auto p-4 space-y-3">
              {MOCK_CODE.map((example) => (
                <div key={example.id} className="bg-black/30 rounded-lg border border-white/10 overflow-hidden">
                  <div className="flex items-center justify-between p-3 border-b border-white/10 bg-black/20">
                    <div className="flex items-center gap-2">
                      <Code className="w-4 h-4 text-cyan-400" />
                      <span className="px-2 py-1 text-xs bg-cyan-500/20 text-cyan-400 rounded">
                        {example.language}
                      </span>
                    </div>
                    <span className="text-xs text-gray-400">{example.file_path}</span>
                  </div>
                  <div className="p-3 text-sm text-gray-300 border-b border-white/10">{example.summary}</div>
                  <pre className="p-4 text-sm overflow-x-auto">
                    <code className="text-gray-300">{example.code}</code>
                  </pre>
                </div>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};
```

## Validation Loop

### Level 1: Syntax & Style (Immediate Feedback)

```bash
# Run after each file creation - fix before proceeding
cd archon-ui-main

# TypeScript type checking
npx tsc --noEmit

# Biome for features directory
npm run biome

# Expected: Zero errors. If errors exist, READ output and fix before proceeding.
```

### Level 2: Component Validation (Build Testing)

```bash
# Build the frontend to ensure no import errors
cd archon-ui-main
npm run build

# Expected: Clean build with no errors
# Common issues:
# - Missing imports (add them)
# - Circular dependencies (refactor imports)
# - Type mismatches (fix type definitions)
```

### Level 3: Visual Validation (Manual Testing)

```bash
# Start dev server
cd archon-ui-main
npm run dev

# Manual checks:
# 1. Navigate to http://localhost:3737/style-guide
# 2. Verify 3 tabs appear (Style Guide, Layouts, Configurators)
# 3. Click each tab and verify content renders:
#    - Style Guide: Typography, Colors, Spacing, Effects visible
#    - Layouts: Navigation explanation, 3 layout examples visible
#    - Configurators: All 8 configurators render correctly
# 4. In Layouts tab, test each example:
#    - Projects: Click different project cards, see selection change
#    - Settings: Click PowerButton icons, see cards expand/collapse
#    - Knowledge: Toggle grid/table view, see layout switch
# 5. In Configurators tab, test one configurator:
#    - GlassCard: Change settings, see live preview update, see code generate
# 6. Verify components.json accessible at http://localhost:3737/components.json
```

### Level 4: AI-Friendliness Validation

```bash
# Test components.json structure
curl http://localhost:3737/components.json | jq '.'

# Expected output: Valid JSON with categories, components, paths, usage
# Verify AI can parse:
# - Each component has "name", "path", "usage"
# - Paths are relative from project root
# - Examples point to specific line numbers

# Simulated AI Query Test:
# Query: "How do I create a horizontal scrolling card layout?"
# AI should:
# 1. Check components.json → find "CardGridLayout"
# 2. See path: archon-ui-main/src/features/projects/components/ProjectList.tsx:100-117
# 3. See pattern: "flex gap-4 overflow-x-auto with min-w-max"
# 4. Navigate to Layouts tab for visual example
```

## Final Validation Checklist

### Technical Validation

- [ ] All 14 implementation tasks completed successfully
- [ ] No TypeScript errors: `npx tsc --noEmit`
- [ ] No linting errors: `npm run biome`
- [ ] Clean build: `npm run build`
- [ ] Frontend dev server runs without errors: `npm run dev`

### Feature Validation

- [ ] 3 tabs render correctly (Style Guide, Layouts, Configurators)
- [ ] Tab navigation works smoothly (click transitions, active states)
- [ ] Style Guide tab shows all 4 foundations (Typography, Colors, Spacing, Effects)
- [ ] Layouts tab shows Navigation explanation + 4 layout examples (Projects, Settings, Knowledge, DocumentBrowser)
- [ ] Configurators tab shows all 9 configurators (GlassCard, Button, Navigation, Modal, Form, Table, Toggle, Switch, Checkbox)
- [ ] All layout examples use hard-coded data (no API calls visible in Network tab)
- [ ] Projects layout: Can select different mock projects, see styling change
- [ ] Settings layout: Can expand/collapse mock cards with PowerButton
- [ ] Knowledge layout: Can toggle grid/table view modes
- [ ] DocumentBrowser layout: Can open modal, switch tabs, see expandable content
- [ ] Projects sidebar mode: Sidebar doesn't cover main navigation (properly positioned)
- [ ] components.json file accessible at /components.json URL
- [ ] components.json has valid JSON structure
- [ ] All Radix primitives used (no native HTML selects, checkboxes, etc.)

### Code Quality Validation

- [ ] Follows Archon vertical slice architecture (features own their code)
- [ ] Uses glassmorphism styles from primitives/styles.ts
- [ ] All hard-coded examples clearly marked with MOCK_ prefix for data
- [ ] No real data fetching in layout examples (no useQuery, no service calls)
- [ ] Proper TypeScript typing (no `any` types)
- [ ] Follows existing naming conventions (camelCase for functions, PascalCase for components)
- [ ] No console.log statements left in code
- [ ] Comments explain "why" not "what" where needed

### User Experience Validation

- [ ] Tab labels are clear and descriptive
- [ ] Layout examples have explanatory text ("Use this layout for...")
- [ ] Navigation explanation is easy to understand
- [ ] Interactive elements have hover states
- [ ] Glassmorphism styling is consistent across all examples
- [ ] Dark mode works correctly for all tabs
- [ ] Responsive layout works on mobile, tablet, desktop
- [ ] No visual glitches or overlapping elements

### AI-Friendliness Validation

- [ ] components.json is valid JSON and parseable
- [ ] All component paths are correct and relative to project root
- [ ] Usage descriptions are clear and actionable
- [ ] Examples include specific line numbers where helpful
- [ ] Component categories make logical sense (navigation, layouts, cards, buttons)
- [ ] Pattern descriptions use code-friendly terminology
- [ ] No ambiguous component names

---

## Anti-Patterns to Avoid

### File Organization Anti-Patterns

- ❌ Don't create components outside the `features/style-guide` directory
- ❌ Don't mix layout examples with real feature code (Projects, Settings, Knowledge)
- ❌ Don't leave old pattern/example files after refactor
- ❌ Don't create nested subdirectories beyond `tabs/` and `layouts/`

### Code Anti-Patterns

- ❌ Don't use real data fetching in layout examples (no useQuery, no API calls)
- ❌ Don't import glassmorphism styles from anywhere except `features/ui/primitives/styles.ts`
- ❌ Don't create new glassmorphism constants - use existing `glassmorphism` and `glassCard` objects
- ❌ Don't hardcode colors - use Tailwind classes and theme variables
- ❌ Don't use `any` types - always provide proper TypeScript types
- ❌ Don't mix Framer Motion animation patterns - follow existing component patterns

### State Management Anti-Patterns

- ❌ Don't use useState for mock data in layout examples - define as constants
- ❌ Don't add localStorage persistence to hard-coded layout examples
- ❌ Don't create global state for style guide - keep it component-local
- ❌ Don't use React Context for tab navigation - simple prop drilling is fine

### Styling Anti-Patterns

- ❌ Don't inline style objects - use Tailwind classes
- ❌ Don't create custom CSS files - use Tailwind utilities
- ❌ Don't duplicate glassmorphism patterns - import from primitives
- ❌ Don't use arbitrary values without reason - prefer Tailwind tokens
- ❌ Don't forget dark mode variants - always include `dark:` prefixes

### Documentation Anti-Patterns

- ❌ Don't create verbose explanatory text - keep it concise (1-2 sentences)
- ❌ Don't include code comments in components.json - keep it data-only
- ❌ Don't use generic descriptions - be specific ("horizontal scrolling card grid" not "card layout")
- ❌ Don't forget to update components.json when adding new layout patterns

### Radix UI Anti-Patterns

- ❌ Don't use native HTML form elements (`<select>`, `<input type="checkbox">`, `<input type="radio">`)
- ❌ Don't import from `@radix-ui/react-*` directly - import from `@/features/ui/primitives/*`
- ❌ Don't create custom styled versions of Radix components - use existing primitives
- ❌ Don't forget compound component pattern - use all required parts (Trigger, Content, Item, etc.)
- ❌ Don't skip accessibility props (aria-label, aria-labelledby, id for labels)
- ❌ Don't forget TooltipProvider wrapper (already in App.tsx, don't add again)
- ❌ Don't use incorrect Radix data attributes (use `data-[state=active]` not `.active` class)
- ❌ Don't forget asChild prop when wrapping custom elements in Radix Trigger components

---

## Confidence Score

**10/10** - One-pass implementation success likelihood

**Reasoning**:
- ✅ Complete file structure provided (current → desired)
- ✅ All source components identified with exact file paths and line numbers
- ✅ All 9 configurators documented (including NavigationConfigurator that was in patterns)
- ✅ Comprehensive Radix UI primitive documentation with code examples
- ✅ Detailed implementation tasks (14 tasks) with code patterns
- ✅ Hard-coded data examples for each layout type with exact mock data structures
- ✅ components.json schema includes all Radix primitives with package names and "information_display" category
- ✅ Clear separation of concerns (3 tabs with explicit purpose)
- ✅ Validation checklist covers technical, feature, UX, and AI aspects (updated to 14 tasks, 4 layout examples)
- ✅ Anti-patterns section includes Radix-specific gotchas (8 specific rules)
- ✅ Comprehensive Radix UI patterns section with 7 primitive examples (added DocumentBrowser)
- ✅ All layout examples specify which Radix components to use
- ✅ Explicit guidance on NOT using native HTML elements
- ✅ DocumentBrowser pattern added for information display modals
- ✅ Sidebar layout positioning clarified (doesn't cover main nav, uses relative positioning)

**No Deductions**: All critical information provided, including:
- NavigationConfigurator (moved from patterns to configurators)
- DocumentBrowser pattern for structured information display
- Complete Radix UI primitive reference with compound component patterns
- Exact code examples for Tabs, Select, Checkbox, ToggleGroup, Tooltip, Dialog, DocumentBrowser
- Clear guidance on when to use Radix vs styled buttons
- Component mapping includes Radix package names and all 16 primitives
- Sidebar layout respects main navigation positioning (pl-[100px] content area)

---

## Additional Notes

### For the Implementing Agent

1. **Start with components.json** - This gives you a map of what needs to be created
2. **Create SimpleTabNavigation first** - You'll need this for the main refactor
3. **Move NavigationPattern → NavigationConfigurator** - Simple rename and file move (Task 10)
4. **Create tab container components** (StyleGuideTab, LayoutsTab, ConfiguratorsTab) before refactoring StyleGuideView
5. **For layout examples**: Copy component structure, strip functionality, add mock data
6. **CRITICAL: Use only Radix primitives** - Never use native HTML `<select>`, `<input type="checkbox">`, etc.
7. **Import Radix from primitives** - Always `@/features/ui/primitives/*`, never direct `@radix-ui/*`
8. **Sidebar positioning**: Ensure sidebar layouts use relative positioning within content area (pl-[100px])
9. **DocumentBrowser**: Full modal with tabs, search, expandable content - use Set<string> for expanded state
10. **Test each tab independently** before moving to the next
11. **Delete old files last** after verifying new implementation works

### Radix UI Quick Reference

**When implementing layout examples, use these Radix primitives:**

| Native HTML | ❌ WRONG | ✅ CORRECT Radix Primitive | Import Path |
|-------------|----------|---------------------------|-------------|
| `<select><option>` | Native dropdown | `<Select><SelectTrigger><SelectContent><SelectItem>` | `@/features/ui/primitives/select` |
| `<input type="checkbox">` | Native checkbox | `<Checkbox>` | `@/features/ui/primitives/checkbox` |
| `<input type="radio">` | Native radio | `<RadioGroup><RadioGroupItem>` | `@/features/ui/primitives/radio-group` |
| Tab buttons | Custom button tabs | `<Tabs><TabsList><TabsTrigger><TabsContent>` | `@/features/ui/primitives/tabs` |
| Modal backdrop | Custom modal | `<Dialog><DialogContent>` | `@/features/ui/primitives/dialog` |
| Toggle buttons | Button group | `<ToggleGroup><ToggleGroupItem>` | `@/features/ui/primitives/toggle-group` |
| Hover tooltip | CSS :hover | `<Tooltip><TooltipTrigger><TooltipContent>` | `@/features/ui/primitives/tooltip` |
| Context menu | Custom dropdown | `<DropdownMenu><DropdownMenuTrigger><DropdownMenuItem>` | `@/features/ui/primitives/dropdown-menu` |

**Color Prop Pattern:**
All Archon Radix primitives support color prop for theme variants:
```tsx
<TabsTrigger color="cyan">Tab</TabsTrigger>
<SelectTrigger color="purple"><SelectValue /></SelectTrigger>
<Checkbox color="blue" />
```

Available colors: `cyan`, `blue`, `purple`, `green`, `orange`, `pink`

### Complete List of Archon Radix Primitives

**Available in `archon-ui-main/src/features/ui/primitives/`:**

1. ✅ **Tabs** - Tab navigation with color variants (`tabs.tsx`)
2. ✅ **Select** - Dropdown select (`select.tsx`)
3. ✅ **Dialog** - Modal dialogs (`dialog.tsx`)
4. ✅ **Checkbox** - Checkbox with colors (`checkbox.tsx`)
5. ✅ **Switch** - Toggle switch (`switch.tsx`)
6. ✅ **Tooltip** - Hover tooltips (`tooltip.tsx`)
7. ✅ **DropdownMenu** - Context menus (`dropdown-menu.tsx`)
8. ✅ **ToggleGroup** - Button groups (`toggle-group.tsx`)
9. ✅ **RadioGroup** - Radio buttons (`radio-group.tsx`)
10. ✅ **AlertDialog** - Confirmation dialogs (`alert-dialog.tsx`)
11. ✅ **Button** - Button with variants (`button.tsx`)
12. ✅ **Card** - GlassCard component (`card.tsx`)
13. ✅ **Input** - Styled text input (`input.tsx`)
14. ✅ **Label** - Form labels (`label.tsx`)
15. ✅ **Toast** - Toast notifications (`toast.tsx`)
16. ✅ **Pill** - Custom pill component (`pill.tsx`)

**When building layout examples, use these primitives exclusively:**
- Forms → Select, Checkbox, Switch, RadioGroup, Input, Label
- Navigation → Tabs (page-level), buttons (styled pill groups)
- Filters → ToggleGroup
- Modals → Dialog, AlertDialog
- Interactive → Tooltip, DropdownMenu
- Display → Card, Button

### Implementation Summary

**Files to CREATE (10 new files):**
1. `archon-ui-main/public/components.json` - Component mapping
2. `archon-ui-main/src/features/style-guide/shared/SimpleTabNavigation.tsx` - 3-tab nav
3. `archon-ui-main/src/features/style-guide/layouts/NavigationExplanation.tsx` - Nav patterns doc
4. `archon-ui-main/src/features/style-guide/layouts/ProjectsLayoutExample.tsx` - Projects (horizontal + sidebar)
5. `archon-ui-main/src/features/style-guide/layouts/SettingsLayoutExample.tsx` - Settings bento grid
6. `archon-ui-main/src/features/style-guide/layouts/KnowledgeLayoutExample.tsx` - Knowledge grid/table
7. `archon-ui-main/src/features/style-guide/layouts/DocumentBrowserExample.tsx` - Info display modal
8. `archon-ui-main/src/features/style-guide/tabs/StyleGuideTab.tsx` - Foundations container
9. `archon-ui-main/src/features/style-guide/tabs/LayoutsTab.tsx` - Layouts container
10. `archon-ui-main/src/features/style-guide/tabs/ConfiguratorsTab.tsx` - Configurators container

**Files to MOVE (1 file):**
- `patterns/NavigationPattern.tsx` → `configurators/NavigationConfigurator.tsx`

**Files to MODIFY (2 files):**
- `archon-ui-main/src/features/style-guide/components/StyleGuideView.tsx` - Main refactor
- `archon-ui-main/src/features/style-guide/index.ts` - Update exports

**Files to DELETE (3 directories):**
- `archon-ui-main/src/features/style-guide/patterns/` - All files
- `archon-ui-main/src/features/style-guide/examples/` - All files
- `archon-ui-main/src/features/style-guide/shared/PillNavigation.tsx` - If not used elsewhere

**Files to KEEP (13 files - no changes):**
- All foundations (Typography, Colors, Spacing, Effects)
- All configurators (GlassCard, Button, Modal, Form, Table, Toggle, Switch, Checkbox)
- Shared utilities (CodeDisplay, ConfiguratorCard, etc.)

### Future Enhancements (Out of Scope)

- Interactive layout customizer (adjust grid columns, spacing, etc.)
- Export layout examples as code snippets
- Component variant preview gallery
- Search functionality in components.json
- Layout comparison tool (side-by-side)
- Responsive breakpoint visualizer
- Code syntax highlighting library integration for DocumentBrowser
