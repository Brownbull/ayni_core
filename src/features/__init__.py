"""
GabeDA Features Package

Modules:
- detector: Feature type detection (aggregation keywords)
- store: Feature storage and filesystem loading
- resolver: Dependency resolution (DFS algorithm)
- analyzer: Feature analysis and execution preparation
"""

from src.features.detector import FeatureTypeDetector
from src.features.store import FeatureStore
from src.features.resolver import DependencyResolver
from src.features.analyzer import FeatureAnalyzer

__all__ = [
    'FeatureTypeDetector',
    'FeatureStore',
    'DependencyResolver',
    'FeatureAnalyzer'
]
