"""
Generate KEY test case CSV files from base_case.csv

This script generates a curated set of important test cases rather than all possible combinations.
It focuses on realistic scenarios that are likely to occur in practice.

Test scenarios generated:
1. Minimal required columns only
2. All columns present (complete dataset)
3. Required + common optional columns (typical case)
4. Missing inferable columns (to test inference logic)
5. Edge cases (specific optional column combinations)
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict

def load_base_case(filepath: str):
    """Load base_case.csv and parse column metadata"""
    df = pd.read_csv(filepath)

    required_cols = []
    optional_cols = []
    inferable_cols = []
    values = {}

    for _, row in df.iterrows():
        if pd.notna(row['col']) and row['col'] != 'case base':
            col_name = row['col']
            values[col_name] = row['case base']

            if int(row['optional']) == 0:
                required_cols.append(col_name)
            else:
                optional_cols.append(col_name)

            if int(row['inferable']) == 1:
                inferable_cols.append(col_name)

    return required_cols, optional_cols, inferable_cols, values


def create_test_case(output_dir: Path, case_name: str, columns: List[str], values: Dict[str, str], description: str):
    """Create a single test case CSV file"""
    data = {col: [values[col]] for col in columns}
    df = pd.DataFrame(data)

    filename = f"{case_name}.csv"
    filepath = output_dir / filename

    df.to_csv(filepath, index=False)
    print(f"[OK] {filename} - {description}")
    print(f"     Columns ({len(columns)}): {', '.join(columns)}\n")

    return filename, columns, description


def main():
    # Path to base_case.csv
    base_path = Path(__file__).parent / "base_case.csv"

    if not base_path.exists():
        print(f"Error: base_case.csv not found at {base_path}")
        return

    print("Loading base_case.csv...\n")
    required_cols, optional_cols, inferable_cols, values = load_base_case(base_path)

    print(f"Column Summary:")
    print(f"  Required: {len(required_cols)} - {', '.join(required_cols)}")
    print(f"  Optional: {len(optional_cols)} - {', '.join(optional_cols)}")
    print(f"  Inferable: {len(inferable_cols)} - {', '.join(inferable_cols)}")
    print(f"\nGenerating key test cases...\n")

    output_dir = base_path.parent
    test_cases = []

    # Test Case 1: Minimal - Required columns only
    test_cases.append(create_test_case(
        output_dir,
        "tc_01_minimal_required",
        required_cols,
        values,
        "Minimal case - only required columns"
    ))

    # Test Case 2: Complete - All columns
    all_cols = required_cols + optional_cols
    test_cases.append(create_test_case(
        output_dir,
        "tc_02_complete_all",
        all_cols,
        values,
        "Complete case - all columns present"
    ))

    # Test Case 3: Typical - Required + quantity column
    typical_cols = required_cols.copy()
    if 'in_quantity' in optional_cols:
        typical_cols.append('in_quantity')
    test_cases.append(create_test_case(
        output_dir,
        "tc_03_typical_with_quantity",
        typical_cols,
        values,
        "Typical case - required + quantity"
    ))

    # Test Case 4: Pricing info - Required + price columns
    pricing_cols = required_cols.copy()
    for col in ['in_price_unit', 'in_price_total', 'in_quantity']:
        if col in optional_cols or col in required_cols:
            if col not in pricing_cols:
                pricing_cols.append(col)
    test_cases.append(create_test_case(
        output_dir,
        "tc_04_with_pricing",
        pricing_cols,
        values,
        "Pricing case - includes price information"
    ))

    # Test Case 5: Costing info - Required + cost columns
    costing_cols = required_cols.copy()
    for col in ['in_cost_unit', 'in_cost_total', 'in_quantity']:
        if col in optional_cols or col in required_cols:
            if col not in costing_cols:
                costing_cols.append(col)
    test_cases.append(create_test_case(
        output_dir,
        "tc_05_with_costing",
        costing_cols,
        values,
        "Costing case - includes cost information"
    ))

    # Test Case 6: Full financial - Required + all financial columns
    financial_cols = required_cols.copy()
    for col in ['in_quantity', 'in_cost_unit', 'in_cost_total', 'in_price_unit',
                'in_price_total', 'in_discount_total', 'in_commission_total', 'in_margin']:
        if col in optional_cols or col in required_cols:
            if col not in financial_cols:
                financial_cols.append(col)
    test_cases.append(create_test_case(
        output_dir,
        "tc_06_full_financial",
        financial_cols,
        values,
        "Full financial case - all monetary columns"
    ))

    # Test Case 7: Missing inferable (unit prices) - Has totals and quantity, missing units
    missing_units_cols = required_cols.copy()
    for col in ['in_quantity', 'in_cost_total', 'in_price_total']:
        if col in optional_cols or col in required_cols:
            if col not in missing_units_cols:
                missing_units_cols.append(col)
    test_cases.append(create_test_case(
        output_dir,
        "tc_07_infer_unit_prices",
        missing_units_cols,
        values,
        "Inference test - has totals, missing unit prices (inferable)"
    ))

    # Test Case 8: Missing inferable (totals) - Has units and quantity, missing totals
    missing_totals_cols = required_cols.copy()
    for col in ['in_quantity', 'in_cost_unit', 'in_price_unit']:
        if col in optional_cols or col in required_cols:
            if col not in missing_totals_cols:
                missing_totals_cols.append(col)
    test_cases.append(create_test_case(
        output_dir,
        "tc_08_infer_totals",
        missing_totals_cols,
        values,
        "Inference test - has units, missing totals (inferable)"
    ))

    # Test Case 9: With metadata - Required + category, stock, unit_type
    metadata_cols = required_cols.copy()
    for col in ['in_category', 'in_stock', 'in_unit_type']:
        if col in optional_cols or col in required_cols:
            if col not in metadata_cols:
                metadata_cols.append(col)
    test_cases.append(create_test_case(
        output_dir,
        "tc_09_with_metadata",
        metadata_cols,
        values,
        "Metadata case - includes product categorization"
    ))

    # Test Case 10: With customer info - Required + customer_id, trans_type
    customer_cols = required_cols.copy()
    for col in ['in_customer_id', 'in_trans_type']:
        if col in optional_cols or col in required_cols:
            if col not in customer_cols:
                customer_cols.append(col)
    test_cases.append(create_test_case(
        output_dir,
        "tc_10_with_customer",
        customer_cols,
        values,
        "Customer case - includes customer tracking"
    ))

    # Test Case 11: Minimal + quantity only (common simple case)
    min_qty_cols = required_cols.copy()
    if 'in_quantity' not in min_qty_cols:
        min_qty_cols.append('in_quantity')
    test_cases.append(create_test_case(
        output_dir,
        "tc_11_minimal_plus_qty",
        min_qty_cols,
        values,
        "Simple case - required + quantity only"
    ))

    # Generate summary
    summary_file = output_dir / "key_test_cases_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("Key Test Cases Summary\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total test cases: {len(test_cases)}\n\n")

        for filename, columns, description in test_cases:
            f.write(f"{filename}\n")
            f.write(f"  Description: {description}\n")
            f.write(f"  Columns ({len(columns)}): {', '.join(columns)}\n\n")

    print(f"[OK] Generated {len(test_cases)} key test case files")
    print(f"[OK] Summary written to {summary_file}")


if __name__ == "__main__":
    main()
