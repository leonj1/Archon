---
description: Analyze UI components for reusability, Radix usage, primitives, and styling consistency
argument-hint: <feature path, component path, or directory>
allowed-tools: Read, Grep, Glob, Write
thinking: auto
---

# UI Consistency Review for Archon

**Review scope**: $ARGUMENTS

I'll analyze the UI components and generate a detailed report on consistency, reusability, and adherence to the Archon design system.

## Analysis Framework

### Design System Standards

**Archon uses:**
- **Primitives**: `/src/features/ui/primitives/` - Reusable Radix components with glassmorphism styling
- **Card Variants**:
  - Base glass card
  - Edge-lit cards: `<Card edgePosition="top" edgeColor="cyan|pink|blue|...">`
  - Outer glow cards
  - Inner glow cards
- **Navigation**: PillNavigation component for all pill-style navigation
- **Glassmorphism**: `backdrop-blur-sm` (minimal), frosted glass backgrounds
- **Colors**: Semantic colors (Primary blue #3b82f6, Success, Warning, Error) + accents

### Scoring Criteria

**1. Reusability (1-10)**
- 10: Uses shared primitives, no hardcoded styles
- 7-9: Mostly reusable, minor hardcoding
- 4-6: Mix of primitives and custom code
- 1-3: Completely custom, duplicates existing patterns

**2. Radix Component Usage (1-10)**
- 10: Uses Radix primitives for ALL interactive elements (Select, Checkbox, Switch, Tabs, Dialog, etc.)
- 7-9: Mostly Radix, few native HTML elements
- 4-6: Mix of Radix and native elements
- 1-3: Primarily native HTML elements

**3. Primitives Usage (1-10)**
- 10: Uses Card, Button, Input primitives with proper props
- 7-9: Uses most primitives, some custom styling
- 4-6: Mix of primitives and manual styling
- 1-3: Hardcoded styling, doesn't use primitives

**4. Styling Consistency (1-10)**
- 10: Matches design system exactly (colors, blur, edge-lit patterns)
- 7-9: Close match, minor deviations
- 4-6: Significant inconsistencies
- 1-3: Completely different styling approach

## Review Process

### Step 1: Identify Components

Scan the provided path for:
- React components (`.tsx` files)
- Component usage patterns
- Imports from primitives vs manual styling

### Step 2: Analyze Each Component

For each component, check:

**Primitives Usage:**
```tsx
// GOOD - Uses Card primitive with props
<Card edgePosition="top" edgeColor="cyan">...</Card>

// BAD - Hardcoded edge glow
<div className="relative overflow-hidden rounded-xl">
  <div className="absolute inset-x-0 top-0 h-[2px] bg-cyan-500..." />
  <div className="absolute inset-x-0 top-0 h-8 bg-gradient-to-b..." />
  ...
</div>
```

**Radix Usage:**
```tsx
// GOOD - Radix Select primitive
import { Select, SelectTrigger, SelectContent, SelectItem } from '@/features/ui/primitives/select';

// BAD - Native HTML
<select><option>...</option></select>
```

**Reusable Patterns:**
```tsx
// GOOD - Shared PillNavigation component
<PillNavigation items={...} colorVariant="orange" />

// BAD - Custom hardcoded pill navigation
<div className="backdrop-blur-sm bg-white/40...">
  {items.map(item => <button className="px-6 py-3...">...)}
</div>
```

### Step 3: Generate Scores

Calculate scores for each component based on:
- Count of primitive vs hardcoded elements
- Radix usage vs native HTML
- Styling duplication vs reuse
- Pattern consistency

### Step 4: Identify Issues

Common anti-patterns to flag:

**Hardcoded Edge-Lit Cards:**
```tsx
// BAD - Manual implementation (like KnowledgeCard currently)
<div className="pointer-events-none absolute inset-x-0 top-0">
  <div className="h-[2px] bg-cyan-500..." />
  <div className="h-8 bg-gradient-to-b..." />
</div>

// GOOD - Use Card primitive
<Card edgePosition="top" edgeColor="cyan">
```

**Native HTML Form Elements:**
```tsx
// BAD
<select>, <input type="checkbox">, <input type="radio">

// GOOD
<Select />, <Checkbox />, <RadioGroup />
```

**Duplicated Pill Navigation:**
```tsx
// BAD - Creating custom pill nav each time
// GOOD - Use PillNavigation component
```

### Step 5: Write Resolution Steps

For each issue, provide:
- What to change
- Why it matters
- Specific code example of the fix
- Impact on consistency

## Report Format

Generate `ui-consistency-review-[feature].md`:

```markdown
# UI Consistency Review

**Date**: [Today's date]
**Scope**: [Path reviewed]
**Components Analyzed**: [Count]

---

## Overall Scores

| Category | Score | Assessment |
|----------|-------|------------|
| Reusability | X/10 | [Good/Needs Work/Poor] |
| Radix Usage | X/10 | [Good/Needs Work/Poor] |
| Primitives Usage | X/10 | [Good/Needs Work/Poor] |
| Styling Consistency | X/10 | [Good/Needs Work/Poor] |

**Overall Grade**: [A-F] - [Summary]

---

## Component-by-Component Analysis

### [ComponentName.tsx]

**Scores:**
- Reusability: X/10
- Radix Usage: X/10
- Primitives Usage: X/10
- Styling Consistency: X/10

**Issues Found:**

1. **[Issue Type]** - [Description]
   - Location: `[file:line]`
   - Current: `[code snippet]`
   - Should be: `[corrected code]`
   - Impact: [Why this matters]

**Standalone vs Primitive:**
[This component SHOULD/SHOULD NOT be standalone because...]

---

## Critical Issues (Must Fix)

### 1. [Issue Title]
- **File**: `[path:line]`
- **Problem**: [Description]
- **Why**: [Impact on consistency/maintainability]
- **Fix**:
  ```tsx
  // Current
  [bad code]

  // Should be
  [good code]
  ```

---

## Recommendations

### Immediate Actions

1. **[Action]** - [Why]
2. **[Action]** - [Why]

### Pattern Improvements

1. **[Pattern]** - [Benefit]
2. **[Pattern]** - [Benefit]

### Refactoring Priorities

1. **High Priority**: [Components that break consistency]
2. **Medium Priority**: [Components that could use primitives]
3. **Low Priority**: [Minor inconsistencies]

---

## Design System Compliance

**Primitives Used Correctly:**
- [List of components using primitives properly]

**Missing Primitive Usage:**
- [List of components that should use primitives]

**Radix Compliance:**
- [List of components using Radix properly]
- [List of components using native HTML instead of Radix]

**Styling Patterns:**
- Edge-lit cards: [X using primitive, Y hardcoded]
- Pill navigation: [X using component, Y custom]
- Glass effects: [X using blur tokens, Y custom values]

---

## Next Steps

1. [Most important fix]
2. [Second priority]
3. [Third priority]

**Estimated Effort**: [X hours for full refactor]
```

## What to Scan

Based on the argument:

**If directory path** (e.g., `src/features/knowledge`):
- Scan all `.tsx` files recursively
- Analyze each component
- Aggregate scores

**If single file** (e.g., `KnowledgeCard.tsx`):
- Deep analysis of that component
- Check all its dependencies
- Compare to similar components

**If feature name** (e.g., `projects`):
- Find feature directory
- Scan all components
- Check consistency within feature

## Red Flags to Auto-Detect

Use grep/glob to find:

```bash
# CRITICAL: Dynamic Tailwind class construction (WILL NOT WORK)
grep -r "bg-\${.*}\|text-\${.*}\|border-\${.*}\|shadow-\${.*}" [path] --include="*.tsx"
grep -r "\`bg-.*-.*\`\|\`text-.*-.*\`\|\`border-.*-.*\`" [path] --include="*.tsx"

# CRITICAL: Unconstrained horizontal scroll (BREAKS LAYOUT)
grep -r "overflow-x-auto" [path] --include="*.tsx" | grep -v "w-full"

# CRITICAL: min-w-max without parent width constraint
grep -r "min-w-max" [path] --include="*.tsx"

# Non-responsive grids (BREAKS MOBILE)
grep -r "grid-cols-[2-9]" [path] --include="*.tsx" | grep -v "md:\|lg:\|sm:\|xl:"

# Fixed widths without max-width constraints
grep -r "w-\[0-9\]\|w-96\|w-80\|w-72" [path] --include="*.tsx" | grep -v "max-w-"

# Hardcoded edge-lit implementations (should use Card primitive)
grep -r "absolute inset-x-0 top-0.*bg-gradient-to-b" [path] --include="*.tsx"

# Native HTML form elements (should use Radix)
grep -r "<select>\|<option>\|<input type=\"checkbox\"\|<input type=\"radio\"" [path] --include="*.tsx"

# Hardcoded pill navigation (should use PillNavigation component)
grep -r "backdrop-blur-sm bg-white/40.*rounded-full.*flex gap-1" [path] --include="*.tsx"

# Missing text truncation on titles/headings
grep -r "<h[1-6].*className.*{" [path] --include="*.tsx" | grep -v "truncate\|line-clamp"

# Not using pre-defined classes from styles.ts
grep -r "glassCard\.variants\|glassmorphism\." [path] --files-without-match --include="*.tsx"
```

## Critical Anti-Patterns

**IMPORTANT:** Read `PRPs/ai_docs/TAILWIND_RESPONSIVE_BEST_PRACTICES.md` for complete anti-pattern reference before starting review.

### 🔴 **BREAKING: Dynamic Tailwind Class Construction**

**Problem:**
```tsx
// BROKEN - Tailwind processes at BUILD time, not runtime
const color = "cyan";
className={`bg-${color}-500`}  // CSS won't be generated

// BROKEN - String interpolation
const glow = `shadow-[0_0_30px_rgba(${rgba},0.4)]`;

// BROKEN - Template literals with variables
<div className={`text-${textColor}-700`} />
```

**Why it fails:**
- Tailwind scans code as plain text at BUILD time
- Dynamic strings aren't scanned - no CSS generated
- Results in missing styles at runtime

**Solution:**
```tsx
// CORRECT - Static class lookup
const colorClasses = {
  cyan: "bg-cyan-500 text-cyan-700",
  purple: "bg-purple-500 text-purple-700",
};
className={colorClasses[color]}

// CORRECT - Use pre-defined classes from styles.ts
const glowVariant = glassCard.variants[glowColor];
className={cn(glowVariant.glow, glowVariant.border)}

// CORRECT - Inline arbitrary values (scanned by Tailwind)
className="shadow-[0_0_30px_rgba(34,211,238,0.4)]"
```

### 🔴 **BREAKING: Unconstrained Horizontal Scroll**

**Problem:**
```tsx
// BROKEN - Forces entire page width to expand
<div className="overflow-x-auto">
  <div className="flex gap-4 min-w-max">
    {/* Wide content */}
  </div>
</div>
```

**Why it fails:**
- `min-w-max` forces container to expand beyond viewport
- Parent has no width constraint
- Entire page becomes horizontally scrollable
- UI controls shift off-screen

**Solution:**
```tsx
// CORRECT - Constrain parent, scroll child only
<div className="w-full">
  <div className="overflow-x-auto -mx-6 px-6">
    <div className="flex gap-4 min-w-max">
      {/* Scrolls within container only */}
    </div>
  </div>
</div>
```

### 🔴 **Not Using styles.ts Pre-Defined Classes**

**Problem:**
```tsx
// WRONG - Hardcoding glassmorphism
<div className="backdrop-blur-md bg-white/10 border border-gray-200 rounded-lg">

// WRONG - Not using existing glassCard.variants
const myCustomGlow = "shadow-[0_0_40px_rgba(34,211,238,0.4)]";
```

**Solution:**
```tsx
// CORRECT - Use glassCard from styles.ts
import { glassCard } from '@/features/ui/primitives/styles';
className={cn(glassCard.base, glassCard.variants.cyan.glow)}

// CORRECT - Use Card primitive with props
<Card glowColor="cyan" edgePosition="top" edgeColor="purple" />
```

### 🔴 **Non-Responsive Grid Layouts**

**Problem:**
```tsx
// BROKEN - Fixed columns break on mobile
<div className="grid grid-cols-4 gap-4">
```

**Solution:**
```tsx
// CORRECT - Responsive columns
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
```

### 🔴 **Missing Text Truncation**

**Problem:**
```tsx
// WRONG - Long text breaks layout
<h3 className="font-medium">{longTitle}</h3>
```

**Solution:**
```tsx
// CORRECT - Truncate or clamp
<h3 className="font-medium truncate">{longTitle}</h3>
<h3 className="font-medium line-clamp-2">{longTitle}</h3>
```

---

## Key Questions to Answer

1. **Does this component duplicate existing primitives?**
2. **Are there any dynamic Tailwind class constructions? (BREAKING)**
3. **Is horizontal scroll properly constrained with w-full parent?**
4. **Are grids responsive with breakpoint variants?**
5. **Should this be refactored to use Card with edgePosition/edgeColor?**
6. **Are there native HTML elements that should be Radix?**
7. **Is text truncation in place for dynamic content?**
8. **Is the glassmorphism consistent with the design system?**
9. **Can multiple components be consolidated into one reusable primitive?**
10. **Does the layout work at 375px, 768px, 1024px, and 1440px widths?**

---

## Execution Flow

### Step 1: Perform Review

Start the review and save the report to `ui-consistency-review-[feature].md` in the project root.

### Step 2: Generate PRP for Fixes

After completing the review report, automatically kick off PRP creation for the identified fixes:

```
/prp-claude-code:prp-claude-code-create UI Consistency Fixes - [feature-name]
```

**Context to provide to PRP:**
- Reference the generated `ui-consistency-review-[feature].md` report
- List all critical issues that need fixing
- Specify exact files that need refactoring
- Include anti-patterns found and their correct implementations
- Reference `PRPs/ai_docs/TAILWIND_RESPONSIVE_BEST_PRACTICES.md` for patterns

**PRP should include:**
- Task for each critical issue (dynamic classes, unconstrained scroll, etc.)
- Task for each component needing primitive refactor
- Task for responsive breakpoint additions
- Task for text truncation additions
- Validation task to run UI consistency review again to verify fixes

---

Start the review now.
