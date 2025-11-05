"""
Feature type detection module for GabeDA.

Single Responsibility: Detect feature types ONLY
- Detects if a feature has aggregation (is_aggregation)
- Does NOT store features, resolve dependencies, or execute features
"""

from typing import Callable, Union
from inspect import getsource
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FeatureTypeDetector:
    """
    Detects feature types based on content analysis.

    Responsibilities:
    - Detect if feature has aggregation keywords (groupby_flg)

    Does NOT:
    - Store features (use FeatureStore)
    - Resolve dependencies (use DependencyResolver)
    - Execute features (use execution package)
    """

    # Aggregation keywords that indicate a feature produces group-level output
    AGGREGATION_KEYWORDS = [
        'np.vectorize(',
        'np.where(',
        '#gby',
        '.sum(',
        '.max(',
        '.min(',
        '.unique(',
        '.nunique(',
        '.mean(',
        '.median(',
        '.percentile(',
        '.take(',
        '[first_value]',
        '.nansum(',
        'np.nanmax(',
        'np.nanmin(',
        'flag1',
        'rows_out',
        'agg_out',
        '#agg',
        '.count_nonzero(',
        'zip(',
        'counter(',
    ]

    def is_aggregation(self, feature_def: Union[Callable, str]) -> bool:
        """
        Detect if feature has aggregation keywords.

        This sets the groupby_flg which is used in the 4-case logic:
        - If groupby_flg=True: ALWAYS an ATTRIBUTE (Case 3)
        - If groupby_flg=False: Could be FILTER or ATTRIBUTE (Cases 1, 2, 4)
          - Determined by: if in_flg and not groupby_flg -> FILTER
          - Otherwise -> ATTRIBUTE

        Args:
            feature_def: Function or string containing feature code

        Returns:
            True if aggregation keywords found, False otherwise
        """
        # Convert callable to source code string
        if callable(feature_def):
            try:
                feature_text = getsource(feature_def)
            except (OSError, TypeError):
                # If source not available, assume no aggregation
                logger.warning(f"Could not get source for {feature_def}, assuming no aggregation")
                return False
        else:
            feature_text = str(feature_def)

        # Case-insensitive search
        feature_text_lower = feature_text.lower()

        # Check for any aggregation keyword
        has_aggregation = any(
            keyword.lower() in feature_text_lower
            for keyword in self.AGGREGATION_KEYWORDS
        )

        if has_aggregation:
            logger.debug(f"Aggregation detected in feature (groupby_flg=True)")
        else:
            logger.debug(f"No aggregation detected in feature (groupby_flg=False)")

        return has_aggregation
