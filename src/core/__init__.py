"""
Core package for GabeDA Analytics.

Provides state management, configuration handling, and system constants.
"""

from src.core.context import GabedaContext
from src.core.config import ConfigManager
from src.core import constants
from src.core.results import (
    OperationResult,
    ModelOutput,
    GroupResult,
    LoadResult,
    SaveResult,
    ExecutionMetrics,
)

__all__ = [
    'GabedaContext',
    'ConfigManager',
    'constants',
    'OperationResult',
    'ModelOutput',
    'GroupResult',
    'LoadResult',
    'SaveResult',
    'ExecutionMetrics',
]
