# PRP: Complete Style Guide Implementation

## Feature Goal
Complete the Archon style guide implementation with fully functional glassmorphism components, properly styled Radix UI toggles with size variants, example components replicating RAG settings, and improved layout patterns with proper sidebar switching behavior.

## Deliverable
A comprehensive style guide page at `/style-guide` route with:
- Fully styled Radix UI Switch components (small, medium, large sizes with icon support)
- Checkbox and Select components with neon glow effects matching RAG settings
- Working layout switcher for sidebar patterns (1/4 sidebar, 3/4 content)
- Complete page examples replacing "coming soon" placeholders
- Consistent application of glassmorphism styles across all components

## Success Definition
- [ ] All Radix UI primitives properly styled with glassmorphism effects
- [ ] Switch component has small, medium, large variants with optional icons
- [ ] RAG-style settings examples fully functional with checkboxes and selects
- [ ] Layout switcher properly adjusts content area proportions
- [ ] No "coming soon" sections - all examples implemented
- [ ] Consistent neon glow effects across all interactive elements
- [ ] All generated code includes proper AI context comments

## Context

```yaml
existing_files:
  style_implementation:
    - path: archon-ui-main/src/pages/StyleGuidePage.tsx
      purpose: Main style guide page entry point
    - path: archon-ui-main/src/components/style-guide/StyleGuideView.tsx
      purpose: Style guide view component with navigation
    - path: archon-ui-main/src/features/ui/primitives/styles.ts
      purpose: Glassmorphism styles and utilities

  existing_components:
    - path: archon-ui-main/src/components/ui/Toggle.tsx
      purpose: Current toggle implementation to replace
    - path: archon-ui-main/src/styles/toggle.css
      purpose: CSS-based toggle styles to migrate
    - path: archon-ui-main/src/components/settings/FeaturesSection.tsx
      purpose: Feature toggles using current Toggle component
    - path: archon-ui-main/src/components/settings/RAGSettings.tsx
      purpose: RAG settings with checkboxes and selects to replicate

  layout_patterns:
    - path: archon-ui-main/src/components/style-guide/patterns/LayoutsPattern.tsx
      purpose: Layout patterns including sidebar switcher
      issue: Sidebar should be 1/4 width, main content 3/4 when in sidebar mode

  placeholder_sections:
    - path: archon-ui-main/src/components/style-guide/examples/PagesExample.tsx
      purpose: Currently shows "coming soon" - needs implementation
    - path: archon-ui-main/src/components/style-guide/examples/CompositionsExample.tsx
      purpose: Has examples but could be expanded

key_requirements:
  switch_component:
    - Create new Radix UI Switch primitive at /features/ui/primitives/switch.tsx
    - Small size: 16px height, no icons
    - Medium size: 24px height, smaller icons
    - Large size: 32px height, full icons (like current feature toggles)
    - Support neon glow effects while maintaining accessibility
    - Icons should be inside the thumb element

  checkbox_component:
    - Create Radix UI Checkbox primitive at /features/ui/primitives/checkbox.tsx
    - Style with neon colors matching priority colors in styles.ts
    - Include check animation and glow effects
    - Support indeterminate state

  select_component:
    - Ensure Select primitive has glassmorphism styling
    - Add neon border highlights on focus
    - Dropdown should have glass effect backdrop

  rag_settings_example:
    - Replicate the model selection dropdown
    - Replicate the styled checkboxes with labels
    - Use new primitives not old components
    - Include neon glow effects on all interactive elements

  layout_improvements:
    - Fix sidebar layout to use proper proportions (1/4 sidebar, 3/4 content)
    - Ensure smooth transitions when switching positions
    - Top position should show cards in grid
    - Left position should show list with proper width constraints

technical_details:
  radix_packages_needed:
    - "@radix-ui/react-switch" (for Switch primitive)
    - "@radix-ui/react-checkbox" (for Checkbox primitive)
    - "@radix-ui/react-select" (already installed)
    - "@radix-ui/react-label" (for form labels)

  style_patterns:
    - Use data-[state=checked] for checked states
    - Use data-[state=unchecked] for unchecked states
    - Use data-[highlighted] for hover states
    - Apply transitions with duration-300 for smooth animations
    - Use shadow-[0_0_Xpx_rgba()] for glow effects

  icon_integration:
    - Small switch: No icons
    - Medium switch: Icons at 12x12px (h-3 w-3)
    - Large switch: Icons at 20x20px (h-5 w-5)
    - Use Lucide React icons consistently

gotchas:
  - Current Toggle component uses CSS file - need to migrate to Tailwind
  - Feature toggles in settings must continue working after migration
  - Radix Switch thumb translation must match container width
  - Checkbox indicator needs proper centering
  - Select dropdown positioning can be tricky with glass effects
  - Layout proportions must be exact (25% / 75% split)
```

## Implementation Tasks

### Phase 1: Create Missing Radix Primitives

1. **Create Switch Primitive** `/features/ui/primitives/switch.tsx`
   - Import and wrap Radix UI Switch components
   - Implement size variants (sm, md, lg) with proper dimensions
   - Add icon support for md and lg sizes
   - Apply glassmorphism styles and neon glow effects
   - Support all accent colors from styles.ts

2. **Create Checkbox Primitive** `/features/ui/primitives/checkbox.tsx`
   - Import and wrap Radix UI Checkbox components
   - Style indicator with check icon and animations
   - Add neon glow effects matching color variants
   - Support checked, unchecked, and indeterminate states

3. **Create Label Primitive** `/features/ui/primitives/label.tsx`
   - Import and wrap Radix UI Label
   - Apply consistent text styling
   - Support disabled states

### Phase 2: Update Existing Components

4. **Enhance Select Primitive** `/features/ui/primitives/select.tsx`
   - Add glassmorphism to dropdown content
   - Apply neon border effects on focus
   - Ensure proper backdrop blur on dropdown

5. **Update Card Primitive** (if needed)
   - Ensure size props work correctly
   - Verify edge glow positions
   - Check all color variants

### Phase 3: Create Style Guide Components

6. **Create Switch Configurator** `/components/style-guide/configurators/SwitchConfigurator.tsx`
   - Configuration for all three sizes
   - Icon selection (on/off icons)
   - Color variant selection
   - Glow effect toggle
   - Generate code with AI context comments

7. **Create Checkbox Configurator** `/components/style-guide/configurators/CheckboxConfigurator.tsx`
   - Color variant selection
   - State configuration (checked/indeterminate/unchecked)
   - Label positioning options
   - Generate appropriate code

8. **Create RAG Settings Example** `/components/style-guide/examples/RAGSettingsExample.tsx`
   - Model selection dropdown with glass effect
   - Styled checkboxes for feature toggles
   - Number inputs with glass styling
   - Replicate layout from actual RAG settings

### Phase 4: Fix Layout Patterns

9. **Update Sidebar Layout** in `/components/style-guide/patterns/LayoutsPattern.tsx`
   - Fix proportions: sidebar 1/4 (w-1/4), content 3/4 (w-3/4)
   - Ensure proper responsive behavior
   - Add smooth transitions between positions
   - Update code generation to reflect correct proportions

### Phase 5: Complete Page Examples

10. **Implement Landing Page Example** in `/components/style-guide/examples/PagesExample.tsx`
    - Hero section with glass effects
    - Feature cards with neon glows
    - Call-to-action buttons
    - Proper responsive layout

11. **Implement Dashboard Page Example**
    - Navigation with glass effect
    - Stats cards with different glow colors
    - Data visualization placeholders
    - Sidebar navigation pattern

12. **Implement Settings Page Example**
    - Form layout with new primitives
    - Grouped settings sections
    - Toggle switches for features
    - Save/cancel actions

### Phase 6: Migration and Integration

13. **Migrate Feature Toggles** in `/components/settings/FeaturesSection.tsx`
    - Replace Toggle component with new Switch primitive
    - Maintain all existing functionality
    - Update icon placement and sizing
    - Test all color variants

14. **Update Imports** across codebase
    - Find all Toggle imports and replace with Switch
    - Update any component using old checkbox styles
    - Ensure consistent primitive usage

15. **Remove Legacy Code**
    - Delete old `/components/ui/Toggle.tsx`
    - Remove `/styles/toggle.css`
    - Clean up any unused style utilities

## Validation Gates

```bash
# TypeScript compilation
cd archon-ui-main
npx tsc --noEmit

# Linting
npm run lint
npm run biome:fix

# Development server
npm run dev
# Navigate to http://localhost:3737/style-guide

# Manual testing checklist:
# - [ ] All switch sizes render correctly
# - [ ] Icons appear in medium and large switches
# - [ ] Checkboxes have neon glow on check
# - [ ] Select dropdowns have glass effect
# - [ ] RAG settings example matches original
# - [ ] Sidebar layout uses 1/4 - 3/4 proportions
# - [ ] Page examples are fully implemented
# - [ ] Code generation includes AI comments
# - [ ] All color variants work
# - [ ] Feature toggles in settings still work
```

## Dependencies

### NPM Packages (verify installation)
```json
{
  "@radix-ui/react-switch": "^1.0.3",
  "@radix-ui/react-checkbox": "^1.0.4",
  "@radix-ui/react-label": "^2.0.2",
  "@radix-ui/react-select": "^2.0.0"
}
```

### External Documentation
- Radix UI Switch: https://www.radix-ui.com/primitives/docs/components/switch
- Radix UI Checkbox: https://www.radix-ui.com/primitives/docs/components/checkbox
- Radix UI Select: https://www.radix-ui.com/primitives/docs/components/select
- Radix UI Styling Guide: https://www.radix-ui.com/primitives/docs/guides/styling
- Tailwind CSS Radix Plugin: https://github.com/ecklf/tailwindcss-radix

## Code Patterns to Follow

### Switch Implementation Pattern
```typescript
// Size variants object
const switchVariants = {
  size: {
    sm: { root: "h-4 w-8", thumb: "h-3 w-3 data-[state=checked]:translate-x-4" },
    md: { root: "h-6 w-11", thumb: "h-5 w-5 data-[state=checked]:translate-x-5" },
    lg: { root: "h-8 w-14", thumb: "h-7 w-7 data-[state=checked]:translate-x-6" }
  }
};

// Glow effects using shadow
"data-[state=checked]:shadow-[0_0_20px_rgba(34,211,238,0.5)]"
```

### Checkbox Pattern
```typescript
// Checkbox with indicator
<Checkbox.Root className="glassmorphism">
  <Checkbox.Indicator>
    <Check className="h-4 w-4" />
  </Checkbox.Indicator>
</Checkbox.Root>
```

### Layout Proportions
```typescript
// Correct sidebar layout
<div className="flex">
  <div className="w-1/4">Sidebar</div>
  <div className="w-3/4">Main Content</div>
</div>
```

## Success Criteria

- **Component Completeness**: All primitives created and working
- **Style Consistency**: Glassmorphism applied uniformly
- **Size Variants**: Switch has functional sm/md/lg sizes
- **Icon Support**: Icons render correctly in switches
- **Glow Effects**: Neon glows on all interactive elements
- **Layout Accuracy**: Sidebar uses exact 25%/75% split
- **Example Quality**: RAG settings replicated accurately
- **Page Examples**: No "coming soon" placeholders remain
- **Code Generation**: All configurators generate working code
- **AI Comments**: Generated code includes decision trees
- **Migration Success**: Feature toggles work with new Switch
- **Performance**: Smooth animations and transitions
- **Accessibility**: Focus states and keyboard navigation work

## Reference Implementation Locations

- Glass styles: `/archon-ui-main/src/features/ui/primitives/styles.ts`
- Current Toggle: `/archon-ui-main/src/components/ui/Toggle.tsx`
- RAG Settings: `/archon-ui-main/src/components/settings/RAGSettings.tsx:lines 400-500`
- Feature Toggles: `/archon-ui-main/src/components/settings/FeaturesSection.tsx:lines 200-316`
- Layout Pattern: `/archon-ui-main/src/components/style-guide/patterns/LayoutsPattern.tsx:lines 95-194`

## Testing Focus Areas

1. **Switch Component**
   - Size transitions are smooth
   - Icons scale appropriately
   - Glow effects visible in dark mode
   - Keyboard navigation works

2. **Checkbox Component**
   - Check animation is smooth
   - Indeterminate state renders
   - Click target is adequate

3. **Select Component**
   - Dropdown positioning correct
   - Glass effect on dropdown
   - Keyboard navigation works

4. **Layout Switcher**
   - Proportions are exactly 25%/75%
   - Transition animations smooth
   - Content reflows properly

5. **Migration**
   - All feature toggles functional
   - No console errors
   - Performance not degraded