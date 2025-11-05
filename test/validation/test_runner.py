"""
Test Runner for Transaction Processor Coverage Testing
Runs test data through processor and validates coverage
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
import json
from datetime import datetime

from transaction_processor import process_transaction_data, ProcessingResult, ValidationIssue
from test_data_generator import generate_test_data


@dataclass
class TestResult:
    """Result of a single test case"""
    case_id: str
    expected_result: str
    actual_result: str
    passed: bool
    expected_issues: List[str]
    actual_issues: List[str]
    missing_issues: List[str]
    unexpected_issues: List[str]
    details: str = ""


class TestRunner:
    """
    Runs test cases and validates coverage
    """
    
    def __init__(self):
        self.test_results: List[TestResult] = []
        self.coverage_stats = {
            'validation_rules_triggered': set(),
            'validation_rules_expected': set(),
            'columns_tested': set()
        }
    
    def run_tests(self, test_df: pd.DataFrame) -> Dict:
        """
        Run all test cases
        
        Args:
            test_df: DataFrame with test data including _test_* columns
            
        Returns:
            Dict with comprehensive test results
        """
        print("="*80)
        print("RUNNING VALIDATION COVERAGE TESTS")
        print("="*80)
        
        # Extract test metadata
        test_metadata = test_df[[c for c in test_df.columns if c.startswith('test_')]].copy()
        
        # Get data without test columns
        data_columns = [c for c in test_df.columns if not c.startswith('test_')]
        test_data = test_df[data_columns].copy()
        
        print(f"\n📊 Test Setup:")
        print(f"   Total test cases: {len(test_df)}")
        print(f"   Expected PASS: {(test_metadata['test_expected_result'] == 'PASS').sum()}")
        print(f"   Expected REJECT: {(test_metadata['test_expected_result'] == 'REJECT').sum()}")
        print(f"   Expected WARNING: {(test_metadata['test_expected_result'] == 'WARNING').sum()}")
        
        # Run through processor
        print(f"\n🔄 Processing test data...\n")
        result = process_transaction_data(test_data)
        
        # Analyze results
        print(f"\n📈 Analyzing results...")
        self._analyze_results(test_df, test_metadata, result)
        
        # Generate coverage report
        print(f"\n📊 Generating coverage report...")
        coverage_report = self._generate_coverage_report()
        
        # Print summary
        self._print_summary()
        
        return {
            'test_results': self.test_results,
            'coverage_report': coverage_report,
            'processing_result': result
        }
    
    def _analyze_results(self, test_df: pd.DataFrame, 
                        test_metadata: pd.DataFrame,
                        result: ProcessingResult):
        """Analyze test results against expectations"""
        
        # Create mapping of original row index to result
        clean_indices = set(result.clean_data.index) if len(result.clean_data) > 0 else set()
        rejected_indices = set(result.rejected_data['original_row_index']) if len(result.rejected_data) > 0 else set()
        
        # Create issue lookup by row
        issues_by_row = {}
        for issue in result.validation_issues:
            row_idx = issue.row_index
            if row_idx not in issues_by_row:
                issues_by_row[row_idx] = []
            issues_by_row[row_idx].append(issue.issue_type)
            
            # Track coverage
            self.coverage_stats['validation_rules_triggered'].add(issue.issue_type)
        
        # Analyze each test case
        for idx, row in test_df.iterrows():
            case_id = row['test_case_id']
            expected_result = row['test_expected_result']
            expected_issues = row['test_expected_issues'].split('|') if row['test_expected_issues'] else []
            
            # Track expected issues
            for issue in expected_issues:
                self.coverage_stats['validation_rules_expected'].add(issue)
            
            # Track columns tested
            category = row['test_category']
            if category not in ['Valid Baseline', 'Formula Validation', 'Edge Cases']:
                self.coverage_stats['columns_tested'].add(category)
            
            # Determine actual result
            if idx in clean_indices:
                actual_result = 'PASS'
                actual_issues = []
            elif idx in rejected_indices:
                actual_result = 'REJECT'
                actual_issues = issues_by_row.get(idx, [])
            else:
                actual_result = 'UNKNOWN'
                actual_issues = []
            
            # Compare expected vs actual issues
            expected_set = set(expected_issues)
            actual_set = set(actual_issues)
            
            missing_issues = list(expected_set - actual_set)
            unexpected_issues = list(actual_set - expected_set)
            
            # Determine if test passed
            # For PASS: should be in clean data with no issues
            # For REJECT: should be in rejected data with expected issues
            # For WARNING: more lenient - can be in either
            
            if expected_result == 'PASS':
                passed = (actual_result == 'PASS')
                details = ""
            elif expected_result == 'REJECT':
                # Must be rejected AND have at least one expected issue
                has_expected_issue = len(expected_set & actual_set) > 0 if expected_set else True
                passed = (actual_result == 'REJECT') and has_expected_issue
                
                if not passed:
                    if actual_result != 'REJECT':
                        details = f"Expected REJECT but got {actual_result}"
                    else:
                        details = f"Expected issues {expected_issues} but got {actual_issues}"
                else:
                    details = ""
            elif expected_result == 'WARNING':
                # Warnings might not reject the row
                passed = len(actual_issues) > 0  # At least flagged something
                details = ""
            else:
                passed = False
                details = f"Unknown expected result: {expected_result}"
            
            # Store result
            test_result = TestResult(
                case_id=case_id,
                expected_result=expected_result,
                actual_result=actual_result,
                passed=passed,
                expected_issues=expected_issues,
                actual_issues=actual_issues,
                missing_issues=missing_issues,
                unexpected_issues=unexpected_issues,
                details=details
            )
            
            self.test_results.append(test_result)
    
    def _generate_coverage_report(self) -> Dict:
        """Generate coverage report"""
        
        # Count results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for t in self.test_results if t.passed)
        failed_tests = total_tests - passed_tests
        
        # Group failures by reason
        failures_by_reason = {}
        for test in self.test_results:
            if not test.passed:
                reason = test.details if test.details else "Validation mismatch"
                failures_by_reason[reason] = failures_by_reason.get(reason, 0) + 1
        
        # Validation rule coverage
        expected_rules = self.coverage_stats['validation_rules_expected']
        triggered_rules = self.coverage_stats['validation_rules_triggered']
        missing_rules = expected_rules - triggered_rules
        unexpected_rules = triggered_rules - expected_rules
        
        # Column coverage
        all_columns = [
            'transaction_id', 'transaction_date', 'customer_id', 'product_sku',
            'quantity', 'unit_price', 'gross_amount', 'discount_amount',
            'net_amount', 'tax_amount', 'total_amount', 'payment_status',
            'payment_date', 'due_date'
        ]
        
        tested_columns = self.coverage_stats['columns_tested']
        untested_columns = set(all_columns) - tested_columns
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'pass_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            'validation_rule_coverage': {
                'expected_rules': sorted(list(expected_rules)),
                'triggered_rules': sorted(list(triggered_rules)),
                'missing_rules': sorted(list(missing_rules)),
                'unexpected_rules': sorted(list(unexpected_rules)),
                'coverage_rate': (len(triggered_rules) / len(expected_rules) * 100) 
                    if expected_rules else 100
            },
            'column_coverage': {
                'tested_columns': sorted(list(tested_columns)),
                'untested_columns': sorted(list(untested_columns)),
                'coverage_rate': (len(tested_columns) / len(all_columns) * 100)
            },
            'failures': failures_by_reason
        }
        
        return report
    
    def _print_summary(self):
        """Print test summary"""
        
        # Calculate stats
        total = len(self.test_results)
        passed = sum(1 for t in self.test_results if t.passed)
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print("\n" + "="*80)
        print("TEST RESULTS SUMMARY")
        print("="*80)
        
        print(f"\n🎯 Overall Results:")
        print(f"   Total tests: {total}")
        print(f"   ✅ Passed: {passed} ({pass_rate:.1f}%)")
        print(f"   ❌ Failed: {failed} ({100-pass_rate:.1f}%)")
        
        # Failed tests detail
        if failed > 0:
            print(f"\n❌ Failed Test Cases:")
            for test in self.test_results:
                if not test.passed:
                    print(f"   {test.case_id}: {test.details or 'Validation mismatch'}")
                    print(f"      Expected: {test.expected_result} with {test.expected_issues}")
                    print(f"      Actual: {test.actual_result} with {test.actual_issues}")
        
        # Validation rule coverage
        expected_rules = self.coverage_stats['validation_rules_expected']
        triggered_rules = self.coverage_stats['validation_rules_triggered']
        missing_rules = expected_rules - triggered_rules
        
        print(f"\n🔍 Validation Rule Coverage:")
        print(f"   Expected rules: {len(expected_rules)}")
        print(f"   Triggered rules: {len(triggered_rules)}")
        coverage = (len(triggered_rules) / len(expected_rules) * 100) if expected_rules else 100
        print(f"   Coverage: {coverage:.1f}%")
        
        if missing_rules:
            print(f"\n⚠️  Missing Rule Coverage:")
            for rule in sorted(missing_rules):
                print(f"   - {rule}")
        
        # Column coverage
        all_columns = [
            'transaction_id', 'transaction_date', 'customer_id', 'product_sku',
            'quantity', 'unit_price', 'gross_amount', 'discount_amount',
            'net_amount', 'tax_amount', 'total_amount', 'payment_status',
            'payment_date', 'due_date'
        ]
        tested = self.coverage_stats['columns_tested']
        untested = set(all_columns) - tested
        
        print(f"\n📋 Column Coverage:")
        print(f"   Tested columns: {len(tested)}/{len(all_columns)}")
        col_coverage = (len(tested) / len(all_columns) * 100)
        print(f"   Coverage: {col_coverage:.1f}%")
        
        if untested:
            print(f"\n⚠️  Untested Columns:")
            for col in sorted(untested):
                print(f"   - {col}")
        
        print("\n" + "="*80 + "\n")
    
    def export_results(self, 
                      results_json: str = 'test_results.json',
                      coverage_csv: str = 'test_coverage.csv'):
        """Export test results"""
        
        # Export detailed results
        results_data = []
        for test in self.test_results:
            results_data.append({
                'case_id': test.case_id,
                'expected_result': test.expected_result,
                'actual_result': test.actual_result,
                'passed': test.passed,
                'expected_issues': '|'.join(test.expected_issues),
                'actual_issues': '|'.join(test.actual_issues),
                'missing_issues': '|'.join(test.missing_issues),
                'unexpected_issues': '|'.join(test.unexpected_issues),
                'details': test.details
            })
        
        results_df = pd.DataFrame(results_data)
        results_df.to_csv(coverage_csv, index=False)
        print(f"✅ Test results exported to: {coverage_csv}")
        
        # Export coverage report
        coverage_report = self._generate_coverage_report()
        coverage_report['timestamp'] = datetime.now().isoformat()
        
        with open(results_json, 'w') as f:
            json.dump(coverage_report, f, indent=2)
        print(f"✅ Coverage report exported to: {results_json}")
        
        return results_df, coverage_report


def run_coverage_tests(test_data_file: str = None) -> Dict:
    """
    Main function to run coverage tests
    
    Args:
        test_data_file: Optional CSV file with test data. If None, generates new test data.
        
    Returns:
        Dict with test results and coverage report
    """
    
    # Generate or load test data
    if test_data_file is None:
        print("Generating test data...")
        test_df, _ = generate_test_data(
            output_csv='test_transactions.csv',
            manifest_json='test_manifest.json'
        )
    else:
        print(f"Loading test data from {test_data_file}...")
        test_df = pd.read_csv(test_data_file)
    
    # Run tests
    runner = TestRunner()
    results = runner.run_tests(test_df)
    
    # Export results
    runner.export_results(
        results_json='test_results.json',
        coverage_csv='test_coverage.csv'
    )
    
    # Generate final recommendation
    coverage_report = results['coverage_report']
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    if coverage_report['summary']['pass_rate'] < 95:
        print("\n⚠️  Test pass rate below 95% - review failed tests")
    else:
        print("\n✅ Test pass rate acceptable")
    
    if coverage_report['validation_rule_coverage']['coverage_rate'] < 100:
        print("\n⚠️  Not all validation rules covered - add more test cases")
        missing = coverage_report['validation_rule_coverage']['missing_rules']
        print(f"   Missing coverage for: {', '.join(missing)}")
    else:
        print("\n✅ All validation rules covered")
    
    if coverage_report['column_coverage']['coverage_rate'] < 100:
        print("\n⚠️  Not all columns tested - add more test cases")
        untested = coverage_report['column_coverage']['untested_columns']
        print(f"   Untested columns: {', '.join(untested)}")
    else:
        print("\n✅ All columns tested")
    
    print("\n" + "="*80 + "\n")
    
    return results


if __name__ == "__main__":
    # Run coverage tests
    results = run_coverage_tests()
    
    # Access results
    test_results = results['test_results']
    coverage_report = results['coverage_report']
    processing_result = results['processing_result']
    
    print(f"✅ Coverage testing complete!")
    print(f"   Test pass rate: {coverage_report['summary']['pass_rate']:.1f}%")
    print(f"   Rule coverage: {coverage_report['validation_rule_coverage']['coverage_rate']:.1f}%")
    print(f"   Column coverage: {coverage_report['column_coverage']['coverage_rate']:.1f}%")
