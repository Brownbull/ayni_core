"""
Test script to demonstrate the automatic cleanup behavior of save_context_state.

This script simulates the workflow:
1. Run 01_transactions notebook -> creates context folder A
2. Run 02_product_daily notebook -> creates context folder B and deletes folder A
3. Run 02_product_daily again -> creates context folder C and deletes folder B
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from src.core.context import GabedaContext
from src.core.persistence import save_context_state, get_latest_state

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Minimal config for testing
test_cfg = {
    'client': 'test_cleanup',
    'input_file': 'data/tests/raw/quick_test_7days.csv',
    'log_level': 'INFO'
}

output_dir = 'data/intermediate'

print("=" * 60)
print("TESTING AUTOMATIC CLEANUP OF OLD CONTEXT STATES")
print("=" * 60)

# Check initial state
print("\n📂 Initial state:")
base_path = Path(output_dir)
if base_path.exists():
    existing = list(base_path.glob('test_cleanup_*'))
    print(f"  Found {len(existing)} existing test_cleanup folders")
    for folder in existing:
        print(f"    - {folder.name}")
else:
    print("  No existing folders")

# Execution 1: First save
print("\n🔹 Execution 1: Creating first context...")
ctx1 = GabedaContext(test_cfg)
ctx1.set_dataset('sample', pd.DataFrame({'a': [1, 2, 3]}))
state1 = save_context_state(ctx1, test_cfg, output_base=output_dir, cleanup_old=True)
print(f"✓ Created: {Path(state1).name}")

# Check folders after execution 1
existing = list(base_path.glob('test_cleanup_*'))
print(f"\n📂 After Execution 1: {len(existing)} folder(s)")
for folder in existing:
    print(f"    - {folder.name}")

# Execution 2: Second save (should delete first)
print("\n🔹 Execution 2: Creating second context...")
print("  (This should delete the first context after successful save)")
ctx2 = GabedaContext(test_cfg)
ctx2.set_dataset('sample', pd.DataFrame({'a': [4, 5, 6]}))
state2 = save_context_state(ctx2, test_cfg, output_base=output_dir, cleanup_old=True)
print(f"✓ Created: {Path(state2).name}")

# Check folders after execution 2
existing = list(base_path.glob('test_cleanup_*'))
print(f"\n📂 After Execution 2: {len(existing)} folder(s)")
for folder in existing:
    print(f"    - {folder.name}")

# Execution 3: Third save (should delete second)
print("\n🔹 Execution 3: Creating third context...")
print("  (This should delete the second context after successful save)")
ctx3 = GabedaContext(test_cfg)
ctx3.set_dataset('sample', pd.DataFrame({'a': [7, 8, 9]}))
state3 = save_context_state(ctx3, test_cfg, output_base=output_dir, cleanup_old=True)
print(f"✓ Created: {Path(state3).name}")

# Final check
existing = list(base_path.glob('test_cleanup_*'))
print(f"\n📂 After Execution 3: {len(existing)} folder(s)")
for folder in existing:
    print(f"    - {folder.name}")

print("\n" + "=" * 60)
print("RESULT:")
if len(existing) == 1:
    print("✅ SUCCESS: Only the latest context folder exists!")
    print(f"   Latest: {existing[0].name}")
else:
    print(f"⚠️  Expected 1 folder, found {len(existing)}")

print("\n💡 To disable automatic cleanup, use:")
print("   save_context_state(ctx, cfg, cleanup_old=False)")
print("=" * 60)
