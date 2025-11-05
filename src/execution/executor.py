"""
Model execution module for GabeDA.

Single Responsibility: Execute a single model ONLY
- Coordinates the full execution pipeline for one model
- Uses analyzer to prepare features
- Uses groupby processor to execute features
- Returns model outputs
- Does NOT orchestrate multiple models (orchestrator does this)
"""

import pandas as pd
from typing import Dict, Any, Tuple, Optional, TYPE_CHECKING
from src.features.analyzer import FeatureAnalyzer
from src.execution.groupby import GroupByProcessor
from src.utils.logger import get_logger
from src.utils import (
    normalize_to_list, validate_required_keys,
    log_model_execution, log_data_shape, log_count_summary, log_operation_complete
)

if TYPE_CHECKING:
    from src.core.context import GabedaContext

logger = get_logger(__name__)


class ModelExecutor:
    """
    Executes a single model.

    Responsibilities:
    - Coordinate full execution pipeline for one model
    - Use analyzer to prepare feature metadata
    - Use groupby processor to execute features
    - Build and return model outputs

    Does NOT:
    - Orchestrate multiple models (use ModelOrchestrator)
    - Store results in context (caller does this)
    - Preprocess data (preprocessing package does this)
    """

    def __init__(
        self,
        analyzer: FeatureAnalyzer,
        groupby_processor: GroupByProcessor,
        context: Optional['GabedaContext'] = None
    ):
        self.analyzer = analyzer
        self.groupby_processor = groupby_processor
        self.context = context

    def execute_model(
        self,
        cfg_model: Dict[str, Any],
        input_dataset_name: str,
        data_in: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Execute a single model.

        Args:
            cfg_model: Model configuration with model_name, exec_seq, features, group_by
            input_dataset_name: Name of input dataset in context (CRITICAL)
            data_in: Input DataFrame (optional - retrieved from context if not provided)

        Returns:
            Dict with:
            - 'filters': DataFrame with filter results
            - 'attrs': DataFrame with attribute results
            - 'input_dataset_name': Name of input dataset (STRING)
            - 'exec_fltrs': List of filter feature names
            - 'exec_attrs': List of attribute feature names

        Raises:
            ValueError: If model_name not in cfg_model or data_in not provided and context not available
        """
        # Extract model_name from config
        validation = validate_required_keys(cfg_model, ['model_name'], logger=logger)
        if not validation.success:
            raise ValueError(validation.errors[0])
        model_name = cfg_model['model_name']

        # Get data from context if not provided
        if data_in is None:
            if self.context is None:
                raise ValueError(
                    "data_in not provided and context not available. "
                    "Either pass data_in or initialize ModelExecutor with context."
                )
            data_in = self.context.get_dataset(input_dataset_name)
            if data_in is None:
                raise ValueError(f"Dataset '{input_dataset_name}' not found in context")
            logger.info(f"Retrieved input dataset '{input_dataset_name}' from context")

        # Normalize group_by to None if missing or empty
        group_by = normalize_to_list(cfg_model.get('group_by'), empty_indicators=[None, '', []], to_none=True)
        cfg_model['group_by'] = group_by

        logger.info(f"===== Executing Model: {model_name} =====")
        logger.info(f"Input dataset: {input_dataset_name}")
        log_data_shape(logger, f"Input '{input_dataset_name}'", data_in, action='Processing')
        logger.info(f"Group by: {group_by} {'(enrichment mode - filters only)' if group_by is None else ''}")
        log_count_summary(logger, 'execution sequence features', len(cfg_model.get('exec_seq', [])),
                         items=cfg_model.get('exec_seq', []))

        # Validate external_data if specified
        if cfg_model.get('external_data'):
            if self.context is None:
                raise ValueError(
                    "Model configuration includes 'external_data' but ModelExecutor was not initialized with context. "
                    "Pass context when creating ModelExecutor to enable external data sources."
                )

            logger.info(f"External data sources configured: {len(cfg_model['external_data'])}")
            for ext_name, ext_config in cfg_model['external_data'].items():
                source = ext_config['source']
                join_on = ext_config['join_on']
                columns = ext_config.get('columns', 'ALL')

                # Validate external dataset exists
                ext_df = self.context.get_dataset(source)
                if ext_df is None:
                    available = self.context.list_datasets()
                    raise ValueError(
                        f"External dataset '{source}' not found in context. "
                        f"Available datasets: {available}"
                    )

                # Validate join columns exist in both datasets
                join_cols = join_on if isinstance(join_on, list) else [join_on]
                missing_in_input = [col for col in join_cols if col not in data_in.columns]
                missing_in_ext = [col for col in join_cols if col not in ext_df.columns]

                if missing_in_input:
                    raise ValueError(
                        f"External data '{ext_name}': join columns {missing_in_input} "
                        f"not found in input dataset '{input_dataset_name}'"
                    )
                if missing_in_ext:
                    raise ValueError(
                        f"External data '{ext_name}': join columns {missing_in_ext} "
                        f"not found in external dataset '{source}'"
                    )

                logger.info(f"  - '{ext_name}': source='{source}', join_on={join_on}, columns={columns}")

        # Log missing columns (informational only)
        if cfg_model.get('missing_cols'):
            logger.info(f"Missing columns (not in exec_seq): {cfg_model['missing_cols']}")

        # Step 1: Analyze features and build execution metadata
        logger.info("Step 1: Analyzing features...")
        analysis_results = self.analyzer.analyze_features(
            exec_seq=cfg_model['exec_seq'],
            data_in_columns=data_in.columns.tolist(),
            model_name=model_name
        )

        # Add analysis results to config
        cfg_model['feature_funcs'] = analysis_results['feature_funcs']
        cfg_model['feature_args'] = analysis_results['feature_args']
        cfg_model['feature_groupby_flg'] = analysis_results['feature_groupby_flg']

        logger.info(f"Analyzed {len(cfg_model['feature_funcs'])} features")

        # Initialize tracking lists
        cfg_model['exec_fltrs'] = []
        cfg_model['exec_attrs'] = []

        # Step 2: Execute features using groupby processor
        logger.info("Step 2: Executing features with single-loop processing...")
        filters_df, attrs_df = self.groupby_processor.process_all_groups(
            data_in=data_in,
            cfg_model=cfg_model,
            context=self.context  # Pass context for external_data support
        )

        # Step 3: Track which features were executed as filters vs attributes
        # This is populated by the groupby processor during execution
        self._update_exec_tracking(cfg_model, filters_df, attrs_df)

        logger.info(f"Execution complete:")
        logger.info(f"  Filters: {len(cfg_model['exec_fltrs'])} features, {len(filters_df)} rows")
        logger.info(f"  Attributes: {len(cfg_model['exec_attrs'])} features, {len(attrs_df)} rows")

        # Step 4: Build output dict
        output = {
            'filters': filters_df if not filters_df.empty else None,
            'attrs': attrs_df if not attrs_df.empty else None,
            'input_dataset_name': input_dataset_name,  # CRITICAL: Store as STRING
            'exec_fltrs': cfg_model['exec_fltrs'],
            'exec_attrs': cfg_model['exec_attrs']
        }

        logger.info(f"===== Model {model_name} Complete =====")

        return output

    def _update_exec_tracking(
        self,
        cfg_model: Dict[str, Any],
        filters_df: pd.DataFrame,
        attrs_df: pd.DataFrame
    ) -> None:
        """
        Update exec_fltrs and exec_attrs lists based on what was actually calculated.

        Args:
            cfg_model: Model configuration (modified in place)
            filters_df: Filters DataFrame
            attrs_df: Attributes DataFrame
        """
        # Get filter columns (exclude group_by and row_id)
        group_by_col = cfg_model.get('group_by')
        row_id_col = cfg_model.get('row_id')
        exclude_cols = normalize_to_list(group_by_col) + normalize_to_list(row_id_col)

        # Filter columns are those in filters_df that aren't excluded
        if not filters_df.empty:
            filter_cols = [
                col for col in filters_df.columns
                if col not in exclude_cols
            ]
            cfg_model['exec_fltrs'] = filter_cols
        else:
            cfg_model['exec_fltrs'] = []

        # Attribute columns are those in attrs_df that aren't the group_by column
        if not attrs_df.empty:
            attr_cols = [
                col for col in attrs_df.columns
                if col not in exclude_cols
            ]
            cfg_model['exec_attrs'] = attr_cols
        else:
            cfg_model['exec_attrs'] = []

        logger.debug(f"Tracked execution: {len(cfg_model['exec_fltrs'])} filters, {len(cfg_model['exec_attrs'])} attributes")
