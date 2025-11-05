# Initialize Orchestration for Existing Project (Enhanced)

You are helping initialize the AI Orchestration Framework for an existing project. This enhanced process handles **existing CLAUDE.md** files and **existing AI documentation**.

---

## Overview

This initialization process will:
1. Scan codebase for tech stack and structure
2. **Scan for existing AI documentation** (ai/, docs/, .claude/)
3. **Analyze existing CLAUDE.md** (if present)
4. Ask clarifying questions
5. **Merge/consolidate existing docs** with orchestration framework
6. Enable **session continuity** for multi-session initialization

---

## Step 1: Run Comprehensive Scans

### 1A: Project Scanner (Codebase)
```python
# Execute: python khujta_ai_sphere/project_scanner.py
```

Detects:
- Tech stack (React, FastAPI, Django, etc.)
- Project structure (frontend/backend/data/devops)
- Entry points (package.json, main.py, etc.)

### 1B: AI Documentation Scanner (NEW)
```python
# Execute: python khujta_ai_sphere/ai_docs_scanner.py
```

Discovers:
- Existing AI folders (ai/, .claude/, etc.)
- Documentation folders (docs/, specifications/)
- **Categorizes by type:**
  - Architecture docs
  - Specifications/features
  - Planning/roadmaps
  - Context/knowledge (ADRs, patterns)
  - Testing docs
- **Detects existing framework:**
  - ai-state/ presence
  - operations.log
  - task registries
  - Prior orchestration work

### 1C: CLAUDE.md Analysis (NEW)
```python
# Execute: python khujta_ai_sphere/claude_md_merger.py
```

If CLAUDE.md exists, analyzes:
- Project overview sections
- Existing architecture info
- Custom workflow instructions
- Coding standards/conventions
- Testing requirements
- **Custom sections to preserve**

---

## Step 2: Review Scan Results with User

Present findings and ask about continuity:

### About Existing Documentation
```
SCAN RESULTS:

[EXISTING AI DOCUMENTATION FOUND]
✓ ai/ folder (45 files, 234 KB)
  - Architecture docs: 8 files
  - Specifications: 12 files
  - Planning: 5 files
  - Context/Knowledge: 10 files

[EXISTING CLAUDE.md FOUND]
✓ CLAUDE.md (187 lines)
  - Has project overview: Yes
  - Has architecture: Yes
  - Has custom workflow: Yes
  - Has coding standards: Yes
  - Custom sections: 5

[PREVIOUS ORCHESTRATION DETECTED]
✓ ai-state/ folder exists
✓ operations.log (last entry: 2025-10-15)
✓ 3 incomplete epics found

QUESTIONS:
1. I found existing AI documentation. Should I:
   a) Incorporate and continue from previous work? (RECOMMENDED)
   b) Start fresh (archive existing docs)?

2. I found existing CLAUDE.md with project guidelines. Should I:
   a) Merge with orchestration framework instructions? (RECOMMENDED)
   b) Replace with framework template?

3. I found previous orchestration work (last session: Oct 15). Should I:
   a) Continue from last session? (RECOMMENDED)
   b) Reset and start over?
```

### About the Project (if no existing docs)
1. "What is the primary purpose of this application?"
2. "Who are the main users/stakeholders?"
3. "What are the most critical features currently?"

### About the Codebase
1. "Are there any areas of technical debt to be aware of?"
2. "What's the current testing approach?"
3. "Are there any known pain points in the development process?"

### About Goals
1. "What are you hoping to achieve with the orchestration framework?"
2. "Are there any upcoming features or refactors planned?"
3. "What quality standards are most important?"

---

## Step 3: Initialize/Merge AI-State

### If NO existing documentation:

Create fresh knowledge base:

**ai-state/knowledge/architecture.md**
```markdown
# Architecture Overview
[Based on scan + user answers]

## System Design
- Frontend: [detected framework]
- Backend: [detected framework]
[... rest based on conversation]
```

### If EXISTING documentation found:

**Consolidate and enhance:**

**ai-state/knowledge/existing-docs-index.md** (NEW)
```markdown
# Existing Documentation Index

## Architecture Documentation
- [ai/architect/ARCHITECTURE.md](../../ai/architect/ARCHITECTURE.md)
- [docs/system-design.md](../../docs/system-design.md)

## Specifications
- [ai/specs/feature-store.md](../../ai/specs/feature-store.md)
[... full index of existing docs]

## Integration Note
All documents above have been indexed and will be referenced
during brainstorming and task planning.
```

**ai-state/knowledge/architecture.md**
```markdown
# Architecture Overview (Consolidated)

*This document consolidates information from:*
*- ai/architect/ARCHITECTURE.md*
*- docs/system-design.md*
*- User interview responses*

[Synthesized architecture combining existing docs + new info]

## References
See [existing-docs-index.md](existing-docs-index.md) for detailed specs.
```

**Same consolidation for:**
- patterns.md (from existing + new)
- decisions.md (from existing ADRs + new)
- context.md (from existing + conversation)

---

## Step 4: Handle CLAUDE.md

### If NO existing CLAUDE.md:
Generate from template with project-specific values.

### If EXISTING CLAUDE.md: (NEW BEHAVIOR)

**Execute merger:**
```python
# Runs automatically: claude_md_merger.py
```

**Creates:**
1. **CLAUDE.md.backup** - Original preserved
2. **CLAUDE.md** - Merged version containing:
   - **Preserved sections:**
     - Original project overview
     - Custom guidelines
     - Existing standards
     - Project-specific conventions
   - **Added sections:**
     - Orchestration quick reference
     - /brainstorm, /write-plan, /init-project commands
     - Quality gates (8.0/10 minimum)
     - 8 test types requirement
     - Observability (operations.log)
   - **Integration note:**
     ```
     This CLAUDE.md has been MERGED to preserve your
     existing project context while adding orchestration
     capabilities. Your original guidelines remain in force.
     ```

---

## Step 5: Session Continuity (NEW)

### If Previous Orchestration Detected:

**Read last session state:**
```yaml
# From ai-state/session-state.json
last_session:
  date: "2025-10-15T14:30:00Z"
  incomplete_epics:
    - epic-003-user-auth
    - epic-005-data-pipeline
    - epic-007-frontend-refactor
  pending_tasks: 12
  last_activity: "Completed task-045-oauth-ui, started task-046-oauth-api"
```

**Ask user:**
```
PREVIOUS SESSION DETECTED:

Last activity: Oct 15, 2025 (20 days ago)

Incomplete work:
  - epic-003-user-auth (2/5 tasks complete)
  - epic-005-data-pipeline (0/8 tasks complete)
  - epic-007-frontend-refactor (1/3 tasks complete)

Last task: task-046-oauth-api (in progress)

OPTIONS:
1. Continue from last session? (RECOMMENDED)
   - Resume task-046-oauth-api
   - Keep existing context
   - Maintain continuity

2. Review and restart epics?
   - Reassess priorities
   - Update roadmap
   - Keep completed work

3. Archive and start fresh?
   - Move to ai-state/archive/
   - Clean slate
```

**If continuing:**
```
[RESUMING SESSION]

Context restored from Oct 15:
✓ 3 epics loaded
✓ 12 pending tasks
✓ Last task: task-046-oauth-api (OAuth API implementation)

QUICK RECAP:
Epic 003 (User Auth):
  ✓ task-045-oauth-ui (completed)
  → task-046-oauth-api (IN PROGRESS - you were here)
  - task-047-oauth-db (pending)
  - task-048-oauth-tests (pending)
  - task-049-oauth-deploy (pending)

Next: Continue with task-046 or review/update?
```

---

## Step 6: Map Existing Code to Contexts

Based on all scans, create/update context mapping:

```yaml
contexts:
  frontend:
    status: existing
    framework: "React (TypeScript)"
    path: "src/"
    test_framework: "Jest + Playwright"
    existing_docs:
      - "ai/frontend/ARCHITECTURE.md"
      - "ai/ux-design/wireframes_summary.md"
    priority_tasks:
      - "Continue epic-007-frontend-refactor"
      - "Add missing E2E tests"
      - "Document component patterns"

  backend:
    status: existing
    framework: "FastAPI"
    path: "backend/"
    test_framework: "pytest"
    existing_docs:
      - "ai/backend/API_DESIGN.md"
      - "ai/backend/DATABASE_SCHEMA.md"
    priority_tasks:
      - "Complete task-046-oauth-api (IN PROGRESS)"
      - "Finish epic-003-user-auth"
      - "Add input validation (all endpoints)"

  [... other contexts]
```

---

## Step 7: Create/Update Session State

**ai-state/session-state.json**
```json
{
  "current_session": {
    "started": "2025-11-04T18:00:00Z",
    "initialization_mode": "merge_existing",
    "previous_session_restored": true
  },
  "active_epics": ["epic-003", "epic-005", "epic-007"],
  "current_task": "task-046-oauth-api",
  "context_focus": "backend",
  "next_steps": [
    "Complete task-046-oauth-api implementation",
    "Run comprehensive tests",
    "Update operations.log",
    "Move to task-047-oauth-db"
  ]
}
```

---

## Step 8: Summarize Initialization

### For Fresh Project:
```
[INITIALIZATION COMPLETE]

Detected Contexts: frontend (React), backend (FastAPI), data (Python)
Documentation Created:
  ✓ ai-state/knowledge/architecture.md
  ✓ ai-state/knowledge/patterns.md
  ✓ ai-state/knowledge/decisions.md
  ✓ ai-state/knowledge/context.md
  ✓ CLAUDE.md

Quality Standards Applied:
  - frontend-standard.md (8.0/10 minimum)
  - backend-standard.md (8.0/10 minimum)
  - data-quality-standard.md (95% minimum)

Next Steps:
  1. Review CLAUDE.md for workflow
  2. Use /brainstorm "first feature"
  3. Use /write-plan to create tasks
```

### For Existing Project with Docs: (NEW)
```
[INITIALIZATION COMPLETE - CONTINUITY MODE]

Existing Documentation Incorporated:
  ✓ ai/ folder (45 files) → Indexed in existing-docs-index.md
  ✓ CLAUDE.md → Merged with orchestration framework
  ✓ Previous session (Oct 15) → Restored

Contexts Detected: frontend, backend, data, devops

Session Continuity:
  ✓ Resumed from task-046-oauth-api
  ✓ 3 incomplete epics loaded
  ✓ 12 pending tasks ready

Documentation Consolidated:
  ✓ architecture.md (merged from 3 sources)
  ✓ patterns.md (merged from 2 sources)
  ✓ decisions.md (15 ADRs preserved + enhanced)
  ✓ CLAUDE.md (original + orchestration = merged)

Quality Standards Applied:
  - Existing standards preserved
  - Orchestration standards added (8.0/10 minimum)
  - 8 test types per task enforced

READY TO CONTINUE:
  Current: task-046-oauth-api (backend OAuth implementation)
  Next: task-047-oauth-db (database schema)
  Epic: epic-003-user-auth (2/5 complete, 60% done)

Commands:
  /brainstorm "continue OAuth implementation"
  tail -f ai-state/operations.log
  cat ai-state/session-state.json
```

---

## Important Notes

### Preservation Priority
- **ALWAYS preserve existing documentation**
- **NEVER overwrite user's CLAUDE.md** (merge instead)
- **NEVER delete existing ai-state/** (enhance instead)
- **ALWAYS backup before merging** (CLAUDE.md.backup)

### Session Continuity
- Check for operations.log to detect previous sessions
- Read session-state.json for context
- Ask user before resuming vs restarting
- Maintain task IDs and epic structure

### Multi-Session Initialization
If initialization takes multiple sessions:
```json
// ai-state/init-progress.json
{
  "initialization_started": "2025-11-04T18:00:00Z",
  "steps_completed": [
    "project_scan",
    "ai_docs_scan",
    "claude_md_analysis"
  ],
  "steps_pending": [
    "knowledge_consolidation",
    "epic_restoration"
  ],
  "resume_from": "step4_consolidation"
}
```

Next session continues from `resume_from` step.

---

## Example: Resuming After Interruption

```
User: Let's continue the initialization from yesterday