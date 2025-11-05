# Unit Tests

**Purpose:** Test individual modules in isolation (108 tests)

---

## Run All Unit Tests

```bash
cd test/unit
pytest . -v

# With coverage
pytest . --cov=src --cov-report=html
```

---

## Test Categories

### Core Tests (`core/`)
- `test_cleanup.py` - Context cleanup utilities (4 tests)

**Run:** `pytest core/ -v`

### Features Tests (`features/`)
- `test_feature_store.py` - Feature storage & inheritance (12 tests)
- `test_resolver.py` - Dependency resolution (DFS algorithm) (8 tests)

**Run:** `pytest features/ -v`

### Execution Tests (`execution/`)
- `test_multi_groupby.py` - Multiple groupby columns (6 tests)

**Run:** `pytest execution/ -v`

### Export Tests (`export/`)
- `test_export.py` - Excel export functions (5 tests)

**Run:** `pytest export/ -v`

### Utils Tests (`utils/`)
- `test_dict_utils.py` - Dictionary utilities (25 tests)
- `test_column_utils_simple.py` - Column operations (18 tests)
- `test_external_data_simple.py` - External data loading (8 tests)
- `test_file_utils_simple.py` - File operations (12 tests)
- `test_log_utils_simple.py` - Logging utilities (15 tests)
- `test_results_simple.py` - Results processing (10 tests)

**Run:** `pytest utils/ -v`

**Direct execution (no pytest):**
```bash
python utils/test_dict_utils.py
python utils/test_column_utils_simple.py
```

---

## Expected Results

- **Total:** 108 unit tests
- **Coverage:** 85%+ per module
- **All tests should pass**

---

**See also:** [TEST_MANIFEST.md](../../docs/testing/TEST_MANIFEST.md) for complete test catalog
