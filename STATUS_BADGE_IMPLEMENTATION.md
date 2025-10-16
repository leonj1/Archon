# Status Badge Implementation Checklist

## Overview
Add visible status badges to knowledge cards showing crawl status: "Completed" ✓, "Pending" ⏰, "Failed" ✗

**Estimated Time**: ~1.5 hours

---

## Phase 1: Backend API Mapping (15 min)

**🤖 AUTOMATED OPTION**: Run the AI agent to complete this phase automatically!
```bash
cd /home/jose/src/Archon
uv run python agents/implement_status_badge_phase1.py
```
See `agents/QUICKSTART.md` for details.

**OR follow the manual steps below:**

### 1. Update `knowledge_item_service.py` - `list_items` method
**File**: `python/src/server/services/knowledge/knowledge_item_service.py`
**Location**: Lines 129-146

- [ ] Find the metadata section in `list_items` method
- [ ] Replace hardcoded `"status": "active"` with mapping logic:
  ```python
  # Map crawl_status to frontend-expected status
  crawl_status = source_metadata.get("crawl_status", "pending")
  frontend_status = {
      "completed": "active",    # Successful crawl = active
      "failed": "error",        # Failed crawl = error
      "pending": "processing"   # Pending/in-progress = processing
  }.get(crawl_status, "processing")

  "metadata": {
      **source_metadata,
      "status": frontend_status,
      "crawl_status": crawl_status,  # Keep original for reference
      ...
  }
  ```
- [ ] Save file

### 2. Update `knowledge_item_service.py` - `_transform_source_to_item` method
**File**: `python/src/server/services/knowledge/knowledge_item_service.py`
**Location**: Lines 149-171

- [ ] Find the metadata section in `_transform_source_to_item` method
- [ ] Apply the same mapping logic as step 1
- [ ] Save file

### 3. Restart Backend
- [ ] Run: `docker compose restart archon-server`
- [ ] Wait for restart to complete (~10 seconds)
- [ ] Verify server is healthy: `curl http://localhost:8181/api/health`

---

## Phase 2: Frontend Types (5 min)

**🤖 AUTOMATED OPTION**: Run the AI agent to complete this phase automatically!
```bash
cd /home/jose/src/Archon
uv run python agents/implement_status_badge_phase2.py
```
See `agents/QUICKSTART.md` for details.

**OR follow the manual steps below:**

### 4. Update TypeScript Interface
**File**: `archon-ui-main/src/features/knowledge/types/knowledge.ts`
**Location**: Line 11 (inside `KnowledgeItemMetadata`)

- [ ] Add `crawl_status` field after `status`:
  ```typescript
  export interface KnowledgeItemMetadata {
    knowledge_type?: "technical" | "business";
    tags?: string[];
    source_type?: "url" | "file" | "group";
    status?: "active" | "processing" | "error";
    crawl_status?: "pending" | "completed" | "failed";  // NEW
    description?: string;
    // ... rest of fields
  }
  ```
- [ ] Save file

---

## Phase 3: Frontend Components (45 min)

**🤖 AUTOMATED OPTION**: Run the AI agent to complete this phase automatically!
```bash
cd /home/jose/src/Archon
uv run python agents/implement_status_badge_phase3.py
```
See `agents/QUICKSTART.md` for details.

**OR follow the manual steps below:**

### 5. Create Status Badge Component
**File**: `archon-ui-main/src/features/knowledge/components/KnowledgeCardStatus.tsx` (NEW)

- [ ] Create new file
- [ ] Copy the following code:

```typescript
/**
 * Knowledge Card Status Badge
 * Displays crawl status with appropriate icon and color
 */

import { CheckCircle, Clock, XCircle } from "lucide-react";
import { cn } from "../../ui/primitives/styles";
import { SimpleTooltip } from "../../ui/primitives/tooltip";

interface KnowledgeCardStatusProps {
  status: "active" | "processing" | "error";
  crawlStatus?: "pending" | "completed" | "failed";
  className?: string;
}

export const KnowledgeCardStatus: React.FC<KnowledgeCardStatusProps> = ({
  status,
  crawlStatus,
  className,
}) => {
  const getStatusConfig = () => {
    switch (status) {
      case "error":
        return {
          label: "Failed",
          icon: <XCircle className="w-3.5 h-3.5" />,
          bgColor: "bg-red-100 dark:bg-red-500/10",
          textColor: "text-red-700 dark:text-red-400",
          borderColor: "border-red-200 dark:border-red-500/20",
          tooltip: "Crawl failed - click refresh to retry",
        };
      case "processing":
        return {
          label: "Pending",
          icon: <Clock className="w-3.5 h-3.5" />,
          bgColor: "bg-yellow-100 dark:bg-yellow-500/10",
          textColor: "text-yellow-700 dark:text-yellow-400",
          borderColor: "border-yellow-200 dark:border-yellow-500/20",
          tooltip: "Crawl not yet completed",
        };
      case "active":
      default:
        return {
          label: "Completed",
          icon: <CheckCircle className="w-3.5 h-3.5" />,
          bgColor: "bg-green-100 dark:bg-green-500/10",
          textColor: "text-green-700 dark:text-green-400",
          borderColor: "border-green-200 dark:border-green-500/20",
          tooltip: "Successfully crawled and indexed",
        };
    }
  };

  const config = getStatusConfig();

  return (
    <SimpleTooltip content={config.tooltip}>
      <div
        className={cn(
          "inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium border",
          config.bgColor,
          config.textColor,
          config.borderColor,
          className,
        )}
      >
        {config.icon}
        <span>{config.label}</span>
      </div>
    </SimpleTooltip>
  );
};
```

- [ ] Save file

### 6. Import Status Badge in KnowledgeCard
**File**: `archon-ui-main/src/features/knowledge/components/KnowledgeCard.tsx`
**Location**: After line 25

- [ ] Add import statement:
  ```typescript
  import { KnowledgeCardStatus } from "./KnowledgeCardStatus";
  ```
- [ ] Save file

### 7. Add Status Badge to Card Header
**File**: `archon-ui-main/src/features/knowledge/components/KnowledgeCard.tsx`
**Location**: Lines 136-152

- [ ] Find the `<div className="flex items-center gap-2">` section
- [ ] Change `gap-2` to `gap-2 flex-wrap`
- [ ] Add status badge after `<KnowledgeCardType />`:
  ```typescript
  <div className="flex items-center gap-2 flex-wrap">
    <SimpleTooltip content={isUrl ? "Content from a web page" : "Uploaded document"}>
      <div className={...}>
        {getSourceIcon()}
        <span>{isUrl ? "Web Page" : "Document"}</span>
      </div>
    </SimpleTooltip>
    <KnowledgeCardType sourceId={item.source_id} knowledgeType={item.knowledge_type} />
    <KnowledgeCardStatus
      status={item.status}
      crawlStatus={item.metadata?.crawl_status}
    />
  </div>
  ```
- [ ] Save file

---

## Phase 4: Testing (30 min)

**🤖 AUTOMATED OPTION**: Run the AI agent for automated verification!
```bash
cd /home/jose/src/Archon
uv run python agents/implement_status_badge_phase4.py
```
This will run automated checks and generate a verification report. Manual UI testing still required.

**OR follow the manual steps below:**

### 8. Verify Backend Changes
- [ ] Open browser to `http://localhost:8181/api/knowledge-items`
- [ ] Check API response includes both `status` and `crawl_status` in metadata
- [ ] Verify mapping:
  - [ ] `crawl_status: "pending"` → `status: "processing"`
  - [ ] `crawl_status: "completed"` → `status: "active"`
  - [ ] `crawl_status: "failed"` → `status: "error"`

### 9. Test Frontend UI
- [ ] Open Archon UI: `http://localhost:3737`
- [ ] Navigate to Knowledge page
- [ ] Verify status badges appear on all cards
- [ ] Check that existing sources show "Pending" badge (yellow with clock icon)
- [ ] Verify badge styling matches design (green/yellow/red with proper icons)

### 10. Test Badge States
- [ ] **Pending State**: Existing sources should show yellow "Pending" badge
- [ ] **Completed State**: Refresh a source and wait for completion → should show green "Completed" badge
- [ ] **Failed State**: (Optional) Simulate failure by disabling API key → should show red "Failed" badge

### 11. Test Responsive Design
- [ ] Desktop view: Badges align properly in header
- [ ] Tablet view: Badges wrap if needed
- [ ] Mobile view: Layout doesn't break
- [ ] Dark mode: Colors look appropriate

### 12. Test Tooltips
- [ ] Hover over "Completed" badge → shows "Successfully crawled and indexed"
- [ ] Hover over "Pending" badge → shows "Crawl not yet completed"
- [ ] Hover over "Failed" badge → shows "Crawl failed - click refresh to retry"

### 13. Test Edge Cases
- [ ] Card with active operation (crawl in progress) - badge should still show
- [ ] Card with missing `crawl_status` - should default to "Pending"
- [ ] Card with optimistic state - badge should render

---

## Phase 5: Verification (10 min)

### 14. Code Quality Checks
- [ ] Run TypeScript compiler: `cd archon-ui-main && npx tsc --noEmit`
- [ ] Check for errors in new component
- [ ] Run Biome formatter: `npm run biome:fix`

### 15. Final Visual Check
- [ ] All knowledge cards show status badge
- [ ] Badge colors match design spec:
  - [ ] Green = Completed
  - [ ] Yellow = Pending
  - [ ] Red = Failed
- [ ] Icons render correctly (CheckCircle, Clock, XCircle)
- [ ] Text is readable in both light and dark mode

### 16. Documentation
- [ ] Update this checklist with any issues encountered
- [ ] Note any deviations from the plan
- [ ] Mark implementation as complete

---

## Rollback Plan (If Needed)

### Backend Rollback
1. [ ] Revert changes to `knowledge_item_service.py`
2. [ ] Restore hardcoded `"status": "active"`
3. [ ] Restart backend: `docker compose restart archon-server`

### Frontend Rollback
1. [ ] Delete `KnowledgeCardStatus.tsx`
2. [ ] Remove import and usage from `KnowledgeCard.tsx`
3. [ ] Revert changes to `knowledge.ts` types
4. [ ] Frontend will fall back to old behavior

---

## Success Criteria

- [x] Backend `crawl_status` stored correctly (from previous work)
- [ ] Backend API maps `crawl_status` to `status` for frontend
- [ ] Frontend displays status badge on all knowledge cards
- [ ] Badge shows correct state (Completed/Pending/Failed)
- [ ] Badge styling matches design (colors, icons, tooltips)
- [ ] Responsive design works on all screen sizes
- [ ] No TypeScript errors
- [ ] No console errors in browser

---

## Notes & Issues

<!-- Use this section to track any problems or deviations during implementation -->

-

---

## Completion

- [ ] All checklist items completed
- [ ] Changes tested and verified
- [ ] No regressions found
- [ ] Ready for commit

**Completed Date**: ___________
**Implemented By**: ___________
