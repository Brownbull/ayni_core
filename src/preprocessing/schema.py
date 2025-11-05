"""
Schema processing module for GabeDA preprocessing.

Single Responsibility: Schema processing and coordination ONLY
- Coordinates schema processing
- Supports new and legacy schema formats
- Combines mapping and type conversion
- Does NOT load, validate, or actually transform data (delegates to other classes)
"""

import pandas as pd
from typing import Dict, List
from dataclasses import dataclass
from src.preprocessing.transformers import ColumnMapper, TypeConverter
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ProcessedSchema:
    """
    Result of schema processing.

    Attributes:
        df: Processed DataFrame with mapped columns and converted types
        available_cols: List of columns successfully mapped
        missing_cols: List of columns not found in source data
        config: Original configuration dictionary
    """
    df: pd.DataFrame
    available_cols: List[str]
    missing_cols: List[str]
    config: Dict


class SchemaProcessor:
    """
    Processes data schemas (new format or legacy).

    Responsibilities:
    - Coordinate schema processing
    - Support new and legacy schema formats
    - Combine mapping and type conversion

    Does NOT:
    - Load data (use DataLoader)
    - Validate data (use DataValidator)
    - Actually transform data (delegates to ColumnMapper and TypeConverter)
    """

    def __init__(self):
        self.mapper = ColumnMapper()
        self.converter = TypeConverter()

    def process_schema(self, df: pd.DataFrame, config: Dict) -> ProcessedSchema:
        """
        Process new unified schema format and transform DataFrame.

        Args:
            df: Raw DataFrame
            config: Configuration with 'data_schema' and optional 'default_formats'

        Returns:
            ProcessedSchema with transformed df and metadata
        """
        schema = config['data_schema']
        default_formats = config.get('default_formats')  # Optional

        # Map columns
        df, available_cols, missing_cols = self.mapper.map_columns(df, schema)

        # Convert types (with optional default formats)
        df = self.converter.convert_types(df, schema, default_formats=default_formats)

        logger.info(f"Schema processed: {len(available_cols)} available, {len(missing_cols)} missing")

        # Check date range for any date columns
        self._check_date_ranges(df, schema)

        return ProcessedSchema(
            df=df,
            available_cols=available_cols,
            missing_cols=missing_cols,
            config=config
        )

    def _check_date_ranges(self, df: pd.DataFrame, schema: Dict) -> None:
        """
        Check date ranges for all date columns and warn if data spans more than one month.

        Args:
            df: DataFrame with processed date columns
            schema: Schema specification
        """
        for target_col, col_spec in schema.items():
            if col_spec.get('dtype') == 'date' and target_col in df.columns:
                # Skip if column is all NaT
                if df[target_col].isna().all():
                    continue

                # Get min and max dates
                min_date = df[target_col].min()
                max_date = df[target_col].max()

                # Calculate month span
                if pd.notna(min_date) and pd.notna(max_date):
                    min_month = (min_date.year, min_date.month)
                    max_month = (max_date.year, max_date.month)

                    # Calculate number of months between min and max
                    months_diff = (max_month[0] - min_month[0]) * 12 + (max_month[1] - min_month[1])

                    if months_diff > 0:
                        logger.warning(
                            f"⚠️  Date column '{target_col}' spans {months_diff + 1} months "
                            f"({min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}). "
                            f"Expected data to cover at most 1 month. "
                            f"This may indicate a date format configuration issue."
                        )
                    else:
                        logger.info(
                            f"✓ Date column '{target_col}' spans single month: "
                            f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
                        )
        