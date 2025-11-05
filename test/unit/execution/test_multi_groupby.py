"""
Test script for multi-column group_by functionality.

This script tests that group_by can accept both:
1. Single column: 'in_product_id'
2. Multiple columns: ['in_product_id', 'in_dt']
"""

import pandas as pd
import numpy as np
from src.utils.logger import setup_logging
from src.core.context import GabedaContext
from src.preprocessing.loaders import DataLoader
from src.preprocessing.schema import SchemaProcessor
from src.features.store import FeatureStore
from src.features.resolver import DependencyResolver
from src.execution.executor import ModelExecutor

# Setup logging
base_cfg = {
    'client': 'test_multi_groupby',
    'log_level': 'INFO'
}
setup_logging(log_level='INFO', config=base_cfg)

# Create sample data
data = {
    'trans_id': [1, 2, 3, 4, 5, 6],
    'fecha': ['2025-01-15', '2025-01-15', '2025-01-15', '2025-01-16', '2025-01-16', '2025-01-16'],
    'producto': ['A', 'A', 'B', 'A', 'B', 'B'],
    'cantidad': [10, 15, 20, 12, 18, 25],
    'total': [100, 150, 200, 120, 180, 250]
}
df = pd.DataFrame(data)
df['fecha'] = pd.to_datetime(df['fecha'])

# Initialize context and components
context = GabedaContext(base_cfg)
loader = DataLoader()
schema_processor = SchemaProcessor()
feature_store = FeatureStore()
resolver = DependencyResolver(feature_store)

# Initialize execution components (needed for executor)
from src.features.detector import FeatureTypeDetector
from src.features.analyzer import FeatureAnalyzer
from src.execution.calculator import FeatureCalculator
from src.execution.groupby import GroupByProcessor

detector = FeatureTypeDetector()
analyzer = FeatureAnalyzer(feature_store, detector)
calculator = FeatureCalculator()
groupby_processor = GroupByProcessor(calculator, detector)
executor = ModelExecutor(analyzer, groupby_processor, context)

# Schema mapping
schema_map = {
    'trans_id': 'in_trans_id',
    'fecha': 'in_dt',
    'producto': 'in_product_id',
    'cantidad': 'in_quantity',
    'total': 'in_price_total'
}

# Load and process data
context.set_dataset('transactions_raw', df)
result = schema_processor.process_schema(df, {'data_schema': {
    'in_trans_id': {'source_column': 'trans_id', 'dtype': 'str'},
    'in_dt': {'source_column': 'fecha', 'dtype': 'date'},
    'in_product_id': {'source_column': 'producto', 'dtype': 'str'},
    'in_quantity': {'source_column': 'cantidad', 'dtype': 'float'},
    'in_price_total': {'source_column': 'total', 'dtype': 'float'}
}})
data_standardized = result.df
context.set_dataset('transactions_enriched', data_standardized)

# Define features
def quantity(in_quantity: float) -> float:
    return in_quantity

def quantity_sum(quantity: float) -> float:
    return np.sum(quantity)

def price_total_sum(in_price_total: float) -> float:
    return np.sum(in_price_total)

def avg_price(quantity_sum: float, price_total_sum: float) -> float:
    return price_total_sum / quantity_sum if quantity_sum > 0 else 0

# Store features
features = {
    'quantity': quantity,
    'quantity_sum': quantity_sum,
    'price_total_sum': price_total_sum,
    'avg_price': avg_price
}
feature_store.store_features(features)

# TEST 1: Single column group_by
print("\n" + "="*80)
print("TEST 1: Single column group_by = 'in_product_id'")
print("="*80)

cfg_product_single = {
    'model_name': 'product_single',
    'group_by': 'in_product_id',
    'row_id': 'in_trans_id',
    'output_cols': ['quantity', 'quantity_sum', 'price_total_sum', 'avg_price'],
    'features': features
}

# Resolve dependencies
in_cols, exec_seq, ext_cols = resolver.resolve_dependencies(
    output_cols=cfg_product_single['output_cols'],
    available_cols=data_standardized.columns.tolist(),
    group_by=[cfg_product_single['group_by']],
    model='product_single'
)
cfg_product_single['in_cols'] = in_cols
cfg_product_single['exec_seq'] = exec_seq
cfg_product_single['ext_cols'] = ext_cols

# Execute model
output_single = executor.execute_model(
    cfg_model=cfg_product_single,
    input_dataset_name='transactions_enriched'
)
context.set_model_output('product_single', output_single)
attrs_single = context.get_model_attrs('product_single')
filters_single = context.get_model_filters('product_single')

print("\nAttributes DataFrame (single group_by):")
print(attrs_single)
print(f"\nColumns: {list(attrs_single.columns)}")
print(f"[OK] Should have 'in_product_id' column: {'in_product_id' in attrs_single.columns}")

print("\nFilters DataFrame (single group_by):")
print(filters_single.head())
print(f"\nColumns: {list(filters_single.columns)}")
print(f"[OK] Should have 'in_product_id' column: {'in_product_id' in filters_single.columns}")

# TEST 2: Multi-column group_by
print("\n" + "="*80)
print("TEST 2: Multi-column group_by = ['in_product_id', 'in_dt']")
print("="*80)

cfg_product_multi = {
    'model_name': 'product_multi',
    'group_by': ['in_product_id', 'in_dt'],
    'row_id': 'in_trans_id',
    'output_cols': ['quantity', 'quantity_sum', 'price_total_sum', 'avg_price'],
    'features': features
}

# Resolve dependencies
in_cols, exec_seq, ext_cols = resolver.resolve_dependencies(
    output_cols=cfg_product_multi['output_cols'],
    available_cols=data_standardized.columns.tolist(),
    group_by=cfg_product_multi['group_by'],  # Already a list
    model='product_multi'
)
cfg_product_multi['in_cols'] = in_cols
cfg_product_multi['exec_seq'] = exec_seq
cfg_product_multi['ext_cols'] = ext_cols

# Execute model
output_multi = executor.execute_model(
    cfg_model=cfg_product_multi,
    input_dataset_name='transactions_enriched'
)
context.set_model_output('product_multi', output_multi)
attrs_multi = context.get_model_attrs('product_multi')
filters_multi = context.get_model_filters('product_multi')

print("\nAttributes DataFrame (multi group_by):")
print(attrs_multi)
print(f"\nColumns: {list(attrs_multi.columns)}")
print(f"[OK] Should have 'in_product_id' column: {'in_product_id' in attrs_multi.columns}")
print(f"[OK] Should have 'in_dt' column: {'in_dt' in attrs_multi.columns}")

print("\nFilters DataFrame (multi group_by):")
print(filters_multi.head())
print(f"\nColumns: {list(filters_multi.columns)}")
print(f"[OK] Should have 'in_product_id' column: {'in_product_id' in filters_multi.columns}")
print(f"[OK] Should have 'in_dt' column: {'in_dt' in filters_multi.columns}")

# Validation
print("\n" + "="*80)
print("VALIDATION SUMMARY")
print("="*80)

validation_passed = True

# Check single group_by
if 'in_product_id' not in attrs_single.columns:
    print("[X] FAILED: attrs_single missing 'in_product_id' column")
    validation_passed = False
else:
    print("[OK] PASSED: attrs_single has 'in_product_id' column")

if 'in_product_id' not in filters_single.columns:
    print("[X] FAILED: filters_single missing 'in_product_id' column")
    validation_passed = False
else:
    print("[OK] PASSED: filters_single has 'in_product_id' column")

# Check multi group_by
if 'in_product_id' not in attrs_multi.columns:
    print("[X] FAILED: attrs_multi missing 'in_product_id' column")
    validation_passed = False
else:
    print("[OK] PASSED: attrs_multi has 'in_product_id' column")

if 'in_dt' not in attrs_multi.columns:
    print("[X] FAILED: attrs_multi missing 'in_dt' column")
    validation_passed = False
else:
    print("[OK] PASSED: attrs_multi has 'in_dt' column")

if 'in_product_id' not in filters_multi.columns:
    print("[X] FAILED: filters_multi missing 'in_product_id' column")
    validation_passed = False
else:
    print("[OK] PASSED: filters_multi has 'in_product_id' column")

if 'in_dt' not in filters_multi.columns:
    print("[X] FAILED: filters_multi missing 'in_dt' column")
    validation_passed = False
else:
    print("[OK] PASSED: filters_multi has 'in_dt' column")

# Check row counts
expected_single_attrs = 2  # 2 products
expected_multi_attrs = 4  # 2 products x 2 dates
if len(attrs_single) != expected_single_attrs:
    print(f"[X] FAILED: attrs_single has {len(attrs_single)} rows, expected {expected_single_attrs}")
    validation_passed = False
else:
    print(f"[OK] PASSED: attrs_single has {expected_single_attrs} rows")

if len(attrs_multi) != expected_multi_attrs:
    print(f"[X] FAILED: attrs_multi has {len(attrs_multi)} rows, expected {expected_multi_attrs}")
    validation_passed = False
else:
    print(f"[OK] PASSED: attrs_multi has {expected_multi_attrs} rows")

print("\n" + "="*80)
if validation_passed:
    print("ALL TESTS PASSED [OK]")
else:
    print("SOME TESTS FAILED [X]")
print("="*80)
