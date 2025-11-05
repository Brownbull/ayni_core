# Integration Tests

**Purpose:** End-to-end testing of refactored v2.0 architecture (6 comprehensive tests)

---

## Run All Integration Tests

```bash
cd test/integration
pytest test_refactored_architecture.py -v

# Or direct execution (no pytest required)
python test_refactored_architecture.py
```

---

## Tests Included

### Test 1: Basic Imports ✅
Verifies all refactored modules can be imported without errors.

### Test 2: Preprocessing Pipeline ✅
Tests DataLoader, DataValidator, SchemaProcessor

### Test 3: Features Package ✅
Tests FeatureStore, FeatureTypeDetector, FeatureAnalyzer, DependencyResolver

### Test 4: Execution Package (4-Case Logic) ⭐ **CRITICAL**
Tests the most important part:
- Case 1: Standard filter (reads data_in only)
- Case 2: Filter using attributes (reads data_in + agg_results)
- Case 3: Attribute with aggregation
- Case 4: Attribute composition (uses only other attributes)

### Test 5: Context Integration ✅
Tests GabedaContext dataset storage/retrieval

### Test 6: Export Functionality ✅
Tests ExcelExporter with context integration

---

## Expected Output

```
============================================================
TEST SUMMARY
============================================================
✓ PASS - Imports
✓ PASS - Preprocessing
✓ PASS - Features
✓ PASS - Execution (4-Case Logic)
✓ PASS - Context Integration
✓ PASS - Export

Results: 6/6 tests passed
```

---

**See also:** [TEST_MANIFEST.md](../../docs/testing/TEST_MANIFEST.md) for complete test catalog
