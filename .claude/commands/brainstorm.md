# /brainstorm Command

Execute brainstorming session using the orchestration system.

## Usage
```
/brainstorm [topic]
```

## What it does
1. Starts interactive brainstorming session
2. Asks clarifying questions about your idea
3. Generates design document
4. Saves to knowledge base
5. Ready for `/write-plan` next

## Integration
```python
import sys
sys.path.append('.')
from orchestrate import Orchestrator

orchestrator = Orchestrator()
design_path = orchestrator.brainstorm()
print(f"Design ready at: {design_path}")
print("Run /write-plan to create implementation tasks")
```

## Example Flow
```
User: /brainstorm "Add dark mode"
System: What problem are you trying to solve?
User: Users want to work at night
System: Who will use this feature?
User: All users
System: [generates design document]
System: Design saved to ai-state/knowledge/brainstorm-add-dark-mode.md
```