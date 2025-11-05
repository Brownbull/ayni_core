"""
Validation Utilities for GabeDA

Single Responsibility: Common validation patterns and helpers

Provides utilities for:
- DataFrame validation (rows, columns, types)
- Dictionary/config validation
- Value range validation
- Mutual exclusivity checks

Usage:
    from src.utils.validation_utils import validate_dataframe, validate_required_keys

    # Validate DataFrame
    result = validate_dataframe(df, min_rows=1, required_cols=['col1', 'col2'])

    # Validate config
    result = validate_required_keys(config, ['model_name', 'input_cols'])

Does NOT:
- Perform data transformations (use transformers)
- Load/save data (use loaders)
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import logging
from src.core.results import OperationResult


def validate_dataframe(df: pd.DataFrame,
                      min_rows: int = 0,
                      max_rows: Optional[int] = None,
                      required_cols: Optional[List[str]] = None,
                      logger: Optional[logging.Logger] = None) -> OperationResult:
    """
    Validate DataFrame basic requirements.

    Args:
        df: DataFrame to validate
        min_rows: Minimum number of rows required
        max_rows: Maximum number of rows allowed (None = no limit)
        required_cols: List of required column names
        logger: Optional logger for messages

    Returns:
        OperationResult with validation status

    Examples:
        >>> result = validate_dataframe(df, min_rows=1, required_cols=['id', 'value'])
        >>> if not result.success:
        ...     print(result.errors)
    """
    result = OperationResult(success=True)

    # Check row count
    if len(df) < min_rows:
        result.add_error(f"DataFrame has {len(df)} rows, minimum required: {min_rows}")

    if max_rows is not None and len(df) > max_rows:
        result.add_error(f"DataFrame has {len(df)} rows, maximum allowed: {max_rows}")

    # Check required columns
    if required_cols:
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            result.add_error(f"Missing required columns: {missing}")
            if logger:
                logger.error(f"Available columns: {df.columns.tolist()}")

    if not result.success and logger:
        logger.error(f"DataFrame validation failed with {len(result.errors)} errors")

    return result


def validate_required_keys(d: Dict,
                          required_keys: List[str],
                          context_name: str = "dictionary",
                          logger: Optional[logging.Logger] = None) -> OperationResult:
    """
    Validate dictionary has all required keys.

    Args:
        d: Dictionary to validate
        required_keys: List of required key names
        context_name: Name of dict for error messages
        logger: Optional logger

    Returns:
        OperationResult with validation status

    Examples:
        >>> result = validate_required_keys(config, ['model_name', 'input_cols'])
        >>> if not result.success:
        ...     print(result.errors)
    """
    result = OperationResult(success=True)

    missing = [key for key in required_keys if key not in d]
    if missing:
        result.add_error(f"{context_name} missing required keys: {missing}")
        if logger:
            logger.error(f"Available keys: {list(d.keys())}")

    return result


def validate_mutually_exclusive(values: Dict[str, Any],
                                field_names: List[str],
                                logger: Optional[logging.Logger] = None) -> OperationResult:
    """
    Validate that only one of the specified fields is set.

    Args:
        values: Dictionary with field values
        field_names: List of field names that are mutually exclusive
        logger: Optional logger

    Returns:
        OperationResult with validation status

    Examples:
        >>> result = validate_mutually_exclusive(
        ...     {'mode_a': True, 'mode_b': None, 'mode_c': None},
        ...     ['mode_a', 'mode_b', 'mode_c']
        ... )
        >>> result.success  # True (only mode_a is set)
    """
    result = OperationResult(success=True)

    # Count how many are set (not None)
    set_fields = [name for name in field_names if values.get(name) is not None]

    if len(set_fields) == 0:
        result.add_error(f"At least one of {field_names} must be set")
    elif len(set_fields) > 1:
        result.add_error(f"Only one of {field_names} can be set, but got: {set_fields}")

    if not result.success and logger:
        logger.error(f"Mutual exclusivity validation failed: {result.errors[0]}")

    return result


def validate_value_range(value: Any,
                        min_value: Optional[Any] = None,
                        max_value: Optional[Any] = None,
                        field_name: str = "value",
                        logger: Optional[logging.Logger] = None) -> OperationResult:
    """
    Validate value is within specified range.

    Args:
        value: Value to validate
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)
        field_name: Name of field for error messages
        logger: Optional logger

    Returns:
        OperationResult with validation status

    Examples:
        >>> result = validate_value_range(5, min_value=1, max_value=10, field_name='count')
        >>> result.success  # True
    """
    result = OperationResult(success=True)

    if min_value is not None and value < min_value:
        result.add_error(f"{field_name} ({value}) is below minimum ({min_value})")

    if max_value is not None and value > max_value:
        result.add_error(f"{field_name} ({value}) is above maximum ({max_value})")

    if not result.success and logger:
        logger.error(result.errors[0])

    return result


def validate_list_not_empty(lst: List,
                           list_name: str = "list",
                           logger: Optional[logging.Logger] = None) -> OperationResult:
    """
    Validate list is not empty.

    Args:
        lst: List to validate
        list_name: Name of list for error messages
        logger: Optional logger

    Returns:
        OperationResult with validation status

    Examples:
        >>> result = validate_list_not_empty([], list_name='features')
        >>> result.success  # False
    """
    result = OperationResult(success=True)

    if not lst or len(lst) == 0:
        result.add_error(f"{list_name} cannot be empty")
        if logger:
            logger.error(f"{list_name} is empty")

    return result


def validate_all(validations: List[OperationResult],
                logger: Optional[logging.Logger] = None) -> OperationResult:
    """
    Combine multiple validation results into one.

    Args:
        validations: List of OperationResult instances
        logger: Optional logger

    Returns:
        Combined OperationResult

    Examples:
        >>> val1 = validate_dataframe(df, min_rows=1)
        >>> val2 = validate_required_keys(config, ['name'])
        >>> combined = validate_all([val1, val2])
        >>> if not combined.success:
        ...     print(combined.errors)
    """
    result = OperationResult(success=True)

    for validation in validations:
        if not validation.success:
            result.success = False
            result.errors.extend(validation.errors)
        result.warnings.extend(validation.warnings)

    if not result.success and logger:
        logger.error(f"Combined validation failed with {len(result.errors)} errors")

    return result


# Module-level exports
__all__ = [
    'validate_dataframe',
    'validate_required_keys',
    'validate_mutually_exclusive',
    'validate_value_range',
    'validate_list_not_empty',
    'validate_all',
]
