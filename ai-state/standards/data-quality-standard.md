# Data Quality Standard

**Version:** 1.0.0
**Purpose:** Quality standard for data pipelines, ETL processes, and analytics

---

## Overview

This standard defines **6 dimensions of data quality** that must be measured and maintained. Minimum passing score: **95%** for production data.

---

## Data Quality Dimensions

### 1. Completeness (Weight: 20%)

**Definition:** All required data is present without gaps.

| Score | Description |
|-------|-------------|
| **100%** | No missing required fields |
| **95-99%** | Rare missing values, documented |
| **90-94%** | Some missing values, within tolerance |
| **80-89%** | Significant gaps, needs attention |
| **<80%** | Unacceptable data loss |

**Checks:**
- [ ] Required fields populated
- [ ] No unexpected NULL values
- [ ] Record counts match source
- [ ] Date ranges complete
- [ ] No dropped records

---

### 2. Accuracy (Weight: 20%)

**Definition:** Data correctly represents real-world values.

| Score | Description |
|-------|-------------|
| **100%** | All values accurate |
| **95-99%** | Minor discrepancies |
| **90-94%** | Some inaccuracies |
| **80-89%** | Notable errors |
| **<80%** | Unreliable data |

**Checks:**
- [ ] Values within expected ranges
- [ ] Calculations verified
- [ ] Cross-source validation
- [ ] Business rules satisfied
- [ ] Statistical distributions normal

---

### 3. Consistency (Weight: 20%)

**Definition:** Data is uniform across all systems and datasets.

| Score | Description |
|-------|-------------|
| **100%** | Perfect consistency |
| **95-99%** | Minor variations |
| **90-94%** | Some inconsistencies |
| **80-89%** | Notable conflicts |
| **<80%** | Major inconsistencies |

**Checks:**
- [ ] Format standardization
- [ ] Referential integrity
- [ ] Cross-system alignment
- [ ] Naming conventions
- [ ] Unit consistency

---

### 4. Timeliness (Weight: 15%)

**Definition:** Data is available when needed and reflects current state.

| Score | Description |
|-------|-------------|
| **100%** | Real-time or within SLA |
| **95-99%** | Minor delays |
| **90-94%** | Acceptable delays |
| **80-89%** | Significant delays |
| **<80%** | Stale data |

**Checks:**
- [ ] Update frequency met
- [ ] Processing within SLA
- [ ] Timestamp accuracy
- [ ] No stale records
- [ ] Refresh schedule maintained

---

### 5. Uniqueness (Weight: 15%)

**Definition:** No unwanted duplicate records exist.

| Score | Description |
|-------|-------------|
| **100%** | No duplicates |
| **95-99%** | Rare duplicates |
| **90-94%** | Some duplicates |
| **80-89%** | Notable duplicates |
| **<80%** | Excessive duplicates |

**Checks:**
- [ ] Primary key uniqueness
- [ ] No duplicate transactions
- [ ] Deduplication rules applied
- [ ] Merge logic correct
- [ ] Identity resolution

---

### 6. Validity (Weight: 10%)

**Definition:** Data conforms to defined formats and types.

| Score | Description |
|-------|-------------|
| **100%** | All data valid |
| **95-99%** | Minor format issues |
| **90-94%** | Some invalid data |
| **80-89%** | Notable format problems |
| **<80%** | Major validity issues |

**Checks:**
- [ ] Data type compliance
- [ ] Format patterns matched
- [ ] Enum values valid
- [ ] Date formats correct
- [ ] Encoding consistent

---

## Quality Score Calculation

```python
quality_score = (
    completeness * 0.20 +
    accuracy * 0.20 +
    consistency * 0.20 +
    timeliness * 0.15 +
    uniqueness * 0.15 +
    validity * 0.10
)
```

### Thresholds
- **95-100%:** Production ready ✅
- **90-94%:** Acceptable with monitoring 🟡
- **<90%:** Requires remediation ❌

---

## Data Validation Rules

### Input Validation
```python
def validate_input(data):
    checks = {
        'schema': validate_schema(data),
        'types': validate_types(data),
        'ranges': validate_ranges(data),
        'required': validate_required(data),
        'formats': validate_formats(data)
    }
    return all(checks.values())
```

### Business Rules
```python
def validate_business_rules(data):
    rules = [
        revenue >= 0,
        quantity > 0,
        date <= today(),
        customer_id.exists(),
        product_id.valid()
    ]
    return all(rules)
```

---

## Monitoring & Alerting

### Quality Metrics
- Record count variations
- NULL percentage trends
- Duplicate rate changes
- Processing time increases
- Error rate spikes

### Alert Thresholds
- **Critical:** Quality < 90%
- **Warning:** Quality < 95%
- **Info:** Anomaly detected

---

## Quality Improvement Process

1. **Measure** - Calculate quality scores
2. **Identify** - Find root causes
3. **Fix** - Implement corrections
4. **Prevent** - Add validations
5. **Monitor** - Track improvements

---

## Evaluation Template

```markdown
# Data Quality Report

**Pipeline:** [Name]
**Date:** [YYYY-MM-DD]
**Records:** [Count]

## Quality Scores

| Dimension | Score | Issues |
|-----------|-------|--------|
| Completeness | X% | |
| Accuracy | X% | |
| Consistency | X% | |
| Timeliness | X% | |
| Uniqueness | X% | |
| Validity | X% | |

**Overall: X%** [PASS/REVIEW/FAIL]

## Issues Found
- [ ] Issue 1...
- [ ] Issue 2...

## Recommendations
- Action 1...
- Action 2...
```