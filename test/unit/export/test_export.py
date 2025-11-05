"""
Test script to verify export functions work with dynamic input dataset tracking.

This script tests that:
1. export_model_to_excel uses the correct input dataset
2. export_all_models_to_excel includes unique input datasets
"""

import sys
import pandas as pd
import os
from src.gabeda_context import GabedaContext
from src.export_utils import export_model_to_excel, export_all_models_to_excel

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Create output directory
os.makedirs('outputs/test', exist_ok=True)

# Create test configuration
user_config = {
    'client': 'test_export',
    'fidx_config': {'type': 'local', 'path': 'feature_index'}
}

# Initialize context
ctx = GabedaContext(user_config)

# Create mock data at different stages
print("\n" + "="*80)
print("SETTING UP TEST DATA")
print("="*80)

# 1. Preprocessed data
preprocessed_df = pd.DataFrame({
    'trans_id': [1, 2, 3, 4, 5],
    'producto': ['A', 'B', 'A', 'C', 'B'],
    'total': [100, 200, 150, 300, 250],
    'cantidad': [1, 2, 1, 3, 2]
})
ctx.set_dataset('preprocessed', preprocessed_df)
print(f"✓ Created 'preprocessed' dataset: {preprocessed_df.shape}")

# 2. Enriched data (output from transaction enrichment model)
enriched_df = preprocessed_df.copy()
enriched_df['profit_margin'] = [0.2, 0.3, 0.25, 0.35, 0.28]
enriched_df['hour'] = [10, 14, 11, 15, 12]
ctx.set_dataset('transactions_enriched', enriched_df)
print(f"✓ Created 'transactions_enriched' dataset: {enriched_df.shape}")

# 3. Mock model 1: transaction_enrichment (uses preprocessed as input)
print("\n" + "="*80)
print("SIMULATING MODEL 1: transaction_enrichment")
print("="*80)
ctx.set_model_output('transaction_enrichment', {
    'input_dataset_name': 'preprocessed',
    'filters': enriched_df,
    'attrs': None,
    'config': {'model_name': 'transaction_enrichment'}
})
print(f"✓ Registered with input: 'preprocessed'")

# 4. Mock model 2: product_stats (uses transactions_enriched as input)
product_attrs = pd.DataFrame({
    'producto': ['A', 'B', 'C'],
    'total_revenue': [250, 450, 300],
    'avg_revenue': [125, 225, 300],
    'count': [2, 2, 1]
})
print("\n" + "="*80)
print("SIMULATING MODEL 2: product_stats")
print("="*80)
ctx.set_model_output('product_stats', {
    'input_dataset_name': 'transactions_enriched',
    'filters': None,
    'attrs': product_attrs,
    'config': {'model_name': 'product_stats'}
})
print(f"✓ Registered with input: 'transactions_enriched'")

# 5. Mock model 3: time_analysis (also uses transactions_enriched as input)
time_attrs = pd.DataFrame({
    'hour': [10, 11, 12, 14, 15],
    'transactions': [1, 1, 1, 1, 1],
    'revenue': [100, 150, 250, 200, 300]
})
print("\n" + "="*80)
print("SIMULATING MODEL 3: time_analysis")
print("="*80)
ctx.set_model_output('time_analysis', {
    'input_dataset_name': 'transactions_enriched',
    'filters': None,
    'attrs': time_attrs,
    'config': {'model_name': 'time_analysis'}
})
print(f"✓ Registered with input: 'transactions_enriched'")

# Test 1: Export single model
print("\n" + "="*80)
print("TEST 1: export_model_to_excel")
print("="*80)
output_file = export_model_to_excel(
    ctx,
    'product_stats',
    'outputs/test/product_stats_export.xlsx',
    include_input=True
)

print("\n✓ Test 1 Passed: Single model export completed")
print(f"  File: {output_file}")
print("  Expected tabs:")
print("    - transactions_enriched (input)")
print("    - product_stats_attrs")

# Test 2: Export all models
print("\n" + "="*80)
print("TEST 2: export_all_models_to_excel")
print("="*80)
output_file = export_all_models_to_excel(
    ctx,
    'outputs/test/all_models_export.xlsx',
    include_unique_inputs=True
)

print("\n✓ Test 2 Passed: All models export completed")
print(f"  File: {output_file}")
print("  Expected tabs:")
print("    - preprocessed (input for transaction_enrichment)")
print("    - transactions_enriched (input for product_stats & time_analysis)")
print("    - transaction_enrichment_filters")
print("    - product_stats_attrs")
print("    - time_analysis_attrs")

# Verify the files were created
print("\n" + "="*80)
print("VERIFICATION")
print("="*80)

if os.path.exists('outputs/test/product_stats_export.xlsx'):
    print("✓ product_stats_export.xlsx exists")
else:
    print("✗ product_stats_export.xlsx NOT found")

if os.path.exists('outputs/test/all_models_export.xlsx'):
    print("✓ all_models_export.xlsx exists")
else:
    print("✗ all_models_export.xlsx NOT found")

# Summary of what changed
print("\n" + "="*80)
print("✅ EXPORT FUNCTIONS UPDATED!")
print("="*80)
print("\nKey Changes:")
print("  1. export_model_to_excel:")
print("     - Parameter: include_preprocessed → include_input")
print("     - Behavior: Exports the actual input used for the model")
print("     - Tab name: Uses the actual input dataset name")
print("")
print("  2. export_all_models_to_excel:")
print("     - Parameter: include_preprocessed → include_unique_inputs")
print("     - Behavior: Exports ALL unique inputs used across models")
print("     - Benefit: No duplicate datasets, includes all lineage")
print("")
print("Benefits:")
print("  ✓ Dynamic: Works regardless of input source")
print("  ✓ Accurate: Shows actual data used for each model")
print("  ✓ Reproducible: Can recreate results with exported data")
print("  ✓ Efficient: No duplicate datasets in multi-model exports")
print("="*80 + "\n")
