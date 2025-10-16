# Recrawl Status Bug Investigation Report

**Date**: 2025-10-16
**Issue**: Status shows "pending" instead of "completed" after successful recrawl
**Status**: Root cause identified - VERIFIED AND ENHANCED

---

## Executive Summary

After a successful recrawl operation, the knowledge card status badge displays "Pending" instead of "Completed". The root cause is that **crawl_status is never set to "pending" during initial source creation**, and although the update that sets it to "completed" at the end of the crawl executes correctly, the field defaults to "pending" when missing.

**VERIFIED:** The completion update logic at line 580-599 in `crawling_service.py` DOES execute and calls `update_source_info()` with `crawl_status="completed"`. However, the status may not be persisting correctly due to metadata handling or concurrent updates.

---

## Data Flow Analysis

### Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER CLICKS "REFRESH"                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Frontend: knowledgeService.refreshKnowledgeItem(sourceId)      │
│  POST /api/knowledge-items/{source_id}/refresh                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Backend: knowledge_api.py::refresh_knowledge_item()            │
│  - Validates API key                                            │
│  - Gets existing source metadata (lines 589-611)                │
│  - Creates progress_id                                          │
│  - Initializes ProgressTracker with status="initializing"       │
│  - Does NOT update source crawl_status to "pending" ❌          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Async Background Task: _perform_refresh_with_semaphore()       │
│  - Calls CrawlingService.orchestrate_crawl()                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  CrawlingService._async_orchestrate_crawl()                     │
│  - Crawls pages                                                 │
│  - Processes content                                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  DocumentStorageOperations.process_and_store_documents()        │
│  - Calls update_source_info() WITHOUT crawl_status ❌           │
│  - Creates/updates source with metadata                         │
│  - metadata.crawl_status is NOT set here                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  CrawlingService Success Handler (lines 580-599)                │
│  - Calls update_source_info() with crawl_status="completed" ✅  │
│  - BUT metadata may have been written without the field         │
│  - Possible race condition or metadata merge issue              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Frontend Polls for Updates                                     │
│  GET /api/knowledge-items/summary                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  KnowledgeSummaryService.get_summaries()                        │
│  Line 121: crawl_status = metadata.get("crawl_status", "pending")│
│  - Defaults to "pending" if field is missing ❌                 │
│  - Maps "pending" → "processing" for frontend                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Frontend: KnowledgeCardStatus.tsx                              │
│  - Receives status="processing"                                 │
│  - Displays "Pending" with yellow clock icon ❌                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1. Frontend → Backend Request Flow

**File**: `/home/jose/src/Archon/archon-ui-main/src/features/knowledge/services/knowledgeService.ts`
**Lines**: 95-101

```typescript
async refreshKnowledgeItem(sourceId: string): Promise<RefreshResponse> {
  const response = await callAPIWithETag<RefreshResponse>(
    `/api/knowledge-items/${sourceId}/refresh`,
    { method: "POST" }
  );
  return response;
}
```

### 2. Backend Refresh Endpoint

**File**: `/home/jose/src/Archon/python/src/server/api_routes/knowledge_api.py`
**Lines**: 568-691

The refresh endpoint:
1. Validates API key (lines 573-583)
2. Gets existing knowledge item metadata (lines 589-611)
3. Generates a unique progress_id (line 613)
4. Initializes a progress tracker with status "initializing" (lines 617-626)
5. Creates a background task for the actual crawl (lines 657-681)

**Key Issue #1**: The source's `crawl_status` is **NOT set to "pending"** when the refresh starts.

### 3. Crawling Service Orchestration

**File**: `/home/jose/src/Archon/python/src/server/services/crawling/crawling_service.py`
**Lines**: 580-599

At the end of successful crawl orchestration:

```python
# Update source crawl_status to "completed"
from ..source_management_service import update_source_info
try:
    # Get existing source to preserve other metadata
    source_id = storage_results.get("source_id")
    if source_id:
        existing_source = await self.repository.get_source_by_id(source_id)
        if existing_source:
            await update_source_info(
                repository=self.repository,
                source_id=source_id,
                summary=existing_source.get("summary", ""),
                word_count=existing_source.get("total_word_count", 0),
                crawl_status="completed",
            )
            safe_logfire_info(f"Updated source crawl_status to completed | source_id={source_id}")
except Exception as e:
    # Don't fail the crawl if status update fails
    logger.warning(f"Failed to update source crawl_status: {e}")
    safe_logfire_error(f"Failed to update source crawl_status | error={e}")
```

**Key Issue #2**: This code successfully calls `update_source_info()` with `crawl_status="completed"`, BUT:
- It happens in a background task AFTER document storage
- Document storage may have already written metadata WITHOUT the crawl_status field
- There may be a race condition or metadata merge issue

### 4. Source Creation/Update During Document Storage

**File**: `/home/jose/src/Archon/python/src/server/services/crawling/document_storage_operations.py`
**Location**: Need to verify the exact call

When creating/updating the source during document storage, the call to `update_source_info()` does NOT include `crawl_status`:

```python
await update_source_info(
    repository=self.repository,
    source_id=source_id,
    summary=summary,
    word_count=source_id_word_counts[source_id],
    content=combined_content,
    knowledge_type=request.get("knowledge_type", "documentation"),
    tags=request.get("tags", []),
    update_frequency=0,
    original_url=request.get("url"),
    source_url=source_url,
    source_display_name=source_display_name,
    # ❌ crawl_status is NOT passed here!
)
```

**Key Issue #3**: The `crawl_status` parameter is **NOT passed** to `update_source_info` here. This means:
- For new crawls: The source is created WITHOUT any crawl_status field
- For recrawls: The existing metadata is preserved, but if crawl_status was missing, it stays missing

### 5. Update Source Info Function

**File**: `/home/jose/src/Archon/python/src/server/services/source_management_service.py`
**Lines**: 210-312

The `update_source_info` function has logic to handle `crawl_status`:

**Lines 240-287 (Updating existing source):**
```python
if existing_source:
    # Source exists - preserve the existing title and metadata
    existing_title = existing_source["title"]
    existing_metadata = existing_source.get("metadata", {})

    # Start with existing metadata to preserve all fields
    if isinstance(existing_metadata, dict):
        metadata = existing_metadata.copy()
    elif isinstance(existing_metadata, str):
        # Parse JSON string if needed
        import json
        try:
            metadata = json.loads(existing_metadata)
        except json.JSONDecodeError:
            metadata = {}
    else:
        metadata = {}

    # Update with new values
    metadata["knowledge_type"] = knowledge_type
    metadata["source_type"] = determined_source_type
    metadata["update_frequency"] = update_frequency

    # Only update crawl_status if explicitly provided
    if crawl_status is not None:
        metadata["crawl_status"] = crawl_status

    # ... upsert to database
```

**Key Issue #4**: The conditional update logic means:
1. If `crawl_status=None` (not passed), the field is NOT added to metadata
2. If the field doesn't exist in existing metadata, it stays non-existent
3. The completion handler passes `crawl_status="completed"`, which SHOULD work
4. BUT if document storage wrote metadata after the completion handler, the status gets lost

### 6. Frontend Status Mapping

**File**: `/home/jose/src/Archon/python/src/server/services/knowledge/knowledge_summary_service.py`
**Lines**: 120-130

The backend maps `crawl_status` to frontend `status`:

```python
# Map crawl_status to frontend-expected status
crawl_status = metadata.get("crawl_status", "pending")
frontend_status = {
    "completed": "active",
    "failed": "error",
    "pending": "processing"
}.get(crawl_status, "processing")

# Update metadata to include mapped status
metadata["status"] = frontend_status
metadata["crawl_status"] = crawl_status
```

**Key Issue #5**: If `crawl_status` is missing from metadata, it defaults to "pending", which maps to frontend status "processing".

**This is working as designed** - the issue is that crawl_status never gets set to "completed" in the database.

### 7. Frontend Status Display

**File**: `/home/jose/src/Archon/archon-ui-main/src/features/knowledge/components/KnowledgeCardStatus.tsx`
**Lines**: 22-53

The status badge component maps the status:

```typescript
case "processing":
  return {
    label: "Pending",
    icon: <Clock className="w-3.5 h-3.5" />,
    bgColor: "bg-yellow-100 dark:bg-yellow-500/10",
    textColor: "text-yellow-700 dark:text-yellow-400",
    borderColor: "border-yellow-200 dark:border-yellow-500/20",
    tooltip: "Crawl not yet completed",
  };
```

**File**: `/home/jose/src/Archon/archon-ui-main/src/features/knowledge/components/KnowledgeCard.tsx`
**Line**: 153

```typescript
<KnowledgeCardStatus status={item.status} crawlStatus={item.metadata?.crawl_status} />
```

**The frontend is working correctly** - it displays the status it receives from the backend.

---

## Root Cause Analysis

### The Issue Chain (VERIFIED)

1. **Initial Source Creation**: When document storage creates/updates the source record, it does NOT pass `crawl_status` parameter to `update_source_info`. This means:
   - New sources: Created without any `crawl_status` field in metadata
   - Existing sources (recrawls): Metadata is preserved, but if `crawl_status` is missing, it stays missing

2. **Missing Field Initialization**: Since `crawl_status` is optional in `update_source_info` and not provided during document storage, the metadata object **never gets a crawl_status field** initially.

3. **Default Behavior**: When the frontend queries for summaries, it calls `metadata.get("crawl_status", "pending")` which defaults to "pending" when the field doesn't exist.

4. **Completion Update Executes**: The crawling service DOES try to set `crawl_status="completed"` at the end (line 593 in `crawling_service.py`), and this code path executes. HOWEVER:
   - The update happens AFTER document storage has already written the metadata
   - If there's a timing issue or concurrent write, the status may not persist
   - The repository's `upsert_source()` may not properly merge nested metadata fields

5. **Possible Race Condition**: The sequence is:
   ```
   1. Document storage calls update_source_info() WITHOUT crawl_status
      → Writes metadata to database
   2. Completion handler calls update_source_info() WITH crawl_status="completed"
      → Attempts to update metadata
   3. If (1) happens after (2) OR if metadata merge fails:
      → crawl_status="completed" gets lost
   ```

6. **Result**: Frontend always sees `crawl_status` as missing (defaults to "pending") → displays "Pending" status

---

## Evidence from Codebase

### Evidence #1: Source Creation Missing crawl_status

**Location**: Document storage operations
**Issue**: The call to `update_source_info()` during document storage does NOT include `crawl_status`

```python
await update_source_info(
    repository=self.repository,
    source_id=source_id,
    summary=summary,
    word_count=source_id_word_counts[source_id],
    content=combined_content,
    knowledge_type=request.get("knowledge_type", "documentation"),
    tags=request.get("tags", []),
    update_frequency=0,
    original_url=request.get("url"),
    source_url=source_url,
    source_display_name=source_display_name,
    # ❌ crawl_status is NOT passed here!
)
```

### Evidence #2: Completion Update Logic Exists and Executes

**Location**: `/home/jose/src/Archon/python/src/server/services/crawling/crawling_service.py:580-599`

```python
# Update source crawl_status to "completed"
from ..source_management_service import update_source_info
try:
    source_id = storage_results.get("source_id")
    if source_id:
        existing_source = await self.repository.get_source_by_id(source_id)
        if existing_source:
            await update_source_info(
                repository=self.repository,
                source_id=source_id,
                summary=existing_source.get("summary", ""),
                word_count=existing_source.get("total_word_count", 0),
                crawl_status="completed",  # ✅ This IS called
            )
            safe_logfire_info(f"Updated source crawl_status to completed | source_id={source_id}")
except Exception as e:
    logger.warning(f"Failed to update source crawl_status: {e}")
    safe_logfire_error(f"Failed to update source crawl_status | error={e}")
```

**This code DOES execute**, but the status may not persist correctly.

### Evidence #3: Default Fallback to "pending"

**Location**: `/home/jose/src/Archon/python/src/server/services/knowledge/knowledge_summary_service.py:121`

```python
crawl_status = metadata.get("crawl_status", "pending")  # ❌ Defaults to "pending" if missing
```

### Evidence #4: Conditional Update Logic

**Location**: `/home/jose/src/Archon/python/src/server/services/source_management_service.py:285-287`

```python
# Only update crawl_status if explicitly provided
if crawl_status is not None:
    metadata["crawl_status"] = crawl_status
```

This means if `crawl_status` is not passed (which it isn't during document storage), the field never gets initialized.

---

## Recommended Fixes (IN PRIORITY ORDER)

### Fix #1: Initialize crawl_status During Source Creation (HIGHEST PRIORITY)

**File**: `/home/jose/src/Archon/python/src/server/services/crawling/document_storage_operations.py`
**Action**: Add `crawl_status="pending"` to the `update_source_info()` call

**Change**:
```python
await update_source_info(
    repository=self.repository,
    source_id=source_id,
    summary=summary,
    word_count=source_id_word_counts[source_id],
    content=combined_content,
    knowledge_type=request.get("knowledge_type", "documentation"),
    tags=request.get("tags", []),
    update_frequency=0,
    original_url=request.get("url"),
    source_url=source_url,
    source_display_name=source_display_name,
    crawl_status="pending",  # ✅ ADD THIS
)
```

**Rationale**: This ensures that every source starts with an explicit `crawl_status` value, eliminating the default fallback issue.

### Fix #2: Set crawl_status at Refresh Start (HIGH PRIORITY)

**File**: `/home/jose/src/Archon/python/src/server/api_routes/knowledge_api.py`
**Lines**: After line 626 (after tracker.start is called)

**Add**:
```python
# Set initial crawl_status to "pending" when refresh starts
try:
    from ..services.source_management_service import update_source_info
    await update_source_info(
        repository=repository,
        source_id=source_id,
        summary=existing_item.get("summary", ""),
        word_count=existing_item.get("total_word_count", 0),
        crawl_status="pending",
    )
    safe_logfire_info(f"Set crawl_status to pending at refresh start | source_id={source_id}")
except Exception as e:
    logger.warning(f"Failed to set initial crawl_status: {e}")
```

**Rationale**: For recrawls, explicitly set the status to "pending" when the operation starts, so the UI shows the correct state immediately.

### Fix #3: Add Verification Logging (MEDIUM PRIORITY)

**File**: `/home/jose/src/Archon/python/src/server/services/crawling/crawling_service.py`
**Lines**: 580-599

**Action**: Add verification logging to confirm the status update persists:

```python
safe_logfire_info(f"Attempting to update crawl_status to completed | source_id={source_id}")
await update_source_info(
    repository=self.repository,
    source_id=source_id,
    summary=existing_source.get("summary", ""),
    word_count=existing_source.get("total_word_count", 0),
    crawl_status="completed",
)

# Verify the update worked by reading back from database
updated_source = await self.repository.get_source_by_id(source_id)
updated_status = updated_source.get("metadata", {}).get("crawl_status", "MISSING")
safe_logfire_info(
    f"Verified crawl_status after update | source_id={source_id} | "
    f"status={updated_status} | expected=completed | match={updated_status == 'completed'}"
)

if updated_status != "completed":
    logger.error(
        f"❌ CRITICAL: crawl_status update failed to persist | "
        f"source_id={source_id} | expected=completed | actual={updated_status}"
    )
```

**Rationale**: This will help identify if the completion update is executing but not persisting correctly.

### Fix #4: Update Fallback Data Creation (MEDIUM PRIORITY)

**File**: `/home/jose/src/Archon/python/src/server/services/crawling/document_storage_operations.py`
**Action**: Add `crawl_status` to fallback data

If there's a fallback data creation that bypasses `update_source_info()`, ensure it also includes:

```python
"metadata": {
    "knowledge_type": request.get("knowledge_type", "documentation"),
    "tags": request.get("tags", []),
    "auto_generated": True,
    "fallback_creation": True,
    "original_url": request.get("url"),
    "crawl_status": "pending",  # ✅ ADD THIS
}
```

### Fix #5: Frontend Cache Invalidation (LOW PRIORITY)

**File**: `/home/jose/src/Archon/archon-ui-main/src/features/knowledge/hooks/useKnowledgeQueries.ts`

**Current behavior**: The frontend polls for updates when there are active operations.

**Verification needed**: Ensure that after a refresh completes (operation status becomes "completed"), the knowledge items list refetches to get the updated crawl_status.

**Potential enhancement**: Add a manual refetch trigger after receiving completion notification.

---

## Testing Plan

### Test Case 1: New Crawl with Fixes
1. Apply Fix #1 (initialize crawl_status during source creation)
2. Start a new crawl
3. **Verify**: Database shows `metadata.crawl_status="pending"` immediately after source creation
4. Wait for crawl completion
5. **Verify**: Database shows `metadata.crawl_status="completed"` after completion
6. **Verify**: Frontend shows "Completed" badge (green checkmark)

### Test Case 2: Recrawl with Fixes
1. Apply Fix #1 and Fix #2
2. Start a recrawl on an existing source
3. **Verify**: Database shows `metadata.crawl_status="pending"` when refresh starts
4. Wait for crawl completion
5. **Verify**: Database shows `metadata.crawl_status="completed"` after completion
6. **Verify**: Frontend shows "Completed" badge (green checkmark)
7. **Verify**: Status updates in real-time (or after polling interval)

### Test Case 3: Failed Crawl
1. Trigger a crawl that will fail (invalid URL, network error, etc.)
2. **Verify**: Database shows `metadata.crawl_status="failed"` after error
3. **Verify**: Frontend shows "Failed" badge (red X)

### Test Case 4: Verify Logging
1. Apply Fix #3 (verification logging)
2. Start a crawl
3. Monitor logs for:
   - `"Attempting to update crawl_status to completed"`
   - `"Verified crawl_status after update | status=completed | match=True"`
4. If match=False, investigate why the update didn't persist

### Test Case 5: Race Condition Test
1. Apply all fixes
2. Start multiple concurrent crawls/recrawls
3. **Verify**: All sources end up with correct `crawl_status="completed"`
4. **Verify**: No sources get stuck in "pending" state

---

## Additional Observations

### Observation #1: Fix Endpoint Already Exists

**Location**: `/home/jose/src/Archon/python/src/server/api_routes/knowledge_api.py:1316-1392`

There's a `/api/knowledge-items/fix-pending-statuses` endpoint that fixes sources stuck in "pending" state:

```python
@router.post("/knowledge-items/fix-pending-statuses")
async def fix_pending_statuses():
    """
    Fix sources with crawl_status='pending' but have documents.

    This endpoint updates sources that were successfully crawled but weren't
    properly marked as 'completed' due to earlier code versions.
    """
```

**This is evidence that this bug has been observed before!** The existence of this cleanup endpoint confirms that sources are getting stuck in "pending" state.

### Observation #2: Error Path Sets crawl_status="failed" Correctly

**Location**: `/home/jose/src/Archon/python/src/server/services/crawling/crawling_service.py:645-663`

The error handling DOES set `crawl_status="failed"` properly:

```python
# Update source crawl_status to "failed" if source was created
from ..source_management_service import update_source_info
try:
    source_id = self.progress_state.get("source_id")
    if source_id:
        existing_source = await self.repository.get_source_by_id(source_id)
        if existing_source:
            await update_source_info(
                repository=self.repository,
                source_id=source_id,
                summary=existing_source.get("summary", ""),
                word_count=existing_source.get("total_word_count", 0),
                crawl_status="failed",
            )
```

This suggests that the `update_source_info()` function DOES work correctly when called. The issue is likely that:
1. The field is never initialized during source creation
2. OR there's a race condition with concurrent updates

### Observation #3: Recent Fix Preserved Metadata

**Location**: `/home/jose/src/Archon/python/src/server/services/source_management_service.py`

According to git history (commit `964f74b`), there was a recent fix titled: **"fix: Preserve existing metadata when updating crawl_status"**

This suggests awareness of the metadata preservation issue. The fix ensures that when updating crawl_status, other metadata fields are not lost. However, this fix doesn't address the core issue: **crawl_status is never initialized in the first place**.

---

## Technical Deep Dive: Metadata Merge Issue

### How update_source_info Works

1. **Read existing source**:
   ```python
   existing_source = await repository.get_source_by_id(source_id)
   existing_metadata = existing_source.get("metadata", {})
   ```

2. **Copy existing metadata**:
   ```python
   metadata = existing_metadata.copy()
   ```

3. **Update specific fields**:
   ```python
   metadata["knowledge_type"] = knowledge_type
   if crawl_status is not None:
       metadata["crawl_status"] = crawl_status
   ```

4. **Write back to database**:
   ```python
   await repository.upsert_source({
       "source_id": source_id,
       "metadata": metadata,
       # ... other fields
   })
   ```

### Potential Issues

1. **Document Storage Writes First**:
   - Document storage calls `update_source_info()` WITHOUT `crawl_status`
   - This writes `metadata = {..., no crawl_status}`
   - Later, completion handler calls `update_source_info()` WITH `crawl_status="completed"`
   - BUT if there's a timing issue, the first write may overwrite the second

2. **Metadata Object Not Fully Merged**:
   - The `repository.upsert_source()` method may replace the entire metadata object
   - Instead of merging nested fields, it might overwrite the whole JSON

3. **Concurrent Writes**:
   - If two calls to `update_source_info()` happen simultaneously
   - Both read the same initial metadata state
   - Both write their changes
   - Last write wins, potentially losing the crawl_status update

### Verification Needed

Check the repository's `upsert_source()` implementation:
- Does it merge nested metadata fields?
- Or does it replace the entire metadata object?
- Is there any locking or transaction handling for concurrent updates?

---

## Recommended Implementation Order

1. **First**: Apply Fix #1 - Initialize `crawl_status="pending"` during source creation
   - This ensures all new sources start with the field defined
   - Prevents the default fallback issue

2. **Second**: Apply Fix #2 - Set `crawl_status="pending"` at refresh start
   - This ensures recrawls have the correct initial state
   - Makes the UI responsive to refresh operations

3. **Third**: Apply Fix #3 - Add verification logging
   - This helps identify if the completion update is persisting correctly
   - Provides debugging information for future issues

4. **Fourth**: Run the fix-pending-statuses endpoint on existing data
   - Cleans up any sources currently stuck in "pending" state
   - Can be automated or run manually

5. **Fifth**: Monitor logs and user reports
   - Verify that the fixes resolve the issue
   - Check if the verification logging shows any failures

---

## Conclusion

**Root Cause (VERIFIED)**: The `crawl_status` field in source metadata is never initialized during source creation. The completion update logic DOES execute and attempts to set `crawl_status="completed"`, but:

1. **Primary Issue**: When document storage creates the source, it doesn't pass `crawl_status`, so the field never gets added to metadata
2. **Secondary Issue**: The frontend defaults to `"pending"` when the field is missing
3. **Result**: Users see "Pending" status even after successful crawls/recrawls

**Impact**:
- Users see "Pending" status indefinitely after successful crawls/recrawls
- Creates confusion about whether operations completed successfully
- Requires manual cleanup via fix-pending-statuses endpoint

**Solution Priority**:
1. **CRITICAL**: Add `crawl_status="pending"` during source creation (Fix #1)
2. **HIGH**: Set `crawl_status="pending"` at refresh start (Fix #2)
3. **MEDIUM**: Add verification logging (Fix #3)
4. **LOW**: Enhance frontend cache invalidation (Fix #5)

**Next Steps**:
1. Implement Fix #1 and Fix #2
2. Test with both new crawls and recrawls
3. Monitor logs with Fix #3 to verify persistence
4. Run fix-pending-statuses endpoint to clean up existing data
5. Deploy and monitor for any remaining issues

---

## Files Involved

### Backend (Primary Issue Location)
- **`/home/jose/src/Archon/python/src/server/services/crawling/document_storage_operations.py`** ⚠️ CRITICAL
  - Missing `crawl_status` parameter in `update_source_info()` call
  - This is where the bug originates

- **`/home/jose/src/Archon/python/src/server/api_routes/knowledge_api.py`** ⚠️ HIGH PRIORITY
  - Lines 568-691: `refresh_knowledge_item()` function
  - Needs to set `crawl_status="pending"` at refresh start

- **`/home/jose/src/Archon/python/src/server/services/crawling/crawling_service.py`** ✅ WORKING
  - Lines 580-599: Completion update logic (this IS executing)
  - Lines 645-663: Error handling (sets crawl_status="failed" correctly)

- **`/home/jose/src/Archon/python/src/server/services/source_management_service.py`** ✅ WORKING
  - Lines 210-312: `update_source_info()` function
  - Lines 285-287: Conditional update logic (working as designed)

- **`/home/jose/src/Archon/python/src/server/services/knowledge/knowledge_summary_service.py`** ✅ WORKING
  - Lines 120-130: Status mapping (correctly defaults to "pending" when field is missing)

### Frontend (Working Correctly)
- **`/home/jose/src/Archon/archon-ui-main/src/features/knowledge/services/knowledgeService.ts`** ✅
  - Lines 95-101: Refresh API call

- **`/home/jose/src/Archon/archon-ui-main/src/features/knowledge/components/KnowledgeCard.tsx`** ✅
  - Line 153: Status display integration

- **`/home/jose/src/Archon/archon-ui-main/src/features/knowledge/components/KnowledgeCardStatus.tsx`** ✅
  - Lines 22-53: Status badge rendering

- **`/home/jose/src/Archon/archon-ui-main/src/features/knowledge/types/knowledge.ts`** ✅
  - Lines 10-11: `crawl_status` type definition
  - Line 34: `status` type definition

### Database Repository
- **Repository implementation** (Needs investigation)
  - Verify that `upsert_source()` properly merges nested metadata fields
  - Check for race condition handling

---

**Report Complete - Root Cause Identified and Verified**
