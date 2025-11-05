"""
Feature analysis module for GabeDA.

Single Responsibility: Analyze and prepare features for execution ONLY
- Extracts function objects from feature definitions
- Extracts argument lists
- Uses detector to determine groupby_flg
- Builds feature metadata (funcs, args, groupby flags)
- Does NOT store, resolve, or execute features
"""

import pandas as pd
import numpy as np
from collections import Counter
from typing import Dict, List, Callable, Any, Optional
from src.features.detector import FeatureTypeDetector
from src.features.store import FeatureStore
from src.utils.logger import get_logger
from src.core import constants

logger = get_logger(__name__)

# Global imports that compiled feature functions may need
# Same as FeatureStore.FEATURE_FUNCTION_GLOBALS and FeatureCalculator.FEATURE_FUNCTION_GLOBALS
# IMPORTANT: This must match calculator.py to ensure consistent feature execution
FEATURE_FUNCTION_GLOBALS = {
    # Standard libraries
    'np': np,
    'pd': pd,
    'Counter': Counter,

    # All constants from src.core.constants
    'DEFAULT_FLOAT': constants.DEFAULT_FLOAT,
    'DEFAULT_INT': constants.DEFAULT_INT,
    'DEFAULT_STRING': constants.DEFAULT_STRING,
    'DEFAULT_BOOL': constants.DEFAULT_BOOL,
    'MARGIN_THRESHOLD_PCT': constants.MARGIN_THRESHOLD_PCT,
    'LOW_STOCK_THRESHOLD': constants.LOW_STOCK_THRESHOLD,
    'DEAD_STOCK_DAYS': constants.DEAD_STOCK_DAYS,
    'HIGH_VALUE_TRANSACTION_MULTIPLIER': constants.HIGH_VALUE_TRANSACTION_MULTIPLIER,
    'BUSINESS_HOURS_START': constants.BUSINESS_HOURS_START,
    'BUSINESS_HOURS_END': constants.BUSINESS_HOURS_END,
    'MORNING_START': constants.MORNING_START,
    'MORNING_END': constants.MORNING_END,
    'AFTERNOON_START': constants.AFTERNOON_START,
    'AFTERNOON_END': constants.AFTERNOON_END,
    'EVENING_START': constants.EVENING_START,
    'EVENING_END': constants.EVENING_END,
    'FIRST_VALUE': constants.FIRST_VALUE,
    'MAX_PRICE_DEVIATION_PCT': constants.MAX_PRICE_DEVIATION_PCT,
    'MIN_QUANTITY': constants.MIN_QUANTITY,
    'MAX_QUANTITY': constants.MAX_QUANTITY,
    'PARETO_THRESHOLD': constants.PARETO_THRESHOLD,
    'TOP_PRODUCTS_PERCENTILE': constants.TOP_PRODUCTS_PERCENTILE,
    'CUSTOMER_CHURN_DAYS': constants.CUSTOMER_CHURN_DAYS,
    'EXCEL_MAX_ROWS_PER_SHEET': constants.EXCEL_MAX_ROWS_PER_SHEET,
    'DECIMAL_PRECISION': constants.DECIMAL_PRECISION,
    'PERCENTAGE_PRECISION': constants.PERCENTAGE_PRECISION,
}


class FeatureAnalyzer:
    """
    Analyzes features and prepares execution metadata.

    Responsibilities:
    - Extract function objects from definitions
    - Extract argument lists
    - Detect groupby flags (delegates to detector)
    - Build execution metadata dictionaries

    Does NOT:
    - Store features (use FeatureStore)
    - Resolve dependencies (use DependencyResolver)
    - Execute features (use execution package)

    CRITICAL: Must support both callable and dict feature definitions
    """

    def __init__(self, feature_store: FeatureStore, detector: FeatureTypeDetector):
        self.store = feature_store
        self.detector = detector

    def analyze_features(
        self,
        exec_seq: List[str],
        data_in_columns: List[str],
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze features and build execution metadata.

        Args:
            exec_seq: Execution sequence (features to analyze)
            data_in_columns: Columns present in input data
            model_name: Model name for feature lookup context

        Returns:
            Dict with:
            - 'feature_funcs': Dict[str, Callable] - Executable functions
            - 'feature_args': Dict[str, List[str]] - Argument lists
            - 'feature_groupby_flg': Dict[str, bool] - Aggregation flags
        """
        feature_funcs = {}
        feature_args = {}
        feature_groupby_flg = {}

        for feature in exec_seq:
            # Skip features already in data_in (available columns)
            if feature in data_in_columns:
                logger.debug(f"Skipping '{feature}' - already in input data")
                continue

            # Get feature definition from store with model context
            feature_def = self.store.get_feature(feature, model=model_name)
            if feature_def is None:
                logger.error(f"Feature '{feature}' not found in store - skipping")
                continue

            # Analyze based on type
            if callable(feature_def):
                # Case 1: Python function
                func, args, groupby_flg = self._analyze_callable(feature, feature_def)
            else:
                # Case 2: Dict with 'udf' and 'args'
                func, args, groupby_flg = self._analyze_dict(feature, feature_def)

            # Store metadata
            feature_funcs[feature] = func
            feature_args[feature] = args
            feature_groupby_flg[feature] = groupby_flg

            logger.info(
                f"Analyzed feature '{feature}': "
                f"{len(args)} args, groupby_flg={groupby_flg}"
            )

        return {
            'feature_funcs': feature_funcs,
            'feature_args': feature_args,
            'feature_groupby_flg': feature_groupby_flg
        }

    def _analyze_callable(self, name: str, func: Callable) -> tuple:
        """
        Analyze a callable function.

        Args:
            name: Feature name
            func: Callable function

        Returns:
            Tuple of (func, args, groupby_flg)
        """
        # Detect aggregation
        groupby_flg = self.detector.is_aggregation(func)

        # Extract arguments
        args = list(func.__code__.co_varnames)[:func.__code__.co_argcount]

        logger.debug(f"Analyzed callable '{name}': args={args}, groupby_flg={groupby_flg}")

        return func, args, groupby_flg

    def _analyze_dict(self, name: str, feature_def: Dict) -> tuple:
        """
        Analyze a dict feature definition.

        Args:
            name: Feature name
            feature_def: Dict with 'udf' (code string) and 'args'

        Returns:
            Tuple of (func, args, groupby_flg)
        """
        udf_code = feature_def['udf']
        args = feature_def['args']

        # Detect aggregation from code string
        groupby_flg = self.detector.is_aggregation(udf_code)

        # Execute code to get callable function
        # CRITICAL: exec() creates function in local scope
        local_scope = {}
        try:
            # Inject necessary globals (np, pd, Counter, DEFAULT_FLOAT) so exec can compile
            global_ns = {'__builtins__': __builtins__}
            global_ns.update(FEATURE_FUNCTION_GLOBALS)
            exec(udf_code, global_ns, local_scope)
            func = local_scope.get(name)

            if func is None:
                raise ValueError(f"Feature function '{name}' not found after exec()")

            logger.debug(
                f"Analyzed dict feature '{name}': "
                f"args={args}, groupby_flg={groupby_flg}"
            )

            return func, args, groupby_flg

        except Exception as e:
            logger.error(f"Error executing UDF for feature '{name}': {e}")
            logger.error(f"UDF code:\n{udf_code}")
            raise

    def validate_arguments(
        self,
        feature: str,
        args: List[str],
        data_in_columns: List[str],
        agg_results_keys: List[str]
    ) -> bool:
        """
        Validate that all arguments are available.

        Args:
            feature: Feature name
            args: Required arguments
            data_in_columns: Available input columns
            agg_results_keys: Available aggregation results

        Returns:
            True if all arguments available, False otherwise
        """
        missing_args = []

        for arg in args:
            if arg not in data_in_columns and arg not in agg_results_keys:
                missing_args.append(arg)

        if missing_args:
            logger.error(f"Feature '{feature}': missing arguments {missing_args}")
            logger.error(f"  Available in data_in: {data_in_columns}")
            logger.error(f"  Available in agg_results: {agg_results_keys}")
            return False

        return True
