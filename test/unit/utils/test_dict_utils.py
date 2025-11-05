"""
Tests for src/utils/dict_utils.py

Comprehensive test coverage for all dictionary utility functions.
"""

import pytest
import logging
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


# ==================== safe_get Tests ====================

def test_safe_get_existing_key():
    """Test safe_get with existing key"""
    d = {'name': 'test', 'count': 5}
    assert safe_get(d, 'name') == 'test'
    assert safe_get(d, 'count') == 5


def test_safe_get_missing_key_with_default():
    """Test safe_get with missing key returns default"""
    d = {'name': 'test'}
    assert safe_get(d, 'missing', default='default') == 'default'
    assert safe_get(d, 'missing', default=0) == 0


def test_safe_get_missing_key_no_default():
    """Test safe_get with missing key and no default returns None"""
    d = {'name': 'test'}
    assert safe_get(d, 'missing') is None


def test_safe_get_with_logger_warning(caplog):
    """Test safe_get logs warning when warn_missing=True"""
    d = {'name': 'test'}
    logger = logging.getLogger('test_dict_utils')

    with caplog.at_level(logging.WARNING):
        result = safe_get(d, 'missing', default='default', logger=logger, warn_missing=True)

    assert result == 'default'
    assert "Key 'missing' not found" in caplog.text


def test_safe_get_no_warning_when_key_exists(caplog):
    """Test safe_get doesn't log when key exists"""
    d = {'name': 'test'}
    logger = logging.getLogger('test_dict_utils')

    with caplog.at_level(logging.WARNING):
        result = safe_get(d, 'name', logger=logger, warn_missing=True)

    assert result == 'test'
    assert len(caplog.records) == 0


# ==================== normalize_to_list Tests ====================

def test_normalize_to_list_none():
    """Test normalize_to_list with None returns empty list"""
    assert normalize_to_list(None) == []


def test_normalize_to_list_empty_string():
    """Test normalize_to_list with empty string returns empty list"""
    assert normalize_to_list('') == []


def test_normalize_to_list_empty_list():
    """Test normalize_to_list with empty list returns empty list"""
    assert normalize_to_list([]) == []


def test_normalize_to_list_single_string():
    """Test normalize_to_list with single string returns list with one item"""
    assert normalize_to_list('product') == ['product']


def test_normalize_to_list_single_number():
    """Test normalize_to_list with single number returns list with one item"""
    assert normalize_to_list(42) == [42]


def test_normalize_to_list_already_list():
    """Test normalize_to_list with list returns same list"""
    items = ['product', 'date']
    result = normalize_to_list(items)
    assert result == ['product', 'date']
    assert result is items  # Should be same object


def test_normalize_to_list_none_to_none():
    """Test normalize_to_list with None and to_none=True returns None"""
    assert normalize_to_list(None, to_none=True) is None


def test_normalize_to_list_empty_string_to_none():
    """Test normalize_to_list with empty string and to_none=True returns None"""
    assert normalize_to_list('', to_none=True) is None


def test_normalize_to_list_empty_list_to_none():
    """Test normalize_to_list with empty list and to_none=True returns None"""
    assert normalize_to_list([], to_none=True) is None


def test_normalize_to_list_value_with_to_none():
    """Test normalize_to_list with value and to_none=True returns list"""
    assert normalize_to_list('product', to_none=True) == ['product']


def test_normalize_to_list_custom_empty_indicators():
    """Test normalize_to_list with custom empty indicators"""
    assert normalize_to_list(0, empty_indicators=[0, -1]) == []
    assert normalize_to_list(-1, empty_indicators=[0, -1]) == []
    assert normalize_to_list(1, empty_indicators=[0, -1]) == [1]


def test_normalize_to_list_executor_pattern():
    """Test normalize_to_list matches executor.py pattern (to_none=True)"""
    # executor.py:93-96 pattern
    group_by = normalize_to_list('', to_none=True)
    assert group_by is None

    group_by = normalize_to_list([], to_none=True)
    assert group_by is None

    group_by = normalize_to_list('product', to_none=True)
    assert group_by == ['product']


def test_normalize_to_list_resolver_pattern():
    """Test normalize_to_list matches resolver.py pattern (to_none=False)"""
    # resolver.py:68-71 pattern
    group_by = normalize_to_list(None)
    assert group_by == []

    group_by = normalize_to_list('')
    assert group_by == []

    group_by = normalize_to_list('product')
    assert group_by == ['product']

    group_by = normalize_to_list(['product', 'date'])
    assert group_by == ['product', 'date']


# ==================== merge_dicts Tests ====================

def test_merge_dicts_no_mutation():
    """Test merge_dicts doesn't mutate base when mutate=False"""
    base = {'a': 1, 'b': 2}
    updates = {'b': 3, 'c': 4}

    result = merge_dicts(base, updates, mutate=False)

    assert result == {'a': 1, 'b': 3, 'c': 4}
    assert base == {'a': 1, 'b': 2}  # Unchanged


def test_merge_dicts_with_mutation():
    """Test merge_dicts mutates base when mutate=True"""
    base = {'a': 1, 'b': 2}
    updates = {'b': 3, 'c': 4}

    result = merge_dicts(base, updates, mutate=True)

    assert result == {'a': 1, 'b': 3, 'c': 4}
    assert base == {'a': 1, 'b': 3, 'c': 4}  # Modified
    assert result is base  # Same object


def test_merge_dicts_empty_updates():
    """Test merge_dicts with empty updates"""
    base = {'a': 1, 'b': 2}
    result = merge_dicts(base, {}, mutate=False)
    assert result == {'a': 1, 'b': 2}


# ==================== get_nested Tests ====================

def test_get_nested_single_level():
    """Test get_nested with single level"""
    d = {'name': 'test', 'count': 5}
    assert get_nested(d, 'name') == 'test'
    assert get_nested(d, 'count') == 5


def test_get_nested_multiple_levels():
    """Test get_nested with multiple levels"""
    d = {'model': {'name': 'test', 'params': {'lr': 0.01, 'epochs': 10}}}
    assert get_nested(d, 'model', 'name') == 'test'
    assert get_nested(d, 'model', 'params', 'lr') == 0.01
    assert get_nested(d, 'model', 'params', 'epochs') == 10


def test_get_nested_missing_key():
    """Test get_nested with missing key returns default"""
    d = {'model': {'name': 'test'}}
    assert get_nested(d, 'model', 'missing', default='default') == 'default'
    assert get_nested(d, 'missing', 'key', default=None) is None


def test_get_nested_non_dict_value():
    """Test get_nested returns default when encountering non-dict value"""
    d = {'model': 'simple_string'}
    assert get_nested(d, 'model', 'name', default='default') == 'default'


def test_get_nested_empty_keys():
    """Test get_nested with no keys returns the dict itself"""
    d = {'name': 'test'}
    assert get_nested(d) == d


# ==================== filter_dict_by_keys Tests ====================

def test_filter_dict_by_keys_safe_mode():
    """Test filter_dict_by_keys in safe mode"""
    d = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    result = filter_dict_by_keys(d, ['a', 'c'])
    assert result == {'a': 1, 'c': 3}


def test_filter_dict_by_keys_safe_mode_missing_keys():
    """Test filter_dict_by_keys in safe mode with missing keys"""
    d = {'a': 1, 'b': 2}
    result = filter_dict_by_keys(d, ['a', 'missing'], safe=True)
    assert result == {'a': 1}


def test_filter_dict_by_keys_unsafe_mode():
    """Test filter_dict_by_keys in unsafe mode raises KeyError"""
    d = {'a': 1, 'b': 2}

    with pytest.raises(KeyError):
        filter_dict_by_keys(d, ['a', 'missing'], safe=False)


def test_filter_dict_by_keys_empty_keys():
    """Test filter_dict_by_keys with empty key list"""
    d = {'a': 1, 'b': 2}
    result = filter_dict_by_keys(d, [])
    assert result == {}


# ==================== get_or_raise Tests ====================

def test_get_or_raise_existing_key():
    """Test get_or_raise with existing key"""
    d = {'name': 'test', 'count': 5}
    assert get_or_raise(d, 'name') == 'test'


def test_get_or_raise_missing_key_default_error():
    """Test get_or_raise with missing key raises KeyError"""
    d = {'name': 'test'}

    with pytest.raises(KeyError, match="Key 'missing' not found"):
        get_or_raise(d, 'missing')


def test_get_or_raise_missing_key_custom_error():
    """Test get_or_raise with custom error class"""
    d = {'name': 'test'}

    with pytest.raises(ValueError, match="Key 'missing' not found"):
        get_or_raise(d, 'missing', error_class=ValueError)


def test_get_or_raise_missing_key_custom_message():
    """Test get_or_raise with custom error message"""
    d = {'name': 'test'}

    with pytest.raises(KeyError, match="Config missing required key"):
        get_or_raise(d, 'missing', message="Config missing required key")


# ==================== has_all_keys Tests ====================

def test_has_all_keys_all_present():
    """Test has_all_keys returns True when all keys present"""
    d = {'name': 'test', 'version': 1, 'enabled': True}
    assert has_all_keys(d, ['name', 'version']) is True


def test_has_all_keys_missing_keys():
    """Test has_all_keys returns False when keys missing"""
    d = {'name': 'test', 'version': 1}
    assert has_all_keys(d, ['name', 'version', 'enabled']) is False


def test_has_all_keys_empty_required():
    """Test has_all_keys returns True for empty required list"""
    d = {'name': 'test'}
    assert has_all_keys(d, []) is True


def test_has_all_keys_empty_dict():
    """Test has_all_keys returns False for empty dict with required keys"""
    assert has_all_keys({}, ['name']) is False


# ==================== get_missing_keys Tests ====================

def test_get_missing_keys_none_missing():
    """Test get_missing_keys returns empty list when all present"""
    d = {'name': 'test', 'version': 1, 'enabled': True}
    assert get_missing_keys(d, ['name', 'version']) == []


def test_get_missing_keys_some_missing():
    """Test get_missing_keys returns list of missing keys"""
    d = {'name': 'test', 'version': 1}
    missing = get_missing_keys(d, ['name', 'version', 'enabled', 'config'])
    assert missing == ['enabled', 'config']


def test_get_missing_keys_all_missing():
    """Test get_missing_keys when all keys missing"""
    d = {'name': 'test'}
    missing = get_missing_keys(d, ['version', 'enabled'])
    assert missing == ['version', 'enabled']


def test_get_missing_keys_empty_required():
    """Test get_missing_keys returns empty list for empty required list"""
    d = {'name': 'test'}
    assert get_missing_keys(d, []) == []


# ==================== invert_dict Tests ====================

def test_invert_dict_simple():
    """Test invert_dict with simple mapping"""
    d = {'a': 1, 'b': 2, 'c': 3}
    result = invert_dict(d)
    assert result == {1: 'a', 2: 'b', 3: 'c'}


def test_invert_dict_non_unique_values():
    """Test invert_dict with non-unique values (last wins)"""
    d = {'a': 1, 'b': 1, 'c': 2}
    result = invert_dict(d)
    assert result[1] in ['a', 'b']  # Last one wins (order depends on dict iteration)
    assert result[2] == 'c'


def test_invert_dict_string_values():
    """Test invert_dict with string values"""
    d = {'product': 'col_1', 'date': 'col_2', 'amount': 'col_3'}
    result = invert_dict(d)
    assert result == {'col_1': 'product', 'col_2': 'date', 'col_3': 'amount'}


def test_invert_dict_empty():
    """Test invert_dict with empty dict"""
    assert invert_dict({}) == {}


# ==================== Integration Tests ====================

def test_normalize_and_safe_get_integration():
    """Test combining normalize_to_list with safe_get"""
    config = {'group_by': 'product', 'filters': []}

    # Pattern: get value and normalize
    group_by = normalize_to_list(safe_get(config, 'group_by'))
    assert group_by == ['product']

    filters = normalize_to_list(safe_get(config, 'filters'))
    assert filters == []

    missing = normalize_to_list(safe_get(config, 'missing', default=None))
    assert missing == []


def test_merge_and_filter_integration():
    """Test combining merge_dicts with filter_dict_by_keys"""
    base_config = {'name': 'model', 'version': 1, 'internal_flag': True}
    runtime_config = {'version': 2, 'debug': True}

    # Merge configs
    full_config = merge_dicts(base_config, runtime_config, mutate=False)

    # Filter to public keys only
    public_config = filter_dict_by_keys(full_config, ['name', 'version', 'debug'], safe=True)

    assert public_config == {'name': 'model', 'version': 2, 'debug': True}
    assert 'internal_flag' not in public_config


def test_nested_get_with_default_integration():
    """Test get_nested with safe_get pattern"""
    config = {
        'models': {
            'model1': {'group_by': 'product'},
            'model2': {}
        }
    }

    # Get nested value with fallback
    group_by1 = get_nested(config, 'models', 'model1', 'group_by', default=None)
    assert group_by1 == 'product'

    group_by2 = get_nested(config, 'models', 'model2', 'group_by', default=None)
    assert group_by2 is None

    # Normalize result
    normalized1 = normalize_to_list(group_by1)
    assert normalized1 == ['product']

    normalized2 = normalize_to_list(group_by2)
    assert normalized2 == []
