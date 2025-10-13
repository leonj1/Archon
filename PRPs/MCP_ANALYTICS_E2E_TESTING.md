# MCP Usage Analytics - End-to-End Testing Documentation

**Version**: 1.0
**Status**: Ready for Testing
**Created**: 2025-01-13
**Purpose**: Manual testing documentation and verification checklist for MCP Usage Analytics feature

---

## Table of Contents

1. [Testing Overview](#testing-overview)
2. [Prerequisites](#prerequisites)
3. [Test Environment Setup](#test-environment-setup)
4. [Test Scenarios](#test-scenarios)
   - [Happy Path Testing](#1-happy-path-testing)
   - [Filter Scenarios](#2-filter-scenarios)
   - [Real-Time Updates](#3-real-time-updates)
   - [Error Scenarios](#4-error-scenarios)
   - [Mobile Testing](#5-mobile-testing)
5. [Cross-Browser Testing](#cross-browser-testing)
6. [Accessibility Testing](#accessibility-testing)
7. [Performance Verification](#performance-verification)
8. [Test Data Generation](#test-data-generation)
9. [Bug Reporting Template](#bug-reporting-template)
10. [Test Summary Report](#test-summary-report)

---

## Testing Overview

### Scope
This document covers manual end-to-end testing for the MCP Usage Analytics feature, which tracks MCP tool usage and displays comprehensive analytics in the Settings page.

### Testing Goals
- Verify complete data flow from MCP tool invocation to UI display
- Validate all filter combinations work correctly
- Ensure real-time updates function as expected
- Confirm error handling is robust and user-friendly
- Validate responsive design and mobile experience
- Verify cross-browser compatibility
- Confirm accessibility standards are met

### Expected Test Duration
- Initial full test pass: 3-4 hours
- Regression testing: 1-2 hours
- Mobile device testing: 1 hour
- Cross-browser testing: 1-2 hours

### Success Criteria
- All test scenarios pass without critical issues
- No data loss or corruption
- All UI states display correctly
- Performance targets met (< 5 seconds end-to-end)
- Mobile experience is smooth
- Cross-browser compatibility verified

---

## Prerequisites

### Before Starting Testing

#### 1. Database Migration
- [ ] Migration SQL executed in Supabase
- [ ] Table `archon_mcp_usage_events` exists
- [ ] Materialized views created:
  - [ ] `archon_mcp_usage_hourly`
  - [ ] `archon_mcp_usage_daily`
- [ ] Database functions created:
  - [ ] `refresh_mcp_usage_views()`
- [ ] Indexes verified

**Verification Command**:
```sql
-- Run in Supabase SQL Editor
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name LIKE 'archon_mcp_usage%';
```

**Expected Result**: Should return 3 tables/views

#### 2. Backend Services Running
- [ ] Main FastAPI server running (port 8181)
- [ ] MCP server running (port 8051)
- [ ] Tracking middleware enabled
- [ ] Analytics API routes registered

**Verification Commands**:
```bash
# Check main server
curl http://localhost:8181/health

# Check MCP server
curl http://localhost:8051/health

# Check analytics endpoint
curl http://localhost:8181/api/mcp/analytics/summary
```

#### 3. Frontend Running
- [ ] Frontend development server running (port 3737)
- [ ] Can access Settings page
- [ ] MCP Usage Analytics section visible

**Verification**:
1. Navigate to `http://localhost:3737`
2. Go to Settings page
3. Scroll to "MCP Usage Analytics" section
4. Verify section exists (may be collapsed)

#### 4. Browser Setup
- [ ] Chrome DevTools installed
- [ ] React DevTools installed
- [ ] TanStack Query DevTools accessible
- [ ] Network throttling available

---

## Test Environment Setup

### Generate Test Data

Before testing, generate usage events for realistic testing:

#### Method 1: Using Claude or Cursor (Recommended)
```
# In Claude/Cursor with MCP connection enabled:
1. Run several RAG searches:
   - Search for "React hooks"
   - Search for "FastAPI endpoints"
   - Search for "authentication"

2. Run project operations (if projects enabled):
   - List projects
   - Create a test project
   - List tasks

3. Run document searches:
   - Search code examples
   - List available sources
```

#### Method 2: Direct API Calls
```bash
# RAG search (generates 1 event)
curl -X POST http://localhost:8051/rag_search_knowledge_base \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication", "match_count": 5}'

# List projects (generates 1 event)
curl http://localhost:8051/find_projects

# Get available sources (generates 1 event)
curl http://localhost:8051/rag_get_available_sources
```

#### Method 3: Test Data Script
```python
# Create file: generate_test_data.py
import requests
import time
import random

MCP_URL = "http://localhost:8051"

test_queries = [
    "authentication JWT",
    "React hooks useState",
    "FastAPI middleware",
    "database migration",
    "TypeScript types"
]

for i in range(20):
    query = random.choice(test_queries)
    requests.post(f"{MCP_URL}/rag_search_knowledge_base",
                  json={"query": query, "match_count": 5})
    time.sleep(0.5)

print("Generated 20 test events")
```

**Run with**: `python generate_test_data.py`

#### Verify Test Data Created
```sql
-- Run in Supabase SQL Editor
SELECT COUNT(*) as event_count FROM archon_mcp_usage_events;
SELECT tool_category, COUNT(*) FROM archon_mcp_usage_events
GROUP BY tool_category;
```

**Expected**: At least 10-20 events across different categories

---

## Test Scenarios

### 1. Happy Path Testing

**Objective**: Verify the complete flow from MCP tool invocation to UI display works correctly.

#### Test Case 1.1: Basic Data Flow

**Steps**:
1. [ ] Open Chrome DevTools → Network tab
2. [ ] Navigate to Settings page → MCP Usage Analytics
3. [ ] Expand the analytics section if collapsed
4. [ ] Note the current "Total Calls" number in summary card
5. [ ] Keep Settings page open
6. [ ] In a separate terminal/Claude, run an MCP tool:
   ```bash
   curl -X POST http://localhost:8051/rag_search_knowledge_base \
     -H "Content-Type: application/json" \
     -d '{"query": "test query", "match_count": 5}'
   ```
7. [ ] Wait 5 seconds (staleTime expiration)
8. [ ] Observe network requests in DevTools
9. [ ] Check if "Total Calls" incremented by 1

**Expected Results**:
- [ ] Network request to `/api/mcp/analytics/summary` appears
- [ ] Total calls increased by 1
- [ ] No console errors
- [ ] UI updates smoothly without flash
- [ ] Complete flow takes < 5 seconds

**Screenshot Required**: Yes - Before and after comparison

**Notes**:
```
Total Calls Before: _____
Total Calls After:  _____
Time to Update:     _____ seconds
Any Errors:         _____
```

---

#### Test Case 1.2: Summary Cards Accuracy

**Steps**:
1. [ ] Note all summary card values:
   - Total Calls (24h)
   - Success Rate (%)
   - Failed Calls
2. [ ] Query database directly to verify accuracy:
   ```sql
   -- Run in Supabase
   SELECT
     COUNT(*) as total_calls,
     SUM(CASE WHEN error_message IS NULL THEN 1 ELSE 0 END) as successful,
     SUM(CASE WHEN error_message IS NOT NULL THEN 1 ELSE 0 END) as failed,
     ROUND(100.0 * SUM(CASE WHEN error_message IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) as success_rate
   FROM archon_mcp_usage_events
   WHERE timestamp >= NOW() - INTERVAL '24 hours';
   ```
3. [ ] Compare UI values with database values

**Expected Results**:
- [ ] Total Calls matches database count (±1 due to timing)
- [ ] Success Rate matches calculated percentage
- [ ] Failed Calls matches database error count
- [ ] All numbers formatted correctly (commas, decimals)

**Data Verification**:
```
UI Total Calls:     _____
DB Total Calls:     _____
Match:              [ ] Yes  [ ] No

UI Success Rate:    _____%
DB Success Rate:    _____%
Match:              [ ] Yes  [ ] No

UI Failed Calls:    _____
DB Failed Calls:    _____
Match:              [ ] Yes  [ ] No
```

---

#### Test Case 1.3: Chart Display and Data

**Steps**:
1. [ ] Verify bar chart is visible and rendered
2. [ ] Check chart has both Total and Error bars
3. [ ] Hover over bars to see tooltips
4. [ ] Verify tooltip shows:
   - Hour/timestamp
   - Total calls
   - Error count
   - Success rate percentage
5. [ ] Count number of bars (should match time range)

**Expected Results**:
- [ ] Chart renders without blank areas
- [ ] Bars are color-coded (blue for total, red for errors)
- [ ] Tooltips appear on hover
- [ ] Tooltip data is accurate
- [ ] X-axis labels are readable
- [ ] Y-axis shows appropriate scale
- [ ] Legend is visible and correct

**Visual Verification**:
- [ ] Chart is not pixelated
- [ ] Colors match theme (Tron-inspired)
- [ ] Dark mode works correctly
- [ ] Animation is smooth (if any)

**Screenshot Required**: Yes - Full chart view with tooltip visible

---

#### Test Case 1.4: Top Tools Table

**Steps**:
1. [ ] Scroll to "Top Tools" table
2. [ ] Verify table shows tool names and call counts
3. [ ] Verify tools are sorted by call count (descending)
4. [ ] Check that only top 10 tools are shown
5. [ ] Query database to verify accuracy:
   ```sql
   SELECT tool_name, COUNT(*) as calls
   FROM archon_mcp_usage_events
   WHERE timestamp >= NOW() - INTERVAL '24 hours'
   GROUP BY tool_name
   ORDER BY calls DESC
   LIMIT 10;
   ```

**Expected Results**:
- [ ] Table displays correctly
- [ ] Tool names match database
- [ ] Call counts match database
- [ ] Sorting is correct (highest to lowest)
- [ ] Table is limited to 10 rows
- [ ] Hover effect works on rows

**Screenshot Required**: Yes - Full table view

---

### 2. Filter Scenarios

**Objective**: Verify all filter combinations work correctly and update the UI appropriately.

#### Test Case 2.1: Time Range Filter

**Steps**:
1. [ ] Note current chart data with 24h filter
2. [ ] Change time range to 48 hours
3. [ ] Observe chart update
4. [ ] Verify more data points appear (up to 48 bars)
5. [ ] Change to 7 days (168 hours)
6. [ ] Verify chart shows weekly data
7. [ ] Change back to 24 hours
8. [ ] Verify chart returns to original state

**Expected Results**:
- [ ] Chart updates immediately on filter change
- [ ] Loading state shown briefly (< 500ms)
- [ ] Number of bars matches selected time range
- [ ] X-axis labels adjust appropriately
- [ ] Summary cards update to reflect time range
- [ ] No data loss between filter changes
- [ ] Network request includes correct `hours` parameter

**Verification in DevTools**:
- [ ] Check Network tab for API calls
- [ ] Verify query parameters: `?hours=24`, `?hours=48`, `?hours=168`
- [ ] Check TanStack Query DevTools for cache updates

**Screenshot Required**: Yes - Chart at 24h, 48h, and 7d

**Notes**:
```
24h bars count:   _____
48h bars count:   _____
7d bars count:    _____
Any issues:       _____
```

---

#### Test Case 2.2: Category Filter

**Steps**:
1. [ ] Note current chart with "All Categories" filter
2. [ ] Change category to "RAG"
3. [ ] Verify chart shows only RAG tool usage
4. [ ] Check summary cards reflect RAG data only
5. [ ] Change to "Project" category
6. [ ] Verify chart updates to show project operations
7. [ ] Change to "Task" category
8. [ ] Change to "Document" category
9. [ ] Return to "All Categories"
10. [ ] Verify full data restored

**Expected Results**:
- [ ] Chart data filters correctly for each category
- [ ] Summary cards update to show category-specific metrics
- [ ] Top Tools table shows only tools from selected category
- [ ] Empty state shown if no data for category
- [ ] Filter persists during time range changes
- [ ] Network requests include correct `tool_category` parameter

**Verification in DevTools**:
```bash
# Check API calls include category filter
# Example: /api/mcp/analytics/hourly?hours=24&tool_category=rag
```

**Test Matrix**:

| Category  | Has Data? | Chart Updates? | Summary Correct? | Top Tools Filtered? |
|-----------|-----------|----------------|------------------|---------------------|
| All       | [ ] Yes   | [ ] Yes        | [ ] Yes          | [ ] Yes             |
| RAG       | [ ] Yes   | [ ] Yes        | [ ] Yes          | [ ] Yes             |
| Project   | [ ] Yes   | [ ] Yes        | [ ] Yes          | [ ] Yes             |
| Task      | [ ] Yes   | [ ] Yes        | [ ] Yes          | [ ] Yes             |
| Document  | [ ] Yes   | [ ] Yes        | [ ] Yes          | [ ] Yes             |

**Screenshot Required**: Yes - Each category filter result

---

#### Test Case 2.3: Combined Filters

**Steps**:
1. [ ] Set time range to 24 hours
2. [ ] Set category to RAG
3. [ ] Verify both filters applied
4. [ ] Change time range to 48 hours (keep RAG selected)
5. [ ] Verify RAG data for 48 hours shown
6. [ ] Change category to All (keep 48 hours)
7. [ ] Verify all data for 48 hours shown

**Expected Results**:
- [ ] Multiple filters work together correctly
- [ ] Changing one filter preserves the other
- [ ] Data accuracy maintained with combined filters
- [ ] Network requests include both parameters
- [ ] UI state synchronized correctly

**Network Verification**:
```
Expected URL: /api/mcp/analytics/hourly?hours=48&tool_category=rag
Actual URL:   _____________________________________
Match:        [ ] Yes  [ ] No
```

---

### 3. Real-Time Updates

**Objective**: Verify the UI auto-refreshes and displays new data without manual intervention.

#### Test Case 3.1: Automatic Data Refresh

**Steps**:
1. [ ] Open Settings → MCP Usage Analytics
2. [ ] Note current total calls count
3. [ ] Keep page open and visible
4. [ ] In another terminal, generate 5 new events:
   ```bash
   for i in {1..5}; do
     curl -X POST http://localhost:8051/rag_search_knowledge_base \
       -H "Content-Type: application/json" \
       -d '{"query": "test '$i'", "match_count": 5}'
     sleep 1
   done
   ```
5. [ ] Wait for staleTime to expire (5 seconds for summary)
6. [ ] Observe if UI updates automatically
7. [ ] Verify new events reflected in UI

**Expected Results**:
- [ ] UI auto-refreshes after staleTime expires
- [ ] Total calls increases by 5
- [ ] Chart updates with new data
- [ ] No page reload required
- [ ] Update happens smoothly (no flash)
- [ ] TanStack Query triggers refetch automatically

**Timing Verification**:
```
Events generated at: _____
UI updated at:       _____
Time difference:     _____ seconds
Expected (5-10s):    [ ] Yes  [ ] No
```

---

#### Test Case 3.2: Tab Visibility Handling

**Steps**:
1. [ ] Open Settings → MCP Usage Analytics
2. [ ] Note current data
3. [ ] Switch to a different browser tab
4. [ ] Wait 30 seconds
5. [ ] Generate 3 new events in terminal
6. [ ] Switch back to Settings tab
7. [ ] Observe if data updates immediately

**Expected Results**:
- [ ] Polling pauses when tab is hidden (verify in Network tab)
- [ ] Data refetches immediately when tab becomes visible
- [ ] New data appears within 1-2 seconds of tab focus
- [ ] No excessive network requests while hidden

**Network Activity Log**:
```
Requests while tab hidden:  _____
Requests after tab visible: _____
Behavior correct:           [ ] Yes  [ ] No
```

---

#### Test Case 3.3: No Data Loss During Refresh

**Steps**:
1. [ ] Apply filters (e.g., 48h + RAG category)
2. [ ] Note specific chart values
3. [ ] Wait for automatic refresh (5-10 seconds)
4. [ ] Verify chart data remains consistent
5. [ ] Verify filters still applied after refresh
6. [ ] Change filter and verify data updates correctly

**Expected Results**:
- [ ] No data loss during automatic refresh
- [ ] Filter state preserved
- [ ] Chart doesn't flicker or reset
- [ ] Scroll position maintained
- [ ] User interactions not interrupted

---

### 4. Error Scenarios

**Objective**: Verify robust error handling and user-friendly error messages.

#### Test Case 4.1: API Failure - Network Error

**Preparation**: Simulate API failure by stopping the backend server temporarily.

**Steps**:
1. [ ] Open Settings → MCP Usage Analytics
2. [ ] Stop the backend server:
   ```bash
   docker compose stop archon-server
   # or kill the FastAPI process
   ```
3. [ ] Wait for next auto-refresh (5-10 seconds)
4. [ ] Observe error state displayed
5. [ ] Verify error message is user-friendly
6. [ ] Check if retry button is available
7. [ ] Restart backend server:
   ```bash
   docker compose start archon-server
   ```
8. [ ] Click retry button (or wait for auto-retry)
9. [ ] Verify data loads successfully

**Expected Results**:
- [ ] Error state displays clearly
- [ ] Error message is user-friendly (not technical stack trace)
- [ ] Retry button is visible and functional
- [ ] UI doesn't crash or show blank screen
- [ ] Error icon (AlertCircle) displayed
- [ ] After retry, data loads successfully
- [ ] No console errors that break the app

**Error State Checklist**:
- [ ] Error message readable
- [ ] Icon appropriate (red AlertCircle)
- [ ] Retry button present
- [ ] Layout not broken
- [ ] Dark mode error state works

**Screenshot Required**: Yes - Error state display

---

#### Test Case 4.2: Empty Data State

**Preparation**: Clear all usage events from database.

**Steps**:
1. [ ] Clear usage events (CAUTION: Test environment only):
   ```sql
   -- Run in Supabase SQL Editor (TEST ENV ONLY)
   DELETE FROM archon_mcp_usage_events;
   ```
2. [ ] Refresh analytics page
3. [ ] Observe empty state displayed
4. [ ] Verify empty state message is helpful
5. [ ] Verify chart area shows empty state (not broken)
6. [ ] Generate a new event
7. [ ] Wait for refresh
8. [ ] Verify data appears correctly

**Expected Results**:
- [ ] Empty state is clear and informative
- [ ] Message explains what to do (use MCP tools)
- [ ] Icon displayed (Activity icon)
- [ ] No broken charts or error messages
- [ ] Layout remains intact
- [ ] After new data, UI populates correctly

**Empty State Checklist**:
- [ ] "No data available" message shown
- [ ] Helpful guidance provided
- [ ] Icon visible and appropriate
- [ ] No JavaScript errors
- [ ] Can recover when data added

**Screenshot Required**: Yes - Empty state display

---

#### Test Case 4.3: Invalid Query Parameters

**Steps**:
1. [ ] Open DevTools → Console
2. [ ] Manually call API with invalid parameters:
   ```javascript
   fetch('http://localhost:8181/api/mcp/analytics/hourly?hours=999')
     .then(r => r.json())
     .then(console.log)
   ```
3. [ ] Verify API returns 400 Bad Request
4. [ ] Try negative hours:
   ```javascript
   fetch('http://localhost:8181/api/mcp/analytics/hourly?hours=-5')
     .then(r => r.json())
     .then(console.log)
   ```
5. [ ] Try invalid category:
   ```javascript
   fetch('http://localhost:8181/api/mcp/analytics/hourly?tool_category=invalid')
     .then(r => r.json())
     .then(console.log)
   ```

**Expected Results**:
- [ ] API returns appropriate HTTP status codes
- [ ] Error messages are descriptive
- [ ] UI handles API errors gracefully
- [ ] No unhandled promise rejections
- [ ] App doesn't crash

**API Response Verification**:
```
Status Code for hours=999:     _____
Status Code for hours=-5:      _____
Status Code for invalid cat:   _____
All handled correctly:         [ ] Yes  [ ] No
```

---

### 5. Mobile Testing

**Objective**: Verify responsive design and mobile usability.

#### Test Case 5.1: Mobile Browser Testing (Chrome DevTools)

**Steps**:
1. [ ] Open Chrome DevTools
2. [ ] Enable device emulation (Cmd/Ctrl + Shift + M)
3. [ ] Test on iPhone SE (375px width):
   - [ ] Navigate to Settings → Analytics
   - [ ] Expand analytics section
   - [ ] Verify summary cards stack vertically
   - [ ] Verify filters are usable
   - [ ] Verify chart is readable
   - [ ] Scroll through entire page
4. [ ] Test on iPad (768px width):
   - [ ] Verify layout adjusts appropriately
   - [ ] Check grid layouts
   - [ ] Verify chart sizing
5. [ ] Test on iPhone 14 Pro Max (430px width)
6. [ ] Test landscape orientation

**Expected Results**:
- [ ] All content visible without horizontal scroll
- [ ] Summary cards stack vertically on mobile
- [ ] Filters remain usable (dropdowns work)
- [ ] Chart scales appropriately
- [ ] Touch targets are adequate (min 44x44px)
- [ ] Text is readable (not too small)
- [ ] Table scrolls horizontally if needed
- [ ] No layout breaks at any breakpoint

**Responsive Breakpoints Checklist**:

| Width   | Device        | Layout OK? | Filters Work? | Chart Readable? | Touch Friendly? |
|---------|---------------|------------|---------------|-----------------|-----------------|
| 375px   | iPhone SE     | [ ]        | [ ]           | [ ]             | [ ]             |
| 390px   | iPhone 14     | [ ]        | [ ]           | [ ]             | [ ]             |
| 430px   | iPhone 14 Max | [ ]        | [ ]           | [ ]             | [ ]             |
| 768px   | iPad          | [ ]        | [ ]           | [ ]             | [ ]             |
| 820px   | iPad Air      | [ ]        | [ ]           | [ ]             | [ ]             |

**Screenshot Required**: Yes - Each breakpoint (portrait and landscape)

---

#### Test Case 5.2: Physical Device Testing

**Preparation**: Use actual mobile devices or emulators.

**Android Device (if available)**:
1. [ ] Open Chrome on Android device
2. [ ] Navigate to `http://<your-ip>:3737`
3. [ ] Test all touch interactions:
   - [ ] Tap to expand analytics section
   - [ ] Select time range filter
   - [ ] Select category filter
   - [ ] Scroll through page
   - [ ] Tap chart bars (verify tooltips)
   - [ ] Scroll table horizontally
4. [ ] Test in portrait mode
5. [ ] Test in landscape mode

**iOS Device (if available)**:
1. [ ] Open Safari on iOS device
2. [ ] Navigate to `http://<your-ip>:3737`
3. [ ] Test all touch interactions (same as Android)
4. [ ] Test both orientations

**Expected Results**:
- [ ] Touch interactions responsive
- [ ] No tap delay (300ms)
- [ ] Tooltips appear on tap
- [ ] Scrolling smooth (60fps)
- [ ] Filters open correctly
- [ ] No layout issues
- [ ] Performance acceptable

**Performance Notes**:
```
Device tested:          _____
Touch delay:            [ ] None  [ ] Noticeable
Scroll performance:     [ ] Smooth  [ ] Janky
Chart performance:      [ ] Good    [ ] Poor
Overall experience:     [ ] Good    [ ] Needs work
```

---

#### Test Case 5.3: Mobile Chart Readability

**Steps**:
1. [ ] On mobile device (< 480px width)
2. [ ] Open analytics with chart visible
3. [ ] Verify bar chart is readable:
   - [ ] Bars are wide enough to tap
   - [ ] X-axis labels readable (not overlapping)
   - [ ] Y-axis labels readable
   - [ ] Legend visible
4. [ ] Tap on bars to show tooltips
5. [ ] Verify tooltip content readable
6. [ ] Rotate to landscape
7. [ ] Verify chart improves in landscape

**Expected Results**:
- [ ] Chart adapts to mobile viewport
- [ ] All text is legible (min 12px)
- [ ] Bars are tappable (min 30px width)
- [ ] Tooltips don't overflow screen
- [ ] Legend doesn't overlap chart
- [ ] Landscape mode improves readability
- [ ] No horizontal scroll for chart

**Screenshot Required**: Yes - Portrait and landscape chart views

---

### Cross-Browser Testing

**Objective**: Verify compatibility across major browsers.

#### Browser Test Matrix

Test the following scenarios on each browser:
1. Page loads without errors
2. Summary cards display correctly
3. Chart renders properly
4. Filters work
5. Tooltips appear
6. Dark mode works
7. Real-time updates function

**Chrome (Latest)**
- [ ] Version tested: _____
- [ ] All scenarios pass
- [ ] Console errors: None / List: _____
- [ ] Screenshot captured

**Firefox (Latest)**
- [ ] Version tested: _____
- [ ] All scenarios pass
- [ ] Console errors: None / List: _____
- [ ] Screenshot captured
- [ ] Special notes: _____

**Safari (Latest - macOS/iOS)**
- [ ] Version tested: _____
- [ ] All scenarios pass
- [ ] Console errors: None / List: _____
- [ ] Screenshot captured
- [ ] Special notes: _____

**Edge (Latest)**
- [ ] Version tested: _____
- [ ] All scenarios pass
- [ ] Console errors: None / List: _____
- [ ] Screenshot captured
- [ ] Special notes: _____

**Known Browser Issues**:
```
Browser:     Issue Description:                      Workaround:
_________    ________________________________        ________________________________
_________    ________________________________        ________________________________
```

---

## Accessibility Testing

**Objective**: Verify WCAG AA compliance and screen reader compatibility.

### Test Case A1: Keyboard Navigation

**Steps**:
1. [ ] Navigate to Settings → Analytics using only keyboard
2. [ ] Tab through all interactive elements:
   - [ ] Expand/collapse button
   - [ ] Time range filter
   - [ ] Category filter
   - [ ] Chart bars (if interactive)
   - [ ] Top tools table rows
3. [ ] Verify focus indicators visible for each element
4. [ ] Verify tab order is logical (top to bottom, left to right)
5. [ ] Test keyboard shortcuts (if any)

**Expected Results**:
- [ ] All interactive elements reachable via Tab
- [ ] Focus indicators clearly visible
- [ ] Focus ring has sufficient contrast
- [ ] Tab order makes sense
- [ ] Enter/Space keys activate controls
- [ ] Escape closes dropdowns
- [ ] No keyboard traps

**Accessibility Checklist**:
- [ ] Focus visible at all times
- [ ] Focus not hidden behind other elements
- [ ] Logical tab order
- [ ] All controls keyboard accessible
- [ ] No keyboard traps

---

### Test Case A2: Screen Reader Testing

**Preparation**: Enable VoiceOver (Mac) or NVDA (Windows)

**Steps**:
1. [ ] Enable screen reader
2. [ ] Navigate to Settings → Analytics
3. [ ] Verify section title is announced
4. [ ] Navigate to summary cards:
   - [ ] Verify card labels announced
   - [ ] Verify values announced
5. [ ] Navigate to filters:
   - [ ] Verify filter labels announced
   - [ ] Verify selected values announced
6. [ ] Navigate to chart area:
   - [ ] Verify chart title/description announced
   - [ ] Verify chart data accessible (via table alternative or ARIA)
7. [ ] Navigate to top tools table:
   - [ ] Verify table structure announced
   - [ ] Verify headers announced
   - [ ] Verify cell content announced

**Expected Results**:
- [ ] All content accessible to screen reader
- [ ] ARIA labels present and meaningful
- [ ] Semantic HTML used correctly
- [ ] Chart has text alternative or data table
- [ ] Form controls properly labeled
- [ ] Status updates announced (ARIA live regions)

---

### Test Case A3: Color Contrast

**Steps**:
1. [ ] Use browser extension (e.g., Lighthouse, axe DevTools)
2. [ ] Run accessibility audit
3. [ ] Check color contrast ratios:
   - [ ] Text vs background: min 4.5:1
   - [ ] Large text vs background: min 3:1
   - [ ] Chart bars vs background
   - [ ] Icons vs background
4. [ ] Test in both light and dark mode

**Expected Results**:
- [ ] All text meets WCAG AA contrast (4.5:1)
- [ ] Large text meets 3:1 ratio
- [ ] Chart elements have sufficient contrast
- [ ] No reliance on color alone for information
- [ ] Dark mode passes contrast checks

**Lighthouse Audit**:
```
Accessibility Score: _____ / 100
Target:             90+
Pass:               [ ] Yes  [ ] No
Issues found:       _____
```

---

### Test Case A4: ARIA Attributes

**Steps**:
1. [ ] Inspect summary cards in DevTools
2. [ ] Verify ARIA attributes:
   - [ ] `aria-label` on cards
   - [ ] `role` attributes appropriate
   - [ ] `aria-describedby` for additional info
3. [ ] Check chart container:
   - [ ] `role="img"` or `role="figure"`
   - [ ] `aria-label` describes chart
   - [ ] `aria-describedby` for details
4. [ ] Check filters:
   - [ ] `aria-labelledby` connects labels
   - [ ] `aria-expanded` for dropdowns
   - [ ] `aria-selected` for options

**Expected Results**:
- [ ] ARIA attributes present and correct
- [ ] Roles match element purposes
- [ ] Labels are descriptive
- [ ] Live regions for dynamic updates
- [ ] No ARIA overuse (semantic HTML preferred)

---

## Performance Verification

### Test Case P1: API Response Times

**Steps**:
1. [ ] Open DevTools → Network tab
2. [ ] Clear cache and hard reload
3. [ ] Load analytics page
4. [ ] Measure API response times:
   ```
   /api/mcp/analytics/summary:  _____ ms
   /api/mcp/analytics/hourly:   _____ ms
   ```
5. [ ] Apply filters and measure again
6. [ ] Generate load with multiple requests:
   ```bash
   for i in {1..10}; do
     curl http://localhost:8181/api/mcp/analytics/hourly?hours=24 &
   done
   ```
7. [ ] Measure 95th percentile response time

**Target Metrics**:
- [ ] Summary endpoint: < 200ms
- [ ] Hourly endpoint: < 500ms
- [ ] Daily endpoint: < 500ms
- [ ] 95th percentile: < 500ms

**Actual Metrics**:
```
Summary avg:    _____ ms  [ ] Pass  [ ] Fail
Hourly avg:     _____ ms  [ ] Pass  [ ] Fail
Daily avg:      _____ ms  [ ] Pass  [ ] Fail
95th percentile: _____ ms  [ ] Pass  [ ] Fail
```

---

### Test Case P2: Frontend Performance

**Steps**:
1. [ ] Open Chrome DevTools → Performance tab
2. [ ] Start recording
3. [ ] Load Settings → Analytics
4. [ ] Stop recording after page fully loaded
5. [ ] Analyze performance metrics:
   - [ ] First Contentful Paint (FCP)
   - [ ] Largest Contentful Paint (LCP)
   - [ ] Time to Interactive (TTI)
   - [ ] Total Blocking Time (TBT)
6. [ ] Run Lighthouse audit
7. [ ] Test filter change performance:
   - [ ] Record performance
   - [ ] Change time range filter
   - [ ] Measure render time

**Target Metrics**:
- [ ] Initial page load: < 2 seconds
- [ ] Chart render: < 200ms
- [ ] Filter change response: < 100ms
- [ ] Lighthouse Performance: > 90

**Actual Metrics**:
```
FCP:               _____ ms  [ ] Pass  [ ] Fail
LCP:               _____ ms  [ ] Pass  [ ] Fail
TTI:               _____ ms  [ ] Pass  [ ] Fail
Chart render:      _____ ms  [ ] Pass  [ ] Fail
Lighthouse score:  _____     [ ] Pass  [ ] Fail
```

---

### Test Case P3: Memory Usage

**Steps**:
1. [ ] Open Chrome DevTools → Memory tab
2. [ ] Take heap snapshot before loading analytics
3. [ ] Load analytics page
4. [ ] Take heap snapshot after load
5. [ ] Apply various filters 20 times
6. [ ] Take heap snapshot after interactions
7. [ ] Check for memory leaks (heap size keeps growing)

**Expected Results**:
- [ ] No significant memory leaks
- [ ] Heap size stabilizes after initial load
- [ ] No detached DOM nodes accumulating
- [ ] TanStack Query cache not growing unbounded

**Memory Analysis**:
```
Initial heap:      _____ MB
After load:        _____ MB
After interactions: _____ MB
Growth:            _____ MB
Acceptable:        [ ] Yes  [ ] No
```

---

### Test Case P4: Bundle Size Impact

**Steps**:
1. [ ] Build production bundle:
   ```bash
   cd archon-ui-main
   npm run build
   ```
2. [ ] Check bundle size analysis
3. [ ] Compare with build before analytics feature
4. [ ] Verify Recharts is tree-shaken properly

**Expected Results**:
- [ ] Bundle size increase < 200KB (gzipped)
- [ ] Recharts imported efficiently
- [ ] No duplicate dependencies
- [ ] Code splitting works (if implemented)

**Bundle Analysis**:
```
Bundle size before:  _____ KB
Bundle size after:   _____ KB
Increase:            _____ KB
Acceptable:          [ ] Yes  [ ] No
```

---

## Test Data Generation

### Generating Realistic Test Data

For comprehensive testing, generate varied data:

#### Script: `generate_comprehensive_test_data.py`

```python
import requests
import time
import random
from datetime import datetime, timedelta

MCP_URL = "http://localhost:8051"

# Categories of operations
operations = {
    "rag": [
        "rag_search_knowledge_base",
        "rag_search_code_examples",
        "rag_get_available_sources",
        "rag_list_pages_for_source",
        "rag_read_full_page"
    ],
    "project": [
        "find_projects",
        "manage_project"
    ],
    "task": [
        "find_tasks",
        "manage_task"
    ],
    "document": [
        "find_documents",
        "manage_document"
    ]
}

# Test queries for RAG
test_queries = [
    "authentication",
    "React hooks",
    "FastAPI",
    "database migration",
    "TypeScript",
    "testing patterns",
    "API endpoints",
    "state management"
]

print("Generating comprehensive test data...")

# Generate 50 events spread over 48 hours
for i in range(50):
    # Random category
    category = random.choice(list(operations.keys()))

    # For RAG, make actual searches
    if category == "rag":
        query = random.choice(test_queries)
        try:
            requests.post(
                f"{MCP_URL}/rag_search_knowledge_base",
                json={"query": query, "match_count": random.randint(3, 10)},
                timeout=5
            )
            print(f"✓ Generated RAG search: {query}")
        except Exception as e:
            print(f"✗ Failed: {e}")

    # For other categories, call list endpoints
    else:
        operation = operations[category][0]  # Use first (list) operation
        try:
            requests.get(f"{MCP_URL}/{operation}", timeout=5)
            print(f"✓ Generated {category} operation")
        except Exception as e:
            print(f"✗ Failed: {e}")

    # Random delay to spread events over time
    time.sleep(random.uniform(0.3, 2))

print(f"\n✓ Generated 50 test events")
print("Check Supabase for events:")
print("SELECT COUNT(*), tool_category FROM archon_mcp_usage_events GROUP BY tool_category;")
```

**Usage**:
```bash
python generate_comprehensive_test_data.py
```

---

### Generating Error Events

To test error handling, generate some failed requests:

```python
# Add to generate_test_data.py
import requests

# Generate errors by calling with invalid parameters
errors = [
    {"url": f"{MCP_URL}/rag_search_knowledge_base", "json": {}},  # Missing query
    {"url": f"{MCP_URL}/find_tasks", "params": {"invalid": "param"}},
]

for error in errors:
    try:
        requests.post(**error, timeout=5)
    except:
        pass  # Expected to fail
    time.sleep(1)

print("Generated error events")
```

---

## Bug Reporting Template

When issues are found, use this template for reporting:

### Bug Report Format

```markdown
## Bug Report

**Test Case ID**: [e.g., 2.1 - Time Range Filter]
**Severity**: [ ] Critical  [ ] High  [ ] Medium  [ ] Low
**Browser**: [e.g., Chrome 120]
**Device**: [e.g., Desktop / iPhone 14]
**Date Found**: [YYYY-MM-DD]

### Description
[Clear description of the issue]

### Steps to Reproduce
1.
2.
3.

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happened]

### Screenshots
[Attach screenshots if applicable]

### Console Errors
```
[Paste any console errors]
```

### Network Errors
[Any failed API calls]

### Additional Context
[Any other relevant information]

### Suggested Fix (optional)
[If you have ideas on how to fix it]
```

---

## Test Summary Report

### Overall Test Results

**Test Date**: __________
**Tester**: __________
**Environment**: [ ] Local  [ ] Staging  [ ] Production

### Test Coverage

| Test Category        | Total Tests | Passed | Failed | Blocked | Pass Rate |
|----------------------|-------------|--------|--------|---------|-----------|
| Happy Path           | 4           |        |        |         |           |
| Filter Scenarios     | 3           |        |        |         |           |
| Real-Time Updates    | 3           |        |        |         |           |
| Error Scenarios      | 3           |        |        |         |           |
| Mobile Testing       | 3           |        |        |         |           |
| Cross-Browser        | 4           |        |        |         |           |
| Accessibility        | 4           |        |        |         |           |
| Performance          | 4           |        |        |         |           |
| **TOTAL**            | **28**      |        |        |         |           |

### Critical Issues Found
1. [Issue description and severity]
2.
3.

### Recommendations
- [ ] Ready for production
- [ ] Minor fixes needed
- [ ] Major fixes required
- [ ] Retest required

### Notes
```
[Additional observations, comments, or suggestions]
```

---

## Appendix: Quick Reference

### Useful Commands

```bash
# Start services
docker compose up -d

# Check logs
docker compose logs -f archon-server

# Test API
curl http://localhost:8181/api/mcp/analytics/summary

# Clear test data (CAREFUL!)
# Run in Supabase SQL Editor
DELETE FROM archon_mcp_usage_events WHERE timestamp < NOW() - INTERVAL '1 hour';

# Refresh materialized views
curl -X POST http://localhost:8181/api/mcp/analytics/refresh-views
```

### DevTools Shortcuts

- **Chrome DevTools**: F12 or Cmd+Option+I (Mac) / Ctrl+Shift+I (Win)
- **Network Tab**: Cmd+Option+I → Network
- **Console**: Cmd+Option+J (Mac) / Ctrl+Shift+J (Win)
- **Device Emulation**: Cmd+Shift+M (Mac) / Ctrl+Shift+M (Win)
- **Performance**: Cmd+Option+I → Performance → Record

### SQL Queries for Verification

```sql
-- Count events by category
SELECT tool_category, COUNT(*)
FROM archon_mcp_usage_events
GROUP BY tool_category;

-- Check recent events
SELECT * FROM archon_mcp_usage_events
ORDER BY timestamp DESC
LIMIT 10;

-- Verify hourly aggregation
SELECT * FROM archon_mcp_usage_hourly
WHERE hour_bucket >= NOW() - INTERVAL '24 hours'
ORDER BY hour_bucket DESC;

-- Check for errors
SELECT tool_name, error_message, COUNT(*)
FROM archon_mcp_usage_events
WHERE error_message IS NOT NULL
GROUP BY tool_name, error_message;
```

---

**End of E2E Testing Documentation**

**Last Updated**: 2025-01-13
**Version**: 1.0
**Next Review**: After Phase 6 completion
