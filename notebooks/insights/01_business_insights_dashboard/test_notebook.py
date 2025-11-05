# Test script to validate notebook logic
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

print("Testing Business Insights Notebook...")
print("=" * 60)

# Configure
sns.set_style('whitegrid')
COLORS = {
    'primary': '#2E86AB',
    'success': '#06A77D',
    'warning': '#F18F01',
    'danger': '#C73E1D',
    'neutral': '#6C757D'
}

DATA_PATH = '../../data/context_states/consolidated_analysis_20251022_173402/datasets/'

# Load data
print("\n1. Loading data...")
df_daily = pd.read_csv(f'{DATA_PATH}daily_attrs.csv')
df_daily['dt_date'] = pd.to_datetime(df_daily['dt_date'])
print(f"   Daily: {len(df_daily)} rows")

df_products = pd.read_csv(f'{DATA_PATH}product_daily_attrs.csv')
df_products['dt_date'] = pd.to_datetime(df_products['dt_date'])
print(f"   Products: {len(df_products)} rows")

df_customers = pd.read_csv(f'{DATA_PATH}customer_daily_attrs.csv')
df_customers['dt_date'] = pd.to_datetime(df_customers['dt_date'])
print(f"   Customers: {len(df_customers)} rows")

df_hourly = pd.read_csv(f'{DATA_PATH}daily_hour_attrs.csv')
df_hourly['dt_date'] = pd.to_datetime(df_hourly['dt_date'])
print(f"   Hourly: {len(df_hourly)} rows")

# Calculate metrics
print("\n2. Calculating KPIs...")
total_revenue = df_daily['price_total_sum'].sum()
total_transactions = df_daily['trans_id_count'].sum()
unique_products = df_products['in_product_id'].nunique()
unique_customers = df_customers['in_customer_id'].nunique()

print(f"   Revenue: ${total_revenue:,.2f}")
print(f"   Transactions: {total_transactions}")
print(f"   Products: {unique_products}")
print(f"   Customers: {unique_customers}")

# Test visualizations
print("\n3. Testing visualizations...")

# Revenue trend
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df_daily['dt_date'], df_daily['price_total_sum'], marker='o')
ax.set_title('Revenue Trend')
plt.savefig('viz_1_revenue_trend.png')
plt.close()
print("   Revenue trend: OK")

# Top products
product_totals = df_products.groupby('in_product_id')['price_total_sum'].sum().sort_values(ascending=False)
top_10 = product_totals.head(10)

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(range(len(top_10)), top_10.values)
plt.savefig('viz_2_top_products.png')
plt.close()
print("   Top products: OK")

# Customer frequency
cust_freq = df_customers.groupby('in_customer_id')['dt_date'].count()

fig, ax = plt.subplots(figsize=(12, 6))
ax.hist(cust_freq, bins=20)
plt.savefig('viz_3_customer_freq.png')
plt.close()
print("   Customer frequency: OK")

# Hourly pattern
if 'hour' in df_hourly.columns:
    hourly = df_hourly.groupby('hour')['trans_id_count'].sum()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(hourly.index, hourly.values)
    plt.savefig('viz_4_hourly.png')
    plt.close()
    print("   Hourly pattern: OK")
else:
    print("   Hourly pattern: SKIPPED (no hour column)")

# Day of week
df_daily['day_name'] = df_daily['dt_date'].dt.day_name()
dow = df_daily.groupby('day_name')['price_total_sum'].mean()

fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(range(len(dow)), dow.values)
plt.savefig('viz_5_day_of_week.png')
plt.close()
print("   Day of week: OK")

print("\n" + "=" * 60)
print("SUCCESS! All tests passed.")
print("=" * 60)
print("\nGenerated visualizations:")
import os
for f in ['viz_1_revenue_trend.png', 'viz_2_top_products.png', 'viz_3_customer_freq.png',
          'viz_4_hourly.png', 'viz_5_day_of_week.png']:
    if os.path.exists(f):
        print(f"  - {f}")
