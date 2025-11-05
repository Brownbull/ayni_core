# /refactor-module Command

Break up large files (>500-800 lines) into smaller, reusable modules with versioning.

## Usage
```bash
/refactor-module <file-path> [--threshold 800] [--version v2]
```

## What It Does
1. **Analyze Module**
   - Scan file for size, complexity, coupling
   - Identify logical boundaries
   - Detect duplicated code
   - Find reusable components

2. **Suggest Breakdown**
   - Propose module structure
   - Recommend naming patterns
   - Create migration plan
   - Preserve old version (for easy revert)

3. **Execute Refactoring**
   - Create smaller modules
   - Extract reusable parts
   - Update imports/references
   - Run tests to verify

4. **Version Management**
   - Keep old file as `[name]_v1.[ext]`
   - New file becomes `[name]_v2.[ext]` or `[name].[ext]`
   - Easy rollback if needed

## When to Use

### Automatic Triggers (if integrated in workflow)
- File exceeds 800 lines during implementation
- Cyclomatic complexity > 15
- More than 5 responsibilities detected

### Manual Triggers
```bash
# After review finds large files
/review-architecture task-007
# Output: "apps/processing/tasks.py: 1,234 lines → NEEDS REFACTORING"

/refactor-module apps/processing/tasks.py

# Or specify threshold
/refactor-module apps/processing/tasks.py --threshold 600

# Or specify version
/refactor-module apps/processing/serializers.py --version v3
```

## Parameters

### `<file-path>` (required)
Path to file to refactor
```bash
/refactor-module apps/processing/tasks.py
/refactor-module src/components/Dashboard.tsx
```

### `--threshold <lines>` (optional, default: 800)
Maximum lines per module
```bash
/refactor-module tasks.py --threshold 500  # Stricter
/refactor-module tasks.py --threshold 1000 # More lenient
```

### `--version <name>` (optional, default: v2)
Version suffix for new files
```bash
/refactor-module auth_service.py --version v2
# Creates: auth_service_v2.py, keeps auth_service.py as v1
```

### `--dry-run` (optional)
Preview refactoring without making changes
```bash
/refactor-module tasks.py --dry-run
# Shows plan but doesn't create files
```

## Output Format

```markdown
# Module Refactoring Plan: [file]

## Current State Analysis

**File:** [path]
**Lines:** [count]
**Threshold:** [threshold]
**Status:** [NEEDS_REFACTORING / OK]

### Complexity Metrics
- Total Lines: [count]
- Functions: [count]
- Classes: [count]
- Avg Function Length: [lines]
- Max Function Length: [lines]
- Cyclomatic Complexity: [max score]

### Responsibilities Detected
1. [Responsibility 1] (lines 1-250)
2. [Responsibility 2] (lines 251-500)
3. [Responsibility 3] (lines 501-750)
...

---

## Proposed Breakdown

### Strategy: [Split by Responsibility / Extract Common / Feature-based]

**Before:**
```
tasks.py (1,234 lines)
├── CSV Processing (400 lines)
├── Validation Logic (350 lines)
├── Database Operations (300 lines)
├── WebSocket Notifications (184 lines)
```

**After:**
```
processing/
├── csv_processor.py (320 lines)
│   └── CSVProcessor class
├── validators.py (280 lines)
│   ├── validate_csv_file()
│   ├── validate_column_mappings()
│   └── ValidationError class
├── database_ops.py (250 lines)
│   ├── save_transactions_to_db()
│   ├── track_data_updates()
│   └── DatabaseTransaction class
├── notifications.py (150 lines)
│   ├── send_ws_notification()
│   └── NotificationHandler class
└── tasks.py (234 lines) ← main orchestration only
    ├── process_csv_upload() ← delegates to modules
    └── cleanup_old_uploads()
```

---

## Migration Plan

### Step 1: Backup Original
```bash
# Original preserved as v1
mv tasks.py tasks_v1.py
# Or with git branch
git checkout -b refactor-tasks
```

### Step 2: Create New Modules
```python
# File 1: processing/csv_processor.py
class CSVProcessor:
    """Handles CSV parsing and transformation."""
    def __init__(self, file_path, column_mappings):
        ...
    
    def parse(self):
        ...
    
    def validate_structure(self):
        ...

# File 2: processing/validators.py
def validate_csv_file(file_path, column_mappings):
    """Validate CSV file structure and content."""
    ...

def validate_column_mappings(mappings, required_columns):
    """Validate column mappings are complete."""
    ...

# File 3: processing/database_ops.py
def save_transactions_to_db(company, upload, data):
    """Bulk save transactions with atomic transaction."""
    ...

# File 4: processing/notifications.py
class NotificationHandler:
    """Handles WebSocket notifications."""
    def send_progress(self, upload_id, progress, message):
        ...
    
    def send_completion(self, upload_id, result):
        ...

# File 5: processing/tasks.py (refactored, 234 lines)
from .csv_processor import CSVProcessor
from .validators import validate_csv_file, validate_column_mappings
from .database_ops import save_transactions_to_db
from .notifications import NotificationHandler

@shared_task(bind=True)
def process_csv_upload(self, upload_id):
    """Main orchestration - delegates to modules."""
    # 1. Validate
    validate_csv_file(file_path, mappings)
    
    # 2. Parse
    processor = CSVProcessor(file_path, mappings)
    data = processor.parse()
    
    # 3. Save
    save_transactions_to_db(company, upload, data)
    
    # 4. Notify
    notifier = NotificationHandler()
    notifier.send_completion(upload_id, result)
```

### Step 3: Update Imports Across Project
```python
# Before
from apps.processing.tasks import validate_csv_file

# After
from apps.processing.validators import validate_csv_file
```

### Step 4: Run Tests
```bash
pytest apps/processing/test_celery_tasks.py -v
# Verify all tests still pass
```

### Step 5: Update Documentation
- [ ] Update endpoints.md with new module structure
- [ ] Update architecture.md if significant change
- [ ] Add migration notes to task report

---

## Extraction Patterns

### Pattern 1: Extract Validators
**When:** Functions that validate input/output
**Location:** `validators.py` or `validation/`
```python
# validators.py
def validate_email(email):
    ...

def validate_rut(rut):
    ...
```

### Pattern 2: Extract Data Operations
**When:** Database queries, transformations
**Location:** `db_operations.py` or `repositories/`
```python
# db_operations.py
class TransactionRepository:
    def save_bulk(self, transactions):
        ...
    
    def get_by_period(self, company_id, period):
        ...
```

### Pattern 3: Extract Business Logic
**When:** Core business rules, calculations
**Location:** `services/` or `domain/`
```python
# services/transaction_service.py
class TransactionService:
    def process_transaction(self, data):
        ...
    
    def calculate_totals(self, transactions):
        ...
```

### Pattern 4: Extract Utilities
**When:** Reusable helper functions
**Location:** `utils.py` or `lib/`
```python
# utils/formatting.py
def format_currency(amount):
    ...

def format_rut(rut):
    ...
```

### Pattern 5: Extract Constants
**When:** Magic numbers, configuration
**Location:** `constants.py` or `config/`
```python
# constants.py
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB
DEFAULT_BATCH_SIZE = 1000
SUPPORTED_FILE_TYPES = ['.csv', '.xlsx']
```

---

## Naming Patterns

### Version Suffixes
```bash
# Keep old version for rollback
auth_service.py → auth_service_v1.py (preserved)
                → auth_service_v2.py (new, refactored)

# After testing v2, can remove v1 or keep as backup
```

### Module Names (Follow Python conventions)
```bash
# Good
user_repository.py
transaction_service.py
validation_utils.py

# Avoid
UserRepo.py (use snake_case, not PascalCase for files)
utils2.py (use descriptive names, not numbers)
new_auth.py (use versioning pattern instead)
```

### Git Branch Strategy
```bash
# Create feature branch for refactoring
git checkout -b refactor/tasks-module

# Make changes, test thoroughly
git add processing/
git commit -m "refactor: break up tasks.py into smaller modules

- Extract CSVProcessor (320 lines)
- Extract validators (280 lines)
- Extract database ops (250 lines)
- Extract notifications (150 lines)
- Main tasks.py now 234 lines (orchestration only)

All tests passing, 0 functionality changes."

# Merge when ready
git checkout main
git merge refactor/tasks-module
```

---

## Rollback Strategy

### If v2 Breaks Something

**Option 1: Quick Revert (versioned files)**
```python
# In imports, change:
from processing.tasks_v2 import process_csv_upload
# To:
from processing.tasks_v1 import process_csv_upload

# Or rename files:
mv tasks_v2.py tasks_v2_broken.py
mv tasks_v1.py tasks.py
```

**Option 2: Git Revert (if committed)**
```bash
git revert <commit-hash>
# Or
git checkout main
git reset --hard HEAD~1
```

**Option 3: Restore from Backup**
```bash
cp tasks_v1.py tasks.py
```

---

## Quality Checks After Refactoring

### Must Verify
- [ ] All tests pass (pytest / npm test)
- [ ] No functionality changed (behavioral equivalence)
- [ ] Imports updated across project
- [ ] Coverage maintained or improved
- [ ] Documentation updated
- [ ] No circular imports introduced

### Refactoring Success Metrics
- ✅ Files under threshold (< 800 lines)
- ✅ Single Responsibility Principle per file
- ✅ Reduced cyclomatic complexity
- ✅ Increased reusability
- ✅ Improved testability
- ✅ Faster CI/CD (smaller files = faster parsing)

---

## Integration with Orchestration

```python
# In orchestrate.py

class Orchestrator:
    def refactor_module(self, file_path, threshold=800, version="v2", dry_run=False):
        """
        Break up large module into smaller parts.
        
        Args:
            file_path: Path to file to refactor
            threshold: Max lines per module (default 800)
            version: Version suffix for new files (default "v2")
            dry_run: Preview only, don't create files
        """
        # 1. Analyze file
        analysis = self.analyze_module(file_path)
        
        if analysis.lines < threshold:
            print(f"[OK] {file_path} is under threshold ({analysis.lines}/{threshold} lines)")
            return
        
        # 2. Generate refactoring plan
        plan = self.generate_refactoring_plan(analysis, threshold)
        
        if dry_run:
            print(f"[DRY-RUN] Refactoring plan for {file_path}")
            self.display_plan(plan)
            return
        
        # 3. Backup original
        backup_path = self.backup_file(file_path, version="v1")
        
        # 4. Create new modules
        new_files = self.create_refactored_modules(plan, version)
        
        # 5. Update imports
        self.update_imports(file_path, new_files)
        
        # 6. Run tests
        test_result = self.run_tests_for_module(file_path)
        
        if not test_result.passed:
            print(f"[FAIL] Tests failed after refactoring. Rolling back...")
            self.rollback_refactoring(backup_path, new_files)
            return
        
        # 7. Generate report
        report_path = f"ai-state/refactorings/{file_path.stem}-refactor.md"
        self.generate_refactoring_report(plan, new_files, report_path)
        
        print(f"[SUCCESS] Refactored {file_path}")
        print(f"[BACKUP] Original saved as {backup_path}")
        print(f"[FILES] Created {len(new_files)} new modules")
        print(f"[REPORT] {report_path}")
        
        return report_path
```

## Example Workflows

### Workflow 1: Review Finds Large File
```bash
# Review finds issue
/review-architecture task-008

# Output:
# [ISSUE] apps/processing/tasks.py: 1,234 lines → NEEDS REFACTORING

# Refactor it
/refactor-module apps/processing/tasks.py

# Output:
[ANALYZE] apps/processing/tasks.py (1,234 lines)
[DETECT] 4 distinct responsibilities
[PLAN] Breaking into 5 modules
[BACKUP] Original → tasks_v1.py
[CREATE] csv_processor.py (320 lines)
[CREATE] validators.py (280 lines)
[CREATE] database_ops.py (250 lines)
[CREATE] notifications.py (150 lines)
[REFACTOR] tasks.py → 234 lines (orchestration only)
[TEST] Running tests... ✓ All passed
[SUCCESS] Refactoring complete

Report: ai-state/refactorings/tasks-refactor.md
```

### Workflow 2: Preventive Refactoring During Development
```bash
# Working on large feature
# File growing quickly

# Check current state
/refactor-module src/services/analytics.py --dry-run

# Output shows plan
# Decide to refactor now before it gets bigger

/refactor-module src/services/analytics.py --threshold 500
```

### Workflow 3: Versioned Iteration
```bash
# Have auth_service.py (working but messy)
/refactor-module auth_service.py --version v2

# Test v2
# Has issues, but don't want to lose work
/refactor-module auth_service_v2.py --version v3

# Now have:
# - auth_service.py (original, always works)
# - auth_service_v2.py (first refactor, has issues)
# - auth_service_v3.py (second refactor, testing)
```

---

## Anti-Patterns

❌ **Don't** refactor without tests - you'll break things
❌ **Don't** delete old version immediately - keep for rollback
❌ **Don't** change behavior during refactoring - refactor ≠ rewrite
❌ **Don't** create too many tiny files - aim for 200-600 lines sweet spot
❌ **Don't** forget to update imports - will cause runtime errors
❌ **Don't** skip documentation - future you will be confused

---

## Best Practices

✅ **Do** refactor early - easier when file is 900 lines vs 2000 lines
✅ **Do** use git branches - isolate refactoring work
✅ **Do** test after every change - incremental verification
✅ **Do** use descriptive module names - makes code self-documenting
✅ **Do** keep reusable parts separate - maximizes value
✅ **Do** document why you refactored - helps team understand

---

**Remember:** Small modules are easier to debug, test, and regenerate. When AI context breaks, you only lose a 300-line file, not a 2000-line monolith.
