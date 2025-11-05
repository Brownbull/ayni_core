"""
Excel export module for GabeDA.

Single Responsibility: Export data to Excel files ONLY
- Export single model to Excel
- Export multiple models to Excel
- Retrieve data from context
- Does NOT format data (formatter does this)
"""

import pandas as pd
import os
from typing import Optional, List, Set
from src.core.context import GabedaContext
from src.export.formatters import ExcelFormatter
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExcelExporter:
    """
    Exports data to Excel files.

    Responsibilities:
    - Export single model results to Excel
    - Export all models to single Excel file
    - Retrieve data from context
    - Coordinate with formatter for post-processing

    Does NOT:
    - Format Excel (ExcelFormatter does this)
    - Execute models or process data
    """

    def __init__(self, context: GabedaContext, formatter: Optional[ExcelFormatter] = None):
        """
        Initialize exporter.

        Args:
            context: GabedaContext with model results
            formatter: Optional ExcelFormatter (creates default if None)
        """
        self.context = context
        self.formatter = formatter or ExcelFormatter()

    def export_model(
        self,
        model_name: str,
        output_path: str,
        include_input: bool = True
    ) -> str:
        """
        Export single model to Excel with separate tabs.

        Creates tabs for:
        - Input dataset (if include_input=True)
        - Model filters
        - Model attributes

        Args:
            model_name: Name of model to export
            output_path: Path for output Excel file
            include_input: Include input dataset tab (default: True)

        Returns:
            Path to created Excel file

        Example:
            exporter = ExcelExporter(ctx)
            exporter.export_model('product_stats', 'outputs/product_analysis.xlsx')
        """
        logger.info(f"Exporting model '{model_name}' to {output_path}")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Create Excel writer
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:

            # Export input dataset
            if include_input:
                self._export_model_input(writer, model_name)

            # Export filters
            self._export_model_filters(writer, model_name)

            # Export attributes
            self._export_model_attrs(writer, model_name)

        # Apply formatting
        self.formatter.format_workbook(output_path)

        logger.info(f"✓ Excel file saved: {output_path}")
        return output_path

    def export_all_models(
        self,
        output_path: str,
        include_unique_inputs: bool = True
    ) -> Optional[str]:
        """
        Export all models to single Excel file.

        Creates tabs for:
        - Unique input datasets (if include_unique_inputs=True)
        - Each model's filters
        - Each model's attributes

        Args:
            output_path: Path for output Excel file
            include_unique_inputs: Include unique input datasets (default: True)

        Returns:
            Path to created Excel file, or None if no models found

        Example:
            exporter = ExcelExporter(ctx)
            exporter.export_all_models('outputs/all_models.xlsx')
        """
        logger.info(f"Exporting all models to {output_path}")

        # Get all models
        model_names = self.context.list_models()

        if not model_names:
            logger.warning("No models found in context")
            return None

        logger.info(f"Found {len(model_names)} models to export: {model_names}")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Create Excel writer
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:

            # Export unique input datasets
            if include_unique_inputs:
                self._export_unique_inputs(writer, model_names)

            # Export each model
            for model_name in model_names:
                logger.info(f"Exporting model: {model_name}")
                self._export_model_filters(writer, model_name)
                self._export_model_attrs(writer, model_name)

        # Apply formatting
        self.formatter.format_workbook(output_path)

        logger.info(f"✓ Excel file saved: {output_path}")
        return output_path

    def _export_model_input(
        self,
        writer: pd.ExcelWriter,
        model_name: str
    ) -> None:
        """
        Export model input dataset to Excel writer.

        Args:
            writer: pandas ExcelWriter
            model_name: Model name
        """
        try:
            input_df = self.context.get_model_input(model_name)
            if input_df is not None:
                # Get input dataset name for better labeling
                model_info = self.context.models.get(model_name, {})
                input_dataset_name = model_info.get('input_dataset_name', 'input')

                # Truncate to Excel's 31 character sheet name limit
                sheet_name = input_dataset_name[:31]
                input_df.to_excel(writer, sheet_name=sheet_name, index=False)

                logger.info(
                    f"✓ Exported '{sheet_name}' tab (input): "
                    f"{input_df.shape[0]} rows × {input_df.shape[1]} cols"
                )
            else:
                logger.warning(f"No input dataset found for model '{model_name}'")
        except Exception as e:
            logger.error(f"Could not export input for '{model_name}': {e}")

    def _export_model_filters(
        self,
        writer: pd.ExcelWriter,
        model_name: str
    ) -> None:
        """
        Export model filters to Excel writer.

        Args:
            writer: pandas ExcelWriter
            model_name: Model name
        """
        try:
            filters_df = self.context.get_model_filters(model_name)
            if filters_df is not None and not filters_df.empty:
                sheet_name = f'{model_name}_filters'[:31]  # Excel limit
                filters_df.to_excel(writer, sheet_name=sheet_name, index=False)

                logger.info(
                    f"✓ Exported '{sheet_name}' tab: "
                    f"{filters_df.shape[0]} rows × {filters_df.shape[1]} cols"
                )
            else:
                logger.warning(f"Filters for '{model_name}' are empty or None")
        except KeyError:
            logger.warning(f"Filters for '{model_name}' not found in context")

    def _export_model_attrs(
        self,
        writer: pd.ExcelWriter,
        model_name: str
    ) -> None:
        """
        Export model attributes to Excel writer.

        Args:
            writer: pandas ExcelWriter
            model_name: Model name
        """
        try:
            attrs_df = self.context.get_model_attrs(model_name)
            if attrs_df is not None and not attrs_df.empty:
                sheet_name = f'{model_name}_attrs'[:31]  # Excel limit
                attrs_df.to_excel(writer, sheet_name=sheet_name, index=False)

                logger.info(
                    f"✓ Exported '{sheet_name}' tab: "
                    f"{attrs_df.shape[0]} rows × {attrs_df.shape[1]} cols"
                )
            else:
                logger.warning(f"Attributes for '{model_name}' are empty or None")
        except KeyError:
            logger.warning(f"Attributes for '{model_name}' not found in context")

    def _export_unique_inputs(
        self,
        writer: pd.ExcelWriter,
        model_names: List[str]
    ) -> None:
        """
        Export unique input datasets used across all models.

        Args:
            writer: pandas ExcelWriter
            model_names: List of model names
        """
        exported_inputs: Set[str] = set()

        for model_name in model_names:
            try:
                model_info = self.context.models.get(model_name, {})
                input_dataset_name = model_info.get('input_dataset_name')

                if input_dataset_name and input_dataset_name not in exported_inputs:
                    input_df = self.context.get_dataset(input_dataset_name)
                    if input_df is not None:
                        sheet_name = input_dataset_name[:31]  # Excel limit
                        input_df.to_excel(writer, sheet_name=sheet_name, index=False)

                        logger.info(
                            f"✓ Exported '{sheet_name}' tab (input): "
                            f"{input_df.shape[0]} rows × {input_df.shape[1]} cols"
                        )
                        exported_inputs.add(input_dataset_name)
            except Exception as e:
                logger.error(f"Could not export input for '{model_name}': {e}")
