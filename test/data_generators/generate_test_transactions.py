"""
Generate complete transaction test data with synthetic schema

This script generates realistic transaction data matching the schema from
data/tests/synthetic but with complete time periods for testing filters,
attributes, and aggregations.

Schema: 17 columns (all from base_case.csv)
- in_dt: Transaction datetime
- in_trans_id: Transaction ID
- in_trans_type: Transaction type
- in_customer_id: Customer ID
- in_product_id: Product ID
- in_description: Product description
- in_category: Product category
- in_unit_type: Unit type
- in_stock: Current stock level
- in_quantity: Quantity sold
- in_cost_unit: Unit cost
- in_cost_total: Total cost
- in_price_unit: Unit price
- in_price_total: Total price (BASE - not inferable)
- in_discount_total: Discount amount
- in_commission_total: Commission amount
- in_margin: Profit margin

This data is designed to test aggregation models described in /docs/specs/model/*.md
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import random


class TestTransactionGenerator:
    """Generate complete transaction test data for aggregation testing"""

    def __init__(
        self,
        start_date: str = "2025-10-01",
        num_days: int = 30,
        seed: int = 42
    ):
        """
        Initialize test transaction generator

        Args:
            start_date: Start date in YYYY-MM-DD format
            num_days: Number of days to generate
            seed: Random seed for reproducibility
        """
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.num_days = num_days
        self.seed = seed

        # Set random seed
        np.random.seed(seed)
        random.seed(seed)

        # Setup test data
        self._setup_test_data()

    def _setup_test_data(self):
        """Setup simplified test products, customers, categories"""

        # Products (10 simple products)
        self.products = [
            {'id': 'prod1', 'description': 'product 1', 'category': 'category A', 'base_price': 150.0, 'base_cost': 100.0},
            {'id': 'prod2', 'description': 'product 2', 'category': 'category A', 'base_price': 200.0, 'base_cost': 130.0},
            {'id': 'prod3', 'description': 'product 3', 'category': 'category B', 'base_price': 250.0, 'base_cost': 170.0},
            {'id': 'prod4', 'description': 'product 4', 'category': 'category B', 'base_price': 300.0, 'base_cost': 200.0},
            {'id': 'prod5', 'description': 'product 5', 'category': 'category C', 'base_price': 180.0, 'base_cost': 120.0},
            {'id': 'prod6', 'description': 'product 6', 'category': 'category C', 'base_price': 220.0, 'base_cost': 150.0},
            {'id': 'prod7', 'description': 'product 7', 'category': 'category A', 'base_price': 350.0, 'base_cost': 240.0},
            {'id': 'prod8', 'description': 'product 8', 'category': 'category B', 'base_price': 280.0, 'base_cost': 190.0},
            {'id': 'prod9', 'description': 'product 9', 'category': 'category C', 'base_price': 160.0, 'base_cost': 110.0},
            {'id': 'prod10', 'description': 'product 10', 'category': 'category A', 'base_price': 400.0, 'base_cost': 280.0},
        ]

        # Customers (15 simple customers)
        self.customers = [f'client{i}' for i in range(1, 16)]

        # Transaction types
        self.transaction_types = ['sale', 'return', 'exchange']

        # Unit types
        self.unit_types = ['unit', 'box', 'pack', 'kg']

    def _get_hourly_pattern(self, hour: int) -> float:
        """Get transaction probability multiplier for given hour"""
        if hour < 8 or hour > 20:
            return 0.05  # Very low activity outside business hours
        elif 8 <= hour < 10:
            return 0.6
        elif 10 <= hour < 12:
            return 1.2  # Morning peak
        elif 12 <= hour < 14:
            return 0.8
        elif 14 <= hour < 17:
            return 1.5  # Afternoon peak
        elif 17 <= hour < 19:
            return 1.0
        else:
            return 0.5

    def _get_daily_pattern(self, date: datetime) -> float:
        """Get transaction probability multiplier for given day"""
        weekday = date.weekday()

        # Weekly pattern
        if weekday == 0:  # Monday
            return 0.9
        elif weekday == 1:  # Tuesday
            return 1.1
        elif weekday == 2:  # Wednesday
            return 1.2
        elif weekday == 3:  # Thursday
            return 1.3
        elif weekday == 4:  # Friday
            return 1.5  # Peak
        elif weekday == 5:  # Saturday
            return 1.1
        else:  # Sunday
            return 0.7

    def generate_transactions(self) -> pd.DataFrame:
        """
        Generate complete transaction data for configured date range

        Returns:
            DataFrame with all 17 columns from synthetic schema
        """
        transactions = []
        transaction_counter = 1

        # Generate transactions for each day
        for day_offset in range(self.num_days):
            current_date = self.start_date + timedelta(days=day_offset)
            daily_multiplier = self._get_daily_pattern(current_date)

            # Base transactions per day: 10-30 depending on pattern
            base_daily_transactions = int(np.random.poisson(18 * daily_multiplier))

            # Generate transactions throughout the day
            for _ in range(base_daily_transactions):
                # Select random hour weighted by pattern
                hour = np.random.choice(24, p=self._get_hourly_weights())
                minute = np.random.randint(0, 60)
                second = np.random.randint(0, 60)

                timestamp = current_date.replace(hour=hour, minute=minute, second=second)

                # Generate transaction
                transaction = self._generate_single_transaction(
                    timestamp,
                    transaction_counter
                )
                transactions.append(transaction)
                transaction_counter += 1

        # Create DataFrame
        df = pd.DataFrame(transactions)

        # Sort by date
        df = df.sort_values('in_dt').reset_index(drop=True)

        return df

    def _get_hourly_weights(self) -> np.ndarray:
        """Get normalized probability weights for each hour"""
        weights = np.array([self._get_hourly_pattern(h) for h in range(24)])
        return weights / weights.sum()

    def _generate_single_transaction(
        self,
        timestamp: datetime,
        transaction_num: int
    ) -> Dict:
        """Generate a single complete transaction record"""

        # Select product
        product = random.choice(self.products)

        # Select customer
        customer_id = random.choice(self.customers)

        # Transaction type (95% sales, 4% returns, 1% exchange)
        trans_type_prob = np.random.random()
        if trans_type_prob < 0.95:
            trans_type = 'sale'
        elif trans_type_prob < 0.99:
            trans_type = 'return'
        else:
            trans_type = 'exchange'

        # Quantity (most 1-5 units)
        if np.random.random() < 0.6:
            quantity = np.random.randint(1, 4)  # 1-3 units (60%)
        elif np.random.random() < 0.85:
            quantity = np.random.randint(4, 8)  # 4-7 units (25%)
        else:
            quantity = np.random.randint(8, 21)  # 8-20 units (15%)

        # Unit type (weighted towards 'unit')
        unit_type_prob = np.random.random()
        if unit_type_prob < 0.6:
            unit_type = 'unit'
        elif unit_type_prob < 0.8:
            unit_type = 'box'
        elif unit_type_prob < 0.95:
            unit_type = 'pack'
        else:
            unit_type = 'kg'

        # Pricing with variance (±10-15%)
        price_variance = np.random.uniform(-0.12, 0.12)
        unit_price = product['base_price'] * (1 + price_variance)

        cost_variance = np.random.uniform(-0.08, 0.08)
        unit_cost = product['base_cost'] * (1 + cost_variance)

        # Total price (BASE COLUMN - most important)
        price_total = unit_price * quantity

        # Total cost
        cost_total = unit_cost * quantity

        # Discount (25% of transactions have discount)
        has_discount = np.random.random() < 0.25
        if has_discount:
            discount_rate = np.random.uniform(0.05, 0.25)
            discount_total = price_total * discount_rate
        else:
            discount_total = 0.0

        # Commission (varies 2-6%)
        commission_rate = np.random.uniform(0.02, 0.06)
        commission_total = price_total * commission_rate

        # Margin (price - cost - commission - discount)
        margin = (price_total - discount_total) - cost_total - commission_total

        # Stock level (simulate inventory)
        stock = np.random.randint(0, 150)

        # Transaction ID
        trans_id = f'trans{transaction_num:06d}'

        # Format datetime
        dt_str = timestamp.strftime("%m/%d/%Y %H:%M")

        # Build complete transaction record (17 columns)
        transaction = {
            # Required columns (optional=0)
            'in_dt': dt_str,
            'in_trans_id': trans_id,
            'in_product_id': product['id'],
            'in_quantity': quantity,
            'in_price_total': round(price_total, 2),  # BASE COLUMN

            # Optional columns (optional=1)
            'in_trans_type': trans_type,
            'in_customer_id': customer_id,
            'in_description': product['description'],
            'in_category': product['category'],
            'in_unit_type': unit_type,
            'in_stock': stock,

            # Inferable columns (inferable=1)
            'in_cost_unit': round(unit_cost, 2),
            'in_cost_total': round(cost_total, 2),
            'in_price_unit': round(unit_price, 2),
            'in_discount_total': round(discount_total, 2),
            'in_commission_total': round(commission_total, 2),
            'in_margin': round(margin, 2),
        }

        return transaction

    def save_to_csv(self, output_filename: str = None) -> str:
        """
        Generate and save transaction data to CSV

        Args:
            output_filename: Custom filename (optional)

        Returns:
            Path to saved file
        """
        df = self.generate_transactions()

        if output_filename is None:
            # Auto-generate filename
            start_str = self.start_date.strftime("%Y%m%d")
            output_filename = f"test_transactions_{start_str}_{self.num_days}days.csv"

        output_path = Path(__file__).parent / output_filename

        # Save with standard UTF-8 encoding
        df.to_csv(output_path, index=False, encoding='utf-8')

        print(f"[OK] Generated {len(df)} transactions")
        print(f"[OK] Date range: {df['in_dt'].iloc[0]} to {df['in_dt'].iloc[-1]}")
        print(f"[OK] Products: {df['in_product_id'].nunique()} unique")
        print(f"[OK] Customers: {df['in_customer_id'].nunique()} unique")
        print(f"[OK] Saved to: {output_path}")

        # Print summary statistics
        print(f"\n[STATS]")
        print(f"  Total revenue: ${df['in_price_total'].sum():,.2f}")
        print(f"  Total cost: ${df['in_cost_total'].sum():,.2f}")
        print(f"  Total margin: ${df['in_margin'].sum():,.2f}")
        print(f"  Avg transaction: ${df['in_price_total'].mean():,.2f}")
        print(f"  Transaction types: {dict(df['in_trans_type'].value_counts())}")

        return str(output_path)


def main():
    """Main execution with example configurations"""

    print("="*70)
    print("TEST TRANSACTION GENERATOR (Synthetic Schema)")
    print("="*70)
    print()

    # Example 1: 7 days (one week) for quick testing
    print("Example 1: One Week (7 days)")
    print("-" * 70)
    generator1 = TestTransactionGenerator(
        start_date="2025-10-01",
        num_days=7,
        seed=42
    )
    generator1.save_to_csv("quick_test_7days.csv")
    print()

    # Example 2: 30 days (one month) for monthly aggregations
    print("Example 2: One Month (30 days)")
    print("-" * 70)
    generator2 = TestTransactionGenerator(
        start_date="2025-10-01",
        num_days=30,
        seed=100
    )
    generator2.save_to_csv("test_transactions_30days.csv")
    print()

    # Example 3: 60 days (two months) for month-over-month
    print("Example 3: Two Months (60 days)")
    print("-" * 70)
    generator3 = TestTransactionGenerator(
        start_date="2025-09-01",
        num_days=60,
        seed=200
    )
    generator3.save_to_csv("test_transactions_60days.csv")
    print()

    # Example 4: 90 days (quarter) for quarterly analysis
    print("Example 4: One Quarter (90 days)")
    print("-" * 70)
    generator4 = TestTransactionGenerator(
        start_date="2025-07-01",
        num_days=90,
        seed=300
    )
    generator4.save_to_csv("test_transactions_90days.csv")
    print()

    print("="*70)
    print("GENERATION COMPLETE")
    print("="*70)
    print()
    print("Files created in: data/tests/raw/")
    print()
    print("Next steps:")
    print("  1. Use quick_test_7days.csv for unit tests")
    print("  2. Use test_transactions_30days.csv for monthly aggregations")
    print("  3. Use test_transactions_60days.csv for month-over-month analysis")
    print("  4. Use test_transactions_90days.csv for quarterly trends")
    print()


if __name__ == "__main__":
    main()
