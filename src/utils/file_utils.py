"""
File and Path Utilities for GabeDA

Single Responsibility: File/path operations and I/O utilities

Provides common patterns for:
- Path validation and creation
- Directory operations
- JSON file I/O
- Safe file operations with error handling

Usage:
    from src.utils.file_utils import ensure_path_exists, save_json

    # Ensure path exists (raises if not)
    path = ensure_path_exists('/path/to/file.csv', is_file=True)

    # Create directory if needed
    dir_path = ensure_directory('/path/to/output')

    # Save/load JSON
    save_json({'key': 'value'}, 'config.json')
    data = load_json('config.json')

Does NOT:
- Process file contents (use loaders/transformers)
- Validate data schemas (use validators)
"""

from pathlib import Path
from typing import Union, Dict, Any, List, Optional, Callable
import json
import logging


def ensure_path_exists(path: Union[str, Path],
                      is_file: bool = False,
                      logger: Optional[logging.Logger] = None) -> Path:
    """
    Ensure path exists, raise if not found.

    Args:
        path: Path to check (string or Path object)
        is_file: If True, check file exists; if False, check directory exists
        logger: Optional logger for error messages

    Returns:
        Path object (validated to exist)

    Raises:
        FileNotFoundError: If path does not exist

    Examples:
        >>> ensure_path_exists('/existing/file.csv', is_file=True)
        Path('/existing/file.csv')
        >>> ensure_path_exists('/missing/file.csv', is_file=True)
        # Raises FileNotFoundError
        >>> ensure_path_exists('/existing/dir', is_file=False)
        Path('/existing/dir')

    Use Cases:
        # Replace: if not path.exists(): raise FileNotFoundError(...)
        path = ensure_path_exists(path_str, is_file=True)

        # persistence.py:263-265
        state_path = ensure_path_exists(state_dir, is_file=False)

        # loaders.py:50
        source_path = ensure_path_exists(source, is_file=True)
    """
    path_obj = Path(path) if isinstance(path, str) else path

    if not path_obj.exists():
        item_type = "file" if is_file else "directory"
        error_msg = f"{item_type.capitalize()} not found: {path_obj}"

        if logger:
            logger.error(error_msg)

        raise FileNotFoundError(error_msg)

    return path_obj


def ensure_directory(path: Union[str, Path],
                    parents: bool = True,
                    exist_ok: bool = True,
                    logger: Optional[logging.Logger] = None) -> Path:
    """
    Create directory if it doesn't exist.

    Args:
        path: Directory path to create
        parents: If True, create parent directories as needed
        exist_ok: If True, don't raise error if directory exists
        logger: Optional logger for info messages

    Returns:
        Path object (created or existing directory)

    Raises:
        FileExistsError: If exist_ok=False and directory exists

    Examples:
        >>> ensure_directory('/path/to/output')
        Path('/path/to/output')
        >>> ensure_directory('/path/to/nested/output', parents=True)
        Path('/path/to/nested/output')

    Use Cases:
        # Replace: path.mkdir(parents=True, exist_ok=True)
        output_dir = ensure_directory(output_path)

        # persistence.py:156
        datasets_dir = ensure_directory(state_dir / 'datasets')

        # store.py:162
        feature_dir = ensure_directory(base_path / model / feature_name)
    """
    path_obj = Path(path) if isinstance(path, str) else path

    if not path_obj.exists():
        path_obj.mkdir(parents=parents, exist_ok=exist_ok)

        if logger:
            logger.debug(f"Created directory: {path_obj}")
    elif logger:
        logger.debug(f"Directory already exists: {path_obj}")

    return path_obj


def path_exists(path: Union[str, Path],
               is_file: Optional[bool] = None) -> bool:
    """
    Check if path exists with optional file/directory verification.

    Args:
        path: Path to check
        is_file: If True, check if file; if False, check if directory; if None, just check existence

    Returns:
        True if path exists and meets file/directory requirement

    Examples:
        >>> path_exists('/existing/file.csv')
        True
        >>> path_exists('/existing/file.csv', is_file=True)
        True
        >>> path_exists('/existing/file.csv', is_file=False)
        False  # It's a file, not a directory
        >>> path_exists('/missing/file.csv')
        False
    """
    path_obj = Path(path) if isinstance(path, str) else path

    if not path_obj.exists():
        return False

    if is_file is None:
        return True
    elif is_file:
        return path_obj.is_file()
    else:
        return path_obj.is_dir()


def find_matching_dirs(base_dir: Union[str, Path],
                      pattern: str,
                      logger: Optional[logging.Logger] = None) -> List[Path]:
    """
    Find directories matching a pattern within base directory.

    Args:
        base_dir: Base directory to search
        pattern: Glob pattern to match (e.g., 'model_*', '2024*')
        logger: Optional logger for debug messages

    Returns:
        List of matching directory paths (sorted)

    Examples:
        >>> find_matching_dirs('/outputs', 'run_*')
        [Path('/outputs/run_001'), Path('/outputs/run_002')]
        >>> find_matching_dirs('/features', 'common')
        [Path('/features/common')]
    """
    base_path = Path(base_dir) if isinstance(base_dir, str) else base_dir

    if not base_path.exists():
        if logger:
            logger.warning(f"Base directory does not exist: {base_path}")
        return []

    matching = [p for p in base_path.glob(pattern) if p.is_dir()]
    matching.sort()

    if logger:
        logger.debug(f"Found {len(matching)} directories matching '{pattern}' in {base_path}")

    return matching


def save_json(data: Dict[str, Any],
             path: Union[str, Path],
             indent: int = 2,
             encoding: str = 'utf-8',
             logger: Optional[logging.Logger] = None) -> None:
    """
    Save dictionary as JSON file with error handling.

    Args:
        data: Dictionary to save
        path: Output file path
        indent: JSON indentation (default: 2)
        encoding: File encoding (default: 'utf-8')
        logger: Optional logger for info/error messages

    Raises:
        IOError: If file cannot be written
        TypeError: If data is not JSON-serializable

    Examples:
        >>> save_json({'name': 'test', 'value': 42}, 'config.json')
        >>> save_json(metadata, output_dir / 'metadata.json', indent=4)

    Use Cases:
        # Replace: with open(..., 'w') as f: json.dump(data, f, indent=2)
        save_json(metadata, metadata_path)

        # persistence.py:204-205
        save_json(metadata, state_dir / 'metadata.json')

        # store.py:224-225
        save_json(feature_metadata, metadata_file)
    """
    path_obj = Path(path) if isinstance(path, str) else path

    try:
        # Ensure parent directory exists
        if not path_obj.parent.exists():
            path_obj.parent.mkdir(parents=True, exist_ok=True)

        with open(path_obj, 'w', encoding=encoding) as f:
            json.dump(data, f, indent=indent)

        if logger:
            logger.debug(f"Saved JSON to: {path_obj}")

    except (IOError, OSError) as e:
        error_msg = f"Failed to save JSON to {path_obj}: {e}"
        if logger:
            logger.error(error_msg)
        raise IOError(error_msg) from e
    except TypeError as e:
        error_msg = f"Data is not JSON-serializable: {e}"
        if logger:
            logger.error(error_msg)
        raise TypeError(error_msg) from e


def load_json(path: Union[str, Path],
             encoding: str = 'utf-8',
             default: Optional[Dict] = None,
             logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """
    Load JSON file with error handling.

    Args:
        path: JSON file path
        encoding: File encoding (default: 'utf-8')
        default: Default value if file not found (if None, raises error)
        logger: Optional logger for info/error messages

    Returns:
        Loaded dictionary

    Raises:
        FileNotFoundError: If file not found and default is None
        json.JSONDecodeError: If file is not valid JSON

    Examples:
        >>> load_json('config.json')
        {'name': 'test', 'value': 42}
        >>> load_json('missing.json', default={})
        {}
        >>> load_json('missing.json')
        # Raises FileNotFoundError

    Use Cases:
        # Replace: with open(..., 'r') as f: data = json.load(f)
        config = load_json(config_path)

        # persistence.py:273-274
        metadata = load_json(state_dir / 'metadata.json')

        # store.py:284-285
        feature_meta = load_json(metadata_file)
    """
    path_obj = Path(path) if isinstance(path, str) else path

    if not path_obj.exists():
        if default is not None:
            if logger:
                logger.debug(f"JSON file not found, using default: {path_obj}")
            return default
        else:
            error_msg = f"JSON file not found: {path_obj}"
            if logger:
                logger.error(error_msg)
            raise FileNotFoundError(error_msg)

    try:
        with open(path_obj, 'r', encoding=encoding) as f:
            data = json.load(f)

        if logger:
            logger.debug(f"Loaded JSON from: {path_obj}")

        return data

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in {path_obj}: {e}"
        if logger:
            logger.error(error_msg)
        raise json.JSONDecodeError(error_msg, e.doc, e.pos) from e
    except (IOError, OSError) as e:
        error_msg = f"Failed to load JSON from {path_obj}: {e}"
        if logger:
            logger.error(error_msg)
        raise IOError(error_msg) from e


def safe_file_operation(operation: Callable,
                       path: Union[str, Path],
                       logger: Optional[logging.Logger] = None,
                       operation_name: str = "file operation",
                       **kwargs) -> Any:
    """
    Wrapper for file operations with standardized error handling.

    Args:
        operation: Function to execute (receives path as first argument)
        path: File path to operate on
        logger: Optional logger for error messages
        operation_name: Human-readable operation name for errors
        **kwargs: Additional arguments to pass to operation

    Returns:
        Result of operation

    Raises:
        IOError: If operation fails

    Examples:
        >>> def read_lines(p): return open(p).readlines()
        >>> lines = safe_file_operation(read_lines, 'file.txt', operation_name='read')
        >>> # If fails, logs: "Failed to read file file.txt: [error]"
    """
    path_obj = Path(path) if isinstance(path, str) else path

    try:
        return operation(path_obj, **kwargs)
    except (IOError, OSError) as e:
        error_msg = f"Failed to {operation_name} file {path_obj}: {e}"
        if logger:
            logger.error(error_msg)
        raise IOError(error_msg) from e


def get_file_size(path: Union[str, Path],
                 logger: Optional[logging.Logger] = None) -> int:
    """
    Get file size in bytes.

    Args:
        path: File path
        logger: Optional logger for error messages

    Returns:
        File size in bytes

    Raises:
        FileNotFoundError: If file does not exist

    Examples:
        >>> get_file_size('data.csv')
        1024567
    """
    path_obj = ensure_path_exists(path, is_file=True, logger=logger)
    return path_obj.stat().st_size


def normalize_path(path: Union[str, Path]) -> Path:
    """
    Normalize path to absolute Path object.

    Args:
        path: Path to normalize (string or Path)

    Returns:
        Absolute Path object

    Examples:
        >>> normalize_path('data/file.csv')
        Path('/absolute/path/to/data/file.csv')
        >>> normalize_path(Path('data/file.csv'))
        Path('/absolute/path/to/data/file.csv')
    """
    path_obj = Path(path) if isinstance(path, str) else path
    return path_obj.resolve()


# Module-level exports
__all__ = [
    'ensure_path_exists',
    'ensure_directory',
    'path_exists',
    'find_matching_dirs',
    'save_json',
    'load_json',
    'safe_file_operation',
    'get_file_size',
    'normalize_path',
]
