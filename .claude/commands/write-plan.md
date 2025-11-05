# /write-plan Command

Generate implementation plan from brainstorm design.

## Usage
```
/write-plan [design-file]
```

## What it does
1. Reads design document (from brainstorm)
2. Creates epic with decomposed tasks
3. Each task has test requirements
4. Saves to task registry
5. Ready for execution

## Integration
```python
import sys
sys.path.append('.')
from orchestrate import Orchestrator

orchestrator = Orchestrator()
epic_id = orchestrator.write_plan()
print(f"Epic created: {epic_id}")
print("Tasks are ready for execution")
```

## Task Structure
Each generated task includes:
- **when**: Start conditions
- **who**: Skill to execute
- **where**: Code location
- **what**: Feature to build
- **how**: Standards to follow
- **goal**: Success criteria
- **check**: Test requirements
- **close**: Completion state

## Example Flow
```
User: /write-plan
System: Using recent design: ai-state/knowledge/brainstorm-dark-mode.md
System: Created Epic: epic-1234567
System: Tasks created: 3
  - task-001: Create UI components
  - task-002: Implement API endpoints
  - task-003: Create test suite
```