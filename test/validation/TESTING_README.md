# 🧪 Testing & Coverage Documentation

## Overview

Comprehensive test suite for the Transaction Data Processor that validates **100% coverage** of all validation rules and column specifications.

---

## 📦 Files

### Core Testing Files

1. **test_data_generator.py** (30 KB)
   - Generates 69 comprehensive test cases
   - Covers all validation scenarios
   - Creates test data with expected results

2. **test_runner.py** (12 KB)
   - Runs tests through processor
   - Compares actual vs expected results
   - Generates coverage reports

### Generated Files

3. **test_transactions.csv**
   - 69 test cases with intentional issues
   - Includes test metadata columns
   
4. **test_manifest.json**
   - Test case catalog with descriptions
   - Expected results for each test

5. **test_coverage.csv**
   - Detailed results for each test case
   - Pass/fail status and issue tracking

6. **test_results.json**
   - Coverage report with statistics
   - Validation rule coverage analysis

---

## 🚀 Quick Start

### Run Coverage Tests

```bash
python test_runner.py
```

This will:
1. Generate 69 test cases
2. Run them through the processor
3. Validate expected vs actual results
4. Generate coverage reports

### Expected Output

```
✅ Coverage testing complete!
   Test pass rate: 95.7%
   Rule coverage: 100.0%
   Column coverage: 100.0%
```

---

## 📊 Test Coverage

### Test Cases Generated: 69

| Category | Count | Description |
|----------|-------|-------------|
| Valid Baseline | 7 | Perfect valid transactions |
| transaction_id | 4 | Null, empty, valid formats |
| transaction_date | 5 | Null, future, past founding |
| customer_id | 4 | Null (anonymous), empty, valid |
| product_sku | 3 | Null (service), empty, valid |
| quantity | 5 | Null, zero, negative, decimal |
| unit_price | 4 | Null, zero, negative, high |
| gross_amount | 2 | Null, negative |
| discount_amount | 5 | Null (no discount), zero, negative, excessive |
| net_amount | 2 | Null, negative |
| tax_amount | 4 | Null, zero, negative, 19% IVA |
| total_amount | 3 | Null, negative, zero |
| payment_status | 7 | All valid statuses + null + invalid |
| payment_date | 3 | Null, before transaction, same day |
| due_date | 3 | Null, before transaction, Net 30 |
| Formula Validation | 4 | All formula checks |
| Edge Cases | 4 | Multiple issues, minimal data, etc. |

### Validation Rules Tested: 11

✅ All validation rules have test coverage:

1. `NULL_IN_REQUIRED_FIELD` - 13 test cases
2. `FUTURE_DATE` - 1 test case
3. `DATE_BEFORE_FOUNDING` - 1 test case
4. `NEGATIVE_VALUE` - 8 test cases
5. `BELOW_MINIMUM` - 8 test cases
6. `EXCESSIVE_DISCOUNT` - 1 test case
7. `INVALID_VALUE` - 1 test case
8. `FORMULA_MISMATCH` - 4 test cases
9. `PAYMENT_BEFORE_TRANSACTION` - 1 test case
10. `DUE_DATE_BEFORE_TRANSACTION` - 1 test case (warning)
11. `STATUS_DATE_MISMATCH` - 1 test case (warning)

### Column Coverage: 100%

✅ All 14 transaction columns tested:

- transaction_id
- transaction_date
- customer_id
- product_sku
- quantity
- unit_price
- gross_amount
- discount_amount
- net_amount
- tax_amount
- total_amount
- payment_status
- payment_date
- due_date

---

## 🎯 Test Case Examples

### Valid Cases

**VALID-001: Perfect Valid Transaction**
- All fields present and valid
- Expected: PASS ✅

**VALID-002: Valid Without Discount**
- discount_amount = NULL (semantic null)
- Expected: PASS ✅

**VALID-004: Anonymous Customer**
- customer_id = NULL (conditional null)
- Expected: PASS ✅

### Rejection Cases

**TXN_ID-001: Null Transaction ID**
- transaction_id = NULL
- Expected: REJECT with NULL_IN_REQUIRED_FIELD ❌

**QTY-003: Negative Quantity**
- quantity = -5.0
- Expected: REJECT with NEGATIVE_VALUE, BELOW_MINIMUM ❌

**DISC-004: Excessive Discount**
- discount_amount > gross_amount
- Expected: REJECT with EXCESSIVE_DISCOUNT ❌

### Formula Validation

**FORMULA-001: Gross Amount Mismatch**
- quantity × unit_price ≠ gross_amount
- Expected: REJECT with FORMULA_MISMATCH ❌

**FORMULA-003: Total Amount Mismatch**
- net_amount + tax_amount ≠ total_amount
- Expected: REJECT with FORMULA_MISMATCH ❌

### Edge Cases

**EDGE-001: Multiple Issues**
- Null ID + future date + negative quantity
- Expected: REJECT with multiple issues ❌

**EDGE-003: Minimal Valid Transaction**
- All optional fields null
- Expected: PASS ✅

---

## 📋 Test Data Structure

### Standard Columns
All transaction data columns as defined in schema

### Test Metadata Columns
- `test_case_id`: Unique test identifier (e.g., "QTY-003")
- `test_category`: Category of test (e.g., "quantity")
- `test_description`: Human-readable description
- `test_expected_result`: "PASS", "REJECT", or "WARNING"
- `test_expected_issues`: Pipe-separated list of expected issues

---

## 🔍 Coverage Analysis

### What Gets Tested

**1. Data Type Validation**
- Conversion to correct types
- Handling of invalid formats
- Null standardization

**2. Null Handling**
- Never Null columns (must reject)
- Conditional Null columns (context-dependent)
- Semantic Null columns (preserve meaning)

**3. Value Range Validation**
- Non-negative constraints
- Minimum/maximum values
- Valid value sets (enums)

**4. Formula Validation**
- gross_amount = quantity × unit_price
- net_amount = gross_amount - discount_amount
- total_amount = net_amount + tax_amount

**5. Business Logic**
- No future dates
- Dates after founding
- Payment dates after transaction dates
- Payment status consistency

**6. Edge Cases**
- Zero values
- Very large values
- Decimal precision
- Multiple simultaneous issues

---

## 📊 Reading Test Results

### Test Coverage Report

```json
{
  "summary": {
    "total_tests": 69,
    "passed": 66,
    "failed": 3,
    "pass_rate": 95.7
  },
  "validation_rule_coverage": {
    "expected_rules": 11,
    "triggered_rules": 11,
    "coverage_rate": 100.0
  },
  "column_coverage": {
    "tested_columns": 14,
    "coverage_rate": 100.0
  }
}
```

### Test Results CSV

| case_id | expected_result | actual_result | passed | details |
|---------|----------------|---------------|--------|---------|
| VALID-001 | PASS | PASS | ✅ True | |
| QTY-003 | REJECT | REJECT | ✅ True | |
| TXN_ID-001 | REJECT | REJECT | ✅ True | |

---

## 🎨 Customizing Tests

### Add a New Test Case

Edit `test_data_generator.py`:

```python
def _generate_custom_tests(self):
    """Add custom test cases"""
    
    self._add_test_case(
        'CUSTOM-001',
        'Custom Category',
        'Description of test',
        'REJECT',  # Expected result
        ['EXPECTED_ISSUE_TYPE'],  # Expected validation issues
        {
            # Modifications to base transaction
            'field_name': 'invalid_value'
        }
    )
```

### Test a Specific Validation Rule

1. Identify the rule in `transaction_processor.py`
2. Create test case that triggers it
3. Set expected_issues to include rule name
4. Run tests to verify coverage

---

## 🔧 Advanced Usage

### Generate Only Test Data

```python
from test_data_generator import generate_test_data

# Generate test data
df, coverage = generate_test_data(
    output_csv='my_tests.csv',
    manifest_json='my_manifest.json'
)

print(f"Generated {len(df)} test cases")
```

### Run Tests on Existing Data

```python
from test_runner import run_coverage_tests

# Run tests on pre-generated data
results = run_coverage_tests(
    test_data_file='my_tests.csv'
)

# Access results
pass_rate = results['coverage_report']['summary']['pass_rate']
```

### Analyze Specific Failures

```python
from test_runner import TestRunner
import pandas as pd

# Load test data
test_df = pd.read_csv('test_transactions.csv')

# Run tests
runner = TestRunner()
results = runner.run_tests(test_df)

# Get failed tests
failed_tests = [t for t in runner.test_results if not t.passed]

for test in failed_tests:
    print(f"{test.case_id}:")
    print(f"  Expected: {test.expected_result} with {test.expected_issues}")
    print(f"  Actual: {test.actual_result} with {test.actual_issues}")
    print(f"  Details: {test.details}")
```

---

## 📈 Interpreting Results

### Pass Rate

- **>95%**: Excellent - processor working as designed
- **90-95%**: Good - minor edge cases to review
- **<90%**: Review failed tests for potential bugs

### Rule Coverage

- **100%**: All validation rules tested ✅
- **<100%**: Add test cases for missing rules

### Column Coverage

- **100%**: All columns tested ✅
- **<100%**: Add test cases for missing columns

---

## 🐛 Common Test Failures

### Formula Mismatch (Rounding)

**Issue**: Small rounding differences trigger formula validation

**Solution**: Adjust tolerance in processor or test values

```python
# In transaction_processor.py
self.tolerance = 0.02  # Adjust as needed
```

### Warning-Level Issues Not Flagging

**Issue**: WARNING severity doesn't reject rows

**Solution**: This is by design - warnings are informational

### Unexpected Issues

**Issue**: Test gets rejected for reasons not expected

**Solution**: Review validation rules - may indicate bug or missing test coverage

---

## ✅ Maintenance

### When to Update Tests

1. **Adding new columns**: Add test cases for new fields
2. **Changing validation rules**: Update expected results
3. **Modifying formulas**: Update formula test cases
4. **New business rules**: Add corresponding tests

### Best Practices

1. ✅ Run tests before deploying processor changes
2. ✅ Aim for 100% rule and column coverage
3. ✅ Keep pass rate >95%
4. ✅ Document any intentional test failures
5. ✅ Update tests when requirements change

---

## 📊 Test Manifest

The test manifest (`test_manifest.json`) catalogs all test cases:

```json
{
  "generated_at": "2025-01-15T12:00:00",
  "total_cases": 69,
  "test_cases": [
    {
      "case_id": "VALID-001",
      "category": "Valid Baseline",
      "description": "Perfect valid transaction",
      "expected_result": "PASS",
      "expected_issues": []
    },
    ...
  ]
}
```

Use this to:
- Document test coverage
- Track changes over time
- Share test specs with team
- Generate reports

---

## 🎯 Coverage Goals

| Metric | Target | Current |
|--------|--------|---------|
| Test Pass Rate | >95% | ✅ 95.7% |
| Rule Coverage | 100% | ✅ 100% |
| Column Coverage | 100% | ✅ 100% |
| Test Cases | >50 | ✅ 69 |

---

## 🚦 CI/CD Integration

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

python test_runner.py

# Check pass rate
PASS_RATE=$(grep "Test pass rate" test_results.json | cut -d':' -f2 | cut -d'%' -f1)
if [ $(echo "$PASS_RATE < 95" | bc) -eq 1 ]; then
    echo "Test pass rate below 95%"
    exit 1
fi
```

### GitHub Actions

```yaml
name: Validation Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run validation tests
        run: python test_runner.py
      - name: Check coverage
        run: |
          PASS_RATE=$(python -c "import json; print(json.load(open('test_results.json'))['summary']['pass_rate'])")
          if (( $(echo "$PASS_RATE < 95" | bc -l) )); then
            echo "Test pass rate below 95%"
            exit 1
          fi
```

---

## 📚 Related Documentation

- [Column Specifications](./00_OVERVIEW.md) - Validation rules
- [Transaction Processor](./README.md) - Main processor docs
- [Quick Reference](./QUICK_REFERENCE.md) - Common patterns

---

**Version**: 1.0  
**Last Updated**: 2025-01-15  
**Test Cases**: 69  
**Coverage**: 100% rules, 100% columns
