"""
GabeDA Execution Package

CRITICAL: Contains the 4-case logic for single-loop execution.

Modules:
- calculator: Feature calculation (filters and attributes)
- groupby: Single-loop group processing with 4-case logic
- executor: Single model execution coordinator
- orchestrator: Multi-model pipeline orchestration

The 4-Case Logic (in groupby.py):
==================================
Case 1: Filter (standard) - in_flg=T, out_flg=F, groupby_flg=F
Case 2: Filter (using attributes) - in_flg=T, out_flg=T, groupby_flg=F [KEY INNOVATION]
Case 3: Attribute (aggregation) - groupby_flg=T
Case 4: Attribute (composition) - in_flg=F, groupby_flg=F

Decision: if in_flg and not groupby_flg -> FILTER else -> ATTRIBUTE
"""

from src.execution.calculator import FeatureCalculator
from src.execution.groupby import GroupByProcessor
from src.execution.executor import ModelExecutor
from src.execution.orchestrator import ExecutionOrchestrator
from src.execution.external_data import ExternalDataManager

__all__ = [
    'FeatureCalculator',
    'GroupByProcessor',
    'ModelExecutor',
    'ExecutionOrchestrator',
    'ExternalDataManager',
]
