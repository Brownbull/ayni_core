"""
Test script for 02_product_performance_matrix.ipynb
Validates all logic runs without errors
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Define paths (same as notebook)
DATA_PATH = '../../data/context_states/consolidated_analysis_20251022_173402/datasets/'
OUTPUT_DIR = '02_product_performance_matrix'

print("=" * 80)
print("TESTING PRODUCT PERFORMANCE MATRIX NOTEBOOK")
print("=" * 80)

# Verify data path exists
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Data path not found: {DATA_PATH}\nCurrent directory: {os.getcwd()}")
print(f"✓ Data path exists: {DATA_PATH}")

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"✓ Output directory created: {OUTPUT_DIR}")

# Load datasets with correct date parsing
print("\nLoading datasets...")
df_daily = pd.read_csv(f'{DATA_PATH}daily_attrs.csv')
df_daily['dt_date'] = pd.to_datetime(df_daily['dt_date'], format='%Y%m%d')
print(f"✓ Loaded daily_attrs.csv: {len(df_daily)} rows")

df_products = pd.read_csv(f'{DATA_PATH}product_daily_attrs.csv')
df_products['dt_date'] = pd.to_datetime(df_products['dt_date'], format='%Y%m%d')
print(f"✓ Loaded product_daily_attrs.csv: {len(df_products)} rows")

# Verify date parsing worked correctly
print(f"\nDate range: {df_products['dt_date'].min()} to {df_products['dt_date'].max()}")
print(f"Days in period: {(df_products['dt_date'].max() - df_products['dt_date'].min()).days + 1}")

# Color scheme (same as notebook)
COLORS = {
    'primary': '#2E86AB',
    'success': '#06A77D',
    'warning': '#F77F00',
    'danger': '#D62828',
    'secondary': '#6C757D'
}

# ==================== PRODUCT AGGREGATION ====================
print("\n" + "=" * 80)
print("SECTION 1: Product Aggregation")
print("=" * 80)

product_summary = df_products.groupby('in_product_id').agg({
    'price_total_sum': 'sum',
    'cost_total_sum': 'sum',
    'quantity_sum': 'sum',
    'trans_id_count': 'sum',
    'customer_id_count': 'sum'
}).reset_index()

product_summary.columns = ['product_id', 'total_revenue', 'total_cost', 'units_sold', 'transactions', 'unique_customers']

# Calculate metrics
product_summary['profit'] = product_summary['total_revenue'] - product_summary['total_cost']
product_summary['margin_pct'] = (product_summary['profit'] / product_summary['total_revenue']) * 100
days_in_period = (df_products['dt_date'].max() - df_products['dt_date'].min()).days + 1
product_summary['velocity'] = product_summary['units_sold'] / days_in_period
product_summary['revenue_pct'] = (product_summary['total_revenue'] / product_summary['total_revenue'].sum()) * 100

print(f"✓ Aggregated {len(product_summary)} unique products")
print(f"✓ Total revenue: ${product_summary['total_revenue'].sum():,.0f}")
print(f"✓ Total units sold: {product_summary['units_sold'].sum():,.0f}")
print(f"✓ Average margin: {product_summary['margin_pct'].mean():.1f}%")

# ==================== 4-QUADRANT CLASSIFICATION ====================
print("\n" + "=" * 80)
print("SECTION 2: 4-Quadrant Classification")
print("=" * 80)

median_velocity = product_summary['velocity'].median()
median_revenue = product_summary['total_revenue'].median()

print(f"Median velocity: {median_velocity:.2f} units/day")
print(f"Median revenue: ${median_revenue:,.0f}")

def classify_quadrant(row):
    if row['velocity'] > median_velocity and row['total_revenue'] > median_revenue:
        return 'STARS'
    elif row['velocity'] <= median_velocity and row['total_revenue'] > median_revenue:
        return 'CASH COWS'
    elif row['velocity'] > median_velocity and row['total_revenue'] <= median_revenue:
        return 'WORKHORSES'
    else:
        return 'DEAD STOCK'

product_summary['quadrant'] = product_summary.apply(classify_quadrant, axis=1)

quadrant_counts = product_summary['quadrant'].value_counts()
print(f"\nQuadrant distribution:")
for quadrant, count in quadrant_counts.items():
    pct = (count / len(product_summary)) * 100
    print(f"  {quadrant}: {count} products ({pct:.1f}%)")

# Visualization 1: Product Quadrant Matrix
fig, ax = plt.subplots(figsize=(14, 10))

for quadrant in ['STARS', 'CASH COWS', 'WORKHORSES', 'DEAD STOCK']:
    subset = product_summary[product_summary['quadrant'] == quadrant]
    if quadrant == 'STARS':
        color = COLORS['success']
    elif quadrant == 'CASH COWS':
        color = COLORS['primary']
    elif quadrant == 'WORKHORSES':
        color = COLORS['warning']
    else:
        color = COLORS['danger']

    ax.scatter(subset['velocity'], subset['total_revenue'],
              s=subset['units_sold']*3, alpha=0.6, color=color,
              label=f'{quadrant} ({len(subset)})', edgecolor='black', linewidth=1)

ax.axhline(median_revenue, color='gray', linestyle='--', linewidth=2, alpha=0.5, label='Median Revenue')
ax.axvline(median_velocity, color='gray', linestyle='--', linewidth=2, alpha=0.5, label='Median Velocity')

ax.set_xlabel('Velocity (Units/Day)', fontsize=14, fontweight='bold')
ax.set_ylabel('Total Revenue ($)', fontsize=14, fontweight='bold')
ax.set_title('Product Performance Matrix: Strategic Quadrants', fontsize=18, fontweight='bold', pad=20)
ax.legend(fontsize=11, loc='upper left', framealpha=0.9)
ax.grid(True, alpha=0.3, linestyle=':')
ax.set_facecolor('#F8F9FA')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/01_product_quadrant_matrix.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"\n✓ Saved: {OUTPUT_DIR}/01_product_quadrant_matrix.png")

# ==================== PARETO ANALYSIS ====================
print("\n" + "=" * 80)
print("SECTION 3: Pareto Analysis (80/20 Rule)")
print("=" * 80)

product_summary_sorted = product_summary.sort_values('total_revenue', ascending=False).reset_index(drop=True)
product_summary_sorted['cumulative_revenue'] = product_summary_sorted['total_revenue'].cumsum()
product_summary_sorted['cumulative_pct'] = (product_summary_sorted['cumulative_revenue'] / product_summary_sorted['total_revenue'].sum()) * 100

products_80 = len(product_summary_sorted[product_summary_sorted['cumulative_pct'] <= 80])
pct_products_80 = (products_80 / len(product_summary_sorted)) * 100

print(f"✓ Top {products_80} products ({pct_products_80:.1f}%) generate 80% of revenue")
print(f"✓ Remaining {len(product_summary_sorted) - products_80} products ({100-pct_products_80:.1f}%) generate 20% of revenue")

# Visualization 2: Pareto Chart
fig, ax1 = plt.subplots(figsize=(14, 8))

x = range(len(product_summary_sorted))
ax1.bar(x, product_summary_sorted['total_revenue'], color=COLORS['primary'], alpha=0.7, label='Revenue')
ax1.set_xlabel('Product Rank (by Revenue)', fontsize=14, fontweight='bold')
ax1.set_ylabel('Revenue ($)', fontsize=14, fontweight='bold', color=COLORS['primary'])
ax1.tick_params(axis='y', labelcolor=COLORS['primary'])

ax2 = ax1.twinx()
ax2.plot(x, product_summary_sorted['cumulative_pct'], color=COLORS['danger'],
         linewidth=3, label='Cumulative %', marker='o', markersize=4)
ax2.axhline(80, color=COLORS['warning'], linestyle='--', linewidth=2, label='80% Line')
ax2.set_ylabel('Cumulative Revenue %', fontsize=14, fontweight='bold', color=COLORS['danger'])
ax2.tick_params(axis='y', labelcolor=COLORS['danger'])
ax2.set_ylim(0, 105)

plt.title('Pareto Analysis: Revenue Concentration', fontsize=18, fontweight='bold', pad=20)
fig.legend(loc='upper left', bbox_to_anchor=(0.12, 0.88), fontsize=11, framealpha=0.9)
plt.grid(True, alpha=0.3, linestyle=':', axis='y')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/02_pareto_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"✓ Saved: {OUTPUT_DIR}/02_pareto_analysis.png")

# ==================== ABC CLASSIFICATION ====================
print("\n" + "=" * 80)
print("SECTION 4: ABC Classification")
print("=" * 80)

def classify_abc(cumulative_pct):
    if cumulative_pct <= 80:
        return 'A'
    elif cumulative_pct <= 95:
        return 'B'
    else:
        return 'C'

product_summary_sorted['abc_class'] = product_summary_sorted['cumulative_pct'].apply(classify_abc)

abc_counts = product_summary_sorted['abc_class'].value_counts().sort_index()
print(f"ABC Classification:")
for abc_class, count in abc_counts.items():
    pct = (count / len(product_summary_sorted)) * 100
    revenue_pct = product_summary_sorted[product_summary_sorted['abc_class'] == abc_class]['total_revenue'].sum() / product_summary_sorted['total_revenue'].sum() * 100
    print(f"  Class {abc_class}: {count} products ({pct:.1f}%) → {revenue_pct:.1f}% of revenue")

# Visualization 3: ABC Classification
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

abc_colors = {'A': COLORS['success'], 'B': COLORS['warning'], 'C': COLORS['danger']}
abc_revenue = product_summary_sorted.groupby('abc_class')['total_revenue'].sum()
abc_products = product_summary_sorted['abc_class'].value_counts().sort_index()

ax1.bar(abc_products.index, abc_products.values, color=[abc_colors[x] for x in abc_products.index],
        edgecolor='black', linewidth=1.5, alpha=0.8)
ax1.set_xlabel('ABC Class', fontsize=14, fontweight='bold')
ax1.set_ylabel('Number of Products', fontsize=14, fontweight='bold')
ax1.set_title('ABC Classification: Product Count', fontsize=16, fontweight='bold')
ax1.grid(True, alpha=0.3, linestyle=':', axis='y')

for i, (idx, val) in enumerate(abc_products.items()):
    ax1.text(i, val + 0.5, f'{val}\n({val/len(product_summary_sorted)*100:.1f}%)',
             ha='center', fontsize=12, fontweight='bold')

ax2.bar(abc_revenue.index, abc_revenue.values, color=[abc_colors[x] for x in abc_revenue.index],
        edgecolor='black', linewidth=1.5, alpha=0.8)
ax2.set_xlabel('ABC Class', fontsize=14, fontweight='bold')
ax2.set_ylabel('Total Revenue ($)', fontsize=14, fontweight='bold')
ax2.set_title('ABC Classification: Revenue Contribution', fontsize=16, fontweight='bold')
ax2.grid(True, alpha=0.3, linestyle=':', axis='y')

for i, (idx, val) in enumerate(abc_revenue.items()):
    ax2.text(i, val + max(abc_revenue.values)*0.02, f'${val:,.0f}\n({val/abc_revenue.sum()*100:.1f}%)',
             ha='center', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/03_abc_classification.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"✓ Saved: {OUTPUT_DIR}/03_abc_classification.png")

# ==================== VELOCITY ANALYSIS ====================
print("\n" + "=" * 80)
print("SECTION 5: Velocity Analysis")
print("=" * 80)

top_velocity = product_summary.nlargest(10, 'velocity')
print(f"\nTop 10 products by velocity:")
for idx, row in top_velocity.iterrows():
    print(f"  Product {row['product_id']}: {row['velocity']:.2f} units/day (${row['total_revenue']:,.0f} revenue)")

# Visualization 4: Velocity Analysis
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

ax1.barh(range(len(top_velocity)), top_velocity['velocity'].values, color=COLORS['success'],
         edgecolor='black', linewidth=1, alpha=0.8)
ax1.set_yticks(range(len(top_velocity)))
ax1.set_yticklabels([f"Product {pid}" for pid in top_velocity['product_id'].values])
ax1.set_xlabel('Velocity (Units/Day)', fontsize=14, fontweight='bold')
ax1.set_ylabel('Product', fontsize=14, fontweight='bold')
ax1.set_title('Top 10 Products by Velocity', fontsize=16, fontweight='bold')
ax1.grid(True, alpha=0.3, linestyle=':', axis='x')

for i, (idx, row) in enumerate(top_velocity.iterrows()):
    ax1.text(row['velocity'] + 0.1, i, f"{row['velocity']:.1f}", va='center', fontsize=11, fontweight='bold')

ax2.hist(product_summary['velocity'], bins=20, color=COLORS['primary'], edgecolor='black', alpha=0.7)
ax2.axvline(product_summary['velocity'].median(), color=COLORS['danger'], linestyle='--',
            linewidth=2, label=f"Median: {product_summary['velocity'].median():.2f}")
ax2.axvline(product_summary['velocity'].mean(), color=COLORS['warning'], linestyle='--',
            linewidth=2, label=f"Mean: {product_summary['velocity'].mean():.2f}")
ax2.set_xlabel('Velocity (Units/Day)', fontsize=14, fontweight='bold')
ax2.set_ylabel('Number of Products', fontsize=14, fontweight='bold')
ax2.set_title('Velocity Distribution', fontsize=16, fontweight='bold')
ax2.legend(fontsize=11, framealpha=0.9)
ax2.grid(True, alpha=0.3, linestyle=':', axis='y')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/04_velocity_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"✓ Saved: {OUTPUT_DIR}/04_velocity_analysis.png")

# ==================== STRATEGIC RECOMMENDATIONS ====================
print("\n" + "=" * 80)
print("SECTION 6: Strategic Recommendations by Quadrant")
print("=" * 80)

recommendations = {
    'STARS': {
        'priority': 'HIGHEST',
        'actions': [
            'Maximize inventory availability',
            'Consider premium pricing opportunities',
            'Protect from stockouts',
            'Bundle with other products'
        ]
    },
    'CASH COWS': {
        'priority': 'HIGH',
        'actions': [
            'Maintain steady supply',
            'Optimize pricing for profitability',
            'Cross-sell with Stars',
            'Monitor for velocity improvements'
        ]
    },
    'WORKHORSES': {
        'priority': 'MEDIUM',
        'actions': [
            'Investigate margin improvement opportunities',
            'Consider upselling strategies',
            'Evaluate bundling with high-value items',
            'Test promotional pricing'
        ]
    },
    'DEAD STOCK': {
        'priority': 'LOW (REVIEW)',
        'actions': [
            'Clearance sales to free capital',
            'Discontinue if margins negative',
            'Reduce inventory levels',
            'Evaluate replacement products'
        ]
    }
}

for quadrant in ['STARS', 'CASH COWS', 'WORKHORSES', 'DEAD STOCK']:
    count = len(product_summary[product_summary['quadrant'] == quadrant])
    if count > 0:
        print(f"\n{quadrant} ({count} products) - Priority: {recommendations[quadrant]['priority']}")
        for action in recommendations[quadrant]['actions']:
            print(f"  • {action}")

print("\n" + "=" * 80)
print("TEST COMPLETED SUCCESSFULLY!")
print("=" * 80)
print(f"\nAll 4 visualizations created in: {OUTPUT_DIR}/")
print("  1. 01_product_quadrant_matrix.png")
print("  2. 02_pareto_analysis.png")
print("  3. 03_abc_classification.png")
print("  4. 04_velocity_analysis.png")
print("\nNotebook is ready for execution in Jupyter!")
