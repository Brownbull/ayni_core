# /review-architecture Command

Self-review architecture and analyze end-to-end data flow before deployment.

## Usage
```bash
/review-architecture [task-id or "current"]
```

## What It Does
1. **Self-Review Phase**
   - AI reviews its own architecture for issues
   - Identifies duplication, missing parts, design flaws
   - Checks against quality standards (8.0/10 minimum)
   - Generates review report

2. **Data Flow Analysis**
   - Explains end-to-end how data flows through the system
   - Identifies missing dependencies
   - Catches naming mismatches
   - Validates integration points

3. **Recommendation Phase**
   - Provides actionable fixes
   - Suggests refactoring if needed
   - Creates fix plan

## When to Use

### After Implementation (Before Marking Complete)
```bash
# Just finished task-007-file-upload-api
/review-architecture task-007-file-upload-api
```

### For Current Work in Progress
```bash
# Working on something, want a review
/review-architecture current
```

### For Entire Epic
```bash
# Review all tasks in an epic
/review-architecture epic-ayni-mvp-foundation
```

## Review Checklist

### Architecture Issues
- [ ] **Duplication**: Same logic in multiple places?
- [ ] **Missing Parts**: Incomplete error handling? Missing tests?
- [ ] **Design Flaws**: Tight coupling? Poor separation of concerns?
- [ ] **Complexity**: Functions > 50 lines? Files > 800 lines?
- [ ] **Dependencies**: Circular dependencies? Missing imports?

### Data Flow Analysis
- [ ] **Entry Points**: Where does data enter the system?
- [ ] **Transformations**: How is data processed/validated?
- [ ] **Storage**: Where/how is data persisted?
- [ ] **Retrieval**: How is data fetched?
- [ ] **Exit Points**: How does data leave the system?
- [ ] **Error Paths**: What happens when things fail?

### Integration Points
- [ ] **Frontend ↔ Backend**: API contracts aligned?
- [ ] **Backend ↔ Database**: Queries optimized?
- [ ] **Backend ↔ Celery**: Task signatures correct?
- [ ] **Celery ↔ WebSocket**: Real-time updates working?

## Output Format

```markdown
# Architecture Review: task-XXX

## Review Date
[timestamp]

## Overall Assessment
[PASS / NEEDS REFINEMENT / FAIL]

## Quality Score
X.X/10 (threshold: 8.0/10)

---

## 1. SELF-REVIEW FINDINGS

### Design Flaws Found
- Issue 1: [description]
  - Impact: [high/medium/low]
  - Location: [file:line]
  - Recommendation: [fix]

- Issue 2: [description]
  ...

### Duplication Detected
- Duplicate 1: [description]
  - Files: [file1, file2]
  - Lines: [approx count]
  - Recommendation: [extract to shared function/class]

### Missing Parts
- Missing 1: [what's missing]
  - Severity: [critical/high/medium/low]
  - Recommendation: [add X]

---

## 2. DATA FLOW ANALYSIS

### Happy Path Flow
```
Entry → Validation → Processing → Storage → Response
  ↓         ↓            ↓          ↓          ↓
[file]   [file]      [file]     [file]    [file]
```

### Detailed Flow Explanation
1. **Entry**: Data enters via [endpoint/upload/etc]
2. **Validation**: [what's validated, where]
3. **Processing**: [transformations, business logic]
4. **Storage**: [database/cache/file]
5. **Response**: [what's returned to user]

### Error Flow
```
Error Occurs → Handler → Log → Notify → Response
```

### Missing Dependencies Detected
- [ ] Missing import: [module] in [file]
- [ ] Undefined function: [function] called in [file]
- [ ] Naming mismatch: [expects X, got Y]

---

## 3. INTEGRATION POINT VALIDATION

### Frontend ↔ Backend
- ✅ Endpoints match API docs
- ⚠️ Request format mismatch in [endpoint]
- ✅ Response types aligned

### Backend ↔ Database
- ✅ Models match schema
- ⚠️ Missing index on [field]
- ✅ Queries optimized

### Backend ↔ Celery
- ✅ Task signatures correct
- ⚠️ Missing retry logic in [task]
- ✅ WebSocket notifications working

---

## 4. FILE SIZE ANALYSIS

### Files Exceeding 800 Lines
- [file1.py]: 1,234 lines → NEEDS REFACTORING
- [file2.tsx]: 956 lines → CONSIDER REFACTORING

### Recommendation
Run `/refactor-module [file]` to break up large files.

---

## 5. COMPLEXITY ANALYSIS

### Functions > 50 Lines
- [function1] in [file]: 87 lines
- [function2] in [file]: 62 lines

### Cyclomatic Complexity > 10
- [function3]: complexity 15

### Recommendation
Refactor complex functions into smaller, testable units.

---

## 6. ACTIONABLE FIXES

### Critical (Fix Before Deploy)
1. [Fix description]
   - File: [file]
   - Action: [specific fix]

### High Priority (Fix Soon)
1. [Fix description]
   - File: [file]
   - Action: [specific fix]

### Medium Priority (Next Sprint)
1. [Fix description]
   - File: [file]
   - Action: [specific fix]

---

## 7. RECOMMENDATIONS

### If Review PASSED
- ✅ Architecture is sound
- ✅ Data flow is clear
- ✅ Integration points validated
- ✅ Ready for deployment

### If Review NEEDS REFINEMENT
- ⚠️ Address [N] critical issues
- ⚠️ Fix [N] high priority items
- Then re-run: `/review-architecture [task-id]`

### If Review FAILED
- ❌ Major architectural flaws detected
- ❌ Recommend redesign or significant refactoring
- Consider starting new chat with review feedback:
  - Copy this review
  - New chat: "Build a fixed version based on this review"

---

## Next Steps
[Based on review results]
```

## Integration with Orchestration

```python
# In orchestrate.py

class Orchestrator:
    def review_architecture(self, target="current"):
        """
        Self-review and data flow analysis.
        
        Args:
            target: "current", task-id, or epic-id
        """
        if target == "current":
            # Review current work in progress
            files = self.get_recently_modified_files()
        elif target.startswith("task-"):
            # Review specific task
            task = self.load_task(target)
            files = task.files_created + task.files_modified
        elif target.startswith("epic-"):
            # Review all tasks in epic
            epic = self.load_epic(target)
            files = self.get_epic_files(epic)
        
        # Run review
        review_report = self.run_self_review(files)
        
        # Analyze data flow
        flow_analysis = self.analyze_data_flow(files)
        
        # Generate report
        report_path = f"ai-state/reviews/{target}-review.md"
        self.generate_review_report(review_report, flow_analysis, report_path)
        
        return report_path
```

## Example Workflows

### Workflow 1: After Implementing Task
```bash
# Completed task-007-file-upload-api
/review-architecture task-007-file-upload-api

# Output:
[REVIEW] Architecture Review: task-007-file-upload-api
[CHECK] Self-reviewing implementation...
[CHECK] Analyzing data flow...
[CHECK] Validating integration points...
[CHECK] Checking file sizes...

[RESULT] Overall: NEEDS REFINEMENT (Score: 7.8/10)
[ISSUE] Critical: Missing error handling in upload validation
[ISSUE] High: File size check inconsistent (views.py:L45 vs serializers.py:L67)
[RECOMMEND] Fix 2 critical issues, then re-run review

Report saved: ai-state/reviews/task-007-review.md
```

### Workflow 2: Review Finds Issues, Copy to New Chat
```bash
# Review found major issues
/review-architecture task-008-celery-setup

# Output shows design flaws
# Copy the review report
# Open new Claude chat
# Paste: "Build a fixed version based on this review: [paste report]"
# AI generates cleaner implementation
```

### Workflow 3: Continuous Review During Development
```bash
# Working on complex feature
# Save work frequently, review often

# Review current state
/review-architecture current

# Fix issues found
# Review again
/review-architecture current

# Iterate until PASS
```

## Best Practices

### When to Review
- ✅ **After** implementing each task (before marking complete)
- ✅ **Before** merging to main branch
- ✅ **During** complex feature development (review frequently)
- ✅ **After** major refactoring

### How to Use Review Feedback
1. **Read the full review** - Don't skip sections
2. **Fix critical issues first** - Block deployment until resolved
3. **Copy to new chat if major** - Let AI rebuild cleanly
4. **Re-review after fixes** - Ensure issues are resolved
5. **Document learnings** - Add to patterns.md if useful

### Red Flags in Review
- 🚩 Multiple design flaws detected
- 🚩 Data flow has missing steps
- 🚩 Files > 1000 lines
- 🚩 Cyclomatic complexity > 15
- 🚩 No error handling paths
- 🚩 Integration points undefined

If you see 3+ red flags: **Consider starting fresh with review feedback in new chat.**

## Integration with Quality Gates

This command **enforces** the 8.0/10 quality threshold:

```yaml
review_gates:
  - self_review_score >= 8.0
  - no_critical_issues: true
  - data_flow_complete: true
  - integration_points_validated: true
  - file_size_under_800_lines: true (or refactor scheduled)
  - no_circular_dependencies: true
```

## Anti-Patterns

❌ **Don't** skip review to "save time" - it catches bugs early
❌ **Don't** ignore critical issues - they compound
❌ **Don't** review only at the end - review during development
❌ **Don't** fix issues without understanding root cause
❌ **Don't** skip data flow analysis - it catches logic errors

---

**Remember:** 10 minutes of review saves hours of debugging. Use this command liberally!
