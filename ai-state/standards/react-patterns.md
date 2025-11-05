# React Development Standards

## Component Standards

### File Structure
```typescript
// ComponentName.tsx
import React from 'react'
import { ComponentProps } from './types'
import { useComponentLogic } from './hooks'
import styles from './ComponentName.module.css'

export const ComponentName: React.FC<ComponentProps> = (props) => {
  // 1. Hooks
  // 2. Handlers
  // 3. Effects
  // 4. Render
}
```

### Naming Conventions
- **Components:** PascalCase (UserProfile, DataTable)
- **Props:** ComponentNameProps interface
- **Hooks:** camelCase starting with 'use' (useAuth, useData)
- **Handlers:** handle + Event (handleClick, handleSubmit)
- **Files:** Match component name (Button.tsx, Button.test.tsx)

## State Management Rules

### When to Use What
- **useState:** Simple, local state (form inputs, toggles)
- **useReducer:** Complex state logic (3+ related values)
- **Context:** Cross-component state (theme, user)
- **Zustand:** Global application state (auth, data)

### State Updates
```typescript
// ✅ CORRECT - Immutable update
setState(prev => ({ ...prev, newField: value }))

// ❌ WRONG - Mutating state
state.field = value  // Never do this
```

## Performance Standards

### Required Optimizations
1. **Memoize expensive computations**
   ```typescript
   const expensiveValue = useMemo(() =>
     calculateExpensive(data), [data]
   )
   ```

2. **Virtualize long lists** (>100 items)
   ```typescript
   import { VirtualList } from '@tanstack/react-virtual'
   ```

3. **Lazy load routes**
   ```typescript
   const Dashboard = lazy(() => import('./Dashboard'))
   ```

## Testing Requirements

### Every Component Must Have
1. **Render test** - Component renders without crashing
2. **Props test** - Component handles all prop variations
3. **User interaction test** - Clicks, inputs work
4. **Edge cases test** - Null, undefined, empty arrays

### Test Structure
```typescript
describe('ComponentName', () => {
  it('renders with required props', () => {})
  it('handles user interaction', () => {})
  it('displays error state', () => {})
  it('handles edge cases', () => {})
})
```

## Accessibility Standards

### Required for All Components
- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation support
- Focus management
- Color contrast (WCAG AA minimum)

### Checklist
```typescript
// ✅ Accessible button
<button
  aria-label="Save changes"
  onClick={handleSave}
  disabled={loading}
>
  {loading ? 'Saving...' : 'Save'}
</button>

// ❌ Not accessible
<div onClick={handleSave}>Save</div>
```

## Error Handling

### Every Component Must
1. Have error boundaries for crashes
2. Show user-friendly error messages
3. Log errors for debugging
4. Provide recovery actions

### Error Boundary Template
```typescript
class ErrorBoundary extends Component {
  state = { hasError: false }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, info) {
    logError(error, info)
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback />
    }
    return this.props.children
  }
}
```

## Code Quality Metrics

### Required Thresholds
- TypeScript strict mode: ON
- ESLint errors: 0
- Test coverage: >80%
- Bundle size increase: <10KB per feature
- Lighthouse performance: >80

## Anti-Patterns to Avoid

### Never Do These
1. ❌ Direct DOM manipulation
2. ❌ Inline function definitions in render
3. ❌ Array index as key in dynamic lists
4. ❌ Async operations without cleanup
5. ❌ Business logic in components
6. ❌ Global variables
7. ❌ Console.log in production

## Review Checklist

Before marking task complete:
- [ ] TypeScript types complete
- [ ] Tests written and passing
- [ ] No ESLint warnings
- [ ] Accessibility checked
- [ ] Error handling implemented
- [ ] Performance optimized
- [ ] Documentation updated