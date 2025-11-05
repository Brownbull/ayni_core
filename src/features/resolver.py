"""
Dependency resolution module for GabeDA.

Single Responsibility: Resolve feature dependencies ONLY
- Performs depth-first search (DFS) to resolve dependencies
- Builds input columns list and execution sequence
- Does NOT store features or detect types
"""

from typing import List, Dict, Any, Tuple, Callable
from src.features.store import FeatureStore
from src.utils.logger import get_logger
from src.utils import normalize_to_list, log_count_summary

logger = get_logger(__name__)


class DependencyResolver:
    """
    Resolves feature dependencies using DFS.

    Responsibilities:
    - Traverse dependency tree recursively
    - Build input columns list (features from data_in)
    - Build execution sequence (topological order)
    - Fetch missing features from feature_index

    Does NOT:
    - Store features (delegates to FeatureStore)
    - Detect types (use FeatureTypeDetector)
    - Execute features (use execution package)

    CRITICAL: Preserves DFS algorithm for correct execution order
    """

    def __init__(self, feature_store: FeatureStore):
        self.store = feature_store

    def resolve_dependencies(
        self,
        output_cols: List[str],
        available_cols: List[str],
        group_by: List[str],
        model: str,
        base_path: str = 'feature_store',
        external_data: Dict[str, Any] = None
    ) -> Tuple[List[str], List[str], Dict[str, List[str]]]:
        """
        Resolve all dependencies for output columns.

        Args:
            output_cols: Features to compute
            available_cols: Columns available in input data
            group_by: Group by columns (excluded from dependencies), can be None or empty list
            model: Model name for feature loading
            base_path: Path to feature_index
            external_data: External data configuration (optional)

        Returns:
            Tuple of (input_cols, exec_seq, ext_cols)
            - input_cols: Columns needed from input data
            - exec_seq: Execution sequence (topological order)
            - ext_cols: Dict mapping external data sources to their requested columns
        """
        input_cols = []
        exec_seq = []

        # Normalize group_by to empty list if None or empty
        group_by = normalize_to_list(group_by, empty_indicators=[None, ''])

        # Get feature index for this model
        feat_idx = self.store.get_feature_index(model, base_path)

        # Resolve each output column
        for feature in output_cols:
            input_cols, exec_seq = self._resolve_feature(
                feature=feature,
                available_cols=available_cols,
                group_by=group_by,
                feat_idx=feat_idx,
                model=model,
                base_path=base_path,
                input_cols=input_cols,
                exec_seq=exec_seq,
                depth=0
            )

        # Build ext_cols dictionary and list by scanning in_cols for external data prefixes
        ext_cols_dict, ext_cols_list = self._extract_external_columns(input_cols, external_data)

        logger.info(f"Dependency resolution complete:")
        log_count_summary(logger, 'input columns', len(input_cols), items=input_cols)
        log_count_summary(logger, 'execution sequence', len(exec_seq), items=exec_seq)
        if ext_cols_dict:
            logger.info(f"  External columns requested:")
            for ext_name, cols in ext_cols_dict.items():
                logger.info(f"    - {ext_name}: {len(cols)} columns - {cols}")
            log_count_summary(logger, 'external column names (full)', len(ext_cols_list), items=ext_cols_list)

        # Return dict for display, list for efficient lookups during execution
        return input_cols, exec_seq, {'dict': ext_cols_dict, 'list': ext_cols_list}

    def _extract_external_columns(
        self,
        input_cols: List[str],
        external_data: Dict[str, Any] = None
    ) -> Tuple[Dict[str, List[str]], List[str]]:
        """
        Extract which columns from input_cols come from external data sources.

        Args:
            input_cols: List of input columns resolved by dependency resolution
            external_data: External data configuration dict from cfg_model

        Returns:
            Tuple of (ext_cols_dict, ext_cols_list):
            - ext_cols_dict: Dict mapping source names to column lists
              Example: {'daily_attrs': ['customer_id_count', 'trans_id_count']}
            - ext_cols_list: Flat list of full external column names for fast lookups
              Example: ['daily_attrs_customer_id_count', 'daily_attrs_trans_id_count']
        """
        ext_cols_dict = {}
        ext_cols_list = []

        # Return empty results if no external data configured
        if not external_data:
            return ext_cols_dict, ext_cols_list

        # For each external data source, find matching columns in input_cols
        for ext_name, ext_config in external_data.items():
            # Build the expected prefix for this external source
            prefix = f"{ext_name}_"

            # Find all input columns that start with this prefix
            matching_cols = [
                col.replace(prefix, '', 1)  # Remove prefix to get original column name
                for col in input_cols
                if col.startswith(prefix)
            ]

            # Build full column names for the list (with prefix)
            full_col_names = [
                col for col in input_cols if col.startswith(prefix)
            ]

            # Only add to dict if we found matching columns
            if matching_cols:
                ext_cols_dict[ext_name] = matching_cols
                ext_cols_list.extend(full_col_names)
                logger.debug(f"Found {len(matching_cols)} columns from external source '{ext_name}': {matching_cols}")

        return ext_cols_dict, ext_cols_list

    def _resolve_feature(
        self,
        feature: str,
        available_cols: List[str],
        group_by: List[str],
        feat_idx: List[str],
        model: str,
        base_path: str,
        input_cols: List[str],
        exec_seq: List[str],
        depth: int
    ) -> Tuple[List[str], List[str]]:
        """
        Recursively resolve a single feature (DFS).

        CRITICAL: This is the DFS algorithm that MUST be preserved.

        Args:
            feature: Feature to resolve
            available_cols: Available input columns
            group_by: Group by columns
            feat_idx: Feature index for this model
            model: Model name
            base_path: Feature index base path
            input_cols: Accumulated input columns (mutated)
            exec_seq: Accumulated execution sequence (mutated)
            depth: Recursion depth for logging

        Returns:
            Updated (input_cols, exec_seq)
        """
        indent = "  " * depth
        logger.debug(f"{indent}Resolving feature: {feature} (depth={depth})")

        # Case 1: Feature is an available column in input data
        if feature in available_cols:
            if feature not in input_cols:
                input_cols.append(feature)
                logger.info(f"{indent}Added available column '{feature}' to input list")
            return input_cols, exec_seq

        # Case 2: Feature not defined yet - try to fetch or add to input
        if not self.store.has_feature(feature):
            # Try to load from feature_index
            if feature in feat_idx:
                self.store.load_from_filesystem(model, feature, base_path)
                logger.info(f"{indent}Fetched feature '{feature}' from model '{model}'")
            else:
                # Feature not found - add to input columns
                if feature not in input_cols:
                    input_cols.append(feature)
                    logger.info(f"{indent}Added feature '{feature}' to input list (not in feature_index)")
                return input_cols, exec_seq

        # Case 3: Feature is defined - resolve its dependencies recursively
        feature_def = self.store.get_feature(feature)

        # Extract argument list
        if callable(feature_def):
            # Python function
            arg_list = list(feature_def.__code__.co_varnames)[:feature_def.__code__.co_argcount]
        else:
            # Dict with 'udf' and 'args'
            arg_list = feature_def.get('args', [])

        logger.debug(f"{indent}Feature '{feature}' has {len(arg_list)} dependencies: {arg_list}")

        # Recursively resolve each dependency
        for arg in arg_list:
            # Skip group_by columns (they're provided by grouping operation)
            if arg not in group_by:
                input_cols, exec_seq = self._resolve_feature(
                    feature=arg,
                    available_cols=available_cols,
                    group_by=group_by,
                    feat_idx=feat_idx,
                    model=model,
                    base_path=base_path,
                    input_cols=input_cols,
                    exec_seq=exec_seq,
                    depth=depth + 1
                )

        # Add current feature to execution sequence
        if feature not in exec_seq:
            exec_seq.append(feature)
            logger.debug(f"{indent}Added '{feature}' to execution sequence")

        return input_cols, exec_seq
