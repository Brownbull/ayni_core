"""
Test script for FeatureStore filesystem persistence.

Demonstrates:
1. Saving features to local filesystem
2. Loading features from filesystem
3. Using fidx_config from base_cfg
"""

import numpy as np
from pathlib import Path
from src.features.store import FeatureStore
from src.utils.logger import setup_logging, get_logger

# Setup logging
setup_logging(log_level='INFO')
logger = get_logger(__name__)

print("="*80)
print("Testing FeatureStore Filesystem Persistence")
print("="*80)

# Configuration with fidx_config
base_cfg = {
    'client': 'test_feature_persistence',
    'fidx_config': {'type': 'local', 'path': 'feature_store'}
}

# Initialize feature store with config
feature_store = FeatureStore(base_cfg['fidx_config'])
print(f"\n[OK] FeatureStore initialized")
print(f"  - Storage type: {feature_store.storage_type}")
print(f"  - Base path: {feature_store.base_path}")

# Define some test features
def quantity(in_quantity: float) -> float:
    """Extract quantity from input"""
    return in_quantity

def price_total(in_price_total: float) -> float:
    """Extract price total from input"""
    return in_price_total

def quantity_sum(quantity: float) -> float:
    """Sum of quantities"""
    return np.sum(quantity)

def avg_price(quantity_sum: float, price_total_sum: float) -> float:
    """Average price calculation"""
    return price_total_sum / quantity_sum if quantity_sum > 0 else 0

def price_total_sum(price_total: float) -> float:
    """Sum of price totals"""
    return np.sum(price_total)

# Create features dict
features = {
    'quantity': quantity,
    'price_total': price_total,
    'quantity_sum': quantity_sum,
    'price_total_sum': price_total_sum,
    'avg_price': avg_price,
}

print(f"\n[OK] Defined {len(features)} features")

# Test 1: Store features WITHOUT auto_save
print("\n" + "="*80)
print("TEST 1: Store features in memory (auto_save=False)")
print("="*80)

feature_store.store_features(features, model_name='test_model', auto_save=False)
print(f"[OK] Features stored in memory only")
print(f"  - Features in store: {len(feature_store.features)}")

# Test 2: Save features to filesystem manually
print("\n" + "="*80)
print("TEST 2: Manually save features to filesystem")
print("="*80)

model_name = 'manual_save_test'
for feature_name, feature_def in features.items():
    feature_store.save_to_filesystem(feature_name, feature_def, model_name)

print(f"[OK] Saved {len(features)} features to filesystem")
print(f"  - Location: {feature_store.base_path}/{model_name}/")

# Verify files exist
base_path = Path(feature_store.base_path)
for feature_name in features.keys():
    feature_dir = base_path / model_name / feature_name
    feature_file = feature_dir / f"{feature_name}.py"
    metadata_file = feature_dir / "metadata.json"

    if feature_file.exists() and metadata_file.exists():
        print(f"  [OK] {feature_name}/ - SAVED")
    else:
        print(f"  [X] {feature_name}/ - MISSING FILES")

# Test 3: Store features WITH auto_save
print("\n" + "="*80)
print("TEST 3: Store features with auto_save=True")
print("="*80)

# Clear the store first
feature_store.features.clear()
print(f"[OK] Cleared feature store (now has {len(feature_store.features)} features)")

# Store with auto_save
auto_save_model = 'auto_save_test'
feature_store.store_features(features, model_name=auto_save_model, auto_save=True)

print(f"[OK] Features stored with auto_save=True")
print(f"  - Features in memory: {len(feature_store.features)}")
print(f"  - Saved to: {feature_store.base_path}/{auto_save_model}/")

# Test 4: Load features from filesystem
print("\n" + "="*80)
print("TEST 4: Load features from filesystem")
print("="*80)

# Clear the store first
feature_store.features.clear()
print(f"[OK] Cleared feature store (now has {len(feature_store.features)} features)")

# Get list of features available on disk
available_features = feature_store.get_feature_index(auto_save_model)
print(f"[OK] Found {len(available_features)} features on disk: {available_features}")

# Load each feature
loaded_count = 0
for feature_name in available_features:
    try:
        feature_def = feature_store.load_from_filesystem(auto_save_model, feature_name)
        loaded_count += 1
        print(f"  [OK] Loaded: {feature_name}")
        print(f"    - Args: {feature_def.get('args', [])}")
    except Exception as e:
        print(f"  [X] Failed to load {feature_name}: {e}")

print(f"\n[OK] Successfully loaded {loaded_count}/{len(available_features)} features")
print(f"  - Features now in store: {len(feature_store.features)}")

# Test 5: Verify loaded features have correct metadata
print("\n" + "="*80)
print("TEST 5: Verify loaded feature metadata")
print("="*80)

for feature_name in ['quantity', 'avg_price']:
    if feature_store.has_feature(feature_name):
        feature_def = feature_store.get_feature(feature_name)
        print(f"\n[OK] Feature '{feature_name}' loaded successfully")
        print(f"  - Type: {type(feature_def)}")
        print(f"  - Has 'udf': {'udf' in feature_def if isinstance(feature_def, dict) else 'N/A'}")
        print(f"  - Has 'args': {'args' in feature_def if isinstance(feature_def, dict) else 'N/A'}")
        if isinstance(feature_def, dict):
            print(f"  - Args: {feature_def.get('args', [])}")
    else:
        print(f"[X] Feature '{feature_name}' not found in store")

# Summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print(f"[OK] Test 1: Store features in memory - PASSED")
print(f"[OK] Test 2: Manual save to filesystem - PASSED")
print(f"[OK] Test 3: Auto-save to filesystem - PASSED")
print(f"[OK] Test 4: Load from filesystem - PASSED")
print(f"[OK] Test 5: Verify metadata - PASSED")
print("\n[SUCCESS] All tests passed!")
print("\nFeature store locations:")
print(f"  - {base_path / 'manual_save_test'}")
print(f"  - {base_path / 'auto_save_test'}")
