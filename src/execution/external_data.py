"""
External Data Management for GabeDA

Single Responsibility: Handle external dataset operations and column resolution

Provides utilities for:
- Validating external data sources exist
- Extracting external column lists from config
- Resolving argument sources with priority (data_in > agg_results > external)
- Preparing external data for model execution

Usage:
    from src.execution.external_data import ExternalDataManager

    manager = ExternalDataManager(context)

    # Validate external sources
    result = manager.validate_external_sources(cfg_model)

    # Get external column list
    ext_cols = manager.get_external_column_list(cfg_model)

    # Resolve argument source
    value, source = manager.resolve_argument_source(
        arg='product_category',
        data_in=data_in,
        agg_results=agg_results,
        ext_cols_list=ext_cols
    )

Does NOT:
- Execute features (use execution modules)
- Store data (use context)
"""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import logging
from src.core.context import GabedaContext
from src.core.results import OperationResult


class ExternalDataManager:
    """
    Manages external dataset operations.

    Handles validation, column extraction, and argument resolution
    for models that use external data sources.
    """

    def __init__(self, context: GabedaContext, logger: Optional[logging.Logger] = None):
        """
        Initialize external data manager.

        Args:
            context: GabedaContext instance
            logger: Optional logger instance
        """
        self.context = context
        self.logger = logger or logging.getLogger(__name__)

    def validate_external_sources(self, cfg_model: Dict[str, Any]) -> OperationResult:
        """
        Validate all external datasets exist in context.

        Args:
            cfg_model: Model configuration dict with 'external_data' key

        Returns:
            OperationResult with success status and error details

        Examples:
            >>> manager = ExternalDataManager(ctx)
            >>> result = manager.validate_external_sources(cfg_model)
            >>> if not result.success:
            ...     print(result.errors)

        Use Cases:
            # executor.py:104-134 - Validate external data
            result = manager.validate_external_sources(cfg_model)
            if not result.success:
                raise ValueError(result.errors[0])
        """
        result = OperationResult(success=True)

        external_data_config = cfg_model.get('external_data')
        if not external_data_config:
            # No external data configured
            return result

        available_datasets = self.context.list_datasets()

        for ext_name, ext_config in external_data_config.items():
            source = ext_config.get('source')
            join_on = ext_config.get('join_on')
            columns = ext_config.get('columns', 'ALL')

            # Validate source exists
            if not source:
                result.add_error(f"External data '{ext_name}': 'source' not specified")
                continue

            ext_df = self.context.get_dataset(source)
            if ext_df is None:
                result.add_error(
                    f"External dataset '{source}' not found in context. "
                    f"Available: {available_datasets}"
                )
                continue

            # Validate join columns exist
            if join_on:
                join_cols = join_on if isinstance(join_on, list) else [join_on]
                missing = [col for col in join_cols if col not in ext_df.columns]
                if missing:
                    result.add_error(
                        f"External dataset '{source}': join columns {missing} not found. "
                        f"Available: {ext_df.columns.tolist()}"
                    )

        if result.has_errors():
            self.logger.error(f"External data validation failed with {len(result.errors)} errors")
        else:
            self.logger.info(f"External data validation passed ({len(external_data_config)} sources)")

        return result

    def get_external_column_list(self, cfg_model: Dict[str, Any]) -> List[str]:
        """
        Extract list of external column names from config.

        This extracts the pre-computed ext_cols.list from config, which is
        created during model execution preparation.

        Args:
            cfg_model: Model configuration dict

        Returns:
            List of external column names (empty if none)

        Examples:
            >>> ext_cols = manager.get_external_column_list(cfg_model)
            >>> print(ext_cols)
            ['product_category', 'supplier_region']

        Use Cases:
            # resolver.py:90-92 - Extract external columns
            ext_cols_list = manager.get_external_column_list(cfg_model)

            # groupby.py:110 - Get external column list
            ext_cols_list = manager.get_external_column_list(cfg_model)
        """
        ext_cols_dict = cfg_model.get('ext_cols', {})
        return ext_cols_dict.get('list', [])

    def resolve_argument_source(self,
                                arg: str,
                                data_in: pd.DataFrame,
                                agg_results: Dict[str, Any],
                                ext_cols_list: List[str],
                                ext_data: Optional[pd.DataFrame] = None) -> Tuple[Any, str]:
        """
        Resolve argument value from multiple sources with priority.

        Priority order:
        1. agg_results (locally computed attributes)
        2. ext_data (external dataset columns) - if ext_data provided
        3. data_in (regular input columns)

        Args:
            arg: Argument name to resolve
            data_in: Input DataFrame
            agg_results: Aggregated results dict
            ext_cols_list: List of external column names
            ext_data: Optional external DataFrame (if available)

        Returns:
            Tuple of (value, source_name) where source is 'agg_results', 'external', or 'data_in'

        Raises:
            ValueError: If argument not found in any source

        Examples:
            >>> value, source = manager.resolve_argument_source(
            ...     'total_revenue',
            ...     data_in=df,
            ...     agg_results={'total_revenue': 1000},
            ...     ext_cols_list=[]
            ... )
            >>> print(source)  # 'agg_results'

        Use Cases:
            # groupby.py:112-134 - Argument resolution with priority
            for arg in args:
                value, source = manager.resolve_argument_source(
                    arg, data_in, agg_results, ext_cols_list
                )
                args_data.append(value)
        """
        # Priority 1: Check agg_results first (locally computed attributes)
        if arg in agg_results:
            self.logger.debug(f"  arg '{arg}' from agg_results")
            return (agg_results[arg], 'agg_results')

        # Priority 2: Check external data
        if arg in ext_cols_list:
            if ext_data is not None and arg in ext_data.columns:
                # Use provided external DataFrame
                value = ext_data[arg].values[0]
                self.logger.debug(f"  arg '{arg}' from external data")
                return (value, 'external')
            elif arg in data_in.columns:
                # External column already joined into data_in
                value = data_in[arg].values[0]
                self.logger.debug(f"  arg '{arg}' from external data (in data_in)")
                return (value, 'external')
            else:
                raise ValueError(
                    f"Argument '{arg}' is in external column list but not found in data_in or ext_data"
                )

        # Priority 3: Check regular input columns
        if arg in data_in.columns:
            self.logger.debug(f"  arg '{arg}' from data_in")
            return (data_in[arg].values, 'data_in')

        # Not found in any source
        raise ValueError(
            f"Argument '{arg}' not found in agg_results, external columns, or data_in. "
            f"Available in data_in: {data_in.columns.tolist()}, "
            f"Available in agg_results: {list(agg_results.keys())}, "
            f"External columns: {ext_cols_list}"
        )

    def prepare_external_data(self, cfg_model: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """
        Load and prepare all external datasets from context.

        Args:
            cfg_model: Model configuration dict with 'external_data' key

        Returns:
            Dict mapping external data names to DataFrames

        Examples:
            >>> ext_data_dict = manager.prepare_external_data(cfg_model)
            >>> product_data = ext_data_dict['product_master']

        Use Cases:
            # executor.py - Pre-load all external datasets
            ext_data = manager.prepare_external_data(cfg_model)
        """
        external_data_config = cfg_model.get('external_data', {})
        ext_data_dict = {}

        for ext_name, ext_config in external_data_config.items():
            source = ext_config['source']
            ext_df = self.context.get_dataset(source)

            if ext_df is not None:
                ext_data_dict[ext_name] = ext_df
                self.logger.debug(f"Loaded external data '{ext_name}' from '{source}'")
            else:
                self.logger.warning(f"External dataset '{source}' not found")

        return ext_data_dict

    def get_external_column_names(self, cfg_model: Dict[str, Any]) -> List[str]:
        """
        Get all external column names from external_data configuration.

        This extracts column names from the external_data config structure,
        not from the pre-computed ext_cols.list.

        Args:
            cfg_model: Model configuration dict

        Returns:
            List of external column names

        Examples:
            >>> cols = manager.get_external_column_names(cfg_model)
            >>> print(cols)
            ['product_category', 'supplier_region', 'warehouse_location']
        """
        external_data_config = cfg_model.get('external_data', {})
        all_columns = []

        for ext_name, ext_config in external_data_config.items():
            columns = ext_config.get('columns', 'ALL')

            if columns == 'ALL':
                # Need to get actual dataset to list columns
                source = ext_config.get('source')
                if source:
                    ext_df = self.context.get_dataset(source)
                    if ext_df is not None:
                        all_columns.extend(ext_df.columns.tolist())
            elif isinstance(columns, list):
                all_columns.extend(columns)

        # Remove duplicates while preserving order
        seen = set()
        unique_columns = []
        for col in all_columns:
            if col not in seen:
                seen.add(col)
                unique_columns.append(col)

        return unique_columns


# Module-level utility functions (for backward compatibility)

def validate_external_sources(context: GabedaContext,
                              cfg_model: Dict[str, Any],
                              logger: Optional[logging.Logger] = None) -> OperationResult:
    """
    Standalone function to validate external sources.

    Args:
        context: GabedaContext instance
        cfg_model: Model configuration
        logger: Optional logger

    Returns:
        OperationResult with validation status
    """
    manager = ExternalDataManager(context, logger)
    return manager.validate_external_sources(cfg_model)


def get_external_column_list(cfg_model: Dict[str, Any]) -> List[str]:
    """
    Standalone function to get external column list.

    Args:
        cfg_model: Model configuration

    Returns:
        List of external column names
    """
    return cfg_model.get('ext_cols', {}).get('list', [])


# Module-level exports
__all__ = [
    'ExternalDataManager',
    'validate_external_sources',
    'get_external_column_list',
]
