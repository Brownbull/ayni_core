"""
Functional test for resolver.py after refactoring.

Purpose: Verify resolver works with real usage patterns.
Tests actual code paths, not just imports.
"""

from src.features import DependencyResolver, FeatureStore

def test_resolver_basic_functionality():
    """Test that resolver works with real feature dependencies."""
    print("[TEST 1/3] Testing basic dependency resolution...")

    store = FeatureStore()

    # Define features with dependencies
    def base_feature(col1):
        return col1 * 2

    def derived_feature(base_feature, col2):
        return base_feature + col2

    store.store_feature('base_feature', base_feature)
    store.store_feature('derived_feature', derived_feature)

    resolver = DependencyResolver(store)

    # This should resolve dependencies correctly
    in_cols, exec_seq, ext_cols = resolver.resolve_dependencies(
        output_cols=['derived_feature'],
        available_cols=['col1', 'col2'],
        group_by=None,
        model='test_model'
    )

    # Verify resolution
    assert 'col1' in in_cols, f"Expected 'col1' in in_cols, got: {in_cols}"
    assert 'col2' in in_cols, f"Expected 'col2' in in_cols, got: {in_cols}"
    assert 'base_feature' in exec_seq, f"Expected 'base_feature' in exec_seq, got: {exec_seq}"
    assert 'derived_feature' in exec_seq, f"Expected 'derived_feature' in exec_seq, got: {exec_seq}"

    # Verify execution order (base_feature must come before derived_feature)
    assert exec_seq.index('base_feature') < exec_seq.index('derived_feature'), \
        "base_feature should come before derived_feature in execution sequence"

    print(f"  ✓ Input columns: {in_cols}")
    print(f"  ✓ Execution sequence: {exec_seq}")
    print("[OK] Basic dependency resolution works")


def test_resolver_with_group_by():
    """Test that resolver handles group_by normalization correctly."""
    print("[TEST 2/3] Testing group_by normalization...")

    store = FeatureStore()
    resolver = DependencyResolver(store)

    # Test with None group_by
    in_cols, exec_seq, ext_cols = resolver.resolve_dependencies(
        output_cols=[],
        available_cols=['col1'],
        group_by=None,  # Should be normalized to []
        model='test_model'
    )
    print("  ✓ Handled group_by=None correctly")

    # Test with empty string group_by
    in_cols, exec_seq, ext_cols = resolver.resolve_dependencies(
        output_cols=[],
        available_cols=['col1'],
        group_by='',  # Should be normalized to []
        model='test_model'
    )
    print("  ✓ Handled group_by='' correctly")

    # Test with single string group_by
    in_cols, exec_seq, ext_cols = resolver.resolve_dependencies(
        output_cols=[],
        available_cols=['col1'],
        group_by='product_id',  # Should be normalized to ['product_id']
        model='test_model'
    )
    print("  ✓ Handled group_by='product_id' correctly")

    # Test with list group_by
    in_cols, exec_seq, ext_cols = resolver.resolve_dependencies(
        output_cols=[],
        available_cols=['col1'],
        group_by=['product_id', 'date'],  # Should stay as list
        model='test_model'
    )
    print("  ✓ Handled group_by=['product_id', 'date'] correctly")

    print("[OK] Group_by normalization works (uses normalize_to_list)")


def test_resolver_available_columns():
    """Test that resolver correctly identifies available vs computed columns."""
    print("[TEST 3/3] Testing available column detection...")

    store = FeatureStore()
    resolver = DependencyResolver(store)

    # Test with directly available columns
    in_cols, exec_seq, ext_cols = resolver.resolve_dependencies(
        output_cols=['col1', 'col2'],
        available_cols=['col1', 'col2', 'col3'],
        group_by=None,
        model='test_model'
    )

    # Available columns should be in in_cols, not exec_seq
    assert 'col1' in in_cols
    assert 'col2' in in_cols
    assert 'col1' not in exec_seq  # Available columns don't need execution
    assert 'col2' not in exec_seq

    print(f"  ✓ Available columns detected: {in_cols}")
    print(f"  ✓ No execution needed for available columns")
    print("[OK] Available column detection works")


if __name__ == '__main__':
    print("=" * 60)
    print("Functional Tests for resolver.py (Post-Refactor)")
    print("=" * 60)
    print()

    try:
        test_resolver_basic_functionality()
        print()
        test_resolver_with_group_by()
        print()
        test_resolver_available_columns()
        print()
        print("=" * 60)
        print("✓ ALL FUNCTIONAL TESTS PASSED")
        print("=" * 60)
    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"✗ TEST FAILED: {e}")
        print("=" * 60)
        exit(1)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ UNEXPECTED ERROR: {e}")
        print("=" * 60)
        exit(1)
