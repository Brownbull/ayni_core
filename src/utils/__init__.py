"""
Utilities package for GabeDA Analytics.
"""

from src.utils.logger import setup_logging, get_logger, get_current_level
from src.utils.dict_utils import (
    safe_get,
    normalize_to_list,
    merge_dicts,
    get_nested,
    filter_dict_by_keys,
    get_or_raise,
    has_all_keys,
    get_missing_keys,
    invert_dict,
)
from src.utils.file_utils import (
    ensure_path_exists,
    ensure_directory,
    path_exists,
    find_matching_dirs,
    save_json,
    load_json,
    safe_file_operation,
    get_file_size,
    normalize_path,
)
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
from src.utils.log_utils import (
    log_operation_start,
    log_operation_complete,
    log_validation_result,
    log_data_shape,
    log_missing_column,
    log_dependency_chain,
    log_feature_execution,
    log_file_operation,
    log_count_summary,
    log_model_execution,
    log_progress,
    STATUS_SUCCESS,
    STATUS_WARNING,
    STATUS_ERROR,
    STATUS_INFO,
)
from src.utils.validation_utils import (
    validate_dataframe,
    validate_required_keys,
    validate_mutually_exclusive,
    validate_value_range,
    validate_list_not_empty,
    validate_all,
)
from src.utils.error_utils import (
    safe_execute,
    error_context,
    create_error_result,
    handle_file_error,
    handle_data_error,
    try_or_none,
    try_or_default,
)

__all__ = [
    # Logger utilities
    'setup_logging',
    'get_logger',
    'get_current_level',
    # Dictionary utilities
    'safe_get',
    'normalize_to_list',
    'merge_dicts',
    'get_nested',
    'filter_dict_by_keys',
    'get_or_raise',
    'has_all_keys',
    'get_missing_keys',
    'invert_dict',
    # File utilities
    'ensure_path_exists',
    'ensure_directory',
    'path_exists',
    'find_matching_dirs',
    'save_json',
    'load_json',
    'safe_file_operation',
    'get_file_size',
    'normalize_path',
    # Column utilities
    'select_columns_safe',
    'filter_columns',
    'build_column_list',
    'ensure_columns_exist',
    'deduplicate_columns',
    'get_columns_by_pattern',
    'get_column_diff',
    'validate_column_subset',
    # Log utilities
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
    'STATUS_SUCCESS',
    'STATUS_WARNING',
    'STATUS_ERROR',
    'STATUS_INFO',
    # Validation utilities
    'validate_dataframe',
    'validate_required_keys',
    'validate_mutually_exclusive',
    'validate_value_range',
    'validate_list_not_empty',
    'validate_all',
    # Error utilities
    'safe_execute',
    'error_context',
    'create_error_result',
    'handle_file_error',
    'handle_data_error',
    'try_or_none',
    'try_or_default',
]
