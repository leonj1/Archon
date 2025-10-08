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
# Hardcoded edge-lit implementations
grep -r "absolute inset-x-0 top-0" [path]

# Native HTML form elements
grep -r "<select>\|<option>\|<input type=\"checkbox\"" [path]

# Hardcoded pill navigation
grep -r "backdrop-blur-sm bg-white/40.*rounded-full" [path]

# Manual glassmorphism
grep -r "bg-gradient-to-b from-white/\|from-purple-100/" [path]

# Hardcoded colors instead of semantic tokens
grep -r "#[0-9a-fA-F]{6}" [path]
```

---

## Key Questions to Answer

1. **Does this component duplicate existing primitives?**
2. **Should this be refactored to use Card with edgePosition/edgeColor?**
3. **Are there native HTML elements that should be Radix?**
4. **Is the glassmorphism consistent with the design system?**
5. **Can multiple components be consolidated into one reusable primitive?**

---

Start the review now and save the report to `ui-consistency-review-[feature].md` in the project root.
