"""
Example usage of the Transaction Data Processor
Demonstrates how to use the processor with sample data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys

# Import the processor
from transaction_processor import process_transaction_data, ProcessingResult


def generate_sample_data(n_rows: int = 100) -> pd.DataFrame:
    """Generate sample transaction data with some intentional issues"""
    
    np.random.seed(42)
    
    # Generate base data
    transaction_ids = [f"TXN-{i:06d}" for i in range(1, n_rows + 1)]
    
    # Add some duplicates (data quality issue)
    transaction_ids[50] = transaction_ids[10]
    
    # Generate dates
    base_date = datetime(2024, 1, 1)
    dates = [base_date + timedelta(days=np.random.randint(0, 300)) for _ in range(n_rows)]
    
    # Add some future dates (invalid)
    dates[15] = datetime.now() + timedelta(days=5)
    
    # Add some null dates (critical issue)
    dates[25] = None
    
    # Customer IDs
    customers = [f"CUST-{np.random.randint(1, 50):04d}" if np.random.random() > 0.15 else None 
                 for _ in range(n_rows)]
    
    # Product SKUs
    products = [f"PROD-{np.random.choice(['A', 'B', 'C', 'D'])}{np.random.randint(100, 999)}" 
                if np.random.random() > 0.1 else None 
                for _ in range(n_rows)]
    
    # Quantities
    quantities = np.random.uniform(1, 100, n_rows)
    quantities = np.round(quantities, 2)
    
    # Add negative quantity (invalid)
    quantities[30] = -5
    
    # Add null quantity (critical issue)
    quantities[35] = None
    
    # Unit prices
    unit_prices = np.random.uniform(100, 10000, n_rows)
    unit_prices = np.round(unit_prices, 2)
    
    # Add negative price (invalid)
    unit_prices[40] = -100
    
    # Calculate gross amounts
    gross_amounts = quantities * unit_prices
    
    # Add formula mismatch
    gross_amounts[45] = gross_amounts[45] * 1.5
    
    # Discount amounts (null means no discount)
    discount_amounts = [np.random.uniform(0, gross) * 0.3 if np.random.random() > 0.6 else None 
                       for gross in gross_amounts]
    
    # Add excessive discount (invalid)
    discount_amounts[55] = gross_amounts[55] * 2
    
    # Net amounts
    net_amounts = [gross - (disc if disc else 0) 
                   for gross, disc in zip(gross_amounts, discount_amounts)]
    
    # Tax amounts (19% IVA)
    tax_amounts = [net * 0.19 if np.random.random() > 0.05 else None 
                   for net in net_amounts]
    
    # Total amounts
    total_amounts = [net + (tax if tax else 0) 
                    for net, tax in zip(net_amounts, tax_amounts)]
    
    # Add null total amount (critical issue)
    total_amounts[60] = None
    
    # Payment status
    payment_statuses = np.random.choice(
        ['PAID', 'PENDING', 'OVERDUE', None], 
        n_rows, 
        p=[0.6, 0.2, 0.1, 0.1]
    )
    
    # Add invalid status
    payment_statuses[65] = 'PROCESSING'  # Not in valid values
    
    # Payment dates (only for PAID)
    payment_dates = [
        date + timedelta(days=np.random.randint(0, 30)) if status == 'PAID' and date is not None else None
        for date, status in zip(dates, payment_statuses)
    ]
    
    # Due dates (only for credit transactions)
    due_dates = [
        date + timedelta(days=30) if status in ['PENDING', 'OVERDUE'] and date is not None else None
        for date, status in zip(dates, payment_statuses)
    ]
    
    # Create DataFrame
    df = pd.DataFrame({
        'transaction_id': transaction_ids,
        'transaction_date': dates,
        'customer_id': customers,
        'product_sku': products,
        'quantity': quantities,
        'unit_price': unit_prices,
        'gross_amount': gross_amounts,
        'discount_amount': discount_amounts,
        'net_amount': net_amounts,
        'tax_amount': tax_amounts,
        'total_amount': total_amounts,
        'payment_status': payment_statuses,
        'payment_date': payment_dates,
        'due_date': due_dates,
        'transaction_type': 'SALE'
    })
    
    return df


def main():
    """Main example function"""
    
    print("="*80)
    print("TRANSACTION DATA PROCESSOR - EXAMPLE USAGE")
    print("="*80)
    
    # Generate sample data
    print("\n1️⃣  Generating sample transaction data...")
    raw_df = generate_sample_data(n_rows=100)
    print(f"   Generated {len(raw_df)} transactions with intentional data quality issues")
    
    # Process the data
    print("\n2️⃣  Processing transaction data...\n")
    result = process_transaction_data(
        df=raw_df,
        strict_mode=False,
        business_founding_date='2020-01-01'
    )
    
    # Print summary
    print("\n3️⃣  Processing Results:")
    result.print_summary()
    
    # Show sample of clean data
    print("\n4️⃣  Sample of Clean Data:")
    print(result.clean_data[['transaction_id', 'transaction_date', 'total_amount', 
                             'has_customer_id', 'has_discount']].head(10))
    
    # Show sample of rejected data
    if len(result.rejected_data) > 0:
        print("\n5️⃣  Sample of Rejected Data:")
        print(result.rejected_data[['transaction_id', 'rejection_reasons']].head(10))
    
    # Show specific issues
    print("\n6️⃣  Critical Issues (First 5):")
    critical_issues = result.get_issues_by_severity('CRITICAL')[:5]
    for issue in critical_issues:
        print(f"   Row {issue.row_index}: {issue.description}")
    
    print("\n7️⃣  Error Issues (First 5):")
    error_issues = result.get_issues_by_severity('ERROR')[:5]
    for issue in error_issues:
        print(f"   Row {issue.row_index}: {issue.description}")
    
    # Export results
    print("\n8️⃣  Exporting results...")
    
    # Save clean data
    result.clean_data.to_csv('clean_transactions.csv', index=False)
    print(f"   ✅ Clean data saved to: clean_transactions.csv ({len(result.clean_data)} rows)")
    
    # Save rejected data
    if len(result.rejected_data) > 0:
        result.rejected_data.to_csv('rejected_transactions.csv', index=False)
        print(f"   ❌ Rejected data saved to: rejected_transactions.csv ({len(result.rejected_data)} rows)")
    
    # Save quality report
    import json
    # Convert non-serializable objects
    report = result.quality_report.copy()
    if 'date_range' in report:
        for key in report['date_range']:
            if hasattr(report['date_range'][key], 'isoformat'):
                report['date_range'][key] = report['date_range'][key].isoformat()
    
    with open('quality_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"   📊 Quality report saved to: quality_report.json")
    
    # Advanced usage examples
    print("\n9️⃣  Advanced Usage Examples:\n")
    
    # Example 1: Filter by specific rejection reason
    print("   Example 1 - Rows rejected for null in required fields:")
    null_issues = [i for i in result.validation_issues 
                   if i.issue_type == 'NULL_IN_REQUIRED_FIELD']
    print(f"   Found {len(null_issues)} null issues in required fields")
    
    # Example 2: Analyze discount patterns
    if 'has_discount' in result.clean_data.columns:
        discount_rate = result.clean_data['has_discount'].mean() * 100
        print(f"\n   Example 2 - Discount analysis:")
        print(f"   {discount_rate:.1f}% of transactions have discounts")
        
        if discount_rate > 0:
            avg_discount = result.clean_data[result.clean_data['has_discount']]['discount_amount'].mean()
            print(f"   Average discount amount: ${avg_discount:,.2f}")
    
    # Example 3: Customer segmentation
    if 'customer_id' in result.clean_data.columns:
        customer_df = result.clean_data[result.clean_data['has_customer_id']]
        if len(customer_df) > 0:
            clv = customer_df.groupby('customer_id')['total_amount'].sum()
            print(f"\n   Example 3 - Customer analysis:")
            print(f"   {len(clv)} unique customers identified")
            print(f"   Average customer lifetime value: ${clv.mean():,.2f}")
            print(f"   Top customer value: ${clv.max():,.2f}")
    
    print("\n" + "="*80)
    print("✅ PROCESSING COMPLETE!")
    print("="*80 + "\n")
    
    return result


if __name__ == "__main__":
    result = main()
