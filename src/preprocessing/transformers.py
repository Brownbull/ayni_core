"""
Data transformation module for GabeDA preprocessing.

Single Responsibility: Data transformation (mapping, type conversion) ONLY
- Maps columns from source names to target names
- Converts data types (date, int, float, str)
- Handles numeric formatting (thousands, decimals)
- Does NOT validate or load data
"""

import pandas as pd
from typing import Dict, Any, Tuple, List, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ColumnMapper:
    """
    Maps columns from source names to target names.

    Responsibilities:
    - Rename columns according to schema
    - Track available vs missing columns

    Does NOT:
    - Convert types (use TypeConverter)
    - Validate data (use DataValidator)
    """

    def map_columns(self, df: pd.DataFrame, schema: Dict[str, Dict]) -> Tuple[pd.DataFrame, List[str], List[str]]:
        """
        Map columns according to schema.

        Args:
            df: DataFrame with original column names
            schema: Mapping from target_col -> {'source_column': source_col, ...}

        Returns:
            Tuple of (mapped_df, available_cols, missing_cols)
        """
        df = df.copy()  # Don't modify original
        available_cols = []
        missing_cols = []

        for target_col, col_spec in schema.items():
            source_col = col_spec.get('source_column')

            if source_col and source_col in df.columns:
                if source_col != target_col:
                    df = df.rename(columns={source_col: target_col})
                    logger.info(f"Mapped '{source_col}' → '{target_col}'")
                available_cols.append(target_col)
            else:
                missing_cols.append(target_col)
                logger.debug(f"Column '{target_col}' (source: '{source_col}') not found")

        return df, available_cols, missing_cols


class TypeConverter:
    """
    Converts column data types.

    Responsibilities:
    - Convert to date, int, float, str
    - Handle numeric formatting (thousands, decimals)
    - Clean numeric strings

    Does NOT:
    - Validate data (use DataValidator)
    - Map columns (use ColumnMapper)
    """

    def convert_types(self, df: pd.DataFrame, schema: Dict[str, Dict],
                     default_formats: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Convert column types according to schema.

        Args:
            df: DataFrame with columns to convert
            schema: Schema with dtype specifications
            default_formats: Optional default formats by dtype (e.g., {'date': '%Y-%m-%d', 'float': {...}})

        Returns:
            DataFrame with converted types
        """
        df = df.copy()  # Don't modify original

        for target_col, col_spec in schema.items():
            if target_col not in df.columns:
                continue

            dtype = col_spec.get('dtype')
            if not dtype:
                continue

            # Get format: column-specific or default
            format_spec = col_spec.get('format')

            # If format is None (not specified) and default_formats exist, use default
            if format_spec is None and default_formats:
                format_spec = default_formats.get(dtype)
                if format_spec:
                    logger.debug(f"Using default format for '{target_col}' ({dtype}): {format_spec}")

            if dtype == 'date':
                df[target_col] = self.convert_dates(df[target_col], format_spec)
                logger.info(f"Converted '{target_col}' to date")
            elif dtype == 'int':
                df[target_col] = self.convert_numeric(df[target_col], format_spec, 'integer')
                logger.info(f"Converted '{target_col}' to int")
            elif dtype == 'float':
                df[target_col] = self.convert_numeric(df[target_col], format_spec, 'float')
                logger.info(f"Converted '{target_col}' to float")
            elif dtype == 'str':
                df[target_col] = df[target_col].astype(str)
                logger.info(f"Converted '{target_col}' to str")

        return df

    def convert_dates(self, series: pd.Series, format_spec: Any) -> pd.Series:
        """
        Convert series to datetime.

        Args:
            series: Series to convert
            format_spec: Date format string or dict

        Returns:
            Series with datetime values
        """
        if isinstance(format_spec, str):
            return pd.to_datetime(series, format=format_spec, errors='coerce')
        elif isinstance(format_spec, dict):
            # Dict format (e.g., {'pattern': '%Y-%m-%d'})
            date_fmt = format_spec.get('pattern')
            if date_fmt:
                return pd.to_datetime(series, format=date_fmt, errors='coerce')

        # No format specified, auto-detect
        return pd.to_datetime(series, errors='coerce')

    def convert_numeric(self, series: pd.Series, format_spec: Optional[Dict],
                       downcast: str) -> pd.Series:
        """
        Convert series to numeric, handling formatting.

        Args:
            series: Series to convert
            format_spec: Format dict with 'thousands' and 'decimal' keys
            downcast: 'integer' or 'float'

        Returns:
            Series with numeric values
        """
        if format_spec:
            # Clean numeric strings before conversion
            series = series.apply(lambda x: self._clean_numeric_string(x, format_spec))
            logger.debug(f"Cleaned numeric strings with format {format_spec}")

        return pd.to_numeric(series, errors='coerce', downcast=downcast)

    def _clean_numeric_string(self, value: Any, format_spec: Dict) -> Any:
        """
        Clean numeric string based on format specification.

        Args:
            value: Value to clean
            format_spec: Dictionary with 'thousands' and 'decimal' keys

        Returns:
            Cleaned string ready for pd.to_numeric conversion
        """
        if pd.isna(value):
            return value

        value_str = str(value).strip()
        if not value_str:
            return value

        # Get format specification
        thousands = format_spec.get('thousands', '')
        decimal = format_spec.get('decimal', '.')

        # Remove thousands separator
        if thousands:
            value_str = value_str.replace(thousands, '')

        # Replace decimal separator with period
        if decimal != '.':
            value_str = value_str.replace(decimal, '.')

        return value_str
