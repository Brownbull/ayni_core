"""
Feature calculation module for GabeDA execution.

Single Responsibility: Calculate feature values ONLY
- Executes filter calculations (row-level)
- Executes attribute calculations (group-level)
- Does NOT determine which type to use (groupby.py does this)
- Does NOT orchestrate execution flow
"""

import numpy as np
import pandas as pd
from typing import Callable, List, Any
from collections import Counter
from src.utils.logger import get_logger
from src.core import constants

logger = get_logger(__name__)

# Global imports that compiled feature functions may need
# Includes all libraries AND all constants from src.core.constants
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


class FeatureCalculator:
    """
    Calculates feature values.

    Responsibilities:
    - Execute filter calculations (vectorized row-level)
    - Execute attribute calculations (scalar group-level)
    - Inject required imports into compiled feature functions

    Does NOT:
    - Determine feature type (groupby.py does 4-case logic)
    - Orchestrate execution (executor.py does this)
    - Load or analyze features (features package does this)

    CRITICAL: This class just calculates - the CALLER determines
    whether to call calculate_filter() or calculate_attribute()
    based on the 4-case logic in groupby.py
    """

    @staticmethod
    def inject_globals_into_function(func: Callable) -> Callable:
        """
        Inject necessary globals (np, pd, Counter, etc.) into a compiled function.

        When features are loaded from feature_store as code strings and compiled
        with exec(), they may not have access to numpy, pandas, etc. This method
        updates the function's __globals__ to include these imports.

        Args:
            func: Function that may need global imports

        Returns:
            Same function with updated __globals__

        Note:
            This modifies the function's __globals__ dict in-place.
            Only injects if the keys don't already exist (non-destructive).
        """
        if not callable(func):
            return func

        # Inject globals if they don't already exist
        for key, value in FEATURE_FUNCTION_GLOBALS.items():
            if key not in func.__globals__:
                func.__globals__[key] = value

        return func

    def calculate_filter(
        self,
        feature_name: str,
        func: Callable,
        args_data: List[Any]
    ) -> np.ndarray:
        """
        Calculate filter (row-level feature).

        Filters produce one value per row in data_in and are added
        as new columns to data_in.

        Args:
            feature_name: Feature name (for logging)
            func: Callable function
            args_data: List of numpy arrays (same length)

        Returns:
            numpy array with one value per row

        CRITICAL: Uses np.vectorize to apply function row-by-row
        """
        logger.info(f"Calculating FILTER: {feature_name} with {len(args_data)} args")
        logger.debug(f"  Args shapes: {[np.array(a).shape for a in args_data]}")

        # Inject required globals (for compiled functions from feature_store)
        func = self.inject_globals_into_function(func)

        # Vectorize and execute
        try:
            result = np.vectorize(func)(*args_data)
            logger.debug(f"  Result shape: {result.shape}, sample: {result[:5] if len(result) > 5 else result}")
            return result
        except Exception as e:
            logger.error(f"Error calculating filter '{feature_name}': {e}")
            logger.error(f"  Function: {func}")
            logger.error(f"  Args count: {len(args_data)}")
            raise

    def calculate_attribute(
        self,
        feature_name: str,
        func: Callable,
        args_data: List[Any]
    ) -> Any:
        """
        Calculate attribute (group-level feature).

        Attributes produce one scalar value per group and are stored
        in agg_results dictionary.

        Args:
            feature_name: Feature name (for logging)
            func: Callable function
            args_data: List of values (could be arrays or scalars)

        Returns:
            Scalar value (or single-element array/value)

        CRITICAL: Calls function directly (no vectorization)
        """
        logger.info(f"Calculating ATTRIBUTE: {feature_name} with {len(args_data)} args")
        logger.debug(f"  Args types: {[type(a).__name__ for a in args_data]}")
        logger.debug(f"  Args preview: {[str(a)[:100] if hasattr(a, '__len__') and len(str(a)) > 100 else a for a in args_data]}")

        # Inject required globals (for compiled functions from feature_store)
        func = self.inject_globals_into_function(func)

        # Execute directly
        try:
            result = func(*args_data)
            logger.debug(f"  Result type: {type(result).__name__}, value: {result}")
            return result
        except Exception as e:
            logger.error(f"Error calculating attribute '{feature_name}': {e}")
            logger.error(f"  Function: {func}")
            logger.error(f"  Args count: {len(args_data)}")
            raise

    def prepare_filter_args(
        self,
        arg: str,
        data_in: pd.DataFrame,
        agg_results: dict
    ) -> Any:
        """
        Prepare argument data for filter calculation.

        For filters, arguments can come from:
        - data_in columns (Case 1: standard filters)
        - agg_results (Case 2: filters using attributes)

        Args:
            arg: Argument name
            data_in: Input DataFrame
            agg_results: Aggregation results dict

        Returns:
            Numpy array or scalar value

        Raises:
            KeyError: If argument not found
        """
        if arg in data_in.columns:
            # From data_in - return as numpy array
            return data_in[arg].values
        elif arg in agg_results:
            # From agg_results - return scalar (will be broadcast by vectorize)
            return agg_results[arg]
        else:
            raise KeyError(f"Argument '{arg}' not found in data_in or agg_results")

    def prepare_attribute_args(
        self,
        arg: str,
        data_in: pd.DataFrame,
        agg_results: dict
    ) -> Any:
        """
        Prepare argument data for attribute calculation.

        For attributes, arguments can come from:
        - data_in columns (Case 3: aggregation attributes)
        - agg_results (Case 4: composition attributes)

        Args:
            arg: Argument name
            data_in: Input DataFrame
            agg_results: Aggregation results dict

        Returns:
            Numpy array or scalar value

        Raises:
            KeyError: If argument not found
        """
        if arg in data_in.columns:
            # From data_in - return as numpy array for aggregation
            return data_in[arg].values
        elif arg in agg_results:
            # From agg_results - return scalar for composition
            return agg_results[arg]
        else:
            raise KeyError(f"Argument '{arg}' not found in data_in or agg_results")
