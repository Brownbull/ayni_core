# Frontend Development Standard

**Version:** 1.0.0
**Purpose:** Quality standard for React/TypeScript frontend development

---

## Overview

This standard defines **8 measurable metrics** for evaluating frontend code quality and user experience. Minimum passing score: **8.0/10**.

---

## Scoring Metrics

### Metric 1: Component Architecture (Weight: 12.5%)

| Score | Description |
|-------|-------------|
| **10** | Perfect component design - Reusable, composable, single responsibility |
| **8-9** | Strong components - Mostly reusable, minor coupling |
| **6-7** | Adequate components - Some reusability issues |
| **4-5** | Weak components - Monolithic, hard to reuse |
| **0-3** | Poor components - No clear structure |

**Checklist:**
- [ ] Components are single-purpose
- [ ] Props are well-defined with TypeScript
- [ ] No business logic in components
- [ ] Proper component hierarchy
- [ ] Reusable across features

---

### Metric 2: State Management (Weight: 12.5%)

| Score | Description |
|-------|-------------|
| **10** | Perfect state management - Clear data flow, no prop drilling |
| **8-9** | Strong state - Mostly clean, minor issues |
| **6-7** | Adequate state - Some prop drilling or unclear flow |
| **4-5** | Weak state - Confusing state management |
| **0-3** | Poor state - No clear state strategy |

**Checklist:**
- [ ] State lifted appropriately
- [ ] No unnecessary re-renders
- [ ] Context/store used properly
- [ ] Immutable updates
- [ ] State shape normalized

---

### Metric 3: TypeScript Usage (Weight: 12.5%)

| Score | Description |
|-------|-------------|
| **10** | Perfect TypeScript - Full type safety, no any |
| **8-9** | Strong typing - Mostly typed, rare any usage |
| **6-7** | Adequate typing - Basic types, some any |
| **4-5** | Weak typing - Many any, missing types |
| **0-3** | Poor typing - No TypeScript benefits |

**Checklist:**
- [ ] All props typed
- [ ] Return types specified
- [ ] No any types (use unknown)
- [ ] Interfaces over type aliases
- [ ] Generics where appropriate

---

### Metric 4: UI/UX Quality (Weight: 12.5%)

| Score | Description |
|-------|-------------|
| **10** | Perfect UX - Intuitive, responsive, accessible |
| **8-9** | Strong UX - Good flow, minor issues |
| **6-7** | Adequate UX - Usable but not polished |
| **4-5** | Weak UX - Confusing or frustrating |
| **0-3** | Poor UX - Unusable interface |

**Checklist:**
- [ ] Responsive design (mobile-first)
- [ ] Loading states
- [ ] Error states
- [ ] Empty states
- [ ] Keyboard navigation
- [ ] ARIA labels

---

### Metric 5: Performance (Weight: 12.5%)

| Score | Description |
|-------|-------------|
| **10** | Perfect performance - <1s load, 60fps, optimized |
| **8-9** | Strong performance - Fast, minor optimizations needed |
| **6-7** | Adequate performance - Acceptable speed |
| **4-5** | Weak performance - Noticeable lag |
| **0-3** | Poor performance - Unusable slowness |

**Checklist:**
- [ ] Code splitting implemented
- [ ] Images optimized
- [ ] Lazy loading used
- [ ] Memoization where needed
- [ ] Bundle size < 200KB
- [ ] No memory leaks

---

### Metric 6: Testing (Weight: 12.5%)

| Score | Description |
|-------|-------------|
| **10** | Perfect testing - Unit, integration, and visual tests |
| **8-9** | Strong testing - Good coverage, some gaps |
| **6-7** | Adequate testing - Basic tests present |
| **4-5** | Weak testing - Few tests |
| **0-3** | Poor testing - No tests |

**Checklist:**
- [ ] Component tests (RTL)
- [ ] Hook tests
- [ ] Integration tests
- [ ] Visual regression tests
- [ ] Accessibility tests
- [ ] > 80% coverage

---

### Metric 7: Accessibility (Weight: 12.5%)

| Score | Description |
|-------|-------------|
| **10** | Perfect accessibility - WCAG AAA compliant |
| **8-9** | Strong accessibility - WCAG AA compliant |
| **6-7** | Adequate accessibility - Basic a11y |
| **4-5** | Weak accessibility - Some violations |
| **0-3** | Poor accessibility - Inaccessible |

**Checklist:**
- [ ] Semantic HTML
- [ ] ARIA attributes
- [ ] Keyboard navigation
- [ ] Screen reader support
- [ ] Color contrast ratios
- [ ] Focus management

---

### Metric 8: Code Organization (Weight: 12.5%)

| Score | Description |
|-------|-------------|
| **10** | Perfect organization - Clear structure, easy to navigate |
| **8-9** | Strong organization - Mostly clear, minor issues |
| **6-7** | Adequate organization - Basic structure |
| **4-5** | Weak organization - Confusing structure |
| **0-3** | Poor organization - No clear structure |

**Checklist:**
- [ ] Feature-based folders
- [ ] Shared components isolated
- [ ] Utils/helpers organized
- [ ] Consistent file naming
- [ ] Index exports used
- [ ] No circular dependencies

---

## Common Patterns

### Component Structure
```typescript
interface ComponentProps {
  data: DataType;
  onAction: (id: string) => void;
}

export const Component: React.FC<ComponentProps> = ({ data, onAction }) => {
  // Hooks first
  // Handlers next
  // Effects last
  // Return JSX
};
```

### Custom Hook Pattern
```typescript
export const useCustomHook = (param: ParamType) => {
  const [state, setState] = useState<StateType>();

  useEffect(() => {
    // Effect logic
  }, [param]);

  return { state, actions };
};
```

---

## Evaluation Template

```markdown
# Frontend Evaluation

**Component/Feature:** [Name]
**Date:** [YYYY-MM-DD]

## Scores

| Metric | Score | Notes |
|--------|-------|-------|
| 1. Component Architecture | X/10 | |
| 2. State Management | X/10 | |
| 3. TypeScript Usage | X/10 | |
| 4. UI/UX Quality | X/10 | |
| 5. Performance | X/10 | |
| 6. Testing | X/10 | |
| 7. Accessibility | X/10 | |
| 8. Code Organization | X/10 | |

**Total: X.X/10** [PASS/REFINE/FAIL]
```