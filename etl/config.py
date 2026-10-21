"""
etl/config.py — Centralised configuration for the ETL pipeline.

All path defaults, schema definitions, and business-rule constants
live here so that callers only need to change one file.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

# ---------------------------------------------------------------------------
# Repository root & default paths
# ---------------------------------------------------------------------------
REPO_ROOT: Path = Path(__file__).resolve().parent.parent

RAW_CSV: Path = REPO_ROOT / "customer_shopping_behavior.csv"
PROCESSED_DIR: Path = REPO_ROOT / "data" / "processed"
DB_PATH: Path = PROCESSED_DIR / "retail_bi.db"

CLEANED_CSV: Path = PROCESSED_DIR / "customer_shopping_behavior_cleaned.csv"
CUSTOMER_INTEL_CSV: Path = PROCESSED_DIR / "customer_intelligence.csv"
PRODUCT_INTEL_CSV: Path = PROCESSED_DIR / "product_intelligence.csv"
CATEGORY_INTEL_CSV: Path = PROCESSED_DIR / "category_intelligence.csv"

LOG_DIR: Path = REPO_ROOT / "logs"

# ---------------------------------------------------------------------------
# Raw-CSV expected columns (used in Extract validation)
# ---------------------------------------------------------------------------
RAW_REQUIRED_COLUMNS: List[str] = [
    "Customer ID",
    "Age",
    "Gender",
    "Item Purchased",
    "Category",
    "Purchase Amount (USD)",
    "Location",
    "Size",
    "Color",
    "Season",
    "Review Rating",
    "Subscription Status",
    "Shipping Type",
    "Discount Applied",
    "Promo Code Used",
    "Previous Purchases",
    "Payment Method",
    "Frequency of Purchases",
]

# ---------------------------------------------------------------------------
# Column rename mapping (raw → snake_case)
# ---------------------------------------------------------------------------
COLUMN_RENAME_MAP: Dict[str, str] = {
    "Customer ID": "customer_id",
    "Age": "age",
    "Gender": "gender",
    "Item Purchased": "item_purchased",
    "Category": "category",
    "Purchase Amount (USD)": "purchase_amount_usd",
    "Location": "location",
    "Size": "size",
    "Color": "color",
    "Season": "season",
    "Review Rating": "review_rating",
    "Subscription Status": "subscription_status",
    "Shipping Type": "shipping_type",
    "Discount Applied": "discount_applied",
    "Promo Code Used": "promo_code_used",
    "Previous Purchases": "previous_purchases",
    "Payment Method": "payment_method",
    "Frequency of Purchases": "frequency_of_purchases",
}

# ---------------------------------------------------------------------------
# Business rules: allowed categorical values
# ---------------------------------------------------------------------------
VALID_CATEGORIES: List[str] = ["Clothing", "Accessories", "Footwear", "Outerwear"]
VALID_GENDERS: List[str] = ["Male", "Female"]
VALID_SUBSCRIPTION_STATUSES: List[str] = ["Yes", "No"]
VALID_DISCOUNT_VALUES: List[str] = ["Yes", "No"]
VALID_SEASONS: List[str] = ["Spring", "Summer", "Fall", "Winter"]

# After harmonisation these are the only valid frequency labels
VALID_FREQUENCIES: List[str] = ["Weekly", "Bi-Weekly", "Monthly", "Quarterly", "Annually"]

FREQUENCY_HARMONISATION_MAP: Dict[str, str] = {
    "Fortnightly": "Bi-Weekly",
    "Bi-Weekly": "Bi-Weekly",
    "Weekly": "Weekly",
    "Monthly": "Monthly",
    "Quarterly": "Quarterly",
    "Every 3 Months": "Quarterly",
    "Annually": "Annually",
}

FREQUENCY_DAYS_MAP: Dict[str, int] = {
    "Weekly": 7,
    "Bi-Weekly": 14,
    "Monthly": 30,
    "Quarterly": 90,
    "Annually": 365,
}

# ---------------------------------------------------------------------------
# Numeric range guards
# ---------------------------------------------------------------------------
AGE_MIN: int = 18
AGE_MAX: int = 70
PURCHASE_MIN: float = 1.0
PURCHASE_MAX: float = 10_000.0
RATING_MIN: float = 1.0
RATING_MAX: float = 5.0
PREV_PURCHASES_MIN: int = 0
PREV_PURCHASES_MAX: int = 500

# ---------------------------------------------------------------------------
# Feature-engineering thresholds (must match notebook logic exactly)
# ---------------------------------------------------------------------------
AGE_BINS = [17, 30, 45, 60, 71]
AGE_LABELS = [
    "18-30 (Young Adult)",
    "31-45 (Adult)",
    "46-60 (Middle-Aged)",
    "61-70 (Senior)",
]

# Customer Value Tier
VALUE_LOW_MAX: float = 40.0       # spend < 40  → Low Value
VALUE_MEDIUM_MAX: float = 75.0    # 40 ≤ spend ≤ 75 → Medium Value
                                   # spend > 75  → High Value

# Engagement Tier
ENGAGEMENT_LOW_MAX: int = 15      # prev_purchases ≤ 15  → Low Engagement
ENGAGEMENT_MED_MAX: int = 35      # 16–35              → Medium Engagement
                                   # > 35               → High Engagement

# ---------------------------------------------------------------------------
# SQLite table name
# ---------------------------------------------------------------------------
TRANSACTIONS_TABLE: str = "customer_transactions"
CUSTOMER_INTEL_TABLE: str = "customer_intelligence"
PRODUCT_INTEL_TABLE: str = "product_intelligence"
CATEGORY_INTEL_TABLE: str = "category_intelligence"

# ---------------------------------------------------------------------------
# Customer-intelligence CSV columns (must match notebook exactly)
# ---------------------------------------------------------------------------
CUSTOMER_INTEL_COLUMNS: List[str] = [
    "customer_id", "age", "gender", "age_group", "purchase_amount_usd",
    "customer_value_tier", "previous_purchases", "engagement_tier",
    "value_engagement_segment", "subscription_status", "frequency_of_purchases",
    "purchase_frequency_days", "category", "item_purchased",
    "review_rating", "discount_applied", "shipping_type",
    "payment_method", "location", "season",
]
