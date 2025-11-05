# Notebook Tests

**Purpose:** Validate notebook execution and outputs (14 tests)

---

## Run Notebook Tests

```bash
cd test/notebooks
pytest . -v
```

---

## Test Files

### Notebook Execution Tests
- `test_feature_notebook.py` - Feature notebook validation
- `test_refactored_notebook.py` - Refactored notebook execution
- `test_quickstart_refactored.py` - Quickstart basic
- `test_quickstart_with_defaults.py` - Quickstart with defaults

### Context Tests
- `test_reuse_context.py` - Context reuse & persistence
- `test_input_lineage.py` - Input dataset lineage tracking

### Reference Output
- `00_transactions_test_output.ipynb` - Expected notebook output

---

## Key Tests

- **Notebook Execution:**
  - Test feature notebook runs without errors
  - Test refactored notebook produces correct output
  - Test quickstart variations
  - Validate output matches expected

- **Context Reuse:**
  - Test context persistence (save/load)
  - Test context folder reuse pattern
  - Test input lineage tracking
  - Test multiple models in same context

---

## Expected Results

- **Total:** 14 notebook tests
- **All notebooks execute successfully**
- **Outputs match expected**
- **Context reuse works correctly**

---

**See also:** [TEST_MANIFEST.md](../../docs/testing/TEST_MANIFEST.md) for complete test catalog
