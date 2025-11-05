"""
Simple test script for results.py (no pytest required)
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.results import (
    OperationResult,
    ModelOutput,
    GroupResult,
    LoadResult,
    SaveResult,
    ExecutionMetrics,
)


def test_operation_result():
    print("Testing OperationResult...")

    # Success case
    result = OperationResult(success=True, data={'count': 5})
    assert result.success is True
    assert result.data == {'count': 5}
    assert result.has_errors() is False

    # Add warning
    result.add_warning('Low memory')
    assert result.has_warnings() is True
    assert result.is_complete_success() is False  # Has warnings

    # Add error
    result.add_error('Critical error')
    assert result.success is False  # Auto-set to False
    assert result.has_errors() is True

    # to_dict
    dict_result = result.to_dict()
    assert 'success' in dict_result
    assert 'errors' in dict_result

    print("  [OK] OperationResult passed")


def test_model_output():
    print("Testing ModelOutput...")

    filters_df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    attrs_df = pd.DataFrame({'total': [10]})

    output = ModelOutput(
        model_name='daily_model',
        input_dataset_name='preprocessed',
        filters=filters_df,
        attrs=attrs_df,
        exec_fltrs=['margin', 'profit'],
        exec_attrs=['total_revenue']
    )

    assert output.model_name == 'daily_model'
    assert output.has_filters() is True
    assert output.has_attrs() is True
    assert output.filter_count() == 2
    assert output.attr_count() == 1
    assert output.total_features() == 3

    # to_dict for backward compatibility
    dict_output = output.to_dict()
    assert 'input_dataset_name' in dict_output
    assert 'filters' in dict_output
    assert 'attrs' in dict_output

    print("  [OK] ModelOutput passed")


def test_group_result():
    print("Testing GroupResult...")

    group_df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    agg = {'total_revenue': 1000, 'total_cost': 600}

    result = GroupResult(
        group_id='ProductA',
        data_in=group_df,
        agg_results=agg,
        filters_calculated=['margin'],
        attrs_calculated=['total_revenue', 'total_cost']
    )

    assert result.group_id == 'ProductA'
    assert result.row_count == 2  # Auto-set
    assert result.has_filters() is True
    assert result.has_attrs() is True

    # to_dict
    dict_result = result.to_dict()
    assert 'group_id' in dict_result
    assert 'agg_results' in dict_result

    print("  [OK] GroupResult passed")


def test_load_result():
    print("Testing LoadResult...")

    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})

    result = LoadResult(
        data=df,
        source='/path/to/data.csv',
        load_time=1.5
    )

    assert result.rows_loaded == 3  # Auto-set
    assert result.columns_loaded == 2  # Auto-set
    assert result.load_time == 1.5
    assert result.has_warnings() is False

    # With warnings
    result.warnings.append('Missing values detected')
    assert result.has_warnings() is True

    print("  [OK] LoadResult passed")


def test_save_result():
    print("Testing SaveResult...")

    result = SaveResult(
        path='/path/to/output.csv',
        rows_saved=1000,
        columns_saved=15,
        save_time=0.5,
        file_size_bytes=1024 * 1024  # 1 MB
    )

    assert result.rows_saved == 1000
    assert result.file_size_mb() == 1.0

    # Without file size
    result2 = SaveResult(path='/test.csv', rows_saved=10, columns_saved=5)
    assert result2.file_size_mb() is None

    print("  [OK] SaveResult passed")


def test_execution_metrics():
    print("Testing ExecutionMetrics...")

    start = datetime(2024, 1, 1, 10, 0, 0)
    end = datetime(2024, 1, 1, 10, 0, 5)

    metrics = ExecutionMetrics(
        operation='load_data',
        start_time=start
    )

    assert metrics.is_complete() is False

    metrics.complete(end_time=end)
    assert metrics.is_complete() is True
    assert metrics.duration_seconds == 5.0

    print("  [OK] ExecutionMetrics passed")


def test_backward_compatibility():
    """Test that ModelOutput.to_dict() matches executor.py structure"""
    print("Testing backward compatibility...")

    filters_df = pd.DataFrame({'a': [1]})
    attrs_df = pd.DataFrame({'total': [10]})

    output = ModelOutput(
        model_name='test_model',
        input_dataset_name='preprocessed',
        filters=filters_df,
        attrs=attrs_df,
        exec_fltrs=['filter1'],
        exec_attrs=['attr1'],
        metadata={'group_by': 'product'}
    )

    # Convert to dict (should match executor.py:64-71 structure)
    result_dict = output.to_dict()

    # Check all expected keys exist
    assert 'input_dataset_name' in result_dict
    assert 'filters' in result_dict
    assert 'attrs' in result_dict
    assert 'exec_fltrs' in result_dict
    assert 'exec_attrs' in result_dict
    assert 'config' in result_dict  # metadata mapped to config

    # Check values
    assert result_dict['input_dataset_name'] == 'preprocessed'
    assert result_dict['exec_fltrs'] == ['filter1']
    assert result_dict['config'] == {'group_by': 'product'}

    print("  [OK] backward compatibility passed")


def main():
    print("=" * 60)
    print("Running results.py tests...")
    print("=" * 60)

    try:
        test_operation_result()
        test_model_output()
        test_group_result()
        test_load_result()
        test_save_result()
        test_execution_metrics()
        test_backward_compatibility()

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
