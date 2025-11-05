"""
Group-by processing module for GabeDA execution.

Single Responsibility: Process features per group with SINGLE-LOOP execution ONLY

CRITICAL: This module contains the 4-case logic that enables filters to use attributes.
DO NOT modify the single-loop execution pattern or the flag tracking logic.
"""

from matplotlib.pylab import f
import pandas as pd
from typing import Dict, Any, Tuple, Optional, TYPE_CHECKING
from src.execution.calculator import FeatureCalculator
from src.features.detector import FeatureTypeDetector
from src.utils.logger import get_logger
from src.utils import log_count_summary, log_data_shape

if TYPE_CHECKING:
    from src.core.context import GabedaContext

logger = get_logger(__name__)


class GroupByProcessor:
    """
    Processes features for each group using single-loop execution.

    Responsibilities:
    - Execute single-loop per group (CRITICAL for Case 2)
    - Track in_flg, out_flg, groupby_flg for 4-case logic
    - Apply correct decision: if in_flg and not groupby_flg -> FILTER else -> ATTRIBUTE
    - Combine results from all groups

    Does NOT:
    - Analyze features (analyzer does this)
    - Orchestrate overall execution (executor does this)

    CRITICAL: The 4-Case Logic
    =========================
    Case 1: Filter (standard)
        - in_flg=True, out_flg=False, groupby_flg=False
        - Reads ONLY from data_in
        - Stored in data_in

    Case 2: Filter (using attributes) - THE KEY INNOVATION
        - in_flg=True, out_flg=True, groupby_flg=False
        - Reads from BOTH data_in AND agg_results
        - Stored in data_in
        - ENABLED by single-loop execution

    Case 3: Attribute (with aggregation)
        - groupby_flg=True (regardless of in_flg/out_flg)
        - Has aggregation keywords
        - Stored in agg_results

    Case 4: Attribute (composition)
        - in_flg=False, groupby_flg=False
        - Uses ONLY other attributes
        - Stored in agg_results

    Decision Logic: if in_flg and not groupby_flg -> FILTER else -> ATTRIBUTE
    """

    def __init__(self, calculator: FeatureCalculator, detector: FeatureTypeDetector):
        self.calculator = calculator
        self.detector = detector

    def process_group(
        self,
        group_df: pd.DataFrame,
        cfg_model: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a single group with single-loop execution.

        CRITICAL: This is the SINGLE LOOP that enables filters to use attributes.

        Args:
            group_df: DataFrame for this group
            cfg_model: Configuration with feature_funcs, feature_args, feature_groupby_flg

        Returns:
            Dict with 'data_in' (DataFrame), 'agg_results' (dict), and 'filters_calculated' (list)
        """
        data_in = group_df.copy()
        agg_results = {}
        filters_calculated = []  # Track filter columns added to data_in

        # CRITICAL: Single loop through exec_seq
        for feature in cfg_model['exec_seq']:
            # Skip if already in input data
            if feature in data_in.columns:
                logger.debug(f"Skipping '{feature}' - already in data_in")
                continue

            func = cfg_model['feature_funcs'][feature]
            args = cfg_model['feature_args'][feature]
            groupby_flg = cfg_model['feature_groupby_flg'][feature]

            logger.debug(f"Processing feature: {feature}")
            logger.debug(f"  Args: {args}")
            logger.debug(f"  groupby_flg: {groupby_flg}")

            # CRITICAL: Prepare arguments from BOTH data_in AND agg_results
            # Track WHERE arguments come from
            args_data = []
            in_flg = False   # Does feature read from data_in (regular input columns)?
            out_flg = False  # Does feature read from agg_results OR external data?

            # Get list of external column names for classification
            ext_cols_list = cfg_model.get('ext_cols', {}).get('list', [])

            for arg in args:
                # CRITICAL: Check priority order for correct classification
                # Priority 1: Check agg_results FIRST (locally computed attributes)
                if arg in agg_results:
                    out_flg = True
                    args_data.append(agg_results[arg])
                    logger.debug(f"  arg '{arg}' from agg_results (out_flg=True)")

                # Priority 2: Check if from external data (using pre-computed list)
                elif arg in ext_cols_list:
                    out_flg = True
                    args_data.append(data_in[arg].values[0])
                    logger.debug(f"  arg '{arg}' from EXTERNAL DATA (out_flg=True)")

                # Priority 3: Check if regular input column
                elif arg in data_in.columns:
                    in_flg = True
                    args_data.append(data_in[arg].values)
                    logger.debug(f"  arg '{arg}' from data_in (in_flg=True)")

                else:
                    # Argument not found
                    logger.error(f"Feature '{feature}': argument '{arg}' not found in data_in or agg_results")
                    logger.error(f"  Available in data_in: {list(data_in.columns)}")
                    logger.error(f"  Available in agg_results: {list(agg_results.keys())}")
                    logger.error(f"  Available in ext_cols: {ext_cols_list}")
                    raise ValueError(f"Argument '{arg}' not found for feature '{feature}'")

            # Validate all arguments found
            if len(args_data) != len(args):
                logger.error(f"Feature '{feature}': expected {len(args)} arguments, found {len(args_data)}")
                continue

            logger.debug(f"  Flags: in_flg={in_flg}, out_flg={out_flg}, groupby_flg={groupby_flg}")

            # CRITICAL: 4-Case Decision Logic
            # Simplified condition: if in_flg and not groupby_flg -> FILTER else -> ATTRIBUTE
            if in_flg and not groupby_flg:
                # Cases 1 & 2: FILTER
                #   Case 1: in_flg=True, out_flg=False, groupby_flg=False (standard filter)
                #   Case 2: in_flg=True, out_flg=True, groupby_flg=False (filter using attributes)
                logger.info(f"→ FILTER: {feature} (Case {'2 - uses attributes' if out_flg else '1 - standard'})")

                # Calculate filter and store in data_in
                data_in[feature] = self.calculator.calculate_filter(
                    feature_name=feature,
                    func=func,
                    args_data=args_data
                )

                # Track that this feature was calculated as a filter
                filters_calculated.append(feature)

                logger.debug(f"  Stored in data_in['{feature}'], sample: {data_in[feature].head(3).tolist()}")

            else:
                # Cases 3 & 4: ATTRIBUTE
                #   Case 3: groupby_flg=True (has aggregation)
                #   Case 4: in_flg=False, groupby_flg=False (composition)
                case_desc = "3 - aggregation" if groupby_flg else "4 - composition"
                logger.info(f"→ ATTRIBUTE: {feature} (Case {case_desc})")

                # Calculate attribute and store in agg_results
                agg_results[feature] = self.calculator.calculate_attribute(
                    feature_name=feature,
                    func=func,
                    args_data=args_data
                )

                logger.debug(f"  Stored in agg_results['{feature}'] = {agg_results[feature]}")

        return {
            'data_in': data_in,
            'agg_results': agg_results,
            'filters_calculated': filters_calculated
        }

    def _merge_external_data(
        self,
        data_in: pd.DataFrame,
        cfg_model: Dict[str, Any],
        context: Optional['GabedaContext']
    ) -> pd.DataFrame:
        """
        Merge external datasets into data_in before feature execution.

        Args:
            data_in: Input DataFrame
            cfg_model: Configuration with optional 'external_data' key
            context: GabedaContext instance to retrieve external datasets

        Returns:
            DataFrame with external data merged in (columns prefixed with dataset name)

        Configuration Format:
            cfg_model['external_data'] = {
                'daily_attrs': {
                    'source': 'daily_attrs',    # Dataset name in context
                    'join_on': ['dt_date'],     # Merge key(s)
                    'columns': None             # None = ALL cols, or list of specific cols
                }
            }
        """
        if not cfg_model.get('external_data'):
            return data_in

        if context is None:
            raise ValueError("external_data specified but context not provided")

        logger.info("Merging external data sources...")

        for ext_name, ext_config in cfg_model['external_data'].items():
            # Get external dataset from context
            source_name = ext_config['source']
            ext_df = context.get_dataset(source_name)

            if ext_df is None:
                raise ValueError(f"External dataset '{source_name}' not found in context")

            # Determine columns to merge
            join_cols = ext_config['join_on']
            if not isinstance(join_cols, list):
                join_cols = [join_cols]

            # Select columns: ALL (except join keys) or specific subset
            if ext_config.get('columns') is None:
                # Bring ALL columns except join keys
                cols_to_merge = [c for c in ext_df.columns if c not in join_cols]
                logger.info(f"  '{ext_name}': merging ALL {len(cols_to_merge)} columns (excluding join keys)")
            else:
                # Bring ONLY specified columns
                cols_to_merge = ext_config['columns']
                logger.info(f"  '{ext_name}': merging {len(cols_to_merge)} specified columns")

            # Rename columns to avoid conflicts (prefix with external dataset name)
            rename_map = {col: f"{ext_name}_{col}" for col in cols_to_merge}
            ext_subset = ext_df[join_cols + cols_to_merge].rename(columns=rename_map)

            # Merge into data_in (broadcast to matching rows)
            before_cols = len(data_in.columns)
            data_in = data_in.merge(ext_subset, on=join_cols, how='left')
            after_cols = len(data_in.columns)

            logger.info(f"  '{ext_name}': added {after_cols - before_cols} columns via join on {join_cols}")
            logger.debug(f"    New columns: {list(rename_map.values())}")

        logger.info(f"External data merge complete: {len(data_in.columns)} total columns")
        return data_in

    def process_all_groups(
        self,
        data_in: pd.DataFrame,
        cfg_model: Dict[str, Any],
        context: Optional['GabedaContext'] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Apply single-loop processing to each group and combine results.

        Args:
            data_in: Input DataFrame
            cfg_model: Configuration with group_by and feature metadata
            context: GabedaContext instance (required if external_data specified)

        Returns:
            Tuple of (filters_df, attrs_df)
            - filters_df: DataFrame with group_by, row_id (if exists), and filter columns
            - attrs_df: DataFrame with group_by and attribute columns

        Special Case: No Group By (Enrichment Mode)
            When group_by is None or empty:
            - ALL features are treated as filters (row-level calculations)
            - Attributes are SKIPPED entirely (attrs_df will be empty)
            - filters_df contains ALL input columns + calculated filter columns
        """
        # CRITICAL: Merge external data BEFORE any processing
        data_in = self._merge_external_data(data_in, cfg_model, context)

        group_by_col = cfg_model.get('group_by')

        # SPECIAL CASE: No grouping - enrichment mode (filters only)
        if group_by_col is None or group_by_col == [] or group_by_col == '':
            logger.info("No group_by specified - ENRICHMENT MODE (filters only, no attributes)")
            return self._process_no_grouping(data_in, cfg_model)

        # Normal case: Apply process_group to each group
        logger.info(f"Processing groups by '{group_by_col}'...")
        grouped_results = data_in.groupby(group_by_col, group_keys=True).apply(
            lambda group: self.process_group(group, cfg_model),
            include_groups=False
        )

        logger.info(f"Processed {len(grouped_results)} groups")
        logger.debug(f"grouped_results type: {type(grouped_results)}")
        logger.debug(f"grouped_results index: {grouped_results.index.tolist()}")
        logger.debug(f"grouped_results index dtype: {grouped_results.index.dtype}")

        # Collect unique filter columns from all groups
        all_filters = set()
        for group_value, result in grouped_results.items():
            all_filters.update(result.get('filters_calculated', []))

        # Store in config for _build_filters_dataframe to use
        cfg_model['exec_fltrs'] = list(all_filters)
        logger.info(f"Identified {len(all_filters)} filter columns: {list(all_filters)}")

        # Extract and combine data_in (filters) from all groups
        data_in_list = []
        for group_value, result in grouped_results.items():
            df = result['data_in'].copy()  # IMPORTANT: Make a copy to avoid modifying original
            if not df.empty:
                logger.debug(f"Processing group: {repr(group_value)} (type: {type(group_value)})")
                logger.debug(f"  df columns before adding group_by: {list(df.columns)}")
                logger.debug(f"  df has '{group_by_col if isinstance(group_by_col, str) else group_by_col[0]}' column: {group_by_col if isinstance(group_by_col, str) else group_by_col[0] in df.columns}")

                # Add group_by column(s) back - handle multi-column group_by
                if isinstance(group_by_col, list):
                    for i, col in enumerate(group_by_col):
                        df[col] = group_value[i] if isinstance(group_value, tuple) else group_value
                        logger.debug(f"  Added group_by column '{col}' = {repr(df[col].iloc[0] if len(df) > 0 else 'EMPTY')}")
                else:
                    df[group_by_col] = group_value
                    logger.debug(f"  Added group_by column '{group_by_col}' = {repr(group_value)} (type: {type(group_value)})")
                # Drop all-NA columns
                df_cleaned = df.dropna(axis=1, how='all')
                data_in_list.append(df_cleaned)

        data_in_combined = pd.concat(data_in_list, ignore_index=True) if data_in_list else pd.DataFrame()

        # Build filters DataFrame (group_by + row_id + filter columns only)
        if not data_in_combined.empty:
            filters_df = self._build_filters_dataframe(data_in_combined, cfg_model)
        else:
            filters_df = pd.DataFrame()

        # Extract and combine agg_results (attributes) from all groups
        attrs_list = []
        for group_value, result in grouped_results.items():
            # Handle multi-column group_by: unpack tuple into separate columns
            if isinstance(group_by_col, list):
                # If group_value is a tuple (multi-column groupby), unpack it
                # If it's a scalar (single-column groupby with list syntax), use it directly
                if isinstance(group_value, tuple):
                    row_dict = {col: group_value[i] for i, col in enumerate(group_by_col)}
                else:
                    # Single value for single-column group_by specified as list
                    row_dict = {group_by_col[0]: group_value}
            else:
                row_dict = {group_by_col: group_value} # save group value to group_by column
            # Add aggregated attributes
            row_dict.update(result['agg_results'])
            attrs_list.append(row_dict) # each row is a dict

        attrs_df = pd.DataFrame(attrs_list) if attrs_list else pd.DataFrame()

        logger.info(f"Results: {len(filters_df)} filter rows, {len(attrs_df)} attribute rows")

        return filters_df, attrs_df

    def _process_no_grouping(
        self,
        data_in: pd.DataFrame,
        cfg_model: Dict[str, Any]
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Process features without grouping (enrichment mode).

        When group_by is not specified:
        - ALL features in exec_seq are calculated as FILTERS (row-level)
        - Features with aggregation (groupby_flg=True) are SKIPPED
        - Output: filters_df = input data + calculated filters, attrs_df = empty

        Args:
            data_in: Input DataFrame
            cfg_model: Configuration with exec_seq and feature metadata

        Returns:
            Tuple of (filters_df, attrs_df)
            - filters_df: Full enriched DataFrame (all input columns + filter columns)
            - attrs_df: Empty DataFrame (no aggregation without grouping)
        """
        logger.info("Processing in ENRICHMENT MODE (no grouping)")

        data_enriched = data_in.copy()
        filters_calculated = []

        # Process each feature in exec_seq
        for feature in cfg_model['exec_seq']:
            # Skip if already in input data
            if feature in data_enriched.columns:
                logger.debug(f"Skipping '{feature}' - already in data")
                continue

            func = cfg_model['feature_funcs'][feature]
            args = cfg_model['feature_args'][feature]
            groupby_flg = cfg_model['feature_groupby_flg'][feature]

            # SKIP attributes (groupby_flg=True) in enrichment mode
            if groupby_flg:
                logger.warning(f"Skipping ATTRIBUTE '{feature}' - cannot calculate without group_by")
                continue

            logger.debug(f"Processing FILTER: {feature}")
            logger.debug(f"  Args: {args}")

            # Prepare arguments from data_enriched only
            args_data = []
            for arg in args:
                if arg in data_enriched.columns:
                    args_data.append(data_enriched[arg].values)
                    logger.debug(f"  arg '{arg}' from data")
                else:
                    logger.error(f"Feature '{feature}': argument '{arg}' not found in data")
                    logger.error(f"  Available columns: {list(data_enriched.columns)}")
                    raise ValueError(f"Argument '{arg}' not found for feature '{feature}' (enrichment mode)")

            # Validate all arguments found
            if len(args_data) != len(args):
                logger.error(f"Feature '{feature}': expected {len(args)} arguments, found {len(args_data)}")
                continue

            # Calculate filter and add to data
            logger.info(f"→ FILTER: {feature} (enrichment mode)")
            data_enriched[feature] = self.calculator.calculate_filter(
                feature_name=feature,
                func=func,
                args_data=args_data
            )

            filters_calculated.append(feature)
            logger.debug(f"  Added column '{feature}', sample: {data_enriched[feature].head(3).tolist()}")

        # Store filter columns in config
        cfg_model['exec_fltrs'] = filters_calculated
        logger.info(f"Enrichment complete: added {len(filters_calculated)} filter columns: {filters_calculated}")

        # Return full enriched DataFrame as filters, empty DataFrame for attrs
        attrs_df = pd.DataFrame()

        logger.info(f"Results: {len(data_enriched)} enriched rows, 0 attribute rows (enrichment mode)")
        
        return data_enriched, attrs_df

    def _build_filters_dataframe(
        self,
        data_in_combined: pd.DataFrame,
        cfg_model: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Build filters DataFrame from combined group data.

        Returns ALL columns from input data plus any calculated filters.
        Input data is always considered complete - filters are appended, not selected.

        Args:
            data_in_combined: Combined DataFrame from all groups (includes input + calculated filters)
            cfg_model: Configuration with group_by, row_id, exec_fltrs

        Returns:
            DataFrame with ALL columns (complete input data + calculated filters)
        """
        if data_in_combined.empty:
            logger.warning("data_in_combined is empty")
            return pd.DataFrame()

        # Return ALL columns - input data is always complete, filters are appended
        filters_df = data_in_combined.reset_index(drop=True)
        logger.info(f"Built filters DataFrame with ALL {len(filters_df.columns)} columns")
        logger.debug(f"  Columns: {list(filters_df.columns)}")

        return filters_df
