# MCP Analytics UI Enhancement - Implementation Checklist

**Status**: Ready to Start
**Estimated Time**: 12-18 hours (MVP in 4-6 hours)
**Priority**: Phase 1 (Knowledge Base Tracking) is High Priority

---

## Phase 1: Knowledge Base Tracking (MVP) - 4-6 hours

### Backend Work (2-3 hours)

- [ ] **Create Knowledge Base Analytics Endpoint**
  - [ ] Add `GET /api/mcp/analytics/knowledge-bases` route
  - [ ] Write SQL query to join `archon_mcp_usage_events` with `sources` table
  - [ ] Return source name, query count, unique queries, avg response time
  - [ ] Add ETag support for caching
  - [ ] Handle empty state (no sources queried)
  - **File**: `python/src/server/api_routes/mcp_analytics_api.py`

- [ ] **Write Backend Tests**
  - [ ] Test knowledge base endpoint with sample data
  - [ ] Test empty state response
  - [ ] Test filtering by time range
  - **File**: `python/tests/server/api_routes/test_mcp_analytics_api.py`

### Frontend Work (2-3 hours)

- [ ] **Create TypeScript Types**
  - [ ] Define `KnowledgeBaseAnalytics` interface
  - [ ] Define `KnowledgeBaseUsageItem` interface
  - **File**: `archon-ui-main/src/features/mcp/types/analytics.ts` (new)

- [ ] **Update API Service**
  - [ ] Add `getKnowledgeBaseAnalytics()` method
  - [ ] Export typed response interface
  - **File**: `archon-ui-main/src/features/mcp/services/mcpAnalyticsService.ts`

- [ ] **Create React Query Hook**
  - [ ] Create `useMcpKnowledgeBaseAnalytics()` hook
  - [ ] Use STALE_TIMES.normal (30 seconds)
  - [ ] Add to knowledge base key factory
  - **File**: `archon-ui-main/src/features/mcp/hooks/useMcpKnowledgeBaseAnalytics.ts` (new)

- [ ] **Build Knowledge Base Usage Card Component**
  - [ ] Create `KnowledgeBaseUsageCard.tsx`
  - [ ] Horizontal bar visualization for top 5 sources
  - [ ] Show query count and percentage
  - [ ] Empty state: "No knowledge bases queried yet"
  - [ ] Loading skeleton
  - [ ] Error handling
  - **File**: `archon-ui-main/src/features/mcp/components/KnowledgeBaseUsageCard.tsx` (new)

- [ ] **Integrate into Main Dashboard**
  - [ ] Import `KnowledgeBaseUsageCard`
  - [ ] Add after summary cards, before filters
  - [ ] Test responsive layout
  - **File**: `archon-ui-main/src/features/mcp/components/MCPUsageAnalytics.tsx`

- [ ] **Write Component Tests**
  - [ ] Test rendering with data
  - [ ] Test empty state
  - [ ] Test loading state
  - [ ] Test error state
  - **File**: `archon-ui-main/src/features/mcp/components/tests/KnowledgeBaseUsageCard.test.tsx` (new)

### Documentation & Testing

- [ ] **Test with Sample Data**
  - [ ] Insert sample MCP events into database
  - [ ] Verify API returns correct data
  - [ ] Verify UI displays correctly
  - [ ] Test on mobile/tablet/desktop

- [ ] **Update Documentation**
  - [ ] Update CLAUDE.md with new analytics features
  - [ ] Add screenshots to PRP document
  - [ ] Document new API endpoints

---

## Phase 2: Popular Queries Display - 3-4 hours

### Backend Work (1-2 hours)

- [ ] **Create Popular Queries Endpoint**
  - [ ] Add `GET /api/mcp/analytics/popular-queries` route
  - [ ] Aggregate by `query_text` column
  - [ ] Return top 10 queries with counts and avg response time
  - [ ] Add optional `source_id` filter
  - **File**: `python/src/server/api_routes/mcp_analytics_api.py`

- [ ] **Write Backend Tests**
  - [ ] Test popular queries endpoint
  - [ ] Test filtering by source
  - [ ] Test empty state
  - **File**: `python/tests/server/api_routes/test_mcp_analytics_api.py`

### Frontend Work (2 hours)

- [ ] **Update Types & Services**
  - [ ] Add `PopularQuery` interface
  - [ ] Add `getPopularQueries()` service method
  - [ ] Create `useMcpPopularQueries()` hook
  - **Files**: `types/analytics.ts`, `services/mcpAnalyticsService.ts`, `hooks/useMcpAnalytics.ts`

- [ ] **Build Popular Queries Card**
  - [ ] Create `PopularQueriesCard.tsx`
  - [ ] Display top 5 queries with counts
  - [ ] Truncate long queries with tooltip
  - [ ] Click query to filter main chart (future enhancement)
  - **File**: `archon-ui-main/src/features/mcp/components/PopularQueriesCard.tsx` (new)

- [ ] **Integrate into Dashboard**
  - [ ] Add below knowledge base card
  - [ ] Test layout

- [ ] **Write Tests**
  - [ ] Component tests for popular queries card
  - **File**: Component test file

---

## Phase 3: Performance Metrics - 3-4 hours

### Backend Work (1-2 hours)

- [ ] **Enhance Summary Endpoint**
  - [ ] Add `performance` object to summary response
  - [ ] Calculate avg, P95, P99 response times
  - [ ] Identify slowest tool
  - [ ] Add performance trends (vs previous period)
  - **File**: `python/src/server/api_routes/mcp_analytics_api.py`

- [ ] **Write Backend Tests**
  - [ ] Test performance calculations
  - [ ] Test percentile accuracy
  - **File**: Backend test file

### Frontend Work (2 hours)

- [ ] **Create Performance Metrics Card**
  - [ ] Create `PerformanceMetricsCard.tsx`
  - [ ] Display avg response time with color coding:
    - Green: < 300ms
    - Yellow: 300-1000ms
    - Red: > 1000ms
  - [ ] Show P95 percentile
  - [ ] Display slowest tool
  - **File**: `archon-ui-main/src/features/mcp/components/PerformanceMetricsCard.tsx` (new)

- [ ] **Update Summary Cards Layout**
  - [ ] Change grid from 3 to 4 columns
  - [ ] Add performance card as 4th card
  - [ ] Ensure responsive (stack on mobile)
  - **File**: `MCPUsageAnalytics.tsx`

- [ ] **Write Tests**
  - [ ] Test color coding logic
  - [ ] Test percentile display
  - **File**: Component test file

---

## Phase 4: Client Distribution (Optional) - 2-3 hours

### Backend Work (1 hour)

- [ ] **Add Client Distribution to Summary**
  - [ ] Add `client_distribution` to summary endpoint
  - [ ] Group by `client_type` column
  - [ ] Return counts and percentages
  - **File**: `python/src/server/api_routes/mcp_analytics_api.py`

### Frontend Work (1-2 hours)

- [ ] **Build Client Distribution Card**
  - [ ] Create `ClientDistributionCard.tsx`
  - [ ] Pie chart using Recharts
  - [ ] Legend with percentages
  - [ ] Show Claude Code, Cursor, Windsurf, Unknown
  - **File**: Component file (new)

- [ ] **Integrate into Dashboard**
  - [ ] Add below bar chart
  - [ ] Test responsive layout

- [ ] **Write Tests**
  - [ ] Test pie chart rendering
  - [ ] Test legend labels
  - **File**: Test file

---

## Cross-Cutting Tasks

### Responsive Design
- [ ] Test all new components on mobile (320px)
- [ ] Test on tablet (768px)
- [ ] Test on desktop (1024px+)
- [ ] Ensure charts adapt to screen size
- [ ] Test portrait and landscape orientations

### Performance
- [ ] Verify API response times < 500ms
- [ ] Check TanStack Query caching works
- [ ] Test with 1000+ events in database
- [ ] Profile component render times
- [ ] Optimize re-renders with useMemo

### Accessibility
- [ ] Add ARIA labels to all interactive elements
- [ ] Ensure keyboard navigation works
- [ ] Test with screen reader
- [ ] Check color contrast ratios
- [ ] Add alt text to visualizations

### Error Handling
- [ ] Handle network errors gracefully
- [ ] Show user-friendly error messages
- [ ] Add retry buttons for failed requests
- [ ] Log errors to console for debugging
- [ ] Test offline behavior

---

## Testing Strategy

### Manual Testing Checklist
- [ ] Insert sample data (100+ events across multiple sources)
- [ ] Verify knowledge base card shows correct data
- [ ] Verify popular queries shows top queries
- [ ] Verify performance metrics calculate correctly
- [ ] Test all time range filters (24h, 48h, 7d)
- [ ] Test category filters
- [ ] Test empty states (no data)
- [ ] Test loading states
- [ ] Test error states
- [ ] Test refresh button
- [ ] Test responsive layout on all screen sizes

### Automated Testing
- [ ] Backend API tests (pytest)
- [ ] Frontend component tests (Vitest + React Testing Library)
- [ ] Integration tests (API + UI)
- [ ] E2E tests (optional, Playwright)

---

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] No console errors/warnings
- [ ] Performance metrics acceptable

### Deployment
- [ ] Merge to feature branch
- [ ] Test in staging environment
- [ ] Run database migrations (if any)
- [ ] Deploy to production
- [ ] Monitor for errors

### Post-Deployment
- [ ] Verify analytics dashboard loads
- [ ] Check API response times
- [ ] Monitor error rates
- [ ] Gather user feedback
- [ ] Plan next iteration

---

## Quick Start Guide

### To Implement Phase 1 (MVP):

1. **Backend** (2-3 hours):
   ```bash
   # Edit API file
   cd python/src/server/api_routes
   # Add knowledge-bases endpoint to mcp_analytics_api.py

   # Write tests
   cd ../../tests/server/api_routes
   # Add tests to test_mcp_analytics_api.py

   # Test locally
   make test-be
   ```

2. **Frontend** (2-3 hours):
   ```bash
   cd archon-ui-main/src/features/mcp

   # Create types
   # Create in types/analytics.ts

   # Update service
   # Edit services/mcpAnalyticsService.ts

   # Create hook
   # Create in hooks/useMcpKnowledgeBaseAnalytics.ts

   # Create component
   # Create in components/KnowledgeBaseUsageCard.tsx

   # Integrate
   # Edit components/MCPUsageAnalytics.tsx

   # Test
   npm test
   ```

3. **Test End-to-End**:
   ```bash
   # Insert sample data
   python scripts/insert_sample_mcp_data.py

   # Start services
   make dev

   # Open browser
   # Navigate to Settings > MCP Usage Analytics
   # Verify knowledge base card displays
   ```

---

## Success Criteria

### Phase 1 Complete When:
- ✅ API endpoint returns knowledge base analytics
- ✅ UI displays top 5 queried knowledge bases
- ✅ Empty state shows when no data
- ✅ Loading and error states work
- ✅ All tests passing
- ✅ Responsive on mobile/desktop

### Phase 2 Complete When:
- ✅ Popular queries displayed in UI
- ✅ Query counts accurate
- ✅ Queries truncated properly
- ✅ All tests passing

### Phase 3 Complete When:
- ✅ Performance metrics card showing
- ✅ Color coding based on thresholds
- ✅ P95 calculation accurate
- ✅ All tests passing

---

## Notes

- Start with Phase 1 (highest priority)
- Phase 2 and 3 can be done in any order
- Phase 4 is optional (nice-to-have)
- Each phase is independently deployable
- Focus on empty states and error handling
- Keep components small and testable

---

**Last Updated**: 2025-10-13
**Next Review**: After Phase 1 completion
