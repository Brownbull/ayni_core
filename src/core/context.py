"""
GabeDA Context - State Management

This module provides the GabedaContext class for managing execution state.

Responsibilities:
- Store and retrieve named datasets
- Store and retrieve model outputs
- Track execution history

Does NOT:
- Manage configuration (use ConfigManager)
- Export data (use export package)
- Generate reports (use reporting tools)
"""

import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GabedaContext:
    """
    Manages execution state for GabeDA analytics pipeline.

    Attributes:
        user_config (Dict): User-provided configuration (immutable)
        datasets (Dict[str, pd.DataFrame]): Named DataFrames
        models (Dict[str, Dict]): Model outputs with metadata
        history (List[Dict]): Execution log
        run_id (str): Unique run identifier
    """

    def __init__(self, user_config: Dict[str, Any]):
        """
        Initialize GabedaContext with user configuration.

        Args:
            user_config: User-provided configuration dictionary
        """
        self.user_config = user_config.copy()  # Immutable copy
        self.datasets: Dict[str, pd.DataFrame] = {}  # Named DataFrames
        self.models: Dict[str, Dict] = {}  # Model outputs
        self.history: List[Dict] = []  # Execution log

        # Runtime variables
        self.now = datetime.now()
        self.run_id = f"{user_config.get('client', 'unknown')}_{self.now.strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"GabedaContext initialized - run_id: {self.run_id}")

    # ==================== Dataset Management ====================

    def set_dataset(self, name: str, df: pd.DataFrame, metadata: Optional[Dict] = None) -> None:
        """
        Store a named DataFrame in the context.

        Args:
            name: Dataset identifier (e.g., 'preprocessed', 'product_filters')
            df: DataFrame to store
            metadata: Optional metadata about the dataset
        """
        if df is None:
            logger.warning(f"Attempting to set None dataset: {name}")
            return

        self.datasets[name] = df
        log_entry = {
            'action': 'set_dataset',
            'name': name,
            'shape': df.shape,
            'columns': len(df.columns),
            'timestamp': datetime.now().isoformat()
        }
        if metadata:
            log_entry['metadata'] = metadata

        self.history.append(log_entry)
        logger.debug(f"Dataset stored: {name} with shape {df.shape}")

    def get_dataset(self, name: str) -> Optional[pd.DataFrame]:
        """
        Retrieve a named DataFrame from the context.

        Supports special pattern '{model_name}_input' to get the input dataset
        that was used for a specific model execution.

        Args:
            name: Dataset identifier (e.g., 'preprocessed', 'product_stats_filters',
                  'product_stats_input')

        Returns:
            DataFrame if found, None otherwise
        """
        # Check if requesting model input with '{model_name}_input' pattern
        if name.endswith('_input'):
            model_name = name[:-6]  # Remove '_input' suffix
            if model_name in self.models:
                input_dataset_name = self.models[model_name].get('input_dataset_name')
                if input_dataset_name:
                    logger.debug(f"Resolved {name} -> {input_dataset_name}")
                    return self.datasets.get(input_dataset_name)
                else:
                    logger.warning(f"Model {model_name} has no input_dataset_name recorded")
                    return None

        # Standard dataset lookup
        df = self.datasets.get(name)
        if df is None:
            logger.warning(f"Dataset not found: {name}. Available: {list(self.datasets.keys())}")
        return df

    def list_datasets(self) -> List[str]:
        """
        List all available datasets.

        Returns:
            List of dataset names
        """
        return list(self.datasets.keys())

    # ==================== Model Output Management ====================

    def set_model_output(self, model_name: str, outputs: Dict[str, Any], cfg_model: Optional[Dict[str, Any]] = None) -> None:
        """
        Store model execution output with metadata.

        Only stores the NEW features calculated by this model (exec_fltrs, exec_attrs)
        plus required ID columns (group_by, row_id). This prevents context_states
        from accumulating all features from previous models.

        Args:
            model_name: Model identifier (e.g., 'product_stats', 'customer_rfm')
            outputs: Dictionary containing:
                - 'input_dataset_name': Name of input dataset used (REQUIRED)
                - 'filters': DataFrame with row-level calculations (optional)
                - 'attrs': DataFrame with aggregated metrics (optional)
                - 'exec_fltrs': List of new filter columns calculated (optional)
                - 'exec_attrs': List of new attribute columns calculated (optional)
                - 'config': Runtime configuration used (optional)
                - 'metadata': Additional metadata (optional)
            cfg_model: Model configuration dictionary (optional, used for column filtering during save)
        """
        self.models[model_name] = {
            'outputs': outputs,
            'cfg_model': cfg_model,  # Store for column filtering
            'timestamp': datetime.now().isoformat(),
            'datasets_generated': [],
            'input_dataset_name': outputs.get('input_dataset_name')  # CRITICAL: Store for chaining
        }

        # Store datasets with model namespace - ONLY NEW FEATURES
        if 'filters' in outputs and outputs['filters'] is not None:
            filters_df = outputs['filters']
            exec_fltrs = outputs.get('exec_fltrs', [])

            # Skip saving filters if no new filter features calculated
            # (This prevents redundant storage when filters is just input passed through)
            if not exec_fltrs or len(exec_fltrs) == 0:
                logger.debug(f"No new filter features calculated - skipping filter storage for {model_name}")
            else:
                # Determine which columns to keep
                # Always keep row_id if present, plus new filter features
                cols_to_keep = []

                # Add row_id if present
                if 'row_id' in filters_df.columns:
                    cols_to_keep.append('row_id')

                # Add new filter columns
                for col in exec_fltrs:
                    if col in filters_df.columns and col not in cols_to_keep:
                        cols_to_keep.append(col)

                # Only store if we have columns to keep
                if cols_to_keep:
                    filtered_df = filters_df[cols_to_keep].copy()
                    dataset_name = f"{model_name}_filters"
                    self.set_dataset(dataset_name, filtered_df)
                    self.models[model_name]['datasets_generated'].append(dataset_name)
                    logger.debug(f"Stored {len(cols_to_keep)} filter columns (saved {len(filters_df.columns) - len(cols_to_keep)} from state)")

        if 'attrs' in outputs and outputs['attrs'] is not None:
            attrs_df = outputs['attrs']
            exec_attrs = outputs.get('exec_attrs', [])

            # Determine which columns to keep
            # Always keep group_by columns if present, plus new attribute features
            cols_to_keep = []

            # Add group_by columns if present
            for col in attrs_df.columns:
                # Check if column looks like a group_by column (not a calculated feature)
                # Heuristic: if it's not in exec_attrs, it's likely a group_by column
                if col not in exec_attrs:
                    cols_to_keep.append(col)

            # Add new attribute columns
            for col in exec_attrs:
                if col in attrs_df.columns and col not in cols_to_keep:
                    cols_to_keep.append(col)

            # Store the filtered dataframe
            filtered_df = attrs_df[cols_to_keep].copy()
            dataset_name = f"{model_name}_attrs"
            self.set_dataset(dataset_name, filtered_df)
            self.models[model_name]['datasets_generated'].append(dataset_name)
            logger.debug(f"Stored {len(cols_to_keep)} attribute columns")

        self.history.append({
            'action': 'model_executed',
            'model': model_name,
            'datasets': self.models[model_name]['datasets_generated'],
            'input_dataset': outputs.get('input_dataset_name'),
            'timestamp': datetime.now().isoformat()
        })

        logger.info(f"Model output stored: {model_name} -> {self.models[model_name]['datasets_generated']}")

    def get_model_output(self, model_name: str) -> Optional[Dict]:
        """
        Retrieve model execution output.

        Args:
            model_name: Model identifier

        Returns:
            Dictionary with model outputs or None
        """
        return self.models.get(model_name)

    def get_model_filters(self, model_name: str) -> Optional[pd.DataFrame]:
        """
        Convenience method to get filters DataFrame from a model.

        Args:
            model_name: Model identifier

        Returns:
            Filters DataFrame or None
        """
        return self.get_dataset(f"{model_name}_filters")

    def get_model_attrs(self, model_name: str) -> Optional[pd.DataFrame]:
        """
        Convenience method to get attributes DataFrame from a model.

        Args:
            model_name: Model identifier

        Returns:
            Attributes DataFrame or None
        """
        return self.get_dataset(f"{model_name}_attrs")

    def get_model_input(self, model_name: str) -> Optional[pd.DataFrame]:
        """
        Convenience method to get the input DataFrame used for a model.

        Args:
            model_name: Model identifier

        Returns:
            Input DataFrame or None
        """
        return self.get_dataset(f"{model_name}_input")

    def list_models(self) -> List[str]:
        """
        List all executed models.

        Returns:
            List of model names
        """
        return list(self.models.keys())

    # ==================== History & Summary ====================

    def get_execution_summary(self) -> Dict:
        """
        Get summary of execution history.

        Returns:
            Dictionary with execution statistics
        """
        return {
            'run_id': self.run_id,
            'total_datasets': len(self.datasets),
            'datasets': list(self.datasets.keys()),
            'total_models': len(self.models),
            'models_executed': list(self.models.keys()),
            'execution_steps': len(self.history),
            'history': self.history
        }

    def print_summary(self) -> None:
        """Print execution summary to console."""
        summary = self.get_execution_summary()
        print("\n" + "="*80)
        print(f"GabeDA Execution Summary - Run ID: {summary['run_id']}")
        print("="*80)
        print(f"\nDatasets ({summary['total_datasets']}):")
        for ds_name in summary['datasets']:
            df = self.datasets[ds_name]
            print(f"  - {ds_name}: {df.shape}")

        print(f"\nModels Executed ({summary['total_models']}):")
        for model_name in summary['models_executed']:
            model_info = self.models[model_name]
            print(f"  - {model_name}: {model_info['datasets_generated']}")

        print(f"\nTotal Steps: {summary['execution_steps']}")
        print("="*80 + "\n")

    # ==================== Persistence Methods ====================

    def save_state(self, output_base: str = 'data/intermediate') -> str:
        """
        Save complete context state to disk.

        This is a convenience method that delegates to the persistence module.
        Requires base_cfg to be available (stored during initialization).

        Args:
            output_base: Base directory for intermediate data

        Returns:
            Path to the saved state directory

        Example:
            >>> state_dir = ctx.save_state()
            >>> print(f"State saved to: {state_dir}")
        """
        from src.core.persistence import save_context_state

        if not hasattr(self, 'user_config'):
            raise ValueError("Cannot save state: user_config not available")

        return save_context_state(
            ctx=self,
            base_cfg=self.user_config,
            output_base=output_base
        )

    @classmethod
    def load_state(cls, state_dir: str) -> tuple:
        """
        Load context state from a previously saved directory.

        This is a convenience class method that delegates to the persistence module.

        Args:
            state_dir: Path to saved state directory

        Returns:
            Tuple of (GabedaContext, base_cfg)

        Example:
            >>> ctx, cfg = GabedaContext.load_state('data/intermediate/01_transactions_20251018_174236')
            >>> enriched = ctx.get_dataset('transactions_enriched')
        """
        from src.core.persistence import load_context_state
        return load_context_state(state_dir)

    def __repr__(self) -> str:
        """String representation of context."""
        return (f"GabedaContext(run_id='{self.run_id}', "
                f"datasets={len(self.datasets)}, "
                f"models={len(self.models)})")
