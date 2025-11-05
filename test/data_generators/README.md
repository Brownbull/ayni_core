# Test Data Generators

**Purpose:** Generate synthetic test data for validation

---

## Generator Scripts

### generate_test_transactions.py
Generates raw transaction data

**Output:** `data/tests/transactions/`

```bash
python generate_test_transactions.py
```

### generate_test_cases.py
Generates synthetic test cases

**Output:** `data/tests/synthetic/`

```bash
python generate_test_cases.py
```

### generate_key_test_cases.py
Generates key edge case datasets

**Output:** `data/tests/synthetic/`

```bash
python generate_key_test_cases.py
```

### generate_lucky_test_cases.py
Generates lucky number test data

**Output:** `data/tests/synthetic/`

```bash
python generate_lucky_test_cases.py
```

---

## Run All Generators

```bash
cd test/data_generators

python generate_test_transactions.py
python generate_test_cases.py
python generate_key_test_cases.py
python generate_lucky_test_cases.py
```

---

## Output Locations

- **Raw data:** `data/tests/transactions/`
- **Synthetic data:** `data/tests/synthetic/`

---

**See also:** [TEST_MANIFEST.md](../../docs/testing/TEST_MANIFEST.md) for complete test catalog
