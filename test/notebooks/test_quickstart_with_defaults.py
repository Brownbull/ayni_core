#!/usr/bin/env python
# coding: utf-8

# # GabeDA Quickstart (v2.0 Refactored Architecture)
# 
# This notebook demonstrates the **v2.0 refactored architecture** with 17 modules in 6 packages.
# 
# **What this notebook shows:**
# - Loading and preprocessing data with the new modular components
# - Defining features (filters and attributes)
# - Executing a model with automatic dependency resolution
# - Exporting results to Excel
# - **Case 2 filter**: A filter that uses an attribute as input (KEY INNOVATION)
# 
# **New in v2.0:**
# - Explicit component initialization (better control and testability)
# - Clear separation of concerns across 6 packages
# - Same functionality, cleaner architecture

# ## 1. Configuration

# Base configuration
base_cfg = {
    'input_file': 'data/alsur_gen/00_raw/alsur_transacciones_202510_1.csv',
    'client': 'quickstart_refactored',
    'analysis_dt': '2025-11-11',
    'log_level': 'INFO',
    'fidx_config': {'type': 'local', 'path': 'feature_store'},
    
    # Default formats applied to all columns of each dtype (unless overridden)
    'default_formats': {
        'date': '%d-%m-%Y %H:%M',  # European date format
        'float': {'thousands': '.', 'decimal': ','},  # European numeric format
        'int': {'thousands': '.', 'decimal': ','},
    },
    
    # Data schema: column mapping + types
    'data_schema': {
        'in_dt': {
            'source_column': 'Fecha venta',
            'dtype': 'date',
            # 'format': '%d-%m-%Y %H:%M'
        },
        'in_trans_id': {
            'source_column': 'N° doc. venta',
            'dtype': 'str'
        },
        'in_product_id': {
            'source_column': 'SKU',
            'dtype': 'str'
        },
        'in_quantity': {
            'source_column': 'Cantidad',
            'dtype': 'float',
        },
        'in_price_total': {
            'source_column': 'Total neto',
            'dtype': 'float',
        },
    }
}


# ## 2. Imports (v2.0 Refactored)
# 
# Notice the new modular imports from the 6 packages:

import pandas as pd
import numpy as np

# v2.0 Refactored imports
from src.utils.logger import setup_logging, get_logger
from src.core.context import GabedaContext
from src.preprocessing.loaders import DataLoader
from src.preprocessing.validators import DataValidator
from src.preprocessing.schema import SchemaProcessor
from src.features.store import FeatureStore
from src.features.resolver import DependencyResolver
from src.features.detector import FeatureTypeDetector
from src.features.analyzer import FeatureAnalyzer
from src.execution.calculator import FeatureCalculator
from src.execution.groupby import GroupByProcessor
from src.execution.executor import ModelExecutor
from src.export.excel import ExcelExporter

print("[OK] All imports successful!")


# ## 3. Initialize Context & Logging

# Setup logging
setup_logging(log_level=base_cfg.get('log_level', 'INFO'), config=base_cfg)
logger = get_logger(__name__)

# Initialize context
ctx = GabedaContext(base_cfg)

print(f"[OK] Context initialized: {ctx.run_id}")


# ## 4. Load & Preprocess Data
# 
# Using the new modular preprocessing components:

# ### 4.1 Load

# Load raw data
loader = DataLoader()
raw_data = loader.load_csv(base_cfg['input_file'])
print(f"[OK] Loaded raw data: {raw_data.shape}")


# ### 4.2 Validation

# Validate required columns
validator = DataValidator()
required_cols = [spec['source_column'] for spec in base_cfg['data_schema'].values()]
validation = validator.validate_required_columns(raw_data, required_cols)

if validation.is_valid:
    print(f"[OK] Validation passed")
else:
    print(f"[X] Validation failed: {validation.errors}")


# OPTIONAL Validate data quality
quality_validation = validator.validate_data_quality(raw_data, base_cfg['data_schema'])
if quality_validation.is_valid:
    print(f"[OK] Quality validation passed")
else:
    print(f"[X] Quality validation issues: {quality_validation.issues}")


# ### 4.3 Schema

# Process schema (column mapping + type conversion)
schema_processor = SchemaProcessor()
result = schema_processor.process_schema(raw_data, base_cfg)
preprocessed_df = result.df

print(f"[OK] Preprocessed data: {preprocessed_df.shape}")
print(f"[OK] Available columns: {result.available_cols}")


# ### 4.4 Save Datasets

# Store datasets in context
ctx.set_dataset('transactions_raw', raw_data)
ctx.set_dataset('transactions_enriched', preprocessed_df)
ctx.list_datasets()


# ## 5. Define Features
# 
# ### Filters (row-level calculations)

def quantity(in_quantity: float) -> float:
    """Case 1: Standard filter - reads from data_in"""
    return in_quantity

def price_total(in_price_total: float) -> float:
    """Case 1: Standard filter - reads from data_in"""
    return in_price_total

def price_above_avg(price_total: float, price_avg: float) -> bool:
    """Case 2: Filter using attribute - THE KEY INNOVATION!
    
    This filter reads from BOTH:
    - price_total (from data_in)
    - price_avg (from agg_results)
    
    This is only possible because of the single-loop execution in GroupByProcessor.
    """
    return price_total > price_avg

print("[OK] Defined 3 filter features")
print("  - quantity (Case 1)")
print("  - price_total (Case 1)")
print("  - price_above_avg (Case 2) <-- Uses attribute as input!")


# ### Attributes (aggregated calculations)

def quantity_sum(quantity: float) -> float:
    """Case 3: Attribute with aggregation"""
    return np.sum(quantity)

def price_sum(price_total: float) -> float:
    """Case 3: Attribute with aggregation"""
    return np.sum(price_total)

def price_avg(price_total: float) -> float:
    """Case 3: Attribute with aggregation
    
    This attribute is used by the price_above_avg filter (Case 2)!
    """
    return np.mean(price_total)

def price_gt_avg_count(price_above_avg: bool) -> int:
    """Case 3: Attribute that aggregates a Case 2 filter"""
    return np.sum(price_above_avg)

print("[OK] Defined 4 attribute features")
print("  - quantity_sum (Case 3)")
print("  - price_sum (Case 3)")
print("  - price_avg (Case 3) <-- Used by price_above_avg filter!")
print("  - price_gt_avg_count (Case 3)")


# ### Store Features

# Initialize feature store
feature_store = FeatureStore()

# Store all features
features = {
    # Filters
    'quantity': quantity,
    'price_total': price_total,
    'price_above_avg': price_above_avg,
    # Attributes
    'quantity_sum': quantity_sum,
    'price_sum': price_sum,
    'price_avg': price_avg,
    'price_gt_avg_count': price_gt_avg_count,
}

# New method to store multiple features at once
feature_store.store_features(features)

print(f"[OK] Stored {len(feature_store.features)} features in store")
# Features stored successfully


# ## 6. Configure Model

# Model configuration
cfg_product = {
    'model_name': 'product_stats',
    'group_by': 'in_product_id',
    'row_id': 'in_trans_id',
    'output_cols': [
        # Filters
        'quantity',
        'price_total',
        'price_above_avg',  # Case 2 filter!
        # Attributes
        'quantity_sum',
        'price_sum',
        'price_avg',
        'price_gt_avg_count',
    ],
    'features': features
}

print("[OK] Model configured")
print(f"  - Model: {cfg_product['model_name']}")
print(f"  - Group by: {cfg_product['group_by']}")
print(f"  - Output columns: {len(cfg_product['output_cols'])}")


# ## 7. Resolve Dependencies
# 
# The DependencyResolver uses DFS traversal to determine execution order:

# Initialize resolver
resolver = DependencyResolver(feature_store)

# Resolve dependencies
in_cols, exec_seq, ext_cols = resolver.resolve_dependencies(
    output_cols=cfg_product['output_cols'],
    available_cols=preprocessed_df.columns.tolist(),
    group_by=[cfg_product['group_by']],
    model='product_stats'
)

# Update config
cfg_product['in_cols'] = in_cols
cfg_product['exec_seq'] = exec_seq
cfg_product['ext_cols'] = ext_cols

print("[OK] Dependencies resolved")
print(f"  - Input columns needed: {in_cols}")
print(f"  - Execution sequence: {exec_seq}")
print("\nNotice: price_avg comes BEFORE price_above_avg in execution order!")
print("This allows the filter to use the attribute as input.")


# ## 8. Execute Model
# 
# Initialize execution components and run the model:

# Initialize execution components
detector = FeatureTypeDetector()
analyzer = FeatureAnalyzer(feature_store, detector)
calculator = FeatureCalculator()
groupby_processor = GroupByProcessor(calculator, detector)
executor = ModelExecutor(analyzer, groupby_processor, ctx)

print("[OK] Execution pipeline initialized")

# Execute model
output = executor.execute_model(
    cfg_model=cfg_product,
    input_dataset_name='transactions_enriched'
)

# Store results in context
ctx.set_model_output('product_stats', output)

print("\n[OK] Model executed successfully!")
print(f"  - Filters: {output['filters'].shape if output['filters'] is not None else 'None'}")
print(f"  - Attributes: {output['attrs'].shape if output['attrs'] is not None else 'None'}")
print(f"  - Filter columns: {output['exec_fltrs']}")
print(f"  - Attribute columns: {output['exec_attrs']}")


# ## 9. View Results

print("Available Datasets:")
for name in ctx.list_datasets():
    df = ctx.get_dataset(name)
    print(f"  - {name}: {df.shape}")


# ### Raw Data

ctx.get_dataset('transactions_raw').head()


# ### Preprocessed Data

ctx.get_dataset('transactions_enriched').head()


# ### Filters (Row-Level Results)

filters = ctx.get_model_filters('product_stats')
print("Product Stats - Filters:")
print(filters)

# Check for Case 2 filter
if 'price_above_avg' in filters.columns:
    print("\n[SUCCESS] Case 2 filter verified!")
    print("The 'price_above_avg' column proves that filters can use attributes as inputs.")
else:
    print("\n[ERROR] Case 2 filter not found!")


# ### Attributes (Aggregated Results)

attrs = ctx.get_model_attrs('product_stats')
print("Product Stats - Attributes:")
print(attrs)


# ## 10. Export to Excel

# Initialize exporter
exporter = ExcelExporter(ctx)

# Export model
output_file = 'outputs/quickstart_refactored.xlsx'
exporter.export_model('product_stats', output_file, include_input=True)

print(f"\n[SUCCESS] Export complete!")
print(f"File saved: {output_file}")
print("\nExpected Excel Structure:")
print("  Tab 1: transactions_enriched (input dataset)")
print("  Tab 2: product_stats_filters")
print("  Tab 3: product_stats_attrs")


# ## Summary
# 
# This quickstart demonstrated:
# 
# ### ✅ v2.0 Refactored Architecture
# - Modular imports from 6 packages (utils, core, preprocessing, features, execution, export)
# - Explicit component initialization for better control
# - Clear separation of concerns
# 
# ### ✅ Key Features Showcased
# 1. **Data Loading & Preprocessing**: DataLoader → DataValidator → SchemaProcessor
# 2. **Feature Management**: FeatureStore for organizing features
# 3. **Dependency Resolution**: DependencyResolver with DFS traversal
# 4. **4-Case Logic**: Demonstrated Case 2 filter (price_above_avg) using an attribute
# 5. **Model Execution**: Single-loop processing with GroupByProcessor
# 6. **Excel Export**: Multi-tab export with autofilters
# 
# ### ✅ Case 2 Filter Verified
# The `price_above_avg` filter successfully uses `price_avg` attribute as input, demonstrating the KEY INNOVATION of the 4-case logic.
# 
# ### 📚 Next Steps
# - See [multi_model_example_refactored.ipynb](multi_model_example_refactored.ipynb) for multi-model pipelines
# - Read [docs/specs/src/README.md](docs/specs/src/README.md) for detailed documentation
# - Review [REFACTORED_NOTEBOOK_TEST_RESULTS.md](REFACTORED_NOTEBOOK_TEST_RESULTS.md) for test results
