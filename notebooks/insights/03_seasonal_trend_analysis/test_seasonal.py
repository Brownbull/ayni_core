"""
Test script for 03_seasonal_trend_analysis.ipynb
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
OUTPUT_DIR = '03_seasonal_trend_analysis'

print("=" * 80)
print("TESTING SEASONAL TREND ANALYSIS NOTEBOOK")
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

df_hourly = pd.read_csv(f'{DATA_PATH}daily_hour_attrs.csv')
df_hourly['dt_date'] = pd.to_datetime(df_hourly['dt_date'], format='%Y%m%d')
print(f"✓ Loaded daily_hour_attrs.csv: {len(df_hourly)} rows")

df_products = pd.read_csv(f'{DATA_PATH}product_daily_attrs.csv')
df_products['dt_date'] = pd.to_datetime(df_products['dt_date'], format='%Y%m%d')
print(f"✓ Loaded product_daily_attrs.csv: {len(df_products)} rows")

print(f"\nDate range: {df_daily['dt_date'].min()} to {df_daily['dt_date'].max()}")
print(f"Days analyzed: {len(df_daily)}")

# Color scheme
COLORS = {
    'primary': '#2E86AB',
    'success': '#06A77D',
    'warning': '#F77F00',
    'danger': '#D62828',
    'secondary': '#6C757D',
    'info': '#17A2B8',
    'purple': '#6F42C1',
    'teal': '#20C997'
}

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# ==================== WEEKLY PATTERNS ANALYSIS ====================
print("\n" + "=" * 80)
print("SECTION 1: Weekly Patterns Analysis")
print("=" * 80)

df_daily['day_of_week'] = df_daily['dt_date'].dt.day_name()
df_daily['is_weekend'] = df_daily['dt_date'].dt.dayofweek.isin([5, 6])
df_daily['day_num'] = df_daily['dt_date'].dt.dayofweek

day_stats = df_daily.groupby('day_of_week').agg({
    'price_total_sum': ['mean', 'sum', 'std'],
    'trans_id_count': ['mean', 'sum'],
    'quantity_sum': ['mean', 'sum'],
    'customer_id_count': ['mean', 'sum']
}).round(2)

day_stats.columns = ['_'.join(col).strip() for col in day_stats.columns.values]
day_stats = day_stats.reset_index()

day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_stats['day_num'] = day_stats['day_of_week'].map({day: i for i, day in enumerate(day_order)})
day_stats = day_stats.sort_values('day_num')

best_day = day_stats.loc[day_stats['price_total_sum_mean'].idxmax(), 'day_of_week']
worst_day = day_stats.loc[day_stats['price_total_sum_mean'].idxmin(), 'day_of_week']
best_revenue = day_stats['price_total_sum_mean'].max()
worst_revenue = day_stats['price_total_sum_mean'].min()
revenue_swing = ((best_revenue - worst_revenue) / worst_revenue) * 100

print(f"Best day: {best_day} (${best_revenue:,.0f})")
print(f"Worst day: {worst_day} (${worst_revenue:,.0f})")
print(f"Revenue swing: {revenue_swing:.1f}%")

# Visualization 1: Weekly patterns
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 12))

bars = ax1.bar(day_stats['day_of_week'], day_stats['price_total_sum_mean'],
               color=[COLORS['danger'] if day == best_day else COLORS['primary'] for day in day_stats['day_of_week']],
               edgecolor='black', linewidth=1.5, alpha=0.8)
ax1.set_xlabel('Day of Week', fontsize=13, fontweight='bold')
ax1.set_ylabel('Average Revenue ($)', fontsize=13, fontweight='bold')
ax1.set_title('Average Revenue by Day of Week', fontsize=15, fontweight='bold', pad=15)
ax1.grid(True, alpha=0.3, linestyle=':', axis='y')
ax1.tick_params(axis='x', rotation=45)

for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'${height:,.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax2.bar(day_stats['day_of_week'], day_stats['trans_id_count_mean'],
        color=COLORS['success'], edgecolor='black', linewidth=1.5, alpha=0.8)
ax2.set_xlabel('Day of Week', fontsize=13, fontweight='bold')
ax2.set_ylabel('Average Transactions', fontsize=13, fontweight='bold')
ax2.set_title('Average Transactions by Day of Week', fontsize=15, fontweight='bold', pad=15)
ax2.grid(True, alpha=0.3, linestyle=':', axis='y')
ax2.tick_params(axis='x', rotation=45)

weekend_stats = df_daily.groupby('is_weekend').agg({
    'price_total_sum': 'mean',
    'trans_id_count': 'mean'
})
weekend_labels = ['Weekday', 'Weekend']
ax3.bar(weekend_labels, weekend_stats['price_total_sum'].values,
        color=[COLORS['primary'], COLORS['warning']], edgecolor='black', linewidth=1.5, alpha=0.8)
ax3.set_ylabel('Average Revenue ($)', fontsize=13, fontweight='bold')
ax3.set_title('Weekend vs Weekday Performance', fontsize=15, fontweight='bold', pad=15)
ax3.grid(True, alpha=0.3, linestyle=':', axis='y')

for i, val in enumerate(weekend_stats['price_total_sum'].values):
    ax3.text(i, val, f'${val:,.0f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

daily_sorted = df_daily.sort_values('dt_date')
ax4.plot(daily_sorted['dt_date'], daily_sorted['price_total_sum'],
         color=COLORS['primary'], linewidth=2, marker='o', markersize=4, alpha=0.7)

z = np.polyfit(range(len(daily_sorted)), daily_sorted['price_total_sum'].values, 1)
p = np.poly1d(z)
ax4.plot(daily_sorted['dt_date'], p(range(len(daily_sorted))),
         "r--", linewidth=2, label=f'Trend: ${z[0]:,.0f}/day', alpha=0.8)

ax4.set_xlabel('Date', fontsize=13, fontweight='bold')
ax4.set_ylabel('Daily Revenue ($)', fontsize=13, fontweight='bold')
ax4.set_title('Revenue Trend Over Time', fontsize=15, fontweight='bold', pad=15)
ax4.legend(fontsize=11, loc='best')
ax4.grid(True, alpha=0.3, linestyle=':')
ax4.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/01_weekly_patterns.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"✓ Saved: {OUTPUT_DIR}/01_weekly_patterns.png")

# ==================== HOURLY PATTERNS ANALYSIS ====================
print("\n" + "=" * 80)
print("SECTION 2: Hourly Patterns Analysis")
print("=" * 80)

hourly_stats = df_hourly.groupby('hour').agg({
    'price_total_sum': ['mean', 'sum', 'std'],
    'trans_id_count': ['mean', 'sum'],
    'quantity_sum': ['mean', 'sum']
}).round(2)

hourly_stats.columns = ['_'.join(col).strip() for col in hourly_stats.columns.values]
hourly_stats = hourly_stats.reset_index().sort_values('hour')

def get_time_period(hour):
    if 6 <= hour < 12:
        return 'Morning (6-12)'
    elif 12 <= hour < 18:
        return 'Afternoon (12-18)'
    elif 18 <= hour < 24:
        return 'Evening (18-24)'
    else:
        return 'Night (0-6)'

hourly_stats['period'] = hourly_stats['hour'].apply(get_time_period)

peak_hour = hourly_stats.loc[hourly_stats['price_total_sum_mean'].idxmax(), 'hour']
peak_revenue = hourly_stats['price_total_sum_mean'].max()
slowest_hour = hourly_stats.loc[hourly_stats['price_total_sum_mean'].idxmin(), 'hour']
slowest_revenue = hourly_stats['price_total_sum_mean'].min()

print(f"Peak hour: {peak_hour}:00 (${peak_revenue:,.0f})")
print(f"Slowest hour: {slowest_hour}:00 (${slowest_revenue:,.0f})")
print(f"Peak/Slowest ratio: {peak_revenue/slowest_revenue:.1f}x")

# Visualization 2: Hourly patterns
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))

colors = [COLORS['danger'] if h == peak_hour else COLORS['primary'] for h in hourly_stats['hour']]
ax1.bar(hourly_stats['hour'], hourly_stats['price_total_sum_mean'],
        color=colors, edgecolor='black', linewidth=1, alpha=0.8)
ax1.set_xlabel('Hour of Day', fontsize=13, fontweight='bold')
ax1.set_ylabel('Average Revenue ($)', fontsize=13, fontweight='bold')
ax1.set_title('Average Revenue by Hour of Day', fontsize=15, fontweight='bold', pad=15)
ax1.set_xticks(range(0, 24))
ax1.grid(True, alpha=0.3, linestyle=':', axis='y')

ax1.annotate(f'Peak: {peak_hour}:00\n${peak_revenue:,.0f}',
            xy=(peak_hour, peak_revenue), xytext=(peak_hour+2, peak_revenue*1.1),
            arrowprops=dict(arrowstyle='->', color=COLORS['danger'], lw=2),
            fontsize=11, fontweight='bold', color=COLORS['danger'])

ax2.plot(hourly_stats['hour'], hourly_stats['trans_id_count_mean'],
         color=COLORS['success'], linewidth=3, marker='o', markersize=8, alpha=0.7)
ax2.fill_between(hourly_stats['hour'], hourly_stats['trans_id_count_mean'],
                 alpha=0.3, color=COLORS['success'])
ax2.set_xlabel('Hour of Day', fontsize=13, fontweight='bold')
ax2.set_ylabel('Average Transactions', fontsize=13, fontweight='bold')
ax2.set_title('Transaction Volume by Hour', fontsize=15, fontweight='bold', pad=15)
ax2.set_xticks(range(0, 24))
ax2.grid(True, alpha=0.3, linestyle=':')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/02_hourly_patterns.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"✓ Saved: {OUTPUT_DIR}/02_hourly_patterns.png")

# ==================== TIME PERIOD ANALYSIS ====================
print("\n" + "=" * 80)
print("SECTION 3: Time Period Comparison")
print("=" * 80)

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

period_order = ['Morning (6-12)', 'Afternoon (12-18)', 'Evening (18-24)', 'Night (0-6)']
period_colors = [COLORS['warning'], COLORS['primary'], COLORS['purple'], COLORS['secondary']]

period_revenue = hourly_stats.groupby('period')['price_total_sum_mean'].mean().reindex(period_order)
ax1.bar(range(len(period_order)), period_revenue.values,
        color=period_colors, edgecolor='black', linewidth=1.5, alpha=0.8)
ax1.set_xticks(range(len(period_order)))
ax1.set_xticklabels(period_order, rotation=45, ha='right')
ax1.set_ylabel('Average Revenue ($)', fontsize=13, fontweight='bold')
ax1.set_title('Revenue by Time Period', fontsize=15, fontweight='bold', pad=15)
ax1.grid(True, alpha=0.3, linestyle=':', axis='y')

for i, val in enumerate(period_revenue.values):
    ax1.text(i, val, f'${val:,.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

period_trans = hourly_stats.groupby('period')['trans_id_count_mean'].mean().reindex(period_order)
ax2.bar(range(len(period_order)), period_trans.values,
        color=period_colors, edgecolor='black', linewidth=1.5, alpha=0.8)
ax2.set_xticks(range(len(period_order)))
ax2.set_xticklabels(period_order, rotation=45, ha='right')
ax2.set_ylabel('Average Transactions', fontsize=13, fontweight='bold')
ax2.set_title('Transactions by Time Period', fontsize=15, fontweight='bold', pad=15)
ax2.grid(True, alpha=0.3, linestyle=':', axis='y')

df_hourly['day_name'] = df_hourly['dt_date'].dt.day_name()
heatmap_data = df_hourly.pivot_table(
    values='price_total_sum',
    index='day_name',
    columns='hour',
    aggfunc='mean'
)
heatmap_data = heatmap_data.reindex(day_order)

sns.heatmap(heatmap_data, cmap='YlOrRd', annot=False, fmt='.0f',
            cbar_kws={'label': 'Revenue ($)'}, ax=ax3)
ax3.set_xlabel('Hour of Day', fontsize=13, fontweight='bold')
ax3.set_ylabel('Day of Week', fontsize=13, fontweight='bold')
ax3.set_title('Revenue Heatmap: Day × Hour', fontsize=15, fontweight='bold', pad=15)

cumulative_revenue = hourly_stats.sort_values('hour')['price_total_sum_sum'].cumsum()
cumulative_pct = (cumulative_revenue / cumulative_revenue.max()) * 100

ax4.plot(hourly_stats.sort_values('hour')['hour'], cumulative_pct,
         color=COLORS['primary'], linewidth=3, marker='o', markersize=6)
ax4.fill_between(hourly_stats.sort_values('hour')['hour'], cumulative_pct,
                 alpha=0.3, color=COLORS['primary'])
ax4.axhline(50, color=COLORS['danger'], linestyle='--', linewidth=2, label='50% of daily revenue')
ax4.set_xlabel('Hour of Day', fontsize=13, fontweight='bold')
ax4.set_ylabel('Cumulative Revenue %', fontsize=13, fontweight='bold')
ax4.set_title('Cumulative Revenue Distribution', fontsize=15, fontweight='bold', pad=15)
ax4.legend(fontsize=11)
ax4.grid(True, alpha=0.3, linestyle=':')
ax4.set_xticks(range(0, 24, 2))

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/03_time_period_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"✓ Saved: {OUTPUT_DIR}/03_time_period_analysis.png")

# ==================== PRODUCT PERFORMANCE BY TIME ====================
print("\n" + "=" * 80)
print("SECTION 4: Product Performance by Time")
print("=" * 80)

df_products['day_of_week'] = df_products['dt_date'].dt.day_name()
df_products['is_weekend'] = df_products['dt_date'].dt.dayofweek.isin([5, 6])

product_day_performance = df_products.groupby(['in_product_id', 'day_of_week']).agg({
    'price_total_sum': 'sum',
    'quantity_sum': 'sum'
}).reset_index()

product_weekend_performance = df_products.groupby(['in_product_id', 'is_weekend']).agg({
    'price_total_sum': 'sum',
    'quantity_sum': 'sum'
}).reset_index()

weekday_leader = product_weekend_performance[product_weekend_performance['is_weekend']==False].nlargest(1, 'price_total_sum')
weekend_leader = product_weekend_performance[product_weekend_performance['is_weekend']==True].nlargest(1, 'price_total_sum')

print(f"Weekday leader: Product {weekday_leader['in_product_id'].values[0]} (${weekday_leader['price_total_sum'].values[0]:,.0f})")
print(f"Weekend leader: Product {weekend_leader['in_product_id'].values[0]} (${weekend_leader['price_total_sum'].values[0]:,.0f})")

# Visualization 4: Product time analysis
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

top_products = df_products.groupby('in_product_id')['price_total_sum'].sum().nlargest(5).index
product_day_pivot = product_day_performance[product_day_performance['in_product_id'].isin(top_products)].pivot_table(
    values='price_total_sum',
    index='in_product_id',
    columns='day_of_week'
)[day_order]

product_day_pivot.T.plot(kind='bar', ax=ax1, width=0.8, edgecolor='black', linewidth=1)
ax1.set_xlabel('Day of Week', fontsize=13, fontweight='bold')
ax1.set_ylabel('Revenue ($)', fontsize=13, fontweight='bold')
ax1.set_title('Top 5 Products: Daily Performance', fontsize=15, fontweight='bold', pad=15)
ax1.legend(title='Product', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
ax1.grid(True, alpha=0.3, linestyle=':', axis='y')
ax1.tick_params(axis='x', rotation=45)

product_weekend_pivot = product_weekend_performance[product_weekend_performance['in_product_id'].isin(top_products)].pivot_table(
    values='price_total_sum',
    index='in_product_id',
    columns='is_weekend'
)
product_weekend_pivot.columns = ['Weekday', 'Weekend']

product_weekend_pivot.plot(kind='bar', ax=ax2, width=0.7,
                           color=[COLORS['primary'], COLORS['warning']],
                           edgecolor='black', linewidth=1.5)
ax2.set_xlabel('Product', fontsize=13, fontweight='bold')
ax2.set_ylabel('Revenue ($)', fontsize=13, fontweight='bold')
ax2.set_title('Top 5 Products: Weekday vs Weekend', fontsize=15, fontweight='bold', pad=15)
ax2.legend(fontsize=11)
ax2.grid(True, alpha=0.3, linestyle=':', axis='y')
ax2.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/04_product_time_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"✓ Saved: {OUTPUT_DIR}/04_product_time_analysis.png")

# ==================== TREND ANALYSIS & FORECASTING ====================
print("\n" + "=" * 80)
print("SECTION 5: Trend Analysis & Forecasting")
print("=" * 80)

daily_sorted = df_daily.sort_values('dt_date').reset_index(drop=True)
daily_sorted['day_number'] = range(len(daily_sorted))

slope, intercept, r_value, p_value, std_err = stats.linregress(
    daily_sorted['day_number'],
    daily_sorted['price_total_sum']
)

avg_revenue = daily_sorted['price_total_sum'].mean()
growth_rate = (slope / avg_revenue) * 100
volatility = (daily_sorted['price_total_sum'].std() / avg_revenue) * 100
trend_strength = r_value ** 2

print(f"Average daily revenue: ${avg_revenue:,.0f}")
print(f"Daily growth rate: {growth_rate:+.2f}%")
print(f"Monthly projected growth: {growth_rate * 30:+.1f}%")
print(f"Revenue volatility: {volatility:.1f}%")
print(f"Trend strength (R²): {trend_strength:.3f}")

if abs(growth_rate) < 0.5:
    trend_classification = "STABLE"
    trend_color = COLORS['secondary']
elif growth_rate > 0:
    trend_classification = "GROWING"
    trend_color = COLORS['success']
else:
    trend_classification = "DECLINING"
    trend_color = COLORS['danger']

print(f"Trend: {trend_classification}")

# Forecast
forecast_days = 7
future_day_numbers = range(len(daily_sorted), len(daily_sorted) + forecast_days)
forecast_revenue = [slope * day + intercept for day in future_day_numbers]
forecast_dates = pd.date_range(start=daily_sorted['dt_date'].max() + pd.Timedelta(days=1), periods=forecast_days)

# Visualization 5: Trend and forecast
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 12))

ax1.scatter(daily_sorted['dt_date'], daily_sorted['price_total_sum'],
           color=COLORS['primary'], s=80, alpha=0.6, edgecolor='black', linewidth=1, label='Actual')
ax1.plot(daily_sorted['dt_date'], slope * daily_sorted['day_number'] + intercept,
        color=trend_color, linewidth=3, linestyle='--', label=f'Trend ({trend_classification})', alpha=0.8)
ax1.plot(forecast_dates, forecast_revenue,
        color=COLORS['warning'], linewidth=2, linestyle=':', marker='s', markersize=6,
        label='7-Day Forecast', alpha=0.8)

ax1.set_xlabel('Date', fontsize=13, fontweight='bold')
ax1.set_ylabel('Revenue ($)', fontsize=13, fontweight='bold')
ax1.set_title(f'Revenue Trend Analysis (R²={trend_strength:.3f})', fontsize=15, fontweight='bold', pad=15)
ax1.legend(fontsize=11, loc='best')
ax1.grid(True, alpha=0.3, linestyle=':')
ax1.tick_params(axis='x', rotation=45)

daily_sorted['MA3'] = daily_sorted['price_total_sum'].rolling(window=3).mean()
daily_sorted['MA7'] = daily_sorted['price_total_sum'].rolling(window=7).mean()

ax2.plot(daily_sorted['dt_date'], daily_sorted['price_total_sum'],
        color=COLORS['secondary'], linewidth=1, alpha=0.5, label='Daily')
ax2.plot(daily_sorted['dt_date'], daily_sorted['MA3'],
        color=COLORS['primary'], linewidth=2, label='3-Day MA')
ax2.plot(daily_sorted['dt_date'], daily_sorted['MA7'],
        color=COLORS['danger'], linewidth=2, label='7-Day MA')

ax2.set_xlabel('Date', fontsize=13, fontweight='bold')
ax2.set_ylabel('Revenue ($)', fontsize=13, fontweight='bold')
ax2.set_title('Moving Averages', fontsize=15, fontweight='bold', pad=15)
ax2.legend(fontsize=11)
ax2.grid(True, alpha=0.3, linestyle=':')
ax2.tick_params(axis='x', rotation=45)

ax3.hist(daily_sorted['price_total_sum'], bins=15, color=COLORS['primary'],
        edgecolor='black', alpha=0.7)
ax3.axvline(daily_sorted['price_total_sum'].mean(), color=COLORS['danger'],
           linestyle='--', linewidth=2, label=f"Mean: ${daily_sorted['price_total_sum'].mean():,.0f}")
ax3.axvline(daily_sorted['price_total_sum'].median(), color=COLORS['warning'],
           linestyle='--', linewidth=2, label=f"Median: ${daily_sorted['price_total_sum'].median():,.0f}")

ax3.set_xlabel('Daily Revenue ($)', fontsize=13, fontweight='bold')
ax3.set_ylabel('Frequency (Days)', fontsize=13, fontweight='bold')
ax3.set_title(f'Revenue Distribution (σ={volatility:.1f}%)', fontsize=15, fontweight='bold', pad=15)
ax3.legend(fontsize=11)
ax3.grid(True, alpha=0.3, linestyle=':', axis='y')

daily_sorted['growth_rate'] = daily_sorted['price_total_sum'].pct_change() * 100
ax4.bar(daily_sorted['dt_date'][1:], daily_sorted['growth_rate'][1:],
       color=[COLORS['success'] if x > 0 else COLORS['danger'] for x in daily_sorted['growth_rate'][1:]],
       edgecolor='black', linewidth=0.5, alpha=0.7)
ax4.axhline(0, color='black', linewidth=1)

ax4.set_xlabel('Date', fontsize=13, fontweight='bold')
ax4.set_ylabel('Day-over-Day Growth %', fontsize=13, fontweight='bold')
ax4.set_title('Daily Growth Rate', fontsize=15, fontweight='bold', pad=15)
ax4.grid(True, alpha=0.3, linestyle=':', axis='y')
ax4.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/05_trend_forecast_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"✓ Saved: {OUTPUT_DIR}/05_trend_forecast_analysis.png")

print("\n" + "=" * 80)
print("TEST COMPLETED SUCCESSFULLY!")
print("=" * 80)
print(f"\nAll 5 visualizations created in: {OUTPUT_DIR}/")
print("  1. 01_weekly_patterns.png")
print("  2. 02_hourly_patterns.png")
print("  3. 03_time_period_analysis.png")
print("  4. 04_product_time_analysis.png")
print("  5. 05_trend_forecast_analysis.png")
print(f"\nKey Metrics:")
print(f"  • Trend: {trend_classification} ({growth_rate:+.2f}% daily)")
print(f"  • Best day: {best_day} (${best_revenue:,.0f})")
print(f"  • Peak hour: {peak_hour}:00 (${peak_revenue:,.0f})")
print(f"  • Volatility: {volatility:.1f}%")
print(f"  • 7-day forecast: ${sum(forecast_revenue):,.0f} total")
print("\nNotebook is ready for execution in Jupyter!")
