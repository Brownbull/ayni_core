"""
Synthetic feature enrichment module for GabeDA preprocessing.

Single Responsibility: Apply synthetic features to enrich preprocessed data ONLY
- Detects which synthetic features can be applied based on available columns
- Executes features in enrichment mode (no grouping)
- Returns enriched DataFrame with inferred columns
- Does NOT modify original data (returns new DataFrame)
"""

import pandas as pd
from typing import Dict, Any, List, Set, Tuple, Optional
from src.features.store import FeatureStore
from src.features.resolver import DependencyResolver
from src.features.analyzer import FeatureAnalyzer
from src.features.detector import FeatureTypeDetector
from src.execution.calculator import FeatureCalculator
from src.execution.groupby import GroupByProcessor
from src.execution.executor import ModelExecutor
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SyntheticEnricher:
    """
    Enriches preprocessed data with synthetic (inferable) features.

    Responsibilities:
    - Load synthetic features from feature store
    - Detect which features can be applied to current data
    - Execute features in enrichment mode
    - Return enriched DataFrame

    Does NOT:
    - Modify original data
    - Perform schema processing (preprocessing package does this)
    - Store results (caller does this)
    """

    # Allowed column names in the output (from base_case.csv)
    ALLOWED_COLUMNS = {
        'in_dt', 'in_trans_id', 'in_trans_type', 'in_customer_id',
        'in_product_id', 'in_description', 'in_category', 'in_unit_type',
        'in_stock', 'in_quantity', 'in_cost_unit', 'in_cost_total',
        'in_price_unit', 'in_price_total', 'in_discount_total',
        'in_commission_total', 'in_margin'
    }

    # Map feature function names to their target column names
    # This maps the function name to the actual column it should produce
    FEATURE_TO_COLUMN_MAP = {
        'in_cost_unit': 'in_cost_unit',
        'in_cost_total': 'in_cost_total',
        'in_price_unit': 'in_price_unit',
        'in_price_total': 'in_price_total',
        'in_discount_total_from_gross': 'in_discount_total',
        'in_discount_total_from_rate': 'in_discount_total',
        'in_commission_total_from_rate': 'in_commission_total',
        'in_commission_total_from_margin': 'in_commission_total',
        'in_margin_from_totals': 'in_margin',
        'in_margin_from_units': 'in_margin',
        'in_margin_with_discounts': 'in_margin',
        'in_margin': 'in_margin',
    }

    def __init__(
        self,
        synthetic_model_name: str = 'synthetic',
        feature_store_path: str = 'feature_store'
    ):
        """
        Initialize synthetic enricher.

        IMPORTANT: Creates its own independent FeatureStore and loads features
        from the filesystem. Does NOT use features defined in notebooks.

        Args:
            synthetic_model_name: Model name for synthetic features (default: 'synthetic')
            feature_store_path: Path to feature store directory (default: 'feature_store')
        """
        # Create independent feature store
        self.feature_store = FeatureStore()
        self.synthetic_model_name = synthetic_model_name
        self.feature_store_path = feature_store_path

        # Initialize execution components
        self.detector = FeatureTypeDetector()
        self.resolver = DependencyResolver(self.feature_store)
        self.analyzer = FeatureAnalyzer(self.feature_store, self.detector)
        self.calculator = FeatureCalculator()
        self.groupby_processor = GroupByProcessor(self.calculator, self.detector)
        self.executor = ModelExecutor(self.analyzer, self.groupby_processor)

        # Load synthetic features from filesystem on initialization
        self._load_synthetic_features()

        logger.info(f"SyntheticEnricher initialized with {len(self.feature_store.features)} features from '{synthetic_model_name}' model")

    def detect_applicable_features(
        self,
        available_columns: List[str],
        target_columns: Optional[List[str]] = None
    ) -> Tuple[List[str], List[str]]:
        """
        Detect which synthetic features can be applied to the data.

        Args:
            available_columns: Columns currently in the DataFrame
            target_columns: Optional list of specific columns to infer (if None, tries all)

        Returns:
            Tuple of (applicable_features, missing_columns)
            - applicable_features: Feature names that can be executed
            - missing_columns: Columns that are missing but can be inferred
        """
        available_set = set(available_columns)

        # Get all features from the synthetic model
        feature_index = self.feature_store.get_feature_index(
            self.synthetic_model_name,
            base_path='feature_store'
        )

        logger.info(f"Found {len(feature_index)} synthetic features in feature store")

        # Determine target columns
        if target_columns is None:
            # Try to infer all allowed columns that are missing
            target_columns = [col for col in self.ALLOWED_COLUMNS if col not in available_set]

        logger.info(f"Target columns to infer: {target_columns}")

        # Map target columns to feature names
        applicable_features = []
        missing_columns = []

        for target_col in target_columns:
            # Find features that produce this column
            candidate_features = [
                feat_name for feat_name, col_name in self.FEATURE_TO_COLUMN_MAP.items()
                if col_name == target_col and feat_name in feature_index
            ]

            if candidate_features:
                # Try each candidate feature to see if it can be resolved
                for feat_name in candidate_features:
                    try:
                        # Check if this feature can be resolved with available columns
                        in_cols, exec_seq = self.resolver.resolve_dependencies(
                            output_cols=[feat_name],
                            available_cols=available_columns,
                            group_by=None,  # Enrichment mode
                            model=self.synthetic_model_name
                        )

                        # CRITICAL: Validate that ALL input columns are actually available
                        # Resolver may add columns to in_cols as "not in feature_index"
                        # but we need to ensure they actually exist in the data
                        missing_inputs = [col for col in in_cols if col not in available_set]
                        if missing_inputs:
                            logger.debug(f"Feature '{feat_name}' requires unavailable columns: {missing_inputs}")
                            continue  # Skip this feature

                        # If exec_seq contains the feature AND all inputs exist, it can be calculated
                        if feat_name in exec_seq:
                            applicable_features.append(feat_name)
                            missing_columns.append(target_col)
                            logger.info(f"✓ Can infer '{target_col}' using feature '{feat_name}'")
                            break  # Use first matching feature
                    except Exception as e:
                        logger.debug(f"Feature '{feat_name}' cannot be applied: {e}")
                        continue

        return applicable_features, missing_columns

    def enrich(
        self,
        data: pd.DataFrame,
        target_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Enrich data with synthetic features.

        Features are loaded from filesystem during __init__, not here.

        Args:
            data: Input DataFrame (preprocessed)
            target_columns: Optional specific columns to infer (if None, tries all)

        Returns:
            Enriched DataFrame with inferred columns

        Raises:
            ValueError: If output contains disallowed column names
        """
        logger.info("Starting synthetic enrichment...")
        logger.info(f"Input shape: {data.shape}")
        logger.info(f"Input columns: {list(data.columns)}")

        # Detect applicable features
        applicable_features, missing_columns = self.detect_applicable_features(
            available_columns=data.columns.tolist(),
            target_columns=target_columns
        )

        if not applicable_features:
            logger.info("No synthetic features applicable - returning original data")
            return data.copy()

        logger.info(f"Applying {len(applicable_features)} synthetic features...")
        logger.info(f"Will infer columns: {missing_columns}")

        # Resolve dependencies for the applicable features
        try:
            in_cols, exec_seq = self.resolver.resolve_dependencies(
                output_cols=applicable_features,
                available_cols=data.columns.tolist(),
                group_by=None,  # Enrichment mode
                model=self.synthetic_model_name
            )
        except Exception as e:
            logger.error(f"Failed to resolve dependencies: {e}")
            logger.warning("Returning original data")
            return data.copy()

        if not exec_seq:
            logger.warning("No features in execution sequence - returning original data")
            return data.copy()

        logger.info(f"Resolved execution sequence: {exec_seq}")

        # Build model configuration for enrichment mode
        cfg_model = {
            'model_name': 'synthetic_enrichment',
            'group_by': None,  # CRITICAL: Enrichment mode
            'output_cols': applicable_features,
            'in_cols': in_cols,
            'exec_seq': exec_seq,  # Add resolved execution sequence
            'features': {}  # Features already in store
        }

        # Execute model in enrichment mode
        try:
            output = self.executor.execute_model(
                data_in=data,
                cfg_model=cfg_model,
                input_dataset_name='synthetic_input'
            )

            # Get enriched data (filters contains all columns in enrichment mode)
            enriched_data = output['filters']

            if enriched_data is None or enriched_data.empty:
                logger.warning("Enrichment produced no data - returning original")
                return data.copy()

            # CRITICAL: Rename feature columns to target column names
            # Features may have names like 'in_margin_from_totals' but should produce 'in_margin'
            rename_map = {}
            for feat_name in applicable_features:
                if feat_name in enriched_data.columns:
                    target_col = self.FEATURE_TO_COLUMN_MAP.get(feat_name, feat_name)
                    if feat_name != target_col:
                        rename_map[feat_name] = target_col
                        logger.debug(f"Renaming feature column '{feat_name}' -> '{target_col}'")

            if rename_map:
                enriched_data = enriched_data.rename(columns=rename_map)
                logger.info(f"Renamed {len(rename_map)} feature columns to target column names")

            # Validate column names
            invalid_cols = [col for col in enriched_data.columns if col not in self.ALLOWED_COLUMNS]
            if invalid_cols:
                raise ValueError(
                    f"Enrichment produced disallowed columns: {invalid_cols}. "
                    f"Allowed columns: {sorted(self.ALLOWED_COLUMNS)}"
                )

            logger.info(f"Enrichment complete!")
            logger.info(f"Output shape: {enriched_data.shape}")
            logger.info(f"Added columns: {[col for col in enriched_data.columns if col not in data.columns]}")

            return enriched_data

        except Exception as e:
            logger.error(f"Synthetic enrichment failed: {e}")
            logger.warning("Returning original data due to enrichment failure")
            return data.copy()

    def _load_synthetic_features(self):
        """Load synthetic features from feature store filesystem."""
        logger.info(f"Loading synthetic features from model '{self.synthetic_model_name}' at '{self.feature_store_path}'...")

        try:
            # Get feature index
            feature_index = self.feature_store.get_feature_index(
                self.synthetic_model_name,
                base_path=self.feature_store_path
            )

            if not feature_index:
                logger.warning(f"No features found in feature index for model '{self.synthetic_model_name}'")
                logger.warning(f"Expected location: {self.feature_store_path}/{self.synthetic_model_name}/")
                return

            # Load each feature
            loaded_count = 0
            for feat_name in feature_index:
                if not self.feature_store.has_feature(feat_name):
                    self.feature_store.load_from_filesystem(
                        model=self.synthetic_model_name,
                        feature=feat_name,  # FIXED: parameter is 'feature' not 'feature_name'
                        base_path=self.feature_store_path
                    )
                    loaded_count += 1

            logger.info(f"Loaded {loaded_count} synthetic features from filesystem")
            logger.info(f"Total features in store: {len(self.feature_store.features)}")

        except Exception as e:
            logger.warning(f"Could not load synthetic features: {e}")
            logger.warning(f"Enricher will not be able to infer any columns without features")
            logger.info(f"To fix: Ensure synthetic features are saved in {self.feature_store_path}/{self.synthetic_model_name}/")

    def get_lucky_score(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate "luck score" - how many columns can be inferred from current data.

        Args:
            data: Input DataFrame

        Returns:
            Dict with:
            - luck_score: Number of columns that can be inferred
            - total_possible: Total number of inferable columns
            - luck_percentage: Percentage (0-100)
            - applicable_features: List of feature names that can be applied
            - missing_columns: List of columns that can be inferred
        """
        applicable_features, missing_columns = self.detect_applicable_features(
            available_columns=data.columns.tolist()
        )

        total_inferable = len([col for col in self.ALLOWED_COLUMNS if col not in data.columns])
        luck_score = len(missing_columns)
        luck_pct = (luck_score / total_inferable * 100) if total_inferable > 0 else 100

        return {
            'luck_score': luck_score,
            'total_possible': total_inferable,
            'luck_percentage': luck_pct,
            'applicable_features': applicable_features,
            'missing_columns': missing_columns
        }
