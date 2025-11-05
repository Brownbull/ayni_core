"""
Standardized Result Classes for GabeDA

Single Responsibility: Provide consistent result/output data structures

Provides standardized classes for:
- Generic operation results
- Model execution outputs
- Group processing results
- Validation results (compatible with existing ValidationResult)

Usage:
    from src.core.results import OperationResult, ModelOutput

    # Generic operation result
    result = OperationResult(
        success=True,
        data={'key': 'value'},
        metadata={'duration': 1.5}
    )

    # Model execution output
    output = ModelOutput(
        model_name='model1',
        input_dataset_name='preprocessed',
        filters=filters_df,
        attrs=attrs_df
    )

Does NOT:
- Execute operations (use execution modules)
- Validate results (use validators)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import pandas as pd
from datetime import datetime


@dataclass
class OperationResult:
    """
    Generic result for any operation.

    Use this for operations that need to return success/failure status
    along with data, errors, warnings, and metadata.

    Attributes:
        success: Whether operation succeeded
        data: Operation result data (any type)
        errors: List of error messages
        warnings: List of warning messages
        metadata: Additional context/metadata

    Examples:
        >>> result = OperationResult(success=True, data={'count': 5})
        >>> result.add_warning('Low memory')
        >>> result.has_warnings()
        True
    """
    success: bool
    data: Optional[Any] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_error(self, error: str) -> None:
        """Add error and mark as failed"""
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str) -> None:
        """Add warning (doesn't affect success)"""
        self.warnings.append(warning)

    def has_errors(self) -> bool:
        """Check if has errors"""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if has warnings"""
        return len(self.warnings) > 0

    def is_complete_success(self) -> bool:
        """Check if succeeded with no warnings"""
        return self.success and not self.has_warnings()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'success': self.success,
            'data': self.data,
            'errors': self.errors,
            'warnings': self.warnings,
            'metadata': self.metadata
        }


@dataclass
class ModelOutput:
    """
    Standardized model execution output.

    This replaces the implicit dict structure used in executor.py
    with a typed data class.

    Attributes:
        model_name: Model identifier
        input_dataset_name: Name of input dataset used
        filters: DataFrame with filter results (row-level)
        attrs: DataFrame with attribute results (aggregated)
        exec_fltrs: List of filter feature names calculated
        exec_attrs: List of attribute feature names calculated
        execution_time: Time taken to execute (seconds)
        status: Execution status ('success', 'warning', 'error')
        metadata: Additional execution metadata

    Examples:
        >>> output = ModelOutput(
        ...     model_name='daily_model',
        ...     input_dataset_name='preprocessed',
        ...     filters=filters_df,
        ...     attrs=attrs_df,
        ...     exec_fltrs=['margin_unit', 'profit_pct'],
        ...     exec_attrs=['total_revenue', 'total_cost']
        ... )
        >>> output.has_filters()
        True

    Use Cases:
        # executor.py:64-71 - Replace dict return
        return ModelOutput(
            model_name=model_name,
            input_dataset_name=input_dataset_name,
            filters=filters_df,
            attrs=attrs_df,
            exec_fltrs=exec_fltrs,
            exec_attrs=exec_attrs,
            metadata=cfg_model
        )
    """
    model_name: str
    input_dataset_name: str
    filters: Optional[pd.DataFrame] = None
    attrs: Optional[pd.DataFrame] = None
    exec_fltrs: List[str] = field(default_factory=list)
    exec_attrs: List[str] = field(default_factory=list)
    execution_time: Optional[float] = None
    status: str = 'success'
    metadata: Dict[str, Any] = field(default_factory=dict)

    def has_filters(self) -> bool:
        """Check if has filter results"""
        return self.filters is not None and len(self.filters) > 0

    def has_attrs(self) -> bool:
        """Check if has attribute results"""
        return self.attrs is not None and len(self.attrs) > 0

    def filter_count(self) -> int:
        """Get number of filters calculated"""
        return len(self.exec_fltrs)

    def attr_count(self) -> int:
        """Get number of attributes calculated"""
        return len(self.exec_attrs)

    def total_features(self) -> int:
        """Get total number of features calculated"""
        return self.filter_count() + self.attr_count()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary (for backward compatibility).

        Returns dict matching the structure expected by context.set_model_output()
        """
        return {
            'input_dataset_name': self.input_dataset_name,
            'filters': self.filters,
            'attrs': self.attrs,
            'exec_fltrs': self.exec_fltrs,
            'exec_attrs': self.exec_attrs,
            'config': self.metadata,  # For backward compatibility
            'execution_time': self.execution_time,
            'status': self.status
        }


@dataclass
class GroupResult:
    """
    Result from processing a single group.

    Used in groupby operations to track filter and attribute calculations
    for a specific group.

    Attributes:
        group_id: Group identifier (value or tuple of values)
        data_in: DataFrame with filter results for this group
        agg_results: Dict of attribute results for this group
        filters_calculated: List of filter feature names calculated
        attrs_calculated: List of attribute feature names calculated
        row_count: Number of rows in group

    Examples:
        >>> result = GroupResult(
        ...     group_id='ProductA',
        ...     data_in=group_df,
        ...     agg_results={'total_revenue': 1000, 'total_cost': 600},
        ...     filters_calculated=['margin_unit', 'profit_pct'],
        ...     attrs_calculated=['total_revenue', 'total_cost']
        ... )
        >>> result.has_filters()
        True

    Use Cases:
        # groupby.py:81-82 - Replace implicit dict
        return GroupResult(
            group_id=group_id,
            data_in=data_in,
            agg_results=agg_results,
            filters_calculated=filters_calc,
            attrs_calculated=attrs_calc,
            row_count=len(data_in)
        )
    """
    group_id: Any
    data_in: pd.DataFrame
    agg_results: Dict[str, Any]
    filters_calculated: List[str] = field(default_factory=list)
    attrs_calculated: List[str] = field(default_factory=list)
    row_count: Optional[int] = None

    def __post_init__(self):
        """Set row_count if not provided"""
        if self.row_count is None and self.data_in is not None:
            self.row_count = len(self.data_in)

    def has_filters(self) -> bool:
        """Check if has filter results"""
        return len(self.filters_calculated) > 0

    def has_attrs(self) -> bool:
        """Check if has attribute results"""
        return len(self.attrs_calculated) > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'group_id': self.group_id,
            'data_in': self.data_in,
            'agg_results': self.agg_results,
            'filters_calculated': self.filters_calculated,
            'attrs_calculated': self.attrs_calculated,
            'row_count': self.row_count
        }


# For backward compatibility with existing ValidationResult in validators.py
# We re-export it here so it can be imported from results.py
# This allows gradual migration: from src.core.results import ValidationResult
try:
    from src.preprocessing.validators import ValidationResult
    __all__ = ['OperationResult', 'ModelOutput', 'GroupResult', 'ValidationResult']
except ImportError:
    # ValidationResult not available yet (during initial module load)
    __all__ = ['OperationResult', 'ModelOutput', 'GroupResult']


# Additional result types for future use

@dataclass
class LoadResult:
    """
    Result from data loading operations.

    Attributes:
        data: Loaded DataFrame
        source: Source path/identifier
        rows_loaded: Number of rows loaded
        columns_loaded: Number of columns loaded
        load_time: Time taken to load (seconds)
        warnings: List of warnings during load
    """
    data: pd.DataFrame
    source: str
    rows_loaded: Optional[int] = None
    columns_loaded: Optional[int] = None
    load_time: Optional[float] = None
    warnings: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Set row/column counts if not provided"""
        if self.rows_loaded is None:
            self.rows_loaded = len(self.data)
        if self.columns_loaded is None:
            self.columns_loaded = len(self.data.columns)

    def has_warnings(self) -> bool:
        """Check if has warnings"""
        return len(self.warnings) > 0


@dataclass
class SaveResult:
    """
    Result from data save operations.

    Attributes:
        path: Saved file path
        rows_saved: Number of rows saved
        columns_saved: Number of columns saved
        save_time: Time taken to save (seconds)
        file_size_bytes: Size of saved file
    """
    path: str
    rows_saved: int
    columns_saved: int
    save_time: Optional[float] = None
    file_size_bytes: Optional[int] = None

    def file_size_mb(self) -> Optional[float]:
        """Get file size in MB"""
        if self.file_size_bytes is not None:
            return self.file_size_bytes / (1024 * 1024)
        return None


@dataclass
class ExecutionMetrics:
    """
    Execution performance metrics.

    Attributes:
        operation: Operation name
        start_time: Operation start timestamp
        end_time: Operation end timestamp
        duration_seconds: Duration in seconds
        memory_used_mb: Memory used in MB
        rows_processed: Number of rows processed
    """
    operation: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    memory_used_mb: Optional[float] = None
    rows_processed: Optional[int] = None

    def complete(self, end_time: Optional[datetime] = None) -> None:
        """Mark operation as complete and calculate duration"""
        self.end_time = end_time or datetime.now()
        self.duration_seconds = (self.end_time - self.start_time).total_seconds()

    def is_complete(self) -> bool:
        """Check if execution is complete"""
        return self.end_time is not None


# Update __all__ to include additional types
__all__.extend(['LoadResult', 'SaveResult', 'ExecutionMetrics'])
