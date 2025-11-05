"""
Test script for feature_development_notebook.ipynb
Runs the notebook logic to detect any errors.
"""

# Imports
import pandas as pd
import numpy as np
from pathlib import Path
import inspect

# GabeDA imports
from src.utils.logger import setup_logging, get_logger
from src.core.context import GabedaContext
from src.features.store import FeatureStore
from src.features.detector import FeatureTypeDetector
from src.preprocessing.loaders import DataLoader

# Setup logging
setup_logging(log_level='INFO')
logger = get_logger(__name__)

print("[OK] Imports complete")

# Configuration
base_cfg = {
    'client': 'feature_development',
    'fidx_config': {'type': 'local', 'path': 'feature_store'},
    'log_level': 'INFO'
}

# Initialize feature store
feature_store = FeatureStore(base_cfg['fidx_config'])
detector = FeatureTypeDetector()

print("[OK] Feature store initialized")
print(f"  - Storage type: {feature_store.storage_type}")
print(f"  - Base path: {feature_store.base_path}")
print(f"  - Common folder: {feature_store.common_folder}")

# Load Sample Data
data_file = 'data/buenacarne/buenacarne_transactions.csv'

if Path(data_file).exists():
    loader = DataLoader()
    df_raw = loader.load_csv(data_file)
    df_sample = df_raw.head(100).copy()
    print(f"[OK] Loaded sample data: {df_sample.shape}")
    print(f"  - Columns: {list(df_sample.columns)}")
else:
    print(f"[!] Data file not found: {data_file}")
    print("  Creating synthetic sample data...")

    df_sample = pd.DataFrame({
        'in_trans_id': [f'T{i:03d}' for i in range(1, 21)],
        'in_dt': pd.date_range('2025-01-01', periods=20, freq='D'),
        'in_product_id': ['A', 'B', 'C', 'A', 'B'] * 4,
        'in_quantity': [10, 15, 20, 12, 18, 25, 8, 14, 22, 16,
                        11, 19, 21, 13, 17, 24, 9, 15, 23, 20],
        'in_price_total': [100, 150, 200, 120, 180, 250, 80, 140, 220, 160,
                           110, 190, 210, 130, 170, 240, 90, 150, 230, 200]
    })
    print(f"[OK] Created synthetic sample data: {df_sample.shape}")

# Display sample (using print instead of display)
print("\nSample Data:")
print(df_sample.head())

# Define features
print("\n" + "="*80)
print("Defining Features")
print("="*80)

def in_quantity(in_quantity: float) -> float:
    """Extract quantity from input (COMMON)"""
    return in_quantity

def in_price_total(in_price_total: float) -> float:
    """Extract price total from input (COMMON)"""
    return in_price_total

def in_product_id(in_product_id: str) -> str:
    """Extract product ID from input (COMMON)"""
    return in_product_id

def in_trans_id(in_trans_id: str) -> str:
    """Extract transaction ID from input (COMMON)"""
    return in_trans_id

def quantity_sum(in_quantity: float) -> float:
    """Sum of quantities (COMMON)"""
    return np.sum(in_quantity)

def price_total_sum(in_price_total: float) -> float:
    """Sum of price totals (COMMON)"""
    return np.sum(in_price_total)

def quantity_mean(in_quantity: float) -> float:
    """Mean of quantities (COMMON)"""
    return np.mean(in_quantity)

def price_total_mean(in_price_total: float) -> float:
    """Mean of price totals (COMMON)"""
    return np.mean(in_price_total)

def transaction_count(in_trans_id: str) -> int:
    """Count of unique transactions (COMMON)"""
    return len(np.unique(in_trans_id))

def product_count(in_product_id: str) -> int:
    """Count of unique products (COMMON)"""
    return len(np.unique(in_product_id))

def avg_price_per_unit(quantity_sum: float, price_total_sum: float) -> float:
    """Average price per unit (COMMON)"""
    return price_total_sum / quantity_sum if quantity_sum > 0 else 0

def avg_transaction_value(price_total_sum: float, transaction_count: int) -> float:
    """Average transaction value (COMMON)"""
    return price_total_sum / transaction_count if transaction_count > 0 else 0

def avg_quantity_per_transaction(quantity_sum: float, transaction_count: int) -> float:
    """Average quantity per transaction (COMMON)"""
    return quantity_sum / transaction_count if transaction_count > 0 else 0

print("[OK] Defined all features")

# Collect features
new_features = {
    'in_quantity': in_quantity,
    'in_price_total': in_price_total,
    'in_product_id': in_product_id,
    'in_trans_id': in_trans_id,
    'quantity_sum': quantity_sum,
    'price_total_sum': price_total_sum,
    'quantity_mean': quantity_mean,
    'price_total_mean': price_total_mean,
    'transaction_count': transaction_count,
    'product_count': product_count,
    'avg_price_per_unit': avg_price_per_unit,
    'avg_transaction_value': avg_transaction_value,
    'avg_quantity_per_transaction': avg_quantity_per_transaction,
}

print(f"[OK] Collected {len(new_features)} new features for testing")

# Test features
print("\n" + "="*80)
print("Testing Features")
print("="*80)

# Test Case 1
test_result = in_quantity(df_sample['in_quantity'].values[0])
print(f"[TEST] in_quantity: {'PASS' if test_result == df_sample['in_quantity'].values[0] else 'FAIL'}")

# Test Case 3
test_result = quantity_sum(df_sample['in_quantity'].values)
expected = df_sample['in_quantity'].sum()
print(f"[TEST] quantity_sum: {'PASS' if test_result == expected else 'FAIL'}")

# Test derived
qty_sum = quantity_sum(df_sample['in_quantity'].values)
price_sum = price_total_sum(df_sample['in_price_total'].values)
test_result = avg_price_per_unit(qty_sum, price_sum)
expected = price_sum / qty_sum if qty_sum > 0 else 0
print(f"[TEST] avg_price_per_unit: {'PASS' if abs(test_result - expected) < 0.01 else 'FAIL'}")

# Validate signatures
print("\n" + "="*80)
print("Validating Feature Signatures")
print("="*80)

validation_results = []
for name, func in new_features.items():
    try:
        if not callable(func):
            validation_results.append((name, 'FAIL', 'Not callable'))
            continue

        sig = inspect.signature(func)
        args = list(sig.parameters.keys())
        source = inspect.getsource(func)
        is_agg = detector.is_aggregation(func)
        feature_type = 'Attribute (aggregation)' if is_agg else 'Filter or Attribute'

        validation_results.append((name, 'PASS', f'{feature_type}, args={args}'))
    except Exception as e:
        validation_results.append((name, 'FAIL', str(e)))

# Display results
for name, status, details in validation_results:
    status_symbol = '[OK]' if status == 'PASS' else '[X]'
    print(f"{status_symbol} {name:30s} - {details}")

passed = sum(1 for _, status, _ in validation_results if status == 'PASS')
total = len(validation_results)
print(f"\n[SUMMARY] {passed}/{total} features validated successfully")

# Feature summary (using print instead of display)
print("\n" + "="*80)
print("Feature Summary")
print("="*80)

feature_summary = []
for name, func in new_features.items():
    sig = inspect.signature(func)
    args = list(sig.parameters.keys())
    is_agg = detector.is_aggregation(func)
    feature_type = 'Attribute (aggregation)' if is_agg else 'Filter or Attribute'
    docstring = func.__doc__ or 'No description'

    feature_summary.append({
        'Feature': name,
        'Type': feature_type,
        'Args': ', '.join(args),
        'Description': docstring.strip()
    })

summary_df = pd.DataFrame(feature_summary)
print(summary_df.to_string())

print(f"\n[INFO] Total features to save: {len(new_features)}")
print(f"[INFO] Destination: {feature_store.base_path}/{feature_store.common_folder}/")

# Save features
print("\n" + "="*80)
print("Saving Features to Common Store")
print("="*80)

feature_store.store_features(
    new_features,
    model_name=None,
    auto_save=True
)

print(f"\n[SUCCESS] Saved {len(new_features)} features to common store")

# Verify
common_path = Path(feature_store.base_path) / feature_store.common_folder
if common_path.exists():
    saved_features = [d.name for d in common_path.iterdir() if d.is_dir()]
    print(f"[INFO] Total features in common folder: {len(saved_features)}")

# Reload and verify
print("\n" + "="*80)
print("Verifying Saved Features")
print("="*80)

feature_store.features.clear()
loaded_count = feature_store.load_common_features()
print(f"[OK] Loaded {loaded_count} features from common folder")

verification_results = []
for name in new_features.keys():
    if feature_store.has_feature(name):
        feature_def = feature_store.get_feature(name)
        if isinstance(feature_def, dict) and 'udf' in feature_def and 'args' in feature_def:
            verification_results.append((name, 'PASS', f"args={feature_def['args']}"))
        else:
            verification_results.append((name, 'FAIL', 'Invalid format'))
    else:
        verification_results.append((name, 'FAIL', 'Not found'))

passed = sum(1 for _, status, _ in verification_results if status == 'PASS')
total = len(verification_results)
print(f"[SUMMARY] {passed}/{total} features verified successfully")

if passed == total:
    print(f"\n[SUCCESS] All features saved and verified!")
else:
    print(f"\n[WARNING] Some features failed verification")

# Inspect a feature
print("\n" + "="*80)
print("Inspecting Feature: avg_price_per_unit")
print("="*80)

inspect_feature = 'avg_price_per_unit'
feature_dir = Path(feature_store.base_path) / feature_store.common_folder / inspect_feature
feature_file = feature_dir / f"{inspect_feature}.py"
metadata_file = feature_dir / "metadata.json"

if feature_file.exists():
    print(f"\n[FILE] {feature_file}")
    print("-" * 80)
    with open(feature_file, 'r', encoding='utf-8') as f:
        print(f.read())

if metadata_file.exists():
    print(f"\n[FILE] {metadata_file}")
    print("-" * 80)
    with open(metadata_file, 'r', encoding='utf-8') as f:
        print(f.read())

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
print("[SUCCESS] Notebook logic executed without errors!")
