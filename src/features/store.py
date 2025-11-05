"""
Feature storage module for GabeDA.

Single Responsibility: Store and retrieve features ONLY
- Stores feature functions and metadata
- Retrieves features by name
- Loads features from filesystem
- Does NOT resolve dependencies or detect types
"""

import json
import inspect
import numpy as np
import pandas as pd
from collections import Counter
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from src.utils.logger import get_logger
from src.utils import (
    ensure_directory, save_json, load_json,
    log_file_operation, log_operation_complete, log_count_summary
)
from src.core import constants

logger = get_logger(__name__)

# Global imports that compiled feature functions may need
# Same as FeatureCalculator.FEATURE_FUNCTION_GLOBALS
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


class FeatureStore:
    """
    Stores and retrieves feature definitions.

    Responsibilities:
    - Store feature functions and metadata
    - Load features from filesystem (feature_index)
    - Retrieve features by name
    - Track available features
    - Save features to filesystem (local or remote)

    Does NOT:
    - Resolve dependencies (use DependencyResolver)
    - Detect types (use FeatureTypeDetector)
    - Execute features (use execution package)
    """

    def __init__(self, fidx_config: Optional[Dict[str, Any]] = None):
        """
        Initialize FeatureStore with optional filesystem configuration.

        Args:
            fidx_config: Feature index configuration with:
                - 'type': 'local', 's3', 'remote', etc.
                - 'path': Base path for local storage (e.g., 'feature_store')
                - 'endpoint': For remote storage (optional)
        """
        self.features: Dict[str, Any] = {}  # "model:feature_name" -> function or dict
        self.current_model: Optional[str] = None  # Track current model context
        self.feature_index: Dict[str, list] = {}  # model_name -> [feature_names]

        # Feature store configuration
        self.fidx_config = fidx_config or {'type': 'local', 'path': 'feature_store'}
        self.storage_type = self.fidx_config.get('type', 'local')
        self.base_path = self.fidx_config.get('path', 'feature_store')
        self.common_folder = 'common'  # Folder name for shared features

        logger.debug(f"FeatureStore initialized - storage_type: {self.storage_type}, base_path: {self.base_path}")

    def store_features(
        self,
        features: Dict[str, Any],
        model_name: Optional[str] = None,
        auto_save: bool = False
    ) -> None:
        """
        Store multiple feature definitions.

        Args:
            features: Dict of feature_name -> function or dict with 'udf' and 'args'
            model_name: Model name for organizing features. If None, features are saved
                       to 'common' folder as shared features available to all models.
            auto_save: If True, save features to filesystem immediately

        Notes:
            - If model_name=None and auto_save=True, features are saved to the 'common' folder
            - Common features are shared across all models
            - Model-specific features override common features with the same name
        """
        for name, feature_def in features.items():
            self.store_feature(name, feature_def)

        if auto_save:
            target = f"model '{model_name}'" if model_name else "'common' (shared features)"
            logger.info(f"Auto-saving {len(features)} features for {target}")
            for name, feature_def in features.items():
                self.save_to_filesystem(name, feature_def, model_name)

    def store_feature(self, name: str, feature_def: Any, model: Optional[str] = None) -> None:
        """
        Store a feature definition with model context.

        Args:
            name: Feature name
            feature_def: Function or dict with 'udf' and 'args'
            model: Model name for scoping (uses current_model if not provided)
        """
        model = model or self.current_model
        key = f"{model}:{name}" if model else name
        self.features[key] = feature_def
        logger.debug(f"Stored feature: {key}")

    def get_feature(self, name: str, model: Optional[str] = None) -> Optional[Any]:
        """
        Retrieve a feature definition with model context.

        Args:
            name: Feature name
            model: Model name for scoping (uses current_model if not provided)

        Returns:
            Feature definition or None if not found
        """
        model = model or self.current_model
        # Try model-scoped key first
        key = f"{model}:{name}" if model else name
        feature_def = self.features.get(key)
        # Fallback to unqualified name for backward compatibility
        if feature_def is None and model:
            feature_def = self.features.get(name)
        return feature_def

    def has_feature(self, name: str) -> bool:
        """
        Check if feature exists in store.

        Args:
            name: Feature name

        Returns:
            True if feature exists
        """
        return name in self.features

    def save_to_filesystem(
        self,
        feature_name: str,
        feature_def: Any,
        model_name: Optional[str] = None
    ) -> None:
        """
        Save a feature to the filesystem.

        Directory structure:
            # Model-specific features
            {base_path}/{model_name}/{feature_name}/
                ├── {feature_name}.py      # Feature function code
                └── metadata.json          # Feature metadata (args, type, etc.)

            # Common/shared features (when model_name=None)
            {base_path}/common/{feature_name}/
                ├── {feature_name}.py
                └── metadata.json

        Args:
            feature_name: Name of the feature
            feature_def: Feature definition (function or dict with 'udf' and 'args')
            model_name: Model name for organizing features. If None, saves to 'common' folder.

        Raises:
            ValueError: If storage_type is not 'local'
            RuntimeError: If unable to extract function source code
        """
        if self.storage_type != 'local':
            raise ValueError(
                f"save_to_filesystem only supports 'local' storage type, got '{self.storage_type}'. "
                "For remote storage, implement a separate save method."
            )

        # Determine target folder (model-specific or common)
        target_folder = model_name if model_name else self.common_folder

        # Build directory structure
        feature_dir = ensure_directory(Path(self.base_path) / target_folder / feature_name, logger=logger)
        feature_file = feature_dir / f"{feature_name}.py"
        metadata_file = feature_dir / "metadata.json"

        # Extract function code and arguments
        if callable(feature_def):
            # Case 1: feature_def is a function
            try:
                source_code = inspect.getsource(feature_def)
            except (OSError, TypeError) as e:
                raise RuntimeError(
                    f"Unable to extract source code for feature '{feature_name}': {e}. "
                    "Ensure the feature is defined in a file (not interactively)."
                )

            # Extract function signature to get arguments
            sig = inspect.signature(feature_def)
            args = list(sig.parameters.keys())

        elif isinstance(feature_def, dict):
            # Case 2: feature_def is a dict with 'udf' and 'args'
            if 'udf' not in feature_def:
                raise ValueError(f"Feature dict for '{feature_name}' must contain 'udf' key")

            udf = feature_def['udf']
            if callable(udf):
                try:
                    source_code = inspect.getsource(udf)
                except (OSError, TypeError) as e:
                    raise RuntimeError(
                        f"Unable to extract source code for feature '{feature_name}': {e}"
                    )
            elif isinstance(udf, str):
                # Already a string (source code)
                source_code = udf
            else:
                raise ValueError(
                    f"Feature '{feature_name}' udf must be a callable or string, got {type(udf)}"
                )

            args = feature_def.get('args', [])

        else:
            raise ValueError(
                f"Feature '{feature_name}' must be a callable or dict with 'udf', got {type(feature_def)}"
            )

        # Save feature code
        with open(feature_file, 'w', encoding='utf-8') as f:
            f.write(source_code)

        # Save metadata
        metadata = {
            'feature_name': feature_name,
            'model_name': model_name if model_name else self.common_folder,
            'is_common': model_name is None,
            'args': args,
            'storage_type': self.storage_type,
            'base_path': self.base_path
        }

        save_json(metadata, metadata_file, logger=logger)

        location = f"common/{feature_name}" if not model_name else f"{model_name}/{feature_name}"
        logger.info(f"Saved feature '{feature_name}' to {self.base_path}/{location}")

    def load_from_filesystem(self, model: str, feature: str, base_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load feature from filesystem and store it.

        Lookup order:
        1. Model-specific folder: {base_path}/{model}/{feature}/
        2. Common folder (fallback): {base_path}/common/{feature}/

        Args:
            model: Model name
            feature: Feature name
            base_path: Base path to feature_index directory (defaults to self.base_path)

        Returns:
            Dict with 'udf' (code string) and 'args' (list)

        Raises:
            FileNotFoundError: If feature files not found in either location
        """
        # Use configured base_path if not provided
        if base_path is None:
            base_path = self.base_path

        # Try model-specific folder first
        feat_path = Path(base_path) / model / feature
        feature_file = feat_path / f"{feature}.py"
        metadata_file = feat_path / "metadata.json"

        # If not found, try common folder
        if not feature_file.exists():
            logger.debug(f"Feature '{feature}' not found in model '{model}', checking common folder...")
            feat_path = Path(base_path) / self.common_folder / feature
            feature_file = feat_path / f"{feature}.py"
            metadata_file = feat_path / "metadata.json"

            if not feature_file.exists():
                raise FileNotFoundError(
                    f"Feature '{feature}' not found in model '{model}' or 'common' folder. "
                    f"Searched: {Path(base_path) / model / feature} and {Path(base_path) / self.common_folder / feature}"
                )
            else:
                logger.info(f"Loading feature '{feature}' from common folder (shared feature)")

        # Read feature function code
        if not feature_file.exists():
            raise FileNotFoundError(f"Feature file not found: {feature_file}")

        with open(feature_file, 'rb') as f:
            udf_code = f.read().decode('utf-8')

        # Read metadata
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

        metadata = load_json(metadata_file, logger=logger)

        feature_def = {
            'udf': udf_code,
            'args': metadata.get('args', [])
        }

        # Store it with model context
        self.store_feature(feature, feature_def, model=model)
        logger.info(f"Loaded feature '{feature}' from model '{model}'")

        return feature_def

    def get_feature_index(self, model: str, base_path: Optional[str] = None) -> list:
        """
        Get list of available features for a model from filesystem.

        Args:
            model: Model name
            base_path: Base path to feature_index directory (defaults to self.base_path)

        Returns:
            List of feature names available in the model directory
        """
        # Use configured base_path if not provided
        if base_path is None:
            base_path = self.base_path

        # Check cache first
        if model in self.feature_index:
            return self.feature_index[model]

        # Build path
        model_path = Path(base_path) / model

        if not model_path.exists():
            logger.warning(f"Model path not found: {model_path}")
            self.feature_index[model] = []
            return []

        # Get subdirectories (each is a feature)
        try:
            feature_names = [
                d.name for d in model_path.iterdir()
                if d.is_dir()
            ]
            self.feature_index[model] = feature_names
            log_count_summary(logger, f"features in model '{model}'", len(feature_names),
                            items=feature_names)
            return feature_names
        except Exception as e:
            logger.error(f"Error reading feature index for model '{model}': {e}")
            self.feature_index[model] = []
            return []

    def load_common_features(self, base_path: Optional[str] = None) -> int:
        """
        Load all common (shared) features from the 'common' folder.

        Args:
            base_path: Base path to feature_index directory (defaults to self.base_path)

        Returns:
            Number of common features loaded

        Example:
            feature_store.load_common_features()
            # Loads all features from feature_store/common/
        """
        # Use configured base_path if not provided
        if base_path is None:
            base_path = self.base_path

        # Get list of common features
        common_features = self.get_feature_index(self.common_folder, base_path)

        if not common_features:
            logger.info("No common features found")
            return 0

        # Load each common feature
        loaded_count = 0
        for feature_name in common_features:
            try:
                self.load_from_filesystem(self.common_folder, feature_name, base_path)
                loaded_count += 1
            except Exception as e:
                logger.warning(f"Failed to load common feature '{feature_name}': {e}")

        logger.info(f"Loaded {loaded_count}/{len(common_features)} common features")
        return loaded_count

    def save_master_config(
        self,
        model_name: str,
        model_config: Dict[str, Any]
    ) -> None:
        """
        Save master configuration file for a model.

        Args:
            model_name: Model name
            model_config: Configuration dict containing:
                - exec_seq: Execution sequence (model_seq in master_cfg.json)
                - group_by: Group by column(s) (optional)
                - row_id: Row ID column (optional)
                - input_dataset_name: Name of input dataset (optional)
                - external_data: External data configuration (optional)
                - ext_cols: External columns resolved from external_data (optional)

        Raises:
            ValueError: If storage_type is not 'local'
        """
        if self.storage_type != 'local':
            raise ValueError(f"save_master_config only supports 'local' storage type")

        model_dir = ensure_directory(Path(self.base_path) / model_name, logger=logger)
        master_cfg_file = model_dir / "master_cfg.json"

        master_cfg = {
            'model_name': model_name,
            'model_seq': model_config.get('exec_seq', []),
            'group_by': model_config.get('group_by'),
            'row_id': model_config.get('row_id'),
            'input_dataset_name': model_config.get('input_dataset_name')
        }

        # Add external_data configuration if present
        if 'external_data' in model_config:
            master_cfg['external_data'] = model_config['external_data']

        # Add ext_cols if present (resolved external columns)
        if 'ext_cols' in model_config:
            master_cfg['ext_cols'] = model_config['ext_cols']

        save_json(master_cfg, master_cfg_file, logger=logger)
        logger.info(f"Saved master_cfg.json for model '{model_name}'")

    def load_master_config(
        self,
        model_name: str,
        base_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load master configuration file for a model.

        Args:
            model_name: Model name
            base_path: Base path to feature_index directory (defaults to self.base_path)

        Returns:
            Dict containing model_name, model_seq, group_by, and row_id

        Raises:
            FileNotFoundError: If master_cfg.json not found
        """
        if base_path is None:
            base_path = self.base_path

        master_cfg_file = Path(base_path) / model_name / "master_cfg.json"

        if not master_cfg_file.exists():
            raise FileNotFoundError(f"master_cfg.json not found for model '{model_name}' at {master_cfg_file}")

        master_cfg = load_json(master_cfg_file, logger=logger)
        logger.info(f"Loaded master_cfg.json for model '{model_name}'")
        return master_cfg

    def save_model(self, cfg_model: Dict[str, Any]) -> None:
        """
        Consolidated method to save features and master_cfg in one call.

        Args:
            cfg_model: Model configuration dict containing:
                - model_name: Model name (required)
                - features: Dict of feature definitions (required)
                - exec_seq: Execution sequence (optional, for master_cfg.json)
                - group_by: Group by column(s) (optional, for master_cfg.json)
                - row_id: Row ID column (optional, for master_cfg.json)

        Raises:
            ValueError: If model_name or features not provided

        Example:
            cfg_product = {
                'model_name': 'product',
                'features': {
                    'revenue': lambda price, quantity: price * quantity,
                    'profit': lambda revenue, cost: revenue - cost
                },
                'exec_seq': ['revenue', 'profit'],
                'group_by': 'product_id',
                'row_id': 'transaction_id'
            }
            feature_store.save_model(cfg_product)
        """
        if 'model_name' not in cfg_model:
            raise ValueError("cfg_model must contain 'model_name'")
        if 'features' not in cfg_model:
            raise ValueError("cfg_model must contain 'features'")

        model_name = cfg_model['model_name']
        features = cfg_model['features']

        # Store and save features
        self.store_features(features=features, model_name=model_name, auto_save=True)
        logger.info(f"Saved {len(features)} features for model '{model_name}'")

        # Save master configuration if exec_seq is provided
        if 'exec_seq' in cfg_model:
            self.save_master_config(model_name, cfg_model)
        else:
            logger.warning(f"No 'exec_seq' found in cfg_model - master_cfg.json not saved")

    def load_model(self, model_name: str) -> Dict[str, Any]:
        """
        Load complete model: features, master config, and compile in one call.

        This is the recommended method for loading models from feature_store.
        It combines get_feature_index(), load_from_filesystem(), load_master_config(),
        and compile_features() into a single convenient method.

        The returned master_cfg is execution-ready and can be used directly with
        execute_model() after adding 'in_cols' via resolve_dependencies().

        Args:
            model_name: Model name (e.g., 'customer_profile', 'product_month')

        Returns:
            Dict containing:
                - 'master_cfg': Execution-ready config with compiled features
                  (just needs 'in_cols' added to use with execute_model)
                - 'compiled_features': Dict of feature_name -> compiled function (for reference)
                - 'feature_names': List of feature names (for reference)

        Example:
            feature_store = FeatureStore()
            model = feature_store.load_model('customer_profile')

            # Extract execution-ready config
            cfg_model = model['master_cfg']

            # Resolve dependencies and add in_cols
            resolver = DependencyResolver(feature_store)
            in_cols, _, _ = resolver.resolve_dependencies(
                output_cols=cfg_model['output_cols'],
                available_cols=input_df.columns.tolist(),
                group_by=cfg_model.get('group_by'),
                model=model_name
            )
            cfg_model['in_cols'] = in_cols

            # Ready to execute!
            output = executor.execute_model(cfg_model, input_dataset_name=...)

        Raises:
            FileNotFoundError: If model directory or master_cfg.json not found
        """
        logger.info(f"Loading model '{model_name}' from feature_store...")

        # Set current model context for feature scoping
        self.current_model = model_name

        # Step 1: Get list of features for this model
        feature_names = self.get_feature_index(model_name)
        if not feature_names:
            raise FileNotFoundError(
                f"No features found for model '{model_name}' in {self.base_path}/{model_name}"
            )
        logger.info(f"  Found {len(feature_names)} features: {feature_names}")

        # Step 2: Load each feature from filesystem
        for feature_name in feature_names:
            self.load_from_filesystem(model_name, feature_name)
        logger.info(f"  Loaded {len(feature_names)} feature definitions from filesystem")

        # Step 3: Load master configuration
        master_cfg = self.load_master_config(model_name)
        logger.info(f"  Loaded master configuration")

        # Step 4: Compile features (will use current_model context)
        compiled_features = self.compile_features(feature_names, model_name=model_name)
        logger.info(f"  Compiled {len(compiled_features)} feature functions")

        # Step 5: Build execution-ready master_cfg (add compiled features)
        # This makes master_cfg compatible with execute_model() - just needs in_cols added
        master_cfg['features'] = compiled_features
        master_cfg['output_cols'] = master_cfg['model_seq']  # Alias for compatibility
        master_cfg['exec_seq'] = master_cfg['model_seq']  # Alias for compatibility

        # Log summary of loaded model
        logger.info(f"✓ Model '{model_name}' loaded successfully!")
        logger.info(f"  - Total features: {len(compiled_features)}")
        logger.info(f"  - Execution sequence: {len(master_cfg['exec_seq'])} steps")
        logger.info(f"  - Group by: {master_cfg.get('group_by', 'None')}")

        return {
            'master_cfg': master_cfg,  # Execution-ready (just needs in_cols)
            'compiled_features': compiled_features,  # For reference
            'feature_names': feature_names  # For reference
        }

    def compile_features(self, feature_names: Optional[list] = None, model_name: Optional[str] = None) -> Dict[str, Callable]:
        """
        Compile feature code strings into callable functions.

        When features are loaded from filesystem, they are stored as code strings
        in the 'udf' field. This method compiles them into executable functions.

        Args:
            feature_names: List of feature names to compile. If None, compiles all
                          features that have 'udf' code strings.
            model_name: Model context for feature lookup

        Returns:
            Dict of feature_name -> compiled function

        Example:
            feature_store = FeatureStore()
            feature_names = feature_store.get_feature_index('customer_profile')
            for fname in feature_names:
                feature_store.load_from_filesystem('customer_profile', fname)

            # Compile all loaded features
            compiled = feature_store.compile_features(feature_names, model_name='customer_profile')

        Note:
            - Compiled functions will have imports injected by FeatureCalculator
            - Only compiles features with 'udf' code strings, skips already-callable features
        """
        if feature_names is None:
            feature_names = list(self.features.keys())

        compiled_features = {}

        for feature_name in feature_names:
            feature_def = self.get_feature(feature_name, model=model_name)

            if feature_def is None:
                logger.warning(f"Feature '{feature_name}' not found in store, skipping")
                continue

            if isinstance(feature_def, dict) and 'udf' in feature_def:
                # Feature stored as code string - compile it
                local_ns = {}

                try:
                    # Execute the code string to define the function
                    # Inject necessary globals (np, pd, Counter, DEFAULT_FLOAT) so exec can compile
                    global_ns = {'__builtins__': __builtins__}
                    global_ns.update(FEATURE_FUNCTION_GLOBALS)
                    exec(feature_def['udf'], global_ns, local_ns)

                    # Extract the function from local namespace
                    compiled_features[feature_name] = local_ns[feature_name]
                    logger.debug(f"Compiled feature '{feature_name}' from code string")

                except Exception as e:
                    logger.error(f"Failed to compile feature '{feature_name}': {e}")
                    raise RuntimeError(f"Failed to compile feature '{feature_name}': {e}")

            elif callable(feature_def):
                # Already a callable function
                compiled_features[feature_name] = feature_def
                logger.debug(f"Feature '{feature_name}' already callable, using as-is")

            else:
                logger.warning(f"Feature '{feature_name}' is neither code string nor callable, skipping")

        logger.info(f"Compiled {len(compiled_features)} features")
        return compiled_features

    def clear(self) -> None:
        """Clear all stored features."""
        self.features.clear()
        self.feature_index.clear()
        logger.debug("Cleared feature store")
