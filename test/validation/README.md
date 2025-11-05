# Validation Test Suite

**Purpose:** Comprehensive validation of 69 test cases (100% rule coverage)

---

## Run Validation Suite

```bash
cd test/validation
python test_runner.py
```

---

## Test Coverage

### 69 Test Cases
- Valid Baseline: 7 tests
- transaction_id: 4 tests
- transaction_date: 5 tests
- customer_id: 4 tests
- product_sku: 3 tests
- quantity: 5 tests
- unit_price: 4 tests
- gross_amount: 2 tests
- discount_amount: 5 tests
- net_amount: 2 tests
- tax_amount: 4 tests
- total_amount: 3 tests
- payment_status: 7 tests
- payment_date: 3 tests
- due_date: 3 tests
- Formula validation: 4 tests
- Edge cases: 4 tests

### 11 Validation Rules (100% Coverage)
1. NULL_IN_REQUIRED_FIELD (13 cases)
2. FUTURE_DATE (1 case)
3. DATE_BEFORE_FOUNDING (1 case)
4. NEGATIVE_VALUE (8 cases)
5. BELOW_MINIMUM (8 cases)
6. EXCESSIVE_DISCOUNT (1 case)
7. INVALID_VALUE (1 case)
8. FORMULA_MISMATCH (4 cases)
9. PAYMENT_BEFORE_TRANSACTION (1 case)
10. DUE_DATE_BEFORE_TRANSACTION (1 case)
11. STATUS_DATE_MISMATCH (1 case)

### 14 Columns (100% Coverage)
All transaction columns tested

---

## Expected Output

```
================================================================================
TEST RESULTS SUMMARY
================================================================================

🎯 Overall Results:
   Total tests: 69
   ✅ Passed: 66 (95.7%)
   ❌ Failed: 3 (4.3%)

🔍 Validation Rule Coverage:
   Expected rules: 11
   Triggered rules: 11
   Coverage: 100.0%

📋 Column Coverage:
   Tested columns: 14/14
   Coverage: 100.0%
```

---

## Output Files

- `test_data/test_transactions.csv` - 69 test cases
- `test_data/test_manifest.json` - Test catalog
- `test_data/test_coverage.csv` - Detailed results
- `test_data/test_results.json` - Coverage statistics

---

**See also:** [TEST_MANIFEST.md](../../docs/testing/TEST_MANIFEST.md) for complete test catalog
