# /regression-test Command

Run regression tests on completed tasks and generate a detailed report with results and suggested fixes.

## Usage
```
/regression-test [task-id]
/regression-test all
```

## What it does
1. Scans completed tasks in `ai-state/active/tests/`
2. Executes all test cases using test-orchestrator skill
3. Validates against quality standards (8.0/10 minimum)
4. Identifies regressions and failures
5. Suggests fixes for failing tests
6. Generates comprehensive report
7. Saves report to `ai-state/regressions/` folder

## Parameters
- **task-id** (optional): Specific task to test (e.g., `task-011-update-tracking`)
- **all**: Run regression tests on all completed tasks

## Integration

The command will invoke the `test-orchestrator` skill to:
- Load task test specifications from `ai-state/active/tests/`
- Execute all 8 test types (valid, error, invalid, edge, functional, visual, performance, security)
- Compare results against expected outcomes
- Calculate quality scores and coverage metrics
- Identify any regressions from previous runs
- Generate actionable fix suggestions

## Report Structure

Each regression report includes:
- **Summary**: Pass/fail counts, regression detection
- **Task Details**: For each tested task
  - Test execution results (8 test types)
  - Quality score comparison (current vs. expected)
  - Coverage metrics
  - Data quality scores (if applicable)
  - Performance benchmarks
- **Regressions Detected**: Tasks that previously passed but now fail
- **Suggested Fixes**: Specific recommendations for each failure
- **Action Items**: Prioritized list of fixes needed

## Example Flow

### Test Single Task
```
User: /regression-test task-011-update-tracking
System: Loading test specification for task-011-update-tracking...
System: Invoking test-orchestrator skill...
System: Running 25 test cases across 8 test types...
System: ✅ All tests passed (25/25)
System: Quality Score: 9.5/10 (meets threshold)
System: Coverage: 93% (exceeds 80% minimum)
System: Report saved to: ai-state/regressions/regression-task-011-2025-11-05T16-30-00.md
```

### Test All Tasks
```
User: /regression-test all
System: Scanning ai-state/active/tests/ for completed tasks...
System: Found 12 completed tasks
System: Invoking test-orchestrator skill...
System: Testing task-001-project-structure... ✅ PASS
System: Testing task-002-database-schema... ✅ PASS
System: Testing task-003-authentication-system... ❌ FAIL (3/25 tests failing)
System: Testing task-004-company-management... ✅ PASS
...
System:
System: Summary:
System: - Total Tasks: 12
System: - Passed: 11
System: - Failed: 1
System: - Regressions: 1 (task-003 previously passed)
System:
System: Report saved to: ai-state/regressions/regression-all-2025-11-05T16-30-00.md
System:
System: ⚠️ Action required for task-003-authentication-system
```

## Report Location

Reports are saved to:
```
ai-state/regressions/regression-[task-id]-[timestamp].md
ai-state/regressions/regression-all-[timestamp].md
```

## Quality Gates

The regression test enforces:
- ✅ All 8 test types must be present
- ✅ Quality score >= 8.0/10
- ✅ Test coverage >= 80%
- ✅ Data quality >= 95/100 (for data context tasks)
- ✅ No regressions from previous runs
- ✅ Performance benchmarks met

## When to Use

Run regression tests:
- ✅ Before merging feature branches
- ✅ After refactoring existing code
- ✅ Before production deployments
- ✅ Weekly as part of CI/CD pipeline
- ✅ When investigating suspected regressions
- ✅ After dependency updates

## Next Steps

After regression testing:
1. Review generated report in `ai-state/regressions/`
2. For failed tests, review suggested fixes
3. Create tasks to address regressions
4. Re-run regression test after fixes applied
5. Update task documentation with lessons learned
