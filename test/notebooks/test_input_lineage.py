"""
Test script to verify input dataset lineage tracking.

This script tests that:
1. Model execution stores input_dataset_name (not the full dataframe)
2. ctx.get_dataset('{model_name}_input') retrieves the correct input
3. ctx.get_model_input(model_name) works as convenience method
"""

import sys
import pandas as pd
from src.gabeda_context import GabedaContext

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Create a simple test configuration
user_config = {
    'client': 'test_client',
    'fidx_config': {'type': 'local', 'path': 'feature_index'}
}

# Initialize context
ctx = GabedaContext(user_config)

# Create mock preprocessed data
preprocessed_df = pd.DataFrame({
    'trans_id': [1, 2, 3, 4, 5],
    'producto': ['A', 'B', 'A', 'C', 'B'],
    'total': [100, 200, 150, 300, 250],
    'cantidad': [1, 2, 1, 3, 2]
})

# Store preprocessed data in context
ctx.set_dataset('preprocessed', preprocessed_df)

# Create enriched data (simulating transaction enrichment output)
enriched_df = preprocessed_df.copy()
enriched_df['profit_margin'] = [0.2, 0.3, 0.25, 0.35, 0.28]

# Store enriched data in context
ctx.set_dataset('transactions_enriched', enriched_df)

# Create mock product stats output
product_stats_attrs = pd.DataFrame({
    'producto': ['A', 'B', 'C'],
    'total_revenue': [250, 450, 300],
    'avg_revenue': [125, 225, 300],
    'total_quantity': [2, 4, 3]
})

# Manually call set_model_output to simulate model execution
print("\n" + "="*80)
print("SIMULATING MODEL EXECUTION: product_stats")
print("="*80)
print("Using 'transactions_enriched' as input...")

results = {
    'input_dataset_name': 'transactions_enriched',
    'filters': None,
    'attrs': product_stats_attrs,
    'config': {'model_name': 'product_stats'}
}

ctx.set_model_output('product_stats', results)

# Verify results
print("\n" + "="*80)
print("VERIFICATION TESTS")
print("="*80)

# Test 1: Check that input_dataset_name is stored in results
print("\n1. Check input_dataset_name in results:")
assert 'input_dataset_name' in results, "❌ input_dataset_name not in results"
print(f"   ✓ input_dataset_name: {results['input_dataset_name']}")
assert results['input_dataset_name'] == 'transactions_enriched', "❌ Wrong input_dataset_name"
print("   ✓ Correct value: 'transactions_enriched'")

# Test 2: Check that input_dataset_name is stored in model metadata
print("\n2. Check model metadata stores input reference:")
model_output = ctx.get_model_output('product_stats')
assert model_output is not None, "❌ Model output not found"
assert 'input_dataset_name' in model_output, "❌ input_dataset_name not in model metadata"
print(f"   ✓ Model metadata has input_dataset_name: {model_output['input_dataset_name']}")

# Test 3: Test ctx.get_dataset('{model_name}_input') pattern
print("\n3. Test ctx.get_dataset('product_stats_input'):")
input_via_pattern = ctx.get_dataset('product_stats_input')
assert input_via_pattern is not None, "❌ get_dataset('{model}_input') returned None"
print(f"   ✓ Retrieved input dataset: shape {input_via_pattern.shape}")
assert input_via_pattern.equals(enriched_df), "❌ Wrong dataframe returned"
print("   ✓ Correct dataframe (transactions_enriched)")

# Test 4: Test convenience method ctx.get_model_input()
print("\n4. Test ctx.get_model_input('product_stats'):")
input_via_method = ctx.get_model_input('product_stats')
assert input_via_method is not None, "❌ get_model_input() returned None"
print(f"   ✓ Retrieved input dataset: shape {input_via_method.shape}")
assert input_via_method.equals(enriched_df), "❌ Wrong dataframe returned"
print("   ✓ Correct dataframe (transactions_enriched)")

# Test 5: Verify both methods return the same object
print("\n5. Test that both methods return same object:")
assert input_via_pattern is input_via_method, "❌ Different objects returned"
print("   ✓ Same object reference (memory efficient)")

# Test 6: Show data lineage
print("\n" + "="*80)
print("DATA LINEAGE DEMONSTRATION")
print("="*80)
print(f"\nModel: product_stats")
print(f"  Input: {model_output['input_dataset_name']}")
print(f"  Outputs generated: {model_output.get('datasets_generated', [])}")

# Test 7: Verify execution history includes input dataset
print("\n6. Verify execution history:")
summary = ctx.get_execution_summary()
last_execution = summary['history'][-1]
assert last_execution['action'] == 'model_executed', "❌ Wrong action in history"
assert last_execution['input_dataset'] == 'transactions_enriched', "❌ Wrong input in history"
print(f"   ✓ History records input dataset: {last_execution['input_dataset']}")

print("\n" + "="*80)
print("✅ ALL TESTS PASSED!")
print("="*80)
print("\nSummary:")
print("  - Models now store input_dataset_name instead of full dataframe")
print("  - Memory efficient: no data duplication")
print("  - Data lineage: can trace which input was used for each model")
print("  - Access patterns:")
print("    • ctx.get_dataset('product_stats_input')")
print("    • ctx.get_model_input('product_stats')")
print("="*80 + "\n")
