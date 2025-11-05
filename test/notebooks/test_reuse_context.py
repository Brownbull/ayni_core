"""
Test script to demonstrate context reuse behavior.

This script simulates the workflow:
1. Notebook 01_transactions creates context folder with 3 datasets
2. Notebook 02_product_daily loads context and adds 2 more datasets to SAME folder
3. Notebook 03_customer loads context and adds 1 more dataset to SAME folder

Result: Single context folder with all 6 datasets accumulated
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from src.core.context import GabedaContext
from src.core.persistence import save_context_state, load_context_state, get_latest_state

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Minimal config for testing
test_cfg = {
    'client': 'test_reuse',
    'input_file': 'data/tests/raw/quick_test_7days.csv',
    'log_level': 'INFO'
}

output_dir = 'data/intermediate'

print("=" * 70)
print("TESTING CONTEXT REUSE BEHAVIOR")
print("=" * 70)

# Check initial state
print("\n📂 Initial state:")
base_path = Path(output_dir)
if base_path.exists():
    existing = list(base_path.glob('test_reuse_*'))
    print(f"  Found {len(existing)} existing test_reuse folders")
    for folder in existing:
        print(f"    - {folder.name}")
else:
    print("  No existing folders")

# ========================================================================
# Simulation 1: First notebook (01_transactions)
# ========================================================================
print("\n" + "=" * 70)
print("NOTEBOOK 1: 01_transactions.ipynb")
print("=" * 70)
print("📝 Creating initial context with 3 datasets...")

ctx1 = GabedaContext(test_cfg)
ctx1.set_dataset('transactions_raw', pd.DataFrame({'a': [1, 2, 3]}))
ctx1.set_dataset('transactions_enriched', pd.DataFrame({'b': [4, 5, 6]}))
ctx1.set_dataset('transactions_filters', pd.DataFrame({'c': [7, 8, 9]}))

state1 = save_context_state(ctx1, test_cfg, output_base=output_dir, reuse_existing=True)
print(f"\n✓ Created context: {Path(state1).name}")
print(f"  - Datasets: {list(ctx1.datasets.keys())}")

# Check folders
existing = list(base_path.glob('test_reuse_*'))
print(f"\n📂 After Notebook 1: {len(existing)} folder(s)")
for folder in existing:
    datasets_count = len(list((folder / 'datasets').glob('*.csv')))
    print(f"    - {folder.name} ({datasets_count} datasets)")

# ========================================================================
# Simulation 2: Second notebook (02_product_daily)
# ========================================================================
print("\n" + "=" * 70)
print("NOTEBOOK 2: 02_product_daily.ipynb")
print("=" * 70)
print("📝 Loading existing context and adding 2 more datasets...")

# Load the context from previous notebook
latest_state = get_latest_state('test_reuse', base_dir=output_dir)
print(f"  - Loading from: {Path(latest_state).name}")
ctx2, cfg2 = load_context_state(latest_state)

print(f"  - Loaded datasets: {list(ctx2.datasets.keys())}")

# Add new datasets
ctx2.set_dataset('product_daily_filters', pd.DataFrame({'d': [10, 11, 12]}))
ctx2.set_dataset('product_daily_attrs', pd.DataFrame({'e': [13, 14, 15]}))

print(f"  - After adding new datasets: {list(ctx2.datasets.keys())}")

# Save (should reuse same folder)
state2 = save_context_state(ctx2, cfg2, output_base=output_dir, reuse_existing=True)
print(f"\n✓ Saved to context: {Path(state2).name}")
print(f"  - Total datasets now: {len(ctx2.datasets)}")

# Check folders
existing = list(base_path.glob('test_reuse_*'))
print(f"\n📂 After Notebook 2: {len(existing)} folder(s)")
for folder in existing:
    datasets_count = len(list((folder / 'datasets').glob('*.csv')))
    print(f"    - {folder.name} ({datasets_count} datasets)")

# ========================================================================
# Simulation 3: Third notebook (03_customer)
# ========================================================================
print("\n" + "=" * 70)
print("NOTEBOOK 3: 03_customer.ipynb")
print("=" * 70)
print("📝 Loading existing context and adding 1 more dataset...")

# Load the context again
latest_state = get_latest_state('test_reuse', base_dir=output_dir)
print(f"  - Loading from: {Path(latest_state).name}")
ctx3, cfg3 = load_context_state(latest_state)

print(f"  - Loaded datasets: {list(ctx3.datasets.keys())}")

# Add another dataset
ctx3.set_dataset('customer_attrs', pd.DataFrame({'f': [16, 17, 18]}))

print(f"  - After adding new dataset: {list(ctx3.datasets.keys())}")

# Save (should reuse same folder)
state3 = save_context_state(ctx3, cfg3, output_base=output_dir, reuse_existing=True)
print(f"\n✓ Saved to context: {Path(state3).name}")
print(f"  - Total datasets now: {len(ctx3.datasets)}")

# Final check
existing = list(base_path.glob('test_reuse_*'))
print(f"\n📂 After Notebook 3: {len(existing)} folder(s)")
for folder in existing:
    datasets_count = len(list((folder / 'datasets').glob('*.csv')))
    datasets = [f.stem for f in (folder / 'datasets').glob('*.csv')]
    print(f"    - {folder.name} ({datasets_count} datasets)")
    print(f"      Datasets: {', '.join(datasets)}")

# ========================================================================
# Verification
# ========================================================================
print("\n" + "=" * 70)
print("VERIFICATION")
print("=" * 70)

if len(existing) == 1:
    folder = existing[0]
    datasets = list((folder / 'datasets').glob('*.csv'))
    print(f"✅ SUCCESS: Only 1 context folder exists!")
    print(f"   Folder: {folder.name}")
    print(f"   Total datasets: {len(datasets)}")
    print(f"   Expected: 6 datasets")

    if len(datasets) == 6:
        print(f"\n🎉 PERFECT! All datasets accumulated in single folder:")
        for ds in sorted(datasets):
            print(f"      ✓ {ds.name}")
    else:
        print(f"\n⚠️  Expected 6 datasets, found {len(datasets)}")
else:
    print(f"⚠️  Expected 1 folder, found {len(existing)}")

print("\n💡 To disable context reuse and create new folders, use:")
print("   save_context_state(ctx, cfg, reuse_existing=False)")
print("=" * 70)

# Cleanup
print("\n🧹 Cleaning up test folder...")
for folder in existing:
    import shutil
    shutil.rmtree(folder)
print("✓ Cleanup complete")
