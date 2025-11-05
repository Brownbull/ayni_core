"""
Execution orchestration module for GabeDA.

Single Responsibility: Orchestrate high-level execution flow ONLY
- Coordinates multiple model executions
- Manages execution order and dependencies
- Does NOT execute individual models (executor does this)
- Does NOT store results (context does this)
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from src.execution.executor import ModelExecutor
from src.core.context import GabedaContext
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExecutionOrchestrator:
    """
    Orchestrates high-level execution flow.

    Responsibilities:
    - Coordinate execution of multiple models
    - Manage execution order (if dependencies exist)
    - Retrieve inputs from context
    - Store outputs to context

    Does NOT:
    - Execute individual models (ModelExecutor does this)
    - Process groups or calculate features (execution package does this)
    - Preprocess data (preprocessing package does this)
    """

    def __init__(
        self,
        executor: ModelExecutor,
        context: GabedaContext
    ):
        self.executor = executor
        self.context = context

    def execute_single_model(
        self,
        model_name: str,
        cfg_model: Dict[str, Any],
        input_dataset_name: str
    ) -> Dict[str, Any]:
        """
        Execute a single model and store results in context.

        Args:
            model_name: Model name (will be added to cfg_model if not present)
            cfg_model: Model configuration
            input_dataset_name: Name of input dataset in context

        Returns:
            Model output dict

        Raises:
            ValueError: If input dataset not found in context
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Orchestrating Model: {model_name}")
        logger.info(f"{'='*60}")

        # Ensure model_name is in cfg_model
        if 'model_name' not in cfg_model:
            cfg_model['model_name'] = model_name

        # Execute model (executor will retrieve data from context)
        output = self.executor.execute_model(
            cfg_model=cfg_model,
            input_dataset_name=input_dataset_name
        )

        # Store output in context
        self.context.set_model_output(model_name, output)
        logger.info(f"Stored model output for '{model_name}' in context")

        return output

    def execute_pipeline(
        self,
        models: List[Dict[str, Any]],
        initial_dataset_name: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Execute a pipeline of models in sequence.

        Each model in the pipeline can use:
        - The initial preprocessed dataset
        - Outputs from previously executed models

        Args:
            models: List of model configs, each with:
                - 'name': Model name
                - 'config': Model configuration
                - 'input_dataset': Name of input dataset in context
            initial_dataset_name: Name of initial preprocessed dataset

        Returns:
            Dict mapping model_name -> output

        Example:
            models = [
                {
                    'name': 'product_stats',
                    'config': {...},
                    'input_dataset': 'preprocessed'
                },
                {
                    'name': 'customer_analysis',
                    'config': {...},
                    'input_dataset': 'product_stats_filters'  # Uses previous model output
                }
            ]
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Executing Pipeline: {len(models)} models")
        logger.info(f"Initial dataset: {initial_dataset_name}")
        logger.info(f"{'='*60}\n")

        results = {}

        for i, model_spec in enumerate(models, 1):
            model_name = model_spec['name']
            cfg_model = model_spec['config']
            input_dataset_name = model_spec.get('input_dataset', initial_dataset_name)

            logger.info(f"\n--- Pipeline Step {i}/{len(models)}: {model_name} ---")
            logger.info(f"Executing model: {model_name}")
            logger.info(f"  - Input dataset: {input_dataset_name}")
            logger.info(f"  - Features to execute: {len(cfg_model.get('exec_seq', []))}")

            # Execute model
            output = self.execute_single_model(
                model_name=model_name,
                cfg_model=cfg_model,
                input_dataset_name=input_dataset_name
            )

            results[model_name] = output

        logger.info(f"\n{'='*60}")
        logger.info(f"Pipeline Complete: {len(results)} models executed")
        logger.info(f"{'='*60}\n")

        return results

    def get_model_output(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve model output from context.

        Args:
            model_name: Model name

        Returns:
            Model output dict or None if not found
        """
        # Context stores outputs internally, so we access via get_model_filters/attrs
        filters = self.context.get_model_filters(model_name)
        attrs = self.context.get_model_attrs(model_name)
        input_name = self.context.get_model_input(model_name)

        if filters is None and attrs is None:
            return None

        return {
            'filters': filters,
            'attrs': attrs,
            'input_dataset_name': input_name
        }

    def list_available_datasets(self) -> List[str]:
        """
        List all datasets available in context.

        Returns:
            List of dataset names
        """
        return list(self.context.datasets.keys())

    def list_executed_models(self) -> List[str]:
        """
        List all models that have been executed.

        Returns:
            List of model names
        """
        return list(self.context.models.keys())
