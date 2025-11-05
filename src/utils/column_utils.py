"""
Column Utilities for GabeDA

Single Responsibility: DataFrame column selection, filtering, and manipulation

Provides common patterns for:
- Safe column selection with validation
- Column filtering (include/exclude patterns)
- Column existence checking
- Column list building with complex rules

Usage:
    from src.utils.column_utils import select_columns_safe, filter_columns

    # Safe column selection
    subset = select_columns_safe(df, ['col1', 'col2'], missing_ok=False)

    # Filter columns with exclude list
    cols = filter_columns(df, exclude=['internal_col', 'row_id'])

    # Build column list with include/exclude rules
    final_cols = build_column_list(
        base_cols=['a', 'b', 'c'],
        exclude=['b'],
        available_cols=df.columns.tolist()
    )

Does NOT:
- Process column data/values (use transformers)
- Validate column schemas (use validators)
- Map column names (use transformers)
"""

from typing import List, Optional, Union
import pandas as pd
import logging


def select_columns_safe(df: pd.DataFrame,
                        columns: List[str],
                        missing_ok: bool = False,
                        logger: Optional[logging.Logger] = None) -> pd.DataFrame:
    """
    Select columns from DataFrame with validation.

    Args:
        df: DataFrame to select from
        columns: List of column names to select
        missing_ok: If False, raise error if any columns missing; if True, select only available columns
        logger: Optional logger for warnings

    Returns:
        DataFrame with selected columns

    Raises:
        KeyError: If missing_ok=False and columns are missing

    Examples:
        >>> df = pd.DataFrame({'a': [1], 'b': [2], 'c': [3]})
        >>> select_columns_safe(df, ['a', 'b'])
           a  b
        0  1  2
        >>> select_columns_safe(df, ['a', 'missing'], missing_ok=True)
           a
        0  1
        >>> select_columns_safe(df, ['a', 'missing'], missing_ok=False)
        # Raises KeyError

    Use Cases:
        # Replace: df[cols_to_keep].copy()
        subset_df = select_columns_safe(df, cols_to_keep)

        # persistence.py:182 - with validation
        df_to_save = select_columns_safe(df, cols_to_save, missing_ok=False)
    """
    if missing_ok:
        # Select only available columns
        available = [col for col in columns if col in df.columns]
        missing = [col for col in columns if col not in df.columns]

        if missing and logger:
            logger.warning(f"Columns not found (skipped): {missing}")

        return df[available].copy() if available else pd.DataFrame()
    else:
        # Validate all columns exist
        missing = [col for col in columns if col not in df.columns]

        if missing:
            error_msg = f"Columns not found in DataFrame: {missing}"
            if logger:
                logger.error(error_msg)
            raise KeyError(error_msg)

        return df[columns].copy()


def filter_columns(df: pd.DataFrame,
                  exclude: Optional[List[str]] = None,
                  keep_first: Optional[List[str]] = None,
                  as_list: bool = True) -> Union[List[str], pd.DataFrame]:
    """
    Get column list from DataFrame, excluding specified columns.

    Args:
        df: DataFrame to get columns from
        exclude: List of column names to exclude
        keep_first: List of columns to keep at the beginning (even if in exclude)
        as_list: If True, return list of column names; if False, return filtered DataFrame

    Returns:
        List of column names or filtered DataFrame

    Examples:
        >>> df = pd.DataFrame({'a': [1], 'b': [2], 'c': [3], 'd': [4]})
        >>> filter_columns(df, exclude=['b', 'd'])
        ['a', 'c']
        >>> filter_columns(df, exclude=['a'], keep_first=['a'])
        ['a', 'b', 'c', 'd']
        >>> filter_columns(df, exclude=['b'], as_list=False)
           a  c  d
        0  1  3  4

    Use Cases:
        # persistence.py:92 - Filter out excluded columns
        cols_to_save = filter_columns(df, exclude=exclude_cols)

        # groupby.py - Get columns excluding infrastructure
        data_cols = filter_columns(group_df, exclude=['row_id', 'group_col'])
    """
    if exclude is None:
        exclude = []

    if keep_first is None:
        keep_first = []

    # Start with all columns
    all_cols = df.columns.tolist()

    # Build result: keep_first + (all_cols - exclude - keep_first)
    result_cols = []

    # Add keep_first columns
    for col in keep_first:
        if col in all_cols and col not in result_cols:
            result_cols.append(col)

    # Add remaining columns (not in exclude, not already added)
    for col in all_cols:
        if col not in exclude and col not in result_cols:
            result_cols.append(col)

    if as_list:
        return result_cols
    else:
        return df[result_cols].copy()


def build_column_list(base_cols: List[str],
                     include: Optional[List[str]] = None,
                     exclude: Optional[List[str]] = None,
                     available_cols: Optional[List[str]] = None,
                     deduplicate: bool = True) -> List[str]:
    """
    Build column list from base + include - exclude, with optional validation.

    Args:
        base_cols: Base list of columns to start with
        include: Additional columns to include
        exclude: Columns to exclude from result
        available_cols: If provided, only return columns that exist in this list
        deduplicate: If True, remove duplicates while preserving order

    Returns:
        Final list of column names

    Examples:
        >>> build_column_list(['a', 'b'], include=['c'], exclude=['b'])
        ['a', 'c']
        >>> build_column_list(['a', 'b', 'a'], deduplicate=True)
        ['a', 'b']
        >>> build_column_list(['a', 'b', 'c'], available_cols=['a', 'c'])
        ['a', 'c']

    Use Cases:
        # persistence.py:75-95 - Complex column building
        cols_to_save = build_column_list(
            base_cols=in_cols,
            exclude=[row_id] + group_by,
            available_cols=df.columns.tolist()
        )

        # executor.py - Build feature columns
        feature_cols = build_column_list(
            base_cols=input_cols,
            include=computed_features,
            exclude=internal_cols
        )
    """
    if include is None:
        include = []
    if exclude is None:
        exclude = []

    # Combine base + include
    result = list(base_cols) + list(include)

    # Remove excluded columns
    result = [col for col in result if col not in exclude]

    # Filter by available columns if provided
    if available_cols is not None:
        result = [col for col in result if col in available_cols]

    # Deduplicate while preserving order
    if deduplicate:
        seen = set()
        deduped = []
        for col in result:
            if col not in seen:
                seen.add(col)
                deduped.append(col)
        result = deduped

    return result


def ensure_columns_exist(df: pd.DataFrame,
                        columns: List[str],
                        raise_on_missing: bool = True,
                        logger: Optional[logging.Logger] = None) -> List[str]:
    """
    Check if columns exist in DataFrame, return missing columns.

    Args:
        df: DataFrame to check
        columns: List of column names to check
        raise_on_missing: If True, raise error if columns missing; if False, just return missing list
        logger: Optional logger for error/warning messages

    Returns:
        List of missing columns (empty if all exist)

    Raises:
        KeyError: If raise_on_missing=True and columns are missing

    Examples:
        >>> df = pd.DataFrame({'a': [1], 'b': [2]})
        >>> ensure_columns_exist(df, ['a', 'b'])
        []
        >>> ensure_columns_exist(df, ['a', 'c'], raise_on_missing=False)
        ['c']
        >>> ensure_columns_exist(df, ['a', 'c'], raise_on_missing=True)
        # Raises KeyError

    Use Cases:
        # validators.py:180 - Check required columns
        missing = ensure_columns_exist(df, required_cols, raise_on_missing=True)

        # executor.py:129 - Validate join columns
        missing = ensure_columns_exist(data_in, join_cols, raise_on_missing=False)
    """
    missing = [col for col in columns if col not in df.columns]

    if missing:
        if raise_on_missing:
            error_msg = f"Required columns not found in DataFrame: {missing}"
            if logger:
                logger.error(error_msg)
                logger.error(f"Available columns: {df.columns.tolist()}")
            raise KeyError(error_msg)
        elif logger:
            logger.warning(f"Columns not found: {missing}")

    return missing


def deduplicate_columns(cols: List[str],
                       preserve_order: bool = True) -> List[str]:
    """
    Remove duplicate column names from list.

    Args:
        cols: List of column names (may have duplicates)
        preserve_order: If True, preserve original order (first occurrence); if False, sort

    Returns:
        List with duplicates removed

    Examples:
        >>> deduplicate_columns(['a', 'b', 'a', 'c', 'b'])
        ['a', 'b', 'c']
        >>> deduplicate_columns(['c', 'a', 'b', 'a'], preserve_order=False)
        ['a', 'b', 'c']
    """
    if preserve_order:
        seen = set()
        result = []
        for col in cols:
            if col not in seen:
                seen.add(col)
                result.append(col)
        return result
    else:
        return sorted(list(set(cols)))


def get_columns_by_pattern(df: pd.DataFrame,
                          pattern: str,
                          exclude: Optional[List[str]] = None,
                          case_sensitive: bool = True) -> List[str]:
    """
    Get columns matching a string pattern.

    Args:
        df: DataFrame to get columns from
        pattern: String pattern to match (substring match, not regex)
        exclude: Optional list of columns to exclude from results
        case_sensitive: If True, case-sensitive matching; if False, case-insensitive

    Returns:
        List of matching column names

    Examples:
        >>> df = pd.DataFrame({'in_price': [1], 'in_cost': [2], 'out_total': [3]})
        >>> get_columns_by_pattern(df, 'in_')
        ['in_price', 'in_cost']
        >>> get_columns_by_pattern(df, 'IN_', case_sensitive=False)
        ['in_price', 'in_cost']
        >>> get_columns_by_pattern(df, 'in_', exclude=['in_cost'])
        ['in_price']

    Use Cases:
        # executor.py:226-228 - Get all exec_ columns
        exec_cols = get_columns_by_pattern(filters_df, 'exec_')

        # Find all input columns
        input_cols = get_columns_by_pattern(df, 'in_')
    """
    if exclude is None:
        exclude = []

    all_cols = df.columns.tolist()

    if case_sensitive:
        matching = [col for col in all_cols if pattern in col and col not in exclude]
    else:
        pattern_lower = pattern.lower()
        matching = [col for col in all_cols if pattern_lower in col.lower() and col not in exclude]

    return matching


def get_column_diff(df1: pd.DataFrame,
                   df2: pd.DataFrame,
                   return_type: str = 'both') -> Union[List[str], tuple]:
    """
    Get difference in columns between two DataFrames.

    Args:
        df1: First DataFrame
        df2: Second DataFrame
        return_type: 'both' returns (in_df1_only, in_df2_only); 'df1' returns only df1; 'df2' returns only df2

    Returns:
        List of column names or tuple of lists depending on return_type

    Examples:
        >>> df1 = pd.DataFrame({'a': [1], 'b': [2], 'c': [3]})
        >>> df2 = pd.DataFrame({'b': [2], 'c': [3], 'd': [4]})
        >>> get_column_diff(df1, df2, return_type='both')
        (['a'], ['d'])
        >>> get_column_diff(df1, df2, return_type='df1')
        ['a']

    Use Cases:
        # Compare input and output columns
        new_cols, removed_cols = get_column_diff(input_df, output_df)
    """
    cols1 = set(df1.columns)
    cols2 = set(df2.columns)

    only_in_df1 = sorted(list(cols1 - cols2))
    only_in_df2 = sorted(list(cols2 - cols1))

    if return_type == 'both':
        return (only_in_df1, only_in_df2)
    elif return_type == 'df1':
        return only_in_df1
    elif return_type == 'df2':
        return only_in_df2
    else:
        raise ValueError(f"Invalid return_type: {return_type}. Must be 'both', 'df1', or 'df2'")


def validate_column_subset(subset: List[str],
                          superset: List[str],
                          logger: Optional[logging.Logger] = None) -> bool:
    """
    Check if subset columns are all in superset columns.

    Args:
        subset: List of columns that should be subset
        superset: List of columns that should contain all subset columns
        logger: Optional logger for error messages

    Returns:
        True if subset is valid, False otherwise

    Examples:
        >>> validate_column_subset(['a', 'b'], ['a', 'b', 'c'])
        True
        >>> validate_column_subset(['a', 'd'], ['a', 'b', 'c'])
        False
    """
    subset_set = set(subset)
    superset_set = set(superset)

    missing = subset_set - superset_set

    if missing:
        if logger:
            logger.error(f"Columns in subset but not in superset: {sorted(missing)}")
        return False

    return True


# Module-level exports
__all__ = [
    'select_columns_safe',
    'filter_columns',
    'build_column_list',
    'ensure_columns_exist',
    'deduplicate_columns',
    'get_columns_by_pattern',
    'get_column_diff',
    'validate_column_subset',
]
