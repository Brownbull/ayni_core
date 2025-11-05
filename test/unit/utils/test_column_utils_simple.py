"""
Simple test script for column_utils (no pytest required)
"""

import sys
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.column_utils import (
    select_columns_safe,
    filter_columns,
    build_column_list,
    ensure_columns_exist,
    deduplicate_columns,
    get_columns_by_pattern,
    get_column_diff,
    validate_column_subset,
)


def test_select_columns_safe():
    print("Testing select_columns_safe...")

    df = pd.DataFrame({'a': [1, 2], 'b': [3, 4], 'c': [5, 6]})

    # Select existing columns
    result = select_columns_safe(df, ['a', 'b'])
    assert list(result.columns) == ['a', 'b']
    assert len(result) == 2

    # missing_ok=True
    result = select_columns_safe(df, ['a', 'missing'], missing_ok=True)
    assert list(result.columns) == ['a']

    # missing_ok=False should raise
    try:
        select_columns_safe(df, ['a', 'missing'], missing_ok=False)
        assert False, "Should have raised KeyError"
    except KeyError:
        pass

    print("  [OK] select_columns_safe passed")


def test_filter_columns():
    print("Testing filter_columns...")

    df = pd.DataFrame({'a': [1], 'b': [2], 'c': [3], 'd': [4]})

    # Exclude columns
    result = filter_columns(df, exclude=['b', 'd'])
    assert result == ['a', 'c']

    # keep_first
    result = filter_columns(df, exclude=['a', 'b'], keep_first=['a'])
    assert result == ['a', 'c', 'd']

    # as_list=False returns DataFrame
    result = filter_columns(df, exclude=['b'], as_list=False)
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ['a', 'c', 'd']

    print("  [OK] filter_columns passed")


def test_build_column_list():
    print("Testing build_column_list...")

    # Base + include
    result = build_column_list(['a', 'b'], include=['c'])
    assert result == ['a', 'b', 'c']

    # With exclude
    result = build_column_list(['a', 'b', 'c'], exclude=['b'])
    assert result == ['a', 'c']

    # With available_cols
    result = build_column_list(['a', 'b', 'c'], available_cols=['a', 'c', 'd'])
    assert result == ['a', 'c']

    # Deduplicate
    result = build_column_list(['a', 'b', 'a', 'c'], deduplicate=True)
    assert result == ['a', 'b', 'c']

    # Complex example
    result = build_column_list(
        base_cols=['a', 'b', 'c'],
        include=['d', 'a'],
        exclude=['b'],
        available_cols=['a', 'c', 'd', 'e'],
        deduplicate=True
    )
    assert result == ['a', 'c', 'd']

    print("  [OK] build_column_list passed")


def test_ensure_columns_exist():
    print("Testing ensure_columns_exist...")

    df = pd.DataFrame({'a': [1], 'b': [2]})

    # All exist
    missing = ensure_columns_exist(df, ['a', 'b'])
    assert missing == []

    # Some missing, raise_on_missing=False
    missing = ensure_columns_exist(df, ['a', 'c'], raise_on_missing=False)
    assert missing == ['c']

    # Some missing, raise_on_missing=True
    try:
        ensure_columns_exist(df, ['a', 'c'], raise_on_missing=True)
        assert False, "Should have raised KeyError"
    except KeyError:
        pass

    print("  [OK] ensure_columns_exist passed")


def test_deduplicate_columns():
    print("Testing deduplicate_columns...")

    # Preserve order
    result = deduplicate_columns(['a', 'b', 'a', 'c', 'b'])
    assert result == ['a', 'b', 'c']

    # Sort
    result = deduplicate_columns(['c', 'a', 'b', 'a'], preserve_order=False)
    assert result == ['a', 'b', 'c']

    print("  [OK] deduplicate_columns passed")


def test_get_columns_by_pattern():
    print("Testing get_columns_by_pattern...")

    df = pd.DataFrame({'in_price': [1], 'in_cost': [2], 'out_total': [3], 'other': [4]})

    # Pattern match
    result = get_columns_by_pattern(df, 'in_')
    assert result == ['in_price', 'in_cost']

    # With exclude
    result = get_columns_by_pattern(df, 'in_', exclude=['in_cost'])
    assert result == ['in_price']

    # Case insensitive
    result = get_columns_by_pattern(df, 'IN_', case_sensitive=False)
    assert result == ['in_price', 'in_cost']

    print("  [OK] get_columns_by_pattern passed")


def test_get_column_diff():
    print("Testing get_column_diff...")

    df1 = pd.DataFrame({'a': [1], 'b': [2], 'c': [3]})
    df2 = pd.DataFrame({'b': [2], 'c': [3], 'd': [4]})

    # Both
    only_in_df1, only_in_df2 = get_column_diff(df1, df2, return_type='both')
    assert only_in_df1 == ['a']
    assert only_in_df2 == ['d']

    # df1 only
    result = get_column_diff(df1, df2, return_type='df1')
    assert result == ['a']

    # df2 only
    result = get_column_diff(df1, df2, return_type='df2')
    assert result == ['d']

    print("  [OK] get_column_diff passed")


def test_validate_column_subset():
    print("Testing validate_column_subset...")

    # Valid subset
    result = validate_column_subset(['a', 'b'], ['a', 'b', 'c'])
    assert result is True

    # Invalid subset
    result = validate_column_subset(['a', 'd'], ['a', 'b', 'c'])
    assert result is False

    print("  [OK] validate_column_subset passed")


def test_persistence_pattern():
    """Test patterns from persistence.py:30-105"""
    print("Testing persistence.py patterns...")

    # Simulate _get_columns_to_save logic
    df = pd.DataFrame({
        'in_price': [100, 150],
        'in_cost': [60, 90],
        'in_quantity': [2, 3],
        'row_id': [1, 2],
        'product': ['A', 'B']
    })

    in_cols = ['in_price', 'in_cost', 'in_quantity', 'row_id', 'product']
    row_id = 'row_id'
    group_by = ['product']

    # OLD: Complex list comprehensions (persistence.py:92-95)
    # exclude_cols = []
    # if row_id: exclude_cols.append(row_id)
    # exclude_cols.extend(group_by)
    # cols_to_save = [col for col in cols_to_save if col not in exclude_cols]
    # cols_to_save = [col for col in cols_to_save if col in df.columns]

    # NEW: Using column_utils
    cols_to_save = build_column_list(
        base_cols=in_cols,
        exclude=[row_id] + group_by,
        available_cols=df.columns.tolist()
    )

    assert 'row_id' not in cols_to_save
    assert 'product' not in cols_to_save
    assert 'in_price' in cols_to_save
    assert 'in_cost' in cols_to_save
    assert 'in_quantity' in cols_to_save

    print("  [OK] persistence.py patterns passed")


def test_executor_pattern():
    """Test patterns from executor.py"""
    print("Testing executor.py patterns...")

    df = pd.DataFrame({
        'in_price': [100],
        'in_cost': [60],
        'exec_margin': [40],
        'exec_profit_pct': [0.4]
    })

    # OLD: [col for col in filters_df.columns if col.startswith('exec_')]
    # NEW:
    exec_cols = get_columns_by_pattern(df, 'exec_')
    assert exec_cols == ['exec_margin', 'exec_profit_pct']

    # OLD: missing = [col for col in join_cols if col not in data_in.columns]
    # NEW:
    join_cols = ['in_price', 'in_cost', 'missing_col']
    missing = ensure_columns_exist(df, join_cols, raise_on_missing=False)
    assert missing == ['missing_col']

    print("  [OK] executor.py patterns passed")


def test_validators_pattern():
    """Test patterns from validators.py"""
    print("Testing validators.py patterns...")

    df = pd.DataFrame({'fecha': [1], 'producto': [2], 'total': [3]})

    required = ['fecha', 'producto', 'total', 'cantidad']

    # OLD: missing = [col for col in required if col not in df.columns]
    # NEW:
    missing = ensure_columns_exist(df, required, raise_on_missing=False)
    assert missing == ['cantidad']

    print("  [OK] validators.py patterns passed")


def main():
    print("=" * 60)
    print("Running column_utils tests...")
    print("=" * 60)

    try:
        test_select_columns_safe()
        test_filter_columns()
        test_build_column_list()
        test_ensure_columns_exist()
        test_deduplicate_columns()
        test_get_columns_by_pattern()
        test_get_column_diff()
        test_validate_column_subset()
        test_persistence_pattern()
        test_executor_pattern()
        test_validators_pattern()

        print("=" * 60)
        print("[OK] ALL TESTS PASSED!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
