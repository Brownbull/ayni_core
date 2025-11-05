# GabeDA Test Suite

**Complete test suite for the GabeDA Business Intelligence System**

📋 **For complete test catalog, see [TEST_MANIFEST.md](../docs/testing/TEST_MANIFEST.md)**

---

## Quick Start

```bash
# Run all tests
pytest test/ -v

# Run with coverage
pytest test/ --cov=src --cov-report=html

# Run specific category
cd test/integration && pytest -v
cd test/unit && pytest -v
cd test/validation && python test_runner.py
cd test/notebooks && pytest -v
```

---

## Test Organization

### 📁 test/integration/ (6 tests)
End-to-end tests of the refactored v2.0 architecture

**Run:** `cd integration && pytest -v`

**Key Tests:**
- Basic imports
- Preprocessing pipeline
- Features package
- **Execution package (4-case logic)** ⭐ CRITICAL
- Context integration
- Export functionality

### 📁 test/unit/ (108 tests)
Module-level unit tests organized by package

**Run:** `cd unit && pytest -v`

**Categories:**
- `core/` - Core utilities (4 tests)
- `features/` - Feature store & resolver (20 tests)
- `execution/` - Execution engine (6 tests)
- `export/` - Excel export (5 tests)
- `utils/` - Utility functions (88 tests)

### 📁 test/validation/ (69 test cases)
Comprehensive data validation suite

**Run:** `cd validation && python test_runner.py`

**Coverage:**
- 11 validation rules (100%)
- 14 columns (100%)
- 95.7% pass rate target

### 📁 test/notebooks/ (14 tests)
Notebook execution and context tests

**Run:** `cd notebooks && pytest -v`

**Tests:**
- Notebook execution validation
- Context reuse & persistence
- Input lineage tracking

### 📁 test/data_generators/
Test data generation scripts

**Run:** `cd data_generators && python generate_*.py`

**Outputs:** `data/tests/transactions/` and `data/tests/synthetic/`

---

## Test Statistics

- **Total Tests:** 197
- **Code Coverage:** 85%
- **Validation Coverage:** 100%

See [TEST_MANIFEST.md](../docs/testing/TEST_MANIFEST.md) for detailed breakdown.

---

## Adding New Tests

1. Create test file in appropriate category
2. Write tests following pytest conventions
3. **Add entry to [TEST_MANIFEST.md](../docs/testing/TEST_MANIFEST.md)**
4. Update test statistics
5. Run tests to verify
6. Commit with message: `test: add [test_name]`

---

## Documentation

- **[TEST_MANIFEST.md](../docs/testing/TEST_MANIFEST.md)** - Complete test catalog (LIVING DOCUMENT)
- **[TESTING.md](../docs/guides/TESTING.md)** - Comprehensive testing guide
- **Category READMEs** - See each subfolder for specific instructions

---

**Last Updated:** 2025-10-22
