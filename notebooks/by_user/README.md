# 👥 User-Focused Notebooks

This folder contains notebooks designed for **specific user personas**, optimized for their unique workflows and pain points.

---

## 📚 Available Notebooks

### 1. Business Analyst Monthly Report
**File:** `business_analyst_monthly_report.ipynb`
**User:** [USER-01: Business Analyst](../../docs/business/users/USER-01-Business-Analyst.md)
**Created:** 2025-10-23

**Purpose:**
Automate the complete monthly business review process for business analysts who spend 8 hours/month on manual Excel reporting.

**What It Does:**
- ✅ Loads data from monthly CSV export
- 📊 Generates 6 executive KPI cards
- 📈 Creates revenue trend analysis with growth rate
- 🏆 Identifies top 10 products and Pareto analysis (80/20 rule)
- 👥 Segments customers by engagement (VIP, Loyal, Regular, Occasional)
- ⏰ Analyzes operational patterns (day of week, hourly peaks)
- 🎯 Produces prioritized action plan for next month
- 💾 Saves 6 professional charts ready for PowerPoint

**Time Savings:**
8 hours → 5 minutes (88% reduction)

**Key Features for Business Analysts:**
1. **Consistency** - Same methodology every month, no "did I calculate this right?" moments
2. **Professional Outputs** - Executive-ready visualizations with proper formatting
3. **Easy Configuration** - Just update data path, run all cells, done
4. **Actionable Insights** - Automatic generation of prioritized recommendations
5. **Error Handling** - Clear error messages if data format is wrong
6. **Validation** - Data quality checks before analysis begins

**Use Case:** [USE-CASE-01: Monthly Business Review](../../docs/business/use_cases/USE-CASE-01-Monthly-Business-Review.md)

---

### 2. Small Business Owner Profit Optimizer
**File:** `small_business_owner_profit_optimizer.ipynb`
**User:** [USER-02: Small Business Owner](../../docs/business/users/USER-02-Small-Business-Owner.md)
**Created:** 2025-10-23

**Purpose:**
Simple, actionable insights to increase profit this month. No technical jargon, just plain English recommendations with dollar amounts.

**What It Does:**
- 💰 **Am I making money?** - Your actual profit margin vs industry benchmarks
- 📦 **What should I order more of?** - Product matrix (Stars, Cash Cows, Workhorses, Dead Stock)
- 🗑️ **What's wasting my cash?** - Dead stock analysis with clearance recommendations
- 💵 **Should I raise prices?** - Underpriced products with pricing opportunities
- 👥 **Who are my best customers?** - VIP identification and 80/20 rule analysis
- 🎯 Personalized action plan with dollar values and ROI

**Time Required:**
3 minutes to review (no technical background needed)

**Key Features for Business Owners:**
1. **Plain English** - No jargon, no technical terms, just "here's what to do"
2. **Dollar Values** - Every recommendation shows expected profit increase
3. **Simple Actions** - "Raise prices 5% on Product X = $5K/year"
4. **Risk-Free Testing** - 30-day test periods for price changes
5. **One-Page Summary** - Quick scan of business health
6. **ROI Focus** - Shows 12:1 typical ROI (12.5x return on investment)

**Expected Outcome:**
15-20% profit increase within 90 days (typical: $30K-50K additional annual profit for $1M revenue businesses)

**Use Cases:**
- [USE-CASE-02: Pricing Strategy Optimization](../../docs/business/use_cases/USE-CASE-02-Pricing-Strategy-Optimization.md)
- Product performance assessment
- Inventory optimization

---

### 3. Operations Manager Staffing & Inventory Optimizer
**File:** `operations_manager_staffing_optimizer.ipynb`
**User:** [USER-03: Operations Manager](../../docs/business/users/USER-03-Operations-Manager.md)
**Created:** 2025-10-23

**Purpose:**
Optimize staffing schedules and inventory orders to cut costs while improving service quality. Tactical, actionable recommendations for weekly operations.

**What It Does:**
- 👥 **Day of Week Analysis** - Identify busy/slow days with specific staffing recommendations
- ⏰ **Hourly Patterns** - Peak hours analysis for shift scheduling
- 📦 **Product Classification** - Stars, Workhorses, Cash Cows, Dead Stock matrix
- 📋 **Ordering Guide** - Exact quantities to order for each product based on velocity
- 💰 **Labor Cost Tracking** - Current labor % vs target with gap analysis
- 🎯 **Weekly Action Plan** - Prioritized list of changes to make this week

**Time Required:**
15 minutes per week (43% time savings vs manual scheduling)

**Key Features for Operations Managers:**
1. **Operational Metrics** - Labor %, inventory turns, velocity (units/day)
2. **Specific Actions** - "Add 1 staff on Friday 5-8 PM, remove 1 on Sunday morning"
3. **Dollar Calculations** - "$8K/year savings by shifting 1 employee"
4. **Order Quantities** - "Product X sells 5 units/day → order 53 units"
5. **Traffic Patterns** - Color-coded high/medium/low traffic hours
6. **Comparison to Target** - "You're at 32% labor, target is 28%, here's how to close gap"

**Expected Outcome:**
- 15% labor cost reduction (typical: $20K-50K/year for $100K/month location)
- 70% dead stock reduction (free up $28K cash)
- 80% fewer stockouts (capture $10-20K lost sales)

**Use Cases:**
- [USE-CASE-03: Staffing Optimization](../../docs/business/use_cases/USE-CASE-03-Staffing-Optimization.md)
- Product performance assessment
- Weekly schedule creation

---

## 🎯 How to Use These Notebooks

### Step 1: Choose Your Persona
- Are you a Business Analyst? → `business_analyst_monthly_report.ipynb`
- Are you a Small Business Owner? → `small_business_owner_profit_optimizer.ipynb`
- Are you an Operations Manager? → `operations_manager_staffing_optimizer.ipynb`

### Step 2: Update Configuration
Open the notebook and edit the configuration cell:
```python
DATA_PATH = '../../data/your_data_folder/'
COMPANY_NAME = "Your Company Name"
```

### Step 3: Run Analysis
- **Option A:** Cell → Run All (executes entire notebook in ~2 minutes)
- **Option B:** Shift+Enter through each cell to see outputs step-by-step

### Step 4: Review Outputs
All charts are saved to a folder named after the notebook (e.g., `business_analyst_monthly_report/`)

### Step 5: Present Insights
Copy charts into your PowerPoint presentation and share with management.

---

## 🆚 Difference from `/insights` Notebooks

| Aspect | `/insights` Notebooks | `/by_user` Notebooks |
|--------|----------------------|---------------------|
| **Focus** | General business insights | User persona-specific workflows |
| **Output** | 4-6 visualizations per notebook | Complete monthly report (6+ charts) |
| **Use Case** | Exploratory analysis | Routine reporting automation |
| **Audience** | Anyone analyzing data | Specific user roles (analyst, owner, manager) |
| **Customization** | Minimal configuration | Persona-optimized settings |
| **Documentation** | Insight-focused | Workflow-focused (matches user pain points) |

**Example:**
- **Insights Notebook:** "03_seasonal_trend_analysis.ipynb" shows seasonal patterns
- **User Notebook:** "business_analyst_monthly_report.ipynb" includes seasonality + KPIs + products + customers + action plan

---

## 📋 Roadmap - Future User Notebooks

### Coming Soon

**Chilean Market Variants** - Localized versions for Chilean businesses
- `business_analyst_monthly_report_CL.ipynb` - CLP currency, SII tax periods
- `small_business_owner_profit_optimizer_CL.ipynb` - Chilean seasonality (Dec/Feb), Boletas vs Facturas
- `operations_manager_staffing_optimizer_CL.ipynb` - Código del Trabajo compliance, Metro schedules
- Expected: Q2 2025

**Additional Personas** - Future user notebooks
- Finance Manager / CFO (budget vs actual, forecasting, scenario modeling)
- Sales Manager (territory analysis, sales team performance, commission tracking)
- Marketing Manager (campaign ROI, customer acquisition cost, attribution)
- Expected: Q3 2025+

---

## 🔧 Technical Notes

### Data Requirements
All notebooks expect data from the GabeDA v2.x architecture:
- `daily_attrs.csv` - Daily aggregated metrics
- `product_daily_attrs.csv` - Product-level daily data
- `customer_daily_attrs.csv` - Customer-level daily data
- `daily_hour_attrs.csv` - Hourly patterns (optional)

### Dependencies
Same as main project:
```bash
pip install pandas numpy matplotlib seaborn jupyter
```

### Output Format
- All charts: PNG at 300 DPI (presentation-ready)
- Folder structure: `{notebook_name}/01_chart_name.png`
- File sizes: ~100-300 KB per chart

---

## 📖 Related Documentation

- **User Profiles:** [docs/business/users/](../../docs/business/users/)
- **Use Cases:** [docs/business/use_cases/](../../docs/business/use_cases/)
- **Business Skill:** [.claude/skills/business/Skill.md](../../.claude/skills/business/Skill.md)
- **Insights Notebooks:** [notebooks/insights/](../insights/)

---

## 💡 Contributing New User Notebooks

To add a new user-focused notebook:

1. **Identify the persona** - Document in `docs/business/users/USER-XX-*.md`
2. **Define the workflow** - What's their current manual process?
3. **Map pain points** - What takes the most time? What causes errors?
4. **Design outputs** - What charts do they need for their stakeholders?
5. **Create notebook** - Follow structure of `business_analyst_monthly_report.ipynb`
6. **Test with real user** - Get feedback from someone in that role
7. **Document** - Update this README with new notebook details

---

**Last Updated:** 2025-10-23
**Maintainer:** GabeDA Business Team
**Feedback:** Open an issue or submit a PR
