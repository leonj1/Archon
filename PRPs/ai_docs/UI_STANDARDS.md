# Archon UI Standards

**Audience**: AI agents performing automated UI audits and refactors
**Purpose**: Single source of truth for UI patterns, violations, and automated detection
**Usage**: Run `/archon:archon-ui-consistency-review` to scan code against these standards

---

## 1. TAILWIND V4

### Rules
- **NO dynamic class construction** - Tailwind scans source code as plain text at build time
  - NEVER: `` `bg-${color}-500` ``, `` `ring-${color}-500` ``, `` `shadow-${size}` ``
  - Use static lookup objects instead
- **Bare HSL values in CSS variables** - NO `hsl()` wrapper
  - Correct: `--background: 0 0% 98%;`
  - Wrong: `--background: hsl(0 0% 98%);`
- **CSS variables allowed in arbitrary values** - Utility name must be static
  - Correct: `bg-[var(--accent)]`
  - Wrong: `` `bg-[var(--${colorName})]` ``
- **Use @theme inline** to map CSS vars to Tailwind utilities
- **Define @custom-variant dark** - Required for `dark:` to work in v4

### Anti-Patterns
```tsx
// ❌ Dynamic classes (NO CSS GENERATED)
const color = "cyan";
<div className={`bg-${color}-500`} />
<div className={`focus-visible:ring-${color}-500`} />  // Common miss!

// ❌ Inline styles for visual CSS
<div style={{ backgroundColor: "#fff" }} />
```

### Good Examples
```tsx
// ✅ Static lookup for discrete variants
const colorClasses = {
  cyan: "bg-cyan-500 text-cyan-900 ring-cyan-500",
  purple: "bg-purple-500 text-purple-900 ring-purple-500",
};
<div className={colorClasses[color]} />

// ✅ CSS variables for dynamic values
<div
  className="bg-[var(--accent)] ring-[var(--accent)]"
  style={{ "--accent": "oklch(0.75 0.12 210)" }}
/>
```

### Automated Scans
```bash
# All dynamic class construction patterns
grep -rn "className.*\`.*\${.*}\`" [path] --include="*.tsx"
grep -rn "bg-\${.*}\|text-\${.*}\|border-\${.*}" [path] --include="*.tsx"
grep -rn "ring-\${.*}\|shadow-\${.*}\|outline-\${.*}\|opacity-\${.*}" [path] --include="*.tsx"

# Inline visual styles (not CSS vars)
grep -rn "style={{.*backgroundColor\|color:\|padding:" [path] --include="*.tsx"
```

**Fix Pattern**: Add all properties to static variant object (checked, glow, focusRing, hover)

---

## 2. LAYOUT & RESPONSIVE

### Rules
- **Responsive grids** - NEVER fixed columns without breakpoints
  - Use: `grid-cols-1 md:grid-cols-2 lg:grid-cols-4`
- **Constrain horizontal scroll** - Parent must have `w-full` or `max-w-*`
- **Add scrollbar-hide** to all `overflow-x-auto` containers
- **min-w-0 on flex parents** containing scroll containers (prevents page expansion)
- **Text truncation** - Always use `truncate`, `line-clamp-N`, or `break-words`
- **Desktop-primary** - Optimize for desktop, add responsive breakpoints down

### Anti-Patterns
```tsx
// ❌ Fixed grid (breaks mobile)
<div className="grid grid-cols-4">

// ❌ Unconstrained scroll (page becomes horizontally scrollable)
<div className="overflow-x-auto">
  <div className="min-w-max">

// ❌ Flex parent without min-w-0 (page expansion)
<div className="flex gap-6">
  <main className="flex-1">  {/* MISSING min-w-0! */}
    <div className="overflow-x-auto">
```

### Good Examples
```tsx
// ✅ Responsive grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

// ✅ Constrained horizontal scroll
<div className="w-full">
  <div className="overflow-x-auto scrollbar-hide">
    <div className="flex gap-4 min-w-max">

// ✅ Flex parent with scroll container
<div className="flex gap-6">
  <main className="flex-1 min-w-0">  {/* min-w-0 CRITICAL */}
```

### Automated Scans
```bash
# Non-responsive grids
grep -rn "grid-cols-[2-9]" [path] --include="*.tsx" | grep -v "md:\|lg:\|xl:"

# Unconstrained scroll
grep -rn "overflow-x-auto" [path] --include="*.tsx"
# Then manually verify parent has w-full

# Missing text truncation
grep -rn "<h[1-6]" [path] --include="*.tsx" | grep -v "truncate\|line-clamp"

# Missing min-w-0
grep -rn "flex-1" [path] --include="*.tsx" | grep -v "min-w-0"
```

**Fix Pattern**: Wrap scroll in `<div className="w-full">`, add responsive breakpoints to grids

---

## 3. THEMING

### Rules
- **Every visible color needs `dark:` variant**
- **Structure identical** between themes (only colors/opacity change)
- **Use tokens** for both light and dark (`--bg` and redefine in `.dark`)

### Anti-Patterns
```tsx
// ❌ No dark variant
<div className="bg-white text-gray-900">

// ❌ Different structure in dark mode
{theme === 'dark' ? <ComponentA /> : <ComponentB />}
```

### Good Examples
```tsx
// ✅ Both themes
<div className="bg-white dark:bg-black text-gray-900 dark:text-white">
```

### Automated Scans
```bash
# Colors without dark variants
grep -rn "bg-.*-[0-9]" [path] --include="*.tsx" | grep -v "dark:"
```

**Fix Pattern**: Add `dark:` variant for every color, border, shadow

---

## 4. RADIX UI

### Rules
- **Use Radix primitives** - NEVER native `<select>`, `<input type="checkbox">`, `<input type="radio">`
- **Compose with asChild** - Don't wrap, attach behavior to your components
- **Style via data attributes** - `[data-state="open"]`, `[data-disabled]`
- **Use Portal** for overlays with proper z-index

### Anti-Patterns
```tsx
// ❌ Native HTML
<select><option>...</option></select>
<input type="checkbox" />

// ❌ Wrong composition
<Dialog.Trigger><button>Open</button></Dialog.Trigger>
```

### Good Examples
```tsx
// ✅ Radix with asChild
<Dialog.Trigger asChild>
  <Button>Open</Button>
</Dialog.Trigger>

// ✅ Radix primitives
<Select><SelectTrigger /></Select>
<Checkbox />
```

### Automated Scans
```bash
# Native HTML form elements
grep -rn "<select>\|<option>" [path] --include="*.tsx"
grep -rn "type=\"checkbox\"\|type=\"radio\"" [path] --include="*.tsx"
```

**Fix Pattern**: Import from `@/features/ui/primitives/`, use Radix primitives

---

## 5. CENTRALIZED STYLING (styles.ts)

### CRITICAL RULE: Use glassCard & glassmorphism from styles.ts

**Location**: `@/features/ui/primitives/styles.ts`

All styling definitions MUST come from the centralized `glassCard` and `glassmorphism` objects in styles.ts. Do NOT duplicate style objects in components.

### Anti-Patterns
```tsx
// ❌ WRONG - Duplicating style definitions
const edgeColors = {
  cyan: { solid: "bg-cyan-500", gradient: "from-cyan-500/40", border: "border-cyan-500/30" },
  // ... more colors
};

// ❌ WRONG - Local variant objects
const colorVariants = {
  cyan: "shadow-cyan-500/20",
  blue: "shadow-blue-500/20",
};
```

### Good Examples
```tsx
// ✅ CORRECT - Use centralized definitions
const edgeStyle = glassCard.edgeColors[edgeColor];
<div className={edgeStyle.border}>
  <div className={edgeStyle.solid} />
  <div className={edgeStyle.gradient} />
</div>

// ✅ CORRECT - Use glassCard variants
const glowVariant = glassCard.variants[glowColor];
<div className={cn(glowVariant.border, glowVariant.glow, glowVariant.hover)} />

// ✅ CORRECT - Use glassmorphism tokens
<div className={cn(glassmorphism.background.card, glassmorphism.border.default)} />
```

### What's in styles.ts

**glassCard object:**
- `blur` - Blur intensity levels (sm, md, lg, xl, 2xl, 3xl)
- `transparency` - Glass transparency (clear, light, medium, frosted, solid)
- `variants` - Color variants with border, glow, hover (purple, blue, cyan, green, orange, pink, red)
- `edgeColors` - Edge-lit styling with solid, gradient, border, bg
- `tints` - Colored glass tints
- `sizes` - Padding variants (none, sm, md, lg, xl)
- `outerGlowSizes` - Glow size variants per color
- `innerGlowSizes` - Inner glow size variants per color
- `edgeLit` - Edge-lit effects (position, color with line/glow/gradient)

**glassmorphism object:**
- `background` - Background variations
- `border` - Border styles
- `interactive` - Interactive states
- `animation` - Animation presets
- `shadow` - Shadow effects with neon glow

### Automated Scans
```bash
# Check for duplicate edge color definitions
grep -rn "const edgeColors = {" [path]/primitives --include="*.tsx"

# Check for duplicate variant objects (should use glassCard.variants)
grep -rn "const.*Variants = {" [path]/primitives --include="*.tsx" -A 3 | grep "cyan:\|blue:\|purple:"

# Check imports - all primitives should import from styles.ts
grep -rn "from \"./styles\"" [path]/primitives --include="*.tsx" --files-without-match
```

**Fix Pattern**: Import glassCard/glassmorphism from styles.ts, use object properties instead of duplicating

---

## 6. PRIMITIVES LIBRARY

### Archon Components
- **Card** - For all glassmorphism effects
- **DataCard** - Cards with header/content/footer slots
- **PillNavigation** - Tab navigation (NEVER create custom)
- **styles.ts** - Central styling definitions (ALWAYS import)

### Rules
- **Use Card props** - blur, transparency, edgePosition, glowColor (don't hardcode)
- **Import from styles.ts** - Don't duplicate blur/glow classes
- **All primitive props must affect rendering** - No unused props
- **Use glassCard for card styling** - edgeColors, variants, tints, sizes
- **Use glassmorphism for general styling** - background, border, shadow, animation

### Anti-Patterns
```tsx
// ❌ Hardcoded glassmorphism
<div className="backdrop-blur-md bg-white/10 border">

// ❌ Custom pill navigation
<div className="rounded-full backdrop-blur-sm">
  <button>...</button>
</div>

// ❌ Primitive with unused prop
interface CardProps { glowColor?: string } // But never used in return!
```

### Good Examples
```tsx
// ✅ Use Card primitive
<Card blur="lg" transparency="light" edgePosition="top" edgeColor="cyan">

// ✅ Use PillNavigation
<PillNavigation items={...} colorVariant="orange" />

// ✅ Import from styles.ts
import { glassCard, cn } from '@/features/ui/primitives/styles';
<div className={cn(glassCard.blur.md, glassCard.transparency.light)}>
```

### Automated Scans
```bash
# Hardcoded glassmorphism
grep -rn "backdrop-blur.*bg-white/.*border" [path] --include="*.tsx"

# Hardcoded pill navigation
grep -rn "rounded-full.*flex gap-" [path] --include="*.tsx"

# Primitives defining own blur classes
grep -rn "const blurClasses\|backdrop-blur-md" [path]/primitives --include="*.tsx"
```

**Manual Check**: Read primitive interfaces, verify all props used in return statement

---

## 6. ACCESSIBILITY

### Rules
- **Keyboard support on all interactive elements**
  - `<div onClick={...}>` needs `role="button"`, `tabIndex={0}`, `onKeyDown`
  - Handle Enter and Space keys
- **ARIA attributes** - `aria-selected`, `aria-current`, `aria-expanded`
- **Never remove focus rings** - Must be color-specific and static

### Anti-Patterns
```tsx
// ❌ Clickable div without keyboard
<div onClick={handler}>Click me</div>

// ❌ role="button" without keyboard
<div onClick={handler} role="button">  // Missing onKeyDown!

// ❌ Clickable icon without button wrapper
<ChevronRight onClick={handler} className="cursor-pointer" />
```

### Good Examples
```tsx
// ✅ Full keyboard support on div
<div
  role="button"
  tabIndex={0}
  onClick={handler}
  onKeyDown={(e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handler();
    }
  }}
  aria-selected={isSelected}
>

// ✅ Clickable icon wrapped in button
<button
  type="button"
  aria-label="Expand menu"
  aria-expanded={isExpanded}
  onClick={handler}
  onKeyDown={(e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handler();
    }
  }}
  className="focus:outline-none focus:ring-2"
>
  <ChevronRight className="h-4 w-4" />
</button>
```

### Automated Scans
```bash
# Interactive divs without keyboard
grep -rn "onClick.*role=\"button\"" [path] --include="*.tsx"
# Then manually verify onKeyDown exists

# Icons with onClick (should be wrapped in button)
grep -rn "<[A-Z].*onClick={" [path] --include="*.tsx" | grep -v "<button\|<Button"
```

**Fix Pattern**:
- Add onKeyDown handler with Enter/Space, add tabIndex={0}, add ARIA
- Wrap clickable icons in `<button type="button">` with proper ARIA attributes

---

## 7. TYPESCRIPT & API CONTRACTS

### Rules
- **Async functions return Promise<void>** - Not just `void` if awaited
- **All props must be used** - If prop in interface, must affect rendering
- **Color types consistent** - Use "green" not "emerald" across components (avoid emerald entirely)
- **Run `tsc --noEmit`** to catch type errors
- **Use `satisfies` for lookup objects** - Enforce type coverage on color variants
- **120 character line limit** - Split long class strings into arrays with `.join(" ")`

### Anti-Patterns
```tsx
// ❌ Async typed as void
setEnabled: (val: boolean) => void;  // But implemented as async!

// ❌ Unused prop
interface CardProps { glowColor?: string }
return <div>  {/* glowColor never used! */}

// ❌ Color type mismatch
// PillNavigation: colorVariant?: "emerald"
// Select: color?: "green"  // Should match!

// ❌ Long class strings (exceeds 120 chars)
const activeClasses = {
  blue: "data-[state=active]:bg-blue-500/20 dark:data-[state=active]:bg-blue-400/20 data-[state=active]:text-blue-700 dark:data-[state=active]:text-blue-300 data-[state=active]:border data-[state=active]:border-blue-400/50",
};

// ❌ Lookup objects without type safety
const colorClasses = {
  cyan: "bg-cyan-500",
  blue: "bg-blue-500",
  // What if we forget purple? No compile error!
};
```

### Good Examples
```tsx
// ✅ Correct async type
setEnabled: (val: boolean) => Promise<void>;

// ✅ All props used
interface CardProps { glowColor?: string }
const glow = glassCard.variants[glowColor];
return <div className={glow.border} />

// ✅ Consistent color types (always use "green", never "emerald")
type Color = "purple" | "blue" | "cyan" | "green" | "orange" | "pink";

// ✅ Split long class strings (under 120 chars per line)
const activeClasses = {
  blue: [
    "data-[state=active]:bg-blue-500/20 dark:data-[state=active]:bg-blue-400/20",
    "data-[state=active]:text-blue-700 dark:data-[state=active]:text-blue-300",
    "data-[state=active]:border data-[state=active]:border-blue-400/50",
  ].join(" "),
};

// ✅ Type-safe lookup objects with satisfies
type Color = "purple" | "blue" | "cyan" | "green" | "orange" | "pink";
const colorClasses = {
  purple: "bg-purple-500",
  blue: "bg-blue-500",
  cyan: "bg-cyan-500",
  green: "bg-green-500",
  orange: "bg-orange-500",
  pink: "bg-pink-500",
} satisfies Record<Color, string>;  // TypeScript enforces all colors present!
```

### Automated Scans
```bash
# TypeScript errors
npx tsc --noEmit [path] 2>&1 | grep "error TS"

# Color type inconsistencies (must use "green" not "emerald")
grep -rn "emerald" [path] --include="*.tsx" --include="*.ts"

# Line length violations (over 120 chars)
grep -rn ".\{121,\}" [path] --include="*.tsx" | grep className

# Lookup objects without satisfies
grep -rn "const.*Classes = {" [path]/primitives --include="*.tsx" -A 5 | grep -v "satisfies"

# Unused props (manual)
grep -rn "interface.*Props" [path]/primitives --include="*.tsx" -A 10
# Then verify each prop name appears in return statement
```

**Fix Pattern**:
- Split long strings into arrays: `["class1", "class2"].join(" ")`
- Add `satisfies Record<ColorType, string>` to lookup objects
- Replace all "emerald" with "green" + update RGB to green-500 (34,197,94)
- Wire all props to rendering

---

## 8. FUNCTIONAL LOGIC

### Rules
- **Interactive UI must be functional** - Especially in demos/examples
- **State changes must affect rendering**
  - Filter state → must filter data before .map()
  - Sort state → must sort data
  - Drag-drop → must have state + onDrop handler
- **Props must do what they advertise** - If edgePosition accepts "left", it must work

### Anti-Patterns
```tsx
// ❌ Filter that doesn't filter
const [filter, setFilter] = useState("all");
return <div>{items.map(...)}</div>  // items not filtered!

// ❌ Drag-drop without state
{[1,2,3].map(num => <DraggableCard />)}  // Always snaps back!

// ❌ Prop that does nothing
edgePosition="left"  // But only "top" is implemented!
```

### Good Examples
```tsx
// ✅ Working filter
const [filter, setFilter] = useState("all");
const filtered = useMemo(() =>
  filter === "all" ? items : items.filter(i => i.type === filter),
[items, filter]);
return <div>{filtered.map(...)}</div>

// ✅ Working drag-drop
const [items, setItems] = useState([...]);
const handleDrop = (id, index) => { /* reorder logic */ };
return <>{items.map((item, i) => <DraggableCard onDrop={handleDrop} />)}</>

// ✅ All edge positions work
if (edgePosition === "top") { /* top impl */ }
if (edgePosition === "left") { /* left impl */ }
// etc for all accepted values
```

### Manual Checks
```bash
# Look for state that never affects rendering
# Pattern: setState called but variable not used in .filter/.sort/.map

# Check prop implementations
# Pattern: Interface accepts values but switch/if only handles subset
```

**Fix Pattern**: Wire state to data transformations (filter/sort/map), add missing implementations

---

## AUTOMATED SCAN REFERENCE

Run ALL these scans during review:

### Critical (Breaking)
- Dynamic classes: `grep -rn "className.*\`.*\${.*}\`\|bg-\${.*}\|ring-\${.*}" [path]`
- Non-responsive grids: `grep -rn "grid-cols-[2-9]" [path] | grep -v "md:\|lg:"`
- Unconstrained scroll: `grep -rn "overflow-x-auto" [path]` (verify w-full parent)
- Native HTML: `grep -rn "<select>\|type=\"checkbox\"" [path]`
- Emerald usage: `grep -rn "emerald" [path] --include="*.tsx" --include="*.ts"` (must use "green")

### High Priority
- Missing keyboard: `grep -rn "onClick.*role=\"button\"" [path]` (verify onKeyDown)
- Clickable icons: `grep -rn "<[A-Z].*onClick={" [path] --include="*.tsx" | grep -v "<button\|<Button"`
- Missing dark mode: `grep -rn "bg-.*-[0-9]" [path] | grep -v "dark:"`
- Hardcoded glass: `grep -rn "backdrop-blur.*bg-white/.*border" [path]`
- Missing min-w-0: `grep -rn "flex-1" [path] | grep -v "min-w-0"`
- Duplicate styling: `grep -rn "const edgeColors = {\|const.*Variants = {" [path]/primitives`

### Medium Priority
- TypeScript: `npx tsc --noEmit [path] 2>&1 | grep "error TS"`
- Line length: `grep -rn ".\{121,\}" [path] --include="*.tsx" | grep className`
- Missing satisfies: `grep -rn "const.*Classes = {" [path]/primitives -A 5 | grep -v "satisfies"`
- Props unused: Manual check interfaces vs usage

---

## QUICK REFERENCE

### Breakpoints
- sm: 640px | md: 768px | lg: 1024px | xl: 1280px | 2xl: 1536px

### Color Variant Checklist (for primitives with colors)
Every color object MUST have:
- [ ] `checked` or `active` state classes
- [ ] `glow` effect
- [ ] `focusRing` - STATIC class like `"focus-visible:ring-cyan-500"`
- [ ] `hover` state
- [ ] All 6 colors: purple, blue, cyan, green, orange, pink

### Common Patterns

**Horizontal Scroll (Archon Standard)**
```tsx
<div className="w-full">
  <div className="overflow-x-auto scrollbar-hide">
    <div className="flex gap-4 min-w-max">
      {items.map(i => <Card className="w-72 shrink-0" />)}
```

**Responsive Grid**
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
```

**Flex + Scroll Container**
```tsx
<div className="flex gap-6">
  <aside className="w-64 shrink-0">Sidebar</aside>
  <main className="flex-1 min-w-0">  {/* min-w-0 REQUIRED */}
    {/* scroll containers here */}
```

**Color Variants (Static Lookup)**
```tsx
const variants = {
  cyan: {
    checked: "data-[state=checked]:bg-cyan-500/20",
    glow: "shadow-[0_0_15px_rgba(34,211,238,0.5)]",
    focusRing: "focus-visible:ring-cyan-500",  // STATIC!
    hover: "hover:bg-cyan-500/10",
  },
  // ... repeat for all colors
};
```

**Keyboard Support**
```tsx
<div
  role="button"
  tabIndex={0}
  onClick={handler}
  onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && handler()}
  aria-selected={isSelected}
>
```

---

## SCORING VIOLATIONS

### Critical (-3 points each)
- Dynamic class construction
- Missing keyboard support on interactive
- Non-responsive grids causing horizontal scroll
- TypeScript errors

### High (-2 points each)
- Unconstrained scroll containers
- Props that do nothing
- Non-functional UI logic (filter/sort/drag-drop)
- Missing dark mode variants

### Medium (-1 point each)
- Native HTML form elements
- Hardcoded glassmorphism
- Missing text truncation
- Color type inconsistencies

**Grading Scale:**
- 0 critical violations: A (9-10/10)
- 1 critical: B (7-8/10)
- 2-3 critical: C (5-6/10)
- 4+ critical: F (1-4/10)

---

## ADDING NEW RULES

When code review finds an issue not caught by automated review:

1. **Identify which section** it belongs to (Tailwind? Layout? A11y?)
2. **Add to that section**:
   - Rule (what to do)
   - Anti-Pattern example
   - Good example
   - Automated scan (if possible)
3. **Add scan to AUTOMATED SCAN REFERENCE**
4. **Done** - Next review will catch it

**Goal**: Eventually eliminate manual code reviews entirely.
