# UI_STANDARDS.md

**Audience**: AI agents performing automated UI audits and refactors.
**Scope**: Radix Primitives + Tailwind CSS (v4) + Responsive (Flexbox-first) with **Light** and **Dark** themes.

**How to use**: Treat **Rules** as MUST, **Anti‑Patterns** as MUST NOT. Prefer the **Good Examples** verbatim unless there's a documented exception.

---

## 0) Project‑wide Conventions (applies to all sections)

**Rules**
- Use **no inline styles** (`style=""`) except when setting CSS variables (e.g., `style={{ "--accent": token }}`). Everything else must use Tailwind utilities or predeclared component classes.
- Use a **single source of truth** for design tokens via Tailwind v4 `@theme` variables (colors, spacing, radii, shadows, breakpoints). Never invent ad‑hoc hex values or pixel sizes.
- Keep markup **semantic and accessible**. Preserve focus outlines and keyboard navigation.
- Prefer **wrapper components** (e.g., `<Button variant="primary" />`) that centralize class lists over duplicating long utility strings across the app.
- Maintain a **z‑index scale** (e.g., base=0, dropdown=30, overlay=40, modal=50, toast=60) and stick to it.
- **Desktop-primary with responsive adaptations**: Optimize for desktop by default and add breakpoint rules for tablets/phones.
- Use **Radix UI primitives** for all interactive elements (Select, Checkbox, RadioGroup, Dialog, etc.) - never native HTML form elements.
- Use **shared component primitives** (Card, PillNavigation, etc.) from `@/features/ui/primitives/` instead of hardcoding repeated patterns.

**Anti‑Patterns**
- Arbitrary values like `bg-[#12abef]`, `text-[17px]`, `w-[913px]` in markup (unless promoted to tokens or used as static one-offs).
- Global layout hacks (e.g., `body { overflow: hidden }`) to "fix" scroll; fix the root cause instead.
- Competing styles on the same element (e.g., `w-full w-1/2`, `px-4 px-8`).
- Native HTML form elements (`<select>`, `<input type="checkbox">`, `<input type="radio">`) - use Radix primitives.
- Hardcoding glassmorphism, edge-lit effects, or pill navigation - use shared primitives.

---

## 1) Radix Primitives

**Rules**
- **Compose, don’t wrap**: use `asChild` to attach Radix behavior to your button/link components.  
- **Use the documented structure** for each primitive (e.g., `Root/Trigger/Portal/Overlay/Content/Close` for Dialog).  
- **Style via your classes and Radix data attributes** (e.g., `[data-state="open"]`, `[data-disabled]`) instead of targeting internal DOM.  
- **Layering**: use `Portal` and your z‑index scale for overlays/popovers; avoid random `z-[9999]`.  
- **A11y**: never remove focus rings or ARIA attributes that primitives rely on.

**Anti‑Patterns**
- Deep styling of internal nodes (e.g., selecting Radix’s internal class names or structure).
- Manually toggling open/close state without Radix APIs.
- Mixing multiple portaled surfaces with arbitrary z‑indices (dialogs behind popovers, etc.).

**Good Examples**
```tsx
// Compose a Trigger with your Button using asChild
<Dialog.Root>
  <Dialog.Trigger asChild>
    <Button variant="primary">Open</Button>
  </Dialog.Trigger>
  <Dialog.Portal>
    <Dialog.Overlay className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40" />
    <Dialog.Content
      className="fixed left-1/2 top-1/2 z-50 w-[min(90vw,38rem)] -translate-x-1/2 -translate-y-1/2 rounded-lg
                 bg-surface/95 dark:bg-surface-dark/95 shadow-xl p-6 focus:outline-none">
      <Dialog.Title className="text-lg font-semibold">Title</Dialog.Title>
      <Dialog.Description className="mt-1 text-muted-foreground">
        Description
      </Dialog.Description>
      <div className="mt-6 flex justify-end gap-2">
        <Dialog.Close asChild><Button variant="ghost">Cancel</Button></Dialog.Close>
        <Button variant="primary">Confirm</Button>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
```

```css
/* State-driven styling via data attributes */
.popover-content[data-state="open"] { /* animations, borders, etc. */ }
```

---

## 2) Tailwind CSS (v4)

**Rules**
- **Define tokens properly**: Variables in `:root` and `.dark`, then map to Tailwind with `@theme inline`.
```css
@import "tailwindcss";

:root {
  --background: hsl(0 0% 98%);
  --foreground: hsl(240 10% 3.9%);
  --border: hsl(240 5.9% 90%);
  --radius: 0.5rem;
  color-scheme: light;
}

.dark {
  --background: hsl(0 0% 0%);
  --foreground: hsl(0 0% 100%);
  --border: hsl(240 3.7% 15.9%);
  color-scheme: dark;
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-border: var(--border);
  --radius-lg: var(--radius);
  --radius-md: calc(var(--radius) - 2px);
}
```

- **CRITICAL: NO dynamic class name construction**. Tailwind processes source code as **plain text at BUILD time**, not runtime. It cannot understand variables, string concatenation, or template literals.
- **CSS variables ARE allowed in arbitrary values** as long as the utility name is static (e.g., `bg-[var(--accent)]`, `border-[color:var(--accent)]`).
- **Use static class lookup objects** for discrete variants (e.g., `const colorClasses = { cyan: "bg-cyan-500 text-cyan-700", ... }`).
- **Use CSS variables pattern** for flexible/continuous values (colors, alphas, glows, gradients).
- **Conditional classes must be complete strings** (use `cn()` helper with full class names, not interpolated fragments).
- **Arbitrary values are allowed** if written as complete static strings in source code (e.g., `shadow-[0_0_30px_rgba(34,211,238,0.4)]`).
- **Inline style allowed ONLY for CSS variables** (e.g., `style={{ "--accent": token }}`), never for direct visual CSS.
- **`@layer` and `@apply` are still valid** in v4 - use them for base styles and component classes. For custom utilities, register with `@utility` first.
- **Dark mode**: use `dark:` variants consistently for colors, borders, shadows (and add `.dark` on `<html>`).
- **No arbitrary values** unless promoted to tokens or used as static one-offs; if you need a value repeatedly, add it to `@theme`.
- **Reference tokens** for any custom CSS (e.g., `border-radius: var(--radius-md)`).
- **If referencing vars inside vars**, use `@theme inline` to avoid resolution pitfalls.

**Anti‑Patterns**
- **Dynamic class construction**: `bg-${color}-500`, `` `text-${textColor}-700` ``, `className={isActive ? \`bg-${activeColor}-500\` : ...}` - CSS WILL NOT BE GENERATED.
- **String interpolation for class names**: Template literals with variables, computed class names.
- `style="..."` for visual styling (except setting local CSS vars).
- Mixing utility classes that conflict or duplicate a property.
- Introducing new colors/sizes ad‑hoc instead of defining in `:root`/`.dark` and mapping via `@theme inline`.

**Good Examples**

### Pattern A: Lookup Map (discrete variants)
```tsx
// ✅ CORRECT - Static class lookup object for finite set of variants
const colorClasses = {
  cyan: "bg-cyan-500 text-cyan-700 border-cyan-500/50",
  purple: "bg-purple-500 text-purple-700 border-purple-500/50",
  blue: "bg-blue-500 text-blue-700 border-blue-500/50",
};
<div className={colorClasses[color]} />

// ✅ CORRECT - Conditional with complete class names
<div className={isActive ? "bg-cyan-500 text-white" : "bg-gray-500 text-gray-300"} />

// ✅ CORRECT - Use cn() helper with complete class strings
<div className={cn(
  "base-classes",
  isActive && "bg-cyan-500 text-white",
  isPinned && "border-purple-500 shadow-lg"
)} />
```

### Pattern B: CSS Variables (flexible values)
```tsx
// ✅ CORRECT - CSS variables in arbitrary values (utility name is static)
// In CSS: :root { --accent: oklch(0.75 0.12 210); }
<div className="bg-[var(--accent)] border-[color:var(--accent)]" />

// ✅ CORRECT - Set variable via inline style, use in static utilities
<div
  className="bg-[var(--glass-bg)] border-[color:var(--accent)] shadow-[0_0_24px_color-mix(in_oklab,var(--accent)_35%,transparent)]"
  style={{ "--accent": "oklch(0.75 0.12 210)" } as React.CSSProperties}
/>

// ✅ CORRECT - Named accent classes that set CSS variables
// In CSS: .accent-cyan { --accent: var(--color-cyan-500); }
const accentClass = {
  cyan: "accent-cyan",
  orange: "accent-orange",
} as const;
<div className={cn("bg-[var(--accent)]", accentClass[color])} />
```

### Anti-Patterns
```tsx
// ❌ BROKEN - Dynamic class construction (CSS NOT GENERATED)
const color = "cyan";
<div className={`bg-${color}-500`} />  // NO CSS OUTPUT
<div className={`text-${textColor}-700 border-${borderColor}-500`} />  // NO CSS OUTPUT

// ❌ BROKEN - Inline style for visual CSS (use variables instead)
<div style={{ backgroundColor: "#12abef" }} />  // Should be className or CSS variable

// ✅ CORRECT alternative - Use CSS variable
<div className="bg-[var(--accent)]" style={{ "--accent": "#12abef" } as React.CSSProperties} />
```

```tsx
// Centralized Button component (preferred over scattered long class strings)
export function Button({ variant = "primary", className = "", ...props }) {
  const base =
    "inline-flex items-center gap-2 rounded-[var(--radius-md)] px-3 py-2 text-sm font-medium " +
    "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 " +
    "transition-colors";
  const variants = {
    primary:
      "bg-brand-500 text-white hover:brightness-110 dark:text-white " +
      "focus-visible:outline-brand-500",
    ghost:
      "bg-transparent text-fg dark:text-fg-dark hover:bg-black/5 dark:hover:bg-white/10"
  };
  return <button className={[base, variants[variant], className].join(' ')} {...props} />;
}
```

```css
/* Local component CSS using tokens (no arbitrary values) */
.card {
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  background: color-mix(in oklab, var(--color-bg) 92%, transparent);
}
.dark .card {
  background: color-mix(in oklab, var(--color-bg-dark) 92%, transparent);
}
```

---

## 3) Responsive Layout (Flexbox‑first)

**Rules**
- **Desktop-primary with responsive adaptations**: Optimize for desktop by default and add breakpoint rules (`md:`, `lg:`, `xl:`) for tablets/phones.
- Prefer **fluid sizing**: `w-full`, percentages, or flex fractions; constrain with `max-w-*` where needed.
- Use **Flexbox** for 1‑D layouts; enable `flex-wrap` or responsive `flex-col md:flex-row` when layouts must adapt.
- Use **`min-w-0` (or `min-h-0` for column layouts)** on flex children that contain text/images to allow proper shrinking without overflow.
- **CRITICAL: Constrain horizontal scroll containers**. When using `overflow-x-auto`, parent MUST have `w-full` or `max-w-*` to prevent forcing entire page width expansion.
- Use **`overflow-x-auto`** only on intended horizontal scroll regions; give scroll items `shrink-0`.
- **Hide scrollbars on horizontal scroll**: Add `scrollbar-hide` class to `overflow-x-auto` containers for cleaner UI (scrollbar-hide utility defined in index.css).
- **Responsive grid columns**: NEVER use fixed grid columns (e.g., `grid-cols-4`) without responsive breakpoints. Use `grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4`.
- **Text truncation**: Always handle long text with `truncate` (single line), `line-clamp-N` (multi-line), or `break-words max-w-full` (wrap).
- For full‑height sections, prefer **`min-h-[100dvh]`** (or allow page scroll) instead of rigid `h-screen` on mobile.
- Keep **spacing with gaps** (`gap-*`) rather than ad‑hoc margins between siblings.
- **Breakpoint reference**: `sm`=640px, `md`=768px, `lg`=1024px, `xl`=1280px, `2xl`=1536px.
- **Test at**: 375px (mobile), 768px (tablet), 1024px (laptop), 1440px+ (desktop).

**Anti‑Patterns**
- Fixed pixel widths on layout containers (e.g., `w-[500px]`) without `max-w-*` constraint.
- Blanket `overflow-hidden` on large containers/pages (clips popovers, toasts, dialogs).
- **Unconstrained scroll containers**: Using `min-w-max` inside `overflow-x-auto` without parent `w-full` - forces entire page to expand horizontally.
- **CRITICAL: Flex parent without min-w-0 containing scroll container**. **SYMPTOM**: Scroll container forces ENTIRE PAGE to expand horizontally, UI controls (toggles, buttons) shift off-screen. The flex child refuses to shrink below its content's natural width, causing page-wide horizontal scroll.
- **Fixed grid columns**: `grid-cols-4` on all screen sizes breaks mobile. **SYMPTOM**: Page scrolls horizontally, UI controls (grid/list toggles, buttons) shift off-screen and become inaccessible.
- **Missing text truncation**: Long text that breaks layout without `truncate` or `line-clamp-*`.
- **Absolute positioning for UI controls**: Fixed position elements shift off-screen when content overflows.
- 100vh "traps" on mobile that hide content behind browser UI; avoid locking scroll inside view‑height panels.
- Mixing contradictory sizing on a single element (e.g., `flex-1` with `w-64`).

**Good Examples**
```tsx
// ✅ CORRECT - Responsive two-column layout
<div className="mx-auto max-w-6xl px-4">
  <div className="flex flex-col md:flex-row gap-6">
    <aside className="w-full md:w-64 shrink-0">…sidebar…</aside>
    <main className="flex-1 min-w-0">…content that can shrink without overflow…</main>
  </div>
</div>

// ✅ CORRECT - Responsive grid with proper breakpoints
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {items.map(item => <Card key={item.id} />)}
</div>

// ✅ CORRECT - Constrained horizontal scroll (Archon pattern)
<div className="w-full">
  <div className="overflow-x-auto -mx-6 px-6 py-8 scrollbar-hide">
    <div className="flex gap-4 min-w-max">
      {items.map(item => <Card key={item.id} className="w-72 shrink-0" />)}
    </div>
  </div>
</div>

// ✅ CORRECT - Flex parent containing scroll container MUST have min-w-0
<div className="flex gap-6">
  <aside className="w-64 shrink-0">Sidebar</aside>
  <main className="flex-1 min-w-0">  {/* min-w-0 is CRITICAL here */}
    {/* This content includes horizontal scroll containers */}
    <div className="w-full">
      <div className="overflow-x-auto scrollbar-hide">
        <div className="flex gap-4 min-w-max">
          {items.map(item => <Card key={item.id} className="w-72 shrink-0" />)}
        </div>
      </div>
    </div>
  </main>
</div>

// ✅ CORRECT - Text truncation patterns
<h3 className="font-medium truncate">{veryLongTitle}</h3>  {/* Single line */}
<h3 className="font-medium line-clamp-2">{description}</h3>  {/* Multi-line */}
<p className="break-words max-w-full">{wrappableContent}</p>  {/* Wrap */}

// ✅ CORRECT - Responsive flexbox with wrapping
<div className="flex flex-col md:flex-row gap-4 flex-wrap">
  <div className="w-full md:w-64">Sidebar</div>
  <div className="flex-1 min-w-0">Content</div>
</div>

// ❌ BROKEN - Unconstrained scroll (entire page becomes horizontally scrollable)
<div className="overflow-x-auto">
  <div className="flex gap-4 min-w-max">
    {/* Page width forced beyond viewport */}
  </div>
</div>

// ❌ CRITICAL BROKEN - Flex parent without min-w-0 containing scroll container
// SYMPTOM: Scroll container forces ENTIRE PAGE to expand, UI controls shift off-screen
<div className="flex gap-6">
  <aside className="w-64 shrink-0">Sidebar</aside>
  <main className="flex-1 max-w-6xl">  {/* MISSING min-w-0! */}
    <div className="w-full">
      <div className="overflow-x-auto">
        <div className="flex gap-4 min-w-max">
          <Card className="w-72 shrink-0" />  {/* Forces flex parent to expand */}
        </div>
      </div>
    </div>
    {/* Grid/list toggle buttons are now OFF-SCREEN → */}
  </main>
</div>

// ❌ BROKEN - Fixed grid columns (breaks mobile, forces page-width expansion)
// SYMPTOM: UI controls (toggles, buttons) shift off-screen, page scrolls horizontally
<div className="grid grid-cols-4 gap-4">
  <Card className="w-72" />  {/* Fixed width × 4 cols = 1152px minimum */}
  {/* User cannot access grid/list toggle buttons - they're off-screen */}
</div>

// ❌ ALSO BROKEN - Responsive grid BUT fixed-width children
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  <Card className="w-72" />  {/* w-72 prevents cards from adapting to grid cell */}
  {/* On md breakpoint: 2 × 288px = 576px + gaps → can still overflow */}
</div>

// ❌ BROKEN - No text truncation
<h3 className="font-medium">{veryLongTitle}</h3>  {/* Overflows layout */}
```

```css
/* Full-height panel that still works on mobile */
.section {
  min-height: 100dvh; /* allows for dynamic mobile toolbars */
}
```

---

## 4) Light/Dark Themes

**Rules**
- Implement dark mode with the **`dark:` variant** and an `.dark` class on `<html>`.  
- Keep structure identical; only colors/opacity/shadows change between themes.  
- Use tokens for both themes (e.g., `--color-bg` and `--color-bg-dark`) and switch via `.dark`.

**Anti‑Patterns**
- Hard‑coding light colors without a dark counterpart.
- Completely different component visuals between themes (beyond color/contrast).
- Using global filters/invert to “fake” dark mode.

**Good Example**
```html
<article class="bg-[var(--color-bg)] text-[var(--color-fg)]
               dark:bg-[var(--color-bg-dark)] dark:text-[var(--color-fg-dark)]">
  …
</article>
```

---

## 5) Component Reusability & Shared Primitives

**Rules**
- **Use Card primitives** from `@/features/ui/primitives/` for all glassmorphism, edge-lit, and card effects - NEVER hardcode these patterns.
- **Use PillNavigation component** for tab navigation - NEVER create custom pill navigation.
- **Use Radix UI primitives** for all interactive elements (Select, Checkbox, RadioGroup, Dialog, Popover, etc.).
- **Import from styles.ts** when you need pre-defined class objects - this is the design system's foundation.
- **CRITICAL: Primitives MUST use styles.ts, not define their own blur/transparency classes**. Import `glassCard.blur` and `glassCard.transparency` instead of creating inline `const blurClasses` or hardcoding `backdrop-blur-md`.
- **Centralize repeated patterns** - if you find yourself copying the same class strings 3+ times, create a wrapper component.

### The styles.ts Design System

**Location**: `archon-ui-main/src/features/ui/primitives/styles.ts`

This file is the **single source of truth** for Archon's Tron-inspired glassmorphism design system. It provides pre-built static class strings that ensure consistency across the entire application.

**What styles.ts Provides:**

1. **`glassmorphism`** - Core glass effect utilities
   - `background.*` - Transparency levels (subtle, strong, card, colored)
   - `border.*` - Border styles (default, colored, focus, hover)
   - `interactive.*` - Interaction states (base, hover, active, selected, disabled)
   - `animation.*` - Animation presets (fadeIn, slideIn, etc.)
   - `shadow.*` - Shadow effects including neon glows
   - `priority.*` - Task priority colors (critical, high, medium, low)

2. **`glassCard`** - Complete card system
   - `base` - Base card structure
   - `blur.*` - Blur intensity levels (none, sm, md, lg, xl, 2xl, 3xl)
   - `transparency.*` - Glass opacity levels (clear, light, medium, frosted, solid)
   - `tints.*` - Colored glass tints (purple, blue, cyan, green, orange, pink, red)
   - `variants.*` - Pre-built color variants with border + glow
   - `edgeLit.*` - Edge-lit effects (position + color + glow)
   - `sizes.*` - Padding variants (none, sm, md, lg, xl)
   - `outerGlowSizes.*` - Outer glow by size and color
   - `innerGlowSizes.*` - Inner glow by size and color

3. **`compoundStyles`** - Common composition patterns
   - `interactiveElement` - Standard button/menu item styling
   - `floatingPanel` - Dropdown/popover/tooltip styling
   - `formControl` - Input/select styling
   - `card` - Basic card styling

4. **`cn()`** - Utility function to combine class strings

**When to Use styles.ts:**

✅ **ALWAYS use for:**
- Glassmorphism backgrounds (`glassmorphism.background.*`)
- Card variants (`glassCard.variants.*`)
- Edge-lit effects (`glassCard.edgeLit.*`)
- Glow effects (`glassCard.outerGlowSizes.*`, `glassCard.innerGlowSizes.*`)
- Interactive states (`glassmorphism.interactive.*`)
- Animations (`glassmorphism.animation.*`)

❌ **DON'T use for:**
- Layout (use Tailwind utilities: `flex`, `grid`, `w-full`, etc.)
- Spacing (use Tailwind: `p-4`, `m-2`, `gap-4`, etc.)
- Typography (use Tailwind: `text-lg`, `font-medium`, etc.)
- One-off custom styling (use inline Tailwind classes)

**How to Use:**

```tsx
import { glassmorphism, glassCard, cn } from '@/features/ui/primitives/styles';

// Example 1: Using glassmorphism utilities
<div className={cn(
  glassmorphism.background.strong,
  glassmorphism.border.default,
  glassmorphism.shadow.lg,
  "p-6 rounded-lg" // Layout/spacing from Tailwind
)}>
  Content
</div>

// Example 2: Using glassCard with variants
<div className={cn(
  glassCard.base,
  glassCard.blur.lg,
  glassCard.transparency.light,
  glassCard.variants.cyan.border,
  glassCard.variants.cyan.glow,
  "p-6" // Padding from Tailwind
)}>
  Card content
</div>

// Example 3: Using edge-lit effects
<div className={cn(
  glassCard.base,
  glassCard.blur.xl,
  glassCard.transparency.medium,
  glassCard.edgeLit.position.top,
  glassCard.edgeLit.color.purple.line,
  glassCard.edgeLit.color.purple.glow,
  "p-8"
)}>
  Edge-lit card
</div>
```

**Why styles.ts Matters:**

1. **Consistency** - Same glass effects across all components
2. **Maintainability** - Change design system in one place
3. **Performance** - Static class strings, no runtime computation
4. **Type Safety** - TypeScript autocomplete for all variants
5. **Design Tokens** - All values reference @theme tokens
6. **DRY Principle** - No duplication of complex class strings

**Anti‑Patterns**
- Hardcoding glassmorphism effects: `backdrop-blur-md bg-white/10 border border-gray-200`.
- Creating custom pill navigation each time instead of using `<PillNavigation />`.
- Using native HTML form elements (`<select>`, `<input type="checkbox">`, `<input type="radio">`) instead of Radix primitives.
- Duplicating edge-lit glow effects across multiple components.

**Good Examples**
```tsx
// ✅ CORRECT - Use Card primitive with props
import { Card } from '@/features/ui/primitives/card';

<Card
  blur="lg"                    // sm, md, lg, xl, 2xl, 3xl
  transparency="light"         // clear, light, medium, frosted, solid
  edgePosition="top"           // none, top, left, right, bottom
  edgeColor="cyan"             // purple, blue, cyan, green, orange, pink, red
  glowColor="cyan"             // For glow effects
  glowType="outer"             // inner or outer
>
  {children}
</Card>

// ✅ CORRECT - Use PillNavigation component
import { PillNavigation } from '@/features/ui/primitives/pill-navigation';

<PillNavigation
  items={[
    { id: 'overview', label: 'Overview' },
    { id: 'tasks', label: 'Tasks' },
  ]}
  activeSection={activeSection}
  onSectionClick={setActiveSection}
  colorVariant="orange"
  size="small"
/>

// ✅ CORRECT - Use Radix primitives
import { Select, SelectTrigger, SelectContent, SelectItem } from '@/features/ui/primitives/select';
import { Checkbox } from '@/features/ui/primitives/checkbox';
import { RadioGroup, RadioGroupItem } from '@/features/ui/primitives/radio-group';

<Select value={value} onValueChange={setValue}>
  <SelectTrigger>Choose option</SelectTrigger>
  <SelectContent>
    <SelectItem value="1">Option 1</SelectItem>
  </SelectContent>
</Select>

// ✅ CORRECT - Use styles.ts for shared class objects
import { glassCard } from '@/features/ui/primitives/styles';
<div className={cn(glassCard.base, glassCard.blur.md, glassCard.transparency.light)}>
  {children}
</div>

// ❌ BROKEN - Hardcoding glassmorphism
<div className="backdrop-blur-md bg-white/10 border border-gray-200 rounded-lg">
  {children}
</div>

// ❌ BROKEN - Custom pill navigation
<div className="backdrop-blur-sm bg-white/40 dark:bg-white/5 border rounded-full p-1">
  <div className="flex gap-1">
    {items.map(item => (
      <button className="px-6 py-2.5 rounded-full text-sm font-medium">
        {item.label}
      </button>
    ))}
  </div>
</div>

// ❌ BROKEN - Native HTML elements
<select>
  <option value="1">Option 1</option>
</select>
```

---

## 6) Tailwind Tokens Quickstart (promote values to tokens)

```css
@import "tailwindcss";

:root {
  --background: hsl(0 0% 98%);
  --foreground: hsl(240 10% 3.9%);
  --border: hsl(240 5.9% 90%);
  --brand-500: oklch(0.70 0.15 220);
  --radius: 0.5rem;
  color-scheme: light;
}

.dark {
  --background: hsl(0 0% 0%);
  --foreground: hsl(0 0% 100%);
  --border: hsl(240 3.7% 15.9%);
  color-scheme: dark;
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-border: var(--border);
  --color-brand-500: var(--brand-500);
  --radius-lg: var(--radius);
  --radius-md: calc(var(--radius) - 2px);
}
```

Then use generated utilities (e.g., `bg-brand-500`, `border-border`) or token references (`bg-[var(--accent)]`).

---

## 7) UI Review Pre-Flight Checklist

Before committing any UI component, verify ALL of these:

### Tailwind v4 Rules
- [ ] **No dynamic class construction** (`bg-${color}-500`, template literals with variables)
- [ ] **CSS variables allowed in arbitrary values** (static utility names: `bg-[var(--accent)]`)
- [ ] **Static class lookup objects** for discrete variants (e.g., `const colorClasses = { cyan: "...", ... }`)
- [ ] **CSS variables pattern** for flexible/continuous values (colors, alphas, glows)
- [ ] **Conditional classes are complete strings** (use `cn()` with full class names)
- [ ] **Arbitrary values are static** (written as complete strings in source code)
- [ ] **Inline style ONLY for CSS variables** (`style={{ "--accent": token }}`), never direct visual CSS
- [ ] **Variables in `:root` and `.dark`**, mapped with `@theme inline`
- [ ] **`@layer` and `@apply` used properly** (base styles and component classes)

### Responsive Layout Rules
- [ ] **Desktop-primary with responsive adaptations** (optimize for desktop, add breakpoints for smaller screens)
- [ ] **Horizontal scroll containers have `w-full` parent** (CRITICAL - prevents page-width expansion)
- [ ] **Horizontal scroll containers use `scrollbar-hide`** (cleaner UI without visible scrollbar)
- [ ] **Flex parent containing scroll container has `min-w-0`** (CRITICAL - prevents page expansion)
- [ ] **Responsive grid columns** (`grid-cols-1 md:grid-cols-2 lg:grid-cols-3` etc.)
- [ ] **Flexbox adapts at breakpoints** (`flex-col md:flex-row`)
- [ ] **Text has truncation/wrapping** (`truncate`, `line-clamp-N`, or `break-words max-w-full`)
- [ ] **Fixed widths have `max-w-*` constraints** (no bare `w-[500px]`)
- [ ] **Add `min-w-0` to flex children** that contain text/images (allows shrinking)
- [ ] **Layout toggle buttons always visible** (not absolutely positioned off-screen)
- [ ] **Use `min-h-[100dvh]`** instead of rigid `h-screen` on mobile
- [ ] **Remove layout-level `overflow-hidden`** (clips popovers/toasts/dialogs)

### Component Reusability Rules
- [ ] **Use Card primitive** for glassmorphism/edge-lit effects (no hardcoded patterns)
- [ ] **Use PillNavigation component** for tab navigation (no custom implementations)
- [ ] **Use Radix UI primitives** for all interactive elements (Select, Checkbox, RadioGroup, Dialog, etc.)
- [ ] **Import from styles.ts** for shared class objects when appropriate
- [ ] **No duplicated styling patterns** (DRY - create wrapper components if repeated 3+ times)

### Radix Primitives Rules
- [ ] **Use `asChild` for custom triggers** (compose, don't wrap)
- [ ] **Follow documented structure** (Root/Trigger/Portal/Overlay/Content/Close)
- [ ] **Style via data attributes** (`[data-state="open"]`, `[data-disabled]`)
- [ ] **Use Portal and z-index scale** for overlays (no random `z-[9999]`)
- [ ] **Never remove focus rings or ARIA** attributes

### Light/Dark Theme Rules
- [ ] **Every color/border/shadow has `dark:` variant** where visible
- [ ] **Structure identical between themes** (only colors/opacity/shadows change)
- [ ] **Use tokens for both themes** (`--color-bg` and `--color-bg-dark`)

### Testing Requirements
- [ ] **Tested at 375px width** (mobile - iPhone SE)
- [ ] **Tested at 768px width** (tablet)
- [ ] **Tested at 1024px width** (laptop)
- [ ] **Tested at 1440px+ width** (desktop)
- [ ] **All UI controls accessible** at all sizes
- [ ] **No unintended horizontal page scroll** (only intentional container scroll)
- [ ] **Images scale responsively**
- [ ] **Modals/dialogs fit within viewport**
- [ ] **Touch targets minimum 44x44px** on mobile

### Common Violations to Fix Immediately
- ❌ `bg-${color}-500` → ✅ `colorClasses[color]`
- ❌ `grid-cols-4` → ✅ `grid-cols-1 md:grid-cols-2 lg:grid-cols-4` (Symptom: page scrolls horizontally, controls off-screen)
- ❌ Hardcoded glassmorphism → ✅ `<Card blur="lg" transparency="light">`
- ❌ `<select>` → ✅ `<Select>` from Radix
- ❌ Custom pill navigation → ✅ `<PillNavigation>`
- ❌ `overflow-x-auto` without `w-full` parent → ✅ Wrap in `<div className="w-full">`
- ❌ Long text with no truncation → ✅ Add `truncate` or `line-clamp-N`
- ❌ Fixed `w-[500px]` → ✅ `w-full max-w-[500px]`
- ❌ Absolute positioned controls → ✅ Use flexbox layout
- ❌ No dark mode variant → ✅ Add `dark:` classes

---

## 8) Automated Scanning Patterns

Use these patterns to programmatically detect violations in `.tsx` files.

### Critical Violations (Breaking Changes)

**Dynamic Tailwind Class Construction (NO CSS GENERATED)**
```bash
grep -rn "className={\`.*\${.*}.*\`}" [path] --include="*.tsx"
grep -rn "bg-\${.*}\|text-\${.*}\|border-\${.*}\|shadow-\${.*}" [path] --include="*.tsx"
```
**Rule**: Section 2 - NO dynamic class name construction
**Fix**: Use static class lookup objects (Pattern A from Section 2)

**Unconstrained Horizontal Scroll (BREAKS LAYOUT)**
```bash
# Find overflow-x-auto without w-full parent
grep -rn "overflow-x-auto" [path] --include="*.tsx"
# Then manually verify parent has w-full or max-w-*
```
**Rule**: Section 3 - Constrain horizontal scroll containers
**Fix**: Wrap in `<div className="w-full">` (Example in Section 3)

**Non-Responsive Grid Columns (BREAKS MOBILE)**
```bash
grep -rn "grid-cols-[2-9]" [path] --include="*.tsx" | grep -v "md:\|lg:\|sm:\|xl:"
```
**Rule**: Section 3 - Responsive grid columns mandatory
**Symptom**: Page scrolls horizontally, UI controls (grid/list toggles, navigation buttons) shift off-screen and become inaccessible
**Fix**: Add responsive breakpoints: `grid-cols-1 md:grid-cols-2 lg:grid-cols-4` (Section 3)

**Min-w-max Without Constraint**
```bash
grep -rn "min-w-max" [path] --include="*.tsx"
```
**Rule**: Section 3 - min-w-max must have constrained parent
**Fix**: Ensure parent has `w-full` or `max-w-*`

### High Priority Violations

**Native HTML Form Elements (Should Use Radix)**
```bash
grep -rn "<select>" [path] --include="*.tsx"
grep -rn "<option>" [path] --include="*.tsx"
grep -rn "type=\"checkbox\"" [path] --include="*.tsx"
grep -rn "type=\"radio\"" [path] --include="*.tsx"
```
**Rule**: Section 0, Section 1 - Use Radix UI primitives
**Fix**: Import from `@/features/ui/primitives/` (Section 5)

**Hardcoded Glassmorphism (Should Use Card Primitive)**
```bash
grep -rn "backdrop-blur.*bg-white/.*border.*rounded" [path] --include="*.tsx"
grep -rn "absolute inset-x-0 top-0.*bg-gradient-to-b" [path] --include="*.tsx"
```
**Rule**: Section 5 - Use Card primitive for glassmorphism
**Fix**: `<Card blur="lg" transparency="light">` (Section 5)

**Hardcoded Pill Navigation (Should Use Component)**
```bash
grep -rn "rounded-full.*flex gap-" [path] --include="*.tsx"
grep -rn "backdrop-blur.*rounded-full.*px-6 py-2" [path] --include="*.tsx"
```
**Rule**: Section 5 - Use PillNavigation component
**Fix**: `<PillNavigation items={...} />` (Section 5)

**Missing Text Truncation**
```bash
grep -rn "<h[1-6].*className" [path] --include="*.tsx" | grep -v "truncate\|line-clamp"
```
**Rule**: Section 3 - Always handle long text
**Fix**: Add `truncate` or `line-clamp-N` (Section 3)

**Fixed Widths Without Constraints**
```bash
grep -rn "w-\[0-9\]" [path] --include="*.tsx" | grep -v "max-w-"
grep -rn "w-96\|w-80\|w-72\|w-64" [path] --include="*.tsx" | grep -v "max-w-"
```
**Rule**: Section 3 - Fixed widths need max-w-* constraints
**Fix**: Change to `w-full max-w-[value]`

**Inline Style for Visual CSS (Not Variables)**
```bash
grep -rn "style={{.*backgroundColor\|color:\|padding:\|margin:" [path] --include="*.tsx"
```
**Rule**: Section 0, Section 2 - Inline style ONLY for CSS variables
**Fix**: Use className or CSS variables (Section 2 Pattern B)

**Missing Dark Mode Variants**
```bash
# Find colors without dark: variant (manual review needed)
grep -rn "bg-.*-[0-9]" [path] --include="*.tsx" | grep -v "dark:"
```
**Rule**: Section 4 - Every visible color needs dark: variant
**Fix**: Add `dark:` classes (Section 4)

### Medium Priority Violations

**Not Using Shared Primitives**
```bash
# Manually check imports - should import from @/features/ui/primitives/
grep -rn "import.*from.*primitives" [path] --include="*.tsx" -L
```
**Rule**: Section 0, Section 5 - Use shared component primitives
**Fix**: Import and use Card, PillNavigation, Radix primitives

**Primitives Defining Own Blur/Transparency (Should Use styles.ts)**
```bash
# Find primitives with hardcoded blur/transparency definitions
grep -rn "const blurClasses\|const transparencyClasses" [path]/features/ui/primitives --include="*.tsx"
grep -rn "backdrop-blur-sm\|backdrop-blur-md\|backdrop-blur-lg" [path]/features/ui/primitives --include="*.tsx"
```
**Rule**: Section 5 - Primitives MUST use glassCard.blur and glassCard.transparency from styles.ts
**Fix**: Import `glassCard` from styles.ts and use `glassCard.blur[blur]` and `glassCard.transparency[transparency]`

**Missing min-w-0 on Flex Children (CRITICAL for scroll containers)**
```bash
# Find flex-1 without min-w-0 (manual review for children containing scroll containers)
grep -rn "flex-1" [path] --include="*.tsx" | grep -v "min-w-0"
```
**Rule**: Section 3 - Flex parent containing scroll container MUST have min-w-0
**Symptom**: Scroll container forces ENTIRE PAGE to expand, UI controls shift off-screen
**Fix**: Add `min-w-0` to flex parent: `className="flex-1 min-w-0"` (Section 3)

### Scoring Guide

For each component, calculate violation score:
- **0 critical violations**: 9-10/10
- **1 critical violation**: 7-8/10
- **2-3 critical violations**: 5-6/10
- **4+ critical violations**: 1-4/10

Adjust based on high/medium priority violations.

---

## 9) Quick Reference

### Archon-Specific Component Patterns

```tsx
// Horizontal Scroll Pattern (constrained, hidden scrollbar)
<div className="w-full">
  <div className="overflow-x-auto -mx-6 px-6 py-8 scrollbar-hide">
    <div className="flex gap-4 min-w-max">
      {items.map(item => <Card key={item.id} className="w-72 shrink-0" />)}
    </div>
  </div>
</div>

// Note: scrollbar-hide utility defined in index.css:
// .scrollbar-hide {
//   -ms-overflow-style: none;
//   scrollbar-width: none;
// }
// .scrollbar-hide::-webkit-scrollbar {
//   display: none;
// }

// Responsive Grid Pattern
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {items.map(item => <Card key={item.id} />)}
</div>

// Sidebar + Main Content Pattern
<div className="flex flex-col lg:flex-row gap-6">
  <aside className="w-full lg:w-64 flex-shrink-0">
    {/* Sidebar content */}
  </aside>
  <main className="flex-1 min-w-0">
    {/* Main content - min-w-0 allows truncation */}
  </main>
</div>

// Card Primitive Usage
<Card
  blur="lg"
  transparency="light"
  edgePosition="top"
  edgeColor="cyan"
  glowColor="cyan"
  glowType="outer"
>
  {children}
</Card>

// Radix Dialog Pattern
<Dialog.Root>
  <Dialog.Trigger asChild>
    <Button variant="primary">Open</Button>
  </Dialog.Trigger>
  <Dialog.Portal>
    <Dialog.Overlay className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40" />
    <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-full max-w-md md:max-w-2xl
                               -translate-x-1/2 -translate-y-1/2 rounded-lg
                               bg-surface/95 dark:bg-surface-dark/95 shadow-xl p-6">
      <Dialog.Title>Title</Dialog.Title>
      <Dialog.Description>Description</Dialog.Description>
      {/* Content */}
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
```

### Color Variant Patterns

**Pattern A: Lookup Map (discrete variants)**
```tsx
// Static class object for finite set of brand colors
const colorClasses = {
  cyan: "bg-cyan-500 text-cyan-900 border-cyan-500/50 shadow-cyan-500/20",
  purple: "bg-purple-500 text-purple-900 border-purple-500/50 shadow-purple-500/20",
  blue: "bg-blue-500 text-blue-900 border-blue-500/50 shadow-blue-500/20",
  orange: "bg-orange-500 text-orange-900 border-orange-500/50 shadow-orange-500/20",
};

<div className={cn("base-styles", colorClasses[colorVariant])} />
```

**Pattern B: CSS Variables (flexible values)**
```css
/* In index.css */
:root {
  --cyan-500: oklch(0.75 0.12 210);
  --orange-500: oklch(0.75 0.16 70);
  --accent: var(--cyan-500);
}

@theme inline {
  --color-cyan-500: var(--cyan-500);
  --color-orange-500: var(--orange-500);
}

/* Named accent classes */
.accent-cyan { --accent: var(--cyan-500); }
.accent-orange { --accent: var(--orange-500); }
```

```tsx
// Component using CSS variables
const accentClass = {
  cyan: "accent-cyan",
  orange: "accent-orange",
} as const;

export function GlassCard({ color = "cyan", customAccent }: Props) {
  return (
    <div
      className={cn(
        "rounded-lg backdrop-blur-md",
        "bg-[var(--glass-bg)] border-[color:var(--accent)]",
        "shadow-[0_0_24px_color-mix(in_oklab,var(--accent)_35%,transparent)]",
        accentClass[color]
      )}
      // Optional: set custom accent dynamically via variable
      style={customAccent ? ({ "--accent": customAccent } as React.CSSProperties) : undefined}
    />
  );
}
```

### Breakpoint Reference

- **sm**: 640px (small tablets)
- **md**: 768px (tablets)
- **lg**: 1024px (laptops)
- **xl**: 1280px (desktops)
- **2xl**: 1536px (large desktops)

### Critical Reminders

1. **NO dynamic class construction** - `bg-${color}-500` will NOT generate CSS
2. **CSS variables ARE allowed** - `bg-[var(--accent)]` works (utility name is static)
3. **Inline style ONLY for CSS variables** - `style={{ "--accent": token }}`, never direct visual CSS
4. **Proper @theme pattern** - Variables in `:root`/`.dark`, map with `@theme inline`
5. **`@layer` and `@apply` still work** - Valid in v4 for base/component styles
6. **Constrain scroll containers** - `overflow-x-auto` parent needs `w-full`
7. **Responsive grids always** - Never fixed `grid-cols-4` without breakpoints
8. **Use primitives** - Card, PillNavigation, Radix UI components
9. **Desktop-primary** - Optimize for desktop, add responsive breakpoints for smaller screens
10. **Text truncation** - Always handle long text explicitly
11. **Dark mode** - Every visible color needs `dark:` variant
