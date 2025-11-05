"""
Generate "Lucky" Test Cases - Minimal Input, Maximum Inference

This script identifies and generates test cases where a MINIMAL set of input columns
can be used to INFER the MAXIMUM number of additional columns using the inference
functions defined in the system.

"Lucky" cases are scenarios where the customer provides just enough data that we can
calculate many derived columns automatically.

Based on base_case.csv inference relationships:
- Required columns: in_dt, in_trans_id, in_product_id, in_quantity, in_price_total
- Inferable columns: in_cost_unit, in_cost_total, in_price_unit, in_discount_total,
                     in_commission_total, in_margin
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Define inference rules: what columns can be calculated from what inputs
INFERENCE_RULES = {
    # Basic calculations
    'in_price_unit': ['in_price_total', 'in_quantity'],
    'in_cost_unit': ['in_cost_total', 'in_quantity'],
    'in_cost_total': ['in_cost_unit', 'in_quantity'],

    # Margin calculations (multiple paths)
    'in_margin': [
        ['in_price_total', 'in_cost_total'],  # Simple margin
        ['in_price_unit', 'in_cost_unit', 'in_quantity'],  # From units
        ['in_price_total', 'in_cost_total', 'in_discount_total', 'in_commission_total'],  # Full
    ],

    # Discount (requires additional rate column not in base case)
    'in_discount_total': [
        ['in_price_unit', 'in_quantity', 'in_price_total'],  # From gross/net difference
    ],

    # Commission (requires rate column not in base case)
    'in_commission_total': [
        ['in_price_total'],  # Needs commission_rate (not standard)
    ],
}


def load_base_case(filepath: str) -> Tuple[List[str], List[str], Dict[str, str]]:
    """Load base_case.csv and parse column metadata"""
    df = pd.read_csv(filepath)

    required_cols = []
    inferable_cols = []
    values = {}

    for _, row in df.iterrows():
        if pd.notna(row['col']) and row['col'] != 'case base':
            col_name = row['col']
            values[col_name] = row['case base']

            # Check if required (optional=0)
            if int(row['optional']) == 0:
                required_cols.append(col_name)

            # Check if inferable (inferable=1)
            if int(row['inferable']) == 1:
                inferable_cols.append(col_name)

    return required_cols, inferable_cols, values


def can_infer_column(target_col: str, available_cols: Set[str]) -> bool:
    """Check if a column can be inferred from available columns"""
    if target_col not in INFERENCE_RULES:
        return False

    rules = INFERENCE_RULES[target_col]

    # If rules is a list of lists (multiple inference paths)
    if isinstance(rules[0], list):
        # Check if ANY path is satisfied
        for rule_set in rules:
            if all(col in available_cols for col in rule_set):
                return True
        return False
    else:
        # Single rule set
        return all(col in available_cols for col in rules)


def get_inferable_columns(available_cols: Set[str], max_iterations: int = 10) -> Set[str]:
    """
    Recursively determine all columns that can be inferred from available columns.

    Args:
        available_cols: Set of columns already available
        max_iterations: Maximum inference iterations to prevent infinite loops

    Returns:
        Set of all columns that can be inferred (including transitively)
    """
    inferable = set()
    current_available = available_cols.copy()

    for _ in range(max_iterations):
        newly_inferable = set()

        for target_col in INFERENCE_RULES.keys():
            if target_col in current_available or target_col in inferable:
                continue

            if can_infer_column(target_col, current_available):
                newly_inferable.add(target_col)

        if not newly_inferable:
            break

        inferable.update(newly_inferable)
        current_available.update(newly_inferable)

    return inferable


def generate_lucky_cases(required_cols: List[str], inferable_cols: List[str], values: Dict[str, str]):
    """Generate lucky test cases with maximum inference potential"""

    lucky_cases = []

    # =========================================================================
    # LUCKY CASE 1: Required + in_cost_total → Infer: price_unit, cost_unit, margin
    # =========================================================================
    case1_cols = required_cols + ['in_cost_total']
    case1_inferable = get_inferable_columns(set(case1_cols))

    lucky_cases.append({
        'name': 'lucky_01_cost_total',
        'description': 'Minimal with cost_total - can infer price_unit, cost_unit, margin',
        'columns': case1_cols,
        'can_infer': sorted(case1_inferable),
        'inference_count': len(case1_inferable)
    })

    # =========================================================================
    # LUCKY CASE 2: Required + in_cost_unit → Infer: price_unit, cost_total, margin
    # =========================================================================
    case2_cols = required_cols + ['in_cost_unit']
    case2_inferable = get_inferable_columns(set(case2_cols))

    lucky_cases.append({
        'name': 'lucky_02_cost_unit',
        'description': 'Minimal with cost_unit - can infer price_unit, cost_total, margin',
        'columns': case2_cols,
        'can_infer': sorted(case2_inferable),
        'inference_count': len(case2_inferable)
    })

    # =========================================================================
    # LUCKY CASE 3: Required + in_price_unit → Infer: Nothing extra (price_total already required)
    # =========================================================================
    case3_cols = required_cols + ['in_price_unit']
    case3_inferable = get_inferable_columns(set(case3_cols))

    lucky_cases.append({
        'name': 'lucky_03_price_unit',
        'description': 'Has price_unit (redundant with price_total) - limited inference',
        'columns': case3_cols,
        'can_infer': sorted(case3_inferable),
        'inference_count': len(case3_inferable)
    })

    # =========================================================================
    # LUCKY CASE 4: Required + cost_total + discount_total → More complete margin
    # =========================================================================
    case4_cols = required_cols + ['in_cost_total', 'in_discount_total']
    case4_inferable = get_inferable_columns(set(case4_cols))

    lucky_cases.append({
        'name': 'lucky_04_cost_discount',
        'description': 'With cost_total and discount - can calculate net margin',
        'columns': case4_cols,
        'can_infer': sorted(case4_inferable),
        'inference_count': len(case4_inferable)
    })

    # =========================================================================
    # LUCKY CASE 5: Required + cost_total + commission_total → Margin with commission
    # =========================================================================
    case5_cols = required_cols + ['in_cost_total', 'in_commission_total']
    case5_inferable = get_inferable_columns(set(case5_cols))

    lucky_cases.append({
        'name': 'lucky_05_cost_commission',
        'description': 'With cost_total and commission - can calculate margin with commission',
        'columns': case5_cols,
        'can_infer': sorted(case5_inferable),
        'inference_count': len(case5_inferable)
    })

    # =========================================================================
    # LUCKY CASE 6: Required + cost_total + discount + commission → FULL margin
    # =========================================================================
    case6_cols = required_cols + ['in_cost_total', 'in_discount_total', 'in_commission_total']
    case6_inferable = get_inferable_columns(set(case6_cols))

    lucky_cases.append({
        'name': 'lucky_06_full_margin',
        'description': 'Complete margin calculation - price, cost, discount, commission',
        'columns': case6_cols,
        'can_infer': sorted(case6_inferable),
        'inference_count': len(case6_inferable)
    })

    # =========================================================================
    # LUCKY CASE 7: Required + price_unit + cost_unit → Dual unit prices
    # =========================================================================
    case7_cols = required_cols + ['in_price_unit', 'in_cost_unit']
    case7_inferable = get_inferable_columns(set(case7_cols))

    lucky_cases.append({
        'name': 'lucky_07_dual_units',
        'description': 'Both unit prices - can calculate totals and margin',
        'columns': case7_cols,
        'can_infer': sorted(case7_inferable),
        'inference_count': len(case7_inferable)
    })

    return lucky_cases


def generate_csv_files(base_path: Path, lucky_cases: List[Dict], values: Dict[str, str]):
    """Generate CSV files for each lucky case"""

    output_dir = base_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating {len(lucky_cases)} lucky test case files...\n")

    for case in lucky_cases:
        # Create single-row dataframe with selected columns
        data = {col: [values[col]] for col in case['columns']}
        df = pd.DataFrame(data)

        # Generate filename
        filename = f"{case['name']}.csv"
        filepath = output_dir / filename

        # Save to CSV
        df.to_csv(filepath, index=False)

        # Print summary
        print(f"[OK] {filename}")
        print(f"     {case['description']}")
        print(f"     Input columns ({len(case['columns'])}): {', '.join(case['columns'])}")
        print(f"     Can infer ({case['inference_count']}): {', '.join(case['can_infer']) if case['can_infer'] else 'None'}")
        print()

    # Generate summary file
    summary_file = output_dir / "lucky_test_cases_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("Lucky Test Cases Summary\n")
        f.write("=" * 80 + "\n\n")
        f.write("These test cases demonstrate MINIMAL input with MAXIMUM inference potential.\n\n")

        for case in lucky_cases:
            f.write(f"{case['name']}.csv\n")
            f.write(f"  Description: {case['description']}\n")
            f.write(f"  Input columns ({len(case['columns'])}): {', '.join(case['columns'])}\n")
            f.write(f"  Can infer ({case['inference_count']}): {', '.join(case['can_infer']) if case['can_infer'] else 'None'}\n")
            f.write(f"\n")

    print(f"[OK] Generated {len(lucky_cases)} lucky test case files")
    print(f"[OK] Summary written to {summary_file}")


def main():
    # Path to base_case.csv
    base_path = Path(__file__).parent / "base_case.csv"

    if not base_path.exists():
        print(f"Error: base_case.csv not found at {base_path}")
        return

    print("Loading base_case.csv...")
    required_cols, inferable_cols, values = load_base_case(base_path)

    print(f"Found {len(required_cols)} required columns: {', '.join(required_cols)}")
    print(f"Found {len(inferable_cols)} inferable columns: {', '.join(inferable_cols)}")
    print()

    print("Analyzing lucky cases (minimal input, maximum inference)...\n")
    lucky_cases = generate_lucky_cases(required_cols, inferable_cols, values)

    # Sort by inference count (descending)
    lucky_cases.sort(key=lambda x: x['inference_count'], reverse=True)

    # Generate CSV files
    generate_csv_files(base_path, lucky_cases, values)

    # Print ranking
    print("\n" + "=" * 80)
    print("LUCKY CASE RANKING (by inference potential):")
    print("=" * 80)
    for i, case in enumerate(lucky_cases, 1):
        print(f"{i}. {case['name']}: {case['inference_count']} inferable columns")
        print(f"   {case['description']}")
    print()


if __name__ == "__main__":
    main()
