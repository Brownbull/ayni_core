"""
Test script for 04_margin_optimization_study.ipynb
Validates all logic runs without errors
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from datetime import datetime
from scipy import stats

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Define paths (same as notebook)
DATA_PATH = '../../data/context_states/consolidated_analysis_20251022_173402/datasets/'
OUTPUT_DIR = '04_margin_optimization_study'

print("=" * 80)
print("TESTING MARGIN OPTIMIZATION STUDY NOTEBOOK")
print("=" * 80)

# Verify data path exists
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Data path not found: {DATA_PATH}\nCurrent directory: {os.getcwd()}")
print(f"✓ Data path exists: {DATA_PATH}")

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"✓ Output directory created: {OUTPUT_DIR}")

# Load datasets
print("\nLoading datasets...")
df_products = pd.read_csv(f'{DATA_PATH}product_daily_attrs.csv')
df_products['dt_date'] = pd.to_datetime(df_products['dt_date'], format='%Y%m%d')
print(f"✓ Loaded product_daily_attrs.csv: {len(df_products)} rows")

df_daily = pd.read_csv(f'{DATA_PATH}daily_attrs.csv')
df_daily['dt_date'] = pd.to_datetime(df_daily['dt_date'], format='%Y%m%d')
print(f"✓ Loaded daily_attrs.csv: {len(df_daily)} rows")

df_trans = pd.read_csv(f'{DATA_PATH}transactions_enriched.csv')
df_trans['dt_date'] = pd.to_datetime(df_trans['in_dt'])
print(f"✓ Loaded transactions_enriched.csv: {len(df_trans)} rows")

print("\n" + "=" * 80)
print("SECTION 1: Product Margin Analysis")
print("=" * 80)

# Aggregate product-level metrics
product_summary = df_products.groupby('in_product_id').agg({
    'price_total_sum': 'sum',
    'cost_total_sum': 'sum',
    'quantity_sum': 'sum',
    'trans_id_count': 'sum',
    'customer_id_count': 'sum'
}).reset_index()

product_summary.columns = ['product_id', 'total_revenue', 'total_cost', 'units_sold', 'transactions', 'unique_customers']

# Calculate margin metrics
product_summary['profit'] = product_summary['total_revenue'] - product_summary['total_cost']
product_summary['margin_pct'] = (product_summary['profit'] / product_summary['total_revenue']) * 100
product_summary['avg_price'] = product_summary['total_revenue'] / product_summary['units_sold']
product_summary['avg_cost'] = product_summary['total_cost'] / product_summary['units_sold']

# Calculate portfolio metrics
total_revenue = product_summary['total_revenue'].sum()
total_cost = product_summary['total_cost'].sum()
total_profit = product_summary['profit'].sum()
portfolio_margin = (total_profit / total_revenue) * 100

print(f"Portfolio margin: {portfolio_margin:.1f}%")
print(f"Total profit: ${total_profit:,.0f}")
print(f"Products analyzed: {len(product_summary)}")

best_margin_product = product_summary.loc[product_summary['margin_pct'].idxmax()]
worst_margin_product = product_summary.loc[product_summary['margin_pct'].idxmin()]

print(f"Best margin: {best_margin_product['product_id']} ({best_margin_product['margin_pct']:.1f}%)")
print(f"Worst margin: {worst_margin_product['product_id']} ({worst_margin_product['margin_pct']:.1f}%)")

COLORS = {
    'primary': '#2E86AB',
    'success': '#06A77D',
    'warning': '#F77F00',
    'danger': '#D62828',
    'secondary': '#6C757D'
}

plt.style.use('seaborn-v0_8-darkgrid')

# Visualization 1
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))

colors = [COLORS['success'] if m >= portfolio_margin else COLORS['danger'] for m in product_summary['margin_pct']]
ax1.barh(product_summary['product_id'], product_summary['margin_pct'], color=colors, edgecolor='black', alpha=0.8)
ax1.axvline(portfolio_margin, color='black', linestyle='--', linewidth=2, alpha=0.7)
ax1.set_xlabel('Margin %')
ax1.set_title('Profit Margin by Product')
ax1.grid(True, alpha=0.3)

ax2.barh(product_summary['product_id'], product_summary['profit'], color=COLORS['primary'], edgecolor='black', alpha=0.8)
ax2.set_xlabel('Profit ($)')
ax2.set_title('Absolute Profit Contribution')
ax2.grid(True, alpha=0.3)

ax3.scatter(product_summary['total_revenue'], product_summary['margin_pct'],
           s=product_summary['units_sold']*2, alpha=0.6, c=product_summary['profit'],
           cmap='RdYlGn', edgecolor='black')
ax3.set_xlabel('Revenue ($)')
ax3.set_ylabel('Margin %')
ax3.set_title('Margin vs Revenue')
ax3.grid(True, alpha=0.3)

ax4.bar(product_summary['product_id'], product_summary['total_revenue'],
       label='Revenue', color=COLORS['primary'], alpha=0.6, edgecolor='black')
ax4.bar(product_summary['product_id'], product_summary['profit'],
       label='Profit', color=COLORS['success'], alpha=0.8, edgecolor='black')
ax4.set_xlabel('Product')
ax4.set_ylabel('Amount ($)')
ax4.set_title('Revenue vs Profit')
ax4.legend()
ax4.tick_params(axis='x', rotation=45)
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/01_margin_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"✓ Saved: {OUTPUT_DIR}/01_margin_analysis.png")

print("\n" + "=" * 80)
print("SECTION 2: Price vs Cost Analysis")
print("=" * 80)

product_summary['unit_profit'] = product_summary['avg_price'] - product_summary['avg_cost']
product_summary['markup_pct'] = ((product_summary['avg_price'] / product_summary['avg_cost']) - 1) * 100

avg_portfolio_markup = ((total_revenue / product_summary['units_sold'].sum()) /
                        (total_cost / product_summary['units_sold'].sum()) - 1) * 100

print(f"Average portfolio markup: {avg_portfolio_markup:.1f}%")

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))

ax1.scatter(product_summary['avg_cost'], product_summary['avg_price'],
           s=product_summary['units_sold']*2, alpha=0.6, edgecolor='black')
max_val = max(product_summary['avg_price'].max(), product_summary['avg_cost'].max())
ax1.plot([0, max_val], [0, max_val], 'r--', linewidth=2, alpha=0.5, label='Break-even')
ax1.set_xlabel('Avg Cost ($)')
ax1.set_ylabel('Avg Price ($)')
ax1.set_title('Price vs Cost per Unit')
ax1.legend()
ax1.grid(True, alpha=0.3)

colors_markup = [COLORS['success'] if m >= avg_portfolio_markup else COLORS['warning'] for m in product_summary['markup_pct']]
ax2.barh(product_summary['product_id'], product_summary['markup_pct'],
        color=colors_markup, edgecolor='black', alpha=0.8)
ax2.axvline(avg_portfolio_markup, color='black', linestyle='--', linewidth=2, alpha=0.7)
ax2.set_xlabel('Markup %')
ax2.set_title('Markup % by Product')
ax2.grid(True, alpha=0.3)

ax3.bar(product_summary['product_id'], product_summary['total_cost'],
       color=COLORS['danger'], edgecolor='black', alpha=0.7)
ax3.set_xlabel('Product')
ax3.set_ylabel('Total Cost ($)')
ax3.set_title('Cost Structure')
ax3.tick_params(axis='x', rotation=45)
ax3.grid(True, alpha=0.3)

product_summary_sorted = product_summary.sort_values('unit_profit', ascending=False)
colors_profit = [COLORS['success'] if up > 0 else COLORS['danger'] for up in product_summary_sorted['unit_profit']]
ax4.bar(product_summary_sorted['product_id'], product_summary_sorted['unit_profit'],
       color=colors_profit, edgecolor='black', alpha=0.8)
ax4.axhline(0, color='black', linewidth=1)
ax4.set_xlabel('Product')
ax4.set_ylabel('Profit per Unit ($)')
ax4.set_title('Unit Profit by Product')
ax4.tick_params(axis='x', rotation=45)
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/02_price_cost_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"✓ Saved: {OUTPUT_DIR}/02_price_cost_analysis.png")

print("\n" + "=" * 80)
print("SECTION 3: Margin Trends")
print("=" * 80)

df_daily['profit'] = df_daily['price_total_sum'] - df_daily['cost_total_sum']
df_daily['margin_pct'] = (df_daily['profit'] / df_daily['price_total_sum']) * 100
df_daily = df_daily.sort_values('dt_date')

margin_trend = stats.linregress(range(len(df_daily)), df_daily['margin_pct'])
print(f"Margin trend: {margin_trend.slope:+.3f} pp/day")
print(f"Starting margin: {df_daily.iloc[0]['margin_pct']:.1f}%")
print(f"Ending margin: {df_daily.iloc[-1]['margin_pct']:.1f}%")

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))

ax1.plot(df_daily['dt_date'], df_daily['margin_pct'],
        color=COLORS['primary'], linewidth=2, marker='o', markersize=4, label='Daily Margin')
z = np.polyfit(range(len(df_daily)), df_daily['margin_pct'], 1)
p = np.poly1d(z)
ax1.plot(df_daily['dt_date'], p(range(len(df_daily))),
        'r--', linewidth=2, label=f'Trend: {z[0]:+.3f} pp/day')
ax1.set_xlabel('Date')
ax1.set_ylabel('Margin %')
ax1.set_title('Portfolio Margin Trend')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.tick_params(axis='x', rotation=45)

ax2.plot(df_daily['dt_date'], df_daily['price_total_sum'], linewidth=2, label='Revenue', color=COLORS['primary'])
ax2.plot(df_daily['dt_date'], df_daily['cost_total_sum'], linewidth=2, label='Cost', color=COLORS['danger'])
ax2.plot(df_daily['dt_date'], df_daily['profit'], linewidth=2, label='Profit', color=COLORS['success'])
ax2.set_xlabel('Date')
ax2.set_ylabel('Amount ($)')
ax2.set_title('Revenue, Cost & Profit')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.tick_params(axis='x', rotation=45)

ax3.hist(df_daily['margin_pct'], bins=15, color=COLORS['primary'], edgecolor='black', alpha=0.7)
ax3.axvline(df_daily['margin_pct'].mean(), color=COLORS['danger'], linestyle='--', linewidth=2)
ax3.set_xlabel('Margin %')
ax3.set_ylabel('Frequency')
ax3.set_title('Margin Distribution')
ax3.grid(True, alpha=0.3)

ax4.text(0.5, 0.5, 'Margin Volatility\nTest Chart', ha='center', va='center', fontsize=14)
ax4.axis('off')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/03_margin_trends.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"✓ Saved: {OUTPUT_DIR}/03_margin_trends.png")

print("\n" + "=" * 80)
print("SECTION 4: Scenario Analysis")
print("=" * 80)

baseline_profit = product_summary['profit'].sum()
scenario1_profit = (total_revenue * 1.05) - total_cost
scenario2_profit = total_revenue - (total_cost * 0.90)
scenario3_profit = (total_revenue * 1.03) - (total_cost * 0.95)

print(f"Baseline profit: ${baseline_profit:,.0f}")
print(f"Scenario 1 (5% price increase): ${scenario1_profit:,.0f} (+${scenario1_profit - baseline_profit:,.0f})")
print(f"Scenario 2 (10% cost reduction): ${scenario2_profit:,.0f} (+${scenario2_profit - baseline_profit:,.0f})")
print(f"Scenario 3 (3% price + 5% cost): ${scenario3_profit:,.0f} (+${scenario3_profit - baseline_profit:,.0f})")

best_increase = max(scenario1_profit - baseline_profit, scenario2_profit - baseline_profit, scenario3_profit - baseline_profit)

scenarios = pd.DataFrame({
    'scenario': ['Baseline', 'Price +5%', 'Cost -10%', 'Price +3% & Cost -5%'],
    'profit': [baseline_profit, scenario1_profit, scenario2_profit, scenario3_profit],
    'change': [0, scenario1_profit - baseline_profit, scenario2_profit - baseline_profit, scenario3_profit - baseline_profit]
})

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

colors_scenario = [COLORS['secondary'] if s == 'Baseline' else COLORS['success'] for s in scenarios['scenario']]
ax1.barh(scenarios['scenario'], scenarios['profit'], color=colors_scenario, edgecolor='black', linewidth=1.5, alpha=0.8)
ax1.set_xlabel('Total Profit ($)')
ax1.set_title('Margin Improvement Scenarios')
ax1.grid(True, alpha=0.3)

scenarios_inc = scenarios[scenarios['change'] > 0]
ax2.barh(scenarios_inc['scenario'], scenarios_inc['change'], color=COLORS['success'], edgecolor='black', linewidth=1.5, alpha=0.8)
ax2.set_xlabel('Incremental Profit ($)')
ax2.set_title('Profit Impact by Scenario')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/04_scenario_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"✓ Saved: {OUTPUT_DIR}/04_scenario_analysis.png")

print("\n" + "=" * 80)
print("TEST COMPLETED SUCCESSFULLY!")
print("=" * 80)
print(f"\nAll 4 visualizations created in: {OUTPUT_DIR}/")
print("  1. 01_margin_analysis.png")
print("  2. 02_price_cost_analysis.png")
print("  3. 03_margin_trends.png")
print("  4. 04_scenario_analysis.png")
print(f"\nKey Metrics:")
print(f"  • Portfolio margin: {portfolio_margin:.1f}%")
print(f"  • Total profit: ${total_profit:,.0f}")
print(f"  • Margin trend: {margin_trend.slope:+.3f} pp/day")
print(f"  • Best scenario improvement: +${best_increase:,.0f}")
print("\nNotebook is ready for execution in Jupyter!")
