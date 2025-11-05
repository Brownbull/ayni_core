"""
Data validation module for GabeDA preprocessing.

Single Responsibility: Data validation ONLY
- Validates required columns exist
- Checks data quality (missing values, duplicates)
- Validates date format compatibility
- Validates required vs optional columns (based on base_case.csv)
- Creates reject files for invalid rows
- Does NOT validate date ranges (removed per constraints)
- Does NOT transform data
"""

import pandas as pd
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from src.utils.logger import get_logger
from src.utils import log_validation_result, log_count_summary
from src.core.constants import COLUMN_SCHEMA

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """
    Result of data validation.

    Attributes:
        is_valid: True if validation passed
        errors: List of error messages (blocking)
        warnings: List of warning messages (non-blocking)
        rejected_rows: DataFrame of rejected rows (if any)
        rejection_reasons: Dict mapping row index to rejection reason
    """
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    rejected_rows: Optional[pd.DataFrame] = None
    rejection_reasons: Dict[int, str] = field(default_factory=dict)


class DataValidator:
    """
    Validates data quality and requirements.

    Responsibilities:
    - Validate required columns exist
    - Check data quality (missing values, duplicates)
    - Validate date format compatibility
    - Validate required vs optional columns
    - Create reject files for invalid rows

    Does NOT:
    - Validate date ranges (removed per constraints)
    - Transform data (use transformers)
    - Load data (use DataLoader)
    """

    def __init__(self, base_case_path: Optional[str] = None):
        """
        Initialize validator with column schema.

        The column schema is now loaded from src.core.constants.COLUMN_SCHEMA
        instead of base_case.csv for better maintainability.

        Args:
            base_case_path: DEPRECATED - Kept for backward compatibility only.
                          Schema is now loaded from constants.COLUMN_SCHEMA.
        """
        self.base_case_path = base_case_path  # Kept for backward compatibility
        self.column_schema = self._load_column_schema()

    def _load_column_schema(self) -> Dict[str, Dict[str, int]]:
        """
        Load column schema from constants.COLUMN_SCHEMA.

        Returns:
            Dict mapping column names to {'optional': 0/1, 'inferable': 0/1}
        """
        # Convert COLUMN_SCHEMA format to legacy format for backward compatibility
        schema = {}
        for col, spec in COLUMN_SCHEMA.items():
            schema[col] = {
                'optional': spec['optional'],
                'inferable': spec['inferable']
            }

        logger.info(f"Loaded column schema from constants.COLUMN_SCHEMA: {len(schema)} columns")
        return schema

    def validate_date_format(
        self,
        df: pd.DataFrame,
        date_column: str,
        expected_format: str,
        source_column: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate that date column can be parsed with the given format.

        This checks a SAMPLE of rows to ensure the format is compatible
        BEFORE attempting full conversion (which would silently create NaT values).

        Args:
            df: DataFrame to validate
            date_column: Target column name (after mapping)
            expected_format: Expected date format string (e.g., '%d/%m/%Y %H:%M')
            source_column: Original column name in df (if different from date_column)

        Returns:
            ValidationResult with errors if format incompatible
        """
        col_to_check = source_column or date_column

        if col_to_check not in df.columns:
            return ValidationResult(
                is_valid=False,
                errors=[f"Date column '{col_to_check}' not found in DataFrame"],
                warnings=[]
            )

        # Sample first 10 non-null rows for format validation
        sample_data = df[col_to_check].dropna().head(10)

        if len(sample_data) == 0:
            warning = f"No data in date column '{col_to_check}' to validate format"
            logger.warning(f"⚠️ {warning}")
            return ValidationResult(is_valid=True, errors=[], warnings=[warning])

        # Try parsing sample with expected format
        errors = []
        for idx, value in sample_data.items():
            try:
                pd.to_datetime(value, format=expected_format, errors='raise')
            except Exception as e:
                error_msg = (
                    f"Date format mismatch in column '{col_to_check}' at row {idx}: "
                    f"value='{value}', expected format='{expected_format}', error: {str(e)}"
                )
                errors.append(error_msg)
                logger.error(f"✗ {error_msg}")

        if errors:
            # Provide helpful suggestion
            sample_value = sample_data.iloc[0]
            suggestion = (
                f"\n  💡 Suggestion: Sample value is '{sample_value}'. "
                f"Try format detection or update config date format."
            )
            logger.error(suggestion)

            return ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=[]
            )

        logger.info(f"✓ Date format validation passed for '{col_to_check}' (format: {expected_format})")
        return ValidationResult(is_valid=True, errors=[], warnings=[])

    def validate_required_columns(self, df: pd.DataFrame, required: List[str]) -> ValidationResult:
        """
        Validate that required columns exist in DataFrame.

        Args:
            df: DataFrame to validate
            required: List of required column names

        Returns:
            ValidationResult with errors if columns missing
        """
        missing = [col for col in required if col not in df.columns]

        if missing:
            error_msg = f"Missing required columns: {missing}"
            logger.error(f"✗ {error_msg}")
            logger.error(f"  Available columns: {list(df.columns)}")
            return ValidationResult(
                is_valid=False,
                errors=[error_msg],
                warnings=[]
            )

        logger.info(f"✓ All required columns present: {required}")
        return ValidationResult(is_valid=True, errors=[], warnings=[])

    def validate_row_level_required_fields(
        self,
        df: pd.DataFrame,
        data_schema: Dict[str, Dict],
        save_to_file: bool = False,
        reject_file_path: Optional[str] = None
    ) -> Tuple[pd.DataFrame, ValidationResult]:
        """
        Validate row-level data based on required/optional columns from constants.COLUMN_SCHEMA.

        Rows with null values in REQUIRED columns (optional=0) are rejected.
        Rows with null values in OPTIONAL columns (optional=1) are kept with warnings.

        Args:
            df: DataFrame to validate
            data_schema: Data schema from config (maps target cols to source cols)
            save_to_file: Whether to save rejected rows to file (default: False)
            reject_file_path: Path to save rejected rows (only used if save_to_file=True)

        Returns:
            Tuple of (clean_df, ValidationResult)
            - clean_df: DataFrame with valid rows only
            - ValidationResult: Contains rejected rows and reasons
                              (rejected_rows can be stored in context)
        """

        rejected_rows = []
        rejection_reasons = {}
        warnings = []

        # Map source columns to target columns for checking
        target_to_source = {
            target: spec['source_column']
            for target, spec in data_schema.items()
            if 'source_column' in spec
        }

        # Check each row
        for idx in df.index:
            row_rejections = []

            for target_col, source_col in target_to_source.items():
                if target_col not in self.column_schema:
                    continue  # Skip columns not in base_case.csv

                schema_info = self.column_schema[target_col]
                is_required = schema_info['optional'] == 0

                # Check if value is null/NaT
                if source_col in df.columns:
                    value = df.loc[idx, source_col]
                    is_null = pd.isna(value)

                    if is_null and is_required:
                        row_rejections.append(
                            f"Required column '{target_col}' (source: '{source_col}') is null"
                        )
                    elif is_null and not is_required:
                        # Optional column with null - log warning but keep row
                        warning = f"Row {idx}: Optional column '{target_col}' is null"
                        if warning not in warnings:
                            warnings.append(warning)

            # If row has any rejections, mark it for rejection
            if row_rejections:
                rejected_rows.append(idx)
                rejection_reasons[idx] = "; ".join(row_rejections)

        # Create rejected and clean dataframes
        if rejected_rows:
            rejected_df = df.loc[rejected_rows].copy()
            rejected_df['rejection_reason'] = rejected_df.index.map(rejection_reasons)
            clean_df = df.drop(rejected_rows).reset_index(drop=True)

            logger.warning(f"⚠️  {len(rejected_rows)} rows rejected due to null required fields")
            logger.info(f"   Clean rows: {len(clean_df)}")

            # Optionally save reject file
            if save_to_file and reject_file_path:
                reject_path = Path(reject_file_path)
                reject_path.parent.mkdir(parents=True, exist_ok=True)

                # Add timestamp to reject file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                reject_file_with_ts = reject_path.parent / f"{reject_path.stem}_{timestamp}{reject_path.suffix}"

                rejected_df.to_csv(reject_file_with_ts, index=False)
                logger.info(f"   📄 Rejected rows saved to: {reject_file_with_ts}")
            else:
                logger.info(f"   💾 Rejected rows available in ValidationResult (not saved to file)")

            return clean_df, ValidationResult(
                is_valid=True,  # True because we handled rejections
                errors=[],
                warnings=warnings,
                rejected_rows=rejected_df,
                rejection_reasons=rejection_reasons
            )
        else:
            logger.info(f"✓ All {len(df)} rows passed required field validation")
            return df, ValidationResult(
                is_valid=True,
                errors=[],
                warnings=warnings
            )

    def validate_data_quality(self, df: pd.DataFrame,
                              check_cols: Optional[List[str]] = None) -> ValidationResult:
        """
        Check data quality metrics.

        Args:
            df: DataFrame to check
            check_cols: Columns to check (default: all)

        Returns:
            ValidationResult with warnings for quality issues
        """
        warnings = []
        cols_to_check = check_cols or df.columns.tolist()

        # Check for missing values
        for col in cols_to_check:
            if col not in df.columns:
                continue

            missing_count = df[col].isna().sum()
            if missing_count > 0:
                missing_pct = (missing_count / len(df)) * 100
                warning_msg = f"Column '{col}' has {missing_count} ({missing_pct:.1f}%) missing values"
                warnings.append(warning_msg)
                logger.warning(f"⚠️ {warning_msg}")

        # Check for duplicate rows
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            duplicate_pct = (duplicate_count / len(df)) * 100
            warning_msg = f"Found {duplicate_count} ({duplicate_pct:.1f}%) duplicate rows"
            warnings.append(warning_msg)
            logger.warning(f"⚠️ {warning_msg}")

        if not warnings:
            logger.info("✓ Data quality check passed (no issues found)")

        return ValidationResult(is_valid=True, errors=[], warnings=warnings)

    def validate_all(
        self,
        df: pd.DataFrame,
        required_cols: List[str],
        data_schema: Optional[Dict] = None,
        default_formats: Optional[Dict] = None,
        quality_check_cols: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Run all validations at once (comprehensive validation).

        This includes:
        1. Date format validation (pre-conversion check)
        2. Required columns validation
        3. Data quality checks

        Args:
            df: DataFrame to validate
            required_cols: Required columns that must exist
            data_schema: Data schema dict from config (for date format validation)
            default_formats: Default formats dict from config
            quality_check_cols: Columns to check quality for (default: all)

        Returns:
            Combined ValidationResult with all errors and warnings
        """
        all_errors = []
        all_warnings = []

        # Step 1: Validate date formats (if schema provided)
        if data_schema and default_formats:
            logger.info("Step 1/3: Validating date formats...")
            for col, spec in data_schema.items():
                if spec.get('dtype') == 'date':
                    fmt = spec.get('format') or default_formats.get('date')
                    if fmt:
                        result = self.validate_date_format(
                            df=df,
                            date_column=col,
                            expected_format=fmt,
                            source_column=spec.get('source_column', col)
                        )
                        if not result.is_valid:
                            all_errors.extend(result.errors)
                        all_warnings.extend(result.warnings)

        # Step 2: Check required columns
        logger.info("Step 2/3: Validating required columns...")
        result1 = self.validate_required_columns(df, required_cols)
        if not result1.is_valid:
            all_errors.extend(result1.errors)
            return ValidationResult(
                is_valid=False,
                errors=all_errors,
                warnings=all_warnings
            )
        all_warnings.extend(result1.warnings)

        # Step 3: Check data quality
        logger.info("Step 3/3: Validating data quality...")
        result2 = self.validate_data_quality(df, quality_check_cols)
        all_warnings.extend(result2.warnings)

        # Return combined result
        is_valid = len(all_errors) == 0

        if is_valid:
            logger.info("✓ All validations passed")
        else:
            logger.error(f"✗ Validation failed with {len(all_errors)} errors")

        return ValidationResult(
            is_valid=is_valid,
            errors=all_errors,
            warnings=all_warnings
        )
