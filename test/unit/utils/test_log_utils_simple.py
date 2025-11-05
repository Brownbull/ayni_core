"""
Simple test script for log_utils (no pytest required)
"""

import sys
import logging
from pathlib import Path
import pandas as pd
from io import StringIO

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.log_utils import (
    log_operation_start,
    log_operation_complete,
    log_validation_result,
    log_data_shape,
    log_missing_column,
    log_dependency_chain,
    log_feature_execution,
    log_file_operation,
    log_count_summary,
    log_model_execution,
    log_progress,
    STATUS_SUCCESS,
    STATUS_WARNING,
    STATUS_ERROR,
)


def setup_test_logger():
    """Create a logger that captures output"""
    logger = logging.getLogger('test_log_utils')
    logger.setLevel(logging.DEBUG)
    logger.handlers = []  # Clear existing handlers

    # Create string buffer handler
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger, log_stream


def get_log_output(log_stream):
    """Get current log output and reset"""
    output = log_stream.getvalue()
    log_stream.truncate(0)
    log_stream.seek(0)
    return output


def test_log_operation_start():
    print("Testing log_operation_start...")

    logger, log_stream = setup_test_logger()

    # Without context
    log_operation_start(logger, 'Loading data')
    output = get_log_output(log_stream)
    assert 'Loading data...' in output

    # With context
    log_operation_start(logger, 'Processing', file_path='/test.csv', model='model1')
    output = get_log_output(log_stream)
    assert 'Processing...' in output
    assert 'file_path=/test.csv' in output
    assert 'model=model1' in output

    print("  [OK] log_operation_start passed")


def test_log_operation_complete():
    print("Testing log_operation_complete...")

    logger, log_stream = setup_test_logger()

    # Success
    log_operation_complete(logger, 'Data validation', status='success')
    output = get_log_output(log_stream)
    assert STATUS_SUCCESS in output
    assert 'Data validation complete' in output

    # Warning
    log_operation_complete(logger, 'Processing', status='warning', count=5)
    output = get_log_output(log_stream)
    assert STATUS_WARNING in output
    assert 'count=5' in output

    # Error
    log_operation_complete(logger, 'Failed operation', status='error')
    output = get_log_output(log_stream)
    assert STATUS_ERROR in output

    print("  [OK] log_operation_complete passed")


def test_log_validation_result():
    print("Testing log_validation_result...")

    logger, log_stream = setup_test_logger()

    # Valid
    log_validation_result(logger, True, 'Required columns')
    output = get_log_output(log_stream)
    assert STATUS_SUCCESS in output
    assert 'validation passed' in output

    # Invalid with errors
    log_validation_result(logger, False, 'Data quality', errors=['Error 1', 'Error 2'])
    output = get_log_output(log_stream)
    assert STATUS_ERROR in output
    assert 'validation failed' in output
    assert 'Error 1' in output
    assert 'Error 2' in output

    # With warnings
    log_validation_result(logger, True, 'Optional fields', warnings=['Warning 1'])
    output = get_log_output(log_stream)
    assert 'Warning 1' in output

    print("  [OK] log_validation_result passed")


def test_log_data_shape():
    print("Testing log_data_shape...")

    logger, log_stream = setup_test_logger()

    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})

    log_data_shape(logger, 'test_data', df, action='Loaded')
    output = get_log_output(log_stream)
    assert 'Loaded test_data' in output
    assert '3 rows' in output
    assert '2 columns' in output

    log_data_shape(logger, 'filtered', df, action='Created')
    output = get_log_output(log_stream)
    assert 'Created filtered' in output

    print("  [OK] log_data_shape passed")


def test_log_missing_column():
    print("Testing log_missing_column...")

    logger, log_stream = setup_test_logger()

    # Without available columns
    log_missing_column(logger, 'missing_col', severity='error')
    output = get_log_output(log_stream)
    assert "Column 'missing_col' not found" in output
    assert STATUS_ERROR in output

    # With available columns
    log_missing_column(logger, 'col', available=['a', 'b', 'c'], severity='warning')
    output = get_log_output(log_stream)
    assert STATUS_WARNING in output
    assert 'Available columns' in output

    print("  [OK] log_missing_column passed")


def test_log_dependency_chain():
    print("Testing log_dependency_chain...")

    logger, log_stream = setup_test_logger()

    log_dependency_chain(logger, 'profit_margin', ['total_revenue', 'total_cost'])
    output = get_log_output(log_stream)
    assert 'Resolved profit_margin' in output
    assert 'total_revenue' in output
    assert 'total_cost' in output

    # No dependencies
    log_dependency_chain(logger, 'basic_feature', [])
    output = get_log_output(log_stream)
    assert 'no dependencies' in output

    print("  [OK] log_dependency_chain passed")


def test_log_feature_execution():
    print("Testing log_feature_execution...")

    logger, log_stream = setup_test_logger()

    log_feature_execution(logger, 'margin_unit', 'filter', args_count=2)
    output = get_log_output(log_stream)
    assert 'Executing filter' in output
    assert 'margin_unit' in output
    assert '2 args' in output

    log_feature_execution(logger, 'total_revenue', 'attribute')
    output = get_log_output(log_stream)
    assert 'Executing attribute' in output

    print("  [OK] log_feature_execution passed")


def test_log_file_operation():
    print("Testing log_file_operation...")

    logger, log_stream = setup_test_logger()

    log_file_operation(logger, 'Saved', '/path/to/file.csv', status='success')
    output = get_log_output(log_stream)
    assert STATUS_SUCCESS in output
    assert 'Saved' in output
    assert '/path/to/file.csv' in output

    log_file_operation(logger, 'Failed to load', '/path', status='error')
    output = get_log_output(log_stream)
    assert STATUS_ERROR in output

    print("  [OK] log_file_operation passed")


def test_log_count_summary():
    print("Testing log_count_summary...")

    logger, log_stream = setup_test_logger()

    # With items list
    log_count_summary(logger, 'models', 3, items=['model1', 'model2', 'model3'])
    output = get_log_output(log_stream)
    assert 'Found 3 models' in output
    assert 'model1' in output

    # Without items
    log_count_summary(logger, 'errors', 15)
    output = get_log_output(log_stream)
    assert 'Found 15 errors' in output

    # Too many items (truncate)
    many_items = [f'item{i}' for i in range(20)]
    log_count_summary(logger, 'items', 20, items=many_items, max_items=5)
    output = get_log_output(log_stream)
    assert '15 more' in output

    print("  [OK] log_count_summary passed")


def test_log_model_execution():
    print("Testing log_model_execution...")

    logger, log_stream = setup_test_logger()

    log_model_execution(logger, 'model1', action='Executing', input_dataset='preprocessed')
    output = get_log_output(log_stream)
    assert 'Executing Model: model1' in output
    assert 'Input dataset: preprocessed' in output

    log_model_execution(logger, 'model1', action='Completed')
    output = get_log_output(log_stream)
    assert 'Completed Model: model1' in output

    print("  [OK] log_model_execution passed")


def test_log_progress():
    print("Testing log_progress...")

    logger, log_stream = setup_test_logger()

    log_progress(logger, 5, 10, item_name='model')
    output = get_log_output(log_stream)
    assert 'Processing model 5/10' in output

    log_progress(logger, 100, 100, item_name='row')
    output = get_log_output(log_stream)
    assert 'Processing row 100/100' in output

    print("  [OK] log_progress passed")


def test_status_constants():
    print("Testing status constants...")

    assert STATUS_SUCCESS == '[OK]'
    assert STATUS_WARNING == '[WARN]'
    assert STATUS_ERROR == '[FAIL]'

    print("  [OK] status constants passed")


def test_validators_pattern():
    """Test patterns from validators.py"""
    print("Testing validators.py patterns...")

    logger, log_stream = setup_test_logger()

    # OLD: logger.info(f"✓ All required columns present: {required}")
    # NEW:
    required = ['col1', 'col2']
    log_validation_result(logger, True, f'All required columns present: {required}')
    output = get_log_output(log_stream)
    assert STATUS_SUCCESS in output
    assert 'validation passed' in output

    # OLD: logger.error(f"✗ {error_msg}")
    # NEW:
    log_validation_result(logger, False, 'Required columns', errors=['Missing col1'])
    output = get_log_output(log_stream)
    assert STATUS_ERROR in output
    assert 'Missing col1' in output

    print("  [OK] validators.py patterns passed")


def test_loaders_pattern():
    """Test patterns from loaders.py"""
    print("Testing loaders.py patterns...")

    logger, log_stream = setup_test_logger()

    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})

    # OLD: logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    # NEW:
    log_data_shape(logger, 'data.csv', df, action='Loaded')
    output = get_log_output(log_stream)
    assert '3 rows' in output
    assert '2 columns' in output

    print("  [OK] loaders.py patterns passed")


def test_excel_pattern():
    """Test patterns from excel.py"""
    print("Testing excel.py patterns...")

    logger, log_stream = setup_test_logger()

    # OLD: logger.info(f"✓ Excel file saved: {output_path}")
    # NEW:
    log_operation_complete(logger, 'Excel file saved', status='success', path='/out/test.xlsx')
    output = get_log_output(log_stream)
    assert STATUS_SUCCESS in output
    assert 'path=/out/test.xlsx' in output

    # OLD: logger.info(f"Found {len(model_names)} models to export: {model_names}")
    # NEW:
    model_names = ['model1', 'model2', 'model3']
    log_count_summary(logger, 'models to export', len(model_names), items=model_names)
    output = get_log_output(log_stream)
    assert 'Found 3 models to export' in output

    print("  [OK] excel.py patterns passed")


def main():
    print("=" * 60)
    print("Running log_utils tests...")
    print("=" * 60)

    try:
        test_log_operation_start()
        test_log_operation_complete()
        test_log_validation_result()
        test_log_data_shape()
        test_log_missing_column()
        test_log_dependency_chain()
        test_log_feature_execution()
        test_log_file_operation()
        test_log_count_summary()
        test_log_model_execution()
        test_log_progress()
        test_status_constants()
        test_validators_pattern()
        test_loaders_pattern()
        test_excel_pattern()

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
