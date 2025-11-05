"""
Error Handling Utilities for GabeDA

Single Responsibility: Standardized error handling patterns

Provides utilities for:
- Safe function execution with error handling
- Context managers for error handling
- Error result creation
- Standardized error logging

Usage:
    from src.utils.error_utils import safe_execute, error_context

    # Safe execution
    result = safe_execute(risky_function, arg1, arg2, logger=logger)

    # Error context
    with error_context('Loading data', logger=logger):
        df = load_data(path)

Does NOT:
- Validate data (use validation_utils)
- Process errors (just handles them)
"""

from typing import Callable, Any, Optional, Dict
from contextlib import contextmanager
import logging
from src.core.results import OperationResult


def safe_execute(func: Callable,
                *args,
                default: Any = None,
                logger: Optional[logging.Logger] = None,
                context: str = "",
                **kwargs) -> Any:
    """
    Execute function with error handling and logging.

    Args:
        func: Function to execute
        *args: Positional arguments for function
        default: Default value to return on error
        logger: Optional logger for error messages
        context: Context description for error messages
        **kwargs: Keyword arguments for function

    Returns:
        Function result or default value on error

    Examples:
        >>> result = safe_execute(int, '123', default=0)
        >>> result  # 123
        >>> result = safe_execute(int, 'abc', default=0, logger=logger)
        >>> result  # 0 (logged error)
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_msg = f"{context}: {e}" if context else str(e)
        if logger:
            logger.error(error_msg)
        return default


@contextmanager
def error_context(operation: str,
                 logger: Optional[logging.Logger] = None,
                 raise_on_error: bool = True):
    """
    Context manager for consistent error handling.

    Args:
        operation: Operation description
        logger: Optional logger
        raise_on_error: If True, re-raise errors; if False, suppress

    Yields:
        None

    Examples:
        >>> with error_context('Loading data', logger=logger):
        ...     df = pd.read_csv('data.csv')
        # Logs: "Error in Loading data: [error message]"

    Usage:
        # Re-raise errors (default)
        with error_context('Processing', logger=logger):
            process_data()

        # Suppress errors
        with error_context('Optional operation', logger=logger, raise_on_error=False):
            optional_operation()
    """
    try:
        yield
    except Exception as e:
        error_msg = f"Error in {operation}: {e}"
        if logger:
            logger.error(error_msg)
        if raise_on_error:
            raise


def create_error_result(error: Exception,
                       operation: str,
                       context: Optional[Dict[str, Any]] = None) -> OperationResult:
    """
    Create standardized error result from exception.

    Args:
        error: Exception that occurred
        operation: Operation description
        context: Optional context dict

    Returns:
        OperationResult with error details

    Examples:
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     result = create_error_result(e, 'Data loading')
        >>> result.success  # False
        >>> result.errors  # ['Data loading failed: [error]']
    """
    result = OperationResult(success=False)
    result.add_error(f"{operation} failed: {str(error)}")

    if context:
        result.metadata.update(context)
        result.metadata['error_type'] = type(error).__name__

    return result


def handle_file_error(error: Exception,
                     path: Any,
                     operation: str,
                     logger: Optional[logging.Logger] = None) -> None:
    """
    Standardized file error handling.

    Args:
        error: Exception that occurred
        path: File path
        operation: Operation description ('read', 'write', etc.)
        logger: Optional logger

    Examples:
        >>> try:
        ...     with open('missing.txt') as f:
        ...         data = f.read()
        ... except Exception as e:
        ...     handle_file_error(e, 'missing.txt', 'read', logger)
    """
    error_msg = f"Failed to {operation} file '{path}': {error}"
    if logger:
        logger.error(error_msg)


def handle_data_error(error: Exception,
                     context: str,
                     logger: Optional[logging.Logger] = None,
                     raise_after_log: bool = True) -> None:
    """
    Standardized data processing error handling.

    Args:
        error: Exception that occurred
        context: Context description
        logger: Optional logger
        raise_after_log: If True, re-raise error after logging

    Examples:
        >>> try:
        ...     df = process_data(raw_data)
        ... except Exception as e:
        ...     handle_data_error(e, 'Processing raw data', logger)
    """
    error_msg = f"Data error in {context}: {error}"
    if logger:
        logger.error(error_msg)
        logger.error(f"Error type: {type(error).__name__}")

    if raise_after_log:
        raise


def try_or_none(func: Callable, *args, **kwargs) -> Optional[Any]:
    """
    Execute function, return None on any error (silent).

    Args:
        func: Function to execute
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Function result or None on error

    Examples:
        >>> result = try_or_none(int, '123')
        >>> result  # 123
        >>> result = try_or_none(int, 'abc')
        >>> result  # None (no error logged)
    """
    try:
        return func(*args, **kwargs)
    except:
        return None


def try_or_default(func: Callable, default: Any, *args, **kwargs) -> Any:
    """
    Execute function, return default on any error (silent).

    Args:
        func: Function to execute
        default: Default value to return on error
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Function result or default on error

    Examples:
        >>> result = try_or_default(int, 0, '123')
        >>> result  # 123
        >>> result = try_or_default(int, 0, 'abc')
        >>> result  # 0
    """
    try:
        return func(*args, **kwargs)
    except:
        return default


# Module-level exports
__all__ = [
    'safe_execute',
    'error_context',
    'create_error_result',
    'handle_file_error',
    'handle_data_error',
    'try_or_none',
    'try_or_default',
]
