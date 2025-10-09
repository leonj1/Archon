# Tailwind CSS & Responsive Design Best Practices

## Critical Tailwind CSS Rules

### Rule 1: NO Dynamic Class Name Construction

Tailwind processes your source code as **plain text at BUILD time**, NOT at runtime. It cannot understand variables, string concatenation, or template literals.

#### BROKEN Patterns (Will Not Work)

```tsx
// BROKEN - Tailwind won't generate these classes
const color = "cyan";
<div className={`bg-${color}-500`} />  // CSS NOT GENERATED

// BROKEN - Template literal concatenation
<div className={`text-${textColor}-700 border-${borderColor}-500`} />

// BROKEN - String interpolation
const glow = `shadow-[0_0_30px_rgba(${rgba},0.4)]`;

// BROKEN - Computed class names
className={isActive ? `bg-${activeColor}-500` : `bg-${inactiveColor}-500`}
```

**Why These Fail:**
- Tailwind scans code as text looking for class tokens
- `bg-cyan-500` exists as a token → CSS generated
- `bg-${color}-500` does NOT exist as a token → NO CSS generated
- At runtime, browser receives class name with no matching CSS

#### CORRECT Patterns (Use These)

```tsx
// CORRECT - Static class lookup object
const colorClasses = {
  cyan: "bg-cyan-500 text-cyan-700 border-cyan-500/50",
  purple: "bg-purple-500 text-purple-700 border-purple-500/50",
  blue: "bg-blue-500 text-blue-700 border-blue-500/50",
};
<div className={colorClasses[color]} />

// CORRECT - Conditional with complete class names
<div className={isActive ? "bg-cyan-500 text-white" : "bg-gray-500 text-gray-300"} />

// CORRECT - Use cn() helper with complete class strings
<div className={cn(
  "base-classes",
  isActive && "bg-cyan-500 text-white",
  isPinned && "border-purple-500 shadow-lg"
)} />

// CORRECT - Static arbitrary values (scanned at build time)
<div className="shadow-[0_0_30px_rgba(34,211,238,0.4)]" />

// CORRECT - Pre-defined classes from styles.ts
import { glassCard } from '@/features/ui/primitives/styles';
className={cn(glassCard.base, glassCard.variants.cyan.glow)}
```

### Rule 2: Use Static Class Mappings

When you need variant styling based on props or state:

```tsx
// CORRECT Pattern
interface ButtonProps {
  variant: "primary" | "secondary" | "danger";
}

const Button = ({ variant }: ButtonProps) => {
  const variantClasses = {
    primary: "bg-blue-500 hover:bg-blue-600 text-white",
    secondary: "bg-gray-200 hover:bg-gray-300 text-gray-900",
    danger: "bg-red-500 hover:bg-red-600 text-white",
  };

  return <button className={variantClasses[variant]}>Click me</button>;
};
```

### Rule 3: Arbitrary Values for One-Off Styles

When you need a specific value not in your theme:

```tsx
// CORRECT - Arbitrary values are scanned at build time
<div className="w-[347px]" />
<div className="shadow-[0_0_30px_rgba(34,211,238,0.4)]" />
<div className="bg-[#316ff6]" />

// These work because the complete string exists in source code
```

## Responsive Design Best Practices

### Rule 1: Mobile-First Approach

Always design for mobile first, then layer styles for larger screens.

```tsx
// CORRECT - Mobile first, then larger screens
<div className="w-full md:w-1/2 lg:w-1/3">

// WRONG - Desktop first (harder to override)
<div className="w-1/3 sm:w-full">
```

### Rule 2: Responsive Grid Columns

Never use fixed grid columns without responsive breakpoints.

```tsx
// WRONG - Fixed 4 columns breaks on mobile
<div className="grid grid-cols-4 gap-4">

// CORRECT - Responsive columns
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
```

### Rule 3: Constrain Horizontal Scroll Containers

**CRITICAL:** When creating horizontally scrollable content, you MUST constrain the parent container.

```tsx
// WRONG - Entire page becomes scrollable
<div className="overflow-x-auto">
  <div className="flex gap-4 min-w-max">
    {/* Wide cards */}
  </div>
</div>

// CORRECT - Scroll isolated to specific container
<div className="w-full">
  <div className="overflow-x-auto -mx-6 px-6">
    <div className="flex gap-4 min-w-max">
      {/* Only cards scroll, page stays within viewport */}
    </div>
  </div>
</div>
```

**Why This Matters:**
- Without `w-full` parent, `min-w-max` forces entire page width to expand
- UI controls shift off-screen
- Layout breaks at all viewport sizes
- User cannot access navigation or buttons

### Rule 4: Responsive Flexbox

Use flex-wrap and responsive flex directions:

```tsx
// WRONG - Overflows on small screens
<div className="flex gap-4">
  <div className="w-64">Sidebar</div>
  <div className="w-96">Content</div>
</div>

// CORRECT - Wraps on mobile, horizontal on desktop
<div className="flex flex-col md:flex-row gap-4">
  <div className="w-full md:w-64">Sidebar</div>
  <div className="flex-1">Content</div>
</div>
```

### Rule 5: Text Truncation & Overflow

Always handle long text content:

```tsx
// WRONG - Long titles break layout
<h3 className="font-medium">{veryLongTitle}</h3>

// CORRECT - Single line truncate
<h3 className="font-medium truncate">{veryLongTitle}</h3>

// CORRECT - Multi-line clamp
<h3 className="font-medium line-clamp-2">{veryLongTitle}</h3>

// CORRECT - Wrap with proper width constraint
<h3 className="font-medium break-words max-w-full">{veryLongTitle}</h3>
```

## Common Layout Anti-Patterns

### Anti-Pattern 1: Fixed Widths Without Constraints

```tsx
// WRONG - Fixed width can overflow viewport
<div className="w-96 p-8">

// CORRECT - Max width with full width fallback
<div className="w-full max-w-96 p-8">
```

### Anti-Pattern 2: Absolute Positioning for UI Controls

```tsx
// WRONG - Controls shift off-screen when content overflows
<div className="absolute top-8 right-8">
  <Button>Toggle View</Button>
</div>

// CORRECT - Use flexbox layout
<div className="flex justify-end mb-4">
  <Button>Toggle View</Button>
</div>
```

### Anti-Pattern 3: Non-Responsive Tables

```tsx
// WRONG - Table breaks on mobile
<table className="w-full">
  <thead>
    <tr>
      <th>Column 1</th>
      <th>Column 2</th>
      <th>Column 3</th>
      <th>Column 4</th>
      <th>Column 5</th>
    </tr>
  </thead>
</table>

// CORRECT - Wrap in overflow container
<div className="overflow-x-auto w-full">
  <table className="w-full">
    {/* Table can scroll horizontally on mobile */}
  </table>
</div>
```

### Anti-Pattern 4: Padding on Scroll Container

```tsx
// WRONG - Padding prevents content from reaching edge
<div className="overflow-x-auto px-8 py-8">
  <div className="flex gap-4 min-w-max">

// CORRECT - Use negative margin to compensate
<div className="w-full">
  <div className="overflow-x-auto -mx-6 px-6">
    <div className="flex gap-4 min-w-max">
```

### Anti-Pattern 5: Missing Width Constraints on Scrollable Parents

```tsx
// WRONG - Parent has no width, child forces expansion
<div>
  <div className="overflow-x-auto">
    <div className="flex gap-4 min-w-max">
      {/* Forces parent to expand beyond viewport */}
    </div>
  </div>
</div>

// CORRECT - Explicit width constraint
<div className="w-full max-w-7xl mx-auto">
  <div className="overflow-x-auto">
    <div className="flex gap-4 min-w-max">
      {/* Scrolls within constrained parent */}
    </div>
  </div>
</div>
```

## Radix UI Integration Best Practices

### Use Radix Primitives for All Interactive Elements

```tsx
// WRONG - Native HTML elements
<select>
  <option value="1">Option 1</option>
</select>
<input type="checkbox" />
<input type="radio" />

// CORRECT - Radix primitives
import { Select, SelectTrigger, SelectContent, SelectItem } from '@/features/ui/primitives/select';
import { Checkbox } from '@/features/ui/primitives/checkbox';
import { RadioGroup, RadioGroupItem } from '@/features/ui/primitives/radio-group';
```

### Modal/Dialog Responsive Patterns

```tsx
// CORRECT - Responsive dialog sizes
<DialogContent className="w-full max-w-md md:max-w-2xl lg:max-w-4xl">
  {/* Adapts to screen size */}
</DialogContent>
```

## Component Reusability Patterns

### Pattern 1: Card Primitives Over Hardcoded Styles

```tsx
// WRONG - Hardcoding glassmorphism and edge-lit effects
<div className="relative rounded-xl overflow-hidden">
  <div className="absolute inset-x-0 top-0 h-[2px] bg-cyan-500" />
  <div className="absolute inset-x-0 top-0 h-16 bg-gradient-to-b from-cyan-500/40 to-transparent blur-lg" />
  <div className="backdrop-blur-md bg-white/10 border border-gray-200 p-4">
    {children}
  </div>
</div>

// CORRECT - Use Card primitive with props
<Card edgePosition="top" edgeColor="cyan" blur="lg" transparency="light">
  {children}
</Card>
```

### Pattern 2: Static Class Objects from styles.ts

```tsx
// WRONG - Hardcoding repeated glass effects
<div className="backdrop-blur-md bg-white/10 border border-gray-200 rounded-lg">

// CORRECT - Use pre-defined classes
import { glassCard } from '@/features/ui/primitives/styles';
<div className={cn(glassCard.base, glassCard.blur.md, glassCard.transparency.light)}>
```

### Pattern 3: Shared Navigation Components

```tsx
// WRONG - Custom pill navigation each time
<div className="backdrop-blur-sm bg-white/40 dark:bg-white/5 border rounded-full p-1">
  <div className="flex gap-1">
    {items.map(item => (
      <button className="px-6 py-2.5 rounded-full text-sm font-medium">
        {item.label}
      </button>
    ))}
  </div>
</div>

// CORRECT - Use PillNavigation component
<PillNavigation
  items={items}
  activeSection={activeSection}
  onSectionClick={setActiveSection}
  colorVariant="orange"
  size="small"
/>
```

## Testing Responsive Layouts

### Required Viewport Tests

Test every layout at these breakpoints:
- **375px** - iPhone SE (smallest modern phone)
- **768px** - Tablet portrait
- **1024px** - Tablet landscape / small laptop
- **1440px** - Desktop
- **1920px** - Large desktop

### Responsive Checklist

For every component:
- [ ] All UI controls visible at all breakpoints
- [ ] No horizontal page scroll (only intentional container scroll)
- [ ] Text truncates or wraps appropriately
- [ ] Images scale responsively
- [ ] Grid adapts to screen size
- [ ] Flexbox wraps or changes direction on mobile
- [ ] Modals/dialogs fit within viewport
- [ ] Touch targets are minimum 44x44px on mobile

## Common Mistakes Summary

### 1. Dynamic Tailwind Classes
**Problem:** String interpolation like `bg-${color}-500`
**Solution:** Static class object lookup

### 2. Unconstrained Scroll Containers
**Problem:** `min-w-max` without `w-full` parent
**Solution:** Always constrain parent width

### 3. Fixed Grid Columns
**Problem:** `grid-cols-4` on all screen sizes
**Solution:** `grid-cols-1 md:grid-cols-2 lg:grid-cols-4`

### 4. Missing Text Truncation
**Problem:** Long text breaks layout
**Solution:** Add `truncate` or `line-clamp-*`

### 5. Hardcoded Component Styles
**Problem:** Duplicating glassmorphism/edge-lit patterns
**Solution:** Use Card/DataCard primitives

### 6. Absolute Positioned Controls
**Problem:** Fixed position elements shift off-screen
**Solution:** Use flexbox for layout positioning

### 7. Native HTML Form Elements
**Problem:** Using `<select>`, `<input type="checkbox">`, etc.
**Solution:** Use Radix UI primitives

## Archon-Specific Patterns

### Overflow Scroll Pattern

```tsx
// Standard pattern for horizontally scrollable cards
<div className="w-full">
  <div className="overflow-x-auto -mx-6 px-6 py-8">
    <div className="flex gap-4 min-w-max">
      {items.map(item => <Card key={item.id} />)}
    </div>
  </div>
</div>
```

### Responsive Grid Pattern

```tsx
// Standard grid for card layouts
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {items.map(item => <Card key={item.id} />)}
</div>
```

### Responsive Flex Layout

```tsx
// Sidebar + main content pattern
<div className="flex flex-col lg:flex-row gap-6">
  <aside className="w-full lg:w-64 flex-shrink-0">
    {/* Sidebar */}
  </aside>
  <main className="flex-1 min-w-0">
    {/* Main content - min-w-0 allows truncation */}
  </main>
</div>
```

### Card Primitive Usage

```tsx
// Use Card primitive props instead of hardcoding
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
```

## Pre-Flight Checklist

Before committing any UI component:

### Tailwind Rules
- [ ] No dynamic class name construction (`bg-${var}-500`)
- [ ] No template literal class building
- [ ] All variant classes defined in static objects
- [ ] Arbitrary values written as complete static strings

### Responsive Rules
- [ ] Horizontal scroll containers have `w-full` parent wrapper
- [ ] Grids use responsive column breakpoints
- [ ] Flex layouts adapt at appropriate breakpoints
- [ ] Text content has truncation or wrapping
- [ ] Fixed widths have `max-w-*` constraints
- [ ] Layout toggle buttons always visible

### Component Rules
- [ ] Using Card primitive for glassmorphism
- [ ] Using Radix primitives for all interactive elements
- [ ] Using shared components (PillNavigation, etc.)
- [ ] No duplicated styling patterns

### Testing
- [ ] Tested at 375px width (mobile)
- [ ] Tested at 768px width (tablet)
- [ ] Tested at 1024px width (laptop)
- [ ] Tested at 1440px+ width (desktop)
- [ ] All UI controls accessible at all sizes
- [ ] No unintended horizontal page scroll
