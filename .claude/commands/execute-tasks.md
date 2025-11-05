# Execute Tasks - Orchestrated Task Execution

This command reads pending tasks from the task registry and executes them via the appropriate orchestrator skills.

---

## Usage

```bash
/execute-tasks [--task-id <id>] [--context <frontend|backend|data|test|devops>]
```

**Options:**
- No arguments: Process all pending tasks
- `--task-id <id>`: Execute specific task
- `--context <name>`: Execute all tasks for a specific context

---

## How It Works

### Step 1: Read Task Registry

Load `ai-state/active/tasks.yaml` and identify tasks to execute:

```yaml
tasks:
  task-001-oauth-ui:
    status: "pending"
    context: "frontend"
    who: "frontend-orchestrator"
    what: "Implement OAuth2 login UI"
    # ... rest of task definition
```

### Step 2: Route to Orchestrator

Based on the task's `context` or `who` field, invoke the appropriate orchestrator skill:

**Routing Map:**
- `context: "frontend"` → Invoke `frontend-orchestrator` skill
- `context: "backend"` → Invoke `backend-orchestrator` skill
- `context: "data"` → Invoke `data-orchestrator` skill
- `context: "test"` → Invoke `test-orchestrator` skill
- `context: "devops"` → Invoke `devops-orchestrator` skill

### Step 3: Invoke Orchestrator Skill

Execute the skill with task context:

```
You are the Frontend Orchestrator executing task-001-oauth-ui.

Task Details:
- What: Implement OAuth2 login UI
- Where: src/components/Auth/
- How: Follow standards/frontend-standard.md
- Goal: Users can login via Google/GitHub
- Standards: 8.0/10 minimum quality score

Test Requirements (all must pass):
- valid: User clicks Google, redirects, logs in successfully
- error: Handle OAuth errors gracefully with user feedback
- invalid: Prevent CSRF attacks, validate state parameter
- edge: Handle popup blockers, network failures
- functional: Store auth tokens correctly, refresh logic
- visual: Button renders properly, loading states
- performance: Redirect completes in < 500ms
- security: No token exposure, secure storage

Instructions:
1. Read the standard: ai-state/standards/frontend-standard.md
2. Implement the feature following the standard
3. Write all 8 test types (TDD approach)
4. Self-evaluate against 8 quality metrics (must be >= 8.0/10)
5. If score < 8.0, refine and re-evaluate
6. Update task status to "completed"
7. **Create test documentation in ai-state/active/tests/{task-id}.md**
8. Log completion event to ai-state/operations.log

When done, report:
- Implementation summary
- Quality score (8 metrics)
- Test results (8 types)
- Files created/modified
- Test documentation path
- Next recommended task (if any)
```

### Step 4: Monitor Execution

The orchestrator skill:
1. Reads the assigned standard
2. Implements the feature
3. Writes all required tests
4. Self-evaluates quality (8 metrics)
5. Refines until >= 8.0/10
6. Updates task status in tasks.yaml
7. Creates test documentation in ai-state/active/tests/
8. Logs event to operations.log

### Step 5: Update Task Status

Update `ai-state/active/tasks.yaml`:

```yaml
tasks:
  task-001-oauth-ui:
    status: "completed"  # Changed from "pending"
    context: "frontend"
    completed_at: "2025-11-04T18:00:00Z"
    quality_score: 8.5
    tests_passed: 8
    files_modified:
      - "src/components/Auth/LoginButton.tsx"
      - "src/components/Auth/LoginButton.test.tsx"
```

### Step 6: Create Test Documentation

**MANDATORY:** Create test documentation in `ai-state/active/tests/{task-id}.md`:

```markdown
# Tests for task-001-oauth-ui

**Task:** Implement OAuth2 login UI
**Context:** frontend
**Created:** 2025-11-04T18:00:00Z
**Quality Score:** 8.5/10
**Test Coverage:** 90%+

---

## Test Files

1. `src/components/Auth/LoginButton.test.tsx` (15 test cases)

---

## How to Run

### Run all tests for this task
```bash
npm test LoginButton.test.tsx
```

### Run with coverage
```bash
npm test LoginButton.test.tsx -- --coverage
```

---

## Expected Results

- **Total Test Cases:** 15
- **Test Types Covered:** 8/8 (valid, error, invalid, edge, functional, visual, performance, security)
- **Expected Coverage:** 90%+
- **Expected Status:** ✅ All tests passing

---

## Obtained Results (Last Run)

- **Date:** 2025-11-04T18:00:00Z
- **Status:** ✅ PASS
- **Tests Passed:** 15/15
- **Coverage:** 92%
- **Duration:** 1.2s

---

**Regression Status:** ACTIVE
```

**Purpose:**
- Enable batch regression testing
- Track expected vs obtained results
- Minimal format for automated processing

### Step 7: Log Event

Append to `ai-state/operations.log`:

```json
{
  "timestamp": "2025-11-04T18:00:00Z",
  "orchestrator": "frontend-orchestrator",
  "event": "task.completed",
  "task_id": "task-001-oauth-ui",
  "quality_score": 8.5,
  "tests_passed": 8,
  "test_doc_created": "ai-state/active/tests/task-001-oauth-ui.md",
  "duration_minutes": 15
}
```

---

## Example Workflows

### Execute All Pending Tasks

```bash
/execute-tasks

[EXECUTE] Found 5 pending tasks
[TASK 1/5] task-001-oauth-ui (frontend)
  → Invoking frontend-orchestrator...
  → Implementing OAuth2 login UI...
  → Writing tests (8 types)...
  → Quality score: 8.5/10 ✓
  → Status: completed

[TASK 2/5] task-002-oauth-api (backend)
  → Invoking backend-orchestrator...
  → Implementing OAuth2 API endpoints...
  → Writing tests (8 types)...
  → Quality score: 8.3/10 ✓
  → Status: completed

[SUMMARY]
Completed: 5/5 tasks
Failed: 0
Average quality: 8.4/10
Total duration: 1.2 hours

Check logs: tail -f ai-state/operations.log
```

### Execute Specific Task

```bash
/execute-tasks --task-id task-003-oauth-db

[EXECUTE] Task: task-003-oauth-db
Context: data
Orchestrator: data-orchestrator

→ Invoking data-orchestrator...
→ Creating OAuth tokens table...
→ Adding migrations...
→ Writing data quality tests...
→ Quality score: 9.0/10 ✓
→ Status: completed

Next task: task-004-oauth-tests (recommended)
```

### Execute by Context

```bash
/execute-tasks --context frontend

[EXECUTE] Found 3 frontend tasks
[TASK 1/3] task-001-oauth-ui
  → Status: completed ✓

[TASK 2/3] task-005-dashboard-ui
  → Invoking frontend-orchestrator...
  → Implementing dashboard components...
  → Status: completed ✓

[TASK 3/3] task-008-error-handling-ui
  → Invoking frontend-orchestrator...
  → Adding error boundaries...
  → Status: completed ✓

All frontend tasks complete!
```

---

## Integration with Orchestrators

Each orchestrator skill receives:

**Input Context:**
```yaml
task:
  id: "task-001-oauth-ui"
  epic: "epic-oauth2"
  context: "frontend"
  when: "Design approved"
  who: "frontend-orchestrator"
  where: "src/components/Auth/"
  what: "Implement OAuth2 login UI"
  how: "standards/frontend-standard.md"
  goal: "Users can login via Google/GitHub"
  check:
    valid: "User clicks Google, redirects, logs in"
    error: "Handle OAuth errors gracefully"
    invalid: "Prevent CSRF attacks"
    edge: "Handle popup blockers"
    functional: "Store auth tokens correctly"
    visual: "Button renders properly"
    performance: "Redirect < 500ms"
    security: "Validate state parameter"
  close: "OAuth UI complete, tested, documented"
```

**Expected Output:**
```yaml
result:
  status: "completed"
  quality_score: 8.5
  metrics:
    code_quality: 9
    test_coverage: 8
    architectural_coherence: 9
    error_handling: 8
    documentation: 8
    performance: 9
    security: 9
    maintainability: 8
  tests_passed:
    valid: true
    error: true
    invalid: true
    edge: true
    functional: true
    visual: true
    performance: true
    security: true
  files_created:
    - "src/components/Auth/LoginButton.tsx"
    - "src/components/Auth/LoginButton.test.tsx"
  test_doc_created: "ai-state/active/tests/task-001-oauth-ui.md"
  next_recommended: "task-002-oauth-api"
```

---

## Orchestrator Skill Invocation

The execute-tasks command uses Claude Code's Skill tool to invoke orchestrators:

```python
from skills import invoke_skill

# For frontend tasks
result = invoke_skill(
    skill_name="frontend-orchestrator",
    task_context=task_data,
    standards_path="ai-state/standards/frontend-standard.md",
    quality_threshold=8.0
)

# For backend tasks
result = invoke_skill(
    skill_name="backend-orchestrator",
    task_context=task_data,
    standards_path="ai-state/standards/backend-standard.md",
    quality_threshold=8.0
)

# And so on for data, test, devops orchestrators
```

---

## Error Handling

### Task Execution Fails

```bash
[EXECUTE] task-006-complex-feature
→ Invoking backend-orchestrator...
→ Implementation failed: Missing database schema
→ Status: blocked
→ Blocker: Requires task-003-oauth-db to complete first

Recommendation: Check task dependencies in tasks.yaml
```

### Quality Score Below Threshold

```bash
[EXECUTE] task-007-api-endpoint
→ Invoking backend-orchestrator...
→ Implementation complete
→ Quality score: 7.2/10 ✗ (below 8.0 threshold)
→ Refining implementation...
→ Quality score: 8.1/10 ✓
→ Status: completed
```

### Tests Failing

```bash
[EXECUTE] task-009-validation
→ Invoking backend-orchestrator...
→ Implementation complete
→ Running tests...
  ✓ valid
  ✓ error
  ✗ invalid (input validation failing)
  ✓ edge
→ Fixing test failures...
→ All tests passing ✓
→ Status: completed
```

---

## Monitoring Active Execution

### Watch Real-Time Progress

```bash
# Terminal 1: Execute tasks
/execute-tasks

# Terminal 2: Watch logs
tail -f ai-state/operations.log

# Output:
{"timestamp":"2025-11-04T18:00:00Z","orchestrator":"frontend-orchestrator","event":"task.started","task_id":"task-001-oauth-ui"}
{"timestamp":"2025-11-04T18:05:00Z","orchestrator":"frontend-orchestrator","event":"implementation.complete","task_id":"task-001-oauth-ui"}
{"timestamp":"2025-11-04T18:08:00Z","orchestrator":"frontend-orchestrator","event":"tests.passed","task_id":"task-001-oauth-ui","count":8}
{"timestamp":"2025-11-04T18:10:00Z","orchestrator":"frontend-orchestrator","event":"task.completed","task_id":"task-001-oauth-ui","quality_score":8.5}
```

### Check Current Status

```bash
python orchestrate.py status

[STATUS] Orchestration System Status
==================================================
[PLAN] Operations logged: 42

[RECENT] Recent events:
  2025-11-04T18:10:00 - task.completed
  2025-11-04T18:08:00 - tests.passed
  2025-11-04T18:05:00 - implementation.complete
  2025-11-04T18:00:00 - task.started
  2025-11-04T17:55:00 - plan.created

[TASKS] Epics: 2
[OK] Tasks: 8

[METRICS] Task Status:
  completed: 3
  in_progress: 1
  pending: 4
  blocked: 0
```

---

## Best Practices

### Sequential vs Parallel Execution

**Sequential (Default):**
- Respects task dependencies
- Executes one at a time
- Ensures stable state between tasks

**Parallel (Advanced):**
```bash
/execute-tasks --context frontend --parallel
# Executes all frontend tasks concurrently
# Only if no dependencies between them
```

### Dependency Management

Tasks with dependencies should specify them:

```yaml
tasks:
  task-002-oauth-api:
    dependencies: []  # Can run immediately

  task-004-oauth-tests:
    dependencies:
      - task-001-oauth-ui
      - task-002-oauth-api
      - task-003-oauth-db
    when: "All OAuth implementation complete"
```

The execute-tasks command respects dependencies automatically.

---

## Troubleshooting

### "No orchestrator found for context"

**Problem:** Task has unknown context
**Solution:** Update task with valid context (frontend/backend/data/test/devops)

### "Quality threshold not met after 3 attempts"

**Problem:** Implementation consistently scores < 8.0
**Solution:** Review the standard, ask for clarification, or adjust complexity

### "Skill invocation failed"

**Problem:** Orchestrator skill not found or misconfigured
**Solution:** Run `python validate_enhanced.py` to check skill setup

---

## Summary

The `/execute-tasks` command is the **execution engine** that:

1. ✅ Reads pending tasks from tasks.yaml
2. ✅ Routes to appropriate orchestrator based on context
3. ✅ Invokes orchestrator skills with full task context
4. ✅ Monitors execution and quality gates
5. ✅ Updates task status upon completion
6. ✅ **Creates test documentation in ai-state/active/tests/**
7. ✅ Logs all events to operations.log
8. ✅ Handles errors and dependencies

**Complete Workflow:**
```
/init-project → /brainstorm → /write-plan → /execute-tasks → Monitor logs
```

This closes the loop and makes the orchestration system fully functional!
