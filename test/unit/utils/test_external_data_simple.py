"""
Simple test script for external_data.py (no pytest required)
"""

import sys
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.context import GabedaContext
from src.execution.external_data import ExternalDataManager, get_external_column_list


def test_get_external_column_list():
    print("Testing get_external_column_list...")

    cfg_model = {
        'ext_cols': {
            'list': ['product_category', 'supplier_region']
        }
    }

    ext_cols = get_external_column_list(cfg_model)
    assert ext_cols == ['product_category', 'supplier_region']

    # Empty case
    cfg_model2 = {}
    ext_cols2 = get_external_column_list(cfg_model2)
    assert ext_cols2 == []

    print("  [OK] get_external_column_list passed")


def test_validate_external_sources():
    print("Testing validate_external_sources...")

    ctx = GabedaContext(user_config={})

    # Add external dataset
    ext_df = pd.DataFrame({'product_id': [1, 2], 'category': ['A', 'B']})
    ctx.set_dataset('product_master', ext_df)

    manager = ExternalDataManager(ctx)

    # Valid configuration
    cfg_model = {
        'external_data': {
            'products': {
                'source': 'product_master',
                'join_on': 'product_id',
                'columns': ['category']
            }
        }
    }

    result = manager.validate_external_sources(cfg_model)
    assert result.success is True

    # Invalid configuration (missing dataset)
    cfg_model2 = {
        'external_data': {
            'suppliers': {
                'source': 'supplier_master',  # Doesn't exist
                'join_on': 'supplier_id'
            }
        }
    }

    result2 = manager.validate_external_sources(cfg_model2)
    assert result2.success is False
    assert len(result2.errors) > 0

    print("  [OK] validate_external_sources passed")


def test_resolve_argument_source():
    print("Testing resolve_argument_source...")

    ctx = GabedaContext(user_config={})
    manager = ExternalDataManager(ctx)

    data_in = pd.DataFrame({'in_price': [100, 150], 'in_cost': [60, 90]})
    agg_results = {'total_revenue': 1000, 'total_cost': 600}
    ext_cols_list = ['product_category']

    # Priority 1: agg_results
    value, source = manager.resolve_argument_source(
        'total_revenue', data_in, agg_results, ext_cols_list
    )
    assert value == 1000
    assert source == 'agg_results'

    # Priority 3: data_in
    value, source = manager.resolve_argument_source(
        'in_price', data_in, agg_results, ext_cols_list
    )
    assert len(value) == 2  # Array from DataFrame column
    assert source == 'data_in'

    # Not found
    try:
        manager.resolve_argument_source(
            'missing_col', data_in, agg_results, ext_cols_list
        )
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert 'not found' in str(e)

    print("  [OK] resolve_argument_source passed")


def test_prepare_external_data():
    print("Testing prepare_external_data...")

    ctx = GabedaContext(user_config={})

    # Add external datasets
    product_df = pd.DataFrame({'product_id': [1, 2], 'category': ['A', 'B']})
    supplier_df = pd.DataFrame({'supplier_id': [1, 2], 'region': ['North', 'South']})

    ctx.set_dataset('product_master', product_df)
    ctx.set_dataset('supplier_master', supplier_df)

    manager = ExternalDataManager(ctx)

    cfg_model = {
        'external_data': {
            'products': {'source': 'product_master'},
            'suppliers': {'source': 'supplier_master'}
        }
    }

    ext_data = manager.prepare_external_data(cfg_model)

    assert 'products' in ext_data
    assert 'suppliers' in ext_data
    assert len(ext_data['products']) == 2
    assert len(ext_data['suppliers']) == 2

    print("  [OK] prepare_external_data passed")


def main():
    print("=" * 60)
    print("Running external_data tests...")
    print("=" * 60)

    try:
        test_get_external_column_list()
        test_validate_external_sources()
        test_resolve_argument_source()
        test_prepare_external_data()

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
