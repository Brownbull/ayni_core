"""
Dictionary Utilities for GabeDA

Single Responsibility: Dictionary access, normalization, and manipulation utilities

Provides common patterns for:
- Safe dictionary access with defaults and logging
- Value normalization (especially list conversion)
- Dictionary merging and filtering
- Nested dictionary access

Usage:
    from src.utils.dict_utils import safe_get, normalize_to_list

    # Safe access with default
    value = safe_get(config, 'key', default='default_value')

    # Normalize to list
    items = normalize_to_list(config.get('group_by'))  # Handles None, [], '', 'value', ['value']

Does NOT:
- Validate dictionary contents (use validation_utils)
- Process configuration schemas (use config module)
"""

from typing import Dict, Any, List, Optional, Union
import logging


def safe_get(d: Dict, key: str, default: Any = None,
             logger: Optional[logging.Logger] = None,
             warn_missing: bool = False) -> Any:
    """
    Safe dictionary access with optional logging.

    Args:
        d: Dictionary to access
        key: Key to retrieve
        default: Default value if key not found
        logger: Optional logger for warnings
        warn_missing: If True, log warning when key is missing

    Returns:
        Value from dictionary or default

    Examples:
        >>> config = {'name': 'test', 'count': 5}
        >>> safe_get(config, 'name')
        'test'
        >>> safe_get(config, 'missing', default='default')
        'default'
        >>> safe_get(config, 'missing', warn_missing=True, logger=my_logger)
        # Logs warning and returns None
    """
    value = d.get(key, default)

    if value is None and warn_missing and logger:
        logger.warning(f"Key '{key}' not found in dictionary, using default: {default}")

    return value


def normalize_to_list(value: Any,
                     empty_indicators: List[Any] = None,
                     to_none: bool = False) -> Union[List, None]:
    """
    Normalize value to list, handling None, empty strings, empty lists, and single values.

    This is the CANONICAL implementation for group_by normalization and similar patterns.

    Args:
        value: Value to normalize (can be None, '', [], 'value', or ['value1', 'value2'])
        empty_indicators: List of values to treat as empty (default: [None, '', []])
        to_none: If True, return None for empty values instead of []

    Returns:
        List, empty list, or None depending on input and to_none flag

    Examples:
        >>> normalize_to_list(None)
        []
        >>> normalize_to_list('')
        []
        >>> normalize_to_list([])
        []
        >>> normalize_to_list('product')
        ['product']
        >>> normalize_to_list(['product', 'date'])
        ['product', 'date']
        >>> normalize_to_list(None, to_none=True)
        None
        >>> normalize_to_list('', to_none=True)
        None

    Use Cases:
        # executor.py pattern (convert empty to None)
        group_by = normalize_to_list(cfg_model.get('group_by'), to_none=True)
        cfg_model['group_by'] = group_by

        # resolver.py pattern (convert empty to [])
        group_by = normalize_to_list(cfg_model.get('group_by'))
    """
    if empty_indicators is None:
        empty_indicators = [None, '', []]

    # Check if value is considered empty
    if value in empty_indicators:
        return None if to_none else []

    # If already a list, return as-is
    if isinstance(value, list):
        return value

    # Single value - wrap in list
    return [value]


def merge_dicts(base: Dict, updates: Dict, mutate: bool = False) -> Dict:
    """
    Merge two dictionaries with optional mutation.

    Args:
        base: Base dictionary
        updates: Dictionary with updates to apply
        mutate: If True, modify base dict in place; if False, create copy

    Returns:
        Merged dictionary (either base or new dict depending on mutate flag)

    Examples:
        >>> base = {'a': 1, 'b': 2}
        >>> updates = {'b': 3, 'c': 4}
        >>> merge_dicts(base, updates, mutate=False)
        {'a': 1, 'b': 3, 'c': 4}
        >>> base  # Unchanged
        {'a': 1, 'b': 2}
        >>> merge_dicts(base, updates, mutate=True)
        {'a': 1, 'b': 3, 'c': 4}
        >>> base  # Modified
        {'a': 1, 'b': 3, 'c': 4}
    """
    if mutate:
        base.update(updates)
        return base
    else:
        result = base.copy()
        result.update(updates)
        return result


def get_nested(d: Dict, *keys, default: Any = None) -> Any:
    """
    Get value from nested dictionary with fallback.

    Args:
        d: Dictionary to access
        *keys: Sequence of keys to traverse (e.g., 'config', 'model', 'name')
        default: Default value if any key not found

    Returns:
        Value from nested dict or default

    Examples:
        >>> config = {'model': {'name': 'test', 'params': {'lr': 0.01}}}
        >>> get_nested(config, 'model', 'name')
        'test'
        >>> get_nested(config, 'model', 'params', 'lr')
        0.01
        >>> get_nested(config, 'model', 'missing', default='default')
        'default'
        >>> get_nested(config, 'missing', 'key', default=None)
        None
    """
    current = d
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def filter_dict_by_keys(d: Dict, keys_to_keep: List[str],
                        safe: bool = True) -> Dict:
    """
    Filter dictionary to only specified keys.

    Args:
        d: Dictionary to filter
        keys_to_keep: Keys to include in result
        safe: If True, ignore missing keys; if False, raise KeyError

    Returns:
        New dictionary with only specified keys

    Raises:
        KeyError: If safe=False and a key is missing

    Examples:
        >>> data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        >>> filter_dict_by_keys(data, ['a', 'c'])
        {'a': 1, 'c': 3}
        >>> filter_dict_by_keys(data, ['a', 'missing'], safe=True)
        {'a': 1}
        >>> filter_dict_by_keys(data, ['a', 'missing'], safe=False)
        # Raises KeyError
    """
    if safe:
        return {k: d[k] for k in keys_to_keep if k in d}
    else:
        return {k: d[k] for k in keys_to_keep}


def get_or_raise(d: Dict, key: str,
                error_class: type = KeyError,
                message: Optional[str] = None) -> Any:
    """
    Get dictionary value or raise custom error.

    Args:
        d: Dictionary to access
        key: Key to retrieve
        error_class: Exception class to raise if key missing
        message: Custom error message (default: "Key '{key}' not found")

    Returns:
        Value from dictionary

    Raises:
        error_class: If key not found in dictionary

    Examples:
        >>> config = {'name': 'test'}
        >>> get_or_raise(config, 'name')
        'test'
        >>> get_or_raise(config, 'missing')
        # Raises KeyError: "Key 'missing' not found"
        >>> get_or_raise(config, 'missing', ValueError, "Config missing required key")
        # Raises ValueError: "Config missing required key"
    """
    if key not in d:
        if message is None:
            message = f"Key '{key}' not found"
        raise error_class(message)
    return d[key]


def has_all_keys(d: Dict, required_keys: List[str]) -> bool:
    """
    Check if dictionary has all required keys.

    Args:
        d: Dictionary to check
        required_keys: List of keys that must be present

    Returns:
        True if all keys present, False otherwise

    Examples:
        >>> config = {'name': 'test', 'version': 1, 'enabled': True}
        >>> has_all_keys(config, ['name', 'version'])
        True
        >>> has_all_keys(config, ['name', 'missing'])
        False
        >>> has_all_keys(config, [])
        True
    """
    return all(key in d for key in required_keys)


def get_missing_keys(d: Dict, required_keys: List[str]) -> List[str]:
    """
    Get list of missing required keys.

    Args:
        d: Dictionary to check
        required_keys: List of keys that should be present

    Returns:
        List of missing keys (empty if all present)

    Examples:
        >>> config = {'name': 'test', 'version': 1}
        >>> get_missing_keys(config, ['name', 'version', 'enabled'])
        ['enabled']
        >>> get_missing_keys(config, ['name', 'version'])
        []
    """
    return [key for key in required_keys if key not in d]


def invert_dict(d: Dict) -> Dict:
    """
    Invert dictionary (swap keys and values).

    Args:
        d: Dictionary to invert

    Returns:
        New dictionary with keys and values swapped

    Note:
        If values are not unique, later entries will overwrite earlier ones.

    Examples:
        >>> mapping = {'a': 1, 'b': 2, 'c': 3}
        >>> invert_dict(mapping)
        {1: 'a', 2: 'b', 3: 'c'}
        >>> invert_dict({'a': 1, 'b': 1})  # Non-unique values
        {1: 'b'}  # Last entry wins
    """
    return {v: k for k, v in d.items()}


# Module-level exports
__all__ = [
    'safe_get',
    'normalize_to_list',
    'merge_dicts',
    'get_nested',
    'filter_dict_by_keys',
    'get_or_raise',
    'has_all_keys',
    'get_missing_keys',
    'invert_dict',
]
