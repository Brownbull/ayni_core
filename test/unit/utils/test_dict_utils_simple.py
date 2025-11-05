"""
Simple test script for dict_utils (no pytest required)
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.dict_utils import (
    safe_get,
    normalize_to_list,
    merge_dicts,
    get_nested,
    filter_dict_by_keys,
    get_or_raise,
    has_all_keys,
    get_missing_keys,
    invert_dict,
)

def test_safe_get():
    print("Testing safe_get...")
    d = {'name': 'test', 'count': 5}
    assert safe_get(d, 'name') == 'test'
    assert safe_get(d, 'missing', default='default') == 'default'
    print("  [OK] safe_get passed")

def test_normalize_to_list():
    print("Testing normalize_to_list...")

    # Empty values
    assert normalize_to_list(None) == []
    assert normalize_to_list('') == []
    assert normalize_to_list([]) == []

    # Single values
    assert normalize_to_list('product') == ['product']
    assert normalize_to_list(42) == [42]

    # Already list
    assert normalize_to_list(['a', 'b']) == ['a', 'b']

    # to_none=True
    assert normalize_to_list(None, to_none=True) is None
    assert normalize_to_list('', to_none=True) is None
    assert normalize_to_list('product', to_none=True) == ['product']

    print("  [OK] normalize_to_list passed")

def test_executor_pattern():
    """Test the exact pattern from executor.py:93-96"""
    print("Testing executor.py pattern...")

    # Simulate executor.py:93-96
    cfg_model = {'group_by': ''}
    group_by = cfg_model.get('group_by')

    # OLD way (executor.py):
    # if group_by is not None and (group_by == [] or group_by == ''):
    #     group_by = None

    # NEW way:
    group_by = normalize_to_list(group_by, to_none=True)
    assert group_by is None

    # Test with actual value
    cfg_model = {'group_by': 'product'}
    group_by = normalize_to_list(cfg_model.get('group_by'), to_none=True)
    assert group_by == ['product']

    # Test with empty list
    cfg_model = {'group_by': []}
    group_by = normalize_to_list(cfg_model.get('group_by'), to_none=True)
    assert group_by is None

    print("  [OK] executor.py pattern passed")

def test_resolver_pattern():
    """Test the exact pattern from resolver.py:68-71"""
    print("Testing resolver.py pattern...")

    # Simulate resolver.py:68-71
    cfg_model = {'group_by': None}

    # OLD way (resolver.py):
    # if group_by is None or group_by == '':
    #     group_by = []
    # elif not isinstance(group_by, list):
    #     group_by = [group_by]

    # NEW way:
    group_by = normalize_to_list(cfg_model.get('group_by'))
    assert group_by == []

    # Test with string
    cfg_model = {'group_by': 'product'}
    group_by = normalize_to_list(cfg_model.get('group_by'))
    assert group_by == ['product']

    # Test with list
    cfg_model = {'group_by': ['product', 'date']}
    group_by = normalize_to_list(cfg_model.get('group_by'))
    assert group_by == ['product', 'date']

    print("  [OK] resolver.py pattern passed")

def test_merge_dicts():
    print("Testing merge_dicts...")
    base = {'a': 1, 'b': 2}
    updates = {'b': 3, 'c': 4}

    # No mutation
    result = merge_dicts(base, updates, mutate=False)
    assert result == {'a': 1, 'b': 3, 'c': 4}
    assert base == {'a': 1, 'b': 2}  # Unchanged

    # With mutation
    base2 = {'a': 1, 'b': 2}
    result2 = merge_dicts(base2, updates, mutate=True)
    assert base2 == {'a': 1, 'b': 3, 'c': 4}  # Changed
    assert result2 is base2

    print("  [OK] merge_dicts passed")

def test_get_nested():
    print("Testing get_nested...")
    d = {'model': {'name': 'test', 'params': {'lr': 0.01}}}

    assert get_nested(d, 'model', 'name') == 'test'
    assert get_nested(d, 'model', 'params', 'lr') == 0.01
    assert get_nested(d, 'model', 'missing', default='default') == 'default'

    print("  [OK] get_nested passed")

def test_filter_dict_by_keys():
    print("Testing filter_dict_by_keys...")
    d = {'a': 1, 'b': 2, 'c': 3, 'd': 4}

    result = filter_dict_by_keys(d, ['a', 'c'])
    assert result == {'a': 1, 'c': 3}

    # Safe mode with missing keys
    result2 = filter_dict_by_keys(d, ['a', 'missing'], safe=True)
    assert result2 == {'a': 1}

    print("  [OK] filter_dict_by_keys passed")

def test_get_or_raise():
    print("Testing get_or_raise...")
    d = {'name': 'test'}

    assert get_or_raise(d, 'name') == 'test'

    try:
        get_or_raise(d, 'missing')
        assert False, "Should have raised KeyError"
    except KeyError as e:
        assert "Key 'missing' not found" in str(e)

    print("  [OK] get_or_raise passed")

def test_has_all_keys():
    print("Testing has_all_keys...")
    d = {'name': 'test', 'version': 1}

    assert has_all_keys(d, ['name', 'version']) is True
    assert has_all_keys(d, ['name', 'version', 'missing']) is False
    assert has_all_keys(d, []) is True

    print("  [OK] has_all_keys passed")

def test_get_missing_keys():
    print("Testing get_missing_keys...")
    d = {'name': 'test', 'version': 1}

    assert get_missing_keys(d, ['name', 'version']) == []
    assert get_missing_keys(d, ['name', 'version', 'enabled']) == ['enabled']

    print("  [OK] get_missing_keys passed")

def test_invert_dict():
    print("Testing invert_dict...")
    d = {'a': 1, 'b': 2, 'c': 3}

    result = invert_dict(d)
    assert result == {1: 'a', 2: 'b', 3: 'c'}

    print("  [OK] invert_dict passed")

def main():
    print("=" * 60)
    print("Running dict_utils tests...")
    print("=" * 60)

    try:
        test_safe_get()
        test_normalize_to_list()
        test_executor_pattern()
        test_resolver_pattern()
        test_merge_dicts()
        test_get_nested()
        test_filter_dict_by_keys()
        test_get_or_raise()
        test_has_all_keys()
        test_get_missing_keys()
        test_invert_dict()

        print("=" * 60)
        print("[OK] ALL TESTS PASSED!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
