"""
Data loading module for GabeDA preprocessing.

Single Responsibility: Load data from various sources ONLY
- Supports CSV, Excel, and DataFrame inputs
- Does NOT validate, transform, or process data
"""

import pandas as pd
from typing import Union
from pathlib import Path
from src.utils.logger import get_logger
from src.utils import log_file_operation, log_data_shape

logger = get_logger(__name__)


class DataLoader:
    """
    Loads data from various sources.

    Responsibilities:
    - Load CSV files
    - Load Excel files
    - Accept DataFrame input

    Does NOT:
    - Validate data (use DataValidator)
    - Transform data (use transformers)
    - Process schema (use SchemaProcessor)
    """

    def load_from_source(self, source: Union[str, Path, pd.DataFrame]) -> pd.DataFrame:
        """
        Load data from any supported source.

        Args:
            source: File path (CSV/Excel) or DataFrame

        Returns:
            Raw DataFrame

        Raises:
            ValueError: If source type not supported
            FileNotFoundError: If file doesn't exist
        """
        if isinstance(source, pd.DataFrame):
            return self.load_dataframe(source)

        source_path = Path(source)
        if not source_path.exists():
            raise FileNotFoundError(f"Data source not found: {source}")

        if source_path.suffix == '.csv':
            return self.load_csv(source_path)
        elif source_path.suffix in ['.xlsx', '.xls']:
            return self.load_excel(source_path)
        else:
            raise ValueError(f"Unsupported file type: {source_path.suffix}")

    def load_csv(self, path: Union[str, Path]) -> pd.DataFrame:
        """
        Load CSV file.

        Args:
            path: Path to CSV file

        Returns:
            DataFrame with CSV data
        """
        logger.info(f"Loading CSV from: {path}")
        df = pd.read_csv(path)
        log_data_shape(logger, str(path), df, action='Loaded')
        return df

    def load_excel(self, path: Union[str, Path]) -> pd.DataFrame:
        """
        Load Excel file.

        Args:
            path: Path to Excel file (.xlsx or .xls)

        Returns:
            DataFrame with Excel data
        """
        logger.info(f"Loading Excel from: {path}")
        df = pd.read_excel(path)
        log_data_shape(logger, str(path), df, action='Loaded')
        return df

    def load_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Accept DataFrame input.

        Args:
            df: DataFrame to use

        Returns:
            Copy of DataFrame
        """
        log_data_shape(logger, 'provided DataFrame', df, action='Using')
        return df.copy()
