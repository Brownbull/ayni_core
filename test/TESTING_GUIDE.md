# GabeDA Refactoring - Testing Guide

This guide explains how to test the refactored code before migration.

---

## Quick Start

**Option 1: Run Integration Test (Recommended)**
```bash
python test_refactored_code.py
```

This will run 6 comprehensive tests covering all refactored modules.

**Option 2: Use Existing Notebook**
See "Testing with Existing Notebooks" section below.

---

## What Gets Tested

### Test 1: Basic Imports ✅
Verifies all refactored modules can be imported without errors.

### Test 2: Preprocessing Pipeline ✅
Tests:
- DataLoader (CSV, Excel, DataFrame)
- DataValidator (required columns, data quality)
- SchemaProcessor (column mapping, type conversion)

### Test 3: Features Package ✅
Tests:
- FeatureStore (store, retrieve, filesystem loading)
- FeatureTypeDetector (aggregation keyword detection)
- FeatureAnalyzer (feature metadata extraction)
- DependencyResolver (DFS algorithm)

### Test 4: Execution Package (4-Case Logic) ✅ **CRITICAL**
Tests the most important part - the 4-case logic:
- Case 1: Standard filter (reads data_in only)
- Case 2: Filter using attributes (reads data_in + agg_results) ⭐
- Case 3: Attribute with aggregation
- Case 4: Attribute composition (uses only other attributes)

Verifies:
- Single-loop execution works
- Flag tracking (in_flg, out_flg, groupby_flg)
- Correct decision logic
- Filters and attributes separated correctly

### Test 5: Context Integration ✅
Tests:
- GabedaContext dataset storage/retrieval
- Model output storage
- Model filters/attrs/input retrieval

### Test 6: Export Functionality ✅
Tests:
- ExcelExporter with context integration
- Excel file creation
- Multiple tabs (input, filters, attrs)

---

## Running the Integration Test

### Prerequisites
```bash
# Ensure you have all dependencies
pip install pandas numpy openpyxl
```

### Execute Test
```bash
# From repository root
python test_refactored_code.py
```

### Expected Output
```
============================================================
REFACTORED CODE INTEGRATION TEST
============================================================
Testing src_new/ implementation

============================================================
TEST 1: Basic Imports
============================================================
✓ All imports successful!

============================================================
TEST 2: Preprocessing Pipeline
============================================================
✓ DataLoader: Loaded 3 rows
✓ DataValidator: Validation passed
✓ SchemaProcessor: Processed 3 columns

... (more tests) ...

============================================================
TEST SUMMARY
============================================================
✓ PASS - Imports
✓ PASS - Preprocessing
✓ PASS - Features
✓ PASS - Execution (4-Case Logic)
✓ PASS - Context Integration
✓ PASS - Export

------------------------------------------------------------
Results: 6/6 tests passed
------------------------------------------------------------

🎉 ALL TESTS PASSED! Refactored code is working correctly.
Next step: Run Phase 8 migration (rename src_new -> src)
```

### If Tests Fail

Check the error output for details. Common issues:
- Missing dependencies → `pip install -r requirements.txt`
- Import errors → Check Python path
- Module not found → Ensure you're in repository root

---

## Testing with Existing Notebooks

### Option 1: Create Test Copy (Recommended)

1. **Copy an existing notebook**:
   ```bash
   # Windows
   copy quickstart.ipynb test_refactored.ipynb

   # Linux/Mac
   cp quickstart.ipynb test_refactored.ipynb
   ```

2. **Update imports in test notebook**:
   ```python
   # OLD
   from src.gabeda_context import GabedaContext
   from src.preprocessing import preprocess_data
   # ... etc

   # NEW
   from src_new.core.context import GabedaContext
   from src_new.preprocessing.schema import SchemaProcessor
   # ... etc
   ```

3. **Run the notebook**:
   - Execute all cells
   - Compare outputs with original notebook
   - Outputs should be identical

4. **Compare Results**:
   ```python
   # In notebook, compare DataFrames
   import pandas as pd

   # Load old results (if saved)
   old_filters = pd.read_csv('old_outputs/filters.csv')
   new_filters = pd.read_csv('new_outputs/filters.csv')

   # Compare
   pd.testing.assert_frame_equal(old_filters, new_filters)
   # If no error, they're identical!
   ```

### Option 2: Temporarily Modify Existing Notebook

⚠️ **Make a backup first!**

1. **Backup**:
   ```bash
   # Windows
   copy quickstart.ipynb quickstart_backup.ipynb

   # Linux/Mac
   cp quickstart.ipynb quickstart_backup.ipynb
   ```

2. **Update imports** (see above)

3. **Run and verify**

4. **Restore backup** when done

---

## Testing Individual Modules

### Test Preprocessing Only

```python
from src_new.preprocessing.loaders import DataLoader
from src_new.preprocessing.validators import DataValidator
from src_new.preprocessing.schema import SchemaProcessor

# Your test code here
loader = DataLoader()
df = loader.load_csv('data/auto_partes/auto_partes_transactions.csv')
print(f"Loaded {len(df)} rows")
```

### Test 4-Case Logic Only

```python
import pandas as pd
import numpy as np
from src_new.features.detector import FeatureTypeDetector
from src_new.execution.calculator import FeatureCalculator
from src_new.execution.groupby import GroupByProcessor

# Create test data
data = pd.DataFrame({
    'product': ['A', 'A', 'B', 'B'],
    'price': [100, 150, 200, 250]
})

# Test Case 1: Standard filter
def price_doubled(price):
    return price * 2

# Test Case 3: Aggregation attribute
def total_price(price):
    return np.sum(price)

# Setup and execute
# ... (see test_refactored_code.py for full example)
```

### Test Export Only

```python
from src_new.core.context import GabedaContext
from src_new.export.excel import ExcelExporter
import pandas as pd

# Create context with data
ctx = GabedaContext({})
ctx.set_dataset('test_data', pd.DataFrame({'col': [1, 2, 3]}))

# Add model output
output = {
    'filters': pd.DataFrame({'filter_col': [1, 2]}),
    'attrs': pd.DataFrame({'attr_col': [10, 20]}),
    'input_dataset_name': 'test_data'
}
ctx.set_model_output('my_model', output)

# Export
exporter = ExcelExporter(ctx)
exporter.export_model('my_model', 'outputs/test.xlsx')
print("✓ Export complete!")
```

---

## Validation Checklist

Before proceeding to Phase 8 migration, verify:

### Functionality
- [ ] Integration test passes all 6 tests
- [ ] Can load data (CSV, Excel, DataFrame)
- [ ] Can validate data
- [ ] Can process schemas
- [ ] Features are analyzed correctly
- [ ] **CRITICAL**: All 4 cases execute correctly
- [ ] Context stores/retrieves data
- [ ] Excel export creates files with correct tabs

### Compatibility
- [ ] Outputs match old implementation exactly
- [ ] No regressions in functionality
- [ ] All existing notebooks work with new imports
- [ ] Excel exports are identical

### Performance (Optional)
- [ ] Execution time similar to old implementation
- [ ] Memory usage acceptable
- [ ] No significant slowdowns

---

## Troubleshooting

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'src_new'`

**Solution**: Make sure you're running from repository root:
```bash
cd /path/to/khujta_ai_business
python test_refactored_code.py
```

### Missing Dependencies

**Error**: `ModuleNotFoundError: No module named 'openpyxl'`

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Test Failures

**Error**: One or more tests fail

**Solution**:
1. Check error message details
2. Review the specific module that failed
3. Check the code in `src_new/` for that module
4. Compare with original implementation in `src/`
5. Check if any critical logic was missed

### Different Results

**Error**: Outputs don't match old implementation

**Solution**:
1. Check if inputs are identical
2. Verify the 4-case logic implementation
3. Check for any differences in:
   - Aggregation keyword detection
   - Flag tracking (in_flg, out_flg, groupby_flg)
   - Decision logic
4. Review `src_new/execution/groupby.py` carefully

---

## Next Steps After Testing

### If All Tests Pass ✅

Proceed to **Phase 8: Migration**
1. Backup your code (git commit)
2. Follow instructions in `ai/plan/REFACTORING_PROGRESS.md` Phase 8
3. Rename directories: `src/` → `src_old/`, `src_new/` → `src/`
4. Update all imports
5. Verify one more time
6. Remove `src_old/`

### If Tests Fail ❌

1. **Review error messages** carefully
2. **Check the failing module** in `src_new/`
3. **Compare with original** in `src/`
4. **Fix the issue** in `src_new/`
5. **Re-run tests**
6. **Repeat until all pass**

---

## Questions?

Refer to:
- **`ai/plan/REFACTORING_COMPLETE.md`** - Complete refactoring summary
- **`ai/plan/REFACTORING_PROGRESS.md`** - Detailed progress and instructions
- **`ai/plan/00_CRITICAL_CONSTRAINTS.md`** - What must be preserved (4-case logic)

---

**Created**: 2025-01-15
**Purpose**: Guide for Phase 7 integration testing
**Status**: Ready to use
