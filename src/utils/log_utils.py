"""
Logging Utilities for GabeDA

Single Responsibility: Standardized logging patterns and helpers

Provides common patterns for:
- Operation logging (start, complete, failed)
- Data shape logging (DataFrame rows/columns)
- Validation result logging (success, warnings, errors)
- Feature execution logging
- Dependency resolution logging
- File operation logging

Usage:
    from src.utils.log_utils import log_operation_start, log_operation_complete, log_data_shape

    # Operation logging
    log_operation_start(logger, 'Loading data', file_path='/path/to/data.csv')
    # ... do operation ...
    log_operation_complete(logger, 'Loading data', status='success')

    # Data shape logging
    log_data_shape(logger, 'input_data', df, action='Loaded')

Does NOT:
- Create loggers (use logger.py get_logger)
- Configure logging (use logger.py setup_logging)
"""

from typing import Optional, Dict, Any, List
import logging
import pandas as pd


# Status symbols for consistent formatting
STATUS_SUCCESS = '[OK]'
STATUS_WARNING = '[WARN]'
STATUS_ERROR = '[FAIL]'
STATUS_INFO = '[INFO]'


def log_operation_start(logger: logging.Logger,
                        operation: str,
                        level: int = logging.INFO,
                        **context) -> None:
    """
    Log operation start with context.

    Args:
        logger: Logger instance
        operation: Operation name/description
        level: Logging level (default: INFO)
        **context: Additional context to log (key=value pairs)

    Examples:
        >>> log_operation_start(logger, 'Loading data', file_path='/data/input.csv')
        # Logs: "Loading data... (file_path=/data/input.csv)"
        >>> log_operation_start(logger, 'Processing model', model_name='model1')
        # Logs: "Processing model... (model_name=model1)"
    """
    if context:
        context_str = ', '.join(f"{k}={v}" for k, v in context.items())
        message = f"{operation}... ({context_str})"
    else:
        message = f"{operation}..."

    logger.log(level, message)


def log_operation_complete(logger: logging.Logger,
                           operation: str,
                           status: str = 'success',
                           level: Optional[int] = None,
                           **context) -> None:
    """
    Log operation completion with status.

    Args:
        logger: Logger instance
        operation: Operation name/description
        status: 'success', 'warning', 'error', or 'info'
        level: Logging level (auto-determined from status if None)
        **context: Additional context to log

    Examples:
        >>> log_operation_complete(logger, 'Data validation', status='success')
        # Logs: "[OK] Data validation complete"
        >>> log_operation_complete(logger, 'Processing', status='warning', count=5)
        # Logs: "[WARN] Processing complete (count=5)"

    Use Cases:
        # persistence.py:229 - Replace: logger.info(f"✓ Context state saved successfully")
        log_operation_complete(logger, 'Context state saved', status='success')

        # excel.py:94 - Replace: logger.info(f"✓ Excel file saved: {output_path}")
        log_operation_complete(logger, 'Excel file saved', status='success', path=output_path)
    """
    # Determine status symbol and level
    if status == 'success':
        symbol = STATUS_SUCCESS
        default_level = logging.INFO
    elif status == 'warning':
        symbol = STATUS_WARNING
        default_level = logging.WARNING
    elif status == 'error':
        symbol = STATUS_ERROR
        default_level = logging.ERROR
    else:  # info
        symbol = STATUS_INFO
        default_level = logging.INFO

    level = level if level is not None else default_level

    # Build message
    if context:
        context_str = ', '.join(f"{k}={v}" for k, v in context.items())
        message = f"{symbol} {operation} complete ({context_str})"
    else:
        message = f"{symbol} {operation} complete"

    logger.log(level, message)


def log_validation_result(logger: logging.Logger,
                          is_valid: bool,
                          context: str,
                          errors: Optional[List[str]] = None,
                          warnings: Optional[List[str]] = None) -> None:
    """
    Log validation result with errors/warnings.

    Args:
        logger: Logger instance
        is_valid: Whether validation passed
        context: Description of what was validated
        errors: List of error messages (logged as ERROR)
        warnings: List of warning messages (logged as WARNING)

    Examples:
        >>> log_validation_result(logger, True, 'Required columns')
        # Logs: "[OK] Required columns validation passed"
        >>> log_validation_result(logger, False, 'Data quality', errors=['Missing values in col1'])
        # Logs: "[FAIL] Data quality validation failed"
        #       "[FAIL] Missing values in col1"

    Use Cases:
        # validators.py:192 - Replace: logger.info(f"✓ All required columns present: {required}")
        log_validation_result(logger, True, f'All required columns present: {required}')

        # validators.py:184 - Replace: logger.error(f"✗ {error_msg}")
        log_validation_result(logger, False, 'Required columns', errors=[error_msg])
    """
    if is_valid:
        logger.info(f"{STATUS_SUCCESS} {context} validation passed")
    else:
        logger.error(f"{STATUS_ERROR} {context} validation failed")

    # Log errors
    if errors:
        for error in errors:
            logger.error(f"{STATUS_ERROR} {error}")

    # Log warnings
    if warnings:
        for warning in warnings:
            logger.warning(f"{STATUS_WARNING} {warning}")


def log_data_shape(logger: logging.Logger,
                  name: str,
                  df: pd.DataFrame,
                  action: str = 'Loaded',
                  level: int = logging.INFO) -> None:
    """
    Log DataFrame shape (rows and columns).

    Args:
        logger: Logger instance
        name: Dataset/DataFrame name
        df: DataFrame to log shape of
        action: Action description (default: 'Loaded')
        level: Logging level (default: INFO)

    Examples:
        >>> log_data_shape(logger, 'input_data', df, action='Loaded')
        # Logs: "Loaded input_data: 1000 rows, 15 columns"
        >>> log_data_shape(logger, 'filtered_data', df, action='Created')
        # Logs: "Created filtered_data: 500 rows, 10 columns"

    Use Cases:
        # loaders.py:72 - Replace: logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        log_data_shape(logger, source_path.name, df, action='Loaded')

        # persistence.py:97 - Replace: logger.debug(f"Filtered {dataset_name} (analytical model): {len(df.columns)} → {len(cols_to_save)} columns")
        log_data_shape(logger, dataset_name, df_filtered, action='Filtered', level=logging.DEBUG)
    """
    rows = len(df)
    cols = len(df.columns)
    message = f"{action} {name}: {rows} rows, {cols} columns"
    logger.log(level, message)


def log_missing_column(logger: logging.Logger,
                      col: str,
                      available: Optional[List[str]] = None,
                      severity: str = 'error') -> None:
    """
    Log missing column with available columns.

    Args:
        logger: Logger instance
        col: Missing column name
        available: List of available columns (optional)
        severity: 'error' or 'warning'

    Examples:
        >>> log_missing_column(logger, 'missing_col', available=['col1', 'col2'])
        # Logs: "[FAIL] Column 'missing_col' not found"
        #       "[FAIL]   Available columns: ['col1', 'col2']"
        >>> log_missing_column(logger, 'optional_col', severity='warning')
        # Logs: "[WARN] Column 'optional_col' not found"

    Use Cases:
        # validators.py:184-185 - Replace multi-line error logging
        log_missing_column(logger, col, available=df.columns.tolist())
    """
    symbol = STATUS_ERROR if severity == 'error' else STATUS_WARNING
    log_func = logger.error if severity == 'error' else logger.warning

    log_func(f"{symbol} Column '{col}' not found")

    if available:
        log_func(f"{symbol}   Available columns: {available}")


def log_dependency_chain(logger: logging.Logger,
                        feature: str,
                        deps: List[str],
                        level: int = logging.DEBUG) -> None:
    """
    Log feature dependency resolution.

    Args:
        logger: Logger instance
        feature: Feature name
        deps: List of dependencies
        level: Logging level (default: DEBUG)

    Examples:
        >>> log_dependency_chain(logger, 'profit_margin', ['total_revenue', 'total_cost'])
        # Logs: "Resolved profit_margin -> [total_revenue, total_cost]"
        >>> log_dependency_chain(logger, 'basic_feature', [])
        # Logs: "Resolved basic_feature -> []"
    """
    deps_str = ', '.join(deps) if deps else 'no dependencies'
    logger.log(level, f"Resolved {feature} -> [{deps_str}]")


def log_feature_execution(logger: logging.Logger,
                         feature_name: str,
                         feature_type: str,
                         args_count: Optional[int] = None,
                         level: int = logging.DEBUG) -> None:
    """
    Log feature calculation execution.

    Args:
        logger: Logger instance
        feature_name: Name of feature being calculated
        feature_type: 'filter' or 'attribute'
        args_count: Number of arguments (optional)
        level: Logging level (default: DEBUG)

    Examples:
        >>> log_feature_execution(logger, 'margin_unit', 'filter', args_count=2)
        # Logs: "Executing filter 'margin_unit' (2 args)"
        >>> log_feature_execution(logger, 'total_revenue', 'attribute')
        # Logs: "Executing attribute 'total_revenue'"
    """
    if args_count is not None:
        message = f"Executing {feature_type} '{feature_name}' ({args_count} args)"
    else:
        message = f"Executing {feature_type} '{feature_name}'"

    logger.log(level, message)


def log_file_operation(logger: logging.Logger,
                      operation: str,
                      path: Any,
                      status: str = 'success',
                      level: Optional[int] = None) -> None:
    """
    Log file operations (read, write, create, delete).

    Args:
        logger: Logger instance
        operation: Operation description ('Saved', 'Loaded', 'Created', etc.)
        path: File path
        status: 'success', 'warning', 'error'
        level: Logging level (auto-determined if None)

    Examples:
        >>> log_file_operation(logger, 'Saved', '/path/to/file.csv', status='success')
        # Logs: "[OK] Saved: /path/to/file.csv"
        >>> log_file_operation(logger, 'Failed to load', '/path/to/file.csv', status='error')
        # Logs: "[FAIL] Failed to load: /path/to/file.csv"

    Use Cases:
        # file_utils.py:248 - Replace: logger.debug(f"Saved JSON to: {path_obj}")
        log_file_operation(logger, 'Saved JSON', path_obj, status='success', level=logging.DEBUG)

        # file_utils.py:318 - Replace: logger.debug(f"Loaded JSON from: {path_obj}")
        log_file_operation(logger, 'Loaded JSON', path_obj, status='success', level=logging.DEBUG)
    """
    # Determine status symbol and level
    if status == 'success':
        symbol = STATUS_SUCCESS
        default_level = logging.DEBUG
    elif status == 'warning':
        symbol = STATUS_WARNING
        default_level = logging.WARNING
    else:  # error
        symbol = STATUS_ERROR
        default_level = logging.ERROR

    level = level if level is not None else default_level

    message = f"{symbol} {operation}: {path}"
    logger.log(level, message)


def log_count_summary(logger: logging.Logger,
                     description: str,
                     count: int,
                     items: Optional[List[str]] = None,
                     level: int = logging.INFO,
                     max_items: int = 10) -> None:
    """
    Log count summary with optional item list.

    Args:
        logger: Logger instance
        description: Description of what's being counted
        count: Count value
        items: Optional list of items (will show first max_items)
        level: Logging level (default: INFO)
        max_items: Maximum number of items to show (default: 10)

    Examples:
        >>> log_count_summary(logger, 'models to export', 3, items=['model1', 'model2', 'model3'])
        # Logs: "Found 3 models to export: ['model1', 'model2', 'model3']"
        >>> log_count_summary(logger, 'errors', 15)
        # Logs: "Found 15 errors"

    Use Cases:
        # excel.py:130 - Replace: logger.info(f"Found {len(model_names)} models to export: {model_names}")
        log_count_summary(logger, 'models to export', len(model_names), items=model_names)

        # synthetic.py:125 - Replace: logger.info(f"Found {len(feature_index)} synthetic features...")
        log_count_summary(logger, 'synthetic features in feature store', len(feature_index))
    """
    message = f"Found {count} {description}"

    if items:
        if len(items) <= max_items:
            message += f": {items}"
        else:
            message += f": {items[:max_items]} ... ({len(items) - max_items} more)"

    logger.log(level, message)


def log_model_execution(logger: logging.Logger,
                       model_name: str,
                       action: str = 'Executing',
                       input_dataset: Optional[str] = None,
                       level: int = logging.INFO) -> None:
    """
    Log model execution with context.

    Args:
        logger: Logger instance
        model_name: Model name
        action: Action description ('Executing', 'Completed', etc.)
        input_dataset: Input dataset name (optional)
        level: Logging level (default: INFO)

    Examples:
        >>> log_model_execution(logger, 'model1', action='Executing', input_dataset='preprocessed')
        # Logs: "===== Executing Model: model1 ====="
        #       "Input dataset: preprocessed"
        >>> log_model_execution(logger, 'model1', action='Completed')
        # Logs: "===== Completed Model: model1 ====="
    """
    logger.log(level, f"===== {action} Model: {model_name} =====")

    if input_dataset:
        logger.log(level, f"Input dataset: {input_dataset}")


def log_progress(logger: logging.Logger,
                current: int,
                total: int,
                item_name: str = 'item',
                level: int = logging.INFO) -> None:
    """
    Log progress (current/total).

    Args:
        logger: Logger instance
        current: Current count
        total: Total count
        item_name: Name of items being processed
        level: Logging level (default: INFO)

    Examples:
        >>> log_progress(logger, 5, 10, item_name='model')
        # Logs: "Processing model 5/10"
        >>> log_progress(logger, 100, 100, item_name='row')
        # Logs: "Processing row 100/100"
    """
    message = f"Processing {item_name} {current}/{total}"
    logger.log(level, message)


# Module-level exports
__all__ = [
    'log_operation_start',
    'log_operation_complete',
    'log_validation_result',
    'log_data_shape',
    'log_missing_column',
    'log_dependency_chain',
    'log_feature_execution',
    'log_file_operation',
    'log_count_summary',
    'log_model_execution',
    'log_progress',
    # Status constants
    'STATUS_SUCCESS',
    'STATUS_WARNING',
    'STATUS_ERROR',
    'STATUS_INFO',
]
