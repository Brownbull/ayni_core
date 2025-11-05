"""
GabeDA Context Persistence - State Serialization & Loading

This module provides functionality to save and load GabedaContext state
between notebook executions, enabling multi-stage analytics pipelines.

Responsibilities:
- Serialize context datasets to CSV files
- Save configuration and metadata as JSON
- Reconstruct context from saved state
- Find latest state for a given client

Does NOT:
- Transform or modify data (use preprocessing)
- Execute models (use execution package)
"""

import os
import json
import pandas as pd
from typing import Dict, Any, Tuple, Optional
from pathlib import Path
from datetime import datetime
from src.utils.logger import get_logger
from src.utils import (
    build_column_list, normalize_to_list,
    ensure_directory, save_json, load_json,
    log_file_operation, log_data_shape
)
from src.core.context import GabedaContext

logger = get_logger(__name__)


def _get_columns_to_save(
    dataset_name: str,
    df: pd.DataFrame,
    ctx: GabedaContext
) -> list:
    """
    Determine which columns to save for a dataset based on model configuration.

    For ANALYTICAL model outputs (models WITH group_by):
    - Apply column filtering based on in_cols
    - These are aggregated results, not needed as full inputs downstream

    For DATA ENRICHMENT model outputs (models WITHOUT group_by):
    - Save ALL columns (no filtering)
    - These are row-level enrichments needed downstream

    For other datasets (raw inputs, preprocessed):
    - Save all columns

    Args:
        dataset_name: Name of the dataset
        df: DataFrame to filter
        ctx: GabedaContext with model metadata

    Returns:
        List of column names to save
    """
    # Check if this is a model output dataset
    if '_filters' in dataset_name or '_attrs' in dataset_name:
        # Extract model name
        model_name = dataset_name.replace('_filters', '').replace('_attrs', '')

        # Get model metadata
        model_info = ctx.models.get(model_name)
        if model_info and model_info.get('cfg_model'):
            cfg_model = model_info['cfg_model']
            group_by = cfg_model.get('group_by')

            # ONLY apply filtering for ANALYTICAL models (those WITH group_by)
            # Data enrichment models (NO group_by) should save ALL columns
            group_by_normalized = normalize_to_list(group_by)
            if group_by_normalized:  # Has group_by - analytical model
                # This is an ANALYTICAL model - apply column filtering
                in_cols = cfg_model.get('in_cols', [])

                if in_cols:
                    # Build column list: start with in_cols, exclude row_id and group_by, filter to available
                    row_id = cfg_model.get('row_id')
                    exclude_cols = normalize_to_list(row_id) + group_by_normalized

                    cols_to_save = build_column_list(
                        base_cols=in_cols,
                        exclude=exclude_cols,
                        available_cols=df.columns.tolist(),
                        deduplicate=True
                    )

                    logger.debug(f"Filtered {dataset_name} (analytical model): {len(df.columns)} → {len(cols_to_save)} columns")
                    return cols_to_save
            else:
                # This is a DATA ENRICHMENT model (no group_by) - save ALL columns
                logger.debug(f"Saving all columns for {dataset_name} (data enrichment model)")
                return list(df.columns)

    # Default: save all columns
    return list(df.columns)


def save_context_state(
    ctx: GabedaContext,
    base_cfg: Dict[str, Any],
    output_base: str = 'data/context_states',
    reuse_existing: bool = True
) -> str:
    """
    Save complete context state to disk for later reuse.

    Creates or updates a directory containing:
    - context_metadata.json: run_id, timestamp, dataset names
    - config.json: base configuration
    - datasets/{name}.csv: individual dataset files

    Args:
        ctx: GabedaContext instance to save
        base_cfg: Base configuration dictionary
        output_base: Base directory for context_states data (default: 'data/context_states')
        reuse_existing: If True, reuse existing context folder for same client (default: True)

    Returns:
        Path to the saved state directory

    Example:
        >>> state_dir = save_context_state(ctx, base_cfg)
        >>> print(f"State saved to: {state_dir}")
    """
    client_name = base_cfg.get('client', 'unknown')

    # Check if we should reuse existing context folder
    existing_state = None
    if reuse_existing:
        existing_state = get_latest_state(client_name, base_dir=output_base)
        if existing_state:
            logger.info(f"Found existing context: {existing_state}")
            logger.info(f"Reusing existing context folder (adding/updating datasets)")
            # Use the existing folder instead of creating new one
            state_dir = Path(existing_state)
        else:
            logger.info(f"No existing context found, creating new one")
            state_dir = Path(output_base) / ctx.run_id
    else:
        # Create new context with current run_id
        state_dir = Path(output_base) / ctx.run_id

    datasets_dir = ensure_directory(state_dir / 'datasets', logger=logger)
    logger.info(f"Saving context state to: {state_dir}")

    # 1. Save metadata
    metadata = {
        'run_id': ctx.run_id,
        'timestamp': ctx.now.isoformat(),
        'client': base_cfg.get('client', 'unknown'),
        'datasets': list(ctx.datasets.keys()),
        'models': list(ctx.models.keys()),
        'total_datasets': len(ctx.datasets),
        'total_models': len(ctx.models),
        'dataset_shapes': {name: list(df.shape) for name, df in ctx.datasets.items()},
        'dataset_dtypes': {},  # Will store column dtypes for reconstruction
        'saved_at': datetime.now().isoformat()
    }

    # 2. Save datasets as CSV with dtype metadata
    for dataset_name, df in ctx.datasets.items():
        csv_path = datasets_dir / f"{dataset_name}.csv"

        # Determine which columns to save based on model config
        cols_to_save = _get_columns_to_save(dataset_name, df, ctx)

        # Filter dataframe to only include columns we want to save
        df_to_save = df[cols_to_save].copy() if cols_to_save else df

        # Save CSV
        df_to_save.to_csv(csv_path, index=False)
        logger.debug(f"Saved dataset: {dataset_name} -> {csv_path} ({len(cols_to_save)} columns)")

        # Store dtype information for proper reconstruction
        dtype_info = {}
        for col in df_to_save.columns:
            dtype_str = str(df_to_save[col].dtype)
            # Special handling for datetime
            if pd.api.types.is_datetime64_any_dtype(df_to_save[col]):
                dtype_info[col] = {'type': 'datetime64', 'format': 'iso8601'}
            elif dtype_str.startswith('datetime'):
                dtype_info[col] = {'type': 'datetime64', 'format': 'iso8601'}
            else:
                dtype_info[col] = {'type': dtype_str}

        metadata['dataset_dtypes'][dataset_name] = dtype_info

    # Save metadata JSON
    metadata_path = state_dir / 'context_metadata.json'
    save_json(metadata, metadata_path, logger=logger)

    # 3. Save configuration
    config_path = state_dir / 'config.json'

    # Create a JSON-serializable version of base_cfg
    serializable_cfg = {}
    for key, value in base_cfg.items():
        if isinstance(value, (str, int, float, bool, list, dict, type(None))):
            serializable_cfg[key] = value
        else:
            serializable_cfg[key] = str(value)

    with open(config_path, 'w') as f:
        json.dump(serializable_cfg, f, indent=2)
    logger.debug(f"Saved config: {config_path}")

    # 4. Save execution history
    history_path = state_dir / 'execution_history.json'
    with open(history_path, 'w') as f:
        json.dump(ctx.history, f, indent=2)
    logger.debug(f"Saved execution history: {history_path}")

    logger.info(f"✓ Context state saved successfully")
    logger.info(f"  - Location: {state_dir}")
    logger.info(f"  - Datasets: {len(ctx.datasets)}")
    logger.info(f"  - Models: {len(ctx.models)}")
    if existing_state:
        logger.info(f"  - Reused existing context (updated datasets)")

    return str(state_dir)


def load_context_state(state_dir: str) -> Tuple[GabedaContext, Dict[str, Any]]:
    """
    Load context state from a previously saved directory.

    Reconstructs:
    - GabedaContext with all datasets
    - Base configuration

    Args:
        state_dir: Path to saved state directory

    Returns:
        Tuple of (GabedaContext, base_cfg)

    Raises:
        FileNotFoundError: If state directory or required files don't exist
        ValueError: If state data is corrupted or invalid

    Example:
        >>> ctx, base_cfg = load_context_state('data/intermediate/01_transactions_20251018_174236')
        >>> enriched = ctx.get_dataset('transactions_enriched')
    """
    state_path = Path(state_dir)

    if not state_path.exists():
        raise FileNotFoundError(f"State directory not found: {state_dir}")

    logger.info(f"Loading context state from: {state_dir}")

    # 1. Load metadata
    metadata_path = state_path / 'context_metadata.json'
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    logger.debug(f"Loaded metadata: {metadata['run_id']}")

    # 2. Load configuration
    config_path = state_path / 'config.json'
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        base_cfg = json.load(f)

    logger.debug(f"Loaded config with {len(base_cfg)} keys")

    # 3. Create new context with loaded config
    # Note: This will generate a NEW run_id, but we'll preserve the original in metadata
    ctx = GabedaContext(base_cfg)

    # Store original run_id as metadata
    ctx.original_run_id = metadata['run_id']
    ctx.loaded_from = str(state_path)
    ctx.original_timestamp = metadata['timestamp']

    logger.debug(f"Created new context: {ctx.run_id} (loaded from {metadata['run_id']})")

    # 4. Load all datasets
    datasets_dir = state_path / 'datasets'
    if not datasets_dir.exists():
        raise FileNotFoundError(f"Datasets directory not found: {datasets_dir}")

    dtype_mapping = metadata.get('dataset_dtypes', {})

    for dataset_name in metadata['datasets']:
        csv_path = datasets_dir / f"{dataset_name}.csv"

        if not csv_path.exists():
            logger.warning(f"Dataset file not found: {csv_path}, skipping")
            continue

        # Load CSV with proper dtype handling
        dtype_info = dtype_mapping.get(dataset_name, {})

        # Separate datetime columns from others
        datetime_cols = [col for col, info in dtype_info.items()
                        if info.get('type') == 'datetime64']

        # Build dtype dict for non-datetime columns
        dtypes = {}
        for col, info in dtype_info.items():
            dtype_type = info.get('type')
            if dtype_type and dtype_type != 'datetime64':
                # Try to convert string dtype to actual dtype
                if dtype_type == 'object':
                    dtypes[col] = 'object'
                elif dtype_type.startswith('float'):
                    dtypes[col] = 'float64'
                elif dtype_type.startswith('int'):
                    dtypes[col] = 'int64'
                elif dtype_type == 'bool':
                    dtypes[col] = 'bool'

        # Load DataFrame
        df = pd.read_csv(
            csv_path,
            dtype=dtypes if dtypes else None,
            parse_dates=datetime_cols if datetime_cols else False
        )

        # Store in context
        ctx.set_dataset(dataset_name, df, metadata={
            'loaded_from': str(csv_path),
            'original_shape': metadata['dataset_shapes'].get(dataset_name)
        })

        logger.debug(f"Loaded dataset: {dataset_name} with shape {df.shape}")

    # 5. Load execution history (optional)
    history_path = state_path / 'execution_history.json'
    if history_path.exists():
        with open(history_path, 'r') as f:
            original_history = json.load(f)
        # Append to new context's history
        ctx.history.insert(0, {
            'action': 'loaded_from_state',
            'original_run_id': metadata['run_id'],
            'state_dir': str(state_path),
            'timestamp': datetime.now().isoformat()
        })
        ctx.original_history = original_history
        logger.debug(f"Loaded execution history with {len(original_history)} entries")

    logger.info(f"✓ Context state loaded successfully")
    logger.info(f"  - Original run_id: {metadata['run_id']}")
    logger.info(f"  - New run_id: {ctx.run_id}")
    logger.info(f"  - Datasets loaded: {len(ctx.datasets)}")
    logger.info(f"  - Available datasets: {list(ctx.datasets.keys())}")

    return ctx, base_cfg


def get_latest_state(
    client_name: str,
    base_dir: str = 'data/intermediate'
) -> Optional[str]:
    """
    Find the most recent state directory for a given client.

    Args:
        client_name: Client identifier (e.g., '01_transactions')
        base_dir: Base directory for intermediate data

    Returns:
        Path to latest state directory, or None if not found

    Example:
        >>> latest = get_latest_state('01_transactions')
        >>> if latest:
        ...     ctx, cfg = load_context_state(latest)
    """
    base_path = Path(base_dir)

    if not base_path.exists():
        logger.warning(f"Base directory not found: {base_dir}")
        return None

    # Find all directories matching client_name pattern
    pattern = f"{client_name}_*"
    matching_dirs = sorted(base_path.glob(pattern), reverse=True)

    if not matching_dirs:
        logger.warning(f"No state directories found for client: {client_name}")
        return None

    latest_dir = matching_dirs[0]
    logger.info(f"Latest state for '{client_name}': {latest_dir}")

    return str(latest_dir)


def list_available_states(base_dir: str = 'data/intermediate') -> Dict[str, list]:
    """
    List all available saved states grouped by client.

    Args:
        base_dir: Base directory for intermediate data

    Returns:
        Dictionary mapping client names to list of state directories

    Example:
        >>> states = list_available_states()
        >>> print(states)
        {'01_transactions': ['01_transactions_20251018_174236', ...]}
    """
    base_path = Path(base_dir)

    if not base_path.exists():
        logger.warning(f"Base directory not found: {base_dir}")
        return {}

    states_by_client = {}

    # Find all directories with metadata
    for dir_path in base_path.iterdir():
        if not dir_path.is_dir():
            continue

        metadata_path = dir_path / 'context_metadata.json'
        if not metadata_path.exists():
            continue

        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

            client = metadata.get('client', 'unknown')
            if client not in states_by_client:
                states_by_client[client] = []

            states_by_client[client].append({
                'path': str(dir_path),
                'run_id': metadata['run_id'],
                'timestamp': metadata['timestamp'],
                'datasets': metadata.get('datasets', []),
                'models': metadata.get('models', [])
            })
        except Exception as e:
            logger.warning(f"Error reading metadata from {dir_path}: {e}")
            continue

    # Sort each client's states by timestamp (newest first)
    for client in states_by_client:
        states_by_client[client].sort(
            key=lambda x: x['timestamp'],
            reverse=True
        )

    return states_by_client
