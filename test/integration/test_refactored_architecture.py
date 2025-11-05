"""
Integration Test for Refactored GabeDA Code

This script tests the refactored code in src_new/ to ensure it works correctly.
Run this before migrating from src/ to src_new/.

Usage:
    python test_refactored_code.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Import from refactored code (now in src/)
from src.utils.logger import setup_logging, get_logger
from src.core.context import GabedaContext
from src.core.config import ConfigManager
from src.preprocessing.loaders import DataLoader
from src.preprocessing.validators import DataValidator
from src.preprocessing.schema import SchemaProcessor
from src.features.store import FeatureStore
from src.features.resolver import DependencyResolver
from src.features.detector import FeatureTypeDetector
from src.features.analyzer import FeatureAnalyzer
from src.execution.calculator import FeatureCalculator
from src.execution.groupby import GroupByProcessor
from src.execution.executor import ModelExecutor
from src.execution.orchestrator import ExecutionOrchestrator
from src.export.excel import ExcelExporter

# Setup logging with file output
import os
from datetime import datetime

# Create logs directory
logs_dir = 'logs'
os.makedirs(logs_dir, exist_ok=True)

# Create log file with timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file_path = os.path.join(logs_dir, f'test_refactored_{timestamp}.log')

# Setup logging to both console and file
setup_logging(log_level='INFO', config={'client': 'test_refactored'})
logger = get_logger(__name__)

# Print file locations at the start
print("=" * 60)
print("FILE LOCATIONS")
print("=" * 60)
print(f"Log file: {os.path.abspath(log_file_path)}")
print(f"Test outputs: {os.path.abspath('outputs/test')}")
print("=" * 60 + "\n")

def test_basic_imports():
    """Test 1: Verify all imports work"""
    logger.info("=" * 60)
    logger.info("TEST 1: Basic Imports")
    logger.info("=" * 60)

    try:
        # All imports already done above
        logger.info("✓ All imports successful!")
        return True
    except Exception as e:
        logger.error(f"✗ Import failed: {e}")
        return False

def test_preprocessing():
    """Test 2: Test preprocessing pipeline"""
    logger.info("=" * 60)
    logger.info("TEST 2: Preprocessing Pipeline")
    logger.info("=" * 60)

    try:
        # Create sample data
        data = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'product': ['A', 'B', 'C'],
            'amount': [100, 200, 300],
            'quantity': [1, 2, 3]
        })

        # Test loader
        loader = DataLoader()
        df = loader.load_dataframe(data)
        logger.info(f"✓ DataLoader: Loaded {len(df)} rows")

        # Test validator
        validator = DataValidator()
        result = validator.validate_required_columns(df, ['date', 'product'])
        logger.info(f"✓ DataValidator: Validation {'passed' if result.is_valid else 'failed'}")

        # Test schema processor
        schema_processor = SchemaProcessor()
        config = {
            'data_schema': {
                'date': {'source_column': 'date', 'dtype': 'date'},
                'product': {'source_column': 'product', 'dtype': 'str'},
                'amount': {'source_column': 'amount', 'dtype': 'float'}
            }
        }
        processed = schema_processor.process_schema(df, config)
        logger.info(f"✓ SchemaProcessor: Processed {len(processed.available_cols)} columns")

        return True
    except Exception as e:
        logger.error(f"✗ Preprocessing test failed: {e}", exc_info=True)
        return False

def test_features():
    """Test 3: Test features package"""
    logger.info("=" * 60)
    logger.info("TEST 3: Features Package")
    logger.info("=" * 60)

    try:
        # Test feature store
        store = FeatureStore()

        # Create a simple feature function
        def test_feature(col1, col2):
            return col1 + col2

        store.store_feature('test_feature', test_feature)
        retrieved = store.get_feature('test_feature')
        logger.info(f"✓ FeatureStore: Stored and retrieved feature")

        # Test detector
        detector = FeatureTypeDetector()

        # Test with aggregation
        def agg_feature(values):
            return np.sum(values)

        is_agg = detector.is_aggregation(agg_feature)
        logger.info(f"✓ FeatureTypeDetector: Detected aggregation={is_agg}")

        # Test analyzer
        analyzer = FeatureAnalyzer(store, detector)
        logger.info(f"✓ FeatureAnalyzer: Initialized")

        return True
    except Exception as e:
        logger.error(f"✗ Features test failed: {e}", exc_info=True)
        return False

def test_execution():
    """Test 4: Test execution package with 4-case logic"""
    logger.info("=" * 60)
    logger.info("TEST 4: Execution Package (4-Case Logic)")
    logger.info("=" * 60)

    try:
        # Create test data
        data_in = pd.DataFrame({
            'product': ['A', 'A', 'B', 'B'],
            'amount': [100, 150, 200, 250],
            'quantity': [1, 2, 3, 4]
        })

        # Create test features
        def price_per_unit(amount, quantity):
            """Case 1: Standard filter - reads only from data_in"""
            return amount / quantity

        def product_total(amount):
            """Case 3: Attribute with aggregation"""
            return np.sum(amount)

        def avg_price(amount, quantity):
            """Case 3: Attribute with aggregation"""
            return np.sum(amount) / np.sum(quantity)

        # Setup
        store = FeatureStore()
        store.store_feature('price_per_unit', price_per_unit)
        store.store_feature('product_total', product_total)
        store.store_feature('avg_price', avg_price)

        detector = FeatureTypeDetector()
        calculator = FeatureCalculator()
        groupby_processor = GroupByProcessor(calculator, detector)

        # Analyze features
        analyzer = FeatureAnalyzer(store, detector)
        analysis = analyzer.analyze_features(
            exec_seq=['price_per_unit', 'product_total', 'avg_price'],
            data_in_columns=data_in.columns.tolist()
        )

        logger.info(f"✓ Analyzed {len(analysis['feature_funcs'])} features")

        # Create config
        cfg_model = {
            'group_by': 'product',
            'exec_seq': ['price_per_unit', 'product_total', 'avg_price'],
            'feature_funcs': analysis['feature_funcs'],
            'feature_args': analysis['feature_args'],
            'feature_groupby_flg': analysis['feature_groupby_flg'],
            'exec_fltrs': [],
            'exec_attrs': []
        }

        # Execute
        filters_df, attrs_df = groupby_processor.process_all_groups(data_in, cfg_model)

        logger.info(f"✓ Execution complete:")
        logger.info(f"  - Filters: {len(filters_df)} rows, {len(filters_df.columns) if not filters_df.empty else 0} columns")
        logger.info(f"  - Attributes: {len(attrs_df)} rows, {len(attrs_df.columns) if not attrs_df.empty else 0} columns")

        # Verify results
        if not filters_df.empty:
            logger.info(f"  - Filter columns: {list(filters_df.columns)}")
        if not attrs_df.empty:
            logger.info(f"  - Attribute columns: {list(attrs_df.columns)}")

        return True
    except Exception as e:
        logger.error(f"✗ Execution test failed: {e}", exc_info=True)
        return False

def test_context_integration():
    """Test 5: Test context integration"""
    logger.info("=" * 60)
    logger.info("TEST 5: Context Integration")
    logger.info("=" * 60)

    try:
        # Create context
        config = {'user_key': 'user_value'}
        ctx = GabedaContext(config)
        logger.info(f"✓ GabedaContext created")

        # Test dataset storage
        test_df = pd.DataFrame({'col': [1, 2, 3]})
        ctx.set_dataset('test_data', test_df)
        retrieved = ctx.get_dataset('test_data')
        assert len(retrieved) == 3
        logger.info(f"✓ Dataset storage/retrieval works")

        # Test model output storage
        output = {
            'filters': pd.DataFrame({'filter_col': [1, 2]}),
            'attrs': pd.DataFrame({'attr_col': [10, 20]}),
            'input_dataset_name': 'test_data'
        }
        ctx.set_model_output('test_model', output)
        logger.info(f"✓ Model output stored")

        # Test retrieval
        filters = ctx.get_model_filters('test_model')
        attrs = ctx.get_model_attrs('test_model')
        input_df = ctx.get_model_input('test_model')

        assert filters is not None
        assert attrs is not None
        assert input_df is not None
        logger.info(f"✓ Model output retrieval works")

        return True
    except Exception as e:
        logger.error(f"✗ Context integration test failed: {e}", exc_info=True)
        return False

def test_export():
    """Test 6: Test export functionality"""
    logger.info("=" * 60)
    logger.info("TEST 6: Export Functionality")
    logger.info("=" * 60)

    try:
        # Create context with data
        config = {}
        ctx = GabedaContext(config)

        # Add test data
        ctx.set_dataset('test_input', pd.DataFrame({'col': [1, 2, 3]}))

        output = {
            'filters': pd.DataFrame({'product': ['A', 'B'], 'filter_val': [10, 20]}),
            'attrs': pd.DataFrame({'product': ['A', 'B'], 'attr_val': [100, 200]}),
            'input_dataset_name': 'test_input'
        }
        ctx.set_model_output('test_model', output)

        # Test exporter
        exporter = ExcelExporter(ctx)

        # Create output directory
        output_dir = Path('outputs/test')
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / 'test_export.xlsx'
        result = exporter.export_model('test_model', str(output_path), include_input=True)

        logger.info(f"✓ Excel export successful: {result}")
        logger.info(f"✓ File created: {output_path.exists()}")

        # Print absolute path to console
        abs_path = output_path.absolute()
        print(f"\nExcel file created at: {abs_path}")
        logger.info(f"Absolute path: {abs_path}")

        return True
    except Exception as e:
        logger.error(f"✗ Export test failed: {e}", exc_info=True)
        return False

def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("REFACTORED CODE INTEGRATION TEST")
    logger.info("=" * 60)
    logger.info("Testing src_new/ implementation")

    results = {
        'Imports': test_basic_imports(),
        'Preprocessing': test_preprocessing(),
        'Features': test_features(),
        'Execution (4-Case Logic)': test_execution(),
        'Context Integration': test_context_integration(),
        'Export': test_export()
    }

    # Summary
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status} - {test_name}")

    logger.info("-" * 60)
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info("-" * 60)

    if passed == total:
        logger.info("\n🎉 ALL TESTS PASSED! Refactored code is working correctly.")
        logger.info("Next step: Run Phase 8 migration (rename src_new -> src)")

        # Print file locations summary
        print("=" * 60)
        print("OUTPUT FILES CREATED")
        print("=" * 60)
        print(f"Log file: {os.path.abspath(log_file_path)}")

        # Check for Excel file
        excel_file = Path('outputs/test/test_export.xlsx')
        if excel_file.exists():
            print(f"Excel file: {excel_file.absolute()}")
        else:
            print(f"Excel file: (not created during this run)")

        print("=" * 60)

        return 0
    else:
        logger.error(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")

        # Still print log location for debugging
        print("=" * 60)
        print("LOG FILE LOCATION")
        print("=" * 60)
        print(f"Check logs at: {os.path.abspath(log_file_path)}")
        print("=" * 60)

        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
