"""
GabeDA Configuration Manager

This module provides configuration management for user and runtime configs.

Responsibilities:
- Store user configuration (immutable)
- Manage runtime configuration per model
- Provide config access methods

Does NOT:
- Validate configuration (use validators)
- Process schemas (use schema processor)
"""

from typing import Dict, Any, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """
    Manages user and runtime configuration.

    Attributes:
        _user_config (Dict): User-provided configuration (immutable)
        _runtime_config (Dict[str, Dict]): Runtime configuration per model
    """

    def __init__(self, user_config: Dict[str, Any]):
        """
        Initialize with user configuration.

        Args:
            user_config: User-provided configuration (stored as immutable copy)
        """
        self._user_config = user_config.copy()
        self._runtime_config: Dict[str, Dict] = {}

        logger.debug(f"ConfigManager initialized with {len(user_config)} user config keys")

    # ==================== User Config Access ====================

    def get_user_config(self, key: str, default: Any = None) -> Any:
        """
        Get value from user config.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self._user_config.get(key, default)

    def get_all_user_config(self) -> Dict:
        """
        Get complete user config (read-only copy).

        Returns:
            Copy of user configuration
        """
        return self._user_config.copy()

    # ==================== Runtime Config Management ====================

    def set_runtime_config(self, model_name: str, config: Dict) -> None:
        """
        Set runtime config for a model.

        Args:
            model_name: Model identifier
            config: Runtime configuration dictionary
        """
        self._runtime_config[model_name] = config.copy()
        logger.debug(f"Runtime config set for '{model_name}' with {len(config)} keys")

    def merge_runtime_config(self, model_name: str, updates: Dict) -> None:
        """
        Merge updates into runtime config.

        Args:
            model_name: Model identifier
            updates: Configuration dictionary to merge
        """
        if model_name not in self._runtime_config:
            self._runtime_config[model_name] = {}

        self._runtime_config[model_name].update(updates)
        logger.debug(f"Runtime config updated for '{model_name}' with {len(updates)} updates")

    def get_runtime_config(self, model_name: str) -> Optional[Dict]:
        """
        Get runtime config for a model.

        Args:
            model_name: Model identifier

        Returns:
            Runtime config dictionary or None if not found
        """
        return self._runtime_config.get(model_name)

    # ==================== Combined Access ====================

    def get_effective_config(self, model_name: str) -> Dict:
        """
        Get merged user + runtime config for a model.

        Runtime config takes precedence over user config for overlapping keys.

        Args:
            model_name: Model identifier

        Returns:
            Merged configuration dictionary
        """
        effective = self._user_config.copy()

        runtime_config = self._runtime_config.get(model_name)
        if runtime_config:
            effective.update(runtime_config)

        return effective

    def __repr__(self) -> str:
        """String representation."""
        return (f"ConfigManager(user_keys={len(self._user_config)}, "
                f"models={len(self._runtime_config)})")
