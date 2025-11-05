"""
Generate all valid test case CSV files from base_case.csv

This script reads the base_case.csv which defines:
- Which columns are required (optional=0) vs optional (optional=1)
- Which columns can be inferred (inferable=1) from other columns
- The base data values for each column

It generates all valid combinations of columns, considering:
1. Required columns (optional=0) must always be present
2. Optional columns (optional=1) can be present or absent
3. Inferable columns (inferable=1) can be omitted if the columns they depend on are present

Output: Multiple CSV files in the same directory, one per valid combination
"""

import pandas as pd
import itertools
from pathlib import Path
from typing import List, Tuple, Dict

# Define inference rules: which columns can be calculated from which other columns
INFERENCE_RULES = {
    'in_cost_total': ['in_cost_unit', 'in_quantity'],
    'in_price_total': ['in_price_unit', 'in_quantity'],
    'in_cost_unit': ['in_cost_total', 'in_quantity'],
    'in_price_unit': ['in_price_total', 'in_quantity'],
    'in_discount_total': [],  # Can be inferred from price differences
    'in_commission_total': [],  # Can be inferred from business rules
    'in_margin': ['in_price_unit', 'in_cost_unit', 'in_quantity', 'in_price_total', 'in_cost_total'],
}


def load_base_case(filepath: str) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """Load base_case.csv and parse column metadata"""
    df = pd.read_csv(filepath)

    # Extract column metadata
    metadata = []
    values = {}

    for _, row in df.iterrows():
        if pd.notna(row['col']) and row['col'] != 'case base':
            col_name = row['col']
            metadata.append({
                'column': col_name,
                'optional': int(row['optional']),
                'inferable': int(row['inferable'])
            })
            values[col_name] = row['case base']

    return pd.DataFrame(metadata), values


def is_column_inferable(column: str, present_columns: List[str]) -> bool:
    """Check if a column can be inferred from the present columns"""
    if column not in INFERENCE_RULES:
        return False

    required_cols = INFERENCE_RULES[column]
    if not required_cols:
        # Can be inferred through complex logic
        return True

    # Check if all required columns for inference are present
    return all(col in present_columns for col in required_cols)


def generate_valid_combinations(metadata_df: pd.DataFrame) -> List[List[str]]:
    """Generate all valid combinations of columns"""

    # Separate columns by type
    required_cols = metadata_df[metadata_df['optional'] == 0]['column'].tolist()
    optional_cols = metadata_df[metadata_df['optional'] == 1]['column'].tolist()
    inferable_cols = metadata_df[metadata_df['inferable'] == 1]['column'].tolist()

    valid_combinations = []

    # Generate all subsets of optional columns (2^n combinations)
    for r in range(len(optional_cols) + 1):
        for optional_subset in itertools.combinations(optional_cols, r):
            optional_subset = list(optional_subset)

            # Start with required columns + selected optional columns
            base_cols = required_cols + optional_subset

            # For inferable columns, generate all valid combinations
            # An inferable column can be omitted if it can be calculated from present columns
            inferable_in_base = [col for col in base_cols if col in inferable_cols]

            # Generate power set of inferable columns that are currently in base
            for inf_r in range(len(inferable_in_base) + 1):
                for inferable_to_remove in itertools.combinations(inferable_in_base, inf_r):
                    candidate_cols = [col for col in base_cols if col not in inferable_to_remove]

                    # Validate: removed inferable columns must be calculable
                    valid = True
                    for removed_col in inferable_to_remove:
                        if not is_column_inferable(removed_col, candidate_cols):
                            valid = False
                            break

                    if valid and candidate_cols not in valid_combinations:
                        valid_combinations.append(sorted(candidate_cols))

    return valid_combinations


def generate_test_case_files(base_path: Path, combinations: List[List[str]], values: Dict[str, str]):
    """Generate CSV files for each valid combination"""

    output_dir = base_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating {len(combinations)} test case files...\n")

    for idx, cols in enumerate(combinations, start=1):
        # Create a single-row dataframe with selected columns
        data = {col: [values[col]] for col in cols}
        df = pd.DataFrame(data)

        # Generate filename
        filename = f"test_case_{idx:03d}.csv"
        filepath = output_dir / filename

        # Save to CSV
        df.to_csv(filepath, index=False)

        # Print summary
        col_list = ', '.join(cols)
        print(f"[OK] {filename}: {len(cols)} columns - {col_list}")

    print(f"\n[OK] Generated {len(combinations)} test case files in {output_dir}")

    # Generate summary file
    summary_file = output_dir / "test_cases_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("Test Case Summary\n")
        f.write("=" * 80 + "\n\n")
        for idx, cols in enumerate(combinations, start=1):
            f.write(f"test_case_{idx:03d}.csv ({len(cols)} columns):\n")
            f.write(f"  {', '.join(cols)}\n\n")

    print(f"[OK] Summary written to {summary_file}")


def main():
    import sys

    # Path to base_case.csv
    base_path = Path(__file__).parent / "base_case.csv"

    if not base_path.exists():
        print(f"Error: base_case.csv not found at {base_path}")
        return

    print("Loading base_case.csv...")
    metadata_df, values = load_base_case(base_path)

    print(f"Found {len(metadata_df)} columns:")
    print(f"  - Required: {len(metadata_df[metadata_df['optional'] == 0])}")
    print(f"  - Optional: {len(metadata_df[metadata_df['optional'] == 1])}")
    print(f"  - Inferable: {len(metadata_df[metadata_df['inferable'] == 1])}")
    print()

    print("Generating valid column combinations...")
    combinations = generate_valid_combinations(metadata_df)
    print(f"Generated {len(combinations)} valid combinations\n")

    # Check if there are too many combinations
    if len(combinations) > 1000:
        print(f"WARNING: This will generate {len(combinations)} files!")
        response = input("Do you want to continue? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Aborted.")
            return

    # Generate test case files
    generate_test_case_files(base_path, combinations, values)


if __name__ == "__main__":
    main()
