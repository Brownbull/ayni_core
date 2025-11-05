# Claude Code - AI Orchestration Framework

**This project uses the AI Orchestration Framework for structured development, testing, and documentation.**

---

## 🎯 Quick Reference

```bash
# Initialize new features
/brainstorm "feature description"
/write-plan

# Check system status
tail -f ai-state/operations.log

# View documentation
cat ai-state/human-docs/INDEX.md
```

---

## 📋 Project Overview

**Project:** ayni_core
**Tech Stack:** To be determined
**Contexts:** frontend, backend, data

### Architecture
Run /init-project to scan and document architecture

### Current Priorities
Initialize orchestration framework

---

## 🔄 Development Workflow

### 1. Feature Development

When implementing new features, **always** follow this cycle:

#### Step 1: Brainstorm & Design
```
/brainstorm "Add user authentication with OAuth2"
```

This will:
- Analyze the feature requirements
- Apply relevant quality standards
- Identify affected contexts (frontend/backend/data)
- Create design decisions

#### Step 2: Create Implementation Plan
```
/write-plan
```

This generates:
- Decomposed tasks with 8 test types each
- Assignment to orchestrators
- Dependencies between tasks
- Quality thresholds

#### Step 3: Implement with Quality Gates

For each task:
1. Read the task from `ai-state/active/tasks.yaml`
2. Follow the assigned standard (e.g., `standards/frontend-standard.md`)
3. Implement the feature
4. Write all 8 test types:
   - **valid**: Happy path scenarios
   - **error**: Error handling
   - **invalid**: Input validation
   - **edge**: Boundary conditions
   - **functional**: Business logic
   - **visual**: UI tests (if applicable)
   - **performance**: Load/speed tests
   - **security**: Security validation

5. Self-evaluate against the standard (minimum 8.0/10)
6. If score < 8.0, refine until passing
7. Update task status in `ai-state/active/tasks.yaml`
8. Log completion to `ai-state/operations.log`

#### Step 4: Documentation

When epic completes:
- Auto-generate role-based documentation via `human-docs-generator`
- Update architecture decisions in `ai-state/knowledge/decisions.md`
- Document new patterns in `ai-state/knowledge/patterns.md`

---

## 📊 Quality Standards

### Code Quality (8.0/10 minimum)

Evaluate on 8 metrics (0-10 each):
1. **Code Quality & Clarity** - Clean code, naming, structure
2. **Test Coverage** - >85% coverage, edge cases included
3. **Architectural Coherence** - Follows established patterns
4. **Error Handling** - Graceful failures, user-friendly errors
5. **Documentation** - Clear comments, examples, API docs
6. **Performance** - Optimized, no bottlenecks
7. **Security** - No vulnerabilities, input validation
8. **Maintainability** - Easy to change, low technical debt

**Formula:** `(sum of 8 metrics) / 8 >= 8.0`

### Context-Specific Standards


**Frontend** (`standards/frontend-standard.md`):
- Component architecture (reusable, single responsibility)
- TypeScript strict mode
- Accessibility (WCAG AA)
- Performance (<1s initial load)
- Testing (React Testing Library + Playwright)



**Backend** (`standards/backend-standard.md`):
- RESTful API design
- Input validation (all endpoints)
- Authentication & authorization
- Error handling (consistent format)
- Performance (<200ms response time)
- Testing (>80% coverage)



**Data Quality** (`standards/data-quality-standard.md`):
- Completeness: 20% (no missing data)
- Accuracy: 20% (correct values)
- Consistency: 20% (uniform across systems)
- Timeliness: 15% (fresh data)
- Uniqueness: 15% (no duplicates)
- Validity: 10% (correct formats)

**Minimum:** 95% overall score



**DevOps** (`standards/devops-standard.md`):
- DORA Metrics:
  - Deploy frequency: >1/day
  - Lead time: <1 hour
  - MTTR: <1 hour
  - Change failure rate: <5%


---

## 🧪 Testing Requirements

Every task MUST include all 8 test types:

### 1. Valid (Happy Path)
```javascript
// Example
test('user can login with correct credentials', async () => {
  const result = await login('user@example.com', 'password123');
  expect(result.success).toBe(true);
});
```

### 2. Error Handling
```javascript
test('handles network errors gracefully', async () => {
  mockNetworkError();
  const result = await login('user@example.com', 'password123');
  expect(result.error).toBe('Connection failed. Please try again.');
});
```

### 3. Invalid Input
```javascript
test('rejects invalid email format', async () => {
  const result = await login('not-an-email', 'password123');
  expect(result.error).toBe('Invalid email format');
});
```

### 4. Edge Cases
```javascript
test('handles empty password', async () => {
  const result = await login('user@example.com', '');
  expect(result.error).toBe('Password is required');
});
```

### 5. Functional (Business Logic)
```javascript
test('increments login attempt counter', async () => {
  await login('user@example.com', 'wrong');
  const attempts = await getLoginAttempts('user@example.com');
  expect(attempts).toBe(1);
});
```

### 6. Visual (UI Components)
```javascript
test('displays error message to user', async () => {
  render(<LoginForm />);
  await userEvent.click(screen.getByRole('button', { name: /login/i }));
  expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
});
```

### 7. Performance
```javascript
test('login completes within 200ms', async () => {
  const start = Date.now();
  await login('user@example.com', 'password123');
  const duration = Date.now() - start;
  expect(duration).toBeLessThan(200);
});
```

### 8. Security
```javascript
test('password is not logged in plaintext', async () => {
  const logSpy = jest.spyOn(console, 'log');
  await login('user@example.com', 'password123');
  expect(logSpy).not.toHaveBeenCalledWith(expect.stringContaining('password123'));
});
```

---

## 📂 File Organization

```
C:\Projects\play\ayni_core

.claude/
├── commands/           # Slash commands
└── skills/            # 7 orchestrators

ai-state/
├── operations.log     # Event log (append-only)
├── active/
│   ├── tasks.yaml    # Current tasks
│   └── */tasks/      # Context-specific tasks
├── standards/         # Quality standards
├── knowledge/         # Architecture, patterns, decisions
└── human-docs/        # Auto-generated guides

orchestration.config.json  # System configuration
```

---

## 🎨 Task Structure

Every task follows this format:

```yaml
task:
  id: "task-001-feature"
  epic: "epic-feature-name"
  context: "frontend|backend|data|devops"
  when: "Prerequisites met"
  who: "orchestrator-skill"
  where: "src/components/Auth.tsx"
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

---

## 🔍 Observability

### Real-Time Monitoring
```bash
tail -f ai-state/operations.log
```

### Event Format
```json
{
  "timestamp": "2025-01-04T12:00:00Z",
  "orchestrator": "frontend-orchestrator",
  "event": "task.completed",
  "task_id": "task-001-oauth-ui",
  "quality_score": 8.5,
  "tests_passed": 8
}
```

### Check Task Status
```bash
cat ai-state/active/tasks.yaml
```

---

## 📖 Documentation

Human-readable docs are auto-generated in `ai-state/human-docs/`:

- **frontend-developer.md** - Component architecture, state management
- **backend-developer.md** - API endpoints, database schema
- **data-engineer.md** - Pipelines, data sources, quality metrics
- **tester.md** - Test strategies, coverage reports
- **devops.md** - Deployment process, monitoring
- **architect.md** - System design, architectural decisions
- **product-manager.md** - Feature status, roadmap
- **end-user-guide.md** - How to use the application

Documentation updates automatically on:
- Epic completion
- Breaking changes
- Architecture decisions

---

## 🚀 Best Practices

### DO:
- ✅ Use `/brainstorm` before starting new features
- ✅ Follow the assigned quality standard
- ✅ Write all 8 test types
- ✅ Self-evaluate and refine until 8.0/10
- ✅ Log events to operations.log
- ✅ Update knowledge base with new patterns/decisions
- ✅ Keep tasks small and focused

### DON'T:
- ❌ Skip test types to "save time"
- ❌ Proceed with quality score < 8.0
- ❌ Create mega-tasks spanning multiple contexts
- ❌ Bypass orchestrators
- ❌ Ignore failed tests
- ❌ Write code without understanding requirements

---

## 🆘 Troubleshooting

### "Task unclear, need more context"
→ Check `ai-state/knowledge/` for architecture and patterns
→ Read related tasks in `ai-state/active/tasks.yaml`
→ Ask clarifying questions

### "Quality score below 8.0"
→ Review the specific metrics that scored low
→ Refer to the relevant standard for guidance
→ Refactor and re-evaluate

### "Test failing"
→ Check operations.log for error details
→ Review test requirements in task definition
→ Ensure all 8 test types are implemented

### "Unclear which orchestrator to use"
→ Frontend: UI, components, state
→ Backend: APIs, services, business logic
→ Data: ETL, pipelines, analytics
→ Test: Testing strategy, coverage
→ DevOps: Infrastructure, CI/CD, deployment

---

## 🎓 Learning Resources

- **Architect Standard**: `ai-state/standards/architect-standard.md`
- **Patterns**: `ai-state/knowledge/patterns.md`
- **Decisions**: `ai-state/knowledge/decisions.md`
- **Architecture**: `ai-state/knowledge/architecture.md`

---

## 🔄 Version Control

**Commit to Git:**
- ✅ `ai-state/knowledge/` (patterns, decisions)
- ✅ `ai-state/active/tasks.yaml` (task registry structure)
- ✅ `orchestration.config.json` (configuration)

**DON'T Commit:**
- ❌ `ai-state/operations.log` (regenerates)
- ❌ `ai-state/active/*/tasks/*` (ephemeral)
- ❌ `*.log.backup`, `*.tmp`

---

**Framework Version:** 2.0.1
**Last Updated:** 2025-11-04T20:45:15.493535Z
**Quality Standards:** 8.0/10 minimum
**Test Coverage:** 80% minimum

For questions about the orchestration framework, refer to `orchestration-bundle/README.md`
