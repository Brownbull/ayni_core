# Testing Requirements Standard

## Overview
Every task must include comprehensive testing before marking complete. Tests are not optional.

## Test Categories

### 1. Valid Cases (Happy Path)
**Purpose:** Verify normal operation works correctly
**Required Coverage:**
- Standard user flow
- Expected inputs
- Successful operations
- Correct outputs

### 2. Error Cases
**Purpose:** Verify error handling works
**Required Coverage:**
- Network failures
- Server errors (500, 503)
- Timeout scenarios
- Permission denied (401, 403)

### 3. Invalid Cases
**Purpose:** Verify validation works
**Required Coverage:**
- Invalid input formats
- Missing required fields
- Out of range values
- Wrong data types

### 4. Edge Cases
**Purpose:** Verify boundary conditions
**Required Coverage:**
- Empty arrays/strings
- Null/undefined values
- Maximum/minimum values
- Concurrent operations

### 5. Functional Tests (Backend)
**Purpose:** Verify business logic works
**Tools:** pytest (Python), Jest (Node.js)
**Required Coverage:**
- API endpoints
- Data transformations
- Database operations
- Business rules

### 6. Visual Tests (Frontend)
**Purpose:** Verify UI renders correctly
**Tools:** Playwright, Chrome DevTools
**Required Coverage:**
- Component rendering
- Responsive layouts
- Loading states
- Error displays

## Test Implementation by Context

### Frontend Testing Stack
```typescript
// Unit Tests - Jest + React Testing Library
test('component renders', () => {
  render(<Component />)
  expect(screen.getByRole('button')).toBeInTheDocument()
})

// Visual Tests - Playwright
test('visual regression', async ({ page }) => {
  await page.goto('/dashboard')
  await expect(page).toHaveScreenshot()
})
```

### Backend Testing Stack
```python
# Unit Tests - pytest
def test_api_endpoint():
    response = client.get('/api/data')
    assert response.status_code == 200
    assert 'data' in response.json()

# Integration Tests
def test_database_operation():
    result = service.process_data(test_data)
    assert result.count() == expected_count
```

## Coverage Requirements

### Minimum Coverage Thresholds
- **Unit Tests:** 80% code coverage
- **Integration Tests:** All API endpoints
- **Visual Tests:** All user-facing components
- **E2E Tests:** Critical user paths

### Coverage Report Format
```yaml
test_results:
  unit:
    coverage: 85%
    passed: 45/45
  integration:
    coverage: 92%
    passed: 12/12
  visual:
    passed: 8/8
    screenshots: updated
  e2e:
    passed: 5/5
    duration: 45s
```

## Test Execution Flow

### 1. Pre-Task Testing
```yaml
before_implementation:
  - Define test cases from requirements
  - Write test skeletons
  - Mark as pending
```

### 2. During Implementation
```yaml
during_implementation:
  - Run tests continuously
  - Fix failures immediately
  - Add edge cases as discovered
```

### 3. Post-Implementation
```yaml
after_implementation:
  - Run full test suite
  - Generate coverage report
  - Document any limitations
```

## Test Retry Logic

### When Tests Fail
1. **First Failure:** Analyze error, fix implementation
2. **Second Failure:** Check test validity, fix test or code
3. **Third Failure:** Escalate to orchestrator, may need design change

### Flaky Test Mitigation
```typescript
// Add stability helpers
await page.waitForLoadState('networkidle')
await expect(element).toBeVisible({ timeout: 10000 })
await page.waitForSelector('.data-loaded')
```

## Test Documentation

### Each Test Must Document
```typescript
describe('Feature: User Authentication', () => {
  test('should login with valid credentials', () => {
    // Given: Valid user exists
    // When: User submits login form
    // Then: User is redirected to dashboard
  })
})
```

## Performance Testing

### Required Metrics
- Response time < 200ms (API)
- First paint < 1.5s (UI)
- Time to interactive < 3s
- Bundle size < 200KB (per chunk)

## Security Testing

### Required Checks
- SQL injection prevention
- XSS protection
- CSRF token validation
- Authentication required
- Authorization enforced

## Anti-Patterns to Avoid

### Never Do These
1. ❌ Skip tests to "save time"
2. ❌ Comment out failing tests
3. ❌ Test implementation details
4. ❌ Use random/time-based data
5. ❌ Ignore flaky tests
6. ❌ Test external services directly

## Test Review Checklist

Before marking complete:
- [ ] All 6 test categories covered
- [ ] Coverage meets thresholds
- [ ] No skipped tests
- [ ] Tests run in CI/CD
- [ ] Performance benchmarks met
- [ ] Security tests pass
- [ ] Documentation complete