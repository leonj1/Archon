---
description: Analyze UI components for reusability, Radix usage, primitives, and styling consistency
argument-hint: <feature path, component path, or directory>
allowed-tools: Read, Grep, Glob, Write
thinking: auto
---

# UI Consistency Review for Archon

**Review scope**: $ARGUMENTS

I'll analyze the UI components and generate a detailed report on consistency, reusability, and adherence to the Archon design system.

## Review Process

### Step 1: Load UI Standards

**CRITICAL: First, read the UI standards document:**

```
/Users/sean/Software/Archon/Archon/PRPs/ai_docs/UI_STANDARDS.md
```

This document contains ALL rules, patterns, anti-patterns, and examples. Use it as the single source of truth for the review.

### Step 2: Scan Components

Scan the provided path for:
- React components (`.tsx` files)
- Component usage patterns
- Imports from primitives vs manual styling

### Step 3: Compare Against Standards

For each component, compare against UI_STANDARDS.md:
- Check all rules from each section (0-7)
- Identify violations of anti-patterns
- Score based on adherence to standards
- Note missing patterns that should be used

### Step 4: Automated Scans

Run automated pattern detection to find common violations:

```bash
# Scan for violations (grep patterns will be in UI_STANDARDS.md)
# Examples: dynamic class construction, unconstrained scroll, non-responsive grids, etc.
```

Use the patterns and anti-patterns documented in UI_STANDARDS.md to guide the automated scans.

### Step 5: Generate Report

Create a detailed report showing:
- Overall compliance scores
- Component-by-component analysis
- Specific violations with references to UI_STANDARDS.md sections
- Recommended fixes with examples from UI_STANDARDS.md

## Report Format

Generate `ui-consistency-review-[feature].md`:

```markdown
# UI Consistency Review

**Date**: [Today's date]
**Scope**: [Path reviewed]
**Components Analyzed**: [Count]
**Standards Reference**: PRPs/ai_docs/UI_STANDARDS.md

---

## Overall Scores

| Category | Score | Assessment |
|----------|-------|------------|
| Tailwind v4 Compliance | X/10 | [Good/Needs Work/Poor] |
| Responsive Layout | X/10 | [Good/Needs Work/Poor] |
| Component Reusability | X/10 | [Good/Needs Work/Poor] |
| Radix Primitives Usage | X/10 | [Good/Needs Work/Poor] |
| Dark Mode Support | X/10 | [Good/Needs Work/Poor] |

**Overall Grade**: [A-F] - [Summary]

---

## Component-by-Component Analysis

### [ComponentName.tsx]

**Scores:** [Individual scores]

**Violations Found:**

1. **[Violation Type]** - [Description]
   - **Standards Reference**: UI_STANDARDS.md Section [X]
   - **Location**: `[file:line]`
   - **Current Code**: `[snippet]`
   - **Required Fix**: `[corrected code from UI_STANDARDS.md]`
   - **Why**: [Reference reason from UI_STANDARDS.md]

---

## Critical Violations (Must Fix)

### 1. [Violation Title]
- **File**: `[path:line]`
- **Standards Section**: UI_STANDARDS.md Section [X]
- **Rule Violated**: [Exact rule from standards]
- **Fix**: [Example from UI_STANDARDS.md Good Examples]

---

## Recommendations

All recommendations are based on PRPs/ai_docs/UI_STANDARDS.md Section 7 (Pre-Flight Checklist).

### High Priority
[List items failing critical checklist items]

### Medium Priority
[List items failing non-critical checklist items]

### Low Priority
[List minor deviations]

---

## Design System Compliance

**Standards Adherence Summary:**
- Tailwind v4 Rules: [X/Y passing]
- Responsive Layout Rules: [X/Y passing]
- Component Reusability Rules: [X/Y passing]
- Radix Primitives Rules: [X/Y passing]
- Dark Mode Rules: [X/Y passing]

---

## Next Steps

1. [Most important fix - reference UI_STANDARDS.md section]
2. [Second priority - reference UI_STANDARDS.md section]
3. [Third priority - reference UI_STANDARDS.md section]

**Estimated Effort**: [X hours for full refactor]
```

## Scanning Strategy

Based on the argument:

**If directory path** (e.g., `src/features/knowledge`):
- Scan all `.tsx` files recursively
- Analyze each component against UI_STANDARDS.md
- Aggregate scores

**If single file** (e.g., `KnowledgeCard.tsx`):
- Deep analysis of that component
- Check all sections of UI_STANDARDS.md
- Compare to similar components

**If feature name** (e.g., `projects`):
- Find feature directory
- Scan all components
- Check consistency within feature

---

## Execution Flow

### Step 1: Read UI Standards

Load `/Users/sean/Software/Archon/Archon/PRPs/ai_docs/UI_STANDARDS.md` completely.

### Step 2: Scan Target

Find all `.tsx` files in the target path.

### Step 3: Analyze Each File

For each file, check against ALL sections of UI_STANDARDS.md:
- Section 0: Project-wide Conventions
- Section 1: Radix Primitives
- Section 2: Tailwind CSS (v4)
- Section 3: Responsive Layout
- Section 4: Light/Dark Themes
- Section 5: Component Reusability
- Section 6: Tailwind Tokens
- Section 7: Pre-Flight Checklist

### Step 4: Generate Report

Create detailed report with:
- Violations mapped to UI_STANDARDS.md sections
- Examples from UI_STANDARDS.md Good Examples
- References to specific rules violated

### Step 5: Save Report

Save to `ui-consistency-review-[feature].md` in project root.

---

Start the review now.
