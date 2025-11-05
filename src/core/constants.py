"""
Central constants and default values for GabeDA system.

Single Responsibility: Define system-wide constants ONLY
- Default values for missing/invalid data
- Threshold values for business logic
- System-wide configuration constants

Usage:
    from src.core.constants import DEFAULT_FLOAT, MARGIN_THRESHOLD_PCT

    def margin_unit_pct(in_price_unit, in_cost_unit):
        if pd.isna(in_price_unit) or pd.isna(in_cost_unit):
            return DEFAULT_FLOAT
        # ... rest of calculation
"""

# ==============================================================================
# DEFAULT VALUES (for missing/invalid data)
# ==============================================================================

DEFAULT_FLOAT = -16.0
"""Default value for float calculations when result is invalid/missing."""

DEFAULT_INT = -16
"""Default value for integer calculations when result is invalid/missing."""

DEFAULT_STRING = "UNKNOWN"
"""Default value for string fields when value is missing."""

DEFAULT_BOOL = False
"""Default value for boolean fields when value is indeterminate."""


# ==============================================================================
# BUSINESS LOGIC THRESHOLDS
# ==============================================================================

MARGIN_THRESHOLD_PCT = 10.0
"""Minimum acceptable margin percentage (default: 10.0%)."""

LOW_STOCK_THRESHOLD = 10
"""Stock level below which product is considered low stock."""

DEAD_STOCK_DAYS = 30
"""Days without sales to consider product as dead stock."""

HIGH_VALUE_TRANSACTION_MULTIPLIER = 2.0
"""Multiplier of average transaction value to flag as high-value."""


# ==============================================================================
# TIME-BASED CONSTANTS
# ==============================================================================

BUSINESS_HOURS_START = 9
"""Start of business hours (24-hour format)."""

BUSINESS_HOURS_END = 18
"""End of business hours (24-hour format)."""

MORNING_START = 5
"""Start of morning period (24-hour format)."""

MORNING_END = 11
"""End of morning period (24-hour format)."""

AFTERNOON_START = 12
"""Start of afternoon period (24-hour format)."""

AFTERNOON_END = 17
"""End of afternoon period (24-hour format)."""

EVENING_START = 17
"""Start of evening period (24-hour format)."""

EVENING_END = 22
"""End of evening period (24-hour format)."""


# ==============================================================================
# ELEMENT CONSTANTS
# ==============================================================================

FIRST_VALUE = 0

# ==============================================================================
# DATA VALIDATION CONSTANTS
# ==============================================================================

MAX_PRICE_DEVIATION_PCT = 500.0
"""Maximum acceptable price deviation percentage for outlier detection."""

MIN_QUANTITY = 0
"""Minimum valid quantity for transactions."""

MAX_QUANTITY = 10000
"""Maximum valid quantity for transactions (outlier threshold)."""


# ==============================================================================
# FEATURE CALCULATION CONSTANTS
# ==============================================================================

PARETO_THRESHOLD = 0.8
"""Threshold for Pareto analysis (80/20 rule)."""

TOP_PRODUCTS_PERCENTILE = 0.2
"""Percentile threshold for top products (top 20%)."""

CUSTOMER_CHURN_DAYS = 90
"""Days of inactivity to consider customer churned."""


# ==============================================================================
# EXPORT/FORMATTING CONSTANTS
# ==============================================================================

EXCEL_MAX_ROWS_PER_SHEET = 1048576
"""Maximum rows per Excel sheet (Excel limit)."""

DECIMAL_PRECISION = 2
"""Default decimal precision for rounding float values."""

PERCENTAGE_PRECISION = 2
"""Default decimal precision for percentage values."""


# ==============================================================================
# COLUMN SCHEMA (base_case.csv structure)
# ==============================================================================
# This defines the validation rules for all input columns
# - optional=0: REQUIRED field (row rejected if null)
# - optional=1: OPTIONAL field (warning if null, row kept)
# - inferable=0: NOT inferable (must be provided or derived from data)
# - inferable=1: INFERABLE (can be calculated from other columns)

COLUMN_SCHEMA = {
    # REQUIRED COLUMNS (optional=0)
    'in_dt': {
        'optional': 0,      # REQUIRED - transaction datetime
        'inferable': 0,     # NOT inferable - must be provided
        'description': 'Transaction datetime',
        'dtype': 'datetime64[ns]'
    },
    'in_trans_id': {
        'optional': 0,      # REQUIRED - unique transaction ID
        'inferable': 0,     # NOT inferable - must be provided
        'description': 'Unique transaction identifier',
        'dtype': 'object'
    },
    'in_product_id': {
        'optional': 0,      # REQUIRED - product identifier
        'inferable': 0,     # NOT inferable - must be provided
        'description': 'Product identifier',
        'dtype': 'object'
    },
    'in_quantity': {
        'optional': 0,      # REQUIRED - quantity sold
        'inferable': 0,     # NOT inferable - must be provided
        'description': 'Quantity of items in transaction',
        'dtype': 'float64'
    },
    'in_price_total': {
        'optional': 0,      # REQUIRED - total price/revenue
        'inferable': 0,     # NOT inferable - must be provided
        'description': 'Total price/revenue for transaction',
        'dtype': 'float64'
    },

    # OPTIONAL COLUMNS (optional=1, inferable=0)
    'in_trans_type': {
        'optional': 1,      # OPTIONAL - transaction type
        'inferable': 0,     # NOT inferable - must be provided if available
        'description': 'Transaction type (sale, return, etc.)',
        'dtype': 'object'
    },
    'in_customer_id': {
        'optional': 1,      # OPTIONAL - customer identifier
        'inferable': 0,     # NOT inferable - must be provided if available
        'description': 'Customer identifier',
        'dtype': 'object'
    },
    'in_description': {
        'optional': 1,      # OPTIONAL - product description
        'inferable': 0,     # NOT inferable - must be provided if available
        'description': 'Product description',
        'dtype': 'object'
    },
    'in_category': {
        'optional': 1,      # OPTIONAL - product category
        'inferable': 0,     # NOT inferable - must be provided if available
        'description': 'Product category',
        'dtype': 'object'
    },
    'in_unit_type': {
        'optional': 1,      # OPTIONAL - unit of measure
        'inferable': 0,     # NOT inferable - must be provided if available
        'description': 'Unit of measure (kg, unit, liter, etc.)',
        'dtype': 'object'
    },
    'in_stock': {
        'optional': 1,      # OPTIONAL - stock level
        'inferable': 0,     # NOT inferable - must be provided if available
        'description': 'Current stock level',
        'dtype': 'float64'
    },

    # INFERABLE COLUMNS (optional=1, inferable=1)
    # These can be calculated from other columns via synthetic features
    'in_cost_unit': {
        'optional': 1,      # OPTIONAL - can be inferred
        'inferable': 1,     # INFERABLE - from in_cost_total / in_quantity
        'description': 'Cost per unit (can be inferred from cost_total/quantity)',
        'dtype': 'float64'
    },
    'in_cost_total': {
        'optional': 1,      # OPTIONAL - can be inferred
        'inferable': 1,     # INFERABLE - from in_cost_unit * in_quantity
        'description': 'Total cost (can be inferred from cost_unit * quantity)',
        'dtype': 'float64'
    },
    'in_price_unit': {
        'optional': 1,      # OPTIONAL - can be inferred
        'inferable': 1,     # INFERABLE - from in_price_total / in_quantity
        'description': 'Price per unit (can be inferred from price_total/quantity)',
        'dtype': 'float64'
    },
    'in_discount_total': {
        'optional': 1,      # OPTIONAL - can be inferred
        'inferable': 1,     # INFERABLE - from gross_total - price_total
        'description': 'Total discount amount (can be inferred)',
        'dtype': 'float64'
    },
    'in_commission_total': {
        'optional': 1,      # OPTIONAL - can be inferred
        'inferable': 1,     # INFERABLE - from commission rate
        'description': 'Total commission amount (can be inferred)',
        'dtype': 'float64'
    },
    'in_margin': {
        'optional': 1,      # OPTIONAL - can be inferred
        'inferable': 1,     # INFERABLE - from (price_total - cost_total) / price_total
        'description': 'Profit margin (can be inferred from price and cost)',
        'dtype': 'float64'
    },
}

# Helper function to get required columns
def get_required_columns():
    """Return list of required column names (optional=0)."""
    return [col for col, spec in COLUMN_SCHEMA.items() if spec['optional'] == 0]

# Helper function to get optional columns
def get_optional_columns():
    """Return list of optional column names (optional=1)."""
    return [col for col, spec in COLUMN_SCHEMA.items() if spec['optional'] == 1]

# Helper function to get inferable columns
def get_inferable_columns():
    """Return list of inferable column names (inferable=1)."""
    return [col for col, spec in COLUMN_SCHEMA.items() if spec['inferable'] == 1]

# Quick reference lists
REQUIRED_COLUMNS = get_required_columns()
"""List of required column names that must not be null."""

OPTIONAL_COLUMNS = get_optional_columns()
"""List of optional column names that can be null."""

INFERABLE_COLUMNS = get_inferable_columns()
"""List of column names that can be inferred from other columns."""
