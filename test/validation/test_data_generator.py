"""
Test Data Generator for Transaction Processor Coverage Testing
Creates specific test cases to validate every validation rule
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from dataclasses import dataclass, field
import json


@dataclass
class TestCase:
    """Represents a single test case"""
    case_id: str
    category: str
    description: str
    expected_result: str  # 'PASS', 'REJECT', 'WARNING'
    expected_issues: List[str] = field(default_factory=list)
    data: Dict = field(default_factory=dict)


class TestDataGenerator:
    """
    Generates comprehensive test data covering all validation scenarios
    """
    
    def __init__(self, business_founding_date: str = '2020-01-01'):
        self.founding_date = pd.Timestamp(business_founding_date)
        self.today = pd.Timestamp.now()
        self.test_cases = []
        self.base_valid_transaction = self._get_base_valid_transaction()
        
    def _get_base_valid_transaction(self) -> Dict:
        """Get a baseline valid transaction"""
        txn_date = self.today - timedelta(days=30)
        return {
            'transaction_id': 'TXN-BASE-001',
            'transaction_date': txn_date,
            'customer_id': 'CUST-001',
            'product_sku': 'PROD-A001',
            'quantity': 10.0,
            'unit_price': 1000.0,
            'gross_amount': 10000.0,
            'discount_amount': 500.0,
            'net_amount': 9500.0,
            'tax_amount': 1805.0,  # 19% of net_amount
            'total_amount': 11305.0,
            'payment_status': 'PAID',
            'payment_date': txn_date + timedelta(days=5),
            'due_date': txn_date + timedelta(days=30),
            'transaction_type': 'SALE'
        }
    
    def generate_all_test_cases(self) -> pd.DataFrame:
        """Generate all test cases"""
        print("Generating comprehensive test cases...")
        
        # Reset test cases
        self.test_cases = []
        
        # Category 1: Valid baseline cases
        self._generate_valid_cases()
        
        # Category 2: transaction_id validation
        self._generate_transaction_id_tests()
        
        # Category 3: transaction_date validation
        self._generate_transaction_date_tests()
        
        # Category 4: customer_id validation
        self._generate_customer_id_tests()
        
        # Category 5: product_sku validation
        self._generate_product_sku_tests()
        
        # Category 6: quantity validation
        self._generate_quantity_tests()
        
        # Category 7: unit_price validation
        self._generate_unit_price_tests()
        
        # Category 8: gross_amount validation
        self._generate_gross_amount_tests()
        
        # Category 9: discount_amount validation
        self._generate_discount_amount_tests()
        
        # Category 10: net_amount validation
        self._generate_net_amount_tests()
        
        # Category 11: tax_amount validation
        self._generate_tax_amount_tests()
        
        # Category 12: total_amount validation
        self._generate_total_amount_tests()
        
        # Category 13: payment_status validation
        self._generate_payment_status_tests()
        
        # Category 14: payment_date validation
        self._generate_payment_date_tests()
        
        # Category 15: due_date validation
        self._generate_due_date_tests()
        
        # Category 16: Formula validation
        self._generate_formula_tests()
        
        # Category 17: Edge cases
        self._generate_edge_cases()
        
        # Convert to DataFrame
        df = self._test_cases_to_dataframe()
        
        print(f"✅ Generated {len(self.test_cases)} test cases")
        print(f"   - Expected PASS: {sum(1 for tc in self.test_cases if tc.expected_result == 'PASS')}")
        print(f"   - Expected REJECT: {sum(1 for tc in self.test_cases if tc.expected_result == 'REJECT')}")
        print(f"   - Expected WARNING: {sum(1 for tc in self.test_cases if tc.expected_result == 'WARNING')}")
        
        return df
    
    def _add_test_case(self, case_id: str, category: str, description: str,
                       expected_result: str, expected_issues: List[str],
                       modifications: Dict = None):
        """Add a test case with modifications to base transaction"""
        data = self.base_valid_transaction.copy()
        
        if modifications:
            data.update(modifications)
        
        self.test_cases.append(TestCase(
            case_id=case_id,
            category=category,
            description=description,
            expected_result=expected_result,
            expected_issues=expected_issues,
            data=data
        ))
    
    def _generate_valid_cases(self):
        """Generate valid baseline cases"""
        
        # Case 1: Perfect valid transaction
        self._add_test_case(
            'VALID-001',
            'Valid Baseline',
            'Perfect valid transaction with all fields',
            'PASS',
            []
        )
        
        # Case 2: Valid with no discount
        self._add_test_case(
            'VALID-002',
            'Valid Baseline',
            'Valid transaction without discount',
            'PASS',
            [],
            {
                'discount_amount': None,
                'net_amount': 10000.0,
                'tax_amount': 1900.0,
                'total_amount': 11900.0
            }
        )
        
        # Case 3: Valid with no tax
        self._add_test_case(
            'VALID-003',
            'Valid Baseline',
            'Valid transaction without tax',
            'PASS',
            [],
            {
                'tax_amount': None,
                'total_amount': 9500.0
            }
        )
        
        # Case 4: Valid with anonymous customer
        self._add_test_case(
            'VALID-004',
            'Valid Baseline',
            'Valid transaction with no customer_id',
            'PASS',
            [],
            {'customer_id': None}
        )
        
        # Case 5: Valid with no product SKU (service fee)
        self._add_test_case(
            'VALID-005',
            'Valid Baseline',
            'Valid transaction with no product_sku',
            'PASS',
            [],
            {'product_sku': None}
        )
        
        # Case 6: Valid decimal quantity
        self._add_test_case(
            'VALID-006',
            'Valid Baseline',
            'Valid transaction with decimal quantity',
            'PASS',
            [],
            {
                'quantity': 12.5,
                'gross_amount': 12500.0,
                'discount_amount': 625.0,
                'net_amount': 11875.0,
                'tax_amount': 2256.25,
                'total_amount': 14131.25
            }
        )
        
        # Case 7: Valid free item (zero price)
        self._add_test_case(
            'VALID-007',
            'Valid Baseline',
            'Valid free item with zero price',
            'PASS',
            [],
            {
                'unit_price': 0.0,
                'gross_amount': 0.0,
                'discount_amount': None,
                'net_amount': 0.0,
                'tax_amount': 0.0,
                'total_amount': 0.0
            }
        )
    
    def _generate_transaction_id_tests(self):
        """Test transaction_id validation"""
        
        # Null transaction_id
        self._add_test_case(
            'TXN_ID-001',
            'transaction_id',
            'Null transaction_id',
            'REJECT',
            ['NULL_IN_REQUIRED_FIELD'],
            {'transaction_id': None}
        )
        
        # Empty string
        self._add_test_case(
            'TXN_ID-002',
            'transaction_id',
            'Empty string transaction_id',
            'REJECT',
            ['NULL_IN_REQUIRED_FIELD'],
            {'transaction_id': ''}
        )
        
        # Valid alphanumeric
        self._add_test_case(
            'TXN_ID-003',
            'transaction_id',
            'Valid alphanumeric transaction_id',
            'PASS',
            [],
            {'transaction_id': 'INV-2024-12345'}
        )
        
        # Valid numeric
        self._add_test_case(
            'TXN_ID-004',
            'transaction_id',
            'Valid numeric transaction_id',
            'PASS',
            [],
            {'transaction_id': '123456789'}
        )
    
    def _generate_transaction_date_tests(self):
        """Test transaction_date validation"""
        
        # Null date
        self._add_test_case(
            'TXN_DATE-001',
            'transaction_date',
            'Null transaction_date',
            'REJECT',
            ['NULL_IN_REQUIRED_FIELD'],
            {'transaction_date': None}
        )
        
        # Future date
        self._add_test_case(
            'TXN_DATE-002',
            'transaction_date',
            'Future transaction_date',
            'REJECT',
            ['FUTURE_DATE'],
            {'transaction_date': self.today + timedelta(days=10)}
        )
        
        # Date before founding
        self._add_test_case(
            'TXN_DATE-003',
            'transaction_date',
            'Date before business founding',
            'REJECT',
            ['DATE_BEFORE_FOUNDING'],
            {
                'transaction_date': self.founding_date - timedelta(days=10),
                'payment_date': self.founding_date - timedelta(days=5)
            }
        )
        
        # Today's date (boundary)
        self._add_test_case(
            'TXN_DATE-004',
            'transaction_date',
            'Transaction today',
            'PASS',
            [],
            {
                'transaction_date': self.today,
                'payment_date': self.today,
                'due_date': self.today + timedelta(days=30)
            }
        )
        
        # Founding date (boundary)
        self._add_test_case(
            'TXN_DATE-005',
            'transaction_date',
            'Transaction on founding date',
            'PASS',
            [],
            {
                'transaction_date': self.founding_date,
                'payment_date': self.founding_date + timedelta(days=5),
                'due_date': self.founding_date + timedelta(days=30)
            }
        )
    
    def _generate_customer_id_tests(self):
        """Test customer_id validation"""
        
        # Null customer_id (valid for anonymous)
        self._add_test_case(
            'CUST_ID-001',
            'customer_id',
            'Null customer_id (anonymous)',
            'PASS',
            [],
            {'customer_id': None}
        )
        
        # Empty string (should convert to null)
        self._add_test_case(
            'CUST_ID-002',
            'customer_id',
            'Empty string customer_id',
            'PASS',
            [],
            {'customer_id': ''}
        )
        
        # Valid customer ID
        self._add_test_case(
            'CUST_ID-003',
            'customer_id',
            'Valid customer_id',
            'PASS',
            [],
            {'customer_id': 'CUST-12345'}
        )
        
        # Chilean RUT format
        self._add_test_case(
            'CUST_ID-004',
            'customer_id',
            'Chilean RUT format',
            'PASS',
            [],
            {'customer_id': '12345678-9'}
        )
    
    def _generate_product_sku_tests(self):
        """Test product_sku validation"""
        
        # Null SKU (valid for services)
        self._add_test_case(
            'SKU-001',
            'product_sku',
            'Null product_sku (service)',
            'PASS',
            [],
            {'product_sku': None}
        )
        
        # Empty string
        self._add_test_case(
            'SKU-002',
            'product_sku',
            'Empty string product_sku',
            'PASS',
            [],
            {'product_sku': ''}
        )
        
        # Valid SKU
        self._add_test_case(
            'SKU-003',
            'product_sku',
            'Valid product_sku',
            'PASS',
            [],
            {'product_sku': 'PROD-XYZ-789'}
        )
    
    def _generate_quantity_tests(self):
        """Test quantity validation"""
        
        # Null quantity
        self._add_test_case(
            'QTY-001',
            'quantity',
            'Null quantity',
            'REJECT',
            ['NULL_IN_REQUIRED_FIELD'],
            {'quantity': None}
        )
        
        # Zero quantity (boundary)
        self._add_test_case(
            'QTY-002',
            'quantity',
            'Zero quantity',
            'PASS',
            [],
            {
                'quantity': 0.0,
                'gross_amount': 0.0,
                'discount_amount': None,
                'net_amount': 0.0,
                'tax_amount': 0.0,
                'total_amount': 0.0
            }
        )
        
        # Negative quantity
        self._add_test_case(
            'QTY-003',
            'quantity',
            'Negative quantity',
            'REJECT',
            ['NEGATIVE_VALUE', 'BELOW_MINIMUM'],
            {
                'quantity': -5.0,
                'gross_amount': -5000.0,
                'net_amount': -5000.0,
                'total_amount': -5950.0
            }
        )
        
        # Very large quantity
        self._add_test_case(
            'QTY-004',
            'quantity',
            'Very large quantity',
            'PASS',
            [],
            {
                'quantity': 10000.0,
                'gross_amount': 10000000.0,
                'discount_amount': 500000.0,
                'net_amount': 9500000.0,
                'tax_amount': 1805000.0,
                'total_amount': 11305000.0
            }
        )
        
        # Decimal quantity
        self._add_test_case(
            'QTY-005',
            'quantity',
            'Decimal quantity (kg)',
            'PASS',
            [],
            {
                'quantity': 2.567,
                'gross_amount': 2567.0,
                'discount_amount': 128.35,
                'net_amount': 2438.65,
                'tax_amount': 463.34,
                'total_amount': 2901.99
            }
        )
    
    def _generate_unit_price_tests(self):
        """Test unit_price validation"""
        
        # Null price
        self._add_test_case(
            'PRICE-001',
            'unit_price',
            'Null unit_price',
            'REJECT',
            ['NULL_IN_REQUIRED_FIELD'],
            {'unit_price': None}
        )
        
        # Zero price (free item)
        self._add_test_case(
            'PRICE-002',
            'unit_price',
            'Zero unit_price (free item)',
            'PASS',
            [],
            {
                'unit_price': 0.0,
                'gross_amount': 0.0,
                'discount_amount': None,
                'net_amount': 0.0,
                'tax_amount': 0.0,
                'total_amount': 0.0
            }
        )
        
        # Negative price
        self._add_test_case(
            'PRICE-003',
            'unit_price',
            'Negative unit_price',
            'REJECT',
            ['NEGATIVE_VALUE', 'BELOW_MINIMUM'],
            {
                'unit_price': -100.0,
                'gross_amount': -1000.0,
                'net_amount': -1000.0,
                'total_amount': -1190.0
            }
        )
        
        # Very high price
        self._add_test_case(
            'PRICE-004',
            'unit_price',
            'Very high unit_price',
            'PASS',
            [],
            {
                'unit_price': 1000000.0,
                'gross_amount': 10000000.0,
                'discount_amount': 500000.0,
                'net_amount': 9500000.0,
                'tax_amount': 1805000.0,
                'total_amount': 11305000.0
            }
        )
    
    def _generate_gross_amount_tests(self):
        """Test gross_amount validation"""
        
        # Null gross_amount
        self._add_test_case(
            'GROSS-001',
            'gross_amount',
            'Null gross_amount',
            'REJECT',
            ['NULL_IN_REQUIRED_FIELD'],
            {'gross_amount': None}
        )
        
        # Negative gross_amount
        self._add_test_case(
            'GROSS-002',
            'gross_amount',
            'Negative gross_amount',
            'REJECT',
            ['NEGATIVE_VALUE', 'BELOW_MINIMUM'],
            {
                'gross_amount': -1000.0,
                'discount_amount': None,
                'net_amount': -1000.0,
                'tax_amount': -190.0,
                'total_amount': -1190.0
            }
        )
    
    def _generate_discount_amount_tests(self):
        """Test discount_amount validation"""
        
        # Null discount (no discount)
        self._add_test_case(
            'DISC-001',
            'discount_amount',
            'Null discount_amount (no discount)',
            'PASS',
            [],
            {
                'discount_amount': None,
                'net_amount': 10000.0,
                'tax_amount': 1900.0,
                'total_amount': 11900.0
            }
        )
        
        # Zero discount
        self._add_test_case(
            'DISC-002',
            'discount_amount',
            'Zero discount_amount',
            'PASS',
            [],
            {
                'discount_amount': 0.0,
                'net_amount': 10000.0,
                'tax_amount': 1900.0,
                'total_amount': 11900.0
            }
        )
        
        # Negative discount
        self._add_test_case(
            'DISC-003',
            'discount_amount',
            'Negative discount_amount',
            'REJECT',
            ['NEGATIVE_VALUE', 'BELOW_MINIMUM'],
            {'discount_amount': -100.0}
        )
        
        # Discount exceeds gross_amount
        self._add_test_case(
            'DISC-004',
            'discount_amount',
            'Discount exceeds gross_amount',
            'REJECT',
            ['EXCESSIVE_DISCOUNT'],
            {
                'discount_amount': 15000.0,
                'net_amount': -5000.0,
                'total_amount': -5950.0
            }
        )
        
        # 100% discount (boundary)
        self._add_test_case(
            'DISC-005',
            'discount_amount',
            '100% discount (free after discount)',
            'PASS',
            [],
            {
                'discount_amount': 10000.0,
                'net_amount': 0.0,
                'tax_amount': 0.0,
                'total_amount': 0.0
            }
        )
    
    def _generate_net_amount_tests(self):
        """Test net_amount validation"""
        
        # Null net_amount
        self._add_test_case(
            'NET-001',
            'net_amount',
            'Null net_amount',
            'REJECT',
            ['NULL_IN_REQUIRED_FIELD'],
            {'net_amount': None}
        )
        
        # Negative net_amount
        self._add_test_case(
            'NET-002',
            'net_amount',
            'Negative net_amount',
            'REJECT',
            ['NEGATIVE_VALUE', 'BELOW_MINIMUM'],
            {
                'net_amount': -100.0,
                'tax_amount': -19.0,
                'total_amount': -119.0
            }
        )
    
    def _generate_tax_amount_tests(self):
        """Test tax_amount validation"""
        
        # Null tax (no tax)
        self._add_test_case(
            'TAX-001',
            'tax_amount',
            'Null tax_amount (no tax)',
            'PASS',
            [],
            {
                'tax_amount': None,
                'total_amount': 9500.0
            }
        )
        
        # Zero tax
        self._add_test_case(
            'TAX-002',
            'tax_amount',
            'Zero tax_amount',
            'PASS',
            [],
            {
                'tax_amount': 0.0,
                'total_amount': 9500.0
            }
        )
        
        # Negative tax
        self._add_test_case(
            'TAX-003',
            'tax_amount',
            'Negative tax_amount',
            'REJECT',
            ['NEGATIVE_VALUE', 'BELOW_MINIMUM'],
            {'tax_amount': -100.0}
        )
        
        # 19% IVA (Chile standard)
        self._add_test_case(
            'TAX-004',
            'tax_amount',
            '19% IVA (Chile standard)',
            'PASS',
            [],
            {
                'net_amount': 10000.0,
                'tax_amount': 1900.0,
                'total_amount': 11900.0
            }
        )
    
    def _generate_total_amount_tests(self):
        """Test total_amount validation"""
        
        # Null total_amount
        self._add_test_case(
            'TOTAL-001',
            'total_amount',
            'Null total_amount',
            'REJECT',
            ['NULL_IN_REQUIRED_FIELD'],
            {'total_amount': None}
        )
        
        # Negative total_amount
        self._add_test_case(
            'TOTAL-002',
            'total_amount',
            'Negative total_amount',
            'REJECT',
            ['NEGATIVE_VALUE', 'BELOW_MINIMUM'],
            {'total_amount': -100.0}
        )
        
        # Zero total_amount (free transaction)
        self._add_test_case(
            'TOTAL-003',
            'total_amount',
            'Zero total_amount (free)',
            'PASS',
            [],
            {
                'quantity': 1.0,
                'unit_price': 0.0,
                'gross_amount': 0.0,
                'discount_amount': None,
                'net_amount': 0.0,
                'tax_amount': 0.0,
                'total_amount': 0.0
            }
        )
    
    def _generate_payment_status_tests(self):
        """Test payment_status validation"""
        
        # Valid statuses
        for status in ['PAID', 'PENDING', 'OVERDUE', 'PARTIAL', 'CANCELLED']:
            self._add_test_case(
                f'STATUS-{status}',
                'payment_status',
                f'Valid payment_status: {status}',
                'PASS',
                [],
                {'payment_status': status}
            )
        
        # Null status (acceptable)
        self._add_test_case(
            'STATUS-NULL',
            'payment_status',
            'Null payment_status',
            'PASS',
            [],
            {'payment_status': None}
        )
        
        # Invalid status
        self._add_test_case(
            'STATUS-INVALID',
            'payment_status',
            'Invalid payment_status',
            'REJECT',
            ['INVALID_VALUE'],
            {'payment_status': 'PROCESSING'}
        )
    
    def _generate_payment_date_tests(self):
        """Test payment_date validation"""
        
        # Null payment_date (not paid)
        self._add_test_case(
            'PAY_DATE-001',
            'payment_date',
            'Null payment_date (not paid)',
            'PASS',
            [],
            {
                'payment_date': None,
                'payment_status': 'PENDING'
            }
        )
        
        # Payment before transaction
        txn_date = self.today - timedelta(days=30)
        self._add_test_case(
            'PAY_DATE-002',
            'payment_date',
            'Payment date before transaction date',
            'REJECT',
            ['PAYMENT_BEFORE_TRANSACTION'],
            {
                'transaction_date': txn_date,
                'payment_date': txn_date - timedelta(days=5)
            }
        )
        
        # Same day payment
        self._add_test_case(
            'PAY_DATE-003',
            'payment_date',
            'Same day payment',
            'PASS',
            [],
            {
                'transaction_date': txn_date,
                'payment_date': txn_date
            }
        )
    
    def _generate_due_date_tests(self):
        """Test due_date validation"""
        
        # Null due_date (cash transaction)
        self._add_test_case(
            'DUE_DATE-001',
            'due_date',
            'Null due_date (cash)',
            'PASS',
            [],
            {'due_date': None}
        )
        
        # Due date before transaction (warning)
        txn_date = self.today - timedelta(days=30)
        self._add_test_case(
            'DUE_DATE-002',
            'due_date',
            'Due date before transaction date',
            'WARNING',
            ['DUE_DATE_BEFORE_TRANSACTION'],
            {
                'transaction_date': txn_date,
                'due_date': txn_date - timedelta(days=5),
                'payment_date': None,
                'payment_status': 'PENDING'
            }
        )
        
        # Net 30 terms
        self._add_test_case(
            'DUE_DATE-003',
            'due_date',
            'Net 30 payment terms',
            'PASS',
            [],
            {
                'transaction_date': txn_date,
                'due_date': txn_date + timedelta(days=30),
                'payment_date': None,
                'payment_status': 'PENDING'
            }
        )
    
    def _generate_formula_tests(self):
        """Test formula validations"""
        
        # gross_amount ≠ quantity × unit_price
        self._add_test_case(
            'FORMULA-001',
            'Formula Validation',
            'gross_amount mismatch with quantity × unit_price',
            'REJECT',
            ['FORMULA_MISMATCH'],
            {
                'quantity': 10.0,
                'unit_price': 1000.0,
                'gross_amount': 15000.0  # Should be 10000
            }
        )
        
        # net_amount ≠ gross_amount - discount_amount
        self._add_test_case(
            'FORMULA-002',
            'Formula Validation',
            'net_amount mismatch with gross - discount',
            'REJECT',
            ['FORMULA_MISMATCH'],
            {
                'gross_amount': 10000.0,
                'discount_amount': 500.0,
                'net_amount': 8000.0  # Should be 9500
            }
        )
        
        # total_amount ≠ net_amount + tax_amount
        self._add_test_case(
            'FORMULA-003',
            'Formula Validation',
            'total_amount mismatch with net + tax',
            'REJECT',
            ['FORMULA_MISMATCH'],
            {
                'net_amount': 9500.0,
                'tax_amount': 1805.0,
                'total_amount': 15000.0  # Should be 11305
            }
        )
        
        # Rounding tolerance (within 0.02)
        self._add_test_case(
            'FORMULA-004',
            'Formula Validation',
            'Formula within rounding tolerance',
            'PASS',
            [],
            {
                'quantity': 3.33,
                'unit_price': 1.50,
                'gross_amount': 4.99,  # Actually 4.995, within tolerance
                'discount_amount': None,
                'net_amount': 4.99,
                'tax_amount': 0.95,  # 19% of 4.99 = 0.9481
                'total_amount': 5.94
            }
        )
    
    def _generate_edge_cases(self):
        """Test edge cases"""
        
        # Multiple issues in one transaction
        self._add_test_case(
            'EDGE-001',
            'Edge Cases',
            'Multiple validation failures',
            'REJECT',
            ['NULL_IN_REQUIRED_FIELD', 'NEGATIVE_VALUE', 'FUTURE_DATE'],
            {
                'transaction_id': None,
                'transaction_date': self.today + timedelta(days=5),
                'quantity': -10.0,
                'gross_amount': -10000.0
            }
        )
        
        # Very small amounts (rounding issues)
        self._add_test_case(
            'EDGE-002',
            'Edge Cases',
            'Very small amounts',
            'PASS',
            [],
            {
                'quantity': 0.01,
                'unit_price': 0.01,
                'gross_amount': 0.0001,
                'discount_amount': None,
                'net_amount': 0.0001,
                'tax_amount': 0.000019,
                'total_amount': 0.000119
            }
        )
        
        # All optional fields null
        self._add_test_case(
            'EDGE-003',
            'Edge Cases',
            'Minimal valid transaction',
            'PASS',
            [],
            {
                'customer_id': None,
                'product_sku': None,
                'discount_amount': None,
                'tax_amount': None,
                'payment_date': None,
                'due_date': None,
                'payment_status': None,
                'net_amount': 10000.0,
                'total_amount': 10000.0
            }
        )
        
        # Payment status inconsistency (has payment_date but status not PAID)
        txn_date = self.today - timedelta(days=30)
        self._add_test_case(
            'EDGE-004',
            'Edge Cases',
            'Payment status inconsistent with payment_date',
            'WARNING',
            ['STATUS_DATE_MISMATCH'],
            {
                'transaction_date': txn_date,
                'payment_date': txn_date + timedelta(days=5),
                'payment_status': 'PENDING'  # Should be PAID
            }
        )
    
    def _test_cases_to_dataframe(self) -> pd.DataFrame:
        """Convert test cases to DataFrame"""
        rows = []
        for tc in self.test_cases:
            row = tc.data.copy()
            row['test_case_id'] = tc.case_id
            row['test_category'] = tc.category
            row['test_description'] = tc.description
            row['test_expected_result'] = tc.expected_result
            row['test_expected_issues'] = '|'.join(tc.expected_issues)
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    def get_coverage_summary(self) -> Dict:
        """Get summary of test coverage"""
        summary = {
            'total_cases': len(self.test_cases),
            'by_category': {},
            'by_expected_result': {},
            'by_column_tested': {}
        }
        
        # By category
        for tc in self.test_cases:
            summary['by_category'][tc.category] = summary['by_category'].get(tc.category, 0) + 1
        
        # By expected result
        for tc in self.test_cases:
            summary['by_expected_result'][tc.expected_result] = \
                summary['by_expected_result'].get(tc.expected_result, 0) + 1
        
        # By column (from category)
        columns = [
            'transaction_id', 'transaction_date', 'customer_id', 'product_sku',
            'quantity', 'unit_price', 'gross_amount', 'discount_amount',
            'net_amount', 'tax_amount', 'total_amount', 'payment_status',
            'payment_date', 'due_date'
        ]
        
        for col in columns:
            count = sum(1 for tc in self.test_cases if col in tc.category.lower())
            if count > 0:
                summary['by_column_tested'][col] = count
        
        return summary
    
    def export_test_manifest(self, filename: str = 'test_manifest.json'):
        """Export test case manifest"""
        manifest = {
            'generated_at': datetime.now().isoformat(),
            'total_cases': len(self.test_cases),
            'coverage_summary': self.get_coverage_summary(),
            'test_cases': [
                {
                    'case_id': tc.case_id,
                    'category': tc.category,
                    'description': tc.description,
                    'expected_result': tc.expected_result,
                    'expected_issues': tc.expected_issues
                }
                for tc in self.test_cases
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(manifest, f, indent=2, default=str)
        
        print(f"✅ Test manifest exported to: {filename}")
        return manifest


def generate_test_data(output_csv: str = 'test_transactions.csv',
                      manifest_json: str = 'test_manifest.json') -> Tuple[pd.DataFrame, Dict]:
    """
    Main function to generate test data
    
    Returns:
        Tuple of (test_dataframe, coverage_summary)
    """
    generator = TestDataGenerator()
    
    # Generate all test cases
    df = generator.generate_all_test_cases()
    
    # Get coverage summary
    coverage = generator.get_coverage_summary()
    
    # Export
    df.to_csv(output_csv, index=False)
    print(f"✅ Test data exported to: {output_csv}")
    
    generator.export_test_manifest(manifest_json)
    
    # Print coverage summary
    print("\n" + "="*80)
    print("TEST COVERAGE SUMMARY")
    print("="*80)
    print(f"\nTotal test cases: {coverage['total_cases']}")
    
    print(f"\n📊 By Expected Result:")
    for result, count in coverage['by_expected_result'].items():
        print(f"   {result}: {count}")
    
    print(f"\n📋 By Category:")
    for category, count in sorted(coverage['by_category'].items()):
        print(f"   {category}: {count}")
    
    print(f"\n🔍 By Column Tested:")
    for column, count in sorted(coverage['by_column_tested'].items()):
        print(f"   {column}: {count}")
    
    print("\n" + "="*80 + "\n")
    
    return df, coverage


if __name__ == "__main__":
    # Generate test data
    test_df, coverage = generate_test_data()
    
    print(f"✅ Generated {len(test_df)} test cases")
    print(f"   Columns: {len(test_df.columns)}")
    print(f"   Test columns: {[c for c in test_df.columns if c.startswith('_test')]}")
